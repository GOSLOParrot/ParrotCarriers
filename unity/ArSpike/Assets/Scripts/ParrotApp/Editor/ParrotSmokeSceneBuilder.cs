#if UNITY_EDITOR
using System.IO;
using ParrotApp.Ecp;
using ParrotApp.Hands;
using ParrotApp.Lifecycle;
using ParrotApp.Parrot;
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

            // ── Wire references via SerializedObject ───────────────────────
            var perchSo = new SerializedObject(perch);
            perchSo.FindProperty("handTracker").objectReferenceValue = handSource;
            perchSo.FindProperty("animDriver").objectReferenceValue = animDriver;
            perchSo.ApplyModifiedPropertiesWithoutUndo();

            var heartbeat = lifecycleGo.GetComponent<LifecycleHeartbeatPublisher>();
            var heartbeatSo = new SerializedObject(heartbeat);
            heartbeatSo.FindProperty("animationDriver").objectReferenceValue = animDriver;
            heartbeatSo.ApplyModifiedPropertiesWithoutUndo();

            // ── Save ───────────────────────────────────────────────────────
            string savePath = EditorUtility.SaveFilePanelInProject(
                "Save Smoke Scene", "ParrotSmokeScene", "unity",
                "Choose where to save the W3.A.2/A.3 smoke scene.");
            if (!string.IsNullOrEmpty(savePath))
                EditorSceneManager.SaveScene(UnityEngine.SceneManagement.SceneManager.GetActiveScene(), savePath);

            Debug.Log(
                "[ParrotSmokeSceneBuilder] Scene built.\n" +
                "► Play → wait 1s for [Heartbeat:LOG] in Console\n" +
                "► Select HandSource → component ⋮ →\n" +
                "    'Debug: Fire \"index_finger_branch\" gesture'\n" +
                "► Parrot should fly to HandSource position, then tilt + wiggle head\n" +
                "► 'Debug: Fire closed_fist' → parrot returns, head resets");
        }

        [MenuItem(MenuPath, validate = true)]
        public static bool Validate() => File.Exists(GlbAssetPath);
    }
}
#endif
