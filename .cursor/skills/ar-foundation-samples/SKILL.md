---
name: ar-foundation-samples
description: Use when looking for concrete AR Foundation 5.1 sample patterns (Unity 2022.3 LTS) — XRCpuImage frame grab, plane detection, image tracking, anchor placement, face/body tracking, Android runtime permissions, XR Simulation setup. Reference implementation from ar-foundation-samples repo.
---

# AR Foundation Samples (Unity 2022.3 LTS, AR Foundation 5.1) Documentation

This skill provides comprehensive documentation and analysis for the `ar-foundation-samples` codebase, specifically targeting Unity 2022.3 LTS with AR Foundation 5.1.x. It includes detailed explanations of various AR features, API usage patterns, configuration best practices, and project structure, all derived from a local code analysis.

## When to Use This Skill

Use this skill when you need to:
*   Understand the implementation details and usage patterns of core AR Foundation 5.1 features.
*   Find practical C# code examples for common AR tasks like plane detection, image tracking, camera access, and anchor placement.
*   Learn how to configure AR Foundation for different platforms (ARCore, ARKit, OpenXR) and manage runtime permissions.
*   Explore advanced AR functionalities such as face tracking, body tracking, meshing, and environment probes.
*   Set up and utilize XR Simulation for efficient development and testing in the Unity editor.
*   Review project-specific documentation (README, CONTRIBUTING, LICENSE) and configuration files.

## ⚡ Quick Reference

This section provides practical, short examples demonstrating common AR Foundation tasks, drawing from the codebase's explicit focus and documented patterns.

### 1. Enabling XR Simulation for Editor Testing (Procedural)

For rapid development and testing without a physical device, enable XR Simulation:
1.  Go to `Edit > Project Settings > XR Plug-in Management`.
2.  In the `XR Plug-in Management` window, ensure `XR Simulation` is enabled for the Editor target.
3.  Use the `XR Simulation` window (`Window > XR > XR Simulation`) to inject virtual planes, point clouds, and images, and navigate the simulated environment using WASD.

### 2. Subscribing to AR Camera Frame Events

To process camera frames as they are received, subscribe to the `ARCameraManager.frameReceived` event. This is crucial for real-time computer vision or custom rendering.

```csharp
using UnityEngine;
using UnityEngine.XR.ARFoundation;
using UnityEngine.XR.ARSubsystems;

public class CameraFrameProcessor : MonoBehaviour
{
    [SerializeField] private ARCameraManager m_CameraManager;

    void OnEnable()
    {
        if (m_CameraManager != null)
        {
            m_CameraManager.frameReceived += OnCameraFrameReceived;
        }
    }

    void OnDisable()
    {
        if (m_CameraManager != null)
        {
            m_CameraManager.frameReceived -= OnCameraFrameReceived;
        }
    }

    void OnCameraFrameReceived(ARCameraFrameEventArgs eventArgs)
    {
        // Process the camera frame data here
        // e.g., access raw image data via XRCpuImage
        Debug.Log("Camera frame received!");
    }
}
```

### 3. Acquiring and Processing `XRCpuImage`

For CPU-based image processing (e.g., for WebRTC or computer vision), acquire an `XRCpuImage` from the `ARCameraManager`.

```csharp
using UnityEngine;
using UnityEngine.XR.ARFoundation;
using UnityEngine.XR.ARSubsystems;

public class CpuImageAcquirer : MonoBehaviour
{
    [SerializeField] private ARCameraManager m_CameraManager;

    void Update()
    {
        if (m_CameraManager.TryAcquireLatestCpuImage(out XRCpuImage cpuImage))
        {
            // Example: Log image details, then dispose
            Debug.Log($"Acquired CPU Image: Width={cpuImage.width}, Height={cpuImage.height}, Format={cpuImage.format}");

            // Access pixel data (e.g., convert to byte array)
            // Example:
            // var conversionParams = new XRCpuImage.ConversionParams
            // {
            //     inputRect = new RectInt(0, 0, cpuImage.width, cpuImage.height),
            //     outputDimensions = new Vector2Int(cpuImage.width, cpuImage.height),
            //     outputFormat = TextureFormat.RGB24, // Or desired format
            //     transformation = XRCpuImage.Transformation.None
            // };
            // int bufferSize = cpuImage.Get:'planeCount' * cpuImage.width * cpuImage.height * 3; // Approx. for RGB24
            // var rawImageData = new byte[bufferSize];
            // cpuImage.Convert(conversionParams, new System.IntPtr(rawImageData), bufferSize);
            // ... process rawImageData ...

            cpuImage.Dispose();
        }
    }
}
```

### 4. Raycasting to Place Virtual Objects on a Plane

Use `ARRaycastManager` to detect planes and place virtual content accurately in the AR scene.

```csharp
using System.Collections.Generic;
using UnityEngine;
using UnityEngine.XR.ARFoundation;
using UnityEngine.XR.ARSubsystems;

public class TapToPlaceObject : MonoBehaviour
{
    [SerializeField] private GameObject m_PlacedObjectPrefab;
    [SerializeField] private ARRaycastManager m_RaycastManager;
    static List<ARRaycastHit> s_Hits = new List<ARRaycastHit>();

    void Update()
    {
        if (Input.touchCount > 0 && Input.GetTouch(0).phase == TouchPhase.Began)
        {
            if (m_RaycastManager.Raycast(Input.GetTouch(0).position, s_Hits, TrackableType.PlaneWithinPolygon))
            {
                // Raycast hits a plane, place object at the hit pose
                Pose hitPose = s_Hits[0].pose;
                Instantiate(m_PlacedObjectPrefab, hitPose.position, hitPose.rotation);
            }
        }
    }
}
```

### 5. Creating an `ARAnchor` to Attach a GameObject

`ARAnchor` firmly attaches a GameObject to a real-world position, ensuring it remains stable even as the device moves.

```csharp
using UnityEngine;
using UnityEngine.XR.ARFoundation;
using UnityEngine.XR.ARSubsystems;

public class AnchorCreator : MonoBehaviour
{
    [SerializeField] private GameObject m_AnchorPrefab;
    [SerializeField] private ARRaycastManager m_RaycastManager;
    [SerializeField] private ARAnchorManager m_AnchorManager;
    static List<ARRaycastHit> s_Hits = new List<ARRaycastHit>();

    void Update()
    {
        if (Input.touchCount > 0 && Input.GetTouch(0).phase == TouchPhase.Began)
        {
            if (m_RaycastManager.Raycast(Input.GetTouch(0).position, s_Hits, TrackableType.PlaneWithinPolygon))
            {
                Pose hitPose = s_Hits[0].pose;
                ARPlane hitPlane = m_AnchorManager.subsystem.Get'>trackableFactory'() => new ARAnchor(s_Hits[0].trackableId);

                // Option 1: Create a simple anchor at the hit pose
                // GameObject newAnchorGO = new GameObject("ARAnchor");
                // newAnchorGO.transform.position = hitPose.position;
                // newAnchorGO.transform.rotation = hitPose.rotation;
                // ARAnchor arAnchor = newAnchorGO.AddComponent<ARAnchor>();

                // Option 2: Attach an anchor to a detected plane (more stable)
                if (hitPlane != null)
                {
                    ARAnchor arAnchor = m_AnchorManager.AttachAnchor(hitPlane, hitPose);
                    if (arAnchor != null)
                    {
                        Instantiate(m_AnchorPrefab, arAnchor.transform); // Parent prefab to anchor
                    }
                }
            }
        }
    }
}
```

### 6. Requesting Android Runtime Permissions

For ARCore on Android, critical permissions like camera access must be requested at runtime before initializing `ARSession`.

```csharp
using UnityEngine;
using System.Collections;
#if UNITY_ANDROID
using UnityEngine.Android;
#endif

public class AndroidPermissionRequester : MonoBehaviour
{
    void Start()
    {
        RequestPermissions();
    }

    void RequestPermissions()
    {
#if UNITY_ANDROID
        // Request Camera permission
        if (!Permission.HasUserAuthorizedPermission(Permission.Camera))
        {
            Permission.RequestUserPermission(Permission.Camera);
        }

        // Request Microphone permission if audio recording is needed (e.g., for LiveKit)
        if (!Permission.HasUserAuthorizedPermission(Permission.Microphone))
        {
            Permission.RequestUserPermission(Permission.Microphone);
        }
        // ... request other necessary permissions
#else
        Debug.Log("Android permissions not applicable on this platform.");
#endif
    }
}
```

### 7. Example Configuration: Stale Bot GitHub Action

Configuration files define project-specific settings. Here's a snippet from a GitHub action configuration.

```yaml
# .github/stale.yml
days-before-stale: 60
days-before-close: 7
stale-issue-message: >
  This issue has been automatically marked as stale because it has not had
  recent activity. It will be closed if no further activity occurs.
  Thank you for your contributions.
stale-pr-message: >
  This PR has been automatically marked as stale because it has not had
  recent activity. It will be closed if no further activity occurs.
  Thank you for your contributions.
```

## Key Concepts

Understanding these core concepts is essential for working with AR Foundation 5.1:

*   **AR Foundation:** Unity's cross-platform framework for building augmented reality experiences, unifying APIs across ARCore (Android), ARKit (iOS), and OpenXR (HoloLens, Meta Quest).
*   **ARSession:** The central component that manages the AR experience, including device tracking, session lifecycle (pause/resume/reset), and communication with the underlying AR provider.
*   **Trackables:** Real-world entities that AR Foundation can detect and track, such as:
    *   **Planes (`ARPlane`):** Flat surfaces in the environment.
    *   **Point Clouds (`ARPointCloud`):** Sparse collections of feature points used for spatial understanding.
    *   **Images (`ARTrackedImage`):** Pre-defined 2D images.
    *   **Objects (`ARTrackedObject`):** Pre-defined 3D objects.
    *   **Faces (`ARFace`):** Human faces.
    *   **Bodies (`ARHumanBody`):** Human bodies (2D/3D skeletons).
*   **ARAnchor:** A point in the real world that AR Foundation attempts to keep stable. Attaching virtual content to an anchor helps it maintain its position and orientation in the AR scene.
*   **ARRaycastManager:** Used to perform raycasts from screen space into the real world to detect intersections with trackables or other real-world geometry.
*   **ARCameraManager:** Manages the device's camera feed, providing access to camera intrinsics, light estimation data, and CPU/GPU camera images.
*   **XRCpuImage:** A CPU-accessible representation of the camera frame, useful for image processing, computer vision, or streaming.
*   **Light Estimation:** Provides real-time information about the ambient light in the physical environment, allowing virtual objects to be lit more realistically.
*   **Occlusion:** The ability for real-world objects to visually block or "occlude" virtual content, enhancing realism. Achieved using depth images or meshing.
*   **Environment Probes:** Captures the real-world environment as a 3D texture, used for realistic reflections on virtual objects.
*   **XR Plug-in Management:** Unity's system for managing and enabling different XR providers (like ARCore, ARKit, OpenXR, XR Simulation) for various build targets.
*   **XR Simulation:** An editor-only feature that allows developers to simulate AR experiences directly in the Unity editor without needing to deploy to a physical device. Essential for quick iteration.

## 📚 Available References

This skill includes detailed reference documentation, organized into the following categories:

*   **Configuration Patterns (`references/config_patterns/`):** Detailed analysis of configuration files found in the project.
*   **Project Documentation (`references/documentation/`):** Extracted markdown files from the project, including:
    *   `CONTRIBUTING.md`: Guidelines for contributing to the project.
    *   `LICENSE.md`: Licensing information for the AR Foundation Samples.
    *   `pull_request_template.md`: Template for pull requests.
    *   `README.md`: Overview of the AR Foundation Samples, available scenes, and usage instructions.
    *   `bug_report.md`: Template for submitting bug reports.
    *   `feature_request.md`: Template for requesting new features.
    *   `how-to.md`: Template for "how-to" questions.
*   **Dependencies (`references/dependencies/`):** (Not explicitly provided in current content, but mentioned in `CURRENT DOCUMENTATION`)
*   **Patterns (`references/patterns/`):** (Not explicitly provided in current content, but mentioned in `CURRENT DOCUMENTATION`)

## Practical Usage Guidance

To effectively navigate and utilize this documentation:

1.  **Start with the `README.md` (`references/documentation/README.md`):** This file provides a high-level overview of the `AR Foundation Samples` project, its dependencies, version compatibility, and a comprehensive table of contents for all included sample scenes. It's the best entry point to understand what features are demonstrated.
2.  **Explore Specific Sample Scenes:** The `README.md` breaks down each sample scene by feature (e.g., "Plane Detection," "Image Tracking," "Face Tracking"). For any given feature, the `README` often describes the core concept and points to relevant C# scripts (e.g., `CpuImageSample.cs`, `PlaneDetectionController.cs`). While the `.cs` files themselves are not embedded here, the descriptions give you the *context* and *API names* to look for.
3.  **Consult the Quick Reference for Common Tasks:** Use the "⚡ Quick Reference" section above for direct, actionable C# code patterns for frequent AR Foundation operations.
4.  **Review Configuration Files:** The `references/config_patterns/config_patterns.md` details various configuration files like `.github\stale.yml`, `Assets\Samples\...\.sample.json`, `Packages\manifest.json`, and `ProjectSettings\SceneTemplateSettings.json`. These reveal how the project is configured and integrated within Unity and its ecosystem.
5.  **Understand Project Governance:** The `CONTRIBUTING.md` and `pull_request_template.md` (found under `references/documentation/`) provide insight into how the original repository manages contributions and feedback.
6.  **Prioritize AR Foundation 5.1 and Unity 2022.3 LTS:** This documentation is strictly focused on these versions. Pay close attention to any version-specific details mentioned in the `README` or other documents. Avoid looking for features or APIs specific to newer or older versions of AR Foundation.
7.  **Leverage XR Simulation:** The `skill_seeker_focus.md` emphasizes XR Simulation. Remember that many AR scenarios can be prototyped and tested in the Editor using this feature before deploying to a device.