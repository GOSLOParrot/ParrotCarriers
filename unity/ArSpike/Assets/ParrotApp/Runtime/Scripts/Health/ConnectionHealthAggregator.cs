using System;
using UnityEngine;

namespace ParrotApp.Health
{
    /// <summary>
    /// IMPL_REF.md §4.2 producer 分工的具体宿主。
    ///
    /// <b>设计立场</b>：
    /// <list type="bullet">
    /// <item>每个字段只有一个 producer。多个 producer 抢写同一字段属于"漏抽象"反模式
    ///   （IMPL_REF.md §4.3 已警告）。</item>
    /// <item>本类只接受 <b>来自</b> producer 的报告（setters），<b>不主动</b>查询
    ///   <c>RoomManager.IsConnected</c> 等运行时状态。</item>
    /// <item><see cref="OnChanged"/> 在任何字段变化时触发；
    ///   <see cref="LifecycleHeartbeatPublisher"/> 用它驱动 <c>connection.health.changed</c>
    ///   事件 + 周期 EcpState 上报。</item>
    /// </list>
    ///
    /// <b>不要</b>把这个类做成 MonoBehaviour 单例。让 producer 通过依赖注入
    /// 拿到引用（<see cref="AppLifecycleManager"/> 持有一份，传给子组件）。
    /// </summary>
    public class ConnectionHealthAggregator
    {
        private ConnectionHealthState _state = ConnectionHealthState.Initial();

        public event Action<ConnectionHealthState> OnChanged;

        /// <summary>当前快照（结构体拷贝，调用方不能反向写）。</summary>
        public ConnectionHealthState Snapshot => _state;

        // ─── Room / signaling (producer: RoomManager) ─────────────────────

        public void ReportRoomConnected(bool connected, double nowUnix)
        {
            if (_state.RoomConnected == connected) return;
            _state.RoomConnected = connected;
            if (!connected) _state.LastDisconnectedAt = nowUnix;
            CommitChange(nowUnix);
        }

        public void ReportBrainPresent(bool present, double nowUnix)
        {
            if (_state.BrainPresent == present) return;
            _state.BrainPresent = present;
            CommitChange(nowUnix);
        }

        public void ReportReconnectAttempt(int newCount, double nowUnix)
        {
            if (_state.ReconnectAttemptCount == newCount) return;
            _state.ReconnectAttemptCount = newCount;
            CommitChange(nowUnix);
        }

        // ─── RPC / DataChannel (producer: ParrotRpcHandler / DataChannel users) ─

        public void ReportRpcReady(bool ready, double nowUnix)
        {
            if (_state.RpcReady == ready) return;
            _state.RpcReady = ready;
            CommitChange(nowUnix);
        }

        public void ReportDataChannelReady(bool ready, double nowUnix)
        {
            if (_state.DataChannelReady == ready) return;
            _state.DataChannelReady = ready;
            CommitChange(nowUnix);
        }

        // ─── Audio publish (producer: MicrophonePublisher) ────────────────

        public void ReportAudioPublishAttempt(double nowUnix)
        {
            if (_state.AudioPublishAttempted) return;
            _state.AudioPublishAttempted = true;
            CommitChange(nowUnix);
        }

        public void ReportAudioPublished(bool published, double nowUnix, string lastError = null)
        {
            bool changed = false;
            if (_state.AudioPublished != published) { _state.AudioPublished = published; changed = true; }
            if (lastError != null && _state.AudioLastError != lastError)
            { _state.AudioLastError = lastError; changed = true; }
            if (changed) CommitChange(nowUnix);
        }

        // ─── Video publish (producer: ARVideoPublisher) ───────────────────

        public void ReportVideoPublishAttempt(double nowUnix)
        {
            if (_state.VideoPublishAttempted) return;
            _state.VideoPublishAttempted = true;
            CommitChange(nowUnix);
        }

        public void ReportVideoPublished(bool published, double nowUnix)
        {
            if (_state.VideoPublished == published) return;
            _state.VideoPublished = published;
            CommitChange(nowUnix);
        }

        public void ReportVideoFirstFrame(double nowUnix)
        {
            if (_state.VideoFirstFrame) return;
            _state.VideoFirstFrame = true;
            _state.VideoFreshFrame = true;
            CommitChange(nowUnix);
        }

        /// <summary>frame fresh / stale 二态。stale 原因放 <see cref="ReportVideoLifecycleReason"/>。</summary>
        public void ReportVideoFreshFrame(bool fresh, double nowUnix)
        {
            if (_state.VideoFreshFrame == fresh) return;
            _state.VideoFreshFrame = fresh;
            CommitChange(nowUnix);
        }

        public void ReportVideoTier(string tier, double nowUnix)
        {
            if (_state.VideoTier == tier) return;
            _state.VideoTier = tier ?? "";
            CommitChange(nowUnix);
        }

        /// <summary>
        /// 区分 stale 原因：<c>paused_arcore</c> / <c>lifecycle_background</c> /
        /// <c>republishing</c> / <c>first_frame_timeout</c>。空字符串表示无降级原因。
        /// </summary>
        public void ReportVideoLifecycleReason(string reason, double nowUnix)
        {
            reason ??= "";
            if (_state.VideoLifecycleReason == reason) return;
            _state.VideoLifecycleReason = reason;
            CommitChange(nowUnix);
        }

        // ─── AR (producer: SceneProfileManager 或 ARLifecycleProbe) ──────

        public void ReportArTrackingState(string state, double nowUnix)
        {
            state ??= "";
            if (_state.ArTrackingState == state) return;
            _state.ArTrackingState = state;
            CommitChange(nowUnix);
        }

        // ─── 内部 ─────────────────────────────────────────────────────────

        private void CommitChange(double nowUnix)
        {
            var newOverall = ConnectionHealthState.ComputeOverall(_state);
            _state.Overall = newOverall;
            _state.LastStateChangeAt = nowUnix;

            // 内部一致性校验：spike 期 Editor 提示
            if (Application.isEditor)
            {
                if (_state.VideoFreshFrame && !_state.VideoFirstFrame)
                {
                    Debug.LogWarning(
                        "[ConnectionHealthAggregator] 不一致：VideoFreshFrame=true 但 VideoFirstFrame=false。" +
                        "首帧门 (IMPL_REF.md §4.2) 必须先翻 VideoFirstFrame。");
                }
            }

            OnChanged?.Invoke(_state);
        }
    }
}
