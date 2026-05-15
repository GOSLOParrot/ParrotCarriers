using System;
using ParrotApp.Config;
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
        [SerializeField] private AppStartupFlowController startupFlow;
        [SerializeField] private FormalMainReadyGate mainReadyGate;
        [SerializeField] private FormalModelPlacementController placementController;
        [SerializeField] private float fallbackWalkSpeedMetersPerSecond = 0.28f;
        [SerializeField] private float fallbackTurnSpeed = 8f;

        public bool RemoteVisible { get; private set; }
        public Vector2 CurrentInput { get; private set; }
        public string LastRemoteStatus { get; private set; } = "waiting_start";

        private Canvas _canvas;
        private RectTransform _root;
        private RectTransform _knob;
        private Text _statusText;
        private bool _walking;
        private float _tick;

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
        }

        private void Update()
        {
            _tick += Time.unscaledDeltaTime;
            if (_tick >= 0.25f)
            {
                _tick = 0f;
                RefreshVisible();
            }

            if (!RemoteVisible || CurrentInput.sqrMagnitude < 0.01f)
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
        }

        private void HandleTransitionStarted(AppStartupConfigDto _)
        {
            CurrentInput = Vector2.zero;
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
            LastRemoteStatus = "startup_failed:" + ShortReason(reason);
            SetVisible(false);
        }

        private void HandleGateChanged(FormalMainReadySnapshot _)
        {
            RefreshVisible();
        }

        private void SetJoystickInput(Vector2 input)
        {
            CurrentInput = Vector2.ClampMagnitude(input, 1f);
            if (CurrentInput.sqrMagnitude < 0.01f)
                EndWalk();
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
                              && placementController.PlacedModel != null;

            SetVisible(shouldShow);
            if (!shouldShow)
            {
                CurrentInput = Vector2.zero;
                LastRemoteStatus = placementController != null && !placementController.HasPlacedModel
                    ? "waiting_placed_model"
                    : "waiting_home_ready";
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
        }

        private bool ApplyModelWalk(Vector2 input, float deltaTime)
        {
            var model = placementController != null ? placementController.PlacedModel : null;
            if (model == null)
            {
                LastRemoteStatus = "model_missing";
                return false;
            }

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

        private void EndWalk()
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
            if (RemoteVisible)
                LastRemoteStatus = "idle";
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

            _root = CreatePanel("FormalModelRemotePad", canvasObject.transform, new Vector2(0f, 0f), new Vector2(0f, 0f), new Vector2(0f, 0f), new Vector2(46f, 34f), new Vector2(214f, 214f), new Color(0.08f, 0.06f, 0.045f, 0.58f));
            var pad = _root.gameObject.AddComponent<JoystickPad>();
            pad.Bind(this, _root, out _knob);

            _statusText = CreateText("FormalModelRemoteStatus", _root, new Vector2(0f, 1f), new Vector2(1f, 1f), new Vector2(0.5f, 1f), new Vector2(0f, -18f), new Vector2(-18f, 32f), 13, TextAnchor.MiddleCenter);
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
            image.color = color;
            return rt;
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
            text.color = new Color(0.92f, 0.82f, 0.66f, 0.94f);
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

        private sealed class JoystickPad : MonoBehaviour, IPointerDownHandler, IDragHandler, IPointerUpHandler
        {
            private FormalModelRemoteController _owner;
            private RectTransform _pad;
            private RectTransform _knob;
            private float _radius;

            public void Bind(FormalModelRemoteController owner, RectTransform pad, out RectTransform knob)
            {
                _owner = owner;
                _pad = pad;
                _radius = Mathf.Min(pad.sizeDelta.x, pad.sizeDelta.y) * 0.38f;
                _knob = CreatePanel("FormalModelRemoteKnob", pad, new Vector2(0.5f, 0.5f), new Vector2(0.5f, 0.5f), new Vector2(0.5f, 0.5f), Vector2.zero, new Vector2(72f, 72f), new Color(0.78f, 0.58f, 0.34f, 0.76f));
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

                Vector2 input = Vector2.ClampMagnitude(local / Mathf.Max(1f, _radius), 1f);
                if (_knob != null) _knob.anchoredPosition = input * (_radius * 0.68f);
                _owner.SetJoystickInput(input);
            }
        }
    }
}
