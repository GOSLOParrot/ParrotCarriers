using System;
using System.Collections.Generic;
using System.Reflection;
using UnityEngine;

namespace ParrotApp.Parrot
{
    /// <summary>
    /// Minimal manifest-driven controller for the imported Ner Spine asset.
    ///
    /// This controller deliberately avoids a compile-time dependency on the
    /// Spine Unity API. The package is present in the Unity project, but using
    /// reflection keeps the App bootstrap path readable even while the Ner
    /// prefab is still being wired.
    /// </summary>
    public class NerSpineController : MonoBehaviour, IParrotController
    {
        [SerializeField] private float walkSpeedMetersPerSecond = 0.35f;

        private ModelManifestDto _manifest;
        private HashSet<string> _supportedCaps = new HashSet<string>();
        private HashSet<string> _knownSpineAnimations = new HashSet<string>();
        private readonly Dictionary<string, string> _handlerByCapability = new Dictionary<string, string>();
        private readonly Dictionary<string, BonePose> _cheekBoneSetup = new Dictionary<string, BonePose>();
        private object _spineAnimationState;
        private MethodInfo _setAnimation;
        private object _spineSkeleton;
        private MethodInfo _findBone;
        private MethodInfo _updateSkeletonWorldTransform;
        private float _reactiveTouchSuppressedUntil;

        public string ModelId => _manifest != null ? _manifest.model_id : "ner_skin2";
        public IReadOnlyCollection<string> SupportedCapabilities => _supportedCaps;
        public bool ParrotReflexEnabled => false;

        void Awake()
        {
            CacheSpineHandles();
        }

        void Start()
        {
            if (_supportedCaps.Count == 0)
            {
                ConfigureFallbackCapabilities();
            }
        }

        public void ConfigureFromManifest(ModelManifestDto manifest)
        {
            if (manifest == null) return;
            _manifest = manifest;
            _supportedCaps = manifest.DeclaredCapabilityIds;
            _handlerByCapability.Clear();

            if (manifest.capabilities != null)
            {
                for (int i = 0; i < manifest.capabilities.Length; i++)
                {
                    var c = manifest.capabilities[i];
                    if (c == null || string.IsNullOrEmpty(c.capability_id)) continue;
                    if (!string.IsNullOrEmpty(c.handler))
                    {
                        _handlerByCapability[c.capability_id] = c.handler;
                    }
                }
            }

            CacheSpineHandles();
        }

        public bool ApplyCapability(string capabilityId, string parametersJson)
        {
            if (string.IsNullOrEmpty(capabilityId)) return false;
            if (_supportedCaps.Count > 0 && !_supportedCaps.Contains(capabilityId)) return false;

            if (capabilityId.StartsWith("lineb_", StringComparison.Ordinal))
            {
                return ApplyLineBVoiceActivity(capabilityId, parametersJson);
            }

            if (IsReactiveTouchSuppressed(capabilityId))
            {
                if (capabilityId == "body_pickup_start"
                    || capabilityId == "body_held_in_air"
                    || capabilityId == "body_dragging_in_air"
                    || capabilityId == "body_place_preview")
                {
                    return false;
                }
                if (capabilityId.StartsWith("cheek_", StringComparison.Ordinal))
                {
                    ResetCheekPose();
                }
                return true;
            }

            if (capabilityId.StartsWith("cheek_", StringComparison.Ordinal))
            {
                return ApplyCheekCapability(capabilityId, parametersJson);
            }

            if (capabilityId.StartsWith("body_", StringComparison.Ordinal))
            {
                return ApplyBodyInteractionCapability(capabilityId, parametersJson);
            }

            if (capabilityId == "spine_walk")
            {
                return ApplyWalk(parametersJson);
            }

            if (!_handlerByCapability.TryGetValue(capabilityId, out var handler)
                || string.IsNullOrEmpty(handler))
            {
                handler = capabilityId;
            }

            var animationName = ResolveAnimationName(handler, parametersJson);
            return TryPlaySpineAnimation(animationName, ShouldLoop(capabilityId));
        }

        private void ConfigureFallbackCapabilities()
        {
            AddFallback("spine_idle", "Idle_1");
            AddFallback("face_happy", "Happy_1");
            AddFallback("face_angry", "Angry_1");
            AddFallback("face_sad", "Sad_1");
            AddFallback("face_shame", "Shame_1");
            AddFallback("face_surprise", "Surprise_1");
            AddFallback("face_panic", "Panic_1");
            AddFallback("touch_idle", "Touch_Idle");
            AddFallback("touch_end", "Touch_End");
            AddFallback("pat_idle", "Pat_Idle");
            AddFallback("pat_end", "Pat_End");
            AddFallback("tickle_idle", "Tickle_Idle_1");
            AddFallback("tickle_end", "Tickle_End");
            AddFallback("eat", "Eat_1");
            AddFallback("cheek_pinch_start", "Touch_Idle");
            AddFallback("cheek_pinch_hold", "");
            AddFallback("cheek_pinch_warning", "Serious_1");
            AddFallback("cheek_pinch_release", "Touch_End");
            AddFallback("cheek_recover", "Idle_1");
            AddFallback("body_pickup_start", "Surprise_1");
            AddFallback("body_held_in_air", "Close_1");
            AddFallback("body_dragging_in_air", "Panic_1");
            AddFallback("body_place_preview", "Think_1");
            AddFallback("body_place_release", "Idle_1");
            AddFallback("body_place_cancel", "Worry_1");
            AddFallback("face_blank", "Blank_1");
            AddFallback("face_close", "Close_1");
            AddFallback("face_notmyfault", "Notmyfault_1");
            AddFallback("face_proud", "Proud_1");
            AddFallback("face_serious", "Serious_1");
            AddFallback("face_sulky", "Sulky_1");
            AddFallback("face_think", "Think_1");
            AddFallback("face_tired", "Tired_1");
            AddFallback("face_worry", "Worry_1");
            AddFallback("smash_end", "Smash_End_1");
            AddFallback("spine_walk", "");
            AddFallback("lineb_speaking", "Close_1");
            AddFallback("lineb_listening", "Think_1");
            AddFallback("lineb_echo_suppressed", "Idle_1");
            AddFallback("lineb_listening_uncertain", "Worry_1");
            AddFallback("lineb_listening_noise", "Idle_1");
        }

        private void AddFallback(string capabilityId, string handler)
        {
            _supportedCaps.Add(capabilityId);
            if (!string.IsNullOrEmpty(handler)) _handlerByCapability[capabilityId] = handler;
        }

        private void CacheSpineHandles()
        {
            _spineAnimationState = null;
            _setAnimation = null;
            _spineSkeleton = null;
            _findBone = null;
            _updateSkeletonWorldTransform = null;
            _cheekBoneSetup.Clear();
            _knownSpineAnimations.Clear();

            var components = GetComponentsInChildren<Component>(true);
            for (int i = 0; i < components.Length; i++)
            {
                var c = components[i];
                if (c == null) continue;
                var type = c.GetType();
                if (type.FullName != "Spine.Unity.SkeletonAnimation"
                    && type.FullName != "Spine.Unity.SkeletonGraphic")
                {
                    continue;
                }

                CollectAnimationNames(c);
                CacheSkeletonHandles(c);

                var stateProperty = type.GetProperty("AnimationState");
                _spineAnimationState = stateProperty?.GetValue(c, null);
                if (_spineAnimationState == null) continue;

                _setAnimation = _spineAnimationState.GetType().GetMethod(
                    "SetAnimation",
                    new[] { typeof(int), typeof(string), typeof(bool) });
                if (_setAnimation != null) return;
            }
        }

        private void CacheSkeletonHandles(Component spineComponent)
        {
            _spineSkeleton = TryGetSkeleton(spineComponent);
            if (_spineSkeleton == null) return;

            var type = _spineSkeleton.GetType();
            _findBone = type.GetMethod("FindBone", new[] { typeof(string) });
            _updateSkeletonWorldTransform = type.GetMethod("UpdateWorldTransform", Type.EmptyTypes);
            CaptureCheekBone("S1_F_Ball_L_CT");
            CaptureCheekBone("S1_F_Ball_R_CT");
            CaptureCheekBone("Character_Ball_Move");
        }

        private bool TryPlaySpineAnimation(string animationName, bool loop)
        {
            if (string.IsNullOrEmpty(animationName)) return false;
            if (_spineAnimationState == null || _setAnimation == null)
            {
                CacheSpineHandles();
            }
            if (_spineAnimationState == null || _setAnimation == null)
            {
                Debug.LogWarning($"[NerSpineController] Spine animation state not found for '{animationName}'.");
                return false;
            }
            if (_knownSpineAnimations.Count > 0 && !_knownSpineAnimations.Contains(animationName))
            {
                Debug.LogWarning($"[NerSpineController] Animation '{animationName}' not found; returning unsupported.");
                TryPlayIdleFallback();
                return false;
            }

            try
            {
                _setAnimation.Invoke(_spineAnimationState, new object[] { 0, animationName, loop });
                return true;
            }
            catch (Exception ex)
            {
                Debug.LogWarning($"[NerSpineController] Failed to play '{animationName}': {ex.Message}");
                TryPlayIdleFallback();
                return false;
            }
        }

        private void TryPlayIdleFallback()
        {
            if (_spineAnimationState == null || _setAnimation == null) return;
            if (_knownSpineAnimations.Count > 0 && !_knownSpineAnimations.Contains("Idle_1")) return;
            try
            {
                _setAnimation.Invoke(_spineAnimationState, new object[] { 0, "Idle_1", true });
            }
            catch
            {
                // Best-effort visual fallback only; caller still receives false.
            }
        }

        private void CollectAnimationNames(Component spineComponent)
        {
            object skeletonData = TryGetSkeletonData(spineComponent);
            if (skeletonData == null) return;

            object animations = skeletonData.GetType().GetProperty("Animations")?.GetValue(skeletonData, null);
            if (animations == null)
            {
                animations = skeletonData.GetType()
                    .GetField("animations", BindingFlags.Instance | BindingFlags.Public | BindingFlags.NonPublic)
                    ?.GetValue(skeletonData);
            }
            var enumerable = animations as System.Collections.IEnumerable;
            if (enumerable == null) return;

            foreach (var animation in enumerable)
            {
                if (animation == null) continue;
                string name = animation.GetType().GetProperty("Name")?.GetValue(animation, null) as string;
                if (string.IsNullOrEmpty(name))
                {
                    name = animation.GetType()
                        .GetField("name", BindingFlags.Instance | BindingFlags.Public | BindingFlags.NonPublic)
                        ?.GetValue(animation) as string;
                }
                if (!string.IsNullOrEmpty(name)) _knownSpineAnimations.Add(name);
            }
        }

        private static object TryGetSkeletonData(Component spineComponent)
        {
            object skeleton = TryGetSkeleton(spineComponent);
            object data = skeleton?.GetType().GetProperty("Data")?.GetValue(skeleton, null);
            if (data != null) return data;

            var type = spineComponent.GetType();
            object skeletonDataAsset = type.GetProperty("SkeletonDataAsset")?.GetValue(spineComponent, null);
            if (skeletonDataAsset == null)
            {
                skeletonDataAsset = type.GetField("skeletonDataAsset", BindingFlags.Instance | BindingFlags.Public | BindingFlags.NonPublic)
                    ?.GetValue(spineComponent);
            }
            if (skeletonDataAsset == null) return null;

            var getSkeletonData = skeletonDataAsset.GetType().GetMethod("GetSkeletonData", new[] { typeof(bool) })
                ?? skeletonDataAsset.GetType().GetMethod("GetSkeletonData", Type.EmptyTypes);
            if (getSkeletonData == null) return null;

            return getSkeletonData.GetParameters().Length == 1
                ? getSkeletonData.Invoke(skeletonDataAsset, new object[] { false })
                : getSkeletonData.Invoke(skeletonDataAsset, null);
        }

        private static object TryGetSkeleton(Component spineComponent)
        {
            if (spineComponent == null) return null;
            return spineComponent.GetType().GetProperty("Skeleton")?.GetValue(spineComponent, null);
        }

        private string ResolveAnimationName(string defaultHandler, string parametersJson)
        {
            if (string.IsNullOrEmpty(parametersJson)) return defaultHandler;
            try
            {
                var p = JsonUtility.FromJson<AnimationJson>(parametersJson);
                if (!string.IsNullOrEmpty(p.animation)) return p.animation;
                if (p.variant > 0)
                {
                    var family = AnimationFamily(defaultHandler);
                    if (!string.IsNullOrEmpty(family)) return family + "_" + p.variant;
                }
            }
            catch
            {
                return defaultHandler;
            }
            return defaultHandler;
        }

        private static string AnimationFamily(string handler)
        {
            if (string.IsNullOrEmpty(handler)) return handler;
            int lastUnderscore = handler.LastIndexOf('_');
            if (lastUnderscore <= 0 || lastUnderscore >= handler.Length - 1) return handler;
            for (int i = lastUnderscore + 1; i < handler.Length; i++)
            {
                if (!char.IsDigit(handler[i])) return handler;
            }
            return handler.Substring(0, lastUnderscore);
        }

        private bool ApplyWalk(string parametersJson)
        {
            Vector3 input = Vector3.zero;
            float dt = Time.deltaTime;
            if (!string.IsNullOrEmpty(parametersJson))
            {
                try
                {
                    var p = JsonUtility.FromJson<WalkJson>(parametersJson);
                    input = new Vector3(p.x, 0f, Mathf.Abs(p.z) > 0.0001f ? p.z : p.y);
                    if (p.deltaTime > 0f) dt = p.deltaTime;
                    else if (p.dt > 0f) dt = p.dt;
                }
                catch
                {
                    input = Vector3.zero;
                }
            }

            if (input.sqrMagnitude > 0.0001f)
            {
                transform.localPosition += input.normalized * walkSpeedMetersPerSecond * dt;
            }
            TryPlaySpineAnimation("Idle_1", loop: true);
            return true;
        }

        private bool ApplyCheekCapability(string capabilityId, string parametersJson)
        {
            var p = ParseCheekPinch(parametersJson);
            if (capabilityId == "cheek_pinch_start")
            {
                TryPlaySpineAnimation("Touch_Idle", loop: true);
                ApplyCheekPose(p.WithDefaultStrength(0.18f));
                return true;
            }
            if (capabilityId == "cheek_pinch_hold")
            {
                ApplyCheekPose(p);
                return true;
            }
            if (capabilityId == "cheek_pinch_warning")
            {
                TryPlaySpineAnimation(p.strength > 0.82f ? "Angry_1" : "Serious_1", loop: false);
                ApplyCheekPose(p);
                return true;
            }
            if (capabilityId == "cheek_pinch_release")
            {
                ResetCheekPose();
                TryPlaySpineAnimation("Touch_End", loop: false);
                return true;
            }
            if (capabilityId == "cheek_recover")
            {
                ResetCheekPose();
                TryPlaySpineAnimation("Idle_1", loop: true);
                return true;
            }

            return false;
        }

        private bool ApplyBodyInteractionCapability(string capabilityId, string parametersJson)
        {
            var p = ParseBodyInteraction(parametersJson);
            if (capabilityId == "body_pickup_start")
            {
                ResetCheekPose();
                return TryPlaySpineAnimation("Surprise_1", loop: false) || TryPlaySpineAnimation("Idle_1", loop: true);
            }
            if (capabilityId == "body_held_in_air")
            {
                return TryPlaySpineAnimation("Close_1", loop: false) || TryPlaySpineAnimation("Idle_1", loop: true);
            }
            if (capabilityId == "body_dragging_in_air")
            {
                string animationName = p.drag_speed > 0.45f ? "Panic_1" : "Close_1";
                return TryPlaySpineAnimation(animationName, loop: false) || TryPlaySpineAnimation("Idle_1", loop: true);
            }
            if (capabilityId == "body_place_preview")
            {
                return TryPlaySpineAnimation("Think_1", loop: false) || TryPlaySpineAnimation("Idle_1", loop: true);
            }
            if (capabilityId == "body_place_release")
            {
                ResetCheekPose();
                return TryPlaySpineAnimation("Idle_1", loop: true);
            }
            if (capabilityId == "body_place_cancel")
            {
                ResetCheekPose();
                return TryPlaySpineAnimation("Worry_1", loop: false) || TryPlaySpineAnimation("Idle_1", loop: true);
            }
            return false;
        }

        private bool ApplyLineBVoiceActivity(string capabilityId, string parametersJson)
        {
            var p = ParseVoiceActivity(parametersJson);
            if (capabilityId == "lineb_speaking")
            {
                ResetCheekPose();
                SuppressReactiveTouch(Mathf.Max(0.35f, p.suppression_duration_s));
                return TryPlaySpineAnimation("Close_1", loop: false) || TryPlaySpineAnimation("Idle_1", loop: true);
            }
            if (capabilityId == "lineb_echo_suppressed")
            {
                ResetCheekPose();
                SuppressReactiveTouch(Mathf.Max(0.6f, p.suppression_duration_s));
                return TryPlaySpineAnimation("Idle_1", loop: true);
            }
            if (capabilityId == "lineb_listening")
            {
                return TryPlaySpineAnimation("Think_1", loop: false) || TryPlaySpineAnimation("Idle_1", loop: true);
            }
            if (capabilityId == "lineb_listening_uncertain")
            {
                return TryPlaySpineAnimation("Worry_1", loop: false) || TryPlaySpineAnimation("Idle_1", loop: true);
            }
            if (capabilityId == "lineb_listening_noise")
            {
                return TryPlaySpineAnimation("Idle_1", loop: true);
            }
            return false;
        }

        private VoiceActivityJson ParseVoiceActivity(string parametersJson)
        {
            if (string.IsNullOrEmpty(parametersJson)) return VoiceActivityJson.Default;
            try
            {
                return JsonUtility.FromJson<VoiceActivityJson>(parametersJson);
            }
            catch
            {
                return VoiceActivityJson.Default;
            }
        }

        private void SuppressReactiveTouch(float durationSeconds)
        {
            _reactiveTouchSuppressedUntil = Mathf.Max(
                _reactiveTouchSuppressedUntil,
                Time.time + Mathf.Max(0f, durationSeconds));
        }

        private bool IsReactiveTouchSuppressed(string capabilityId)
        {
            if (Time.time >= _reactiveTouchSuppressedUntil) return false;
            if (capabilityId == "cheek_pinch_release" || capabilityId == "cheek_recover") return false;
            if (capabilityId == "touch_end" || capabilityId == "pat_end" || capabilityId == "tickle_end") return false;
            if (capabilityId == "body_place_release" || capabilityId == "body_place_cancel") return false;
            return capabilityId.StartsWith("cheek_", StringComparison.Ordinal)
                || capabilityId.StartsWith("touch_", StringComparison.Ordinal)
                || capabilityId.StartsWith("pat_", StringComparison.Ordinal)
                || capabilityId.StartsWith("tickle_", StringComparison.Ordinal)
                || capabilityId.StartsWith("body_", StringComparison.Ordinal);
        }

        private CheekPinchJson ParseCheekPinch(string parametersJson)
        {
            if (string.IsNullOrEmpty(parametersJson)) return CheekPinchJson.Default;
            try
            {
                var p = JsonUtility.FromJson<CheekPinchJson>(parametersJson);
                p.side = NormalizeCheekSide(p.side);
                return p;
            }
            catch
            {
                return CheekPinchJson.Default;
            }
        }

        private BodyInteractionJson ParseBodyInteraction(string parametersJson)
        {
            if (string.IsNullOrEmpty(parametersJson)) return BodyInteractionJson.Default;
            try
            {
                return JsonUtility.FromJson<BodyInteractionJson>(parametersJson);
            }
            catch
            {
                return BodyInteractionJson.Default;
            }
        }

        private void ApplyCheekPose(CheekPinchJson p)
        {
            if (_spineSkeleton == null || _findBone == null) CacheSpineHandles();
            if (_spineSkeleton == null || _findBone == null) return;

            float strength = Mathf.Clamp01(p.strength);
            float dragX = Mathf.Clamp(p.drag_x, -1f, 1f);
            float dragY = Mathf.Clamp(p.drag_y, -1f, 1f);
            if (Mathf.Abs(dragX) < 0.001f && Mathf.Abs(dragY) < 0.001f)
            {
                dragX = p.side == "left" ? -1f : p.side == "right" ? 1f : 0f;
            }

            bool left = p.side != "right";
            bool right = p.side != "left";
            if (left) ApplyCheekBone("S1_F_Ball_L_CT", -Mathf.Abs(dragX), dragY, strength);
            if (right) ApplyCheekBone("S1_F_Ball_R_CT", Mathf.Abs(dragX), dragY, strength);
            ApplyCheekBone("Character_Ball_Move", dragX * 0.3f, dragY * 0.2f, strength * 0.35f);
            _updateSkeletonWorldTransform?.Invoke(_spineSkeleton, null);
        }

        private void ApplyCheekBone(string boneName, float xDirection, float yDirection, float strength)
        {
            var pose = GetCheekPose(boneName);
            if (pose.Bone == null) return;

            float pullUnits = 20f * strength;
            SetFloatProperty(pose.Bone, "X", pose.X + xDirection * pullUnits);
            SetFloatProperty(pose.Bone, "Y", pose.Y + yDirection * pullUnits * 0.45f);
            SetFloatProperty(pose.Bone, "ScaleX", pose.ScaleX * (1f + 0.12f * strength));
            SetFloatProperty(pose.Bone, "ScaleY", pose.ScaleY * (1f - 0.06f * strength));
        }

        private void ResetCheekPose()
        {
            if (_spineSkeleton == null || _findBone == null) CacheSpineHandles();
            foreach (var item in _cheekBoneSetup)
            {
                var pose = item.Value;
                if (pose.Bone == null) continue;
                SetFloatProperty(pose.Bone, "X", pose.X);
                SetFloatProperty(pose.Bone, "Y", pose.Y);
                SetFloatProperty(pose.Bone, "ScaleX", pose.ScaleX);
                SetFloatProperty(pose.Bone, "ScaleY", pose.ScaleY);
            }
            _updateSkeletonWorldTransform?.Invoke(_spineSkeleton, null);
        }

        private BonePose GetCheekPose(string boneName)
        {
            if (_cheekBoneSetup.TryGetValue(boneName, out var pose)) return pose;
            return CaptureCheekBone(boneName);
        }

        private BonePose CaptureCheekBone(string boneName)
        {
            if (_spineSkeleton == null || _findBone == null) return BonePose.Empty;
            var bone = _findBone.Invoke(_spineSkeleton, new object[] { boneName });
            if (bone == null) return BonePose.Empty;

            var pose = new BonePose
            {
                Bone = bone,
                X = GetFloatProperty(bone, "X"),
                Y = GetFloatProperty(bone, "Y"),
                ScaleX = GetFloatProperty(bone, "ScaleX"),
                ScaleY = GetFloatProperty(bone, "ScaleY"),
            };
            _cheekBoneSetup[boneName] = pose;
            return pose;
        }

        private static float GetFloatProperty(object target, string propertyName)
        {
            if (target == null) return 0f;
            var property = target.GetType().GetProperty(propertyName);
            if (property == null || !property.CanRead) return 0f;
            var value = property.GetValue(target, null);
            return value is float f ? f : 0f;
        }

        private static void SetFloatProperty(object target, string propertyName, float value)
        {
            if (target == null) return;
            var property = target.GetType().GetProperty(propertyName);
            if (property != null && property.CanWrite)
            {
                property.SetValue(target, value, null);
            }
        }

        private static string NormalizeCheekSide(string side)
        {
            var normalized = (side ?? "").Trim().ToLowerInvariant();
            return normalized == "left" || normalized == "right" || normalized == "both"
                ? normalized
                : "both";
        }

        private static bool ShouldLoop(string capabilityId)
        {
            return capabilityId == "spine_idle"
                || capabilityId == "touch_idle"
                || capabilityId == "cheek_pinch_start"
                || capabilityId == "cheek_pinch_hold"
                || capabilityId == "pat_idle"
                || capabilityId == "tickle_idle"
                || capabilityId == "spine_walk"
                || capabilityId == "lineb_speaking"
                || capabilityId == "body_held_in_air"
                || capabilityId == "body_dragging_in_air"
                || capabilityId == "body_place_preview";
        }

        [Serializable]
        private struct WalkJson
        {
            public float x;
            public float y;
            public float z;
            public float dt;
            public float deltaTime;
        }

        [Serializable]
        private struct AnimationJson
        {
            public string animation;
            public int variant;
        }

        [Serializable]
        private struct CheekPinchJson
        {
            public string side;
            public float strength;
            public float drag_x;
            public float drag_y;

            public static CheekPinchJson Default => new CheekPinchJson
            {
                side = "both",
                strength = 0f,
                drag_x = 0f,
                drag_y = 0f,
            };

            public CheekPinchJson WithDefaultStrength(float fallback)
            {
                if (strength <= 0f) strength = fallback;
                side = NormalizeCheekSide(side);
                return this;
            }
        }

        [Serializable]
        private struct VoiceActivityJson
        {
            public string state;
            public string source;
            public string segment_id;
            public string input_id;
            public string turn_decision;
            public string speaker_role;
            public float echo_score;
            public string model_reaction_policy;
            public string recommended_model_trigger;
            public float suppression_duration_s;

            public static VoiceActivityJson Default => new VoiceActivityJson
            {
                state = "",
                source = "",
                segment_id = "",
                input_id = "",
                turn_decision = "",
                speaker_role = "",
                echo_score = 0f,
                model_reaction_policy = "",
                recommended_model_trigger = "",
                suppression_duration_s = 0f,
            };
        }

        [Serializable]
        private struct BodyInteractionJson
        {
            public string state;
            public float held_seconds;
            public float lift_m;
            public float drag_speed;
            public float ground_x;
            public float ground_y;
            public float ground_z;

            public static BodyInteractionJson Default => new BodyInteractionJson
            {
                state = "",
                held_seconds = 0f,
                lift_m = 0f,
                drag_speed = 0f,
                ground_x = 0f,
                ground_y = 0f,
                ground_z = 0f,
            };
        }

        private struct BonePose
        {
            public object Bone;
            public float X;
            public float Y;
            public float ScaleX;
            public float ScaleY;

            public static BonePose Empty => new BonePose { Bone = null };
        }
    }
}
