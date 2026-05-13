from __future__ import annotations

import json
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
UNITY_ROOT = ROOT / "unity" / "ArSpike" / "Assets"
BUILD_SETTINGS = ROOT / "unity" / "ArSpike" / "ProjectSettings" / "EditorBuildSettings.asset"
PROJECT_SETTINGS = ROOT / "unity" / "ArSpike" / "ProjectSettings" / "ProjectSettings.asset"
PROJECT_VERSION = ROOT / "unity" / "ArSpike" / "ProjectSettings" / "ProjectVersion.txt"
PACKAGE_MANIFEST = ROOT / "unity" / "ArSpike" / "Packages" / "manifest.json"
PARROT_APP = UNITY_ROOT / "ParrotApp"
FORMAL_STARTUP_SCENE = PARROT_APP / "Scenes" / "ParrotApp_Startup.unity"
SCRIPT_ROOT = PARROT_APP / "Runtime" / "Scripts"
META_UI = SCRIPT_ROOT / "UI" / "AppV1MetaUiController.cs"
STARTUP_CONFIG = (
    SCRIPT_ROOT / "Config" / "AppStartupConfigDto.cs"
)
STARTUP_FLOW = (
    SCRIPT_ROOT / "Lifecycle" / "AppStartupFlowController.cs"
)
SHUTDOWN_SERVICE = (
    SCRIPT_ROOT / "Lifecycle" / "LifecycleShutdownService.cs"
)
FORMAL_STARTUP_UI = (
    SCRIPT_ROOT / "Startup" / "ParrotAppStartupUiController.cs"
)
ROOM_SETTING_CLIENT = (
    SCRIPT_ROOT / "Backend" / "AppRoomSettingClient.cs"
)
ORCHESTRATOR_CLIENT = (
    SCRIPT_ROOT / "Backend" / "OrchestratorClient.cs"
)
RUNTIME_CONFIG = (
    SCRIPT_ROOT / "Backend" / "ParrotRuntimeConfig.cs"
)
ROOM_SETTING_DTOS = (
    SCRIPT_ROOT / "Backend" / "RoomSettingDtos.cs"
)
PARROT_CONTROLLER = (
    SCRIPT_ROOT / "Parrot" / "ParrotController.cs"
)
ANIMATION_DRIVER = (
    SCRIPT_ROOT / "Parrot" / "AnimationDriver.cs"
)
MODEL_DRIVER = (
    SCRIPT_ROOT / "Parrot" / "ModelDriver.cs"
)
NER_SPINE_CONTROLLER = (
    SCRIPT_ROOT / "Parrot" / "NerSpineController.cs"
)
NER_CHEEK_PINCH_INTERACTOR = (
    SCRIPT_ROOT / "Parrot" / "NerCheekPinchInteractor.cs"
)
NER_PICKUP_PLACE_INTERACTOR = (
    SCRIPT_ROOT / "Parrot" / "NerPickupPlaceInteractor.cs"
)
NER_CHEEK_HIT_REGION = (
    SCRIPT_ROOT / "Parrot" / "NerCheekHitRegion.cs"
)
NER_SPINE_AUDIT = (
    PARROT_APP / "Editor" / "NerSpineAnimationAudit.cs"
)
TOKEN_MINT_CLIENT = (
    SCRIPT_ROOT / "LiveKit" / "LiveKitTokenMintClient.cs"
)
SMOKE_BUILDER = (
    UNITY_ROOT
    / "Tests"
    / "Smoke"
    / "Editor"
    / "ParrotSmokeSceneBuilder.cs"
)
ASSET_MANIFEST = PARROT_APP / "Art" / "AppV1" / "app_v1_asset_manifest.json"
STARTUP_PAPER_RESOURCES = PARROT_APP / "Art" / "Startup" / "Resources" / "StartupPaperCraft"
NER_MODEL_MANIFEST = PARROT_APP / "Resources" / "parrot_models" / "ner_skin2.json"


def _unity_guid(asset: Path) -> str:
    meta = asset.with_suffix(asset.suffix + ".meta")
    match = re.search(r"^guid:\s*([0-9a-f]+)$", meta.read_text(encoding="utf-8"), re.M)
    assert match, meta
    return match.group(1)


def test_meta_ui_keeps_app_v1_flow_and_existing_controller_boundaries() -> None:
    text = META_UI.read_text(encoding="utf-8")

    assert "StartupSurface" in text
    assert "StartupTitleBoard_GosloParrot" in text
    assert "StartupScenePanel_RoomSettingEntry" in text
    assert "RoomSettingPanel_StartupProfileEditor" in text
    assert "StartupModeLever" in text
    assert "StartupModelSlot_SelectedModel" in text
    assert "BuildSelectedStartupConfig" in text
    assert "SelectNerLineBRoomProfile" in text
    assert "ner_lineb_room" in text
    assert "lineb_ner_ja_test" in text
    assert "startupFlow.StartFromConfig(config)" in text
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


def test_unity_ar_foundation_and_livekit_version_locks_are_pinned() -> None:
    project_version = PROJECT_VERSION.read_text(encoding="utf-8")
    manifest = json.loads(PACKAGE_MANIFEST.read_text(encoding="utf-8"))
    deps = manifest["dependencies"]

    assert "m_EditorVersion: 2022.3.62f3" in project_version
    assert deps["com.unity.xr.arfoundation"] == "5.2.2"
    assert deps["com.unity.xr.arcore"] == "5.2.2"
    assert deps["com.unity.xr.arkit"] == "5.2.2"
    assert deps["io.livekit.livekit-sdk"].endswith(
        "#7d868ef5cc5615c30a3ef4b73ae0dbb5cc4d6796"
    )


def test_startup_room_setting_selection_syncs_to_brain_before_capability() -> None:
    config = STARTUP_CONFIG.read_text(encoding="utf-8")
    flow = STARTUP_FLOW.read_text(encoding="utf-8")

    for field in [
        "room_profile_id",
        "line_id",
        "line_profile_id",
        "experience_mode",
        "skin_id",
        "setting_file_refs",
        "app_api_url",
        "orchestrator_url",
        "orchestrator_secret",
        "compatibility_state",
        "compatibility_summary",
    ]:
        assert f"public string {field}" in config or f"public string[] {field}" in config
    assert "public int setting_change_tier" in config
    assert "public bool requires_livekit_reconnect" in config

    assert "SyncStartupRoomProfile" in flow
    assert '"applyRoomProfile"' in flow
    assert "BuildRoomProfilePayload" in flow
    assert "startup_room_profile" in flow
    assert "startup_reuse_room_profile" in flow
    assert "brain_rpc_room_profile_sync_timeout" in flow
    assert '\\"room_profile_id\\"' in flow
    assert '\\"line_profile_id\\"' in flow
    assert '\\"experience_mode\\"' in flow
    assert '\\"skin_id\\"' in flow
    assert flow.index('"startup_reuse_room_profile"') < flow.index('"startup_reuse_capability_mode"')
    assert flow.index('"startup_room_profile"') < flow.index('"startup_capability_mode"')


def test_formal_startup_playmode_uses_experience_mode_not_preview_switch() -> None:
    text = FORMAL_STARTUP_UI.read_text(encoding="utf-8")

    assert "StartupExperienceModes" in text
    assert '"ar_companion"' in text
    assert '"2d_hall"' in text
    assert '"room_only"' in text
    assert "button.onClick.AddListener(CycleExperienceMode)" in text
    assert 'if (_config.experience_mode == "ar_companion" && _config.scene_id != "ar_handheld")' in text
    assert '_config.scene_id = "ar_handheld";' in text
    assert "ExperienceModeSelectors()" in text
    assert "AddModeLever(controls, new Vector2(300f, 0f)" in text
    assert "StartLocalPreview" not in text


def test_formal_startup_scene_is_first_enabled_build_scene() -> None:
    text = BUILD_SETTINGS.read_text(encoding="utf-8")

    formal = "path: Assets/ParrotApp/Scenes/ParrotApp_Startup.unity"
    assert formal in text
    assert "- enabled: 1\n    " + formal in text
    assert "Assets/Scenes/SampleScene.unity" not in text


def test_formal_startup_scene_explicitly_mounts_runtime_services() -> None:
    text = FORMAL_STARTUP_SCENE.read_text(encoding="utf-8")

    assert f"guid: {_unity_guid(META_UI)}" not in text

    for script in [
        ROOM_SETTING_CLIENT,
        ORCHESTRATOR_CLIENT,
        SCRIPT_ROOT / "Ecp" / "LifecycleHeartbeatPublisher.cs",
        SCRIPT_ROOT / "LiveKit" / "AudioRouteDetector.cs",
        SCRIPT_ROOT / "LiveKit" / "MicrophonePublisher.cs",
        SCRIPT_ROOT / "LiveKit" / "ARVideoPublisher.cs",
        SCRIPT_ROOT / "LiveKit" / "VideoStateReporter.cs",
        SCRIPT_ROOT / "LiveKit" / "VideoTierReceiver.cs",
    ]:
        assert f"guid: {_unity_guid(script)}" in text, script

    for field in [
        "roomSettingClient",
        "microphonePublisher",
        "videoPublisher",
        "orchestratorClient",
        "heartbeatPublisher",
    ]:
        assert f"{field}: {{fileID: 0}}" not in text


def test_project_settings_default_scene_is_formal_startup_scene() -> None:
    text = PROJECT_SETTINGS.read_text(encoding="utf-8")

    assert "templateDefaultScene: Assets/ParrotApp/Scenes/ParrotApp_Startup.unity" in text
    assert "templateDefaultScene: Assets/Scenes/SampleScene.unity" not in text


def test_formal_startup_roomsetting_cold_load_uses_app_http_facade() -> None:
    ui = FORMAL_STARTUP_UI.read_text(encoding="utf-8")
    client = ROOM_SETTING_CLIENT.read_text(encoding="utf-8")
    dtos = ROOM_SETTING_DTOS.read_text(encoding="utf-8")
    runtime = RUNTIME_CONFIG.read_text(encoding="utf-8")

    assert "AppRoomSettingClient roomSettingClient" in ui
    assert "LoadRoomSettingSnapshotIfNeeded()" in ui
    assert "roomSettingClient.LoadSnapshot" in ui
    assert "roomSettingClient.Preview" in ui
    assert "roomSettingClient.NewRoomProfile" in ui
    assert "roomSettingClient.SaveRoomProfile" in ui
    assert "ApplyCompatibility" in ui
    assert "DefaultLineProfileFor" in ui
    assert "SceneId(SceneSelectorDto" in ui
    assert "ToggleTheme" in ui
    assert "DisplayThemeValue" in ui
    assert "startupFlow?.CancelStartup" in ui

    assert "class AppRoomSettingClient" in client
    assert '"/api/app/room-setting"' in client
    assert '"/api/app/room-setting/preview"' in client
    assert '"/api/app/room-setting/new"' in client
    assert '"/api/app/room-setting/save"' in client
    assert '"/api/app/room-setting/apply"' in client
    assert "NewRoomProfileResponseDto" in dtos
    assert "SkinSelectorDto" in dtos
    assert "public SkinSelectorDto[] skins" in dtos
    assert "ApplyRoomProfileResponseDto" in dtos
    assert "appApiUrl" in runtime


def test_formal_startup_layout_targets_landscape_phone_and_theme_selector() -> None:
    text = FORMAL_STARTUP_UI.read_text(encoding="utf-8")

    assert "private const float ReferenceWidth = 2800f" in text
    assert "private const float ReferenceHeight = 1260f" in text
    assert "iQOO Neo9 landscape target" in text
    assert "StartupSelectionSummary" in text
    assert "new Vector2(2140f, 900f)" in text
    assert 'Tr("套装", "Theme")' in text
    assert "ToggleTheme" in text
    assert 'Tr("Scene", "Scene")' not in text
    assert 'Tr("AR 就绪", "AR READY")' in text
    assert 'Tr("新建", "NEW")' in text
    assert 'Tr("保存", "SAVE")' in text


def test_startup_livekit_tier1_rpc_business_failure_and_heartbeat_contract() -> None:
    flow = STARTUP_FLOW.read_text(encoding="utf-8")
    orch = ORCHESTRATOR_CLIENT.read_text(encoding="utf-8")
    shutdown = SHUTDOWN_SERVICE.read_text(encoding="utf-8")
    video = (SCRIPT_ROOT / "LiveKit" / "ARVideoPublisher.cs").read_text(encoding="utf-8")
    mic = (SCRIPT_ROOT / "LiveKit" / "MicrophonePublisher.cs").read_text(encoding="utf-8")

    assert "OrchestratorClient orchestratorClient" in flow
    assert "PrepareTierOneRuntimeConfig" in flow
    assert "RequiresTierOneStartup" in flow
    assert "orchestrator_required_for_tier1_startup" in flow
    assert "tier1_setting_requires_fresh_livekit_reconnect" in flow
    assert "orchestrator_apply_room_profile_failed" in flow
    assert "rpcCall.Payload" in flow
    assert "IsRpcBusinessOk" in flow
    assert "RpcStatusEnvelope" in flow
    assert "ApplyRoomProfileRpcResponse" in flow
    assert "!response.result.success" in flow
    assert "LiveKitDataChannelHeartbeatTransport" in flow
    assert "heartbeatPublisher.Transport" in flow

    assert '"/apply_room_profile"' in orch
    assert '"/set_active_line"' in orch
    assert '"/force_unity_reconnect"' in orch

    assert "s_syncDrainDepth" in shutdown
    assert "DrainDeltaSeconds()" in shutdown
    assert "waited += DrainDeltaSeconds()" in shutdown
    assert "cd += DrainDeltaSeconds()" in shutdown
    assert "IsSynchronousQuitDrain" in video
    assert "IsSynchronousQuitDrain" in mic
    assert "sync quit drain skips waiting for UnpublishTrack" in video
    assert "sync quit drain skips waiting for UnpublishTrack" in mic


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


def test_custom_capability_parameters_reach_model_controller() -> None:
    controller = PARROT_CONTROLLER.read_text(encoding="utf-8")
    rpc = (SCRIPT_ROOT / "RPC" / "ParrotRpcHandler.cs").read_text(encoding="utf-8")

    assert "public void PlayAnimation(string animationName, string modelId, string parametersJson)" in controller
    assert "public bool TryPlayAnimation(string animationName, string modelId, string parametersJson, bool strictCapability)" in controller
    assert "controller.ApplyCapability(animationName, parametersJson ?? \"\")" in controller
    assert "public string parameters_json" in rpc
    assert "public bool strict_capability" in rpc
    assert "_parrot.TryPlayAnimation(p.animation, modelId, p.parameters_json, p.strict_capability)" in rpc
    assert "capability_unsupported" in controller
    assert "capability_unsupported" in rpc


def test_model_driver_configures_manifest_back_into_controllers() -> None:
    driver = MODEL_DRIVER.read_text(encoding="utf-8")

    assert "ConfigureControllerFromManifest();" in driver
    assert '"ConfigureFromManifest"' in driver
    assert "typeof(ModelManifestDto)" in driver
    assert "method.Invoke" in driver


def test_ner_spine_model_manifest_and_controller_probe_are_registered() -> None:
    manifest = json.loads(NER_MODEL_MANIFEST.read_text(encoding="utf-8"))
    controller = NER_SPINE_CONTROLLER.read_text(encoding="utf-8")

    assert manifest["model_id"] == "ner_skin2"
    assert manifest["controller_type"] == "ParrotApp.Parrot.NerSpineController"
    capability_ids = {c["capability_id"] for c in manifest["capabilities"]}
    assert {
        "spine_idle",
        "spine_walk",
        "face_happy",
        "face_angry",
        "face_sad",
        "face_serious",
        "face_sulky",
        "face_tired",
        "cheek_pinch_start",
        "cheek_pinch_hold",
        "cheek_pinch_release",
        "body_pickup_start",
        "body_held_in_air",
        "body_dragging_in_air",
        "body_place_release",
        "touch_idle",
        "pat_idle",
        "tickle_idle",
        "lineb_speaking",
        "lineb_listening",
        "lineb_echo_suppressed",
    } <= capability_ids
    assert "fly" not in capability_ids
    assert "perch" not in capability_ids

    assert "class NerSpineController" in controller
    assert "IParrotController" in controller
    assert "ConfigureFromManifest(ModelManifestDto manifest)" in controller
    assert '"Spine.Unity.SkeletonAnimation"' in controller
    assert '"spine_walk"' in controller
    assert "ResolveAnimationName" in controller
    assert "public int variant" in controller
    assert "TryPlayIdleFallback" in controller
    assert "ApplyCheekCapability" in controller
    assert "ApplyBodyInteractionCapability" in controller
    assert "ApplyLineBVoiceActivity" in controller
    assert "_reactiveTouchSuppressedUntil" in controller
    assert "IsReactiveTouchSuppressed" in controller
    assert '"body_pickup_start"' in controller
    assert '"body_place_release"' in controller
    assert "BodyInteractionJson" in controller
    assert '"lineb_speaking"' in controller
    assert '"lineb_echo_suppressed"' in controller
    assert '"S1_F_Ball_L_CT"' in controller
    assert '"S1_F_Ball_R_CT"' in controller
    assert '"Character_Ball_Move"' in controller


def test_ner_manifest_handlers_match_editor_verified_spine_names() -> None:
    manifest = json.loads(NER_MODEL_MANIFEST.read_text(encoding="utf-8"))
    audit = NER_SPINE_AUDIT.read_text(encoding="utf-8")

    known = {
        "Angry_1", "Angry_2", "Angry_3", "Angry_4", "Angry_5", "Angry_6", "Angry_7", "Angry_8",
        "Blank_1", "Blank_2", "Close_1", "Eat_1", "Eat_2",
        "Happy_1", "Happy_2", "Happy_3", "Happy_4", "Happy_5", "Happy_6",
        "Idle_1", "Notmyfault_1", "Panic_1", "Panic_2", "Panic_3",
        "Pat_End", "Pat_Idle", "Proud_1",
        "Sad_1", "Sad_2", "Sad_3", "Sad_4", "Sad_5", "Sad_6", "Sad_7", "Sad_8",
        "Serious_1", "Serious_2", "Serious_3", "Serious_4",
        "Shame_1", "Shame_2", "Smash_End_1", "Smash_End_2",
        "Sulky_1", "Sulky_2", "Sulky_3", "Surprise_1", "Think_1",
        "Tickle_End", "Tickle_Idle_1", "Tickle_Idle_2",
        "Tired_1", "Tired_2", "Tired_3", "Tired_4", "Tired_5",
        "Touch_End", "Touch_Idle", "Worry_1", "Worry_2",
    }
    handlers = {c["handler"] for c in manifest["capabilities"] if c.get("handler")}
    variants = {
        v
        for c in manifest["capabilities"]
        for v in c.get("parameters", {}).get("variants", [])
    }

    assert manifest["author_meta"]["animation_count"] == "60"
    assert handlers <= known
    assert variants <= known
    assert "ValidateManifestHandlers" in audit
    assert "GetSkeletonData" in audit


def test_ner_cheek_pinch_interactor_is_ar_camera_raycast_based() -> None:
    interactor = NER_CHEEK_PINCH_INTERACTOR.read_text(encoding="utf-8")
    hit_region = NER_CHEEK_HIT_REGION.read_text(encoding="utf-8")

    assert "class NerCheekPinchInteractor" in interactor
    assert "Camera.main" in interactor
    assert "ScreenPointToRay" in interactor
    assert "Physics.RaycastAll" in interactor
    assert "QueryTriggerInteraction.Collide" in interactor
    assert "Input.touchCount" in interactor
    assert "Input.GetTouch" in interactor
    assert "activeTouchSeen" in interactor
    assert "void OnDisable()" in interactor
    assert "cheek_recover" in interactor
    assert "cheek_pinch_start" in interactor
    assert "cheek_pinch_hold" in interactor
    assert "cheek_pinch_warning" in interactor
    assert "cheek_pinch_release" in interactor
    assert "EventSystem.current.IsPointerOverGameObject" in interactor
    assert "class NerCheekHitRegion" in hit_region
    assert "NormalizeCheekSide" in NER_SPINE_CONTROLLER.read_text(encoding="utf-8")


def test_ner_pickup_place_interactor_is_long_press_ar_placement_based() -> None:
    interactor = NER_PICKUP_PLACE_INTERACTOR.read_text(encoding="utf-8")

    assert "class NerPickupPlaceInteractor" in interactor
    assert "longPressSeconds" in interactor
    assert "cancelBeforeHoldPixels" in interactor
    assert "autoCreateBodyCollider" in interactor
    assert "BoxCollider" in interactor
    assert "NerBodyPickupHit" in interactor
    assert "Physics.RaycastAll" in interactor
    assert "QueryTriggerInteraction.Collide" in interactor
    assert "QueryTriggerInteraction.Ignore" in interactor
    assert "new Plane(Vector3.up" in interactor
    assert "targetRoot.position = LiftedGroundPoint(groundPoint)" in interactor
    assert "targetRoot.position = groundPoint" in interactor
    assert "DropToLastGroundPoint" in interactor
    assert "IsOwnModelCollider" in interactor
    assert "_lastScreenPosition = screenPosition" in interactor
    assert "UpdatePickupLiftFromPointer" in interactor
    assert "heightDragPixelsForFullRange" in interactor
    assert "LiftedGroundPoint" in interactor
    assert "body_held_in_air" in interactor
    assert "body_place_release" in interactor
    assert "body_place_cancel" in interactor
    assert "EventSystem.current.IsPointerOverGameObject" in interactor
    assert "NerCheekHitRegion" in interactor


def test_app_v1_curated_asset_slots_are_imported_to_unity() -> None:
    manifest = json.loads(ASSET_MANIFEST.read_text(encoding="utf-8"))
    root = ASSET_MANIFEST.parent

    assert manifest["schema_version"] == 1
    assert manifest["unity_root"] == "Assets/ParrotApp/Art/AppV1"

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
    example = PARROT_APP / "Resources" / "parrot_config.json.example"

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
    assert config["appApiUrl"].endswith(":8790")
    assert config["orchestratorUrl"].endswith(":7890")
    assert config["orchestratorSecret"] == "dev-only-same-as-PARROT_ORCH_SECRET"


def test_unity_project_has_no_legacy_duplicate_app_roots() -> None:
    forbidden = [
        UNITY_ROOT / "Scripts" / "ParrotApp",
        UNITY_ROOT / "Scripts",
        UNITY_ROOT / "UI" / "ParrotApp",
        UNITY_ROOT / "UI",
        UNITY_ROOT / "Models",
        UNITY_ROOT / "NerTuningTest",
        UNITY_ROOT / "Samples",
        UNITY_ROOT / "MobileARTemplateAssets",
        UNITY_ROOT / "Scenes" / "SampleScene.unity",
        UNITY_ROOT / "TextMesh Pro",
    ]

    for path in forbidden:
        assert not path.exists(), f"legacy Unity path should be removed: {path}"

    assert SCRIPT_ROOT.is_dir()
    assert (PARROT_APP / "Resources" / "parrot_models").is_dir()
    assert (PARROT_APP / "Art" / "AppV1").is_dir()
    assert (PARROT_APP / "Models").is_dir()


def test_startup_resources_only_contains_runtime_loaded_paper_sprites() -> None:
    text = FORMAL_STARTUP_UI.read_text(encoding="utf-8")
    loaded = set(re.findall(r'LoadSprite\("([^"]+)"\)', text))
    pngs = {path.stem for path in STARTUP_PAPER_RESOURCES.glob("*.png")}

    assert pngs == loaded
    for path in STARTUP_PAPER_RESOURCES.glob("*.png"):
        assert path.with_suffix(path.suffix + ".meta").exists()


def test_top_level_resources_only_contains_livekit_sdk_generated_version_file() -> None:
    resources = UNITY_ROOT / "Resources"

    assert not (resources / "parrot_config.json").exists()
    assert not (resources / "parrot_config.json.example").exists()
    assert not (resources / "parrot_models").exists()
    if resources.exists():
        allowed = {"LiveKitSdkVersionInfo.txt", "LiveKitSdkVersionInfo.txt.meta"}
        assert {child.name for child in resources.iterdir()} <= allowed
