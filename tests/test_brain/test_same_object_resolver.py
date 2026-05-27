from __future__ import annotations

import importlib
import json
from pathlib import Path

import pytest
from PIL import Image

from parrot.brain.vision.evidence import EvidenceKind, SampleRegion, get_evidence_ledger
from parrot.brain.vision.object_discovery import accept_new_object_from_evidence
from parrot.brain.vision.same_object_resolver import resolve_same_object
from parrot.dsg.l2b_graph import L2BGraph
from parrot.dsg.l2b_types import ConfirmationStatus, NodeKind, SemanticNode


@pytest.fixture(autouse=True)
def _reset_state(tmp_path: Path, monkeypatch: pytest.MonkeyPatch):
    monkeypatch.setenv("PARROT_VISION_ROOT", str(tmp_path / "vision"))
    monkeypatch.setenv(
        "PARROT_MEMORY_IDENTITY_REF_INDEX_PATH",
        str(tmp_path / "identity_ref_index.json"),
    )
    get_evidence_ledger().reset_for_tests()
    graph_module = importlib.import_module("parrot.dsg.l2b_graph")
    graph_module._instance = L2BGraph()
    yield
    get_evidence_ledger().reset_for_tests()
    graph_module._instance = None


@pytest.mark.asyncio
async def test_same_object_resolver_matches_accepted_sample(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    graph_module = importlib.import_module("parrot.dsg.l2b_graph")
    graph = graph_module.get_l2b_graph()
    graph.upsert_node(
        SemanticNode(
            uuid="obj_resolver",
            kind=NodeKind.OBJECT,
            label="red cup",
            category="cup",
            confirmation=ConfirmationStatus.CONFIRMED,
        )
    )
    accepted_asset = _write_image(tmp_path / "accepted.png", size=(96, 96), color=(230, 20, 20))
    accepted_evidence = get_evidence_ledger().record_sample(
        kind=EvidenceKind.IMAGE_ASSET,
        asset_path=str(accepted_asset),
        mime_type="image/png",
        region=SampleRegion(x=0.0, y=0.0, width=1.0, height=1.0),
    )
    accept_new_object_from_evidence(
        object_uuid="obj_resolver",
        description="red cup",
        category="cup",
        evidence_sample=accepted_evidence,
    )
    target_asset = _write_image(tmp_path / "target.png", size=(96, 96), color=(230, 20, 20))
    target_evidence = get_evidence_ledger().record_sample(
        kind=EvidenceKind.IMAGE_ASSET,
        asset_path=str(target_asset),
        mime_type="image/png",
        region=SampleRegion(x=0.0, y=0.0, width=1.0, height=1.0),
        meta={"photo_id": "ph_target"},
    )

    async def fake_compare(current_b64, candidates, model_name="gemini-2.5-flash"):
        assert current_b64
        assert candidates[0]["uuid"] == "obj_resolver"
        assert candidates[0]["reference_image_b64"]
        return ("obj_resolver", 0.83)

    visual_match = importlib.import_module("parrot.brain.vision.visual_match")
    monkeypatch.setattr(visual_match, "compare_current_frame", fake_compare)

    report = await resolve_same_object(
        evidence_sample=target_evidence,
        description="red cup",
        category="cup",
        photo_id="ph_target",
    )

    assert report["status"] == "matched"
    assert report["best_object_uuid"] == "obj_resolver"
    assert report["best_confidence"] == pytest.approx(0.83)
    assert report["recommended_action"] == "bind_existing"
    assert Path(report["report_path"]).is_file()
    persisted = json.loads(Path(report["report_path"]).read_text(encoding="utf-8"))
    assert persisted["report_path"] == report["report_path"]
    assert report["candidate_objects"][0]["sample_ids"]
    assert report["compared_samples"][0]["confidence"] == pytest.approx(0.83)
    assert "reference_image_b64" not in str(report)


@pytest.mark.asyncio
async def test_identify_object_match_waits_for_same_object_resolver(monkeypatch: pytest.MonkeyPatch):
    id_module = importlib.import_module("parrot.brain.tools.identify_object")
    evidence = get_evidence_ledger().record_sample(
        kind=EvidenceKind.IMAGE_ASSET,
        asset_path=str(Path(__file__).resolve()),
        mime_type="image/png",
    )
    matched_calls: list[dict] = []

    async def fake_capture(**kwargs):
        return evidence

    async def fake_describe(sample):
        return "red cup"

    async def fake_resolver(**kwargs):
        return {
            "status": "matched",
            "best_object_uuid": "obj_waited",
            "best_confidence": 0.86,
            "report_path": "data/vision/reports/same_object/job.json",
            "candidate_objects": [
                {"object_uuid": "obj_waited", "label": "red cup"},
            ],
        }

    async def fake_on_match(**kwargs):
        matched_calls.append(kwargs)

    async def fail_l0(*args, **kwargs):
        raise AssertionError("L0 should not run after same-object matched")

    monkeypatch.setattr(id_module, "resolve_identify_evidence", fake_capture)
    monkeypatch.setattr(id_module, "describe_evidence_sample", fake_describe)
    monkeypatch.setattr(id_module, "resolve_same_object", fake_resolver)
    monkeypatch.setattr(id_module, "_on_match", fake_on_match)
    monkeypatch.setattr(id_module, "_l0_text_fast_match", fail_l0)

    out = await id_module._match_staged("cup", "cup")

    assert "[same-object] matched" in out
    assert "identified: red cup" in out
    assert matched_calls[0]["source"] == "same_object_resolver"
    assert matched_calls[0]["uuid"] == "obj_waited"


def _write_image(path: Path, *, size: tuple[int, int], color: tuple[int, int, int]) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    image = Image.new("RGB", size, color=color)
    image.save(path)
    return path
