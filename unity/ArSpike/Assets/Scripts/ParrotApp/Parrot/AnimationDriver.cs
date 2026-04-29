using System;
using UnityEngine;

namespace ParrotApp.Parrot
{
    /// <summary>
    /// Sprint4 Phase 4 W3.A.2 / Animation-Port — Programmatic body/head state driver for GOSLO.
    ///
    /// <b>本类是 body_state / head_state 两条 wire 字段的 sole producer</b>。
    ///
    /// W3.A.2 改造点：
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
    /// Animation-Port 改造点（Minecraft Java Parrot 风格骨骼动画）：
    /// <list type="bullet">
    /// <item>新增 <see cref="BodyState.Dance"/> / <see cref="BodyState.Sit"/></item>
    /// <item>Awake 缓存 left_wing_rotation / right_wing_rotation / left_leg /
    ///   right_leg / tail / feather Transform + 各自 _BaseRot</item>
    /// <item>Idle：尾巴慢摆 + 翅膀轻微呼吸 + 头部慢速 cos 左右摆（Minecraft 公开算法）</item>
    /// <item>Fly：双翅高频对称拍动 + 偏置展开 + 尾巴平展（Minecraft 公开算法）</item>
    /// <item>Dance：身体上下抖 + 头快摇 + 翅膀同步拍 + 尾巴扇形（Minecraft 公开算法）</item>
    /// <item>Sit：腿弯曲 + 身体下移 + 翅膀贴身 + 尾巴微抬</item>
    /// <item>PerchedOnHand：保留呼吸缩放 + 补充翅膀/尾巴/腿轻微摆动</item>
    /// </list>
    ///
    /// Wire-string 约定（与 Brain 端 _state_context.py 对齐）：
    /// <list type="bullet">
    /// <item>body_state ：lowercase / snake_case（idle / flying / perching / perched_on_hand / dancing）</item>
    /// <item>head_state ：UPPERCASE HEAD_* 前缀（HEAD_FORWARD / HEAD_LOOK_AT / HEAD_TILT / HEAD_NOD）</item>
    /// </list>
    ///
    /// Minecraft 算法来源：Forge javadoc / Yarn 1.20.3-pre1 / MCreator 教程（公开 modding 参考，
    /// 非 Mojang 私有代码）。所有 sin/cos 系数注释均标注来源。
    /// </summary>
    public class AnimationDriver : MonoBehaviour
    {
        // Dance and Sit added by Animation-Port; existing values NOT modified.
        // Wire-mapper extended below (BodyStateToWire).
        public enum BodyState { Idle, HeadBob, Fly, Perch, PerchedOnHand, Dance, Sit }
        public enum HeadState { Forward, LookAt, Tilt, Nod }

        // ─── existing inspector fields (W3.A.2 baseline — DO NOT REMOVE) ──

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

        [Header("Model nodes (head + body, W3.A.2)")]
        [SerializeField] private string headNodeName = "Head";
        [SerializeField] private string bodyNodeName = "Body";

        // ─── new inspector fields (Animation-Port — Minecraft bone nodes) ──

        [Header("Model nodes — extra bones (Animation-Port)")]
        [Tooltip("Nested rotation Empty inside left_wing group")]
        [SerializeField] private string leftWingRotNodeName = "left_wing_rotation";
        [Tooltip("Nested rotation Empty inside right_wing group")]
        [SerializeField] private string rightWingRotNodeName = "right_wing_rotation";
        [SerializeField] private string leftLegNodeName = "left_leg";
        [SerializeField] private string rightLegNodeName = "right_leg";
        [SerializeField] private string tailNodeName = "tail";
        [SerializeField] private string featherNodeName = "feather";

        [Header("Idle — Minecraft extra bones")]
        [Tooltip("Amplitude of the idle head yaw sway (degrees). " +
                 "Minecraft ref: cos(age*0.7)*0.4 rad ≈ 23°; tuned down for subtlety.")]
        [SerializeField] private float idleHeadSwayDegrees = 14f;
        [Tooltip("Idle head sway frequency (cycles/sec). Minecraft ref: 0.7.")]
        [SerializeField] private float idleHeadSwayFreq = 0.7f;
        [Tooltip("Amplitude of idle tail yaw sway (degrees). " +
                 "Minecraft ref: cos(age*0.3)*0.2 rad ≈ 11.5°.")]
        [SerializeField] private float idleTailSwayDegrees = 11f;
        [Tooltip("Idle tail sway frequency (cycles/sec). Minecraft ref: 0.3.")]
        [SerializeField] private float idleTailSwayFreq = 0.3f;
        [Tooltip("Wing breathing amplitude during idle/perched (degrees, z-roll).")]
        [SerializeField] private float idleWingBreathDegrees = 8f;

        [Header("Fly — Minecraft wing flap")]
        [Tooltip("Wing flap frequency (cycles/sec). Minecraft ref: 0.6.")]
        [SerializeField] private float flyWingFlapFreq = 0.6f;
        [Tooltip("Wing flap amplitude (degrees). Minecraft ref: 0.5 rad ≈ 28.6°.")]
        [SerializeField] private float flyWingFlapDegrees = 29f;
        [Tooltip("Wing open bias so wings stay spread during flight (degrees). " +
                 "Minecraft ref: +1.0 rad ≈ 57°.")]
        [SerializeField] private float flyWingOpenBias = 57f;

        [Header("Dance — Minecraft party parrot")]
        [Tooltip("Body vertical bob amplitude (m). Minecraft ref: sin(age*0.3)*amplitude.")]
        [SerializeField] private float danceBodyBobAmplitude = 0.04f;
        [Tooltip("Body bob frequency (cycles/sec). Minecraft ref: 0.3.")]
        [SerializeField] private float danceBodyBobFreq = 0.3f;
        [Tooltip("Head fast-shake amplitude (degrees). " +
                 "Minecraft ref: sin(age*0.6662)*0.5 rad ≈ 28.6°.")]
        [SerializeField] private float danceHeadShakeDegrees = 28f;
        [Tooltip("Head shake frequency (cycles/sec). Minecraft ref: 0.6662.")]
        [SerializeField] private float danceHeadShakeFreq = 0.6662f;
        [Tooltip("Wing flap amplitude during dance (degrees). " +
                 "Minecraft ref: cos(age*0.3)*0.4 rad ≈ 22.9°.")]
        [SerializeField] private float danceWingDegrees = 23f;
        [Tooltip("Wing flap frequency during dance (cycles/sec). Minecraft ref: 0.3.")]
        [SerializeField] private float danceWingFreq = 0.3f;
        [Tooltip("Tail fan sway amplitude during dance (degrees).")]
        [SerializeField] private float danceTailFanDegrees = 20f;

        [Header("Sit")]
        [Tooltip("Downward body offset when sitting (m).")]
        [SerializeField] private float sitBodyLower = 0.03f;
        [Tooltip("Leg bend angle when sitting (degrees, x-pitch).")]
        [SerializeField] private float sitLegBendDegrees = 30f;
        [Tooltip("Wing fold angle when sitting (degrees, z-roll; wings tuck inward).")]
        [SerializeField] private float sitWingCloseDegrees = 12f;

        // ─── public state ────────────────────────────────────────────────

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

        // ─── private runtime state ───────────────────────────────────────

        private Vector3 _flyTarget;
        private bool _isFlying;
        private Vector3 _basePosition;
        private Quaternion _baseRotation;
        private Vector3 _baseScale;
        private float _stateTimer;
        private float _headStateTimer;

        // W3.A.2 cached transforms
        private Transform _headTransform;
        private Transform _bodyTransform;
        private Quaternion _headBaseRot;
        private Quaternion _bodyBaseRot;

        // Animation-Port cached transforms (FindDeep in Awake)
        private Transform _leftWingRotTransform;
        private Transform _rightWingRotTransform;
        private Transform _leftLegTransform;
        private Transform _rightLegTransform;
        private Transform _tailTransform;
        private Transform _featherTransform;
        private Quaternion _leftWingRotBaseRot;
        private Quaternion _rightWingRotBaseRot;
        private Quaternion _leftLegBaseRot;
        private Quaternion _rightLegBaseRot;
        private Quaternion _tailBaseRot;
        private Quaternion _featherBaseRot;

        // ─── lifecycle ───────────────────────────────────────────────────

        void Awake()
        {
            _basePosition = transform.localPosition;
            _baseRotation = transform.localRotation;
            _baseScale = transform.localScale;

            // W3.A.2 nodes
            if (!string.IsNullOrEmpty(headNodeName))
                _headTransform = FindDeep(transform, headNodeName);
            if (!string.IsNullOrEmpty(bodyNodeName))
                _bodyTransform = FindDeep(transform, bodyNodeName);

            if (_headTransform != null) _headBaseRot = _headTransform.localRotation;
            if (_bodyTransform != null) _bodyBaseRot = _bodyTransform.localRotation;

            // Animation-Port nodes
            _leftWingRotTransform  = FindDeepLog(leftWingRotNodeName);
            _rightWingRotTransform = FindDeepLog(rightWingRotNodeName);
            _leftLegTransform      = FindDeepLog(leftLegNodeName);
            _rightLegTransform     = FindDeepLog(rightLegNodeName);
            _tailTransform         = FindDeepLog(tailNodeName);
            _featherTransform      = FindDeepLog(featherNodeName);

            if (_leftWingRotTransform  != null) _leftWingRotBaseRot  = _leftWingRotTransform.localRotation;
            if (_rightWingRotTransform != null) _rightWingRotBaseRot = _rightWingRotTransform.localRotation;
            if (_leftLegTransform      != null) _leftLegBaseRot      = _leftLegTransform.localRotation;
            if (_rightLegTransform     != null) _rightLegBaseRot     = _rightLegTransform.localRotation;
            if (_tailTransform         != null) _tailBaseRot         = _tailTransform.localRotation;
            if (_featherTransform      != null) _featherBaseRot      = _featherTransform.localRotation;
        }

        void Update()
        {
            _stateTimer += Time.deltaTime;
            _headStateTimer += Time.deltaTime;

            switch (CurrentState)
            {
                case BodyState.Idle:         UpdateIdle();          break;
                case BodyState.HeadBob:      UpdateHeadBob();       break;
                case BodyState.Fly:          UpdateFly();           break;
                case BodyState.Perch:        UpdatePerch();         break;
                case BodyState.PerchedOnHand: UpdatePerchedOnHand(); break;
                case BodyState.Dance:        UpdateDance();         break;
                case BodyState.Sit:          UpdateSit();           break;
            }

            UpdateHeadOverlay();
        }

        // ─── public control ──────────────────────────────────────────────

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
                case "dance":
                case "dancing": SetState(BodyState.Dance); break;
                case "sit":
                case "sitting": SetState(BodyState.Sit); break;
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

        // ─── wire mappers (DO NOT RENAME — Brain wire contract) ─────────

        public static string BodyStateToWire(BodyState s)
        {
            switch (s)
            {
                case BodyState.Idle:          return "idle";
                case BodyState.HeadBob:       return "idle"; // HeadBob is head-layer only; body wire stays idle
                case BodyState.Fly:           return "flying";
                case BodyState.Perch:         return "perching";
                case BodyState.PerchedOnHand: return "perched_on_hand";
                case BodyState.Dance:         return "dancing";
                case BodyState.Sit:           return "idle"; // Sit is a visual pose variant; wire stays idle
                default:                      return "idle";
            }
        }

        public static string HeadStateToWire(HeadState s)
        {
            switch (s)
            {
                case HeadState.Forward: return "HEAD_FORWARD";
                case HeadState.LookAt:  return "HEAD_LOOK_AT";
                case HeadState.Tilt:    return "HEAD_TILT";
                case HeadState.Nod:     return "HEAD_NOD";
                default:                return "HEAD_FORWARD";
            }
        }

        // ─── ContextMenu debug entries ───────────────────────────────────

        [ContextMenu("Debug: Play Idle")]
        private void DebugPlayIdle() => SetState(BodyState.Idle);

        [ContextMenu("Debug: Play Fly")]
        private void DebugPlayFly()
        {
            _flyTarget = transform.position + transform.forward * 2f;
            _isFlying = true;
            SetState(BodyState.Fly);
        }

        [ContextMenu("Debug: Play Dance")]
        private void DebugPlayDance() => SetState(BodyState.Dance);

        [ContextMenu("Debug: Play Sit")]
        private void DebugPlaySit() => SetState(BodyState.Sit);

        // ─── per-state body update ───────────────────────────────────────

        private void UpdateIdle()
        {
            float age = Time.time;

            // Position hover bob (existing baseline)
            float bob = Mathf.Sin(_stateTimer * idleBobFrequency * Mathf.PI * 2f) * idleBobAmplitude;
            transform.localPosition = _basePosition + new Vector3(0f, bob, 0f);
            transform.Rotate(Vector3.up, idleRotateSpeed * Time.deltaTime, Space.Self);

            // Tail gentle yaw sway: cos(age * 0.3) * 0.2 rad — modding standard, see Forge javadoc / Yarn 1.20.3
            if (_tailTransform != null)
            {
                float tailSway = Mathf.Cos(age * idleTailSwayFreq * Mathf.PI * 2f) * idleTailSwayDegrees;
                _tailTransform.localRotation = _tailBaseRot * Quaternion.Euler(0f, tailSway, 0f);
            }

            // Wing subtle breathing (z-roll, symmetric)
            ApplyWingBreath(age, idleWingBreathDegrees, perchBreathFrequency);

            // Legs return to base when idle (may have been bent in Sit)
            LerpLegsToBase(4f);
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

            // Bones return to base in HeadBob
            LerpBonesToBase(3f);
        }

        private void UpdateFly()
        {
            if (!_isFlying) return;

            float age = Time.time;

            var dir = (_flyTarget - transform.position).normalized;
            transform.position = Vector3.MoveTowards(transform.position, _flyTarget, flySpeed * Time.deltaTime);

            if (dir.magnitude > 0.01f)
            {
                var targetRot = Quaternion.LookRotation(dir, Vector3.up)
                                * Quaternion.Euler(-flyTiltDegrees, 0f, 0f);
                transform.rotation = Quaternion.Slerp(transform.rotation, targetRot, 8f * Time.deltaTime);
            }

            // Wing flap: cos(age * 0.6) * 0.5 rad + 1.0 rad bias — modding standard, see Forge javadoc / Yarn 1.20.3
            // zRot: right wing mirrors left (negative z), keeps wings spread and flapping symmetrically
            if (_leftWingRotTransform != null && _rightWingRotTransform != null)
            {
                float flapZ = Mathf.Cos(age * flyWingFlapFreq * Mathf.PI * 2f) * flyWingFlapDegrees + flyWingOpenBias;
                _leftWingRotTransform.localRotation  = _leftWingRotBaseRot  * Quaternion.Euler(0f, 0f,  flapZ);
                _rightWingRotTransform.localRotation = _rightWingRotBaseRot * Quaternion.Euler(0f, 0f, -flapZ);
            }

            // Tail flat/extended during flight (pitch slightly down)
            if (_tailTransform != null)
            {
                _tailTransform.localRotation = Quaternion.Slerp(
                    _tailTransform.localRotation,
                    _tailBaseRot * Quaternion.Euler(-10f, 0f, 0f),
                    5f * Time.deltaTime);
            }

            LerpLegsToBase(3f);

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

            LerpBonesToBase(3f);
        }

        /// <summary>
        /// PerchedOnHand body state: position is driven externally by
        /// <c>ParrotApp.Hands.PerchOnHand</c> (per-frame Lerp to IndexIntermediate
        /// joint). This driver adds breathing-scale + subtle idle bone movement so
        /// the parrot looks alive while perched and not stiff.
        /// </summary>
        private void UpdatePerchedOnHand()
        {
            float age = Time.time;

            float breath = Mathf.Sin(age * perchBreathFrequency * Mathf.PI * 2f) * perchBreathAmplitude;
            transform.localScale = _baseScale * (1f + breath);
            // Position/rotation owned by PerchOnHand — do not write transform.position here.

            // Wing idle breathing (half amplitude, perch-calming)
            ApplyWingBreath(age, idleWingBreathDegrees * 0.5f, perchBreathFrequency);

            // Tail gentle sway — half amplitude so it's subtle (modding standard, see Forge javadoc / Yarn 1.20.3)
            if (_tailTransform != null)
            {
                float tailSway = Mathf.Cos(age * idleTailSwayFreq * Mathf.PI * 2f) * (idleTailSwayDegrees * 0.5f);
                _tailTransform.localRotation = _tailBaseRot * Quaternion.Euler(0f, tailSway, 0f);
            }

            // Leg subtle weight-shift (perched birds shift weight between feet)
            if (_leftLegTransform != null && _rightLegTransform != null)
            {
                float legShift = Mathf.Sin(age * idleTailSwayFreq * Mathf.PI * 2f) * 4f;
                _leftLegTransform.localRotation  = _leftLegBaseRot  * Quaternion.Euler( legShift, 0f, 0f);
                _rightLegTransform.localRotation = _rightLegBaseRot * Quaternion.Euler(-legShift, 0f, 0f);
            }
        }

        /// <summary>
        /// Dance / Party parrot state.
        /// Head animation is driven here directly (parrot_behavior_rules §2.2: Dance
        /// owns its own head animation; UpdateHeadOverlay skips this state).
        /// </summary>
        private void UpdateDance()
        {
            float age = Time.time;

            // Body vertical bob: sin(age * 0.3) * amplitude — modding standard, see Forge javadoc / Yarn 1.20.3
            float bodyBob = Mathf.Sin(age * danceBodyBobFreq * Mathf.PI * 2f) * danceBodyBobAmplitude;
            transform.localPosition = _basePosition + new Vector3(0f, bodyBob, 0f);

            // Head fast yaw shake: sin(age * 0.6662) * 0.5 rad — modding standard, see Forge javadoc / Yarn 1.20.3
            if (_headTransform != null)
            {
                float headYaw = Mathf.Sin(age * danceHeadShakeFreq * Mathf.PI * 2f) * danceHeadShakeDegrees;
                _headTransform.localRotation = _headBaseRot * Quaternion.Euler(0f, headYaw, 0f);
            }

            // Wings synchronized flap (both up-down together): cos(age * 0.3) * 0.4 rad
            // modding standard, see Forge javadoc / Yarn 1.20.3
            if (_leftWingRotTransform != null && _rightWingRotTransform != null)
            {
                float wingZ = Mathf.Cos(age * danceWingFreq * Mathf.PI * 2f) * danceWingDegrees;
                _leftWingRotTransform.localRotation  = _leftWingRotBaseRot  * Quaternion.Euler(0f, 0f,  wingZ);
                _rightWingRotTransform.localRotation = _rightWingRotBaseRot * Quaternion.Euler(0f, 0f, -wingZ);
            }

            // Tail fan sway: cos(age * 0.3) * fan amplitude — modding standard, see Forge javadoc / Yarn 1.20.3
            if (_tailTransform != null)
            {
                float tailFan = Mathf.Cos(age * danceBodyBobFreq * Mathf.PI * 2f) * danceTailFanDegrees;
                _tailTransform.localRotation = _tailBaseRot * Quaternion.Euler(0f, tailFan, 0f);
            }

            LerpLegsToBase(3f);
        }

        private void UpdateSit()
        {
            // Body lowered — lerp to avoid snap
            transform.localPosition = Vector3.Lerp(
                transform.localPosition,
                _basePosition - new Vector3(0f, sitBodyLower, 0f),
                5f * Time.deltaTime);

            // Legs bent (x-pitch simulates knee bend)
            if (_leftLegTransform != null && _rightLegTransform != null)
            {
                var legBent = Quaternion.Euler(sitLegBendDegrees, 0f, 0f);
                _leftLegTransform.localRotation = Quaternion.Slerp(
                    _leftLegTransform.localRotation, _leftLegBaseRot * legBent, 5f * Time.deltaTime);
                _rightLegTransform.localRotation = Quaternion.Slerp(
                    _rightLegTransform.localRotation, _rightLegBaseRot * legBent, 5f * Time.deltaTime);
            }

            // Wings folded close to body (small z-roll inward)
            if (_leftWingRotTransform != null && _rightWingRotTransform != null)
            {
                _leftWingRotTransform.localRotation = Quaternion.Slerp(
                    _leftWingRotTransform.localRotation,
                    _leftWingRotBaseRot * Quaternion.Euler(0f, 0f, -sitWingCloseDegrees),
                    5f * Time.deltaTime);
                _rightWingRotTransform.localRotation = Quaternion.Slerp(
                    _rightWingRotTransform.localRotation,
                    _rightWingRotBaseRot * Quaternion.Euler(0f, 0f, sitWingCloseDegrees),
                    5f * Time.deltaTime);
            }

            // Tail slightly elevated when sitting
            if (_tailTransform != null)
            {
                _tailTransform.localRotation = Quaternion.Slerp(
                    _tailTransform.localRotation,
                    _tailBaseRot * Quaternion.Euler(-12f, 0f, 0f),
                    5f * Time.deltaTime);
            }
        }

        // ─── head overlay (every frame, regardless of body state) ────────

        private void UpdateHeadOverlay()
        {
            if (_headTransform == null) return;

            // HeadBob drives head internally when HEAD_FORWARD; skip to avoid double-write.
            if (CurrentState == BodyState.HeadBob && CurrentHeadState == HeadState.Forward) return;

            // Dance owns its own head animation (parrot_behavior_rules §2.2); skip.
            if (CurrentState == BodyState.Dance) return;

            float age = Time.time;
            Quaternion target;

            switch (CurrentHeadState)
            {
                case HeadState.Tilt:
                {
                    float wiggleRoll = Mathf.Sin(_headStateTimer * headTiltWiggleFrequency * Mathf.PI * 2f) * headTiltWiggleDegrees;
                    float wiggleYaw  = Mathf.Cos(_headStateTimer * headTiltWiggleFrequency * Mathf.PI * 2f * 0.7f) * (headTiltWiggleDegrees * 0.5f);
                    target = _headBaseRot * Quaternion.Euler(
                        headTiltPitchDegrees,
                        wiggleYaw,
                        headTiltRollDegrees + wiggleRoll);
                    break;
                }
                case HeadState.Forward:
                default:
                {
                    // Idle-like states get Minecraft idle head yaw sway:
                    // cos(age * 0.7) * amplitude — modding standard, see Forge javadoc / Yarn 1.20.3
                    bool idleLike = CurrentState == BodyState.Idle
                                 || CurrentState == BodyState.Sit
                                 || CurrentState == BodyState.Perch
                                 || CurrentState == BodyState.HeadBob;
                    if (idleLike)
                    {
                        float headYaw = Mathf.Cos(age * idleHeadSwayFreq * Mathf.PI * 2f) * idleHeadSwayDegrees;
                        target = _headBaseRot * Quaternion.Euler(0f, headYaw, 0f);
                    }
                    else
                    {
                        target = _headBaseRot;
                    }
                    break;
                }
                case HeadState.LookAt:
                case HeadState.Nod:
                    target = _headBaseRot;
                    break;
            }

            _headTransform.localRotation = Quaternion.Slerp(
                _headTransform.localRotation, target, headTransitionLerpSpeed * Time.deltaTime);
        }

        // ─── helpers ─────────────────────────────────────────────────────

        /// <summary>
        /// Symmetric wing breathing used by Idle and PerchedOnHand.
        /// Both wings do the same z-roll magnitude but mirrored (left +, right −).
        /// </summary>
        private void ApplyWingBreath(float age, float amplitudeDeg, float freqHz)
        {
            if (_leftWingRotTransform == null || _rightWingRotTransform == null) return;
            float breath = Mathf.Cos(age * freqHz * Mathf.PI * 2f) * amplitudeDeg;
            _leftWingRotTransform.localRotation  = _leftWingRotBaseRot  * Quaternion.Euler(0f, 0f,  breath);
            _rightWingRotTransform.localRotation = _rightWingRotBaseRot * Quaternion.Euler(0f, 0f, -breath);
        }

        /// <summary>Lerp legs back to base when the current state doesn't own them.</summary>
        private void LerpLegsToBase(float speed)
        {
            float t = speed * Time.deltaTime;
            if (_leftLegTransform  != null) _leftLegTransform.localRotation  = Quaternion.Slerp(_leftLegTransform.localRotation,  _leftLegBaseRot,  t);
            if (_rightLegTransform != null) _rightLegTransform.localRotation = Quaternion.Slerp(_rightLegTransform.localRotation, _rightLegBaseRot, t);
        }

        /// <summary>Lerp all extra bones (wings + legs + tail) back to base.</summary>
        private void LerpBonesToBase(float speed)
        {
            float t = speed * Time.deltaTime;
            if (_leftWingRotTransform  != null) _leftWingRotTransform.localRotation  = Quaternion.Slerp(_leftWingRotTransform.localRotation,  _leftWingRotBaseRot,  t);
            if (_rightWingRotTransform != null) _rightWingRotTransform.localRotation = Quaternion.Slerp(_rightWingRotTransform.localRotation, _rightWingRotBaseRot, t);
            if (_leftLegTransform      != null) _leftLegTransform.localRotation      = Quaternion.Slerp(_leftLegTransform.localRotation,      _leftLegBaseRot,      t);
            if (_rightLegTransform     != null) _rightLegTransform.localRotation     = Quaternion.Slerp(_rightLegTransform.localRotation,     _rightLegBaseRot,     t);
            if (_tailTransform         != null) _tailTransform.localRotation         = Quaternion.Slerp(_tailTransform.localRotation,         _tailBaseRot,         t);
        }

        private Transform FindDeepLog(string nodeName)
        {
            if (string.IsNullOrEmpty(nodeName)) return null;
            var t = FindDeep(transform, nodeName);
            if (t == null)
                Debug.LogWarning($"[AnimationDriver] Bone not found: '{nodeName}' — animation for this bone will be skipped");
            return t;
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
