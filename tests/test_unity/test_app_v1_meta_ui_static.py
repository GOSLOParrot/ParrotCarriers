from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
UNITY_ROOT = ROOT / "unity" / "ArSpike" / "Assets"
META_UI = UNITY_ROOT / "Scripts" / "ParrotApp" / "UI" / "AppV1MetaUiController.cs"
SMOKE_BUILDER = (
    UNITY_ROOT
    / "Scripts"
    / "ParrotApp"
    / "Editor"
    / "ParrotSmokeSceneBuilder.cs"
)
ASSET_MANIFEST = UNITY_ROOT / "UI" / "ParrotApp" / "app_v1_asset_manifest.json"


def test_meta_ui_keeps_app_v1_flow_and_existing_controller_boundaries() -> None:
    text = META_UI.read_text(encoding="utf-8")

    assert "StartupSurface" in text
    assert "StartupTransitionSurface" in text
    assert "ToolCabinet_WoodDrawer" in text
    assert "AppV1_2DWorkdesk" in text
    assert "NanobotNoteStack" in text
    assert "MagnifierFocusOverlay_Draggable" in text
    assert "BoundaryBoxOverlay_DraggableResizable" in text
    assert "MagnificationSlider" in text
    assert "DebugFireBranchGesture" in text

    assert "photoController.CapturePhoto()" in text
    assert "focusController.AnchorFocus" in text
    assert "focusController.ReleaseFocus" in text
    assert "bboxController.PlaceBBox" in text
    assert "bboxController.RemoveBBox" in text
    assert "startupFlow.ReportGosloPlaced()" in text


def test_smoke_scene_builder_mounts_meta_ui_and_wires_existing_tools() -> None:
    text = SMOKE_BUILDER.read_text(encoding="utf-8")

    assert "using ParrotApp.UI;" in text
    assert "AddComponent<AppV1MetaUiController>()" in text
    assert 'FindProperty("photoController")' in text
    assert 'FindProperty("focusController")' in text
    assert 'FindProperty("bboxController")' in text
    assert 'FindProperty("handGestureSource")' in text
    assert "LOCAL PREVIEW" in text
    assert "Magnifier creates a draggable Focus overlay" in text


def test_app_v1_curated_asset_slots_are_imported_to_unity() -> None:
    manifest = json.loads(ASSET_MANIFEST.read_text(encoding="utf-8"))
    root = ASSET_MANIFEST.parent

    assert manifest["schema_version"] == 1
    assert manifest["unity_root"] == "Assets/UI/ParrotApp"

    slots = {slot["slot"]: slot for slot in manifest["slots"]}
    assert {
        "ToolDrawerWood",
        "ToolButtonWood",
        "PaperNoteSmall",
        "PaperNoteFilled",
        "CameraIcon",
        "FocusMagnifierIcon",
        "BoundaryBoxIcon",
    } <= set(slots)

    for slot in slots.values():
        asset = root / slot["unity"]
        assert asset.exists(), slot
        meta = asset.with_suffix(asset.suffix + ".meta")
        assert meta.exists(), slot
        meta_text = meta.read_text(encoding="utf-8")
        assert "textureType: 8" in meta_text
        assert "spriteMode: 1" in meta_text
        assert "filterMode: 0" in meta_text
        assert "enableMipMap: 0" in meta_text

    assert slots["CameraIcon"]["status"] == "placeholder"
