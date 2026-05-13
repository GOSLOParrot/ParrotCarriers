using System;
using System.Collections.Generic;
using UnityEngine;

namespace ParrotApp.Parrot
{
    /// <summary>
    /// Capability declaration mirror of Python
    /// <c>parrot.shared.model_manifest.Capability</c>. Fields are
    /// JsonUtility-friendly (no dictionaries / no tuples).
    ///
    /// <para>
    /// <c>parameters</c> and <c>description</c> from the Python schema are
    /// intentionally omitted here — Step 2 controllers don't need them on
    /// Unity side, and JsonUtility cannot deserialise <c>dict[str, Any]</c>.
    /// If a future capability needs structured parameters, the call site
    /// will read it from the live RPC payload instead.
    /// </para>
    /// </summary>
    [Serializable]
    public class CapabilityDto
    {
        public string capability_id = "";
        public string kind = "pose";
        public string handler = "";
    }

    /// <summary>
    /// Unity-side mirror of Python <c>parrot.shared.model_manifest.ModelManifest</c>.
    ///
    /// <para>
    /// Spec source: <c>.cursor/memory/architecture/goslo_model_manifest_protocol_v1.md</c>
    /// + <c>src/parrot/shared/model_manifest.py</c>.
    /// </para>
    ///
    /// <para>
    /// JsonUtility constraints intentionally drop a couple of fields from
    /// the Python schema:
    /// </para>
    /// <list type="bullet">
    /// <item><c>author_meta: dict[str, str]</c> — JsonUtility cannot decode
    /// arbitrary string→string maps. Omitted on Unity side; if Unity needs
    /// these later, add a typed adapter.</item>
    /// <item><c>schema_version</c> / <c>manifest_version</c> are read but the
    /// loader does not enforce equality — manifest files can carry newer
    /// minor versions; unrecognised fields are silently ignored, which is
    /// the safe forward-compat behaviour we want for the AI CLI's output.
    /// </item>
    /// </list>
    /// </summary>
    [Serializable]
    public class ModelManifestDto
    {
        public int schema_version = 1;
        public int manifest_version = 1;
        public string model_id = "";
        public string display_name = "";
        public string asset_path = "";
        public string controller_type = "";

        // ─── Coordinate / unit / scale (minimal_lock) ──────────────────
        public string forward_axis = "+Z";
        public string up_axis = "+Y";
        public float unit_meters = 1.0f;
        public float default_pet_height_m = 0.20f;
        public bool auto_scale_to_pet_height = true;

        // ─── Capabilities ─────────────────────────────────────────────
        public CapabilityDto[] capabilities = new CapabilityDto[0];

        // ─── Metadata ────────────────────────────────────────────────
        public string preview_image = "";

        // ─── Reserved Parrot capability set (mirror of Python) ───────
        // Brain LLM vocabulary AND Parrot Reflex layer trigger. Locked to
        // ParrotAnimation enum's 8 string values; do NOT extend / shrink
        // here — the wire-locked source is on the Python side.
        private static readonly HashSet<string> ReservedParrotCapabilityIds = new HashSet<string>
        {
            "idle",
            "fly",
            "dance",
            "wing_flap",
            "perch",
            "sit",
            "head_bob",
            "sleep",
        };

        public static bool IsReservedParrotCapabilityId(string capabilityId)
        {
            return !string.IsNullOrEmpty(capabilityId)
                && ReservedParrotCapabilityIds.Contains(capabilityId);
        }

        /// <summary>
        /// True if any declared capability_id falls in the reserved set.
        /// Mirror of Python <c>ModelManifest.parrot_reflex_enabled</c>.
        /// </summary>
        public bool ParrotReflexEnabled
        {
            get
            {
                if (capabilities == null) return false;
                for (int i = 0; i < capabilities.Length; i++)
                {
                    var c = capabilities[i];
                    if (c != null && IsReservedParrotCapabilityId(c.capability_id))
                        return true;
                }
                return false;
            }
        }

        /// <summary>
        /// Set of declared capability_id strings. Built lazily on first
        /// access; safe for repeated calls. Empty / null capabilities array
        /// produces an empty set.
        /// </summary>
        public HashSet<string> DeclaredCapabilityIds
        {
            get
            {
                var set = new HashSet<string>();
                if (capabilities == null) return set;
                for (int i = 0; i < capabilities.Length; i++)
                {
                    var c = capabilities[i];
                    if (c != null && !string.IsNullOrEmpty(c.capability_id))
                        set.Add(c.capability_id);
                }
                return set;
            }
        }

        public bool Supports(string capabilityId)
        {
            if (string.IsNullOrEmpty(capabilityId) || capabilities == null) return false;
            for (int i = 0; i < capabilities.Length; i++)
            {
                var c = capabilities[i];
                if (c != null && c.capability_id == capabilityId) return true;
            }
            return false;
        }

        /// <summary>
        /// Load a manifest from <c>Resources/parrot_models/&lt;modelId&gt;.json</c>.
        /// Returns null on missing file / parse failure (caller falls back to
        /// the legacy AnimationDriver path); a soft warning is logged so the
        /// problem is visible in Console.
        /// </summary>
        public static ModelManifestDto LoadFromResources(string modelId)
        {
            if (string.IsNullOrEmpty(modelId))
            {
                Debug.LogWarning("[ModelManifest] LoadFromResources: empty modelId");
                return null;
            }

            var path = "parrot_models/" + modelId;
            var ta = Resources.Load<TextAsset>(path);
            if (ta == null)
            {
                Debug.LogWarning($"[ModelManifest] Manifest TextAsset not found: Resources/{path}.json");
                return null;
            }

            try
            {
                var dto = JsonUtility.FromJson<ModelManifestDto>(ta.text);
                if (dto == null || string.IsNullOrEmpty(dto.model_id))
                {
                    Debug.LogWarning($"[ModelManifest] Parsed manifest is empty or missing model_id: Resources/{path}.json");
                    return null;
                }
                return dto;
            }
            catch (Exception ex)
            {
                Debug.LogError($"[ModelManifest] Parse failed for Resources/{path}.json: {ex.Message}");
                return null;
            }
        }
    }
}
