using System;
using ParrotApp.Config;
using ParrotApp.Hands;
using ParrotApp.Parrot;
using UnityEngine;

namespace ParrotApp.Lifecycle
{
    /// <summary>
    /// Formal homepage owner for the local camera/XR hand-to-perch reflex.
    ///
    /// This is intentionally a Unity-local owner. It mounts the existing
    /// HandGestureSource and PerchOnHand only after the formal main-ready and
    /// placement gates are satisfied, then degrades loudly when the selected
    /// model cannot support the reflex. It does not send Brain RPC, save menu
    /// state, or treat editor debug hand events as phone proof.
    /// </summary>
    [DisallowMultipleComponent]
    public class FormalXrHandPerchController : MonoBehaviour
    {
        [SerializeField] private AppStartupFlowController startupFlow;
        [SerializeField] private FormalMainReadyGate mainReadyGate;
        [SerializeField] private FormalModelPlacementController placementController;
        [SerializeField] private HandGestureSource handGestureSource;
        [SerializeField] private bool autoCreateGestureSource = true;
        [SerializeField] private float reevaluateIntervalSeconds = 0.35f;

        public bool PerchMounted { get; private set; }
        public string LastXrHandStatus { get; private set; } = "waiting_start";
        public bool RealXrHandsCompiled
        {
            get
            {
#if UNITY_XR_HANDS
                return true;
#else
                return false;
#endif
            }
        }

        private PerchOnHand _mountedPerch;
        private GameObject _gestureSourceOwner;
        private float _nextReevaluateAt;
        private string _lastLoggedStatus = "";

        private void OnEnable()
        {
            Bind();
        }

        private void Start()
        {
            Bind();
            RefreshMount();
        }

        private void Update()
        {
            if (Time.unscaledTime < _nextReevaluateAt) return;
            _nextReevaluateAt = Time.unscaledTime + Mathf.Max(0.1f, reevaluateIntervalSeconds);
            RefreshMount();
        }

        private void OnDisable()
        {
            Unbind();
            if (_mountedPerch != null) _mountedPerch.enabled = false;
            PerchMounted = false;
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
            if (_mountedPerch != null) _mountedPerch.enabled = false;
            _mountedPerch = null;
            PerchMounted = false;
            SetStatus("waiting_placed_model");
        }

        private void HandleMainUiReady(AppStartupConfigDto _)
        {
            RefreshMount();
        }

        private void HandleStartupFailed(string reason)
        {
            if (_mountedPerch != null) _mountedPerch.enabled = false;
            PerchMounted = false;
            SetStatus("startup_failed:" + ShortReason(reason));
        }

        private void HandleGateChanged(FormalMainReadySnapshot _)
        {
            RefreshMount();
        }

        public void RefreshMount()
        {
            Bind();

            if (startupFlow == null || !startupFlow.MainUiReadyOnce)
            {
                SetPerchInactive("waiting_home_ready");
                return;
            }

            EnsureGestureSource();

            if (mainReadyGate != null && !mainReadyGate.IsReady)
            {
                SetPerchInactive(WithTracking("home_gates_wait:" + ShortReason(mainReadyGate.LastMissingGates)));
                return;
            }

            if (placementController == null)
                placementController = FindObjectOfType<FormalModelPlacementController>();
            if (placementController == null || !placementController.HasPlacedModel || placementController.PlacedModel == null)
            {
                SetPerchInactive(WithTracking("waiting_placed_model"));
                return;
            }

            var model = placementController.PlacedModel;
            string modelId = ResolveModelId(model);
            if (!SupportsPerch(model, modelId))
            {
                SetPerchInactive(WithTracking("model_perch_unsupported:" + ShortReason(modelId)));
                return;
            }

            if (model.GetComponentInChildren<AnimationDriver>(true) == null)
            {
                SetPerchInactive(WithTracking("model_no_animation_driver:" + ShortReason(modelId)));
                return;
            }

            if (handGestureSource == null)
            {
                SetPerchInactive("hand_source_missing");
                return;
            }

            var perch = model.GetComponent<PerchOnHand>();
            if (perch == null) perch = model.AddComponent<PerchOnHand>();
            if (_mountedPerch != null && _mountedPerch != perch)
                _mountedPerch.enabled = false;
            perch.enabled = true;
            _mountedPerch = perch;
            PerchMounted = true;
            if (handGestureSource.RealCameraCvCompiled)
                SetStatus(handGestureSource.IsHandDetected
                    ? "camera_cv_tracking_active_perch_owner_mounted"
                    : WithTracking("camera_cv_owner_mounted_waiting_tracking"));
            else if (!RealXrHandsCompiled)
                SetStatus("xrhand_debug_only_package_missing");
            else
                SetStatus(handGestureSource.IsHandDetected
                    ? "xrhand_tracking_active_perch_owner_mounted"
                    : WithTracking("xrhand_owner_mounted_waiting_tracking"));
        }

        public void DebugFireBranchGesture()
        {
            EnsureGestureSource();
            handGestureSource?.DebugFireBranchGesture();
            SetStatus("debug_branch_fired");
        }

        public void DebugFireFistGesture()
        {
            EnsureGestureSource();
            handGestureSource?.DebugFireFistGesture();
            SetStatus("debug_fist_fired");
        }

        private void EnsureGestureSource()
        {
            if (handGestureSource != null) return;
            handGestureSource = FindObjectOfType<HandGestureSource>();
            if (handGestureSource != null || !autoCreateGestureSource) return;

            _gestureSourceOwner = new GameObject("FormalXrHandGestureSource");
            _gestureSourceOwner.transform.SetParent(transform, false);
            handGestureSource = _gestureSourceOwner.AddComponent<HandGestureSource>();
        }

        private void SetPerchInactive(string status)
        {
            if (_mountedPerch != null) _mountedPerch.enabled = false;
            PerchMounted = false;
            SetStatus(status);
        }

        private void SetStatus(string status)
        {
            LastXrHandStatus = string.IsNullOrWhiteSpace(status) ? "unknown" : status;
            if (string.Equals(_lastLoggedStatus, LastXrHandStatus, StringComparison.Ordinal))
                return;
            _lastLoggedStatus = LastXrHandStatus;
            Debug.Log("[FormalXrHandPerch] " + LastXrHandStatus);
        }

        private string WithTracking(string ownerStatus)
        {
            if (handGestureSource == null)
                return ownerStatus;

            string detected = handGestureSource.IsHandDetected ? "hand_seen" : "hand_wait";
            string source = string.IsNullOrWhiteSpace(handGestureSource.TrackingSource)
                ? "source_none"
                : handGestureSource.TrackingSource;
            string tracking = string.IsNullOrWhiteSpace(handGestureSource.LastTrackingStatus)
                ? "tracking_unknown"
                : handGestureSource.LastTrackingStatus;
            return ownerStatus + "/" + detected + "/" + ShortReason(source) + "/" + ShortReason(tracking);
        }

        private string ResolveModelId(GameObject model)
        {
            if (placementController != null && !string.IsNullOrWhiteSpace(placementController.ActiveModelId))
                return placementController.ActiveModelId;

            var driver = model != null ? model.GetComponentInChildren<ModelDriver>(true) : null;
            if (driver != null && driver.Manifest != null && !string.IsNullOrWhiteSpace(driver.Manifest.model_id))
                return driver.Manifest.model_id;

            return "";
        }

        private static bool SupportsPerch(GameObject model, string modelId)
        {
            var driver = model != null ? model.GetComponentInChildren<ModelDriver>(true) : null;
            if (driver != null && driver.Manifest != null && HasCapability(driver.Manifest, "perch"))
                return true;

            var registryController = !string.IsNullOrWhiteSpace(modelId) && ParrotRegistry.Instance != null
                ? ParrotRegistry.Instance.Resolve(modelId)
                : null;
            if (Supports(registryController, "perch")) return true;

            var localController = model != null ? model.GetComponentInChildren<IParrotController>(true) : null;
            return Supports(localController, "perch");
        }

        private static bool HasCapability(ModelManifestDto manifest, string capabilityId)
        {
            if (manifest == null || manifest.capabilities == null) return false;
            for (int i = 0; i < manifest.capabilities.Length; i++)
            {
                var capability = manifest.capabilities[i];
                if (capability != null
                    && string.Equals(capability.capability_id, capabilityId, StringComparison.Ordinal))
                {
                    return true;
                }
            }
            return false;
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

        private static string ShortReason(string raw)
        {
            if (string.IsNullOrWhiteSpace(raw)) return "";
            raw = raw.Trim();
            return raw.Length <= 42 ? raw : raw.Substring(0, 42);
        }
    }
}
