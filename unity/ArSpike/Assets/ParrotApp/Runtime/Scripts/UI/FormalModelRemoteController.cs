using System;
using ParrotApp.Config;
using ParrotApp.Ecp;
using ParrotApp.Lifecycle;
using ParrotApp.Parrot;
using UnityEngine;
using UnityEngine.EventSystems;
using UnityEngine.UI;

namespace ParrotApp.UI
{
    /// <summary>
    /// Formal homepage model joystick owner.
    ///
    /// This is a local Unity control for the placed model. It deliberately does
    /// not call Brain RPC, does not mutate RoomSetting/menu persistence, and
    /// does not stand in for XRHand fly/perch. Brain-directed motion remains in
    /// compact RPC/ECP commands such as flyTo/animate; the on-screen joystick is
    /// the user's direct mobile control after the placement gate is complete.
    /// </summary>
    [DisallowMultipleComponent]
    public class FormalModelRemoteController : MonoBehaviour
    {
        private const string BodyLock = "body";
        private const float LiftJoystickDirectionDeadZone = 0.12f;
        private static readonly Color JoystickPadColor = new Color(1f, 1f, 1f, 0.16f);
        private static readonly Color JoystickKnobColor = new Color(1f, 1f, 1f, 0.38f);
        private static Sprite _joystickCircleSprite;

        [SerializeField] private AppStartupFlowController startupFlow;
        [SerializeField] private FormalMainReadyGate mainReadyGate;
        [SerializeField] private FormalModelPlacementController placementController;
        [SerializeField] private float fallbackWalkSpeedMetersPerSecond = 0.28f;
        [SerializeField] private float fallbackTurnSpeed = 8f;
        [SerializeField] private float fallbackFlightHorizontalSpeedMetersPerSecond = 0.4f;
        [SerializeField] private float fallbackFlightVerticalSpeedMetersPerSecond = 0.5f;
        [SerializeField] private float remoteFlightMaxHeightMeters = 1.2f;
        [SerializeField] private float remoteLandingEpsilonMeters = 0.025f;
        [SerializeField] private bool experimentalBirdFlightEnabled = true;
        [SerializeField] private bool randomizeRemoteFlightStyle = true;
        [SerializeField] private float remoteFlightVelocitySmoothTime = 0.1f;
        [SerializeField] private float remoteFlightFlutterMetersPerSecond = 0.055f;
        [SerializeField] private float remoteFlightSwayMetersPerSecond = 0.025f;
        [SerializeField] private float remoteFlightStyleMinSeconds = 1.2f;
        [SerializeField] private float remoteFlightStyleMaxSeconds = 2.6f;
        [SerializeField] private AnimationCurve remoteFlightFlutterCurve = new AnimationCurve(
            new Keyframe(0f, 0f),
            new Keyframe(0.25f, 1f),
            new Keyframe(0.5f, 0f),
            new Keyframe(0.75f, -0.55f),
            new Keyframe(1f, 0f));
        [SerializeField] private AnimationCurve remoteFlightGlideCurve = new AnimationCurve(
            new Keyframe(0f, 0.2f),
            new Keyframe(0.5f, -0.12f),
            new Keyframe(1f, 0.2f));

        public bool RemoteVisible { get; private set; }
        public Vector2 CurrentInput { get; private set; }
        public float CurrentLiftInput { get; private set; }
        public string LastRemoteStatus { get; private set; } = "waiting_start";

        private Canvas _canvas;
        private RectTransform _root;
        private RectTransform _knob;
        private RectTransform _liftRoot;
        private RectTransform _liftKnob;
        private Text _statusText;
        private Text _liftStatusText;
        private bool _walking;
        private bool _remoteFlying;
        private bool _hasFlightGroundY;
        private float _flightGroundY;
        private RemoteFlightStyle _remoteFlightStyle = RemoteFlightStyle.ShortFlutter;
        private Vector3 _remoteFlightVelocity;
        private Vector3 _remoteFlightVelocityRef;
        private float _remoteFlightStartedAt;
        private float _remoteFlightNoiseSeed;
        private float _nextRemoteFlightStyleAt;
        private string _remoteControlCommandId = "";
        private float _tick;
        private FormalModelPlacementController _subscribedPlacementController;

        private void OnEnable()
        {
            Bind();
        }

        private void Start()
        {
            Bind();
            EnsureUi();
            RefreshVisible();
        }

        private void OnDisable()
        {
            Unbind();
            EndWalk();
            PublishRemoteBodyState("idle");
            EndRemoteBodyControl();
        }

        private void Update()
        {
            _tick += Time.unscaledDeltaTime;
            if (_tick >= 0.25f)
            {
                _tick = 0f;
                RefreshVisible();
            }

            bool wantsMove = CurrentInput.sqrMagnitude >= 0.01f;
            bool wantsLift = Mathf.Abs(CurrentLiftInput) >= 0.01f;

            if (!RemoteVisible)
            {
                if (_walking) EndWalk();
                if (_remoteFlying) EndRemoteFlight(landed: false, continueWalking: false);
                else EndRemoteBodyControl();
                return;
            }

            if (_remoteFlying || wantsLift)
            {
                if (_walking) EndWalk(releaseRemoteControl: false);
                ApplyModelFlight(CurrentInput, CurrentLiftInput, Time.deltaTime);
                RefreshStatusText();
                return;
            }

            if (!wantsMove)
            {
                if (_walking) EndWalk();
                return;
            }

            _walking = ApplyModelWalk(CurrentInput, Time.deltaTime);
            RefreshStatusText();
        }

        private void Bind()
        {
            if (startupFlow == null) startupFlow = FindObjectOfType<AppStartupFlowController>();
            if (mainReadyGate == null) mainReadyGate = FindObjectOfType<FormalMainReadyGate>();
            if (placementController == null) placementController = FindObjectOfType<FormalModelPlacementController>();

            if (startupFlow != null)
            {
                startupFlow.OnTransitionStarted -= HandleTransitionStarted;
                startupFlow.OnMainUiReady -= HandleMainUiReady;
                startupFlow.OnStartupFailed -= HandleStartupFailed;
                startupFlow.OnTransitionStarted += HandleTransitionStarted;
                startupFlow.OnMainUiReady += HandleMainUiReady;
                startupFlow.OnStartupFailed += HandleStartupFailed;
            }

            if (mainReadyGate != null)
            {
                mainReadyGate.OnGateChanged -= HandleGateChanged;
                mainReadyGate.OnGateChanged += HandleGateChanged;
            }

            if (_subscribedPlacementController != placementController)
            {
                if (_subscribedPlacementController != null)
                    _subscribedPlacementController.OnPlacementStateChanged -= HandlePlacementStateChanged;
                _subscribedPlacementController = placementController;
                if (_subscribedPlacementController != null)
                    _subscribedPlacementController.OnPlacementStateChanged += HandlePlacementStateChanged;
            }
        }

        private void Unbind()
        {
            if (startupFlow != null)
            {
                startupFlow.OnTransitionStarted -= HandleTransitionStarted;
                startupFlow.OnMainUiReady -= HandleMainUiReady;
                startupFlow.OnStartupFailed -= HandleStartupFailed;
            }
            if (mainReadyGate != null)
                mainReadyGate.OnGateChanged -= HandleGateChanged;
            if (_subscribedPlacementController != null)
            {
                _subscribedPlacementController.OnPlacementStateChanged -= HandlePlacementStateChanged;
                _subscribedPlacementController = null;
            }
        }

        private void HandleTransitionStarted(AppStartupConfigDto _)
        {
            CurrentInput = Vector2.zero;
            CurrentLiftInput = 0f;
            PublishRemoteBodyState("idle");
            EndRemoteBodyControl();
            LastRemoteStatus = "waiting_place";
            SetVisible(false);
        }

        private void HandleMainUiReady(AppStartupConfigDto _)
        {
            RefreshVisible();
        }

        private void HandleStartupFailed(string reason)
        {
            CurrentInput = Vector2.zero;
            CurrentLiftInput = 0f;
            PublishRemoteBodyState("idle");
            EndRemoteBodyControl();
            LastRemoteStatus = "startup_failed:" + ShortReason(reason);
            SetVisible(false);
        }

        private void HandleGateChanged(FormalMainReadySnapshot _)
        {
            RefreshVisible();
        }

        private void HandlePlacementStateChanged(FormalModelPlacementController placement)
        {
            if (placement != null)
                placementController = placement;
            RefreshVisible();
        }

        private void SetJoystickInput(Vector2 input)
        {
            CurrentInput = Vector2.ClampMagnitude(input, 1f);
            if (CurrentInput.sqrMagnitude < 0.01f && !_remoteFlying)
                EndWalk();
            RefreshStatusText();
        }

        private void SetLiftInput(float input)
        {
            CurrentLiftInput = Mathf.Abs(input) < 0.04f ? 0f : Mathf.Clamp(input, -1f, 1f);
            RefreshStatusText();
        }

        private void RefreshVisible()
        {
            EnsureUi();
            if (placementController == null)
                placementController = FindObjectOfType<FormalModelPlacementController>();

            bool shouldShow = startupFlow != null
                              && startupFlow.MainUiReadyOnce
                              && (mainReadyGate == null || mainReadyGate.IsReady)
                              && placementController != null
                              && placementController.HasPlacedModel
                              && placementController.HasSelectedModel
                              && placementController.PlacedModel != null;

            SetVisible(shouldShow);
            if (!shouldShow)
            {
                CurrentInput = Vector2.zero;
                CurrentLiftInput = 0f;
                if (_remoteFlying) EndRemoteFlight(landed: false, continueWalking: false);
                else if (_walking) EndWalk();
                else EndRemoteBodyControl();
                if (placementController == null || !placementController.HasPlacedModel)
                    LastRemoteStatus = "waiting_placed_model";
                else if (!placementController.HasSelectedModel)
                    LastRemoteStatus = "waiting_selected_model";
                else
                    LastRemoteStatus = "waiting_home_ready";
            }
            else if (CurrentInput.sqrMagnitude < 0.01f && !_walking)
            {
                LastRemoteStatus = "idle";
            }
            RefreshStatusText();
        }

        private void SetVisible(bool visible)
        {
            RemoteVisible = visible;
            if (_root != null && _root.gameObject.activeSelf != visible)
                _root.gameObject.SetActive(visible);
            if (_liftRoot != null && _liftRoot.gameObject.activeSelf != visible)
                _liftRoot.gameObject.SetActive(visible);
        }

        private bool ApplyModelWalk(Vector2 input, float deltaTime)
        {
            var model = placementController != null ? placementController.PlacedModel : null;
            if (model == null)
            {
                LastRemoteStatus = "model_missing";
                return false;
            }

            BeginRemoteBodyControl("walk");
            PublishRemoteBodyState("walking");

            var parrot = model.GetComponentInChildren<ParrotController>(true);
            if (parrot != null)
            {
                parrot.WalkOnPlane(input, deltaTime);
                LastRemoteStatus = "walking:parrot_controller";
                return true;
            }

            var driver = model.GetComponentInChildren<ModelDriver>(true);
            string modelId = driver != null && driver.Manifest != null
                ? driver.Manifest.model_id
                : (placementController != null ? placementController.ActiveModelId : "");
            var controller = ParrotRegistry.Instance != null
                ? ParrotRegistry.Instance.Resolve(modelId)
                : null;
            if (controller != null && Supports(controller, "spine_walk"))
            {
                var payload = new WalkPayload
                {
                    x = input.x,
                    z = input.y,
                    deltaTime = deltaTime,
                };
                if (controller.ApplyCapability("spine_walk", JsonUtility.ToJson(payload)))
                {
                    LastRemoteStatus = "walking:spine_walk";
                    return true;
                }
            }

            var animationDriver = model.GetComponentInChildren<AnimationDriver>(true);
            if (animationDriver != null)
            {
                animationDriver.WalkOnPlane(input, deltaTime, fallbackWalkSpeedMetersPerSecond, fallbackTurnSpeed);
                LastRemoteStatus = "walking:animation_driver";
                return true;
            }

            ApplyFallbackTranslate(model.transform, input, deltaTime);
            LastRemoteStatus = "walking:fallback_translate";
            return true;
        }

        private bool ApplyModelFlight(Vector2 planarInput, float liftInput, float deltaTime)
        {
            var model = placementController != null ? placementController.PlacedModel : null;
            if (model == null)
            {
                LastRemoteStatus = "model_missing";
                return false;
            }

            Transform target = ResolveMotionTarget(model, out AnimationDriver animationDriver, out Animator animator);
            if (target == null)
            {
                LastRemoteStatus = "flight_target_missing";
                return false;
            }

            if (animationDriver != null && animationDriver.CurrentState == AnimationDriver.BodyState.PerchedOnHand)
            {
                LastRemoteStatus = "perched_on_hand";
                PublishRemoteBodyState("perched_on_hand");
                return false;
            }

            BeginRemoteBodyControl("flight");
            PublishRemoteBodyState("flying");

            if (!_remoteFlying)
            {
                _remoteFlying = true;
                _flightGroundY = target.position.y;
                _hasFlightGroundY = true;
                BeginRemoteFlightStyle();
            }
            if (!_hasFlightGroundY)
            {
                _flightGroundY = target.position.y;
                _hasFlightGroundY = true;
            }
            MaybeSwitchRemoteFlightStyle();

            Vector3 planar = ResolveCameraRelativePlanarDirection(planarInput);
            Vector3 desiredVelocity = planar * fallbackFlightHorizontalSpeedMetersPerSecond
                                      + Vector3.up * (liftInput * fallbackFlightVerticalSpeedMetersPerSecond);
            if (experimentalBirdFlightEnabled)
                desiredVelocity += ResolveBirdFlightVelocity(planar, liftInput);

            float maxSpeed = Mathf.Max(
                fallbackFlightHorizontalSpeedMetersPerSecond,
                fallbackFlightVerticalSpeedMetersPerSecond) * 1.8f;
            _remoteFlightVelocity = Vector3.SmoothDamp(
                _remoteFlightVelocity,
                desiredVelocity,
                ref _remoteFlightVelocityRef,
                Mathf.Max(0.01f, remoteFlightVelocitySmoothTime),
                Mathf.Max(0.1f, maxSpeed),
                deltaTime);
            if (liftInput < -0.05f && _remoteFlightVelocity.y > desiredVelocity.y)
                _remoteFlightVelocity.y = desiredVelocity.y;

            Vector3 next = target.position + _remoteFlightVelocity * deltaTime;

            float maxY = _flightGroundY + Mathf.Max(0.05f, remoteFlightMaxHeightMeters);
            next.y = Mathf.Clamp(next.y, _flightGroundY, maxY);

            bool descendingToGround = liftInput < -0.05f
                                      && next.y <= _flightGroundY + Mathf.Max(0.001f, remoteLandingEpsilonMeters);
            if (descendingToGround)
                next.y = _flightGroundY;

            target.position = next;
            if (planar.sqrMagnitude > 0.0001f)
            {
                target.rotation = Quaternion.Slerp(
                    target.rotation,
                    Quaternion.LookRotation(planar, Vector3.up),
                    fallbackTurnSpeed * deltaTime);
            }

            if (animationDriver != null)
            {
                if (!descendingToGround)
                    animationDriver.SetState(AnimationDriver.BodyState.Fly);
                animationDriver.RebaseBaseTransformFromCurrent();
            }
            ApplyAnimatorFlight(animator, !descendingToGround, false);

            if (descendingToGround)
            {
                bool continueWalking = planarInput.sqrMagnitude >= 0.01f;
                EndRemoteFlight(landed: true, continueWalking: continueWalking);
                if (continueWalking)
                    _walking = ApplyModelWalk(planarInput, deltaTime);
                return false;
            }

            float height = Mathf.Max(0f, target.position.y - _flightGroundY);
            LastRemoteStatus = "flying:remote_lift:" + height.ToString("0.00");
            return true;
        }

        private void EndWalk(bool releaseRemoteControl = true)
        {
            var model = placementController != null ? placementController.PlacedModel : null;
            if (model != null)
            {
                var parrot = model.GetComponentInChildren<ParrotController>(true);
                if (parrot != null) parrot.EndPlaneWalk();

                var animationDriver = model.GetComponentInChildren<AnimationDriver>(true);
                if (animationDriver != null) animationDriver.EndPlaneWalk();

                string modelId = placementController != null ? placementController.ActiveModelId : "";
                var controller = ParrotRegistry.Instance != null
                    ? ParrotRegistry.Instance.Resolve(modelId)
                    : null;
                if (controller != null && Supports(controller, "spine_idle"))
                    controller.ApplyCapability("spine_idle", "{}");
            }

            _walking = false;
            if (releaseRemoteControl && !_remoteFlying)
            {
                PublishRemoteBodyState("idle");
                EndRemoteBodyControl();
            }
            if (RemoteVisible)
                LastRemoteStatus = "idle";
        }

        private void EndRemoteFlight(bool landed, bool continueWalking)
        {
            var model = placementController != null ? placementController.PlacedModel : null;
            if (model != null)
            {
                Transform target = ResolveMotionTarget(model, out AnimationDriver animationDriver, out Animator animator);
                if (landed && target != null && _hasFlightGroundY)
                {
                    Vector3 p = target.position;
                    p.y = _flightGroundY;
                    target.position = p;
                }

                if (animationDriver != null)
                {
                    animationDriver.RebaseBaseTransformFromCurrent();
                    animationDriver.SetState(landed && continueWalking
                        ? AnimationDriver.BodyState.Walk
                        : AnimationDriver.BodyState.Idle);
                }
                ApplyAnimatorFlight(animator, false, landed && continueWalking);
            }

            _remoteFlying = false;
            _hasFlightGroundY = false;
            _remoteFlightVelocity = Vector3.zero;
            _remoteFlightVelocityRef = Vector3.zero;
            PublishRemoteBodyState(landed && continueWalking ? "walking" : "idle");
            if (!continueWalking)
                EndRemoteBodyControl();
            LastRemoteStatus = landed && continueWalking ? "walking:landed" : (landed ? "idle:landed" : "idle");
        }

        private void BeginRemoteBodyControl(string mode)
        {
            if (string.IsNullOrEmpty(_remoteControlCommandId))
            {
                string suffix = Mathf.RoundToInt(Time.unscaledTime * 1000f).ToString();
                _remoteControlCommandId = "local_remote_" + (string.IsNullOrWhiteSpace(mode) ? "body" : mode) + "_" + suffix;
            }
            LifecycleHeartbeatPublisher.Instance?.ReportActiveCommand(_remoteControlCommandId, new[] { BodyLock });
        }

        private void EndRemoteBodyControl()
        {
            if (string.IsNullOrEmpty(_remoteControlCommandId)) return;
            LifecycleHeartbeatPublisher.Instance?.ClearActiveCommand(_remoteControlCommandId);
            _remoteControlCommandId = "";
        }

        private static void PublishRemoteBodyState(string bodyStateWire)
        {
            LifecycleHeartbeatPublisher.Instance?.ReportBodyState(bodyStateWire);
        }

        private void BeginRemoteFlightStyle()
        {
            _remoteFlightStartedAt = Time.unscaledTime;
            _remoteFlightNoiseSeed = UnityEngine.Random.Range(0f, 1000f);
            PickRemoteFlightStyle();
            _remoteFlightVelocity = Vector3.zero;
            _remoteFlightVelocityRef = Vector3.zero;
        }

        private void MaybeSwitchRemoteFlightStyle()
        {
            if (!experimentalBirdFlightEnabled || !randomizeRemoteFlightStyle)
                return;
            if (Time.unscaledTime < _nextRemoteFlightStyleAt)
                return;
            PickRemoteFlightStyle();
        }

        private void PickRemoteFlightStyle()
        {
            _remoteFlightStyle = randomizeRemoteFlightStyle && UnityEngine.Random.value > 0.5f
                ? RemoteFlightStyle.ShortGlide
                : RemoteFlightStyle.ShortFlutter;
            float minSeconds = Mathf.Max(0.5f, remoteFlightStyleMinSeconds);
            float maxSeconds = Mathf.Max(minSeconds, remoteFlightStyleMaxSeconds);
            _nextRemoteFlightStyleAt = Time.unscaledTime + UnityEngine.Random.Range(minSeconds, maxSeconds);
        }

        private Vector3 ResolveBirdFlightVelocity(Vector3 planar, float liftInput)
        {
            float activity = Mathf.Clamp01(planar.magnitude + Mathf.Abs(liftInput));
            if (activity <= 0.001f)
                return Vector3.zero;

            float flightT = Mathf.Max(0f, Time.unscaledTime - _remoteFlightStartedAt);
            float descendingScale = liftInput < -0.05f ? 0.35f : 1f;
            float curvePhase;
            float vertical;
            switch (_remoteFlightStyle)
            {
                case RemoteFlightStyle.ShortGlide:
                    curvePhase = Mathf.Repeat(flightT * 0.85f, 1f);
                    vertical = remoteFlightGlideCurve.Evaluate(curvePhase)
                               * remoteFlightFlutterMetersPerSecond
                               * 0.45f
                               * activity
                               * descendingScale;
                    break;
                case RemoteFlightStyle.ShortFlutter:
                default:
                    curvePhase = Mathf.Repeat(flightT * 3.8f, 1f);
                    vertical = remoteFlightFlutterCurve.Evaluate(curvePhase)
                               * remoteFlightFlutterMetersPerSecond
                               * activity
                               * descendingScale;
                    break;
            }

            Vector3 side = Vector3.zero;
            if (planar.sqrMagnitude > 0.0001f)
            {
                float noise = Mathf.PerlinNoise(_remoteFlightNoiseSeed, flightT * 1.4f) - 0.5f;
                side = Vector3.Cross(Vector3.up, planar.normalized)
                       * (noise * 2f * remoteFlightSwayMetersPerSecond * activity);
            }
            return side + Vector3.up * vertical;
        }

        private void ApplyFallbackTranslate(Transform target, Vector2 input, float deltaTime)
        {
            if (target == null) return;
            Camera camera = Camera.main;
            Vector3 forward = camera != null ? camera.transform.forward : Vector3.forward;
            Vector3 right = camera != null ? camera.transform.right : Vector3.right;
            forward.y = 0f;
            right.y = 0f;
            if (forward.sqrMagnitude < 0.001f) forward = Vector3.forward;
            if (right.sqrMagnitude < 0.001f) right = Vector3.right;
            forward.Normalize();
            right.Normalize();

            Vector3 direction = right * input.x + forward * input.y;
            if (direction.sqrMagnitude < 0.001f) return;
            direction = Vector3.ClampMagnitude(direction, 1f);
            target.position += direction * (fallbackWalkSpeedMetersPerSecond * deltaTime);
            target.rotation = Quaternion.Slerp(
                target.rotation,
                Quaternion.LookRotation(direction, Vector3.up),
                fallbackTurnSpeed * deltaTime);
        }

        private Transform ResolveMotionTarget(GameObject model, out AnimationDriver animationDriver, out Animator animator)
        {
            animationDriver = model != null ? model.GetComponentInChildren<AnimationDriver>(true) : null;
            animator = model != null ? model.GetComponentInChildren<Animator>(true) : null;
            if (animationDriver != null) return animationDriver.transform;

            var parrot = model != null ? model.GetComponentInChildren<ParrotController>(true) : null;
            if (parrot != null) return parrot.transform;
            return model != null ? model.transform : null;
        }

        private static void ApplyAnimatorFlight(Animator animator, bool flying, bool walking)
        {
            if (animator == null) return;
            SetAnimatorBoolIfExists(animator, "isFlying", flying);
            SetAnimatorBoolIfExists(animator, "isWalking", walking);
        }

        private static void SetAnimatorBoolIfExists(Animator animator, string parameterName, bool value)
        {
            if (animator == null || string.IsNullOrEmpty(parameterName)) return;
            foreach (var parameter in animator.parameters)
            {
                if (parameter.type == AnimatorControllerParameterType.Bool
                    && string.Equals(parameter.name, parameterName, StringComparison.Ordinal))
                {
                    animator.SetBool(parameterName, value);
                    return;
                }
            }
        }

        private static Vector3 ResolveCameraRelativePlanarDirection(Vector2 input)
        {
            Vector2 clamped = Vector2.ClampMagnitude(input, 1f);
            if (clamped.sqrMagnitude < 0.001f) return Vector3.zero;

            Camera camera = Camera.main;
            Vector3 forward = camera != null ? camera.transform.forward : Vector3.forward;
            Vector3 right = camera != null ? camera.transform.right : Vector3.right;
            forward.y = 0f;
            right.y = 0f;
            if (forward.sqrMagnitude < 0.001f) forward = Vector3.forward;
            if (right.sqrMagnitude < 0.001f) right = Vector3.right;
            forward.Normalize();
            right.Normalize();
            return Vector3.ClampMagnitude(right * clamped.x + forward * clamped.y, 1f);
        }

        private void EnsureUi()
        {
            if (_canvas != null) return;

            var canvasObject = new GameObject("FormalModelRemoteCanvas");
            canvasObject.transform.SetParent(transform, false);
            _canvas = canvasObject.AddComponent<Canvas>();
            _canvas.renderMode = RenderMode.ScreenSpaceOverlay;
            _canvas.sortingOrder = 71;

            var scaler = canvasObject.AddComponent<CanvasScaler>();
            scaler.uiScaleMode = CanvasScaler.ScaleMode.ScaleWithScreenSize;
            scaler.referenceResolution = new Vector2(2800f, 1260f);
            scaler.matchWidthOrHeight = 0.5f;
            canvasObject.AddComponent<GraphicRaycaster>();

            _root = CreatePanel("FormalModelRemotePad", canvasObject.transform, new Vector2(0f, 0f), new Vector2(0f, 0f), new Vector2(0f, 0f), new Vector2(46f, 34f), new Vector2(417f, 417f), JoystickPadColor);
            var pad = _root.gameObject.AddComponent<JoystickPad>();
            pad.Bind(this, _root, JoystickAxis.Planar, out _knob);

            _statusText = CreateText("FormalModelRemoteStatus", _root, new Vector2(0f, 1f), new Vector2(1f, 1f), new Vector2(0.5f, 1f), new Vector2(0f, -18f), new Vector2(-18f, 32f), 13, TextAnchor.MiddleCenter);

            _liftRoot = CreatePanel("FormalModelLiftPad", canvasObject.transform, new Vector2(1f, 0f), new Vector2(1f, 0f), new Vector2(1f, 0f), new Vector2(-46f, 34f), new Vector2(417f, 417f), JoystickPadColor);
            var liftPad = _liftRoot.gameObject.AddComponent<JoystickPad>();
            liftPad.Bind(this, _liftRoot, JoystickAxis.Vertical, out _liftKnob);
            _liftStatusText = CreateText("FormalModelLiftStatus", _liftRoot, new Vector2(0f, 1f), new Vector2(1f, 1f), new Vector2(0.5f, 1f), new Vector2(0f, -18f), new Vector2(-14f, 32f), 13, TextAnchor.MiddleCenter);
            SetVisible(false);
        }

        private void RefreshStatusText()
        {
            if (_statusText == null) return;
            if (!RemoteVisible)
            {
                _statusText.text = "";
                return;
            }
            _statusText.text = CurrentInput.sqrMagnitude > 0.01f
                ? "MOVE " + CurrentInput.magnitude.ToString("0.0")
                : ShortReason(LastRemoteStatus);
            if (_liftStatusText != null)
            {
                if (!RemoteVisible)
                    _liftStatusText.text = "";
                else if (_remoteFlying)
                    _liftStatusText.text = "FLY " + CurrentLiftInput.ToString("+0.0;-0.0;0.0");
                else
                    _liftStatusText.text = Mathf.Abs(CurrentLiftInput) > 0.01f ? "LIFT" : "";
            }
        }

        private static bool Supports(IParrotController controller, string capabilityId)
        {
            if (controller == null || controller.SupportedCapabilities == null) return false;
            foreach (var capability in controller.SupportedCapabilities)
            {
                if (string.Equals(capability, capabilityId, StringComparison.Ordinal))
                    return true;
            }
            return false;
        }

        private static RectTransform CreatePanel(string name, Transform parent, Vector2 anchorMin, Vector2 anchorMax, Vector2 pivot, Vector2 anchoredPosition, Vector2 size, Color color)
        {
            var go = new GameObject(name);
            go.transform.SetParent(parent, false);
            var rt = go.AddComponent<RectTransform>();
            rt.anchorMin = anchorMin;
            rt.anchorMax = anchorMax;
            rt.pivot = pivot;
            rt.anchoredPosition = anchoredPosition;
            rt.sizeDelta = size;
            var image = go.AddComponent<Image>();
            image.sprite = GetJoystickCircleSprite();
            image.preserveAspect = true;
            image.color = color;
            return rt;
        }

        private static Sprite GetJoystickCircleSprite()
        {
            if (_joystickCircleSprite != null) return _joystickCircleSprite;

            const int Size = 64;
            var texture = new Texture2D(Size, Size, TextureFormat.ARGB32, false);
            texture.wrapMode = TextureWrapMode.Clamp;
            texture.filterMode = FilterMode.Bilinear;
            Vector2 center = new Vector2((Size - 1) * 0.5f, (Size - 1) * 0.5f);
            float radius = (Size - 1) * 0.5f;
            for (int y = 0; y < Size; y++)
            {
                for (int x = 0; x < Size; x++)
                {
                    float d = Vector2.Distance(new Vector2(x, y), center) / radius;
                    float alpha = d <= 1f ? Mathf.SmoothStep(1f, 0f, Mathf.Clamp01((d - 0.88f) / 0.12f)) : 0f;
                    texture.SetPixel(x, y, new Color(1f, 1f, 1f, alpha));
                }
            }
            texture.Apply();
            _joystickCircleSprite = Sprite.Create(texture, new Rect(0f, 0f, Size, Size), new Vector2(0.5f, 0.5f), Size);
            return _joystickCircleSprite;
        }

        private static Text CreateText(string name, Transform parent, Vector2 anchorMin, Vector2 anchorMax, Vector2 pivot, Vector2 anchoredPosition, Vector2 size, int fontSize, TextAnchor anchor)
        {
            var go = new GameObject(name);
            go.transform.SetParent(parent, false);
            var rt = go.AddComponent<RectTransform>();
            rt.anchorMin = anchorMin;
            rt.anchorMax = anchorMax;
            rt.pivot = pivot;
            rt.anchoredPosition = anchoredPosition;
            rt.sizeDelta = size;
            var text = go.AddComponent<Text>();
            text.font = Resources.GetBuiltinResource<Font>("LegacyRuntime.ttf");
            text.fontSize = fontSize;
            text.alignment = anchor;
            text.color = new Color(1f, 1f, 1f, 0.78f);
            text.raycastTarget = false;
            return text;
        }

        private static string ShortReason(string raw)
        {
            if (string.IsNullOrWhiteSpace(raw)) return "idle";
            raw = raw.Trim();
            return raw.Length <= 24 ? raw : raw.Substring(0, 24);
        }

        [Serializable]
        private struct WalkPayload
        {
            public float x;
            public float z;
            public float deltaTime;
        }

        private enum JoystickAxis
        {
            Planar,
            Vertical,
        }

        private enum RemoteFlightStyle
        {
            ShortFlutter,
            ShortGlide,
        }

        private sealed class JoystickPad : MonoBehaviour, IPointerDownHandler, IDragHandler, IPointerUpHandler
        {
            private FormalModelRemoteController _owner;
            private RectTransform _pad;
            private RectTransform _knob;
            private JoystickAxis _axis;
            private float _radius;

            public void Bind(FormalModelRemoteController owner, RectTransform pad, JoystickAxis axis, out RectTransform knob)
            {
                _owner = owner;
                _pad = pad;
                _axis = axis;
                _radius = Mathf.Min(pad.sizeDelta.x, pad.sizeDelta.y) * 0.38f;
                string knobName = axis == JoystickAxis.Vertical ? "FormalModelLiftKnob" : "FormalModelRemoteKnob";
                Vector2 knobSize = new Vector2(138f, 138f);
                _knob = CreatePanel(knobName, pad, new Vector2(0.5f, 0.5f), new Vector2(0.5f, 0.5f), new Vector2(0.5f, 0.5f), Vector2.zero, knobSize, JoystickKnobColor);
                knob = _knob;
            }

            public void OnPointerDown(PointerEventData eventData)
            {
                UpdatePointer(eventData);
            }

            public void OnDrag(PointerEventData eventData)
            {
                UpdatePointer(eventData);
            }

            public void OnPointerUp(PointerEventData eventData)
            {
                if (_knob != null) _knob.anchoredPosition = Vector2.zero;
                if (_axis == JoystickAxis.Vertical)
                    _owner?.SetLiftInput(0f);
                else
                    _owner?.SetJoystickInput(Vector2.zero);
            }

            private void UpdatePointer(PointerEventData eventData)
            {
                if (_owner == null || _pad == null) return;
                if (!RectTransformUtility.ScreenPointToLocalPointInRectangle(
                        _pad,
                        eventData.position,
                        eventData.pressEventCamera,
                        out Vector2 local))
                {
                    return;
                }

                Vector2 center = new Vector2(
                    (0.5f - _pad.pivot.x) * _pad.rect.width,
                    (0.5f - _pad.pivot.y) * _pad.rect.height);
                Vector2 localFromCenter = local - center;

                Vector2 input = Vector2.ClampMagnitude(localFromCenter / Mathf.Max(1f, _radius), 1f);
                if (_knob != null) _knob.anchoredPosition = input * (_radius * 0.68f);
                if (_axis == JoystickAxis.Vertical)
                {
                    float lift = Mathf.Abs(input.y) < LiftJoystickDirectionDeadZone
                        ? 0f
                        : input.y;
                    _owner.SetLiftInput(lift);
                    return;
                }

                _owner.SetJoystickInput(input);
            }
        }
    }
}
