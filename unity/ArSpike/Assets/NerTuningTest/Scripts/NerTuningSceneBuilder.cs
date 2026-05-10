#if UNITY_EDITOR
using System.IO;
using ParrotApp.Parrot;
using Spine.Unity;
using UnityEditor;
using UnityEditor.SceneManagement;
using UnityEngine;

namespace ParrotApp.NerTuning.Editor
{
    /// <summary>
    /// Editor-only builder for the isolated Ner mouse tuning scene.
    /// It deliberately writes only under Assets/NerTuningTest.
    /// </summary>
    public static class NerTuningSceneBuilder
    {
        private const string MenuPath = "ParrotApp/Ner/Rebuild Mouse Tuning Test Scene";
        private const string RootFolder = "Assets/NerTuningTest";
        private const string ScenesFolder = "Assets/NerTuningTest/Scenes";
        private const string PrefabsFolder = "Assets/NerTuningTest/Prefabs";
        private const string MaterialsFolder = "Assets/NerTuningTest/Materials";
        private const string ScenePath = "Assets/NerTuningTest/Scenes/NerMouseTuningScene.unity";
        private const string PrefabPath = "Assets/NerTuningTest/Prefabs/NerMouseTuningRig.prefab";
        private const string GroundMaterialPath = "Assets/NerTuningTest/Materials/NerTuningGround.mat";
        private const string GridMaterialPath = "Assets/NerTuningTest/Materials/NerTuningGrid.mat";
        private const string MarkerMaterialPath = "Assets/NerTuningTest/Materials/NerTuningMarker.mat";
        private const string SkeletonPath = "Assets/Models/Ner/NerSkin2_SkeletonData.asset";

        [MenuItem(MenuPath)]
        public static void RebuildMouseTuningScene()
        {
            EnsureFolder(RootFolder);
            EnsureFolder(ScenesFolder);
            EnsureFolder(PrefabsFolder);
            EnsureFolder(MaterialsFolder);

            var skeletonData = AssetDatabase.LoadAssetAtPath<SkeletonDataAsset>(SkeletonPath);
            if (skeletonData == null)
            {
                Debug.LogError("[NerTuningSceneBuilder] Missing skeleton data: " + SkeletonPath);
                return;
            }

            var groundMaterial = LoadOrCreateMaterial(GroundMaterialPath, new Color(0.32f, 0.34f, 0.34f, 1f));
            var gridMaterial = LoadOrCreateMaterial(GridMaterialPath, new Color(0.12f, 0.13f, 0.13f, 1f));
            var markerMaterial = LoadOrCreateMaterial(MarkerMaterialPath, new Color(0.74f, 0.84f, 0.92f, 1f));

            var scene = EditorSceneManager.NewScene(NewSceneSetup.EmptyScene, NewSceneMode.Single);
            scene.name = "NerMouseTuningScene";

            var camera = CreateCamera();
            CreateLights();
            CreateGround(groundMaterial, gridMaterial, markerMaterial);
            var rig = CreateRig(skeletonData, camera);

            PrefabUtility.SaveAsPrefabAsset(rig, PrefabPath);
            EditorSceneManager.SaveScene(scene, ScenePath);
            AssetDatabase.SaveAssets();
            AssetDatabase.Refresh();

            Selection.activeGameObject = rig;
            if (SceneView.lastActiveSceneView != null)
            {
                SceneView.lastActiveSceneView.FrameSelected();
            }

            Debug.Log("[NerTuningSceneBuilder] Rebuilt " + ScenePath + " and " + PrefabPath);
        }

        private static Camera CreateCamera()
        {
            var cameraGo = new GameObject("Main Camera");
            cameraGo.tag = "MainCamera";
            cameraGo.transform.position = new Vector3(0f, 0.46f, -1.28f);
            cameraGo.transform.rotation = Quaternion.Euler(12f, 0f, 0f);
            var camera = cameraGo.AddComponent<Camera>();
            camera.fieldOfView = 38f;
            camera.nearClipPlane = 0.03f;
            camera.farClipPlane = 12f;
            camera.clearFlags = CameraClearFlags.SolidColor;
            camera.backgroundColor = new Color(0.50f, 0.62f, 0.75f, 1f);
            cameraGo.AddComponent<AudioListener>();
            return camera;
        }

        private static void CreateLights()
        {
            var directional = new GameObject("Directional Light");
            directional.transform.rotation = Quaternion.Euler(45f, -30f, 0f);
            var light = directional.AddComponent<Light>();
            light.type = LightType.Directional;
            light.intensity = 1.15f;

            var fill = new GameObject("Tuning Fill Light");
            fill.transform.position = new Vector3(0f, 0.7f, -0.5f);
            var fillLight = fill.AddComponent<Light>();
            fillLight.type = LightType.Point;
            fillLight.intensity = 0.35f;
            fillLight.range = 3f;
        }

        private static void CreateGround(Material groundMaterial, Material gridMaterial, Material markerMaterial)
        {
            var floor = GameObject.CreatePrimitive(PrimitiveType.Cube);
            floor.name = "TuningGround_PlaceTarget";
            floor.transform.position = new Vector3(0f, -0.015f, 0.18f);
            floor.transform.localScale = new Vector3(2.4f, 0.03f, 2.4f);
            floor.GetComponent<Renderer>().sharedMaterial = groundMaterial;

            var grid = new GameObject("TuningGroundGrid_NoCollider");
            for (int i = -4; i <= 4; i++)
            {
                CreateGridLine(grid.transform, "GridLine_X_" + i, new Vector3(0f, 0.003f, 0.18f + i * 0.25f), new Vector3(2.4f, 0.004f, 0.006f), gridMaterial);
                CreateGridLine(grid.transform, "GridLine_Z_" + i, new Vector3(i * 0.25f, 0.004f, 0.18f), new Vector3(0.006f, 0.004f, 2.4f), gridMaterial);
            }

            var markers = new GameObject("TuningCornerMarkers_NoCollider");
            var markerPositions = new[]
            {
                new Vector3(-1.05f, 0.025f, -0.87f),
                new Vector3(1.05f, 0.025f, -0.87f),
                new Vector3(-1.05f, 0.025f, 1.23f),
                new Vector3(1.05f, 0.025f, 1.23f),
            };
            for (int i = 0; i < markerPositions.Length; i++)
            {
                var marker = GameObject.CreatePrimitive(PrimitiveType.Cube);
                marker.name = "MovementMarker_" + i;
                marker.transform.SetParent(markers.transform, false);
                marker.transform.position = markerPositions[i];
                marker.transform.localScale = new Vector3(0.06f, 0.05f, 0.06f);
                marker.GetComponent<Renderer>().sharedMaterial = markerMaterial;
                Object.DestroyImmediate(marker.GetComponent<Collider>());
            }
        }

        private static void CreateGridLine(Transform parent, string name, Vector3 position, Vector3 scale, Material material)
        {
            var line = GameObject.CreatePrimitive(PrimitiveType.Cube);
            line.name = name;
            line.transform.SetParent(parent, false);
            line.transform.position = position;
            line.transform.localScale = scale;
            line.GetComponent<Renderer>().sharedMaterial = material;
            Object.DestroyImmediate(line.GetComponent<Collider>());
        }

        private static GameObject CreateRig(SkeletonDataAsset skeletonData, Camera camera)
        {
            var root = new GameObject("NerMouseTuningRig");
            var skeletonAnimation = SkeletonAnimation.AddToGameObject(root, skeletonData, quiet: true);
            skeletonAnimation.initialSkinName = "Normal";
            skeletonAnimation.loop = true;
            skeletonAnimation.Initialize(true, quiet: true);
            var skeleton = skeletonAnimation.Skeleton;
            if (skeleton == null)
            {
                skeletonAnimation.skeletonDataAsset = skeletonData;
                skeletonAnimation.Initialize(true, quiet: false);
                skeleton = skeletonAnimation.Skeleton;
            }
            if (skeleton != null && skeletonAnimation.AnimationState != null)
            {
                skeleton.SetSkin("Normal");
                skeleton.SetSlotsToSetupPose();
                skeletonAnimation.AnimationState.SetAnimation(0, "Idle_1", true);
                skeletonAnimation.Update(0f);
                skeletonAnimation.LateUpdate();

                FitRootToHeight(root, 0.32f);
            }
            else
            {
                Debug.LogWarning("[NerTuningSceneBuilder] Ner SkeletonAnimation did not initialize before component wiring.");
            }

            var controller = root.AddComponent<NerSpineController>();
            var modelDriver = root.AddComponent<ModelDriver>();
            SetString(modelDriver, "modelId", "ner_skin2");
            SetBool(modelDriver, "verbose", true);

            var harness = root.AddComponent<NerMouseTuningHarness>();
            var probe = root.AddComponent<NerTuningAcceptanceProbe>();
            ConfigureHarnessAndProbe(root, camera, controller, harness, probe);
            return root;
        }

        private static void ConfigureHarnessAndProbe(
            GameObject root,
            Camera camera,
            NerSpineController controller,
            NerMouseTuningHarness harness,
            NerTuningAcceptanceProbe probe)
        {
            var bounds = GetRendererBounds(root);
            float height = Mathf.Max(0.001f, bounds.size.y);
            float width = Mathf.Max(0.001f, bounds.size.x);
            float scale = Mathf.Max(0.0001f, root.transform.lossyScale.x);

            var leftCheekWorld = new Vector3(bounds.center.x - width * 0.32f, bounds.min.y + height * 0.61f, bounds.center.z - 0.024f);
            var rightCheekWorld = new Vector3(bounds.center.x + width * 0.26f, bounds.min.y + height * 0.61f, bounds.center.z - 0.024f);
            var headPatWorld = new Vector3(bounds.center.x, bounds.min.y + height * 0.67f, bounds.center.z - 0.026f);
            var bodyWorld = new Vector3(bounds.center.x, bounds.min.y + height * 0.42f, bounds.center.z - 0.006f);
            var bodySize = new Vector3(Mathf.Max(width * 0.72f, height * 0.30f) / scale, height * 0.68f / scale, 0.12f / scale);

            SetFloat(controller, "cheekMaxPullUnits", 10.5f);
            SetFloat(controller, "cheekVerticalPullRatio", 0.28f);
            SetFloat(controller, "cheekScaleXAtFullPull", 0.055f);
            SetFloat(controller, "cheekScaleYAtFullPull", -0.025f);
            SetFloat(controller, "cheekHeadFollowStrength", 0.2f);
            SetFloat(controller, "cheekReleaseSeconds", 0.28f);
            SetFloat(controller, "cheekReleaseBounce", 0.22f);
            SetFloat(controller, "cheekReleaseSquash", 0.025f);
            SetFloat(controller, "touchSquash", 0.038f);
            SetFloat(controller, "squashBounceSeconds", 0.34f);
            SetFloat(controller, "squashBounceCycles", 2.35f);

            SetObjectRef(harness, "targetCamera", camera);
            SetObjectRef(harness, "controller", controller);
            SetObjectRef(harness, "targetRoot", root.transform);
            SetVector3(harness, "leftCheekLocalPosition", root.transform.InverseTransformPoint(leftCheekWorld));
            SetVector3(harness, "rightCheekLocalPosition", root.transform.InverseTransformPoint(rightCheekWorld));
            SetBool(harness, "enableRightCheek", false);
            SetFloat(harness, "cheekRadiusMeters", Mathf.Clamp(height * 0.085f, 0.024f, 0.034f) / scale);
            SetVector3(harness, "headPatLocalPosition", root.transform.InverseTransformPoint(headPatWorld));
            SetFloat(harness, "headPatRadiusMeters", Mathf.Clamp(height * 0.115f, 0.032f, 0.046f) / scale);
            SetVector3(harness, "bodyColliderCenter", root.transform.InverseTransformPoint(bodyWorld));
            SetVector3(harness, "bodyColliderSize", bodySize);
            SetFloat(harness, "dragPixelsForFullStrength", 180f);
            SetFloat(harness, "warningStrength", 0.78f);
            SetFloat(harness, "warningIntervalSeconds", 0.75f);
            SetFloat(harness, "longPressSeconds", 0.58f);
            SetFloat(harness, "cancelBeforeHoldPixels", 28f);
            SetFloat(harness, "clickMaxPixels", 22f);
            SetFloat(harness, "facePatClickMaxSeconds", 0.36f);
            SetFloat(harness, "clickEndDelaySeconds", 0.55f);
            SetFloat(harness, "pickupLiftMeters", 0.12f);
            SetFloat(harness, "minPickupLiftMeters", 0.06f);
            SetFloat(harness, "maxPickupLiftMeters", 0.24f);
            SetFloat(harness, "heightDragPixelsForFullRange", 260f);
            SetFloat(harness, "pickupHeightWheelStepMeters", 0.015f);
            SetFloat(harness, "pickupAscentSeconds", 0.16f);
            SetFloat(harness, "maxRayDistanceMeters", 8f);
            SetBool(harness, "keyboardMovementEnabled", true);
            SetFloat(harness, "moveSpeedMetersPerSecond", 0.28f);
            SetInt(harness, "raycastMask", -1);

            SetObjectRef(probe, "targetCamera", camera);
            SetObjectRef(probe, "controller", controller);
            SetObjectRef(probe, "targetRoot", root.transform);
            SetBool(probe, "runOnStart", true);
            SetInt(probe, "minimumVisibleAttachments", 50);
            SetBool(probe, "expectRightCheekHit", false);
        }

        private static void FitRootToHeight(GameObject root, float targetHeight)
        {
            var bounds = GetRendererBounds(root);
            if (bounds.size.y > 0.0001f)
            {
                root.transform.localScale *= targetHeight / bounds.size.y;
            }

            var skeletonAnimation = root.GetComponent<SkeletonAnimation>();
            if (skeletonAnimation != null)
            {
                skeletonAnimation.LateUpdate();
            }

            bounds = GetRendererBounds(root);
            root.transform.position += new Vector3(0f, -bounds.min.y, 0f);
        }

        private static Bounds GetRendererBounds(GameObject root)
        {
            var renderers = root.GetComponentsInChildren<Renderer>(includeInactive: true);
            var bounds = new Bounds(root.transform.position, Vector3.zero);
            bool found = false;
            for (int i = 0; i < renderers.Length; i++)
            {
                if (renderers[i] == null || !renderers[i].enabled) continue;
                if (!found)
                {
                    bounds = renderers[i].bounds;
                    found = true;
                }
                else
                {
                    bounds.Encapsulate(renderers[i].bounds);
                }
            }
            return bounds;
        }

        private static Material LoadOrCreateMaterial(string path, Color color)
        {
            var material = AssetDatabase.LoadAssetAtPath<Material>(path);
            if (material != null)
            {
                material.color = color;
                EditorUtility.SetDirty(material);
                return material;
            }

            var shader = Shader.Find("Universal Render Pipeline/Lit");
            if (shader == null) shader = Shader.Find("Standard");
            material = new Material(shader);
            material.color = color;
            AssetDatabase.CreateAsset(material, path);
            return material;
        }

        private static void EnsureFolder(string assetFolderPath)
        {
            assetFolderPath = assetFolderPath.Replace('\\', '/');
            if (AssetDatabase.IsValidFolder(assetFolderPath)) return;

            string parent = Path.GetDirectoryName(assetFolderPath)?.Replace('\\', '/');
            string name = Path.GetFileName(assetFolderPath);
            if (string.IsNullOrEmpty(parent) || string.IsNullOrEmpty(name)) return;
            if (!AssetDatabase.IsValidFolder(parent)) EnsureFolder(parent);
            AssetDatabase.CreateFolder(parent, name);
        }

        private static void SetObjectRef(Object target, string propertyName, Object value)
        {
            var so = new SerializedObject(target);
            var prop = so.FindProperty(propertyName);
            if (prop != null) prop.objectReferenceValue = value;
            so.ApplyModifiedPropertiesWithoutUndo();
        }

        private static void SetString(Object target, string propertyName, string value)
        {
            var so = new SerializedObject(target);
            var prop = so.FindProperty(propertyName);
            if (prop != null) prop.stringValue = value;
            so.ApplyModifiedPropertiesWithoutUndo();
        }

        private static void SetBool(Object target, string propertyName, bool value)
        {
            var so = new SerializedObject(target);
            var prop = so.FindProperty(propertyName);
            if (prop != null) prop.boolValue = value;
            so.ApplyModifiedPropertiesWithoutUndo();
        }

        private static void SetFloat(Object target, string propertyName, float value)
        {
            var so = new SerializedObject(target);
            var prop = so.FindProperty(propertyName);
            if (prop != null) prop.floatValue = value;
            so.ApplyModifiedPropertiesWithoutUndo();
        }

        private static void SetVector3(Object target, string propertyName, Vector3 value)
        {
            var so = new SerializedObject(target);
            var prop = so.FindProperty(propertyName);
            if (prop != null) prop.vector3Value = value;
            so.ApplyModifiedPropertiesWithoutUndo();
        }

        private static void SetInt(Object target, string propertyName, int value)
        {
            var so = new SerializedObject(target);
            var prop = so.FindProperty(propertyName);
            if (prop != null) prop.intValue = value;
            so.ApplyModifiedPropertiesWithoutUndo();
        }
    }
}
#endif
