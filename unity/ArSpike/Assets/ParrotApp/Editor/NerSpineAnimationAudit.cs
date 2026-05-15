#if UNITY_EDITOR
using System;
using System.Collections;
using System.Collections.Generic;
using System.Text;
using ParrotApp.Parrot;
using UnityEditor;
using UnityEngine;

namespace ParrotApp.Editor
{
    /// <summary>
    /// Editor-only probe for Ner Spine import readiness.
    /// It reads the SkeletonDataAsset directly, so manifest handlers can be
    /// checked against real imported animation names instead of binary grep.
    /// </summary>
    public static class NerSpineAnimationAudit
    {
        private const string SkeletonDataPath = "Assets/ParrotApp/Resources/Models/Ner/NerSkin2_SkeletonData.asset";
        private const string ManifestPath = "Assets/ParrotApp/Resources/parrot_models/ner_skin2.json";

        [MenuItem("ParrotApp/Ner/Log NerSkin2 Animations")]
        public static void LogNerSkin2Animations()
        {
            var names = ReadAnimationNames(SkeletonDataPath);
            var sb = new StringBuilder();
            sb.AppendLine($"[NerSpineAnimationAudit] {SkeletonDataPath}");
            sb.AppendLine($"animation_count={names.Count}");
            foreach (var name in names) sb.AppendLine(name);
            Debug.Log(sb.ToString());
        }

        [MenuItem("ParrotApp/Ner/Validate Ner Manifest Handlers")]
        public static void ValidateManifestHandlers()
        {
            var known = new HashSet<string>(ReadAnimationNames(SkeletonDataPath));
            var manifestText = AssetDatabase.LoadAssetAtPath<TextAsset>(ManifestPath);
            if (manifestText == null)
            {
                Debug.LogError($"[NerSpineAnimationAudit] Missing manifest: {ManifestPath}");
                return;
            }

            var manifest = JsonUtility.FromJson<ModelManifestDto>(manifestText.text);
            if (manifest == null || manifest.capabilities == null)
            {
                Debug.LogError($"[NerSpineAnimationAudit] Failed to parse manifest: {ManifestPath}");
                return;
            }

            int checkedHandlers = 0;
            var missing = new List<string>();
            foreach (var capability in manifest.capabilities)
            {
                if (capability == null || string.IsNullOrEmpty(capability.handler)) continue;
                checkedHandlers++;
                if (!known.Contains(capability.handler))
                {
                    missing.Add($"{capability.capability_id}->{capability.handler}");
                }
            }

            if (missing.Count > 0)
            {
                Debug.LogError(
                    $"[NerSpineAnimationAudit] Missing {missing.Count}/{checkedHandlers} manifest handlers: "
                    + string.Join(", ", missing));
                return;
            }

            Debug.Log($"[NerSpineAnimationAudit] OK: {checkedHandlers} manifest handlers match {known.Count} imported animations.");
        }

        public static IReadOnlyList<string> ReadAnimationNames(string skeletonDataAssetPath)
        {
            var asset = AssetDatabase.LoadAssetAtPath<UnityEngine.Object>(skeletonDataAssetPath);
            if (asset == null) return Array.Empty<string>();

            var getSkeletonData = asset.GetType().GetMethod("GetSkeletonData", new[] { typeof(bool) })
                ?? asset.GetType().GetMethod("GetSkeletonData", Type.EmptyTypes);
            if (getSkeletonData == null) return Array.Empty<string>();

            object skeletonData = getSkeletonData.GetParameters().Length == 1
                ? getSkeletonData.Invoke(asset, new object[] { false })
                : getSkeletonData.Invoke(asset, null);
            if (skeletonData == null) return Array.Empty<string>();

            object animations = skeletonData.GetType().GetProperty("Animations")?.GetValue(skeletonData, null);
            if (animations == null)
            {
                animations = skeletonData.GetType()
                    .GetField("animations", System.Reflection.BindingFlags.Instance | System.Reflection.BindingFlags.Public | System.Reflection.BindingFlags.NonPublic)
                    ?.GetValue(skeletonData);
            }

            var result = new List<string>();
            var enumerable = animations as IEnumerable;
            if (enumerable == null) return result;

            foreach (var animation in enumerable)
            {
                if (animation == null) continue;
                string name = animation.GetType().GetProperty("Name")?.GetValue(animation, null) as string;
                if (string.IsNullOrEmpty(name))
                {
                    name = animation.GetType()
                        .GetField("name", System.Reflection.BindingFlags.Instance | System.Reflection.BindingFlags.Public | System.Reflection.BindingFlags.NonPublic)
                        ?.GetValue(animation) as string;
                }
                if (!string.IsNullOrEmpty(name)) result.Add(name);
            }
            return result;
        }
    }
}
#endif
