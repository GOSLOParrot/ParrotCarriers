using System;
using UnityEngine;

#if UNITY_XR_HANDS
using UnityEngine.XR.Hands;
#endif

namespace ParrotApp.Hands
{
    /// <summary>
    /// Sprint4 Phase 4 W3.A.2 — pure local gesture event source.
    ///
    /// <b>本类与 ParrotDev 的 <c>XRHandTracker</c> 不同的地方</b>（按用户 2026-04-29
    /// 决定）：
    /// <list type="bullet">
    /// <item><b>不发 LiveKit DataChannel</b>。手势是 Reflex 层（行为矩阵 §3.3 第 2 行），
    ///   消费者只在 Unity 进程内（<c>PerchOnHand</c>）。Brain 不需要原始手势流；
    ///   后果（如 PERCHED_ON_HAND body 状态）通过 EcpState A.3 双触发外溢。</item>
    /// <item><b>新增 <see cref="HandGestureSnapshot.IndexIntermediate"/></b>：食指中段
    ///   指节，作为"鸟踩树枝"的物理落点（<c>parrot_behavior_rules §5.1</c> +
    ///   entry doc §3.3 末段"成功判定点"——食指中段，不是指尖）。</item>
    /// <item><b>手势改为 <see cref="GestureBranch"/></b>：单手横着伸出食指（其他手指
    ///   弯曲 + 食指方向接近水平），像一根树枝。</item>
    /// </list>
    ///
    /// <b>包依赖</b>：实际手势检测依赖 <c>com.unity.xr.hands</c>。当前 ArSpike
    /// <c>Packages/manifest.json</c> 没装该包，<c>csc.rsp</c> 也没 define
    /// <c>UNITY_XR_HANDS</c>。装包并加 define 后本类自动启用真实检测；之前可走
    /// <see cref="DebugFireBranchGesture"/> Inspector ContextMenu 触发。
    /// </summary>
    public class HandGestureSource : MonoBehaviour
    {
        public const string GestureNone = "none";
        public const string GestureBranch = "index_finger_branch";
        public const string GestureFist = "closed_fist";

#if UNITY_XR_HANDS
        public enum Handedness { Left, Right }

        [Header("Tracking")]
        [SerializeField] private Handedness preferredHand = Handedness.Right;

        [Header("Gesture Thresholds")]
        [Tooltip("Max curl angle (deg) for a finger to count as extended")]
        [SerializeField] private float fingerExtendedMaxAngle = 40f;
        [Tooltip("Min curl angle (deg) for a finger to count as curled")]
        [SerializeField] private float fingerCurledMinAngle = 60f;
        [Tooltip("|dot(indexDir, Vector3.up)| <= this => 'horizontal' (branch-like)")]
        [SerializeField] private float indexHorizontalMaxAbsDotUp = 0.45f;
#endif

        [Header("Update")]
        [Tooltip("Interval between OnGestureSnapshot fires (seconds). 0 = every frame.")]
        [SerializeField] private float snapshotIntervalSeconds = 0.05f;

        public bool IsHandDetected { get; private set; }
        public string CurrentGesture { get; private set; } = GestureNone;
        public Vector3 PalmPosition { get; private set; }
        public Vector3 IndexTipPosition { get; private set; }

        /// <summary>
        /// 食指中段指节（<see cref="XRHandJointID.IndexIntermediate"/> 经
        /// XROrigin 变换后的世界坐标）。<see cref="PerchOnHand"/> 用作飞行目标。
        /// </summary>
        public Vector3 IndexIntermediatePosition { get; private set; }

        public event Action<HandGestureSnapshot> OnGestureSnapshot;

        private float _lastSnapshotAt;
        private string _lastSnapshotGesture = GestureNone;
        private bool _lastSnapshotDetected;

#if UNITY_XR_HANDS
        private XRHandSubsystem _handSubsystem;
#endif

        public struct HandGestureSnapshot
        {
            public bool HandDetected;
            public string Gesture;
            public Vector3 Palm;
            public Vector3 IndexTip;
            public Vector3 IndexIntermediate;
            public float Timestamp;
        }

        void Start()
        {
#if UNITY_XR_HANDS
            var subsystems = new System.Collections.Generic.List<XRHandSubsystem>();
            SubsystemManager.GetSubsystems(subsystems);
            if (subsystems.Count > 0)
            {
                _handSubsystem = subsystems[0];
                Debug.Log($"[HandGestureSource] XR Hand subsystem found: {_handSubsystem.GetType().Name}");
            }
            else
            {
                Debug.LogWarning("[HandGestureSource] No XR Hand subsystem available — gesture detection idle");
            }
#else
            Debug.LogWarning(
                "[HandGestureSource] com.unity.xr.hands / UNITY_XR_HANDS not enabled — " +
                "gesture detection inactive. Use DebugFireBranchGesture() ContextMenu to manually trigger.");
#endif
        }

        void Update()
        {
#if UNITY_XR_HANDS
            UpdateRealHand();
#endif
        }

#if UNITY_XR_HANDS
        private void UpdateRealHand()
        {
            if (_handSubsystem == null || !_handSubsystem.running)
            {
                if (IsHandDetected) MarkHandLost();
                return;
            }

            XRHand hand = preferredHand == Handedness.Right
                ? _handSubsystem.rightHand
                : _handSubsystem.leftHand;

            if (!hand.isTracked)
            {
                if (IsHandDetected) MarkHandLost();
                return;
            }

            IsHandDetected = true;
            UpdateJointPositions(hand);
            CurrentGesture = DetectGesture(hand);
            MaybeFireSnapshot();
        }

        private void UpdateJointPositions(XRHand hand)
        {
            var xrOrigin = FindAnyObjectByType<Unity.XR.CoreUtils.XROrigin>();
            Pose originPose = xrOrigin != null
                ? new Pose(xrOrigin.transform.position, xrOrigin.transform.rotation)
                : Pose.identity;

            if (hand.GetJoint(XRHandJointID.Palm).TryGetPose(out Pose palmPose))
                PalmPosition = palmPose.GetTransformedBy(originPose).position;

            if (hand.GetJoint(XRHandJointID.IndexTip).TryGetPose(out Pose tipPose))
                IndexTipPosition = tipPose.GetTransformedBy(originPose).position;

            if (hand.GetJoint(XRHandJointID.IndexIntermediate).TryGetPose(out Pose midPose))
                IndexIntermediatePosition = midPose.GetTransformedBy(originPose).position;
        }

        /// <summary>
        /// Detection rules (entry doc §3.3 + parrot_behavior_rules §5.1):
        /// <list type="bullet">
        /// <item><c>index_finger_branch</c>: index extended + middle/ring/little
        ///   curled + index direction is roughly horizontal (|dot(dir, up)|
        ///   <= <see cref="indexHorizontalMaxAbsDotUp"/>).</item>
        /// <item><c>closed_fist</c>: ≤ 1 finger extended (kept from ParrotDev
        ///   for "shoo" semantics).</item>
        /// <item><c>none</c>: anything else.</item>
        /// </list>
        /// Thumb is intentionally ignored — natural "branch" pose can have
        /// thumb either tucked or relaxed.
        /// </summary>
        private string DetectGesture(XRHand hand)
        {
            float indexAngle = FingerCurlAngle(hand, XRHandJointID.IndexTip, XRHandJointID.IndexProximal);
            float middleAngle = FingerCurlAngle(hand, XRHandJointID.MiddleTip, XRHandJointID.MiddleProximal);
            float ringAngle = FingerCurlAngle(hand, XRHandJointID.RingTip, XRHandJointID.RingProximal);
            float littleAngle = FingerCurlAngle(hand, XRHandJointID.LittleTip, XRHandJointID.LittleProximal);

            int extendedCount = 0;
            if (indexAngle < fingerExtendedMaxAngle) extendedCount++;
            if (middleAngle < fingerExtendedMaxAngle) extendedCount++;
            if (ringAngle < fingerExtendedMaxAngle) extendedCount++;
            if (littleAngle < fingerExtendedMaxAngle) extendedCount++;

            // closed fist: nothing extended (or only thumb, which we don't count)
            if (extendedCount == 0) return GestureFist;

            // index_finger_branch: only index extended, others curled, horizontal
            bool onlyIndexExtended = indexAngle < fingerExtendedMaxAngle
                && middleAngle > fingerCurledMinAngle
                && ringAngle > fingerCurledMinAngle
                && littleAngle > fingerCurledMinAngle;

            if (onlyIndexExtended)
            {
                if (hand.GetJoint(XRHandJointID.IndexTip).TryGetPose(out Pose tipPose) &&
                    hand.GetJoint(XRHandJointID.IndexProximal).TryGetPose(out Pose proxPose))
                {
                    Vector3 indexDir = (tipPose.position - proxPose.position).normalized;
                    if (Mathf.Abs(Vector3.Dot(indexDir, Vector3.up)) <= indexHorizontalMaxAbsDotUp)
                        return GestureBranch;
                }
            }

            return GestureNone;
        }

        private static float FingerCurlAngle(XRHand hand, XRHandJointID tip, XRHandJointID proximal)
        {
            if (!hand.GetJoint(tip).TryGetPose(out Pose tipPose)) return 90f;
            if (!hand.GetJoint(proximal).TryGetPose(out Pose proxPose)) return 90f;
            if (!hand.GetJoint(XRHandJointID.Palm).TryGetPose(out Pose palmPose)) return 90f;

            Vector3 fingerDir = (tipPose.position - proxPose.position).normalized;
            Vector3 handForward = palmPose.rotation * Vector3.forward;
            return Vector3.Angle(fingerDir, handForward);
        }
#endif

        private void MarkHandLost()
        {
            IsHandDetected = false;
            CurrentGesture = GestureNone;
            FireSnapshot();
        }

        private void MaybeFireSnapshot()
        {
            bool changed = CurrentGesture != _lastSnapshotGesture
                           || IsHandDetected != _lastSnapshotDetected;
            bool intervalElapsed = (Time.time - _lastSnapshotAt) >= snapshotIntervalSeconds;
            if (changed || intervalElapsed) FireSnapshot();
        }

        private void FireSnapshot()
        {
            _lastSnapshotAt = Time.time;
            _lastSnapshotGesture = CurrentGesture;
            _lastSnapshotDetected = IsHandDetected;

            var snap = new HandGestureSnapshot
            {
                HandDetected = IsHandDetected,
                Gesture = CurrentGesture,
                Palm = PalmPosition,
                IndexTip = IndexTipPosition,
                IndexIntermediate = IndexIntermediatePosition,
                Timestamp = Time.time,
            };

            try { OnGestureSnapshot?.Invoke(snap); }
            catch (Exception ex) { Debug.LogError($"[HandGestureSource] OnGestureSnapshot subscriber threw: {ex}"); }
        }

        // ─── Editor / debug entry ────────────────────────────────────

        /// <summary>
        /// Editor smoke entry: simulate a horizontal index-finger branch in front
        /// of the parrot. Useful when <c>com.unity.xr.hands</c> isn't installed
        /// or while testing PerchOnHand without donning a head-tracked rig.
        /// </summary>
        [ContextMenu("Debug: Fire 'index_finger_branch' gesture (1m forward)")]
        public void DebugFireBranchGesture()
        {
            IsHandDetected = true;
            CurrentGesture = GestureBranch;
            Vector3 forward = transform.position + Vector3.forward * 0.5f + Vector3.right * 0.2f;
            PalmPosition = forward + Vector3.left * 0.08f;
            IndexIntermediatePosition = forward;
            IndexTipPosition = forward + Vector3.right * 0.04f;
            FireSnapshot();
        }

        [ContextMenu("Debug: Fire 'closed_fist' (release perch)")]
        public void DebugFireFistGesture()
        {
            IsHandDetected = true;
            CurrentGesture = GestureFist;
            FireSnapshot();
        }

        [ContextMenu("Debug: Hand lost")]
        public void DebugFireHandLost()
        {
            MarkHandLost();
        }
    }
}
