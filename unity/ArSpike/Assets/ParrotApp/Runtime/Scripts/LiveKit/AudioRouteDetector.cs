using System;
using System.Collections;
using UnityEngine;

namespace ParrotApp.LiveKit
{
    /// <summary>
    /// 跨平台音频路由探测器。
    ///
    /// <b>用途</b>：让 <see cref="MicrophonePublisher"/> 知道当前是 speaker / wired /
    /// bluetooth，并在路由切换时触发 unpublish-republish 与采样率重协商。
    ///
    /// <b>Sprint4 范围</b>：能跑、能区分蓝牙、能告诉 publisher "需要换采样率"。
    /// <b>不做</b>：UI 设备选择器、原生全平台 portType enum、AudioRoutePolicy 进 ECP /
    /// Blackboard（候选 BB 键 <c>session/audio_route_policy</c> 留 # CANDIDATE，归 Phase 4）。
    ///
    /// <b>平台实现</b>：
    /// <list type="bullet">
    /// <item><b>Android</b>：通过 <c>AudioManager.isBluetoothScoOn</c> /
    ///   <c>isBluetoothA2dpOn</c> / <c>isWiredHeadsetOn</c> / <c>isSpeakerphoneOn</c>
    ///   读 flag。这些 API 在 API 31+ 已 deprecated，但 spike 阶段仍可用；
    ///   long-term 应迁到 <c>AudioManager.getDevices(GET_DEVICES_INPUTS)</c>
    ///   + <c>AudioDeviceInfo.getType()</c>。</item>
    /// <item><b>iOS</b>：Sprint4 暂用 <c>Microphone.devices</c> 名字模糊匹配
    ///   （Airpods / Bluetooth / Headset / Headphone 关键词）。原生
    ///   <c>AVAudioSession.currentRoute.outputs[0].portType</c> bridge 归 Phase 4。</item>
    /// <item><b>Editor / 其他</b>：总是 <see cref="AudioRouteKind.Speaker"/>。</item>
    /// </list>
    ///
    /// <b>触发源</b>：
    /// <list type="bullet">
    /// <item><see cref="AudioSettings.OnAudioConfigurationChanged"/>（设备热切立即触发）。</item>
    /// <item>周期 polling（默认 2 s）兜底，覆盖 AudioSettings 不触发的场景
    ///   （蓝牙 A2DP→SCO mode switch 在部分 ARM Android 上有时静默）。</item>
    /// </list>
    ///
    /// <b>非 producer 单写约束的对象</b>：本类只产生事件，不直接写
    /// <c>ConnectionHealthAggregator</c> 任何字段（避免抢 <see cref="MicrophonePublisher"/>
    /// 在 IMPL_REF.md §4.2 表中的 producer 角色）。
    /// </summary>
    public class AudioRouteDetector : MonoBehaviour
    {
        [Tooltip("路由 polling 间隔（秒）；设 0 关闭兜底轮询，仅用 AudioSettings 事件。")]
        [SerializeField] private float pollIntervalSeconds = 2.0f;

        [Tooltip("Editor 下也启用 polling（默认仅响应 AudioSettings 事件，省 Console 噪音）。")]
        [SerializeField] private bool pollInEditor = false;

        public AudioRoutePolicy CurrentPolicy { get; private set; } = AudioRoutePolicy.Default();
        public string LastDetectionSource { get; private set; } = "unknown";
        public string LastDeviceSummary { get; private set; } = "";

        /// <summary>(oldPolicy, newPolicy)；只在 <see cref="AudioRoutePolicy.Equals"/>
        /// 判定有变化时触发，避免 polling 抖动产生空事件。</summary>
        public event Action<AudioRoutePolicy, AudioRoutePolicy> OnRouteChanged;

        private bool _hookedAudioSettings;
        private Coroutine _pollCoroutine;

        void OnEnable()
        {
            CurrentPolicy = DetectNow();

            if (!_hookedAudioSettings)
            {
                AudioSettings.OnAudioConfigurationChanged += OnAudioConfigChanged;
                _hookedAudioSettings = true;
            }

            bool shouldPoll = pollIntervalSeconds > 0f && (!Application.isEditor || pollInEditor);
            if (shouldPoll)
                _pollCoroutine = StartCoroutine(PollLoop());

            Debug.Log($"[AudioRouteDetector] enabled; initialPolicy={CurrentPolicy}, polling={shouldPoll}");
        }

        void OnDisable()
        {
            if (_hookedAudioSettings)
            {
                AudioSettings.OnAudioConfigurationChanged -= OnAudioConfigChanged;
                _hookedAudioSettings = false;
            }
            if (_pollCoroutine != null)
            {
                StopCoroutine(_pollCoroutine);
                _pollCoroutine = null;
            }
        }

        private void OnAudioConfigChanged(bool deviceWasChanged)
        {
            // deviceWasChanged=false 也 re-detect（仅采样率 / buffer 变化时也可能影响 SCO 判定）
            ReevaluateAndFire(deviceWasChanged ? "audio_device_changed" : "audio_config_changed");
        }

        private IEnumerator PollLoop()
        {
            var wait = new WaitForSeconds(pollIntervalSeconds);
            while (true)
            {
                yield return wait;
                ReevaluateAndFire("poll");
            }
        }

        private void ReevaluateAndFire(string trigger)
        {
            var newPolicy = DetectNow();
            if (newPolicy.Equals(CurrentPolicy)) return;

            var old = CurrentPolicy;
            CurrentPolicy = newPolicy;
            Debug.Log($"[AudioRouteDetector] route changed via {trigger}: {old} → {newPolicy}");

            // 防 listener 抛异常炸掉自己的 polling
            try { OnRouteChanged?.Invoke(old, newPolicy); }
            catch (Exception e)
            {
                Debug.LogError($"[AudioRouteDetector] OnRouteChanged listener threw: {e.Message}");
            }
        }

        /// <summary>立即 detect 当前路由（不触发 OnRouteChanged）；外部组件可在
        /// publish 之前主动拉一次拿到最新 policy。</summary>
        public AudioRoutePolicy DetectNow()
        {
#if UNITY_ANDROID && !UNITY_EDITOR
            return DetectAndroid();
#elif UNITY_IOS && !UNITY_EDITOR
            return DetectIOSFallback();
#else
            return AudioRoutePolicy.ForKind(AudioRouteKind.Speaker);
#endif
        }

        public AudioRoutePolicy RefreshCurrentPolicy(string trigger = "manual_rescan")
        {
            ReevaluateAndFire(string.IsNullOrWhiteSpace(trigger) ? "manual_rescan" : trigger);
            return CurrentPolicy;
        }

#if UNITY_ANDROID && !UNITY_EDITOR
        private AudioRoutePolicy DetectAndroid()
        {
            try
            {
                using (var unityPlayer = new AndroidJavaClass("com.unity3d.player.UnityPlayer"))
                using (var activity = unityPlayer.GetStatic<AndroidJavaObject>("currentActivity"))
                using (var audioManager = activity.Call<AndroidJavaObject>("getSystemService", "audio"))
                {
                    AudioRoutePolicy policy;
                    string summary;
                    if (TryDetectAndroidDevices(audioManager, out policy, out summary))
                    {
                        LastDetectionSource = "get_devices";
                        LastDeviceSummary = summary;
                        return policy;
                    }

                    LastDetectionSource = "legacy_flags";
                    policy = DetectAndroidLegacyFlags(audioManager, out summary);
                    LastDeviceSummary = summary;
                    return policy;
                }
            }
            catch (Exception e)
            {
                Debug.LogWarning($"[AudioRouteDetector] Android detect failed: {e.Message}");
                LastDetectionSource = "android_error";
                LastDeviceSummary = e.Message;
                return AudioRoutePolicy.Default();
            }
        }

        private static AudioRoutePolicy DetectAndroidLegacyFlags(AndroidJavaObject audioManager, out string summary)
        {
            bool sco = SafeBool(audioManager, "isBluetoothScoOn");
            bool a2dp = SafeBool(audioManager, "isBluetoothA2dpOn");
            bool wired = SafeBool(audioManager, "isWiredHeadsetOn");
            bool speakerOn = SafeBool(audioManager, "isSpeakerphoneOn");
            summary = $"legacy:sco={sco},a2dp={a2dp},wired={wired},speaker={speakerOn}";

            // Input direction first: SCO is the real Bluetooth mic path. A2DP
            // is output-only, so Brain should keep input as system default.
            if (sco) return AudioRoutePolicy.ForKind(AudioRouteKind.BluetoothSco);
            if (a2dp) return AudioRoutePolicy.ForKind(AudioRouteKind.BluetoothA2dp);
            if (wired) return AudioRoutePolicy.ForKind(AudioRouteKind.WiredHeadset);
            if (speakerOn) return AudioRoutePolicy.ForKind(AudioRouteKind.Speaker);
            return AudioRoutePolicy.ForKind(AudioRouteKind.Earpiece);
        }

        private static bool TryDetectAndroidDevices(
            AndroidJavaObject audioManager,
            out AudioRoutePolicy policy,
            out string summary)
        {
            policy = AudioRoutePolicy.Default();
            summary = "";
            try
            {
                using (var audioManagerClass = new AndroidJavaClass("android.media.AudioManager"))
                using (var deviceInfoClass = new AndroidJavaClass("android.media.AudioDeviceInfo"))
                {
                    int getInputs = SafeStaticInt(audioManagerClass, "GET_DEVICES_INPUTS", 1);
                    int getOutputs = SafeStaticInt(audioManagerClass, "GET_DEVICES_OUTPUTS", 2);
                    var inputs = SafeGetDevices(audioManager, getInputs);
                    var outputs = SafeGetDevices(audioManager, getOutputs);

                    int typeBluetoothSco = SafeStaticInt(deviceInfoClass, "TYPE_BLUETOOTH_SCO", 7);
                    int typeBluetoothA2dp = SafeStaticInt(deviceInfoClass, "TYPE_BLUETOOTH_A2DP", 8);
                    int typeWiredHeadset = SafeStaticInt(deviceInfoClass, "TYPE_WIRED_HEADSET", 3);
                    int typeWiredHeadphones = SafeStaticInt(deviceInfoClass, "TYPE_WIRED_HEADPHONES", 4);
                    int typeUsbHeadset = SafeStaticInt(deviceInfoClass, "TYPE_USB_HEADSET", 22);
                    int typeSpeaker = SafeStaticInt(deviceInfoClass, "TYPE_BUILTIN_SPEAKER", 2);
                    int typeEarpiece = SafeStaticInt(deviceInfoClass, "TYPE_BUILTIN_EARPIECE", 1);

                    summary = "inputs=[" + DeviceTypesSummary(inputs) + "],outputs=[" + DeviceTypesSummary(outputs) + "]";

                    if (HasDeviceType(inputs, typeBluetoothSco))
                    {
                        policy = AudioRoutePolicy.ForKind(AudioRouteKind.BluetoothSco);
                        return true;
                    }
                    if (HasAnyDeviceType(inputs, typeWiredHeadset, typeUsbHeadset))
                    {
                        policy = AudioRoutePolicy.ForKind(AudioRouteKind.WiredHeadset);
                        return true;
                    }
                    if (HasDeviceType(outputs, typeBluetoothA2dp))
                    {
                        policy = AudioRoutePolicy.ForKind(AudioRouteKind.BluetoothA2dp);
                        return true;
                    }
                    if (HasAnyDeviceType(outputs, typeWiredHeadset, typeWiredHeadphones, typeUsbHeadset))
                    {
                        policy = AudioRoutePolicy.ForKind(AudioRouteKind.WiredHeadset);
                        return true;
                    }
                    if (HasDeviceType(outputs, typeSpeaker))
                    {
                        policy = AudioRoutePolicy.ForKind(AudioRouteKind.Speaker);
                        return true;
                    }
                    if (HasDeviceType(outputs, typeEarpiece))
                    {
                        policy = AudioRoutePolicy.ForKind(AudioRouteKind.Earpiece);
                        return true;
                    }
                    return false;
                }
            }
            catch (Exception e)
            {
                summary = "getDevices_error:" + e.Message;
                return false;
            }
        }

        private static AndroidJavaObject[] SafeGetDevices(AndroidJavaObject audioManager, int flags)
        {
            try { return audioManager.Call<AndroidJavaObject[]>("getDevices", flags) ?? new AndroidJavaObject[0]; }
            catch (Exception) { return new AndroidJavaObject[0]; }
        }

        private static bool HasAnyDeviceType(AndroidJavaObject[] devices, params int[] types)
        {
            for (int i = 0; i < types.Length; i++)
                if (HasDeviceType(devices, types[i]))
                    return true;
            return false;
        }

        private static bool HasDeviceType(AndroidJavaObject[] devices, int type)
        {
            if (devices == null) return false;
            for (int i = 0; i < devices.Length; i++)
            {
                var device = devices[i];
                if (device == null) continue;
                try
                {
                    if (device.Call<int>("getType") == type)
                        return true;
                }
                catch (Exception) { }
            }
            return false;
        }

        private static string DeviceTypesSummary(AndroidJavaObject[] devices)
        {
            if (devices == null || devices.Length == 0) return "none";
            var parts = new string[devices.Length];
            for (int i = 0; i < devices.Length; i++)
            {
                try { parts[i] = devices[i] != null ? devices[i].Call<int>("getType").ToString() : "null"; }
                catch (Exception) { parts[i] = "error"; }
            }
            return string.Join(",", parts);
        }

        private static int SafeStaticInt(AndroidJavaClass klass, string field, int fallback)
        {
            try { return klass.GetStatic<int>(field); }
            catch (Exception) { return fallback; }
        }

        private static bool SafeBool(AndroidJavaObject obj, string method)
        {
            try { return obj.Call<bool>(method); }
            catch (Exception) { return false; }
        }
#endif

#if UNITY_IOS && !UNITY_EDITOR
        private AudioRoutePolicy DetectIOSFallback()
        {
            // Sprint4 Phase 3 简化：用 Microphone.devices 名字模糊匹配。
            // 原生 AVAudioSession bridge（currentRoute.outputs[].portType）归 Phase 4。
            foreach (var device in Microphone.devices)
            {
                var name = device?.ToLowerInvariant() ?? "";
                if (name.Contains("airpods") || name.Contains("bluetooth"))
                    return AudioRoutePolicy.ForKind(AudioRouteKind.BluetoothSco);
                if (name.Contains("headset") || name.Contains("headphone"))
                    return AudioRoutePolicy.ForKind(AudioRouteKind.WiredHeadset);
            }
            return AudioRoutePolicy.ForKind(AudioRouteKind.Speaker);
        }
#endif
    }
}
