using System;
using System.Collections.Generic;
using System.Reflection;
using ParrotApp.Config;
using ParrotApp.Parrot;
using UnityEngine;
using UnityEngine.EventSystems;

#if ENABLE_INPUT_SYSTEM
using UnityEngine.InputSystem;
using EnhancedTouch = UnityEngine.InputSystem.EnhancedTouch.Touch;
using EnhancedTouchPhase = UnityEngine.InputSystem.TouchPhase;
using EnhancedTouchSupport = UnityEngine.InputSystem.EnhancedTouch.EnhancedTouchSupport;
#endif

#if UNITY_AR_FOUNDATION
using UnityEngine.XR.ARFoundation;
using UnityEngine.XR.ARSubsystems;
#endif

namespace ParrotApp.Lifecycle
{
    /// <summary>
    /// Formal homepage owner for the model placement gate.
    ///
    /// This component deliberately owns the first real onGosloPlaced trigger.
    /// Startup, AR baseline, and menu loading may prove transport readiness,
    /// but they must not greet or mark the companion as placed. For the current
    /// white-box slice follows the Unity AR Mobile template interaction
    /// contract: tap a plane to place, tap the model to select, drag on a plane
    /// to move, and pinch to scale. It refuses placement when AR raycast misses.
    /// The whitebox fallback is only for missing runtime visuals after a valid
    /// placement. Final prefabs can replace only InstantiateModel.
    /// </summary>
    [DisallowMultipleComponent]
    public class FormalModelPlacementController : MonoBehaviour
    {
        [SerializeField] private AppStartupFlowController startupFlow;
        [SerializeField] private FormalMainReadyGate mainReadyGate;
        [SerializeField] private FormalModelReadyReporter modelReadyReporter;
        [SerializeField] private Transform modelRoot;
        [SerializeField] private Camera placementCamera;
        [SerializeField] private bool preferArRaycastPlacement = true;
        [SerializeField] private bool fallbackToPreviewWhenArMisses = false;
        [SerializeField] private bool enableTouchPlacementAndSelection = true;
        [SerializeField] private bool enableDragMove = true;
        [SerializeField] private bool enablePinchScale = true;
        [SerializeField] private bool applyDemoRandomAngleAtSpawn = true;
        [SerializeField] private float defaultDistanceMeters = 1.2f;
        [SerializeField] private float minScaleMultiplier = 0.25f;
        [SerializeField] private float maxScaleMultiplier = 2f;
        [SerializeField] private float demoSpawnAngleRangeDegrees = 45f;
        [SerializeField] private float tapMaxSeconds = 0.32f;
        [SerializeField] private float tapMaxMovePixels = 28f;
        [SerializeField] private Vector3 fallbackPosition = new Vector3(0f, -0.25f, 1.2f);
#if UNITY_AR_FOUNDATION
        [SerializeField] private ARRaycastManager arRaycastManager;
        private static readonly List<ARRaycastHit> RaycastHits = new List<ARRaycastHit>();
#endif

        public bool HasPlacedModel { get; private set; }
        public string ActiveModelId { get; private set; } = "GOSLO_default";
        public string LastPlacementStatus { get; private set; } = "waiting_start";
        public string LastPlacementMode { get; private set; } = "none";
        public string LastVisualSource { get; private set; } = "none";
        public bool HasSelectedModel { get; private set; }
        public float ScaleMultiplier { get; private set; } = 1f;
        public string LastSelectionStatus { get; private set; } = "not_selected";
        public GameObject PlacedModel { get; private set; }
        public string LastDiagnosticSummary
        {
            get
            {
                string place = string.IsNullOrWhiteSpace(LastPlacementStatus) ? "unknown" : LastPlacementStatus;
                string mode = string.IsNullOrWhiteSpace(LastPlacementMode) ? "none" : LastPlacementMode;
                string visual = string.IsNullOrWhiteSpace(LastVisualSource) ? "none" : LastVisualSource;
                string selected = HasSelectedModel ? "selected" : "not_selected";
                return mode + " " + place + " " + selected + " " + visual;
            }
        }
        public bool CanPlaceNow => startupFlow != null
                                   && startupFlow.MainUiReadyOnce
                                   && (mainReadyGate == null || mainReadyGate.IsReady)
                                   && _manifest != null;

        private bool _reportedGosloPlaced;
        private ModelManifestDto _manifest;
        private bool _touchStartedOverUi;
        private bool _touchStartedOnModel;
        private bool _mouseStartedOverUi;
        private bool _mouseStartedOnModel;
        private bool _isDraggingModel;
        private bool _mouseDraggingModel;
        private Vector2 _touchStartPosition;
        private float _touchStartTime;
        private Vector3 _dragWorldOffset;
        private float _pinchStartDistance;
        private float _pinchStartScaleMultiplier = 1f;
        private Vector3 _placedBaseScale = Vector3.one;
        private GameObject _selectionVisual;
        private Material _selectionVisualMaterial;

        private void OnEnable()
        {
#if ENABLE_INPUT_SYSTEM
            EnhancedTouchSupport.Enable();
#endif
            Bind();
        }

        private void Start()
        {
            Bind();
            if (startupFlow != null && startupFlow.MainUiReadyOnce)
                PrepareForMain(startupFlow.ActiveConfig);
        }

        private void OnDisable()
        {
            Unbind();
        }

        private void Update()
        {
            if (!enableTouchPlacementAndSelection)
                return;

#if ENABLE_INPUT_SYSTEM
            HandleInputSystemTouchPlacementAndSelection();
            HandleInputSystemMousePlacementAndSelection();
#else
            HandleTouchPlacementAndSelection();
            HandleEditorMousePlacementAndSelection();
#endif
            UpdateSelectionVisual();
        }

        private void Bind()
        {
            if (startupFlow == null) startupFlow = FindObjectOfType<AppStartupFlowController>();
            if (mainReadyGate == null) mainReadyGate = FindObjectOfType<FormalMainReadyGate>();
            if (modelReadyReporter == null) modelReadyReporter = FindObjectOfType<FormalModelReadyReporter>();
            if (placementCamera == null) placementCamera = Camera.main;
#if UNITY_AR_FOUNDATION
            if (arRaycastManager == null) arRaycastManager = FindObjectOfType<ARRaycastManager>();
#endif

            if (startupFlow != null)
            {
                startupFlow.OnTransitionStarted -= HandleTransitionStarted;
                startupFlow.OnMainUiReady -= HandleMainUiReady;
                startupFlow.OnStartupFailed -= HandleStartupFailed;
                startupFlow.OnTransitionStarted += HandleTransitionStarted;
                startupFlow.OnMainUiReady += HandleMainUiReady;
                startupFlow.OnStartupFailed += HandleStartupFailed;
            }
        }

        private void Unbind()
        {
            if (startupFlow == null) return;
            startupFlow.OnTransitionStarted -= HandleTransitionStarted;
            startupFlow.OnMainUiReady -= HandleMainUiReady;
            startupFlow.OnStartupFailed -= HandleStartupFailed;
        }

        private void HandleTransitionStarted(AppStartupConfigDto config)
        {
            ClearPlacedModel();
            _reportedGosloPlaced = false;
            HasPlacedModel = false;
            HasSelectedModel = false;
            ScaleMultiplier = 1f;
            LastPlacementMode = "none";
            LastSelectionStatus = "not_selected";
            PrepareManifest(config);
            LastPlacementStatus = "waiting_main_ready";
        }

        private void HandleMainUiReady(AppStartupConfigDto config)
        {
            PrepareForMain(config);
        }

        private void HandleStartupFailed(string reason)
        {
            LastPlacementStatus = "startup_failed:" + ShortReason(reason);
        }

        public void PrepareForMain(AppStartupConfigDto config)
        {
            PrepareManifest(config);
            EnsureModelRoot();
            LastPlacementStatus = _manifest != null
                ? "ready_to_place:" + ActiveModelId
                : "manifest_missing:" + ActiveModelId;
        }

        public void PlaceAtDefaultPreview()
        {
            if (!CanPlace())
            {
                if (startupFlow == null || !startupFlow.MainUiReadyOnce)
                    LastPlacementStatus = "main_not_ready";
                else if (mainReadyGate != null && !mainReadyGate.IsReady)
                    LastPlacementStatus = "home_gates_wait:" + ShortReason(mainReadyGate.LastMissingGates);
                else
                    LastPlacementStatus = "manifest_missing:" + ActiveModelId;
                return;
            }

            Vector2 screenPoint = new Vector2(Screen.width * 0.5f, Screen.height * 0.5f);
            if (TryResolveArRaycastPose(screenPoint, out Pose arPose, out Vector3 surfaceNormal, out string raycastStatus))
            {
                LastPlacementMode = "ar_raycast";
                PlaceAt(arPose.position, ResolveDemoSpawnRotation(arPose.position, surfaceNormal), "ar_raycast_plane");
                return;
            }

            if (!fallbackToPreviewWhenArMisses)
            {
                LastPlacementMode = "ar_raycast_miss";
                LastPlacementStatus = raycastStatus;
                return;
            }

            Vector3 position = ResolveDefaultPosition();
            Quaternion rotation = ResolveDefaultRotation(position);
            LastPlacementMode = "preview_fallback";
            PlaceAt(position, rotation, string.IsNullOrWhiteSpace(raycastStatus) ? "preview_fallback" : raycastStatus);
        }

        public void PlaceAtScreenPoint(Vector2 screenPoint)
        {
            if (!CanPlace())
            {
                LastPlacementStatus = startupFlow == null || !startupFlow.MainUiReadyOnce
                    ? "main_not_ready"
                    : "home_gates_wait:" + ShortReason(mainReadyGate != null ? mainReadyGate.LastMissingGates : "");
                return;
            }

            if (TryResolveArRaycastPose(screenPoint, out Pose arPose, out Vector3 surfaceNormal, out string raycastStatus))
            {
                LastPlacementMode = "ar_raycast";
                PlaceAt(arPose.position, ResolveDemoSpawnRotation(arPose.position, surfaceNormal), "ar_raycast_plane");
                return;
            }

            LastPlacementMode = "ar_raycast_miss";
            LastPlacementStatus = raycastStatus;
        }

        public void PlaceAt(Vector3 position, Quaternion rotation, string reason)
        {
            if (!CanPlace()) return;
            EnsureModelRoot();
            if (modelRoot == null)
            {
                LastPlacementStatus = "model_root_missing";
                return;
            }

            bool firstPlacement = PlacedModel == null;
            if (firstPlacement)
                PlacedModel = InstantiateModel();

            if (PlacedModel == null)
            {
                LastPlacementStatus = "instantiate_failed:" + ActiveModelId;
                return;
            }

            PlacedModel.transform.SetParent(modelRoot, worldPositionStays: true);
            PlacedModel.transform.SetPositionAndRotation(position, rotation);
            PlacedModel.SetActive(true);
            if (firstPlacement)
            {
                _placedBaseScale = PlacedModel.transform.localScale;
                ScaleMultiplier = 1f;
                PlayPlacementGreeting();
            }
            ApplyScaleMultiplier();
            SelectPlacedModel(true, "placed");
            HasPlacedModel = true;
            LastPlacementStatus = "placed:" + ShortReason(reason);

            if (!_reportedGosloPlaced)
            {
                _reportedGosloPlaced = true;
                startupFlow?.ReportGosloPlaced();
            }
        }

        public void ClearPlacedModel()
        {
            if (PlacedModel != null)
            {
                Destroy(PlacedModel);
                PlacedModel = null;
            }
            DestroySelectionVisual();
            HasPlacedModel = false;
            HasSelectedModel = false;
            ScaleMultiplier = 1f;
            _isDraggingModel = false;
            _mouseDraggingModel = false;
            LastPlacementMode = "none";
            LastVisualSource = "none";
            LastPlacementStatus = "cleared";
            LastSelectionStatus = "cleared";
        }

        public void SelectPlacedModel(bool selected, string reason = "manual")
        {
            HasSelectedModel = selected && PlacedModel != null;
            LastSelectionStatus = HasSelectedModel
                ? "selected:" + ShortReason(reason)
                : "not_selected:" + ShortReason(reason);
            if (!HasSelectedModel)
                DestroySelectionVisual();
        }

        public void ScaleSelectedModel(float multiplier, string reason = "manual")
        {
            if (PlacedModel == null) return;
            ScaleMultiplier = Mathf.Clamp(multiplier, Mathf.Max(0.05f, minScaleMultiplier), Mathf.Max(minScaleMultiplier, maxScaleMultiplier));
            ApplyScaleMultiplier();
            LastSelectionStatus = "scaled:" + ScaleMultiplier.ToString("0.00") + ":" + ShortReason(reason);
        }

        private bool CanPlace()
        {
            if (startupFlow == null || !startupFlow.MainUiReadyOnce) return false;
            if (_manifest == null) PrepareManifest(startupFlow.ActiveConfig);
            if (mainReadyGate != null && !mainReadyGate.IsReady) return false;
            return _manifest != null;
        }

        private bool TryResolveArRaycastPose(Vector2 screenPoint, out Pose pose, out Vector3 surfaceNormal, out string status)
        {
            pose = new Pose();
            surfaceNormal = Vector3.up;
            status = "";
            if (!preferArRaycastPlacement)
            {
                status = "ar_raycast_disabled";
                return false;
            }

#if UNITY_AR_FOUNDATION
            if (arRaycastManager == null)
                arRaycastManager = FindObjectOfType<ARRaycastManager>();
            if (arRaycastManager == null)
            {
                status = "ar_raycast_manager_missing";
                return false;
            }
            if (!arRaycastManager.isActiveAndEnabled)
            {
                status = "ar_raycast_manager_inactive";
                return false;
            }

            RaycastHits.Clear();
            if (!arRaycastManager.Raycast(screenPoint, RaycastHits, TrackableType.PlaneWithinPolygon))
            {
                status = "ar_raycast_no_plane";
                return false;
            }

            pose = RaycastHits[0].pose;
            surfaceNormal = pose.up;
            if (RaycastHits[0].trackable is ARPlane arPlane)
                surfaceNormal = arPlane.normal;
            status = "ar_raycast_plane";
            return true;
#else
            status = "ar_foundation_not_compiled";
            return false;
#endif
        }

        private void PrepareManifest(AppStartupConfigDto config)
        {
            var active = config ?? AppStartupConfigDto.Default();
            active.Normalize();
            ActiveModelId = string.IsNullOrWhiteSpace(active.model_id)
                ? "GOSLO_default"
                : active.model_id.Trim();

            _manifest = modelReadyReporter != null
                && modelReadyReporter.LastManifest != null
                && string.Equals(modelReadyReporter.LastManifest.model_id, ActiveModelId, System.StringComparison.OrdinalIgnoreCase)
                    ? modelReadyReporter.LastManifest
                    : ModelManifestDto.LoadFromResources(ActiveModelId);
        }

        private void EnsureModelRoot()
        {
            if (modelRoot != null) return;
            var stage = GameObject.Find("AssetPreviewStage");
            if (stage != null)
            {
                modelRoot = stage.transform;
                return;
            }

            var root = new GameObject("FormalModelPlacementRoot");
            root.transform.SetParent(transform, false);
            modelRoot = root.transform;
        }

        private GameObject InstantiateModel()
        {
            string visualSource;
            var go = TryInstantiateManifestVisual(out visualSource);
            if (go == null)
            {
                go = CreateWhiteboxPlaceholder();
                visualSource = "whitebox_placeholder";
            }

            LastVisualSource = visualSource;
            go.name = visualSource == "whitebox_placeholder"
                ? "FormalPlacedModelWhitebox_" + SafeName(ActiveModelId)
                : "FormalPlacedModel_" + SafeName(ActiveModelId);

            var driver = go.GetComponent<ModelDriver>();
            if (driver == null) driver = go.AddComponent<ModelDriver>();
            driver.ConfigureModelId(ActiveModelId);
            driver.BootstrapNow();
            return go;
        }

        private void HandleTouchPlacementAndSelection()
        {
            if (Input.touchCount <= 0)
            {
                _pinchStartDistance = 0f;
                _isDraggingModel = false;
                _touchStartedOnModel = false;
                return;
            }

            if (Input.touchCount >= 2 && enablePinchScale && HasSelectedModel && PlacedModel != null)
            {
                _isDraggingModel = false;
                var a = Input.GetTouch(0);
                var b = Input.GetTouch(1);
                if (IsPointerOverUi(a.fingerId) || IsPointerOverUi(b.fingerId))
                    return;

                float distance = Vector2.Distance(a.position, b.position);
                if (_pinchStartDistance <= 1f || a.phase == UnityEngine.TouchPhase.Began || b.phase == UnityEngine.TouchPhase.Began)
                {
                    _pinchStartDistance = Mathf.Max(1f, distance);
                    _pinchStartScaleMultiplier = ScaleMultiplier;
                    LastSelectionStatus = "pinch_start";
                    return;
                }

                ScaleSelectedModel(_pinchStartScaleMultiplier * distance / Mathf.Max(1f, _pinchStartDistance), "pinch");
                return;
            }

            var touch = Input.GetTouch(0);
            if (touch.phase == UnityEngine.TouchPhase.Began)
            {
                _touchStartPosition = touch.position;
                _touchStartTime = Time.unscaledTime;
                _touchStartedOverUi = IsPointerOverUi(touch.fingerId);
                _touchStartedOnModel = !_touchStartedOverUi && HasPlacedModel && RayIntersectsPlacedModel(touch.position);
                _isDraggingModel = false;
                if (_touchStartedOnModel)
                {
                    SelectPlacedModel(true, "touch_model");
                    CaptureDragOffset(touch.position);
                }
                return;
            }

            if (touch.phase == UnityEngine.TouchPhase.Moved || touch.phase == UnityEngine.TouchPhase.Stationary)
            {
                if (!_touchStartedOverUi && _touchStartedOnModel && enableDragMove && HasSelectedModel && PlacedModel != null)
                {
                    float dragDistance = Vector2.Distance(_touchStartPosition, touch.position);
                    if (_isDraggingModel || dragDistance > tapMaxMovePixels)
                    {
                        _isDraggingModel = TryMoveSelectedModelOnPlane(touch.position, "touch_drag");
                    }
                }
                return;
            }

            if (touch.phase != UnityEngine.TouchPhase.Ended && touch.phase != UnityEngine.TouchPhase.Canceled)
                return;

            if (_touchStartedOverUi || IsPointerOverUi(touch.fingerId))
            {
                _isDraggingModel = false;
                return;
            }

            if (_isDraggingModel)
            {
                _isDraggingModel = false;
                LastSelectionStatus = "drag_end";
                return;
            }

            float elapsed = Time.unscaledTime - _touchStartTime;
            float moved = Vector2.Distance(_touchStartPosition, touch.position);
            if (elapsed > tapMaxSeconds || moved > tapMaxMovePixels)
                return;

            HandleTap(touch.position);
        }

        private void HandleEditorMousePlacementAndSelection()
        {
            if (!Application.isEditor)
                return;

            if (Input.GetMouseButtonDown(0))
            {
                _mouseStartedOverUi = IsPointerOverUi(-1);
                _mouseStartedOnModel = !_mouseStartedOverUi && HasPlacedModel && RayIntersectsPlacedModel(Input.mousePosition);
                _mouseDraggingModel = false;
                if (_mouseStartedOnModel)
                {
                    SelectPlacedModel(true, "mouse_model");
                    CaptureDragOffset(Input.mousePosition);
                }
            }

            if (Input.GetMouseButton(0) && !_mouseStartedOverUi && _mouseStartedOnModel && enableDragMove && HasSelectedModel && PlacedModel != null)
            {
                _mouseDraggingModel = TryMoveSelectedModelOnPlane(Input.mousePosition, "editor_drag");
                return;
            }

            if (Input.GetMouseButtonUp(0) && !_mouseStartedOverUi && !IsPointerOverUi(-1))
            {
                if (_mouseDraggingModel)
                {
                    _mouseDraggingModel = false;
                    LastSelectionStatus = "drag_end";
                    return;
                }
                HandleTap(Input.mousePosition);
            }

            if (HasSelectedModel && enablePinchScale && PlacedModel != null)
            {
                float wheel = Input.mouseScrollDelta.y;
                if (Mathf.Abs(wheel) > 0.001f)
                    ScaleSelectedModel(ScaleMultiplier * (1f + wheel * 0.08f), "editor_wheel");
            }
        }

        private void HandleTap(Vector2 screenPoint)
        {
            if (!HasPlacedModel || PlacedModel == null)
            {
                PlaceAtScreenPoint(screenPoint);
                return;
            }

            if (RayIntersectsPlacedModel(screenPoint))
                SelectPlacedModel(true, "tap_model");
            else if (HasSelectedModel)
                SelectPlacedModel(false, "tap_empty");
        }

#if ENABLE_INPUT_SYSTEM
        private void HandleInputSystemTouchPlacementAndSelection()
        {
            var touches = EnhancedTouch.activeTouches;
            if (touches.Count <= 0)
            {
                ResetActiveTouchGesture();
                return;
            }

            if (touches.Count >= 2 && enablePinchScale && HasSelectedModel && PlacedModel != null)
            {
                _isDraggingModel = false;
                var a = touches[0];
                var b = touches[1];
                if (IsTouchPointerOverUi(a.finger.index) || IsTouchPointerOverUi(b.finger.index))
                    return;

                float distance = Vector2.Distance(a.screenPosition, b.screenPosition);
                if (_pinchStartDistance <= 1f || a.phase == EnhancedTouchPhase.Began || b.phase == EnhancedTouchPhase.Began)
                {
                    _pinchStartDistance = Mathf.Max(1f, distance);
                    _pinchStartScaleMultiplier = ScaleMultiplier;
                    LastSelectionStatus = "pinch_start";
                    return;
                }

                ScaleSelectedModel(_pinchStartScaleMultiplier * distance / Mathf.Max(1f, _pinchStartDistance), "pinch");
                return;
            }

            var touch = touches[0];
            var screenPoint = touch.screenPosition;
            int pointerId = touch.finger.index;
            if (touch.phase == EnhancedTouchPhase.Began)
            {
                _touchStartPosition = screenPoint;
                _touchStartTime = Time.unscaledTime;
                _touchStartedOverUi = IsTouchPointerOverUi(pointerId);
                _touchStartedOnModel = !_touchStartedOverUi && HasPlacedModel && RayIntersectsPlacedModel(screenPoint);
                _isDraggingModel = false;
                if (_touchStartedOnModel)
                {
                    SelectPlacedModel(true, "touch_model");
                    CaptureDragOffset(screenPoint);
                }
                return;
            }

            if (touch.phase == EnhancedTouchPhase.Moved || touch.phase == EnhancedTouchPhase.Stationary)
            {
                if (!_touchStartedOverUi && _touchStartedOnModel && enableDragMove && HasSelectedModel && PlacedModel != null)
                {
                    float moved = Vector2.Distance(_touchStartPosition, screenPoint);
                    if (_isDraggingModel || moved > tapMaxMovePixels)
                        _isDraggingModel = TryMoveSelectedModelOnPlane(screenPoint, "touch_drag");
                }
                return;
            }

            if (touch.phase != EnhancedTouchPhase.Ended && touch.phase != EnhancedTouchPhase.Canceled)
                return;

            if (_touchStartedOverUi || IsTouchPointerOverUi(pointerId))
            {
                _isDraggingModel = false;
                return;
            }

            if (_isDraggingModel)
            {
                _isDraggingModel = false;
                LastSelectionStatus = "drag_end";
                return;
            }

            float elapsed = Time.unscaledTime - _touchStartTime;
            float movedDistance = Vector2.Distance(_touchStartPosition, screenPoint);
            if (elapsed > tapMaxSeconds || movedDistance > tapMaxMovePixels)
                return;

            HandleTap(screenPoint);
        }

        private void HandleInputSystemMousePlacementAndSelection()
        {
            if (!Application.isEditor || Mouse.current == null)
                return;

            var mouse = Mouse.current;
            Vector2 screenPoint = mouse.position.ReadValue();
            if (mouse.leftButton.wasPressedThisFrame)
            {
                _mouseStartedOverUi = IsPointerOverUi(-1);
                _mouseStartedOnModel = !_mouseStartedOverUi && HasPlacedModel && RayIntersectsPlacedModel(screenPoint);
                _mouseDraggingModel = false;
                if (_mouseStartedOnModel)
                {
                    SelectPlacedModel(true, "mouse_model");
                    CaptureDragOffset(screenPoint);
                }
            }

            if (mouse.leftButton.isPressed && !_mouseStartedOverUi && _mouseStartedOnModel && enableDragMove && HasSelectedModel && PlacedModel != null)
            {
                _mouseDraggingModel = TryMoveSelectedModelOnPlane(screenPoint, "editor_drag");
                return;
            }

            if (mouse.leftButton.wasReleasedThisFrame && !_mouseStartedOverUi && !IsPointerOverUi(-1))
            {
                if (_mouseDraggingModel)
                {
                    _mouseDraggingModel = false;
                    LastSelectionStatus = "drag_end";
                    return;
                }
                HandleTap(screenPoint);
            }

            if (HasSelectedModel && enablePinchScale && PlacedModel != null)
            {
                float wheel = mouse.scroll.ReadValue().y;
                if (Mathf.Abs(wheel) > 0.001f)
                    ScaleSelectedModel(ScaleMultiplier * (1f + wheel * 0.0008f), "editor_wheel");
            }
        }
#endif

        private void ResetActiveTouchGesture()
        {
            _pinchStartDistance = 0f;
            _isDraggingModel = false;
            _touchStartedOnModel = false;
        }

        private void CaptureDragOffset(Vector2 screenPoint)
        {
            _dragWorldOffset = Vector3.zero;
            if (PlacedModel == null) return;
            if (!TryResolveArRaycastPose(screenPoint, out Pose pose, out Vector3 surfaceNormal, out _))
                return;

            _dragWorldOffset = Vector3.ProjectOnPlane(PlacedModel.transform.position - pose.position, surfaceNormal);
        }

        private bool TryMoveSelectedModelOnPlane(Vector2 screenPoint, string reason)
        {
            if (PlacedModel == null) return false;
            if (!TryResolveArRaycastPose(screenPoint, out Pose pose, out Vector3 surfaceNormal, out string status))
            {
                LastSelectionStatus = ShortReason(status);
                return false;
            }

            Vector3 offset = Vector3.ProjectOnPlane(_dragWorldOffset, surfaceNormal);
            PlacedModel.transform.position = pose.position + offset;
            LastPlacementMode = "ar_drag";
            LastPlacementStatus = "placed:ar_drag_plane";
            LastSelectionStatus = "dragging:" + ShortReason(reason);
            return true;
        }

        private bool RayIntersectsPlacedModel(Vector2 screenPoint)
        {
            if (PlacedModel == null) return false;
            if (placementCamera == null) placementCamera = Camera.main;
            if (placementCamera == null) return false;

            var ray = placementCamera.ScreenPointToRay(screenPoint);
            Bounds bounds;
            if (!TryGetPlacedModelBounds(out bounds))
            {
                bounds = new Bounds(PlacedModel.transform.position, Vector3.one * 0.25f);
            }
            return bounds.IntersectRay(ray);
        }

        private bool TryGetPlacedModelBounds(out Bounds bounds)
        {
            bounds = new Bounds();
            if (PlacedModel == null) return false;
            var renderers = PlacedModel.GetComponentsInChildren<Renderer>(true);
            bool hasBounds = false;
            for (int i = 0; i < renderers.Length; i++)
            {
                var renderer = renderers[i];
                if (renderer == null || !renderer.enabled) continue;
                if (!hasBounds)
                {
                    bounds = renderer.bounds;
                    hasBounds = true;
                }
                else
                {
                    bounds.Encapsulate(renderer.bounds);
                }
            }
            return hasBounds;
        }

        private void ApplyScaleMultiplier()
        {
            if (PlacedModel == null) return;
            if (_placedBaseScale.sqrMagnitude < 0.0001f)
                _placedBaseScale = PlacedModel.transform.localScale;
            PlacedModel.transform.localScale = _placedBaseScale * ScaleMultiplier;
        }

        private void PlayPlacementGreeting()
        {
            var animationDriver = PlacedModel != null ? PlacedModel.GetComponentInChildren<AnimationDriver>(true) : null;
            if (animationDriver != null)
            {
                animationDriver.SetState(AnimationDriver.BodyState.HeadBob);
                animationDriver.SetHeadState(AnimationDriver.HeadState.Tilt);
                LastSelectionStatus = "greeting:animation_driver";
                return;
            }

            string modelId = ActiveModelId;
            var controller = ParrotRegistry.Instance != null ? ParrotRegistry.Instance.Resolve(modelId) : null;
            if (controller != null)
            {
                if (Supports(controller, "spine_idle"))
                    controller.ApplyCapability("spine_idle", "{}");
                if (Supports(controller, "face_serious"))
                    controller.ApplyCapability("face_serious", "{}");
                LastSelectionStatus = "greeting:model_controller";
            }
        }

        private void UpdateSelectionVisual()
        {
            if (!HasSelectedModel || PlacedModel == null)
                return;

            Bounds bounds;
            if (!TryGetPlacedModelBounds(out bounds))
                bounds = new Bounds(PlacedModel.transform.position, Vector3.one * 0.25f);

            if (_selectionVisual == null)
            {
                _selectionVisual = GameObject.CreatePrimitive(PrimitiveType.Cylinder);
                _selectionVisual.name = "FormalPlacedModelSelectionRing";
                var collider = _selectionVisual.GetComponent<Collider>();
                if (collider != null) Destroy(collider);
                var renderer = _selectionVisual.GetComponent<Renderer>();
                if (renderer != null)
                    renderer.material = SelectionVisualMaterial();
            }

            float radius = Mathf.Clamp(Mathf.Max(bounds.extents.x, bounds.extents.z) * 1.25f, 0.08f, 1.25f);
            _selectionVisual.transform.position = new Vector3(bounds.center.x, bounds.min.y + 0.012f, bounds.center.z);
            _selectionVisual.transform.rotation = Quaternion.identity;
            _selectionVisual.transform.localScale = new Vector3(radius * 2f, 0.004f, radius * 2f);
        }

        private void DestroySelectionVisual()
        {
            if (_selectionVisual != null)
            {
                Destroy(_selectionVisual);
                _selectionVisual = null;
            }
        }

        private Material SelectionVisualMaterial()
        {
            if (_selectionVisualMaterial != null) return _selectionVisualMaterial;
            var shader = Shader.Find("Sprites/Default") ?? Shader.Find("Universal Render Pipeline/Unlit") ?? Shader.Find("Standard");
            if (shader == null)
                shader = Shader.Find("UI/Default");
            if (shader == null)
                shader = Shader.Find("Hidden/Internal-Colored");
            _selectionVisualMaterial = new Material(shader);
            _selectionVisualMaterial.color = new Color(0.95f, 0.72f, 0.32f, 0.62f);
            _selectionVisualMaterial.renderQueue = 3000;
            return _selectionVisualMaterial;
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

        private static bool IsPointerOverUi(int pointerId)
        {
            if (EventSystem.current == null) return false;
            return pointerId >= 0
                ? EventSystem.current.IsPointerOverGameObject(pointerId)
                : EventSystem.current.IsPointerOverGameObject();
        }

#if ENABLE_INPUT_SYSTEM
        private static bool IsTouchPointerOverUi(int pointerId)
        {
            return IsPointerOverUi(pointerId) || IsPointerOverUi(-1);
        }
#endif

        private GameObject TryInstantiateManifestVisual(out string visualSource)
        {
            visualSource = "asset_path_missing";
            if (_manifest == null || string.IsNullOrWhiteSpace(_manifest.asset_path))
                return null;

            string path = _manifest.asset_path.Trim();
            var prefab = Resources.Load<GameObject>(path);
            if (prefab != null)
            {
                visualSource = "resource_gameobject:" + path;
                return Instantiate(prefab);
            }

            var resource = Resources.Load<UnityEngine.Object>(path);
            if (resource == null)
            {
                visualSource = "resource_missing:" + path;
                return null;
            }

            var spineVisual = TryCreateSpineSkeletonVisual(resource);
            if (spineVisual != null)
            {
                visualSource = "resource_spine_skeleton:" + path;
                return spineVisual;
            }

            visualSource = "resource_unhandled:" + resource.GetType().FullName;
            return null;
        }

        private static GameObject TryCreateSpineSkeletonVisual(UnityEngine.Object resource)
        {
            if (resource == null || resource.GetType().FullName != "Spine.Unity.SkeletonDataAsset")
                return null;

            Type spineType = FindTypeByFullName("Spine.Unity.SkeletonAnimation");
            if (spineType == null || !typeof(Component).IsAssignableFrom(spineType))
                return null;

            var go = new GameObject("FormalPlacedSpineVisual");
            var component = go.AddComponent(spineType);
            if (!TryAssignSpineSkeletonDataAsset(component, resource))
            {
                UnityEngine.Object.Destroy(go);
                return null;
            }

            TryInitializeSpineSkeleton(component);
            return go;
        }

        private static bool TryAssignSpineSkeletonDataAsset(Component component, UnityEngine.Object resource)
        {
            var type = component.GetType();
            var property = type.GetProperty(
                "SkeletonDataAsset",
                BindingFlags.Instance | BindingFlags.Public | BindingFlags.NonPublic);
            if (property != null && property.CanWrite && property.PropertyType.IsInstanceOfType(resource))
            {
                property.SetValue(component, resource, null);
                return true;
            }

            var field = type.GetField(
                "skeletonDataAsset",
                BindingFlags.Instance | BindingFlags.Public | BindingFlags.NonPublic);
            if (field != null && field.FieldType.IsInstanceOfType(resource))
            {
                field.SetValue(component, resource);
                return true;
            }

            return false;
        }

        private static void TryInitializeSpineSkeleton(Component component)
        {
            var type = component.GetType();
            var initialize = type.GetMethod(
                "Initialize",
                BindingFlags.Instance | BindingFlags.Public | BindingFlags.NonPublic,
                null,
                new[] { typeof(bool) },
                null);
            try
            {
                initialize?.Invoke(component, new object[] { true });
            }
            catch (Exception ex)
            {
                Debug.LogWarning("[FormalModelPlacement] Spine visual Initialize failed: " + ex.Message);
            }
        }

        private static Type FindTypeByFullName(string fullName)
        {
            var assemblies = AppDomain.CurrentDomain.GetAssemblies();
            for (int i = 0; i < assemblies.Length; i++)
            {
                try
                {
                    var type = assemblies[i].GetType(fullName);
                    if (type != null) return type;
                }
                catch
                {
                    // Some Unity editor assemblies can throw during reflection.
                    // They are irrelevant to optional Spine visual creation.
                }
            }
            return null;
        }

        private GameObject CreateWhiteboxPlaceholder()
        {
            var go = GameObject.CreatePrimitive(PrimitiveType.Capsule);
            var collider = go.GetComponent<Collider>();
            if (collider != null) Destroy(collider);

            float targetHeight = _manifest != null && _manifest.default_pet_height_m > 0f
                ? _manifest.default_pet_height_m
                : 0.24f;
            go.transform.localScale = new Vector3(targetHeight * 0.45f, targetHeight * 0.5f, targetHeight * 0.45f);

            var renderer = go.GetComponent<Renderer>();
            if (renderer != null)
            {
                var shader = Shader.Find("Universal Render Pipeline/Lit") ?? Shader.Find("Standard");
                if (shader != null)
                {
                    var material = new Material(shader);
                    material.color = new Color(0.90f, 0.82f, 0.66f, 1f);
                    renderer.material = material;
                }
            }
            return go;
        }

        private Vector3 ResolveDefaultPosition()
        {
            if (placementCamera == null) placementCamera = Camera.main;
            if (placementCamera == null) return fallbackPosition;
            return placementCamera.transform.position + placementCamera.transform.forward * Mathf.Max(0.35f, defaultDistanceMeters);
        }

        private Quaternion ResolveDefaultRotation(Vector3 position)
        {
            if (placementCamera == null) placementCamera = Camera.main;
            if (placementCamera == null) return Quaternion.identity;

            Vector3 look = placementCamera.transform.position - position;
            look.y = 0f;
            if (look.sqrMagnitude < 0.0001f) return Quaternion.identity;
            return Quaternion.LookRotation(look.normalized, Vector3.up);
        }

        private Quaternion ResolveDemoSpawnRotation(Vector3 position, Vector3 surfaceNormal)
        {
            if (placementCamera == null) placementCamera = Camera.main;

            Vector3 normal = surfaceNormal.sqrMagnitude > 0.0001f
                ? surfaceNormal.normalized
                : Vector3.up;
            if (placementCamera == null)
                return Quaternion.LookRotation(ResolvePlaneTangent(normal), normal);

            Vector3 forward = placementCamera.transform.position - position;
            forward = Vector3.ProjectOnPlane(forward, normal);
            if (forward.sqrMagnitude < 0.0001f)
                forward = Vector3.ProjectOnPlane(-placementCamera.transform.forward, normal);
            if (forward.sqrMagnitude < 0.0001f)
                forward = ResolvePlaneTangent(normal);

            var rotation = Quaternion.LookRotation(forward.normalized, normal);
            if (applyDemoRandomAngleAtSpawn && demoSpawnAngleRangeDegrees > 0.001f)
                rotation *= Quaternion.AngleAxis(UnityEngine.Random.Range(-demoSpawnAngleRangeDegrees, demoSpawnAngleRangeDegrees), Vector3.up);
            return rotation;
        }

        private static Vector3 ResolvePlaneTangent(Vector3 normal)
        {
            Vector3 tangent = Vector3.ProjectOnPlane(Vector3.forward, normal);
            if (tangent.sqrMagnitude < 0.0001f)
                tangent = Vector3.ProjectOnPlane(Vector3.right, normal);
            if (tangent.sqrMagnitude < 0.0001f)
                tangent = Vector3.Cross(normal, Vector3.up);
            if (tangent.sqrMagnitude < 0.0001f)
                tangent = Vector3.Cross(normal, Vector3.right);
            return tangent.sqrMagnitude < 0.0001f ? Vector3.forward : tangent.normalized;
        }

        private static string SafeName(string raw)
        {
            if (string.IsNullOrWhiteSpace(raw)) return "model";
            var chars = raw.Trim().ToCharArray();
            for (int i = 0; i < chars.Length; i++)
            {
                if (!char.IsLetterOrDigit(chars[i]) && chars[i] != '_' && chars[i] != '-')
                    chars[i] = '_';
            }
            return new string(chars);
        }

        private static string ShortReason(string raw)
        {
            if (string.IsNullOrWhiteSpace(raw)) return "unknown";
            raw = raw.Trim();
            return raw.Length <= 40 ? raw : raw.Substring(0, 40);
        }
    }
}
