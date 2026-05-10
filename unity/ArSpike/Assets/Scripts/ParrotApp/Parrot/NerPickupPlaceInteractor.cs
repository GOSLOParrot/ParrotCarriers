using System;
using System.Collections.Generic;
using UnityEngine;
using UnityEngine.EventSystems;

namespace ParrotApp.Parrot
{
    /// <summary>
    /// Mobile/AR first-pass body pickup and placement for Ner.
    ///
    /// A long press on the model body enters a held state, screen movement
    /// drags the model above the current placement plane, and release drops it.
    /// AR Foundation scenes can provide plane colliders; otherwise this falls
    /// back to a horizontal plane through the model's current Y position.
    /// </summary>
    public class NerPickupPlaceInteractor : MonoBehaviour
    {
        [SerializeField] private Camera targetCamera;
        [SerializeField] private NerSpineController controller;
        [SerializeField] private Transform targetRoot;
        [SerializeField] private bool autoCreateBodyCollider = true;
        [SerializeField] private Vector3 bodyColliderCenter = new Vector3(0f, 0.12f, 0f);
        [SerializeField] private Vector3 bodyColliderSize = new Vector3(0.16f, 0.24f, 0.10f);
        [SerializeField] private float longPressSeconds = 0.58f;
        [SerializeField] private float cancelBeforeHoldPixels = 22f;
        [SerializeField] private float clickMaxPixels = 22f;
        [SerializeField] private float clickEndDelaySeconds = 0.55f;
        [SerializeField] private float pickupLiftMeters = 0.08f;
        [SerializeField] private float minPickupLiftMeters = 0.05f;
        [SerializeField] private float maxPickupLiftMeters = 0.18f;
        [SerializeField] private float heightDragPixelsForFullRange = 260f;
        [SerializeField] private float pickupAscentSeconds = 0.16f;
        [SerializeField] private float maxRayDistanceMeters = 8f;
        [SerializeField] private LayerMask bodyRaycastMask = ~0;
        [SerializeField] private LayerMask placementRaycastMask = ~0;

        private readonly HashSet<Collider> _autoBodyColliders = new HashSet<Collider>();
        private PickupState _state = PickupState.Idle;
        private int _activePointerId = int.MinValue;
        private Vector2 _pressScreenPosition;
        private Vector2 _lastScreenPosition;
        private Vector3 _lastGroundPoint;
        private float _pressStartedAt;
        private float _heldStartedAt;
        private float _dragPlaneY;
        private float _currentPickupLiftMeters;
        private float _pickupBaseLiftMeters;
        private Vector2 _pickupStartScreenPosition;
        private string _queuedCapabilityId = "";
        private float _queuedCapabilityAt = -1f;

        void Awake()
        {
            if (controller == null) controller = GetComponentInParent<NerSpineController>();
            if (targetRoot == null) targetRoot = transform;
            if (targetCamera == null) targetCamera = Camera.main;
            if (autoCreateBodyCollider) EnsureBodyCollider();
        }

        void Update()
        {
            if (targetCamera == null) targetCamera = Camera.main;
            if (targetCamera == null) return;
            if (targetRoot == null) targetRoot = transform;
            UpdateQueuedCapability();
            UpdateHeldLoopCapability();

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
                    CancelPickup();
                }
                return;
            }

            HandleMouse();
        }

        void OnDisable()
        {
            if (_state == PickupState.Held)
            {
                SendBodyCapability("body_place_cancel", _lastGroundPoint, 0f);
                DropToLastGroundPoint();
            }
            ClearQueuedCapability();
            ResetState();
        }

        private void HandleTouch(Touch touch)
        {
            if (_activePointerId != int.MinValue && touch.fingerId != _activePointerId) return;

            if (touch.phase == TouchPhase.Began)
            {
                if (IsPointerOverUi(touch.fingerId)) return;
                TryStartPress(touch.fingerId, touch.position);
            }
            else if (_activePointerId == touch.fingerId
                     && (touch.phase == TouchPhase.Moved || touch.phase == TouchPhase.Stationary))
            {
                ContinuePointer(touch.position);
            }
            else if (_activePointerId == touch.fingerId
                     && (touch.phase == TouchPhase.Ended || touch.phase == TouchPhase.Canceled))
            {
                ReleaseOrCancel();
            }
        }

        private void HandleMouse()
        {
            const int mousePointerId = -1;
            var mousePosition = (Vector2)Input.mousePosition;
            if (Input.GetMouseButtonDown(0))
            {
                if (IsPointerOverUi(mousePointerId)) return;
                TryStartPress(mousePointerId, mousePosition);
            }
            else if (_activePointerId == mousePointerId && Input.GetMouseButton(0))
            {
                ContinuePointer(mousePosition);
            }
            else if (_activePointerId == mousePointerId && Input.GetMouseButtonUp(0))
            {
                ReleaseOrCancel();
            }
        }

        private bool TryStartPress(int pointerId, Vector2 screenPosition)
        {
            if (_state != PickupState.Idle) return false;
            if (!TryHitBody(screenPosition)) return false;

            _state = PickupState.Pressing;
            _activePointerId = pointerId;
            _pressScreenPosition = screenPosition;
            _lastScreenPosition = screenPosition;
            _pressStartedAt = Time.time;
            _dragPlaneY = targetRoot.position.y;
            _lastGroundPoint = targetRoot.position;
            return true;
        }

        private void ContinuePointer(Vector2 screenPosition)
        {
            if (_state == PickupState.Pressing)
            {
                _lastScreenPosition = screenPosition;
                if (Time.time - _pressStartedAt >= longPressSeconds)
                {
                    BeginPickup(screenPosition);
                }
                return;
            }

            if (_state != PickupState.Held) return;
            DragHeldModel(screenPosition);
        }

        private void BeginPickup(Vector2 screenPosition)
        {
            if (!TryResolveGroundPoint(screenPosition, out var groundPoint))
            {
                groundPoint = targetRoot.position;
            }

            _state = PickupState.Held;
            _heldStartedAt = Time.time;
            _currentPickupLiftMeters = ClampedPickupLift(pickupLiftMeters);
            _pickupBaseLiftMeters = _currentPickupLiftMeters;
            _pickupStartScreenPosition = screenPosition;
            _lastGroundPoint = groundPoint;
            _lastScreenPosition = screenPosition;

            if (!SendBodyCapability("body_held_in_air", groundPoint, 0f))
            {
                ResetState();
                return;
            }

            targetRoot.position = LiftedGroundPoint(groundPoint);
        }

        private void DragHeldModel(Vector2 screenPosition)
        {
            if (!TryResolveGroundPoint(screenPosition, out var groundPoint)) return;
            UpdatePickupLiftFromPointer(screenPosition);

            _lastGroundPoint = groundPoint;
            _lastScreenPosition = screenPosition;
            targetRoot.position = LiftedGroundPoint(groundPoint);
        }

        private void ReleaseOrCancel()
        {
            if (_state == PickupState.Held)
            {
                if (TryResolveGroundPoint(_lastScreenPosition, out var groundPoint))
                {
                    _lastGroundPoint = groundPoint;
                    targetRoot.position = groundPoint;
                    SendBodyCapability("body_place_release", groundPoint, 0f);
                }
                else
                {
                    SendBodyCapability("body_place_cancel", _lastGroundPoint, 0f);
                    DropToLastGroundPoint();
                }
            }
            else if (_state == PickupState.Pressing && IsClickGesture())
            {
                TriggerBodyClick();
            }
            ResetState();
        }

        private void CancelPickup()
        {
            if (_state == PickupState.Held)
            {
                SendBodyCapability("body_place_cancel", _lastGroundPoint, 0f);
                DropToLastGroundPoint();
            }
            ResetState();
        }

        private bool TryHitBody(Vector2 screenPosition)
        {
            var ray = targetCamera.ScreenPointToRay(screenPosition);
            var hits = Physics.RaycastAll(ray, maxRayDistanceMeters, bodyRaycastMask, QueryTriggerInteraction.Collide);
            if (hits == null || hits.Length == 0) return false;

            Array.Sort(hits, (a, b) => a.distance.CompareTo(b.distance));
            for (int i = 0; i < hits.Length; i++)
            {
                var hit = hits[i];
                if (hit.collider == null) continue;
                if (hit.collider.GetComponentInParent<NerCheekHitRegion>() != null) return false;
                if (_autoBodyColliders.Contains(hit.collider)) return true;
                if (IsOwnModelCollider(hit.collider)) return true;
            }
            return false;
        }

        private bool TryResolveGroundPoint(Vector2 screenPosition, out Vector3 groundPoint)
        {
            var ray = targetCamera.ScreenPointToRay(screenPosition);
            var hits = Physics.RaycastAll(ray, maxRayDistanceMeters, placementRaycastMask, QueryTriggerInteraction.Ignore);
            if (hits != null && hits.Length > 0)
            {
                Array.Sort(hits, (a, b) => a.distance.CompareTo(b.distance));
                for (int i = 0; i < hits.Length; i++)
                {
                    var hit = hits[i];
                    if (hit.collider == null) continue;
                    if (IsOwnModelCollider(hit.collider)) continue;
                    groundPoint = hit.point;
                    return true;
                }
            }

            var plane = new Plane(Vector3.up, new Vector3(0f, _dragPlaneY, 0f));
            if (plane.Raycast(ray, out float enter))
            {
                groundPoint = ray.GetPoint(enter);
                return true;
            }

            groundPoint = targetRoot != null ? targetRoot.position : transform.position;
            return false;
        }

        private bool SendBodyCapability(string capabilityId, Vector3 groundPoint, float dragSpeed)
        {
            if (controller == null) return true;
            var payload = new BodyInteractionPayload
            {
                state = capabilityId,
                held_seconds = _state == PickupState.Held ? Mathf.Max(0f, Time.time - _heldStartedAt) : 0f,
                lift_m = _state == PickupState.Held ? _currentPickupLiftMeters : pickupLiftMeters,
                drag_speed = Mathf.Max(0f, dragSpeed),
                ground_x = groundPoint.x,
                ground_y = groundPoint.y,
                ground_z = groundPoint.z,
            };
            return controller.ApplyCapability(capabilityId, JsonUtility.ToJson(payload));
        }

        private void UpdateHeldLoopCapability()
        {
            if (_state != PickupState.Held) return;
            targetRoot.position = LiftedGroundPoint(_lastGroundPoint);
        }

        private void UpdatePickupLiftFromPointer(Vector2 screenPosition)
        {
            float range = Mathf.Max(0.001f, maxPickupLiftMeters - minPickupLiftMeters);
            float normalizedDelta = (screenPosition.y - _pickupStartScreenPosition.y) / Mathf.Max(1f, heightDragPixelsForFullRange);
            _currentPickupLiftMeters = ClampedPickupLift(_pickupBaseLiftMeters + normalizedDelta * range);
        }

        private float ClampedPickupLift(float liftMeters)
        {
            float minLift = Mathf.Min(minPickupLiftMeters, maxPickupLiftMeters);
            float maxLift = Mathf.Max(minPickupLiftMeters, maxPickupLiftMeters);
            return Mathf.Clamp(liftMeters, minLift, maxLift);
        }

        private Vector3 LiftedGroundPoint(Vector3 groundPoint)
        {
            float ascent = pickupAscentSeconds <= 0f
                ? 1f
                : Mathf.Clamp01((Time.time - _heldStartedAt) / pickupAscentSeconds);
            ascent = ascent * ascent * (3f - 2f * ascent);
            return groundPoint + Vector3.up * (_currentPickupLiftMeters * ascent);
        }

        private void TriggerBodyClick()
        {
            if (controller == null) return;
            controller.ApplyCapability("pat_idle", "{}");
            QueueCapability("pat_end", clickEndDelaySeconds);
        }

        private void QueueCapability(string capabilityId, float delaySeconds)
        {
            _queuedCapabilityId = capabilityId;
            _queuedCapabilityAt = Time.time + Mathf.Max(0f, delaySeconds);
        }

        private void UpdateQueuedCapability()
        {
            if (controller == null) return;
            if (string.IsNullOrEmpty(_queuedCapabilityId)) return;
            if (Time.time < _queuedCapabilityAt) return;

            string capabilityId = _queuedCapabilityId;
            ClearQueuedCapability();
            controller.ApplyCapability(capabilityId, "{}");
        }

        private void ClearQueuedCapability()
        {
            _queuedCapabilityId = "";
            _queuedCapabilityAt = -1f;
        }

        private void EnsureBodyCollider()
        {
            if (_autoBodyColliders.Count > 0) return;

            var go = new GameObject("NerBodyPickupHit");
            go.transform.SetParent(transform, false);
            go.transform.localPosition = Vector3.zero;
            go.transform.localRotation = Quaternion.identity;
            go.transform.localScale = Vector3.one;

            var collider = go.AddComponent<BoxCollider>();
            collider.isTrigger = true;
            collider.center = bodyColliderCenter;
            collider.size = bodyColliderSize;
            _autoBodyColliders.Add(collider);
        }

        private void ResetState()
        {
            _state = PickupState.Idle;
            _activePointerId = int.MinValue;
        }

        private void DropToLastGroundPoint()
        {
            if (targetRoot == null) return;
            targetRoot.position = _lastGroundPoint;
        }

        private bool IsOwnModelCollider(Collider collider)
        {
            if (collider == null) return false;
            var hitTransform = collider.transform;
            return hitTransform.IsChildOf(transform)
                || (targetRoot != null && hitTransform.IsChildOf(targetRoot));
        }

        private bool IsClickGesture()
        {
            float clickThreshold = Mathf.Min(Mathf.Max(1f, clickMaxPixels), Mathf.Max(1f, cancelBeforeHoldPixels));
            return (_lastScreenPosition - _pressScreenPosition).magnitude <= clickThreshold;
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
            Gizmos.color = new Color(0.45f, 0.75f, 1f, 0.32f);
            Gizmos.matrix = transform.localToWorldMatrix;
            Gizmos.DrawCube(bodyColliderCenter, bodyColliderSize);
        }

        private enum PickupState
        {
            Idle,
            Pressing,
            Held,
        }

        [Serializable]
        private struct BodyInteractionPayload
        {
            public string state;
            public float held_seconds;
            public float lift_m;
            public float drag_speed;
            public float ground_x;
            public float ground_y;
            public float ground_z;
        }
    }
}
