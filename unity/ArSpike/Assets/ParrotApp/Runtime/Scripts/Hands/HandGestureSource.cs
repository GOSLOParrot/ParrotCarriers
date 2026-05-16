using System;
using System.Collections.Generic;
using UnityEngine;

#if UNITY_XR_HANDS
using Unity.XR.CoreUtils;
using UnityEngine.XR.Hands;
#endif

namespace ParrotApp.Hands
{
    [DisallowMultipleComponent]
    public class HandGestureSource : MonoBehaviour
    {
        public const string GestureNone = "none";
        public const string GestureBranch = "index_finger_branch";
        public const string GestureFist = "closed_fist";

#if UNITY_XR_HANDS
        public enum PreferredHand { Left, Right }

        [Header("Tracking")]
        [SerializeField] private PreferredHand preferredHand = PreferredHand.Right;
#endif

        [Header("Gesture thresholds")]
        [SerializeField] private float indexStraightMaxBendDegrees = 35f;
        [SerializeField] private float curledMinBendDegrees = 55f;
        [SerializeField] private float curledDistanceRatio = 0.86f;
        [SerializeField] private float indexHorizontalMaxAbsDotUp = 0.42f;
        [SerializeField] private float minBranchConfidence = 0.55f;

        [Header("Perch pose")]
        [SerializeField] private float middleSegmentBlend = 0.5f;
        [SerializeField] private bool faceMainCameraWhenPossible = true;

        [Header("Update")]
        [SerializeField] private float snapshotIntervalSeconds = 0.05f;
        [SerializeField] private float subsystemRetryIntervalSeconds = 1f;

        public bool IsHandDetected { get; private set; }
        public string CurrentGesture { get; private set; } = GestureNone;
        public string TrackingSource { get; private set; } = "none";
        public string LastTrackingStatus { get; private set; } = "not_started";
        public Vector3 PalmPosition { get; private set; }
        public Vector3 IndexTipPosition { get; private set; }
        public Vector3 IndexIntermediatePosition { get; private set; }
        public Vector3 IndexDistalPosition { get; private set; }
        public Vector3 IndexPerchPosition { get; private set; }
        public Vector3 IndexDirection { get; private set; } = Vector3.right;
        public Vector3 PalmNormal { get; private set; } = Vector3.up;
        public HandPerchPose CurrentPerchPose { get; private set; }

        public event Action<HandGestureSnapshot> OnGestureSnapshot;

        private float _lastSnapshotAt;
        private string _lastSnapshotGesture = GestureNone;
        private bool _lastSnapshotDetected;
        private float _nextSubsystemRetryAt;

#if UNITY_XR_HANDS
        private XRHandSubsystem _handSubsystem;
        private XROrigin _xrOrigin;
#endif

        public struct HandGestureSnapshot
        {
            public bool HandDetected;
            public string Gesture;
            public Vector3 Palm;
            public Vector3 IndexTip;
            public Vector3 IndexIntermediate;
            public Vector3 IndexDistal;
            public Vector3 IndexPerch;
            public Vector3 IndexDirection;
            public HandPerchPose PerchPose;
            public string Source;
            public float Confidence;
            public float Timestamp;
        }

        private struct FingerJoints
        {
            public Vector3 Proximal;
            public Vector3 Intermediate;
            public Vector3 Tip;
            public bool Valid;
        }

        private void Start()
        {
#if UNITY_XR_HANDS
            TryBindSubsystem();
#else
            LastTrackingStatus = "xr_hands_package_not_compiled";
            Debug.LogWarning(
                "[HandGestureSource] UNITY_XR_HANDS is not defined. " +
                "Install com.unity.xr.hands and keep Assets/csc.rsp enabled for real tracking.");
#endif
        }

        private void Update()
        {
#if UNITY_XR_HANDS
            if ((_handSubsystem == null || !_handSubsystem.running) && Time.unscaledTime >= _nextSubsystemRetryAt)
            {
                _nextSubsystemRetryAt = Time.unscaledTime + Mathf.Max(0.25f, subsystemRetryIntervalSeconds);
                TryBindSubsystem();
                if (_handSubsystem == null || !_handSubsystem.running)
                    MarkHandLost("subsystem_not_running");
            }
#endif
        }

        private void OnDestroy()
        {
#if UNITY_XR_HANDS
            UnsubscribeSubsystem();
#endif
        }

#if UNITY_XR_HANDS
        private void TryBindSubsystem()
        {
            if (_handSubsystem != null && _handSubsystem.running) return;

            UnsubscribeSubsystem();
            var subsystems = new List<XRHandSubsystem>();
            SubsystemManager.GetSubsystems(subsystems);
            for (int i = 0; i < subsystems.Count; i++)
            {
                if (subsystems[i] != null && subsystems[i].running)
                {
                    _handSubsystem = subsystems[i];
                    break;
                }
            }

            if (_handSubsystem == null)
            {
                LastTrackingStatus = "no_running_xrhand_subsystem";
                return;
            }

            _xrOrigin = FindObjectOfType<XROrigin>();
            _handSubsystem.updatedHands += HandleUpdatedHands;
            _handSubsystem.trackingLost += HandleTrackingLost;
            _handSubsystem.trackingAcquired += HandleTrackingAcquired;
            LastTrackingStatus = "xrhand_subsystem_bound";
            Debug.Log($"[HandGestureSource] XRHandSubsystem bound: {_handSubsystem.GetType().Name}");
        }

        private void UnsubscribeSubsystem()
        {
            if (_handSubsystem == null) return;
            _handSubsystem.updatedHands -= HandleUpdatedHands;
            _handSubsystem.trackingLost -= HandleTrackingLost;
            _handSubsystem.trackingAcquired -= HandleTrackingAcquired;
            _handSubsystem = null;
        }

        private void HandleTrackingAcquired(XRHand hand)
        {
            LastTrackingStatus = "tracking_acquired";
        }

        private void HandleTrackingLost(XRHand hand)
        {
            MarkHandLost("tracking_lost");
        }

        private void HandleUpdatedHands(
            XRHandSubsystem subsystem,
            XRHandSubsystem.UpdateSuccessFlags updateSuccessFlags,
            XRHandSubsystem.UpdateType updateType)
        {
            if (updateType != XRHandSubsystem.UpdateType.Dynamic) return;

            XRHand hand = preferredHand == PreferredHand.Right
                ? subsystem.rightHand
                : subsystem.leftHand;

            UpdateTrackedHand(hand);
        }

        private void UpdateTrackedHand(XRHand hand)
        {
            if (!hand.isTracked)
            {
                MarkHandLost("hand_not_tracked");
                return;
            }

            if (!TryBuildPerchPose(hand, out HandPerchPose pose, out float confidence))
            {
                IsHandDetected = true;
                CurrentGesture = GestureNone;
                CurrentPerchPose = default;
                LastTrackingStatus = "required_joints_unavailable";
                MaybeFireSnapshot();
                return;
            }

            CurrentPerchPose = pose;
            PalmPosition = pose.PalmPosition;
            PalmNormal = pose.PalmNormal;
            IndexPerchPosition = pose.Position;
            IndexDirection = pose.FingerDirection;
            TrackingSource = "xr_hands";
            IsHandDetected = true;
            CurrentGesture = DetectGesture(hand, confidence);
            LastTrackingStatus = "tracking";
            MaybeFireSnapshot();
        }

        private bool TryBuildPerchPose(XRHand hand, out HandPerchPose pose, out float confidence)
        {
            pose = default;
            confidence = 0f;

            if (!TryGetWorldPose(hand, XRHandJointID.Palm, out Pose palmPose)) return false;
            if (!TryGetWorldPosition(hand, XRHandJointID.IndexProximal, out Vector3 indexProximal)) return false;
            if (!TryGetWorldPosition(hand, XRHandJointID.IndexIntermediate, out Vector3 indexIntermediate)) return false;
            if (!TryGetWorldPosition(hand, XRHandJointID.IndexTip, out Vector3 indexTip)) return false;

            bool hasDistal = TryGetWorldPosition(hand, XRHandJointID.IndexDistal, out Vector3 indexDistal);
            if (!hasDistal) indexDistal = Vector3.Lerp(indexIntermediate, indexTip, 0.45f);

            PalmPosition = palmPose.position;
            IndexTipPosition = indexTip;
            IndexIntermediatePosition = indexIntermediate;
            IndexDistalPosition = indexDistal;

            Vector3 segmentCenter = Vector3.Lerp(
                indexIntermediate,
                indexDistal,
                Mathf.Clamp01(middleSegmentBlend));

            Vector3 fingerDir = indexTip - indexProximal;
            if (fingerDir.sqrMagnitude < 0.00001f) return false;
            fingerDir.Normalize();

            Vector3 palmNormal = palmPose.rotation * Vector3.up;
            if (palmNormal.sqrMagnitude < 0.00001f) palmNormal = Vector3.up;
            palmNormal.Normalize();

            Vector3 facing = ResolveFacingDirection(segmentCenter, fingerDir);
            Vector3 up = Vector3.Cross(facing, fingerDir);
            if (up.sqrMagnitude < 0.00001f) up = Vector3.up;
            up.Normalize();
            facing = Vector3.Cross(fingerDir, up).normalized;

            float horizontalScore = 1f - Mathf.Clamp01(Mathf.Abs(Vector3.Dot(fingerDir, Vector3.up)) / Mathf.Max(0.01f, indexHorizontalMaxAbsDotUp));
            confidence = Mathf.Clamp01(0.55f + horizontalScore * 0.35f);

            pose = new HandPerchPose
            {
                IsValid = true,
                Position = segmentCenter,
                Rotation = Quaternion.LookRotation(facing, up),
                FingerDirection = fingerDir,
                PalmPosition = palmPose.position,
                PalmNormal = palmNormal,
                FacingDirection = facing,
                Confidence = confidence,
                Source = "xr_hands",
            };
            return true;
        }

        private Vector3 ResolveFacingDirection(Vector3 perchPosition, Vector3 fingerDir)
        {
            Vector3 desired = Vector3.zero;
            if (faceMainCameraWhenPossible && Camera.main != null)
                desired = Camera.main.transform.position - perchPosition;
            if (desired.sqrMagnitude < 0.0001f)
                desired = Vector3.Cross(Vector3.up, fingerDir);
            desired = Vector3.ProjectOnPlane(desired, fingerDir);
            if (desired.sqrMagnitude < 0.0001f)
                desired = Vector3.Cross(Vector3.forward, fingerDir);
            if (desired.sqrMagnitude < 0.0001f)
                desired = Vector3.forward;
            return desired.normalized;
        }

        private string DetectGesture(XRHand hand, float poseConfidence)
        {
            if (!TryGetFinger(hand, XRHandJointID.IndexProximal, XRHandJointID.IndexIntermediate, XRHandJointID.IndexTip, out FingerJoints index))
                return GestureNone;
            if (!TryGetFinger(hand, XRHandJointID.MiddleProximal, XRHandJointID.MiddleIntermediate, XRHandJointID.MiddleTip, out FingerJoints middle))
                return GestureNone;
            if (!TryGetFinger(hand, XRHandJointID.RingProximal, XRHandJointID.RingIntermediate, XRHandJointID.RingTip, out FingerJoints ring))
                return GestureNone;
            if (!TryGetFinger(hand, XRHandJointID.LittleProximal, XRHandJointID.LittleIntermediate, XRHandJointID.LittleTip, out FingerJoints little))
                return GestureNone;

            float indexBend = BendAngle(index);
            float middleBend = BendAngle(middle);
            float ringBend = BendAngle(ring);
            float littleBend = BendAngle(little);

            float indexPalmDistance = Vector3.Distance(PalmPosition, index.Tip);
            bool indexExtended = indexBend <= indexStraightMaxBendDegrees;
            bool middleCurled = IsCurled(middle, middleBend, indexPalmDistance);
            bool ringCurled = IsCurled(ring, ringBend, indexPalmDistance);
            bool littleCurled = IsCurled(little, littleBend, indexPalmDistance);
            bool horizontal = Mathf.Abs(Vector3.Dot(IndexDirection, Vector3.up)) <= indexHorizontalMaxAbsDotUp;

            if (indexExtended && middleCurled && ringCurled && littleCurled && horizontal && poseConfidence >= minBranchConfidence)
                return GestureBranch;

            int extendedCount = 0;
            if (indexExtended) extendedCount++;
            if (middleBend <= indexStraightMaxBendDegrees) extendedCount++;
            if (ringBend <= indexStraightMaxBendDegrees) extendedCount++;
            if (littleBend <= indexStraightMaxBendDegrees) extendedCount++;
            return extendedCount == 0 ? GestureFist : GestureNone;
        }

        private bool TryGetFinger(XRHand hand, XRHandJointID proximal, XRHandJointID intermediate, XRHandJointID tip, out FingerJoints joints)
        {
            joints = default;
            if (!TryGetWorldPosition(hand, proximal, out joints.Proximal)) return false;
            if (!TryGetWorldPosition(hand, intermediate, out joints.Intermediate)) return false;
            if (!TryGetWorldPosition(hand, tip, out joints.Tip)) return false;
            joints.Valid = true;
            return true;
        }

        private bool TryGetWorldPosition(XRHand hand, XRHandJointID jointId, out Vector3 position)
        {
            position = default;
            if (!TryGetWorldPose(hand, jointId, out Pose pose)) return false;
            position = pose.position;
            return true;
        }

        private bool TryGetWorldPose(XRHand hand, XRHandJointID jointId, out Pose worldPose)
        {
            worldPose = default;
            if (!hand.GetJoint(jointId).TryGetPose(out Pose localPose)) return false;
            if (_xrOrigin == null) _xrOrigin = FindObjectOfType<XROrigin>();
            if (_xrOrigin != null)
            {
                Transform origin = _xrOrigin.transform;
                worldPose = new Pose(
                    origin.TransformPoint(localPose.position),
                    origin.rotation * localPose.rotation);
                return true;
            }
            worldPose = localPose;
            return true;
        }
#endif

        private static float BendAngle(FingerJoints finger)
        {
            Vector3 a = finger.Intermediate - finger.Proximal;
            Vector3 b = finger.Tip - finger.Intermediate;
            if (a.sqrMagnitude < 0.00001f || b.sqrMagnitude < 0.00001f) return 90f;
            return Vector3.Angle(a, b);
        }

        private bool IsCurled(FingerJoints finger, float bendAngle, float indexPalmDistance)
        {
            if (bendAngle >= curledMinBendDegrees) return true;
            float distance = Vector3.Distance(PalmPosition, finger.Tip);
            return distance <= indexPalmDistance * Mathf.Clamp(curledDistanceRatio, 0.5f, 1.1f);
        }

        private void MarkHandLost(string reason)
        {
            bool changed = IsHandDetected || CurrentGesture != GestureNone;
            IsHandDetected = false;
            CurrentGesture = GestureNone;
            TrackingSource = "none";
            LastTrackingStatus = reason;
            CurrentPerchPose = default;
            if (changed) FireSnapshot();
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
                IndexDistal = IndexDistalPosition,
                IndexPerch = IndexPerchPosition,
                IndexDirection = IndexDirection,
                PerchPose = CurrentPerchPose,
                Source = TrackingSource,
                Confidence = CurrentPerchPose.Confidence,
                Timestamp = Time.time,
            };

            try { OnGestureSnapshot?.Invoke(snap); }
            catch (Exception ex) { Debug.LogError($"[HandGestureSource] OnGestureSnapshot subscriber threw: {ex}"); }
        }

        [ContextMenu("Debug: Fire 'index_finger_branch' gesture (camera space)")]
        public void DebugFireBranchGesture()
        {
            Vector3 center;
            Vector3 fingerDir;
            Vector3 facing;
            if (Camera.main != null)
            {
                Transform cam = Camera.main.transform;
                center = cam.position + cam.forward * 0.55f + cam.right * 0.12f - cam.up * 0.05f;
                fingerDir = cam.right.normalized;
                facing = Vector3.ProjectOnPlane(cam.position - center, fingerDir).normalized;
            }
            else
            {
                center = transform.position + Vector3.forward * 0.55f + Vector3.right * 0.12f;
                fingerDir = Vector3.right;
                facing = Vector3.back;
            }

            if (facing.sqrMagnitude < 0.0001f) facing = Vector3.forward;
            Vector3 up = Vector3.Cross(facing, fingerDir).normalized;
            facing = Vector3.Cross(fingerDir, up).normalized;

            IsHandDetected = true;
            CurrentGesture = GestureBranch;
            TrackingSource = "debug";
            LastTrackingStatus = "debug_branch";
            PalmPosition = center - fingerDir * 0.08f;
            IndexIntermediatePosition = center - fingerDir * 0.025f;
            IndexDistalPosition = center + fingerDir * 0.025f;
            IndexPerchPosition = center;
            IndexTipPosition = center + fingerDir * 0.075f;
            IndexDirection = fingerDir;
            PalmNormal = up;
            CurrentPerchPose = new HandPerchPose
            {
                IsValid = true,
                Position = IndexPerchPosition,
                Rotation = Quaternion.LookRotation(facing, up),
                FingerDirection = fingerDir,
                PalmPosition = PalmPosition,
                PalmNormal = PalmNormal,
                FacingDirection = facing,
                Confidence = 1f,
                Source = "debug",
            };
            FireSnapshot();
        }

        [ContextMenu("Debug: Fire 'closed_fist' (release perch)")]
        public void DebugFireFistGesture()
        {
            IsHandDetected = true;
            CurrentGesture = GestureFist;
            TrackingSource = "debug";
            LastTrackingStatus = "debug_fist";
            FireSnapshot();
        }

        [ContextMenu("Debug: Hand lost")]
        public void DebugFireHandLost()
        {
            MarkHandLost("debug_hand_lost");
        }
    }
}
