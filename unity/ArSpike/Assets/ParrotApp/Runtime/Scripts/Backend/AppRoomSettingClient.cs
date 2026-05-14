using System;
using System.Collections;
using System.Text;
using UnityEngine;
using UnityEngine.Networking;

namespace ParrotApp.Backend
{
    public class AppRoomSettingClient : MonoBehaviour
    {
        // Deliberately empty by default. A phone build must get this from
        // gitignored Resources/parrot_config.json or an explicit Inspector
        // override; otherwise START should fail fast instead of trying the
        // device's own localhost.
        [SerializeField] private string appApiBaseUrl = "";
        [SerializeField] private string bearerSecret = "";

        public string AppApiBaseUrl
        {
            get => appApiBaseUrl;
            set => appApiBaseUrl = (value ?? "").TrimEnd('/');
        }

        public bool HasEndpoint => !string.IsNullOrWhiteSpace(appApiBaseUrl);

        private void Awake()
        {
            LoadRuntimeConfig();
        }

        private void LoadRuntimeConfig()
        {
            var config = ParrotRuntimeConfig.Load();
            if (!string.IsNullOrWhiteSpace(config.appApiUrl))
                appApiBaseUrl = config.appApiUrl.TrimEnd('/');
            if (!string.IsNullOrWhiteSpace(config.appApiSecret))
                bearerSecret = config.appApiSecret;
        }

        public IEnumerator LoadSnapshot(string roomProfileId, Action<RequestResult<RoomSettingSnapshotDto>> onComplete)
        {
            if (!HasEndpoint)
            {
                onComplete?.Invoke(RequestResult<RoomSettingSnapshotDto>.Fail("app_api_url_empty"));
                yield break;
            }

            string url = appApiBaseUrl.TrimEnd('/') + "/api/app/room-setting";
            if (!string.IsNullOrWhiteSpace(roomProfileId))
                url += "?room_profile_id=" + UnityWebRequest.EscapeURL(roomProfileId);

            using (var req = UnityWebRequest.Get(url))
            {
                ApplyAuth(req);
                yield return req.SendWebRequest();
                if (req.result != UnityWebRequest.Result.Success)
                {
                    onComplete?.Invoke(RequestResult<RoomSettingSnapshotDto>.Fail(req.error ?? "snapshot_request_failed"));
                    yield break;
                }

                try
                {
                    var dto = JsonUtility.FromJson<RoomSettingSnapshotDto>(req.downloadHandler.text);
                    onComplete?.Invoke(RequestResult<RoomSettingSnapshotDto>.Ok(dto));
                }
                catch (Exception ex)
                {
                    onComplete?.Invoke(RequestResult<RoomSettingSnapshotDto>.Fail("snapshot_parse_failed:" + ex.Message));
                }
            }
        }

        public IEnumerator Preview(RoomProfileDto roomProfile, Action<RequestResult<RoomProfilePreviewDto>> onComplete)
        {
            string body = "{\"room_profile\":" + JsonUtility.ToJson(roomProfile ?? new RoomProfileDto()) + "}";
            yield return PostJson("/api/app/room-setting/preview", body, text =>
            {
                try
                {
                    return RequestResult<RoomProfilePreviewDto>.Ok(JsonUtility.FromJson<RoomProfilePreviewDto>(text));
                }
                catch (Exception ex)
                {
                    return RequestResult<RoomProfilePreviewDto>.Fail("preview_parse_failed:" + ex.Message);
                }
            }, onComplete);
        }

        public IEnumerator NewRoomProfile(string baseId, string displayName, Action<RequestResult<NewRoomProfileResponseDto>> onComplete)
        {
            string body = "{"
                          + "\"base_id\":" + JsonQuote(baseId) + ","
                          + "\"display_name\":" + JsonQuote(displayName)
                          + "}";
            yield return PostJson("/api/app/room-setting/new", body, text =>
            {
                try
                {
                    var dto = JsonUtility.FromJson<NewRoomProfileResponseDto>(text);
                    if (dto == null || dto.room_profile == null)
                        return RequestResult<NewRoomProfileResponseDto>.Fail("new_room_missing_profile");
                    return RequestResult<NewRoomProfileResponseDto>.Ok(dto);
                }
                catch (Exception ex)
                {
                    return RequestResult<NewRoomProfileResponseDto>.Fail("new_room_parse_failed:" + ex.Message);
                }
            }, onComplete);
        }

        public IEnumerator SaveRoomProfile(RoomProfileDto roomProfile, Action<RequestResult<SaveRoomProfileResponseDto>> onComplete)
        {
            string body = "{\"room_profile\":" + JsonUtility.ToJson(roomProfile ?? new RoomProfileDto()) + "}";
            yield return PostJson("/api/app/room-setting/save", body, text =>
            {
                try
                {
                    var dto = JsonUtility.FromJson<SaveRoomProfileResponseDto>(text);
                    if (dto != null && !string.IsNullOrWhiteSpace(dto.status)
                        && !string.Equals(dto.status, "ok", StringComparison.OrdinalIgnoreCase))
                    {
                        return RequestResult<SaveRoomProfileResponseDto>.Fail("save_room_profile_rejected:" + dto.status);
                    }
                    if (dto == null || dto.room_profile == null
                        || string.IsNullOrWhiteSpace(dto.room_profile.room_profile_id))
                    {
                        return RequestResult<SaveRoomProfileResponseDto>.Fail("save_room_profile_missing_profile");
                    }
                    return RequestResult<SaveRoomProfileResponseDto>.Ok(dto);
                }
                catch (Exception ex)
                {
                    return RequestResult<SaveRoomProfileResponseDto>.Fail("save_room_parse_failed:" + ex.Message);
                }
            }, onComplete);
        }

        public IEnumerator ApplyRoomProfile(RoomProfileDto roomProfile, Action<RequestResult<ApplyRoomProfileResponseDto>> onComplete)
        {
            string body = "{\"room_profile\":" + JsonUtility.ToJson(roomProfile ?? new RoomProfileDto()) + "}";
            yield return PostJson("/api/app/room-setting/apply", body, text =>
            {
                try
                {
                    var dto = JsonUtility.FromJson<ApplyRoomProfileResponseDto>(text);
                    if (dto != null && !dto.success)
                        return RequestResult<ApplyRoomProfileResponseDto>.Fail("apply_room_profile_rejected");
                    if (dto == null || dto.room_profile == null
                        || string.IsNullOrWhiteSpace(dto.room_profile.room_profile_id))
                    {
                        return RequestResult<ApplyRoomProfileResponseDto>.Fail("apply_room_profile_missing_profile");
                    }
                    return RequestResult<ApplyRoomProfileResponseDto>.Ok(dto);
                }
                catch (Exception ex)
                {
                    return RequestResult<ApplyRoomProfileResponseDto>.Fail("apply_room_parse_failed:" + ex.Message);
                }
            }, onComplete);
        }

        private IEnumerator PostJson<T>(
            string path,
            string body,
            Func<string, RequestResult<T>> parser,
            Action<RequestResult<T>> onComplete)
        {
            if (!HasEndpoint)
            {
                onComplete?.Invoke(RequestResult<T>.Fail("app_api_url_empty"));
                yield break;
            }

            string url = appApiBaseUrl.TrimEnd('/') + path;
            byte[] bytes = Encoding.UTF8.GetBytes(body ?? "{}");
            using (var req = new UnityWebRequest(url, UnityWebRequest.kHttpVerbPOST))
            {
                req.uploadHandler = new UploadHandlerRaw(bytes);
                req.downloadHandler = new DownloadHandlerBuffer();
                req.SetRequestHeader("Content-Type", "application/json");
                ApplyAuth(req);
                yield return req.SendWebRequest();
                if (req.result != UnityWebRequest.Result.Success)
                {
                    onComplete?.Invoke(RequestResult<T>.Fail(req.error ?? "post_failed"));
                    yield break;
                }
                onComplete?.Invoke(parser(req.downloadHandler.text));
            }
        }

        private void ApplyAuth(UnityWebRequest req)
        {
            if (!string.IsNullOrWhiteSpace(bearerSecret))
                req.SetRequestHeader("Authorization", "Bearer " + bearerSecret);
        }

        private static string JsonQuote(string value)
        {
            if (value == null) return "\"\"";
            return "\"" + value.Replace("\\", "\\\\").Replace("\"", "\\\"") + "\"";
        }
    }

    public struct RequestResult<T>
    {
        public bool Success;
        public T Value;
        public string Error;

        public static RequestResult<T> Ok(T value)
            => new RequestResult<T> { Success = true, Value = value, Error = "" };

        public static RequestResult<T> Fail(string error)
            => new RequestResult<T> { Success = false, Value = default(T), Error = error ?? "" };
    }
}
