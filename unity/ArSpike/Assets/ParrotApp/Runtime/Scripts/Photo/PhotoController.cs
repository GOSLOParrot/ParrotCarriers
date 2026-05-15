using System;
using System.Collections.Generic;
using System.Globalization;
using System.Net.Http;
using System.Net.Http.Headers;
using System.Text;
using System.Threading.Tasks;
using ParrotApp.Attention;
using ParrotApp.Ecp;
using ParrotApp.LiveKit;
using UnityEngine;

namespace ParrotApp.Photo
{
    /// <summary>
    /// Sprint4 Phase 4 W8 — Unity 半边照片捕获闭环。
    ///
    /// <b>流程</b>：CapturePhoto → 256px preview JPEG (≤8KB base64)
    ///   → EcpEvent <c>photo.taken_preview</c> (12字段 payload, schema_version=1)
    ///   → HTTP POST 全分辨率 JPEG → Brain :7889/upload/photo/{photo_id}
    ///
    /// <b>photo_id 格式</b>：<c>ph_&lt;guid8&gt;</c>
    ///   （与 bbox_id "bb_&lt;guid8&gt;" / focus_id "fc_&lt;guid8&gt;" 命名空间隔离）。
    ///   Brain 端 PhotoNode.uuid 直接复用此 photo_id。
    ///
    /// <b>Reconnect 行为</b>（§B.6 — 与 BBox/Focus 不同）：
    /// <list type="bullet">
    ///   <item>已上传成功 (status=Uploaded)：<b>不重发</b>（asset 已落 Brain disk，重传无意义）</item>
    ///   <item>上传失败 (status=Failed)：Log 警告；spike 期未缓存 bytes，不能自动重试</item>
    /// </list>
    ///
    /// <b>Brain 端只读接收方</b>：
    /// <list type="bullet">
    ///   <item><c>src/parrot/brain/observer/photo.py</c> — _on_photo_taken_preview（PhotoNode upsert + BB write）</item>
    ///   <item><c>src/parrot/brain/photo_upload_server.py</c> — POST /upload/photo/{photo_id}（cache + publish photo.asset_uploaded）</item>
    /// </list>
    ///
    /// <b>硬约束</b>（entry doc §8.1 + 不允许 §7）：
    /// <list type="bullet">
    ///   <item>不发 <c>photo.asset_uploaded</c>（brain source；Unity 发 = source enum 错位）</item>
    ///   <item>preview_jpeg_b64 必须 &lt; 8KB（pre-check + quality cascade 75→60→50→40）</item>
    ///   <item>HTTP POST 必带 <c>X-Photo-Preview-Event-Id</c> header（Brain correlation_id 依赖）</item>
    ///   <item>不改 EcpEventPublisher / EcpEventDispatcher / BBoxController / FocusController 业务逻辑</item>
    /// </list>
    /// </summary>
    public class PhotoController : MonoBehaviour
    {
        // ─── Inspector fields ──────────────────────────────────────────

        [Header("Brain Upload Server")]
        [Tooltip("Brain photo_upload_server scheme. Editor/dev defaults to http; production can set https through photoUploadUrl.")]
        [SerializeField] private string brainScheme = "http";

        [Tooltip("Brain 端 photo_upload_server 主机（Editor: 127.0.0.1；真机: Castle 公网域名/内网IP）")]
        [SerializeField] private string brainHost = "127.0.0.1";

        [Tooltip("Brain 端 photo_upload_server 端口（锁定 7889 — 与 photo_upload_server.py:_DEFAULT_PORT 一致）")]
        [SerializeField] private int brainPort = 7889;

        [Header("Preview Encoding")]
        [Tooltip("Preview JPEG 初始质量（默认 75）；超 8KB 自动降级 60→50→40")]
        [SerializeField] [Range(10, 95)] private int previewJpegQuality = 75;

        [Tooltip("Full-res asset JPEG 质量（HTTP POST body 用；与 AR 帧分辨率无关）")]
        [SerializeField] [Range(50, 100)] private int fullResJpegQuality = 90;

        [Header("Dependencies")]
        [Tooltip("EcpEventPublisher；空时 Start 时自动 Find Instance。")]
        [SerializeField] private EcpEventPublisher publisher;

        [Tooltip("RoomManager；空时 Start 时自动 Find Instance（reconnect 监听）。")]
        [SerializeField] private RoomManager roomManager;

        // ─── Singleton ─────────────────────────────────────────────────

        public static PhotoController Instance { get; private set; }

        // ─── Upload status ─────────────────────────────────────────────

        private enum UploadStatus { Pending, Uploaded, Failed }

        private class PendingPhoto
        {
            public string PhotoId;
            public float CapturedAt;
            public string PreviewEventId;
            public UploadStatus Status;
            /// <summary>true = preview EcpEvent was actually delivered to LiveKit (not just dropped).</summary>
            public bool PreviewSent;
            /// <summary>Cached full-res JPEG bytes for reconnect retry when Status=Failed.
            /// Held until Status=Uploaded or app quits. Spike-acceptable memory cost (~100-500KB/photo).</summary>
            public byte[] FullResJpeg;
        }

        // ─── State ────────────────────────────────────────────────────

        // Key: photo_id. Source of truth for all captured photos this session.
        private readonly Dictionary<string, PendingPhoto> _pendingPhotos = new();

        public int PendingCount => _pendingPhotos.Count;
        public string UploadEndpointLabel => $"{brainScheme}://{brainHost}:{brainPort}";
        public bool IsUploadEndpointLoopback => IsLoopbackHost(brainHost);

        public void ConfigureUploadEndpoint(string host, int port)
        {
            if (string.IsNullOrWhiteSpace(host) || port <= 0)
                return;

            string normalizedHost = host.Trim();
            if (normalizedHost.StartsWith("http://", StringComparison.OrdinalIgnoreCase)
                || normalizedHost.StartsWith("https://", StringComparison.OrdinalIgnoreCase))
            {
                if (TryConfigureUploadEndpoint(normalizedHost))
                    return;
            }

            brainScheme = "http";
            brainHost = normalizedHost.TrimEnd('/');
            brainPort = port;
            Debug.Log($"[PhotoController] upload endpoint configured: {UploadEndpointLabel}");
        }

        public bool TryConfigureUploadEndpoint(string endpointUrl)
        {
            if (string.IsNullOrWhiteSpace(endpointUrl))
                return false;
            if (!Uri.TryCreate(endpointUrl.Trim(), UriKind.Absolute, out var uri))
                return false;
            if (!string.Equals(uri.Scheme, Uri.UriSchemeHttp, StringComparison.OrdinalIgnoreCase)
                && !string.Equals(uri.Scheme, Uri.UriSchemeHttps, StringComparison.OrdinalIgnoreCase))
                return false;

            brainScheme = string.Equals(uri.Scheme, Uri.UriSchemeHttps, StringComparison.OrdinalIgnoreCase)
                ? "https"
                : "http";
            brainHost = uri.Host;
            brainPort = uri.IsDefaultPort ? 7889 : uri.Port;
            Debug.Log($"[PhotoController] upload endpoint configured: {UploadEndpointLabel}");
            return true;
        }

        // ─── Lifecycle ─────────────────────────────────────────────────

        void Awake()
        {
            if (Instance != null && Instance != this)
            {
                Destroy(this);
                return;
            }
            Instance = this;
            if (publisher == null) publisher = EcpEventPublisher.Instance;
            if (roomManager == null) roomManager = RoomManager.Instance;
        }

        void Start()
        {
            if (publisher == null) publisher = EcpEventPublisher.Instance;
            if (roomManager == null) roomManager = RoomManager.Instance;
            if (roomManager != null)
                roomManager.OnConnected += OnRoomConnected;
        }

        void OnDestroy()
        {
            if (roomManager != null) roomManager.OnConnected -= OnRoomConnected;
            if (Instance == this) Instance = null;
        }

        // ─── Reconnect (§B.5) ─────────────────────────────────────────

        private void OnRoomConnected()
        {
            // Photo reconnect 与 BBox/Focus 不同（§B.5 锁定）：
            // - Uploaded：不重发（asset 已在 Brain disk；PhotoNode 幂等；重传无意义）
            // - Failed + PreviewSent=true：重试 HTTP POST（Brain 已有 preview → PhotoNode
            //   存在，只缺 asset_ref；不重发 preview）
            // - Failed + PreviewSent=false：preview 也未到 Brain，无法恢复（只 log）
            int retriedCount = 0;
            int noRetryCount = 0;
            int uploadedCount = 0;
            foreach (var kv in _pendingPhotos)
            {
                var p = kv.Value;
                switch (p.Status)
                {
                    case UploadStatus.Uploaded:
                        uploadedCount++;
                        break;
                    case UploadStatus.Failed:
                        if (p.PreviewSent && p.FullResJpeg != null)
                        {
                            // Preview reached Brain → retry HTTP POST only
                            retriedCount++;
                            p.Status = UploadStatus.Pending;
                            _ = UploadAssetAsync(p.PhotoId, p.FullResJpeg, p.PreviewEventId);
                        }
                        else
                        {
                            // Preview was never sent — Brain has no PhotoNode; cannot recover
                            noRetryCount++;
                            Debug.LogWarning(
                                $"[PhotoController] Reconnect: photo_id={kv.Key} status=Failed " +
                                $"previewSent={p.PreviewSent} — Brain missing preview; cannot retry.");
                        }
                        break;
                }
            }
            Debug.Log(
                $"[PhotoController] Reconnect: {uploadedCount} uploaded (NOT re-publishing) / " +
                $"{retriedCount} failed-retry-started / {noRetryCount} failed-no-preview (unrecoverable).");
        }

        // ─── Public API ───────────────────────────────────────────────

        /// <summary>拍照（无候选对象）。</summary>
        public void CapturePhoto() => CapturePhotoInternal("");

        /// <summary>拍照并指定候选对象 UUID（Brain 端 CANDIDATE_SUBJECT edge，Phase 5+ 实际建边）。</summary>
        public void CapturePhotoWithCandidate(string subjectUuid)
            => CapturePhotoInternal(subjectUuid ?? "");

        // ─── Main capture flow ─────────────────────────────────────────

        private void CapturePhotoInternal(string candidateSubjectUuid)
        {
            // 1. Capture full-res JPEG from Camera.main (spike: offscreen render)
            (byte[] fullResJpeg, int srcWidth, int srcHeight) = CaptureFullResJpeg();
            if (fullResJpeg == null || fullResJpeg.Length == 0)
            {
                Debug.LogError("[PhotoController] CapturePhoto: frame capture failed — Camera.main null or zero size");
                return;
            }

            // 2. Generate photo_id (ph_<guid8>)
            string photoId = GeneratePhotoId();

            // 3. Get camera pose (flat px/py/pz/qx/qy/qz/qw format — entry §8.1 spec)
            string poseJson = GetCameraPoseJson();

            // 4. Collect current active BBox/Focus refs
            var bboxRefs = GetActiveBboxRefs();
            var focusRefs = GetActiveFocusRefs();

            // 5. Build 256px preview → base64 with quality cascade
            string previewB64 = BuildPreviewBase64(fullResJpeg, out int usedQuality);
            if (previewB64 == null)
            {
                Debug.LogError(
                    $"[PhotoController] CapturePhoto: photo_id={photoId} — " +
                    $"preview_jpeg_b64 still >{EcpEventConsts.PayloadLimitBytes}B at Q40 (unusual for 256px). Aborting.");
                return;
            }

            // 6. Build 12-field payload JSON (schema_version=1, entry §8.3 + bb_schema.py transient/last_photo_event)
            long tsMs = EcpEventBuilder.UnixMilliseconds();
            string payloadJson = BuildPreviewPayloadJson(
                photoId: photoId,
                poseJson: poseJson,
                bboxRefs: bboxRefs,
                focusRefs: focusRefs,
                candidateSubjectUuid: candidateSubjectUuid,
                previewB64: previewB64,
                tsMs: tsMs);

            // 7. Build EcpEvent DTO (captures event_id for X-Photo-Preview-Event-Id header)
            string identity = roomManager != null ? roomManager.JoinIdentity : "";
            string roomName = roomManager != null ? roomManager.RoomName : "";
            var dto = EcpEventBuilder.BuildUnityEvent(
                eventType: EcpEventTypeNames.PhotoTakenPreview,
                payloadJson: payloadJson,
                unityIdentity: identity,
                roomId: roomName);
            if (dto == null)
            {
                // EcpEventBuilder already logged a warning (payload > 8KB)
                Debug.LogError(
                    $"[PhotoController] photo_id={photoId} — EcpEventBuilder rejected payload " +
                    $"(preview_jpeg_b64 Q{usedQuality} too large). Cascade logic should prevent this.");
                return;
            }
            string previewEventId = dto.event_id;

            // 8. Publish photo.taken_preview EcpEvent
            bool previewSent = false;
            if (publisher != null)
            {
                previewSent = publisher.Publish(dto);
            }
            else
            {
                Debug.LogWarning(
                    $"[PhotoController] photo_id={photoId} — no EcpEventPublisher; " +
                    $"preview EcpEvent dropped (event_id={previewEventId}).");
            }

            if (!previewSent)
            {
                // Preview was dropped (room not ready / publisher missing).
                // Brain has no PhotoNode yet. HTTP POST will still proceed so
                // the asset lands on Brain disk, but Brain's photo_upload_server
                // will log "asset_uploaded for unknown photo_id" (observer.photo
                // §B.5). reconnect retry is disabled for this photo (PreviewSent=false).
                Debug.LogWarning(
                    $"[PhotoController] photo_id={photoId} — preview EcpEvent NOT delivered. " +
                    "Brain will receive asset upload but PhotoNode may be missing (observer.photo " +
                    "asset_for_unknown_photo_id). Reconnect will not retry HTTP POST for this photo.");
            }

            // 9. Register in pending dict (cache full-res bytes for reconnect retry)
            _pendingPhotos[photoId] = new PendingPhoto
            {
                PhotoId = photoId,
                CapturedAt = Time.realtimeSinceStartup,
                PreviewEventId = previewEventId,
                Status = UploadStatus.Pending,
                PreviewSent = previewSent,
                FullResJpeg = fullResJpeg,
            };

            Debug.Log(
                $"[PhotoController] photo_id={photoId} preview_event_id={previewEventId} " +
                $"src={srcWidth}x{srcHeight} jpeg_q={usedQuality} b64_bytes={previewB64.Length} " +
                $"bbox_refs=[{string.Join(",", bboxRefs)}] focus_refs=[{string.Join(",", focusRefs)}] " +
                $"candidate={candidateSubjectUuid} previewSent={previewSent}");

            // 10. HTTP POST full-res asset (async, non-blocking)
            _ = UploadAssetAsync(photoId, fullResJpeg, previewEventId);
        }

        // ─── Frame capture ────────────────────────────────────────────

        /// <summary>
        /// Spike 路径：渲染 Camera.main 到 RenderTexture → 读像素 → JPEG 编码。
        /// #if UNITY_AR_FOUNDATION 时应扩展为 ARCameraManager.frameReceived 路径（Phase 5+）。
        /// </summary>
        private (byte[] jpeg, int width, int height) CaptureFullResJpeg()
        {
            var cam = Camera.main;
            if (cam == null) return (null, 0, 0);

            int w = cam.pixelWidth;
            int h = cam.pixelHeight;
            if (w <= 0 || h <= 0) return (null, 0, 0);

            // Offscreen render
            var rt = RenderTexture.GetTemporary(w, h, 24, RenderTextureFormat.ARGB32);
            var prevTarget = cam.targetTexture;
            cam.targetTexture = rt;
            cam.Render();
            cam.targetTexture = prevTarget;

            // Read pixels into Texture2D
            var tex = new Texture2D(w, h, TextureFormat.RGB24, mipChain: false);
            var prevActive = RenderTexture.active;
            RenderTexture.active = rt;
            tex.ReadPixels(new Rect(0, 0, w, h), 0, 0);
            tex.Apply();
            RenderTexture.active = prevActive;
            RenderTexture.ReleaseTemporary(rt);

            byte[] jpeg = ImageConversion.EncodeToJPG(tex, fullResJpegQuality);
            Destroy(tex);
            return (jpeg, w, h);
        }

        // ─── 256px preview encoding ────────────────────────────────────

        /// <summary>
        /// 从全分辨率 JPEG bytes 生成 256px 最长边缩放的 JPEG base64 字符串。
        /// Quality cascade: 75→60→50→40。返回 null 表示所有档位均超 8KB（极罕见）。
        /// </summary>
        private string BuildPreviewBase64(byte[] fullResJpeg, out int usedQuality)
        {
            // Decode full-res JPEG into Texture2D for scaling
            var src = new Texture2D(2, 2);
            ImageConversion.LoadImage(src, fullResJpeg);

            Texture2D preview = DownscaleToMax256(src);
            bool newTexture = !ReferenceEquals(preview, src);
            if (newTexture) Destroy(src);

            // headroom: 8KB limit minus ~300 bytes for other payload fields
            int base64Limit = EcpEventConsts.PayloadLimitBytes - 300;

            // Quality cascade: start at inspector value, fall back to 60→50→40
            int[] cascade = BuildQualityCascade(previewJpegQuality);
            string result = null;
            usedQuality = cascade[cascade.Length - 1];

            foreach (int q in cascade)
            {
                byte[] jpg = ImageConversion.EncodeToJPG(preview, q);
                string b64 = Convert.ToBase64String(jpg);
                // b64.Length in UTF-8 bytes = b64.Length (all ASCII)
                if (b64.Length <= base64Limit)
                {
                    usedQuality = q;
                    result = b64;
                    break;
                }
                Debug.LogWarning(
                    $"[PhotoController] preview_jpeg_b64 Q{q} len={b64.Length}B > limit ({base64Limit}B); trying lower quality");
            }

            Destroy(preview);
            return result;
        }

        private static int[] BuildQualityCascade(int startQuality)
        {
            // Always include 60/50/40 as fallbacks below the user-configured start
            var levels = new List<int> { startQuality };
            foreach (int q in new[] { 60, 50, 40 })
            {
                if (q < startQuality) levels.Add(q);
            }
            return levels.ToArray();
        }

        /// <summary>Scale <paramref name="src"/> to max 256px on longest side. Returns
        /// <paramref name="src"/> unchanged if already ≤256px on both sides.</summary>
        private static Texture2D DownscaleToMax256(Texture2D src)
        {
            int srcW = src.width;
            int srcH = src.height;
            int maxSide = Mathf.Max(srcW, srcH);
            if (maxSide <= 256) return src;  // no scaling needed

            float scale = 256f / maxSide;
            int dstW = Mathf.Max(1, Mathf.RoundToInt(srcW * scale));
            int dstH = Mathf.Max(1, Mathf.RoundToInt(srcH * scale));

            var rt = RenderTexture.GetTemporary(dstW, dstH, 0, RenderTextureFormat.ARGB32);
            Graphics.Blit(src, rt);

            var dst = new Texture2D(dstW, dstH, TextureFormat.RGB24, mipChain: false);
            var prevActive = RenderTexture.active;
            RenderTexture.active = rt;
            dst.ReadPixels(new Rect(0, 0, dstW, dstH), 0, 0);
            dst.Apply();
            RenderTexture.active = prevActive;
            RenderTexture.ReleaseTemporary(rt);
            return dst;
        }

        // ─── Payload builder ──────────────────────────────────────────

        /// <summary>
        /// Build the 12-field photo.taken_preview payload JSON, strictly aligned with
        /// Brain-side <c>observer/photo._build_bb_payload</c> and
        /// <c>bb_schema.py:transient/last_photo_event</c> comment.
        ///
        /// Fields: schema_version | photo_id | stage | pose | episode_ref |
        ///         focus_refs | bbox_refs | candidate_subject_uuid |
        ///         preview_jpeg_b64 | asset_ref | asset_bytes | ts_ms
        /// </summary>
        private static string BuildPreviewPayloadJson(
            string photoId,
            string poseJson,
            List<string> bboxRefs,
            List<string> focusRefs,
            string candidateSubjectUuid,
            string previewB64,
            long tsMs)
        {
            var ci = CultureInfo.InvariantCulture;
            var sb = new StringBuilder(previewB64.Length + 256);
            sb.Append('{');
            sb.Append("\"schema_version\":1,");
            sb.Append("\"photo_id\":").Append(QuoteJson(photoId)).Append(',');
            sb.Append("\"stage\":\"preview\",");
            sb.Append("\"pose\":").Append(poseJson).Append(',');
            sb.Append("\"episode_ref\":\"\",");
            sb.Append("\"focus_refs\":").Append(SerializeStringList(focusRefs)).Append(',');
            sb.Append("\"bbox_refs\":").Append(SerializeStringList(bboxRefs)).Append(',');
            sb.Append("\"candidate_subject_uuid\":").Append(QuoteJson(candidateSubjectUuid)).Append(',');
            sb.Append("\"preview_jpeg_b64\":").Append(QuoteJson(previewB64)).Append(',');
            sb.Append("\"asset_ref\":\"\",");
            sb.Append("\"asset_bytes\":0,");
            sb.Append("\"ts_ms\":").Append(tsMs.ToString(ci));
            sb.Append('}');
            return sb.ToString();
        }

        // ─── Pose helper ──────────────────────────────────────────────

        /// <summary>
        /// Camera pose as flat JSON object with px/py/pz/qx/qy/qz/qw keys.
        /// (entry doc §8.1 payload spec; Brain stores in PhotoNode.meta["pose"])
        /// </summary>
        private static string GetCameraPoseJson()
        {
            var cam = Camera.main;
            if (cam == null)
                return "{\"px\":0,\"py\":0,\"pz\":0,\"qx\":0,\"qy\":0,\"qz\":0,\"qw\":1}";

            var pos = cam.transform.position;
            var rot = cam.transform.rotation;
            var ci = CultureInfo.InvariantCulture;
            return "{"
                + "\"px\":" + pos.x.ToString("R", ci) + ","
                + "\"py\":" + pos.y.ToString("R", ci) + ","
                + "\"pz\":" + pos.z.ToString("R", ci) + ","
                + "\"qx\":" + rot.x.ToString("R", ci) + ","
                + "\"qy\":" + rot.y.ToString("R", ci) + ","
                + "\"qz\":" + rot.z.ToString("R", ci) + ","
                + "\"qw\":" + rot.w.ToString("R", ci)
                + "}";
        }

        // ─── HttpClient (replaces UnityWebRequest to bypass Android cleartext policy) ──

        // Single shared instance — HttpClient is designed to be reused.
        // Using System.Net.Http.HttpClient bypasses Unity's UnityWebRequest
        // Android cleartext-traffic security layer, which blocks http:// in
        // Editor Play Mode when the build target is Android.
        private static readonly HttpClient _httpClient = new HttpClient { Timeout = TimeSpan.FromSeconds(10) };

        // ─── Active refs helpers ──────────────────────────────────────

        private static List<string> GetActiveBboxRefs()
        {
            var result = new List<string>();
            var bc = BBoxController.Instance;
            if (bc != null) bc.AppendActiveIds(result);
            return result;
        }

        private static List<string> GetActiveFocusRefs()
        {
            var result = new List<string>();
            var fc = FocusController.Instance;
            if (fc != null) fc.AppendActiveIds(result);
            return result;
        }

        // ─── HTTP upload ──────────────────────────────────────────────

        /// <summary>
        /// POST full-res JPEG to Brain photo_upload_server using System.Net.Http.HttpClient.
        /// Uses HttpClient instead of UnityWebRequest to bypass Unity's Android cleartext-
        /// traffic security layer (which blocks http:// in Editor with Android build target).
        /// Retry up to 3 times: 1s / 2s / 4s exponential backoff.
        /// </summary>
        private async Task UploadAssetAsync(string photoId, byte[] fullResJpeg, string previewEventId)
        {
            string url = $"{brainScheme}://{brainHost}:{brainPort}/upload/photo/{photoId}";
            // 4 total attempts = initial attempt + 3 retries (1s / 2s / 4s backoff)
            int[] retryDelaysMs = { 1000, 2000, 4000 };
            bool success = false;

            for (int attempt = 0; attempt < 4; attempt++)
            {
                if (attempt > 0)
                {
                    int delay = retryDelaysMs[attempt - 1];
                    Debug.Log($"[PhotoController] HTTP POST retry {attempt}/3 in {delay}ms for photo_id={photoId}");
                    await Task.Delay(delay);
                }

                try
                {
                    using var content = new ByteArrayContent(fullResJpeg);
                    content.Headers.ContentType = new MediaTypeHeaderValue("image/jpeg");

                    using var request = new HttpRequestMessage(HttpMethod.Post, url);
                    request.Content = content;
                    // Required: Brain uses this as correlation_id for photo.asset_uploaded event
                    request.Headers.TryAddWithoutValidation("X-Photo-Preview-Event-Id", previewEventId);

                    using var response = await _httpClient.SendAsync(request);
                    int statusCode = (int)response.StatusCode;

                    if (response.IsSuccessStatusCode)
                    {
                        Debug.Log(
                            $"[PhotoController] HTTP POST /upload/photo/{photoId} → {statusCode} " +
                            $"bytes={fullResJpeg.Length}");
                        if (_pendingPhotos.TryGetValue(photoId, out var p))
                        {
                            p.Status = UploadStatus.Uploaded;
                            p.FullResJpeg = null;  // Release cached bytes once uploaded
                        }
                        success = true;
                        break;
                    }

                    Debug.LogWarning(
                        $"[PhotoController] HTTP POST /upload/photo/{photoId} attempt={attempt + 1}/3 " +
                        $"status={statusCode}");
                }
                catch (Exception ex)
                {
                    Debug.LogWarning(
                        $"[PhotoController] HTTP POST /upload/photo/{photoId} attempt={attempt + 1}/3 " +
                        $"exception: {ex.GetType().Name}: {ex.Message}");
                }
            }

            if (!success)
            {
                if (_pendingPhotos.TryGetValue(photoId, out var p))
                    p.Status = UploadStatus.Failed;
                Debug.LogError(
                    $"[PhotoController] HTTP POST /upload/photo/{photoId} FAILED after 3 attempts (status=Failed).");
            }
        }

        // ─── photo_id generation ──────────────────────────────────────

        private static string GeneratePhotoId()
        {
            // ph_<guid8> — Brain 端 observer/photo.py 直接用此作为 PhotoNode.uuid
            // 命名空间与 bbox_id (bb_) / focus_id (fc_) 隔离
            string g = Guid.NewGuid().ToString("N").Substring(0, 8);
            return "ph_" + g;
        }

        private static bool IsLoopbackHost(string host)
        {
            if (string.IsNullOrWhiteSpace(host)) return true;
            string normalized = host.Trim().TrimEnd('/').ToLowerInvariant();
            return normalized == "127.0.0.1"
                   || normalized == "localhost"
                   || normalized == "::1"
                   || normalized == "0.0.0.0";
        }

        // ─── JSON helpers ─────────────────────────────────────────────

        private static string SerializeStringList(List<string> items)
        {
            if (items == null || items.Count == 0) return "[]";
            var sb = new StringBuilder(items.Count * 24);
            sb.Append('[');
            for (int i = 0; i < items.Count; i++)
            {
                if (i > 0) sb.Append(',');
                sb.Append(QuoteJson(items[i]));
            }
            sb.Append(']');
            return sb.ToString();
        }

        private static string QuoteJson(string s)
        {
            if (s == null) return "\"\"";
            var sb = new StringBuilder(s.Length + 2);
            sb.Append('"');
            foreach (char c in s)
            {
                switch (c)
                {
                    case '\\': sb.Append("\\\\"); break;
                    case '"': sb.Append("\\\""); break;
                    case '\n': sb.Append("\\n"); break;
                    case '\r': sb.Append("\\r"); break;
                    case '\t': sb.Append("\\t"); break;
                    default:
                        if (c < 0x20) sb.AppendFormat("\\u{0:x4}", (int)c);
                        else sb.Append(c);
                        break;
                }
            }
            sb.Append('"');
            return sb.ToString();
        }

        // ─── Editor smoke ContextMenu entries ─────────────────────────

        [ContextMenu("Debug: Capture Test Photo")]
        public void DebugCaptureTestPhoto()
        {
            Debug.Log("[PhotoController] DEBUG: Capture Test Photo (no candidate)");
            CapturePhoto();
        }

        [ContextMenu("Debug: Capture With Test Candidate")]
        public void DebugCaptureWithTestCandidate()
        {
            Debug.Log("[PhotoController] DEBUG: Capture With Test Candidate (candidate_subject_uuid=obj_test_42)");
            CapturePhotoWithCandidate("obj_test_42");
        }

        [ContextMenu("Debug: Capture With Active Refs")]
        public void DebugCaptureWithActiveRefs()
        {
            var bboxRefs = GetActiveBboxRefs();
            var focusRefs = GetActiveFocusRefs();
            Debug.Log(
                $"[PhotoController] DEBUG: Capture With Active Refs " +
                $"bbox=[{string.Join(",", bboxRefs)}] focus=[{string.Join(",", focusRefs)}]");
            // CapturePhotoInternal already reads from BBoxController/FocusController internally
            CapturePhoto();
        }
    }
}
