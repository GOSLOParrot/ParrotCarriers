using System;
using UnityEditor;
using UnityEditor.SceneManagement;
using UnityEngine;
using UnityEngine.EventSystems;
using UnityEngine.SceneManagement;
using Unity.XR.CoreUtils;

/// <summary>
/// <b>Testing/Editor</b> — incrementally wires the open scene for Sprint 3 (AR + LiveKit receivers + ParrotDiagnostics).
/// </summary>
public static class Sprint3SceneAugment
{
    private const string MenuPath = "Parrot/Sprint3 — Augment Open Scene (AR + receivers)";

    private static class ArTypes
    {
        private const string AssemblyName = "Unity.XR.ARFoundation";

        public static readonly Type Session = Type.GetType($"UnityEngine.XR.ARFoundation.ARSession, {AssemblyName}");
        public static readonly Type PlaneManager = Type.GetType($"UnityEngine.XR.ARFoundation.ARPlaneManager, {AssemblyName}");
        public static readonly Type RaycastManager = Type.GetType($"UnityEngine.XR.ARFoundation.ARRaycastManager, {AssemblyName}");
        public static readonly Type AnchorManager = Type.GetType($"UnityEngine.XR.ARFoundation.ARAnchorManager, {AssemblyName}");
        public static readonly Type CameraManager = Type.GetType($"UnityEngine.XR.ARFoundation.ARCameraManager, {AssemblyName}");
        public static readonly Type CameraBackground = Type.GetType($"UnityEngine.XR.ARFoundation.ARCameraBackground, {AssemblyName}");

        public static bool Available => Session != null && PlaneManager != null && CameraManager != null;

        public static Component FindInScene(Type type, Scene scene)
        {
            if (type == null)
                return null;
            foreach (var obj in Resources.FindObjectsOfTypeAll(type))
            {
                if (obj is not Component c)
                    continue;
                if (!c.gameObject.scene.IsValid() || c.gameObject.scene != scene)
                    continue;
                if (EditorUtility.IsPersistent(c.gameObject))
                    continue;
                return c;
            }

            return null;
        }

        public static Component GetOrAddComponent(GameObject go, Type type)
        {
            if (type == null)
                return null;
            var existing = go.GetComponent(type);
            if (existing != null)
                return existing;
            return Undo.AddComponent(go, type);
        }
    }

    [MenuItem(MenuPath)]
    public static void Augment()
    {
        if (!ArTypes.Available)
        {
            EditorUtility.DisplayDialog(
                "Sprint3 Scene Augment",
                "Could not load AR Foundation types (Unity.XR.ARFoundation). Ensure package com.unity.xr.arfoundation is installed and let the Editor finish compiling, then retry.",
                "OK");
            return;
        }

        var scene = SceneManager.GetActiveScene();
        if (!scene.isLoaded)
        {
            EditorUtility.DisplayDialog("Sprint3 Scene Augment", "No active scene.", "OK");
            return;
        }

        if (!EditorUtility.DisplayDialog(
                "Sprint3 Scene Augment",
                "This will add AR Session, XR Origin + AR camera, TapToPlace, VideoTierReceiver, TokenService, and SceneProfileManager to the OPEN scene.\n\n" +
                "Disable the old \"Main Camera\" if an AR camera is created.\n\nContinue?",
                "Yes", "Cancel"))
            return;

        Undo.IncrementCurrentGroup();
        Undo.SetCurrentGroupName("Sprint3 AR augment");

        if (UnityEngine.Object.FindObjectOfType<EventSystem>() == null)
        {
            var es = new GameObject("EventSystem");
            Undo.RegisterCreatedObjectUndo(es, "EventSystem");
            es.AddComponent<EventSystem>();
            es.AddComponent<StandaloneInputModule>();
        }

        if (UnityEngine.Object.FindObjectOfType<TokenService>() == null)
        {
            var go = new GameObject("TokenService");
            Undo.RegisterCreatedObjectUndo(go, "TokenService");
            go.AddComponent<TokenService>();
        }

        if (UnityEngine.Object.FindObjectOfType<SceneProfileManager>() == null)
        {
            var go = new GameObject("SceneProfileManager");
            Undo.RegisterCreatedObjectUndo(go, "SceneProfileManager");
            go.AddComponent<SceneProfileManager>();
        }

        var liveKit = GameObject.Find("LiveKitManager");
        if (liveKit != null && liveKit.GetComponent<VideoTierReceiver>() == null)
            Undo.AddComponent<VideoTierReceiver>(liveKit);

        var hadOrigin = UnityEngine.Object.FindObjectOfType<XROrigin>() != null;

        var oldMain = GameObject.Find("Main Camera");
        if (oldMain != null && !hadOrigin)
        {
            Undo.RecordObject(oldMain, "Disable old Main Camera");
            oldMain.tag = "Untagged";
            var oldAl = oldMain.GetComponent<AudioListener>();
            if (oldAl != null)
            {
                Undo.RecordObject(oldAl, "Disable old AudioListener");
                oldAl.enabled = false;
            }

            oldMain.SetActive(false);
        }

        if (ArTypes.FindInScene(ArTypes.Session, scene) == null)
        {
            var sessionGo = new GameObject("AR Session");
            Undo.RegisterCreatedObjectUndo(sessionGo, "AR Session");
            ArTypes.GetOrAddComponent(sessionGo, ArTypes.Session);
        }

        XROrigin xr = UnityEngine.Object.FindObjectOfType<XROrigin>();
        Camera arCam;
        if (xr != null)
        {
            var root = xr.gameObject;
            arCam = xr.Camera != null ? xr.Camera : xr.GetComponentInChildren<Camera>();
            if (arCam != null)
            {
                ArTypes.GetOrAddComponent(arCam.gameObject, ArTypes.CameraManager);
                ArTypes.GetOrAddComponent(arCam.gameObject, ArTypes.CameraBackground);
                if (arCam.GetComponent<AudioListener>() == null)
                    Undo.AddComponent<AudioListener>(arCam.gameObject);
            }

            ArTypes.GetOrAddComponent(root, ArTypes.PlaneManager);
            ArTypes.GetOrAddComponent(root, ArTypes.RaycastManager);
            ArTypes.GetOrAddComponent(root, ArTypes.AnchorManager);
            if (root.GetComponent<ARFoundationSetup>() == null)
                Undo.AddComponent<ARFoundationSetup>(root);
        }
        else
        {
            var originGo = new GameObject("XR Origin");
            Undo.RegisterCreatedObjectUndo(originGo, "XR Origin");
            var origin = originGo.AddComponent<XROrigin>();

            var floorOffset = new GameObject("Camera Floor Offset");
            Undo.RegisterCreatedObjectUndo(floorOffset, "Camera Floor Offset");
            floorOffset.transform.SetParent(originGo.transform, false);

            var camGo = new GameObject("Main Camera");
            Undo.RegisterCreatedObjectUndo(camGo, "AR Main Camera");
            camGo.tag = "MainCamera";
            camGo.transform.SetParent(floorOffset.transform, false);
            camGo.transform.localPosition = Vector3.zero;
            camGo.transform.localRotation = Quaternion.identity;

            arCam = camGo.AddComponent<Camera>();
            arCam.clearFlags = CameraClearFlags.Skybox;
            arCam.nearClipPlane = 0.1f;
            arCam.farClipPlane = 100f;

            if (camGo.GetComponent<AudioListener>() == null)
                camGo.AddComponent<AudioListener>();

            ArTypes.GetOrAddComponent(camGo, ArTypes.CameraManager);
            ArTypes.GetOrAddComponent(camGo, ArTypes.CameraBackground);

            origin.CameraFloorOffsetObject = floorOffset;
            origin.Camera = arCam;

            ArTypes.GetOrAddComponent(originGo, ArTypes.PlaneManager);
            ArTypes.GetOrAddComponent(originGo, ArTypes.RaycastManager);
            ArTypes.GetOrAddComponent(originGo, ArTypes.AnchorManager);
            if (originGo.GetComponent<ARFoundationSetup>() == null)
                Undo.AddComponent<ARFoundationSetup>(originGo);

            xr = origin;
        }

        EnsureSingleMainCamera(xr);

        var pub = UnityEngine.Object.FindObjectOfType<ARVideoPublisher>();
        if (pub != null && arCam != null)
        {
            var so = new SerializedObject(pub);
            so.FindProperty("arCamera").objectReferenceValue = arCam;
            so.FindProperty("useWebcamFallback").boolValue = false;
            so.ApplyModifiedProperties();
        }

        if (UnityEngine.Object.FindObjectOfType<TapToPlace>() == null)
        {
            var tapGo = new GameObject("TapToPlace");
            Undo.RegisterCreatedObjectUndo(tapGo, "TapToPlace");
            var tap = tapGo.AddComponent<TapToPlace>();
            var cube = GameObject.Find("ParrotCube");
            if (cube != null)
            {
                var so = new SerializedObject(tap);
                var p = so.FindProperty("gosloPrefab");
                if (p != null)
                {
                    p.objectReferenceValue = cube;
                    so.ApplyModifiedProperties();
                }
            }
        }

        if (UnityEngine.Object.FindObjectOfType<ParrotDiagnosticsLog>() == null)
        {
            var diag = new GameObject("ParrotDiagnostics");
            Undo.RegisterCreatedObjectUndo(diag, "ParrotDiagnostics");
            diag.AddComponent<ParrotDiagnosticsLog>();
            diag.AddComponent<ParrotSelfTestCoordinator>();
            diag.AddComponent<ParrotRpcRttProbe>();
            diag.AddComponent<ParrotRuntimeHud>();
        }

        EditorSceneManager.MarkSceneDirty(scene);

        Debug.Log(
            "[Sprint3SceneAugment] Done. Editor: XR Simulation (Editor tab). Android: ARCore. "
            + "Testing/Runtime: F3 HUD + parrot_diagnostics.log. Testing/Editor: Parrot/Test/Editor/* menus.");

        EditorUtility.DisplayDialog(
            "Sprint3 Scene Augment",
            "Scene updated. Save the scene.\n\n" +
            "Editor (XR Simulation): Project Settings → XR Plug-in Management → Editor → XR Simulation → Window → XR → XR Simulation.\n\n" +
            "Android: XR Plug-in Management → Android → Google ARCore → build APK.\n\n" +
            "ParrotDiagnostics (if added): Assets/Scripts/Testing/Runtime — HUD + file log.\n" +
            "More Editor tests: Parrot/Test/Editor/… (disconnect/reconnect, AR checklist).\n\n" +
            "Active Build Target can stay Standalone for this menu.",
            "OK");
    }

    private static void EnsureSingleMainCamera(XROrigin xr)
    {
        if (xr == null || xr.Camera == null)
            return;

        var main = xr.Camera;
        Undo.RecordObject(main, "XR Main Camera");
        main.tag = "MainCamera";
        main.enabled = true;

        foreach (var cam in UnityEngine.Object.FindObjectsOfType<Camera>())
        {
            if (cam == main)
                continue;
            if (!cam.CompareTag("MainCamera"))
                continue;
            Undo.RecordObject(cam.gameObject, "Demote duplicate MainCamera");
            cam.tag = "Untagged";
            cam.enabled = false;
            var al = cam.GetComponent<AudioListener>();
            if (al != null)
            {
                Undo.RecordObject(al, "Disable duplicate AudioListener");
                al.enabled = false;
            }
        }
    }
}
