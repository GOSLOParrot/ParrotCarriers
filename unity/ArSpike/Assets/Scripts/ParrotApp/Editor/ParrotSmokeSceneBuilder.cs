#if UNITY_EDITOR
using System.IO;
using ParrotApp.Attention;
using ParrotApp.Config;
using ParrotApp.Ecp;
using ParrotApp.Hands;
using ParrotApp.Lifecycle;
using ParrotApp.LiveKit;
using ParrotApp.Parrot;
using ParrotApp.Photo;
using ParrotApp.UI;
using UnityEditor;
using UnityEditor.SceneManagement;
using UnityEngine;

namespace ParrotApp.EditorTools
{
    /// <summary>
    /// Sprint4 Phase 4 W3.A.2 — one-click smoke scene builder.
    /// Tools / Parrot / Build A2 Smoke Scene
    ///
    /// 修订（NullReferenceException 修复）：
    /// 不再在 Editor 构建期直接调 AppLifecycleManager 的状态推进方法
    /// （Awake 未运行，HealthAggregator 为 null）。改为在场景里添加一个
    /// <see cref="LifecycleSmokeForcer"/> MonoBehaviour，它在 Start() 里
    /// （Awake 之后）推生命周期状态机到 Connected，让
    /// LifecycleHeartbeatPublisher 的 chokepoint 不挡心跳。
    /// </summary>
    public static class ParrotSmokeSceneBuilder
    {
        private const string GlbAssetPath = "Assets/Models/GOSLO.glb";
        private const string MenuPath = "Tools/Parrot/Build A2 Smoke Scene";
        private const string UpgradeMenuPath = "Tools/Parrot/Upgrade Current A2 Smoke Scene";
        private const string ToolDrawerWoodSpritePath = "Assets/UI/ParrotApp/ToolCabinet/ToolDrawer_Wood_Menu1.png";
        private const string ToolButtonWoodSpritePath = "Assets/UI/ParrotApp/ToolCabinet/ToolButton_Wood_Front.png";
        private const string PaperNoteSmallSpritePath = "Assets/UI/ParrotApp/Notifications/PaperNote_Blank_New.png";
        private const string PaperNoteFilledSpritePath = "Assets/UI/ParrotApp/Notifications/PaperNote_Filled_Old.png";
        private const string NekoClawSpritePath = "Assets/UI/ParrotApp/Notifications/NekoClaw_Cutout.png";

        [MenuItem(MenuPath)]
        public static void BuildSmokeScene()
        {
            if (!File.Exists(GlbAssetPath))
            {
                EditorUtility.DisplayDialog(
                    "GOSLO.glb not found",
                    $"Expected at {GlbAssetPath}.\n\nRun the asset copy step first.",
                    "OK");
                return;
            }

            var glbAsset = AssetDatabase.LoadAssetAtPath<GameObject>(GlbAssetPath);
            if (glbAsset == null)
            {
                EditorUtility.DisplayDialog(
                    "GOSLO.glb not imported",
                    "Asset exists but Unity hasn't imported it as a GameObject.\n\n" +
                    "Make sure com.unity.cloud.gltfast is installed, then right-click\n" +
                    "GOSLO.glb in Project window and choose Reimport.",
                    "OK");
                return;
            }

            // ── New scene ──────────────────────────────────────────────────
            EditorSceneManager.NewScene(NewSceneSetup.DefaultGameObjects, NewSceneMode.Single);

            var cam = Camera.main;
            if (cam != null)
            {
                cam.transform.position = new Vector3(0f, 1.4f, -1.5f);
                cam.transform.rotation = Quaternion.Euler(8f, 0f, 0f);
                cam.backgroundColor = new Color(0.1f, 0.12f, 0.16f);
                cam.clearFlags = CameraClearFlags.SolidColor;
            }

            // ── Lifecycle host ─────────────────────────────────────────────
            // AppLifecycleManager.Awake() initialises HealthAggregator — we
            // must NOT call ReportRoomConnected() here (Editor-time, Awake not
            // yet run → NullReferenceException). Instead, add LifecycleSmokeForcer
            // which runs in Start() (after Awake) and pushes the FSM to Connected.
            var lifecycleGo = new GameObject("Lifecycle");
            var lifecycleManager = lifecycleGo.AddComponent<AppLifecycleManager>();
            lifecycleGo.AddComponent<LifecycleHeartbeatPublisher>();
            lifecycleGo.AddComponent<LifecycleSmokeForcer>();
            var shutdownService = lifecycleGo.AddComponent<LifecycleShutdownService>();
            var startupFlow = lifecycleGo.AddComponent<AppStartupFlowController>();
            var tokenMintClient = lifecycleGo.AddComponent<LiveKitTokenMintClient>();

            var roomManager = new GameObject("RoomManager").AddComponent<RoomManager>();
            ConfigureRoomManagerForMint(roomManager);

            // ── Parrot ─────────────────────────────────────────────────────
            var glbInstance = (GameObject)PrefabUtility.InstantiatePrefab(glbAsset);
            glbInstance.name = "ParrotModel";

            var parrotRoot = new GameObject("Parrot");
            parrotRoot.transform.position = new Vector3(0f, 1.0f, 0f);
            glbInstance.transform.SetParent(parrotRoot.transform, worldPositionStays: false);
            glbInstance.transform.localPosition = Vector3.zero;
            glbInstance.transform.localRotation = Quaternion.identity;
            // Blockbench exports at 1-unit-per-voxel; 0.04 ≈ hand-sized parrot
            glbInstance.transform.localScale = Vector3.one * 0.04f;

            var animDriver = parrotRoot.AddComponent<AnimationDriver>();
            var parrotController = parrotRoot.AddComponent<ParrotController>();
            var perch = parrotRoot.AddComponent<PerchOnHand>();

            // ── Hand source ────────────────────────────────────────────────
            var handGo = new GameObject("HandSource");
            handGo.transform.position = new Vector3(0.3f, 1.0f, 0.4f);
            var handSource = handGo.AddComponent<HandGestureSource>();

            // ── Phase 4 W6-7: Attention (BBox / Focus / Echo) ──────────────
            // RoomManager: 联机 smoke 时 publisher 用 (本场景为离线 smoke，
            // EcpEventPublisher.logEvenWhenDropped 默认 true → 在 Console 打 wire JSON)
            var attentionRootGo = new GameObject("Attention");
            attentionRootGo.AddComponent<EcpEventPublisher>();
            attentionRootGo.AddComponent<BBoxController>();
            attentionRootGo.AddComponent<FocusController>();
            var echoPub = attentionRootGo.AddComponent<AttentionConfigEchoPublisher>();

            // ParrotAttentionConfig SO: 用 §8.1 L9 锁定起步值；保存到 Assets 让
            // smoke + 真机一致。如果已存在则复用，避免每次 Build 重写。
            //
            // F-A22 fix (cold-read audit): 必须用 AssetDatabase.CreateFolder 而不是
            // Directory.CreateDirectory —— OS 目录创建后 AssetDatabase 不会立即识别，
            // CreateAsset 会报 "Could not create asset"。
            const string AttentionConfigAssetPath =
                "Assets/ParrotApp/Config/ParrotAttentionConfig.asset";
            var attentionConfig =
                AssetDatabase.LoadAssetAtPath<ParrotAttentionConfig>(AttentionConfigAssetPath);
            if (attentionConfig == null)
            {
                EnsureAssetFolder("Assets/ParrotApp/Config");
                attentionConfig = ScriptableObject.CreateInstance<ParrotAttentionConfig>();
                AssetDatabase.CreateAsset(attentionConfig, AttentionConfigAssetPath);
                AssetDatabase.SaveAssets();
                Debug.Log($"[ParrotSmokeSceneBuilder] Created {AttentionConfigAssetPath}");
            }

            // ── Phase 4 W8: Photo (capturePhoto + 256px preview + HTTP POST) ───
            // PhotoController: 离线 smoke 用 ContextMenu 触发，联机 smoke 验证 HTTP POST 路径
            var photoRootGo = new GameObject("Photo");
            var photoController = photoRootGo.AddComponent<PhotoController>();

            // ── App V1 Meta UI: startup page, HUD, tool cabinet, workdesk,
            // draggable magnifier Focus and resizable BoundaryBox overlays.
            var uiRootGo = new GameObject("AppV1MetaUI");
            var appUi = uiRootGo.AddComponent<AppV1MetaUiController>();

            // ── Wire references via SerializedObject ───────────────────────
            var perchSo = new SerializedObject(perch);
            perchSo.FindProperty("handTracker").objectReferenceValue = handSource;
            perchSo.FindProperty("animDriver").objectReferenceValue = animDriver;
            perchSo.ApplyModifiedPropertiesWithoutUndo();

            var heartbeat = lifecycleGo.GetComponent<LifecycleHeartbeatPublisher>();
            var heartbeatSo = new SerializedObject(heartbeat);
            heartbeatSo.FindProperty("animationDriver").objectReferenceValue = animDriver;
            heartbeatSo.ApplyModifiedPropertiesWithoutUndo();

            var echoSo = new SerializedObject(echoPub);
            echoSo.FindProperty("config").objectReferenceValue = attentionConfig;
            echoSo.ApplyModifiedPropertiesWithoutUndo();

            var uiSo = new SerializedObject(appUi);
            uiSo.FindProperty("startupFlow").objectReferenceValue = startupFlow;
            uiSo.FindProperty("photoController").objectReferenceValue = photoController;
            uiSo.FindProperty("parrotController").objectReferenceValue = parrotController;
            uiSo.FindProperty("focusController").objectReferenceValue =
                attentionRootGo.GetComponent<FocusController>();
            uiSo.FindProperty("bboxController").objectReferenceValue =
                attentionRootGo.GetComponent<BBoxController>();
            uiSo.FindProperty("handGestureSource").objectReferenceValue = handSource;
            uiSo.FindProperty("woodDrawerSprite").objectReferenceValue = LoadSprite(ToolDrawerWoodSpritePath);
            uiSo.FindProperty("woodButtonSprite").objectReferenceValue = LoadSprite(ToolButtonWoodSpritePath);
            uiSo.FindProperty("smallPaperNoteSprite").objectReferenceValue = LoadSprite(PaperNoteSmallSpritePath);
            uiSo.FindProperty("filledPaperNoteSprite").objectReferenceValue = LoadSprite(PaperNoteFilledSpritePath);
            uiSo.FindProperty("nekoClawSprite").objectReferenceValue = LoadSprite(NekoClawSpritePath);
            uiSo.ApplyModifiedPropertiesWithoutUndo();

            WireStartupFlow(startupFlow, roomManager, lifecycleManager, shutdownService, tokenMintClient);

            // ── Save ───────────────────────────────────────────────────────
            string savePath = EditorUtility.SaveFilePanelInProject(
                "Save Smoke Scene", "ParrotSmokeScene", "unity",
                "Choose where to save the W3.A.2/A.3 + W6-7 smoke scene.");
            if (!string.IsNullOrEmpty(savePath))
                EditorSceneManager.SaveScene(UnityEngine.SceneManagement.SceneManager.GetActiveScene(), savePath);

            Debug.Log(
                "[ParrotSmokeSceneBuilder] Scene built.\n" +
                "── W3.A.2/A.3 (perch + EcpState) ───────────────\n" +
                "► Play → wait 1s for [Heartbeat:LOG] in Console\n" +
                "► Select HandSource → component ⋮ →\n" +
                "    'Debug: Fire \"index_finger_branch\" gesture'\n" +
                "► Parrot should fly, tilt + wiggle head\n" +
                "── W6-7 (BBox / Focus / Attention Echo) ─────────\n" +
                "► Select Attention → BBoxController ⋮ → 'Debug: Place Test BBox'\n" +
                "    Console shows [EcpEvent:DROPPED room not ready] (no LiveKit) +\n" +
                "    wire JSON for bbox.placed (event_id, payload incl. bbox_id/corners/pose)\n" +
                "► FocusController ⋮ → 'Debug: Anchor Test Focus' (same dropped wire JSON)\n" +
                "► AttentionConfigEchoPublisher ⋮ → 'Debug: Echo Now'\n" +
                "    wire JSON for attention.config.echo (Δ + threshold + TTL + schema_version)\n" +
                "── W8 (Photo capture + preview + HTTP POST) ──────\n" +
                "► Select Photo → PhotoController ⋮ → 'Debug: Capture Test Photo'\n" +
                "    Console shows [EcpEvent:DROPPED] event_type=photo.taken_preview\n" +
                "    wire JSON contains 12-field payload incl. preview_jpeg_b64 + pose\n" +
                "    [PhotoController] HTTP POST attempt will fail (Brain not running) — expected\n" +
                "► 'Debug: Capture With Test Candidate' → same + candidate_subject_uuid=obj_test_42\n" +
                "► 'Debug: Capture With Active Refs' → same + bbox_refs/focus_refs from active controllers\n" +
                "── App V1 Meta UI ─────────────────────────────\n" +
                "► Play → StartupSurface appears. Choose LOCAL PREVIEW for offline UI smoke\n" +
                "► HUD Tools opens a wood pull-out cabinet\n" +
                "► Magnifier creates a draggable Focus overlay with x + gear\n" +
                "► BoundaryBox creates a draggable/resizable BBox overlay with x + gear\n" +
                "► Notes spawns selectable paper notes; drag to TRASH or DESK targets\n" +
                "► Bottom-left joystick walks the parrot on the plane; home flies back to desk");
        }

        [MenuItem(MenuPath, validate = true)]
        public static bool Validate() => File.Exists(GlbAssetPath);

        [MenuItem(UpgradeMenuPath)]
        public static void UpgradeCurrentSmokeScene()
        {
            var parrotRoot = GameObject.Find("Parrot");
            var animDriver = parrotRoot != null
                ? GetOrAdd<AnimationDriver>(parrotRoot)
                : Object.FindObjectOfType<AnimationDriver>();
            var parrotController = parrotRoot != null
                ? GetOrAdd<ParrotController>(parrotRoot)
                : Object.FindObjectOfType<ParrotController>();
            var perch = parrotRoot != null
                ? GetOrAdd<PerchOnHand>(parrotRoot)
                : Object.FindObjectOfType<PerchOnHand>();

            var lifecycleRoot = FindOrCreateRoot("Lifecycle");
            var lifecycleManager = GetOrAdd<AppLifecycleManager>(lifecycleRoot);
            var shutdownService = GetOrAdd<LifecycleShutdownService>(lifecycleRoot);
            var startupFlow = GetOrAdd<AppStartupFlowController>(lifecycleRoot);
            var tokenMintClient = GetOrAdd<LiveKitTokenMintClient>(lifecycleRoot);
            GetOrAdd<RoomManagerLifecycleBridge>(lifecycleRoot);

            var roomManager = Object.FindObjectOfType<RoomManager>();
            if (roomManager == null)
                roomManager = GetOrAdd<RoomManager>(FindOrCreateRoot("RoomManager"));
            ConfigureRoomManagerForMint(roomManager);

            var handSource = Object.FindObjectOfType<HandGestureSource>();
            if (handSource == null)
                handSource = GetOrAdd<HandGestureSource>(FindOrCreateRoot("HandSource"));

            var photoController = Object.FindObjectOfType<PhotoController>();
            if (photoController == null)
                photoController = GetOrAdd<PhotoController>(FindOrCreateRoot("Photo"));

            var attentionRoot = FindOrCreateRoot("Attention");
            GetOrAdd<EcpEventPublisher>(attentionRoot);
            var bboxController = Object.FindObjectOfType<BBoxController>() ?? GetOrAdd<BBoxController>(attentionRoot);
            var focusController = Object.FindObjectOfType<FocusController>() ?? GetOrAdd<FocusController>(attentionRoot);
            GetOrAdd<AttentionConfigEchoPublisher>(attentionRoot);

            var uiRoot = FindOrCreateRoot("AppV1MetaUI");
            var appUi = GetOrAdd<AppV1MetaUiController>(uiRoot);

            SetObjectRef(appUi, "startupFlow", startupFlow);
            SetObjectRef(appUi, "photoController", photoController);
            SetObjectRef(appUi, "focusController", focusController);
            SetObjectRef(appUi, "bboxController", bboxController);
            SetObjectRef(appUi, "handGestureSource", handSource);
            SetObjectRef(appUi, "parrotController", parrotController);
            SetOptionalAppSprites(appUi);

            SetObjectRef(perch, "handTracker", handSource);
            SetObjectRef(perch, "animDriver", animDriver);
            WireStartupFlow(startupFlow, roomManager, lifecycleManager, shutdownService, tokenMintClient);

            EditorUtility.SetDirty(lifecycleRoot);
            EditorUtility.SetDirty(roomManager);
            EditorUtility.SetDirty(uiRoot);
            EditorUtility.SetDirty(attentionRoot);
            if (parrotRoot != null) EditorUtility.SetDirty(parrotRoot);

            var activeScene = UnityEngine.SceneManagement.SceneManager.GetActiveScene();
            EditorSceneManager.MarkSceneDirty(activeScene);
            if (!string.IsNullOrEmpty(activeScene.path))
                EditorSceneManager.SaveScene(activeScene);

            Debug.Log(
                "[ParrotSmokeSceneBuilder] Current scene upgraded for App V1: " +
                "AppV1MetaUI, Mint startup flow, paper-note drag/drop UI, " +
                "parrot joystick wiring, Photo/Focus/BBox/XRHand references.");
        }

        // ─── helpers ──────────────────────────────────────────────────────

        private static GameObject FindOrCreateRoot(string name)
        {
            var go = GameObject.Find(name);
            if (go != null) return go;
            go = new GameObject(name);
            Undo.RegisterCreatedObjectUndo(go, "Create " + name);
            return go;
        }

        private static T GetOrAdd<T>(GameObject go) where T : Component
        {
            var component = go.GetComponent<T>();
            if (component != null) return component;
            return Undo.AddComponent<T>(go);
        }

        private static void SetObjectRef(UnityEngine.Object target, string propertyName, UnityEngine.Object value)
        {
            if (target == null || value == null) return;
            var so = new SerializedObject(target);
            var prop = so.FindProperty(propertyName);
            if (prop == null) return;
            prop.objectReferenceValue = value;
            so.ApplyModifiedPropertiesWithoutUndo();
        }

        private static void ConfigureRoomManagerForMint(RoomManager roomManager)
        {
            if (roomManager == null) return;
            SetBool(roomManager, "autoConnectOnStart", false);
            SetBool(roomManager, "allowEditorTokenFile", false);
        }

        private static void WireStartupFlow(
            AppStartupFlowController startupFlow,
            RoomManager roomManager,
            AppLifecycleManager lifecycleManager,
            LifecycleShutdownService shutdownService,
            LiveKitTokenMintClient tokenMintClient)
        {
            if (startupFlow == null) return;
            SetObjectRef(startupFlow, "roomManager", roomManager);
            SetObjectRef(startupFlow, "lifecycleManager", lifecycleManager);
            SetObjectRef(startupFlow, "shutdownService", shutdownService);
            SetObjectRef(startupFlow, "tokenMintClient", tokenMintClient);
            SetObjectRef(startupFlow, "microphonePublisher", Object.FindObjectOfType<MicrophonePublisher>());
            SetObjectRef(startupFlow, "videoPublisher", Object.FindObjectOfType<ARVideoPublisher>());
        }

        private static void SetBool(UnityEngine.Object target, string propertyName, bool value)
        {
            if (target == null) return;
            var so = new SerializedObject(target);
            var prop = so.FindProperty(propertyName);
            if (prop == null || prop.propertyType != SerializedPropertyType.Boolean) return;
            prop.boolValue = value;
            so.ApplyModifiedPropertiesWithoutUndo();
        }

        private static void SetOptionalAppSprites(AppV1MetaUiController appUi)
        {
            SetObjectRef(appUi, "woodDrawerSprite", LoadSprite(ToolDrawerWoodSpritePath));
            SetObjectRef(appUi, "woodButtonSprite", LoadSprite(ToolButtonWoodSpritePath));
            SetObjectRef(appUi, "smallPaperNoteSprite", LoadSprite(PaperNoteSmallSpritePath));
            SetObjectRef(appUi, "filledPaperNoteSprite", LoadSprite(PaperNoteFilledSpritePath));
            SetObjectRef(appUi, "nekoClawSprite", LoadSprite(NekoClawSpritePath));
        }

        private static Sprite LoadSprite(string path)
        {
            return AssetDatabase.LoadAssetAtPath<Sprite>(path);
        }

        /// <summary>
        /// 递归确保 AssetDatabase-recognized 资源目录存在。仅在 <c>Assets/</c> 下
        /// 工作（外部目录用 <c>Directory.CreateDirectory</c>）。
        /// 必须用本方法而不是直接 <c>Directory.CreateDirectory</c>：OS 目录创建
        /// 后 Unity AssetDatabase 不会立即扫描到，<c>CreateAsset</c> 会报错。
        /// </summary>
        private static void EnsureAssetFolder(string assetFolderPath)
        {
            if (string.IsNullOrEmpty(assetFolderPath)) return;
            assetFolderPath = assetFolderPath.Replace('\\', '/');
            if (AssetDatabase.IsValidFolder(assetFolderPath)) return;

            string parent = Path.GetDirectoryName(assetFolderPath)?.Replace('\\', '/');
            string name = Path.GetFileName(assetFolderPath);

            if (string.IsNullOrEmpty(parent) || string.IsNullOrEmpty(name)) return;

            if (!AssetDatabase.IsValidFolder(parent))
            {
                EnsureAssetFolder(parent);
            }
            AssetDatabase.CreateFolder(parent, name);
        }
    }
}
#endif
