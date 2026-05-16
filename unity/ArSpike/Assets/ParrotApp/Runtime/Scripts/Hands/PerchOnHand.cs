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

        [Header("Flight route")]
        [SerializeField] private float flyToSpeed = 1.8f;
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
        [SerializeField] private Vector3 rootClearanceLocalOffset = new Vector3(0f, 0.012f, 0f);
        [SerializeField] private float perchedFollowLerp = 18f;
        [SerializeField] private float perchedRotateLerp = 14f;

        [Header("Return")]
        [SerializeField] private float returnSpeed = 1.8f;
        [SerializeField] private float returnArrivalDistance = 0.05f;
        [SerializeField] private Vector3 explicitReturnPosition = Vector3.zero;

        [Header("RPC")]
        [SerializeField] private float maxRpcWaitSeconds = 5f;

        public PerchState State { get; private set; } = PerchState.IDLE;
        public string ActivePerchCommandId { get; private set; } = "";
        public string ActiveTrigger { get; private set; } = "";

        private Vector3 _returnPosition;
        private Quaternion _returnRotation;
        private FlightRoute _route;
        private Vector3 _routeTargetPosition;
        private Quaternion _routeTargetRotation = Quaternion.identity;
        private LineRenderer _trail;
        private TaskCompletionSource<PerchRpcResult> _activeRpcCompletion;
        private bool _activeRequiresBranchGesture;
        private bool _footAnchorResolved;
        private Vector3 _resolvedFootAnchorLocalOffset;
        private string _lastGestureEvent = HandGestureSource.GestureNone;
        private float _perchStartedAt;

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
            if (animDriver == null) animDriver = GetComponentInChildren<AnimationDriver>();
            if (animDriver == null) animDriver = FindObjectOfType<AnimationDriver>();
            ResolveFootAnchor();
        }

        private void Start()
        {
            if (handTracker == null) handTracker = FindObjectOfType<HandGestureSource>();
            if (handTracker == null)
            {
                Debug.LogWarning("[PerchOnHand] No HandGestureSource found; hand perch disabled.");
                enabled = false;
                return;
            }
            if (animDriver == null)
            {
                Debug.LogWarning("[PerchOnHand] No AnimationDriver found; hand perch disabled.");
                enabled = false;
                return;
            }
            handTracker.OnGestureSnapshot += OnGesture;
        }

        private void OnDisable()
        {
            HideTrail();
            CompleteActiveRpc(false, "disabled");
            if (State != PerchState.IDLE)
                LifecycleHeartbeatPublisher.Instance?.ClearActiveCommand(ActivePerchCommandId);
            State = PerchState.IDLE;
            ActivePerchCommandId = "";
            ActiveTrigger = "";
        }

        private void OnDestroy()
        {
            if (handTracker != null) handTracker.OnGestureSnapshot -= OnGesture;
        }

        private void Update()
        {
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
                completion?.TrySetResult(PerchRpcResult.Completed());
                return true;
            }

            if (State != PerchState.IDLE)
            {
                reason = "body_busy";
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

        private void OnGesture(HandGestureSource.HandGestureSnapshot snap)
        {
            PublishGestureEventIfChanged(snap);

            switch (State)
            {
                case PerchState.IDLE:
                    if (snap.HandDetected && snap.Gesture == HandGestureSource.GestureBranch)
                    {
                        string commandId = "gesture_perch_" + Mathf.RoundToInt(Time.unscaledTime * 1000f);
                        BeginPerch("gesture", commandId, null, true, out _);
                    }
                    break;

                case PerchState.FLYING_TO_HAND:
                case PerchState.PERCHED:
                    if (!snap.HandDetected || snap.Gesture == HandGestureSource.GestureFist)
                    {
                        string reason = !snap.HandDetected ? "hand_lost" : "gesture_release";
                        CompleteActiveRpc(false, reason);
                        PublishPerchLifecycle("release", reason);
                        TransitionTo(PerchState.RETURNING);
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
            if (handTracker == null || !handTracker.IsHandDetected || !handTracker.CurrentPerchPose.IsValid)
            {
                reason = "hand_pose_unavailable";
                completion?.TrySetResult(PerchRpcResult.Rejected(reason));
                return false;
            }

            if (requireBranchGesture && handTracker.CurrentGesture != HandGestureSource.GestureBranch)
            {
                reason = "branch_gesture_required";
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

            LifecycleHeartbeatPublisher.Instance?.ReportActiveCommand(ActivePerchCommandId, new[] { BodyLock });
            PublishPerchLifecycle("started", "");
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
                TransitionTo(PerchState.RETURNING);
                return;
            }

            if (_activeRequiresBranchGesture && handTracker.CurrentGesture != HandGestureSource.GestureBranch)
            {
                CompleteActiveRpc(false, "branch_gesture_lost");
                PublishPerchLifecycle("abort", "branch_gesture_lost");
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
                desired = Quaternion.LookRotation(tangent.normalized, Vector3.up);
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
                State = PerchState.IDLE;
                ActivePerchCommandId = "";
                ActiveTrigger = "";
                return;
            }

            if (!CanUseCurrentHandPose(out HandPerchPose pose, out string reason))
            {
                CompleteActiveRpc(false, reason);
                PublishPerchLifecycle("abort", reason);
                TransitionTo(PerchState.RETURNING);
                return;
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
                PublishPerchLifecycle("returned", "");
                TransitionTo(PerchState.IDLE);
            }
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
            Vector3 rootPosition = pose.ToRootPosition(_resolvedFootAnchorLocalOffset, rootClearanceLocalOffset);
            return new Pose(rootPosition, pose.Rotation);
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
            Vector3 dir = toTarget.sqrMagnitude > 0.0001f ? toTarget.normalized : transform.forward;
            float height = Mathf.Clamp(distance * flightArcHeightPerMeter, flightArcMinHeight, flightArcMaxHeight);

            Vector3 approach = targetRotation * Vector3.forward;
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
            Vector3 approach = targetRotation * Vector3.forward;
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
            Debug.Log($"[PerchOnHand] {prev} -> {next} trigger={ActiveTrigger} cmd={ActivePerchCommandId}");

            switch (next)
            {
                case PerchState.FLYING_TO_HAND:
                    animDriver.SetState(AnimationDriver.BodyState.Fly);
                    animDriver.SetHeadState(AnimationDriver.HeadState.Forward);
                    break;
                case PerchState.PERCHED:
                    HideTrail();
                    animDriver.SetState(AnimationDriver.BodyState.PerchedOnHand);
                    animDriver.SetHeadState(AnimationDriver.HeadState.Tilt);
                    break;
                case PerchState.RETURNING:
                    animDriver.SetState(AnimationDriver.BodyState.Fly);
                    animDriver.SetHeadState(AnimationDriver.HeadState.Forward);
                    break;
                case PerchState.IDLE:
                    HideTrail();
                    animDriver.SetState(AnimationDriver.BodyState.Idle);
                    animDriver.SetHeadState(AnimationDriver.HeadState.Forward);
                    LifecycleHeartbeatPublisher.Instance?.ClearActiveCommand(ActivePerchCommandId);
                    ActivePerchCommandId = "";
                    ActiveTrigger = "";
                    _activeRequiresBranchGesture = false;
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
            Debug.Log(
                $"[PerchOnHand] lifecycle phase={phase ?? ""} reason={reason ?? ""} " +
                $"trigger={ActiveTrigger ?? ""} cmd={ActivePerchCommandId ?? ""} state={State}");
        }

        private void ResolveFootAnchor()
        {
            if (_footAnchorResolved) return;
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
