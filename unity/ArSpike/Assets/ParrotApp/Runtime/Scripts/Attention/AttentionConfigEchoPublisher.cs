using ParrotApp.Config;
using ParrotApp.Ecp;
using ParrotApp.LiveKit;
using UnityEngine;

namespace ParrotApp.Attention
{
    /// <summary>
    /// Sprint4 Phase 4 W6-7 — F-05 Echo path Unity 半边。
    ///
    /// 在 <see cref="RoomManager.OnConnected"/>（含 reconnect / Brain 管线切换 — §B.6）
    /// 时把 <see cref="ParrotAttentionConfig"/> 的当前值通过 EcpEvent
    /// <c>attention.config.echo</c> 发到 Brain；Brain 端 <c>attention_config_handler</c>
    /// 写 BB <c>global/attention_thresholds</c>。
    ///
    /// <b>F-05 prerequisite chain</b>（参考 <see cref="ParrotAttentionConfig"/> 类注释）：
    /// 本类 + Brain 端 <c>attention_config_handler.py</c> 完成 ① + ②。
    /// FocusBboxThreshold 读 BB（③）留给 Brain 后续 chat。
    ///
    /// <b>触发清单</b>：
    /// <list type="bullet">
    /// <item>RoomManager.OnConnected → EchoNow()（reconnect / pipeline switch 必发）</item>
    /// <item>ContextMenu <c>Debug: Echo Now</c> → 兜底（Inspector 改 SO 后手动同步）</item>
    /// </list>
    ///
    /// <b>不做</b>：
    /// <list type="bullet">
    /// <item>不监听 SO 的 <c>OnValidate</c> 自动 publish — Editor live-edit 不是
    ///   spike 主路径，自动发会让 reconnect 路径产生重复风暴</item>
    /// <item>不做 dedup（reliable transport + Brain 60s window 足够；reconnect
    ///   超 60s 是设计行为）</item>
    /// </list>
    /// </summary>
    public class AttentionConfigEchoPublisher : MonoBehaviour
    {
        [Tooltip("阈值菜单 SO（必传）。Inspector 拖入或 spike 期通过 SetConfig 注入。")]
        [SerializeField] private ParrotAttentionConfig config;

        [Tooltip("Echo 出包用；空时 Awake 时 Find。")]
        [SerializeField] private EcpEventPublisher publisher;

        [Tooltip("RoomManager 用于订阅 OnConnected；空时 Awake 时 Find。")]
        [SerializeField] private RoomManager roomManager;

        public int EchoCount { get; private set; }

        void Awake()
        {
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
                if (roomManager.IsConnected)
                {
                    EchoNow();
                }
            }
        }

        void OnDestroy()
        {
            if (roomManager != null) roomManager.OnConnected -= OnRoomConnected;
        }

        public void SetConfig(ParrotAttentionConfig c) => config = c;

        private void OnRoomConnected()
        {
            EchoNow();
        }

        /// <summary>立即把当前 SO 值 publish 一次。room 不可用时仍走 publisher 的 dropped 路径。</summary>
        [ContextMenu("Debug: Echo Now")]
        public void EchoNow()
        {
            if (config == null)
            {
                Debug.LogWarning(
                    "[AttentionConfigEchoPublisher] No ParrotAttentionConfig assigned — Echo skipped");
                return;
            }
            if (publisher == null)
            {
                Debug.LogWarning(
                    "[AttentionConfigEchoPublisher] No EcpEventPublisher — Echo skipped");
                return;
            }
            string payload = config.ToWireJson();
            bool sent = publisher.PublishUnityEvent(EcpEventTypeNames.AttentionConfigEcho, payload);
            if (sent) EchoCount++;
            Debug.Log($"[AttentionConfigEchoPublisher] EchoNow sent={sent} payload={payload}");
        }
    }
}
