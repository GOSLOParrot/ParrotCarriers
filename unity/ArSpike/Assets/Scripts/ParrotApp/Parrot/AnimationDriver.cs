using System;
using UnityEngine;

namespace ParrotApp.Parrot
{
    /// <summary>
    /// Sprint4 Phase 4 — Programmatic body/head state driver for GOSLO.glb (Blockbench parrot).
    ///
    /// Animation formulas come from two verified public sources:
    ///   [A] Vanilla ParrotModel.java (Forge/Fabric javadoc + SpigotMC decompile thread):
    ///         flying: leftWing.zRot = Mth.cos(limbSwing * 0.6662f) * 0.25f  (radians, no bias)
    ///                 rightWing.zRot = -leftWing.zRot
    ///         party:  leftWing.zRot = -0.34906584f  rightWing.zRot = +0.34906584f  (fixed ±20°)
    ///                 body bounces with sin(ageInTicks * 0.6662f)
    ///   [B] Blockbench Outline from user screenshot: left_wing_rotation has rotation Y=-180,
    ///       so we drive the PARENT left_wing / right_wing shoulder group to avoid mid-mesh pivot.
    ///
    /// Wing axis mapping (GOSLO.glb → Unity via gltfast):
    ///   Use <see cref="WingFlapAxisMode"/> to select correct local axis empirically in Play mode.
    ///   Default = <see cref="WingFlapAxisMode.NegZ"/> which matches vanilla zRot after glTF import.
    ///   Use ContextMenu "Debug: Axis Test …" entries to find the correct axis quickly.
    ///
    /// Wire-string contract (Brain _state_context.py alignment) — NOT CHANGED:
    ///   body_state: lowercase snake_case  (idle / flying / perching / perched_on_hand / dancing)
    ///   head_state: UPPERCASE HEAD_*      (HEAD_FORWARD / HEAD_LOOK_AT / HEAD_TILT / HEAD_NOD)
    /// </summary>
    public class AnimationDriver : MonoBehaviour
    {
        // ─── enums ───────────────────────────────────────────────────────

        // Dance and Sit added by Animation-Port; existing values NOT modified.
        public enum BodyState { Idle, HeadBob, Fly, Perch, PerchedOnHand, Dance, Sit }
        public enum HeadState { Forward, LookAt, Tilt, Nod }

        /// <summary>
        /// Which local axis to use when applying wing-flap Euler deltas.
        /// Try each in Play mode with <c>Debug: Axis Test …</c> ContextMenus.
        /// </summary>
        public enum WingFlapAxisMode
        {
            PosZ = 0,
            NegZ = 1,
            PosX = 2,
            NegX = 3,
        }

        // ─── inspector: existing baseline (W3.A.2 — DO NOT REMOVE) ──────

        [Header("Movement")]
        [SerializeField] private float flySpeed = 2.5f;
        [SerializeField] private float flyArrivalThreshold = 0.04f;
        [SerializeField] private float flyTiltDegrees = 15f;

        [Header("Idle / Perch breathing")]
        [SerializeField] private float idleBobAmplitude = 0.04f;
        [SerializeField] private float idleBobFrequency = 1.2f;
        [SerializeField] private float perchBreathAmplitude = 0.03f;
        [SerializeField] private float perchBreathFrequency = 0.8f;

        [Header("Head bob (listening)")]
        [SerializeField] private float headBobAmplitude = 0.06f;
        [SerializeField] private float headBobFrequency = 2.5f;

        [Header("Head Tilt — confusion expression")]
        [Tooltip("+x = nod down")]
        [SerializeField] private float headTiltPitchDegrees = 18f;
        [Tooltip("+z = roll right")]
        [SerializeField] private float headTiltRollDegrees = 12f;
        [SerializeField] private float headTiltWiggleDegrees = 6f;
        [SerializeField] private float headTiltWiggleFrequency = 1.6f;
        [SerializeField] private float headTransitionLerpSpeed = 6f;

        [Header("Model nodes — head + body (W3.A.2)")]
        [SerializeField] private string headNodeName = "Head";
        [SerializeField] private string bodyNodeName = "Body";

        // ─── inspector: Animation-Port bone config ───────────────────────

        [Header("Wing bones — drive from shoulder group (recommended)")]
        [Tooltip("Drive left_wing / right_wing GROUP pivot (shoulder). Avoids the Y=-180 mid-mesh empty.")]
        [SerializeField] private bool driveWingsFromShoulderGroup = true;
        [SerializeField] private string leftWingGroupNodeName  = "left_wing";
        [SerializeField] private string rightWingGroupNodeName = "right_wing";
        [Tooltip("Only used when driveWingsFromShoulderGroup = false")]
        [SerializeField] private string leftWingRotNodeName  = "left_wing_rotation";
        [SerializeField] private string rightWingRotNodeName = "right_wing_rotation";
        [Tooltip("Local axis for wing delta. Use 'Debug: Axis Test' ContextMenus to find the right one.")]
        [SerializeField] private WingFlapAxisMode wingFlapAxisMode = WingFlapAxisMode.NegZ;

        [Header("Other bones")]
        [SerializeField] private string leftLegNodeName  = "left_leg";
        [SerializeField] private string rightLegNodeName = "right_leg";
        [SerializeField] private string tailNodeName     = "tail";
        [SerializeField] private string featherNodeName  = "feather";

        // ─── inspector: idle bone animation ─────────────────────────────

        [Header("Idle — vanilla tail + head sway")]
        [Tooltip("Head yaw sway amplitude (deg). Vanilla: cos(age*0.7)*0.4 rad ≈ 23°; tuned down.")]
        [SerializeField] private float idleHeadSwayDegrees = 12f;
        [Tooltip("Tail yaw sway amplitude (deg). Vanilla: cos(age*0.3)*0.2 rad ≈ 11.5°.")]
        [SerializeField] private float idleTailSwayDegrees = 11f;
        [Tooltip("Wing closed-position breath amplitude (deg, tiny).")]
        [SerializeField] private float idleWingBreathDegrees = 5f;

        // ─── inspector: fly wing (vanilla-correct) ───────────────────────

        [Header("Fly wing — vanilla ParrotModel formula (source A)")]
        [Tooltip("Vanilla: cos(limbSwing*0.6662)*0.25 rad. Amplitude = 0.25 rad ≈ 14.3°. NO bias.")]
        [SerializeField] private float flyWingAmpRad = 0.25f;
        [Tooltip("Angular frequency multiplier on McAge. Vanilla uses ~6.662 rad/s (= 0.6662 * ~10 limbSwing rate).")]
        [SerializeField] private float flyWingFreqMult = 6.662f;

        // ─── inspector: party / dance ────────────────────────────────────

        [Header("Dance — vanilla PARTY parrot (source A)")]
        [Tooltip("Wings held fixed at this spread (radians). Vanilla: ±0.34906584 rad ≈ ±20°.")]
        [SerializeField] private float danceWingSpreadRad = 0.349f;
        [Tooltip("Body vertical bounce amplitude (m).")]
        [SerializeField] private float danceBodyBobMeters = 0.022f;
        [Tooltip("Body bounce angular frequency. Vanilla ageInTicks * 0.6662 → ~13 rad/s at 20 ticks/s.")]
        [SerializeField] private float danceBodyBobFreqMult = 13.324f;
        [Tooltip("Head bob amplitude during party (degrees, pitch).")]
        [SerializeField] private float danceHeadBobDegrees = 12f;
        [Tooltip("Tail fan max angle during party (degrees).")]
        [SerializeField] private float danceTailFanDegrees = 18f;

        // ─── inspector: sit ──────────────────────────────────────────────

        [Header("Sit")]
        [SerializeField] private float sitBodyLower = 0.03f;
        [SerializeField] private float sitLegBendDegrees = 30f;
        [SerializeField] private float sitWingCloseDegrees = 10f;

        // ─── public state ────────────────────────────────────────────────

        public BodyState CurrentState { get; private set; } = BodyState.Idle;
        public HeadState CurrentHeadState { get; private set; } = HeadState.Forward;

        /// <summary>Wire event for body state change (lowercase). Subscribed by LifecycleHeartbeatPublisher (A.3).</summary>
        public event Action<string> OnBodyStateWireChanged;
        /// <summary>Wire event for head state change (UPPERCASE HEAD_*). Same EcpState trigger.</summary>
        public event Action<string> OnHeadStateWireChanged;

        // ─── runtime state ───────────────────────────────────────────────

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

        private Transform _leftWingTransform;
        private Transform _rightWingTransform;
        private Transform _leftLegTransform;
        private Transform _rightLegTransform;
        private Transform _tailTransform;
        private Transform _featherTransform;
        private Quaternion _leftWingBaseRot;
        private Quaternion _rightWingBaseRot;
        private Quaternion _leftLegBaseRot;
        private Quaternion _rightLegBaseRot;
        private Quaternion _tailBaseRot;
        private Quaternion _featherBaseRot;

        // ─── tick timeline ───────────────────────────────────────────────

        /// <summary>Vanilla Minecraft age approximation: ~20 ticks per second.</summary>
        private const float McTicksPerSec = 20f;
        private static float McAge => Time.time * McTicksPerSec;

        // ─── lifecycle ───────────────────────────────────────────────────

        void Awake()
        {
            _basePosition = transform.localPosition;
            _baseRotation = transform.localRotation;
            _baseScale    = transform.localScale;

            _headTransform = FindDeep(transform, headNodeName);
            _bodyTransform = FindDeep(transform, bodyNodeName);
            if (_headTransform != null) _headBaseRot = _headTransform.localRotation;
            if (_bodyTransform != null) _bodyBaseRot = _bodyTransform.localRotation;

            // Wing pivot: prefer shoulder group over mid-mesh rotation empty.
            if (driveWingsFromShoulderGroup)
            {
                _leftWingTransform  = FindDeepLog(leftWingGroupNodeName);
                _rightWingTransform = FindDeepLog(rightWingGroupNodeName);
            }
            else
            {
                _leftWingTransform  = FindDeepLog(leftWingRotNodeName);
                _rightWingTransform = FindDeepLog(rightWingRotNodeName);
            }

            _leftLegTransform  = FindDeepLog(leftLegNodeName);
            _rightLegTransform = FindDeepLog(rightLegNodeName);
            _tailTransform     = FindDeepLog(tailNodeName);
            _featherTransform  = FindDeepLog(featherNodeName);

            if (_leftWingTransform  != null) _leftWingBaseRot  = _leftWingTransform.localRotation;
            if (_rightWingTransform != null) _rightWingBaseRot = _rightWingTransform.localRotation;
            if (_leftLegTransform   != null) _leftLegBaseRot   = _leftLegTransform.localRotation;
            if (_rightLegTransform  != null) _rightLegBaseRot  = _rightLegTransform.localRotation;
            if (_tailTransform      != null) _tailBaseRot      = _tailTransform.localRotation;
            if (_featherTransform   != null) _featherBaseRot   = _featherTransform.localRotation;
        }

        void Update()
        {
            _stateTimer     += Time.deltaTime;
            _headStateTimer += Time.deltaTime;

            switch (CurrentState)
            {
                case BodyState.Idle:          UpdateIdle();          break;
                case BodyState.HeadBob:       UpdateHeadBob();       break;
                case BodyState.Fly:           UpdateFly();           break;
                case BodyState.Perch:         UpdatePerch();         break;
                case BodyState.PerchedOnHand: UpdatePerchedOnHand(); break;
                case BodyState.Dance:         UpdateDance();         break;
                case BodyState.Sit:           UpdateSit();           break;
            }

            UpdateHeadOverlay();
        }

        // ─── public control ──────────────────────────────────────────────

        public void FlyTo(Vector3 target)
        {
            _flyTarget = target;
            _isFlying  = true;
            SetState(BodyState.Fly);
        }

        public void SetState(BodyState state)
        {
            if (CurrentState == state) return;
            string oldWire = BodyStateToWire(CurrentState);
            CurrentState = state;
            _stateTimer  = 0f;

            // parrot_behavior_rules §2.2: no head tilt during flight
            if (state == BodyState.Fly && CurrentHeadState != HeadState.Forward)
                SetHeadState(HeadState.Forward);

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
            _headStateTimer  = 0f;

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
                case "idle":             SetState(BodyState.Idle);          break;
                case "head_bob":
                case "listening":        SetState(BodyState.HeadBob);       break;
                case "fly":
                case "flying":           SetState(BodyState.Fly);           break;
                case "perch":
                case "perching":         SetState(BodyState.Perch);         break;
                case "perched_on_hand":  SetState(BodyState.PerchedOnHand); break;
                case "dance":
                case "dancing":          SetState(BodyState.Dance);         break;
                case "sit":
                case "sitting":          SetState(BodyState.Sit);           break;
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

        // ─── wire mappers (Brain wire contract — DO NOT RENAME) ──────────

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

        // ─── ContextMenu — state debug ───────────────────────────────────

        [ContextMenu("Debug: Play Idle")]
        private void DebugPlayIdle() => SetState(BodyState.Idle);

        [ContextMenu("Debug: Play Fly")]
        private void DebugPlayFly()
        {
            _flyTarget = transform.position + transform.forward * 2f;
            _isFlying  = true;
            SetState(BodyState.Fly);
        }

        [ContextMenu("Debug: Play Dance")]
        private void DebugPlayDance() => SetState(BodyState.Dance);

        [ContextMenu("Debug: Play Sit")]
        private void DebugPlaySit() => SetState(BodyState.Sit);

        // ─── ContextMenu — wing axis diagnostic ─────────────────────────
        // Use these in Play mode to find which axis makes wings flap up/down.

        [ContextMenu("Debug: Axis Test +Z 30°")]
        private void AxisTestPosZ() => ApplyWingDeltaDeg_Diagnostic(30f, WingFlapAxisMode.PosZ);

        [ContextMenu("Debug: Axis Test -Z 30°")]
        private void AxisTestNegZ() => ApplyWingDeltaDeg_Diagnostic(30f, WingFlapAxisMode.NegZ);

        [ContextMenu("Debug: Axis Test +X 30°")]
        private void AxisTestPosX() => ApplyWingDeltaDeg_Diagnostic(30f, WingFlapAxisMode.PosX);

        [ContextMenu("Debug: Axis Test -X 30°")]
        private void AxisTestNegX() => ApplyWingDeltaDeg_Diagnostic(30f, WingFlapAxisMode.NegX);

        [ContextMenu("Debug: Wing Reset to Base")]
        private void WingResetToBase()
        {
            if (_leftWingTransform  != null) _leftWingTransform.localRotation  = _leftWingBaseRot;
            if (_rightWingTransform != null) _rightWingTransform.localRotation = _rightWingBaseRot;
        }

        // ─── per-state update ────────────────────────────────────────────

        private void UpdateIdle()
        {
            float t = _stateTimer;
            float mc = McAge;

            // Gentle hover bob (keep existing to not disturb W3.A.2 feel)
            float bob = Mathf.Sin(t * idleBobFrequency * Mathf.PI * 2f) * idleBobAmplitude;
            transform.localPosition = _basePosition + new Vector3(0f, bob, 0f);
            // NOTE: no constant Y-rotation here — vanilla parrot just stands.

            // Tail gentle yaw sway — vanilla ref cos(age*0.3)*0.2 rad (source A)
            if (_tailTransform != null)
            {
                float tailSway = Mathf.Cos(mc * 0.3f) * idleTailSwayDegrees;
                _tailTransform.localRotation = _tailBaseRot * Quaternion.Euler(0f, tailSway, 0f);
            }

            // Wings barely breathe — tiny fold/unfold, not real flapping
            ApplyWingDeltaDeg(Mathf.Sin(t * 0.8f * Mathf.PI * 2f) * idleWingBreathDegrees);

            ResetBodyToBase(4f);
            LerpLegsToBase(4f);
        }

        private void UpdateHeadBob()
        {
            float t = _stateTimer;
            float bob = Mathf.Sin(t * idleBobFrequency * Mathf.PI * 2f) * idleBobAmplitude;
            transform.localPosition = _basePosition + new Vector3(0f, bob, 0f);

            if (_headTransform != null && CurrentHeadState == HeadState.Forward)
            {
                float nod = Mathf.Sin(t * headBobFrequency * Mathf.PI * 2f) * headBobAmplitude * 90f;
                _headTransform.localRotation = _headBaseRot * Quaternion.Euler(nod, 0f, 0f);
            }

            LerpBonesToBase(3f);
        }

        private void UpdateFly()
        {
            if (!_isFlying) return;

            float t   = Time.time;
            var   dir = (_flyTarget - transform.position).normalized;
            transform.position = Vector3.MoveTowards(transform.position, _flyTarget, flySpeed * Time.deltaTime);

            if (dir.sqrMagnitude > 0.0001f)
            {
                var targetRot = Quaternion.LookRotation(dir, Vector3.up)
                                * Quaternion.Euler(-flyTiltDegrees, 0f, 0f);
                transform.rotation = Quaternion.Slerp(transform.rotation, targetRot, 8f * Time.deltaTime);
            }

            // Vanilla flying wing: leftWing.zRot = cos(limbSwing * 0.6662f) * 0.25f (rad), rightWing = -left
            // source A: SpigotMC + Forge javadoc decompile
            float leftRad = Mathf.Cos(t * flyWingFreqMult) * flyWingAmpRad;
            ApplyWingMirroredRad(leftRad);

            // Forward body tilt during flight
            if (_bodyTransform != null)
                _bodyTransform.localRotation = Quaternion.Slerp(
                    _bodyTransform.localRotation,
                    _bodyBaseRot * Quaternion.Euler(20f, 0f, 0f),
                    5f * Time.deltaTime);

            if (_tailTransform != null)
                _tailTransform.localRotation = Quaternion.Slerp(
                    _tailTransform.localRotation,
                    _tailBaseRot * Quaternion.Euler(-10f, 0f, 0f),
                    5f * Time.deltaTime);

            LerpLegsToBase(3f);

            if (Vector3.Distance(transform.position, _flyTarget) < flyArrivalThreshold)
            {
                transform.position = _flyTarget;
                _isFlying  = false;
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
        /// Position driven externally by <c>PerchOnHand</c>. Driver only adds subtle
        /// alive-feeling idle animation on bones.
        /// </summary>
        private void UpdatePerchedOnHand()
        {
            float t  = Time.time;
            float mc = McAge;

            float breath = Mathf.Sin(t * perchBreathFrequency * Mathf.PI * 2f) * perchBreathAmplitude;
            transform.localScale = _baseScale * (1f + breath);

            // Tiny wing breath — wings should be mostly closed when perched
            ApplyWingDeltaDeg(Mathf.Sin(t * 0.8f * Mathf.PI * 2f) * (idleWingBreathDegrees * 0.5f));

            if (_tailTransform != null)
            {
                float sway = Mathf.Cos(mc * 0.3f) * (idleTailSwayDegrees * 0.5f);
                _tailTransform.localRotation = _tailBaseRot * Quaternion.Euler(0f, sway, 0f);
            }

            // Weight-shift between feet
            if (_leftLegTransform != null && _rightLegTransform != null)
            {
                float shift = Mathf.Sin(mc * 0.3f) * 4f;
                _leftLegTransform.localRotation  = _leftLegBaseRot  * Quaternion.Euler( shift, 0f, 0f);
                _rightLegTransform.localRotation = _rightLegBaseRot * Quaternion.Euler(-shift, 0f, 0f);
            }

            ResetBodyToBase(4f);
        }

        /// <summary>
        /// Vanilla PARTY state (source A):
        ///   • Wings FIXED at ±0.349 rad (≈±20°) — NOT animated
        ///   • Body bounces vertically with sin(ageInTicks * 0.6662)
        ///   • Head bobs in sync
        ///   Dance owns head animation; UpdateHeadOverlay skips this state (parrot_behavior_rules §2.2).
        /// </summary>
        private void UpdateDance()
        {
            float t  = Time.time;
            float mc = McAge;

            // Body vertical bounce — vanilla: driven by danceAngle = ageInTicks % N
            float bodyBob = Mathf.Sin(t * danceBodyBobFreqMult) * danceBodyBobMeters;
            transform.localPosition = _basePosition + new Vector3(0f, bodyBob, 0f);

            // Body slight rock
            if (_bodyTransform != null)
            {
                float roll = Mathf.Sin(t * danceBodyBobFreqMult * 0.5f) * 6f;
                _bodyTransform.localRotation = _bodyBaseRot * Quaternion.Euler(0f, 0f, roll);
            }

            // Head bobs with body bounce (pitch)
            if (_headTransform != null)
            {
                float pitch = Mathf.Sin(t * danceBodyBobFreqMult) * danceHeadBobDegrees;
                _headTransform.localRotation = _headBaseRot * Quaternion.Euler(pitch, 0f, 0f);
            }

            // Wings FIXED at party spread — vanilla: leftWing.zRot = -0.34906584f, rightWing = +0.34906584f
            // source A: SpigotMC decompile snippet (rotateAngleZ values for PARTY)
            ApplyWingPartySpread();

            // Tail fans with body bob
            if (_tailTransform != null)
            {
                float fan = Mathf.Cos(mc * 0.3f) * danceTailFanDegrees;
                _tailTransform.localRotation = _tailBaseRot * Quaternion.Euler(0f, fan, 0f);
            }

            LerpLegsToBase(3f);
        }

        private void UpdateSit()
        {
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

            if (_leftWingTransform != null && _rightWingTransform != null)
            {
                float closeDeg = -sitWingCloseDegrees;
                _leftWingTransform.localRotation  = Quaternion.Slerp(_leftWingTransform.localRotation,
                    _leftWingBaseRot  * MakeWingDelta(-closeDeg), 5f * Time.deltaTime);
                _rightWingTransform.localRotation = Quaternion.Slerp(_rightWingTransform.localRotation,
                    _rightWingBaseRot * MakeWingDelta( closeDeg), 5f * Time.deltaTime);
            }

            if (_tailTransform != null)
                _tailTransform.localRotation = Quaternion.Slerp(
                    _tailTransform.localRotation,
                    _tailBaseRot * Quaternion.Euler(-12f, 0f, 0f),
                    5f * Time.deltaTime);

            ResetBodyToBase(4f);
        }

        // ─── head overlay (every frame) ──────────────────────────────────

        private void UpdateHeadOverlay()
        {
            if (_headTransform == null) return;
            if (CurrentState == BodyState.HeadBob && CurrentHeadState == HeadState.Forward) return;
            if (CurrentState == BodyState.Dance) return; // Dance drives head internally

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
                    // Gentle idle head yaw sway on idle-like states — vanilla ref cos(age*0.7)*~12°
                    bool idleLike = CurrentState == BodyState.Idle
                                 || CurrentState == BodyState.Sit
                                 || CurrentState == BodyState.Perch
                                 || CurrentState == BodyState.HeadBob;
                    if (idleLike)
                    {
                        float headYaw = Mathf.Cos(McAge * 0.7f) * idleHeadSwayDegrees;
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

        // ─── wing helpers ─────────────────────────────────────────────────

        /// <summary>
        /// Flying mirror: left = +rad, right = -rad (vanilla leftWing.zRot / rightWing.zRot = -left).
        /// Radians are converted to degrees and applied on the configured axis.
        /// </summary>
        private void ApplyWingMirroredRad(float leftRad)
        {
            if (_leftWingTransform == null || _rightWingTransform == null) return;
            float lDeg = leftRad * Mathf.Rad2Deg;
            _leftWingTransform.localRotation  = _leftWingBaseRot  * MakeWingDelta( lDeg);
            _rightWingTransform.localRotation = _rightWingBaseRot * MakeWingDelta(-lDeg);
        }

        /// <summary>Symmetric delta (same magnitude, mirrored) — used for idle breath and perch.</summary>
        private void ApplyWingDeltaDeg(float deltaDeg)
        {
            if (_leftWingTransform == null || _rightWingTransform == null) return;
            _leftWingTransform.localRotation  = _leftWingBaseRot  * MakeWingDelta( deltaDeg);
            _rightWingTransform.localRotation = _rightWingBaseRot * MakeWingDelta(-deltaDeg);
        }

        /// <summary>
        /// Vanilla PARTY fixed spread: leftWing = -0.349 rad, rightWing = +0.349 rad.
        /// This is the NEGATED convention from vanilla (left wing tucks under, right spreads, or vice versa —
        /// exact visual depends on bone axis; adjust danceWingSpreadRad sign if needed).
        /// Source A: SpigotMC decompile: leftWing.rotateAngleZ = -0.34906584F, right = +0.34906584F.
        /// </summary>
        private void ApplyWingPartySpread()
        {
            if (_leftWingTransform == null || _rightWingTransform == null) return;
            float spreadDeg = danceWingSpreadRad * Mathf.Rad2Deg;
            _leftWingTransform.localRotation  = _leftWingBaseRot  * MakeWingDelta(-spreadDeg);
            _rightWingTransform.localRotation = _rightWingBaseRot * MakeWingDelta( spreadDeg);
        }

        private Quaternion MakeWingDelta(float deg)
        {
            switch (wingFlapAxisMode)
            {
                case WingFlapAxisMode.PosZ:  return Quaternion.Euler(0f, 0f,  deg);
                case WingFlapAxisMode.NegZ:  return Quaternion.Euler(0f, 0f, -deg);
                case WingFlapAxisMode.PosX:  return Quaternion.Euler( deg, 0f, 0f);
                case WingFlapAxisMode.NegX:  return Quaternion.Euler(-deg, 0f, 0f);
                default:                     return Quaternion.Euler(0f, 0f, -deg);
            }
        }

        private void ApplyWingDeltaDeg_Diagnostic(float deg, WingFlapAxisMode mode)
        {
            if (_leftWingTransform == null || _rightWingTransform == null)
            {
                Debug.LogWarning("[AnimationDriver] Wing transforms not found — can't axis-test.");
                return;
            }
            Quaternion deltaL = Quaternion.identity, deltaR = Quaternion.identity;
            switch (mode)
            {
                case WingFlapAxisMode.PosZ: deltaL = Quaternion.Euler(0f, 0f,  deg); deltaR = Quaternion.Euler(0f, 0f, -deg); break;
                case WingFlapAxisMode.NegZ: deltaL = Quaternion.Euler(0f, 0f, -deg); deltaR = Quaternion.Euler(0f, 0f,  deg); break;
                case WingFlapAxisMode.PosX: deltaL = Quaternion.Euler( deg, 0f, 0f); deltaR = Quaternion.Euler(-deg, 0f, 0f); break;
                case WingFlapAxisMode.NegX: deltaL = Quaternion.Euler(-deg, 0f, 0f); deltaR = Quaternion.Euler( deg, 0f, 0f); break;
            }
            _leftWingTransform.localRotation  = _leftWingBaseRot  * deltaL;
            _rightWingTransform.localRotation = _rightWingBaseRot * deltaR;
            Debug.Log($"[AnimationDriver] Axis test {mode} {deg}°. Check if wings flap toward body or away.");
        }

        // ─── misc helpers ─────────────────────────────────────────────────

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

        private Transform FindDeepLog(string nodeName)
        {
            if (string.IsNullOrEmpty(nodeName)) return null;
            var t = FindDeep(transform, nodeName);
            if (t == null)
                Debug.LogWarning($"[AnimationDriver] Bone not found: '{nodeName}'");
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
