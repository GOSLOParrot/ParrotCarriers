using UnityEditor;
using UnityEditor.SceneManagement;
using UnityEngine;
using UnityEngine.SceneManagement;

/// <summary>
/// One-click Dev scene creation for ParrotCarriers Phase 1.
/// Menu: Parrot > Setup Dev Scene
/// Creates: Main Camera, Directional Light, LiveKitManager, ParrotCube.
/// </summary>
public static class DevSceneSetup
{
    [MenuItem("Parrot/Setup Dev Scene")]
    public static void SetupDevScene()
    {
        var scene = EditorSceneManager.NewScene(NewSceneSetup.EmptyScene, NewSceneMode.Single);

        // --- Camera ---
        var camGo = new GameObject("Main Camera");
        camGo.tag = "MainCamera";
        var cam = camGo.AddComponent<Camera>();
        cam.clearFlags = CameraClearFlags.Skybox;
        cam.fieldOfView = 60f;
        camGo.transform.position = new Vector3(0f, 1.5f, -5f);
        camGo.transform.rotation = Quaternion.Euler(10f, 0f, 0f);
        camGo.AddComponent<AudioListener>();

        // --- Light ---
        var lightGo = new GameObject("Directional Light");
        var light = lightGo.AddComponent<Light>();
        light.type = LightType.Directional;
        light.color = new Color(1f, 0.96f, 0.84f);
        light.intensity = 1f;
        lightGo.transform.rotation = Quaternion.Euler(50f, -30f, 0f);

        // --- Ground plane (visual reference) ---
        var ground = GameObject.CreatePrimitive(PrimitiveType.Plane);
        ground.name = "Ground";
        ground.transform.position = Vector3.zero;
        ground.transform.localScale = new Vector3(2f, 1f, 2f);
        var groundMat = new Material(Shader.Find("Standard"));
        groundMat.color = new Color(0.25f, 0.3f, 0.25f);
        ground.GetComponent<Renderer>().sharedMaterial = groundMat;

        // --- LiveKitManager ---
        var lkGo = new GameObject("LiveKitManager");
        lkGo.AddComponent<RoomManager>();

        // --- ParrotCube (dev placeholder) ---
        var parrotGo = GameObject.CreatePrimitive(PrimitiveType.Cube);
        parrotGo.name = "ParrotCube";
        parrotGo.transform.position = new Vector3(0f, 1f, 0f);
        parrotGo.transform.localScale = new Vector3(0.5f, 0.5f, 0.5f);
        var parrotMat = new Material(Shader.Find("Standard"));
        parrotMat.color = new Color(0.2f, 0.8f, 0.3f);
        parrotGo.GetComponent<Renderer>().sharedMaterial = parrotMat;
        parrotGo.AddComponent<ParrotController>();
        parrotGo.AddComponent<ParrotRpcHandler>();

        // --- Save scene ---
        string scenePath = "Assets/Scenes/Dev.unity";
        EditorSceneManager.SaveScene(scene, scenePath);
        EditorSceneManager.OpenScene(scenePath);

        Debug.Log("[DevSceneSetup] Dev scene created and saved to " + scenePath);
        Debug.Log("[DevSceneSetup] Next: paste a token into LiveKitManager > Join Token, then Play.");

        Selection.activeGameObject = lkGo;
        EditorGUIUtility.PingObject(lkGo);
    }
}
