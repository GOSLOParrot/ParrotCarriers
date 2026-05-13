using System.Collections.Generic;
using UnityEngine;

namespace ParrotApp.Parrot
{
    /// <summary>
    /// IParrotController implementation that wraps the existing
    /// <see cref="AnimationDriver"/> — the GOSLO model's procedural
    /// (sin/cos) animation engine.
    ///
    /// <para>
    /// Sprint4 GOSLO model modularization (Step 2, 2026-05-06):
    /// </para>
    /// <list type="bullet">
    /// <item>Routes <c>capability_id</c> → <see cref="AnimationDriver.SetState"/>
    /// or <see cref="AnimationDriver.ApplyBodyStateString"/> equivalents,
    /// covering the 8 reserved ParrotAnimation entries 1:1.</item>
    /// <item>Reflex layer (idle breath / head bob / tail sway / wing micro-flap)
    /// is the AnimationDriver's <c>Update()</c> behaviour by design — this
    /// controller toggles it on/off via <see cref="AnimationDriver.ReflexEnabled"/>
    /// based on the manifest's <c>parrot_reflex_enabled</c> flag.</item>
    /// <item>For GOSLO_default, <c>parrot_reflex_enabled</c> is true and the
    /// observable behaviour matches the pre-modularization AnimationDriver
    /// exactly — Step 2 promises 0 behavioural drift for the default
    /// parrot model.</item>
    /// </list>
    ///
    /// <para>
    /// Wiring: live on the same GameObject as
    /// <see cref="AnimationDriver"/> + <see cref="ModelDriver"/>. ModelDriver
    /// instantiates / discovers this component during Start, then calls
    /// <see cref="ConfigureFromManifest"/> with the loaded manifest so the
    /// controller adopts <c>model_id</c> + capability set + reflex flag.
    /// Without ModelDriver, this component is dormant and the legacy
    /// direct-AnimationDriver path remains the live one.
    /// </para>
    /// </summary>
    [RequireComponent(typeof(AnimationDriver))]
    public class GosloLegacyController : MonoBehaviour, IParrotController
    {
        private AnimationDriver _animDriver;
        private ModelManifestDto _manifest;
        private HashSet<string> _supportedCaps = new HashSet<string>();
        private bool _reflexEnabled = true;

        public string ModelId => _manifest != null ? _manifest.model_id : "GOSLO_default";
        public IReadOnlyCollection<string> SupportedCapabilities => _supportedCaps;
        public bool ParrotReflexEnabled => _reflexEnabled;

        void Awake()
        {
            _animDriver = GetComponent<AnimationDriver>();
            if (_animDriver == null)
            {
                Debug.LogError("[GosloLegacyController] Missing AnimationDriver on same GameObject.");
            }
        }

        void Start()
        {
            // If a ModelDriver is on the same object, it will call
            // ConfigureFromManifest later in its own Start. If there's none,
            // adopt a "GOSLO with all 8 caps + reflex on" default so this
            // controller still functions when used standalone.
            if (_manifest == null)
            {
                _supportedCaps = new HashSet<string>(GosloDefaultCapabilities);
                _reflexEnabled = true;
                if (_animDriver != null) _animDriver.ReflexEnabled = true;
            }
        }

        /// <summary>
        /// Adopt the manifest values. Called by <see cref="ModelDriver"/>
        /// during its Start, after this component has Awake'd. Idempotent.
        /// </summary>
        public void ConfigureFromManifest(ModelManifestDto manifest)
        {
            if (manifest == null) return;
            _manifest = manifest;
            _supportedCaps = manifest.DeclaredCapabilityIds;
            _reflexEnabled = manifest.ParrotReflexEnabled;
            if (_animDriver != null) _animDriver.ReflexEnabled = _reflexEnabled;
        }

        public bool ApplyCapability(string capabilityId, string parametersJson)
        {
            if (_animDriver == null) return false;
            if (string.IsNullOrEmpty(capabilityId)) return false;

            // Graceful-ignore for capabilities the manifest didn't declare.
            // When configured-from-manifest is empty (standalone test mode),
            // _supportedCaps falls back to GosloDefaultCapabilities so all 8
            // reserved ids work out of the box.
            if (_supportedCaps != null
                && _supportedCaps.Count > 0
                && !_supportedCaps.Contains(capabilityId))
            {
                return false;
            }

            // Reserved ParrotAnimation id → existing AnimationDriver SetState/
            // ApplyBodyStateString path. Wire identical to the pre-modular
            // ParrotController.PlayAnimation flow for GOSLO_default.
            switch (capabilityId)
            {
                case "fly":
                    if (TryGetVector3(parametersJson, out var target))
                        _animDriver.FlyTo(target);
                    else
                        _animDriver.SetState(AnimationDriver.BodyState.Fly);
                    return true;

                case "idle":
                case "sleep":
                    _animDriver.SetState(AnimationDriver.BodyState.Idle);
                    return true;

                case "head_bob":
                    _animDriver.SetState(AnimationDriver.BodyState.HeadBob);
                    return true;

                case "perch":
                    _animDriver.SetState(AnimationDriver.BodyState.Perch);
                    return true;

                case "sit":
                    _animDriver.SetState(AnimationDriver.BodyState.Sit);
                    return true;

                case "dance":
                case "wing_flap":
                    _animDriver.SetState(AnimationDriver.BodyState.Dance);
                    return true;

                default:
                    // Unknown capability that was nonetheless declared in the
                    // manifest — should be rare. Forward to ApplyBodyStateString
                    // as a last-resort wire-string match (covers
                    // perched_on_hand / flying / perching / dancing aliases).
                    _animDriver.ApplyBodyStateString(capabilityId);
                    return true;
            }
        }

        // The 8 ParrotAnimation enum entries — used as the standalone fallback
        // capability set when this controller runs without a manifest.
        private static readonly string[] GosloDefaultCapabilities = new[]
        {
            "idle", "fly", "dance", "wing_flap", "perch", "sit", "head_bob", "sleep",
        };

        // Inline payload helper so we don't depend on a shared payload type.
        // RPC handler typically passes the raw FlyToPayload JSON
        // (`{"x":...,"y":...,"z":...,"_ecp":...}`); we extract x/y/z when
        // present without forcing the caller to define a struct here.
        [System.Serializable] private struct Vec3Json { public float x, y, z; }

        private static bool TryGetVector3(string parametersJson, out Vector3 v)
        {
            v = Vector3.zero;
            if (string.IsNullOrEmpty(parametersJson)) return false;
            try
            {
                var p = JsonUtility.FromJson<Vec3Json>(parametersJson);
                v = new Vector3(p.x, p.y, p.z);
                return true;
            }
            catch
            {
                return false;
            }
        }
    }
}
