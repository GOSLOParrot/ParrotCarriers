---
name: ar-foundation-api
description: Use when working with Unity AR Foundation 5.1.x / 5.2.x API (workspace lock: Unity 2022.3.62f3 + AR Foundation/ARCore/ARKit 5.2.2) — XRCameraSubsystem, ARFaceManager, ARPlaneManager, ARRaycastManager, ARAnchor, XRCpuImage, XR Simulation editor workflow. Reject any AR Foundation 6.x or Unity 6 references.
---

# Ar-Foundation-Api Skill

> ⚠️ **NOTICE (2026-04-29)** — 工作区版本锁已从 AR Foundation **5.1.5 升至 5.2.2**（含 ARCore/ARKit），原因是 ARCore XR Plugin 5.2.2 才把 `libarcore_sdk_c.so` 改 16KB ELF 对齐，满足 Android 15+ Play 商店硬性要求。本 SKILL 文档主体仍以 5.1.x 蒸馏，**5.1 → 5.2 我们用到的 API 面（`XRCameraSubsystem` / `ARCameraManager.frameReceived` / `ARCameraBackground.material` / `ARPlane.extents` / `XRCpuImage` / XR Simulation）未变**，可继续作为参考。详见 `.cursor/rules/ar-foundation.mdc` §0–§1。

This skill provides comprehensive documentation for **Unity AR Foundation 5.1.x / 5.2.x**, specifically targeting **Unity 2022.3 LTS** (currently 2022.3.62f3; project packages pinned to AR Foundation / ARCore / ARKit 5.2.2). It covers various AR Foundation features, APIs, and best practices.

## Governance Rules
- **STRICTLY Unity 2022.3 LTS + AR Foundation 5.2.x project lock; 5.1.x docs remain API-shape reference where unchanged.**
- **REJECT any mention of Unity 6, AR Foundation 6.x, XRResultStatus, or URP Compatibility Mode removal.**
- **Never use deprecated SubsystemManager APIs from 4.x.**
- **Always use XR Simulation for editor testing** — never require a physical device for dev iteration.

## When to Use This Skill

This skill should be triggered when:
- Working with Unity's AR Foundation 5.1.x for augmented reality development.
- Asking about AR Foundation 5.1 features or APIs.
- Implementing AR Foundation 5.1 solutions for plane detection, face tracking, raycasting, and camera access.
- Debugging AR Foundation 5.1 code in Unity 2022.3 LTS.
- Learning AR Foundation 5.1 best practices for development and editor workflow (e.g., XR Simulation).

## Key Concepts

AR Foundation is a framework that unifies the various AR SDKs (ARCore, ARKit, OpenXR) into a single API surface for Unity developers.

-   **AR Session**: Controls the lifecycle of an AR experience, enabling or disabling AR features on the target platform.
-   **XR Origin**: The central GameObject in an AR scene that manages the AR camera and coordinate space.
-   **Trackables**: Virtual representations of real-world features that AR devices can detect and track. Examples include `ARFace`, `ARPlane`, `ARPointCloud`, and `ARAnchor`.
-   **Managers**: Components (e.g., `ARPlaneManager`, `ARFaceManager`, `ARRaycastManager`) that provide scripting interfaces for AR features, creating and managing `Trackables` in your scene.
-   **XR Simulation**: A powerful feature for testing AR Foundation apps directly in the Unity Editor without a physical device, allowing for injection of virtual planes, point clouds, and images.

## Quick Reference

Here are practical code examples for common AR Foundation tasks:

### 1. Checking XRCameraSubsystem Support
Determine if the platform supports the camera subsystem at runtime.

```csharp
void Start()
{
    if (LoaderUtility
            .GetActiveLoader()?
            .GetLoadedSubsystem<XRCameraSubsystem>() != null)
    {
        // XRCameraSubsystem was loaded. The platform supports the camera subsystem.
    }
}
```

### 2. Checking XRFaceSubsystem Support
Determine if the platform supports face tracking at runtime.

```csharp
void Start()
{
    if (LoaderUtility
            .GetActiveLoader()?
            .GetLoadedSubsystem<XRFaceSubsystem>() != null)
    {
        // XRFaceSubsystem was loaded. The platform supports face detection.
    }
}
```

### 3. Subscribing to ARFaceManager Changes
Handle added, updated, or removed faces detected by the `ARFaceManager`.

```csharp
public void OnFacesChanged(ARFacesChangedEventArgs changes)
{
    foreach (var face in changes.added)
    {
        // Handle newly detected faces
        Debug.Log($"Face added: {face.trackableId}");
    }

    foreach (var face in changes.updated)
    {
        // Handle updated face data (e.g., blend shapes, pose)
        Debug.Log($"Face updated: {face.trackableId}");
    }

    foreach (var face in changes.removed)
    {
        // Handle removed faces
        Debug.Log($"Face removed: {face.trackableId}");
    }
}

void SubscribeToFacesChanged()
{
    // Ensure you have an ARFaceManager component in your scene
    var manager = Object.FindObjectOfType<ARFaceManager>();
    if (manager != null)
    {
        manager.facesChanged += OnFacesChanged;
    }
}
```

### 4. Subscribing to ARPlaneManager Changes
Handle added, updated, or removed planes detected by the `ARPlaneManager`.

```csharp
public void OnPlanesChanged(ARPlanesChangedEventArgs changes)
{
    foreach (var plane in changes.added)
    {
        // Handle newly detected planes
        Debug.Log($"Plane added: {plane.trackableId}");
    }

    foreach (var plane in changes.updated)
    {
        // Handle updated plane data (e.g., boundary, pose)
        Debug.Log($"Plane updated: {plane.trackableId}");
    }

    foreach (var plane in changes.removed)
    {
        // Handle removed planes
        Debug.Log($"Plane removed: {plane.trackableId}");
    }
}

void SubscribeToPlanesChanged()
{
    // Ensure you have an ARPlaneManager component in your scene
    var manager = Object.FindObjectOfType<ARPlaneManager>();
    if (manager != null)
    {
        manager.planesChanged += OnPlanesChanged;
    }
}
```

### 5. Performing a Screen-Point Raycast
Cast a ray from a screen position (e.g., touch input) to detect AR trackables.

```csharp
[SerializeField]
ARRaycastManager m_RaycastManager; // Assign in Inspector

List<ARRaycastHit> m_Hits = new List<ARRaycastHit>();

void OnEnable()
{
    // Enable Enhanced Touch Input System if used
    InputSystem.EnhancedTouch.EnhancedTouchSupport.Enable();
}

void OnDisable()
{
    InputSystem.EnhancedTouch.EnhancedTouchSupport.Disable();
}

void Update()
{
    var activeTouches = InputSystem.EnhancedTouch.Touch.activeTouches;
    if (activeTouches.Count == 0)
        return;

    // Perform raycast on the first active touch
    if (m_RaycastManager.Raycast(activeTouches[0].screenPosition, m_Hits, TrackableType.PlaneWithinPolygon))
    {
        // At least one hit was found. Process m_Hits list.
        Debug.Log($"Raycast hit {m_Hits.Count} trackables.");
        // Example: Handle the first hit
        HandleRaycast(m_Hits[0]);
    }
}
```

### 6. Handling ARRaycastHit Results
Determine what type of trackable was hit by a raycast and access its properties.

```csharp
void HandleRaycast(ARRaycastHit hit)
{
    if (hit.trackable is ARPlane plane)
    {
        // Do something with the detected plane
        Debug.Log($"Raycast hit a plane with alignment: {plane.alignment}");
        // Example: Instantiate an anchor at the hit pose
        // m_AnchorManager.AddAnchor(hit.pose);
    }
    else
    {
        // Log the type of trackable hit if it's not a plane
        Debug.Log($"Raycast hit a {hit.hitType}");
    }
}
```

## Reference Files

This skill includes comprehensive documentation extracted from official sources, organized in `references/`:

-   **Packages.md** - Detailed documentation for various AR Foundation components and their usage.

Use `view` to read specific reference files when detailed information is needed.

## Working with This Skill

### For Beginners
Start by reviewing the "Key Concepts" section to understand fundamental AR Foundation terminology. Then, explore `Packages.md` for introductory topics like `AR Session` setup.

### For Specific Features
Consult `Packages.md` for detailed information on individual AR Foundation components and features such as:
-   `AR Face component` and `AR Face Manager component` for face tracking.
-   `AR Plane component` and `AR Plane Manager component` for plane detection.
-   `AR Raycast Manager component` for hit testing.
-   `AR Mesh Manager component` for environment meshing.
-   `AR Occlusion Manager component` for realistic rendering.
-   `AR Point Cloud Manager component` for understanding feature points.
-   `AR Participant Manager component` for collaborative sessions.

### For Code Examples
The "Quick Reference" section above provides practical, short code snippets for common tasks. For more elaborate examples, refer to the `Packages.md` file, which contains examples directly from the official documentation.

### For Editor Workflow and XR Simulation
Focus on the guidance provided by the governance rules, emphasizing `XR Simulation` for development iteration.

## Resources

### references/
Organized documentation extracted from official sources. These files contain:
-   Detailed explanations of AR Foundation components.
-   Code examples with language annotations.
-   Links to original documentation for further reading.
-   Table of contents for quick navigation within the file.

### scripts/
Add helper scripts here for common automation tasks.

### assets/
Add templates, boilerplate, or example projects here.

## Notes

-   This skill was automatically generated from official documentation.
-   Reference files preserve the structure and examples from source documents.
-   Code examples include language detection for better syntax highlighting.
-   Quick reference patterns are extracted from common usage examples in the docs.
-   This skill is specifically curated for **Unity 2022.3 LTS** and **AR Foundation 5.1.x**.

## Updating

To refresh this skill with updated documentation:
1.  Re-run the scraper with the same configuration.
2.  The skill will be rebuilt with the latest information.
