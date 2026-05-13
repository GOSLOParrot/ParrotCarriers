"""Tests for the GOSLO model manifest CLI (Step 4 MVP).

Coverage map:
* Capability spec parsing (``id`` / ``id:kind`` / ``id:kind:handler`` / errors).
* Preset application + explicit-flag override layering.
* Scaffolding flow end-to-end (writes a valid manifest, exit 0).
* Validate-only flow on an existing manifest.
* MMD preset bakes the unit_meters=0.08 default user explicitly asked for
  (design Q5, 2026-05-06).
* Validation warnings appear when expected (no caps / no reserved cap /
  weird unit_meters / no namespace dot in controller_type).
* Heuristic capability_id rename suggester fires for near-misses.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import pytest

# Make src/scripts/ importable as a package; mirror the runtime path-setup
# the script itself uses when invoked directly.
_REPO_ROOT = Path(__file__).resolve().parents[2]
if str(_REPO_ROOT / "src") not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT / "src"))
if str(_REPO_ROOT / "src" / "scripts") not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT / "src" / "scripts"))

import asset_to_manifest as cli  # noqa: E402


# ─── Capability spec parser ────────────────────────────────────────────────


def test_capability_spec_full_triple():
    cap = cli.parse_capability_spec("fly:pose:Fly")
    assert cap.capability_id == "fly"
    assert cap.kind.value == "pose"
    assert cap.handler == "Fly"


def test_capability_spec_id_only_defaults_to_pose():
    cap = cli.parse_capability_spec("idle")
    assert cap.capability_id == "idle"
    assert cap.kind.value == "pose"
    assert cap.handler == ""


def test_capability_spec_id_and_kind_no_handler():
    cap = cli.parse_capability_spec("wing_flap:animation")
    assert cap.capability_id == "wing_flap"
    assert cap.kind.value == "animation"
    assert cap.handler == ""


def test_capability_spec_invalid_kind_rejected():
    with pytest.raises(argparse.ArgumentTypeError):
        cli.parse_capability_spec("fly:not_a_kind:Fly")


def test_capability_spec_empty_rejected():
    with pytest.raises(argparse.ArgumentTypeError):
        cli.parse_capability_spec("")
    with pytest.raises(argparse.ArgumentTypeError):
        cli.parse_capability_spec(":pose:Fly")


# ─── Preset layering ───────────────────────────────────────────────────────


def test_preset_default_keeps_gltf_conventions():
    args = cli.build_parser().parse_args([
        "--model-id", "x",
        "--asset-path", "x",
        "--controller-type", "ParrotApp.Parrot.X",
    ])
    coord = cli.apply_preset_defaults(args)
    assert coord["forward_axis"] == "+Z"
    assert coord["up_axis"] == "+Y"
    assert coord["unit_meters"] == 1.0
    assert coord["auto_scale_to_pet_height"] is True


def test_preset_mmd_bakes_unit_meters_eight_centimetres():
    """User Q5 (2026-05-06) explicitly asked for the MMD .pmx + .vmd → FBX
    workflow. MMD's native unit ≈ 8 cm — without baking this preset, every
    MMD import would silently become an 8x-too-big desktop pet."""
    args = cli.build_parser().parse_args([
        "--preset", "mmd",
        "--model-id", "qfufu_v1",
        "--asset-path", "parrot_models/qfufu_v1",
        "--controller-type", "ParrotApp.Parrot.QFufuController",
    ])
    coord = cli.apply_preset_defaults(args)
    assert coord["unit_meters"] == pytest.approx(0.08)
    assert coord["auto_scale_to_pet_height"] is True
    assert coord["default_pet_height_m"] == pytest.approx(0.18)


def test_explicit_flag_overrides_preset():
    args = cli.build_parser().parse_args([
        "--preset", "mmd",
        "--unit-meters", "1.0",
        "--no-auto-scale",
        "--model-id", "x",
        "--asset-path", "x",
        "--controller-type", "ParrotApp.Parrot.X",
    ])
    coord = cli.apply_preset_defaults(args)
    assert coord["unit_meters"] == 1.0
    assert coord["auto_scale_to_pet_height"] is False


# ─── Author meta parsing ───────────────────────────────────────────────────


def test_parse_author_meta_simple():
    out = cli.parse_author_meta(["license=CC-BY-4.0", "author=Alice"])
    assert out == {"license": "CC-BY-4.0", "author": "Alice"}


def test_parse_author_meta_rejects_bare_token():
    with pytest.raises(argparse.ArgumentTypeError):
        cli.parse_author_meta(["broken"])


def test_parse_author_meta_keeps_value_with_equals():
    """`a=b=c` should split on the FIRST '=' only, keeping `b=c` as the value."""
    out = cli.parse_author_meta(["url=https://x?y=1"])
    assert out == {"url": "https://x?y=1"}


# ─── Scaffolding end-to-end ────────────────────────────────────────────────


def _run_main(argv: list[str], capsys) -> tuple[int, str, str]:
    code = cli.main(argv)
    captured = capsys.readouterr()
    return code, captured.out, captured.err


def test_scaffold_minimal_manifest_round_trips_through_pydantic(tmp_path, capsys):
    out_path = tmp_path / "owl.json"
    code, out, err = _run_main(
        [
            "--model-id", "owl_v1",
            "--display-name", "Sparkle the Owl",
            "--asset-path", "parrot_models/owl_v1",
            "--controller-type", "ParrotApp.Parrot.OwlController",
            "--capability", "idle:pose:Idle",
            "--capability", "fly:pose:Fly",
            "--capability", "head_bob:pose:HeadBob",
            "--out", str(out_path),
        ],
        capsys,
    )
    assert code == 0, err
    assert out_path.exists()

    raw = json.loads(out_path.read_text(encoding="utf-8"))
    assert raw["model_id"] == "owl_v1"
    assert raw["display_name"] == "Sparkle the Owl"
    assert {c["capability_id"] for c in raw["capabilities"]} == {
        "idle", "fly", "head_bob",
    }
    # Reflex layer should be ON because all three are reserved ids.
    # The CLI report must say so.
    assert "Parrot Reflex layer   : ENABLED" in out


def test_scaffold_missing_required_args_exits_2(tmp_path, capsys):
    code, _out, err = _run_main(
        ["--model-id", "x"],   # missing asset-path + controller-type
        capsys,
    )
    assert code == 2
    assert "scaffolding requires" in err


def test_scaffold_invalid_capability_id_rejected_by_pydantic(tmp_path, capsys):
    """Whitespace in capability_id must be caught by ``Capability``'s
    field_validator. argparse aborts with SystemExit(2) when the
    ``parse_capability_spec`` type-converter raises ArgumentTypeError;
    the wrapper turns the Pydantic ValidationError into a readable
    "schema validation failed" message."""
    with pytest.raises(SystemExit) as excinfo:
        _run_main(
            [
                "--model-id", "x",
                "--asset-path", "x",
                "--controller-type", "ParrotApp.Parrot.X",
                # Embedded space — Capability.capability_id rejects it.
                "--capability", "head bob:pose",
                "--out", str(tmp_path / "x.json"),
            ],
            capsys,
        )
    assert excinfo.value.code == 2
    err = capsys.readouterr().err
    assert "schema validation failed" in err


def test_scaffold_print_only_does_not_write_file(tmp_path, capsys):
    code, out, _err = _run_main(
        [
            "--model-id", "x",
            "--asset-path", "x",
            "--controller-type", "ParrotApp.Parrot.X",
            "--capability", "idle",
            "--print-only",
        ],
        capsys,
    )
    assert code == 0
    # JSON body is on stdout
    assert '"model_id": "x"' in out
    assert "wrote " not in out


# ─── Validate-only flow ────────────────────────────────────────────────────


def test_validate_only_on_goslo_default_baseline(capsys):
    """The shipped GOSLO default manifest must validate cleanly — this is
    the in-repo sentinel guarding Step 2's compatibility promise."""
    baseline = (
        _REPO_ROOT
        / "unity"
            / "ArSpike"
            / "Assets"
            / "ParrotApp"
            / "Resources"
            / "parrot_models"
            / "goslo_default.json"
    )
    code, out, err = _run_main(
        ["--validate-only", "--in", str(baseline)],
        capsys,
    )
    assert code == 0, err
    assert "Parrot Reflex layer   : ENABLED" in out
    assert "model_id              : GOSLO_default" in out


def test_validate_only_reports_schema_failure_with_exit_2(tmp_path, capsys):
    bad = tmp_path / "bad.json"
    bad.write_text(
        json.dumps({
            "model_id": "bad",
            "asset_path": "x",
            "controller_type": "x",
            "forward_axis": "north",   # invalid — schema must reject
        }),
        encoding="utf-8",
    )
    code, _out, err = _run_main(
        ["--validate-only", "--in", str(bad)],
        capsys,
    )
    assert code == 2
    assert "schema validation failed" in err


def test_validate_only_reports_invalid_json_with_exit_2(tmp_path, capsys):
    bad = tmp_path / "garbage.json"
    bad.write_text("{ not json", encoding="utf-8")
    code, _out, err = _run_main(
        ["--validate-only", "--in", str(bad)],
        capsys,
    )
    assert code == 2
    assert "not valid JSON" in err


# ─── Validation report content ─────────────────────────────────────────────


def test_report_warns_when_no_capabilities_declared(tmp_path, capsys):
    code, out, _err = _run_main(
        [
            "--model-id", "x",
            "--asset-path", "x",
            "--controller-type", "ParrotApp.Parrot.X",
            "--print-only",
        ],
        capsys,
    )
    assert code == 0
    assert "No capabilities declared" in out


def test_report_warns_when_only_custom_caps(tmp_path, capsys):
    code, out, _err = _run_main(
        [
            "--model-id", "qfufu_v1",
            "--asset-path", "parrot_models/qfufu_v1",
            "--controller-type", "ParrotApp.Parrot.QFufuController",
            "--capability", "wave_hand:animation",
            "--capability", "bow:animation",
            "--print-only",
        ],
        capsys,
    )
    assert code == 0
    assert "No reserved ParrotAnimation capability_id declared" in out
    assert "Parrot Reflex layer   : disabled" in out


def test_report_warns_when_controller_type_missing_namespace(tmp_path, capsys):
    code, out, _err = _run_main(
        [
            "--model-id", "x",
            "--asset-path", "x",
            "--controller-type", "OwlController",  # no dot
            "--capability", "idle",
            "--print-only",
        ],
        capsys,
    )
    assert code == 0
    assert "has no namespace dot" in out


# ─── Heuristic suggestion ──────────────────────────────────────────────────


def test_suggester_recommends_renaming_near_miss_to_reserved(tmp_path, capsys):
    """`flying` is a custom id that contains the reserved `fly` — the
    heuristic should suggest the rename so Brain's default tool reaches it."""
    code, out, _err = _run_main(
        [
            "--model-id", "x",
            "--asset-path", "x",
            "--controller-type", "ParrotApp.Parrot.X",
            "--capability", "flying:pose:Fly",
            "--print-only",
        ],
        capsys,
    )
    assert code == 0
    assert "Naming suggestions" in out
    assert "fly" in out


def test_suggester_silent_when_capability_already_reserved(tmp_path, capsys):
    code, out, _err = _run_main(
        [
            "--model-id", "x",
            "--asset-path", "x",
            "--controller-type", "ParrotApp.Parrot.X",
            "--capability", "fly:pose:Fly",
            "--print-only",
        ],
        capsys,
    )
    assert code == 0
    assert "Naming suggestions" not in out
