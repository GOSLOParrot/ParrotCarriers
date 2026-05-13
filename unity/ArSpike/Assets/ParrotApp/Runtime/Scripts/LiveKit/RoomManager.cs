using System;
using System.Collections;
using System.Collections.Generic;
using System.IO;
using LiveKit;
using UnityEngine;

namespace ParrotApp.LiveKit
{
    /// <summary>
    /// Manages LiveKit Room lifecycle for the ArSpike production app skeleton.
    ///
    /// <b>从 ParrotDev 搬迁 (Sprint4 Phase 3 / L3 Group 1)</b>。差异：
    /// <list type="bullet">
    /// <item>命名空间收口为 <c>ParrotApp.LiveKit</c>，与其他 ParrotApp 组件一致。</item>
    /// <item>新增 <c>OnConnecting</c> / <c>OnParticipantConnected</c> /
    ///   <c>OnParticipantDisconnected</c> 三个 event，给
    ///   <c>RoomManagerLifecycleBridge</c> 用来灌
    ///   <see cref="ParrotApp.Health.ConnectionHealthAggregator"/>
    ///   的 <c>brain_present</c> / <c>reconnect_attempt_count</c> 等字段。</item>
    /// <item>新增 <c>IsDisconnecting</c> flag + <see cref="MarkIntentDisconnecting"/>
    ///   方法，让 <c>LifecycleShutdownService</c> 显式标记"主动断"，避免
    ///   <c>Room.Disconnected</c> event 路径误把 graceful 当成被动失联。
    ///   见 <c>livekit-unity-lifecycle/IMPL_REF.md §1.1 / §9</c>。</item>
    /// <item>移除 <c>TriggerGreetingAfterDelay</c>（Sprint3 <c>onSceneReady</c> 灰盒；
    ///   ECP 化的 brain handshake 是 Phase 4 工作）。</item>
    /// <item>移除 <c>StartEditorReconnectTest</c>（测试束菜单，不进产品）。</item>
    /// <item>保留 <see cref="DisconnectForTesting"/> 与
    ///   <see cref="ReconnectUsingCachedCredentials"/>，作为 Editor 单场景调试入口；
    ///   <b>不</b>替代 <see cref="MarkIntentDisconnecting"/>+graceful chokepoint。</item>
    /// </list>
    ///
    /// <b>不允许误读（与锚点 sprint4_phase3_l3_entry_20260429.md §0 一致）</b>：
    /// <list type="bullet">
    /// <item>本类<b>不</b>实现 graceful shutdown chokepoint。chokepoint 协程在
    ///   <c>LifecycleShutdownService</c>，由 Group 2 落地。</item>
    /// <item>本类<b>不</b>暴露 lifecycle FSM 状态给后端 BT；后端通过 EcpState 感知。</item>
    /// </list>
    /// </summary>
    public class RoomManager : MonoBehaviour
    {
        [Header("LiveKit Connection")]
        [Tooltip("LiveKit server URL. Local dev: ws://localhost:7880")]
        [SerializeField] private string serverUrl = "ws://localhost:7880";

        [Tooltip("JWT join token — generate with src/scripts/generate_token.py")]
        [SerializeField] private string joinToken = "";

        [Tooltip(
            "Auto-connect on Start() using the inspector/file token.\n" +
            "Set to FALSE in production scenes — UI / token gate calls Connect() after fetching a fresh token.\n" +
            "Leave TRUE in single-scene spike testing only.")]
        [SerializeField] private bool autoConnectOnStart = false;

        [Tooltip("Editor 调试：spike 期允许从 ../unity_join_token.txt 读 token，避免在场景里手贴。" +
                 "正式 build 应通过 Connect(token) 注入。")]
        [SerializeField] private bool allowEditorTokenFile = true;

        public Room Room { get; private set; }
        public bool IsConnected { get; private set; }

        /// <summary>
        /// chokepoint 协程进入 graceful shutdown 时显式置 true。
        /// <see cref="Room.Disconnected"/> event 路径根据本 flag 区分主动 vs 被动。
        /// </summary>
        public bool IsDisconnecting { get; private set; }

        /// <summary>
        /// 当前 <see cref="ConnectToRoom"/> 协程引用（R1 重入锁）。同一时刻只允许一份在跑：
        /// <list type="bullet">
        /// <item>UI/token 连点两次会让两份协程并行 <c>Room.Disconnect()</c> +
        ///   <c>new Room()</c>，互相把 <c>Room</c> 字段抢掉，最后
        ///   <c>Room.LocalParticipant</c> 不可预期。</item>
        /// <item>Sprint3 <c>brain_connected_black_video_20260425.md</c> 是同根因。</item>
        /// </list>
        /// 进入 <see cref="Connect"/> 时如果非 <c>null</c>，先 <c>StopCoroutine</c> 再启新一份。
        /// </summary>
        private Coroutine _connecting;

        /// <summary>本地参与者 identity（连接成功后）。</summary>
        public string JoinIdentity =>
            Room?.LocalParticipant?.Identity ?? "";

        /// <summary>Room 名（连接成功后）。</summary>
        public string RoomName => Room?.Name ?? "";

        public static RoomManager Instance { get; private set; }
        private readonly Dictionary<string, AudioStream> _remoteAudioStreams = new();

        /// <summary>Seconds for the last successful <see cref="ConnectToRoom"/>。</summary>
        public float? LastConnectDurationSeconds { get; private set; }

        /// <summary>
        /// 即将调用 <c>Room.Connect</c>。Bridge 用本事件把
        /// <see cref="ParrotApp.Lifecycle.AppLifecycleManager"/>
        /// 推到 <c>Connecting</c>。
        /// </summary>
        public event Action OnConnecting;

        /// <summary><c>Room.Connect</c> 成功后。</summary>
        public event Action OnConnected;

        /// <summary><c>Room.Disconnected</c> event 触发后。</summary>
        public event Action OnDisconnected;

        /// <summary>
        /// 远端参与者加入；Bridge 监听用于检测 <c>brain_present</c>（agent-* identity）。
        /// </summary>
        public event Action<RemoteParticipant> OnParticipantConnected;

        /// <summary>远端参与者离开；同上。</summary>
        public event Action<RemoteParticipant> OnParticipantDisconnected;

        void Awake()
        {
            if (Instance != null && Instance != this)
            {
                // ArSpike 期暂时容许重复，让多场景挂载不破坏现有 publishers / Bridge。
                // 多余实例只销毁 component，不动 GameObject。
                Destroy(this);
                return;
            }
            Instance = this;
            DontDestroyOnLoad(gameObject);
        }

        void Start()
        {
            if (!autoConnectOnStart)
            {
                Debug.Log("[RoomManager] autoConnectOnStart=false — waiting for Connect()");
                return;
            }

            if (string.IsNullOrWhiteSpace(joinToken) && allowEditorTokenFile)
                TryLoadTokenFromArSpikeFile();

            if (!string.IsNullOrWhiteSpace(joinToken))
            {
                Debug.Log($"[RoomManager] Join token length={joinToken.Length}, connecting...");
                StartConnect("auto_start");
            }
            else
            {
                Debug.LogWarning(
                    "[RoomManager] No token. Run: python src/scripts/generate_token.py "
                    + "(writes unity_join_token.txt at the project root) or paste JWT into Inspector.");
            }
        }

        /// <summary>
        /// Editor 单场景联调：与 <c>generate_token.py</c> 默认输出路径对齐。
        /// 仅当 <see cref="allowEditorTokenFile"/> 为 true 时使用；正式 build 应注入。
        /// </summary>
        private void TryLoadTokenFromArSpikeFile()
        {
            try
            {
                // Application.dataPath = .../ArSpike/Assets → 上级为 ArSpike 工程根
                var path = Path.GetFullPath(Path.Combine(Application.dataPath, "..", "unity_join_token.txt"));
                if (!File.Exists(path)) return;

                var t = File.ReadAllText(path).Trim();
                if (string.IsNullOrEmpty(t)) return;

                joinToken = t;
                Debug.Log($"[RoomManager] Loaded join token from file ({t.Length} chars): {path}");
            }
            catch (Exception e)
            {
                Debug.LogWarning($"[RoomManager] Could not read unity_join_token.txt: {e.Message}");
            }
        }

        /// <summary>
        /// 调用方：UI / token gate；运行时使用新 token 触发连接。
        ///
        /// <b>R1 重入锁</b>：如果已有一份 <see cref="ConnectToRoom"/> 在跑，先停掉再启新一份；
        /// 不会让两份协程并行抢 <c>Room</c> 字段。<br/>
        /// <b>R2 shutdown 拦截</b>：<see cref="IsDisconnecting"/> 为 true 时
        /// （chokepoint 协程进行中）拒绝新连接，避免半路打穿 cool-down。
        /// </summary>
        public void Connect(string token, string url = null)
        {
            if (IsDisconnecting)
            {
                Debug.LogWarning(
                    "[RoomManager] Connect rejected: chokepoint shutdown in progress. " +
                    "Wait for AppLifecycleState=Disconnected before reconnecting.");
                return;
            }

            joinToken = token;
            if (!string.IsNullOrEmpty(url)) serverUrl = url;
            StartConnect("Connect(token)");
        }

        /// <summary>R1 重入锁实现：旧协程若在跑就停掉，再启新一份。</summary>
        private void StartConnect(string reason)
        {
            if (_connecting != null)
            {
                Debug.LogWarning(
                    $"[RoomManager] StartConnect({reason}) ignored: ConnectToRoom is already in flight. " +
                    "Wait for OnConnected/OnDisconnected before starting another connection.");
                return;
            }
            _connecting = StartCoroutine(ConnectToRoom());
        }

        /// <summary>
        /// chokepoint 入口的标记 setter。<see cref="LifecycleShutdownService"/> 在
        /// 调 <c>Room.Disconnect()</c> 前必须先调本方法，标记"主动断"。
        /// 本方法只翻 flag，不实际断开；断开走 chokepoint 协程。
        /// </summary>
        public void MarkIntentDisconnecting()
        {
            IsDisconnecting = true;
        }

        /// <summary>
        /// Finalizes the graceful shutdown chokepoint after Disconnect and Dispose.
        ///
        /// RoomManager owns the Room reference, so the shutdown service calls back
        /// here once it has waited for Disconnected and disposed the SDK object.
        /// This keeps the next START/reconnect from seeing a stale Room or a
        /// permanently true <see cref="IsDisconnecting"/> flag.
        /// </summary>
        public void CompleteChokepointDisconnect(string reason)
        {
            ClearRemoteAudioStreams($"chokepoint_complete:{reason}");
            Room = null;
            IsConnected = false;
            IsDisconnecting = false;
            _connecting = null;
            Debug.Log($"[RoomManager] chokepoint ownership cleared (reason={reason})");
        }

        /// <summary>
        /// Editor 单场景调试入口：直接调 <c>Room.Disconnect()</c>，<b>不走 chokepoint</b>。
        /// 正式断开必须走 <c>LifecycleShutdownService</c>。
        /// </summary>
        public void DisconnectForTesting()
        {
            if (Room == null)
            {
                Debug.Log("[RoomManager] DisconnectForTesting: no active Room");
                return;
            }

            try
            {
                Debug.Log("[RoomManager] DisconnectForTesting (bypasses chokepoint)");
                Room.Disconnect();
            }
            catch (Exception e)
            {
                Debug.LogWarning($"[RoomManager] DisconnectForTesting: {e.Message}");
            }
        }

        /// <summary>用当前 <c>joinToken</c> 重新连接（Editor 调试）。</summary>
        public void ReconnectUsingCachedCredentials()
        {
            if (IsDisconnecting)
            {
                Debug.LogWarning(
                    "[RoomManager] Reconnect rejected: chokepoint shutdown in progress (R2)");
                return;
            }
            if (string.IsNullOrWhiteSpace(joinToken))
            {
                Debug.LogWarning(
                    "[RoomManager] Reconnect skipped — no joinToken.");
                return;
            }
            StartConnect("ReconnectUsingCachedCredentials");
        }

        private IEnumerator ConnectToRoom()
        {
            var t0 = Time.realtimeSinceStartup;
            LastConnectDurationSeconds = null;

            // 重连场景：清掉 IsDisconnecting，否则 Bridge 会把这次的 Disconnected 误判为 graceful
            IsDisconnecting = false;

            if (Room != null)
            {
                if (IsConnected)
                {
                    Debug.LogWarning(
                        "[RoomManager] Connect rejected: an active Room already exists. " +
                        "Use LifecycleShutdownService before joining a different room.");
                    _connecting = null;
                    yield break;
                }

                // The previous Room is already disconnected or failed to connect.
                // Do not call Room.Disconnect here; active disconnects must pass
                // through LifecycleShutdownService so unpublish, Disconnected wait,
                // Dispose, and cooldown stay ordered.
                Debug.Log("[RoomManager] Disposing stale disconnected Room before fresh connect");
                ClearRemoteAudioStreams("dispose_stale_room");
                try { (Room as IDisposable)?.Dispose(); }
                catch (Exception e) { Debug.LogWarning($"[RoomManager] Dispose stale room: {e.Message}"); }
                Room = null;
                IsConnected = false;
                yield return null;
            }

            try { OnConnecting?.Invoke(); }
            catch (Exception ex) { Debug.LogWarning($"[RoomManager] OnConnecting listener threw: {ex.Message}"); }

            Room = new Room();

            Room.TrackSubscribed += OnTrackSubscribed;
            Room.ParticipantConnected += p =>
            {
                Debug.Log($"[RoomManager] + {p.Identity}");
                if (p is RemoteParticipant rp)
                    try { OnParticipantConnected?.Invoke(rp); }
                    catch (Exception ex) { Debug.LogWarning($"[RoomManager] OnParticipantConnected threw: {ex.Message}"); }
            };
            Room.ParticipantDisconnected += p =>
            {
                Debug.Log($"[RoomManager] - {p.Identity}");
                if (p is RemoteParticipant rp)
                    try { OnParticipantDisconnected?.Invoke(rp); }
                    catch (Exception ex) { Debug.LogWarning($"[RoomManager] OnParticipantDisconnected threw: {ex.Message}"); }
            };
            Room.Disconnected += _ =>
            {
                Debug.Log($"[RoomManager] Disconnected (intent={IsDisconnecting})");
                IsConnected = false;
                ClearRemoteAudioStreams("room_disconnected");
                try { OnDisconnected?.Invoke(); }
                catch (Exception ex) { Debug.LogWarning($"[RoomManager] OnDisconnected listener threw: {ex.Message}"); }
            };

            Debug.Log($"[RoomManager] Connecting to {serverUrl} ...");
            var connect = Room.Connect(serverUrl, joinToken, new RoomOptions());
            yield return connect;

            if (connect.IsError)
            {
                Debug.LogError(
                    "[RoomManager] Connection failed (check: LiveKit on :7880, token not expired, Brain worker registered).");
                LastConnectDurationSeconds = null;
                try { (Room as IDisposable)?.Dispose(); }
                catch (Exception e) { Debug.LogWarning($"[RoomManager] Dispose failed Room: {e.Message}"); }
                Room = null;
                IsConnected = false;
                _connecting = null;
                yield break;
            }

            LastConnectDurationSeconds = Time.realtimeSinceStartup - t0;
            Debug.Log(
                $"[RoomManager] Connected — room='{Room.Name}' identity='{Room.LocalParticipant.Identity}' "
                + $"(connect {LastConnectDurationSeconds:F2}s)");
            IsConnected = true;

            try { OnConnected?.Invoke(); }
            catch (Exception ex) { Debug.LogWarning($"[RoomManager] OnConnected listener threw: {ex.Message}"); }

            // R1: 协程跑完，清空重入锁。失败/yield break 路径不会到这一行，但 StartConnect
            // 进入时会 StopCoroutine + 覆盖，所以 leak 受控。
            _connecting = null;
        }

        private void OnTrackSubscribed(
            IRemoteTrack track,
            RemoteTrackPublication publication,
            RemoteParticipant participant)
        {
            if (track is RemoteAudioTrack audioTrack)
            {
                Debug.Log($"[RoomManager] Audio track from {participant.Identity}");
                var key = $"{participant.Identity}:{publication.Sid}";
                if (_remoteAudioStreams.ContainsKey(key))
                {
                    Debug.Log($"[RoomManager] Audio stream already exists for {key}");
                    return;
                }

                var go = new GameObject($"Audio_{key}");
                go.transform.SetParent(transform);
                var source = go.AddComponent<AudioSource>();
                source.spatialBlend = 0f;
                source.playOnAwake = false;

                // 强引用：避免 Mono GC 在远端 track 仍订阅时回收 AudioStream，
                // 否则真机会随机断流 (Sprint3 已踩)。
                _remoteAudioStreams[key] = new AudioStream(audioTrack, source);
            }
        }

        private void ClearRemoteAudioStreams(string reason)
        {
            foreach (var kv in _remoteAudioStreams)
            {
                try { kv.Value.Dispose(); }
                catch (Exception e)
                {
                    Debug.LogWarning($"[RoomManager] Dispose audio stream {kv.Key} failed ({reason}): {e.Message}");
                }
            }
            _remoteAudioStreams.Clear();

            for (int i = transform.childCount - 1; i >= 0; i--)
            {
                var child = transform.GetChild(i);
                if (child.name.StartsWith("Audio_", StringComparison.Ordinal))
                    Destroy(child.gameObject);
            }
        }

        void OnDestroy()
        {
            ClearRemoteAudioStreams("destroy");

            // 真正 graceful 关闭走 LifecycleShutdownService。
            // OnDestroy 路径无法保证 SDK 协程跑完（IMPL_REF.md §2 已知坑），
            // 但仍要尽力 Dispose —— Editor 脚本重编译 / scene 切换不会走 OnApplicationQuit。
            // R6: 不显式 Dispose 时 C# GC 不及时，下次 Connect 同 identity 会被服务端拒。
            try { Room?.Disconnect(); }
            catch (Exception e) { Debug.LogWarning($"[RoomManager] OnDestroy Disconnect threw: {e.Message}"); }
            try { (Room as IDisposable)?.Dispose(); }
            catch (Exception e) { Debug.LogWarning($"[RoomManager] OnDestroy Dispose threw: {e.Message}"); }

            Room = null;
            if (Instance == this) Instance = null;
        }
    }
}
