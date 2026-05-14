using ParrotApp.Config;
using ParrotApp.Parrot;
using UnityEngine;

namespace ParrotApp.Lifecycle
{
    /// <summary>
    /// Resolves the selected model manifest for the formal homepage gate.
    /// The final model placement/interaction UI is a separate responsibility.
    /// </summary>
    [DisallowMultipleComponent]
    public class FormalModelReadyReporter : MonoBehaviour
    {
        [SerializeField] private AppStartupFlowController startupFlow;
        [SerializeField] private FormalMainReadyGate mainReadyGate;
        [SerializeField] private ModelDriver modelDriver;

        public ModelManifestDto LastManifest { get; private set; }
        public string LastError { get; private set; } = "";

        private void OnEnable()
        {
            Bind();
        }

        private void Start()
        {
            Bind();
        }

        private void OnDisable()
        {
            Unbind();
        }

        private void Bind()
        {
            if (startupFlow == null) startupFlow = FindObjectOfType<AppStartupFlowController>();
            if (mainReadyGate == null) mainReadyGate = FindObjectOfType<FormalMainReadyGate>();
            if (modelDriver == null) modelDriver = FindObjectOfType<ModelDriver>();

            if (startupFlow != null)
            {
                startupFlow.OnTransitionStarted -= HandleTransitionStarted;
                startupFlow.OnMainUiReady -= HandleStartupMainReady;
                startupFlow.OnStartupFailed -= HandleStartupFailed;
                startupFlow.OnTransitionStarted += HandleTransitionStarted;
                startupFlow.OnMainUiReady += HandleStartupMainReady;
                startupFlow.OnStartupFailed += HandleStartupFailed;

                if (startupFlow.MainUiReadyOnce
                    && LastManifest == null
                    && string.IsNullOrWhiteSpace(LastError))
                {
                    HandleStartupMainReady(startupFlow.ActiveConfig);
                }
            }
        }

        private void Unbind()
        {
            if (startupFlow == null) return;
            startupFlow.OnTransitionStarted -= HandleTransitionStarted;
            startupFlow.OnMainUiReady -= HandleStartupMainReady;
            startupFlow.OnStartupFailed -= HandleStartupFailed;
        }

        private void HandleTransitionStarted(AppStartupConfigDto _)
        {
            LastManifest = null;
            LastError = "";
            mainReadyGate?.ReportGateInvalidated("model_resolved");
        }

        private void HandleStartupFailed(string reason)
        {
            LastError = reason ?? "startup_failed";
        }

        private void HandleStartupMainReady(AppStartupConfigDto config)
        {
            var active = config ?? AppStartupConfigDto.Default();
            active.Normalize();
            string modelId = active.model_id;

            LastManifest = ResolveManifest(modelId);
            if (LastManifest == null)
            {
                LastError = "model_manifest_missing:" + modelId;
                Debug.LogWarning("[FormalModelReadyReporter] " + LastError);
                return;
            }

            LastError = "";
            mainReadyGate?.ReportModelResolved("manifest:" + LastManifest.model_id);
        }

        private ModelManifestDto ResolveManifest(string modelId)
        {
            if (modelDriver != null
                && modelDriver.Manifest != null
                && !string.IsNullOrWhiteSpace(modelDriver.Manifest.model_id)
                && string.Equals(modelDriver.Manifest.model_id, modelId, System.StringComparison.OrdinalIgnoreCase))
            {
                return modelDriver.Manifest;
            }

            return ModelManifestDto.LoadFromResources(modelId);
        }
    }
}
