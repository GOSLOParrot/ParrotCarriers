using System;
using System.Collections;
using System.Collections.Generic;
using UnityEngine;
using UnityEngine.XR.Management;

#if ENABLE_INPUT_SYSTEM
using UnityEngine.InputSystem;
using UnityEngine.InputSystem.XR;
#endif

#if UNITY_AR_FOUNDATION
using Unity.XR.CoreUtils;
using UnityEngine.XR.ARFoundation;
using UnityEngine.XR.ARSubsystems;
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
        [SerializeField] private int maxPointCloudDotsPerCloud = 96;
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
        public bool XrLifecycleReady { get; private set; }
        public bool XrLifecycleRequired { get; private set; }
        public bool XrLifecycleFailed { get; private set; }
        public string LastStatus { get; private set; } = "";
        public string LastSpatialVisualStatus { get; private set; } = "not_mounted";

        private bool _xrStartInProgress;
        private bool _startedXrSubsystems;
        private bool _initializedXrLoader;

#if UNITY_AR_FOUNDATION
        private ARPlaneManager _planeManager;
        private ARPointCloudManager _pointCloudManager;
        private Material _planeVisualMaterial;
        private Material _pointCloudDotMaterial;
        private readonly Dictionary<TrackableId, GameObject> _planeVisuals = new Dictionary<TrackableId, GameObject>();
        private readonly Dictionary<TrackableId, List<GameObject>> _pointCloudDots = new Dictionary<TrackableId, List<GameObject>>();
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
            LastStatus = $"ar_runtime_bootstrap origin={XrOriginMounted} session={SessionMounted} camera={CameraManagersMounted} placement={PlacementManagersMounted} spatial={SpatialVisualsMounted}";
#else
            XrOriginMounted = false;
            SessionMounted = false;
            CameraManagersMounted = false;
            PlacementManagersMounted = false;
            SpatialVisualsMounted = false;
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
            if (origin.GetComponent<ARPointCloudManager>() == null)
                origin.gameObject.AddComponent<ARPointCloudManager>();

            SpatialVisualsMounted = BindSpatialVisuals(origin);
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
            _pointCloudManager = origin.GetComponent<ARPointCloudManager>();
            if (_planeManager == null || _pointCloudManager == null)
            {
                LastSpatialVisualStatus = "manager_missing";
                return false;
            }

            _planeManager.planesChanged -= HandlePlanesChanged;
            _planeManager.planesChanged += HandlePlanesChanged;
            _pointCloudManager.pointCloudsChanged -= HandlePointCloudsChanged;
            _pointCloudManager.pointCloudsChanged += HandlePointCloudsChanged;
            LastSpatialVisualStatus = "plane_pointcloud_visuals_bound";
            return true;
        }

        private void UnbindSpatialVisuals()
        {
            if (_planeManager != null)
                _planeManager.planesChanged -= HandlePlanesChanged;
            if (_pointCloudManager != null)
                _pointCloudManager.pointCloudsChanged -= HandlePointCloudsChanged;
        }

        private void HandlePlanesChanged(ARPlanesChangedEventArgs args)
        {
            for (int i = 0; i < args.added.Count; i++)
                CreateOrUpdatePlaneVisual(args.added[i]);
            for (int i = 0; i < args.updated.Count; i++)
                CreateOrUpdatePlaneVisual(args.updated[i]);
            for (int i = 0; i < args.removed.Count; i++)
                RemovePlaneVisual(args.removed[i]);

            LastSpatialVisualStatus = $"planes={_planeVisuals.Count} pointclouds={_pointCloudDots.Count}";
        }

        private void CreateOrUpdatePlaneVisual(ARPlane plane)
        {
            if (plane == null) return;
            GameObject visual;
            if (!_planeVisuals.TryGetValue(plane.trackableId, out visual) || visual == null)
            {
                visual = GameObject.CreatePrimitive(PrimitiveType.Quad);
                visual.name = "FormalARPlaneVisual_" + plane.trackableId;
                visual.transform.SetParent(plane.transform, false);
                var collider = visual.GetComponent<Collider>();
                if (collider != null) Destroy(collider);
                var renderer = visual.GetComponent<Renderer>();
                if (renderer != null)
                    renderer.material = PlaneVisualMaterial();
                _planeVisuals[plane.trackableId] = visual;
            }

            visual.transform.localPosition = Vector3.zero;
            visual.transform.localRotation = Quaternion.Euler(90f, 0f, 0f);
            Vector2 size = plane.size;
            visual.transform.localScale = new Vector3(
                Mathf.Max(0.06f, size.x),
                Mathf.Max(0.06f, size.y),
                1f);
            visual.SetActive(plane.enabled);
        }

        private void RemovePlaneVisual(ARPlane plane)
        {
            if (plane == null) return;
            GameObject visual;
            if (_planeVisuals.TryGetValue(plane.trackableId, out visual) && visual != null)
                Destroy(visual);
            _planeVisuals.Remove(plane.trackableId);
        }

        private void HandlePointCloudsChanged(ARPointCloudChangedEventArgs args)
        {
            for (int i = 0; i < args.added.Count; i++)
                CreateOrUpdatePointCloudVisual(args.added[i]);
            for (int i = 0; i < args.updated.Count; i++)
                CreateOrUpdatePointCloudVisual(args.updated[i]);
            for (int i = 0; i < args.removed.Count; i++)
                RemovePointCloudVisual(args.removed[i]);

            LastSpatialVisualStatus = $"planes={_planeVisuals.Count} pointclouds={_pointCloudDots.Count}";
        }

        private void CreateOrUpdatePointCloudVisual(ARPointCloud pointCloud)
        {
            if (pointCloud == null || !pointCloud.positions.HasValue) return;
            var positions = pointCloud.positions.Value;
            int count = Mathf.Min(positions.Length, Mathf.Max(0, maxPointCloudDotsPerCloud));

            List<GameObject> dots;
            if (!_pointCloudDots.TryGetValue(pointCloud.trackableId, out dots))
            {
                dots = new List<GameObject>(count);
                _pointCloudDots[pointCloud.trackableId] = dots;
            }

            while (dots.Count < count)
            {
                var dot = GameObject.CreatePrimitive(PrimitiveType.Sphere);
                dot.name = "FormalARPointDot";
                dot.transform.SetParent(pointCloud.transform, false);
                dot.transform.localScale = Vector3.one * 0.018f;
                var collider = dot.GetComponent<Collider>();
                if (collider != null) Destroy(collider);
                var renderer = dot.GetComponent<Renderer>();
                if (renderer != null)
                    renderer.material = PointCloudDotMaterial();
                dots.Add(dot);
            }

            for (int i = 0; i < dots.Count; i++)
            {
                var dot = dots[i];
                if (dot == null) continue;
                bool active = i < count;
                dot.SetActive(active);
                if (active)
                    dot.transform.localPosition = positions[i];
            }
        }

        private void RemovePointCloudVisual(ARPointCloud pointCloud)
        {
            if (pointCloud == null) return;
            List<GameObject> dots;
            if (_pointCloudDots.TryGetValue(pointCloud.trackableId, out dots))
            {
                for (int i = 0; i < dots.Count; i++)
                    if (dots[i] != null) Destroy(dots[i]);
            }
            _pointCloudDots.Remove(pointCloud.trackableId);
        }

        private Material PlaneVisualMaterial()
        {
            if (_planeVisualMaterial != null) return _planeVisualMaterial;
            _planeVisualMaterial = CreateTransparentMaterial(new Color(0.23f, 0.58f, 1f, 0.18f));
            return _planeVisualMaterial;
        }

        private Material PointCloudDotMaterial()
        {
            if (_pointCloudDotMaterial != null) return _pointCloudDotMaterial;
            _pointCloudDotMaterial = CreateTransparentMaterial(new Color(1f, 1f, 1f, 0.92f));
            return _pointCloudDotMaterial;
        }

        private static Material CreateTransparentMaterial(Color color)
        {
            var shader = Shader.Find("Sprites/Default") ?? Shader.Find("Universal Render Pipeline/Unlit") ?? Shader.Find("Standard");
            if (shader == null)
                shader = Shader.Find("UI/Default");
            if (shader == null)
                shader = Shader.Find("Hidden/Internal-Colored");
            var material = new Material(shader);
            material.color = color;
            material.renderQueue = 3000;
            return material;
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
