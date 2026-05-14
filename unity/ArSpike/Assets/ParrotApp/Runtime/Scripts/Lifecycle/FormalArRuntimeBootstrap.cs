using System;
using UnityEngine;

#if UNITY_AR_FOUNDATION
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
        public string LastStatus { get; private set; } = "";

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

        public void EnsureArRuntime()
        {
#if UNITY_AR_FOUNDATION
            SessionMounted = EnsureSession();
            CameraManagersMounted = EnsureCameraManagers();
            LastStatus = $"ar_runtime_bootstrap session={SessionMounted} camera={CameraManagersMounted}";
#else
            SessionMounted = false;
            CameraManagersMounted = false;
            LastStatus = "unity_ar_foundation_symbol_missing";
            Debug.LogWarning("[FormalArRuntimeBootstrap] UNITY_AR_FOUNDATION is not defined; AR runtime was not mounted.");
#endif
        }

#if UNITY_AR_FOUNDATION
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
