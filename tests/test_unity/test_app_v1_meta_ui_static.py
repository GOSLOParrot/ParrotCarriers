from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
UNITY_ROOT = ROOT / "unity" / "ArSpike" / "Assets"
META_UI = UNITY_ROOT / "Scripts" / "ParrotApp" / "UI" / "AppV1MetaUiController.cs"
PARROT_CONTROLLER = (
    UNITY_ROOT / "Scripts" / "ParrotApp" / "Parrot" / "ParrotController.cs"
)
ANIMATION_DRIVER = (
    UNITY_ROOT / "Scripts" / "ParrotApp" / "Parrot" / "AnimationDriver.cs"
)
TOKEN_MINT_CLIENT = (
    UNITY_ROOT / "Scripts" / "ParrotApp" / "LiveKit" / "LiveKitTokenMintClient.cs"
)
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
    assert "AppV1SettingsDialoguePanel" in text
    assert "SettingsDialogueStatus" in text
    assert "CameraModeOverlay_TransparentWysiwyg" in text
    assert "CameraModeTinyTopEdge" in text
    assert "CameraGestureRail_Zoom" in text
    assert "CameraExposureRail" in text
    assert "CameraProSettingsPanel" in text
    assert "CameraToolbox_PixelBBoxStamp" in text
    assert "CameraModeShutterButton" in text
    assert "AppV1_2DWorkdesk" in text
    assert "NanobotNoteStack" in text
    assert "NekoClawReportPaw" in text
    assert "nekoClawSprite" in text
    assert "PaperNote_DraggableSelectable" in text
    assert "PaperNoteDropTargets_RightRail" in text
    assert "PaperDropTarget_Trash" in text
    assert "PaperDropTarget_Workdesk" in text
    assert "TrashCrumpledPaperPlaceholder" in text
    assert "MovePaperNoteToTrash" in text
    assert "MovePaperNoteToWorkdesk" in text
    assert "ParrotJoystick_PlaneWalkPad" in text
    assert "parrotController.WalkOnPlane" in text
    assert 'Resources.GetBuiltinResource<Font>("LegacyRuntime.ttf")' in text
    assert "Arial.ttf" not in text
    assert "MagnifierFocusOverlay_Draggable" in text
    assert "BoundaryBoxOverlay_DraggableResizable" in text
    assert "MagnificationSlider" in text
    assert "DebugFireBranchGesture" in text

    assert "photoController.CapturePhoto()" in text
    assert "AppCapabilityModeNames.SessionOnlySilent" in text
    assert "ReportSceneReadyFromSettings" in text
    assert "ToggleAwarenessMode" in text
    assert "SceneReady does not greet" in text
    assert "ready_after_placement" in text
    assert 'SetCameraOverlayMode("preview")' in text
    assert 'SetCameraOverlayMode("capture_locked")' in text
    assert "ToggleCameraProSettings" in text
    assert "SetCameraZoom" in text
    assert "SetCameraExposure" in text
    assert "Camera mode is deliberately WYSIWYG" in text
    assert "CameraPreviewFrame" not in text
    assert "focusController.AnchorFocus" in text
    assert "focusController.ReleaseFocus" in text
    assert "bboxController.PlaceBBox" in text
    assert "bboxController.RemoveBBox" in text
    assert "startupFlow.ReportGosloPlaced()" in text


def test_smoke_scene_builder_mounts_meta_ui_and_wires_existing_tools() -> None:
    text = SMOKE_BUILDER.read_text(encoding="utf-8")

    assert "using ParrotApp.UI;" in text
    assert "AddComponent<AppV1MetaUiController>()" in text
    assert "AddComponent<AppStartupFlowController>()" in text
    assert "AddComponent<LiveKitTokenMintClient>()" in text
    assert "ConfigureRoomManagerForMint" in text
    assert 'SetBool(roomManager, "autoConnectOnStart", false)' in text
    assert 'SetBool(roomManager, "allowEditorTokenFile", false)' in text
    assert "Upgrade Current A2 Smoke Scene" in text
    assert "UpgradeCurrentSmokeScene" in text
    assert "FindOrCreateRoot(\"AppV1MetaUI\")" in text
    assert 'FindProperty("startupFlow")' in text
    assert 'FindProperty("photoController")' in text
    assert 'FindProperty("parrotController")' in text
    assert 'FindProperty("focusController")' in text
    assert 'FindProperty("bboxController")' in text
    assert 'FindProperty("handGestureSource")' in text
    assert 'FindProperty("nekoClawSprite")' in text
    assert "NekoClaw_Cutout.png" in text
    assert "LOCAL PREVIEW" in text
    assert "Magnifier creates a draggable Focus overlay" in text
    assert "Bottom-left joystick walks the parrot on the plane" in text


def test_parrot_joystick_uses_existing_parrot_controller_boundary() -> None:
    controller = PARROT_CONTROLLER.read_text(encoding="utf-8")
    animation = ANIMATION_DRIVER.read_text(encoding="utf-8")

    assert "public void WalkOnPlane(Vector2 input, float deltaTime)" in controller
    assert "public void EndPlaneWalk()" in controller
    assert "public void ReturnToPlaneWalkHome()" in controller
    assert "does not create a Brain" in controller
    assert "BodyState.Walk" in controller

    assert "WalkOnPlane(Vector2 input" in animation
    assert "UpdateWalk()" in animation
    assert "case BodyState.Walk" in animation
    assert 'case "walking"' in animation
    assert 'return "walking"' in animation


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
        "NanobotReportPaper",
        "CalendarReminderPaper",
        "TrashCrumpledPaper",
        "OrangeCatPaw",
        "ParrotJoystick",
        "CameraIcon",
        "FocusMagnifierIcon",
        "BoundaryBoxIcon",
    } <= set(slots)

    for slot in slots.values():
        if not slot["unity"].endswith(".png"):
            assert slot["status"] in {"runtime_placeholder", "slot_only"}
            assert slot["fallback"]
            continue
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


def test_arspike_mint_client_uses_gitignored_runtime_config_without_logging_secret() -> None:
    text = TOKEN_MINT_CLIENT.read_text(encoding="utf-8")
    example = UNITY_ROOT / "Resources" / "parrot_config.json.example"

    assert 'Resources.Load<TextAsset>("parrot_config")' in text
    assert "mintUrl" in text
    assert "mintSecret" in text
    assert "SetRequestHeader(\"Authorization\"" in text
    assert "loaded parrot_config" in text
    debug_lines = [line for line in text.splitlines() if "Debug." in line]
    assert all("bearerSecret" not in line for line in debug_lines)
    assert all("mintSecret" not in line for line in debug_lines)

    assert example.exists()
    config = json.loads(example.read_text(encoding="utf-8"))
    assert config["mintUrl"].endswith(":7888/mint")
    assert config["mintSecret"] == "same-as-PARROT_MINT_SECRET-on-castle"
    assert config["room"] == "parrot-main"
