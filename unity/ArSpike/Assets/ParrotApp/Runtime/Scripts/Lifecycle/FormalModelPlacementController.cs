using System;
using System.Collections.Generic;
using System.Reflection;
using ParrotApp.Config;
using ParrotApp.Parrot;
using UnityEngine;

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
    /// white-box slice it first tries a formal AR raycast against tracked
    /// planes, then falls back to a camera-forward preview placement when AR
    /// raycast is unavailable. Final prefabs can replace only InstantiateModel.
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
        [SerializeField] private bool fallbackToPreviewWhenArMisses = true;
        [SerializeField] private float defaultDistanceMeters = 1.2f;
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
        public GameObject PlacedModel { get; private set; }
        public bool CanPlaceNow => startupFlow != null
                                   && startupFlow.MainUiReadyOnce
                                   && (mainReadyGate == null || mainReadyGate.IsReady)
                                   && _manifest != null;

        private bool _reportedGosloPlaced;
        private ModelManifestDto _manifest;

        private void OnEnable()
        {
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
            LastPlacementMode = "none";
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
            if (TryResolveArRaycastPose(screenPoint, out Pose arPose, out string raycastStatus))
            {
                LastPlacementMode = "ar_raycast";
                PlaceAt(arPose.position, ResolveDefaultRotation(arPose.position), "ar_raycast_plane");
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

            if (TryResolveArRaycastPose(screenPoint, out Pose arPose, out string raycastStatus))
            {
                LastPlacementMode = "ar_raycast";
                PlaceAt(arPose.position, ResolveDefaultRotation(arPose.position), "ar_raycast_plane");
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

            if (PlacedModel == null)
                PlacedModel = InstantiateModel();

            if (PlacedModel == null)
            {
                LastPlacementStatus = "instantiate_failed:" + ActiveModelId;
                return;
            }

            PlacedModel.transform.SetParent(modelRoot, worldPositionStays: true);
            PlacedModel.transform.SetPositionAndRotation(position, rotation);
            PlacedModel.SetActive(true);
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
            HasPlacedModel = false;
            LastPlacementMode = "none";
            LastVisualSource = "none";
        }

        private bool CanPlace()
        {
            if (startupFlow == null || !startupFlow.MainUiReadyOnce) return false;
            if (_manifest == null) PrepareManifest(startupFlow.ActiveConfig);
            if (mainReadyGate != null && !mainReadyGate.IsReady) return false;
            return _manifest != null;
        }

        private bool TryResolveArRaycastPose(Vector2 screenPoint, out Pose pose, out string status)
        {
            pose = new Pose();
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
            return go;
        }

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
