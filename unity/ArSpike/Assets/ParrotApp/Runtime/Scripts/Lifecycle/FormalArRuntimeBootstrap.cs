using System;
using System.Collections;
using System.Collections.Generic;
using UnityEngine;
using UnityEngine.XR.Management;

#if ENABLE_INPUT_SYSTEM
using UnityEngine.InputSystem;
using UnityEngine.InputSystem.UI;
using UnityEngine.InputSystem.XR;
using UnityEngine.XR.Interaction.Toolkit.Inputs;
#endif

#if UNITY_AR_FOUNDATION
using Unity.XR.CoreUtils;
using UnityEngine.EventSystems;
using UnityEngine.XR.ARFoundation;
using UnityEngine.XR.ARSubsystems;
using UnityEngine.XR.Interaction.Toolkit;
using UnityEngine.XR.Interaction.Toolkit.AR.Inputs;
using UnityEngine.XR.Interaction.Toolkit.Interactors;
using UnityEngine.XR.Interaction.Toolkit.Samples.ARStarterAssets;
using UnityEngine.XR.Interaction.Toolkit.Samples.StarterAssets;
using UnityEngine.XR.Interaction.Toolkit.UI;
#endif

namespace ParrotApp.Lifecycle
{
    /// <summary>
    /// Mounts the minimal AR Foundation runtime services expected by the
    /// formal mobile App scene.
    ///
    /// The startup scene is assembled from runtime services rather than a
    /// template AR scene. Without this bootstrap, Android FullAR START can pass
    /// transport and still never produce ARCameraManager frames.
    /// </summary>
    [DisallowMultipleComponent]
    public class FormalArRuntimeBootstrap : MonoBehaviour
    {
        [SerializeField] private Camera arCamera;
        [SerializeField] private bool bootstrapOnAwake = false;
        [SerializeField] private bool createArSessionObject = true;
        [SerializeField] private bool attachCameraManagers = true;
        [SerializeField] private bool mountXrOriginAndPlacementManagers = true;
        [SerializeField] private bool mountPlaneAndPointCloudVisuals = true;
        [SerializeField] private string arTemplatePlanePrefabResourcePath = "ARMobileTemplate/Prefabs/ARFeatheredPlane";
        [SerializeField] private bool mountArMobileTemplateInteraction = true;
        [SerializeField] private string arTemplateInputActionsResourcePath = "ARMobileTemplate/XRIStarterAssets/XRI Default Input Actions";
        [SerializeField] private string arTemplateScreenRayInteractorResourcePath = "ARMobileTemplate/XRIStarterAssets/Screen Space Ray Interactor";
        [SerializeField] private bool showArMobileTemplatePlaneSurfaces = true;
        [SerializeField] private bool manageXrLifecycle = true;
        [SerializeField] private bool skipXrLifecycleInEditor = true;

        public bool ArFoundationCompiled
        {
            get
            {
#if UNITY_AR_FOUNDATION
                return true;
#else
                return false;
#endif
            }
        }

        public bool SessionMounted { get; private set; }
        public bool CameraManagersMounted { get; private set; }
        public bool XrOriginMounted { get; private set; }
        public bool PlacementManagersMounted { get; private set; }
        public bool SpatialVisualsMounted { get; private set; }
        public bool ArMobileTemplateInteractionMounted { get; private set; }
        public bool XrLifecycleReady { get; private set; }
        public bool XrLifecycleRequired { get; private set; }
        public bool XrLifecycleFailed { get; private set; }
        public string LastStatus { get; private set; } = "";
        public string LastSpatialVisualStatus { get; private set; } = "not_mounted";
        public string LastPlaneMaterialStatus { get; private set; } = "not_seen";
        public string LastTemplateInteractionStatus { get; private set; } = "not_mounted";

        private bool _xrStartInProgress;
        private bool _startedXrSubsystems;
        private bool _initializedXrLoader;

#if UNITY_AR_FOUNDATION
        private ARPlaneManager _planeManager;
        private readonly List<ARFeatheredPlaneMeshVisualizerCompanion> _planeVisualCompanions =
            new List<ARFeatheredPlaneMeshVisualizerCompanion>();
        private GameObject _templateScreenRayInteractor;
        private GameObject _templateSpawnProxy;
        private ObjectSpawner _templateObjectSpawner;
        private ARInteractorSpawnTrigger _templateSpawnTrigger;
#endif

        private void Awake()
        {
            if (bootstrapOnAwake)
                EnsureArRuntime();
        }

        private void Start()
        {
            if (bootstrapOnAwake)
                EnsureArRuntime();
        }

        private void OnDestroy()
        {
#if UNITY_AR_FOUNDATION
            UnbindSpatialVisuals();
#endif
            StopManagedXrLifecycle();
        }

        public void EnsureArRuntime()
        {
#if UNITY_AR_FOUNDATION
            XrOriginMounted = EnsureXrOrigin();
            SessionMounted = EnsureSession();
            CameraManagersMounted = EnsureCameraManagers();
            PlacementManagersMounted = EnsurePlacementManagers();
            LastStatus = $"ar_runtime_bootstrap origin={XrOriginMounted} session={SessionMounted} camera={CameraManagersMounted} placement={PlacementManagersMounted} spatial={SpatialVisualsMounted} template_xri={ArMobileTemplateInteractionMounted}";
#else
            XrOriginMounted = false;
            SessionMounted = false;
            CameraManagersMounted = false;
            PlacementManagersMounted = false;
            SpatialVisualsMounted = false;
            ArMobileTemplateInteractionMounted = false;
            LastStatus = "unity_ar_foundation_symbol_missing";
            Debug.LogWarning("[FormalArRuntimeBootstrap] UNITY_AR_FOUNDATION is not defined; AR runtime was not mounted.");
#endif
        }

        public IEnumerator EnsureArRuntimeReady()
        {
#if UNITY_AR_FOUNDATION
            yield return EnsureXrLifecycleReady();
            if (XrLifecycleFailed)
                yield break;
            EnsureArRuntime();
#else
            EnsureArRuntime();
            yield break;
#endif
        }

        private IEnumerator EnsureXrLifecycleReady()
        {
            XrLifecycleRequired = ShouldManageXrLifecycle();
            if (!XrLifecycleRequired)
            {
                XrLifecycleReady = true;
                XrLifecycleFailed = false;
                yield break;
            }

            while (_xrStartInProgress)
                yield return null;

            if (XrLifecycleReady)
                yield break;

            _xrStartInProgress = true;
            XrLifecycleFailed = false;

            var generalSettings = XRGeneralSettings.Instance;
            var manager = generalSettings != null ? generalSettings.Manager : null;
            if (manager == null)
            {
                LastStatus = "xr_manager_missing";
                XrLifecycleFailed = true;
                _xrStartInProgress = false;
                yield break;
            }

            if (!manager.isInitializationComplete)
            {
                yield return manager.InitializeLoader();
                _initializedXrLoader = manager.isInitializationComplete;
            }

            if (!manager.isInitializationComplete || manager.activeLoader == null)
            {
                LastStatus = "xr_loader_initialize_failed";
                XrLifecycleFailed = true;
                _xrStartInProgress = false;
                yield break;
            }

            manager.StartSubsystems();
            _startedXrSubsystems = true;
            XrLifecycleReady = true;
            LastStatus = "xr_lifecycle_ready:" + manager.activeLoader.name;
            _xrStartInProgress = false;
        }

        private bool ShouldManageXrLifecycle()
        {
            if (!manageXrLifecycle)
                return false;
            if (skipXrLifecycleInEditor && Application.isEditor)
                return false;
            return Application.isMobilePlatform;
        }

        private void StopManagedXrLifecycle()
        {
            if (!_initializedXrLoader && !_startedXrSubsystems)
                return;

            var generalSettings = XRGeneralSettings.Instance;
            var manager = generalSettings != null ? generalSettings.Manager : null;
            if (manager == null || !manager.isInitializationComplete)
                return;

            if (_startedXrSubsystems)
                manager.StopSubsystems();
            if (_initializedXrLoader)
                manager.DeinitializeLoader();

            _startedXrSubsystems = false;
            _initializedXrLoader = false;
            XrLifecycleReady = false;
        }

#if UNITY_AR_FOUNDATION
        private bool EnsureXrOrigin()
        {
            if (!mountXrOriginAndPlacementManagers)
                return FindObjectOfType<XROrigin>() != null;

            if (arCamera == null)
                arCamera = Camera.main;

            var origin = FindObjectOfType<XROrigin>();
            if (origin == null)
            {
                var go = new GameObject("FormalXROrigin");
                go.transform.SetParent(transform, false);
                origin = go.AddComponent<XROrigin>();
            }

            if (origin.CameraFloorOffsetObject == null)
            {
                var offset = new GameObject("FormalARCameraOffset");
                offset.transform.SetParent(origin.transform, false);
                origin.CameraFloorOffsetObject = offset;
            }

            origin.Origin = origin.gameObject;
            origin.RequestedTrackingOriginMode = XROrigin.TrackingOriginMode.Device;
            origin.CameraYOffset = 0f;
            if (origin.CameraFloorOffsetObject != null)
                origin.CameraFloorOffsetObject.transform.localPosition = Vector3.zero;

            if (arCamera != null)
            {
                origin.Camera = arCamera;
                if (arCamera.transform.GetComponentInParent<XROrigin>() != origin)
                    arCamera.transform.SetParent(origin.CameraFloorOffsetObject.transform, worldPositionStays: true);
            }

            return origin != null && origin.Camera != null;
        }

        private bool EnsureSession()
        {
            if (!createArSessionObject)
                return FindObjectOfType<ARSession>() != null;

            var session = FindObjectOfType<ARSession>();
            if (session == null)
            {
                var go = new GameObject("FormalARSession");
                go.transform.SetParent(transform, false);
                session = go.AddComponent<ARSession>();
                EnsureArInputManager(go);
            }
            else
            {
                EnsureArInputManager(session.gameObject);
            }

            session.enabled = true;
            return true;
        }

        private bool EnsureCameraManagers()
        {
            if (!attachCameraManagers)
                return true;

            if (arCamera == null)
                arCamera = Camera.main;
            if (arCamera == null)
            {
                LastStatus = "ar_camera_missing";
                Debug.LogWarning("[FormalArRuntimeBootstrap] Main AR camera is missing.");
                return false;
            }

            if (arCamera.GetComponent<ARCameraManager>() == null)
                arCamera.gameObject.AddComponent<ARCameraManager>();
            if (arCamera.GetComponent<ARCameraBackground>() == null)
                arCamera.gameObject.AddComponent<ARCameraBackground>();
            EnsureTrackedPoseDriver(arCamera);
            return true;
        }

        private static void EnsureTrackedPoseDriver(Camera camera)
        {
            if (camera == null) return;
#if ENABLE_INPUT_SYSTEM
            if (camera.GetComponent<TrackedPoseDriver>() != null)
                return;

            var driver = camera.gameObject.AddComponent<TrackedPoseDriver>();
            var positionAction = new InputAction("Position", binding: "<XRHMD>/centerEyePosition", expectedControlType: "Vector3");
            positionAction.AddBinding("<HandheldARInputDevice>/devicePosition");
            var rotationAction = new InputAction("Rotation", binding: "<XRHMD>/centerEyeRotation", expectedControlType: "Quaternion");
            rotationAction.AddBinding("<HandheldARInputDevice>/deviceRotation");
            driver.positionInput = new InputActionProperty(positionAction);
            driver.rotationInput = new InputActionProperty(rotationAction);
#endif
        }

        private bool EnsurePlacementManagers()
        {
            if (!mountXrOriginAndPlacementManagers)
                return true;

            var origin = FindObjectOfType<XROrigin>();
            if (origin == null)
            {
                LastStatus = "xr_origin_missing_for_placement";
                return false;
            }

            if (origin.GetComponent<ARRaycastManager>() == null)
                origin.gameObject.AddComponent<ARRaycastManager>();
            if (origin.GetComponent<ARPlaneManager>() == null)
                origin.gameObject.AddComponent<ARPlaneManager>();

            SpatialVisualsMounted = BindSpatialVisuals(origin);
            ArMobileTemplateInteractionMounted = EnsureArMobileTemplateInteraction(origin);
            return true;
        }

        private bool BindSpatialVisuals(XROrigin origin)
        {
            if (!mountPlaneAndPointCloudVisuals || origin == null)
            {
                LastSpatialVisualStatus = "disabled";
                return false;
            }

            _planeManager = origin.GetComponent<ARPlaneManager>();
            if (_planeManager == null)
            {
                LastSpatialVisualStatus = "manager_missing";
                return false;
            }

            return ConfigureArMobileTemplatePlane(_planeManager);
        }

        private void UnbindSpatialVisuals()
        {
            if (_planeManager != null)
                _planeManager.planesChanged -= HandlePlanesChanged;
            _planeManager = null;
            _planeVisualCompanions.Clear();
        }

        private bool ConfigureArMobileTemplatePlane(ARPlaneManager planeManager)
        {
            var prefab = Resources.Load<GameObject>(arTemplatePlanePrefabResourcePath);
            if (prefab == null)
            {
                LastSpatialVisualStatus = "ar_mobile_template_plane_missing:" + arTemplatePlanePrefabResourcePath;
                Debug.LogWarning("[FormalArRuntimeBootstrap] Missing AR Mobile template plane prefab at Resources/" + arTemplatePlanePrefabResourcePath + ".");
                return false;
            }

            // Match the Unity AR Mobile template: detected planes are rendered by
            // its feathered plane prefab instead of an App-owned debug mesh.
            planeManager.planePrefab = prefab;
            // Demo2 serializes ARPlaneManager.m_DetectionMode as -1. AR Foundation
            // 5.2.2 exposes only Horizontal/Vertical names, so keep the template
            // value explicitly instead of inventing an App-specific mode.
            planeManager.requestedDetectionMode = (PlaneDetectionMode)(-1);
            planeManager.planesChanged -= HandlePlanesChanged;
            planeManager.planesChanged += HandlePlanesChanged;
            SyncPlaneSurfaceVisibility();
            LastSpatialVisualStatus = "ar_mobile_template_plane:" + arTemplatePlanePrefabResourcePath
                                      + ":surface=" + (showArMobileTemplatePlaneSurfaces ? "on" : "dots");
            RefreshPlaneMaterialStatus();
            return true;
        }

        private void HandlePlanesChanged(ARPlanesChangedEventArgs eventArgs)
        {
            if (eventArgs.added != null)
            {
                for (int i = 0; i < eventArgs.added.Count; i++)
                    TrackPlaneVisualizer(eventArgs.added[i]);
            }

            if (eventArgs.removed != null)
            {
                for (int i = 0; i < eventArgs.removed.Count; i++)
                    UntrackPlaneVisualizer(eventArgs.removed[i]);
            }

            SyncPlaneSurfaceVisibility();
        }

        private void SyncPlaneSurfaceVisibility()
        {
            if (_planeManager == null)
                return;

            if (_planeVisualCompanions.Count != _planeManager.trackables.count)
            {
                _planeVisualCompanions.Clear();
                foreach (var plane in _planeManager.trackables)
                    TrackPlaneVisualizer(plane);
            }

            for (int i = 0; i < _planeVisualCompanions.Count; i++)
            {
                if (_planeVisualCompanions[i] != null)
                    _planeVisualCompanions[i].visualizeSurfaces = showArMobileTemplatePlaneSurfaces;
            }
            RefreshPlaneMaterialStatus();
        }

        private void RefreshPlaneMaterialStatus()
        {
            LastPlaneMaterialStatus = "planes=" + _planeVisualCompanions.Count;
            for (int i = 0; i < _planeVisualCompanions.Count; i++)
            {
                var visualizer = _planeVisualCompanions[i];
                if (visualizer == null)
                    continue;
                LastPlaneMaterialStatus += ":" + visualizer.materialDebugSummary;
                return;
            }
        }

        private void TrackPlaneVisualizer(ARPlane plane)
        {
            if (plane == null)
                return;
            if (!plane.TryGetComponent(out ARFeatheredPlaneMeshVisualizerCompanion visualizer))
                return;
            if (!_planeVisualCompanions.Contains(visualizer))
                _planeVisualCompanions.Add(visualizer);
            visualizer.visualizeSurfaces = showArMobileTemplatePlaneSurfaces;
        }

        private void UntrackPlaneVisualizer(ARPlane plane)
        {
            if (plane == null)
                return;
            if (plane.TryGetComponent(out ARFeatheredPlaneMeshVisualizerCompanion visualizer))
                _planeVisualCompanions.Remove(visualizer);
        }

        private bool EnsureArMobileTemplateInteraction(XROrigin origin)
        {
            if (!mountArMobileTemplateInteraction)
            {
                LastTemplateInteractionStatus = "disabled";
                return false;
            }

            if (origin == null)
            {
                LastTemplateInteractionStatus = "xr_origin_missing";
                return false;
            }

            bool inputReady = EnsureTemplateInputActions(origin);
            bool uiReady = EnsureTemplateEventSystem(origin.Camera != null ? origin.Camera : Camera.main);
            var rayInteractor = EnsureTemplateScreenRayInteractor(origin);
            if (rayInteractor == null)
                return false;

            var placement = FindObjectOfType<FormalModelPlacementController>();
            if (placement != null)
                placement.SetTemplateXriInteractionActive(true, "ar_mobile_template_xri");

            bool spawnerReady = EnsureTemplateObjectSpawner(origin, rayInteractor, placement);
            LastTemplateInteractionStatus = "xri_template input=" + inputReady + " ui=" + uiReady + " interactor=mounted spawner=" + spawnerReady;
            if (placement != null)
                placement.ReportTemplateXriStatus(LastTemplateInteractionStatus);
            return inputReady && uiReady && spawnerReady;
        }

        private bool EnsureTemplateInputActions(XROrigin origin)
        {
#if ENABLE_INPUT_SYSTEM
            var asset = Resources.Load<InputActionAsset>(arTemplateInputActionsResourcePath);
            if (asset == null)
            {
                LastTemplateInteractionStatus = "input_actions_missing:" + arTemplateInputActionsResourcePath;
                return false;
            }

            var manager = origin.GetComponent<InputActionManager>();
            if (manager == null)
                manager = origin.gameObject.AddComponent<InputActionManager>();

            if (manager.actionAssets == null)
                manager.actionAssets = new List<InputActionAsset>();

            bool hasAsset = false;
            for (int i = 0; i < manager.actionAssets.Count; i++)
            {
                if (manager.actionAssets[i] == asset)
                {
                    hasAsset = true;
                    break;
                }
            }

            if (!hasAsset)
                manager.actionAssets.Add(asset);

            if (manager.isActiveAndEnabled)
                manager.EnableInput();
            return true;
#else
            LastTemplateInteractionStatus = "input_system_disabled";
            return false;
#endif
        }

        private bool EnsureTemplateEventSystem(Camera uiCamera)
        {
            var eventSystem = EventSystem.current != null
                ? EventSystem.current
                : FindObjectOfType<EventSystem>();
            if (eventSystem == null)
            {
                var go = new GameObject("EventSystem");
                eventSystem = go.AddComponent<EventSystem>();
            }

#if ENABLE_INPUT_SYSTEM
            // The AR Mobile template uses XRUIInputModule. The startup UI may
            // have created InputSystemUIInputModule earlier; keep only the XRI
            // module active once the formal AR workspace is mounted so screen
            // ray select attempts match the template scene.
            var inputSystemUiModule = eventSystem.GetComponent<InputSystemUIInputModule>();
            if (inputSystemUiModule != null)
                inputSystemUiModule.enabled = false;
#endif

            var standaloneModule = eventSystem.GetComponent<StandaloneInputModule>();
            if (standaloneModule != null)
                standaloneModule.enabled = false;

            var xrModule = eventSystem.GetComponent<XRUIInputModule>();
            if (xrModule == null)
                xrModule = eventSystem.gameObject.AddComponent<XRUIInputModule>();

            xrModule.enabled = true;
            xrModule.uiCamera = uiCamera;
            xrModule.clickSpeed = 0.3f;
            xrModule.moveDeadzone = 0.6f;
            xrModule.repeatDelay = 0.5f;
            xrModule.repeatRate = 0.1f;
            xrModule.trackedDeviceDragThresholdMultiplier = 2f;
            xrModule.trackedScrollDeltaMultiplier = 5f;
            xrModule.enableXRInput = true;
            xrModule.enableMouseInput = true;
            xrModule.enableTouchInput = true;
            xrModule.enableGamepadInput = true;
            xrModule.enableJoystickInput = true;
            xrModule.enableBuiltinActionsAsFallback = true;

#if ENABLE_INPUT_SYSTEM
            var asset = Resources.Load<InputActionAsset>(arTemplateInputActionsResourcePath);
            if (asset != null)
                AssignTemplateUiActions(xrModule, asset);
#endif

            return xrModule.isActiveAndEnabled;
        }

#if ENABLE_INPUT_SYSTEM
        private static void AssignTemplateUiActions(XRUIInputModule module, InputActionAsset asset)
        {
            if (module == null || asset == null)
                return;

            var map = asset.FindActionMap("XRI UI", throwIfNotFound: false);
            if (map == null)
                return;

            AssignActionReference(action => module.pointAction = action, map, "Point");
            AssignActionReference(action => module.leftClickAction = action, map, "Click");
            AssignActionReference(action => module.middleClickAction = action, map, "MiddleClick");
            AssignActionReference(action => module.rightClickAction = action, map, "RightClick");
            AssignActionReference(action => module.scrollWheelAction = action, map, "ScrollWheel");
            AssignActionReference(action => module.navigateAction = action, map, "Navigate");
            AssignActionReference(action => module.submitAction = action, map, "Submit");
            AssignActionReference(action => module.cancelAction = action, map, "Cancel");
        }

        private static void AssignActionReference(Action<InputActionReference> assign, InputActionMap map, string actionName)
        {
            var action = map != null ? map.FindAction(actionName, throwIfNotFound: false) : null;
            if (action == null)
                return;

            assign(InputActionReference.Create(action));
        }
#endif

        private XRRayInteractor EnsureTemplateScreenRayInteractor(XROrigin origin)
        {
            if (_templateScreenRayInteractor == null)
            {
                var existing = FindTemplateScreenRayInteractor(origin);
                if (existing != null)
                    _templateScreenRayInteractor = existing.gameObject;
            }

            if (_templateScreenRayInteractor == null)
            {
                var prefab = Resources.Load<GameObject>(arTemplateScreenRayInteractorResourcePath);
                if (prefab == null)
                {
                    LastTemplateInteractionStatus = "screen_ray_prefab_missing:" + arTemplateScreenRayInteractorResourcePath;
                    Debug.LogWarning("[FormalArRuntimeBootstrap] Missing AR Mobile template screen ray interactor at Resources/" + arTemplateScreenRayInteractorResourcePath + ".");
                    return null;
                }

                var parent = origin.CameraFloorOffsetObject != null
                    ? origin.CameraFloorOffsetObject.transform
                    : origin.transform;
                _templateScreenRayInteractor = Instantiate(prefab, parent, worldPositionStays: false);
                _templateScreenRayInteractor.name = "Screen Space Ray Interactor";
            }

            var camera = origin.Camera != null ? origin.Camera : Camera.main;
            BindTemplateInteractorCamera(_templateScreenRayInteractor, camera);

            var rayInteractor = _templateScreenRayInteractor.GetComponentInChildren<XRRayInteractor>(true);
            if (rayInteractor == null)
            {
                LastTemplateInteractionStatus = "screen_ray_interactor_missing";
                return null;
            }

            rayInteractor.enableARRaycasting = true;
            rayInteractor.blockInteractionsWithScreenSpaceUI = true;
            rayInteractor.occludeARHitsWith2DObjects = true;
            rayInteractor.occludeARHitsWith3DObjects = false;
            return rayInteractor;
        }

        private static XRRayInteractor FindTemplateScreenRayInteractor(XROrigin origin)
        {
            if (origin == null)
                return null;

            var interactors = origin.GetComponentsInChildren<XRRayInteractor>(true);
            for (int i = 0; i < interactors.Length; i++)
            {
                var interactor = interactors[i];
                if (interactor != null && interactor.gameObject.name == "Screen Space Ray Interactor")
                    return interactor;
            }
            return null;
        }

        private static void BindTemplateInteractorCamera(GameObject interactorRoot, Camera camera)
        {
            if (interactorRoot == null || camera == null)
                return;

            var poseDrivers = interactorRoot.GetComponentsInChildren<ScreenSpaceRayPoseDriver>(true);
            for (int i = 0; i < poseDrivers.Length; i++)
                poseDrivers[i].controllerCamera = camera;

#pragma warning disable CS0618
            var screenControllers = interactorRoot.GetComponentsInChildren<XRScreenSpaceController>(true);
            for (int i = 0; i < screenControllers.Length; i++)
            {
                screenControllers[i].controllerCamera = camera;
                screenControllers[i].blockInteractionsWithScreenSpaceUI = true;
            }
#pragma warning restore CS0618
        }

        private bool EnsureTemplateObjectSpawner(
            XROrigin origin,
            XRRayInteractor rayInteractor,
            FormalModelPlacementController placement)
        {
            if (origin == null || rayInteractor == null)
            {
                LastTemplateInteractionStatus = "spawner_missing_dependency";
                return false;
            }

            GameObject spawnerObject = _templateObjectSpawner != null
                ? _templateObjectSpawner.gameObject
                : GameObject.Find("FormalARMobileTemplateObjectSpawner");
            if (spawnerObject == null)
            {
                spawnerObject = new GameObject("FormalARMobileTemplateObjectSpawner");
                spawnerObject.transform.SetParent(origin.transform, false);
            }

            if (_templateObjectSpawner == null || _templateObjectSpawner.gameObject != spawnerObject)
                _templateObjectSpawner = spawnerObject.GetComponent<ObjectSpawner>();
            if (_templateObjectSpawner == null)
                _templateObjectSpawner = spawnerObject.AddComponent<ObjectSpawner>();

            if (_templateSpawnTrigger == null || _templateSpawnTrigger.gameObject != spawnerObject)
                _templateSpawnTrigger = spawnerObject.GetComponent<ARInteractorSpawnTrigger>();
            if (_templateSpawnTrigger == null)
                _templateSpawnTrigger = spawnerObject.AddComponent<ARInteractorSpawnTrigger>();

            if (!spawnerObject.transform.IsChildOf(origin.transform))
            {
                spawnerObject.transform.SetParent(origin.transform, false);
            }

            _templateObjectSpawner.cameraToFace = origin.Camera != null ? origin.Camera : Camera.main;
            _templateObjectSpawner.objectPrefabs = new List<GameObject> { EnsureTemplateSpawnProxy(origin) };
            _templateObjectSpawner.spawnOptionIndex = 0;
            _templateObjectSpawner.onlySpawnInView = true;
            _templateObjectSpawner.viewportPeriphery = 0f;
            _templateObjectSpawner.applyRandomAngleAtSpawn = true;
            _templateObjectSpawner.spawnAngleRange = 45f;
            // Match the user's AR Mobile demo2 SampleScene: the spawner owns
            // the transient spawned proxy before formal placement takes over.
            _templateObjectSpawner.spawnAsChildren = true;
            _templateObjectSpawner.objectSpawned -= HandleTemplateObjectSpawned;
            _templateObjectSpawner.objectSpawned += HandleTemplateObjectSpawned;
            _templateObjectSpawner.enabled = true;

            _templateSpawnTrigger.arInteractor = rayInteractor;
            _templateSpawnTrigger.objectSpawner = _templateObjectSpawner;
            _templateSpawnTrigger.requireHorizontalUpSurface = true;
            _templateSpawnTrigger.spawnTriggerType = ARInteractorSpawnTrigger.SpawnTriggerType.SelectAttempt;
            _templateSpawnTrigger.blockSpawnWhenInteractorHasSelection = true;
            _templateSpawnTrigger.enabled = true;

            if (placement == null)
                LastTemplateInteractionStatus = "placement_controller_missing";
            return placement != null;
        }

        private GameObject EnsureTemplateSpawnProxy(XROrigin origin)
        {
            var parent = origin != null ? origin.transform : transform;

            if (_templateSpawnProxy == null)
                _templateSpawnProxy = new GameObject("FormalARMobileTemplateSpawnProxy");

            if (!_templateSpawnProxy.transform.IsChildOf(parent))
                _templateSpawnProxy.transform.SetParent(parent, false);
            return _templateSpawnProxy;
        }

        private void HandleTemplateObjectSpawned(GameObject spawned)
        {
            if (spawned == null)
                return;

            var placement = FindObjectOfType<FormalModelPlacementController>();
            if (placement == null)
            {
                LastTemplateInteractionStatus = "spawn_rejected:placement_controller_missing";
                Destroy(spawned);
                return;
            }

            var position = spawned.transform.position;
            var rotation = spawned.transform.rotation;
            Destroy(spawned);

            if (!placement.CanPlaceNow)
            {
                LastTemplateInteractionStatus = "spawn_rejected:" + placement.LastPlacementStatus;
                placement.ReportTemplateXriStatus(LastTemplateInteractionStatus);
                return;
            }

            placement.PlaceAt(position, rotation, "ar_mobile_template_object_spawner");
            LastTemplateInteractionStatus = "spawned:" + placement.LastPlacementStatus;
            placement.ReportTemplateXriStatus(LastTemplateInteractionStatus);
        }

        private static void EnsureArInputManager(GameObject target)
        {
            if (target == null) return;

            // ARInputManager exists in AR Foundation 5.x, but adding it by
            // reflection keeps this bootstrap tolerant of package API reshapes.
            var type = Type.GetType("UnityEngine.XR.ARFoundation.ARInputManager, Unity.XR.ARFoundation");
            if (type != null && target.GetComponent(type) == null)
                target.AddComponent(type);
        }
#endif
    }
}
