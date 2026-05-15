using System;
using UnityEngine;

namespace ParrotApp.Parrot
{
    /// <summary>
    /// Manifest-driven bootstrapper for one model GameObject.
    ///
    /// <para>
    /// Spec source: <c>.cursor/memory/architecture/goslo_model_manifest_protocol_v1.md</c>
    /// + <c>src/parrot/shared/model_manifest.py</c>.
    /// </para>
    ///
    /// <para>
    /// Sprint4 GOSLO model modularization (Step 2, 2026-05-06):
    /// </para>
    /// <list type="number">
    /// <item>Awake: load <c>ModelManifestDto</c> from
    /// <c>Resources/parrot_models/&lt;modelId&gt;.json</c>. If absent the
    /// component is a no-op — existing scenes without a manifest keep
    /// working through the legacy <see cref="AnimationDriver"/> direct path.</item>
    /// <item>Start: resolve the controller via reflection
    /// (<c>Type.GetType(controller_type)</c>). If the type is already a
    /// component on the same GameObject (typical for hand-wired GOSLO
    /// prefab + <see cref="GosloLegacyController"/>), reuse it; otherwise
    /// AddComponent.</item>
    /// <item>Apply <c>auto_scale_to_pet_height</c> if requested — multiplies
    /// transform.localScale uniformly so the rendered model lands near
    /// <c>default_pet_height_m</c>. The actual scale ratio is computed off
    /// the renderer bounds when available; falls back to <c>unit_meters</c>
    /// if no Renderer is found.</item>
    /// <item>Register the controller with <see cref="ParrotRegistry"/> —
    /// downstream RPC handlers can then route by <c>meta.model_id</c>.</item>
    /// </list>
    ///
    /// <para>
    /// This component is OPTIONAL. Existing GOSLO test scenes that have not
    /// added a ModelDriver still work — <see cref="ParrotController"/> and
    /// <see cref="ParrotApp.RPC.ParrotRpcHandler"/> fall back to the direct
    /// AnimationDriver path when no Registry / controller is found.
    /// </para>
    /// </summary>
    public class ModelDriver : MonoBehaviour
    {
        [Tooltip("model_id used to load Resources/parrot_models/<modelId>.json. " +
                 "Leave empty to use 'GOSLO_default'.")]
        [SerializeField] private string modelId = "";

        [Tooltip("If true, log noisy diagnostics — useful when ImportingNewModel " +
                 "for the first time. Production should keep false.")]
        [SerializeField] private bool verbose = false;

        public ModelManifestDto Manifest { get; private set; }
        public IParrotController Controller { get; private set; }

        public string EffectiveModelId =>
            !string.IsNullOrEmpty(modelId) ? modelId : "GOSLO_default";

        /// <summary>
        /// Runtime placement owners call this before Start so a white-box
        /// placeholder can still use the selected RoomSetting model manifest.
        /// Existing hand-wired prefabs can keep the serialized modelId path.
        /// </summary>
        public void ConfigureModelId(string newModelId)
        {
            modelId = string.IsNullOrWhiteSpace(newModelId) ? "" : newModelId.Trim();
            ParrotRegistry.EnsureInstance();
            Manifest = ModelManifestDto.LoadFromResources(EffectiveModelId);
        }

        void Awake()
        {
            // Make sure the registry exists before any controller calls Register.
            ParrotRegistry.EnsureInstance();

            Manifest = ModelManifestDto.LoadFromResources(EffectiveModelId);
            if (Manifest == null)
            {
                Debug.LogWarning(
                    $"[ModelDriver] No manifest for model_id='{EffectiveModelId}' — " +
                    $"existing AnimationDriver / ParrotController fallback path remains active.");
                return;
            }

            if (verbose)
            {
                Debug.Log(
                    $"[ModelDriver] Manifest loaded: model_id='{Manifest.model_id}' " +
                    $"controller_type='{Manifest.controller_type}' " +
                    $"reflex={Manifest.ParrotReflexEnabled} " +
                    $"caps={Manifest.DeclaredCapabilityIds.Count}");
            }
        }

        void Start()
        {
            if (Manifest == null) return;

            Controller = ResolveOrAttachController(Manifest.controller_type);
            if (Controller == null)
            {
                Debug.LogError(
                    $"[ModelDriver] Failed to attach controller_type='{Manifest.controller_type}' " +
                    $"for model_id='{Manifest.model_id}'. Falling back to AnimationDriver direct path.");
                return;
            }

            ConfigureControllerFromManifest();

            if (Manifest.auto_scale_to_pet_height)
            {
                ApplyAutoScale();
            }

            ParrotRegistry.Instance?.Register(Controller);
        }

        private void ConfigureControllerFromManifest()
        {
            var target = Controller as object;
            if (target == null || Manifest == null) return;

            var method = target.GetType().GetMethod(
                "ConfigureFromManifest",
                System.Reflection.BindingFlags.Instance
                    | System.Reflection.BindingFlags.Public
                    | System.Reflection.BindingFlags.NonPublic,
                null,
                new[] { typeof(ModelManifestDto) },
                null);

            if (method == null)
            {
                if (verbose)
                    Debug.Log($"[ModelDriver] Controller '{target.GetType().FullName}' has no ConfigureFromManifest hook.");
                return;
            }

            try
            {
                method.Invoke(target, new object[] { Manifest });
            }
            catch (Exception ex)
            {
                Debug.LogError($"[ModelDriver] ConfigureFromManifest failed for '{target.GetType().FullName}': {ex.Message}");
            }
        }

        private IParrotController ResolveOrAttachController(string controllerType)
        {
            if (string.IsNullOrEmpty(controllerType))
            {
                Debug.LogWarning("[ModelDriver] Manifest controller_type is empty.");
                return null;
            }

            // 1) If the controller is already a component on this GameObject,
            //    reuse it (the typical wiring for hand-set-up prefabs).
            var existing = GetComponentInChildren<IParrotController>();
            if (existing != null)
            {
                if (verbose) Debug.Log($"[ModelDriver] Reusing existing controller '{existing.GetType().FullName}'");
                return existing;
            }

            // 2) Otherwise, reflect the type and AddComponent.
            //    Works inside a single Assembly-CSharp setup (current ArSpike
            //    layout); if the project ever adopts asmdef partitions, the
            //    type-resolution path will need an assembly hint.
            Type t = Type.GetType(controllerType);
            if (t == null)
            {
                Debug.LogError($"[ModelDriver] Type.GetType('{controllerType}') returned null. " +
                               $"Check controller_type spelling + assembly setup.");
                return null;
            }

            if (!typeof(MonoBehaviour).IsAssignableFrom(t))
            {
                Debug.LogError($"[ModelDriver] '{controllerType}' is not a MonoBehaviour.");
                return null;
            }
            if (!typeof(IParrotController).IsAssignableFrom(t))
            {
                Debug.LogError($"[ModelDriver] '{controllerType}' does not implement IParrotController.");
                return null;
            }

            var added = gameObject.AddComponent(t) as IParrotController;
            if (verbose && added != null)
                Debug.Log($"[ModelDriver] Attached new controller '{controllerType}'");
            return added;
        }

        private void ApplyAutoScale()
        {
            // Estimate current rendered height from combined renderer bounds.
            // Falls back to unit_meters if no renderer (rare — most prefabs
            // have at least one MeshRenderer or SkinnedMeshRenderer).
            float currentHeight = 0f;
            var renderers = GetComponentsInChildren<Renderer>(includeInactive: false);
            if (renderers != null && renderers.Length > 0)
            {
                Bounds combined = renderers[0].bounds;
                for (int i = 1; i < renderers.Length; i++) combined.Encapsulate(renderers[i].bounds);
                currentHeight = combined.size.y;
            }

            if (currentHeight <= 0f)
            {
                currentHeight = Manifest.unit_meters; // best-effort fallback
            }
            if (currentHeight <= 0f)
            {
                Debug.LogWarning("[ModelDriver] Auto-scale skipped — could not estimate current model height.");
                return;
            }

            float ratio = Manifest.default_pet_height_m / currentHeight;
            if (ratio <= 0f || float.IsNaN(ratio) || float.IsInfinity(ratio))
            {
                Debug.LogWarning($"[ModelDriver] Auto-scale skipped — invalid ratio {ratio}.");
                return;
            }

            transform.localScale = transform.localScale * ratio;
            if (verbose)
                Debug.Log($"[ModelDriver] Auto-scaled by ×{ratio:F3} (renderer height {currentHeight:F3}m → " +
                          $"target {Manifest.default_pet_height_m}m)");
        }
    }
}
