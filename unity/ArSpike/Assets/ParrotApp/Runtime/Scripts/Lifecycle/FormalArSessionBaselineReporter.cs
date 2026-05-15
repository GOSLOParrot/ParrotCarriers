using System.Collections;
using ParrotApp.Config;
using ParrotApp.LiveKit;
using UnityEngine;

#if UNITY_AR_FOUNDATION
using UnityEngine.XR.ARFoundation;
#endif

namespace ParrotApp.Lifecycle
{
    /// <summary>
    /// Reports only the AR/session baseline gate for entering the formal home.
    /// It does not claim GOSLO is placed; placement still belongs to
    /// onSceneReady/onGosloPlaced.
    /// </summary>
    [DisallowMultipleComponent]
    public class FormalArSessionBaselineReporter : MonoBehaviour
    {
        [SerializeField] private AppStartupFlowController startupFlow;
        [SerializeField] private FormalMainReadyGate mainReadyGate;
        [SerializeField] private ARVideoPublisher videoPublisher;
        [SerializeField] private FormalArRuntimeBootstrap arRuntimeBootstrap;
        [SerializeField] private float arStateWaitSeconds = 12f;
        [SerializeField] private float arRetryIntervalSeconds = 0.5f;
        [SerializeField] private float arWarnIntervalSeconds = 2f;

        private Coroutine _checkCoroutine;

        public string LastStatus { get; private set; } = "";

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
            StopCheck();
        }

        private void Bind()
        {
            if (startupFlow == null) startupFlow = FindObjectOfType<AppStartupFlowController>();
            if (mainReadyGate == null) mainReadyGate = FindObjectOfType<FormalMainReadyGate>();
            if (videoPublisher == null) videoPublisher = FindObjectOfType<ARVideoPublisher>();
            if (arRuntimeBootstrap == null) arRuntimeBootstrap = FindObjectOfType<FormalArRuntimeBootstrap>();

            if (startupFlow != null)
            {
                startupFlow.OnTransitionStarted -= HandleTransitionStarted;
                startupFlow.OnMainUiReady -= HandleStartupMainReady;
                startupFlow.OnStartupFailed -= HandleStartupFailed;
                startupFlow.OnTransitionStarted += HandleTransitionStarted;
                startupFlow.OnMainUiReady += HandleStartupMainReady;
                startupFlow.OnStartupFailed += HandleStartupFailed;

                if (startupFlow.MainUiReadyOnce
                    && string.IsNullOrWhiteSpace(LastStatus)
                    && _checkCoroutine == null)
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
            LastStatus = "";
            mainReadyGate?.ReportGateInvalidated("ar_session_baseline_clean");
            StopCheck();
        }

        private void HandleStartupFailed(string reason)
        {
            LastStatus = reason ?? "startup_failed";
            StopCheck();
        }

        private void HandleStartupMainReady(AppStartupConfigDto config)
        {
            StopCheck();
            _checkCoroutine = StartCoroutine(CheckBaseline(config ?? AppStartupConfigDto.Default()));
        }

        private IEnumerator CheckBaseline(AppStartupConfigDto config)
        {
            config.Normalize();
            yield return null;

            if (!AppCapabilityModeNames.VideoEnabled(config.capability_mode))
            {
                ReportClean("video_not_required:" + config.capability_mode);
                _checkCoroutine = null;
                yield break;
            }

            if (Application.isEditor || !Application.isMobilePlatform)
            {
                ReportClean(videoPublisher != null
                    ? "non_mobile_video_publisher_baseline"
                    : "non_mobile_no_ar_required");
                _checkCoroutine = null;
                yield break;
            }

#if UNITY_AR_FOUNDATION
            float warningDeadline = Time.realtimeSinceStartup + Mathf.Max(0.1f, arStateWaitSeconds);
            float nextWarnAt = Time.realtimeSinceStartup + Mathf.Max(0.1f, arWarnIntervalSeconds);
            var wait = new WaitForSeconds(Mathf.Max(0.1f, arRetryIntervalSeconds));

            while (true)
            {
                if (arRuntimeBootstrap != null)
                    yield return arRuntimeBootstrap.EnsureArRuntimeReady();
                else
                    yield return null;

                var arSession = FindObjectOfType<ARSession>();
                if (arSession == null)
                {
                    LastStatus = "mobile_ar_session_not_mounted";
                }
                else if (ARSession.state == ARSessionState.SessionTracking)
                {
                    ReportClean("ar_foundation:" + ARSession.state);
                    _checkCoroutine = null;
                    yield break;
                }
                else if (ARSession.state == ARSessionState.Unsupported)
                {
                    LastStatus = "ar_session_unsupported";
                    Debug.LogWarning("[FormalArSessionBaselineReporter] " + LastStatus);
                    _checkCoroutine = null;
                    yield break;
                }
                else
                {
                    LastStatus = "ar_session_waiting:" + ARSession.state;
                }

                if (Time.realtimeSinceStartup >= warningDeadline
                    && Time.realtimeSinceStartup >= nextWarnAt)
                {
                    Debug.LogWarning("[FormalArSessionBaselineReporter] " + LastStatus);
                    nextWarnAt = Time.realtimeSinceStartup + Mathf.Max(0.1f, arWarnIntervalSeconds);
                }

                yield return wait;
            }
#else

            LastStatus = "mobile_ar_session_not_mounted";
            Debug.LogWarning("[FormalArSessionBaselineReporter] " + LastStatus);
            _checkCoroutine = null;
#endif
        }

        private void ReportClean(string status)
        {
            LastStatus = status ?? "";
            mainReadyGate?.ReportArSessionBaselineClean(LastStatus);
        }

        private void StopCheck()
        {
            if (_checkCoroutine == null) return;
            StopCoroutine(_checkCoroutine);
            _checkCoroutine = null;
        }
    }
}
