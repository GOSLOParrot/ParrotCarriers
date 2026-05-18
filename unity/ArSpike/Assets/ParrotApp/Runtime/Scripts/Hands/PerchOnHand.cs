using System;
using System.Threading.Tasks;
using ParrotApp.Ecp;
using ParrotApp.Parrot;
using UnityEngine;

namespace ParrotApp.Hands
{
    [DisallowMultipleComponent]
    public class PerchOnHand : MonoBehaviour
    {
        private const string BodyLock = "body";
        private const string EventGestureRecognized = EcpEventTypeNames.GestureRecognized;

        [Header("References")]
        [SerializeField] private HandGestureSource handTracker;
        [SerializeField] private AnimationDriver animDriver;
        [SerializeField] private float referenceRetryIntervalSeconds = 0.5f;

        [Header("Flight route")]
        [SerializeField] private float flyToSpeed = 1.55f;
        [SerializeField] private float arrivalDistance = 0.045f;
        [SerializeField] private float routeReplanDistance = 0.08f;
        [SerializeField] private float flightArcMinHeight = 0.12f;
        [SerializeField] private float flightArcMaxHeight = 0.42f;
        [SerializeField] private float flightArcHeightPerMeter = 0.42f;
        [SerializeField] private float landingApproachDistance = 0.11f;
        [SerializeField] private float flightRotationLerp = 10f;
        [SerializeField] private bool renderFlightTrail = true;

        [Header("Finger anchor")]
        [SerializeField] private bool autoResolveFootAnchor = true;
        [SerializeField] private string leftFootNodeName = "left_leg";
        [SerializeField] private string rightFootNodeName = "right_leg";
        [SerializeField] private Vector3 footAnchorLocalOffset = Vector3.zero;
        [SerializeField] private Vector3 rootClearanceLocalOffset = new Vector3(0f, 0.004f, 0f);
        [SerializeField] private float fingerSurfaceLiftMeters = 0.01f;
        [SerializeField] private float footGripSinkMeters = 0.004f;
        [SerializeField] private float fingerAlongOffsetMeters = 0f;
        [SerializeField] private float perchedFollowLerp = 18f;
        [SerializeField] private float perchedRotateLerp = 14f;

        [Header("Camera CV safety")]
        [SerializeField] private bool stabilizeCameraCvRootPose = true;
        [SerializeField] private float cameraCvMinForwardMeters = 0.14f;
        [SerializeField] private float cameraCvMaxForwardMeters = 1.75f;
        [SerializeField] private float cameraCvMaxLateralMeters = 0.9f;
        [SerializeField] private float cameraCvMaxVerticalMeters = 0.75f;
        [SerializeField] private float cameraCvAllowedBelowStartMeters = 0.06f;
        [SerializeField] private float cameraCvMaxDistanceFromStartMeters = 1.9f;
        [SerializeField] private float cameraCvLeadSeconds = 0.08f;
        [SerializeField] private float cameraCvMaxPredictionStepMeters = 0.06f;
        [SerializeField] private bool logCameraCvTargets = true;

        [Header("Return")]
        [SerializeField] private float returnSpeed = 1.8f;
        [SerializeField] private float returnArrivalDistance = 0.05f;
        [SerializeField] private Vector3 explicitReturnPosition = Vector3.zero;
        [SerializeField] private float returnToViewDistance = 0.75f;
        [SerializeField] private float returnToViewVerticalOffset = -0.12f;

        [Header("RPC")]
        [SerializeField] private float maxRpcWaitSeconds = 5f;

        public PerchState State { get; private set; } = PerchState.IDLE;
        public string ActivePerchCommandId { get; private set; } = "";
        public string ActiveTrigger { get; private set; } = "";
        public string LastPerchStatus { get; private set; } = "idle";
        public string LastPerchLifecycle { get; private set; } = "";
        public string LastPerchRejectReason { get; private set; } = "";

        private Vector3 _returnPosition;
        private Quaternion _returnRotation;
        private FlightRoute _route;
        private Vector3 _routeTargetPosition;
        private Quaternion _routeTargetRotation = Quaternion.identity;
        private LineRenderer _trail;
        private TaskCompletionSource<PerchRpcResult> _activeRpcCompletion;
        private bool _activeRequiresBranchGesture;
        private bool _footAnchorResolved;
        private HandGestureSource _subscribedHandTracker;
        private bool _perchedTrackingLost;
        private Vector3 _resolvedFootAnchorLocalOffset;
        private string _lastGestureEvent = HandGestureSource.GestureNone;
        private float _perchStartedAt;
        private float _nextReferenceRetryAt;
        private float _nextCameraCvTargetLogAt;
        private bool _hasLastCameraCvRootPosition;
        private Vector3 _lastCameraCvRootPosition;
        private float _lastCameraCvRootAt;

        public enum PerchState
        {
            IDLE,
            FLYING_TO_HAND,
            PERCHED,
            RETURNING,
        }

        public struct PerchRpcResult
        {
            public bool Ok;
            public string Reason;

            public static PerchRpcResult Completed() => new PerchRpcResult { Ok = true, Reason = EcpAckJson.ReasonApplied };
            public static PerchRpcResult Rejected(string reason) => new PerchRpcResult { Ok = false, Reason = reason ?? EcpAckJson.ReasonRejected };
        }

        private struct FlightRoute
        {
            public bool Valid;
            public Vector3 P0;
            public Vector3 P1;
            public Vector3 P2;
            public Vector3 P3;
            public float StartedAt;
            public float Duration;
        }

        private void Awake()
        {
            ResolveReferences(force: true);
            ResolveFootAnchor(force: true);
        }

        private void Start()
        {
            ResolveReferences(force: true);
            if (handTracker == null)
            {
                Debug.LogWarning("[PerchOnHand] No HandGestureSource found yet; hand perch will retry when re-enabled.");
                return;
            }
            if (animDriver == null)
            {
                Debug.LogWarning("[PerchOnHand] No AnimationDriver found yet; hand perch will retry when re-enabled.");
                return;
            }
            TrySubscribe();
        }

        private void OnEnable()
        {
            ResolveReferences(force: true);
            TrySubscribe();
        }

        private void OnDisable()
        {
            Unsubscribe();
            HideTrail();
            CompleteActiveRpc(false, "disabled");
            if (State != PerchState.IDLE)
                LifecycleHeartbeatPublisher.Instance?.ClearActiveCommand(ActivePerchCommandId);
            State = PerchState.IDLE;
            ActivePerchCommandId = "";
            ActiveTrigger = "";
            _perchedTrackingLost = false;
            SetPerchStatus("disabled", "disabled");
        }

        private void OnDestroy()
        {
            Unsubscribe();
        }

        private void TrySubscribe()
        {
            ResolveReferences();
            if (_subscribedHandTracker == handTracker && _subscribedHandTracker != null) return;
            Unsubscribe();
            if (handTracker == null) return;
            handTracker.OnGestureSnapshot += OnGesture;
            _subscribedHandTracker = handTracker;
        }

        private void Unsubscribe()
        {
            if (_subscribedHandTracker == null) return;
            _subscribedHandTracker.OnGestureSnapshot -= OnGesture;
            _subscribedHandTracker = null;
        }

        private void Update()
        {
            if (_subscribedHandTracker == null || handTracker == null || animDriver == null)
                TrySubscribe();

            switch (State)
            {
                case PerchState.FLYING_TO_HAND:
                    TickFlyingToHand();
                    break;
                case PerchState.PERCHED:
                    TickPerched();
                    break;
                case PerchState.RETURNING:
                    TickReturning();
                    break;
            }
        }

        public bool TryRequestRpcPerch(
            string commandId,
            bool requireBranchGesture,
            TaskCompletionSource<PerchRpcResult> completion,
            out string reason)
        {
            commandId = string.IsNullOrWhiteSpace(commandId)
                ? "cmd_perch_to_finger_" + Guid.NewGuid().ToString("N").Substring(0, 8)
                : commandId.Trim();

            if (State == PerchState.PERCHED)
            {
                reason = "already_perched";
                SetPerchStatus("accepted", reason);
                completion?.TrySetResult(PerchRpcResult.Completed());
                return true;
            }

            if (State != PerchState.IDLE)
            {
                reason = "body_busy";
                SetPerchStatus("rejected", reason);
                return false;
            }

            return BeginPerch("goslo_rpc", commandId, completion, requireBranchGesture, out reason);
        }

        public void CancelRpcPerch(string commandId, string reason)
        {
            if (State == PerchState.IDLE) return;
            if (!string.IsNullOrWhiteSpace(commandId)
                && !string.Equals(ActivePerchCommandId, commandId, StringComparison.Ordinal))
            {
                return;
            }

            CompleteActiveRpc(false, string.IsNullOrWhiteSpace(reason) ? "cancelled" : reason);
            PublishPerchLifecycle("cancelled", reason);
            TransitionTo(PerchState.RETURNING);
        }

        public bool TryRequestReturnToView(
            string commandId,
            TaskCompletionSource<PerchRpcResult> completion,
            out string reason)
        {
            commandId = string.IsNullOrWhiteSpace(commandId)
                ? "cmd_return_to_view_" + Guid.NewGuid().ToString("N").Substring(0, 8)
                : commandId.Trim();

            if (State == PerchState.IDLE)
            {
                reason = "already_in_view";
                SetPerchStatus("accepted", reason);
                completion?.TrySetResult(PerchRpcResult.Completed());
                return true;
            }
            if (State == PerchState.RETURNING)
            {
                reason = "already_returning";
                SetPerchStatus("rejected", reason);
                return false;
            }

            CompleteActiveRpc(false, "return_to_view");
            _returnPosition = ResolveReturnToViewPosition();
            _returnRotation = ResolveReturnToViewRotation(_returnPosition);
            _activeRpcCompletion = completion;
            _activeRequiresBranchGesture = false;
            ActivePerchCommandId = commandId;
            ActiveTrigger = "goslo_return_to_view";
            _perchedTrackingLost = false;

            LifecycleHeartbeatPublisher.Instance?.ReportActiveCommand(ActivePerchCommandId, new[] { BodyLock });
            PublishPerchLifecycle("return_requested", "");
            TransitionTo(PerchState.RETURNING);
            reason = "";
            return true;
        }

        private void OnGesture(HandGestureSource.HandGestureSnapshot snap)
        {
            PublishGestureEventIfChanged(snap);

            switch (State)
            {
                case PerchState.IDLE:
                    if (snap.HandDetected && snap.Gesture == HandGestureSource.GestureBranch)
                    {
                        string commandId = "gesture_perch_" + Mathf.RoundToInt(Time.unscaledTime * 1000f);
                        if (!BeginPerch("gesture", commandId, null, true, out string reason))
                            SetPerchStatus("gesture_rejected", reason);
                    }
                    break;

                case PerchState.FLYING_TO_HAND:
                    if (!snap.HandDetected || snap.Gesture == HandGestureSource.GestureFist)
                    {
                        string reason = !snap.HandDetected ? "hand_lost" : "gesture_release";
                        CompleteActiveRpc(false, reason);
                        PublishPerchLifecycle("release", reason);
                        TransitionTo(PerchState.RETURNING);
                    }
                    break;

                case PerchState.PERCHED:
                    if (snap.Gesture == HandGestureSource.GestureFist)
                    {
                        CompleteActiveRpc(false, "gesture_release");
                        PublishPerchLifecycle("release", "gesture_release");
                        TransitionTo(PerchState.RETURNING);
                    }
                    else if (!snap.HandDetected)
                    {
                        HandlePerchedTrackingLost("hand_lost");
                    }
                    break;
            }
        }

        private bool BeginPerch(
            string trigger,
            string commandId,
            TaskCompletionSource<PerchRpcResult> completion,
            bool requireBranchGesture,
            out string reason)
        {
            reason = "";
            ResolveReferences(force: true);
            if (handTracker == null || !handTracker.IsHandDetected || !handTracker.CurrentPerchPose.IsValid)
            {
                reason = "hand_pose_unavailable";
                SetPerchStatus("rejected", reason);
                completion?.TrySetResult(PerchRpcResult.Rejected(reason));
                return false;
            }

            if (requireBranchGesture && handTracker.CurrentGesture != HandGestureSource.GestureBranch)
            {
                reason = "branch_gesture_required";
                SetPerchStatus("rejected", reason);
                completion?.TrySetResult(PerchRpcResult.Rejected(reason));
                return false;
            }

            if (animDriver == null)
            {
                reason = "animation_driver_unavailable";
                SetPerchStatus("rejected", reason);
                completion?.TrySetResult(PerchRpcResult.Rejected(reason));
                return false;
            }

            _returnPosition = explicitReturnPosition == Vector3.zero ? transform.position : explicitReturnPosition;
            _returnRotation = transform.rotation;
            _activeRpcCompletion = completion;
            _activeRequiresBranchGesture = requireBranchGesture;
            ActivePerchCommandId = commandId ?? "";
            ActiveTrigger = trigger ?? "";
            _perchStartedAt = Time.unscaledTime;
            _hasLastCameraCvRootPosition = false;
            ResolveFootAnchor(force: true);

            LifecycleHeartbeatPublisher.Instance?.ReportActiveCommand(ActivePerchCommandId, new[] { BodyLock });
            PublishPerchLifecycle("started", "");
            SetPerchStatus("accepted", trigger);
            TransitionTo(PerchState.FLYING_TO_HAND);
            PlanRouteToCurrentHandPose(force: true);
            return true;
        }

        private void TickFlyingToHand()
        {
            if (!CanUseCurrentHandPose(out HandPerchPose pose, out string reason))
            {
                CompleteActiveRpc(false, reason);
                PublishPerchLifecycle("abort", reason);
                SetPerchStatus("abort", reason);
                TransitionTo(PerchState.RETURNING);
                return;
            }

            if (_activeRequiresBranchGesture && handTracker.CurrentGesture != HandGestureSource.GestureBranch)
            {
                CompleteActiveRpc(false, "branch_gesture_lost");
                PublishPerchLifecycle("abort", "branch_gesture_lost");
                SetPerchStatus("abort", "branch_gesture_lost");
                TransitionTo(PerchState.RETURNING);
                return;
            }

            Pose targetRoot = ResolveRootPose(pose);
            if (!_route.Valid || Vector3.Distance(_routeTargetPosition, targetRoot.position) > routeReplanDistance)
                PlanRoute(targetRoot.position, targetRoot.rotation);
            else
                UpdateRouteEnd(targetRoot.position, targetRoot.rotation);

            float t = _route.Duration > 0f
                ? Mathf.Clamp01((Time.unscaledTime - _route.StartedAt) / _route.Duration)
                : 1f;
            float eased = EaseInOut(t);
            Vector3 next = Bezier(_route.P0, _route.P1, _route.P2, _route.P3, eased);
            Vector3 tangent = BezierDerivative(_route.P0, _route.P1, _route.P2, _route.P3, Mathf.Clamp01(eased + 0.01f));

            transform.position = next;
            Quaternion desired = targetRoot.rotation;
            if (tangent.sqrMagnitude > 0.0001f && t < 0.85f)
                desired = ResolveMotionFacingRotation(tangent.normalized, Vector3.up);
            transform.rotation = Quaternion.Slerp(transform.rotation, desired, flightRotationLerp * Time.deltaTime);
            UpdateTrail();

            if (t >= 0.98f || Vector3.Distance(transform.position, targetRoot.position) <= arrivalDistance)
            {
                transform.SetPositionAndRotation(targetRoot.position, targetRoot.rotation);
                PublishPerchLifecycle("landed", "");
                TransitionTo(PerchState.PERCHED);
                CompleteActiveRpc(true, EcpAckJson.ReasonApplied);
            }

            if (_activeRpcCompletion != null && Time.unscaledTime - _perchStartedAt > Mathf.Max(1f, maxRpcWaitSeconds))
            {
                CompleteActiveRpc(false, "timeout");
                PublishPerchLifecycle("abort", "timeout");
                SetPerchStatus("abort", "timeout");
                TransitionTo(PerchState.RETURNING);
            }
        }

        private void TickPerched()
        {
            if (animDriver.CurrentState != AnimationDriver.BodyState.PerchedOnHand)
            {
                PublishPerchLifecycle("preempted", AnimationDriver.BodyStateToWire(animDriver.CurrentState));
                LifecycleHeartbeatPublisher.Instance?.ClearActiveCommand(ActivePerchCommandId);
                CompleteActiveRpc(false, "preempted");
                SetPerchStatus("preempted", AnimationDriver.BodyStateToWire(animDriver.CurrentState));
                State = PerchState.IDLE;
                ActivePerchCommandId = "";
                ActiveTrigger = "";
                return;
            }

            if (!CanUseCurrentHandPose(out HandPerchPose pose, out string reason))
            {
                HandlePerchedTrackingLost(reason);
                return;
            }

            if (_perchedTrackingLost)
            {
                _perchedTrackingLost = false;
                PublishPerchLifecycle("tracking_resumed", "");
            }

            Pose targetRoot = ResolveRootPose(pose);
            float followT = 1f - Mathf.Exp(-Mathf.Max(0.1f, perchedFollowLerp) * Time.deltaTime);
            float rotateT = 1f - Mathf.Exp(-Mathf.Max(0.1f, perchedRotateLerp) * Time.deltaTime);
            transform.position = Vector3.Lerp(transform.position, targetRoot.position, followT);
            transform.rotation = Quaternion.Slerp(transform.rotation, targetRoot.rotation, rotateT);
        }

        private void TickReturning()
        {
            HideTrail();

            Vector3 next = Vector3.MoveTowards(transform.position, _returnPosition, returnSpeed * Time.deltaTime);
            transform.position = next;
            transform.rotation = Quaternion.Slerp(transform.rotation, _returnRotation, 8f * Time.deltaTime);

            if (Vector3.Distance(transform.position, _returnPosition) < returnArrivalDistance)
            {
                transform.SetPositionAndRotation(_returnPosition, _returnRotation);
                CompleteActiveRpc(true, EcpAckJson.ReasonApplied);
                PublishPerchLifecycle("returned", "");
                TransitionTo(PerchState.IDLE);
            }
        }

        private void HandlePerchedTrackingLost(string reason)
        {
            if (_perchedTrackingLost) return;
            _perchedTrackingLost = true;
            PublishPerchLifecycle("tracking_lost_hold_on_hand", reason);
            SetPerchStatus("tracking_lost_hold_on_hand", reason);
        }

        private bool CanUseCurrentHandPose(out HandPerchPose pose, out string reason)
        {
            pose = handTracker != null ? handTracker.CurrentPerchPose : default;
            if (handTracker == null || !handTracker.IsHandDetected)
            {
                reason = "hand_lost";
                return false;
            }
            if (!pose.IsValid)
            {
                reason = "hand_pose_unavailable";
                return false;
            }
            reason = "";
            return true;
        }

        private Pose ResolveRootPose(HandPerchPose pose)
        {
            ResolveFootAnchor();
            Quaternion rootRotation = ResolveMotionFacingRotation(pose.Rotation);
            Vector3 footOffset = ScaleLocalOffsetForCurrentRoot(_resolvedFootAnchorLocalOffset);
            Vector3 clearanceOffset = ScaleLocalOffsetForCurrentRoot(rootClearanceLocalOffset);
            Vector3 gripPosition = ResolveFingerGripPosition(pose);
            Vector3 rootPosition = gripPosition
                                   - (rootRotation * footOffset)
                                   + (rootRotation * clearanceOffset);
            rootPosition -= (rootRotation * Vector3.up) * Mathf.Max(0f, footGripSinkMeters);
            rootPosition = StabilizeCameraCvRootPosition(pose, rootPosition);
            return new Pose(rootPosition, rootRotation);
        }

        private Vector3 ResolveFingerGripPosition(HandPerchPose pose)
        {
            Vector3 fingerDir = pose.FingerDirection.sqrMagnitude > 0.0001f
                ? pose.FingerDirection.normalized
                : Vector3.right;
            Vector3 surfaceNormal = ResolveFingerSurfaceNormal(pose);
            return pose.Position
                   + surfaceNormal * Mathf.Max(0f, fingerSurfaceLiftMeters)
                   + fingerDir * fingerAlongOffsetMeters;
        }

        private Vector3 ResolveFingerSurfaceNormal(HandPerchPose pose)
        {
            Vector3 normal = pose.PalmNormal.sqrMagnitude > 0.0001f
                ? pose.PalmNormal.normalized
                : pose.Rotation * Vector3.up;
            Vector3 poseUp = pose.Rotation * Vector3.up;
            if (Vector3.Dot(normal, poseUp) < 0f)
                normal = -normal;
            Camera cam = Camera.main;
            if (cam != null && Vector3.Dot(normal, cam.transform.position - pose.Position) < 0f)
                normal = -normal;
            return normal.sqrMagnitude > 0.0001f ? normal.normalized : Vector3.up;
        }

        private Vector3 ScaleLocalOffsetForCurrentRoot(Vector3 localOffset)
        {
            Vector3 scale = transform.lossyScale;
            return new Vector3(localOffset.x * scale.x, localOffset.y * scale.y, localOffset.z * scale.z);
        }

        private Vector3 StabilizeCameraCvRootPosition(HandPerchPose pose, Vector3 rootPosition)
        {
            if (!stabilizeCameraCvRootPose
                || !string.Equals(pose.Source, "mediapipe_camera", StringComparison.OrdinalIgnoreCase))
            {
                return rootPosition;
            }

            Vector3 original = rootPosition;
            Vector3 stabilized = ClampCameraCvRootPosition(rootPosition);
            Vector3 predicted = PredictCameraCvRootPosition(stabilized);
            predicted = ClampCameraCvRootPosition(predicted);
            LogCameraCvTargetIfNeeded(pose.Position, original, predicted);
            return predicted;
        }

        private Vector3 ClampCameraCvRootPosition(Vector3 rootPosition)
        {
            Vector3 stabilized = rootPosition;
            Camera cam = Camera.main;
            if (cam != null)
            {
                Vector3 local = cam.transform.InverseTransformPoint(stabilized);
                local.z = Mathf.Clamp(
                    local.z,
                    Mathf.Max(0.05f, cameraCvMinForwardMeters),
                    Mathf.Max(cameraCvMinForwardMeters + 0.05f, cameraCvMaxForwardMeters));
                local.x = Mathf.Clamp(
                    local.x,
                    -Mathf.Max(0.05f, cameraCvMaxLateralMeters),
                    Mathf.Max(0.05f, cameraCvMaxLateralMeters));
                local.y = Mathf.Clamp(
                    local.y,
                    -Mathf.Max(0.05f, cameraCvMaxVerticalMeters),
                    Mathf.Max(0.05f, cameraCvMaxVerticalMeters));
                stabilized = cam.transform.TransformPoint(local);
            }

            float minY = _returnPosition.y - Mathf.Max(0f, cameraCvAllowedBelowStartMeters);
            if (stabilized.y < minY)
                stabilized.y = minY;

            float maxDistance = Mathf.Max(0.2f, cameraCvMaxDistanceFromStartMeters);
            Vector3 fromStart = stabilized - _returnPosition;
            if (fromStart.sqrMagnitude > maxDistance * maxDistance)
                stabilized = _returnPosition + fromStart.normalized * maxDistance;
            return stabilized;
        }

        private Vector3 PredictCameraCvRootPosition(Vector3 stabilized)
        {
            float now = Time.unscaledTime;
            Vector3 predicted = stabilized;
            if (_hasLastCameraCvRootPosition)
            {
                float dt = Mathf.Max(0.001f, now - _lastCameraCvRootAt);
                if (dt < 0.35f)
                {
                    Vector3 velocity = (stabilized - _lastCameraCvRootPosition) / dt;
                    Vector3 step = Vector3.ClampMagnitude(
                        velocity * Mathf.Max(0f, cameraCvLeadSeconds),
                        Mathf.Max(0f, cameraCvMaxPredictionStepMeters));
                    predicted += step;
                }
            }
            _lastCameraCvRootPosition = stabilized;
            _lastCameraCvRootAt = now;
            _hasLastCameraCvRootPosition = true;
            return predicted;
        }

        private Vector3 ResolveReturnToViewPosition()
        {
            Camera cam = Camera.main;
            if (cam != null)
            {
                return cam.transform.position
                       + cam.transform.forward * Mathf.Max(0.25f, returnToViewDistance)
                       + cam.transform.up * returnToViewVerticalOffset;
            }
            if (explicitReturnPosition != Vector3.zero) return explicitReturnPosition;
            return _returnPosition;
        }

        private Quaternion ResolveReturnToViewRotation(Vector3 returnPosition)
        {
            Camera cam = Camera.main;
            if (cam == null) return _returnRotation;
            Vector3 towardCamera = cam.transform.position - returnPosition;
            if (towardCamera.sqrMagnitude < 0.0001f) return _returnRotation;
            return ResolveMotionFacingRotation(towardCamera.normalized, Vector3.up);
        }

        private void PlanRouteToCurrentHandPose(bool force)
        {
            if (!CanUseCurrentHandPose(out HandPerchPose pose, out _)) return;
            Pose targetRoot = ResolveRootPose(pose);
            if (force || !_route.Valid)
                PlanRoute(targetRoot.position, targetRoot.rotation);
        }

        private void PlanRoute(Vector3 targetPosition, Quaternion targetRotation)
        {
            Vector3 start = transform.position;
            Vector3 toTarget = targetPosition - start;
            float distance = Mathf.Max(0.01f, toTarget.magnitude);
            Vector3 dir = toTarget.sqrMagnitude > 0.0001f
                ? toTarget.normalized
                : ResolveMotionForward(transform.rotation);
            float height = Mathf.Clamp(distance * flightArcHeightPerMeter, flightArcMinHeight, flightArcMaxHeight);

            Vector3 approach = ResolveMotionForward(targetRotation);
            if (approach.sqrMagnitude < 0.0001f) approach = -dir;
            approach.Normalize();

            _route = new FlightRoute
            {
                Valid = true,
                P0 = start,
                P1 = start + Vector3.up * height + dir * distance * 0.18f,
                P2 = targetPosition - approach * landingApproachDistance + Vector3.up * (height * 0.45f),
                P3 = targetPosition,
                StartedAt = Time.unscaledTime,
                Duration = Mathf.Max(0.35f, distance / Mathf.Max(0.1f, flyToSpeed)),
            };
            _routeTargetPosition = targetPosition;
            _routeTargetRotation = targetRotation;
            UpdateTrail();
        }

        private void UpdateRouteEnd(Vector3 targetPosition, Quaternion targetRotation)
        {
            _route.P3 = targetPosition;
            Vector3 approach = ResolveMotionForward(targetRotation);
            if (approach.sqrMagnitude < 0.0001f)
                approach = (_route.P3 - _route.P2).normalized;
            _route.P2 = targetPosition - approach.normalized * landingApproachDistance
                        + Vector3.up * Mathf.Max(0.04f, flightArcMinHeight * 0.35f);
            _routeTargetPosition = targetPosition;
            _routeTargetRotation = targetRotation;
        }

        private void TransitionTo(PerchState next)
        {
            if (State == next) return;
            PerchState prev = State;
            State = next;
            SetPerchStatus("state_" + next.ToString().ToLowerInvariant(), ActiveTrigger);
            Debug.Log($"[PerchOnHand] {prev} -> {next} trigger={ActiveTrigger} cmd={ActivePerchCommandId}");

            switch (next)
            {
                case PerchState.FLYING_TO_HAND:
                    _perchedTrackingLost = false;
                    animDriver.SetState(AnimationDriver.BodyState.Fly);
                    animDriver.SetHeadState(AnimationDriver.HeadState.Forward);
                    LifecycleHeartbeatPublisher.Instance?.ReportBodyState("flying");
                    break;
                case PerchState.PERCHED:
                    HideTrail();
                    animDriver.SetState(AnimationDriver.BodyState.PerchedOnHand);
                    animDriver.PlayHeadTiltOnce();
                    LifecycleHeartbeatPublisher.Instance?.ReportBodyState("perched_on_hand");
                    LifecycleHeartbeatPublisher.Instance?.ClearActiveCommand(ActivePerchCommandId);
                    break;
                case PerchState.RETURNING:
                    _perchedTrackingLost = false;
                    animDriver.SetState(AnimationDriver.BodyState.Fly);
                    animDriver.SetHeadState(AnimationDriver.HeadState.Forward);
                    LifecycleHeartbeatPublisher.Instance?.ReportBodyState("flying");
                    break;
                case PerchState.IDLE:
                    HideTrail();
                    animDriver.SetState(AnimationDriver.BodyState.Idle);
                    animDriver.SetHeadState(AnimationDriver.HeadState.Forward);
                    LifecycleHeartbeatPublisher.Instance?.ReportBodyState("idle");
                    LifecycleHeartbeatPublisher.Instance?.ClearActiveCommand(ActivePerchCommandId);
                    ActivePerchCommandId = "";
                    ActiveTrigger = "";
                    _activeRequiresBranchGesture = false;
                    _perchedTrackingLost = false;
                    break;
            }
        }

        private void CompleteActiveRpc(bool ok, string reason)
        {
            TaskCompletionSource<PerchRpcResult> completion = _activeRpcCompletion;
            _activeRpcCompletion = null;
            if (completion == null) return;

            completion.TrySetResult(ok
                ? PerchRpcResult.Completed()
                : PerchRpcResult.Rejected(string.IsNullOrWhiteSpace(reason) ? EcpAckJson.ReasonRejected : reason));
        }

        private Quaternion ResolveMotionFacingRotation(Vector3 direction, Vector3 up)
        {
            if (animDriver != null)
                return animDriver.ResolveMotionFacingRotation(direction, up);
            if (direction.sqrMagnitude < 0.0001f)
                return transform.rotation;
            Vector3 safeUp = up.sqrMagnitude > 0.0001f ? up.normalized : Vector3.up;
            return Quaternion.LookRotation(direction.normalized, safeUp);
        }

        private Quaternion ResolveMotionFacingRotation(Quaternion visualForwardRotation)
        {
            return animDriver != null
                ? animDriver.ResolveMotionFacingRotation(visualForwardRotation)
                : visualForwardRotation;
        }

        private Vector3 ResolveMotionForward(Quaternion rootRotation)
        {
            return animDriver != null
                ? animDriver.ResolveMotionForward(rootRotation)
                : rootRotation * Vector3.forward;
        }

        private void LogCameraCvTargetIfNeeded(Vector3 perchPosition, Vector3 originalRoot, Vector3 stabilizedRoot)
        {
            if (!logCameraCvTargets || Time.unscaledTime < _nextCameraCvTargetLogAt)
                return;
            _nextCameraCvTargetLogAt = Time.unscaledTime + 1.0f;
            Debug.Log(
                "[PerchOnHand] camera_cv_target perch=" + FormatVec3(perchPosition)
                + " root_raw=" + FormatVec3(originalRoot)
                + " root_safe=" + FormatVec3(stabilizedRoot)
                + " start=" + FormatVec3(_returnPosition)
                + " foot_local=" + FormatVec3(_resolvedFootAnchorLocalOffset)
                + " scale=" + FormatVec3(transform.lossyScale));
        }

        private static string FormatVec3(Vector3 value)
        {
            return value.x.ToString("0.00") + "," + value.y.ToString("0.00") + "," + value.z.ToString("0.00");
        }

        private void PublishGestureEventIfChanged(HandGestureSource.HandGestureSnapshot snap)
        {
            string gesture = snap.Gesture ?? HandGestureSource.GestureNone;
            if (gesture == _lastGestureEvent) return;
            _lastGestureEvent = gesture;
            if (gesture == HandGestureSource.GestureNone) return;

            string payload = JsonUtility.ToJson(new GestureEventPayload
            {
                gesture = gesture,
                hand_detected = snap.HandDetected,
                source = snap.Source ?? "",
                confidence = snap.Confidence,
                index_perch = Vec3Dto.From(snap.IndexPerch),
                index_direction = Vec3Dto.From(snap.IndexDirection),
            });
            EcpEventPublisher.Instance?.PublishUnityEvent(EventGestureRecognized, payload, ActivePerchCommandId);
        }

        private void PublishPerchLifecycle(string phase, string reason)
        {
            LastPerchLifecycle =
                (string.IsNullOrWhiteSpace(phase) ? "unknown" : phase)
                + (string.IsNullOrWhiteSpace(reason) ? "" : ":" + reason);
            Debug.Log(
                $"[PerchOnHand] lifecycle phase={phase ?? ""} reason={reason ?? ""} " +
                $"trigger={ActiveTrigger ?? ""} cmd={ActivePerchCommandId ?? ""} state={State}");
        }

        private void SetPerchStatus(string status, string reason)
        {
            LastPerchStatus = string.IsNullOrWhiteSpace(status) ? "unknown" : status;
            LastPerchRejectReason = string.IsNullOrWhiteSpace(reason) ? "" : reason;
        }

        private void ResolveReferences(bool force = false)
        {
            if (!force && Time.unscaledTime < _nextReferenceRetryAt) return;
            _nextReferenceRetryAt = Time.unscaledTime + Mathf.Max(0.1f, referenceRetryIntervalSeconds);

            if (handTracker == null) handTracker = FindObjectOfType<HandGestureSource>();
            if (animDriver == null) animDriver = GetComponentInChildren<AnimationDriver>(true);
            if (animDriver == null) animDriver = FindObjectOfType<AnimationDriver>();
        }

        private void ResolveFootAnchor(bool force = false)
        {
            if (_footAnchorResolved && !force) return;
            _resolvedFootAnchorLocalOffset = footAnchorLocalOffset;
            _footAnchorResolved = true;
            if (!autoResolveFootAnchor) return;

            Transform left = FindDeep(transform, leftFootNodeName);
            Transform right = FindDeep(transform, rightFootNodeName);
            if (left != null && right != null)
            {
                Vector3 mid = (left.position + right.position) * 0.5f;
                _resolvedFootAnchorLocalOffset = transform.InverseTransformPoint(mid);
                return;
            }
            if (left != null || right != null)
            {
                Transform foot = left != null ? left : right;
                _resolvedFootAnchorLocalOffset = transform.InverseTransformPoint(foot.position);
                return;
            }

            Renderer[] renderers = GetComponentsInChildren<Renderer>(false);
            if (renderers == null || renderers.Length == 0) return;
            Bounds bounds = renderers[0].bounds;
            for (int i = 1; i < renderers.Length; i++) bounds.Encapsulate(renderers[i].bounds);
            Vector3 bottomCenter = new Vector3(bounds.center.x, bounds.min.y, bounds.center.z);
            _resolvedFootAnchorLocalOffset = transform.InverseTransformPoint(bottomCenter);
        }

        private void EnsureTrail()
        {
            if (!renderFlightTrail || _trail != null) return;
            var go = new GameObject("FormalPerchFlightTrail");
            go.transform.SetParent(transform.parent, false);
            _trail = go.AddComponent<LineRenderer>();
            _trail.useWorldSpace = true;
            _trail.positionCount = 0;
            _trail.widthMultiplier = 0.012f;
            _trail.numCapVertices = 4;
            _trail.numCornerVertices = 2;
            _trail.shadowCastingMode = UnityEngine.Rendering.ShadowCastingMode.Off;
            _trail.receiveShadows = false;
            var shader = Shader.Find("Sprites/Default");
            if (shader != null)
                _trail.material = new Material(shader);
            _trail.startColor = new Color(0.72f, 0.95f, 1f, 0.75f);
            _trail.endColor = new Color(1f, 1f, 1f, 0f);
        }

        private void UpdateTrail()
        {
            if (!renderFlightTrail || !_route.Valid) return;
            EnsureTrail();
            if (_trail == null) return;

            const int Count = 24;
            _trail.enabled = true;
            _trail.positionCount = Count;
            for (int i = 0; i < Count; i++)
            {
                float t = i / (float)(Count - 1);
                _trail.SetPosition(i, Bezier(_route.P0, _route.P1, _route.P2, _route.P3, t));
            }
        }

        private void HideTrail()
        {
            if (_trail != null)
            {
                _trail.positionCount = 0;
                _trail.enabled = false;
            }
        }

        private static float EaseInOut(float t)
        {
            t = Mathf.Clamp01(t);
            return t * t * (3f - 2f * t);
        }

        private static Vector3 Bezier(Vector3 p0, Vector3 p1, Vector3 p2, Vector3 p3, float t)
        {
            float u = 1f - t;
            return u * u * u * p0
                   + 3f * u * u * t * p1
                   + 3f * u * t * t * p2
                   + t * t * t * p3;
        }

        private static Vector3 BezierDerivative(Vector3 p0, Vector3 p1, Vector3 p2, Vector3 p3, float t)
        {
            float u = 1f - t;
            return 3f * u * u * (p1 - p0)
                   + 6f * u * t * (p2 - p1)
                   + 3f * t * t * (p3 - p2);
        }

        private static Transform FindDeep(Transform root, string name)
        {
            if (root == null || string.IsNullOrEmpty(name)) return null;
            foreach (Transform c in root.GetComponentsInChildren<Transform>(true))
                if (string.Equals(c.name, name, StringComparison.OrdinalIgnoreCase))
                    return c;
            return null;
        }

        [Serializable]
        private struct Vec3Dto
        {
            public float x;
            public float y;
            public float z;

            public static Vec3Dto From(Vector3 v) => new Vec3Dto { x = v.x, y = v.y, z = v.z };
        }

        [Serializable]
        private struct GestureEventPayload
        {
            public string gesture;
            public bool hand_detected;
            public string source;
            public float confidence;
            public Vec3Dto index_perch;
            public Vec3Dto index_direction;
        }

    }
}
