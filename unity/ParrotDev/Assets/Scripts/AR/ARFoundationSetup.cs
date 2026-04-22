using UnityEngine;

#if UNITY_AR_FOUNDATION
using UnityEngine.XR.ARFoundation;
using UnityEngine.XR.ARSubsystems;
#endif

/// <summary>
/// Sprint 3 T-U1 (S3.A2-A3): AR Foundation plane detection bootstrap.
///
/// Configures ARPlaneManager for horizontal planes only (table/desk detection).
/// Shows/hides plane visualisers and enforces minimum area filtering via events.
///
/// Attach to the AR Session Origin GameObject. Requires:
///   - ARSession (parent or sibling)
///   - ARSessionOrigin (or XROrigin in AR Foundation 5.x)
///   - ARPlaneManager component
///   - ARRaycastManager component
///   - ARAnchorManager component (optional, for anchor creation)
/// </summary>
public class ARFoundationSetup : MonoBehaviour
{
#if UNITY_AR_FOUNDATION
    [Header("Plane Detection")]
    [Tooltip("Plane visualiser prefab. Leave null to use ARPlaneManager default.")]
    [SerializeField] private GameObject planePrefab;
    [Tooltip("Show plane mesh overlay during AR session.")]
    [SerializeField] private bool showPlaneVisuals = true;
    [Tooltip("Minimum plane area (m²) to show. Smaller planes are still tracked, just hidden.")]
    [SerializeField] private float minVisibleArea = 0.09f;

    private ARPlaneManager _planeManager;
    private ARSession _arSession;

    void Awake()
    {
        _planeManager = GetComponent<ARPlaneManager>();
        _arSession = FindObjectOfType<ARSession>();

        if (_planeManager == null)
        {
            Debug.LogWarning("[ARFoundationSetup] ARPlaneManager not found on this GameObject");
            return;
        }

        // Sprint 3 constraint: horizontal planes only (desk/table surface).
        // Walls and floors are out of scope (ar_feature_implementation_plan §S3.A3).
        _planeManager.requestedDetectionMode = PlaneDetectionMode.Horizontal;

        if (planePrefab != null)
            _planeManager.planePrefab = planePrefab;

        _planeManager.planesChanged += OnPlanesChanged;
        Debug.Log("[ARFoundationSetup] Configured: Horizontal plane detection");
    }

    void OnEnable()
    {
        if (_arSession != null)
            ARSession.stateChanged += OnARSessionStateChanged;
    }

    void OnDisable()
    {
        ARSession.stateChanged -= OnARSessionStateChanged;
        if (_planeManager != null)
            _planeManager.planesChanged -= OnPlanesChanged;
    }

    private void OnARSessionStateChanged(ARSessionStateChangedEventArgs args)
    {
        Debug.Log($"[ARFoundationSetup] AR session state → {args.state}");
        switch (args.state)
        {
            case ARSessionState.SessionTracking:
                Debug.Log("[ARFoundationSetup] AR tracking active — plane detection running");
                break;
            case ARSessionState.Unsupported:
                Debug.LogWarning("[ARFoundationSetup] ARCore not supported on this device");
                break;
        }
    }

    private void OnPlanesChanged(ARPlanesChangedEventArgs args)
    {
        // Show only planes that meet minimum area threshold
        foreach (var plane in args.added)
            UpdatePlaneVisibility(plane);
        foreach (var plane in args.updated)
            UpdatePlaneVisibility(plane);
        foreach (var plane in args.removed)
            Debug.Log($"[ARFoundationSetup] Plane removed: {plane.trackableId}");
    }

    private void UpdatePlaneVisibility(ARPlane plane)
    {
        if (!showPlaneVisuals)
        {
            plane.gameObject.SetActive(false);
            return;
        }

        float area = 4f * plane.extents.x * plane.extents.z;
        bool visible = area >= minVisibleArea;
        plane.gameObject.SetActive(visible);

        if (visible)
            Debug.Log($"[ARFoundationSetup] Plane visible: {plane.trackableId} area={area:F3}m²");
    }
#else
    void Start()
    {
        Debug.Log("[ARFoundationSetup] AR Foundation not available — desktop webcam mode active");
    }
#endif
}
