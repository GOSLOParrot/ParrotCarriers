using System;
using UnityEngine;

#if UNITY_MEDIAPIPE && UNITY_AR_FOUNDATION
using Mediapipe;
using Mediapipe.Tasks.Core;
using Mediapipe.Tasks.Vision.Core;
using Mediapipe.Tasks.Vision.HandLandmarker;
using Unity.Collections;
using UnityEngine.XR.ARFoundation;
using UnityEngine.XR.ARSubsystems;
using TaskCategory = Mediapipe.Tasks.Components.Containers.Category;
using TaskNormalizedLandmark = Mediapipe.Tasks.Components.Containers.NormalizedLandmark;
#endif

namespace ParrotApp.Hands
{
    [DisallowMultipleComponent]
    public class MediaPipeCameraHandPoseProvider : MonoBehaviour
    {
        public event Action<CameraHandPoseFrame> OnHandPose;

        public string LastStatus { get; private set; } = "not_started";
        public bool IsTracking { get; private set; }
        public static bool RealMediaPipeCompiled
        {
            get
            {
#if UNITY_MEDIAPIPE && UNITY_AR_FOUNDATION
                return true;
#else
                return false;
#endif
            }
        }

        public bool IsRealProviderCompiled => RealMediaPipeCompiled;

#if UNITY_MEDIAPIPE && UNITY_AR_FOUNDATION
        private const int Wrist = 0;
        private const int IndexMcp = 5;
        private const int IndexPip = 6;
        private const int IndexDip = 7;
        private const int IndexTip = 8;
        private const int MiddleMcp = 9;
        private const int MiddlePip = 10;
        private const int MiddleTip = 12;
        private const int RingMcp = 13;
        private const int RingPip = 14;
        private const int RingTip = 16;
        private const int LittleMcp = 17;
        private const int LittlePip = 18;
        private const int LittleTip = 20;
        private const int LandmarkCount = 21;

        [Header("AR Camera")]
        [SerializeField] private ARCameraManager cameraManager;
        [SerializeField] private int maxInputWidth = 320;
        [SerializeField] private float targetFps = 12f;
        [SerializeField] private float bindRetryIntervalSeconds = 0.75f;
        [SerializeField] private XRCpuImage.Transformation cpuImageTransformation = XRCpuImage.Transformation.None;
        [SerializeField] private int imageRotationDegrees = 0;
        [SerializeField] private bool mirrorNormalizedX = false;

        [Header("MediaPipe")]
        [SerializeField] private TextAsset handLandmarkerModel;
        [SerializeField] private string resourcesModelPath = "MediaPipe/hand_landmarker";
        [SerializeField] private bool preferGpuDelegateOnMobile = false;
        [SerializeField] private int numHands = 1;
        [SerializeField] private float minHandDetectionConfidence = 0.55f;
        [SerializeField] private float minHandPresenceConfidence = 0.55f;
        [SerializeField] private float minTrackingConfidence = 0.5f;

        [Header("Depth estimate")]
        [SerializeField] private float assumedIndexFingerLengthMeters = 0.095f;
        [SerializeField] private float fallbackDepthMeters = 0.62f;
        [SerializeField] private float minDepthMeters = 0.25f;
        [SerializeField] private float maxDepthMeters = 1.45f;
        [SerializeField] private float depthSmooth = 0.35f;
        [SerializeField] private float landmarkZScale = 0.08f;
        [SerializeField] private float middleSegmentBlend = 0.5f;
        [SerializeField] private bool faceMainCameraWhenPossible = true;
        [SerializeField] private float handLostAfterSeconds = 0.45f;
        [SerializeField] private bool diagnosticLog = true;

        private HandLandmarker _landmarker;
        private HandLandmarkerResult _result;
        private Texture2D _inputTexture;
        private NativeArray<byte> _pixelBuffer;
        private Vector2Int _inputDimensions;
        private ImageProcessingOptions _imageProcessingOptions;
        private float _nextCaptureAt;
        private float _nextBindRetryAt;
        private float _lastDetectedAt = -1000f;
        private float _smoothedDepth;
        private bool _hasPublishedLost;
        private bool _firstFrameLogged;
        private bool _firstTrackingLogged;
        private bool _gpuInitFallbackTried;
        private bool _landmarkerInitBlocked;
        private bool _nativeUnavailableLogged;
        private string _lastLoggedStatus = "";
#if UNITY_ANDROID && !UNITY_EDITOR
        private static bool _androidNativeLibrariesPreloaded;
#endif

        private void OnEnable()
        {
            BindCamera();
            TryInitializeLandmarker();
        }

        private void OnDisable()
        {
            if (cameraManager != null)
                cameraManager.frameReceived -= HandleCameraFrame;
            ReleaseLandmarker();
            DisposePixelBuffer();
            if (_inputTexture != null)
                Destroy(_inputTexture);
            _inputTexture = null;
            _inputDimensions = default;
            IsTracking = false;
        }

        private void Update()
        {
            bool shouldRetryLandmarker = _landmarker == null && !_landmarkerInitBlocked;
            if ((cameraManager == null || shouldRetryLandmarker) && Time.unscaledTime >= _nextBindRetryAt)
            {
                _nextBindRetryAt = Time.unscaledTime + Mathf.Max(0.1f, bindRetryIntervalSeconds);
                if (cameraManager == null)
                    BindCamera();
                if (shouldRetryLandmarker)
                    TryInitializeLandmarker();
            }
            if (IsTracking && Time.unscaledTime - _lastDetectedAt > Mathf.Max(0.1f, handLostAfterSeconds))
                PublishLost("camera_cv_timeout");
            LogStatusIfChanged();
        }

        private void BindCamera()
        {
            if (cameraManager == null && Camera.main != null)
                cameraManager = Camera.main.GetComponent<ARCameraManager>();
            if (cameraManager == null)
                cameraManager = FindObjectOfType<ARCameraManager>();
            if (cameraManager == null)
            {
                SetStatus("ar_camera_manager_missing");
                return;
            }

            cameraManager.frameReceived -= HandleCameraFrame;
            cameraManager.frameReceived += HandleCameraFrame;
            DebugLog("camera_bound:" + cameraManager.gameObject.name);
        }

        private void TryInitializeLandmarker()
        {
            if (_landmarker != null || _landmarkerInitBlocked)
                return;

            if (handLandmarkerModel == null && !string.IsNullOrWhiteSpace(resourcesModelPath))
                handLandmarkerModel = Resources.Load<TextAsset>(resourcesModelPath);
            if (handLandmarkerModel == null || handLandmarkerModel.bytes == null || handLandmarkerModel.bytes.Length == 0)
            {
                SetStatus("hand_landmarker_model_missing:Resources/" + resourcesModelPath + ".bytes");
                return;
            }

            try
            {
                PreloadAndroidNativeLibraries();
                var delegateCase = preferGpuDelegateOnMobile && Application.isMobilePlatform
                    && !_gpuInitFallbackTried
                    ? BaseOptions.Delegate.GPU
                    : BaseOptions.Delegate.CPU;
                CreateLandmarker(delegateCase, "mediapipe_hand_landmarker_ready");
            }
            catch (Exception ex)
            {
                ReleaseLandmarker();
                if (IsNativeLibraryFailure(ex))
                {
                    MarkNativeUnavailable(ex);
                    return;
                }

                if (preferGpuDelegateOnMobile && Application.isMobilePlatform && !_gpuInitFallbackTried)
                {
                    _gpuInitFallbackTried = true;
                    Debug.LogWarning("[MediaPipeCameraHandPoseProvider] gpu_delegate_failed_fallback_cpu: " + ex.Message);
                    try
                    {
                        CreateLandmarker(BaseOptions.Delegate.CPU, "mediapipe_hand_landmarker_ready_cpu_fallback");
                        return;
                    }
                    catch (Exception cpuEx)
                    {
                        ReleaseLandmarker();
                        if (IsNativeLibraryFailure(cpuEx))
                        {
                            MarkNativeUnavailable(cpuEx);
                            return;
                        }

                        ex = cpuEx;
                    }
                }
                _landmarkerInitBlocked = true;
                SetStatus("mediapipe_init_failed:" + ShortReason(ex.Message));
                Debug.LogError("[MediaPipeCameraHandPoseProvider] " + ex);
            }
        }

        private void CreateLandmarker(BaseOptions.Delegate delegateCase, string readyStatus)
        {
            var baseOptions = new BaseOptions(delegateCase, modelAssetBuffer: handLandmarkerModel.bytes);
            var options = new HandLandmarkerOptions(
                baseOptions,
                runningMode: RunningMode.VIDEO,
                numHands: Mathf.Max(1, numHands),
                minHandDetectionConfidence: Mathf.Clamp01(minHandDetectionConfidence),
                minHandPresenceConfidence: Mathf.Clamp01(minHandPresenceConfidence),
                minTrackingConfidence: Mathf.Clamp01(minTrackingConfidence));
            _landmarker = HandLandmarker.CreateFromOptions(options);
            _result = HandLandmarkerResult.Alloc(options.numHands);
            _imageProcessingOptions = new ImageProcessingOptions(rotationDegrees: imageRotationDegrees);
            _smoothedDepth = Mathf.Clamp(fallbackDepthMeters, minDepthMeters, maxDepthMeters);
            SetStatus(readyStatus);
            DebugLog(
                "hand_landmarker_ready bytes=" + handLandmarkerModel.bytes.Length
                + " delegate=" + delegateCase
                + " maxWidth=" + maxInputWidth
                + " fps=" + targetFps);
        }

        private void ReleaseLandmarker()
        {
            if (_landmarker != null)
                ((IDisposable)_landmarker).Dispose();
            _landmarker = null;
        }

        private void HandleCameraFrame(ARCameraFrameEventArgs _)
        {
            if (_landmarker == null)
                return;
            if (cameraManager == null)
            {
                BindCamera();
                return;
            }
            if (Time.unscaledTime < _nextCaptureAt)
                return;

            _nextCaptureAt = Time.unscaledTime + 1f / Mathf.Max(1f, targetFps);
            if (!cameraManager.TryAcquireLatestCpuImage(out XRCpuImage cpuImage))
            {
                SetStatus("cpu_image_unavailable");
                return;
            }

            using (cpuImage)
            {
                var dimensions = ResolveInputDimensions(cpuImage.width, cpuImage.height);
                EnsureInputTexture(dimensions.x, dimensions.y);

                var conversionParams = new XRCpuImage.ConversionParams
                {
                    inputRect = new RectInt(0, 0, cpuImage.width, cpuImage.height),
                    outputDimensions = dimensions,
                    outputFormat = TextureFormat.RGBA32,
                    transformation = cpuImageTransformation,
                };

                int convertedSize = cpuImage.GetConvertedDataSize(conversionParams);
                EnsurePixelBuffer(convertedSize);
                cpuImage.Convert(conversionParams, _pixelBuffer);
                if (!_firstFrameLogged)
                {
                    _firstFrameLogged = true;
                    DebugLog(
                        "cpu_image_first_frame source=" + cpuImage.width + "x" + cpuImage.height
                        + " input=" + dimensions.x + "x" + dimensions.y
                        + " bytes=" + convertedSize);
                }
            }

            _inputTexture.LoadRawTextureData(_pixelBuffer);
            _inputTexture.Apply(updateMipmaps: false);

            try
            {
                using var image = new Image(_inputTexture);
                long timestamp = Mathf.RoundToInt(Time.realtimeSinceStartup * 1000f);
                if (!_landmarker.TryDetectForVideo(image, timestamp, _imageProcessingOptions, ref _result))
                {
                    PublishLost("mediapipe_no_result");
                    return;
                }
                PublishResult(_result);
            }
            catch (Exception ex)
            {
                PublishLost("mediapipe_detect_failed:" + ShortReason(ex.Message));
                Debug.LogWarning("[MediaPipeCameraHandPoseProvider] " + ex);
            }
        }

        private Vector2Int ResolveInputDimensions(int sourceWidth, int sourceHeight)
        {
            int maxWidth = Mathf.Clamp(maxInputWidth, 160, 640);
            if (sourceWidth <= maxWidth)
                return new Vector2Int(sourceWidth, sourceHeight);

            float scale = maxWidth / (float)Mathf.Max(1, sourceWidth);
            int height = Mathf.Max(1, Mathf.RoundToInt(sourceHeight * scale));
            return new Vector2Int(maxWidth, height);
        }

        private void EnsureInputTexture(int width, int height)
        {
            if (_inputTexture != null && _inputDimensions.x == width && _inputDimensions.y == height)
                return;

            if (_inputTexture != null)
                Destroy(_inputTexture);
            _inputTexture = new Texture2D(width, height, TextureFormat.RGBA32, mipChain: false);
            _inputDimensions = new Vector2Int(width, height);
        }

        private void EnsurePixelBuffer(int length)
        {
            if (_pixelBuffer.IsCreated && _pixelBuffer.Length == length)
                return;
            DisposePixelBuffer();
            _pixelBuffer = new NativeArray<byte>(length, Allocator.Persistent, NativeArrayOptions.UninitializedMemory);
        }

        private void DisposePixelBuffer()
        {
            if (_pixelBuffer.IsCreated)
                _pixelBuffer.Dispose();
        }

        private void PublishResult(HandLandmarkerResult result)
        {
            if (result.handLandmarks == null || result.handLandmarks.Count == 0)
            {
                PublishLost("mediapipe_no_hand");
                return;
            }

            int handIndex = SelectHandIndex(result);
            var normalized = result.handLandmarks[handIndex].landmarks;
            if (normalized == null || normalized.Count < LandmarkCount)
            {
                PublishLost("mediapipe_landmarks_incomplete");
                return;
            }

            Camera cam = Camera.main;
            if (cam == null)
            {
                PublishLost("main_camera_missing");
                return;
            }

            float handednessScore = ResolveHandednessScore(result, handIndex, out bool isRightHand);
            float depth = EstimateDepth(normalized, cam);
            Vector3 wrist = ToWorld(normalized[Wrist], depth, cam);
            Vector3 indexMcp = ToWorld(normalized[IndexMcp], depth, cam);
            Vector3 indexPip = ToWorld(normalized[IndexPip], depth, cam);
            Vector3 indexDip = ToWorld(normalized[IndexDip], depth, cam);
            Vector3 indexTip = ToWorld(normalized[IndexTip], depth, cam);
            Vector3 middleMcp = ToWorld(normalized[MiddleMcp], depth, cam);
            Vector3 middlePip = ToWorld(normalized[MiddlePip], depth, cam);
            Vector3 middleTip = ToWorld(normalized[MiddleTip], depth, cam);
            Vector3 ringMcp = ToWorld(normalized[RingMcp], depth, cam);
            Vector3 ringPip = ToWorld(normalized[RingPip], depth, cam);
            Vector3 ringTip = ToWorld(normalized[RingTip], depth, cam);
            Vector3 littleMcp = ToWorld(normalized[LittleMcp], depth, cam);
            Vector3 littlePip = ToWorld(normalized[LittlePip], depth, cam);
            Vector3 littleTip = ToWorld(normalized[LittleTip], depth, cam);

            Vector3 palm = (wrist + indexMcp + littleMcp) / 3f;
            Vector3 palmNormal = Vector3.Cross(indexMcp - wrist, littleMcp - wrist);
            if (palmNormal.sqrMagnitude < 0.00001f)
                palmNormal = cam.transform.up;
            palmNormal.Normalize();

            if (!TryBuildPerchPose(
                    cam,
                    palm,
                    palmNormal,
                    indexMcp,
                    indexPip,
                    indexDip,
                    indexTip,
                    handednessScore,
                    out HandPerchPose perchPose))
            {
                PublishLost("mediapipe_pose_invalid");
                return;
            }

            IsTracking = true;
            _hasPublishedLost = false;
            _lastDetectedAt = Time.unscaledTime;
            SetStatus("mediapipe_camera_tracking");
            if (!_firstTrackingLogged)
            {
                _firstTrackingLogged = true;
                DebugLog(
                    "first_hand depth=" + depth.ToString("0.00")
                    + " confidence=" + perchPose.Confidence.ToString("0.00")
                    + " right=" + isRightHand);
            }

            OnHandPose?.Invoke(new CameraHandPoseFrame
            {
                HandDetected = true,
                HasFingerJoints = true,
                IsRightHand = isRightHand,
                Source = "mediapipe_camera",
                Status = LastStatus,
                Confidence = perchPose.Confidence,
                EstimatedDepthMeters = depth,
                WristPosition = wrist,
                PalmPosition = palm,
                PalmNormal = palmNormal,
                IndexProximal = indexMcp,
                IndexIntermediate = indexPip,
                IndexDistal = indexDip,
                IndexTip = indexTip,
                MiddleProximal = middleMcp,
                MiddleIntermediate = middlePip,
                MiddleTip = middleTip,
                RingProximal = ringMcp,
                RingIntermediate = ringPip,
                RingTip = ringTip,
                LittleProximal = littleMcp,
                LittleIntermediate = littlePip,
                LittleTip = littleTip,
                PerchPose = perchPose,
            });
        }

        private int SelectHandIndex(HandLandmarkerResult result)
        {
            if (result.handedness == null || result.handedness.Count == 0)
                return 0;

            int bestIndex = 0;
            float bestScore = -1f;
            for (int i = 0; i < result.handedness.Count; i++)
            {
                float score = ResolveHandednessScore(result, i, out _);
                if (score > bestScore)
                {
                    bestIndex = i;
                    bestScore = score;
                }
            }
            return Mathf.Clamp(bestIndex, 0, result.handLandmarks.Count - 1);
        }

        private static float ResolveHandednessScore(HandLandmarkerResult result, int handIndex, out bool isRightHand)
        {
            isRightHand = true;
            if (result.handedness == null
                || handIndex < 0
                || handIndex >= result.handedness.Count
                || result.handedness[handIndex].categories == null
                || result.handedness[handIndex].categories.Count == 0)
            {
                return 0.75f;
            }

            TaskCategory category = result.handedness[handIndex].categories[0];
            string label = category.categoryName ?? category.displayName ?? "";
            isRightHand = !label.Equals("Left", StringComparison.OrdinalIgnoreCase);
            return Mathf.Clamp01(category.score);
        }

        private float EstimateDepth(System.Collections.Generic.List<TaskNormalizedLandmark> landmarks, Camera cam)
        {
            float pixelLength = Vector2.Distance(
                ToPixel(landmarks[IndexMcp]),
                ToPixel(landmarks[IndexTip]));
            if (pixelLength < 1f || cam == null)
                return _smoothedDepth > 0f ? _smoothedDepth : fallbackDepthMeters;

            float focalPixels = 0.5f * Mathf.Max(_inputDimensions.x, _inputDimensions.y)
                                / Mathf.Tan(Mathf.Max(1f, cam.fieldOfView) * 0.5f * Mathf.Deg2Rad);
            float estimated = assumedIndexFingerLengthMeters * focalPixels / pixelLength;
            estimated = Mathf.Clamp(estimated, minDepthMeters, maxDepthMeters);
            _smoothedDepth = Mathf.Lerp(
                _smoothedDepth <= 0f ? estimated : _smoothedDepth,
                estimated,
                Mathf.Clamp01(depthSmooth));
            return _smoothedDepth;
        }

        private Vector2 ToPixel(TaskNormalizedLandmark landmark)
        {
            float x = mirrorNormalizedX ? 1f - landmark.x : landmark.x;
            return new Vector2(
                Mathf.Clamp01(x) * Mathf.Max(1, _inputDimensions.x),
                Mathf.Clamp01(landmark.y) * Mathf.Max(1, _inputDimensions.y));
        }

        private Vector3 ToWorld(TaskNormalizedLandmark landmark, float depth, Camera cam)
        {
            float x = mirrorNormalizedX ? 1f - landmark.x : landmark.x;
            float viewportY = 1f - landmark.y;
            Ray ray = cam.ViewportPointToRay(new Vector3(Mathf.Clamp01(x), Mathf.Clamp01(viewportY), 0f));
            float localDepth = Mathf.Clamp(-landmark.z * landmarkZScale, -0.08f, 0.08f);
            return ray.GetPoint(Mathf.Clamp(depth + localDepth, minDepthMeters, maxDepthMeters));
        }

        private bool TryBuildPerchPose(
            Camera cam,
            Vector3 palm,
            Vector3 palmNormal,
            Vector3 indexMcp,
            Vector3 indexPip,
            Vector3 indexDip,
            Vector3 indexTip,
            float score,
            out HandPerchPose pose)
        {
            pose = default;
            Vector3 fingerDir = indexTip - indexMcp;
            if (fingerDir.sqrMagnitude < 0.00001f)
                return false;
            fingerDir.Normalize();

            Vector3 perch = Vector3.Lerp(indexPip, indexDip, Mathf.Clamp01(middleSegmentBlend));
            Vector3 facing = ResolveFacingDirection(cam, perch, fingerDir);
            Vector3 up = Vector3.Cross(facing, fingerDir);
            if (up.sqrMagnitude < 0.00001f)
                up = palmNormal.sqrMagnitude > 0.00001f ? palmNormal : Vector3.up;
            up.Normalize();
            facing = Vector3.Cross(fingerDir, up).normalized;

            float horizontalScore = 1f - Mathf.Clamp01(Mathf.Abs(Vector3.Dot(fingerDir, Vector3.up)) / 0.65f);
            float confidence = Mathf.Clamp01(score * 0.65f + horizontalScore * 0.35f);
            pose = new HandPerchPose
            {
                IsValid = true,
                Position = perch,
                Rotation = Quaternion.LookRotation(facing, up),
                FingerDirection = fingerDir,
                PalmPosition = palm,
                PalmNormal = palmNormal,
                FacingDirection = facing,
                Confidence = confidence,
                Source = "mediapipe_camera",
            };
            return true;
        }

        private Vector3 ResolveFacingDirection(Camera cam, Vector3 perchPosition, Vector3 fingerDir)
        {
            Vector3 desired = Vector3.zero;
            if (faceMainCameraWhenPossible && cam != null)
                desired = cam.transform.position - perchPosition;
            if (desired.sqrMagnitude < 0.0001f)
                desired = Vector3.Cross(Vector3.up, fingerDir);
            desired = Vector3.ProjectOnPlane(desired, fingerDir);
            if (desired.sqrMagnitude < 0.0001f)
                desired = Vector3.Cross(Vector3.forward, fingerDir);
            if (desired.sqrMagnitude < 0.0001f)
                desired = Vector3.forward;
            return desired.normalized;
        }

        private void PublishLost(string status)
        {
            if (_hasPublishedLost && !IsTracking)
                return;
            IsTracking = false;
            _hasPublishedLost = true;
            SetStatus(status);
            DebugLog("hand_lost:" + status);
            OnHandPose?.Invoke(CameraHandPoseFrame.Lost("mediapipe_camera", status));
        }

        private void MarkNativeUnavailable(Exception ex)
        {
            _landmarkerInitBlocked = true;
            string status = "mediapipe_native_unavailable:" + DeepReason(ex);
            SetStatus(status);
            PublishLost(status);
            if (_nativeUnavailableLogged)
                return;

            _nativeUnavailableLogged = true;
            Debug.LogError("[MediaPipeCameraHandPoseProvider] " + status + "\n" + ex);
        }

        private static bool IsNativeLibraryFailure(Exception ex)
        {
            for (Exception current = ex; current != null; current = current.InnerException)
            {
                string text = current.ToString();
                if (text.IndexOf("mediapipe_jni", StringComparison.OrdinalIgnoreCase) >= 0
                    || text.IndexOf("opencv_java4", StringComparison.OrdinalIgnoreCase) >= 0
                    || text.IndexOf("Unable to load DLL", StringComparison.OrdinalIgnoreCase) >= 0
                    || text.IndexOf("UnsatisfiedLinkError", StringComparison.OrdinalIgnoreCase) >= 0
                    || text.IndexOf("dlopen", StringComparison.OrdinalIgnoreCase) >= 0)
                {
                    return true;
                }
            }

            return false;
        }

        private static string DeepReason(Exception ex)
        {
            Exception current = ex;
            while (current != null && current.InnerException != null)
                current = current.InnerException;
            return ShortReason(current == null ? "" : current.Message);
        }

        private static void PreloadAndroidNativeLibraries()
        {
#if UNITY_ANDROID && !UNITY_EDITOR
            if (_androidNativeLibrariesPreloaded)
                return;

            using (var systemClass = new AndroidJavaClass("java.lang.System"))
            {
                systemClass.CallStatic("loadLibrary", "opencv_java4");
                systemClass.CallStatic("loadLibrary", "mediapipe_jni");
            }
            _androidNativeLibrariesPreloaded = true;
#endif
        }
#else
        [SerializeField] private string disabledReason = "UNITY_MEDIAPIPE and UNITY_AR_FOUNDATION are required";

        private void OnEnable()
        {
            LastStatus = "mediapipe_camera_provider_not_compiled";
        }
#endif

        private static string ShortReason(string raw)
        {
            if (string.IsNullOrWhiteSpace(raw))
                return "";
            raw = raw.Trim().Replace("\r", " ").Replace("\n", " ");
            return raw.Length <= 80 ? raw : raw.Substring(0, 80);
        }

#if UNITY_MEDIAPIPE && UNITY_AR_FOUNDATION
        private void SetStatus(string status)
        {
            LastStatus = string.IsNullOrWhiteSpace(status) ? "unknown" : status;
        }

        private void LogStatusIfChanged()
        {
            if (!diagnosticLog || string.Equals(_lastLoggedStatus, LastStatus, StringComparison.Ordinal))
                return;
            _lastLoggedStatus = LastStatus;
            DebugLog("status=" + LastStatus);
        }

        private void DebugLog(string message)
        {
            if (!diagnosticLog)
                return;
            Debug.Log("[MediaPipeCameraHandPoseProvider] " + message);
        }
#endif
    }
}
