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
    /// Sprint4 Phase 4 W6-7 — BBox UI 状态机 + EcpEvent 出包。
    ///
    /// <b>UI 范围</b>（entry doc §8.1 L5 锁定）：
    /// <list type="bullet">
    /// <item>用户<b>显式</b>放置 BBox → reliable EcpEvent <c>bbox.placed</c></item>
    /// <item>用户显式移除 BBox → reliable EcpEvent <c>bbox.removed</c></item>
    /// <item><b>不发</b>拖动 lossy <c>parrot.ecp.tick</c>（W6-7 范围外，待 GOSLO 反馈
    ///   UI 设计完成后再 spec drag payload schema）</item>
    /// </list>
    ///
    /// <b>必须 ON/OFF 显式</b>（§8.1 L5）：本类不做"放着自动 ON"——
    /// API 调用方（手势 / 屏幕拖框 / 测试 ContextMenu）自己决定何时 Place / Remove。
    ///
    /// <b>bbox_id 生成</b>：<c>bb_&lt;guid8&gt;</c>。Brain 端
    /// <c>parrot/brain/observer/bbox.py</c> 用 bbox_id 索引 RefBinding，
    /// <c>parrot/dsg/attention/threshold.py</c> 用 bbox_id 作 _targets key
    /// （compound key <c>bbox:&lt;id&gt;</c>），所以 bbox_id 必须稳定（不要每次
    /// publish 都换）。
    ///
    /// <b>Reconnect 行为</b>（§B.6 — Brain 管线切换 / 网络瞬断同型）：
    /// 订阅 <see cref="RoomManager.OnConnected"/>，在 reconnect 时把当前所有
    /// ON 的 BBox <b>全量重 publish</b>。Brain 端 <c>refs.bind_bbox</c> 是幂等
    /// 的（同 bbox_id 命中既存 Ref → 不创建重复），所以重发安全。
    ///
    /// <b>不做（与 §3.7 Observer/Attention 边界一致 + audit defended）</b>：
    /// <list type="bullet">
    /// <item>不在 Unity 端做 attention 数学（Δ / threshold 全在 Brain
    ///   <c>dsg/attention/threshold.py</c>）</item>
    /// <item>不发 dsg.observer.sighting EcpEvent（那是 identify_object 路径，
    ///   工具 ②；本类只管 BBox UI artifact 生命周期）</item>
    /// <item>不持久化 BBox 跨 session（关 App = 用户的"我不感兴趣了"信号；
    ///   §3.7 + threshold.py docstring）</item>
    /// </list>
    /// </summary>
    public class BBoxController : MonoBehaviour
    {
        [Tooltip("Echo 出包用；空时 Awake 时 Find。")]
        [SerializeField] private EcpEventPublisher publisher;

        [Tooltip("RoomManager 用于订阅 OnConnected 触发 reconnect 重 publish；空时 Awake 时 Find。")]
        [SerializeField] private RoomManager roomManager;

        public static BBoxController Instance { get; private set; }

        // 当前 ON 的 BBox。key = bbox_id；reconnect 时整体重发。
        private readonly Dictionary<string, BBoxRecord> _active = new();

        public int ActiveCount => _active.Count;

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
        /// 用户主动放置一个 BBox。corners 是屏幕空间或 AR 平面坐标，由 caller 决定语义；
        /// pose 是 AR 世界坐标的 anchor pose（可空，传 <see cref="Pose.identity"/>）。
        /// 返回生成的 <c>bbox_id</c>（caller 可用它后续 <see cref="RemoveBBox"/>）。
        /// </summary>
        public string PlaceBBox(Vector2[] corners, Pose pose, string label = "")
        {
            string id = GenerateBboxId();
            var record = new BBoxRecord
            {
                BboxId = id,
                Corners = corners ?? Array.Empty<Vector2>(),
                Pose = pose,
                Label = label ?? "",
                PlacedAt = Time.realtimeSinceStartup,
            };
            _active[id] = record;
            PublishPlaced(record);
            return id;
        }

        /// <summary>
        /// 移除一个 BBox。返回 true = 找到并移除；false = 不存在该 id。
        /// </summary>
        public bool RemoveBBox(string bboxId)
        {
            if (string.IsNullOrEmpty(bboxId)) return false;
            if (!_active.TryGetValue(bboxId, out var record)) return false;
            _active.Remove(bboxId);
            PublishRemoved(record);
            return true;
        }

        /// <summary>清空所有当前 ON 的 BBox（每个发独立 removed 事件）。</summary>
        public void RemoveAll()
        {
            // ToArray 避免修改时迭代异常
            var ids = new List<string>(_active.Keys);
            foreach (var id in ids) RemoveBBox(id);
        }

        // ─── reconnect re-publish (§B.6) ─────────────────────────────

        private void OnRoomConnected()
        {
            if (_active.Count == 0) return;
            Debug.Log($"[BBoxController] Room connected — re-publishing {_active.Count} ON bbox(es)");
            foreach (var record in _active.Values)
            {
                PublishPlaced(record);
            }
        }

        // ─── publish helpers ─────────────────────────────────────────

        private void PublishPlaced(BBoxRecord r)
        {
            if (publisher == null)
            {
                Debug.LogWarning("[BBoxController] No EcpEventPublisher — bbox.placed dropped");
                return;
            }
            string payload = BuildPlacedPayload(r);
            publisher.PublishUnityEvent(EcpEventTypeNames.BboxPlaced, payload);
        }

        private void PublishRemoved(BBoxRecord r)
        {
            if (publisher == null)
            {
                Debug.LogWarning("[BBoxController] No EcpEventPublisher — bbox.removed dropped");
                return;
            }
            string payload = "{\"bbox_id\":" + Quote(r.BboxId) + "}";
            publisher.PublishUnityEvent(EcpEventTypeNames.BboxRemoved, payload);
        }

        private static string BuildPlacedPayload(BBoxRecord r)
        {
            var ci = CultureInfo.InvariantCulture;
            var sb = new StringBuilder(256);
            sb.Append("{");
            sb.Append("\"bbox_id\":").Append(Quote(r.BboxId)).Append(',');
            sb.Append("\"corners\":[");
            for (int i = 0; i < r.Corners.Length; i++)
            {
                if (i > 0) sb.Append(',');
                sb.Append('[').Append(r.Corners[i].x.ToString("R", ci))
                  .Append(',').Append(r.Corners[i].y.ToString("R", ci)).Append(']');
            }
            sb.Append("],");
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

        private static string GenerateBboxId()
        {
            // bb_<guid8> — Brain 端 observer/bbox.py / threshold.py 用 bbox_id
            // 索引 RefBinding 与 _targets。8 hex 已够 spike 期不碰撞。
            string g = Guid.NewGuid().ToString("N").Substring(0, 8);
            return "bb_" + g;
        }

        // ─── Editor smoke 入口 ───────────────────────────────────────

        [ContextMenu("Debug: Place Test BBox")]
        public void DebugPlaceTestBBox()
        {
            var corners = new[]
            {
                new Vector2(0.2f, 0.3f),
                new Vector2(0.8f, 0.7f),
            };
            var pose = new Pose(new Vector3(0f, 1f, 0.5f), Quaternion.identity);
            string id = PlaceBBox(corners, pose, label: "test_bbox");
            Debug.Log($"[BBoxController] DEBUG placed bbox_id={id} (active={ActiveCount})");
        }

        [ContextMenu("Debug: Remove Last BBox")]
        public void DebugRemoveLastBBox()
        {
            if (_active.Count == 0)
            {
                Debug.Log("[BBoxController] DEBUG remove last: no active BBox");
                return;
            }
            // Dictionary 没顺序保证，spike 期取任意一个就行
            string anyId = "";
            foreach (var k in _active.Keys) { anyId = k; break; }
            bool ok = RemoveBBox(anyId);
            Debug.Log($"[BBoxController] DEBUG removed bbox_id={anyId} ok={ok} (active={ActiveCount})");
        }

        [ContextMenu("Debug: Remove All")]
        public void DebugRemoveAll()
        {
            int before = ActiveCount;
            RemoveAll();
            Debug.Log($"[BBoxController] DEBUG remove all: {before} → 0");
        }

        // ─── inner records ───────────────────────────────────────────

        private struct BBoxRecord
        {
            public string BboxId;
            public Vector2[] Corners;
            public Pose Pose;
            public string Label;
            public float PlacedAt;
        }
    }
}
