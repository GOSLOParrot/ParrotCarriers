using UnityEngine;

/// <summary>
/// Controls the parrot GameObject: movement and animation.
/// Supports both real GOSLO model (with child renderers) and dev Cube.
///
/// FlyTo: smooth MoveTowards to target position.
/// PlayAnimation: triggers Animator states, or visual pulse as dev fallback.
/// </summary>
public class ParrotController : MonoBehaviour
{
    [Header("Movement")]
    [SerializeField] private float moveSpeed = 3f;
    [SerializeField] private float arrivalThreshold = 0.05f;

    private Vector3 _targetPosition;
    private bool _isMoving;
    private Animator _animator;
    private Renderer[] _renderers;
    private string _currentAnimation = "idle";

    private Vector3 _baseScale;
    private float _pulseTimer;
    private bool _isPulsing;

    void Awake()
    {
        _animator = GetComponentInChildren<Animator>();
        _renderers = GetComponentsInChildren<Renderer>();
        _targetPosition = transform.position;
        _baseScale = transform.localScale;
    }

    void Update()
    {
        if (_isMoving)
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
            _pulseTimer += Time.deltaTime * 4f;
            float s = 1f + Mathf.Sin(_pulseTimer) * 0.1f;
            transform.localScale = _baseScale * s;
            if (_pulseTimer > Mathf.PI * 4f)
            {
                _isPulsing = false;
                transform.localScale = _baseScale;
            }
        }
    }

    /// <summary>Command the parrot to fly to a world-space position.</summary>
    public void FlyTo(Vector3 target)
    {
        _targetPosition = target;
        _isMoving = true;
        Debug.Log($"[Parrot] FlyTo -> {target}");

        if (_animator != null)
        {
            _animator.SetBool("isFlying", true);
            _animator.SetTrigger("flyTo");
        }
    }

    /// <summary>Play a named animation on the parrot.</summary>
    public void PlayAnimation(string animationName)
    {
        _currentAnimation = animationName;
        Debug.Log($"[Parrot] PlayAnimation -> {animationName}");

        if (_animator != null)
        {
            _animator.SetBool("isFlying", false);
            _animator.SetTrigger(animationName);
        }
        else
        {
            _isPulsing = true;
            _pulseTimer = 0f;
            Debug.Log($"[Parrot] (no Animator) Pulse for: {animationName}");
        }
    }
}
