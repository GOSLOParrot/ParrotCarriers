using System;
using System.Collections.Generic;
using System.Globalization;
using System.Text;
using ParrotApp.Ecp;
using ParrotApp.LiveKit;
using UnityEngine;

namespace ParrotApp.Attention
{
    /// <summary>
    /// Sprint4 Phase 4 W6-7 — Focus 放大镜 UI 状态机 + EcpEvent 出包。
    ///
    /// <b>UI 范围</b>（entry doc §8.1 L6 锁定）：
    /// <list type="bullet">
    /// <item>用户锚定 Focus → reliable EcpEvent <c>focus.anchored</c></item>
    /// <item>用户释放 Focus → reliable EcpEvent <c>focus.released</c></item>
    /// <item><b>不发</b>拖动 lossy <c>parrot.ecp.tick</c>（W6-7 范围外，同 BBox）</item>
    /// </list>
    ///
    /// <b>Focus vs BBox 区分度</b>（entry doc §3.3 用户级补充）：
    /// <list type="bullet">
    /// <item>放大镜本身有"放大查看"功能，<b>不那么烦人</b> → Δ_focus = 0.2，5 次累加才到 threshold</item>
    /// <item>Brain 端 <c>FocusBboxThreshold</c> 用 compound key <c>focus:&lt;id&gt;</c> 与 BBox
    ///   隔离累加（refs.py 同样按 kind+id 隔离，threshold 与 refs 一致）</item>
    /// </list>
    ///
    /// <b>focus_id 生成</b>：<c>fc_&lt;guid8&gt;</c>。Brain 端 observer/focus.py 用它索引 RefBinding。
    ///
    /// <b>Reconnect 行为</b>（§B.6）：与 <see cref="BBoxController"/> 同——OnConnected 时
    /// 全量重 publish；refs.bind_focus 幂等保护。
    ///
    /// <b>不做</b>：与 <see cref="BBoxController"/> 同 5 条边界。
    /// </summary>
    public class FocusController : MonoBehaviour
    {
        [Tooltip("Echo 出包用；空时 Awake 时 Find。")]
        [SerializeField] private EcpEventPublisher publisher;

        [Tooltip("RoomManager 用于订阅 OnConnected 触发 reconnect 重 publish；空时 Awake 时 Find。")]
        [SerializeField] private RoomManager roomManager;

        public static FocusController Instance { get; private set; }

        private readonly Dictionary<string, FocusRecord> _active = new();

        public int ActiveCount => _active.Count;

        /// <summary>Append current active focus_id strings into <paramref name="output"/>.
        /// Read-only accessor for PhotoController payload building.</summary>
        public void AppendActiveIds(System.Collections.Generic.List<string> output)
        {
            foreach (var k in _active.Keys) output.Add(k);
        }

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
            {
                roomManager.OnConnected += OnRoomConnected;
            }
        }

        void OnDestroy()
        {
            if (roomManager != null) roomManager.OnConnected -= OnRoomConnected;
            if (Instance == this) Instance = null;
        }

        // ─── public API ──────────────────────────────────────────────

        /// <summary>
        /// 锚定一个 Focus（放大镜定位）。
        /// center / radius 是屏幕 / 平面坐标，由 caller 决定单位。
        /// </summary>
        public string AnchorFocus(Vector2 center, float radius, Pose pose, string label = "")
        {
            string id = GenerateFocusId();
            var record = new FocusRecord
            {
                FocusId = id,
                Center = center,
                Radius = radius,
                Pose = pose,
                Label = label ?? "",
                AnchoredAt = Time.realtimeSinceStartup,
            };
            _active[id] = record;
            PublishAnchored(record);
            return id;
        }

        public bool ReleaseFocus(string focusId)
        {
            if (string.IsNullOrEmpty(focusId)) return false;
            if (!_active.TryGetValue(focusId, out var record)) return false;
            _active.Remove(focusId);
            PublishReleased(record);
            return true;
        }

        public void ReleaseAll()
        {
            var ids = new List<string>(_active.Keys);
            foreach (var id in ids) ReleaseFocus(id);
        }

        // ─── reconnect re-publish (§B.6) ─────────────────────────────

        private void OnRoomConnected()
        {
            if (_active.Count == 0) return;
            Debug.Log($"[FocusController] Room connected — re-publishing {_active.Count} ON focus(es)");
            foreach (var record in _active.Values)
            {
                PublishAnchored(record);
            }
        }

        // ─── publish helpers ─────────────────────────────────────────

        private void PublishAnchored(FocusRecord r)
        {
            if (publisher == null)
            {
                Debug.LogWarning("[FocusController] No EcpEventPublisher — focus.anchored dropped");
                return;
            }
            string payload = BuildAnchoredPayload(r);
            publisher.PublishUnityEvent(EcpEventTypeNames.FocusAnchored, payload);
        }

        private void PublishReleased(FocusRecord r)
        {
            if (publisher == null)
            {
                Debug.LogWarning("[FocusController] No EcpEventPublisher — focus.released dropped");
                return;
            }
            string payload = "{\"focus_id\":" + Quote(r.FocusId) + "}";
            publisher.PublishUnityEvent(EcpEventTypeNames.FocusReleased, payload);
        }

        private static string BuildAnchoredPayload(FocusRecord r)
        {
            var ci = CultureInfo.InvariantCulture;
            var sb = new StringBuilder(192);
            sb.Append("{");
            sb.Append("\"focus_id\":").Append(Quote(r.FocusId)).Append(',');
            sb.Append("\"center\":[")
              .Append(r.Center.x.ToString("R", ci)).Append(',')
              .Append(r.Center.y.ToString("R", ci)).Append("],");
            sb.Append("\"radius\":").Append(r.Radius.ToString("R", ci)).Append(',');
            sb.Append("\"pose\":").Append(SerializePose(r.Pose, ci)).Append(',');
            sb.Append("\"label\":").Append(Quote(r.Label));
            sb.Append("}");
            return sb.ToString();
        }

        private static string SerializePose(Pose p, CultureInfo ci)
        {
            return "{"
                + "\"position\":[" + p.position.x.ToString("R", ci) + ","
                                   + p.position.y.ToString("R", ci) + ","
                                   + p.position.z.ToString("R", ci) + "],"
                + "\"rotation\":[" + p.rotation.x.ToString("R", ci) + ","
                                   + p.rotation.y.ToString("R", ci) + ","
                                   + p.rotation.z.ToString("R", ci) + ","
                                   + p.rotation.w.ToString("R", ci) + "]"
                + "}";
        }

        private static string Quote(string s)
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

        private static string GenerateFocusId()
        {
            string g = Guid.NewGuid().ToString("N").Substring(0, 8);
            return "fc_" + g;
        }

        // ─── Editor smoke 入口 ───────────────────────────────────────

        [ContextMenu("Debug: Anchor Test Focus")]
        public void DebugAnchorTestFocus()
        {
            var pose = new Pose(new Vector3(0f, 1.2f, 0.6f), Quaternion.identity);
            string id = AnchorFocus(
                center: new Vector2(0.5f, 0.5f),
                radius: 0.15f,
                pose: pose,
                label: "test_focus");
            Debug.Log($"[FocusController] DEBUG anchored focus_id={id} (active={ActiveCount})");
        }

        [ContextMenu("Debug: Release Last Focus")]
        public void DebugReleaseLastFocus()
        {
            if (_active.Count == 0)
            {
                Debug.Log("[FocusController] DEBUG release last: no active Focus");
                return;
            }
            string anyId = "";
            foreach (var k in _active.Keys) { anyId = k; break; }
            bool ok = ReleaseFocus(anyId);
            Debug.Log($"[FocusController] DEBUG released focus_id={anyId} ok={ok} (active={ActiveCount})");
        }

        [ContextMenu("Debug: Release All")]
        public void DebugReleaseAll()
        {
            int before = ActiveCount;
            ReleaseAll();
            Debug.Log($"[FocusController] DEBUG release all: {before} → 0");
        }

        // ─── inner records ───────────────────────────────────────────

        private struct FocusRecord
        {
            public string FocusId;
            public Vector2 Center;
            public float Radius;
            public Pose Pose;
            public string Label;
            public float AnchoredAt;
        }
    }
}
