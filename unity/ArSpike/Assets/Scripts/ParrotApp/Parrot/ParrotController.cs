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

        /// <summary>
        /// Sprint4 GOSLO model modularization (Step 2, 2026-05-06):
        ///   When a <see cref="ParrotApp.Parrot.ParrotRegistry"/> exists and
        ///   has a controller for the requested <paramref name="modelId"/>
        ///   (or any active controller for empty modelId), route the call
        ///   through <see cref="IParrotController.ApplyCapability"/>.
        ///   Returns the controller if routed, null otherwise — caller falls
        ///   back to the legacy AnimationDriver / Animator / dev-pulse path.
        /// </summary>
        private IParrotController ResolveControllerOrFallback(string modelId)
        {
            var registry = ParrotRegistry.Instance;
            if (registry == null) return null;
            return registry.Resolve(modelId);
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
            FlyTo(target, modelId: "");
        }

        /// <summary>
        /// Sprint4 GOSLO model modularization (Step 2, 2026-05-06): routing
        /// overload. <paramref name="modelId"/> comes from
        /// <c>EcpCommandDto.meta.model_id</c>. Empty = active controller via
        /// Registry, or legacy AnimationDriver fallback when no Registry.
        /// </summary>
        public void FlyTo(Vector3 target, string modelId)
        {
            Debug.Log($"[Parrot] FlyTo -> {target} (model_id='{modelId ?? ""}')");

            // Manifest-driven path: route through IParrotController.fly capability.
            var controller = ResolveControllerOrFallback(modelId);
            if (controller != null)
            {
                var paramsJson = JsonUtility.ToJson(new Vec3JsonPayload { x = target.x, y = target.y, z = target.z });
                if (controller.ApplyCapability("fly", paramsJson)) return;
                Debug.LogWarning(
                    $"[Parrot] controller '{controller.GetType().Name}' did not declare 'fly' " +
                    $"capability — falling back to legacy AnimationDriver.");
            }

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
            PlayAnimation(animationName, modelId: "");
        }

        /// <summary>
        /// Sprint4 GOSLO model modularization (Step 2, 2026-05-06): routing
        /// overload. <paramref name="modelId"/> comes from
        /// <c>EcpCommandDto.meta.model_id</c>.
        /// </summary>
        public void PlayAnimation(string animationName, string modelId)
        {
            _currentAnimation = animationName;
            Debug.Log($"[Parrot] PlayAnimation -> {animationName} (model_id='{modelId ?? ""}')");

            // Manifest-driven path: route through IParrotController.
            var controller = ResolveControllerOrFallback(modelId);
            if (controller != null)
            {
                if (controller.ApplyCapability(animationName, "")) return;
                Debug.LogWarning(
                    $"[Parrot] controller '{controller.GetType().Name}' did not declare " +
                    $"capability_id='{animationName}' — falling back to legacy AnimationDriver.");
            }

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

        // Local payload helper — kept private to avoid leaking a typed
        // payload to other modules. Mirrors the FlyToPayload x/y/z subset
        // GosloLegacyController already deserialises.
        [System.Serializable] private struct Vec3JsonPayload { public float x, y, z; }
    }
}
