#if UNITY_EDITOR
using System.IO;
using ParrotApp.Config;
using UnityEditor;
using UnityEngine;

namespace ParrotApp.Config.EditorTools
{
    /// <summary>
    /// <c>Tools / Parrot / Lifecycle Tuning</c>：
    /// 选中或创建 Project 内的 <see cref="ParrotLifecycleConfig"/> asset，方便 spike 期间调参。
    /// 未来挂入 app 设置面板的入口也走这个 asset，不再分散硬编。
    /// </summary>
    public static class ParrotLifecycleConfigMenu
    {
        private const string MenuPath = "Tools/Parrot/Lifecycle Tuning";
        private const string DefaultAssetDir = "Assets/Scripts/ParrotApp/Config";
        private const string DefaultAssetName = "ParrotLifecycleConfig.asset";

        [MenuItem(MenuPath, priority = 200)]
        private static void OpenOrCreate()
        {
            var existing = LoadFirst();
            if (existing != null)
            {
                Selection.activeObject = existing;
                EditorGUIUtility.PingObject(existing);
                return;
            }

            if (!AssetDatabase.IsValidFolder(DefaultAssetDir))
            {
                Directory.CreateDirectory(DefaultAssetDir);
                AssetDatabase.Refresh();
            }

            var asset = ScriptableObject.CreateInstance<ParrotLifecycleConfig>();
            var path = AssetDatabase.GenerateUniqueAssetPath(
                Path.Combine(DefaultAssetDir, DefaultAssetName).Replace("\\", "/"));
            AssetDatabase.CreateAsset(asset, path);
            AssetDatabase.SaveAssets();
            AssetDatabase.Refresh();

            Selection.activeObject = asset;
            EditorGUIUtility.PingObject(asset);
            Debug.Log($"[ParrotLifecycleConfig] created at {path}");
        }

        private static ParrotLifecycleConfig LoadFirst()
        {
            var guids = AssetDatabase.FindAssets($"t:{nameof(ParrotLifecycleConfig)}");
            foreach (var guid in guids)
            {
                var path = AssetDatabase.GUIDToAssetPath(guid);
                var asset = AssetDatabase.LoadAssetAtPath<ParrotLifecycleConfig>(path);
                if (asset != null) return asset;
            }
            return null;
        }
    }
}
#endif
