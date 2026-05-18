using System.Collections.Generic;
using UnityEngine;

namespace ParrotApp.Parrot
{
    /// <summary>
    /// Routing registry for installed model controllers.
    ///
    /// <para>
    /// Sprint4 GOSLO model modularization (Step 2, 2026-05-06) — P1 single-active stub:
    /// </para>
    /// <list type="bullet">
    /// <item>Multiple controllers may register, but <see cref="Resolve"/> always
    /// returns the most-recently-registered (the "active") controller —
    /// regardless of the requested <c>model_id</c>. This is the
    /// single-active deployment promise the design draft (§G) made.</item>
    /// <item>P3 multi-actor will swap this stub for true model_id-keyed routing
    /// + spawn / despawn tools. Wire is unchanged: P1 callers can keep
    /// passing <c>meta.model_id = ""</c> for the active controller, and P3
    /// will start honouring non-empty values.</item>
    /// </list>
    ///
    /// <para>
    /// Lifecycle: scene-singleton (matches <c>RoomManager</c> / similar managers
    /// in <c>ParrotApp.LiveKit</c>). Created either by a <see cref="ModelDriver"/>
    /// during its first Awake or by being placed manually on a manager
    /// GameObject. <c>Instance</c> may be null during cold start; consumers
    /// must null-check.
    /// </para>
    /// </summary>
    public class ParrotRegistry : MonoBehaviour
    {
        public static ParrotRegistry Instance { get; private set; }

        // Insertion-ordered store — last-registered wins for Resolve("") in P1.
        // Dictionary keyed by model_id so future P3 lookup is O(1) without
        // a schema change.
        private readonly Dictionary<string, IParrotController> _byModelId =
            new Dictionary<string, IParrotController>();
        private string _activeModelId = "";

        /// <summary>
        /// Ensures a Registry exists in the scene; idempotent. Call from
        /// <see cref="ModelDriver"/> Awake so manual prefab wiring is
        /// optional. Returns the live instance.
        /// </summary>
        public static ParrotRegistry EnsureInstance()
        {
            if (Instance != null) return Instance;
            var existing = FindObjectOfType<ParrotRegistry>();
            if (existing != null)
            {
                Instance = existing;
                return Instance;
            }
            var go = new GameObject("ParrotRegistry");
            Instance = go.AddComponent<ParrotRegistry>();
            return Instance;
        }

        void Awake()
        {
            if (Instance != null && Instance != this)
            {
                Debug.LogWarning("[ParrotRegistry] Duplicate instance — destroying the new one");
                Destroy(this);
                return;
            }
            Instance = this;
        }

        void OnDestroy()
        {
            if (Instance == this) Instance = null;
            _byModelId.Clear();
            _activeModelId = "";
        }

        /// <summary>
        /// Register a controller. Last-registered becomes the active one
        /// (P1 single-active semantics). Re-registering the same model_id
        /// updates the entry but does NOT reorder activity.
        /// </summary>
        public void Register(IParrotController controller)
        {
            if (IsDestroyed(controller))
            {
                Debug.LogWarning("[ParrotRegistry] Register: null controller");
                return;
            }
            var modelId = controller.ModelId ?? "";
            if (string.IsNullOrEmpty(modelId))
            {
                Debug.LogWarning("[ParrotRegistry] Register: controller has empty ModelId — using fallback key 'unnamed'");
                modelId = "unnamed";
            }

            _byModelId[modelId] = controller;
            _activeModelId = modelId;
            Debug.Log($"[ParrotRegistry] Registered model_id='{modelId}' caps={controller.SupportedCapabilities?.Count ?? 0}");
        }

        public void Unregister(string modelId)
        {
            if (string.IsNullOrEmpty(modelId)) return;
            if (_byModelId.Remove(modelId))
            {
                if (_activeModelId == modelId) _activeModelId = "";
                Debug.Log($"[ParrotRegistry] Unregistered model_id='{modelId}'");
            }
        }

        public void Unregister(IParrotController controller)
        {
            if (IsDestroyed(controller)) return;
            var modelId = controller.ModelId ?? "";
            if (string.IsNullOrEmpty(modelId)) return;

            if (_byModelId.TryGetValue(modelId, out var registered)
                && ReferenceEquals(registered, controller))
            {
                Unregister(modelId);
            }
        }

        /// <summary>
        /// P1 stub: empty / unknown <paramref name="modelId"/> returns the
        /// active controller (last-registered). Non-empty matches return the
        /// registered entry IF it exists, else still falls through to active
        /// — preserving P1 single-active backward compat. P3 will tighten
        /// this to throw / explicit-null on unknown ids.
        /// </summary>
        public IParrotController Resolve(string modelId)
        {
            PruneDestroyedControllers();

            if (!string.IsNullOrEmpty(modelId)
                && _byModelId.TryGetValue(modelId, out var found))
            {
                return found;
            }

            if (!string.IsNullOrEmpty(_activeModelId)
                && _byModelId.TryGetValue(_activeModelId, out var active))
            {
                return active;
            }
            return null;
        }

        private void PruneDestroyedControllers()
        {
            if (_byModelId.Count == 0) return;

            var dead = new List<string>();
            foreach (var kv in _byModelId)
            {
                if (IsDestroyed(kv.Value))
                    dead.Add(kv.Key);
            }

            for (int i = 0; i < dead.Count; i++)
            {
                _byModelId.Remove(dead[i]);
                if (_activeModelId == dead[i]) _activeModelId = "";
                Debug.Log($"[ParrotRegistry] Pruned destroyed model_id='{dead[i]}'");
            }
        }

        private static bool IsDestroyed(IParrotController controller)
        {
            if (ReferenceEquals(controller, null)) return true;
            var unityObject = controller as Object;
            return !ReferenceEquals(unityObject, null) && unityObject == null;
        }

        public string ActiveModelId => _activeModelId;

        public IReadOnlyCollection<string> RegisteredModelIds => _byModelId.Keys;
    }
}
