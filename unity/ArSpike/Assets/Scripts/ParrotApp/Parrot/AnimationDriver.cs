using System;
using UnityEngine;

namespace ParrotApp.Parrot
{
    /// <summary>
    /// Sprint4 Phase 4 W3.A.2 — Programmatic body/head state driver for GOSLO.
    ///
    /// <b>本类是 body_state / head_state 两条 wire 字段的 sole producer</b>。
    /// 改造点（W3.A.2）：
    /// <list type="bullet">
    /// <item>新增 <see cref="BodyState.PerchedOnHand"/>（站在手指中段）</item>
    /// <item>新增 <see cref="HeadState"/> enum + Update 末尾每帧 lerp 头部旋转</item>
    /// <item>新增 producer events <see cref="OnBodyStateWireChanged"/> /
    ///   <see cref="OnHeadStateWireChanged"/>，由
    ///   <c>LifecycleHeartbeatPublisher</c>（A.3）订阅触发 EcpState 立即上报</item>
    /// <item><see cref="HeadState.Tilt"/> 渲染：基础 18° pitch + 12° roll，
    ///   外加 ~6° / 1.6Hz 的 sine 摆动，表达"怎么了吗？"</item>
    /// </list>
    ///
    /// Wire-string 约定（与 Brain 端 _state_context.py 对齐）：
    /// <list type="bullet">
    /// <item>body_state ：lowercase / snake_case，匹配
    ///   <c>parrot.shared.parrot_actions.ParrotBodyState.value</c>
    ///   （<c>idle / flying / perching / perched_on_hand / dancing / frozen</c>）</item>
    /// <item>head_state ：UPPERCASE 带 <c>HEAD_</c> 前缀，匹配
    ///   <c>_state_context.py:_DEFAULT_HEAD = "HEAD_FORWARD"</c>
    ///   （<c>HEAD_FORWARD / HEAD_LOOK_AT / HEAD_TILT / HEAD_NOD</c>）</item>
    /// </list>
    /// 内部 enum 名（<see cref="BodyState.Fly"/> / <see cref="HeadState.Tilt"/>）
    /// 是 Unity 风格的简称；wire 翻译走静态 mapper，不污染 Update 主循环。
    /// </summary>
    public class AnimationDriver : MonoBehaviour
    {
        public enum BodyState { Idle, HeadBob, Fly, Perch, PerchedOnHand }
        public enum HeadState { Forward, LookAt, Tilt, Nod }

        [Header("Movement")]
        [SerializeField] private float flySpeed = 2.5f;
        [SerializeField] private float flyArrivalThreshold = 0.04f;
        [SerializeField] private float flyTiltDegrees = 15f;

        [Header("Idle hover")]
        [SerializeField] private float idleBobAmplitude = 0.04f;
        [SerializeField] private float idleBobFrequency = 1.2f;
        [SerializeField] private float idleRotateSpeed = 18f;

        [Header("Head bob (listening)")]
        [SerializeField] private float headBobAmplitude = 0.06f;
        [SerializeField] private float headBobFrequency = 2.5f;

        [Header("Perch (breathing scale)")]
        [SerializeField] private float perchBreathAmplitude = 0.03f;
        [SerializeField] private float perchBreathFrequency = 0.8f;

        [Header("Head Tilt (\"怎么了吗？\" expression)")]
        [Tooltip("Base pitch when HEAD_TILT is active (degrees, +x = nod down)")]
        [SerializeField] private float headTiltPitchDegrees = 18f;
        [Tooltip("Base roll when HEAD_TILT is active (degrees, +z = roll right)")]
        [SerializeField] private float headTiltRollDegrees = 12f;
        [Tooltip("Amplitude of curiosity wiggle layered on top of base tilt (degrees)")]
        [SerializeField] private float headTiltWiggleDegrees = 6f;
        [Tooltip("Wiggle frequency (Hz) — bird-like curious head motion")]
        [SerializeField] private float headTiltWiggleFrequency = 1.6f;
        [Tooltip("Lerp speed for transitioning between head states")]
        [SerializeField] private float headTransitionLerpSpeed = 6f;

        [Header("Model nodes (by name, D6 decision)")]
        [SerializeField] private string headNodeName = "Head";
        [SerializeField] private string bodyNodeName = "Body";

        public BodyState CurrentState { get; private set; } = BodyState.Idle;
        public HeadState CurrentHeadState { get; private set; } = HeadState.Forward;

        /// <summary>
        /// Fired every time the body wire string changes (lowercase snake_case).
        /// Subscribed by <c>LifecycleHeartbeatPublisher</c> (A.3) to trigger
        /// immediate EcpState upload (entry doc §8.1 L1 "事件驱动 + 1Hz").
        /// </summary>
        public event Action<string> OnBodyStateWireChanged;

        /// <summary>
        /// Fired every time the head wire string changes (UPPERCASE HEAD_*).
        /// Same EcpState trigger contract as <see cref="OnBodyStateWireChanged"/>.
        /// </summary>
        public event Action<string> OnHeadStateWireChanged;

        private Vector3 _flyTarget;
        private bool _isFlying;
        private Vector3 _basePosition;
        private Quaternion _baseRotation;
        private Vector3 _baseScale;
        private float _stateTimer;
        private float _headStateTimer;

        private Transform _headTransform;
        private Transform _bodyTransform;
        private Quaternion _headBaseRot;
        private Quaternion _bodyBaseRot;

        void Awake()
        {
            _basePosition = transform.localPosition;
            _baseRotation = transform.localRotation;
            _baseScale = transform.localScale;

            if (!string.IsNullOrEmpty(headNodeName))
                _headTransform = FindDeep(transform, headNodeName);
            if (!string.IsNullOrEmpty(bodyNodeName))
                _bodyTransform = FindDeep(transform, bodyNodeName);

            if (_headTransform != null) _headBaseRot = _headTransform.localRotation;
            if (_bodyTransform != null) _bodyBaseRot = _bodyTransform.localRotation;
        }

        void Update()
        {
            _stateTimer += Time.deltaTime;
            _headStateTimer += Time.deltaTime;

            switch (CurrentState)
            {
                case BodyState.Idle: UpdateIdle(); break;
                case BodyState.HeadBob: UpdateHeadBob(); break;
                case BodyState.Fly: UpdateFly(); break;
                case BodyState.Perch: UpdatePerch(); break;
                case BodyState.PerchedOnHand: UpdatePerchedOnHand(); break;
            }

            UpdateHeadOverlay();
        }

        public void FlyTo(Vector3 target)
        {
            _flyTarget = target;
            _isFlying = true;
            SetState(BodyState.Fly);
        }

        public void SetState(BodyState state)
        {
            if (CurrentState == state) return;
            string oldWire = BodyStateToWire(CurrentState);
            CurrentState = state;
            _stateTimer = 0f;

            // Compatibility (parrot_behavior_rules §2.2): flying body 不允许歪头
            if (state == BodyState.Fly && CurrentHeadState != HeadState.Forward)
            {
                SetHeadState(HeadState.Forward);
            }

            string newWire = BodyStateToWire(state);
            Debug.Log($"[AnimationDriver] BodyState → {state} (wire={newWire})");

            if (oldWire != newWire)
            {
                try { OnBodyStateWireChanged?.Invoke(newWire); }
                catch (Exception ex) { Debug.LogError($"[AnimationDriver] OnBodyStateWireChanged threw: {ex}"); }
            }
        }

        public void SetHeadState(HeadState state)
        {
            if (CurrentHeadState == state) return;
            string oldWire = HeadStateToWire(CurrentHeadState);
            CurrentHeadState = state;
            _headStateTimer = 0f;

            string newWire = HeadStateToWire(state);
            Debug.Log($"[AnimationDriver] HeadState → {state} (wire={newWire})");

            if (oldWire != newWire)
            {
                try { OnHeadStateWireChanged?.Invoke(newWire); }
                catch (Exception ex) { Debug.LogError($"[AnimationDriver] OnHeadStateWireChanged threw: {ex}"); }
            }
        }

        public void ApplyBodyStateString(string bodyState)
        {
            switch ((bodyState ?? "").ToLowerInvariant().Replace("-", "_"))
            {
                case "idle": SetState(BodyState.Idle); break;
                case "head_bob":
                case "listening": SetState(BodyState.HeadBob); break;
                case "fly":
                case "flying": SetState(BodyState.Fly); break;
                case "perch":
                case "perching": SetState(BodyState.Perch); break;
                case "perched_on_hand": SetState(BodyState.PerchedOnHand); break;
                default:
                    Debug.LogWarning($"[AnimationDriver] Unknown body_state: '{bodyState}' — staying {CurrentState}");
                    break;
            }
        }

        public void ApplyHeadStateString(string headState)
        {
            switch ((headState ?? "").ToUpperInvariant().Replace("-", "_"))
            {
                case "":
                case "HEAD_FORWARD":
                case "FORWARD": SetHeadState(HeadState.Forward); break;
                case "HEAD_LOOK_AT":
                case "LOOK_AT": SetHeadState(HeadState.LookAt); break;
                case "HEAD_TILT":
                case "TILT": SetHeadState(HeadState.Tilt); break;
                case "HEAD_NOD":
                case "NOD": SetHeadState(HeadState.Nod); break;
                default:
                    Debug.LogWarning($"[AnimationDriver] Unknown head_state: '{headState}' — staying {CurrentHeadState}");
                    break;
            }
        }

        // ─── wire mappers ────────────────────────────────────────────────

        public static string BodyStateToWire(BodyState s)
        {
            switch (s)
            {
                case BodyState.Idle: return "idle";
                case BodyState.HeadBob: return "idle"; // HeadBob is a head-layer hint; body remains idle on the wire
                case BodyState.Fly: return "flying";
                case BodyState.Perch: return "perching";
                case BodyState.PerchedOnHand: return "perched_on_hand";
                default: return "idle";
            }
        }

        public static string HeadStateToWire(HeadState s)
        {
            switch (s)
            {
                case HeadState.Forward: return "HEAD_FORWARD";
                case HeadState.LookAt: return "HEAD_LOOK_AT";
                case HeadState.Tilt: return "HEAD_TILT";
                case HeadState.Nod: return "HEAD_NOD";
                default: return "HEAD_FORWARD";
            }
        }

        // ─── per-state body update ───────────────────────────────────────

        private void UpdateIdle()
        {
            float bob = Mathf.Sin(_stateTimer * idleBobFrequency * Mathf.PI * 2f) * idleBobAmplitude;
            transform.localPosition = _basePosition + new Vector3(0f, bob, 0f);
            transform.Rotate(Vector3.up, idleRotateSpeed * Time.deltaTime, Space.Self);
        }

        private void UpdateHeadBob()
        {
            float bob = Mathf.Sin(_stateTimer * idleBobFrequency * Mathf.PI * 2f) * idleBobAmplitude;
            transform.localPosition = _basePosition + new Vector3(0f, bob, 0f);

            if (_headTransform != null && CurrentHeadState == HeadState.Forward)
            {
                float nod = Mathf.Sin(_stateTimer * headBobFrequency * Mathf.PI * 2f) * headBobAmplitude * 90f;
                _headTransform.localRotation = _headBaseRot * Quaternion.Euler(nod, 0f, 0f);
            }
        }

        private void UpdateFly()
        {
            if (!_isFlying) return;

            var dir = (_flyTarget - transform.position).normalized;
            transform.position = Vector3.MoveTowards(transform.position, _flyTarget, flySpeed * Time.deltaTime);

            if (dir.magnitude > 0.01f)
            {
                var targetRot = Quaternion.LookRotation(dir, Vector3.up)
                                * Quaternion.Euler(-flyTiltDegrees, 0f, 0f);
                transform.rotation = Quaternion.Slerp(transform.rotation, targetRot, 8f * Time.deltaTime);
            }

            if (Vector3.Distance(transform.position, _flyTarget) < flyArrivalThreshold)
            {
                transform.position = _flyTarget;
                _isFlying = false;
                _basePosition = _flyTarget;
                SetState(BodyState.Idle);
                Debug.Log($"[AnimationDriver] Arrived at {_flyTarget}");
            }
        }

        private void UpdatePerch()
        {
            float breath = Mathf.Sin(_stateTimer * perchBreathFrequency * Mathf.PI * 2f) * perchBreathAmplitude;
            transform.localScale = _baseScale * (1f + breath);
            transform.localRotation = Quaternion.Slerp(transform.localRotation, _baseRotation, 3f * Time.deltaTime);
        }

        /// <summary>
        /// PerchedOnHand body state: position is driven externally by
        /// <c>ParrotApp.Hands.PerchOnHand</c> (per-frame Lerp to IndexIntermediate
        /// joint). This driver only adds the breathing-scale layer so it looks
        /// alive while perched.
        /// </summary>
        private void UpdatePerchedOnHand()
        {
            float breath = Mathf.Sin(_stateTimer * perchBreathFrequency * Mathf.PI * 2f) * perchBreathAmplitude;
            transform.localScale = _baseScale * (1f + breath);
            // Do not rewrite position/rotation — PerchOnHand owns them.
        }

        // ─── head overlay (every frame, regardless of body state) ──────

        private void UpdateHeadOverlay()
        {
            if (_headTransform == null) return;
            // HeadBob has its own head-driving inside UpdateHeadBob; do not
            // double-write when that body state is active.
            if (CurrentState == BodyState.HeadBob && CurrentHeadState == HeadState.Forward) return;

            Quaternion target;
            switch (CurrentHeadState)
            {
                case HeadState.Tilt:
                {
                    float wiggleRoll = Mathf.Sin(_headStateTimer * headTiltWiggleFrequency * Mathf.PI * 2f) * headTiltWiggleDegrees;
                    float wiggleYaw = Mathf.Cos(_headStateTimer * headTiltWiggleFrequency * Mathf.PI * 2f * 0.7f) * (headTiltWiggleDegrees * 0.5f);
                    target = _headBaseRot * Quaternion.Euler(
                        headTiltPitchDegrees,
                        wiggleYaw,
                        headTiltRollDegrees + wiggleRoll);
                    break;
                }
                case HeadState.LookAt:
                case HeadState.Nod:
                case HeadState.Forward:
                default:
                    target = _headBaseRot;
                    break;
            }

            _headTransform.localRotation = Quaternion.Slerp(
                _headTransform.localRotation, target, headTransitionLerpSpeed * Time.deltaTime);
        }

        private static Transform FindDeep(Transform root, string name)
        {
            foreach (Transform child in root.GetComponentsInChildren<Transform>(includeInactive: true))
            {
                if (string.Equals(child.name, name, StringComparison.OrdinalIgnoreCase))
                    return child;
            }
            return null;
        }
    }
}
