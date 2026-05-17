using System;
using ParrotApp.Core;
using UnityEngine;

namespace ParrotApp.LiveKit
{
    /// <summary>
    /// Thin Unity wrapper around the formal Android audio-route bridge.
    /// Non-Android builds use no-op methods and let <see cref="AudioRouteDetector"/>
    /// remain the fallback diagnostic provider.
    /// </summary>
    public sealed class AndroidAudioRouteManager : IDisposable
    {
#if UNITY_ANDROID && !UNITY_EDITOR
        private AndroidJavaObject _native;
        private AudioRouteSnapshotCallbackProxy _callbackProxy;
#endif
        public bool IsAvailable { get; private set; }

        public AndroidAudioRouteManager(Action<string> snapshotCallback)
        {
#if UNITY_ANDROID && !UNITY_EDITOR
            try
            {
                using (var unityPlayer = new AndroidJavaClass("com.unity3d.player.UnityPlayer"))
                using (var activity = unityPlayer.GetStatic<AndroidJavaObject>("currentActivity"))
                using (var klass = new AndroidJavaClass("com.parrotcarriers.audio.AndroidAudioRouteManager"))
                {
                    _native = klass.CallStatic<AndroidJavaObject>("getInstance");
                    if (_native != null)
                    {
                        _callbackProxy = new AudioRouteSnapshotCallbackProxy(snapshotCallback);
                        _native.Call("initialize", activity, _callbackProxy);
                        IsAvailable = true;
                    }
                }
            }
            catch (Exception e)
            {
                Debug.LogWarning("[AndroidAudioRouteManager] native bridge unavailable: " + e.Message);
                IsAvailable = false;
            }
#else
            IsAvailable = false;
#endif
        }

        public void Refresh()
        {
#if UNITY_ANDROID && !UNITY_EDITOR
            SafeCall("refresh");
#endif
        }

        public void SetRoutePreference(string preference)
        {
#if UNITY_ANDROID && !UNITY_EDITOR
            SafeCall("setRoutePreference", preference ?? "auto");
#endif
        }

        public void RequestCommunicationMode(bool enabled)
        {
#if UNITY_ANDROID && !UNITY_EDITOR
            SafeCall("requestCommunicationMode", enabled);
#endif
        }

        public void ApplyPreferredCommunicationDevice()
        {
#if UNITY_ANDROID && !UNITY_EDITOR
            SafeCall("applyPreferredCommunicationDevice");
#endif
        }

        public void ClearCommunicationDevice()
        {
#if UNITY_ANDROID && !UNITY_EDITOR
            SafeCall("clearCommunicationDevice");
#endif
        }

        public void StartMicrophoneForegroundService()
        {
#if UNITY_ANDROID && !UNITY_EDITOR
            SafeCall("startMicrophoneForegroundService");
#endif
        }

        public void StopMicrophoneForegroundService()
        {
#if UNITY_ANDROID && !UNITY_EDITOR
            SafeCall("stopMicrophoneForegroundService");
#endif
        }

        public void Dispose()
        {
#if UNITY_ANDROID && !UNITY_EDITOR
            StopMicrophoneForegroundService();
            SafeCall("dispose");
            _callbackProxy = null;
            _native?.Dispose();
            _native = null;
#endif
            IsAvailable = false;
        }

#if UNITY_ANDROID && !UNITY_EDITOR
        private void SafeCall(string method)
        {
            try { _native?.Call(method); }
            catch (Exception e) { Debug.LogWarning("[AndroidAudioRouteManager] " + method + " failed: " + e.Message); }
        }

        private void SafeCall<T>(string method, T value)
        {
            try { _native?.Call(method, value); }
            catch (Exception e) { Debug.LogWarning("[AndroidAudioRouteManager] " + method + " failed: " + e.Message); }
        }

        private sealed class AudioRouteSnapshotCallbackProxy : AndroidJavaProxy
        {
            private readonly Action<string> _snapshotCallback;

            public AudioRouteSnapshotCallbackProxy(Action<string> snapshotCallback)
                : base("com.parrotcarriers.audio.AudioRouteSnapshotCallback")
            {
                _snapshotCallback = snapshotCallback;
            }

            // Called from Android. Marshal back before touching Unity objects.
            public void onAudioRouteSnapshot(string json)
            {
                string snapshotJson = json;
                UnityMainThread.Enqueue(() => _snapshotCallback?.Invoke(snapshotJson));
            }
        }
#endif
    }
}
