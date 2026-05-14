using System;
using System.Collections;
using ParrotApp.Backend;
using ParrotApp.Config;
using ParrotApp.Lifecycle;
using UnityEngine;

namespace ParrotApp.UI
{
    /// <summary>
    /// Loads the formal home/menu snapshot from App HTTP after START transport
    /// is proven. This component intentionally does not build the final drawer
    /// UI yet; it only owns the data-loading gate for the homepage.
    /// </summary>
    [DisallowMultipleComponent]
    public class FormalHomeMenuLoader : MonoBehaviour
    {
        [SerializeField] private AppStartupFlowController startupFlow;
        [SerializeField] private FormalMainReadyGate mainReadyGate;
        [SerializeField] private AppHomeMenuClient menuClient;
        [SerializeField] private int maxLoadAttempts = 3;
        [SerializeField] private float retryDelaySeconds = 1.25f;

        private Coroutine _loadCoroutine;
        private AppStartupConfigDto _activeConfig = AppStartupConfigDto.Default();

        public AppCanvasSnapshotDto LastSnapshot { get; private set; }
        public string LastError { get; private set; } = "";
        public bool Loaded => LastSnapshot != null && string.IsNullOrWhiteSpace(LastError);

        private void OnEnable()
        {
            Bind(allowMainReadyCatchUp: true);
        }

        private void Start()
        {
            Bind(allowMainReadyCatchUp: true);
        }

        private void OnDisable()
        {
            Unbind();
        }

        private void Bind(bool allowMainReadyCatchUp)
        {
            if (startupFlow == null) startupFlow = FindObjectOfType<AppStartupFlowController>();
            if (mainReadyGate == null) mainReadyGate = FindObjectOfType<FormalMainReadyGate>();
            if (menuClient == null) menuClient = FindObjectOfType<AppHomeMenuClient>();
            if (menuClient == null) menuClient = gameObject.AddComponent<AppHomeMenuClient>();

            if (startupFlow != null)
            {
                startupFlow.OnTransitionStarted -= HandleTransitionStarted;
                startupFlow.OnMainUiReady -= HandleStartupMainReady;
                startupFlow.OnStartupFailed -= HandleStartupFailed;
                startupFlow.OnTransitionStarted += HandleTransitionStarted;
                startupFlow.OnMainUiReady += HandleStartupMainReady;
                startupFlow.OnStartupFailed += HandleStartupFailed;

                if (allowMainReadyCatchUp
                    && startupFlow.MainUiReadyOnce
                    && LastSnapshot == null
                    && string.IsNullOrWhiteSpace(LastError)
                    && _loadCoroutine == null)
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

        private void HandleTransitionStarted(AppStartupConfigDto config)
        {
            _activeConfig = config ?? AppStartupConfigDto.Default();
            _activeConfig.Normalize();
            LastSnapshot = null;
            LastError = "";
            mainReadyGate?.ReportGateInvalidated("menu_snapshot_loaded");
            StopLoad();
        }

        private void HandleStartupMainReady(AppStartupConfigDto config)
        {
            _activeConfig = config ?? AppStartupConfigDto.Default();
            _activeConfig.Normalize();
            StopLoad();
            _loadCoroutine = StartCoroutine(LoadSnapshot());
        }

        private void HandleStartupFailed(string reason)
        {
            LastError = reason ?? "startup_failed";
            StopLoad();
        }

        private IEnumerator LoadSnapshot()
        {
            Bind(allowMainReadyCatchUp: false);

            if (menuClient == null || !menuClient.HasEndpoint)
            {
                LastError = "app_home_menu_http_required";
                Debug.LogWarning("[FormalHomeMenuLoader] " + LastError);
                _loadCoroutine = null;
                yield break;
            }

            int attempts = Mathf.Max(1, maxLoadAttempts);
            for (int attempt = 1; attempt <= attempts; attempt++)
            {
                RequestResult<AppCanvasSnapshotDto> result = default;
                yield return menuClient.LoadCanvasSnapshot(r => result = r);

                if (result.Success && result.Value != null)
                {
                    LastSnapshot = result.Value;
                    LastError = "";
                    mainReadyGate?.ReportMenuSnapshotLoaded(
                        "app_http_canvas_snapshot:" + (_activeConfig.workspace_id ?? ""));
                    _loadCoroutine = null;
                    yield break;
                }

                LastSnapshot = null;
                LastError = string.IsNullOrWhiteSpace(result.Error)
                    ? "canvas_snapshot_load_failed"
                    : result.Error;
                Debug.LogWarning("[FormalHomeMenuLoader] " + LastError);

                if (attempt < attempts && retryDelaySeconds > 0f)
                    yield return new WaitForSeconds(retryDelaySeconds * attempt);
            }

            _loadCoroutine = null;
        }

        private void StopLoad()
        {
            if (_loadCoroutine == null) return;
            StopCoroutine(_loadCoroutine);
            _loadCoroutine = null;
        }
    }
}
