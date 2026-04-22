using System;
using System.Collections;
using UnityEngine;

/// <summary>
/// Sprint 3 T-U4: Programmatic animation driver for GOSLO.
///
/// Drives four body states via procedural motion (no Mixamo/skeleton):
///   idle     — gentle hover bob + slow rotation
///   head_bob — nod cycle (used when listening / thinking)
///   fly      — smooth MoveTowards target + tilt into direction
///   perch    — land + subtle breathing scale
///
/// Interface design is Sprint 4-safe: FlyTo / SetState can be called
/// from ParrotController (RPC path) or TapToPlace (AR placement path).
/// The GOSLO.glb model uses Transform.Find() for bone nodes so the
/// coupling is by node name, not skeleton rig index.
///
/// Body state changes arrive via DataChannel "body_state" events
/// (telemetry_receiver.py → Unity DataChannel → here).
/// </summary>
public class AnimationDriver : MonoBehaviour
{
    public enum BodyState { Idle, HeadBob, Fly, Perch }

    [Header("Movement")]
    [SerializeField] private float flySpeed = 2.5f;
    [SerializeField] private float flyArrivalThreshold = 0.04f;
    [SerializeField] private float flyTiltDegrees = 15f;

    [Header("Idle hover")]
    [SerializeField] private float idleBobAmplitude = 0.04f;
    [SerializeField] private float idleBobFrequency = 1.2f;
    [SerializeField] private float idleRotateSpeed = 18f;

    [Header("Head bob (listening)")]
    [SerializeField] private float headBobAmplitude = 0.06f;
    [SerializeField] private float headBobFrequency = 2.5f;

    [Header("Perch (breathing scale)")]
    [SerializeField] private float perchBreathAmplitude = 0.03f;
    [SerializeField] private float perchBreathFrequency = 0.8f;

    [Header("Model nodes (by name, D6 decision)")]
    [Tooltip("Name of the head Transform inside GOSLO.glb hierarchy. Leave empty if not present.")]
    [SerializeField] private string headNodeName = "Head";
    [Tooltip("Name of the body Transform inside GOSLO.glb hierarchy. Leave empty to use root.")]
    [SerializeField] private string bodyNodeName = "Body";

    public BodyState CurrentState { get; private set; } = BodyState.Idle;

    private Vector3 _flyTarget;
    private bool _isFlying;
    private Vector3 _basePosition;
    private Quaternion _baseRotation;
    private Vector3 _baseScale;
    private float _stateTimer;

    private Transform _headTransform;
    private Transform _bodyTransform;
    private Quaternion _headBaseRot;
    private Quaternion _bodyBaseRot;

    void Awake()
    {
        _basePosition = transform.localPosition;
        _baseRotation = transform.localRotation;
        _baseScale = transform.localScale;

        // Find model nodes by name (D6: Transform.Find — works for both
        // GOSLO.glb and simple cube placeholder)
        if (!string.IsNullOrEmpty(headNodeName))
            _headTransform = FindDeep(transform, headNodeName);
        if (!string.IsNullOrEmpty(bodyNodeName))
            _bodyTransform = FindDeep(transform, bodyNodeName);

        if (_headTransform != null) _headBaseRot = _headTransform.localRotation;
        if (_bodyTransform != null) _bodyBaseRot = _bodyTransform.localRotation;
    }

    void Update()
    {
        _stateTimer += Time.deltaTime;

        switch (CurrentState)
        {
            case BodyState.Idle:
                UpdateIdle();
                break;
            case BodyState.HeadBob:
                UpdateHeadBob();
                break;
            case BodyState.Fly:
                UpdateFly();
                break;
            case BodyState.Perch:
                UpdatePerch();
                break;
        }
    }

    // ── Public API ────────────────────────────────────────────────────

    /// <summary>
    /// Smoothly fly GOSLO to world-space <paramref name="target"/>.
    /// Automatically switches to Fly state; returns to Idle on arrival.
    /// </summary>
    public void FlyTo(Vector3 target)
    {
        _flyTarget = target;
        _isFlying = true;
        SetState(BodyState.Fly);
    }

    /// <summary>
    /// Directly set body state (called from DataChannel body_state events
    /// and ParrotRpcHandler animate RPC).
    /// </summary>
    public void SetState(BodyState state)
    {
        if (CurrentState == state) return;
        CurrentState = state;
        _stateTimer = 0f;

        // Reset head/body to base when leaving special states
        if (_headTransform != null && state != BodyState.HeadBob)
            _headTransform.localRotation = _headBaseRot;

        Debug.Log($"[AnimationDriver] State → {state}");
    }

    /// <summary>
    /// Parse a body_state string (from DataChannel) and apply it.
    /// Recognised strings: "idle", "listening" / "head_bob", "fly", "perch".
    /// </summary>
    public void ApplyBodyStateString(string bodyState)
    {
        switch (bodyState.ToLowerInvariant().Replace("-", "_"))
        {
            case "idle":       SetState(BodyState.Idle);    break;
            case "head_bob":
            case "listening":  SetState(BodyState.HeadBob); break;
            case "fly":        SetState(BodyState.Fly);     break;
            case "perch":      SetState(BodyState.Perch);   break;
            default:
                Debug.LogWarning($"[AnimationDriver] Unknown body_state: '{bodyState}' — staying {CurrentState}");
                break;
        }
    }

    // ── Idle ──────────────────────────────────────────────────────────

    private void UpdateIdle()
    {
        // Gentle hover bob on local Y
        float bob = Mathf.Sin(_stateTimer * idleBobFrequency * Mathf.PI * 2f) * idleBobAmplitude;
        transform.localPosition = _basePosition + new Vector3(0f, bob, 0f);

        // Slow rotation around Y (looking around)
        transform.Rotate(Vector3.up, idleRotateSpeed * Time.deltaTime, Space.Self);
    }

    // ── HeadBob (listening) ───────────────────────────────────────────

    private void UpdateHeadBob()
    {
        // Body still hovers
        float bob = Mathf.Sin(_stateTimer * idleBobFrequency * Mathf.PI * 2f) * idleBobAmplitude;
        transform.localPosition = _basePosition + new Vector3(0f, bob, 0f);

        if (_headTransform != null)
        {
            float nod = Mathf.Sin(_stateTimer * headBobFrequency * Mathf.PI * 2f) * headBobAmplitude * 90f;
            _headTransform.localRotation = _headBaseRot * Quaternion.Euler(nod, 0f, 0f);
        }
    }

    // ── Fly ──────────────────────────────────────────────────────────

    private void UpdateFly()
    {
        if (!_isFlying) return;

        var dir = (_flyTarget - transform.position).normalized;
        transform.position = Vector3.MoveTowards(transform.position, _flyTarget, flySpeed * Time.deltaTime);

        // Tilt into flight direction (pitch forward, roll into sideward movement)
        if (dir.magnitude > 0.01f)
        {
            var targetRot = Quaternion.LookRotation(dir, Vector3.up)
                            * Quaternion.Euler(-flyTiltDegrees, 0f, 0f);
            transform.rotation = Quaternion.Slerp(transform.rotation, targetRot, 8f * Time.deltaTime);
        }

        if (Vector3.Distance(transform.position, _flyTarget) < flyArrivalThreshold)
        {
            transform.position = _flyTarget;
            _isFlying = false;
            _basePosition = _flyTarget;
            SetState(BodyState.Idle);
            Debug.Log($"[AnimationDriver] Arrived at {_flyTarget}");
        }
    }

    // ── Perch ─────────────────────────────────────────────────────────

    private void UpdatePerch()
    {
        // Subtle breathing scale
        float breath = Mathf.Sin(_stateTimer * perchBreathFrequency * Mathf.PI * 2f) * perchBreathAmplitude;
        transform.localScale = _baseScale * (1f + breath);

        // Drift back toward base rotation
        transform.localRotation = Quaternion.Slerp(transform.localRotation, _baseRotation, 3f * Time.deltaTime);
    }

    // ── Utility ──────────────────────────────────────────────────────

    private static Transform FindDeep(Transform root, string name)
    {
        foreach (Transform child in root.GetComponentsInChildren<Transform>(includeInactive: true))
        {
            if (string.Equals(child.name, name, StringComparison.OrdinalIgnoreCase))
                return child;
        }
        return null;
    }
}
