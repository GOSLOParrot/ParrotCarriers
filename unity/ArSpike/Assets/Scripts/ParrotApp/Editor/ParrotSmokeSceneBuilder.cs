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
            lifecycleGo.AddComponent<AppLifecycleManager>();
            lifecycleGo.AddComponent<LifecycleHeartbeatPublisher>();
            lifecycleGo.AddComponent<LifecycleSmokeForcer>();

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
            parrotRoot.AddComponent<ParrotController>();
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
            photoRootGo.AddComponent<PhotoController>();

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
                "► 'Debug: Capture With Active Refs' → same + bbox_refs/focus_refs from active controllers");
        }

        [MenuItem(MenuPath, validate = true)]
        public static bool Validate() => File.Exists(GlbAssetPath);

        // ─── helpers ──────────────────────────────────────────────────────

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
