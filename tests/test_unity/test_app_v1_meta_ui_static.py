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
CSC_RSP = ROOT / "unity" / "ArSpike" / "Assets" / "csc.rsp"
XR_GENERAL_SETTINGS = ROOT / "unity" / "ArSpike" / "Assets" / "XR" / "XRGeneralSettings.asset"
PARROT_APP = UNITY_ROOT / "ParrotApp"
RUNTIME_MODELS = PARROT_APP / "Resources" / "Models"
NER_SKIN2_TEXTURE_META = RUNTIME_MODELS / "Ner" / "NerSkin2.png.meta"
FORMAL_STARTUP_SCENE = PARROT_APP / "Scenes" / "ParrotApp_Startup.unity"
SCRIPT_ROOT = PARROT_APP / "Runtime" / "Scripts"
SMOKE_REFERENCE_UI = UNITY_ROOT / "Tests" / "Smoke" / "Scripts" / "AppV1SmokeReferenceUiController.cs"
SMOKE_LIFECYCLE_FORCER = UNITY_ROOT / "Tests" / "Smoke" / "Scripts" / "LifecycleSmokeForcer.cs"
STARTUP_CONFIG = (
    SCRIPT_ROOT / "Config" / "AppStartupConfigDto.cs"
)
STARTUP_FLOW = (
    SCRIPT_ROOT / "Lifecycle" / "AppStartupFlowController.cs"
)
FORMAL_MAIN_READY_GATE = (
    SCRIPT_ROOT / "Lifecycle" / "FormalMainReadyGate.cs"
)
APP_LIFECYCLE_MANAGER = (
    SCRIPT_ROOT / "Lifecycle" / "AppLifecycleManager.cs"
)
ANDROID_RUNTIME_PERMISSIONS = (
    SCRIPT_ROOT / "Core" / "AndroidRuntimePermissions.cs"
)
SHUTDOWN_SERVICE = (
    SCRIPT_ROOT / "Lifecycle" / "LifecycleShutdownService.cs"
)
FORMAL_STARTUP_UI = (
    SCRIPT_ROOT / "Startup" / "ParrotAppStartupUiController.cs"
)
FORMAL_HOME_HUD = (
    SCRIPT_ROOT / "UI" / "FormalHomeHudController.cs"
)
FORMAL_HOME_MENU_LOADER = (
    SCRIPT_ROOT / "UI" / "FormalHomeMenuLoader.cs"
)
FORMAL_HOME_MENU_CONTROLLER = (
    SCRIPT_ROOT / "UI" / "FormalHomeMenuController.cs"
)
FORMAL_HOME_TOOL_CONTROLLER = (
    SCRIPT_ROOT / "UI" / "FormalHomeToolController.cs"
)
FORMAL_CAMERA_MODE_CONTROLLER = (
    SCRIPT_ROOT / "UI" / "FormalCameraModeController.cs"
)
VISUAL_TOOL_PACKET_BUILDER = (
    SCRIPT_ROOT / "VisualTools" / "VisualToolPacketBuilder.cs"
)
VISUAL_TOOL_HTTP_CLIENT = (
    SCRIPT_ROOT / "VisualTools" / "VisualToolHttpClient.cs"
)
BBOX_VISUAL_TOOL_CONTROLLER = (
    SCRIPT_ROOT / "VisualTools" / "BBoxVisualToolController.cs"
)
MAGNIFIER_VISUAL_TOOL_CONTROLLER = (
    SCRIPT_ROOT / "VisualTools" / "MagnifierVisualToolController.cs"
)
FORMAL_MODEL_REMOTE_CONTROLLER = (
    SCRIPT_ROOT / "UI" / "FormalModelRemoteController.cs"
)
FORMAL_XRHAND_PERCH_CONTROLLER = (
    SCRIPT_ROOT / "Lifecycle" / "FormalXrHandPerchController.cs"
)
HAND_GESTURE_SOURCE = (
    SCRIPT_ROOT / "Hands" / "HandGestureSource.cs"
)
CAMERA_HAND_POSE_FRAME = (
    SCRIPT_ROOT / "Hands" / "CameraHandPoseFrame.cs"
)
MEDIAPIPE_CAMERA_HAND_PROVIDER = (
    SCRIPT_ROOT / "Hands" / "MediaPipeCameraHandPoseProvider.cs"
)
MEDIAPIPE_HAND_LANDMARKER_MODEL = (
    PARROT_APP / "Resources" / "MediaPipe" / "hand_landmarker.bytes"
)
MEDIAPIPE_UNITY_PACKAGE = (
    ROOT / "unity" / "ArSpike" / "Packages" / "com.github.homuler.mediapipe-0.16.3.tgz"
)
ANDROID_LIBCXX_SHARED = (
    UNITY_ROOT / "Plugins" / "Android" / "arm64-v8a" / "libc++_shared.so"
)
ROOM_SETTING_CLIENT = (
    SCRIPT_ROOT / "Backend" / "AppRoomSettingClient.cs"
)
HOME_MENU_CLIENT = (
    SCRIPT_ROOT / "Backend" / "AppHomeMenuClient.cs"
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
MODEL_MANIFEST_DTO = (
    SCRIPT_ROOT / "Parrot" / "ModelManifestDto.cs"
)
FORMAL_MODEL_READY_REPORTER = (
    SCRIPT_ROOT / "Lifecycle" / "FormalModelReadyReporter.cs"
)
FORMAL_MODEL_PLACEMENT_CONTROLLER = (
    SCRIPT_ROOT / "Lifecycle" / "FormalModelPlacementController.cs"
)
FORMAL_AR_SESSION_BASELINE_REPORTER = (
    SCRIPT_ROOT / "Lifecycle" / "FormalArSessionBaselineReporter.cs"
)
FORMAL_AR_RUNTIME_BOOTSTRAP = (
    SCRIPT_ROOT / "Lifecycle" / "FormalArRuntimeBootstrap.cs"
)
AR_MOBILE_TEMPLATE_PLANE_PREFAB = (
    PARROT_APP / "Resources" / "ARMobileTemplate" / "Prefabs" / "ARFeatheredPlane.prefab"
)
AR_MOBILE_TEMPLATE_PLANE_VISUALIZER = (
    SCRIPT_ROOT / "ARMobileTemplate" / "ARFeatheredPlaneMeshVisualizer.cs"
)
AR_MOBILE_TEMPLATE_PLANE_COMPANION = (
    SCRIPT_ROOT / "ARMobileTemplate" / "ARFeatheredPlaneMeshVisualizerCompanion.cs"
)
AR_MOBILE_TEMPLATE_PLACE_ICON = (
    PARROT_APP / "Resources" / "ARMobileTemplate" / "UI" / "Sprites" / "Icon-Cube.png"
)
AR_MOBILE_TEMPLATE_XRI_INPUT_ACTIONS = (
    PARROT_APP / "Resources" / "ARMobileTemplate" / "XRIStarterAssets" / "XRI Default Input Actions.inputactions"
)
AR_MOBILE_TEMPLATE_SCREEN_RAY_PREFAB = (
    PARROT_APP / "Resources" / "ARMobileTemplate" / "XRIStarterAssets" / "Screen Space Ray Interactor.prefab"
)
AR_MOBILE_TEMPLATE_SHADOW_FUNCTIONS = (
    PARROT_APP / "Resources" / "ARMobileTemplate" / "Shaders" / "ShadowReceiver" / "ShadowReceiverShaderFunctions.hlsl"
)
AR_MOBILE_TEMPLATE_PLANE_FALLBACK_SHADER = (
    PARROT_APP / "Resources" / "ARMobileTemplate" / "Shaders" / "ParrotARPlaneFallback.shader"
)
AR_MOBILE_TEMPLATE_OBJECT_SPAWNER = (
    SCRIPT_ROOT / "ARMobileTemplate" / "XRIStarterAssets" / "ObjectSpawner.cs"
)
AR_MOBILE_TEMPLATE_SPAWN_TRIGGER = (
    SCRIPT_ROOT / "ARMobileTemplate" / "XRIStarterAssets" / "ARInteractorSpawnTrigger.cs"
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
AUDIO_ROUTE_MANAGER = (
    SCRIPT_ROOT / "LiveKit" / "AudioRouteManager.cs"
)
ANDROID_AUDIO_ROUTE_MANAGER = (
    SCRIPT_ROOT / "LiveKit" / "AndroidAudioRouteManager.cs"
)
AUDIO_ROUTE_SNAPSHOT = (
    SCRIPT_ROOT / "LiveKit" / "AudioRouteSnapshot.cs"
)
AUDIO_ROUTE_POLICY_REPORTER = (
    SCRIPT_ROOT / "LiveKit" / "AudioRoutePolicyBrainReporter.cs"
)
AUDIO_ROUTE_POLICY = (
    SCRIPT_ROOT / "LiveKit" / "AudioRoutePolicy.cs"
)
AUDIO_ROUTE_DETECTOR = (
    SCRIPT_ROOT / "LiveKit" / "AudioRouteDetector.cs"
)
RECONNECT_SUPERVISOR = (
    SCRIPT_ROOT / "LiveKit" / "LiveKitReconnectSupervisor.cs"
)
ROOM_MANAGER = (
    SCRIPT_ROOT / "LiveKit" / "RoomManager.cs"
)
ECP_EVENT_PUBLISHER = (
    SCRIPT_ROOT / "Ecp" / "EcpEventPublisher.cs"
)
PHOTO_CONTROLLER = (
    SCRIPT_ROOT / "Photo" / "PhotoController.cs"
)
FOCUS_CONTROLLER = (
    SCRIPT_ROOT / "Attention" / "FocusController.cs"
)
BBOX_CONTROLLER = (
    SCRIPT_ROOT / "Attention" / "BBoxController.cs"
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
GOSLO_MODEL_MANIFEST = PARROT_APP / "Resources" / "parrot_models" / "goslo_default.json"
ANDROID_AUDIO_ROUTE_MANIFEST = (
    UNITY_ROOT
    / "Plugins"
    / "Android"
    / "ParrotAudioRoute.androidlib"
    / "AndroidManifest.xml"
)
ANDROID_AUDIO_ROUTE_GRADLE = (
    UNITY_ROOT
    / "Plugins"
    / "Android"
    / "ParrotAudioRoute.androidlib"
    / "build.gradle"
)
ANDROID_AUDIO_ROUTE_JAVA = (
    UNITY_ROOT
    / "Plugins"
    / "Android"
    / "ParrotAudioRoute.androidlib"
    / "src"
    / "main"
    / "java"
    / "com"
    / "parrotcarriers"
    / "audio"
    / "AndroidAudioRouteManager.java"
)
ANDROID_AUDIO_ROUTE_CALLBACK_JAVA = (
    UNITY_ROOT
    / "Plugins"
    / "Android"
    / "ParrotAudioRoute.androidlib"
    / "src"
    / "main"
    / "java"
    / "com"
    / "parrotcarriers"
    / "audio"
    / "AudioRouteSnapshotCallback.java"
)
ANDROID_PCM_MIC_CAPTURE_JAVA = (
    UNITY_ROOT
    / "Plugins"
    / "Android"
    / "ParrotAudioRoute.androidlib"
    / "src"
    / "main"
    / "java"
    / "com"
    / "parrotcarriers"
    / "audio"
    / "AndroidPcmMicCapture.java"
)
ANDROID_MIC_FOREGROUND_SERVICE_JAVA = (
    UNITY_ROOT
    / "Plugins"
    / "Android"
    / "ParrotAudioRoute.androidlib"
    / "src"
    / "main"
    / "java"
    / "com"
    / "parrotcarriers"
    / "audio"
    / "ParrotMicForegroundService.java"
)
ANDROID_PCM_AUDIO_CALLBACK_JAVA = (
    UNITY_ROOT
    / "Plugins"
    / "Android"
    / "ParrotAudioRoute.androidlib"
    / "src"
    / "main"
    / "java"
    / "com"
    / "parrotcarriers"
    / "audio"
    / "AndroidPcmAudioCallback.java"
)


def _unity_guid(asset: Path) -> str:
    meta = asset.with_suffix(asset.suffix + ".meta")
    match = re.search(r"^guid:\s*([0-9a-f]+)$", meta.read_text(encoding="utf-8"), re.M)
    assert match, meta
    return match.group(1)


def test_smoke_reference_ui_keeps_app_v1_reference_flow_and_boundaries() -> None:
    text = SMOKE_REFERENCE_UI.read_text(encoding="utf-8")

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
    assert deps["com.github.homuler.mediapipe"] == "file:com.github.homuler.mediapipe-0.16.3.tgz"
    assert deps["io.livekit.livekit-sdk"].endswith(
        "#7d868ef5cc5615c30a3ef4b73ae0dbb5cc4d6796"
    )
    csc_rsp = CSC_RSP.read_text(encoding="utf-8")
    assert "UNITY_AR_FOUNDATION" in csc_rsp
    assert "UNITY_XR_HANDS" in csc_rsp
    assert "UNITY_MEDIAPIPE" in csc_rsp
    assert MEDIAPIPE_UNITY_PACKAGE.is_file()
    assert MEDIAPIPE_UNITY_PACKAGE.stat().st_size > 250_000_000
    assert MEDIAPIPE_HAND_LANDMARKER_MODEL.is_file()
    assert MEDIAPIPE_HAND_LANDMARKER_MODEL.stat().st_size > 1_000_000

    xr = XR_GENERAL_SETTINGS.read_text(encoding="utf-8")
    for provider in ["Android Providers", "iPhone Providers"]:
        assert re.search(
            rf"m_Name: {provider}[\s\S]{{0,260}}m_AutomaticLoading: 0[\s\S]{{0,80}}m_AutomaticRunning: 0",
            xr,
        ), provider
    for settings in ["Android Settings", "iPhone Settings"]:
        assert re.search(
            rf"m_Name: {settings}[\s\S]{{0,220}}m_InitManagerOnStart: 0",
            xr,
        ), settings
    assert re.search(
        r"m_Name: Standalone Settings[\s\S]{0,220}m_InitManagerOnStart: 0",
        xr,
    )
    assert re.search(
        r"m_Name: Standalone Providers[\s\S]{0,260}m_AutomaticLoading: 0[\s\S]{0,80}m_AutomaticRunning: 0",
        xr,
    )


def test_ner_spine_texture_importer_uses_alpha_transparency() -> None:
    meta = NER_SKIN2_TEXTURE_META.read_text(encoding="utf-8")

    assert "alphaIsTransparency: 1" in meta


def test_formal_model_runtime_assets_are_resources_loadable() -> None:
    goslo_manifest = json.loads(GOSLO_MODEL_MANIFEST.read_text(encoding="utf-8"))
    ner_manifest = json.loads(NER_MODEL_MANIFEST.read_text(encoding="utf-8"))
    audit = NER_SPINE_AUDIT.read_text(encoding="utf-8")

    assert goslo_manifest["asset_path"] == "Models/GOSLO"
    assert goslo_manifest["auto_scale_to_pet_height"] is True
    assert 0.10 <= goslo_manifest["default_pet_height_m"] <= 0.18
    assert ner_manifest["asset_path"] == "Models/Ner/NerSkin2_SkeletonData"
    assert (RUNTIME_MODELS / "GOSLO.glb").is_file()
    assert (RUNTIME_MODELS / "GOSLO.glb.meta").is_file()
    assert (RUNTIME_MODELS / "Ner" / "NerSkin2_SkeletonData.asset").is_file()
    assert (RUNTIME_MODELS / "Ner" / "NerSkin2_SkeletonData.asset.meta").is_file()
    assert (RUNTIME_MODELS / "Ner" / "NerSkin2.png.meta").is_file()
    assert (PARROT_APP / "Models" / "README.md").is_file()
    assert (PARROT_APP / "Models" / "README.md.meta").is_file()
    assert "Assets/ParrotApp/Resources/Models/Ner/NerSkin2_SkeletonData.asset" in audit
    assert "Assets/ParrotApp/Models/Ner/NerSkin2_SkeletonData.asset" not in audit


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
    assert all(line == line.rstrip() for line in text.splitlines())


def test_formal_startup_scene_explicitly_mounts_runtime_services() -> None:
    text = FORMAL_STARTUP_SCENE.read_text(encoding="utf-8")

    assert f"guid: {_unity_guid(SMOKE_REFERENCE_UI)}" not in text

    for script in [
        ROOM_SETTING_CLIENT,
        ORCHESTRATOR_CLIENT,
        SCRIPT_ROOT / "Ecp" / "LifecycleHeartbeatPublisher.cs",
        SCRIPT_ROOT / "LiveKit" / "AudioRouteDetector.cs",
        SCRIPT_ROOT / "LiveKit" / "MicrophonePublisher.cs",
        SCRIPT_ROOT / "LiveKit" / "ARVideoPublisher.cs",
        SCRIPT_ROOT / "LiveKit" / "VideoStateReporter.cs",
        SCRIPT_ROOT / "LiveKit" / "VideoTierReceiver.cs",
        AUDIO_ROUTE_POLICY_REPORTER,
        RECONNECT_SUPERVISOR,
        FORMAL_MAIN_READY_GATE,
        FORMAL_HOME_HUD,
        HOME_MENU_CLIENT,
        FORMAL_HOME_MENU_LOADER,
        FORMAL_MODEL_READY_REPORTER,
        FORMAL_MODEL_PLACEMENT_CONTROLLER,
        FORMAL_AR_SESSION_BASELINE_REPORTER,
        FORMAL_AR_RUNTIME_BOOTSTRAP,
    ]:
        assert f"guid: {_unity_guid(script)}" in text, script

    for field in [
        "roomSettingClient",
        "homeMenuClient",
        "microphonePublisher",
        "videoPublisher",
        "orchestratorClient",
        "heartbeatPublisher",
        "mainReadyGate",
        "homeHudController",
        "homeMenuLoader",
        "modelReadyReporter",
        "modelPlacementController",
        "arRuntimeBootstrap",
        "arSessionBaselineReporter",
    ]:
        assert f"{field}: {{fileID:" in text
        assert f"{field}: {{fileID: 0}}" not in text
    assert "bootstrapOnAwake: 0" in text
    assert "modelRoot: {fileID: 1775703627}" in text
    assert "placementCamera: {fileID: 275410333}" in text
    assert "mountXrOriginAndPlacementManagers: 1" in text
    assert "appApiBaseUrl: http://127.0.0.1:8790" not in text
    assert "appApiBaseUrl: http://localhost:8790" not in text


def test_ar_mobile_template_plane_assets_are_imported_into_formal_app() -> None:
    plane_companion = AR_MOBILE_TEMPLATE_PLANE_COMPANION.read_text(encoding="utf-8")
    for path in [
        AR_MOBILE_TEMPLATE_PLANE_PREFAB,
        AR_MOBILE_TEMPLATE_PLANE_VISUALIZER,
        AR_MOBILE_TEMPLATE_PLANE_COMPANION,
        AR_MOBILE_TEMPLATE_PLACE_ICON,
        AR_MOBILE_TEMPLATE_XRI_INPUT_ACTIONS,
        AR_MOBILE_TEMPLATE_SCREEN_RAY_PREFAB,
        AR_MOBILE_TEMPLATE_SHADOW_FUNCTIONS,
        AR_MOBILE_TEMPLATE_OBJECT_SPAWNER,
        AR_MOBILE_TEMPLATE_SPAWN_TRIGGER,
        PARROT_APP / "Resources" / "ARMobileTemplate" / "Materials" / "ShadowReceiver.mat",
        PARROT_APP / "Resources" / "ARMobileTemplate" / "Materials" / "OcclusionMaterial.mat",
        PARROT_APP / "Resources" / "ARMobileTemplate" / "Shaders" / "URPShadowReceiver.shader",
        PARROT_APP / "Resources" / "ARMobileTemplate" / "Shaders" / "InteractablePrimitive.shadergraph",
        PARROT_APP / "Resources" / "ARMobileTemplate" / "Shaders" / "PlaneOcclusionShader.shader",
        AR_MOBILE_TEMPLATE_PLANE_FALLBACK_SHADER,
        PARROT_APP / "Resources" / "ARMobileTemplate" / "Shaders" / "ShadowReceiver" / "ShadowReceiver.shadergraph",
        PARROT_APP / "Resources" / "ARMobileTemplate" / "Shaders" / "ShadowReceiver" / "MainLightShadowsSubgraph.shadersubgraph",
        PARROT_APP / "Resources" / "ARMobileTemplate" / "Textures" / "PlanePatternDot.png",
    ]:
        assert path.exists(), path
        assert path.with_suffix(path.suffix + ".meta").exists(), path

    prefab = AR_MOBILE_TEMPLATE_PLANE_PREFAB.read_text(encoding="utf-8")
    assert "ARFeatheredPlane" in prefab
    assert _unity_guid(AR_MOBILE_TEMPLATE_PLANE_VISUALIZER) in prefab
    assert _unity_guid(AR_MOBILE_TEMPLATE_PLANE_COMPANION) in prefab

    screen_ray = AR_MOBILE_TEMPLATE_SCREEN_RAY_PREFAB.read_text(encoding="utf-8")
    assert "Screen Space Ray Interactor" in screen_ray
    assert _unity_guid(AR_MOBILE_TEMPLATE_XRI_INPUT_ACTIONS) in screen_ray
    assert "m_EnableARRaycasting: 1" in screen_ray

    spawn_trigger = AR_MOBILE_TEMPLATE_SPAWN_TRIGGER.read_text(encoding="utf-8")
    assert "#if AR_FOUNDATION_PRESENT || UNITY_AR_FOUNDATION" in spawn_trigger
    assert "ARInteractorSpawnTrigger" in spawn_trigger
    assert "ObjectSpawner" in AR_MOBILE_TEMPLATE_OBJECT_SPAWNER.read_text(encoding="utf-8")
    assert "EnsureRuntimeSafeMaterialFallback" in plane_companion
    assert "m_UseRuntimeSafeMaterialFallback || Application.isMobilePlatform" in plane_companion
    assert "m_ForceMobileMaterialFallback = false" in plane_companion
    assert "m_ForceMobileMaterialFallback && Application.isMobilePlatform" in plane_companion
    assert "bool m_UseAndroidShaderGraphPlaneFallback = true" in plane_companion
    assert "!m_UseAndroidShaderGraphPlaneFallback && !Application.isMobilePlatform" in plane_companion
    assert "Root fix remains the demo2 ShaderGraph chain" in plane_companion
    assert "simple translucent white surface" in plane_companion
    assert "Hidden/Shader Graph/FallbackError" in plane_companion
    assert 'shaderName.Equals("Shader Graphs/ShadowReceiver"' in plane_companion
    assert "render as Unity's magenta error material" in plane_companion
    assert 'Resources.Load<Shader>("ARMobileTemplate/Shaders/ParrotARPlaneFallback")' in plane_companion
    assert "m_ReplaceMobileOcclusionSlot = true" in plane_companion
    assert "m_ReplaceMobileOcclusionSlot || Application.isMobilePlatform" in plane_companion
    assert "ShouldReplaceOcclusionSlot(original)" in plane_companion
    assert 'shaderName.Equals("AR/Occlusion"' in plane_companion
    assert 'materialName.IndexOf("Occlusion"' in plane_companion
    assert "ParrotRuntimeNoopARPlaneOcclusion" in plane_companion
    assert "Keep the demo2 surface/dot material" in plane_companion
    assert "bool replacedAny = false" in plane_companion
    assert "NeedsRuntimeSafeFallback(original)" in plane_companion
    assert "NeedsAndroidPlaneShaderFallback(original)" in plane_companion
    assert "runtimeSafeMaterialActive" in plane_companion
    assert "materialDebugSummary" in plane_companion
    assert "MaterialShaderSummary" in plane_companion
    assert "ParrotRuntimeSafeARPlaneTranslucentWhite" in plane_companion
    assert "FindRuntimeSafeTransparentShader" in plane_companion
    assert '"Unlit/Transparent"' in plane_companion
    assert 'shaderName.Equals("Parrot/ARPlaneFallbackTransparent"' in plane_companion
    assert plane_companion.index('"Unlit/Transparent"') < plane_companion.index('"Universal Render Pipeline/Unlit"')
    assert plane_companion.index('"Unlit/Transparent"') < plane_companion.index("ParrotARPlaneFallback")
    assert "shader != null && shader.isSupported" in plane_companion
    assert 'SetOverrideTag("RenderType", "Transparent")' in plane_companion
    assert "CullMode.Off" in plane_companion
    assert "ARMobileTemplate/Textures/PlanePatternDot" in plane_companion

    shadow_receiver = (
        PARROT_APP / "Resources" / "ARMobileTemplate" / "Materials" / "ShadowReceiver.mat"
    ).read_text(encoding="utf-8")
    assert _unity_guid(PARROT_APP / "Resources" / "ARMobileTemplate" / "Textures" / "PlanePatternDot.png") in shadow_receiver
    assert "f682ded1fcdaacb4fb33ca928c0d632a" not in shadow_receiver

    shadow_functions_guid = _unity_guid(AR_MOBILE_TEMPLATE_SHADOW_FUNCTIONS)
    subgraph = (
        PARROT_APP
        / "Resources"
        / "ARMobileTemplate"
        / "Shaders"
        / "ShadowReceiver"
        / "MainLightShadowsSubgraph.shadersubgraph"
    ).read_text(encoding="utf-8")
    assert shadow_functions_guid in subgraph

    plane_visualizer = AR_MOBILE_TEMPLATE_PLANE_VISUALIZER.read_text(encoding="utf-8")
    assert "m_FeatheredPlaneMaterial.SetFloat(\"_ShortestUVMapping\", shortestUVMapping)" in plane_visualizer
    assert "mesh.SetUVs(1, s_FeatheringUVs)" in plane_visualizer
    assert "m_Plane.boundaryChanged += ARPlane_boundaryUpdated" in plane_visualizer

def test_project_settings_default_scene_is_formal_startup_scene() -> None:
    text = PROJECT_SETTINGS.read_text(encoding="utf-8")

    assert "templateDefaultScene: Assets/ParrotApp/Scenes/ParrotApp_Startup.unity" in text
    assert "templateDefaultScene: Assets/Scenes/SampleScene.unity" not in text


def test_project_settings_are_formal_landscape_android_app() -> None:
    text = PROJECT_SETTINGS.read_text(encoding="utf-8")

    assert "companyName: ParrotCarriers" in text
    assert "productName: ParrotApp" in text
    assert "Android: com.parrotcarriers.app" in text
    assert "com.unity.template.ar_mobile" not in text
    assert "companyName: DefaultCompany" not in text

    assert "defaultScreenOrientation: 3" in text
    assert "allowedAutorotateToPortrait: 0" in text
    assert "allowedAutorotateToPortraitUpsideDown: 0" in text
    assert "allowedAutorotateToLandscapeRight: 1" in text
    assert "allowedAutorotateToLandscapeLeft: 1" in text
    assert "androidDefaultWindowWidth: 1920" in text
    assert "androidDefaultWindowHeight: 1080" in text
    assert "insecureHttpOption: 2" in text


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
    assert "_previewRequestRevision" in ui
    assert "PreviewCurrentRoomProfile(int revision)" in ui
    assert "Preview stale ignored" in ui
    assert "BuildWritableRoomProfileForSave" in ui
    assert "IsReservedRoomProfileId" in ui
    assert 'string.Equals(id, "ner_lineb_room", StringComparison.Ordinal)' in ui
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
    assert "save_room_profile_missing_profile" in client
    assert "apply_room_profile_missing_profile" in client
    assert "NewRoomProfileResponseDto" in dtos
    assert "SkinSelectorDto" in dtos
    assert "public SkinSelectorDto[] skins" in dtos
    assert "ApplyRoomProfileResponseDto" in dtos
    assert "appApiUrl" in runtime
    assert "appApiSecret" in runtime
    assert "config.appApiSecret" in client


def test_formal_startup_layout_targets_landscape_phone_and_theme_selector() -> None:
    text = FORMAL_STARTUP_UI.read_text(encoding="utf-8")

    assert 'Resources.GetBuiltinResource<Font>("LegacyRuntime.ttf")' in text
    assert "Arial.ttf" not in text
    assert "private const float ReferenceWidth = 2800f" in text
    assert "private const float ReferenceHeight = 1260f" in text
    assert "iQOO Neo9 landscape target" in text
    assert "StartupSelectionSummary" in text
    assert "new Vector2(2140f, 900f)" in text
    assert 'Tr("套装", "Theme")' in text
    assert "ToggleTheme" in text
    assert "FormalMainReadyGate mainReadyGate" in text
    assert "Loading home gates" in text
    assert "MainReadyMissingText" in text
    assert "HideMainReadySurfaceForFormalHome" in text
    assert "startup surface hidden for formal home" in text
    assert "RemoveLegacyInputModule(standaloneModule)" in text
    assert "GetComponent<InputSystemUIInputModule>()" in text
    assert "GetComponent<StandaloneInputModule>()" in text
    assert "ReportGosloPlaced" not in text
    assert '"PLACED"' not in text
    assert 'Tr("Scene", "Scene")' not in text
    assert 'Tr("AR 就绪", "AR READY")' in text
    assert 'Tr("新建", "NEW")' in text
    assert 'Tr("保存", "SAVE")' in text


def test_startup_livekit_tier1_rpc_business_failure_and_heartbeat_contract() -> None:
    flow = STARTUP_FLOW.read_text(encoding="utf-8")
    main_ready = FORMAL_MAIN_READY_GATE.read_text(encoding="utf-8")
    home_hud = FORMAL_HOME_HUD.read_text(encoding="utf-8")
    orch = ORCHESTRATOR_CLIENT.read_text(encoding="utf-8")
    shutdown = SHUTDOWN_SERVICE.read_text(encoding="utf-8")
    room_manager = ROOM_MANAGER.read_text(encoding="utf-8")
    video = (SCRIPT_ROOT / "LiveKit" / "ARVideoPublisher.cs").read_text(encoding="utf-8")
    video_tier_receiver = (SCRIPT_ROOT / "LiveKit" / "VideoTierReceiver.cs").read_text(encoding="utf-8")
    mic = (SCRIPT_ROOT / "LiveKit" / "MicrophonePublisher.cs").read_text(encoding="utf-8")
    route_manager = AUDIO_ROUTE_MANAGER.read_text(encoding="utf-8")
    android_route_manager = ANDROID_AUDIO_ROUTE_MANAGER.read_text(encoding="utf-8")
    route_snapshot = AUDIO_ROUTE_SNAPSHOT.read_text(encoding="utf-8")
    route_reporter = AUDIO_ROUTE_POLICY_REPORTER.read_text(encoding="utf-8")
    route_policy = AUDIO_ROUTE_POLICY.read_text(encoding="utf-8")
    route_detector = AUDIO_ROUTE_DETECTOR.read_text(encoding="utf-8")
    android_route_manifest = ANDROID_AUDIO_ROUTE_MANIFEST.read_text(encoding="utf-8")
    android_route_gradle = ANDROID_AUDIO_ROUTE_GRADLE.read_text(encoding="utf-8")
    android_route_java = ANDROID_AUDIO_ROUTE_JAVA.read_text(encoding="utf-8")
    android_route_callback_java = ANDROID_AUDIO_ROUTE_CALLBACK_JAVA.read_text(encoding="utf-8")
    android_pcm_capture_java = ANDROID_PCM_MIC_CAPTURE_JAVA.read_text(encoding="utf-8")
    android_mic_foreground_service_java = ANDROID_MIC_FOREGROUND_SERVICE_JAVA.read_text(encoding="utf-8")
    android_pcm_callback_java = ANDROID_PCM_AUDIO_CALLBACK_JAVA.read_text(encoding="utf-8")
    android_pcm_source = (SCRIPT_ROOT / "LiveKit" / "AndroidPcmMicrophoneSource.cs").read_text(encoding="utf-8")
    reconnect_supervisor = RECONNECT_SUPERVISOR.read_text(encoding="utf-8")
    lifecycle = APP_LIFECYCLE_MANAGER.read_text(encoding="utf-8")
    ecp_dto = (SCRIPT_ROOT / "Ecp" / "EcpEventDto.cs").read_text(encoding="utf-8")
    ecp_dispatcher = (SCRIPT_ROOT / "Ecp" / "EcpEventDispatcher.cs").read_text(encoding="utf-8")
    heartbeat = (SCRIPT_ROOT / "Ecp" / "LifecycleHeartbeatPublisher.cs").read_text(encoding="utf-8")

    assert "OrchestratorClient orchestratorClient" in flow
    assert "AppRoomSettingClient roomSettingClient" in flow
    assert "PrepareTierOneRuntimeConfig" in flow
    assert "ApplyStartupRoomProfileHttp" in flow
    assert "room_setting_http_apply_required" in flow
    assert "roomSettingClient.ApplyRoomProfile" in flow
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
    assert "AudioRouteManager" in flow
    assert "host.AddComponent<AudioRouteManager>()" in flow
    assert "AudioRoutePolicyBrainReporter" in flow
    assert "host.AddComponent<AudioRoutePolicyBrainReporter>()" in flow
    assert "LiveKitReconnectSupervisor" in flow
    assert "host.AddComponent<LiveKitReconnectSupervisor>()" in flow
    assert "FormalMainReadyGate mainReadyGate" in flow
    assert "host.AddComponent<FormalMainReadyGate>()" in flow
    assert "FormalHomeHudController homeHudController" in flow
    assert "host.AddComponent<FormalHomeHudController>()" in flow
    assert "AppHomeMenuClient homeMenuClient" in flow
    assert "AddComponent<AppHomeMenuClient>()" in flow
    assert "FormalHomeMenuLoader homeMenuLoader" in flow
    assert "host.AddComponent<FormalHomeMenuLoader>()" in flow
    assert "FormalHomeMenuController homeMenuController" in flow
    assert "host.AddComponent<FormalHomeMenuController>()" in flow
    assert "EcpEventPublisher ecpEventPublisher" in flow
    assert "host.AddComponent<EcpEventPublisher>()" in flow
    assert "FormalHomeToolController homeToolController" in flow
    assert "host.AddComponent<FormalHomeToolController>()" in flow
    assert "FormalCameraModeController cameraModeController" in flow
    assert "host.AddComponent<FormalCameraModeController>()" in flow
    assert "VisualToolHttpClient visualToolHttpClient" in flow
    assert "host.AddComponent<VisualToolHttpClient>()" in flow
    assert "BBoxVisualToolController bboxVisualToolController" in flow
    assert "host.AddComponent<BBoxVisualToolController>()" in flow
    assert "MagnifierVisualToolController magnifierVisualToolController" in flow
    assert "host.AddComponent<MagnifierVisualToolController>()" in flow
    assert "FormalModelRemoteController modelRemoteController" in flow
    assert "host.AddComponent<FormalModelRemoteController>()" in flow
    assert "FormalXrHandPerchController xrHandPerchController" in flow
    assert "host.AddComponent<FormalXrHandPerchController>()" in flow
    assert "SwitchWorkspace(string workspaceId, string layoutKind)" in flow
    assert "_workspaceSwitchCoroutine" in flow
    assert "_hasQueuedWorkspaceSwitch" in flow
    assert "_queuedWorkspaceId" in flow
    assert "workspace switch queued" in flow
    assert "EnsureConfirmedSessionState" in flow
    assert "RecordConfirmedSessionState" in flow
    assert "NormalizeWorkspaceId" in flow
    assert "SwitchWorkspaceRoutine" in flow
    assert "CapabilityModeForWorkspace" in flow
    assert '"2d_workspace"' in flow
    assert "AppCapabilityModeNames.VoiceOnlyNoVideo" in flow
    assert "workspace_session_policy" in flow
    assert flow.index('"workspace_session_policy"') < flow.index('"workspace_switch"')
    assert "workspace_session_policy_failed" in flow
    policy_failure_block = flow[flow.index("workspace_session_policy_failed"):flow.index('"workspace_switch"')]
    assert "yield break;" in policy_failure_block
    assert "workspace_session_policy_rollback" in flow
    assert "workspace_switch_failed" in flow
    assert "OnWorkspaceSwitchApplied" in flow
    assert "OnWorkspaceSwitchFailed" in flow
    assert "OnCompactControlApplied" in flow
    assert "OnCompactControlFailed" in flow
    assert "ApplyCompactControlRoutine" in flow
    assert "SetPhotoAwarenessPolicy" in flow
    assert '"setPhotoAwareness"' in flow
    assert "SetCameraMode" in flow
    assert '"setCameraMode"' in flow
    assert "SetXrHandMode" in flow
    assert '"setXrHandMode"' in flow
    assert "FormalModelReadyReporter modelReadyReporter" in flow
    assert "host.AddComponent<FormalModelReadyReporter>()" in flow
    assert "FormalModelPlacementController modelPlacementController" in flow
    assert "host.AddComponent<FormalModelPlacementController>()" in flow
    assert "FormalArRuntimeBootstrap arRuntimeBootstrap" in flow
    assert "host.AddComponent<FormalArRuntimeBootstrap>()" in flow
    assert "PrepareArRuntimeForVideoIfNeeded" in flow
    assert "yield return arRuntimeBootstrap.EnsureArRuntimeReady()" in flow
    assert flow.index('"startup_reuse_capability_mode"') < flow.index("PrepareArRuntimeForVideoIfNeeded")
    assert "ar_runtime_prepare_failed" in flow
    assert "FormalArSessionBaselineReporter arSessionBaselineReporter" in flow
    assert "host.AddComponent<FormalArSessionBaselineReporter>()" in flow
    assert "RequestFreshTokenReconnect" in flow
    assert "fresh_reconnect_token_mint_failed" in flow
    assert "fresh_reconnect_room_profile_sync_timeout" in flow
    assert "RestartConnectedRoomForTierOne" in flow
    assert "shutdownService.RequestShutdown(\"tier1_setting_requires_fresh_livekit_reconnect\")" in flow
    assert "tier1_fresh_reconnect_shutdown_timeout" in flow
    assert "tier1_fresh_reconnect_waits_for_shutdown_cooldown" in flow
    assert "tier1_fresh_reconnect_reenter_token_gate" in flow
    assert "tier1_fresh_reconnect_room_profile" in flow
    assert "ExpiredWarningMinIntervalSeconds" in video_tier_receiver
    assert "LogExpiredCommand" in video_tier_receiver
    assert "suppressed \" + _suppressedExpiredWarnings" in video_tier_receiver
    assert '"setLineBAudioRoutePolicy"' in route_reporter
    assert "AudioRouteManager routeManager" in route_reporter
    assert "unity_audio_route_policy" in route_reporter
    assert "BrainParticipantResolver.FindBrainParticipantId" in route_reporter
    assert "RefreshAndReportCurrentPolicy" in route_reporter
    assert "ReportPending" in route_reporter
    assert "RpcBusinessResponse" in route_reporter
    assert "response.result.success" in route_reporter
    assert "LastInputRoute" in route_reporter
    assert "LastOutputRoute" in route_reporter
    assert "LastPreferredSampleRate" in route_reporter
    assert "LastDetectionSource" in route_reporter
    assert "LastDeviceSummary" in route_reporter
    assert "LastReportReason" in route_reporter
    assert "CachePolicy" in route_reporter
    assert "InputRouteFor" in route_reporter
    assert "system_default_microphone" in route_reporter
    assert "input_route" in route_reporter
    assert "output_route" in route_reporter
    assert "class AudioRouteManager" in route_manager
    assert "AndroidAudioRouteManager" in route_manager
    assert "OnAndroidAudioRouteSnapshot" in route_manager
    assert "AudioRouteSnapshotDto" in route_manager
    assert "RequestCommunicationMode(bool enabled)" in route_manager
    assert "SetPreference(AudioRoutePreference" in route_manager
    assert "ApplyTemporaryNativePreference(AudioRoutePreference" in route_manager
    assert "Temporary capture fallbacks are session-local" in route_manager
    assert "!enabled && _temporaryNativePreferenceActive" in route_manager
    assert "ShouldRestoreTemporaryPreference" in route_manager
    assert "return false;" in route_manager
    assert 'return string.Equals(reason, "device_added"' not in route_manager
    assert "can undo the fallback that just made uplink work" in route_manager
    assert "CurrentPolicy = AudioRoutePolicy.Default();" in route_manager
    assert "if (changed)" in route_manager
    assert "changed ||" not in route_manager
    assert "OnRoutePolicyChanged" in route_manager
    assert "AudioRouteDetector" in route_manager
    assert "fallback/diagnostic" in route_manager
    assert "class AndroidAudioRouteManager" in android_route_manager
    assert "com.parrotcarriers.audio.AndroidAudioRouteManager" in android_route_manager
    assert "AudioRouteSnapshotCallbackProxy" in android_route_manager
    assert "com.parrotcarriers.audio.AudioRouteSnapshotCallback" in android_route_manager
    assert "UnityMainThread.Enqueue" in android_route_manager
    assert "requestCommunicationMode" in android_route_manager
    assert "BLUETOOTH_CONNECT" in android_route_manifest
    assert "MODIFY_AUDIO_SETTINGS" in android_route_manifest
    assert "RECORD_AUDIO" in android_route_manifest
    assert "FOREGROUND_SERVICE" in android_route_manifest
    assert "FOREGROUND_SERVICE_MICROPHONE" in android_route_manifest
    assert 'android:foregroundServiceType="microphone"' in android_route_manifest
    assert "ParrotMicForegroundService" in android_route_manifest
    assert 'package="com.parrotcarriers.audio"' in android_route_manifest
    assert 'namespace "com.parrotcarriers.audio"' in android_route_gradle
    assert "buildConfig false" in android_route_gradle
    assert "com.parrotcarriers.app" not in android_route_gradle
    assert "setCommunicationDevice" in android_route_java
    assert "startMicrophoneForegroundService" in android_route_java
    assert "stopMicrophoneForegroundService" in android_route_java
    assert "startForegroundService(intent)" in android_route_java
    assert "activity.stopService(intent)" in android_route_java
    assert 'handleDeviceTopologyChanged("device_added")' in android_route_java
    assert 'handleDeviceTopologyChanged("device_removed")' in android_route_java
    assert "applyPreferredCommunicationDevice(reason)" in android_route_java
    assert 'reasonPrefix + "_cleared_for_system_default"' in android_route_java
    assert 'reasonPrefix + "_cleared_for_output_bluetooth"' in android_route_java
    assert "getAvailableCommunicationDevices" in android_route_java
    assert "requestAudioFocus" in android_route_java
    assert "preference_changed_cached" in android_route_java
    assert "Always enter observe/media mode on initialize" in android_route_java
    assert "MicrophonePublisher will explicitly request routing again" in android_route_java
    assert "boolean canUseBluetooth = hasBluetoothConnectPermission()" in android_route_java
    assert 'if (canUseBluetooth && ("bluetooth".equals(preference) || "auto".equals(preference)))' in android_route_java
    assert "hasBluetoothOutputType(getDevices(AudioManager.GET_DEVICES_OUTPUTS))" in android_route_java
    assert "shouldKeepMediaModeForOutputBluetooth" in android_route_java
    assert "shouldKeepMediaModeForDefaultCapture" in android_route_java
    assert '"auto".equals(preference)' in android_route_java
    assert '"system_default".equals(preference)' in android_route_java
    assert '"phone_mic".equals(preference)' in android_route_java
    assert "communication_mode_kept_media_bluetooth_output" in android_route_java
    assert "communication_mode_kept_media_phone_output" in android_route_java
    assert "mediaBluetoothReason(reason)" in android_route_java
    assert "mediaPhoneReason(reason)" in android_route_java
    assert "mediaModeReason(\"communication_mode\")" in android_route_java
    assert "setSpeakerphoneOn(false)" in android_route_java
    assert 'keepMediaMode(mediaBluetoothReason(reason), "normal_bt_output")' in android_route_java
    assert 'keepMediaMode(mediaPhoneReason(reason), "normal_phone_output")' in android_route_java
    assert 'reasonPrefix + "_bluetooth_rejected"' in android_route_java
    assert "MODE_IN_COMMUNICATION" in android_route_java and "phone speaker" in android_route_java
    assert "do not" in android_route_java and "steal Parrot audio away from the" in android_route_java
    assert "Explicit Bluetooth preference is advisory" in android_route_java
    assert "AR companion mode is a hands-free voice session" in android_route_java
    assert android_route_java.index("AudioDeviceInfo speaker = firstDevice(devices, AudioDeviceInfo.TYPE_BUILTIN_SPEAKER)") < android_route_java.index("return firstDevice(devices, AudioDeviceInfo.TYPE_BUILTIN_EARPIECE)")
    assert "bluetooth_connect_denied" not in android_route_java
    assert "class Api31" in android_route_java
    assert "Object communicationDeviceChangedListener" in android_route_java
    assert "OnCommunicationDeviceChangedListener communicationDeviceChangedListener" not in android_route_java
    assert "UnityPlayer" not in android_route_java
    assert "AudioRouteSnapshotCallback callback" in android_route_java
    assert "callback.onAudioRouteSnapshot(json)" in android_route_java
    assert "interface AudioRouteSnapshotCallback" in android_route_callback_java
    assert "interface AndroidPcmAudioCallback" in android_pcm_callback_java
    assert "AudioRecord" in android_pcm_capture_java
    assert "buildFirstUsableAudioRecord" in android_pcm_capture_java
    assert "one strict sample rate per Java capture instance" in android_pcm_capture_java
    assert "requestedSampleRate > 0 ? requestedSampleRate : 48000" in android_pcm_capture_java
    assert "sampleRateCandidates" not in android_pcm_capture_java
    assert "MediaRecorder.AudioSource.VOICE_COMMUNICATION" in android_pcm_capture_java
    assert "MediaRecorder.AudioSource.MIC" in android_pcm_capture_java
    assert "preferVoiceCommunication" in android_pcm_capture_java
    assert "already proved the plain MIC source is producing" in android_pcm_capture_java
    assert "gates or silences" in android_pcm_capture_java and "near-end capture" in android_pcm_capture_java
    assert "rate=\" + activeSampleRate" in android_pcm_capture_java
    assert "source_name" in android_pcm_capture_java
    assert "+ \"\\\",\\\"recording\\\":\" + isRecording()" in android_pcm_capture_java
    assert "pcm_callback_failed" in android_pcm_capture_java
    assert "read_error_persistent" in android_pcm_capture_java
    assert "read_zero_persistent" in android_pcm_capture_java
    assert "com.unity3d.player.UnityPlayer" not in android_pcm_capture_java
    assert "FOREGROUND_SERVICE_TYPE_MICROPHONE" in android_mic_foreground_service_java
    assert "android.R.drawable.ic_btn_speak_now" in android_mic_foreground_service_java
    assert "Keeps the AR companion microphone capture active" in android_mic_foreground_service_java
    assert "AndroidJavaProxy" in android_pcm_source
    assert "com.parrotcarriers.audio.AndroidPcmAudioCallback" in android_pcm_source
    assert "new AndroidJavaObject(\"com.parrotcarriers.audio.AndroidPcmMicCapture\")" in android_pcm_source
    assert "AndroidPcmMicrophoneSource is Android-only" in android_pcm_source
    assert "RefreshNativeError(\"start_returned_false\")" in android_pcm_source
    assert "_native.Call<string>(\"lastError\")" in android_pcm_source
    assert "BuildNativeStartError" in android_pcm_source
    assert "android_pcm_bridge_unavailable" in android_pcm_source
    assert "ShortMessage" in android_pcm_source
    assert "LastNativeSourceName" in android_pcm_source
    assert "ExtractJsonString(LastNativeState, \"source_name\")" in android_pcm_source
    assert android_pcm_source.index("if (_started) return;") < android_pcm_source.index("base.Start();")
    assert android_pcm_source.index("_started = true;") < android_pcm_source.index("_native.Call<bool>(")
    assert "LastNativeState = string.IsNullOrWhiteSpace(LastNativeState)" in android_pcm_source
    assert "_started = false;\n                CleanupNative();" in android_pcm_source
    assert "CleanupNative();\n                base.Stop();" in android_pcm_source
    assert "Math.Min(length, samples.Length)" in android_pcm_source
    assert "Mathf.Min(length, samples.Length)" not in android_pcm_source
    assert "TYPE_BLUETOOTH_SCO" in android_route_java
    assert "TYPE_BLUETOOTH_A2DP" in android_route_java
    assert "TYPE_BLE_HEADSET" in android_route_java
    assert "TYPE_BLE_SPEAKER" in android_route_java
    assert "TYPE_HEARING_AID" in android_route_java
    assert "isBluetoothVoiceType" in android_route_java
    assert "hasBluetoothOutputType" in android_route_java
    assert "shouldClearCommunicationDeviceForOutputBluetooth" in android_route_java
    assert '"_cleared_for_output_bluetooth"' in android_route_java
    assert "Clearing here lets Android keep Bluetooth media" in android_route_java
    assert "bluetooth_connect_permission" in android_route_java
    assert "getDevices() is only an availability list" in android_route_java
    assert 'if (hasDeviceType(inputs, AudioDeviceInfo.TYPE_BLUETOOTH_SCO)) {' not in android_route_java
    assert 'if (hasDeviceType(outputs, AudioDeviceInfo.TYPE_BLUETOOTH_SCO)) {' not in android_route_java
    assert "class AudioRouteSnapshotDto" in route_snapshot
    assert "AudioRoutePreference" in route_snapshot
    assert "requires_mic_republish" in route_snapshot
    assert "recommended_sample_rate_hz" in route_snapshot
    assert "KindFromRoutes" in route_snapshot
    assert "This policy drives the microphone source" in route_snapshot
    assert "output route is A2DP" in route_snapshot
    assert "RefreshCurrentPolicy" in route_detector
    assert "ReevaluateAndFire" in route_detector
    assert "TryDetectAndroidDevices" in route_detector
    assert '"getDevices"' in route_detector
    assert '"getCommunicationDevice"' in route_detector
    assert '"communication=" + communicationType' in route_detector
    assert "getDevices(GET_DEVICES_INPUTS) is an availability list" in route_detector
    assert "falsely force the formal App into bt-sco@16k" in route_detector
    assert "HasAnyDeviceType(inputs, typeBluetoothSco" not in route_detector
    assert "HasAnyDeviceType(inputs, typeWiredHeadset" not in route_detector
    assert "GET_DEVICES_INPUTS" in route_detector
    assert "GET_DEVICES_OUTPUTS" in route_detector
    assert "TYPE_BLUETOOTH_SCO" in route_detector
    assert "TYPE_BLUETOOTH_A2DP" in route_detector
    assert "TYPE_BLE_HEADSET" in route_detector
    assert "TYPE_BLE_SPEAKER" in route_detector
    assert "TYPE_HEARING_AID" in route_detector
    assert "DetectAndroidLegacyFlags" in route_detector
    assert "LastDetectionSource" in route_detector
    assert "LastDeviceSummary" in route_detector
    assert "A2DP stay at 48 kHz" in route_policy
    assert "case AudioRouteKind.BluetoothSco:" in route_policy
    assert "case AudioRouteKind.BluetoothA2dp:" in route_policy
    assert "BluetoothA2dp:\n                case AudioRouteKind.WiredHeadset" in route_policy
    assert "allowAndroidDefaultMicrophoneWhenDeviceListEmpty = true" in mic
    assert "ShouldUseAndroidDefaultMicrophoneWhenDeviceListEmpty" in mic
    assert "Native route snapshots can briefly be stale or unknown" in mic
    assert "android_default_microphone" in mic
    assert 'LastManualDeviceStatus = "auto:android_default_microphone"' in mic
    assert 'return ShouldUseAndroidDefaultMicrophoneWhenDeviceListEmpty()' in mic
    assert "IsAndroidMicInputRoute" in mic
    assert "CreateAudioSourceForAttempt" in mic
    assert "ShouldUseAndroidAudioRecordFallbackSource" in mic
    assert "uplinkWatchdogZeroPeakSeconds" in mic
    assert "uplink_watchdog_zero_peak_unity_microphone" in mic
    assert "_forceAndroidAudioRecordNextPublish = true" in mic
    assert "ShouldPromoteSilentUnityStreamToAndroidAudioRecord" in mic
    assert "AddAndroidAudioRecordFallbackAttempts" in mic
    assert "new AndroidPcmMicrophoneSource(_configuredSampleRate, 1" in mic
    assert "new MicrophoneSource(" in mic
    assert "requiresUnityMicrophonePosition = false" in mic
    assert 'sourceKind = "android_audio_record"' in mic
    assert '"source:" + sourceKind' in mic
    assert "string.IsNullOrEmpty(attempt?.DeviceName) ? null : attempt.DeviceName" in mic
    assert "RequestFreshTokenReconnect" in reconnect_supervisor
    assert "Mathf.Pow(2f" in reconnect_supervisor
    assert "IsBackgroundState" in reconnect_supervisor
    assert "roomManager.IsDisconnecting" in reconnect_supervisor
    assert "fresh_token_backoff" in reconnect_supervisor
    assert "CurrentState == AppLifecycleState.Reconnecting" in lifecycle
    assert "CurrentState == AppLifecycleState.Connecting" in lifecycle
    assert "CurrentState == AppLifecycleState.ArSessionStarting" in lifecycle
    assert "CurrentState == AppLifecycleState.TokenGate" in lifecycle
    assert "FromWireJson" in ecp_dto
    assert "ExtractBalancedJson" in ecp_dto
    assert "EcpEventBuilder.FromWireJson(json)" in ecp_dispatcher
    assert "AnimationDriver _subscribedAnimationDriver" in heartbeat
    assert "AnimationDriverBindRetrySeconds" in heartbeat
    assert "_nextAnimationDriverBindAt" in heartbeat
    assert "EnsureAnimationDriverBound();" in heartbeat
    assert "FindObjectOfType<AnimationDriver>()" in heartbeat
    assert '"animation_driver_bound"' in heartbeat
    assert "public void ReportBodyState(string bodyStateWire)" in heartbeat
    assert '"body_state_external"' in heartbeat
    assert "UnbindAnimationDriver();" in heartbeat
    assert "class FormalMainReadyGate" in main_ready
    assert "OnMainUiReady += HandleStartupMainReady" in main_ready
    assert "ReportRunning()" in main_ready
    assert '"startup_transport_ready"' in main_ready
    assert '"startup_brain_rpc_synced"' in main_ready
    assert '"heartbeat_datachannel_ready"' in main_ready
    assert '"hud_loaded"' in main_ready
    assert '"menu_snapshot_loaded"' in main_ready
    assert '"model_resolved"' in main_ready
    assert '"ar_session_baseline_clean"' in main_ready
    assert "requireAudioWhenModeNeedsMic = false" in main_ready
    assert "requireVideoWhenModeNeedsVideo = false" in main_ready
    scene = FORMAL_STARTUP_SCENE.read_text(encoding="utf-8")
    assert "requireAudioWhenModeNeedsMic: 0" in scene
    assert "requireVideoWhenModeNeedsVideo: 0" in scene
    assert "AppCapabilityModeNames.MicrophoneEnabled" in main_ready
    assert "VideoFreshFrame" in main_ready
    assert "OnGateChanged" in main_ready
    assert "waitingReevaluateIntervalSeconds" in main_ready
    assert "waiting_tick" in main_ready
    assert "class FormalHomeHudController" in home_hud
    assert "ReportHudLoaded" in home_hud
    assert "formal_home_hud_shell" in home_hud
    assert "FormalHomeHudCanvas" in home_hud
    assert "OnMainUiReady += HandleStartupMainReady" in home_hud
    assert "LastMissingGates" in home_hud
    assert "FormalHomeMenuLoader menuLoader" in home_hud
    assert "LiveKitReconnectSupervisor reconnectSupervisor" in home_hud
    assert "AudioRoutePolicyBrainReporter audioRouteReporter" in home_hud
    assert "MicrophonePublisher microphonePublisher" in home_hud
    assert "FormalModelPlacementController modelPlacementController" in home_hud
    assert "FormalArSessionBaselineReporter arSessionBaselineReporter" in home_hud
    assert "FormalArRuntimeBootstrap arRuntimeBootstrap" in home_hud
    assert "FormalXrHandPerchController xrHandPerchController" in home_hud
    assert "FormalCameraModeController cameraModeController" in home_hud
    assert "BBoxVisualToolController bboxVisualToolController" in home_hud
    assert "MagnifierVisualToolController magnifierVisualToolController" in home_hud
    assert "AudioRouteHudLabel" in home_hud
    assert "MicrophoneHudLabel" in home_hud
    assert "MicrophoneDeviceHudLabel" in home_hud
    assert "UplinkHudLabel" in home_hud
    assert "UsingMic" in home_hud
    assert "Uplink " in home_hud
    assert '" nz="' in home_hud
    assert "microphonePublisher.LastNonSilentAudioAgeSeconds" in home_hud
    assert "MicPublishSummary(health)" in home_hud
    assert "health.AudioPublishAttempted ? \"wait\" : \"idle\"" in home_hud
    assert "PlacementHudLabel" in home_hud
    assert "ArHudLabel" in home_hud
    assert "Hand {XrHandHudLabel()}" in home_hud
    assert "XrHandHudLabel" in home_hud
    assert "Camera {CameraHudLabel()}" in home_hud
    assert "CameraHudLabel" in home_hud
    assert "cameraModeController.LastHttpStatus" in home_hud
    assert "cameraModeController.LastPhotoStatus" in home_hud
    assert "VTool {VisualToolsHudLabel()}" in home_hud
    assert "VisualToolsHudLabel" in home_hud
    assert "VisualToolHudPart" in home_hud
    assert "controller.LastRenderStatus" in home_hud
    assert "controller.LastHttpStatus" in home_hud
    assert "controller.LastAssetStatus" in home_hud
    assert "modelPlacementController.LastDiagnosticSummary" in home_hud
    assert "arSessionBaselineReporter.LastStatus" in home_hud
    assert "arRuntimeBootstrap.LastSpatialVisualStatus" in home_hud
    assert "arRuntimeBootstrap.LastPlaneMaterialStatus" in home_hud
    assert "arRuntimeBootstrap.LastTemplateInteractionStatus" in home_hud
    assert "panelImage.raycastTarget = false" in home_hud
    assert "_statusDot.raycastTarget = false" in home_hud
    assert "_statusText.raycastTarget = false" in home_hud
    assert "audioRouteReporter.LastInputRoute" in home_hud
    assert "audioRouteReporter.LastOutputRoute" in home_hud
    assert "audioRouteReporter.LastDetectionSource" in home_hud
    assert "audioRouteReporter.ReportPending" in home_hud
    assert "audioRouteReporter.ReportSuccessCount" in home_hud
    assert "audioRouteReporter.ReportAttemptCount" in home_hud
    assert "AudioRouteManager audioRouteManager" in home_hud
    assert "audioRouteManager.CurrentSnapshot" in home_hud
    assert "audioRouteManager.CurrentPolicy" in home_hud
    assert "audioRouteManager.NativeAvailable" in home_hud
    assert "snapshot.bluetooth_connect_permission" in home_hud
    assert "snapshot.audio_focus" in home_hud
    assert "microphonePublisher.SelectedDevice" in home_hud
    assert "microphonePublisher.AvailableDeviceCount" in home_hud
    assert "microphonePublisher.AvailableDevicesLabel(160)" in home_hud
    assert "microphonePublisher.ConfiguredSampleRate" in home_hud
    assert "microphonePublisher.LastManualDeviceStatus" in home_hud
    assert "microphonePublisher.UplinkStateLabel" in home_hud
    assert "microphonePublisher.LastPublishStage" in home_hud
    assert "microphonePublisher.ActiveAudioSourceKind" in home_hud
    assert "microphonePublisher.AudioReadFrameCount" in home_hud
    assert "microphonePublisher.LastAudioReadChannels" in home_hud
    assert "microphonePublisher.LastAudioReadSampleRate" in home_hud
    assert "microphonePublisher.LastAudioReadPeak" in home_hud
    assert "microphonePublisher.LastAudioReadAgeSeconds" in home_hud
    assert "microphonePublisher.UplinkWatchdogState" in home_hud
    assert "microphonePublisher.LastCaptureFallbackStatus" in home_hud
    assert "microphonePublisher.NativeAudioRecordState" in home_hud
    assert "microphonePublisher.NativeAudioRecordError" in home_hud
    assert "microphonePublisher.NativeAudioRecordSource" in home_hud
    assert "\" nsrc=\"" in home_hud
    assert "microphonePublisher.UplinkWatchdogMicrophoneRecording" in home_hud
    assert "microphonePublisher.UplinkWatchdogRecoveryCount" in home_hud
    assert "microphonePublisher.PublishedRouteVersion" in home_hud
    assert "microphonePublisher.RouteVersion" in home_hud
    assert "VerticalWrapMode.Overflow" in home_hud
    assert "new Vector2(980f, 528f)" in home_hud
    assert "SafeLabel(modelPlacementController.LastDiagnosticSummary + rpc)" in home_hud
    assert "ShortRoute" in home_hud
    assert "ShortRouteSource" in home_hud
    assert "ShortRoutePreference" in home_hud
    assert "menuLoader.LastError" in home_hud
    assert "reconnectSupervisor.ReconnectPending" in home_hud
    assert "startupFlow.LastError" in home_hud
    assert 'Resources.GetBuiltinResource<Font>("LegacyRuntime.ttf")' in home_hud
    assert "Arial.ttf" not in home_hud
    assert "AddComponent<AudioRouteManager>()" not in route_reporter

    assert "var persistentRoot = gameObject" in room_manager
    assert "transform.SetParent(null, true)" in room_manager
    assert "DontDestroyOnLoad(persistentRoot)" in room_manager

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
    assert "A2DP is output-only" in mic
    assert "AudioRouteManager routeManager" in mic
    assert "routeManager.RequestCommunicationMode(true)" in mic
    assert "routeManager.RequestCommunicationMode(false)" in mic
    assert "UnityEngine.Android.Permission.RequestUserPermission" in mic
    assert "android.permission.BLUETOOTH_CONNECT" in mic
    assert "OnLifecycleStateChanged" in mic
    assert "lifecycle_resumed" in mic
    assert "routeManager.OnRoutePolicyChanged += OnAudioRouteChanged" in mic
    assert "RequiresMicRebuild" in mic
    assert "CaptureClass" in mic
    assert "route changed without mic rebuild" in mic
    assert "route version changed during publish without mic rebuild" in mic
    assert "microphoneStartTimeoutSeconds, routeRepublishDebounceSeconds" in mic
    assert "bluetoothScoRouteSettleSeconds = 0.75f" in mic
    assert "bluetoothScoStartTimeoutSeconds = 2f" in mic
    assert "StartupTimeoutSeconds" in mic
    assert "PreStartDelaySeconds" in mic
    assert "scoProbeTimeout" in mic
    assert "scoPreStartSettle" in mic
    assert "capture_route_settle" in mic
    assert "attempt.StartupTimeoutSeconds > 0f" in mic
    assert "RequestFreshTokenReconnect" not in mic
    assert "RequestFreshTokenReconnect" not in route_manager
    assert "Room.Connect" not in route_manager
    assert "policy.Kind == AudioRouteKind.BluetoothSco" in mic
    assert "CyclePreferredDevice" in mic
    assert "ClearPreferredDevice" in mic
    assert "PreferredDevice" in mic
    assert "PublishInProgress" in mic
    assert "LastPublishStage" in mic
    assert "UplinkStateLabel" in mic
    assert "AudioReadFrameCount" in mic
    assert "ActiveAudioSourceKind" in mic
    assert "NativeAudioRecordState" in mic
    assert "NativeAudioRecordError" in mic
    assert "NativeAudioRecordSource" in mic
    assert "_lastNativeAudioRecordState" in mic
    assert "_lastNativeAudioRecordError" in mic
    assert "_lastNativeAudioRecordSource" in mic
    assert "CacheNativeAudioRecordDiagnostics" in mic
    assert "uplinkRuntimeWatchdogEnabled = true" in mic
    assert "UplinkRuntimeWatchdogLoop" in mic
    assert "Microphone.IsRecording" in mic
    assert "LastAudioReadAgeSeconds" in mic
    assert "uplink_watchdog_audio_frames_stale" in mic
    assert "uplink_watchdog_microphone_stopped" in mic
    assert "BuildCaptureAttempts" in mic
    assert "sco_capture_48k_retry" in mic
    assert "bluetooth_sco_capture_48k" in mic
    assert "phone_default_mic_after_sco_failure" in mic
    assert "phone_default_microphone" in mic
    assert "android_audio_record_after_unity_timeout" in mic
    assert "android_audio_record_44100_after_unity_timeout" in mic
    assert "android_audio_record_16000_after_unity_timeout" in mic
    assert "the SDK/FFI rejects PCM frames whose sample rate differs" in mic
    assert "ApplyCaptureRouteOverride" in mic
    assert "RouteOverridePreference" in mic
    assert "AudioRoutePreference.SystemDefault" in mic
    assert "explicit/manual recovery" in mic
    assert "ApplyTemporaryNativePreference(" in mic
    assert "SetPreference(AudioRoutePreference.PhoneMic)" not in mic
    assert "route_override:\" + overrideLabel" in mic
    assert "capture_route_override" in mic
    assert "Prefer system" in mic and "A2DP/BLE output can stay on" in mic
    assert "route change accepted during capture override without republish" in mic
    assert 'string.Equals(_selectedDevice, "phone_default_microphone"' in mic
    assert "LastCaptureFallbackStatus" in mic
    assert "BuildSuccessFallbackStatus" in mic
    assert "source:\" + sourceKind" in mic
    assert "AudioRead freshness is the stronger formal-app signal" in mic
    assert "Headset/route glitches recover by rebuilding only the local mic track" in mic
    assert "QueueRouteRepublish(_activePolicy, reason)" in mic
    assert "StopUplinkWatchdog(reason)" in mic
    assert "pinned LiveKit Unity SDK does not dispose our C# source" in mic
    assert "(source as IDisposable)?.Dispose()" in mic
    assert "preferAndroidAudioRecordOnAndroid = true" in mic
    assert "ShouldPreferAndroidAudioRecordPrimary" in mic
    assert "android_audio_record_primary" in mic
    assert "Unity MicrophoneSource can locally" in mic
    assert "emit AudioRead frames while the remote room still receives no" in mic
    assert "RtcAudioSource.DefaultSampleRate = (uint)targetRate" in mic
    assert "private void OnApplicationFocus(bool hasFocus)" in mic
    assert "ShortExceptionMessage" in mic
    assert "focus_resume" in mic
    assert "focus_resume_during_publish" in mic
    assert "Android may keep the LiveKit room alive while resetting" in mic
    android_pcm_source = (
        SCRIPT_ROOT / "LiveKit" / "AndroidPcmMicrophoneSource.cs"
    ).read_text(encoding="utf-8")
    assert "RtcAudioSourceType.AudioSourceCustom" in android_pcm_source
    assert "RtcAudioSourceType.AudioSourceMicrophone" not in android_pcm_source
    assert "_native.RequestCommunicationMode(false);" in route_manager
    assert "stale communication-device pin" in route_manager
    assert "_forceAndroidAudioRecordVoiceCommunicationNextPublish" in mic
    assert "ShouldPromoteSilentAndroidAudioRecordToVoiceCommunication" in mic
    assert "android_audio_record_voice_communication_after_zero_peak" in mic
    assert "uplink_watchdog_zero_peak_android_audio_record_mic" in mic
    assert "uplink_watchdog_zero_peak_android_audio_record" in mic
    assert "routeManager?.RequestCommunicationMode(false);" in mic
    assert "Room.Connect" not in mic
    assert "OnMicrophoneAudioRead" in mic
    assert "Mathf.Abs(data[i])" not in mic
    assert "_micSource.AudioRead += OnMicrophoneAudioRead" in mic
    assert "source.AudioRead -= OnMicrophoneAudioRead" in mic
    assert "PublishedRouteVersion" in mic
    assert "RouteVersion" in mic
    assert "_selectedDevice" in mic
    assert "LastManualDeviceStatus" in mic
    assert "QueueManualDeviceRepublish" in mic
    assert "mic_device_changed" in mic
    assert "AvailableDevicesLabel" in mic
    assert "microphoneStartTimeoutSeconds = 4f" in mic
    assert "TryGetMicrophonePosition" in mic
    assert "audio_read_timeout" in mic
    assert '_lastPublishStage = "audio_read_timeout"' in mic
    assert "IsHardNativeAudioRecordFailure" in mic
    assert "native_audio_record_failed:" in mic
    assert "ShouldPreserveCaptureStartupError" in mic
    assert "CacheNativeAudioRecordDiagnostics(activeNativeSource)" in mic
    assert "read_error_persistent" in mic
    assert "read_zero_persistent" in mic
    assert "pcm_callback_failed" in mic
    assert "AudioReadFrameCount > audioReadBaseline" in mic
    assert "microphone_start_timeout" in mic
    assert "microphone_start_exception" in mic
    assert "microphone_start_aborted" in mic
    assert "microphone_ready_aborted" in mic
    assert "audio_track_create_failed" in mic
    assert "StopPublishingInner();" in mic
    assert "HealthAggregator?.ReportAudioPublished(false, UnixSeconds(), _lastError);" in mic
    assert "SnapshotRpcHandler" not in flow
    assert "CaptureSnapshotForRpc" not in video
    assert "AsyncGPUReadback.Request" not in video


def test_formal_home_loaders_use_app_http_model_manifest_and_ar_gate() -> None:
    menu_client = HOME_MENU_CLIENT.read_text(encoding="utf-8")
    room_client = ROOM_SETTING_CLIENT.read_text(encoding="utf-8")
    menu_loader = FORMAL_HOME_MENU_LOADER.read_text(encoding="utf-8")
    menu_controller = FORMAL_HOME_MENU_CONTROLLER.read_text(encoding="utf-8")
    tool_controller = FORMAL_HOME_TOOL_CONTROLLER.read_text(encoding="utf-8")
    camera_mode_controller = FORMAL_CAMERA_MODE_CONTROLLER.read_text(encoding="utf-8")
    visual_packet = VISUAL_TOOL_PACKET_BUILDER.read_text(encoding="utf-8")
    visual_http = VISUAL_TOOL_HTTP_CLIENT.read_text(encoding="utf-8")
    bbox_visual = BBOX_VISUAL_TOOL_CONTROLLER.read_text(encoding="utf-8")
    mag_visual = MAGNIFIER_VISUAL_TOOL_CONTROLLER.read_text(encoding="utf-8")
    model_remote = FORMAL_MODEL_REMOTE_CONTROLLER.read_text(encoding="utf-8")
    xrhand_perch = FORMAL_XRHAND_PERCH_CONTROLLER.read_text(encoding="utf-8")
    hand_gesture = HAND_GESTURE_SOURCE.read_text(encoding="utf-8")
    camera_pose_frame = CAMERA_HAND_POSE_FRAME.read_text(encoding="utf-8")
    mediapipe_provider = MEDIAPIPE_CAMERA_HAND_PROVIDER.read_text(encoding="utf-8")
    perch_on_hand = (SCRIPT_ROOT / "Hands" / "PerchOnHand.cs").read_text(encoding="utf-8")
    rpc = (SCRIPT_ROOT / "RPC" / "ParrotRpcHandler.cs").read_text(encoding="utf-8")
    animation = ANIMATION_DRIVER.read_text(encoding="utf-8")
    model_reporter = FORMAL_MODEL_READY_REPORTER.read_text(encoding="utf-8")
    model_placement = FORMAL_MODEL_PLACEMENT_CONTROLLER.read_text(encoding="utf-8")
    ar_reporter = FORMAL_AR_SESSION_BASELINE_REPORTER.read_text(encoding="utf-8")
    ar_bootstrap = FORMAL_AR_RUNTIME_BOOTSTRAP.read_text(encoding="utf-8")
    manifest = MODEL_MANIFEST_DTO.read_text(encoding="utf-8")
    model_driver = MODEL_DRIVER.read_text(encoding="utf-8")
    flow = STARTUP_FLOW.read_text(encoding="utf-8")
    runtime_config = RUNTIME_CONFIG.read_text(encoding="utf-8")
    photo_controller = PHOTO_CONTROLLER.read_text(encoding="utf-8")

    assert "class AppHomeMenuClient" in menu_client
    assert '"/api/app/canvas"' in menu_client
    assert "latency-sensitive in-room control" in menu_client
    assert "AppCanvasSnapshotDto" in menu_client
    assert "AppActionResultDto" in menu_client
    assert "public string layout_kind" in menu_client
    assert "public float generated_at" in menu_client
    assert "public double generated_at" not in menu_client
    assert "public string[] action_endpoints" in menu_client
    assert "AppPersonaOptionDto" in menu_client
    assert "AppLineProfileOptionDto" in menu_client
    assert '"/api/app/personas"' in menu_client
    assert '"/api/app/line-profiles"' in menu_client
    assert '"/api/app/workspace/apply"' in menu_client
    assert '"/api/app/camera/mode"' in menu_client
    assert '"/api/app/awareness"' in menu_client
    assert '"/api/app/xrhand/mode"' in menu_client
    assert "LoadPersonas" in menu_client
    assert "LoadLineProfiles" in menu_client
    assert "ApplyWorkspace" in menu_client
    assert "SetCameraMode" in menu_client
    assert "SetPhotoAwarenessPolicy" in menu_client
    assert "SetXrHandMode" in menu_client
    assert "PostActionJson" in menu_client
    assert "_rejected:" in menu_client
    assert "AppPersonaOptionArrayEnvelope" in menu_client
    assert "AppLineProfileOptionArrayEnvelope" in menu_client
    assert "HasUsableHomePayload" in menu_client
    assert "hasMenuShell" in menu_client
    assert "&& !string.IsNullOrWhiteSpace(active_workspace_id)" in menu_client
    assert "config.appApiUrl" in menu_client
    assert "config.appApiSecret" in menu_client
    assert 'private string appApiBaseUrl = "";' in menu_client
    assert 'private string appApiBaseUrl = "";' in room_client
    assert "device's own localhost" in menu_client
    assert "device's own localhost" in room_client
    assert "http://127.0.0.1:8790" not in menu_client
    assert "http://127.0.0.1:8790" not in room_client

    assert "class FormalHomeMenuLoader" in menu_loader
    assert "menuClient.LoadCanvasSnapshot" in menu_loader
    assert "maxLoadAttempts" in menu_loader
    assert "_loadCoroutine = null" in menu_loader
    assert "startupFlow.MainUiReadyOnce" in menu_loader
    assert "Bind(allowMainReadyCatchUp: false)" in menu_loader
    assert "ReportMenuSnapshotLoaded" in menu_loader
    assert "app_http_canvas_snapshot" in menu_loader
    assert "ReportGateInvalidated(\"menu_snapshot_loaded\")" in menu_loader
    assert "OnSnapshotLoaded?.Invoke(LastSnapshot)" in menu_loader
    assert "OnSnapshotLoadFailed?.Invoke(LastError)" in menu_loader
    assert "LastPersonas" in menu_loader
    assert "LastLineProfiles" in menu_loader
    assert "LastSelectorError" in menu_loader
    assert "LoadSelectorCatalogs" in menu_loader
    assert "menuClient.LoadPersonas" in menu_loader
    assert "menuClient.LoadLineProfiles" in menu_loader
    assert "OnSelectorCatalogLoaded?.Invoke" in menu_loader
    assert "OnSelectorCatalogLoadFailed?.Invoke" in menu_loader
    assert "AppV1SmokeReferenceUiController" not in menu_loader

    assert "class FormalHomeMenuController" in menu_controller
    assert "FormalHomeMenuCanvas" in menu_controller
    assert "FormalHomeToolbar" in menu_controller
    assert "ToolButtonCamera" in menu_controller
    assert "ToolButtonMagnifier" in menu_controller
    assert "ToolButtonBBox" in menu_controller
    assert "ToolButtonCanvasMenu" in menu_controller
    assert "ToolButtonWorkspace" in menu_controller
    assert "ToolButtonSettings" in menu_controller
    assert "AppHomeMenuClient homeMenuClient" in menu_controller
    assert "FormalHomeToolController homeToolController" in menu_controller
    assert "FormalCameraModeController cameraModeController" in menu_controller
    assert "cameraModeController?.SetModeLocal" in menu_controller
    assert "cameraModeController?.MarkHttpPending(nextMode)" in menu_controller
    assert "cameraModeController?.MarkHttpResult(mode, true)" in menu_controller
    assert "cameraModeController?.MarkHttpResult(mode, false" in menu_controller
    assert "FormalCameraModeController _subscribedCameraModeController" in menu_controller
    assert "ResolveCameraModeController" in menu_controller
    assert "SyncCameraModeSubscription" in menu_controller
    assert menu_controller.count("FindObjectOfType<FormalCameraModeController>()") == 1
    assert "OnModeApplyPending += HandleCameraModeApplyPending" in menu_controller
    assert "OnModeApplySucceeded += HandleCameraModeApplySucceeded" in menu_controller
    assert "OnModeApplyFailed += HandleCameraModeApplyFailed" in menu_controller
    assert "NormalizeCameraMode" in menu_controller
    assert "private void HandleCameraModeApplySucceeded" in menu_controller
    camera_success_block = menu_controller[
        menu_controller.index("private void HandleCameraModeApplySucceeded"):
        menu_controller.index("private void HandleCameraModeApplyFailed")
    ]
    assert "_cameraMode = NormalizeCameraMode(mode)" in camera_success_block
    assert "_pendingCameraMode = \"\"" in camera_success_block
    camera_cycle_block = menu_controller[
        menu_controller.index("private void CycleCameraMode"):
        menu_controller.index("private void TogglePhotoAwareness")
    ]
    assert "cameraModeController?.SetModeLocal(nextMode)" not in camera_cycle_block
    assert camera_cycle_block.index("cameraModeController?.MarkHttpPending(nextMode)") < camera_cycle_block.index("StartCoroutine(ApplyCameraModeHttp(nextMode))")
    assert "Camera HTTP pending " in camera_cycle_block
    assert camera_cycle_block.index("if (!string.IsNullOrWhiteSpace(_pendingCameraMode)") < camera_cycle_block.index("string nextMode = NextCameraMode(_cameraMode)")
    assert "string controllerPendingMode = cameraModeController != null ? cameraModeController.PendingMode : \"\"" in camera_cycle_block
    assert "|| !string.IsNullOrWhiteSpace(controllerPendingMode)" in camera_cycle_block
    assert "cameraModeController?.MarkPhotoCaptureStatus" in menu_controller
    assert "BBoxVisualToolController bboxVisualToolController" in menu_controller
    assert "MagnifierVisualToolController magnifierVisualToolController" in menu_controller
    assert "CapturePhotoTool" in menu_controller
    assert "ToggleMagnifierTool" in menu_controller
    assert "ToggleBBoxTool" in menu_controller
    assert "homeToolController.CapturePhoto()" in menu_controller
    assert "homeToolController.ToggleMagnifier()" not in menu_controller
    assert "homeToolController.ToggleBBox()" not in menu_controller
    assert "magnifierVisualToolController.ToggleTool()" in menu_controller
    assert "bboxVisualToolController.ToggleTool()" in menu_controller
    assert "ToolStatusForMenu" in menu_controller
    assert "dev_flag_off" in menu_controller
    assert "MAG after phone stability" in menu_controller
    assert "BOX after phone stability" in menu_controller
    assert "OpenMagnifierPlaceholder" not in menu_controller
    assert "OpenBBoxPlaceholder" not in menu_controller
    assert "TryOpen2DWorkspace" in menu_controller
    assert "openDrawerOnLoad = false" in menu_controller
    assert "SettingsAudioRouteStatus" in menu_controller
    assert "FormalHomeMenuDrawer" in menu_controller
    assert "FormalHomeWorkspaceStrip" in menu_controller
    assert "OnSnapshotLoaded += HandleSnapshotLoaded" in menu_controller
    assert "OnSelectorCatalogLoaded += HandleSelectorCatalogLoaded" in menu_controller
    assert "RenderSnapshot" in menu_controller
    assert "AppCanvasSnapshotDto" in menu_controller
    assert "RenderSelectorRows" in menu_controller
    assert "SelectorPersona" in menu_controller
    assert "SelectorLineProfile" in menu_controller
    assert "SelectorCatalogDegraded" in menu_controller
    assert "FindPersonaLabel" in menu_controller
    assert "FindLineProfileLabel" in menu_controller
    assert "homeMenuClient.ApplyWorkspace(workspaceId" in menu_controller
    assert "ApplyWorkspaceHttp" in menu_controller
    assert "OnWorkspaceSwitchApplied += HandleWorkspaceSwitchApplied" not in menu_controller
    assert "OnWorkspaceSwitchFailed += HandleWorkspaceSwitchFailed" not in menu_controller
    assert "OnCompactControlApplied += HandleCompactControlApplied" not in menu_controller
    assert "OnCompactControlFailed += HandleCompactControlFailed" not in menu_controller
    assert "HandleWorkspaceSwitchApplied" not in menu_controller
    assert "HandleWorkspaceSwitchFailed" not in menu_controller
    assert "HandleCompactControlApplied" not in menu_controller
    assert "HandleCompactControlFailed" not in menu_controller
    try_switch_block = menu_controller[
        menu_controller.index("private void TrySwitchWorkspace"):
        menu_controller.index("private IEnumerator ApplyWorkspaceHttp")
    ]
    assert "Workspace HTTP " in try_switch_block
    assert "_snapshot.active_workspace_id = workspaceId" not in try_switch_block
    assert "WorkspacePolicyLabel" in menu_controller
    assert "CanApplyMenuHttp()" in menu_controller
    assert "CanSendCompactControl()" in menu_controller
    assert "FormalHomeQuickActionStrip" in menu_controller
    assert "QuickCameraMode" in menu_controller
    assert "QuickPhotoAwareness" in menu_controller
    assert "QuickXrHandMode" in menu_controller
    assert "ModelPlacementPlaceButton" in menu_controller
    assert "ARMobileTemplatePlaceButton" in menu_controller
    assert "LoadArMobileTemplateSprite(\"ActivationButtonOpaque\")" in menu_controller
    assert "LoadArMobileTemplateSprite(\"Icon-Cube\")" in menu_controller
    assert "image.raycastTarget = false" in menu_controller
    assert "image.raycastTarget = true" in menu_controller
    assert "iconImage.raycastTarget = false" in menu_controller
    assert "text.raycastTarget = false" in menu_controller
    assert "QuickAudioRouteRefresh" in menu_controller
    assert "MicDeviceCycleButton" in menu_controller
    assert "MicDeviceAutoButton" in menu_controller
    assert "AudioRouteDetector audioRouteDetector" in menu_controller
    assert "AudioRouteManager audioRouteManager" in menu_controller
    assert "AudioRoutePolicyBrainReporter audioRouteReporter" in menu_controller
    assert "MicrophonePublisher microphonePublisher" in menu_controller
    assert "RenderAudioRouteRow" in menu_controller
    assert "AudioRouteStatus" in menu_controller
    assert "AudioRouteStatusLabel" in menu_controller
    assert "MicrophoneStatusLabel" in menu_controller
    assert "CycleMicrophoneDevicePreference" in menu_controller
    assert "ClearMicrophoneDevicePreference" in menu_controller
    assert "microphonePublisher.CyclePreferredDevice" in menu_controller
    assert "microphonePublisher.ClearPreferredDevice" in menu_controller
    assert "MicrophonePreferenceShortLabel" in menu_controller
    assert "RefreshAudioRoutePolicy" in menu_controller
    assert 'audioRouteReporter.RefreshAndReportCurrentPolicy("formal_home_manual_rescan")' in menu_controller
    assert 'audioRouteManager.RefreshCurrentPolicy("formal_home_manual_rescan")' in menu_controller
    assert "modelPlacementController.PlaceAtDefaultPreview()" in menu_controller
    assert "modelPlacementController.CanPlaceNow" in menu_controller
    assert "PlaceModelPreview" in menu_controller
    assert "PlacementShortLabel" in menu_controller
    assert "OnPlacementStateChanged += HandlePlacementStateChanged" in menu_controller
    assert "OnPlacementStateChanged -= HandlePlacementStateChanged" in menu_controller
    assert "audioRouteReporter.ReportPending" in menu_controller
    assert "audioRouteReporter.LastReportError" in menu_controller
    assert "audioRouteReporter.LastDetectionSource" in menu_controller
    assert "AudioRouteSourceLabel" in menu_controller
    assert "AudioRouteShortLabel" in menu_controller
    assert "_pendingCameraMode" in menu_controller
    assert "_pendingAwarenessPolicy" in menu_controller
    assert "_pendingXrHandMode" in menu_controller
    assert "_workspaceApplyPending" in menu_controller
    assert "_audioRouteReportPending" in menu_controller
    assert "homeMenuClient.SetCameraMode(mode" in menu_controller
    assert "homeMenuClient.SetPhotoAwarenessPolicy(policy" in menu_controller
    assert "homeMenuClient.SetXrHandMode(mode" in menu_controller
    assert "Camera HTTP " in menu_controller
    assert "Photo HTTP " in menu_controller
    assert "Hands HTTP " in menu_controller
    assert "PendingOrCurrentLabel" in menu_controller
    assert "NextCameraMode" in menu_controller
    assert "NextXrHandMode" in menu_controller
    assert "AWARE_SILENT" in menu_controller
    assert "UNAWARE_RECORDED" in menu_controller
    assert "PerformRpc" not in menu_controller
    assert 'Resources.GetBuiltinResource<Font>("LegacyRuntime.ttf")' in menu_controller
    assert "Arial.ttf" not in menu_controller
    assert "AppV1SmokeReferenceUiController" not in menu_controller

    assert "class FormalCameraModeController" in camera_mode_controller
    assert "FormalCameraModeCanvas" in camera_mode_controller
    assert "FormalCameraModeOverlay_TransparentWysiwyg" in camera_mode_controller
    assert "FormalCameraModeTinyTopEdge" in camera_mode_controller
    assert "FormalCameraModeTinyBottomEdge" in camera_mode_controller
    assert "CameraGestureRail_Zoom" in camera_mode_controller
    assert "CameraExposureRail" in camera_mode_controller
    assert "CameraProSettingsPanel" in camera_mode_controller
    assert "CameraToolbox_PixelBBoxStamp" in camera_mode_controller
    assert "FormalCameraModeShutterButton" in camera_mode_controller
    assert "SetModeLocal" in camera_mode_controller
    assert "RequestModeApply" in camera_mode_controller
    assert "ApplyModeHttp" in camera_mode_controller
    assert "homeMenuClient.SetCameraMode" in camera_mode_controller
    assert "public event Action<string> OnModeApplyPending" in camera_mode_controller
    assert "public event Action<string> OnModeApplySucceeded" in camera_mode_controller
    assert "public event Action<string, string> OnModeApplyFailed" in camera_mode_controller
    assert "public bool HasPendingHttpRequest => _modeApplyCoroutine != null || !string.IsNullOrWhiteSpace(_pendingMode)" in camera_mode_controller
    assert "OnModeApplyPending?.Invoke(_pendingMode)" in camera_mode_controller
    assert "OnModeApplySucceeded?.Invoke(normalized)" in camera_mode_controller
    assert "OnModeApplyFailed?.Invoke(normalized, error ?? \"\")" in camera_mode_controller
    assert "camera_http_request_already_pending" in camera_mode_controller
    assert "StopCoroutine(_modeApplyCoroutine)" not in camera_mode_controller
    camera_mode_apply_block = camera_mode_controller[
        camera_mode_controller.index("public string RequestModeApply"):
        camera_mode_controller.index("public void MarkHttpPending")
    ]
    assert "SetModeLocal(normalized)" not in camera_mode_apply_block
    assert "if (HasPendingHttpRequest)" in camera_mode_apply_block
    assert camera_mode_apply_block.index("if (HasPendingHttpRequest)") < camera_mode_apply_block.index("MarkHttpPending(normalized)")
    camera_mode_http_block = camera_mode_controller[
        camera_mode_controller.index("private IEnumerator ApplyModeHttp"):
        camera_mode_controller.index("public void MarkPhotoCaptureStatus")
    ]
    assert 'MarkHttpResult(mode, false, "home_menu_client_missing")' in camera_mode_http_block
    assert "MarkHttpResult(mode, false, result.Error)" in camera_mode_http_block
    assert "MarkHttpResult(previousMode, false" not in camera_mode_http_block
    camera_mark_pending_block = camera_mode_controller[
        camera_mode_controller.index("public void MarkHttpPending"):
        camera_mode_controller.index("public void MarkHttpResult")
    ]
    assert "EnsureUi()" in camera_mark_pending_block
    assert "SetVisible(true)" in camera_mark_pending_block
    assert "MarkHttpPending" in camera_mode_controller
    assert "MarkHttpResult" in camera_mode_controller
    assert "CapturePhotoFromCameraMode" in camera_mode_controller
    assert "homeToolController.CapturePhoto()" in camera_mode_controller
    assert '"Ready", () => RequestModeApply("photo_ready")' in camera_mode_controller
    assert '"Preview", () => RequestModeApply("preview")' in camera_mode_controller
    assert '"x", () => RequestModeApply("off")' in camera_mode_controller
    assert '() => SetModeLocal("photo_ready")' not in camera_mode_controller
    assert '() => SetModeLocal("preview")' not in camera_mode_controller
    camera_capture_block = camera_mode_controller[
        camera_mode_controller.index("public string CapturePhotoFromCameraMode"):
        camera_mode_controller.index("public void MarkPhotoCaptureStatus")
    ]
    assert camera_capture_block.index("homeToolController.CapturePhoto()") < camera_capture_block.index("SetModeLocal(\"capture_locked\")")
    assert "SetZoom" in camera_mode_controller
    assert "SetExposure" in camera_mode_controller
    assert "CycleFilter" in camera_mode_controller
    assert "Slider" in camera_mode_controller
    assert '"preview"' in camera_mode_controller
    assert '"photo_ready"' in camera_mode_controller
    assert '"capture_locked"' in camera_mode_controller
    assert "WYSIWYG" in camera_mode_controller
    assert "CameraPreviewFrame" not in camera_mode_controller
    assert "PhotoController photoController" not in camera_mode_controller
    assert "captureSnapshot" not in camera_mode_controller
    assert "CaptureSnapshot" not in camera_mode_controller
    assert "PerformRpc" not in camera_mode_controller
    assert "AppV1SmokeReferenceUiController" not in camera_mode_controller

    assert "class FormalHomeToolController" in tool_controller
    assert "FormalHomeToolCanvas" in tool_controller
    assert "PhotoController photoController" in tool_controller
    assert "FocusController focusController" not in tool_controller
    assert "BBoxController bboxController" not in tool_controller
    assert "EcpEventPublisher ecpEventPublisher" not in tool_controller
    assert "AddComponent<EcpEventPublisher>()" not in tool_controller
    assert "AddComponent<FocusController>()" not in tool_controller
    assert "AddComponent<BBoxController>()" not in tool_controller
    assert "AddComponent<PhotoController>()" in tool_controller
    assert "AnchorFocus" not in tool_controller
    assert "ReleaseFocus" not in tool_controller
    assert "PlaceBBox" not in tool_controller
    assert "RemoveBBox" not in tool_controller
    assert "magnifier_deferred_phone_stability" in tool_controller
    assert "bbox_deferred_phone_stability" in tool_controller
    assert "photoController.CapturePhoto()" in tool_controller
    assert "photo_upload_endpoint_not_phone_safe" in tool_controller
    assert "_statusText.raycastTarget = false" in tool_controller
    assert "!Application.isEditor" in tool_controller
    assert "config.photoUploadUrl" in tool_controller
    assert "config.photoUploadHost" in tool_controller
    assert "TryConfigureUploadEndpoint" in tool_controller
    assert "ConfigureUploadEndpoint" in tool_controller
    assert "PerformRpc" not in tool_controller
    assert "captureSnapshot" not in tool_controller
    assert "CaptureSnapshot" not in tool_controller
    assert "identify_object" not in tool_controller
    assert "AppV1SmokeReferenceUiController" not in tool_controller

    assert "class VisualToolLifecyclePacket" in visual_packet
    assert "VisualToolRegion" in visual_packet
    assert "VisualToolTimebase" in visual_packet
    assert '"preview_start"' in visual_packet
    assert '"drag_update"' in visual_packet
    assert '"resize_update"' in visual_packet
    assert '"confirm"' in visual_packet
    assert '"explicit_send"' in visual_packet
    assert "public const string Hover" not in visual_packet
    assert "public const string SettingsOpen" not in visual_packet
    assert '"screen_normalized"' in visual_packet
    assert '"unity:formal_app"' in visual_packet
    assert '"c4"' not in visual_packet
    assert "public const string C4" not in visual_packet
    assert "GenerateToolId" in visual_packet
    assert "ToJson(VisualToolLifecyclePacket packet)" in visual_packet
    assert "asset_path" in visual_packet
    assert "mime_type" in visual_packet
    object_json_block = visual_packet[
        visual_packet.index("private static string ObjectJson"):
        visual_packet.index("    }\n}", visual_packet.index("private static string ObjectJson"))
    ]
    assert 'StartsWith("{", StringComparison.Ordinal)' in object_json_block
    assert 'StartsWith("[", StringComparison.Ordinal)' not in object_json_block

    assert "class VisualToolHttpClient" in visual_http
    assert '"/api/app/visual-tool/event"' in visual_http
    assert '"/api/app/visual-tool/asset/"' in visual_http
    assert '"X-Parrot-Tool-Id"' in visual_http
    assert '"X-Parrot-Timebase"' in visual_http
    assert '"X-Parrot-Region"' in visual_http
    assert '"X-Parrot-Source-Surface"' in visual_http
    assert '"X-Parrot-Source-Id"' in visual_http
    assert '"X-Parrot-Description"' in visual_http
    assert "AssetDescription(packet)" in visual_http
    assert "config.appApiUrl" in visual_http
    assert "config.appApiSecret" in visual_http
    assert "UploadHandlerRaw" in visual_http
    assert "RequestErrorLabel" in visual_http
    lifecycle_request_error_block = visual_http[
        visual_http.index('LastLifecycleOk = false;'):
        visual_http.index('string text = req.downloadHandler.text ?? "";')
    ]
    assert 'RequestErrorLabel(req, "visual_tool_lifecycle_request_failed")' in lifecycle_request_error_block
    asset_request_error_block = visual_http[
        visual_http.index('LastAssetOk = false;', visual_http.index('if (req.result != UnityWebRequest.Result.Success)', visual_http.index('public IEnumerator UploadAsset'))):
        visual_http.index('string text = req.downloadHandler.text ?? "";', visual_http.index('public IEnumerator UploadAsset'))
    ]
    assert 'RequestErrorLabel(req, "visual_tool_asset_request_failed")' in asset_request_error_block

    assert "class VisualToolControllerBase" in (SCRIPT_ROOT / "VisualTools" / "VisualToolControllerBase.cs").read_text(encoding="utf-8")
    visual_base = (SCRIPT_ROOT / "VisualTools" / "VisualToolControllerBase.cs").read_text(encoding="utf-8")
    assert "visualToolDevEnabled" in visual_base
    assert "visualToolHttpEnabled" in visual_base
    assert "allowLowFrequencyUpdateEvents" in visual_base
    assert "PointerSample" in visual_base
    assert "TryReadPrimaryPointer" in visual_base
    assert "ScreenToNormalizedTopLeft" in visual_base
    assert "ScreenDeltaToNormalizedTopLeft" in visual_base
    assert "EnsureEventSystemForDevCanvas" in visual_base
    assert "using UnityEngine.InputSystem.UI" in visual_base
    ensure_event_system_block = visual_base[
        visual_base.index("protected static void EnsureEventSystemForDevCanvas"):
        visual_base.index("protected static Vector2 ScreenToNormalizedTopLeft")
    ]
    assert "if (EventSystem.current != null) return;" in ensure_event_system_block
    assert "current.GetComponent<StandaloneInputModule>()" not in ensure_event_system_block
    assert "current.gameObject.AddComponent<InputSystemUIInputModule>()" not in ensure_event_system_block
    assert "Destroy(legacy)" not in ensure_event_system_block
    assert "eventSystem.AddComponent<InputSystemUIInputModule>()" in visual_base
    assert "UpdateLocalRegion" in visual_base
    update_region_block = visual_base[
        visual_base.index("public virtual string UpdateLocalRegion"):
        visual_base.index("public virtual string Lock")
    ]
    assert update_region_block.index("if (IsLocked)") < update_region_block.index("CurrentRegion = region.Clamped()")
    assert "string phase = NormalizeUpdatePhase(updatePhase)" in update_region_block
    assert "bool openedFromClosed = !IsOpen" in update_region_block
    assert "return EmitPhase(VisualToolPhases.PreviewStart, PreviewDeliveryPreference)" in update_region_block
    assert update_region_block.index("return EmitPhase(VisualToolPhases.PreviewStart, PreviewDeliveryPreference)") < update_region_block.index("if (allowLowFrequencyUpdateEvents")
    assert "return EmitPhase(phase, PreviewDeliveryPreference)" in update_region_block
    assert 'return SetStatus(ToolKind + "_local_" + phase, true)' in update_region_block
    assert "DwellTick" in visual_base
    assert "ConfirmWithRenderedAsset" in visual_base
    assert "ApplyStablePhaseLocalState(VisualToolPhases.Confirm)" in visual_base
    assert "_interactionGeneration = 1" in visual_base
    assert "_semanticSequence = 1" in visual_base
    assert "BeginNewInteractionGeneration()" in visual_base
    assert "BeginSemanticSequence()" in visual_base
    assert "IsOlderSemanticCompletion" in visual_base
    assert "InvalidatePendingSemanticWork()" in visual_base
    assert "IsStaleInteraction" in visual_base
    assert "ShouldIgnoreStaleCompletion" in visual_base
    assert "SetStaleSemanticStatus" in visual_base
    assert "OnPreviewOpened()" in visual_base
    assert "OnStableInteractionApplied" in visual_base
    assert "OnStableInteractionReleased" in visual_base
    assert "OnToolClosed" in visual_base
    assert "_screenRegionAssetOverlayHideDepth" in visual_base
    assert "BeginScreenRegionAssetOverlayHide" in visual_base
    assert "EndScreenRegionAssetOverlayHide" in visual_base
    assert "SetOverlayVisibleForScreenRegionAsset(true)" in visual_base
    unlock_block = visual_base[
        visual_base.index("public virtual string Unlock"):
        visual_base.index("public virtual string DwellTick")
    ]
    assert unlock_block.index("IsLocked = false") < unlock_block.index("OnStableInteractionReleased")
    confirm_block = visual_base[
        visual_base.index("public virtual string Confirm()"):
        visual_base.index("public virtual string ExplicitSend()")
    ]
    assert "ApplyStablePhaseLocalState(VisualToolPhases.Confirm)" in confirm_block
    assert "IsLocked = true" not in confirm_block
    explicit_block = visual_base[
        visual_base.index("public virtual string ExplicitSend()"):
        visual_base.index("public virtual string ConfirmWithRenderedAsset")
    ]
    assert "ApplyStablePhaseLocalState(VisualToolPhases.ExplicitSend)" in explicit_block
    assert "IsLocked = true" not in explicit_block
    rendered_asset_block = visual_base[
        visual_base.index("public virtual string ConfirmWithRenderedAsset"):
        visual_base.index("public virtual string ConfirmWithScreenRegionAsset")
    ]
    assert rendered_asset_block.index("ApplyStablePhaseLocalState(VisualToolPhases.Confirm)") < rendered_asset_block.index("if (!RuntimeHttpEnabled || !sendHttpLifecycleEvents)")
    assert "long semanticSequence = BeginSemanticSequence()" in rendered_asset_block
    assert "UploadAssetThenLifecycle(packet, imageBytes, mimeType, _interactionGeneration, semanticSequence)" in rendered_asset_block
    cancel_release_block = visual_base[
        visual_base.index("public virtual string Cancel"):
        visual_base.index("protected VisualToolLifecyclePacket BuildPacket")
    ]
    assert "allowStaleCompletion: true" in cancel_release_block
    assert cancel_release_block.index("EmitPhase(") < cancel_release_block.index("InvalidatePendingSemanticWork()")
    assert "ConfirmWithScreenRegionAsset" in visual_base
    assert "ExplicitSendWithScreenRegionAsset" in visual_base
    assert "QueueScreenRegionAssetLifecycle" in visual_base
    assert "ApplyStablePhaseLocalState(phase)" in visual_base
    assert "EmitLifecycleWithAssetStatus" in visual_base
    assert "screen_region_asset_disabled" in visual_base
    assert 'SetStatus(ToolKind + "_screen_region_asset_disabled", false)' not in visual_base
    screen_asset_block = visual_base[
        visual_base.index("protected string QueueScreenRegionAssetLifecycle"):
        visual_base.index("protected struct PointerSample")
    ]
    assert "if (!IsAllowedLifecyclePhase(phase))" in screen_asset_block
    assert screen_asset_block.index("ApplyStablePhaseLocalState(phase)") < screen_asset_block.index("if (!enableScreenRegionAssetCapture)")
    assert screen_asset_block.index("if (!enableScreenRegionAssetCapture)") < screen_asset_block.index("EmitLifecycleWithAssetStatus")
    assert "long semanticSequence = BeginSemanticSequence()" in screen_asset_block
    assert "CaptureScreenRegionAssetThenLifecycle(packet, _interactionGeneration, semanticSequence)" in screen_asset_block
    send_lifecycle_block = visual_base[
        visual_base.index("private IEnumerator SendLifecycle"):
        visual_base.index("private IEnumerator UploadAssetThenLifecycle")
    ]
    assert "int generation" in send_lifecycle_block
    assert "allowStaleCompletion" in send_lifecycle_block
    assert "long semanticSequence" in send_lifecycle_block
    assert "ShouldIgnoreStaleCompletion(packet, generation)" in send_lifecycle_block
    assert "IsOlderSemanticCompletion(semanticSequence)" in send_lifecycle_block
    assert send_lifecycle_block.index("if (!IsOlderSemanticCompletion(semanticSequence))") < send_lifecycle_block.index("SetStaleSemanticStatus(packet)")
    emit_phase_block = visual_base[
        visual_base.index("protected string EmitPhase"):
        visual_base.index("protected string SetStatus")
    ]
    assert "if (!IsAllowedLifecyclePhase(phase))" in emit_phase_block
    assert "RejectUnsupportedLifecyclePhase(phase)" in emit_phase_block
    assert "NormalizeUpdatePhase" in visual_base
    assert "IsAllowedLifecyclePhase" in visual_base
    assert "RejectUnsupportedLifecyclePhase" in visual_base
    upload_lifecycle_block = visual_base[
        visual_base.index("private IEnumerator UploadAssetThenLifecycle"):
        visual_base.index("private IEnumerator CaptureScreenRegionAssetThenLifecycle")
    ]
    assert upload_lifecycle_block.index("if (IsOlderSemanticCompletion(semanticSequence))") < upload_lifecycle_block.index("if (IsStaleInteraction(generation))")
    assert upload_lifecycle_block.index("IsStaleInteraction(generation)") < upload_lifecycle_block.index("httpClient.UploadAsset")
    assert upload_lifecycle_block.index("httpClient.UploadAsset") < upload_lifecycle_block.index("if (IsOlderSemanticCompletion(semanticSequence))", upload_lifecycle_block.index("httpClient.UploadAsset"))
    assert "SetStaleSemanticStatus(packet)" in upload_lifecycle_block
    assert "IsOlderSemanticCompletion(semanticSequence)" in upload_lifecycle_block
    assert upload_lifecycle_block.index("if (!IsOlderSemanticCompletion(semanticSequence))") < upload_lifecycle_block.index("SetStaleSemanticStatus(packet)")
    assert "string.Equals(phase, VisualToolPhases.ExplicitSend" in visual_base
    assert "CaptureScreenRegionAssetThenLifecycle" in visual_base
    assert "WaitForEndOfFrame" in visual_base
    assert "ReadPixels" in visual_base
    assert "EncodeToPNG" in visual_base
    assert "SetOverlayVisibleForScreenRegionAsset" in visual_base
    assert "hideOverlayDuringAssetCapture" in visual_base
    capture_overlay_block = visual_base[
        visual_base.index("private IEnumerator CaptureScreenRegionAssetThenLifecycle"):
        visual_base.index("private bool EnsureOpenForStablePhase")
    ]
    assert capture_overlay_block.index("if (IsOlderSemanticCompletion(semanticSequence))") < capture_overlay_block.index("bool restoreOverlay = BeginScreenRegionAssetOverlayHide()")
    assert "bool restoreOverlay = BeginScreenRegionAssetOverlayHide()" in capture_overlay_block
    assert "EndScreenRegionAssetOverlayHide(restoreOverlay)" in capture_overlay_block
    assert capture_overlay_block.index("yield return new WaitForEndOfFrame()") < capture_overlay_block.index("EndScreenRegionAssetOverlayHide(restoreOverlay)")
    assert "sendLifecycleIfAssetCaptureFails" in visual_base
    assert "sendLifecycleIfAssetUploadFails" in visual_base
    assert "AddMetaField" in visual_base
    assert '"asset_status"' in visual_base
    assert "asset_upload_failed" in visual_base
    assert "yield return SendLifecycle(packet, generation, allowStaleCompletion: false, semanticSequence: semanticSequence)" in visual_base
    assert "UploadAssetThenLifecycle" in visual_base
    assert "LastAssetStatus" in visual_base
    assert "IntentWorkspace" not in visual_base
    assert "Graphiti" not in visual_base
    assert "Blackboard" not in visual_base
    assert "captureSnapshot" not in visual_base
    assert "CaptureSnapshot" not in visual_base
    assert "bbox.placed" not in visual_base
    assert "focus.anchored" not in visual_base

    assert "class BBoxVisualToolController" in bbox_visual
    assert "VisualToolKinds.BBox" in bbox_visual
    assert "formal_home.bbox" in bbox_visual
    assert "BBoxVisualToolDevCanvas" in bbox_visual
    assert "BBoxVisualToolLocalRegion" in bbox_visual
    assert "BBoxInteractionMode" in bbox_visual
    assert "HandlePointerInput" in bbox_visual
    assert "HitTestInteraction" in bbox_visual
    assert "ApplyInteractionDelta" in bbox_visual
    assert "VisualToolPhases.ResizeUpdate" in bbox_visual
    assert "BBoxDevConfirmButton" in bbox_visual
    assert "BBoxDevAssetConfirmButton" in bbox_visual
    assert "BBoxDevExplicitSendButton" in bbox_visual
    assert "ConfirmWithScreenRegionAsset" in bbox_visual
    assert "ExplicitSendWithScreenRegionAsset" in bbox_visual
    assert "SetOverlayVisibleForScreenRegionAsset" in bbox_visual
    assert "emitLockOnPointerRelease" in bbox_visual
    assert "ConfirmAttentionHint => 1.0f" in bbox_visual
    assert "bbox_locked_unlock_required" in bbox_visual
    assert "protected override void OnPreviewOpened()" in bbox_visual
    assert "protected override void OnStableInteractionApplied" in bbox_visual
    assert "protected override void OnStableInteractionReleased" in bbox_visual
    assert "protected override void OnToolClosed" in bbox_visual
    assert "EndLocalPointerGesture()" in bbox_visual
    bbox_update_overlay_block = bbox_visual[
        bbox_visual.index("protected override void UpdateOverlay"):
        bbox_visual.index("private void EnsureOverlay")
    ]
    assert "if (_canvas == null && (!FeatureEnabled || !IsOpen))" in bbox_update_overlay_block
    assert bbox_update_overlay_block.index("if (_canvas == null && (!FeatureEnabled || !IsOpen))") < bbox_update_overlay_block.index("EnsureOverlay()")
    bbox_pointer_block = bbox_visual[
        bbox_visual.index("private void HandlePointerInput"):
        bbox_visual.index("private BBoxInteractionMode HitTestInteraction")
    ]
    assert bbox_pointer_block.index("if (IsLocked)") < bbox_pointer_block.index("IsLocked = false")
    assert "raycastTarget = false" in bbox_visual
    assert "PlaceBBox" not in bbox_visual
    assert "bbox.placed" not in bbox_visual

    assert "class MagnifierVisualToolController" in mag_visual
    assert "VisualToolKinds.Mag" in mag_visual
    assert "formal_home.mag" in mag_visual
    assert "MagnifierVisualToolDevCanvas" in mag_visual
    assert "MagnifierVisualToolLocalLens" in mag_visual
    assert "HandlePointerInput" in mag_visual
    assert "HandleDwellTick" in mag_visual
    assert "if (!emitDwellTicks || _pointerActive || IsLocked)" in mag_visual
    assert "emitDwellTicks" in mag_visual
    assert "SetZoom" in mag_visual
    assert "AdjustZoom" in mag_visual
    assert "MagnifierDevExplicitSendButton" in mag_visual
    assert "MagnifierDevAssetConfirmButton" in mag_visual
    assert "MagnifierDevZoomInButton" in mag_visual
    assert "ConfirmWithScreenRegionAsset" in mag_visual
    assert "ExplicitSendWithScreenRegionAsset" in mag_visual
    assert "SetOverlayVisibleForScreenRegionAsset" in mag_visual
    assert "VisualToolDeliveryPreferences.IntentOnly" in mag_visual
    assert "VisualToolDeliveryPreferences.C3" in mag_visual
    assert "mag_locked_unlock_required" in mag_visual
    assert "protected override void OnPreviewOpened()" in mag_visual
    assert "protected override void OnStableInteractionApplied" in mag_visual
    assert "protected override void OnStableInteractionReleased" in mag_visual
    assert "protected override void OnToolClosed" in mag_visual
    assert "ResetLocalInspectionTiming" in mag_visual
    assert "public override string BeginPreview" not in mag_visual
    mag_update_overlay_block = mag_visual[
        mag_visual.index("protected override void UpdateOverlay"):
        mag_visual.index("private void EnsureOverlay")
    ]
    assert "if (_canvas == null && (!FeatureEnabled || !IsOpen))" in mag_update_overlay_block
    assert mag_update_overlay_block.index("if (_canvas == null && (!FeatureEnabled || !IsOpen))") < mag_update_overlay_block.index("EnsureOverlay()")
    mag_pointer_block = mag_visual[
        mag_visual.index("private void HandlePointerInput"):
        mag_visual.index("private void HandleMouseWheelZoom")
    ]
    assert mag_pointer_block.index("if (IsLocked)") < mag_pointer_block.index("IsLocked = false")
    mag_zoom_block = mag_visual[
        mag_visual.index("public string SetZoom"):
        mag_visual.index("public string AdjustZoom")
    ]
    assert mag_zoom_block.index("if (IsLocked)") < mag_zoom_block.index("zoom = Mathf.Clamp")
    assert "AnchorFocus" not in mag_visual
    assert "focus.anchored" not in mag_visual

    assert "public string photoUploadUrl" in runtime_config
    assert "public string photoUploadHost" in runtime_config
    assert "public int photoUploadPort" in runtime_config
    assert "public bool visualToolDevEnabled" in runtime_config
    assert "public bool visualToolHttpEnabled" in runtime_config
    assert "public string UploadEndpointLabel" in photo_controller
    assert 'brainScheme = "http"' in photo_controller
    assert 'brainScheme = string.Equals(uri.Scheme, Uri.UriSchemeHttps' in photo_controller
    assert 'string url = $"{brainScheme}://{brainHost}:{brainPort}/upload/photo/{photoId}"' in photo_controller
    assert "public bool IsUploadEndpointLoopback" in photo_controller
    assert "public void ConfigureUploadEndpoint" in photo_controller
    assert "public bool TryConfigureUploadEndpoint" in photo_controller
    assert '"X-Parrot-Timebase"' in photo_controller
    assert "BuildUploadTimebaseJson" in photo_controller

    assert "class FormalModelReadyReporter" in model_reporter
    assert "ModelManifestDto.LoadFromResources" in model_reporter
    assert "startupFlow.MainUiReadyOnce" in model_reporter
    assert "ReportModelResolved" in model_reporter
    assert "model_manifest_missing" in model_reporter
    assert "public void ConfigureModelId" in model_driver
    assert "ModelManifestDto.LoadFromResources(EffectiveModelId)" in model_driver
    assert "public void BootstrapNow()" in model_driver
    assert "ResolveOrAttachController(Manifest.controller_type)" in model_driver
    assert "ParrotRegistry.Instance?.Register(Controller)" in model_driver
    assert "ToLowerInvariant()" in manifest

    assert "class FormalModelPlacementController" in model_placement
    assert "using System.Collections;" in model_placement
    assert "This component deliberately owns the first real onGosloPlaced trigger" in model_placement
    assert "FormalMainReadyGate mainReadyGate" in model_placement
    assert "public bool CanPlaceNow" in model_placement
    assert "mainReadyGate.IsReady" in model_placement
    assert "home_gates_wait" in model_placement
    assert "ARRaycastManager arRaycastManager" in model_placement
    assert "TrackableType.PlaneWithinPolygon" in model_placement
    assert "TryResolveArRaycastPose" in model_placement
    assert "public void PlaceAtScreenPoint(Vector2 screenPoint)" in model_placement
    assert "LastPlacementMode" in model_placement
    assert "LastDiagnosticSummary" in model_placement
    assert "fallbackToPreviewWhenArMisses" in model_placement
    assert "fallbackToPreviewWhenArMisses = false" in model_placement
    assert "preferHorizontalPlacementPlanes = true" in model_placement
    assert "minPlacementPlaneUpDot = 0.75f" in model_placement
    assert "forceManifestHeightAfterPlacement = true" in model_placement
    assert "EnhancedTouchSupport.Enable()" in model_placement
    assert "HandleInputSystemTouchPlacementAndSelection" in model_placement
    assert "HandleInputSystemMousePlacementAndSelection" in model_placement
    assert "IsTouchPointerOverUi" in model_placement
    assert "UnityEngine.TouchPhase" in model_placement
    assert "enableDragMove" in model_placement
    assert "minScaleMultiplier = 0.25f" in model_placement
    assert "maxScaleMultiplier = 2f" in model_placement
    assert "demoSpawnAngleRangeDegrees = 45f" in model_placement
    assert "TemplateXriInteractionActive" in model_placement
    assert "disableCustomGesturesWhenTemplateXriActive = true" in model_placement
    assert "public event Action<FormalModelPlacementController> OnPlacementStateChanged" in model_placement
    assert "NotifyPlacementStateChanged()" in model_placement
    assert "ReportTemplateXriStatus" in model_placement
    assert "ConfigureArMobileTemplateXriInteractable" in model_placement
    assert "XRGrabInteractable" in model_placement
    assert "ARTransformer" in model_placement
    assert "grab.distanceCalculationMode = XRBaseInteractable.DistanceCalculationMode.ColliderPosition" in model_placement
    assert "XRBaseInteractable.MovementType.Instantaneous" in model_placement
    assert "InteractableSelectMode.Single" in model_placement
    assert "InteractableFocusMode.Single" in model_placement
    assert "grab.addDefaultGrabTransformers = true" in model_placement
    assert "transformer.objectPlaneTranslationMode = ARTransformer.PlaneTranslationMode.Any" in model_placement
    assert "SyncTemplateTransformerScaleRange(go)" in model_placement
    assert "ARTransformer's min/max are absolute root localScale values" in model_placement
    assert "baseScale * minMultiplier" in model_placement
    assert "baseScale * maxMultiplier" in model_placement
    assert "SyncTemplateTransformerScaleRange(PlacedModel)" in model_placement
    assert "selectionHitboxPaddingMeters" in model_placement
    assert "_templateSelectionHitbox" in model_placement
    assert "EnsureArMobileTemplateCollider(PlacedModel)" in model_placement
    assert "box.isTrigger = false" in model_placement
    assert "collider.Raycast(ray" in model_placement
    assert 'SelectPlacedModel(true, "xri_release")' in model_placement
    assert "SnapPlacedModelBottomToLastSurface" in model_placement
    assert "Keep the visual bottom on the" in model_placement
    assert "RebasePlacedAnimationDrivers()" in model_placement
    assert "RebaseBaseTransformFromCurrent" in (
        SCRIPT_ROOT / "Parrot" / "AnimationDriver.cs"
    ).read_text(encoding="utf-8")
    assert "grab.startingSingleGrabTransformers.Add(transformer)" in model_placement
    assert "grab.AddSingleGrabTransformer(transformer)" in model_placement
    assert "BoxCollider" in model_placement
    assert "ResolveDemoSpawnRotation" in model_placement
    assert "ResolvePlaneTangent" in model_placement
    assert "Vector3.ProjectOnPlane" in model_placement
    assert "Vector3 upright = preferHorizontalPlacementPlanes ? Vector3.up : normal" in model_placement
    assert "model world-upright" in model_placement
    assert "TryMoveSelectedModelOnPlane" in model_placement
    assert "CaptureDragOffset" in model_placement
    assert 'SelectPlacedModel(true, "tap_model")' in model_placement
    assert "ar_raycast_no_horizontal_plane" in model_placement
    assert "startupFlow.OnMainUiReady += HandleMainUiReady" in model_placement
    assert "ClearPlacedModel(reportOutOfView: false)" in model_placement
    assert "public void PlaceAtDefaultPreview()" in model_placement
    assert "public void PlaceAt(Vector3 position, Quaternion rotation, string reason)" in model_placement
    assert "GameObject.Find(\"AssetPreviewStage\")" in model_placement
    assert "Resources.Load<GameObject>(path)" in model_placement
    assert "Resources.Load<UnityEngine.Object>(path)" in model_placement
    assert "TryCreateSpineSkeletonVisual" in model_placement
    assert "Spine.Unity.SkeletonDataAsset" in model_placement
    assert "LastVisualSource" in model_placement
    assert "public void ClearPlacedModel(bool reportOutOfView = true)" in model_placement
    assert 'LastPlacementStatus = "cleared"' in model_placement
    assert "startupFlow?.ReportGosloRemovedFromView()" in model_placement
    assert "startupFlow?.ReportGosloReturnedToView()" in model_placement
    assert "_reportedGosloOutOfView = true" in model_placement
    assert 'LastSelectionStatus = "out_of_view:voice_only"' in model_placement
    assert "FormalPlacedModelWhitebox" in model_placement
    assert "driver.ConfigureModelId(ActiveModelId)" in model_placement
    assert "driver.BootstrapNow()" in model_placement
    assert "ForceManifestHeightAfterPlacement(\"initial\")" in model_placement
    assert "manifestHeightNormalizationPasses = 40" in model_placement
    assert "manifestHeightNormalizationDelaySeconds = 0.1f" in model_placement
    assert "StartHeightNormalizationPasses" in model_placement
    assert "HeightNormalizationPasses" in model_placement
    assert "currentHeight.ToString" in model_placement
    assert ":height=" in model_placement
    assert "_placedBaseScale = PlacedModel.transform.localScale;" in model_placement
    assert "_userScaleOverrideActive" in model_placement
    assert "_heightNormalizedOnce" in model_placement
    assert "_lastHeightNormalizationStatus" in model_placement
    assert "HandleTemplateXriSelectEntered" in model_placement
    assert "if (_heightNormalizedOnce)" in model_placement
    assert "height_wait_xri_select" in model_placement
    assert "stay at importer size on phone" in model_placement
    assert "TryMoveSelectedModelOnPlane" in model_placement
    assert "startupFlow?.ReportGosloPlaced()" in model_placement
    assert "enableTouchPlacementAndSelection" in model_placement
    assert "HandleTouchPlacementAndSelection" in model_placement
    assert "EventSystem.current.IsPointerOverGameObject" in model_placement
    assert "RayIntersectsPlacedModel" in model_placement
    assert "HasSelectedModel" in model_placement
    assert "ScaleSelectedModel" in model_placement
    assert "Input.touchCount >= 2" in model_placement
    assert "ScaleMultiplier" in model_placement
    assert "FormalPlacedModelSelectionRing" in model_placement
    assert "LineRenderer" in model_placement
    assert "PrimitiveType.Cylinder" not in model_placement
    assert "selectionRingColor" in model_placement
    assert "selectionRingWidthMeters" in model_placement
    assert "FormalSelectionRingTransparentWhite" in model_placement
    assert "PlayPlacementGreeting" in model_placement
    assert "SetHeadState(AnimationDriver.HeadState.Tilt)" in model_placement
    assert "SetState(AnimationDriver.BodyState.HeadBob)" in model_placement
    assert 'ApplyCapability("head_bob"' in model_placement
    assert "minecraftStandingBodyPitchWeight = 0f" in animation
    assert "minecraftFlyingBodyPitchWeight = 0f" in animation
    assert "Manual AR hover should flap without folding the body cube forward" in animation
    assert "ResolveMinecraftBodyXRot" in animation
    assert "MinecraftParrotPose.OnShoulder" in animation
    assert "McBodyXRot * Mathf.Clamp(minecraftStandingBodyPitchWeight" in animation
    assert "McBodyXRot * Mathf.Clamp(minecraftFlyingBodyPitchWeight" in animation
    assert "ReportGosloPlaced()" not in model_reporter
    assert "public string LastBrainRpcStatus" in flow
    assert "LastBrainRpcStatus = method + \":ok\"" in flow
    assert "goslo_placed_rpc_failed" in flow
    assert "public void ReportGosloRemovedFromView()" in flow
    assert 'SwitchWorkspace(ActiveConfig.workspace_id, "2d_workspace")' in flow
    assert "public void ReportGosloReturnedToView()" in flow
    assert 'SwitchWorkspace(ActiveConfig.workspace_id, "ar_workspace")' in flow
    assert "RequestDialogueShutdown" not in flow[
        flow.index("public void ReportGosloRemovedFromView()"):
        flow.index("private IEnumerator SwitchWorkspaceRoutine")
    ]

    assert "class FormalModelRemoteController" in model_remote
    assert "using ParrotApp.Config;" in model_remote
    assert "using ParrotApp.Ecp;" in model_remote
    assert "IPointerDownHandler" in model_remote
    assert "IDragHandler" in model_remote
    assert "IPointerUpHandler" in model_remote
    assert "FormalModelRemoteCanvas" in model_remote
    assert "placementController.HasPlacedModel" in model_remote
    assert "placementController.HasSelectedModel" in model_remote
    assert "waiting_selected_model" in model_remote
    assert "placementController.PlacedModel" in model_remote
    assert "OnPlacementStateChanged += HandlePlacementStateChanged" in model_remote
    assert "OnPlacementStateChanged -= HandlePlacementStateChanged" in model_remote
    assert 'LastRemoteStatus = "idle";' in model_remote
    assert "CurrentLiftInput" in model_remote
    assert "FormalModelLiftPad" in model_remote
    assert "new Vector2(417f, 417f)" in model_remote
    assert model_remote.count("new Vector2(417f, 417f)") >= 2
    assert "new Vector2(138f, 138f)" in model_remote
    assert "JoystickPadColor" in model_remote
    assert "JoystickKnobColor" in model_remote
    assert "GetJoystickCircleSprite" in model_remote
    assert "Sprite.Create" in model_remote
    assert "JoystickAxis.Vertical" in model_remote
    assert "SetLiftInput" in model_remote
    assert "ApplyModelFlight" in model_remote
    assert "fallbackFlightHorizontalSpeedMetersPerSecond = 0.4f" in model_remote
    assert "fallbackFlightVerticalSpeedMetersPerSecond = 0.5f" in model_remote
    assert "fallbackFlightVerticalSpeedMetersPerSecond" in model_remote
    assert "remoteFlightMaxHeightMeters" in model_remote
    assert "experimentalBirdFlightEnabled" in model_remote
    assert "randomizeRemoteFlightStyle" in model_remote
    assert "RemoteFlightStyle" in model_remote
    assert "ShortFlutter" in model_remote
    assert "ShortGlide" in model_remote
    assert "AnimationCurve" in model_remote
    assert "remoteFlightFlutterCurve.Evaluate" in model_remote
    assert "remoteFlightGlideCurve.Evaluate" in model_remote
    assert "Mathf.PerlinNoise" in model_remote
    assert "Vector3.SmoothDamp" in model_remote
    assert "liftInput < -0.05f && _remoteFlightVelocity.y > desiredVelocity.y" in model_remote
    assert "LiftJoystickDirectionDeadZone" in model_remote
    assert ": input.y;" in model_remote
    assert "Mathf.Sign(input.y) * input.magnitude" not in model_remote
    assert "input * (_radius * 0.68f)" in model_remote
    assert "new Vector2(0f, lift *" not in model_remote
    assert "SetState(AnimationDriver.BodyState.Fly)" in model_remote
    assert "EndRemoteFlight(landed: true" in model_remote
    assert "SetState(landed && continueWalking" in model_remote
    assert "LifecycleHeartbeatPublisher.Instance?.ReportActiveCommand" in model_remote
    assert "LifecycleHeartbeatPublisher.Instance?.ClearActiveCommand" in model_remote
    assert "LifecycleHeartbeatPublisher.Instance?.ReportBodyState" in model_remote
    assert '"local_remote_"' in model_remote
    assert "new[] { BodyLock }" in model_remote
    assert 'PublishRemoteBodyState("flying")' in model_remote
    assert 'PublishRemoteBodyState("walking")' in model_remote
    assert 'PublishRemoteBodyState("idle")' in model_remote
    assert "SetAnimatorBoolIfExists" in model_remote
    assert "AnimatorControllerParameterType.Bool" in model_remote
    assert "localFromCenter" in model_remote
    assert "ResolveCameraRelativePlanarInput(input)" in model_remote
    assert "WalkOnPlane(worldInput, deltaTime)" in model_remote
    assert "ResolveMotionFacingRotation(planar, animationDriver)" in model_remote
    assert "new Vector3(input.x, 0f, input.y)" in model_remote
    assert "ApplyCapability(\"spine_walk\"" in model_remote
    assert "ParrotRegistry.Instance.Resolve(modelId)" in model_remote
    assert "fallback_translate:camera_relative" in model_remote
    assert "CallBrainRpc" not in model_remote
    assert "PerformRpc" not in model_remote
    assert "AppV1SmokeReferenceUiController" not in model_remote
    assert 'Resources.GetBuiltinResource<Font>("LegacyRuntime.ttf")' in model_remote

    assert "class FormalXrHandPerchController" in xrhand_perch
    assert "using ParrotApp.Hands;" in xrhand_perch
    assert "using UnityEngine.UI;" in xrhand_perch
    assert "FormalMainReadyGate mainReadyGate" in xrhand_perch
    assert "FormalModelPlacementController placementController" in xrhand_perch
    assert "HandGestureSource handGestureSource" in xrhand_perch
    assert "PerchOnHand" in xrhand_perch
    assert "RealXrHandsCompiled" in xrhand_perch
    assert "UNITY_XR_HANDS" in xrhand_perch
    assert "startupFlow.MainUiReadyOnce" in xrhand_perch
    assert "mainReadyGate.IsReady" in xrhand_perch
    assert "placementController.HasPlacedModel" in xrhand_perch
    assert "model_perch_unsupported" in xrhand_perch
    assert "model_no_animation_driver" in xrhand_perch
    assert "SupportsPerch" in xrhand_perch
    assert "AnimationDriver" in xrhand_perch
    assert "EnsureGestureSource();" in xrhand_perch
    assert 'WithTracking("home_gates_wait:" + ShortReason(mainReadyGate.LastMissingGates))' in xrhand_perch
    assert 'WithTracking("waiting_placed_model")' in xrhand_perch
    assert 'Debug.Log("[FormalXrHandPerch] " + LastXrHandStatus)' in xrhand_perch
    assert "xrhand_debug_only_package_missing" in xrhand_perch
    assert "camera_cv_owner_mounted_waiting_tracking" in xrhand_perch
    assert "camera_cv_tracking_active_perch_owner_mounted" in xrhand_perch
    assert "xrhand_owner_mounted_waiting_tracking" in xrhand_perch
    assert "xrhand_tracking_active_perch_owner_mounted" in xrhand_perch
    assert "showRuntimeDiagnostics = true" in xrhand_perch
    assert "ShouldShowDiagnosticOverlay" in xrhand_perch
    assert "startupFlow.MainUiReadyOnce" in xrhand_perch
    assert "FormalXrHandDiagnosticsCanvas" in xrhand_perch
    assert "FormalXrHandDiagnosticsText" in xrhand_perch
    assert "BuildDiagnosticText" in xrhand_perch
    assert "diagnosticPanelTopRightOffset" in xrhand_perch
    assert "TextAnchor.UpperLeft" in xrhand_perch
    assert "HorizontalWrapMode.Wrap" in xrhand_perch
    assert "VerticalWrapMode.Truncate" in xrhand_perch
    assert "resizeTextForBestFit = true" in xrhand_perch
    assert "native missing: libc++_shared.so" in xrhand_perch
    assert "CompactDiagnostic(tracking)" in xrhand_perch
    assert "handGestureSource.LastGestureDebugSummary" in xrhand_perch
    assert "_mountedPerch.LastPerchLifecycle" in xrhand_perch
    assert "_mountedPerch.LastPerchStatus" in xrhand_perch
    assert "_mountedPerch != null && _mountedPerch != perch" in xrhand_perch
    assert "DebugFireBranchGesture" in xrhand_perch
    assert "CallBrainRpc" not in xrhand_perch
    assert "PerformRpc" not in xrhand_perch
    assert "AppV1SmokeReferenceUiController" not in xrhand_perch

    assert "class HandGestureSource" in hand_gesture
    assert "TrackingMode { Auto, CameraCv, XrHands, DebugOnly }" in hand_gesture
    assert "MediaPipeCameraHandPoseProvider cameraPoseProvider" in hand_gesture
    assert "ApplyCameraHandPose(CameraHandPoseFrame frame)" in hand_gesture
    assert "DetectGesture(CameraHandPoseFrame frame" in hand_gesture
    assert "RealCameraCvCompiled" in hand_gesture
    assert "LastGestureConfidence" in hand_gesture
    assert "LastGestureDebugSummary" in hand_gesture
    assert "LastGestureRejectReason" in hand_gesture
    assert "DebugSummary" in hand_gesture
    assert "TrackingStatus" in hand_gesture
    assert "ResolveFingerGesture" in hand_gesture
    assert "ResolveBranchRejectReason" in hand_gesture
    assert "index_not_horizontal" in hand_gesture
    assert "confidence_low" in hand_gesture
    assert "bends=" in hand_gesture
    assert '"[HandGestureSource] "' in hand_gesture
    assert "camera_cv_provider_created" in hand_gesture
    assert "camera_cv_provider_subscribed" in hand_gesture

    assert "struct CameraHandPoseFrame" in camera_pose_frame
    assert "HandPerchPose PerchPose" in camera_pose_frame
    assert "IndexIntermediate" in camera_pose_frame
    assert "IndexDistal" in camera_pose_frame

    assert "class MediaPipeCameraHandPoseProvider" in mediapipe_provider
    assert "UNITY_MEDIAPIPE && UNITY_AR_FOUNDATION" in mediapipe_provider
    assert "HandLandmarker.CreateFromOptions" in mediapipe_provider
    assert "modelAssetBuffer: handLandmarkerModel.bytes" in mediapipe_provider
    assert "preferGpuDelegateOnMobile = false" in mediapipe_provider
    assert "gpu_delegate_failed_fallback_cpu" in mediapipe_provider
    assert "mediapipe_hand_landmarker_ready_cpu_fallback" in mediapipe_provider
    assert "ARCameraManager" in mediapipe_provider
    assert "TryAcquireLatestCpuImage" in mediapipe_provider
    assert "TryDetectForVideo" in mediapipe_provider
    assert "bindRetryIntervalSeconds" in mediapipe_provider
    assert 'CallStatic("loadLibrary", "c++_shared")' in mediapipe_provider
    assert 'CallStatic("loadLibrary", "mediapipe_jni")' in mediapipe_provider
    assert "PreloadAndroidNativeLibraries" in mediapipe_provider
    assert "mediapipe_native_unavailable" in mediapipe_provider
    assert "_landmarkerInitBlocked" in mediapipe_provider
    assert "assumedIndexFingerLengthMeters" in mediapipe_provider
    assert "worldLandmarkDepthBlend" in mediapipe_provider
    assert "EstimateDepth" in mediapipe_provider
    assert "ResolveWorldLandmarks" in mediapipe_provider
    assert "AddDepthSample" in mediapipe_provider
    assert "ResolvePhysicalLengthMeters" in mediapipe_provider
    assert "samples=" in mediapipe_provider
    assert "compensateCameraImageAspectToScreen" in mediapipe_provider
    assert "ToScreenViewport" in mediapipe_provider
    assert "LogPoseDiagnosticIfNeeded" in mediapipe_provider
    assert "Resources.Load<TextAsset>(resourcesModelPath)" in mediapipe_provider
    assert '"MediaPipe/hand_landmarker"' in mediapipe_provider
    assert "cpu_image_first_frame" in mediapipe_provider
    assert "first_hand depth=" in mediapipe_provider
    assert 'PublishLost("mediapipe_detect_failed:" + ShortReason(ex.Message))' in mediapipe_provider
    assert ANDROID_LIBCXX_SHARED.exists()
    assert ANDROID_LIBCXX_SHARED.stat().st_size > 1_000_000

    assert "TryRequestReturnToView" in perch_on_hand
    assert "HandGestureSource _subscribedHandTracker" in perch_on_hand
    assert "LastPerchStatus" in perch_on_hand
    assert "LastPerchLifecycle" in perch_on_hand
    assert "LastPerchRejectReason" in perch_on_hand
    assert "SetPerchStatus" in perch_on_hand
    assert "ResolveReferences(force: true)" in perch_on_hand
    assert "GetComponentInChildren<AnimationDriver>(true)" in perch_on_hand
    assert "_subscribedHandTracker.OnGestureSnapshot -= OnGesture" in perch_on_hand
    assert "ResolveFootAnchor(force: true)" in perch_on_hand
    assert "ResolveMotionFacingRotation(pose.Rotation)" in perch_on_hand
    assert "ResolveMotionFacingRotation(tangent.normalized, Vector3.up)" in perch_on_hand
    assert "ResolveMotionForward(targetRotation)" in perch_on_hand
    assert "animDriver.ResolveMotionFacingRotation(visualForwardRotation)" in perch_on_hand
    assert "ScaleLocalOffsetForCurrentRoot(_resolvedFootAnchorLocalOffset)" in perch_on_hand
    assert "ResolveFingerGripPosition(pose)" in perch_on_hand
    assert "ResolveFingerSurfaceNormal" in perch_on_hand
    assert "StabilizeCameraCvRootPosition(pose, rootPosition)" in perch_on_hand
    assert "ClampCameraCvRootPosition" in perch_on_hand
    assert "PredictCameraCvRootPosition" in perch_on_hand
    assert "cameraCvLeadSeconds" in perch_on_hand
    assert "cameraCvAllowedBelowStartMeters" in perch_on_hand
    assert "camera_cv_target" in perch_on_hand
    assert "tracking_lost_hold_on_hand" in perch_on_hand
    assert 'ReportBodyState("flying")' in perch_on_hand
    assert 'ReportBodyState("perched_on_hand")' in perch_on_hand
    assert 'ReportBodyState("idle")' in perch_on_hand
    assert "ResolveReturnToViewPosition" in perch_on_hand
    assert "PlayHeadTiltOnce()" in perch_on_hand
    assert "public void PlayHeadTiltOnce()" in animation
    assert "_headTiltOneShot" in animation
    assert 'RegisterRpcMethod("returnToView", HandleReturnToView)' in rpc
    assert "HandleReturnToView" in rpc

    assert "class FormalArSessionBaselineReporter" in ar_reporter
    assert "FormalArRuntimeBootstrap arRuntimeBootstrap" in ar_reporter
    assert "yield return arRuntimeBootstrap.EnsureArRuntimeReady()" in ar_reporter
    assert "startupFlow.MainUiReadyOnce" in ar_reporter
    assert "ReportArSessionBaselineClean" in ar_reporter
    assert "ARSessionState.SessionTracking" in ar_reporter
    assert "ar_session_waiting" in ar_reporter
    assert "mobile_ar_session_not_mounted" in ar_reporter
    assert "yield return null;" in ar_reporter
    assert "_checkCoroutine = null;" in ar_reporter
    assert "ARSessionState.Ready" not in ar_reporter
    assert "ARSessionState.SessionInitializing" not in ar_reporter
    assert "ReportGosloPlaced" not in ar_reporter
    assert "CallBrainRpc" not in ar_reporter

    assert "class FormalArRuntimeBootstrap" in ar_bootstrap
    assert "UNITY_AR_FOUNDATION" in ar_bootstrap
    assert "using Unity.XR.CoreUtils" in ar_bootstrap
    assert "mountXrOriginAndPlacementManagers" in ar_bootstrap
    assert "XrOriginMounted" in ar_bootstrap
    assert "PlacementManagersMounted" in ar_bootstrap
    assert "EnsureXrOrigin" in ar_bootstrap
    assert "EnsurePlacementManagers" in ar_bootstrap
    assert "AddComponent<XROrigin>()" in ar_bootstrap
    assert "origin.RequestedTrackingOriginMode = XROrigin.TrackingOriginMode.Device" in ar_bootstrap
    assert "origin.CameraYOffset = 0f" in ar_bootstrap
    assert "AddComponent<ARRaycastManager>()" in ar_bootstrap
    assert "AddComponent<ARPlaneManager>()" in ar_bootstrap
    assert "SpatialVisualsMounted" in ar_bootstrap
    assert "mountPlaneAndPointCloudVisuals" in ar_bootstrap
    assert "ARMobileTemplate/Prefabs/ARFeatheredPlane" in ar_bootstrap
    assert "ARMobileTemplate/XRIStarterAssets/XRI Default Input Actions" in ar_bootstrap
    assert "ARMobileTemplate/XRIStarterAssets/Screen Space Ray Interactor" in ar_bootstrap
    assert "InputActionManager" in ar_bootstrap
    assert "EnsureTemplateEventSystem" in ar_bootstrap
    assert "XRUIInputModule" in ar_bootstrap
    assert "InputSystemUIInputModule" in ar_bootstrap
    assert "AssignTemplateUiActions" in ar_bootstrap
    assert 'asset.FindActionMap("XRI UI", throwIfNotFound: false)' in ar_bootstrap
    assert 'map.FindAction(actionName, throwIfNotFound: false)' in ar_bootstrap
    assert "xrModule.enableXRInput = true" in ar_bootstrap
    assert "xrModule.enableTouchInput = true" in ar_bootstrap
    assert "xrModule.trackedDeviceDragThresholdMultiplier = 2f" in ar_bootstrap
    assert "inputSystemUiModule.enabled = false" in ar_bootstrap
    assert "ScreenSpaceRayPoseDriver" in ar_bootstrap
    assert "XRScreenSpaceController" in ar_bootstrap
    assert "XRRayInteractor" in ar_bootstrap
    assert "ObjectSpawner" in ar_bootstrap
    assert "ARInteractorSpawnTrigger" in ar_bootstrap
    assert "_templateSpawnTrigger.requireHorizontalUpSurface = true" in ar_bootstrap
    assert "placement.ReportTemplateXriStatus(LastTemplateInteractionStatus)" in ar_bootstrap
    assert 'GameObject.Find("FormalARMobileTemplateObjectSpawner")' in ar_bootstrap
    assert "_templateObjectSpawner == null || _templateObjectSpawner.gameObject != spawnerObject" in ar_bootstrap
    assert "_templateSpawnTrigger == null || _templateSpawnTrigger.gameObject != spawnerObject" in ar_bootstrap
    assert "SpawnTriggerType.SelectAttempt" in ar_bootstrap
    assert "spawnAsChildren = true" in ar_bootstrap
    assert "_templateObjectSpawner.enabled = true" in ar_bootstrap
    assert "_templateSpawnTrigger.enabled = true" in ar_bootstrap
    assert "var parent = origin != null ? origin.transform : transform" in ar_bootstrap
    assert "_templateSpawnProxy.transform.SetParent(parent, false)" in ar_bootstrap
    assert '"xri_template input=" + inputReady + " ui=" + uiReady' in ar_bootstrap
    assert "placement.PlaceAt(position, rotation, \"ar_mobile_template_object_spawner\")" in ar_bootstrap
    assert "ConfigureArMobileTemplatePlane" in ar_bootstrap
    assert "planeManager.planePrefab = prefab" in ar_bootstrap
    assert "planeManager.requestedDetectionMode = (PlaneDetectionMode)(-1)" in ar_bootstrap
    assert "showArMobileTemplatePlaneSurfaces = true" in ar_bootstrap
    assert "ARFeatheredPlaneMeshVisualizerCompanion" in ar_bootstrap
    assert "LastPlaneMaterialStatus" in ar_bootstrap
    assert "RefreshPlaneMaterialStatus" in ar_bootstrap
    assert "planesChanged += HandlePlanesChanged" in ar_bootstrap
    assert "visualizeSurfaces = showArMobileTemplatePlaneSurfaces" in ar_bootstrap
    assert "FormalARPlaneVisual_" not in ar_bootstrap
    assert "FormalARPointDot" not in ar_bootstrap
    assert "pointCloud.positions.HasValue" not in ar_bootstrap
    assert "EnsureTrackedPoseDriver" in ar_bootstrap
    assert "AddComponent<TrackedPoseDriver>()" in ar_bootstrap
    assert '"<HandheldARInputDevice>/devicePosition"' in ar_bootstrap
    assert '"<HandheldARInputDevice>/deviceRotation"' in ar_bootstrap
    assert "bootstrapOnAwake = false" in ar_bootstrap
    assert "if (bootstrapOnAwake)" in ar_bootstrap
    assert "XRGeneralSettings.Instance" in ar_bootstrap
    assert "InitializeLoader()" in ar_bootstrap
    assert "StartSubsystems()" in ar_bootstrap
    assert "StopSubsystems()" in ar_bootstrap
    assert ar_bootstrap.index("manager.StopSubsystems();") < ar_bootstrap.index("manager.DeinitializeLoader();")
    assert "skipXrLifecycleInEditor = true" in ar_bootstrap
    assert "ARSession" in ar_bootstrap
    assert "ARCameraManager" in ar_bootstrap
    assert "ARCameraBackground" in ar_bootstrap
    assert "EnsureArRuntime" in ar_bootstrap
    assert "ARInputManager" in ar_bootstrap


def test_smoke_scene_builder_mounts_reference_ui_and_wires_existing_tools() -> None:
    text = SMOKE_BUILDER.read_text(encoding="utf-8")
    reference_ui = SMOKE_REFERENCE_UI.read_text(encoding="utf-8")
    lifecycle_forcer = SMOKE_LIFECYCLE_FORCER.read_text(encoding="utf-8")

    assert "using ParrotApp.UI;" in text
    assert "AddComponent<AppV1SmokeReferenceUiController>()" in text
    assert "AddComponent<AppStartupFlowController>()" in text
    assert "AddComponent<LiveKitTokenMintClient>()" in text
    assert "ConfigureRoomManagerForMint" in text
    assert 'SetBool(roomManager, "autoConnectOnStart", false)' in text
    assert 'SetBool(roomManager, "allowEditorTokenFile", false)' in text
    assert "Upgrade Current A2 Smoke Scene" in text
    assert "UpgradeCurrentSmokeScene" in text
    assert "FindOrCreateRoot(\"AppV1SmokeReferenceUI\")" in text
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
    assert reference_ui.startswith("#if UNITY_EDITOR")
    assert lifecycle_forcer.startswith("#if UNITY_EDITOR")
    assert "homepage reference extraction only" in reference_ui
    assert "Smoke-scene-only helper" in lifecycle_forcer


def test_parrot_joystick_uses_existing_parrot_controller_boundary() -> None:
    controller = PARROT_CONTROLLER.read_text(encoding="utf-8")
    animation = ANIMATION_DRIVER.read_text(encoding="utf-8")

    assert "public void WalkOnPlane(Vector2 input, float deltaTime)" in controller
    assert "public void EndPlaneWalk()" in controller
    assert "public void ReturnToPlaneWalkHome()" in controller
    assert "does not create a Brain" in controller
    assert "BodyState.Walk" in controller
    assert "motionFacingYawOffsetDegrees = 180f" in controller
    assert "ResolveMotionFacingRotation(direction, Vector3.up)" in controller

    assert "WalkOnPlane(Vector2 input" in animation
    assert "motionFacingYawOffsetDegrees = 180f" in animation
    assert "ResolveMotionFacingRotation(Vector3 direction, Vector3 up)" in animation
    assert "ResolveMotionFacingRotation(Quaternion visualForwardRotation)" in animation
    assert "ResolveMotionForward(Quaternion rootRotation)" in animation
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
    assert "NormalizeMintEndpoint(config.mintUrl)" in text
    assert 'endpoint.EndsWith("/mint"' in text
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
    assert config["appApiUrl"].startswith("http://YOUR_CASTLE_IP:")
    assert config["appApiSecret"] == "dev-only-same-as-PARROT_APP_MONITOR_SECRET-when-enabled"
    assert config["orchestratorUrl"].endswith(":7890")
    assert config["orchestratorUrl"].startswith("http://YOUR_CASTLE_IP:")
    assert config["orchestratorSecret"] == "dev-only-same-as-PARROT_ORCH_SECRET"
    assert config["photoUploadUrl"].endswith(":7889")


def test_android_microphone_permission_uses_runtime_permission_gate() -> None:
    permission_util = ANDROID_RUNTIME_PERMISSIONS.read_text(encoding="utf-8")
    startup = STARTUP_FLOW.read_text(encoding="utf-8")
    publisher = (SCRIPT_ROOT / "LiveKit" / "MicrophonePublisher.cs").read_text(encoding="utf-8")
    route_manager = (SCRIPT_ROOT / "LiveKit" / "AudioRouteManager.cs").read_text(encoding="utf-8")
    android_pcm = (SCRIPT_ROOT / "LiveKit" / "AndroidPcmMicrophoneSource.cs").read_text(encoding="utf-8")

    assert 'RecordAudio = "android.permission.RECORD_AUDIO"' in permission_util
    assert "UnityEngine.Android.Permission.RequestUserPermission(RecordAudio, callbacks)" in permission_util
    assert "UnityEngine.Android.Permission.HasUserAuthorizedPermission(RecordAudio)" in permission_util
    assert "MicrophonePermissionState" in permission_util
    assert "|| Application.HasUserAuthorization(UserAuthorization.Microphone)" not in permission_util
    assert "RequestMicrophonePermission" in startup
    assert "HasMicrophonePermission" in startup
    assert "MicrophonePermissionState" in startup
    assert "RequestMicrophonePermission" in publisher
    assert "HasMicrophonePermission" in publisher
    assert "MicrophonePermissionState" in publisher
    assert "HasMicrophonePermission" in route_manager
    assert "HasMicrophonePermission" in android_pcm


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
    assert not (SCRIPT_ROOT / "UI" / "AppV1SmokeReferenceUiController.cs").exists()
    assert SMOKE_REFERENCE_UI.is_file()
    assert (PARROT_APP / "Resources" / "parrot_models").is_dir()
    assert (PARROT_APP / "Resources" / "Models").is_dir()
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
