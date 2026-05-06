using System.Collections.Generic;

namespace ParrotApp.Parrot
{
    /// <summary>
    /// Capability dispatch contract for any model controller wired into the
    /// ParrotCarriers ECP layer.
    ///
    /// <para>
    /// Spec source: <c>.cursor/memory/architecture/goslo_model_manifest_protocol_v1.md</c>
    /// (§4.2 Step 2 — Controller implementation rules).
    /// </para>
    ///
    /// <para>
    /// Sprint4 GOSLO model modularization (Step 2, 2026-05-06):
    /// </para>
    /// <list type="bullet">
    /// <item>
    /// Brain stays decoupled from per-model bone names / Animator state names.
    /// It speaks <c>capability_id</c>; the controller decides how to play it.
    /// </item>
    /// <item>
    /// A controller declares supported <c>capability_id</c> values via its
    /// manifest. <c>ApplyCapability</c> returns false for any capability_id
    /// the controller did not declare — the caller (RPC handler / Brain
    /// observer) can then surface a <c>capability_unsupported</c> ack, no
    /// silent drops.
    /// </item>
    /// <item>
    /// Reserved <c>capability_id</c> values (intersection with
    /// <c>RESERVED_PARROT_CAPABILITY_IDS</c> = <c>ParrotAnimation</c> enum)
    /// activate the Parrot Reflex layer when the controller exposes any of
    /// them. Non-bird controllers simply omit those ids and Reflex stays off.
    /// </item>
    /// </list>
    /// </summary>
    public interface IParrotController
    {
        /// <summary>
        /// Stable identifier this controller answers to in
        /// <see cref="ParrotRegistry"/>. Must match the manifest's
        /// <c>model_id</c> (and, by convention, the manifest filename under
        /// <c>Resources/parrot_models/</c>).
        /// </summary>
        string ModelId { get; }

        /// <summary>
        /// The <c>capability_id</c> set this controller was constructed with
        /// (driven by the manifest). Used by Brain-side query_scene tools and
        /// by the RPC handler's graceful-ignore path.
        /// </summary>
        IReadOnlyCollection<string> SupportedCapabilities { get; }

        /// <summary>
        /// True when this controller's manifest declares any capability whose
        /// id falls in <c>RESERVED_PARROT_CAPABILITY_IDS</c>. Driven by the
        /// loaded <see cref="ModelManifestDto.ParrotReflexEnabled"/> property
        /// — controllers do not invent it.
        /// </summary>
        bool ParrotReflexEnabled { get; }

        /// <summary>
        /// Dispatch a capability call. <paramref name="parametersJson"/> is
        /// the RPC payload's free-form parameters JSON (e.g. flyTo's
        /// <c>{"x":1,"y":0,"z":2}</c> or animate's
        /// <c>{"animation":"dance"}</c>) — the controller parses what it needs
        /// via <c>UnityEngine.JsonUtility</c>.
        /// </summary>
        /// <param name="capabilityId">Capability id; free-form, lower-case
        /// snake_case recommended. May or may not be in the reserved
        /// ParrotAnimation set.</param>
        /// <param name="parametersJson">JSON object as a string. Empty / null
        /// is allowed for capabilities that take no parameters.</param>
        /// <returns>
        /// True if the capability was dispatched (controller began executing
        /// it). False when the controller does not declare this
        /// capability — the caller is expected to surface a
        /// <c>capability_unsupported</c> failure ack so Brain learns about it
        /// instead of getting a silent success.
        /// </returns>
        bool ApplyCapability(string capabilityId, string parametersJson);
    }
}
