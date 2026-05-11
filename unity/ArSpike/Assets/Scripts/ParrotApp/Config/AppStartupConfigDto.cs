using System;
using UnityEngine;

namespace ParrotApp.Config
{
    /// <summary>
    /// User-visible capability mode names shared by startup flow, menu RPCs,
    /// and Brain session_policy.py.
    /// </summary>
    public static class AppCapabilityModeNames
    {
        public const string SessionOnlySilent = "SessionOnlySilent";
        public const string VoiceOnlyNoVideo = "VoiceOnlyNoVideo";
        public const string VoiceVideoNoActionMonitor = "VoiceVideoNoActionMonitor";
        public const string FullARCompanion = "FullARCompanion";

        public static bool MicrophoneEnabled(string mode)
            => mode == VoiceOnlyNoVideo
               || mode == VoiceVideoNoActionMonitor
               || mode == FullARCompanion;

        public static bool VideoEnabled(string mode)
            => mode == VoiceVideoNoActionMonitor || mode == FullARCompanion;

        public static bool ActionMonitorEnabled(string mode)
            => mode == FullARCompanion;

        public static string Normalize(string mode)
        {
            switch (mode)
            {
                case SessionOnlySilent:
                case VoiceOnlyNoVideo:
                case VoiceVideoNoActionMonitor:
                case FullARCompanion:
                    return mode;
                default:
                    return FullARCompanion;
            }
        }
    }

    /// <summary>
    /// Startup-page selection DTO.
    ///
    /// reason: The old flow spread scene/room/model/mode/persona across
    /// inspector fields and implicit defaults. This DTO gives START one stable
    /// payload while keeping old presets compatible through default values.
    /// </summary>
    [Serializable]
    public class AppStartupConfigDto
    {
        // Scene selects the perception baseline, such as AR handheld vs a
        // desktop webcam session. It is intentionally separate from
        // workspace_id, which selects the in-app 2D surface.
        public string scene_id = "ar_handheld";

        // Room and identity feed token minting. Tokens are fetched at START
        // time instead of being persisted as long-lived app settings.
        public string room_id = "parrot-main";
        public string room_profile_id = "default";
        public string model_id = "GOSLO_default";
        public string persona_id = "goslo_parrot_default";
        public string pattern_id = "default";
        public string line_id = "line_a";
        public string line_profile_id = "linea_gemini_realtime";
        public string experience_mode = "ar_companion";
        public string skin_id = "manor";
        public string[] setting_file_refs = new string[0];

        // Capability mode gates microphone publishing, camera publishing,
        // greeting, and action-monitor semantics as one business bundle.
        public string capability_mode = AppCapabilityModeNames.FullARCompanion;

        // 2DWorkspace is the visible app/canvas surface. It may reference
        // IntentWorkspace items in metadata later, but it is not the Brain
        // IntentWorkspace storage itself.
        public string workspace_id = "mansion_hub";

        public string livekit_url = "";
        public string join_token = "";
        public string unity_identity = "";

        public void Normalize()
        {
            if (string.IsNullOrWhiteSpace(scene_id)) scene_id = "ar_handheld";
            if (string.IsNullOrWhiteSpace(room_id)) room_id = "parrot-main";
            if (string.IsNullOrWhiteSpace(room_profile_id)) room_profile_id = pattern_id;
            if (string.IsNullOrWhiteSpace(room_profile_id)) room_profile_id = "default";
            if (string.IsNullOrWhiteSpace(model_id)) model_id = "GOSLO_default";
            if (string.IsNullOrWhiteSpace(persona_id)) persona_id = "goslo_parrot_default";
            if (string.IsNullOrWhiteSpace(pattern_id)) pattern_id = "default";
            if (string.IsNullOrWhiteSpace(line_id)) line_id = "line_a";
            if (string.IsNullOrWhiteSpace(line_profile_id))
                line_profile_id = line_id == "line_b" ? "lineb_google_default" : "linea_gemini_realtime";
            if (string.IsNullOrWhiteSpace(experience_mode)) experience_mode = "ar_companion";
            if (string.IsNullOrWhiteSpace(skin_id)) skin_id = "manor";
            if (setting_file_refs == null) setting_file_refs = new string[0];
            if (string.IsNullOrWhiteSpace(workspace_id)) workspace_id = "mansion_hub";
            capability_mode = AppCapabilityModeNames.Normalize(capability_mode);
        }

        public static AppStartupConfigDto Default()
        {
            var dto = new AppStartupConfigDto();
            dto.Normalize();
            return dto;
        }
    }

    [Serializable]
    public class StartupPermissionSnapshotDto
    {
        public bool microphone_required;
        public bool microphone_authorized;
        public bool camera_required;
        public bool camera_authorized;
        public bool network_reachable;
        public string failure_reason = "";

        public bool IsOk =>
            network_reachable
            && (!microphone_required || microphone_authorized)
            && (!camera_required || camera_authorized);

        public string ToJson() => JsonUtility.ToJson(this);
    }
}
