using System.Collections;
using UnityEngine;

namespace ParrotApp.Core
{
    /// <summary>
    /// Android runtime permission helpers for the formal mobile App path.
    /// Unity's legacy <see cref="Application.RequestUserAuthorization"/> can
    /// report stale microphone state on targetSdk 36 devices, so Android builds
    /// must check the platform permission directly before starting LiveKit audio.
    /// </summary>
    public static class AndroidRuntimePermissions
    {
        public const string RecordAudio = "android.permission.RECORD_AUDIO";
        public const string BluetoothConnect = "android.permission.BLUETOOTH_CONNECT";

        public static bool HasMicrophonePermission()
        {
#if UNITY_ANDROID && !UNITY_EDITOR
            // On targetSdk 36 devices Unity's legacy microphone authorization
            // flag can remain true even while Android AppOps still reports
            // RECORD_AUDIO=ignore. The formal mobile path must trust the
            // platform runtime permission only; otherwise START can enter a
            // fake "Mic wait" state without a usable input device.
            return UnityEngine.Android.Permission.HasUserAuthorizedPermission(RecordAudio);
#else
            return Application.HasUserAuthorization(UserAuthorization.Microphone);
#endif
        }

        public static string MicrophonePermissionState()
        {
#if UNITY_ANDROID && !UNITY_EDITOR
            bool androidGranted = UnityEngine.Android.Permission.HasUserAuthorizedPermission(RecordAudio);
            bool legacyGranted = Application.HasUserAuthorization(UserAuthorization.Microphone);
            return $"android_record_audio={(androidGranted ? "granted" : "denied")} legacy_unity={(legacyGranted ? "granted" : "denied")}";
#else
            return Application.HasUserAuthorization(UserAuthorization.Microphone)
                ? "unity_microphone=granted"
                : "unity_microphone=denied";
#endif
        }

        public static IEnumerator RequestMicrophonePermission(float timeoutSeconds = 4f)
        {
#if UNITY_ANDROID && !UNITY_EDITOR
            Debug.Log("[AndroidRuntimePermissions] RECORD_AUDIO preflight: " + MicrophonePermissionState());
            if (HasMicrophonePermission())
            {
                Debug.Log("[AndroidRuntimePermissions] RECORD_AUDIO already granted");
                yield break;
            }

            bool callbackCompleted = false;
            string callbackState = "";
            var callbacks = new UnityEngine.Android.PermissionCallbacks();
            callbacks.PermissionGranted += permissionName =>
            {
                if (permissionName != RecordAudio) return;
                callbackState = "granted";
                callbackCompleted = true;
            };
            callbacks.PermissionDenied += permissionName =>
            {
                if (permissionName != RecordAudio) return;
                callbackState = "denied";
                callbackCompleted = true;
            };
            callbacks.PermissionDeniedAndDontAskAgain += permissionName =>
            {
                if (permissionName != RecordAudio) return;
                callbackState = "denied_and_dont_ask_again";
                callbackCompleted = true;
            };

            UnityEngine.Android.Permission.RequestUserPermission(RecordAudio, callbacks);
            float deadline = Time.realtimeSinceStartup + Mathf.Max(0.5f, timeoutSeconds);
            while (!HasMicrophonePermission() && !callbackCompleted && Time.realtimeSinceStartup < deadline)
                yield return null;

            if (!HasMicrophonePermission())
            {
                string suffix = string.IsNullOrWhiteSpace(callbackState)
                    ? "timeout/no_callback"
                    : callbackState;
                Debug.LogWarning("[AndroidRuntimePermissions] RECORD_AUDIO not granted after request: "
                                 + suffix + " " + MicrophonePermissionState());
            }
            else
            {
                Debug.Log("[AndroidRuntimePermissions] RECORD_AUDIO granted after request");
            }
#else
            if (!Application.HasUserAuthorization(UserAuthorization.Microphone))
                yield return Application.RequestUserAuthorization(UserAuthorization.Microphone);
#endif
        }
    }
}
