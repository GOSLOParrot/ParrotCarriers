using System.Text;
using UnityEngine;
using LiveKit;

/// <summary>
/// Makes the parrot fly to and perch on the user's hand when open_palm is detected.
///
/// State machine:
///   IDLE → (open_palm detected) → FLYING_TO_HAND → (arrived) → PERCHED → (hand lost / fist) → RETURNING
///
/// While PERCHED, the parrot transform tracks IndexTip position every frame (pure local, no network).
/// The Brain Agent is notified of state changes via DataChannel for awareness (not for control).
///
/// Requires XRHandTracker on the same or parent GameObject.
/// </summary>
[RequireComponent(typeof(ParrotController))]
public class PerchOnHand : MonoBehaviour
{
    [Header("References")]
    [SerializeField] private XRHandTracker handTracker;

    [Header("Perch Settings")]
    [Tooltip("Offset from index tip where parrot sits (local to finger direction)")]
    [SerializeField] private Vector3 perchOffset = new Vector3(0f, 0.02f, 0f);
    [SerializeField] private float arrivalDistance = 0.08f;
    [SerializeField] private float followSpeed = 20f;
    [SerializeField] private float flyToSpeed = 5f;

    [Header("Return")]
    [SerializeField] private Vector3 defaultPosition = new Vector3(0.3f, 1.5f, -0.5f);

    private ParrotController _parrot;
    private PerchState _state = PerchState.IDLE;
    private Vector3 _returnPosition;

    public PerchState State => _state;

    public enum PerchState
    {
        IDLE,
        FLYING_TO_HAND,
        PERCHED,
        RETURNING,
    }

    void Awake()
    {
        _parrot = GetComponent<ParrotController>();
        _returnPosition = defaultPosition;
    }

    void Start()
    {
        if (handTracker == null)
            handTracker = FindAnyObjectByType<XRHandTracker>();

        if (handTracker == null)
        {
            Debug.LogWarning("[PerchOnHand] No XRHandTracker found — perch disabled");
            enabled = false;
            return;
        }

        handTracker.OnHandTelemetry += OnHandUpdate;
    }

    void Update()
    {
        switch (_state)
        {
            case PerchState.FLYING_TO_HAND:
                UpdateFlyingToHand();
                break;
            case PerchState.PERCHED:
                UpdatePerched();
                break;
            case PerchState.RETURNING:
                UpdateReturning();
                break;
        }
    }

    private void OnHandUpdate(XRHandTracker.HandTelemetry telemetry)
    {
        switch (_state)
        {
            case PerchState.IDLE:
                if (telemetry.hand_detected && telemetry.gesture == "open_palm")
                {
                    _returnPosition = transform.position;
                    TransitionTo(PerchState.FLYING_TO_HAND);
                }
                break;

            case PerchState.FLYING_TO_HAND:
            case PerchState.PERCHED:
                if (!telemetry.hand_detected || telemetry.gesture == "closed_fist")
                {
                    TransitionTo(PerchState.RETURNING);
                }
                break;
        }
    }

    private void UpdateFlyingToHand()
    {
        if (!handTracker.IsHandDetected)
        {
            TransitionTo(PerchState.RETURNING);
            return;
        }

        Vector3 target = handTracker.IndexTipPosition + perchOffset;
        transform.position = Vector3.MoveTowards(
            transform.position, target, flyToSpeed * Time.deltaTime
        );

        Vector3 lookDir = target - transform.position;
        if (lookDir.sqrMagnitude > 0.001f)
            transform.rotation = Quaternion.Slerp(
                transform.rotation,
                Quaternion.LookRotation(lookDir),
                10f * Time.deltaTime
            );

        if (Vector3.Distance(transform.position, target) < arrivalDistance)
        {
            TransitionTo(PerchState.PERCHED);
        }
    }

    private void UpdatePerched()
    {
        if (!handTracker.IsHandDetected)
        {
            TransitionTo(PerchState.RETURNING);
            return;
        }

        Vector3 target = handTracker.IndexTipPosition + perchOffset;
        transform.position = Vector3.Lerp(
            transform.position, target, followSpeed * Time.deltaTime
        );
    }

    private void UpdateReturning()
    {
        transform.position = Vector3.MoveTowards(
            transform.position, _returnPosition, flyToSpeed * Time.deltaTime
        );

        if (Vector3.Distance(transform.position, _returnPosition) < 0.05f)
        {
            transform.position = _returnPosition;
            TransitionTo(PerchState.IDLE);
        }
    }

    private void TransitionTo(PerchState newState)
    {
        if (_state == newState) return;

        var oldState = _state;
        _state = newState;
        Debug.Log($"[PerchOnHand] {oldState} → {newState}");

        switch (newState)
        {
            case PerchState.FLYING_TO_HAND:
                _parrot.PlayAnimation("fly");
                break;
            case PerchState.PERCHED:
                _parrot.PlayAnimation("perch");
                break;
            case PerchState.RETURNING:
                _parrot.PlayAnimation("fly");
                break;
            case PerchState.IDLE:
                _parrot.PlayAnimation("idle");
                break;
        }

        NotifyBrainStateChange(newState);
    }

    private void NotifyBrainStateChange(PerchState state)
    {
        var room = RoomManager.Instance?.Room;
        if (room == null || !RoomManager.Instance.IsConnected) return;

        string json = $"{{\"type\":\"perch_state\",\"payload\":{{\"state\":\"{state}\",\"position\":{{\"x\":{transform.position.x:F2},\"y\":{transform.position.y:F2},\"z\":{transform.position.z:F2}}}}},\"timestamp\":{Time.time}}}";

        room.LocalParticipant.PublishData(
            Encoding.UTF8.GetBytes(json),
            DataPacketKind.RELIABLE,
            topic: "parrot.event"
        );
    }

    void OnDestroy()
    {
        if (handTracker != null)
            handTracker.OnHandTelemetry -= OnHandUpdate;
    }
}
