using System;
using System.Text;
using UnityEngine;
using LiveKit;

#if UNITY_XR_HANDS
using UnityEngine.XR.Hands;
using UnityEngine.XR;
#endif

/// <summary>
/// Tracks hand poses via XR Hands subsystem and sends telemetry to Brain Agent.
///
/// Detects gestures:
///   - open_palm: all fingers extended, palm facing up → "perch invitation"
///   - closed_fist: all fingers curled → "dismiss" / "shoo"
///   - none: hand visible but no recognized gesture
///
/// Sends hand telemetry via DataChannel (Lossy, ~10Hz) on topic "parrot.event"
/// when hand state changes, or every N frames for position updates.
///
/// Works with both left and right hands; prefers right hand for perching.
/// </summary>
public class XRHandTracker : MonoBehaviour
{
    [Header("Tracking Settings")]
#if UNITY_XR_HANDS
    [SerializeField] private Handedness preferredHand = Handedness.Right;
#endif
    [SerializeField] private float sendIntervalSeconds = 0.1f;

#if UNITY_XR_HANDS
    [Header("Gesture Thresholds")]
    [Tooltip("Min dot(palmNormal, Vector3.up) to count as palm-up")]
    [SerializeField] private float palmUpThreshold = 0.5f;
    [Tooltip("Max curl angle (degrees) for a finger to count as extended")]
    [SerializeField] private float fingerExtendedMaxAngle = 40f;
#endif

    public enum Handedness { Left, Right }

    public bool IsHandDetected { get; private set; }
    public string CurrentGesture { get; private set; } = "none";
    public Vector3 PalmPosition { get; private set; }
    public Vector3 IndexTipPosition { get; private set; }

    public event Action<HandTelemetry> OnHandTelemetry;

    private float _lastSendTime;
    private string _lastSentGesture = "";
    private bool _lastHandDetected;

#if UNITY_XR_HANDS
    private XRHandSubsystem _handSubsystem;
#endif

    [Serializable]
    public struct HandTelemetry
    {
        public bool hand_detected;
        public string gesture;
        public SerVec3 palm_position;
        public SerVec3 index_tip_position;
        public float timestamp;
    }

    [Serializable]
    public struct SerVec3
    {
        public float x, y, z;
        public SerVec3(Vector3 v) { x = v.x; y = v.y; z = v.z; }
    }

    void Start()
    {
#if UNITY_XR_HANDS
        var subsystems = new System.Collections.Generic.List<XRHandSubsystem>();
        SubsystemManager.GetSubsystems(subsystems);
        if (subsystems.Count > 0)
        {
            _handSubsystem = subsystems[0];
            Debug.Log($"[XRHandTracker] XR Hand subsystem found: {_handSubsystem.GetType().Name}");
        }
        else
        {
            Debug.LogWarning("[XRHandTracker] No XR Hand subsystem available");
        }
#else
        Debug.LogWarning("[XRHandTracker] XR Hands package not installed (define UNITY_XR_HANDS)");
#endif
    }

    void Update()
    {
#if UNITY_XR_HANDS
        if (_handSubsystem == null || !_handSubsystem.running)
        {
            if (IsHandDetected) SetHandLost();
            return;
        }

        XRHand hand = preferredHand == Handedness.Right
            ? _handSubsystem.rightHand
            : _handSubsystem.leftHand;

        if (!hand.isTracked)
        {
            if (IsHandDetected) SetHandLost();
            return;
        }

        IsHandDetected = true;
        UpdateJointPositions(hand);
        DetectGesture(hand);
        MaybeSendTelemetry();
#endif
    }

#if UNITY_XR_HANDS
    private void UpdateJointPositions(XRHand hand)
    {
        var xrOrigin = FindAnyObjectByType<Unity.XR.CoreUtils.XROrigin>();
        Pose originPose = xrOrigin != null
            ? new Pose(xrOrigin.transform.position, xrOrigin.transform.rotation)
            : Pose.identity;

        if (hand.GetJoint(XRHandJointID.Palm).TryGetPose(out Pose palmPose))
        {
            PalmPosition = palmPose.GetTransformedBy(originPose).position;
        }

        if (hand.GetJoint(XRHandJointID.IndexTip).TryGetPose(out Pose indexPose))
        {
            IndexTipPosition = indexPose.GetTransformedBy(originPose).position;
        }
    }

    private void DetectGesture(XRHand hand)
    {
        if (!hand.GetJoint(XRHandJointID.Palm).TryGetPose(out Pose palmPose))
        {
            CurrentGesture = "none";
            return;
        }

        var xrOrigin = FindAnyObjectByType<Unity.XR.CoreUtils.XROrigin>();
        Pose originPose = xrOrigin != null
            ? new Pose(xrOrigin.transform.position, xrOrigin.transform.rotation)
            : Pose.identity;

        Pose worldPalm = palmPose.GetTransformedBy(originPose);
        Vector3 palmNormal = worldPalm.rotation * Vector3.down;
        bool palmFacingUp = Vector3.Dot(palmNormal, Vector3.up) > palmUpThreshold;

        int extendedCount = 0;
        XRHandJointID[] fingerTips = {
            XRHandJointID.ThumbTip,
            XRHandJointID.IndexTip,
            XRHandJointID.MiddleTip,
            XRHandJointID.RingTip,
            XRHandJointID.LittleTip,
        };
        XRHandJointID[] fingerProximals = {
            XRHandJointID.ThumbProximal,
            XRHandJointID.IndexProximal,
            XRHandJointID.MiddleProximal,
            XRHandJointID.RingProximal,
            XRHandJointID.LittleProximal,
        };

        for (int i = 0; i < fingerTips.Length; i++)
        {
            if (hand.GetJoint(fingerTips[i]).TryGetPose(out Pose tipPose) &&
                hand.GetJoint(fingerProximals[i]).TryGetPose(out Pose proxPose))
            {
                Vector3 fingerDir = (tipPose.position - proxPose.position).normalized;
                Vector3 handForward = palmPose.rotation * Vector3.forward;
                float angle = Vector3.Angle(fingerDir, handForward);
                if (angle < fingerExtendedMaxAngle)
                    extendedCount++;
            }
        }

        if (palmFacingUp && extendedCount >= 4)
            CurrentGesture = "open_palm";
        else if (extendedCount <= 1)
            CurrentGesture = "closed_fist";
        else
            CurrentGesture = "none";
    }
#endif

    private void SetHandLost()
    {
        IsHandDetected = false;
        CurrentGesture = "none";
        SendTelemetry();
    }

    private void MaybeSendTelemetry()
    {
        bool gestureChanged = CurrentGesture != _lastSentGesture;
        bool detectionChanged = IsHandDetected != _lastHandDetected;
        bool intervalElapsed = Time.time - _lastSendTime >= sendIntervalSeconds;

        if (gestureChanged || detectionChanged || intervalElapsed)
            SendTelemetry();
    }

    private void SendTelemetry()
    {
        _lastSendTime = Time.time;
        _lastSentGesture = CurrentGesture;
        _lastHandDetected = IsHandDetected;

        var telemetry = new HandTelemetry
        {
            hand_detected = IsHandDetected,
            gesture = CurrentGesture,
            palm_position = new SerVec3(PalmPosition),
            index_tip_position = new SerVec3(IndexTipPosition),
            timestamp = Time.time,
        };

        OnHandTelemetry?.Invoke(telemetry);
        PublishToDataChannel(telemetry);
    }

    private void PublishToDataChannel(HandTelemetry telemetry)
    {
        var room = RoomManager.Instance?.Room;
        if (room == null || !RoomManager.Instance.IsConnected) return;

        string json = JsonUtility.ToJson(telemetry);

        var payload = Encoding.UTF8.GetBytes(
            $"{{\"type\":\"hand_gesture\",\"payload\":{json},\"timestamp\":{telemetry.timestamp}}}"
        );

        room.LocalParticipant.PublishData(
            payload,
            reliable: false,
            topic: "parrot.event"
        );
    }
}
