using UnityEngine;

namespace ParrotApp.Parrot
{
    /// <summary>
    /// Controls the parrot GameObject: movement and animation.<br/>
    /// 从 ParrotDev 1:1 搬迁（Sprint4 Phase 3 / L3 Group 4），仅加 <c>ParrotApp.Parrot</c>
    /// 命名空间，行为零变化。
    ///
    /// FlyTo / PlayAnimation 是给 <see cref="ParrotApp.RPC.ParrotRpcHandler"/> 用的公共 API。
    /// 优先委托给 <see cref="AnimationDriver"/>；fallback 走 Animator 或 dev pulse。
    /// </summary>
    public class ParrotController : MonoBehaviour
    {
        [Header("Movement")]
        [SerializeField] private float moveSpeed = 3f;
        [SerializeField] private float arrivalThreshold = 0.05f;

        [Header("Dev fallback (no Animator, no AnimationDriver)")]
        [SerializeField] private float devPulseScaleAmplitude = 0.35f;
        [SerializeField] private float devPulseYawDegrees = 22f;
        [SerializeField] private float devPulseDurationCycles = 3f;

        private Vector3 _targetPosition;
        private bool _isMoving;
        private Animator _animator;
        private AnimationDriver _animDriver;
        private Renderer[] _renderers;
        private string _currentAnimation = "idle";

        private Vector3 _baseScale;
        private float _pulseTimer;
        private bool _isPulsing;
        private Quaternion _pulseStartRotation;

        void Awake()
        {
            _animator = GetComponentInChildren<Animator>();
            _animDriver = GetComponentInChildren<AnimationDriver>();
            _renderers = GetComponentsInChildren<Renderer>();
            _targetPosition = transform.position;
            _baseScale = transform.localScale;

            if (_animDriver != null)
                Debug.Log("[Parrot] AnimationDriver found — Sprint 3 procedural animation active");
            else if (_animator != null)
                Debug.Log("[Parrot] Animator found — legacy Animator path");
            else
                Debug.Log("[Parrot] No Animator/AnimationDriver — dev pulse fallback");
        }

        void Update()
        {
            if (_animDriver == null && _isMoving)
            {
                transform.position = Vector3.MoveTowards(
                    transform.position, _targetPosition, moveSpeed * Time.deltaTime);

                if (Vector3.Distance(transform.position, _targetPosition) < arrivalThreshold)
                {
                    transform.position = _targetPosition;
                    _isMoving = false;
                    Debug.Log($"[Parrot] Arrived at {_targetPosition}");
                }
            }

            if (_isPulsing)
            {
                _pulseTimer += Time.deltaTime * 5f;
                float s = 1f + Mathf.Sin(_pulseTimer) * devPulseScaleAmplitude;
                transform.localScale = _baseScale * s;
                float yaw = Mathf.Sin(_pulseTimer * 2.1f) * devPulseYawDegrees;
                transform.rotation = _pulseStartRotation * Quaternion.Euler(0f, yaw, 0f);

                float endPhase = Mathf.PI * 2f * devPulseDurationCycles;
                if (_pulseTimer > endPhase)
                {
                    _isPulsing = false;
                    transform.localScale = _baseScale;
                    transform.rotation = _pulseStartRotation;
                    Debug.Log("[Parrot] Dev pulse finished.");
                }
            }
        }

        public void FlyTo(Vector3 target)
        {
            Debug.Log($"[Parrot] FlyTo -> {target}");

            if (_animDriver != null)
            {
                _animDriver.FlyTo(target);
                return;
            }

            _targetPosition = target;
            _isMoving = true;

            if (_animator != null)
            {
                _animator.SetBool("isFlying", true);
                _animator.SetTrigger("flyTo");
            }
        }

        public void PlayAnimation(string animationName)
        {
            _currentAnimation = animationName;
            Debug.Log($"[Parrot] PlayAnimation -> {animationName}");

            if (_animDriver != null)
            {
                _animDriver.ApplyBodyStateString(animationName);
                return;
            }

            if (_animator != null)
            {
                _animator.SetBool("isFlying", false);
                _animator.SetTrigger(animationName);
            }
            else
            {
                _pulseStartRotation = transform.rotation;
                _isPulsing = true;
                _pulseTimer = 0f;
                Debug.Log(
                    $"[Parrot] (no Animator) Pulse for: {animationName} "
                    + $"(scale ±{devPulseScaleAmplitude:P0}, yaw ±{devPulseYawDegrees}° — watch Game view)");
            }
        }
    }
}
