using System;
using System.Collections.Generic;
using UnityEngine;
using UnityEngine.EventSystems;

namespace ParrotApp.Parrot
{
    /// <summary>
    /// AR/mobile-friendly cheek pinch input for Ner.
    /// Uses camera screen rays against cheek trigger colliders so the same
    /// component works in AR Foundation camera scenes and editor mouse tests.
    /// </summary>
    public class NerCheekPinchInteractor : MonoBehaviour
    {
        [SerializeField] private Camera targetCamera;
        [SerializeField] private NerSpineController controller;
        [SerializeField] private bool autoCreateCheekColliders = true;
        [SerializeField] private Vector3 leftCheekLocalPosition = new Vector3(-0.055f, 0.115f, -0.005f);
        [SerializeField] private Vector3 rightCheekLocalPosition = new Vector3(0.055f, 0.115f, -0.005f);
        [SerializeField] private float cheekRadiusMeters = 0.045f;
        [SerializeField] private float dragPixelsForFullStrength = 140f;
        [SerializeField] private float warningStrength = 0.72f;
        [SerializeField] private float warningIntervalSeconds = 0.9f;
        [SerializeField] private LayerMask raycastMask = ~0;

        private readonly Dictionary<Collider, string> _sideByCollider = new Dictionary<Collider, string>();
        private int _activePointerId = int.MinValue;
        private string _activeSide = "";
        private Vector2 _startScreenPosition;
        private float _lastWarningAt = -999f;

        void Awake()
        {
            if (controller == null) controller = GetComponentInParent<NerSpineController>();
            if (targetCamera == null) targetCamera = Camera.main;
            if (autoCreateCheekColliders) EnsureCheekColliders();
        }

        void Update()
        {
            if (controller == null) return;
            if (targetCamera == null) targetCamera = Camera.main;
            if (targetCamera == null) return;

            if (Input.touchCount > 0)
            {
                bool activeTouchSeen = false;
                for (int i = 0; i < Input.touchCount; i++)
                {
                    var touch = Input.GetTouch(i);
                    if (touch.fingerId == _activePointerId) activeTouchSeen = true;
                    HandleTouch(touch);
                }
                if (_activePointerId >= 0 && !activeTouchSeen)
                {
                    EndPinch();
                }
                return;
            }

            HandleMouse();
        }

        private void HandleTouch(Touch touch)
        {
            if (_activePointerId != int.MinValue && touch.fingerId != _activePointerId) return;

            if (touch.phase == TouchPhase.Began)
            {
                if (IsPointerOverUi(touch.fingerId)) return;
                TryBegin(touch.fingerId, touch.position);
            }
            else if (_activePointerId == touch.fingerId
                     && (touch.phase == TouchPhase.Moved || touch.phase == TouchPhase.Stationary))
            {
                ContinuePinch(touch.position);
            }
            else if (_activePointerId == touch.fingerId
                     && (touch.phase == TouchPhase.Ended || touch.phase == TouchPhase.Canceled))
            {
                EndPinch();
            }
        }

        void OnDisable()
        {
            if (_activePointerId != int.MinValue)
            {
                SendCheekCapability("cheek_recover", 0f, Vector2.zero);
            }
            _activePointerId = int.MinValue;
            _activeSide = "";
        }

        private void HandleMouse()
        {
            const int mousePointerId = -1;
            if (Input.GetMouseButtonDown(0))
            {
                if (IsPointerOverUi(mousePointerId)) return;
                TryBegin(mousePointerId, Input.mousePosition);
            }
            else if (_activePointerId == mousePointerId && Input.GetMouseButton(0))
            {
                ContinuePinch(Input.mousePosition);
            }
            else if (_activePointerId == mousePointerId && Input.GetMouseButtonUp(0))
            {
                EndPinch();
            }
        }

        private bool TryBegin(int pointerId, Vector2 screenPosition)
        {
            if (!TryHitCheek(screenPosition, out var side)) return false;

            _activePointerId = pointerId;
            _activeSide = side;
            _startScreenPosition = screenPosition;
            _lastWarningAt = -999f;
            SendCheekCapability("cheek_pinch_start", 0.12f, Vector2.zero);
            return true;
        }

        private void ContinuePinch(Vector2 screenPosition)
        {
            var drag = (screenPosition - _startScreenPosition) / Mathf.Max(1f, dragPixelsForFullStrength);
            drag = Vector2.ClampMagnitude(drag, 1f);
            float strength = Mathf.Clamp01(drag.magnitude);

            if (strength >= warningStrength && Time.time - _lastWarningAt >= warningIntervalSeconds)
            {
                _lastWarningAt = Time.time;
                SendCheekCapability("cheek_pinch_warning", strength, drag);
                return;
            }

            SendCheekCapability("cheek_pinch_hold", strength, drag);
        }

        private void EndPinch()
        {
            SendCheekCapability("cheek_pinch_release", 0f, Vector2.zero);
            _activePointerId = int.MinValue;
            _activeSide = "";
        }

        private bool TryHitCheek(Vector2 screenPosition, out string side)
        {
            side = "";
            var ray = targetCamera.ScreenPointToRay(screenPosition);
            var hits = Physics.RaycastAll(ray, 100f, raycastMask, QueryTriggerInteraction.Collide);
            if (hits == null || hits.Length == 0)
            {
                return false;
            }

            Array.Sort(hits, (a, b) => a.distance.CompareTo(b.distance));
            for (int i = 0; i < hits.Length; i++)
            {
                var hit = hits[i];
                if (hit.collider == null) continue;

                if (_sideByCollider.TryGetValue(hit.collider, out side)) return true;

                var marker = hit.collider.GetComponentInParent<NerCheekHitRegion>();
                if (marker != null && marker.Owner == this)
                {
                    side = marker.Side;
                    return !string.IsNullOrEmpty(side);
                }
            }
            return false;
        }

        private void SendCheekCapability(string capabilityId, float strength, Vector2 drag)
        {
            if (controller == null) return;
            var payload = new CheekPinchPayload
            {
                side = string.IsNullOrEmpty(_activeSide) ? "both" : _activeSide,
                strength = Mathf.Clamp01(strength),
                drag_x = Mathf.Clamp(drag.x, -1f, 1f),
                drag_y = Mathf.Clamp(drag.y, -1f, 1f),
            };
            controller.ApplyCapability(capabilityId, JsonUtility.ToJson(payload));
        }

        private void EnsureCheekColliders()
        {
            if (_sideByCollider.Count > 0) return;
            RegisterCheekCollider("left", leftCheekLocalPosition);
            RegisterCheekCollider("right", rightCheekLocalPosition);
        }

        private void RegisterCheekCollider(string side, Vector3 localPosition)
        {
            var go = new GameObject("NerCheekHit_" + side);
            go.transform.SetParent(transform, false);
            go.transform.localPosition = localPosition;
            go.transform.localRotation = Quaternion.identity;
            go.transform.localScale = Vector3.one;

            var marker = go.AddComponent<NerCheekHitRegion>();
            marker.Configure(this, side);

            var collider = go.AddComponent<SphereCollider>();
            collider.isTrigger = true;
            collider.radius = cheekRadiusMeters;
            _sideByCollider[collider] = side;
        }

        private static bool IsPointerOverUi(int pointerId)
        {
            if (EventSystem.current == null) return false;
            return pointerId >= 0
                ? EventSystem.current.IsPointerOverGameObject(pointerId)
                : EventSystem.current.IsPointerOverGameObject();
        }

        void OnDrawGizmosSelected()
        {
            Gizmos.color = new Color(1f, 0.55f, 0.72f, 0.38f);
            Gizmos.matrix = transform.localToWorldMatrix;
            Gizmos.DrawSphere(leftCheekLocalPosition, cheekRadiusMeters);
            Gizmos.DrawSphere(rightCheekLocalPosition, cheekRadiusMeters);
        }

        [Serializable]
        private struct CheekPinchPayload
        {
            public string side;
            public float strength;
            public float drag_x;
            public float drag_y;
        }
    }
}
