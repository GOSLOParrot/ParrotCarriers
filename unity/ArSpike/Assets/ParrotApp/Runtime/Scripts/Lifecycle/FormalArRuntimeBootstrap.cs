using System;
using System.Collections;
using UnityEngine;
using UnityEngine.XR.Management;

#if ENABLE_INPUT_SYSTEM
using UnityEngine.InputSystem;
using UnityEngine.InputSystem.XR;
#endif

#if UNITY_AR_FOUNDATION
using Unity.XR.CoreUtils;
using UnityEngine.XR.ARFoundation;
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
        public bool XrLifecycleReady { get; private set; }
        public bool XrLifecycleRequired { get; private set; }
        public bool XrLifecycleFailed { get; private set; }
        public string LastStatus { get; private set; } = "";

        private bool _xrStartInProgress;
        private bool _startedXrSubsystems;
        private bool _initializedXrLoader;

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
            StopManagedXrLifecycle();
        }

        public void EnsureArRuntime()
        {
#if UNITY_AR_FOUNDATION
            XrOriginMounted = EnsureXrOrigin();
            SessionMounted = EnsureSession();
            CameraManagersMounted = EnsureCameraManagers();
            PlacementManagersMounted = EnsurePlacementManagers();
            LastStatus = $"ar_runtime_bootstrap origin={XrOriginMounted} session={SessionMounted} camera={CameraManagersMounted} placement={PlacementManagersMounted}";
#else
            XrOriginMounted = false;
            SessionMounted = false;
            CameraManagersMounted = false;
            PlacementManagersMounted = false;
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

            if (_initializedXrLoader)
                manager.DeinitializeLoader();
            else if (_startedXrSubsystems)
                manager.StopSubsystems();

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
            return true;
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
