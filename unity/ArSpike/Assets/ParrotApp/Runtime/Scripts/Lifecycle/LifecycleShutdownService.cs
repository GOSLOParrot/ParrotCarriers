using System;
using System.Collections;
using System.Collections.Generic;
using System.Linq;
using ParrotApp.Health;
using ParrotApp.LiveKit;
using UnityEngine;

namespace ParrotApp.Lifecycle
{
    /// <summary>
    /// IMPL_REF.md §2 graceful shutdown chokepoint 的 Unity 端实现。
    ///
    /// <b>步骤（设计源：<c>livekit-unity-lifecycle/IMPL_REF.md §2.1</c>）</b>：
    /// <list type="number">
    /// <item>调所有 <see cref="IGracefulShutdownParticipant"/> 的 <c>UnpublishAndStop</c>
    ///   （按 <c>ShutdownOrder</c> 升序，视频先 / 音频后）。</item>
    /// <item><see cref="RoomManager.MarkIntentDisconnecting"/> 后调
    ///   <c>Room.Disconnect()</c>，<b>不</b>立即 Dispose。</item>
    /// <item>等 <c>Room.Disconnected</c> event 触发，<see cref="ParrotApp.Config.ParrotLifecycleConfig.T_DISCONNECT_WAIT_HARD"/>
    ///   软超时兜底（iOS 飞行模式 #90 可能根本不触发）。</item>
    /// <item>显式 <c>Room.Dispose()</c>（C# GC 不及时会让下次 Connect 抢占 identity）。</item>
    /// <item>cool-down <see cref="ParrotApp.Config.ParrotLifecycleConfig.T_SHUTDOWN_COOLDOWN"/>
    ///   秒，避免 30s ICE 残留。</item>
    /// <item><see cref="AppLifecycleManager.ReportDisconnected"/>，进 <c>Disconnected</c> 终态。</item>
    /// </list>
    ///
    /// <b>触发方式</b>：
    /// <list type="bullet">
    /// <item><c>OnApplicationQuit</c>：自动跑（同步等待，避免 Unity 进程在协程跑完前退出）。</item>
    /// <item><see cref="AppLifecycleManager.OnStateChanged"/> 进 <c>ShuttingDown</c>：自动跑。</item>
    /// <item><see cref="RequestShutdown"/>：手动入口（UI 退出按钮 / Editor 工具）。</item>
    /// </list>
    ///
    /// <b>不允许误读</b>：本协程<b>不</b>替代 lifecycle FSM；FSM 已经在
    /// <c>ShuttingDown</c> 时<b>本协程才能跑</b>。如果直接通过本类的
    /// <see cref="RequestShutdown"/> 触发，会先把 FSM 推到 <c>ShuttingDown</c> 再走协程。
    /// </summary>
    [RequireComponent(typeof(AppLifecycleManager))]
    public class LifecycleShutdownService : MonoBehaviour
    {
        [Tooltip("可选；为空时使用 RoomManager.Instance（singleton）")]
        [SerializeField] private RoomManager roomManager;

        [Tooltip("OnApplicationQuit 时自动触发 chokepoint。Editor 单元测试时可关掉。")]
        [SerializeField] private bool runOnApplicationQuit = true;

        private AppLifecycleManager _lifecycle;
        private bool _running;
        private static int s_syncDrainDepth;

        public static bool IsSynchronousQuitDrain => s_syncDrainDepth > 0;

        private static double UnixSeconds()
            => (DateTime.UtcNow - new DateTime(1970, 1, 1, 0, 0, 0, DateTimeKind.Utc)).TotalSeconds;

        private static float DrainDeltaSeconds()
            => s_syncDrainDepth > 0 ? 0.05f : Mathf.Max(Time.unscaledDeltaTime, 0.001f);

        protected virtual void Awake()
        {
            _lifecycle = GetComponent<AppLifecycleManager>();
        }

        protected virtual void OnEnable()
        {
            if (_lifecycle != null)
                _lifecycle.OnStateChanged += HandleLifecycleChanged;
        }

        protected virtual void OnDisable()
        {
            if (_lifecycle != null)
                _lifecycle.OnStateChanged -= HandleLifecycleChanged;
        }

        private void HandleLifecycleChanged(AppLifecycleState prev, AppLifecycleState next)
        {
            if (next == AppLifecycleState.ShuttingDown && !_running)
            {
                StartCoroutine(ChokepointCoroutine("lifecycle_state_changed"));
            }
        }

        /// <summary>
        /// 手动入口：先把 lifecycle 推到 <c>ShuttingDown</c>（这会自动触发
        /// <see cref="HandleLifecycleChanged"/> 启动协程；本方法是幂等保护）。
        /// </summary>
        public void RequestShutdown(string reason)
        {
            if (_running) return;
            // ReportShuttingDown 内部会触发 OnStateChanged，进而启动协程；
            // 但如果当前已经在 ShuttingDown，OnStateChanged 不会再 fire，
            // 所以这里兜底直接启动。
            if (_lifecycle.CurrentState == AppLifecycleState.ShuttingDown)
                StartCoroutine(ChokepointCoroutine(reason));
            else
                _lifecycle.ReportShuttingDown(reason);
        }

        /// <summary>
        /// OnApplicationQuit 路径：必须同步等到协程结束，否则 Unity 进程退出会
        /// 切断 SDK 内部清理。Unity 实际会等 <c>OnApplicationQuit</c> 同步部分跑完，
        /// 所以这里用阻塞 while 轮询协程状态而不是 yield。
        ///
        /// IMPL_REF.md §2.2 已知坑：<c>OnDestroy</c> 路径不可靠；必须走
        /// <c>OnApplicationQuit</c> 或显式 <c>RequestShutdown</c>。
        /// </summary>
        protected virtual void OnApplicationQuit()
        {
            if (!runOnApplicationQuit) return;
            if (_running) return;
            if (roomManager == null) roomManager = RoomManager.Instance;
            if (roomManager == null || roomManager.Room == null)
            {
                Debug.Log("[Shutdown] OnApplicationQuit: no active Room, nothing to do");
                return;
            }

            // Unity Player 在 OnApplicationQuit 后会立刻销毁 GameObject，
            // 协程可能跑不完。这里走 Run-to-completion：直接同步执行 IEnumerator。
            // 注意：IEnumerator 内部任何 WaitForSeconds 都会被 yield-return null
            // 等价化（同步阻塞），失去精确等待；这是预期妥协 —— 退出路径首要保证
            // Disconnect/Dispose 调到。
            try
            {
                Debug.Log("[Shutdown] OnApplicationQuit chokepoint (sync drain)");
                DrainCoroutine(ChokepointCoroutine("application_quit"));
            }
            catch (Exception ex)
            {
                Debug.LogWarning($"[Shutdown] OnApplicationQuit chokepoint threw: {ex.Message}");
            }
        }

        /// <summary>
        /// 同步驱动 IEnumerator：把 yield 全部当作 null 推进。
        /// 在 OnApplicationQuit 路径上避免 Unity 协程调度被中断。
        /// </summary>
        private static void DrainCoroutine(IEnumerator routine)
        {
            s_syncDrainDepth++;
            try
            {
                int safety = 100_000;
                while (routine.MoveNext() && --safety > 0)
                {
                    if (routine.Current is IEnumerator inner)
                        DrainCoroutine(inner);
                }
                if (safety <= 0)
                    Debug.LogError("[Shutdown] DrainCoroutine safety exhausted; possible infinite loop in shutdown participant");
            }
            finally
            {
                s_syncDrainDepth--;
            }
        }

        // ─── chokepoint 主协程 ────────────────────────────────────────────

        private IEnumerator ChokepointCoroutine(string reason)
        {
            if (_running) yield break;
            _running = true;
            Debug.Log($"[Shutdown] chokepoint start (reason={reason})");

            if (roomManager == null) roomManager = RoomManager.Instance;
            var config = _lifecycle != null ? _lifecycle.Config : null;

            float waitHard = config != null ? config.T_DISCONNECT_WAIT_HARD : 5f;
            float coolDown = config != null ? config.T_SHUTDOWN_COOLDOWN : 5f;

            // 步骤 1+2：让所有 publisher 自己 unpublish
            yield return DrainShutdownParticipants(reason);

            // 步骤 3：标记 intent，调 Room.Disconnect()
            if (roomManager != null && roomManager.Room != null)
            {
                roomManager.MarkIntentDisconnecting();

                // D5 修复：用 try/finally 包 += / -=，避免 Disconnect() 抛异常时
                // -= 漏跑导致每次 chokepoint 都 leak 一份 lambda 订阅。
                bool disconnectedFired = false;
                Action _ondc = () => { disconnectedFired = true; };
                roomManager.OnDisconnected += _ondc;

                float waited = 0f;
                try
                {
                    try
                    {
                        Debug.Log("[Shutdown] step 3: Room.Disconnect()");
                        roomManager.Room.Disconnect();
                    }
                    catch (Exception e)
                    {
                        Debug.LogWarning($"[Shutdown] Room.Disconnect threw: {e.Message}");
                    }

                    // 步骤 4：等 Disconnected event，硬超时兜底（iOS Issue #90）
                    while (!disconnectedFired && waited < waitHard)
                    {
                        yield return null;
                        waited += DrainDeltaSeconds();
                    }
                }
                finally
                {
                    roomManager.OnDisconnected -= _ondc;
                }
                Debug.Log($"[Shutdown] step 4: Disconnected event fired={disconnectedFired} (waited {waited:F2}s / {waitHard:F2}s)");

                // 步骤 5：显式 Dispose；C# GC 不及时会让下次 Connect 抢占 identity
                try
                {
                    if (roomManager.Room is IDisposable disposable)
                    {
                        disposable.Dispose();
                        Debug.Log("[Shutdown] step 5: Room.Dispose() done");
                    }
                    roomManager.CompleteChokepointDisconnect(reason);
                }
                catch (Exception e)
                {
                    Debug.LogWarning($"[Shutdown] Room.Dispose threw: {e.Message}");
                    roomManager.CompleteChokepointDisconnect($"dispose_failed:{reason}");
                }
            }
            else
            {
                Debug.Log("[Shutdown] step 3-5 skipped: no active Room");
            }

            // 步骤 6：cool-down
            Debug.Log($"[Shutdown] step 6: cool-down {coolDown:F2}s");
            float cd = 0f;
            while (cd < coolDown)
            {
                yield return null;
                cd += DrainDeltaSeconds();
            }

            // 步骤 7：终态 + 灌 health "全断"
            if (_lifecycle != null)
            {
                var now = UnixSeconds();
                _lifecycle.HealthAggregator?.ReportRoomConnected(false, now);
                _lifecycle.HealthAggregator?.ReportBrainPresent(false, now);
                _lifecycle.HealthAggregator?.ReportRpcReady(false, now);
                _lifecycle.HealthAggregator?.ReportDataChannelReady(false, now);

                _lifecycle.ReportDisconnected(reason);
            }

            Debug.Log($"[Shutdown] chokepoint done (reason={reason})");
            _running = false;
        }

        private IEnumerator DrainShutdownParticipants(string reason)
        {
            // 找所有 IGracefulShutdownParticipant；按 ShutdownOrder 升序
            // FindObjectsOfType 只返回 MonoBehaviour，OfType 过滤接口实现。
            var participants =
                FindObjectsOfType<MonoBehaviour>()
                    .OfType<IGracefulShutdownParticipant>()
                    .OrderBy(p => p.ShutdownOrder)
                    .ToList();

            if (participants.Count == 0)
            {
                Debug.Log("[Shutdown] step 1-2 skipped: no IGracefulShutdownParticipant in scene");
                yield break;
            }

            foreach (var p in participants)
            {
                IEnumerator routine = null;
                try { routine = p.UnpublishAndStop(reason); }
                catch (Exception ex)
                {
                    Debug.LogWarning($"[Shutdown] {p.GetType().Name}.UnpublishAndStop threw on enter: {ex.Message}");
                    continue;
                }
                if (routine == null) continue;

                // 不能 try/catch 包 yield；使用安全 stepper：单步推进 + 异常吞掉
                yield return SafeRun(routine, p.GetType().Name);
            }
        }

        private static IEnumerator SafeRun(IEnumerator routine, string label)
        {
            while (true)
            {
                bool moved;
                object current = null;
                try
                {
                    moved = routine.MoveNext();
                    if (moved) current = routine.Current;
                }
                catch (Exception ex)
                {
                    Debug.LogWarning($"[Shutdown] {label} threw mid-routine: {ex.Message}");
                    yield break;
                }
                if (!moved) yield break;
                yield return current;
            }
        }
    }
}
