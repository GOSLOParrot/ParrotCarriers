using System;
using LiveKit;
using ParrotApp.Core;
using UnityEngine;

namespace ParrotApp.LiveKit
{
    /// <summary>
    /// Android-only LiveKit audio source backed by AudioRecord.
    ///
    /// Formal Android builds may prefer this source before Unity's
    /// <see cref="MicrophoneSource"/> because some devices expose a Unity mic
    /// path that appears locally alive but does not produce usable remote
    /// uplink. Manual named mic selection still opts into Unity's device path.
    /// This class does not reconnect the LiveKit room or dispatch a new Brain
    /// job; it only supplies PCM frames to the existing local audio track.
    /// </summary>
    public sealed class AndroidPcmMicrophoneSource : RtcAudioSource
    {
        public override event Action<float[], int, int> AudioRead;

        private readonly int _sampleRate;
        private readonly int _channels;
        private readonly string _routeHint;
        private AndroidJavaObject _native;
        private AndroidPcmAudioCallbackProxy _callback;
        private bool _started;
        private bool _disposed;

        public bool IsNativeRecording { get; private set; }
        public string LastNativeState { get; private set; } = "not_started";
        public string LastNativeError { get; private set; } = "";
        public string LastNativeSourceName { get; private set; } = "";

        public AndroidPcmMicrophoneSource(int sampleRate, int channels, string routeHint)
            : base(Mathf.Clamp(channels, 1, 2), RtcAudioSourceType.AudioSourceCustom)
        {
            _sampleRate = sampleRate > 0 ? sampleRate : 48000;
            _channels = Mathf.Clamp(channels, 1, 2);
            _routeHint = string.IsNullOrWhiteSpace(routeHint) ? "android_audio_record" : routeHint;
        }

        public override void Start()
        {
            if (_started) return;
            base.Start();

#if UNITY_ANDROID && !UNITY_EDITOR
            if (!AndroidRuntimePermissions.HasMicrophonePermission())
            {
                base.Stop();
                throw new InvalidOperationException("Microphone access not authorized");
            }

            try
            {
                using (var unityPlayer = new AndroidJavaClass("com.unity3d.player.UnityPlayer"))
                using (var activity = unityPlayer.GetStatic<AndroidJavaObject>("currentActivity"))
                {
                    _native = new AndroidJavaObject("com.parrotcarriers.audio.AndroidPcmMicCapture");
                    _callback = new AndroidPcmAudioCallbackProxy(this);
                    // Java starts its capture thread immediately after
                    // AudioRecord.startRecording(). Mark the source as started
                    // before crossing the bridge so the first PCM frames are not
                    // discarded by OnNativePcmFrame on fast devices.
                    _started = true;
                    bool ok = _native.Call<bool>(
                        "start",
                        activity,
                        _sampleRate,
                        _channels,
                        _routeHint,
                        _callback);
                    if (!ok)
                    {
                        RefreshNativeError("start_returned_false");
                        throw new InvalidOperationException("Android AudioRecord start failed: " + LastNativeError);
                    }
                }
            }
            catch (Exception e)
            {
                LastNativeError = BuildNativeStartError(e, LastNativeError);
                LastNativeState = string.IsNullOrWhiteSpace(LastNativeState)
                    ? "start_exception:" + LastNativeError
                    : LastNativeState;
                _started = false;
                CleanupNative();
                base.Stop();
                throw;
            }
#else
            base.Stop();
            throw new PlatformNotSupportedException("AndroidPcmMicrophoneSource is Android-only");
#endif
        }

        public override void Stop()
        {
            base.Stop();
            if (!_started && _native == null) return;
            _started = false;
            CleanupNative();
        }

        protected override void Dispose(bool disposing)
        {
            if (_disposed) return;
            if (disposing) Stop();
            _disposed = true;
            base.Dispose(disposing);
        }

        private void CleanupNative()
        {
#if UNITY_ANDROID && !UNITY_EDITOR
            if (_native != null)
            {
                try { _native.Call("dispose"); }
                catch (Exception e) { Debug.LogWarning("[AndroidPcmMicrophoneSource] dispose failed: " + e.Message); }
                _native.Dispose();
                _native = null;
            }
#endif
            IsNativeRecording = false;
            _callback = null;
        }

        private void OnNativePcmFrame(float[] samples, int length, int sampleRate, int channels)
        {
            if (!_started || _disposed || samples == null || length <= 0)
                return;

            IsNativeRecording = true;
            int safeLength = Math.Min(length, samples.Length);
            if (safeLength <= 0)
                return;

            float[] frame = samples;
            if (safeLength != samples.Length)
            {
                frame = new float[safeLength];
                Array.Copy(samples, frame, safeLength);
            }
            int safeChannels = channels <= 1 ? 1 : 2;
            AudioRead?.Invoke(frame, safeChannels, sampleRate > 0 ? sampleRate : _sampleRate);
        }

        private void RefreshNativeError(string state)
        {
#if UNITY_ANDROID && !UNITY_EDITOR
            if (_native == null)
                return;
            try
            {
                string error = _native.Call<string>("lastError");
                if (!string.IsNullOrWhiteSpace(error))
                    LastNativeError = error;
                LastNativeState = string.IsNullOrWhiteSpace(error)
                    ? state
                    : state + ":" + error;
            }
            catch (Exception e)
            {
                LastNativeError = string.IsNullOrWhiteSpace(LastNativeError)
                    ? "last_error_failed:" + e.GetType().Name
                    : LastNativeError;
            }
#endif
        }

        private static string BuildNativeStartError(Exception exception, string existingError)
        {
            if (!string.IsNullOrWhiteSpace(existingError))
                return existingError;
            if (exception == null)
                return "android_pcm_start_exception";

            string message = exception.Message ?? "";
            string marker = message.IndexOf("com.parrotcarriers.audio.AndroidPcmMicCapture", StringComparison.Ordinal) >= 0
                ? "android_pcm_bridge_unavailable"
                : "android_pcm_start_exception";
            return marker + ":" + exception.GetType().Name + ":" + ShortMessage(message);
        }

        private static string ShortMessage(string message)
        {
            if (string.IsNullOrWhiteSpace(message))
                return "no_message";
            message = message.Replace('\r', ' ').Replace('\n', ' ').Trim();
            const int max = 160;
            return message.Length <= max ? message : message.Substring(0, max);
        }

        private void OnNativeState(string json)
        {
            LastNativeState = string.IsNullOrWhiteSpace(json) ? "native_state_empty" : json;
            IsNativeRecording = LastNativeState.Contains("\"recording\":true");
            LastNativeError = ExtractJsonString(LastNativeState, "error");
            LastNativeSourceName = ExtractJsonString(LastNativeState, "source_name");
        }

        private static string ExtractJsonString(string json, string field)
        {
            if (string.IsNullOrWhiteSpace(json) || string.IsNullOrWhiteSpace(field))
                return "";
            string marker = "\"" + field + "\":\"";
            int start = json.IndexOf(marker, StringComparison.Ordinal);
            if (start < 0)
                return "";
            start += marker.Length;
            int end = json.IndexOf('"', start);
            return end > start ? json.Substring(start, end - start) : "";
        }

        private sealed class AndroidPcmAudioCallbackProxy : AndroidJavaProxy
        {
            private readonly AndroidPcmMicrophoneSource _owner;

            public AndroidPcmAudioCallbackProxy(AndroidPcmMicrophoneSource owner)
                : base("com.parrotcarriers.audio.AndroidPcmAudioCallback")
            {
                _owner = owner;
            }

            public void onPcmFrame(float[] samples, int length, int sampleRate, int channels)
                => _owner?.OnNativePcmFrame(samples, length, sampleRate, channels);

            public void onPcmState(string json)
                => _owner?.OnNativeState(json);
        }
    }
}
