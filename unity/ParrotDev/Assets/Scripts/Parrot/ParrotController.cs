using UnityEngine;

/// <summary>
/// Controls the parrot GameObject: movement and animation.
/// Phase 1 uses a simple cube stand-in; Phase 2 swaps in the Minecraft model.
///
/// FlyTo: smooth lerp to target position.
/// PlayAnimation: triggers Animator states (or logs in dev mode without Animator).
/// </summary>
public class ParrotController : MonoBehaviour
{
    [Header("Movement")]
    [SerializeField] private float moveSpeed = 3f;
    [SerializeField] private float arrivalThreshold = 0.05f;

    [Header("Visual Feedback (Dev)")]
    [SerializeField] private Color idleColor = Color.green;
    [SerializeField] private Color movingColor = Color.yellow;
    [SerializeField] private Color animatingColor = Color.cyan;

    private Vector3 _targetPosition;
    private bool _isMoving;
    private Animator _animator;
    private Renderer _renderer;
    private string _currentAnimation = "idle";

    void Awake()
    {
        _animator = GetComponent<Animator>();
        _renderer = GetComponent<Renderer>();
        _targetPosition = transform.position;
    }

    void Update()
    {
        if (!_isMoving) return;

        transform.position = Vector3.MoveTowards(
            transform.position, _targetPosition, moveSpeed * Time.deltaTime);

        if (Vector3.Distance(transform.position, _targetPosition) < arrivalThreshold)
        {
            transform.position = _targetPosition;
            _isMoving = false;
            SetDevColor(idleColor);
            Debug.Log($"[Parrot] Arrived at {_targetPosition}");
        }
    }

    /// <summary>Command the parrot to fly to a world-space position.</summary>
    public void FlyTo(Vector3 target)
    {
        _targetPosition = target;
        _isMoving = true;
        SetDevColor(movingColor);
        Debug.Log($"[Parrot] FlyTo → {target}");

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
        Debug.Log($"[Parrot] PlayAnimation → {animationName}");

        if (_animator != null)
        {
            _animator.SetBool("isFlying", false);
            _animator.SetTrigger(animationName);
        }
        else
        {
            SetDevColor(animatingColor);
            Debug.Log($"[Parrot] (no Animator) Would play: {animationName}");
        }
    }

    private void SetDevColor(Color c)
    {
        if (_renderer != null && _renderer.material != null)
            _renderer.material.color = c;
    }
}
