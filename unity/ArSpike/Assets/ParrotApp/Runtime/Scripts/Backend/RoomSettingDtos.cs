using System;
using ParrotApp.Config;

namespace ParrotApp.Backend
{
    [Serializable]
    public class RoomProfileDto
    {
        public int schema_version = 3;
        public string kind = "room_profile";
        public string room_profile_id = "default";
        public string display_name = "Default GOSLO setup";
        public string model_id = "GOSLO_default";
        public string persona_id = "goslo_parrot_default";
        public string line_id = "line_a";
        public string line_profile_id = "linea_gemini_realtime";
        public string scene_profile_id = "ar_handheld";
        public string experience_mode = "ar_companion";
        public string workspace_id = "mansion_hub";
        public string map_id = "mansion_hub";
        public string skin_id = "manor";
        public string[] setting_file_refs = Array.Empty<string>();
        public string livekit_room_id = "parrot-main";
    }

    [Serializable]
    public class RoomSettingSnapshotDto
    {
        public RoomProfileDto[] rooms = Array.Empty<RoomProfileDto>();
        public RoomProfileDto active_room = new RoomProfileDto();
        public RoomSettingSelectorsDto selectors = new RoomSettingSelectorsDto();
        public RoomCompatibilityDto compatibility = new RoomCompatibilityDto();
    }

    [Serializable]
    public class RoomSettingSelectorsDto
    {
        public ModelSelectorDto[] models = Array.Empty<ModelSelectorDto>();
        public RoomProfileDto[] rooms = Array.Empty<RoomProfileDto>();
        public PersonaSelectorDto[] personas = Array.Empty<PersonaSelectorDto>();
        public LineSelectorDto[] lines = Array.Empty<LineSelectorDto>();
        public LineProfileSelectorDto[] line_profiles = Array.Empty<LineProfileSelectorDto>();
        public SceneSelectorDto[] scenes = Array.Empty<SceneSelectorDto>();
        public SkinSelectorDto[] skins = Array.Empty<SkinSelectorDto>();
        public WorkspaceSelectorDto[] workspaces = Array.Empty<WorkspaceSelectorDto>();
        public ExperienceModeSelectorDto[] experience_modes = Array.Empty<ExperienceModeSelectorDto>();
        public RoomSettingDefaultsDto defaults = new RoomSettingDefaultsDto();
    }

    [Serializable]
    public class ModelSelectorDto
    {
        public string model_id = "";
        public string display_name = "";
    }

    [Serializable]
    public class PersonaSelectorDto
    {
        public string persona_id = "";
        public string display_name = "";
    }

    [Serializable]
    public class LineSelectorDto
    {
        public string line_id = "";
        public string display_name = "";
        public string state = "";
        public string health = "";
        public string summary = "";
        public LineSelectionPolicyDto selection_policy = new LineSelectionPolicyDto();
    }

    [Serializable]
    public class LineSelectionPolicyDto
    {
        public string scope = "";
        public bool requires_brain_restart;
        public string current_process_line_id = "";
        public int tier;
        public string tier_label = "";
        public string tier_summary = "";
        public string tier_summary_zh = "";
        public string tier_ui_action = "";
        public bool orchestrator_capable;
    }

    [Serializable]
    public class LineProfileSelectorDto
    {
        public string line_profile_id = "";
        public string display_name = "";
        public string line_id = "";
    }

    [Serializable]
    public class SceneSelectorDto
    {
        public string scene_id = "";
        public string scene_profile_id = "";
        public string display_name = "";
    }

    [Serializable]
    public class SkinSelectorDto
    {
        public string skin_id = "";
        public string display_name = "";
    }

    [Serializable]
    public class WorkspaceSelectorDto
    {
        public string workspace_id = "";
        public string display_name = "";
    }

    [Serializable]
    public class ExperienceModeSelectorDto
    {
        public string experience_mode = "";
        public string display_name = "";
    }

    [Serializable]
    public class RoomSettingDefaultsDto
    {
        public string line_id = "line_a";
        public string line_profile_id = "linea_gemini_realtime";
        public string experience_mode = "ar_companion";
        public string skin_id = "manor";
    }

    [Serializable]
    public class RoomProfilePreviewDto
    {
        public RoomProfileDto room_profile = new RoomProfileDto();
        public RoomCompatibilityDto compatibility = new RoomCompatibilityDto();
    }

    [Serializable]
    public class NewRoomProfileResponseDto
    {
        public RoomProfileDto room_profile = new RoomProfileDto();
        public RoomCompatibilityDto compatibility = new RoomCompatibilityDto();
    }

    [Serializable]
    public class RoomCompatibilityDto
    {
        public string state = "";
        public CapabilityDecisionDto[] decisions = Array.Empty<CapabilityDecisionDto>();
        public int tier;
        public string tier_label = "";
        public string tier_summary = "";
        public string tier_summary_zh = "";
        public string tier_ui_action = "";
    }

    [Serializable]
    public class CapabilityDecisionDto
    {
        public string capability_id = "";
        public string state = "";
        public string reason = "";
        public string source = "";
        public string fallback_action = "";
    }

    [Serializable]
    public class SaveRoomProfileResponseDto
    {
        public string status = "";
        public RoomProfileDto room_profile = new RoomProfileDto();
        public string room_profile_id = "";
        public string path = "";
        public string[] errors = Array.Empty<string>();
        public RoomCompatibilityDto compatibility = new RoomCompatibilityDto();
    }

    [Serializable]
    public class ApplyRoomProfileResponseDto
    {
        public bool success;
        public string room_profile_id = "";
        public RoomProfileDto room_profile = new RoomProfileDto();
        public string[] applied_keys = Array.Empty<string>();
        public string[] errors = Array.Empty<string>();
        public RoomCompatibilityDto compatibility = new RoomCompatibilityDto();
    }

    [Serializable]
    public class RoomProfileRequestEnvelopeDto
    {
        public RoomProfileDto room_profile = new RoomProfileDto();
    }

    public static class RoomSettingDtoMapper
    {
        public static AppStartupConfigDto ToStartupConfig(RoomProfileDto profile, AppStartupConfigDto fallback)
        {
            var config = fallback ?? AppStartupConfigDto.Default();
            if (profile == null)
            {
                config.Normalize();
                return config;
            }

            config.room_profile_id = NonEmpty(profile.room_profile_id, config.room_profile_id);
            config.pattern_id = config.room_profile_id;
            config.model_id = NonEmpty(profile.model_id, config.model_id);
            config.persona_id = NonEmpty(profile.persona_id, config.persona_id);
            config.line_id = NonEmpty(profile.line_id, config.line_id);
            config.line_profile_id = NonEmpty(profile.line_profile_id, config.line_profile_id);
            config.scene_id = NonEmpty(profile.scene_profile_id, config.scene_id);
            config.experience_mode = NonEmpty(profile.experience_mode, config.experience_mode);
            config.workspace_id = NonEmpty(profile.workspace_id, config.workspace_id);
            config.skin_id = NonEmpty(profile.skin_id, config.skin_id);
            config.room_id = NonEmpty(profile.livekit_room_id, config.room_id);
            config.setting_file_refs = profile.setting_file_refs ?? Array.Empty<string>();
            config.Normalize();
            return config;
        }

        public static RoomProfileDto FromStartupConfig(AppStartupConfigDto config, string displayName)
        {
            config = config ?? AppStartupConfigDto.Default();
            config.Normalize();
            return new RoomProfileDto
            {
                schema_version = 3,
                kind = "room_profile",
                room_profile_id = config.room_profile_id,
                display_name = string.IsNullOrWhiteSpace(displayName) ? config.room_profile_id : displayName,
                model_id = config.model_id,
                persona_id = config.persona_id,
                line_id = config.line_id,
                line_profile_id = config.line_profile_id,
                scene_profile_id = config.scene_id,
                experience_mode = config.experience_mode,
                workspace_id = config.workspace_id,
                map_id = config.workspace_id,
                skin_id = config.skin_id,
                setting_file_refs = config.setting_file_refs ?? Array.Empty<string>(),
                livekit_room_id = config.room_id,
            };
        }

        private static string NonEmpty(string value, string fallback)
            => string.IsNullOrWhiteSpace(value) ? fallback : value;
    }
}
