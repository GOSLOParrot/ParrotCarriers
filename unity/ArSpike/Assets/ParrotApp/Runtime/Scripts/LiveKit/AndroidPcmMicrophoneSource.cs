using System;
using LiveKit;
using UnityEngine;

namespace ParrotApp.LiveKit
{
    /// <summary>
    /// Android-only LiveKit audio source backed by AudioRecord.
    ///
    /// Unity's <see cref="MicrophoneSource"/> is still the primary path when
    /// <see cref="Microphone.devices"/> returns a usable device. This source is
    /// a formal App fallback for Android phones where Unity reports zero devices
    /// or never advances <c>Microphone.GetPosition(null)</c> even after the app
    /// has microphone permission. It does not reconnect the LiveKit room or
    /// dispatch a new Brain job; it only supplies PCM frames to the existing
    /// local audio track.
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

        public AndroidPcmMicrophoneSource(int sampleRate, int channels, string routeHint)
            : base(Mathf.Clamp(channels, 1, 2), RtcAudioSourceType.AudioSourceMicrophone)
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
            if (!Application.HasUserAuthorization(UserAuthorization.Microphone))
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
                LastNativeError = string.IsNullOrWhiteSpace(LastNativeError)
                    ? e.GetType().Name
                    : LastNativeError;
                LastNativeState = string.IsNullOrWhiteSpace(LastNativeState)
                    ? "start_exception:" + e.GetType().Name
                    : LastNativeState;
                CleanupNative();
                base.Stop();
                throw;
            }

            _started = true;
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
            int safeLength = Mathf.Min(length, samples.Length);
            if (safeLength <= 0)
                return;

            float[] frame = samples;
            if (safeLength != samples.Length)
            {
                frame = new float[safeLength];
                Array.Copy(samples, frame, safeLength);
            }
            AudioRead?.Invoke(frame, Mathf.Clamp(channels, 1, 2), sampleRate > 0 ? sampleRate : _sampleRate);
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

        private void OnNativeState(string json)
        {
            LastNativeState = string.IsNullOrWhiteSpace(json) ? "native_state_empty" : json;
            IsNativeRecording = LastNativeState.Contains("\"recording\":true");
            int errorStart = LastNativeState.IndexOf("\"error\":\"", StringComparison.Ordinal);
            if (errorStart >= 0)
            {
                errorStart += "\"error\":\"".Length;
                int errorEnd = LastNativeState.IndexOf('"', errorStart);
                LastNativeError = errorEnd > errorStart
                    ? LastNativeState.Substring(errorStart, errorEnd - errorStart)
                    : "";
            }
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
