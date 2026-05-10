using System;
using System.Collections.Generic;
using ParrotApp.Parrot;
using UnityEngine;

#if ENABLE_INPUT_SYSTEM
using UnityEngine.InputSystem;
using UnityEngine.InputSystem.Controls;
#endif

namespace ParrotApp.NerTuning
{
    /// <summary>
    /// Test-only mouse harness for the Ner tuning scene.
    /// Kept under Assets/NerTuningTest so the App runtime interactors stay untouched.
    /// </summary>
    public class NerMouseTuningHarness : MonoBehaviour
    {
        [SerializeField] private Camera targetCamera;
        [SerializeField] private NerSpineController controller;
        [SerializeField] private Transform targetRoot;
        [SerializeField] private Vector3 leftCheekLocalPosition = new Vector3(-0.42f, 2.0f, -0.23f);
        [SerializeField] private Vector3 rightCheekLocalPosition = new Vector3(0.42f, 2.0f, -0.23f);
        [SerializeField] private bool enableRightCheek = false;
        [SerializeField] private float cheekRadiusMeters = 0.35f;
        [SerializeField] private Vector3 headPatLocalPosition = new Vector3(0f, 2.55f, -0.2f);
        [SerializeField] private float headPatRadiusMeters = 0.42f;
        [SerializeField] private Vector3 bodyColliderCenter = new Vector3(0f, 1.1f, -0.1f);
        [SerializeField] private Vector3 bodyColliderSize = new Vector3(1.5f, 2.4f, 1.2f);
        [SerializeField] private float dragPixelsForFullStrength = 120f;
        [SerializeField] private float warningStrength = 0.68f;
        [SerializeField] private float warningIntervalSeconds = 0.75f;
        [SerializeField] private float longPressSeconds = 0.58f;
        [SerializeField] private float cancelBeforeHoldPixels = 28f;
        [SerializeField] private float clickMaxPixels = 22f;
        [SerializeField] private float facePatClickMaxSeconds = 0.36f;
        [SerializeField] private float clickEndDelaySeconds = 0.55f;
        [SerializeField] private float pickupLiftMeters = 0.12f;
        [SerializeField] private float minPickupLiftMeters = 0.06f;
        [SerializeField] private float maxPickupLiftMeters = 0.22f;
        [SerializeField] private float heightDragPixelsForFullRange = 260f;
        [SerializeField] private float pickupHeightWheelStepMeters = 0.015f;
        [SerializeField] private float pickupAscentSeconds = 0.16f;
        [SerializeField] private float maxRayDistanceMeters = 8f;
        [SerializeField] private bool keyboardMovementEnabled = true;
        [SerializeField] private float moveSpeedMetersPerSecond = 0.28f;
        [SerializeField] private float controllerWalkBaselineMetersPerSecond = 0.35f;
        [SerializeField] private LayerMask raycastMask = ~0;

        private readonly Dictionary<Collider, string> _cheekSideByCollider = new Dictionary<Collider, string>();
        private readonly HashSet<Collider> _headPatColliders = new HashSet<Collider>();
        private readonly HashSet<Collider> _bodyColliders = new HashSet<Collider>();
        private PointerMode _mode = PointerMode.Idle;
        private string _activeSide = "";
        private Vector2 _pressScreenPosition;
        private Vector2 _lastScreenPosition;
        private Vector3 _lastGroundPoint;
        private float _pressStartedAt;
        private float _heldStartedAt;
        private float _dragPlaneY;
        private float _lastWarningAt = -999f;
        private float _currentPickupLiftMeters;
        private float _pickupBaseLiftMeters;
        private Vector2 _pickupStartScreenPosition;
        private string _queuedCapabilityId = "";
        private float _queuedCapabilityAt = -1f;
        private bool _missingInputLogged;

        void Awake()
        {
            if (targetCamera == null) targetCamera = Camera.main;
            if (controller == null) controller = GetComponentInParent<NerSpineController>();
            if (targetRoot == null) targetRoot = transform;
            EnsureTestColliders();
        }

        void Update()
        {
            if (targetCamera == null) targetCamera = Camera.main;
            if (targetCamera == null || controller == null || targetRoot == null) return;
            UpdateQueuedCapability();
            UpdateHeldLoopCapability();

#if ENABLE_INPUT_SYSTEM
            var mouse = Mouse.current;
            if (keyboardMovementEnabled && _mode == PointerMode.Idle)
            {
                HandleKeyboardMovement();
            }

            if (mouse == null) return;

            var screenPosition = mouse.position.ReadValue();
            if (mouse.leftButton.wasPressedThisFrame)
            {
                BeginPointer(screenPosition);
            }
            else if (mouse.leftButton.isPressed)
            {
                ContinuePointer(screenPosition);
            }
            else if (mouse.leftButton.wasReleasedThisFrame)
            {
                ReleasePointer();
            }
#else
            if (!_missingInputLogged)
            {
                _missingInputLogged = true;
                Debug.LogWarning("[NerMouseTuningHarness] Unity Input System is not enabled; mouse tuning is unavailable.");
            }
#endif
        }

        void OnDisable()
        {
            if (_mode == PointerMode.Cheek)
            {
                SendCheekCapability("cheek_recover", 0f, Vector2.zero);
            }
            else if (_mode == PointerMode.HeadPat)
            {
                // Face-center pat is a tap-only gesture, so no release capability is needed here.
            }
            else if (_mode == PointerMode.HeldBody)
            {
                SendBodyCapability("body_place_cancel", _lastGroundPoint, 0f);
                targetRoot.position = _lastGroundPoint;
            }
            ClearQueuedCapability();
            ResetPointer();
        }

        private void BeginPointer(Vector2 screenPosition)
        {
            _pressScreenPosition = screenPosition;
            _lastScreenPosition = screenPosition;
            _pressStartedAt = Time.time;
            _lastWarningAt = -999f;

            if (TryHitCheek(screenPosition, out var side))
            {
                _mode = PointerMode.Cheek;
                _activeSide = side;
                SendCheekCapability("cheek_pinch_start", 0.14f, Vector2.zero);
                return;
            }

            if (TryHitHeadPat(screenPosition))
            {
                _mode = PointerMode.HeadPat;
                return;
            }

            if (TryHitBody(screenPosition))
            {
                _mode = PointerMode.PressingBody;
                _dragPlaneY = targetRoot.position.y;
                _lastGroundPoint = targetRoot.position;
            }
        }

        private void ContinuePointer(Vector2 screenPosition)
        {
            if (_mode == PointerMode.Cheek)
            {
                ContinueCheek(screenPosition);
                return;
            }

            if (_mode == PointerMode.HeadPat)
            {
                _lastScreenPosition = screenPosition;
                return;
            }

            if (_mode == PointerMode.PressingBody)
            {
                _lastScreenPosition = screenPosition;
                if (Time.time - _pressStartedAt >= longPressSeconds)
                {
                    BeginPickup(screenPosition);
                }
                return;
            }

            if (_mode == PointerMode.HeldBody)
            {
                DragHeldModel(screenPosition);
            }
        }

        private void ReleasePointer()
        {
            if (_mode == PointerMode.Cheek)
            {
                bool isClick = IsClickGesture();
                SendCheekCapability("cheek_pinch_release", 0f, Vector2.zero);
                if (isClick) TriggerCheekClick();
            }
            else if (_mode == PointerMode.HeadPat)
            {
                if (IsClickGesture() && Time.time - _pressStartedAt <= facePatClickMaxSeconds)
                {
                    TriggerFacePatClick();
                }
            }
            else if (_mode == PointerMode.PressingBody)
            {
                if (IsClickGesture())
                {
                    TriggerBodyClick();
                }
            }
            else if (_mode == PointerMode.HeldBody)
            {
                ReleasePickup();
            }
            ResetPointer();
        }

        private void ContinueCheek(Vector2 screenPosition)
        {
            _lastScreenPosition = screenPosition;
            var drag = (screenPosition - _pressScreenPosition) / Mathf.Max(1f, dragPixelsForFullStrength);
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

        private void BeginPickup(Vector2 screenPosition)
        {
            if (!TryResolveGroundPoint(screenPosition, out var groundPoint))
            {
                groundPoint = targetRoot.position;
            }

            _mode = PointerMode.HeldBody;
            _heldStartedAt = Time.time;
            _currentPickupLiftMeters = ClampedPickupLift(pickupLiftMeters);
            _pickupBaseLiftMeters = _currentPickupLiftMeters;
            _pickupStartScreenPosition = screenPosition;
            _lastGroundPoint = groundPoint;
            _lastScreenPosition = screenPosition;

            if (!SendBodyCapability("body_held_in_air", groundPoint, 0f))
            {
                ResetPointer();
                return;
            }

            targetRoot.position = LiftedGroundPoint(groundPoint);
        }

        private void DragHeldModel(Vector2 screenPosition)
        {
            if (!TryResolveGroundPoint(screenPosition, out var groundPoint)) return;
            UpdatePickupLiftFromPointer(screenPosition);
            UpdatePickupLiftFromMouseWheel(screenPosition);

            _lastGroundPoint = groundPoint;
            _lastScreenPosition = screenPosition;
            targetRoot.position = LiftedGroundPoint(groundPoint);
        }

        private void ReleasePickup()
        {
            if (TryResolveGroundPoint(_lastScreenPosition, out var groundPoint))
            {
                _lastGroundPoint = groundPoint;
            }

            targetRoot.position = _lastGroundPoint;
            SendBodyCapability("body_place_release", _lastGroundPoint, 0f);
        }

#if ENABLE_INPUT_SYSTEM
        private void HandleKeyboardMovement()
        {
            var keyboard = Keyboard.current;
            if (keyboard == null) return;

            var input = Vector2.zero;
            if (IsPressed(keyboard.aKey) || IsPressed(keyboard.leftArrowKey)) input.x -= 1f;
            if (IsPressed(keyboard.dKey) || IsPressed(keyboard.rightArrowKey)) input.x += 1f;
            if (IsPressed(keyboard.wKey) || IsPressed(keyboard.upArrowKey)) input.y += 1f;
            if (IsPressed(keyboard.sKey) || IsPressed(keyboard.downArrowKey)) input.y -= 1f;
            if (input.sqrMagnitude <= 0.0001f) return;

            input = Vector2.ClampMagnitude(input, 1f);
            float scaledDeltaTime = Time.deltaTime;
            if (controllerWalkBaselineMetersPerSecond > 0.001f)
            {
                scaledDeltaTime *= moveSpeedMetersPerSecond / controllerWalkBaselineMetersPerSecond;
            }

            var payload = new WalkPayload
            {
                x = input.x,
                y = 0f,
                z = input.y,
                deltaTime = scaledDeltaTime,
            };
            controller.ApplyCapability("spine_walk", JsonUtility.ToJson(payload));
        }

        private static bool IsPressed(ButtonControl key)
        {
            return key != null && key.isPressed;
        }
#endif

        private bool TryHitCheek(Vector2 screenPosition, out string side)
        {
            side = "";
            var ray = targetCamera.ScreenPointToRay(screenPosition);
            var hits = Physics.RaycastAll(ray, maxRayDistanceMeters, raycastMask, QueryTriggerInteraction.Collide);
            if (hits == null || hits.Length == 0) return false;

            Array.Sort(hits, (a, b) => a.distance.CompareTo(b.distance));
            for (int i = 0; i < hits.Length; i++)
            {
                if (hits[i].collider == null) continue;
                if (_cheekSideByCollider.TryGetValue(hits[i].collider, out side)) return true;
            }
            return false;
        }

        private bool TryHitHeadPat(Vector2 screenPosition)
        {
            var ray = targetCamera.ScreenPointToRay(screenPosition);
            var hits = Physics.RaycastAll(ray, maxRayDistanceMeters, raycastMask, QueryTriggerInteraction.Collide);
            if (hits == null || hits.Length == 0) return false;

            Array.Sort(hits, (a, b) => a.distance.CompareTo(b.distance));
            for (int i = 0; i < hits.Length; i++)
            {
                var collider = hits[i].collider;
                if (collider == null) continue;
                if (_headPatColliders.Contains(collider)) return true;
            }
            return false;
        }

        private bool TryHitBody(Vector2 screenPosition)
        {
            var ray = targetCamera.ScreenPointToRay(screenPosition);
            var hits = Physics.RaycastAll(ray, maxRayDistanceMeters, raycastMask, QueryTriggerInteraction.Collide);
            if (hits == null || hits.Length == 0) return false;

            Array.Sort(hits, (a, b) => a.distance.CompareTo(b.distance));
            for (int i = 0; i < hits.Length; i++)
            {
                var collider = hits[i].collider;
                if (collider == null) continue;
                if (_cheekSideByCollider.ContainsKey(collider)) return false;
                if (_headPatColliders.Contains(collider)) return false;
                if (_bodyColliders.Contains(collider)) return true;
            }
            return false;
        }

        private bool TryResolveGroundPoint(Vector2 screenPosition, out Vector3 groundPoint)
        {
            var ray = targetCamera.ScreenPointToRay(screenPosition);
            var hits = Physics.RaycastAll(ray, maxRayDistanceMeters, raycastMask, QueryTriggerInteraction.Ignore);
            if (hits != null && hits.Length > 0)
            {
                Array.Sort(hits, (a, b) => a.distance.CompareTo(b.distance));
                for (int i = 0; i < hits.Length; i++)
                {
                    var collider = hits[i].collider;
                    if (collider == null) continue;
                    if (IsOwnCollider(collider)) continue;
                    groundPoint = hits[i].point;
                    return true;
                }
            }

            var plane = new Plane(Vector3.up, new Vector3(0f, _dragPlaneY, 0f));
            if (plane.Raycast(ray, out float enter))
            {
                groundPoint = ray.GetPoint(enter);
                return true;
            }

            groundPoint = targetRoot.position;
            return false;
        }

        private void SendCheekCapability(string capabilityId, float strength, Vector2 drag)
        {
            var payload = new CheekPayload
            {
                side = string.IsNullOrEmpty(_activeSide) ? "both" : _activeSide,
                strength = Mathf.Clamp01(strength),
                drag_x = Mathf.Clamp(drag.x, -1f, 1f),
                drag_y = Mathf.Clamp(drag.y, -1f, 1f),
            };
            controller.ApplyCapability(capabilityId, JsonUtility.ToJson(payload));
        }

        private bool SendBodyCapability(string capabilityId, Vector3 groundPoint, float dragSpeed)
        {
            var payload = new BodyPayload
            {
                state = capabilityId,
                held_seconds = _mode == PointerMode.HeldBody ? Mathf.Max(0f, Time.time - _heldStartedAt) : 0f,
                lift_m = _mode == PointerMode.HeldBody ? _currentPickupLiftMeters : pickupLiftMeters,
                drag_speed = Mathf.Max(0f, dragSpeed),
                ground_x = groundPoint.x,
                ground_y = groundPoint.y,
                ground_z = groundPoint.z,
            };
            return controller.ApplyCapability(capabilityId, JsonUtility.ToJson(payload));
        }

        private void TriggerCheekClick()
        {
            controller.ApplyCapability("touch_idle", "{}");
            QueueCapability("touch_end", clickEndDelaySeconds);
        }

        private void TriggerBodyClick()
        {
            controller.ApplyCapability("pat_idle", "{}");
            QueueCapability("pat_end", clickEndDelaySeconds);
        }

        private void TriggerFacePatClick()
        {
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

        private void UpdateHeldLoopCapability()
        {
            if (_mode != PointerMode.HeldBody) return;
            targetRoot.position = LiftedGroundPoint(_lastGroundPoint);
        }

        private void UpdatePickupLiftFromPointer(Vector2 screenPosition)
        {
            float range = Mathf.Max(0.001f, maxPickupLiftMeters - minPickupLiftMeters);
            float normalizedDelta = (screenPosition.y - _pickupStartScreenPosition.y) / Mathf.Max(1f, heightDragPixelsForFullRange);
            _currentPickupLiftMeters = ClampedPickupLift(_pickupBaseLiftMeters + normalizedDelta * range);
        }

        private void UpdatePickupLiftFromMouseWheel(Vector2 screenPosition)
        {
#if ENABLE_INPUT_SYSTEM
            var mouse = Mouse.current;
            if (mouse == null) return;

            float scroll = mouse.scroll.ReadValue().y;
            if (Mathf.Abs(scroll) <= 0.01f) return;
            _currentPickupLiftMeters = ClampedPickupLift(
                _currentPickupLiftMeters + Mathf.Sign(scroll) * pickupHeightWheelStepMeters);
            _pickupBaseLiftMeters = _currentPickupLiftMeters;
            _pickupStartScreenPosition = screenPosition;
#endif
        }

        private Vector3 LiftedGroundPoint(Vector3 groundPoint)
        {
            float ascent = pickupAscentSeconds <= 0f
                ? 1f
                : Mathf.Clamp01((Time.time - _heldStartedAt) / pickupAscentSeconds);
            ascent = ascent * ascent * (3f - 2f * ascent);
            return groundPoint + Vector3.up * (_currentPickupLiftMeters * ascent);
        }

        private float ClampedPickupLift(float liftMeters)
        {
            float minLift = Mathf.Min(minPickupLiftMeters, maxPickupLiftMeters);
            float maxLift = Mathf.Max(minPickupLiftMeters, maxPickupLiftMeters);
            return Mathf.Clamp(liftMeters, minLift, maxLift);
        }

        private bool IsClickGesture()
        {
            float clickThreshold = Mathf.Min(Mathf.Max(1f, clickMaxPixels), Mathf.Max(1f, cancelBeforeHoldPixels));
            return (_lastScreenPosition - _pressScreenPosition).magnitude <= clickThreshold;
        }

        private void EnsureTestColliders()
        {
            if (_cheekSideByCollider.Count == 0)
            {
                RegisterCheekCollider("left", leftCheekLocalPosition);
                if (enableRightCheek) RegisterCheekCollider("right", rightCheekLocalPosition);
            }
            if (_headPatColliders.Count == 0)
            {
                RegisterHeadPatCollider();
            }
            if (_bodyColliders.Count == 0)
            {
                var go = new GameObject("NerTuningBodyHit");
                go.transform.SetParent(transform, false);
                go.transform.localPosition = Vector3.zero;
                var collider = go.AddComponent<BoxCollider>();
                collider.isTrigger = true;
                collider.center = bodyColliderCenter;
                collider.size = bodyColliderSize;
                _bodyColliders.Add(collider);
            }
        }

        private void RegisterCheekCollider(string side, Vector3 localPosition)
        {
            var go = new GameObject("NerTuningCheekHit_" + side);
            go.transform.SetParent(transform, false);
            go.transform.localPosition = localPosition;
            var collider = go.AddComponent<SphereCollider>();
            collider.isTrigger = true;
            collider.radius = cheekRadiusMeters;
            _cheekSideByCollider[collider] = side;
        }

        private void RegisterHeadPatCollider()
        {
            var go = new GameObject("NerTuningFacePatHit");
            go.transform.SetParent(transform, false);
            go.transform.localPosition = headPatLocalPosition;
            var collider = go.AddComponent<SphereCollider>();
            collider.isTrigger = true;
            collider.radius = headPatRadiusMeters;
            _headPatColliders.Add(collider);
        }

        private bool IsOwnCollider(Collider collider)
        {
            if (collider == null) return false;
            return collider.transform.IsChildOf(transform)
                || (targetRoot != null && collider.transform.IsChildOf(targetRoot));
        }

        private void ResetPointer()
        {
            _mode = PointerMode.Idle;
            _activeSide = "";
        }

        void OnDrawGizmosSelected()
        {
            Gizmos.matrix = transform.localToWorldMatrix;
            Gizmos.color = new Color(1f, 0.55f, 0.72f, 0.38f);
            Gizmos.DrawSphere(leftCheekLocalPosition, cheekRadiusMeters);
            if (enableRightCheek) Gizmos.DrawSphere(rightCheekLocalPosition, cheekRadiusMeters);
            Gizmos.color = new Color(1f, 0.9f, 0.45f, 0.36f);
            Gizmos.DrawSphere(headPatLocalPosition, headPatRadiusMeters);
            Gizmos.color = new Color(0.45f, 0.75f, 1f, 0.32f);
            Gizmos.DrawCube(bodyColliderCenter, bodyColliderSize);
        }

        public bool RunScriptedPickupDropProbe()
        {
            if (controller == null || targetRoot == null) return false;

            Vector3 before = targetRoot.position;
            Vector3 groundPoint = before;
            Vector3 draggedGroundPoint = before + new Vector3(0.08f, 0f, 0.08f);
            _mode = PointerMode.HeldBody;
            _heldStartedAt = Time.time - pickupAscentSeconds;
            _currentPickupLiftMeters = ClampedPickupLift(pickupLiftMeters);
            _pickupBaseLiftMeters = _currentPickupLiftMeters;
            _lastGroundPoint = groundPoint;

            bool started = SendBodyCapability("body_held_in_air", groundPoint, 0f);
            targetRoot.position = LiftedGroundPoint(groundPoint);
            bool lifted = targetRoot.position.y >= groundPoint.y + _currentPickupLiftMeters * 0.8f;
            bool held = SendBodyCapability("body_held_in_air", groundPoint, 0f);
            targetRoot.position = LiftedGroundPoint(draggedGroundPoint);
            bool dragged = SendBodyCapability("body_dragging_in_air", draggedGroundPoint, 0.5f);
            targetRoot.position = draggedGroundPoint;
            bool released = SendBodyCapability("body_place_release", draggedGroundPoint, 0f);
            bool placed = Mathf.Abs(targetRoot.position.y - draggedGroundPoint.y) <= 0.002f;

            targetRoot.position = before;
            _lastGroundPoint = before;
            ResetPointer();
            return started && lifted && held && dragged && released && placed;
        }

        private enum PointerMode
        {
            Idle,
            Cheek,
            HeadPat,
            PressingBody,
            HeldBody,
        }

        [Serializable]
        private struct CheekPayload
        {
            public string side;
            public float strength;
            public float drag_x;
            public float drag_y;
        }

        [Serializable]
        private struct BodyPayload
        {
            public string state;
            public float held_seconds;
            public float lift_m;
            public float drag_speed;
            public float ground_x;
            public float ground_y;
            public float ground_z;
        }

        [Serializable]
        private struct WalkPayload
        {
            public float x;
            public float y;
            public float z;
            public float deltaTime;
        }
    }
}
