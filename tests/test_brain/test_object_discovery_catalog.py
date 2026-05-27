from __future__ import annotations

import importlib
import json
import re
from pathlib import Path
from types import SimpleNamespace

import pytest
from PIL import Image

from parrot.brain.vision.evidence import (
    ClockDomain,
    EvidenceKind,
    SampleRegion,
    TimebaseStamp,
    get_evidence_ledger,
)
from parrot.brain.vision.object_discovery import (
    accept_new_object_from_evidence,
    list_object_samples,
    record_photo_asset,
    record_visual_tool_object_draft,
    reject_object_sample_draft,
)
from parrot.brain.vision.a10_export import export_accepted_samples_for_a10
from parrot.brain.vision.a10_import import record_a10_detections_as_sample_drafts
from parrot.brain.intent_workspace import (
    IntentWorkspace,
    StagedRefKind,
    get_intent_workspace,
    set_intent_workspace_for_test,
)
from parrot.dsg.l1_5_protocol import Detection, DetectionAuthority, FrameSource, SensorFrame
from parrot.dsg.l2b_graph import L2BGraph
from parrot.dsg.l2b_types import ConfirmationStatus, NodeKind, SemanticNode
from parrot.shared.snapshot import BBox


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
    set_intent_workspace_for_test(IntentWorkspace())
    yield
    get_evidence_ledger().reset_for_tests()
    graph_module._instance = None
    set_intent_workspace_for_test(None)


def test_photo_asset_catalog_record_is_idempotent(tmp_path: Path):
    asset_path = _write_image(tmp_path / "photo.jpg", size=(160, 100))

    result = record_photo_asset(
        photo_uuid="ph_catalog_photo",
        asset_path=str(asset_path),
        evidence_id="ev_photo_asset",
        asset_ref="/asset/ph_catalog_photo.jpg",
        asset_bytes=asset_path.stat().st_size,
        payload={"photo_id": "ph_catalog_photo"},
        captured_at_ms=1_777_000_000_000,
    )
    again = record_photo_asset(
        photo_uuid="ph_catalog_photo",
        asset_path=str(asset_path),
        evidence_id="ev_photo_asset",
        asset_ref="/asset/ph_catalog_photo.jpg",
        asset_bytes=asset_path.stat().st_size,
        payload={"photo_id": "ph_catalog_photo"},
        captured_at_ms=1_777_000_000_000,
    )

    photo = result["photo"]
    assert result["success"] is True
    assert photo["photo_uuid"] == "ph_catalog_photo"
    assert photo["evidence_id"] == "ev_photo_asset"
    assert photo["width"] == 160
    assert photo["height"] == 100
    assert len(photo["content_sha256"]) == 64
    assert again["idempotent"] is True


def test_bbox_confirm_creates_photo_object_and_sample_draft(tmp_path: Path):
    asset_path = _write_image(tmp_path / "frame.png", size=(120, 80))
    sample = get_evidence_ledger().record_sample(
        kind=EvidenceKind.IMAGE_ASSET,
        timebase=TimebaseStamp.now(clock_domain=ClockDomain.UNITY, source_id="unit"),
        asset_path=str(asset_path),
        mime_type="image/png",
        region=SampleRegion(x=0.1, y=0.2, width=0.5, height=0.4, coordinate_space="screen_normalized"),
        meta={"photo_id": "ph_catalog"},
    )
    packet = SimpleNamespace(
        tool_kind="bbox",
        interaction_phase="confirm",
        tool_event_id="evt_bbox_catalog",
        tool_id="bbox_catalog",
        attention_hint=1.0,
        source_surface="unit",
        subject_hint="red cup",
        label="BBox:red cup",
        meta={"photo_id": "ph_catalog", "sample_label": "cup"},
    )

    result = record_visual_tool_object_draft(packet=packet, sample=sample, ref_id="bbox_ref_1")
    again = record_visual_tool_object_draft(packet=packet, sample=sample, ref_id="bbox_ref_1")

    photo_object = result["photo_object"]
    sample_record = result["sample"]
    assert result["success"] is True
    assert result["intent_workspace_ref_id"]
    assert Path(result["manifest_path"]).is_file()
    assert photo_object["object_ref_id"].startswith("pobj_")
    assert photo_object["sample_draft_id"].startswith("os_")
    assert photo_object["photo_uuid"] == "ph_catalog"
    assert photo_object["review_status"] == "draft"
    assert sample_record["review_status"] == "draft"
    assert sample_record["object_uuid"] == ""
    assert Path(sample_record["crop_path"]).is_file()
    assert sample_record["bbox"]["width"] == pytest.approx(0.5)
    with Image.open(sample_record["crop_path"]) as crop:
        assert crop.size == (60, 32)
    draft_refs = get_intent_workspace().list_active(
        kinds=frozenset({StagedRefKind.RICH_REPORT}),
        role="object_sample_draft",
    )
    assert len(draft_refs) == 1
    assert draft_refs[0].metadata.custom_meta["sample_uuid"] == sample_record["sample_uuid"]
    manifest = json.loads(Path(result["manifest_path"]).read_text(encoding="utf-8"))
    assert manifest["intent_workspace_ref_id"] == result["intent_workspace_ref_id"]
    assert again["idempotent"] is True
    assert again["photo_object"]["object_ref_id"] == photo_object["object_ref_id"]


def test_reject_object_sample_draft_marks_latest_review_state(tmp_path: Path):
    asset_path = _write_image(tmp_path / "reject_frame.png", size=(90, 60))
    sample = get_evidence_ledger().record_sample(
        kind=EvidenceKind.IMAGE_ASSET,
        asset_path=str(asset_path),
        mime_type="image/png",
        region=SampleRegion(x=0.0, y=0.0, width=1.0, height=1.0),
        meta={"photo_id": "ph_reject"},
    )
    packet = SimpleNamespace(
        tool_kind="bbox",
        interaction_phase="confirm",
        tool_event_id="evt_reject_draft",
        tool_id="bbox_reject",
        attention_hint=1.0,
        source_surface="unit",
        subject_hint="bad crop",
        label="BBox:bad crop",
        meta={"photo_id": "ph_reject", "sample_label": "bad crop"},
    )
    draft = record_visual_tool_object_draft(packet=packet, sample=sample, ref_id="bbox_reject_ref")

    rejected = reject_object_sample_draft(
        object_ref_id=draft["photo_object"]["object_ref_id"],
        reason="too blurry",
        reviewer="unit_test",
    )
    again = reject_object_sample_draft(sample_uuid=draft["sample"]["sample_uuid"])

    assert rejected["success"] is True
    assert rejected["sample"]["review_status"] == "rejected"
    assert rejected["photo_object"]["review_status"] == "rejected"
    assert rejected["sample"]["object_uuid"] == ""
    assert rejected["audit"]["identity_binding"] == "rejected_draft_no_object_identity"
    assert again["idempotent"] is True
    manifest = json.loads(Path(rejected["manifest_path"]).read_text(encoding="utf-8"))
    assert manifest["review_status"] == "rejected"
    assert manifest["sample"]["meta"]["review"]["reason"] == "too blurry"
    assert len(list_object_samples(review_status="rejected")) == 1
    export = export_accepted_samples_for_a10(export_uuid="exp_reject")
    assert export["sample_count"] == 0


def test_accept_new_object_writes_sample_identity_and_photo_edge(tmp_path: Path):
    graph_module = importlib.import_module("parrot.dsg.l2b_graph")
    graph = graph_module.get_l2b_graph()
    graph.upsert_node(
        SemanticNode(
            uuid="ph_accept",
            kind=NodeKind.PHOTO,
            label="photo:ph_accept",
            confirmation=ConfirmationStatus.CONFIRMED,
        )
    )
    graph.upsert_node(
        SemanticNode(
            uuid="obj_accept",
            kind=NodeKind.OBJECT,
            label="red cup",
            confirmation=ConfirmationStatus.TENTATIVE,
        )
    )
    asset_path = _write_image(tmp_path / "object.png", size=(80, 80))
    sample = get_evidence_ledger().record_sample(
        kind=EvidenceKind.IMAGE_ASSET,
        asset_path=str(asset_path),
        mime_type="image/png",
        region=SampleRegion(x=0.0, y=0.0, width=1.0, height=1.0, coordinate_space="normalized"),
        related_refs=("ph_accept",),
        meta={"photo_id": "ph_accept"},
    )

    result = accept_new_object_from_evidence(
        object_uuid="obj_accept",
        description="red cup",
        category="cup",
        evidence_sample=sample,
        photo_uuid="ph_accept",
        match_source="user_confirmed",
        match_confidence=0.9,
    )

    accepted = result["sample"]
    assert result["success"] is True
    assert accepted["review_status"] == "accepted"
    assert accepted["object_uuid"] == "obj_accept"
    assert Path(accepted["crop_path"]).is_file()
    assert result["edge"]["edge_status"] == "confirmed"
    assert result["l2b_edge_written"] is True

    object_node = graph.get_node("obj_accept")
    assert object_node is not None
    assert object_node.reference_image_path == accepted["crop_path"]
    assert object_node.meta["object_profile"]["primary_sample_id"] == accepted["sample_uuid"]
    assert any(
        src.uuid == "ph_accept" and dst.uuid == "obj_accept"
        for src, dst, _edge in graph.all_edges()
    )
    identity_path = tmp_path / "identity_ref_index.json"
    assert identity_path.is_file()
    assert accepted["sample_uuid"] in identity_path.read_text(encoding="utf-8")
    object_report = result["object_report"]
    assert object_report["success"] is True
    assert object_report["sample_count"] == 1
    assert object_report["edge_count"] == 1
    report_path = Path(object_report["report_path"])
    report = json.loads(report_path.read_text(encoding="utf-8"))
    assert report["object_uuid"] == "obj_accept"
    assert report["accepted_samples"][0]["sample_uuid"] == accepted["sample_uuid"]
    assert report["photo_edges"][0]["photo_uuid"] == "ph_accept"
    assert report["audit"]["identity_binding"] == "report_index_only_no_identity_mutation"
    refs = get_intent_workspace().list_active(
        kinds=frozenset({StagedRefKind.RICH_REPORT}),
        role="object_analysis_report",
    )
    assert len(refs) == 1
    assert refs[0].metadata.related_node_uuid == "obj_accept"
    assert object_node.meta["object_profile"]["object_report_paths"] == [str(report_path)]
    assert object_node.meta["object_profile"]["object_report_ref_ids"] == [refs[0].ref_id]


def test_a10_export_uses_only_accepted_samples_and_preserves_uuid_mapping(tmp_path: Path):
    asset_path = _write_image(tmp_path / "export_object.png", size=(72, 48))
    sample = get_evidence_ledger().record_sample(
        kind=EvidenceKind.IMAGE_ASSET,
        asset_path=str(asset_path),
        mime_type="image/png",
        region=SampleRegion(x=0.0, y=0.0, width=1.0, height=1.0, coordinate_space="normalized"),
        related_refs=("ph_export",),
        meta={"photo_id": "ph_export"},
    )
    accepted = accept_new_object_from_evidence(
        object_uuid="obj_export",
        description="green sample box",
        category="box",
        evidence_sample=sample,
        photo_uuid="ph_export",
        match_source="user_confirmed",
        match_confidence=0.95,
    )["sample"]
    draft_asset = _write_image(tmp_path / "draft.png", size=(24, 24))
    draft_sample = get_evidence_ledger().record_sample(
        kind=EvidenceKind.IMAGE_ASSET,
        asset_path=str(draft_asset),
        mime_type="image/png",
        region=SampleRegion(x=0.0, y=0.0, width=1.0, height=1.0),
        meta={"photo_id": "ph_export"},
    )
    packet = SimpleNamespace(
        tool_kind="bbox",
        interaction_phase="confirm",
        tool_event_id="evt_export_draft",
        tool_id="bbox_export",
        attention_hint=1.0,
        source_surface="unit",
        subject_hint="draft",
        label="BBox:draft",
        meta={"photo_id": "ph_export", "sample_label": "draft"},
    )
    record_visual_tool_object_draft(packet=packet, sample=draft_sample, ref_id="bbox_export_ref")

    result = export_accepted_samples_for_a10(export_uuid="exp_unit", subset="train")

    assert result["success"] is True
    assert result["sample_count"] == 1
    manifest = json.loads(Path(result["manifest_path"]).read_text(encoding="utf-8"))
    assert manifest["audit"]["accepted_samples_only"] is True
    assert manifest["records"][0]["sample_uuid"] == accepted["sample_uuid"]
    assert manifest["records"][0]["object_uuid"] == "obj_export"
    assert Path(manifest["records"][0]["export_image_path"]).is_file()
    assert Path(manifest["records"][0]["export_label_path"]).read_text(encoding="utf-8").strip() == (
        "0 0.500000 0.500000 1.000000 1.000000"
    )
    coco = json.loads(Path(result["coco_annotations_path"]).read_text(encoding="utf-8"))
    assert coco["images"][0]["parrot_sample_uuid"] == accepted["sample_uuid"]
    assert coco["annotations"][0]["attributes"]["object_uuid"] == "obj_export"
    assert coco["annotations"][0]["bbox"] == [0, 0, 72, 48]
    names = Path(result["yolo_names_path"]).read_text(encoding="utf-8").splitlines()
    assert names == ["box"]


def test_a10_detection_import_creates_reviewable_sample_drafts(tmp_path: Path):
    frame_asset = _write_image(tmp_path / "a10_frame.jpg", size=(100, 80))
    frame = SensorFrame(
        frame_uuid="frame_a10",
        source=FrameSource.A10_YOLO_WORLD,
        frame_ref=str(frame_asset),
        meta={"photo_id": "ph_a10"},
        detections=(
            Detection(
                det_id="det_cup",
                label="cup",
                confidence=0.77,
                authority=DetectionAuthority.YOLO_SINGLE,
                bbox=BBox(x1=0.1, y1=0.2, x2=0.6, y2=0.7),
                track_id="trk_1",
                meta={"category": "cup", "clip_score": 0.55},
            ),
            Detection(
                det_id="det_no_bbox",
                label="box",
                confidence=0.5,
                authority=DetectionAuthority.YOLO_SINGLE,
            ),
        ),
    )

    result = record_a10_detections_as_sample_drafts(frame)

    assert result["success"] is True
    assert result["draft_count"] == 1
    assert result["skipped"] == [{"det_id": "det_no_bbox", "reason": "missing_bbox"}]
    draft = result["drafts"][0]
    assert draft["photo_object"]["photo_uuid"] == "ph_a10"
    assert draft["photo_object"]["source"] == "a10_detection"
    assert draft["photo_object"]["tool_event_id"] == "a10:frame_a10:det_cup"
    assert draft["sample"]["created_by"] == "a10_detection"
    assert draft["intent_workspace_ref_id"]
    assert Path(draft["manifest_path"]).is_file()
    assert draft["sample"]["review_status"] == "draft"
    assert draft["sample"]["object_uuid"] == ""
    assert draft["sample"]["bbox"]["width"] == pytest.approx(0.5)
    assert Path(draft["sample"]["crop_path"]).is_file()
    with Image.open(draft["sample"]["crop_path"]) as crop:
        assert crop.size == (50, 40)
    refs = get_intent_workspace().list_active(
        kinds=frozenset({StagedRefKind.RICH_REPORT}),
        role="object_sample_draft",
    )
    assert len(refs) == 1
    assert refs[0].metadata.custom_meta["source"] == "a10_detection"
    assert result["audit"]["identity_binding"] == "draft_only_no_object_identity"


@pytest.mark.asyncio
async def test_identify_object_save_new_accepts_current_evidence(tmp_path: Path):
    id_module = importlib.import_module("parrot.brain.tools.identify_object")
    graph_module = importlib.import_module("parrot.dsg.l2b_graph")
    graph = graph_module.get_l2b_graph()
    graph.upsert_node(
        SemanticNode(
            uuid="ph_save",
            kind=NodeKind.PHOTO,
            label="photo:ph_save",
            confirmation=ConfirmationStatus.CONFIRMED,
        )
    )
    asset_path = _write_image(tmp_path / "save_new.png", size=(96, 96))
    sample = get_evidence_ledger().record_sample(
        kind=EvidenceKind.IMAGE_ASSET,
        asset_path=str(asset_path),
        mime_type="image/png",
        region=SampleRegion(x=0.0, y=0.0, width=1.0, height=1.0),
        related_refs=("ph_save",),
        meta={"photo_id": "ph_save"},
    )

    out = await id_module._save_new_object(
        "red cup with white logo",
        "cup",
        evidence_id=sample.evidence_id,
        photo_id="ph_save",
    )

    assert "Saved new object" in out
    assert "ObjectSample=os_" in out
    obj_id = re.search(r"id: (obj_[0-9a-f]+)", out).group(1)
    object_node = graph.get_node(obj_id)
    assert object_node is not None
    assert object_node.reference_image_path
    assert Path(object_node.reference_image_path).is_file()
    assert any(src.uuid == "ph_save" and dst.uuid == obj_id for src, dst, _edge in graph.all_edges())


def _write_image(path: Path, *, size: tuple[int, int]) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    image = Image.new("RGB", size, color=(220, 40, 30))
    image.save(path)
    return path
