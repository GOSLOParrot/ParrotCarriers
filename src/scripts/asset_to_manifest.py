"""GOSLO model manifest CLI — MVP for ``goslo_model_modularization`` Step 4.

Spec source:
    .cursor/memory/architecture/goslo_model_manifest_protocol_v1.md
    src/parrot/shared/model_manifest.py

WHY THIS SCRIPT EXISTS
----------------------
Sprint4 GOSLO model modularization (2026-05-06) introduces a manifest-driven
controller layer on the Unity side (``ModelDriver`` / ``IParrotController``).
A model author hand-writing every manifest is doable but error-prone — this
CLI is the "rules-bearing" assistant that:

* Builds a syntactically valid manifest from ``--key value`` flags so the
  author cannot typo a field name (the Pydantic schema rejects unknown keys).
* Emits warnings for non-standard coordinate axes, unusual unit scales, or
  empty capability sets — the kind of thing that compiles but feels wrong.
* Supports presets (``--preset mmd``) for the common MMD ``.pmx + .vmd → FBX``
  workflow user explicitly asked about (design Q5, 2026-05-06).
* Has a ``--validate-only`` mode for "I wrote this by hand, did I get it
  right?" sanity checks.

WHAT THIS SCRIPT INTENTIONALLY DOES NOT DO (Step 4 MVP)
-------------------------------------------------------
* No ``.fbx`` / ``.glb`` binary parsing — depending on ``pyassimp`` /
  ``gltflib`` is out of scope for this Chat (would need a new optional
  dependency group). Bone / clip auto-discovery is a future enhancement,
  documented in the residual debt audit.
* No Gemini Flash LLM call for ``clip_name → capability_id`` suggestions.
  The CLI prints "consider mapping clip 'X' to capability_id 'Y'" guidance
  based on simple heuristics (substring match against reserved ids), not
  via an external API.
* No controller ``.cs`` codegen. Per design Q-C, we only emit manifest +
  validation report; the model author writes their own MonoBehaviour. The
  protocol-rule documentation in
  ``goslo_model_manifest_protocol_v1.md §4.2`` walks them through it.

USAGE
-----
Quick scaffolding (non-MMD model with custom capabilities)::

    python src/scripts/asset_to_manifest.py \\
        --model-id owl_v1 \\
        --display-name "Sparkle the Owl" \\
        --asset-path parrot_models/owl_v1 \\
        --controller-type ParrotApp.Parrot.OwlController \\
        --capability idle:pose:Idle \\
        --capability fly:pose:Fly \\
        --capability head_bob:pose:HeadBob \\
        --out unity/ArSpike/Assets/ParrotApp/Resources/parrot_models/owl_v1.json

MMD preset (auto-sets unit_meters=0.08, auto_scale_to_pet_height=true)::

    python src/scripts/asset_to_manifest.py \\
        --preset mmd \\
        --model-id qfufu_v1 \\
        --display-name "橘福福" \\
        --asset-path parrot_models/qfufu_v1 \\
        --controller-type ParrotApp.Parrot.QFufuController \\
        --capability idle:pose:Idle \\
        --capability wave_hand:animation:Wave \\
        --capability dance_q_pose:animation:Dance \\
        --capability bow:animation:Bow \\
        --out unity/ArSpike/Assets/ParrotApp/Resources/parrot_models/qfufu_v1.json

Validate an existing manifest in place::

    python src/scripts/asset_to_manifest.py \\
        --validate-only \\
        --in unity/ArSpike/Assets/ParrotApp/Resources/parrot_models/qfufu_v1.json
"""

from __future__ import annotations

import argparse
import json
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any

# Make `parrot.shared.model_manifest` importable when running this file
# directly (mirrors the pattern used by other src/scripts/*.py scripts).
_REPO_ROOT = Path(__file__).resolve().parents[2]
if str(_REPO_ROOT / "src") not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT / "src"))

from parrot.shared.model_manifest import (  # noqa: E402  (post-sys.path edit)
    DEFAULT_MODEL_ID,
    RESERVED_PARROT_CAPABILITY_IDS,
    Capability,
    CapabilityKind,
    ModelManifest,
)


# ─── Presets ───────────────────────────────────────────────────────────────


@dataclass(frozen=True)
class Preset:
    """A preset is a curated bundle of axis / unit / scale defaults that
    shortcut the common case for a particular asset family. Authors can
    still override any preset value with an explicit flag — argparse
    layering takes care of that automatically."""

    name: str
    forward_axis: str = "+Z"
    up_axis: str = "+Y"
    unit_meters: float = 1.0
    default_pet_height_m: float = 0.20
    auto_scale_to_pet_height: bool = True
    note: str = ""


PRESETS: dict[str, Preset] = {
    "default": Preset(
        name="default",
        note="glTF-standard +Z forward / +Y up / 1 unit = 1 metre.",
    ),
    "mmd": Preset(
        name="mmd",
        unit_meters=0.08,
        default_pet_height_m=0.18,
        auto_scale_to_pet_height=True,
        note="MMD .pmx + .vmd → FBX (1 unit ≈ 8 cm). auto-scale → desktop pet size.",
    ),
}


# ─── Parsing helpers ───────────────────────────────────────────────────────


def parse_capability_spec(spec: str) -> Capability:
    """Parse a ``capability_id:kind:handler`` triple into a Capability.

    ``handler`` is optional (defaults to empty string). ``kind`` defaults
    to ``"pose"`` when only one segment is given. Empty strings between
    colons are treated as "use the default" so authors can say
    ``--capability fly`` (kind=pose, handler="") for a quick prototype.
    """
    parts = spec.split(":")
    if not parts or not parts[0]:
        raise argparse.ArgumentTypeError(f"empty capability spec: {spec!r}")

    capability_id = parts[0].strip()
    kind_raw = (parts[1].strip() if len(parts) >= 2 and parts[1].strip() else "pose")
    handler = parts[2].strip() if len(parts) >= 3 else ""

    try:
        kind = CapabilityKind(kind_raw)
    except ValueError:
        valid = ", ".join(k.value for k in CapabilityKind)
        raise argparse.ArgumentTypeError(
            f"invalid capability kind {kind_raw!r} in {spec!r}; valid: {valid}"
        )

    # Wrap the Pydantic ValidationError so argparse surfaces a readable
    # "schema validation failed: ..." message instead of the generic
    # "invalid parse_capability_spec value" wording.
    try:
        return Capability(capability_id=capability_id, kind=kind, handler=handler)
    except Exception as e:
        raise argparse.ArgumentTypeError(
            f"schema validation failed for capability {spec!r}: {e}"
        )


# ─── CLI definition ────────────────────────────────────────────────────────


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        prog="asset_to_manifest",
        description="GOSLO model manifest scaffolding + validation CLI.",
    )

    p.add_argument(
        "--validate-only",
        action="store_true",
        help="Read --in and just validate it; print a report and exit.",
    )
    p.add_argument(
        "--in",
        dest="in_path",
        type=Path,
        default=None,
        help="Manifest path to validate (with --validate-only).",
    )

    # Identity
    p.add_argument("--model-id", type=str, default=None,
                   help=f"Manifest model_id. Default: '{DEFAULT_MODEL_ID}'.")
    p.add_argument("--display-name", type=str, default="",
                   help="Human-readable name. May contain non-ASCII / Chinese.")
    p.add_argument("--asset-path", type=str, default=None,
                   help="Unity Resources path (no extension).")
    p.add_argument("--controller-type", type=str, default=None,
                   help="MonoBehaviour FQCN for IParrotController, "
                        "e.g. ParrotApp.Parrot.OwlController.")

    # Preset + coord/scale
    p.add_argument("--preset", type=str, choices=sorted(PRESETS), default="default",
                   help="Coordinate / unit preset bundle.")
    p.add_argument("--forward-axis", type=str, default=None,
                   choices=["+X", "-X", "+Y", "-Y", "+Z", "-Z"])
    p.add_argument("--up-axis", type=str, default=None,
                   choices=["+X", "-X", "+Y", "-Y", "+Z", "-Z"])
    p.add_argument("--unit-meters", type=float, default=None)
    p.add_argument("--default-pet-height-m", type=float, default=None)
    p.add_argument("--auto-scale", dest="auto_scale", action="store_true", default=None)
    p.add_argument("--no-auto-scale", dest="auto_scale", action="store_false")

    # Capabilities (repeated)
    p.add_argument(
        "--capability",
        action="append",
        type=parse_capability_spec,
        default=[],
        metavar="ID[:KIND[:HANDLER]]",
        help="Declare one capability. Repeat --capability for each. "
             "KIND is pose / animation / procedural (default pose). "
             "HANDLER is optional controller-internal name.",
    )

    # Metadata
    p.add_argument("--preview-image", type=str, default="",
                   help="Resources path of preview image (no extension).")
    p.add_argument(
        "--author-meta",
        action="append",
        default=[],
        metavar="KEY=VALUE",
        help="Repeated. Free metadata pairs (e.g. license=CC-BY-4.0).",
    )

    # Output
    p.add_argument("--out", type=Path, default=None,
                   help="Output manifest path. Defaults to <model-id>.json next to CWD.")
    p.add_argument("--print-only", action="store_true",
                   help="Print the JSON to stdout without writing a file.")

    return p


def parse_author_meta(specs: list[str]) -> dict[str, str]:
    out: dict[str, str] = {}
    for s in specs:
        if "=" not in s:
            raise argparse.ArgumentTypeError(f"--author-meta must be KEY=VALUE, got {s!r}")
        k, v = s.split("=", 1)
        out[k.strip()] = v.strip()
    return out


def apply_preset_defaults(args: argparse.Namespace) -> dict[str, Any]:
    """Resolve effective values: explicit flags override preset, preset
    overrides hard defaults. Returns a kwargs dict for ModelManifest."""
    preset = PRESETS[args.preset]

    return dict(
        forward_axis=args.forward_axis or preset.forward_axis,
        up_axis=args.up_axis or preset.up_axis,
        unit_meters=args.unit_meters if args.unit_meters is not None else preset.unit_meters,
        default_pet_height_m=(
            args.default_pet_height_m
            if args.default_pet_height_m is not None
            else preset.default_pet_height_m
        ),
        auto_scale_to_pet_height=(
            args.auto_scale
            if args.auto_scale is not None
            else preset.auto_scale_to_pet_height
        ),
    )


# ─── Reporting ─────────────────────────────────────────────────────────────


def render_validation_report(manifest: ModelManifest) -> list[str]:
    """Render a short, opinionated report — non-fatal warnings + summary.

    Returns a list of lines; caller prints them. Designed to surface the
    "compiles but feels wrong" cases (no reserved capabilities → reflex
    silently disabled; unit_meters very different from 1 → likely scale
    issue; empty capability set → controller is a no-op).
    """
    lines: list[str] = []
    lines.append(f"model_id              : {manifest.model_id}")
    if manifest.display_name:
        lines.append(f"display_name          : {manifest.display_name}")
    lines.append(f"asset_path            : {manifest.asset_path}")
    lines.append(f"controller_type       : {manifest.controller_type}")
    lines.append(f"forward / up          : {manifest.forward_axis} / {manifest.up_axis}")
    lines.append(f"unit_meters           : {manifest.unit_meters}")
    lines.append(
        f"default_pet_height_m  : {manifest.default_pet_height_m} "
        f"(auto_scale={manifest.auto_scale_to_pet_height})"
    )
    lines.append(f"capabilities ({len(manifest.capabilities)})    :")
    reserved = []
    custom = []
    for c in manifest.capabilities:
        tag = "reserved" if c.is_reserved_parrot_id else "custom"
        bullet = f"    - {c.capability_id} ({c.kind.value}) [{tag}]"
        if c.handler:
            bullet += f" handler={c.handler}"
        lines.append(bullet)
        (reserved if c.is_reserved_parrot_id else custom).append(c.capability_id)

    lines.append("")
    lines.append(
        f"Parrot Reflex layer   : "
        f"{'ENABLED' if manifest.parrot_reflex_enabled else 'disabled'} "
        f"({len(reserved)} reserved capability_id(s) declared)"
    )

    # Warnings
    warnings: list[str] = []
    if not manifest.capabilities:
        warnings.append(
            "No capabilities declared — the controller will graceful-ignore "
            "every Brain call. Add at least one --capability."
        )
    if manifest.forward_axis != "+Z":
        warnings.append(
            f"forward_axis={manifest.forward_axis} differs from glTF default '+Z'. "
            "Make sure the controller agrees."
        )
    if manifest.up_axis != "+Y":
        warnings.append(
            f"up_axis={manifest.up_axis} differs from Unity default '+Y'. "
            "Double-check rigging."
        )
    if manifest.unit_meters <= 0.0 or manifest.unit_meters > 100.0:
        warnings.append(
            f"unit_meters={manifest.unit_meters} looks suspicious (expected ~0.01–10)."
        )
    if not reserved and manifest.capabilities:
        warnings.append(
            "No reserved ParrotAnimation capability_id declared — Brain LLM's "
            "default vocabulary (idle/fly/dance/...) cannot drive this model. "
            "Triggers must come from dispatch_task or a future custom tool. "
            "If this is intentional (non-bird companion), ignore this warning."
        )
    if manifest.controller_type and "." not in manifest.controller_type:
        warnings.append(
            f"controller_type='{manifest.controller_type}' has no namespace dot — "
            "MonoBehaviour FQCN usually looks like 'ParrotApp.Parrot.<Name>Controller'."
        )

    if warnings:
        lines.append("")
        lines.append("Warnings:")
        for w in warnings:
            lines.append(f"  ! {w}")

    return lines


# ─── Main flows ────────────────────────────────────────────────────────────


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)

    if args.validate_only:
        return _run_validate_only(args)
    return _run_scaffold(args)


def _run_validate_only(args: argparse.Namespace) -> int:
    if args.in_path is None:
        print("error: --validate-only requires --in <path>", file=sys.stderr)
        return 2
    if not args.in_path.exists():
        print(f"error: manifest not found: {args.in_path}", file=sys.stderr)
        return 2
    try:
        raw = json.loads(args.in_path.read_text(encoding="utf-8"))
        manifest = ModelManifest.model_validate(raw)
    except json.JSONDecodeError as e:
        print(f"error: not valid JSON: {e}", file=sys.stderr)
        return 2
    except Exception as e:
        print(f"error: schema validation failed: {e}", file=sys.stderr)
        return 2

    print(f"OK  {args.in_path}")
    for line in render_validation_report(manifest):
        print(line)
    return 0


def _run_scaffold(args: argparse.Namespace) -> int:
    # Required fields when scaffolding (validate-only path doesn't need them)
    missing = [
        flag
        for flag, value in [
            ("--model-id", args.model_id),
            ("--asset-path", args.asset_path),
            ("--controller-type", args.controller_type),
        ]
        if not value
    ]
    if missing:
        print(
            f"error: scaffolding requires {', '.join(missing)}. "
            "Add them or use --validate-only on an existing manifest.",
            file=sys.stderr,
        )
        return 2

    coord = apply_preset_defaults(args)
    try:
        author_meta = parse_author_meta(args.author_meta)
        manifest = ModelManifest(
            model_id=args.model_id,
            display_name=args.display_name,
            asset_path=args.asset_path,
            controller_type=args.controller_type,
            capabilities=tuple(args.capability),
            preview_image=args.preview_image,
            author_meta=author_meta,
            **coord,
        )
    except Exception as e:
        print(f"error: schema validation failed: {e}", file=sys.stderr)
        return 2

    out_json = json.dumps(
        manifest.model_dump(mode="json"),
        ensure_ascii=False,
        indent=2,
    ) + "\n"

    if args.print_only:
        print(out_json, end="")
    else:
        out_path = args.out or Path(f"{manifest.model_id}.json")
        out_path.parent.mkdir(parents=True, exist_ok=True)
        out_path.write_text(out_json, encoding="utf-8")
        print(f"wrote {out_path}")

    print()
    for line in render_validation_report(manifest):
        print(line)

    # Heuristic suggestion: if author declared a custom capability_id whose
    # text is similar to a reserved one, hint at the rename. Cheap and
    # offline — no LLM call.
    suggestions = _suggest_capability_renames(manifest)
    if suggestions:
        print()
        print("Naming suggestions (heuristic — review before applying):")
        for s in suggestions:
            print(f"  ? {s}")

    return 0


def _suggest_capability_renames(manifest: ModelManifest) -> list[str]:
    """Tiny offline suggester — when a custom capability_id is a substring
    or near-match of a reserved id, recommend the rename so Brain LLM can
    actually drive it. Strictly substring/prefix-based; no LLM.
    """
    out: list[str] = []
    declared = manifest.declared_capability_ids
    for c in manifest.capabilities:
        if c.is_reserved_parrot_id:
            continue
        cid = c.capability_id.lower()
        for reserved in RESERVED_PARROT_CAPABILITY_IDS:
            if reserved in declared:
                continue  # already declared by manifest
            if reserved == cid:
                continue
            if reserved in cid or cid in reserved:
                out.append(
                    f"capability_id '{c.capability_id}' looks similar to reserved "
                    f"'{reserved}' — consider declaring it under that name so Brain "
                    f"LLM's default `animate(animation_name='{reserved}')` reaches it."
                )
                break
    return out


if __name__ == "__main__":
    sys.exit(main())
