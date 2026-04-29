using System.Collections;

namespace ParrotApp.Lifecycle
{
    /// <summary>
    /// 任何在 graceful shutdown chokepoint 时需要"先 unpublish 后 dispose"的组件
    /// 都实现本接口（典型：<c>ARVideoPublisher</c> / <c>MicrophonePublisher</c>）。
    ///
    /// <c>LifecycleShutdownService</c> 会按 <see cref="ShutdownOrder"/> 升序依次
    /// 等每个 participant 的 <see cref="UnpublishAndStop"/> 协程结束，再调
    /// <c>Room.Disconnect()</c>。
    ///
    /// <b>设计立场</b>：通过接口解耦，让 Group 2（chokepoint）不依赖 Group 3
    /// （publishers）的具体类型。Group 3 实现时只需 <c>: IGracefulShutdownParticipant</c>。
    /// 依据 <c>livekit-unity-lifecycle/IMPL_REF.md §2.1</c>。
    /// </summary>
    public interface IGracefulShutdownParticipant
    {
        /// <summary>越小越先执行；建议视频 = 10、音频 = 20、其他 = 100。</summary>
        int ShutdownOrder { get; }

        /// <summary>
        /// Unpublish 并停止本组件持有的 LiveKit 资源；返回 IEnumerator 让 chokepoint
        /// 可以 <c>yield return</c> 等待。<paramref name="reason"/> 用于日志，例如
        /// <c>"app_quit"</c> / <c>"long_background"</c>。
        ///
        /// 实现要求：
        /// <list type="bullet">
        /// <item>幂等：多次调用不应崩。</item>
        /// <item>有界：内部 yield 必须有超时保护（≤ 2s）；超时直接走完，
        ///   chokepoint 自己有 hard timeout 兜底。</item>
        /// <item>无副作用回灌：本协程内<b>不</b>再灌 ConnectionHealthAggregator
        ///   （chokepoint 完成后由 LifecycleShutdownService 统一灌"全断"快照）。</item>
        /// </list>
        /// </summary>
        IEnumerator UnpublishAndStop(string reason);
    }
}
