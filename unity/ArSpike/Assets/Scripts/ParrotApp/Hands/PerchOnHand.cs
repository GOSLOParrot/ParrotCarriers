using ParrotApp.Parrot;
using UnityEngine;

namespace ParrotApp.Hands
{
    /// <summary>
    /// Sprint4 Phase 4 W3.A.2 — gesture-driven perch reflex.
    ///
    /// State machine (parrot_behavior_rules §5.1 verbatim):
    /// <code>
    /// IDLE
    ///   → (gesture == index_finger_branch) → FLYING_TO_HAND
    ///   → (Distance(self, IndexIntermediate + perchOffset) < arrivalDistance) → PERCHED
    ///   → (hand lost / closed_fist) → RETURNING
    ///   → (Distance(self, returnPosition) < returnArrivalDistance) → IDLE
    /// </code>
    ///
    /// <b>Reflex 层职责（行为矩阵 §3.3 第 2 行）</b>：纯本地反射，不阻塞对话，
    /// 不直接上报 LLM。状态外溢通过 <see cref="AnimationDriver"/> 的 producer
    /// events → <c>LifecycleHeartbeatPublisher</c>（A.3）→ EcpState 双触发上行。
    ///
    /// <b>"接续 Intent"（行为矩阵 §3.3 第 3 行 verbatim）</b>：到达手指中段
    /// （成功判定）后自动 SetBody=PerchedOnHand + SetHead=Tilt，由
    /// <see cref="AnimationDriver"/> 渲染歪头 + 摆动表达"怎么了吗？"。
    ///
    /// <b>不发 DataChannel</b>（按用户 2026-04-29 决定，删除 ParrotDev 的
    /// <c>NotifyBrainStateChange</c> 旧路径）。Brain 通过 EcpState 看到
    /// body=perched_on_hand / head=HEAD_TILT 即知发生 perch。
    ///
    /// <b>抢断兼容（§5.2 "站在手上 + fly_to 指令"）</b>：PERCHED 期间检测到
    /// AnimationDriver.CurrentState 已被 RPC 抢走（不是 PerchedOnHand），就
    /// 退回 IDLE 让 RPC 接管，不再尝试归位。
    /// </summary>
    [DisallowMultipleComponent]
    public class PerchOnHand : MonoBehaviour
    {
        [Header("References")]
        [SerializeField] private HandGestureSource handTracker;
        [SerializeField] private AnimationDriver animDriver;

        [Header("Perch geometry")]
        [Tooltip("Offset from IndexIntermediate where the parrot perches " +
                 "(world space; +y lifts the bird above the finger).")]
        [SerializeField] private Vector3 perchOffset = new Vector3(0f, 0.02f, 0f);
        [Tooltip("Arrival distance to count as 'landed on the finger'.")]
        [SerializeField] private float arrivalDistance = 0.06f;
        [Tooltip("Speed (m/s) for FLYING_TO_HAND transit.")]
        [SerializeField] private float flyToSpeed = 1.8f;
        [Tooltip("Lerp factor used while PERCHED to smoothly follow finger jitter.")]
        [SerializeField] private float perchedFollowLerp = 18f;

        [Header("Return")]
        [Tooltip("Speed (m/s) for the RETURNING leg.")]
        [SerializeField] private float returnSpeed = 1.8f;
        [Tooltip("Arrival distance for RETURNING → IDLE.")]
        [SerializeField] private float returnArrivalDistance = 0.05f;
        [Tooltip("If non-zero, used as the RETURN target. Zero = parrot's position " +
                 "at the moment the gesture was first seen.")]
        [SerializeField] private Vector3 explicitReturnPosition = Vector3.zero;

        public PerchState State { get; private set; } = PerchState.IDLE;

        private Vector3 _returnPosition;

        public enum PerchState
        {
            IDLE,
            FLYING_TO_HAND,
            PERCHED,
            RETURNING,
        }

        void Awake()
        {
            if (animDriver == null) animDriver = GetComponentInChildren<AnimationDriver>();
            if (animDriver == null) animDriver = FindObjectOfType<AnimationDriver>();
        }

        void Start()
        {
            if (handTracker == null) handTracker = FindObjectOfType<HandGestureSource>();
            if (handTracker == null)
            {
                Debug.LogWarning("[PerchOnHand] No HandGestureSource found — perch disabled");
                enabled = false;
                return;
            }
            if (animDriver == null)
            {
                Debug.LogWarning("[PerchOnHand] No AnimationDriver found — perch disabled");
                enabled = false;
                return;
            }
            handTracker.OnGestureSnapshot += OnGesture;
        }

        void OnDestroy()
        {
            if (handTracker != null) handTracker.OnGestureSnapshot -= OnGesture;
        }

        void Update()
        {
            switch (State)
            {
                case PerchState.FLYING_TO_HAND: TickFlyingToHand(); break;
                case PerchState.PERCHED: TickPerched(); break;
                case PerchState.RETURNING: TickReturning(); break;
            }
        }

        // ─── gesture handler ─────────────────────────────────────────

        private void OnGesture(HandGestureSource.HandGestureSnapshot snap)
        {
            switch (State)
            {
                case PerchState.IDLE:
                    if (snap.HandDetected && snap.Gesture == HandGestureSource.GestureBranch)
                    {
                        // Cache the spot we should fly back to. Using the parrot's
                        // *current* position (not the SerializeField default zero)
                        // keeps the feature decoupled from scene placement.
                        _returnPosition = (explicitReturnPosition == Vector3.zero)
                            ? transform.position
                            : explicitReturnPosition;
                        TransitionTo(PerchState.FLYING_TO_HAND);
                    }
                    break;

                case PerchState.FLYING_TO_HAND:
                case PerchState.PERCHED:
                    if (!snap.HandDetected || snap.Gesture == HandGestureSource.GestureFist)
                        TransitionTo(PerchState.RETURNING);
                    break;
            }
        }

        // ─── per-state ticks ─────────────────────────────────────────

        private void TickFlyingToHand()
        {
            if (!handTracker.IsHandDetected)
            {
                TransitionTo(PerchState.RETURNING);
                return;
            }

            Vector3 target = handTracker.IndexIntermediatePosition + perchOffset;
            transform.position = Vector3.MoveTowards(
                transform.position, target, flyToSpeed * Time.deltaTime);

            Vector3 lookDir = target - transform.position;
            if (lookDir.sqrMagnitude > 0.0001f)
            {
                transform.rotation = Quaternion.Slerp(
                    transform.rotation,
                    Quaternion.LookRotation(lookDir, Vector3.up),
                    10f * Time.deltaTime);
            }

            if (Vector3.Distance(transform.position, target) < arrivalDistance)
            {
                TransitionTo(PerchState.PERCHED);
            }
        }

        private void TickPerched()
        {
            // §5.2 "站在手上 + fly_to 指令": if a higher-priority body command
            // (RPC) overrode our PerchedOnHand state, surrender gracefully.
            if (animDriver.CurrentState != AnimationDriver.BodyState.PerchedOnHand)
            {
                Debug.Log($"[PerchOnHand] Body state preempted ({animDriver.CurrentState}) — abandoning perch");
                State = PerchState.IDLE;
                _havePosedReturn = false;
                return;
            }

            if (!handTracker.IsHandDetected)
            {
                TransitionTo(PerchState.RETURNING);
                return;
            }

            // Smooth follow so finger jitter doesn't snap the parrot every frame.
            Vector3 target = handTracker.IndexIntermediatePosition + perchOffset;
            transform.position = Vector3.Lerp(
                transform.position, target, perchedFollowLerp * Time.deltaTime);
        }

        private void TickReturning()
        {
            transform.position = Vector3.MoveTowards(
                transform.position, _returnPosition, returnSpeed * Time.deltaTime);

            if (Vector3.Distance(transform.position, _returnPosition) < returnArrivalDistance)
            {
                transform.position = _returnPosition;
                TransitionTo(PerchState.IDLE);
            }
        }

        // ─── transitions ─────────────────────────────────────────────

        private void TransitionTo(PerchState next)
        {
            if (State == next) return;
            var prev = State;
            State = next;
            Debug.Log($"[PerchOnHand] {prev} → {next}");

            switch (next)
            {
                case PerchState.FLYING_TO_HAND:
                    animDriver.SetState(AnimationDriver.BodyState.Fly);
                    animDriver.SetHeadState(AnimationDriver.HeadState.Forward);
                    break;

                case PerchState.PERCHED:
                    // Auto-continue Intent (entry doc §3.3 row 3 verbatim):
                    // body=PERCHED_ON_HAND + head=HEAD_TILT for "怎么了吗？".
                    animDriver.SetState(AnimationDriver.BodyState.PerchedOnHand);
                    animDriver.SetHeadState(AnimationDriver.HeadState.Tilt);
                    break;

                case PerchState.RETURNING:
                    animDriver.SetState(AnimationDriver.BodyState.Fly);
                    animDriver.SetHeadState(AnimationDriver.HeadState.Forward);
                    break;

                case PerchState.IDLE:
                    animDriver.SetState(AnimationDriver.BodyState.Idle);
                    animDriver.SetHeadState(AnimationDriver.HeadState.Forward);
                    break;
            }
        }
    }
}
