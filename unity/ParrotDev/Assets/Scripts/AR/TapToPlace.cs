using System.Collections.Generic;
using UnityEngine;

#if UNITY_AR_FOUNDATION
using UnityEngine.XR.ARFoundation;
using UnityEngine.XR.ARSubsystems;
#endif

/// <summary>
/// Sprint 3 T-U1: Tap-to-place GOSLO on a detected horizontal AR plane.
///
/// On first tap on a valid plane:
///   1. Raycast into ARPlaneManager planes
///   2. Validate surface area >= MIN_PLANE_AREA (0.3×0.3m = 0.09 m²)
///   3. Instantiate GOSLO prefab (or move existing) at hit point
///   4. Create ARAnchor at placement point so GOSLO tracks the surface
///   5. Notify AnimationDriver to play "fly in from above" sequence
///   6. Send setScene RPC to Brain with anchor world position
///
/// Dev fallback (Editor without AR): click in Game view → raycast against
/// virtual y=0 plane, no ARAnchor (Desktop Webcam path).
/// </summary>
public class TapToPlace : MonoBehaviour
{
    [Header("Placement")]
    [Tooltip("GOSLO prefab (or existing GO in scene to move)")]
    [SerializeField] private GameObject gosloPrefab;
    [Tooltip("Minimum valid plane area (m²). 0.09 = 0.3×0.3m table surface.")]
    [SerializeField] private float minPlaneArea = 0.09f;
    [Tooltip("Height above placement point when GOSLO flies in")]
    [SerializeField] private float flyInHeight = 0.5f;

    [Header("Scene bounds (desktop fallback)")]
    [SerializeField] private float desktopRadius = 2.0f;

#if UNITY_AR_FOUNDATION
    private ARRaycastManager _raycastManager;
    private ARPlaneManager _planeManager;
    private ARAnchorManager _anchorManager;
    private readonly List<ARRaycastHit> _hits = new List<ARRaycastHit>();
#endif

    private GameObject _gosloInstance;
    private bool _placed;
    private Camera _cam;

    void Awake()
    {
        _cam = Camera.main;
    }

    void Start()
    {
#if UNITY_AR_FOUNDATION
        _raycastManager = FindObjectOfType<ARRaycastManager>();
        _planeManager = FindObjectOfType<ARPlaneManager>();
        _anchorManager = FindObjectOfType<ARAnchorManager>();

        if (_raycastManager == null)
            Debug.LogWarning("[TapToPlace] ARRaycastManager not found — AR tap disabled");
        if (_planeManager == null)
            Debug.LogWarning("[TapToPlace] ARPlaneManager not found — plane detection disabled");
#endif
    }

    void Update()
    {
        bool tapped = false;
        Vector2 tapPos = Vector2.zero;

#if UNITY_ANDROID && !UNITY_EDITOR
        if (Input.touchCount > 0)
        {
            var touch = Input.GetTouch(0);
            if (touch.phase == TouchPhase.Began)
            {
                tapped = true;
                tapPos = touch.position;
            }
        }
#else
        if (Input.GetMouseButtonDown(0))
        {
            tapped = true;
            tapPos = Input.mousePosition;
        }
#endif

        if (!tapped) return;
        HandleTap(tapPos);
    }

    private void HandleTap(Vector2 screenPos)
    {
#if UNITY_AR_FOUNDATION
        if (_raycastManager != null && _planeManager != null)
        {
            HandleARTap(screenPos);
            return;
        }
#endif
        HandleDesktopTap(screenPos);
    }

#if UNITY_AR_FOUNDATION
    private void HandleARTap(Vector2 screenPos)
    {
        _hits.Clear();
        bool hit = _raycastManager.Raycast(screenPos, _hits, TrackableType.PlaneWithinPolygon);
        if (!hit || _hits.Count == 0) return;

        var bestHit = _hits[0];
        var plane = _planeManager.GetPlane(bestHit.trackableId);
        if (plane == null) return;

        // Validate plane area (extents = half-size, so area = 4 × x × z)
        var extents = plane.extents;
        float area = 4f * extents.x * extents.z;
        if (area < minPlaneArea)
        {
            Debug.Log($"[TapToPlace] Plane too small ({area:F3} m² < {minPlaneArea} m²), ignoring tap");
            return;
        }

        var pose = bestHit.pose;
        PlaceGoslo(pose.position, pose.rotation, anchorPose: pose, createAnchor: true);
    }
#endif

    private void HandleDesktopTap(Vector2 screenPos)
    {
        if (_cam == null) return;
        var ray = _cam.ScreenPointToRay(screenPos);
        var plane = new Plane(Vector3.up, Vector3.zero);
        if (!plane.Raycast(ray, out float dist)) return;
        var point = ray.GetPoint(dist);

        // Clamp to scene bounds
        point.x = Mathf.Clamp(point.x, -desktopRadius, desktopRadius);
        point.z = Mathf.Clamp(point.z, -desktopRadius, desktopRadius);
        point.y = 0f;

        PlaceGoslo(point, Quaternion.identity, anchorPose: new Pose(point, Quaternion.identity), createAnchor: false);
    }

    private void PlaceGoslo(Vector3 targetPos, Quaternion targetRot, Pose anchorPose, bool createAnchor)
    {
        if (_gosloInstance == null)
        {
            if (gosloPrefab != null)
                _gosloInstance = Instantiate(gosloPrefab);
            else
            {
                // Dev: find GOSLO in scene
                _gosloInstance = GameObject.Find("GOSLO");
                if (_gosloInstance == null)
                {
                    Debug.LogWarning("[TapToPlace] No gosloPrefab assigned and no GOSLO found in scene");
                    return;
                }
            }
        }

        // Fly in from above
        var flyInStart = targetPos + Vector3.up * flyInHeight;
        _gosloInstance.transform.position = flyInStart;
        _gosloInstance.transform.rotation = targetRot;
        _gosloInstance.SetActive(true);

        // Trigger AnimationDriver fly-in sequence
        var driver = _gosloInstance.GetComponentInChildren<AnimationDriver>();
        if (driver != null)
            driver.FlyTo(targetPos);
        else
            _gosloInstance.transform.position = targetPos;

#if UNITY_AR_FOUNDATION
        if (createAnchor && _anchorManager != null)
        {
            var anchor = _anchorManager.AttachAnchor(null, anchorPose);
            if (anchor != null)
            {
                // Parent GOSLO to anchor so it tracks the surface
                _gosloInstance.transform.SetParent(anchor.transform, worldPositionStays: true);
                Debug.Log($"[TapToPlace] ARAnchor created at {targetPos}");
            }
        }
#endif

        _placed = true;
        Debug.Log($"[TapToPlace] GOSLO placed at {targetPos} (anchor={createAnchor})");

        // Notify Brain via RPC about anchor position
        NotifyBrainPlacement(targetPos);
    }

    private void NotifyBrainPlacement(Vector3 worldPos)
    {
        StartCoroutine(NotifyBrainPlacementCoroutine(worldPos));
    }

    private IEnumerator NotifyBrainPlacementCoroutine(Vector3 worldPos)
    {
        var room = RoomManager.Instance?.Room;
        if (room == null) yield break;

        string brainId = FindBrainIdentity(room);
        if (string.IsNullOrEmpty(brainId)) yield break;

        string payload = $"{{\"x\":{worldPos.x:F3},\"y\":{worldPos.y:F3},\"z\":{worldPos.z:F3}}}";
        var rpcCall = room.LocalParticipant.PerformRpc(new PerformRpcParams
        {
            DestinationIdentity = brainId,
            Method = "onGosloPlaced",
            Payload = payload,
            ResponseTimeout = 3000,
        });
        yield return rpcCall;

        if (rpcCall.IsError)
            Debug.LogWarning($"[TapToPlace] onGosloPlaced error: {rpcCall.Error?.Message}");
    }

    private static string FindBrainIdentity(Room room)
    {
        foreach (var p in room.RemoteParticipants.Values)
        {
            if (!string.IsNullOrEmpty(p.Identity) && p.Identity.StartsWith("agent-"))
                return p.Identity;
        }
        return null;
    }
}
