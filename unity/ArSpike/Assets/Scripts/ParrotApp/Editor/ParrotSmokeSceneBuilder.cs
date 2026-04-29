#if UNITY_EDITOR
using System.IO;
using ParrotApp.Ecp;
using ParrotApp.Hands;
using ParrotApp.Lifecycle;
using ParrotApp.Parrot;
using UnityEditor;
using UnityEditor.SceneManagement;
using UnityEngine;
using UnityEngine.SceneManagement;

namespace ParrotApp.EditorTools
{
    /// <summary>
    /// Sprint4 Phase 4 W3.A.2 — one-click smoke scene builder.
    ///
    /// Tools / Parrot / Build A2 Smoke Scene:
    /// <list type="bullet">
    /// <item>Loads <c>Assets/Models/GOSLO.glb</c> via gltfast importer</item>
    /// <item>Wraps in a "Parrot" GameObject + attaches
    ///   <see cref="ParrotController"/> + <see cref="AnimationDriver"/> +
    ///   <see cref="PerchOnHand"/></item>
    /// <item>Creates a "HandSource" GameObject with
    ///   <see cref="HandGestureSource"/></item>
    /// <item>Creates a "Lifecycle" GameObject with
    ///   <see cref="AppLifecycleManager"/> +
    ///   <see cref="LifecycleHeartbeatPublisher"/>（让 A.3 双触发心跳能在
    ///   Editor 内被 LogHeartbeatTransport 打出来）</item>
    /// <item>Wires PerchOnHand.handTracker / animDriver references</item>
    /// <item>Logs a summary; user saves the scene manually.</item>
    /// </list>
    ///
    /// 适用：Editor 内验收 W3.A.2 + W3.A.3 不带任何 LiveKit 真连接。
    /// 真连接需要 RoomManager + Token，那是另一条 wire-up 路径。
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
                    $"Expected at {GlbAssetPath}.\n\n" +
                    "Run the W3.A.2 commit's asset copy step first or check\n" +
                    "Assets/Models/ in Project window.",
                    "OK");
                return;
            }

            // 1. Load the imported glTF as a prefab-instantiable asset.
            var glbAsset = AssetDatabase.LoadAssetAtPath<GameObject>(GlbAssetPath);
            if (glbAsset == null)
            {
                EditorUtility.DisplayDialog(
                    "GOSLO.glb not imported",
                    "Asset exists on disk but Unity hasn't imported it as a GameObject.\n\n" +
                    "Make sure com.unity.cloud.gltfast is installed (see\n" +
                    "Packages/manifest.json), then right-click GOSLO.glb in Project\n" +
                    "and choose Reimport.",
                    "OK");
                return;
            }

            // 2. Build a brand new scene so we don't pollute the AR sample one.
            var scene = EditorSceneManager.NewScene(NewSceneSetup.DefaultGameObjects, NewSceneSetup.DefaultGameObjects == NewSceneSetup.DefaultGameObjects ? NewSceneMode.Single : NewSceneMode.Single);
            scene.name = "ParrotSmokeScene";

            // 3. Position the main camera so the bird is in frame.
            var cam = Camera.main;
            if (cam != null)
            {
                cam.transform.position = new Vector3(0f, 1.4f, -1.5f);
                cam.transform.rotation = Quaternion.Euler(8f, 0f, 0f);
                cam.backgroundColor = new Color(0.1f, 0.12f, 0.16f);
                cam.clearFlags = CameraClearFlags.SolidColor;
            }

            // 4. Lifecycle host — required by LifecycleHeartbeatPublisher
            //    (RequireComponent(typeof(AppLifecycleManager))).
            var lifecycleGo = new GameObject("Lifecycle");
            var lifecycle = lifecycleGo.AddComponent<AppLifecycleManager>();
            var heartbeat = lifecycleGo.AddComponent<LifecycleHeartbeatPublisher>();
            // 让 publisher 立刻有传输：默认 LogHeartbeatTransport (Inspector 上
            // useLogTransportInEditor 默认 true，Awake 时会自动 new 一个)
            // UnityIdentity / RoomId 留空 — Editor smoke 没真 Room
            // Force a benign lifecycle so heartbeat publisher will actually fire.
            // (ColdStart / ShuttingDown / Disconnected 都会被 chokepoint 跳过)
            lifecycle.EnterTokenGate();           // PreConnect-family
            lifecycle.EnterArSessionStarting();
            lifecycle.EnterConnecting();
            lifecycle.ReportRoomConnected();      // → Connected family — heartbeat starts

            // 5. Parrot — instantiate GLB prefab and wrap with our scripts.
            var glbInstance = (GameObject)PrefabUtility.InstantiatePrefab(glbAsset);
            glbInstance.name = "ParrotModel";
            var parrotRoot = new GameObject("Parrot");
            parrotRoot.transform.position = new Vector3(0f, 1.0f, 0f);
            glbInstance.transform.SetParent(parrotRoot.transform, worldPositionStays: false);
            glbInstance.transform.localPosition = Vector3.zero;
            glbInstance.transform.localRotation = Quaternion.identity;
            // GLBs from blockbench tend to come in 16x scale; tone down so the
            // bird is roughly hand-sized (a parrot is ~20cm tall).
            glbInstance.transform.localScale = Vector3.one * 0.04f;

            var animDriver = parrotRoot.AddComponent<AnimationDriver>();
            var parrotCtl = parrotRoot.AddComponent<ParrotController>();
            var perch = parrotRoot.AddComponent<PerchOnHand>();
            // Suppress unused-variable warnings — these references are used
            // implicitly via GetComponent in the script lifecycles.
            _ = parrotCtl;

            // 6. Hand source — separate root so it can move independently.
            var handGo = new GameObject("HandSource");
            handGo.transform.position = new Vector3(0.3f, 1.0f, 0.4f);
            var handSource = handGo.AddComponent<HandGestureSource>();

            // 7. Wire references — PerchOnHand needs both.
            // Use SerializedObject so we set the SerializeField even though
            // the field is private (matches Inspector wiring exactly).
            var perchSo = new SerializedObject(perch);
            perchSo.FindProperty("handTracker").objectReferenceValue = handSource;
            perchSo.FindProperty("animDriver").objectReferenceValue = animDriver;
            perchSo.ApplyModifiedPropertiesWithoutUndo();

            var heartbeatSo = new SerializedObject(heartbeat);
            heartbeatSo.FindProperty("animationDriver").objectReferenceValue = animDriver;
            heartbeatSo.ApplyModifiedPropertiesWithoutUndo();

            // 8. Save dialog so user can choose where to put the scene.
            string savePath = EditorUtility.SaveFilePanelInProject(
                "Save Smoke Scene",
                "ParrotSmokeScene",
                "unity",
                "Choose where to save the W3.A.2/A.3 smoke scene.");
            if (!string.IsNullOrEmpty(savePath))
            {
                EditorSceneManager.SaveScene(scene, savePath);
            }

            // 9. Summary.
            Debug.Log(
                "[ParrotSmokeSceneBuilder] Scene built.\n" +
                $"  Parrot root  : {parrotRoot.name} (position {parrotRoot.transform.position})\n" +
                $"  GLB instance : {glbInstance.name} (scale {glbInstance.transform.localScale.x:F2})\n" +
                $"  Hand source  : {handGo.name} (position {handGo.transform.position})\n" +
                $"  Lifecycle    : {lifecycleGo.name} → state={lifecycle.CurrentState}\n" +
                "\n" +
                "Editor smoke steps:\n" +
                "  1. ▶ Play\n" +
                "  2. Console should show [Heartbeat:LOG] EcpState every ~1s\n" +
                "  3. Select HandSource → component ⋮ menu →\n" +
                "       'Debug: Fire \"index_finger_branch\" gesture (1m forward)'\n" +
                "  4. Watch the parrot fly to the gesture spot, then tilt + wiggle head\n" +
                "  5. Fire 'closed_fist' to send it back to the spawn position\n" +
                "\n" +
                "Bone wiring: AnimationDriver.headNodeName=\"Head\" / bodyNodeName=\"Body\"\n" +
                "matches the GLB's top-level 'head' / 'body' Empty groups.\n" +
                "If head doesn't tilt, expand ParrotModel in Hierarchy and confirm those\n" +
                "two transforms exist as immediate children of the GLB root.");
        }

        [MenuItem(MenuPath, validate = true)]
        public static bool BuildSmokeSceneValidate()
        {
            return File.Exists(GlbAssetPath);
        }
    }
}
#endif
