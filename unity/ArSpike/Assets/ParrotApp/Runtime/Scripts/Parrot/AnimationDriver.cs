using System;
using UnityEngine;

namespace ParrotApp.Parrot
{
    /// <summary>
    /// Sprint4 Phase 4 — GOSLO.glb 程序化骨骼动画驱动器。
    ///
    /// ════════════════════════════════════════════════════════
    ///  坐标系映射（来源：gltfast v4+ 文档 + Blockbench 约定）
    /// ════════════════════════════════════════════════════════
    ///
    ///  Blockbench/glTF（右手 Y-up）：
    ///    +X = 模型正面朝向时的「右侧」
    ///    +Y = 上
    ///    +Z = 朝向观察者（屏幕方向）
    ///    模型正面 = +Z（"The front of a glTF asset faces +Z"）
    ///
    ///  gltfast v4+ 转换规则（来源：官方 Upgrade Guide）：
    ///    "the coordinate space conversion is performed by inverting the X-axis"
    ///    Blockbench +X → Unity  -X
    ///    Blockbench +Y → Unity  +Y   （不变）
    ///    Blockbench +Z → Unity  +Z   （不变，正面仍朝 Unity +Z）
    ///
    ///  GOSLO.glb 骨骼在 Unity 世界中的实际位置（X 取反后）：
    ///    Blockbench 截图显示：
    ///      left_wing_rotation  pivot ≈ (-1.5, 4.6, -0.8)  → Unity (+1.5, 4.6, -0.8)
    ///      right_wing 在 Blockbench +X 侧                  → Unity -X 侧
    ///      left_wing  在 Blockbench -X 侧（pivot负）        → Unity +X 侧
    ///
    ///  旋转轴换算（右手→左手，X 取反）：
    ///    正旋转方向从右手变为左手：
    ///      绕 Z 轴旋转：glTF +zRot（CCW from +Z）→ Unity 中等价为 -Z 旋转（CW from +Z）
    ///      绕 X 轴旋转：方向不变（X 轴本身被取反但旋转方向也随之反转，净效果不变）
    ///      绕 Y 轴旋转：方向反转
    ///
    ///  GOSLO left_wing_rotation 的 Y=-180° 问题：
    ///    该空体在 Blockbench 里旋转 Y=-180°，是通过镜像复制右翼生成左翼的常见做法。
    ///    代码绕过此问题的方法：驱动父层 left_wing GROUP（肩点），不动子 rotation 空体。
    ///
    ///  翅膀拍翅轴推导：
    ///    left_wing 父组在 Unity 坐标中位于 +X 侧。
    ///    "翅膀向上"意味着翼尖（从肩点向下悬挂）绕肩点转向 +Y。
    ///    对位于 +X 的骨骼，要让其末端向 +Y 运动，需绕 -Z 轴旋转（左手系：-Z 旋转 = +X→+Y）。
    ///    → 推荐 WingFlapAxisMode.NegZ。
    ///    如果翅膀方向相反，切换到 PosZ。
    ///    若翅膀是前后运动而不是上下，切换到 NegX/PosX。
    ///
    /// ════════════════════════════════════════════════════════
    ///  Wire-string 契约（Brain _state_context.py 对齐，不可改）：
    ///    body_state: lowercase snake_case
    ///    head_state: UPPERCASE HEAD_*
    /// ════════════════════════════════════════════════════════
    /// </summary>
    public class AnimationDriver : MonoBehaviour
    {
        // ─── 枚举 ────────────────────────────────────────────────────────

        public enum BodyState { Idle, HeadBob, Fly, Perch, PerchedOnHand, Dance, Sit, Walk }
        public enum HeadState { Forward, LookAt, Tilt, Nod }

        /// <summary>
        /// 翅膀拍翅方向轴。在 Play 模式用 "Debug: Axis Test" ContextMenu 逐一验证。
        /// 推荐先试 NegZ（理论分析：left_wing 在 Unity +X 侧，-Z 旋转令翼尖向 +Y）。
        /// </summary>
        public enum WingFlapAxisMode { PosZ = 0, NegZ = 1, PosX = 2, NegX = 3 }

        private enum MinecraftParrotPose { Flying, Standing, Sitting, Party, OnShoulder }

        private const float McRadToDeg = 57.29578f;
        private const float McPi = 3.1415927f;
        private const float McFeatherXRot = -0.2214f;
        private const float McBodyXRot = 0.4937f;
        private const float McWingXRot = -0.6981f;
        private const float McWingYRot = -3.1415927f;
        private const float McLegXRot = -0.0299f;
        private const float McTailStandingXRot = 1.015f;
        private const float McTailSittingXRot = 1.5388988f;
        private const float McWingLeftZBase = -0.0873f;
        private const float McWingRightZBase = 0.0873f;
        private const float McLegFlyingAddX = 0.6981317f;
        private const float McLegSittingAddX = 1.5707964f;
        private const float McLegPartyLeftZ = -0.34906584f;
        private const float McLegPartyRightZ = 0.34906584f;

        private const float McHeadX = 0f;
        private const float McBodyX = 0f;
        private const float McTailX = 0f;
        private const float McLeftWingX = 1.5f;
        private const float McRightWingX = -1.5f;

        private const float McHeadY = 15.69f;
        private const float McBodyY = 16.5f;
        private const float McTailY = 21.07f;
        private const float McWingY = 16.94f;
        private const float McLegY = 22f;

        // ─── Inspector：W3.A.2 baseline（不要删） ────────────────────────

        [Header("Movement")]
        [SerializeField] private float flySpeed = 2.5f;
        [SerializeField] private float flyArrivalThreshold = 0.04f;

        [Header("Breath / Perch")]
        [SerializeField] private float perchBreathAmplitude = 0.02f;
        [SerializeField] private float perchBreathFrequency = 0.6f;

        [Header("Head bob (listening)")]
        [SerializeField] private float headBobAmplitude = 0.06f;
        [SerializeField] private float headBobFrequency = 2.5f;

        [Header("Head Tilt — 疑惑表情（歪头-保持-恢复循环）")]
        [Tooltip("Roll 角度，正值向右倒（度）")]
        [SerializeField] private float headTiltRollDegrees = 28f;
        [Tooltip("Pitch 角度，正值低头（度）")]
        [SerializeField] private float headTiltPitchDegrees = 10f;
        [Tooltip("歪过去的时长（秒）")]
        [SerializeField] private float headTiltInDuration = 0.4f;
        [Tooltip("保持歪头的时长（秒）")]
        [SerializeField] private float headTiltHoldDuration = 1.8f;
        [Tooltip("恢复正头的时长（秒）")]
        [SerializeField] private float headTiltOutDuration = 0.4f;
        [Tooltip("恢复后等待再次歪头的时长（秒），0 = 不自动循环（由外部 SetHeadState 控制）")]
        [SerializeField] private float headTiltWaitDuration = 0.5f;
        [Tooltip("保持时的微摆幅度（度），模仿鸟类小幅调整颈部")]
        [SerializeField] private float headTiltMicroWiggleDegrees = 2f;
        [Tooltip("头部过渡 Lerp 速度")]
        [SerializeField] private float headTransitionLerpSpeed = 7f;

        [Header("Model nodes — head + body (W3.A.2)")]
        [SerializeField] private string headNodeName = "Head";
        [SerializeField] private string bodyNodeName = "Body";

        // ─── Inspector：Animation-Port 骨骼配置 ─────────────────────────

        [Header("Wing — 从肩点父组驱动（绕过 rotation 空体 Y=-180° 问题）")]
        [SerializeField] private bool driveWingsFromShoulderGroup = true;
        [SerializeField] private string leftWingGroupNodeName  = "left_wing";
        [SerializeField] private string rightWingGroupNodeName = "right_wing";
        [Tooltip("仅在 driveWingsFromShoulderGroup=false 时使用")]
        [SerializeField] private string leftWingRotNodeName  = "left_wing_rotation";
        [SerializeField] private string rightWingRotNodeName = "right_wing_rotation";
        [Tooltip("翅膀拍翅方向轴，用 ContextMenu Axis Test 验证。实测 NegZ 向内穿模时换成 PosZ。")]
        [SerializeField] private WingFlapAxisMode wingFlapAxisMode = WingFlapAxisMode.PosZ;

        [Header("其他骨骼节点")]
        [SerializeField] private string featherNodeName  = "feather";
        [SerializeField] private string leftLegNodeName  = "left_leg";
        [SerializeField] private string rightLegNodeName = "right_leg";
        [SerializeField] private string tailNodeName     = "tail";

        [Header("Minecraft Java 1.20.1 parrot pose")]
        [SerializeField] private bool useMinecraftJavaParrotPose = true;
        [Tooltip("Unity metres per Minecraft model pixel for animated part position offsets.")]
        [SerializeField] private float minecraftUnitScale = 0.01f;
        [Tooltip("Minecraft model X is mirrored by the glTF/Unity import path used by GOSLO.glb.")]
        [SerializeField] private bool invertMinecraftXOffsets = true;
        [Tooltip("Minecraft model Y is down; Unity local Y is up.")]
        [SerializeField] private bool invertMinecraftYOffsets = true;
        [Tooltip("GOSLO.glb bakes the wing mirror yaw into left_wing_rotation/right_wing_rotation, so the shoulder groups normally should not receive Minecraft's -PI wing yaw again.")]
        [SerializeField] private bool applyMinecraftWingYaw = false;
        [SerializeField] private float minecraftWalkLimbSwingSpeed = 6f;
        [Range(0f, 1f)]
        [SerializeField] private float minecraftWalkLimbSwingAmount = 0.65f;

        // ─── Inspector：Fly ──────────────────────────────────────────────

        [Header("Fly — 简单翅膀拍动")]
        [Tooltip("拍翅振幅（度），翅膀从收拢到展开的最大角度")]
        [SerializeField] private float flyWingAmpDegrees = 40f;
        [Tooltip("拍翅频率（Hz），2.5 ≈ 鸟类快速飞行节奏")]
        [SerializeField] private float flyWingHz = 2.5f;
        [Tooltip("飞行时 body 前倾角（度）")]
        [SerializeField] private float flyBodyTiltDegrees = 18f;
        [Tooltip("起飞加速度（m/s²），让飞行有起步感")]
        [SerializeField] private float flyAcceleration = 6f;

        // ─── Inspector：Dance ────────────────────────────────────────────

        [Header("Dance — 简单跳舞弹跳")]
        [Tooltip("弹跳幅度（m）")]
        [SerializeField] private float danceBobMeters = 0.02f;
        [Tooltip("弹跳频率（Hz）")]
        [SerializeField] private float danceBobHz = 2f;
        [Tooltip("身体左右摇摆幅度（度，Y 轴旋转）")]
        [SerializeField] private float danceBodySwayDegrees = 8f;
        [Tooltip("头部反向摇摆幅度（度，Y 轴）")]
        [SerializeField] private float danceHeadSwayDegrees = 12f;
        [Tooltip("舞蹈时翅膀展开角度（度，固定展开，不拍动）")]
        [SerializeField] private float danceWingSpreadDegrees = 22f;
        [Tooltip("尾巴扇形幅度（度）")]
        [SerializeField] private float danceTailFanDegrees = 18f;

        // ─── Inspector：PerchedOnHand / Sit ──────────────────────────────

        [Header("PerchedOnHand — 站树枝")]
        [Tooltip("翅膀收拢角度（度，向内折）")]
        [SerializeField] private float perchWingFoldDegrees = 8f;
        [Tooltip("腿弯曲角度（度，X 轴 pitch）")]
        [SerializeField] private float perchLegBendDegrees = 15f;

        [Header("Sit（坐姿变体）")]
        [SerializeField] private float sitBodyLower = 0.03f;
        [SerializeField] private float sitLegBendDegrees = 30f;
        [SerializeField] private float sitWingCloseDegrees = 10f;

        // ─── 公开状态 ────────────────────────────────────────────────────

        public BodyState CurrentState     { get; private set; } = BodyState.Idle;
        public HeadState CurrentHeadState { get; private set; } = HeadState.Forward;

        public event Action<string> OnBodyStateWireChanged;
        public event Action<string> OnHeadStateWireChanged;

        /// <summary>
        /// Sprint4 GOSLO model modularization (Step 2, 2026-05-06): when
        /// false, the per-frame sin/cos reflex behaviour (idle breath /
        /// head bob / tail sway / wing micro-flap) does not run — only
        /// explicit state transitions still apply. Set by
        /// <see cref="GosloLegacyController.ConfigureFromManifest"/> based
        /// on the manifest's <c>parrot_reflex_enabled</c> derived flag, so
        /// non-bird models with no reserved ParrotAnimation capability
        /// avoid bird-flavoured idle motion they don't have rigging for.
        /// Defaults to true — backward compat with pre-modularization
        /// scenes that do not load a manifest.
        /// </summary>
        public bool ReflexEnabled { get; set; } = true;

        // ─── 私有运行时 ──────────────────────────────────────────────────

        private Vector3    _flyTarget;
        private bool       _isFlying;
        private float      _flyCurrentSpeed;
        private Vector3    _basePosition;
        private Quaternion _baseRotation;
        private Vector3    _baseScale;
        private float      _stateTimer;
        private float      _headTiltCycleTimer;

        private Transform _headTransform;
        private Transform _bodyTransform;
        private Transform _featherTransform;
        private Transform _leftWingTransform;
        private Transform _rightWingTransform;
        private Transform _leftLegTransform;
        private Transform _rightLegTransform;
        private Transform _tailTransform;

        private Quaternion _headBaseRot;
        private Quaternion _bodyBaseRot;
        private Quaternion _featherBaseRot;
        private Quaternion _leftWingBaseRot;
        private Quaternion _rightWingBaseRot;
        private Quaternion _leftLegBaseRot;
        private Quaternion _rightLegBaseRot;
        private Quaternion _tailBaseRot;

        private Vector3 _headBasePos;
        private Vector3 _bodyBasePos;
        private Vector3 _featherBasePos;
        private Vector3 _leftWingBasePos;
        private Vector3 _rightWingBasePos;
        private Vector3 _leftLegBasePos;
        private Vector3 _rightLegBasePos;
        private Vector3 _tailBasePos;

        private float _minecraftTicks;
        private float _mcFlap;
        private float _mcFlapSpeed;
        private float _mcOldFlapSpeed;
        private float _mcOldFlap;
        private float _mcFlapping;

        // ─── Awake ───────────────────────────────────────────────────────

        void Awake()
        {
            _basePosition = transform.localPosition;
            _baseRotation = transform.localRotation;
            _baseScale    = transform.localScale;

            _headTransform = FindDeep(transform, headNodeName);
            _bodyTransform = FindDeep(transform, bodyNodeName);
            if (_headTransform != null) _headBaseRot = _headTransform.localRotation;
            if (_bodyTransform != null) _bodyBaseRot = _bodyTransform.localRotation;

            _featherTransform   = FindDeepLog(featherNodeName);
            _leftWingTransform  = FindDeepLog(driveWingsFromShoulderGroup ? leftWingGroupNodeName  : leftWingRotNodeName);
            _rightWingTransform = FindDeepLog(driveWingsFromShoulderGroup ? rightWingGroupNodeName : rightWingRotNodeName);
            _leftLegTransform   = FindDeepLog(leftLegNodeName);
            _rightLegTransform  = FindDeepLog(rightLegNodeName);
            _tailTransform      = FindDeepLog(tailNodeName);

            if (_featherTransform   != null) _featherBaseRot   = _featherTransform.localRotation;
            if (_leftWingTransform  != null) _leftWingBaseRot  = _leftWingTransform.localRotation;
            if (_rightWingTransform != null) _rightWingBaseRot = _rightWingTransform.localRotation;
            if (_leftLegTransform   != null) _leftLegBaseRot   = _leftLegTransform.localRotation;
            if (_rightLegTransform  != null) _rightLegBaseRot  = _rightLegTransform.localRotation;
            if (_tailTransform      != null) _tailBaseRot      = _tailTransform.localRotation;

            if (_headTransform      != null) _headBasePos      = _headTransform.localPosition;
            if (_bodyTransform      != null) _bodyBasePos      = _bodyTransform.localPosition;
            if (_featherTransform   != null) _featherBasePos   = _featherTransform.localPosition;
            if (_leftWingTransform  != null) _leftWingBasePos  = _leftWingTransform.localPosition;
            if (_rightWingTransform != null) _rightWingBasePos = _rightWingTransform.localPosition;
            if (_leftLegTransform   != null) _leftLegBasePos   = _leftLegTransform.localPosition;
            if (_rightLegTransform  != null) _rightLegBasePos  = _rightLegTransform.localPosition;
            if (_tailTransform      != null) _tailBasePos      = _tailTransform.localPosition;
        }

        // ─── Update ──────────────────────────────────────────────────────

        void Update()
        {
            _stateTimer += Time.deltaTime;
            UpdateMinecraftFlapModel();

            // Manifest-driven reflex gate (Step 2, 2026-05-06).
            // When disabled we still honour Fly's actual translation (it's
            // motion, not reflex) but skip all sin/cos secondary motion —
            // non-bird controllers handle their own animation via Animator
            // clip / timeline and don't want bird-flavoured idle breathing.
            if (!ReflexEnabled)
            {
                if (CurrentState == BodyState.Fly) UpdateFly();
                return;
            }

            switch (CurrentState)
            {
                case BodyState.Idle:          UpdateIdle();          break;
                case BodyState.HeadBob:       UpdateHeadBob();       break;
                case BodyState.Fly:           UpdateFly();           break;
                case BodyState.Perch:         UpdatePerch();         break;
                case BodyState.PerchedOnHand: UpdatePerchedOnHand(); break;
                case BodyState.Dance:         UpdateDance();         break;
                case BodyState.Sit:           UpdateSit();           break;
                case BodyState.Walk:          UpdateWalk();          break;
            }

            // Head overlay 和 Dance 各自管头部，Dance 跳过 overlay
            if (CurrentState != BodyState.Dance)
                UpdateHeadOverlay();
        }

        // ─── 公开控制 ────────────────────────────────────────────────────

        public void FlyTo(Vector3 target)
        {
            _flyTarget = target;
            _isFlying  = true;
            SetState(BodyState.Fly);
        }

        public void WalkOnPlane(Vector2 input, float deltaTime, float walkSpeed, float turnSpeed)
        {
            if (CurrentState == BodyState.Fly || CurrentState == BodyState.PerchedOnHand)
                return;

            Vector2 clamped = Vector2.ClampMagnitude(input, 1f);
            if (clamped.sqrMagnitude < 0.01f)
            {
                EndPlaneWalk();
                return;
            }

            if (CurrentState != BodyState.Walk)
                SetState(BodyState.Walk);

            Vector3 direction = new Vector3(clamped.x, 0f, clamped.y);
            transform.position += direction * (walkSpeed * deltaTime);
            _basePosition = transform.localPosition;

            if (direction.sqrMagnitude > 0.0001f)
            {
                transform.rotation = Quaternion.Slerp(
                    transform.rotation,
                    Quaternion.LookRotation(direction, Vector3.up),
                    turnSpeed * deltaTime);
                _baseRotation = transform.localRotation;
            }
        }

        public void EndPlaneWalk()
        {
            if (CurrentState == BodyState.Walk)
                SetState(BodyState.Idle);
        }

        public void SetState(BodyState state)
        {
            if (CurrentState == state) return;
            string oldWire = BodyStateToWire(CurrentState);
            CurrentState = state;
            _stateTimer  = 0f;

            if (state == BodyState.Fly)
            {
                _flyCurrentSpeed = 0f;
                if (CurrentHeadState != HeadState.Forward) SetHeadState(HeadState.Forward);
            }

            string newWire = BodyStateToWire(state);
            Debug.Log($"[AnimationDriver] BodyState → {state} (wire={newWire})");

            if (oldWire != newWire)
                try { OnBodyStateWireChanged?.Invoke(newWire); }
                catch (Exception ex) { Debug.LogError($"[AnimationDriver] OnBodyStateWireChanged: {ex}"); }
        }

        public void SetHeadState(HeadState state)
        {
            if (CurrentHeadState == state) return;
            string oldWire = HeadStateToWire(CurrentHeadState);
            CurrentHeadState = state;
            _headTiltCycleTimer = 0f;

            string newWire = HeadStateToWire(state);
            Debug.Log($"[AnimationDriver] HeadState → {state} (wire={newWire})");

            if (oldWire != newWire)
                try { OnHeadStateWireChanged?.Invoke(newWire); }
                catch (Exception ex) { Debug.LogError($"[AnimationDriver] OnHeadStateWireChanged: {ex}"); }
        }

        public void ApplyBodyStateString(string bodyState)
        {
            switch ((bodyState ?? "").ToLowerInvariant().Replace("-", "_"))
            {
                case "idle":            SetState(BodyState.Idle);          break;
                case "head_bob":
                case "listening":       SetState(BodyState.HeadBob);       break;
                case "fly":
                case "flying":          SetState(BodyState.Fly);           break;
                case "perch":
                case "perching":        SetState(BodyState.Perch);         break;
                case "perched_on_hand": SetState(BodyState.PerchedOnHand); break;
                case "dance":
                case "dancing":         SetState(BodyState.Dance);         break;
                case "sit":
                case "sitting":         SetState(BodyState.Sit);           break;
                case "walk":
                case "walking":         SetState(BodyState.Walk);          break;
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
                case "FORWARD":   SetHeadState(HeadState.Forward); break;
                case "HEAD_LOOK_AT":
                case "LOOK_AT":   SetHeadState(HeadState.LookAt);  break;
                case "HEAD_TILT":
                case "TILT":      SetHeadState(HeadState.Tilt);    break;
                case "HEAD_NOD":
                case "NOD":       SetHeadState(HeadState.Nod);     break;
                default:
                    Debug.LogWarning($"[AnimationDriver] Unknown head_state: '{headState}' — staying {CurrentHeadState}");
                    break;
            }
        }

        // ─── Wire mappers（不可改名，Brain wire 契约） ────────────────────

        public static string BodyStateToWire(BodyState s)
        {
            switch (s)
            {
                case BodyState.Idle:          return "idle";
                case BodyState.HeadBob:       return "idle";
                case BodyState.Fly:           return "flying";
                case BodyState.Perch:         return "perching";
                case BodyState.PerchedOnHand: return "perched_on_hand";
                case BodyState.Dance:         return "dancing";
                case BodyState.Sit:           return "idle";
                case BodyState.Walk:          return "walking";
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

        // ─── ContextMenu：状态切换 ───────────────────────────────────────

        [ContextMenu("Debug: Play Idle")]
        private void DebugPlayIdle() => SetState(BodyState.Idle);

        [ContextMenu("Debug: Play Fly")]
        private void DebugPlayFly()
        {
            // 5m 距离足够展示完整的加速→拍翅→减速循环
            _flyTarget = transform.position + transform.forward * 5f;
            _isFlying  = true;
            SetState(BodyState.Fly);
        }

        [ContextMenu("Debug: Play Dance")]
        private void DebugPlayDance() => SetState(BodyState.Dance);

        [ContextMenu("Debug: Play Sit")]
        private void DebugPlaySit() => SetState(BodyState.Sit);

        [ContextMenu("Debug: Head Tilt")]
        private void DebugHeadTilt() => SetHeadState(HeadState.Tilt);

        [ContextMenu("Debug: Head Forward")]
        private void DebugHeadForward() => SetHeadState(HeadState.Forward);

        // ─── ContextMenu：翅膀轴测试（Play 模式用） ─────────────────────

        [ContextMenu("Debug: Axis Test +Z 30°")]
        private void AxisTestPosZ() => TestWingAxis(30f, WingFlapAxisMode.PosZ);

        [ContextMenu("Debug: Axis Test -Z 30°")]
        private void AxisTestNegZ() => TestWingAxis(30f, WingFlapAxisMode.NegZ);

        [ContextMenu("Debug: Axis Test +X 30°")]
        private void AxisTestPosX() => TestWingAxis(30f, WingFlapAxisMode.PosX);

        [ContextMenu("Debug: Axis Test -X 30°")]
        private void AxisTestNegX() => TestWingAxis(30f, WingFlapAxisMode.NegX);

        [ContextMenu("Debug: Wing Reset")]
        private void WingReset()
        {
            if (_leftWingTransform  != null) _leftWingTransform.localRotation  = _leftWingBaseRot;
            if (_rightWingTransform != null) _rightWingTransform.localRotation = _rightWingBaseRot;
        }

        // ─── 各状态动画 ──────────────────────────────────────────────────

        private void UpdateIdle()
        {
            if (useMinecraftJavaParrotPose)
            {
                transform.localPosition = _basePosition;
                transform.localScale = _baseScale;
                ApplyMinecraftPose(MinecraftParrotPose.Standing, 0f, 0f, 0f, 0f);
                return;
            }

            // 仅轻微上下浮动，不旋转整体（vanilla 站立鹦鹉不转）
            float bob = Mathf.Sin(_stateTimer * Mathf.PI * 2f) * 0.012f;
            transform.localPosition = _basePosition + new Vector3(0f, bob, 0f);

            // 翅膀轻微呼吸（几乎不动）
            float breathDeg = Mathf.Sin(_stateTimer * perchBreathFrequency * Mathf.PI * 2f) * 4f;
            SetWings(breathDeg);

            // 尾巴缓慢侧摆
            if (_tailTransform != null)
            {
                float tailYaw = Mathf.Sin(_stateTimer * 0.5f * Mathf.PI * 2f) * 8f;
                _tailTransform.localRotation = _tailBaseRot * Quaternion.Euler(0f, tailYaw, 0f);
            }

            ResetBodyToBase(3f);
            LerpLegsToBase(3f);
        }

        private void UpdateHeadBob()
        {
            if (useMinecraftJavaParrotPose)
            {
                transform.localPosition = _basePosition;
                transform.localScale = _baseScale;
                ApplyMinecraftPose(MinecraftParrotPose.Standing, 0f, 0f, 0f, 0f);

                if (_headTransform != null && CurrentHeadState == HeadState.Forward)
                {
                    float nodDeg = Mathf.Sin(_stateTimer * headBobFrequency * Mathf.PI * 2f) * headBobAmplitude * 80f;
                    _headTransform.localRotation = _headBaseRot * MinecraftEuler(nodDeg * Mathf.Deg2Rad, 0f, 0f);
                }
                return;
            }

            float bob = Mathf.Sin(_stateTimer * Mathf.PI * 2f) * 0.012f;
            transform.localPosition = _basePosition + new Vector3(0f, bob, 0f);

            if (_headTransform != null && CurrentHeadState == HeadState.Forward)
            {
                float nod = Mathf.Sin(_stateTimer * headBobFrequency * Mathf.PI * 2f) * headBobAmplitude * 80f;
                _headTransform.localRotation = _headBaseRot * Quaternion.Euler(nod, 0f, 0f);
            }

            LerpBonesToBase(3f);
        }

        /// <summary>
        /// 简单飞行：
        ///   速度曲线  — 加速起飞（flyAcceleration），距目标 0.6m 内减速
        ///   翅膀公式  — (1 - cos(t)) / 2 * amp，从 0 开始平滑爬升到振幅，无负值，无起跳
        ///   body 前倾，尾巴后展
        /// </summary>
        private void UpdateFly()
        {
            if (!_isFlying)
            {
                if (useMinecraftJavaParrotPose)
                {
                    transform.localScale = _baseScale;
                    ApplyMinecraftPose(MinecraftParrotPose.Flying, 0f, 0f, 0f, 0f);
                }
                return;
            }

            float dist = Vector3.Distance(transform.position, _flyTarget);
            var   dir  = (_flyTarget - transform.position).normalized;

            // 速度曲线：线性加速 + 近终点减速
            const float decelDist = 0.6f;
            float topSpeed = dist < decelDist
                ? flySpeed * Mathf.Sqrt(Mathf.Max(0, dist / decelDist))
                : flySpeed;
            _flyCurrentSpeed = Mathf.MoveTowards(_flyCurrentSpeed, topSpeed, flyAcceleration * Time.deltaTime);

            transform.position = Vector3.MoveTowards(transform.position, _flyTarget, _flyCurrentSpeed * Time.deltaTime);

            if (dir.sqrMagnitude > 0.0001f)
            {
                var targetRot = Quaternion.LookRotation(dir, Vector3.up)
                                * Quaternion.Euler(-flyBodyTiltDegrees * 0.5f, 0f, 0f);
                transform.rotation = Quaternion.Slerp(transform.rotation, targetRot, 8f * Time.deltaTime);
            }

            // 翅膀拍动：(1 - cos) / 2 * amp
            //   t=0     → 0（无起跳）
            //   t=0.5/Hz → amp（最大展开）
            //   t=1/Hz  → 0（收拢，开始下一拍）
            //   值域 [0, amp]，翅膀永远向外，不会穿进身体
            if (useMinecraftJavaParrotPose)
            {
                transform.localScale = _baseScale;
                ApplyMinecraftPose(MinecraftParrotPose.Flying, 0f, 0f, 0f, 0f);

                if (dist < flyArrivalThreshold)
                {
                    transform.position = _flyTarget;
                    _isFlying     = false;
                    _basePosition = _flyTarget;
                    SetState(BodyState.Idle);
                    Debug.Log($"[AnimationDriver] Arrived at {_flyTarget}");
                }
                return;
            }

            float wingDeg = (1f - Mathf.Cos(_stateTimer * flyWingHz * Mathf.PI * 2f)) * 0.5f * flyWingAmpDegrees;
            SetWingsMirrored(wingDeg);

            // body 前倾
            if (_bodyTransform != null)
                _bodyTransform.localRotation = Quaternion.Slerp(
                    _bodyTransform.localRotation,
                    _bodyBaseRot * Quaternion.Euler(flyBodyTiltDegrees, 0f, 0f),
                    5f * Time.deltaTime);

            // 尾巴后展
            if (_tailTransform != null)
                _tailTransform.localRotation = Quaternion.Slerp(
                    _tailTransform.localRotation,
                    _tailBaseRot * Quaternion.Euler(-12f, 0f, 0f),
                    5f * Time.deltaTime);

            LerpLegsToBase(3f);

            if (dist < flyArrivalThreshold)
            {
                transform.position = _flyTarget;
                _isFlying     = false;
                _basePosition = _flyTarget;
                SetState(BodyState.Idle);
                Debug.Log($"[AnimationDriver] Arrived at {_flyTarget}");
            }
        }

        private void UpdatePerch()
        {
            if (useMinecraftJavaParrotPose)
            {
                transform.localScale = _baseScale;
                ApplyMinecraftPose(MinecraftParrotPose.Standing, 0f, 0f, 0f, 0f);
                return;
            }

            float breath = Mathf.Sin(_stateTimer * perchBreathFrequency * Mathf.PI * 2f) * perchBreathAmplitude;
            transform.localScale    = _baseScale * (1f + breath);
            transform.localRotation = Quaternion.Slerp(transform.localRotation, _baseRotation, 3f * Time.deltaTime);
            LerpBonesToBase(3f);
        }

        /// <summary>
        /// PerchedOnHand（站树枝/手指）：
        ///   PerchOnHand 驱动 position，本类只做：
        ///   呼吸缩放 + 翅膀收拢 + 腿弯曲 + 身体直立
        /// </summary>
        private void UpdatePerchedOnHand()
        {
            if (useMinecraftJavaParrotPose)
            {
                transform.localScale = _baseScale;
                ApplyMinecraftPose(MinecraftParrotPose.OnShoulder, 0f, 0f, 0f, 0f, true, 0f);
                return;
            }

            float t = _stateTimer;

            // 呼吸缩放
            float breath = Mathf.Sin(t * perchBreathFrequency * Mathf.PI * 2f) * perchBreathAmplitude;
            transform.localScale = _baseScale * (1f + breath);

            // 翅膀收拢（向内微折，两侧对称内收）
            SetWings(-perchWingFoldDegrees);

            // 腿弯曲（像抓住树枝）
            if (_leftLegTransform != null && _rightLegTransform != null)
            {
                var bent = Quaternion.Euler(perchLegBendDegrees, 0f, 0f);
                _leftLegTransform.localRotation  = Quaternion.Slerp(_leftLegTransform.localRotation,  _leftLegBaseRot  * bent, 5f * Time.deltaTime);
                _rightLegTransform.localRotation = Quaternion.Slerp(_rightLegTransform.localRotation, _rightLegBaseRot * bent, 5f * Time.deltaTime);
            }

            // 尾巴轻摆
            if (_tailTransform != null)
            {
                float sway = Mathf.Sin(t * 0.4f * Mathf.PI * 2f) * 6f;
                _tailTransform.localRotation = _tailBaseRot * Quaternion.Euler(0f, sway, 0f);
            }

            // 身体直立
            ResetBodyToBase(4f);
        }

        /// <summary>
        /// Dance（简单跳舞）：
        ///   身体 danceBobHz Hz 弹跳
        ///   身体左右摇 + 头部反向摇
        ///   翅膀固定展开 danceWingSpreadDegrees（不拍动）
        ///   尾巴扇摆
        /// </summary>
        private void UpdateDance()
        {
            if (useMinecraftJavaParrotPose)
            {
                transform.localPosition = _basePosition;
                transform.localScale = _baseScale;
                ApplyMinecraftPose(MinecraftParrotPose.Party, 0f, 0f, 0f, 0f);
                return;
            }

            float t = _stateTimer;
            float phase = t * danceBobHz * Mathf.PI * 2f;

            // 根节点弹跳
            float bob = Mathf.Abs(Mathf.Sin(phase)) * danceBobMeters;
            transform.localPosition = _basePosition + new Vector3(0f, bob, 0f);

            // 身体左右摇（Y 轴）
            if (_bodyTransform != null)
            {
                float bodyYaw = Mathf.Sin(phase) * danceBodySwayDegrees;
                _bodyTransform.localRotation = _bodyBaseRot * Quaternion.Euler(0f, bodyYaw, 0f);
            }

            // 头部反向摇（与身体反相）
            if (_headTransform != null)
            {
                float headYaw = -Mathf.Sin(phase) * danceHeadSwayDegrees;
                _headTransform.localRotation = _headBaseRot * Quaternion.Euler(0f, headYaw, 0f);
            }

            // 翅膀固定展开（不拍动，舞蹈感觉）
            SetWingsMirrored(danceWingSpreadDegrees);

            // 尾巴扇摆
            if (_tailTransform != null)
            {
                float fan = Mathf.Sin(phase * 0.5f) * danceTailFanDegrees;
                _tailTransform.localRotation = _tailBaseRot * Quaternion.Euler(0f, fan, 0f);
            }

            LerpLegsToBase(3f);
        }

        private void UpdateSit()
        {
            if (useMinecraftJavaParrotPose)
            {
                transform.localPosition = _basePosition;
                transform.localScale = _baseScale;
                ApplyMinecraftPose(MinecraftParrotPose.Sitting, 0f, 0f, 0f, 0f);
                return;
            }

            transform.localPosition = Vector3.Lerp(
                transform.localPosition,
                _basePosition - new Vector3(0f, sitBodyLower, 0f),
                5f * Time.deltaTime);

            if (_leftLegTransform != null && _rightLegTransform != null)
            {
                var bent = Quaternion.Euler(sitLegBendDegrees, 0f, 0f);
                _leftLegTransform.localRotation  = Quaternion.Slerp(_leftLegTransform.localRotation,  _leftLegBaseRot  * bent, 5f * Time.deltaTime);
                _rightLegTransform.localRotation = Quaternion.Slerp(_rightLegTransform.localRotation, _rightLegBaseRot * bent, 5f * Time.deltaTime);
            }

            SetWings(-sitWingCloseDegrees);

            if (_tailTransform != null)
                _tailTransform.localRotation = Quaternion.Slerp(
                    _tailTransform.localRotation,
                    _tailBaseRot * Quaternion.Euler(-12f, 0f, 0f),
                    5f * Time.deltaTime);

            ResetBodyToBase(4f);
        }

        private void UpdateWalk()
        {
            if (useMinecraftJavaParrotPose)
            {
                transform.localPosition = _basePosition;
                transform.localScale = _baseScale;
                float limbSwing = _stateTimer * minecraftWalkLimbSwingSpeed;
                ApplyMinecraftPose(MinecraftParrotPose.Standing, limbSwing, minecraftWalkLimbSwingAmount, 0f, 0f);
                return;
            }

            float phase = _stateTimer * Mathf.PI * 2.7f;
            float bob = Mathf.Abs(Mathf.Sin(phase)) * 0.018f;
            transform.localPosition = Vector3.Lerp(
                transform.localPosition,
                _basePosition + new Vector3(0f, bob, 0f),
                10f * Time.deltaTime);

            if (_bodyTransform != null)
            {
                float sway = Mathf.Sin(phase) * 4f;
                _bodyTransform.localRotation = Quaternion.Slerp(
                    _bodyTransform.localRotation,
                    _bodyBaseRot * Quaternion.Euler(0f, 0f, sway),
                    9f * Time.deltaTime);
            }

            if (_leftLegTransform != null && _rightLegTransform != null)
            {
                float step = Mathf.Sin(phase) * 18f;
                _leftLegTransform.localRotation = Quaternion.Slerp(
                    _leftLegTransform.localRotation,
                    _leftLegBaseRot * Quaternion.Euler(step, 0f, 0f),
                    12f * Time.deltaTime);
                _rightLegTransform.localRotation = Quaternion.Slerp(
                    _rightLegTransform.localRotation,
                    _rightLegBaseRot * Quaternion.Euler(-step, 0f, 0f),
                    12f * Time.deltaTime);
            }

            SetWings(-6f);

            if (_tailTransform != null)
            {
                float tail = Mathf.Sin(phase * 0.5f) * 10f;
                _tailTransform.localRotation = _tailBaseRot * Quaternion.Euler(0f, tail, 0f);
            }
        }

        // ─── Head Overlay ────────────────────────────────────────────────

        /// <summary>
        /// HEAD_TILT：歪头-保持-恢复循环（timer-driven，不是左右摇头）。
        ///   Phase 0 [0, tiltIn)           : lerp 到歪头姿势
        ///   Phase 1 [tiltIn, tiltIn+hold) : 保持，微小呼吸式摆动
        ///   Phase 2 [tiltIn+hold, end)    : lerp 回正
        ///   Phase 3 [end, end+wait)       : 复位后等待
        ///   如果 headTiltWaitDuration > 0，等待后自动重新歪头（循环）
        ///   如果 headTiltWaitDuration = 0，停在正头，等外部 SetHeadState(Tilt) 再次触发
        /// </summary>
        private void UpdateHeadOverlay()
        {
            if (_headTransform == null) return;
            if (useMinecraftJavaParrotPose && CurrentHeadState == HeadState.Forward) return;

            // HeadBob 自己驱动头部
            if (CurrentState == BodyState.HeadBob && CurrentHeadState == HeadState.Forward) return;

            Quaternion target;

            switch (CurrentHeadState)
            {
                case HeadState.Tilt:
                {
                    _headTiltCycleTimer += Time.deltaTime;

                    float tiltIn   = headTiltInDuration;
                    float hold     = headTiltHoldDuration;
                    float tiltOut  = headTiltOutDuration;
                    float wait     = headTiltWaitDuration;
                    float cycleLen = tiltIn + hold + tiltOut + wait;

                    // 在循环范围内取当前阶段时间
                    float ct = headTiltWaitDuration > 0f
                        ? _headTiltCycleTimer % cycleLen
                        : Mathf.Min(_headTiltCycleTimer, tiltIn + hold + tiltOut);

                    // 目标歪头姿势
                    var tiltTarget = _headBaseRot * Quaternion.Euler(headTiltPitchDegrees, 0f, headTiltRollDegrees);

                    if (ct < tiltIn)
                    {
                        // Phase 0: 歪过去
                        float p = ct / tiltIn;
                        target = Quaternion.Slerp(_headBaseRot, tiltTarget, p);
                    }
                    else if (ct < tiltIn + hold)
                    {
                        // Phase 1: 保持，加微小呼吸摆
                        float holdTimer = ct - tiltIn;
                        float microRoll = Mathf.Sin(holdTimer * 1.5f * Mathf.PI * 2f) * headTiltMicroWiggleDegrees;
                        target = _headBaseRot * Quaternion.Euler(headTiltPitchDegrees, 0f, headTiltRollDegrees + microRoll);
                    }
                    else if (ct < tiltIn + hold + tiltOut)
                    {
                        // Phase 2: 恢复
                        float p = (ct - tiltIn - hold) / tiltOut;
                        target = Quaternion.Slerp(tiltTarget, _headBaseRot, p);
                    }
                    else
                    {
                        // Phase 3: 等待（正头）
                        target = _headBaseRot;
                    }

                    _headTransform.localRotation = Quaternion.Slerp(
                        _headTransform.localRotation, target, headTransitionLerpSpeed * Time.deltaTime);
                    return;
                }

                case HeadState.Forward:
                default:
                {
                    // Idle 类状态加轻微 Yaw 摆动（小幅，不明显）
                    bool addSway = CurrentState == BodyState.Idle
                                || CurrentState == BodyState.Sit
                                || CurrentState == BodyState.Perch;
                    if (addSway)
                    {
                        float yaw = Mathf.Cos(_stateTimer * 0.6f * Mathf.PI * 2f) * 8f;
                        target = _headBaseRot * Quaternion.Euler(0f, yaw, 0f);
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

        // ─── 翅膀辅助 ────────────────────────────────────────────────────

        /// <summary>
        /// 对称翅膀：left = +deg，right = -deg（对折方向相反）。
        /// </summary>
        private void UpdateMinecraftFlapModel()
        {
            float tickDelta = Time.deltaTime * 20f;
            if (tickDelta <= 0f) return;

            bool airborne = CurrentState == BodyState.Fly;
            _minecraftTicks += tickDelta;
            _mcOldFlap = _mcFlap;
            _mcOldFlapSpeed = _mcFlapSpeed;

            _mcFlapSpeed += (airborne ? 4f : -1f) * 0.3f * tickDelta;
            _mcFlapSpeed = Mathf.Clamp01(_mcFlapSpeed);

            if (airborne && _mcFlapping < 1f)
                _mcFlapping = 1f;

            _mcFlapping *= Mathf.Pow(0.9f, tickDelta);
            _mcFlap += _mcFlapping * 2f * tickDelta;
        }

        private float GetMinecraftAnimationProgress()
        {
            float flap = Mathf.Lerp(_mcOldFlap, _mcFlap, 1f);
            float flapSpeedValue = Mathf.Lerp(_mcOldFlapSpeed, _mcFlapSpeed, 1f);
            return (Mathf.Sin(flap) + 1f) * flapSpeedValue;
        }

        private void ApplyMinecraftPose(
            MinecraftParrotPose pose,
            float limbSwing,
            float limbSwingAmount,
            float headYawDegrees,
            float headPitchDegrees,
            bool forceAnimationProgress = false,
            float forcedAnimationProgress = 0f)
        {
            float animationProgress = forceAnimationProgress ? forcedAnimationProgress : GetMinecraftAnimationProgress();

            PrepareMinecraftPose(pose);

            SetMinecraftRotation(_headTransform, _headBaseRot,
                headPitchDegrees * Mathf.Deg2Rad,
                headYawDegrees * Mathf.Deg2Rad,
                0f);

            SetMinecraftPartXPosition(_headTransform, _headBasePos, McHeadX, McHeadX);
            SetMinecraftPartXPosition(_bodyTransform, _bodyBasePos, McBodyX, McBodyX);
            SetMinecraftPartXPosition(_tailTransform, _tailBasePos, McTailX, McTailX);
            SetMinecraftPartXPosition(_leftWingTransform, _leftWingBasePos, McLeftWingX, McLeftWingX);
            SetMinecraftPartXPosition(_rightWingTransform, _rightWingBasePos, McRightWingX, McRightWingX);

            switch (pose)
            {
                case MinecraftParrotPose.Sitting:
                    return;

                case MinecraftParrotPose.Party:
                {
                    int tick = Mathf.FloorToInt(_minecraftTicks);
                    float x = Mathf.Cos(tick);
                    float y = Mathf.Sin(tick);

                    SetMinecraftPartPosition(_headTransform, _headBasePos, McHeadX, McHeadY, x, McHeadY + y);
                    SetMinecraftRotation(_headTransform, _headBaseRot, 0f, 0f, Mathf.Sin(tick) * 0.4f);

                    SetMinecraftPartPosition(_bodyTransform, _bodyBasePos, McBodyX, McBodyY, x, McBodyY + y);
                    SetWingMinecraftRotation(_leftWingTransform, _leftWingBaseRot, McWingXRot, McWingYRot, McWingLeftZBase - animationProgress);
                    SetMinecraftPartPosition(_leftWingTransform, _leftWingBasePos, McLeftWingX, McWingY, McLeftWingX + x, McWingY + y);
                    SetWingMinecraftRotation(_rightWingTransform, _rightWingBaseRot, McWingXRot, McWingYRot, McWingRightZBase + animationProgress);
                    SetMinecraftPartPosition(_rightWingTransform, _rightWingBasePos, McRightWingX, McWingY, McRightWingX + x, McWingY + y);
                    SetMinecraftPartPosition(_tailTransform, _tailBasePos, McTailX, McTailY, x, McTailY + y);
                    return;
                }

                case MinecraftParrotPose.Standing:
                {
                    AddMinecraftRotation(_leftLegTransform, _leftLegBaseRot,
                        McLegXRot + Mathf.Cos(limbSwing * 0.6662f) * 1.4f * limbSwingAmount,
                        0f,
                        0f);
                    AddMinecraftRotation(_rightLegTransform, _rightLegBaseRot,
                        McLegXRot + Mathf.Cos(limbSwing * 0.6662f + McPi) * 1.4f * limbSwingAmount,
                        0f,
                        0f);
                    ApplyMinecraftCommonMotion(limbSwing, limbSwingAmount, animationProgress);
                    return;
                }

                case MinecraftParrotPose.Flying:
                case MinecraftParrotPose.OnShoulder:
                default:
                    ApplyMinecraftCommonMotion(limbSwing, limbSwingAmount, animationProgress);
                    return;
            }
        }

        private void PrepareMinecraftPose(MinecraftParrotPose pose)
        {
            SetMinecraftRotation(_featherTransform, _featherBaseRot, McFeatherXRot, 0f, 0f);
            SetMinecraftRotation(_bodyTransform, _bodyBaseRot, McBodyXRot, 0f, 0f);
            if (_tailTransform != null) _tailTransform.localRotation = _tailBaseRot;
            SetWingMinecraftRotation(_leftWingTransform, _leftWingBaseRot, McWingXRot, McWingYRot, 0f);
            SetWingMinecraftRotation(_rightWingTransform, _rightWingBaseRot, McWingXRot, McWingYRot, 0f);
            SetMinecraftRotation(_leftLegTransform, _leftLegBaseRot, McLegXRot, 0f, 0f);
            SetMinecraftRotation(_rightLegTransform, _rightLegBaseRot, McLegXRot, 0f, 0f);
            SetMinecraftPartPosition(_leftLegTransform, _leftLegBasePos, 0f, McLegY, 0f, McLegY);
            SetMinecraftPartPosition(_rightLegTransform, _rightLegBasePos, 0f, McLegY, 0f, McLegY);

            switch (pose)
            {
                case MinecraftParrotPose.Flying:
                    AddMinecraftRotation(_leftLegTransform, _leftLegBaseRot, McLegXRot + McLegFlyingAddX, 0f, 0f);
                    AddMinecraftRotation(_rightLegTransform, _rightLegBaseRot, McLegXRot + McLegFlyingAddX, 0f, 0f);
                    break;

                case MinecraftParrotPose.Sitting:
                    SetMinecraftPartPosition(_headTransform, _headBasePos, McHeadX, McHeadY, McHeadX, 17.59f);
                    SetMinecraftRotation(_tailTransform, _tailBaseRot, McTailSittingXRot, 0f, 0f);
                    SetMinecraftPartPosition(_tailTransform, _tailBasePos, McTailX, McTailY, McTailX, 22.97f);
                    SetMinecraftPartPosition(_bodyTransform, _bodyBasePos, McBodyX, McBodyY, McBodyX, 18.4f);
                    SetWingMinecraftRotation(_leftWingTransform, _leftWingBaseRot, McWingXRot, McWingYRot, McWingLeftZBase);
                    SetMinecraftPartPosition(_leftWingTransform, _leftWingBasePos, McLeftWingX, McWingY, McLeftWingX, 18.84f);
                    SetWingMinecraftRotation(_rightWingTransform, _rightWingBaseRot, McWingXRot, McWingYRot, McWingRightZBase);
                    SetMinecraftPartPosition(_rightWingTransform, _rightWingBasePos, McRightWingX, McWingY, McRightWingX, 18.84f);
                    SetMinecraftPartPosition(_leftLegTransform, _leftLegBasePos, 0f, McLegY, 0f, McLegY + 1.9f);
                    SetMinecraftPartPosition(_rightLegTransform, _rightLegBasePos, 0f, McLegY, 0f, McLegY + 1.9f);
                    AddMinecraftRotation(_leftLegTransform, _leftLegBaseRot, McLegXRot + McLegSittingAddX, 0f, 0f);
                    AddMinecraftRotation(_rightLegTransform, _rightLegBaseRot, McLegXRot + McLegSittingAddX, 0f, 0f);
                    break;

                case MinecraftParrotPose.Party:
                    SetMinecraftRotation(_leftLegTransform, _leftLegBaseRot, McLegXRot, 0f, McLegPartyLeftZ);
                    SetMinecraftRotation(_rightLegTransform, _rightLegBaseRot, McLegXRot, 0f, McLegPartyRightZ);
                    break;
            }
        }

        private void ApplyMinecraftCommonMotion(float limbSwing, float limbSwingAmount, float animationProgress)
        {
            float bob = animationProgress * 0.3f;

            SetMinecraftPartPosition(_headTransform, _headBasePos, McHeadX, McHeadY, McHeadX, McHeadY + bob);
            SetMinecraftRotation(_tailTransform, _tailBaseRot,
                McTailStandingXRot + Mathf.Cos(limbSwing * 0.6662f) * 0.3f * limbSwingAmount,
                0f,
                0f);
            SetMinecraftPartPosition(_tailTransform, _tailBasePos, McTailX, McTailY, McTailX, McTailY + bob);
            SetMinecraftPartPosition(_bodyTransform, _bodyBasePos, McBodyX, McBodyY, McBodyX, McBodyY + bob);
            SetWingMinecraftRotation(_leftWingTransform, _leftWingBaseRot, McWingXRot, McWingYRot, McWingLeftZBase - animationProgress);
            SetMinecraftPartPosition(_leftWingTransform, _leftWingBasePos, McLeftWingX, McWingY, McLeftWingX, McWingY + bob);
            SetWingMinecraftRotation(_rightWingTransform, _rightWingBaseRot, McWingXRot, McWingYRot, McWingRightZBase + animationProgress);
            SetMinecraftPartPosition(_rightWingTransform, _rightWingBasePos, McRightWingX, McWingY, McRightWingX, McWingY + bob);
            SetMinecraftPartPosition(_leftLegTransform, _leftLegBasePos, 0f, McLegY, 0f, McLegY + bob);
            SetMinecraftPartPosition(_rightLegTransform, _rightLegBasePos, 0f, McLegY, 0f, McLegY + bob);
        }

        private void SetWingMinecraftRotation(Transform part, Quaternion baseRotation, float xRot, float yRot, float zRot)
        {
            SetMinecraftRotation(part, baseRotation, xRot, applyMinecraftWingYaw ? yRot : 0f, zRot);
        }

        private void AddMinecraftRotation(Transform part, Quaternion baseRotation, float xRot, float yRot, float zRot)
        {
            SetMinecraftRotation(part, baseRotation, xRot, yRot, zRot);
        }

        private void SetMinecraftRotation(Transform part, Quaternion baseRotation, float xRot, float yRot, float zRot)
        {
            if (part == null) return;
            part.localRotation = baseRotation * MinecraftEuler(xRot, yRot, zRot);
        }

        private Quaternion MinecraftEuler(float xRot, float yRot, float zRot)
        {
            return Quaternion.Euler(xRot * McRadToDeg, -yRot * McRadToDeg, -zRot * McRadToDeg);
        }

        private void SetMinecraftPartPosition(
            Transform part,
            Vector3 basePosition,
            float sourceBaseX,
            float sourceBaseY,
            float sourceX,
            float sourceY)
        {
            if (part == null) return;

            float scale = Mathf.Max(0f, minecraftUnitScale);
            float dx = (sourceX - sourceBaseX) * scale;
            float dy = (sourceY - sourceBaseY) * scale;
            if (invertMinecraftXOffsets) dx = -dx;
            if (invertMinecraftYOffsets) dy = -dy;

            part.localPosition = basePosition + new Vector3(dx, dy, 0f);
        }

        private void SetMinecraftPartXPosition(
            Transform part,
            Vector3 basePosition,
            float sourceBaseX,
            float sourceX)
        {
            if (part == null) return;

            float dx = (sourceX - sourceBaseX) * Mathf.Max(0f, minecraftUnitScale);
            if (invertMinecraftXOffsets) dx = -dx;

            Vector3 current = part.localPosition;
            part.localPosition = new Vector3(basePosition.x + dx, current.y, current.z);
        }

        private void SetWingsMirrored(float leftDeg)
        {
            if (_leftWingTransform == null || _rightWingTransform == null) return;
            _leftWingTransform.localRotation  = _leftWingBaseRot  * MakeWingDelta( leftDeg);
            _rightWingTransform.localRotation = _rightWingBaseRot * MakeWingDelta(-leftDeg);
        }

        /// <summary>
        /// 两翅同方向（用于收拢/展开对称动作，如呼吸、站立折翼）。
        /// </summary>
        private void SetWings(float deg)
        {
            if (_leftWingTransform == null || _rightWingTransform == null) return;
            _leftWingTransform.localRotation  = _leftWingBaseRot  * MakeWingDelta(deg);
            _rightWingTransform.localRotation = _rightWingBaseRot * MakeWingDelta(deg);
        }

        private Quaternion MakeWingDelta(float deg)
        {
            switch (wingFlapAxisMode)
            {
                case WingFlapAxisMode.PosZ: return Quaternion.Euler(0f, 0f,  deg);
                case WingFlapAxisMode.NegZ: return Quaternion.Euler(0f, 0f, -deg);
                case WingFlapAxisMode.PosX: return Quaternion.Euler( deg, 0f, 0f);
                case WingFlapAxisMode.NegX: return Quaternion.Euler(-deg, 0f, 0f);
                default:                    return Quaternion.Euler(0f, 0f, -deg);
            }
        }

        private void TestWingAxis(float deg, WingFlapAxisMode mode)
        {
            if (_leftWingTransform == null || _rightWingTransform == null)
            { Debug.LogWarning("[AnimationDriver] Wing transforms not found"); return; }

            Quaternion l, r;
            switch (mode)
            {
                case WingFlapAxisMode.PosZ: l = Quaternion.Euler(0f, 0f,  deg); r = Quaternion.Euler(0f, 0f, -deg); break;
                case WingFlapAxisMode.NegZ: l = Quaternion.Euler(0f, 0f, -deg); r = Quaternion.Euler(0f, 0f,  deg); break;
                case WingFlapAxisMode.PosX: l = Quaternion.Euler( deg, 0f, 0f); r = Quaternion.Euler(-deg, 0f, 0f); break;
                default:                    l = Quaternion.Euler(-deg, 0f, 0f); r = Quaternion.Euler( deg, 0f, 0f); break;
            }
            _leftWingTransform.localRotation  = _leftWingBaseRot  * l;
            _rightWingTransform.localRotation = _rightWingBaseRot * r;
            Debug.Log($"[AnimationDriver] Axis test {mode} ±{deg}° — 如果翅膀向上则此轴正确，设为 wingFlapAxisMode");
        }

        // ─── 通用辅助 ─────────────────────────────────────────────────────

        private void ResetBodyToBase(float speed)
        {
            if (_bodyTransform == null) return;
            _bodyTransform.localRotation = Quaternion.Slerp(
                _bodyTransform.localRotation, _bodyBaseRot, speed * Time.deltaTime);
        }

        private void LerpLegsToBase(float speed)
        {
            float t = speed * Time.deltaTime;
            if (_leftLegTransform  != null) _leftLegTransform.localRotation  = Quaternion.Slerp(_leftLegTransform.localRotation,  _leftLegBaseRot,  t);
            if (_rightLegTransform != null) _rightLegTransform.localRotation = Quaternion.Slerp(_rightLegTransform.localRotation, _rightLegBaseRot, t);
        }

        private void LerpBonesToBase(float speed)
        {
            float t = speed * Time.deltaTime;
            if (_leftWingTransform  != null) _leftWingTransform.localRotation  = Quaternion.Slerp(_leftWingTransform.localRotation,  _leftWingBaseRot,  t);
            if (_rightWingTransform != null) _rightWingTransform.localRotation = Quaternion.Slerp(_rightWingTransform.localRotation, _rightWingBaseRot, t);
            if (_leftLegTransform   != null) _leftLegTransform.localRotation   = Quaternion.Slerp(_leftLegTransform.localRotation,   _leftLegBaseRot,   t);
            if (_rightLegTransform  != null) _rightLegTransform.localRotation  = Quaternion.Slerp(_rightLegTransform.localRotation,  _rightLegBaseRot,  t);
            if (_tailTransform      != null) _tailTransform.localRotation      = Quaternion.Slerp(_tailTransform.localRotation,      _tailBaseRot,      t);
        }

        private Transform FindDeepLog(string name)
        {
            if (string.IsNullOrEmpty(name)) return null;
            var t = FindDeep(transform, name);
            if (t == null) Debug.LogWarning($"[AnimationDriver] Bone not found: '{name}'");
            return t;
        }

        private static Transform FindDeep(Transform root, string name)
        {
            if (string.IsNullOrEmpty(name)) return null;
            foreach (Transform c in root.GetComponentsInChildren<Transform>(true))
                if (string.Equals(c.name, name, StringComparison.OrdinalIgnoreCase))
                    return c;
            return null;
        }
    }
}
