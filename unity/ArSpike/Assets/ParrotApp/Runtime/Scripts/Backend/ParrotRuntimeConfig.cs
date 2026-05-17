using System;
using UnityEngine;

namespace ParrotApp.Backend
{
    [Serializable]
    public class ParrotRuntimeConfigDto
    {
        public string mintUrl = "";
        public string mintSecret = "";
        public string liveKitUrl = "";
        public string room = "";
        public string appApiUrl = "";
        public string appApiSecret = "";
        public string orchestratorUrl = "";
        public string orchestratorSecret = "";
        public string photoUploadUrl = "";
        public string photoUploadHost = "";
        public int photoUploadPort = 0;
        public bool visualToolDevEnabled = false;
        public bool visualToolHttpEnabled = true;
    }

    public static class ParrotRuntimeConfig
    {
        public static ParrotRuntimeConfigDto Load()
        {
            var dto = new ParrotRuntimeConfigDto();
            var asset = Resources.Load<TextAsset>("parrot_config");
            if (asset == null) return dto;

            try
            {
                var parsed = JsonUtility.FromJson<ParrotRuntimeConfigDto>(asset.text);
                return parsed ?? dto;
            }
            catch (Exception ex)
            {
                Debug.LogWarning($"[ParrotRuntimeConfig] failed to parse parrot_config: {ex.Message}");
                return dto;
            }
        }
    }
}
