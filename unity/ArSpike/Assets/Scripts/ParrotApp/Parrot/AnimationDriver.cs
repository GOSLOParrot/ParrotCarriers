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
    /// <item>Awake 缓存翅膀驱动（默认 shoulder：left_wing / right_wing，可切回 rotation 空体）+ 腿 / 尾 / feather</item>
    /// <item>Vanilla <c>age</c> 用 <c>Time.time * 20</c> 近似 tick 轴；飞行翅膀用弧度式 cos(McAge*0.6)*osc+bias</item>
    /// <item><see cref="WingFlapAxisMode.LocalXShoulderFlap"/> 将增量映射到本地 X，减轻 GLB zRoll 枢轴落在翅中段时的穿模</item>
    /// <item>Idle：尾摆 + 翅呼吸 + McAge 时间轴</item>
    /// <item>Fly：vanilla 镜像右翼 + 尾下压</item>
    /// <item>Dance：身体 yaw/roll + 头 pitch/yaw + 双翅 cos(…)/cos(…+π) 快速反相（jukebox PARTY）</item>
    /// <item>Sit：腿弯 + 身体降低 + 翅贴身 + 尾微抬</item>
    /// <item>PerchedOnHand：呼吸 + 轻量翅/尾/腿</item>
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

        /// <summary>
        /// Minecraft Java parrot wings use <i>roll</i> (ModelPart.zRot). Blockbench-GLB
        /// import may map that to Unity local Z correctly — or not. If wings slice into
        /// the torso, try <see cref="LocalXShoulderFlap"/>.
        /// </summary>
        public enum WingFlapAxisMode
        {
            /// <summary>Match vanilla: delta applied on local Z (roll), right wing negated.</summary>
            MinecraftZRoll = 0,
            /// <summary>Unity-friendly shoulder hinge: delta on local X, right wing negated.</summary>
            LocalXShoulderFlap = 1,
        }

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
        [Tooltip("If true, drive wings from left_wing / right_wing group pivots (Blockbench shoulder). " +
                 "False = use the serialized rotation empties below (e.g. left_wing_rotation). " +
                 "When the inner empty sits mid-mesh, shoulder parenting fixes clipping.")]
        [SerializeField] private bool driveWingsFromShoulderGroup = true;
        [Tooltip("Nested rotation Empty inside left_wing group (used when driveWingsFromShoulderGroup=false)")]
        [SerializeField] private string leftWingRotNodeName = "left_wing_rotation";
        [Tooltip("Nested rotation Empty inside right_wing group (used when driveWingsFromShoulderGroup=false)")]
        [SerializeField] private string rightWingRotNodeName = "right_wing_rotation";
        [Tooltip("Parent group pivot — used when driveWingsFromShoulderGroup=true (case-insensitive FindDeep)")]
        [SerializeField] private string leftWingGroupNodeName = "left_wing";
        [SerializeField] private string rightWingGroupNodeName = "right_wing";

        [Tooltip("How cosine-driven wing angles map into Unity local Euler deltas.")]
        [SerializeField] private WingFlapAxisMode wingFlapAxisMode = WingFlapAxisMode.LocalXShoulderFlap;
        [SerializeField] private string leftLegNodeName = "left_leg";
        [SerializeField] private string rightLegNodeName = "right_leg";
        [SerializeField] private string tailNodeName = "tail";
        [SerializeField] private string featherNodeName = "feather";

        [Header("Idle — Minecraft extra bones")]
        [Tooltip("Amplitude of the idle head yaw sway (degrees). " +
                 "Minecraft ref: cos(age*0.7)*0.4 rad ≈ 23°; tuned down for subtlety.")]
        [SerializeField] private float idleHeadSwayDegrees = 14f;
        [Tooltip("Idle head sway: cos(McAge * mult) * degrees. Vanilla multiplier ≈ 0.7 (tick timeline).")]
        [SerializeField] private float idleHeadSwayMcMult = 0.7f;
        [Tooltip("Amplitude of idle tail yaw sway (degrees). " +
                 "Minecraft ref: cos(age*0.3)*0.2 rad ≈ 11.5°.")]
        [SerializeField] private float idleTailSwayDegrees = 11f;
        [Tooltip("Idle tail sway: cos(McAge * mult) * degrees. Vanilla multiplier ≈ 0.3.")]
        [SerializeField] private float idleTailSwayMcMult = 0.3f;
        [Tooltip("Wing breathing amplitude during idle/perched (degrees, z-roll).")]
        [SerializeField] private float idleWingBreathDegrees = 8f;

        [Header("Fly — vanilla ParrotEntityModel (tick timeline)")]
        [Tooltip("Vanilla flying wing: zRot = cos(age * 0.6) * osc + bias (radians). " +
                 "`age` advances ~20 per second (Minecraft ticks) — we use (Time.time * McTicksPerSecond).")]
        [SerializeField] private float flyWingBiasRad = 1.0f;
        [SerializeField] private float flyWingOscRad = 0.5f;
        [Tooltip("Multiply the cos term only (clip-safe tuning without killing mean spread).")]
        [SerializeField] private float flyWingOscillationScale = 0.55f;

        [Header("Dance — jukebox / PARTY parrot (approx vanilla pacing)")]
        [Tooltip("Root vertical bob (m) — bounce on locomotion root only.")]
        [SerializeField] private float danceRootBobMeters = 0.022f;
        [Tooltip("Body group yaw sway (degrees) — party groove.")]
        [SerializeField] private float danceBodyYawDegrees = 14f;
        [Tooltip("Body roll wobble amplitude (degrees).")]
        [SerializeField] private float danceBodyRollDegrees = 10f;
        [Tooltip("Head pitch amplitude (degrees) — PARTY is not only left-right head.")]
        [SerializeField] private float danceHeadPitchDegrees = 18f;
        [Tooltip("Head yaw amplitude (degrees).")]
        [SerializeField] private float danceHeadYawDegrees = 22f;
        [Tooltip("Party wings: left channel uses cos(age*0.8)*osc+bias (radians); right uses +π phase.")]
        [SerializeField] private float danceWingBiasRad = 0.75f;
        [SerializeField] private float danceWingOscRad = 0.55f;
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

        /// <summary>
        /// Vanilla client animation uses a tick clock (partial ticks). Good-enough Unity mapping:
        /// treat `age` in wiki/javadoc cos/sin as ~McTicksPerSecond * time(seconds).
        /// </summary>
        private const float McTicksPerSecond = 20f;

        private static float McAge => Time.time * McTicksPerSecond;

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

            // Wing drives: prefer shoulder group pivot (fixes mid-mesh rotation empties).
            if (driveWingsFromShoulderGroup)
            {
                _leftWingRotTransform  = FindDeepLog(leftWingGroupNodeName);
                _rightWingRotTransform = FindDeepLog(rightWingGroupNodeName);
            }
            else
            {
                _leftWingRotTransform  = FindDeepLog(leftWingRotNodeName);
                _rightWingRotTransform = FindDeepLog(rightWingRotNodeName);
            }
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
            float mc = McAge;

            // Position hover bob (existing baseline)
            float bob = Mathf.Sin(_stateTimer * idleBobFrequency * Mathf.PI * 2f) * idleBobAmplitude;
            transform.localPosition = _basePosition + new Vector3(0f, bob, 0f);
            transform.Rotate(Vector3.up, idleRotateSpeed * Time.deltaTime, Space.Self);

            // Tail gentle yaw sway — modding standard, see Forge javadoc / Yarn 1.20.3 (tick timeline)
            if (_tailTransform != null)
            {
                float tailSway = Mathf.Cos(mc * idleTailSwayMcMult) * idleTailSwayDegrees;
                _tailTransform.localRotation = _tailBaseRot * Quaternion.Euler(0f, tailSway, 0f);
            }

            ApplyWingBreathDeltaDegrees(Mathf.Cos(mc * 0.8f) * idleWingBreathDegrees);

            LerpLegsToBase(4f);
            ResetBodyBoneTowardBase(4f);
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

            LerpBonesToBase(3f);
            ResetBodyBoneTowardBase(3f);
        }

        private void UpdateFly()
        {
            if (!_isFlying) return;

            float mc = McAge;

            var dir = (_flyTarget - transform.position).normalized;
            transform.position = Vector3.MoveTowards(transform.position, _flyTarget, flySpeed * Time.deltaTime);

            if (dir.magnitude > 0.01f)
            {
                var targetRot = Quaternion.LookRotation(dir, Vector3.up)
                                * Quaternion.Euler(-flyTiltDegrees, 0f, 0f);
                transform.rotation = Quaternion.Slerp(transform.rotation, targetRot, 8f * Time.deltaTime);
            }

            // Flying wing — vanilla ParrotEntityModel: leftWing.zRot = cos(age*0.6)*0.5 + 1.0 (radians),
            // rightWing.zRot = -leftWing.zRot. `age` is tick-like; modding standard, see Forge javadoc / Yarn 1.20.
            float leftZRad = Mathf.Cos(mc * 0.6f) * (flyWingOscRad * flyWingOscillationScale) + flyWingBiasRad;
            ApplyWingsMirroredFromLeftZRads(leftZRad);

            if (_tailTransform != null)
            {
                _tailTransform.localRotation = Quaternion.Slerp(
                    _tailTransform.localRotation,
                    _tailBaseRot * Quaternion.Euler(-10f, 0f, 0f),
                    5f * Time.deltaTime);
            }

            LerpLegsToBase(3f);
            ResetBodyBoneTowardBase(3f);

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
            ResetBodyBoneTowardBase(3f);
        }

        /// <summary>
        /// <c>ParrotApp.Hands.PerchOnHand</c> (per-frame Lerp to IndexIntermediate
        /// joint). This driver adds breathing-scale + subtle idle bone movement so
        /// the parrot looks alive while perched and not stiff.
        /// </summary>
        private void UpdatePerchedOnHand()
        {
            float mc = McAge;

            float breath = Mathf.Sin(Time.time * perchBreathFrequency * Mathf.PI * 2f) * perchBreathAmplitude;
            transform.localScale = _baseScale * (1f + breath);

            ApplyWingBreathDeltaDegrees(Mathf.Cos(mc * 0.8f) * (idleWingBreathDegrees * 0.5f));

            if (_tailTransform != null)
            {
                float tailSway = Mathf.Cos(mc * idleTailSwayMcMult) * (idleTailSwayDegrees * 0.5f);
                _tailTransform.localRotation = _tailBaseRot * Quaternion.Euler(0f, tailSway, 0f);
            }

            if (_leftLegTransform != null && _rightLegTransform != null)
            {
                float legShift = Mathf.Sin(mc * idleTailSwayMcMult) * 4f;
                _leftLegTransform.localRotation  = _leftLegBaseRot  * Quaternion.Euler( legShift, 0f, 0f);
                _rightLegTransform.localRotation = _rightLegBaseRot * Quaternion.Euler(-legShift, 0f, 0f);
            }

            ResetBodyBoneTowardBase(4f);
        }

        /// <summary>
        /// Dance / Party parrot state.
        /// Head animation is driven here directly (parrot_behavior_rules §2.2: Dance
        /// owns its own head animation; UpdateHeadOverlay skips this state).
        /// </summary>
        private void UpdateDance()
        {
            float mc = McAge;

            // Root bounce (small) + body bone groove (jukebox PARTY reads as whole-bird sway, not only head yaw)
            float rootBob = Mathf.Sin(mc * 0.3f) * danceRootBobMeters;
            transform.localPosition = _basePosition + new Vector3(0f, rootBob, 0f);

            if (_bodyTransform != null)
            {
                float yaw = Mathf.Sin(mc * 0.5f) * danceBodyYawDegrees;
                float roll = Mathf.Sin(mc * 0.35f) * danceBodyRollDegrees;
                _bodyTransform.localRotation = _bodyBaseRot * Quaternion.Euler(0f, yaw, roll);
            }

            if (_headTransform != null)
            {
                float pitch = Mathf.Sin(mc * 0.7f) * danceHeadPitchDegrees;
                float yaw = Mathf.Sin(mc * 1.15f) * danceHeadYawDegrees;
                _headTransform.localRotation = _headBaseRot * Quaternion.Euler(pitch, yaw, 0f);
            }

            // PARTY wings: faster than mistaken "Hz" version; opposite phase between sides (jukebox feel)
            float leftRad = Mathf.Cos(mc * 0.8f) * danceWingOscRad + danceWingBiasRad;
            float rightRad = Mathf.Cos(mc * 0.8f + Mathf.PI) * danceWingOscRad + danceWingBiasRad;
            ApplyWingsIndependentZRads(leftRad, rightRad);

            if (_tailTransform != null)
            {
                float tailFan = Mathf.Cos(mc * 0.3f) * danceTailFanDegrees;
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

            ResetBodyBoneTowardBase(4f);
        }

        // ─── head overlay (every frame, regardless of body state) ────────

        private void UpdateHeadOverlay()
        {
            if (_headTransform == null) return;

            // HeadBob drives head internally when HEAD_FORWARD; skip to avoid double-write.
            if (CurrentState == BodyState.HeadBob && CurrentHeadState == HeadState.Forward) return;

            // Dance owns its own head animation (parrot_behavior_rules §2.2); skip.
            if (CurrentState == BodyState.Dance) return;

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
                    // Idle-like head yaw — cos(McAge * 0.7) style (tick timeline); modding standard, see Forge javadoc / Yarn 1.20.
                    bool idleLike = CurrentState == BodyState.Idle
                                 || CurrentState == BodyState.Sit
                                 || CurrentState == BodyState.Perch
                                 || CurrentState == BodyState.HeadBob;
                    if (idleLike)
                    {
                        float headYaw = Mathf.Cos(McAge * idleHeadSwayMcMult) * idleHeadSwayDegrees;
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

        private void ResetBodyBoneTowardBase(float speed)
        {
            if (_bodyTransform == null) return;
            _bodyTransform.localRotation = Quaternion.Slerp(
                _bodyTransform.localRotation, _bodyBaseRot, speed * Time.deltaTime);
        }

        /// <summary>
        /// Vanilla flying mirror: rightWing.z = -leftWing.z. We map signed Z radians through
        /// <see cref="wingFlapAxisMode"/> into Unity local Euler deltas on top of bind pose.
        /// </summary>
        private void ApplyWingsMirroredFromLeftZRads(float leftWingZRotRad)
        {
            if (_leftWingRotTransform == null || _rightWingRotTransform == null) return;

            float lDeg = leftWingZRotRad * Mathf.Rad2Deg;
            float rDeg = -leftWingZRotRad * Mathf.Rad2Deg;

            switch (wingFlapAxisMode)
            {
                case WingFlapAxisMode.MinecraftZRoll:
                    _leftWingRotTransform.localRotation  = _leftWingRotBaseRot  * Quaternion.Euler(0f, 0f, lDeg);
                    _rightWingRotTransform.localRotation = _rightWingRotBaseRot * Quaternion.Euler(0f, 0f, rDeg);
                    break;
                case WingFlapAxisMode.LocalXShoulderFlap:
                    // Shoulder hinge for side-mounted wings (reduces mid-mesh Z pivot clipping on GLB)
                    _leftWingRotTransform.localRotation  = _leftWingRotBaseRot  * Quaternion.Euler(lDeg, 0f, 0f);
                    _rightWingRotTransform.localRotation = _rightWingRotBaseRot * Quaternion.Euler(rDeg, 0f, 0f);
                    break;
            }
        }

        private void ApplyWingsIndependentZRads(float leftWingZRotRad, float rightWingZRotRad)
        {
            if (_leftWingRotTransform == null || _rightWingRotTransform == null) return;
            float lDeg = leftWingZRotRad * Mathf.Rad2Deg;
            float rDeg = rightWingZRotRad * Mathf.Rad2Deg;
            switch (wingFlapAxisMode)
            {
                case WingFlapAxisMode.MinecraftZRoll:
                    _leftWingRotTransform.localRotation  = _leftWingRotBaseRot  * Quaternion.Euler(0f, 0f, lDeg);
                    _rightWingRotTransform.localRotation = _rightWingRotBaseRot * Quaternion.Euler(0f, 0f, rDeg);
                    break;
                case WingFlapAxisMode.LocalXShoulderFlap:
                    _leftWingRotTransform.localRotation  = _leftWingRotBaseRot  * Quaternion.Euler(lDeg, 0f, 0f);
                    _rightWingRotTransform.localRotation = _rightWingRotBaseRot * Quaternion.Euler(rDeg, 0f, 0f);
                    break;
            }
        }

        private void ApplyWingBreathDeltaDegrees(float deltaDeg)
        {
            if (_leftWingRotTransform == null || _rightWingRotTransform == null) return;
            switch (wingFlapAxisMode)
            {
                case WingFlapAxisMode.MinecraftZRoll:
                    _leftWingRotTransform.localRotation  = _leftWingRotBaseRot  * Quaternion.Euler(0f, 0f,  deltaDeg);
                    _rightWingRotTransform.localRotation = _rightWingRotBaseRot * Quaternion.Euler(0f, 0f, -deltaDeg);
                    break;
                case WingFlapAxisMode.LocalXShoulderFlap:
                    _leftWingRotTransform.localRotation  = _leftWingRotBaseRot  * Quaternion.Euler(deltaDeg, 0f, 0f);
                    _rightWingRotTransform.localRotation = _rightWingRotBaseRot * Quaternion.Euler(-deltaDeg, 0f, 0f);
                    break;
            }
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
