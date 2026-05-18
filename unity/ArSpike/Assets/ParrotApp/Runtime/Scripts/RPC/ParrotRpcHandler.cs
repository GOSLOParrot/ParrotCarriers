using System;
using System.Threading.Tasks;
using LiveKit;
using ParrotApp.Core;
using ParrotApp.Ecp;
using ParrotApp.Hands;
using ParrotApp.Health;
using ParrotApp.Lifecycle;
using ParrotApp.LiveKit;
using ParrotApp.Parrot;
using UnityEngine;

namespace ParrotApp.RPC
{
    /// <summary>
    /// Registers RPC methods that the Brain Agent calls via <c>_rpc_bridge.py</c>:
    ///   <c>flyTo</c> -> <see cref="ParrotController.FlyTo"/>
    ///   <c>animate</c> -> <see cref="ParrotController.PlayAnimation"/>
    ///   <c>perchToFinger</c> -> <see cref="PerchOnHand.TryRequestRpcPerch"/>
    ///   <c>returnToView</c> -> <see cref="PerchOnHand.TryRequestReturnToView"/>
    ///
    /// 从 ParrotDev 搬迁（Sprint4 Phase 3 / L3 Group 4），保留 ECP-minimal 已落地的所有行为：
    /// <list type="bullet">
    /// <item><c>expires_at</c> 校验 → <see cref="EcpAckJson.Expired"/>。</item>
    /// <item><c>active_locks=["body"]</c> 在 <see cref="EcpAckJson.Completed"/> 中。</item>
    /// <item>异常路径走 <see cref="EcpAckJson.Failed"/>。</item>
    /// </list>
    /// 增量：
    /// <list type="bullet">
    /// <item>命名空间收口为 <c>ParrotApp.RPC</c>。</item>
    /// <item>本类是 <c>rpc_ready</c> 的<b>唯一</b> producer（IMPL_REF.md §4.2）：
    ///   两个 RegisterRpcMethod 都成功后灌 <see cref="ConnectionHealthAggregator.ReportRpcReady"/>。</item>
    /// </list>
    ///
    /// 挂载：与 <see cref="ParrotController"/> 同 GameObject。
    /// </summary>
    [RequireComponent(typeof(ParrotController))]
    public class ParrotRpcHandler : MonoBehaviour
    {
        [Tooltip("可选；为空时 FindObjectOfType。用于灌 rpc_ready。")]
        [SerializeField] private AppLifecycleManager lifecycleManager;

        private ParrotController _parrot;
        private Room _rpcRegisteredOnRoom;
        private bool _rpcReadyReported;

        private ConnectionHealthAggregator HealthAggregator =>
            lifecycleManager != null ? lifecycleManager.HealthAggregator : null;

        void Awake()
        {
            _parrot = GetComponent<ParrotController>();
        }

        void Start()
        {
            if (lifecycleManager == null)
                lifecycleManager = FindObjectOfType<AppLifecycleManager>();

            var rm = RoomManager.Instance;
            if (rm == null)
            {
                Debug.LogError("[ParrotRPC] RoomManager not found");
                return;
            }

            rm.OnConnected += Register;
            rm.OnDisconnected += OnRoomDisconnected;
            if (rm.IsConnected) Register();
        }

        private void Register()
        {
            var room = RoomManager.Instance?.Room;
            if (room == null) return;
            if (_rpcRegisteredOnRoom == room) return;

            try
            {
                room.LocalParticipant.RegisterRpcMethod("flyTo", HandleFlyTo);
                room.LocalParticipant.RegisterRpcMethod("animate", HandleAnimate);
                room.LocalParticipant.RegisterRpcMethod("perchToFinger", HandlePerchToFinger);
                room.LocalParticipant.RegisterRpcMethod("returnToView", HandleReturnToView);
                _rpcRegisteredOnRoom = room;
                Debug.Log("[ParrotRPC] Registered: flyTo, animate, perchToFinger, returnToView");

                if (!_rpcReadyReported)
                {
                    _rpcReadyReported = true;
                    HealthAggregator?.ReportRpcReady(true, UnixSeconds());
                }
            }
            catch (Exception ex)
            {
                _rpcRegisteredOnRoom = null;
                _rpcReadyReported = false;
                Debug.LogError($"[ParrotRPC] RegisterRpcMethod failed: {ex.Message}");
                HealthAggregator?.ReportRpcReady(false, UnixSeconds());
            }
        }

        private void OnRoomDisconnected()
        {
            _rpcRegisteredOnRoom = null;
            if (_rpcReadyReported)
            {
                _rpcReadyReported = false;
                HealthAggregator?.ReportRpcReady(false, UnixSeconds());
            }
        }

        private async Task<string> HandleFlyTo(RpcInvocationData data)
        {
            Debug.Log($"[ParrotRPC] flyTo <- {data.CallerIdentity}: {data.Payload}");
            FlyToPayload p = default;
            string commandId = "";
            bool reported = false;
            try
            {
                p = JsonUtility.FromJson<FlyToPayload>(data.Payload);

                if (p._ecp != null && p._ecp.IsExpired(EcpAckJson.UnixSeconds()))
                {
                    Debug.LogWarning($"[ParrotRPC] flyTo expired (command_id={p._ecp.command_id})");
                    return EcpAckJson.Expired(p._ecp, $"expires_at={p._ecp.expires_at}");
                }

                // Sprint4 Phase 4 W3.A.3: surface active_command_id + locks=["body"]
                // through EcpState immediately, so Brain (once ingest is wired)
                // sees the cmd before flyTo physically completes.
                commandId = p._ecp?.command_id ?? "";
                LifecycleHeartbeatPublisher.Instance?.ReportActiveCommand(commandId, new[] { "body" });
                reported = true;

                // Sprint4 GOSLO model modularization (Step 2, 2026-05-06):
                // route through ParrotController by model_id from _ecp.meta.
                // ParrotController falls back to AnimationDriver direct path
                // when no Registry / controller is present, so existing GOSLO
                // scenes that haven't added a ModelDriver keep working.
                string modelId = p._ecp?.ModelId ?? "";

                var tcs = new TaskCompletionSource<bool>();
                UnityMainThread.Enqueue(() =>
                {
                    _parrot.FlyTo(new Vector3(p.x, p.y, p.z), modelId);
                    tcs.SetResult(true);
                });

                await tcs.Task;
                return EcpAckJson.Completed(
                    p._ecp,
                    EcpFrontendStateDto.ForBody("flying", p._ecp?.command_id, new[] { "body" })
                );
            }
            catch (Exception e)
            {
                Debug.LogError($"[ParrotRPC] flyTo error: {e.Message}");
                return EcpAckJson.Failed(p._ecp, e.Message);
            }
            finally
            {
                if (reported)
                    LifecycleHeartbeatPublisher.Instance?.ClearActiveCommand(commandId);
            }
        }

        private async Task<string> HandleAnimate(RpcInvocationData data)
        {
            Debug.Log($"[ParrotRPC] animate <- {data.CallerIdentity}: {data.Payload}");
            AnimatePayload p = default;
            string commandId = "";
            bool reported = false;
            try
            {
                p = JsonUtility.FromJson<AnimatePayload>(data.Payload);

                if (string.IsNullOrWhiteSpace(p.animation))
                {
                    Debug.LogWarning("[ParrotRPC] animate malformed: missing animation");
                    return EcpAckJson.Failed(p._ecp, "missing_animation", EcpAckJson.ReasonMalformed);
                }

                if (p._ecp != null && p._ecp.IsExpired(EcpAckJson.UnixSeconds()))
                {
                    Debug.LogWarning($"[ParrotRPC] animate expired (command_id={p._ecp.command_id})");
                    return EcpAckJson.Expired(p._ecp, $"expires_at={p._ecp.expires_at}");
                }

                commandId = p._ecp?.command_id ?? "";
                LifecycleHeartbeatPublisher.Instance?.ReportActiveCommand(commandId, new[] { "body" });
                reported = true;

                // Sprint4 GOSLO model modularization (Step 2, 2026-05-06):
                // pass model_id through to ParrotController; see HandleFlyTo
                // for the routing rationale.
                string modelId = p._ecp?.ModelId ?? "";
                Debug.Log(
                    $"[ParrotRPC] animate parsed animation='{p.animation}' model_id='{modelId}' " +
                    $"strict={p.strict_capability} command_id='{commandId}'");

                var tcs = new TaskCompletionSource<bool>();
                UnityMainThread.Enqueue(() =>
                {
                    tcs.SetResult(_parrot.TryPlayAnimation(p.animation, modelId, p.parameters_json, p.strict_capability));
                });

                bool played = await tcs.Task;
                if (!played)
                {
                    return EcpAckJson.Failed(p._ecp, $"capability_unsupported:{p.animation}");
                }

                return EcpAckJson.Completed(
                    p._ecp,
                    EcpFrontendStateDto.ForBody(AnimationToBodyState(p.animation), p._ecp?.command_id, new[] { "body" })
                );
            }
            catch (Exception e)
            {
                Debug.LogError($"[ParrotRPC] animate error: {e.Message}");
                return EcpAckJson.Failed(p._ecp, e.Message);
            }
            finally
            {
                if (reported)
                    LifecycleHeartbeatPublisher.Instance?.ClearActiveCommand(commandId);
            }
        }

        private async Task<string> HandlePerchToFinger(RpcInvocationData data)
        {
            Debug.Log($"[ParrotRPC] perchToFinger <- {data.CallerIdentity}: {data.Payload}");
            PerchToFingerPayload p = default;
            try
            {
                p = JsonUtility.FromJson<PerchToFingerPayload>(data.Payload);

                if (p._ecp != null && p._ecp.IsExpired(EcpAckJson.UnixSeconds()))
                {
                    Debug.LogWarning($"[ParrotRPC] perchToFinger expired (command_id={p._ecp.command_id})");
                    return EcpAckJson.Expired(p._ecp, $"expires_at={p._ecp.expires_at}");
                }

                string commandId = p._ecp?.command_id ?? "";
                string modelId = p._ecp?.ModelId ?? "";
                float timeoutSeconds = p.timeout_seconds > 0f ? p.timeout_seconds : 6f;
                var started = new TaskCompletionSource<string>();
                var landed = new TaskCompletionSource<PerchOnHand.PerchRpcResult>();

                UnityMainThread.Enqueue(() =>
                {
                    try
                    {
                        var perch = ResolvePerchOwner(modelId);
                        if (perch == null)
                        {
                            started.TrySetResult("perch_owner_missing");
                            landed.TrySetResult(PerchOnHand.PerchRpcResult.Rejected("perch_owner_missing"));
                            return;
                        }

                        if (!perch.TryRequestRpcPerch(
                                commandId,
                                p.require_branch_gesture,
                                landed,
                                out string reason))
                        {
                            started.TrySetResult(reason);
                            landed.TrySetResult(PerchOnHand.PerchRpcResult.Rejected(reason));
                            return;
                        }

                        started.TrySetResult("");
                    }
                    catch (Exception ex)
                    {
                        started.TrySetResult("failed");
                        landed.TrySetResult(PerchOnHand.PerchRpcResult.Rejected(ex.Message));
                    }
                });

                string startReason = await started.Task;
                if (!string.IsNullOrEmpty(startReason))
                    return EcpAckJson.Rejected(p._ecp, startReason, startReason);

                Task finished = await Task.WhenAny(
                    landed.Task,
                    Task.Delay(TimeSpan.FromSeconds(Math.Max(1.0, timeoutSeconds))));
                if (finished != landed.Task)
                {
                    UnityMainThread.Enqueue(() =>
                    {
                        var perch = ResolvePerchOwner(modelId);
                        perch?.CancelRpcPerch(commandId, "timeout");
                    });
                    return EcpAckJson.Failed(p._ecp, "timeout", "timeout");
                }

                PerchOnHand.PerchRpcResult result = await landed.Task;
                if (!result.Ok)
                    return EcpAckJson.Rejected(p._ecp, result.Reason, result.Reason);

                return EcpAckJson.Completed(
                    p._ecp,
                    EcpFrontendStateDto.ForBody("perched_on_hand", commandId, new[] { "body" }));
            }
            catch (Exception e)
            {
                Debug.LogError($"[ParrotRPC] perchToFinger error: {e.Message}");
                return EcpAckJson.Failed(p._ecp, e.Message);
            }
        }

        private async Task<string> HandleReturnToView(RpcInvocationData data)
        {
            Debug.Log($"[ParrotRPC] returnToView <- {data.CallerIdentity}: {data.Payload}");
            ReturnToViewPayload p = default;
            try
            {
                p = JsonUtility.FromJson<ReturnToViewPayload>(data.Payload);

                if (p._ecp != null && p._ecp.IsExpired(EcpAckJson.UnixSeconds()))
                {
                    Debug.LogWarning($"[ParrotRPC] returnToView expired (command_id={p._ecp.command_id})");
                    return EcpAckJson.Expired(p._ecp, $"expires_at={p._ecp.expires_at}");
                }

                string commandId = p._ecp?.command_id ?? "";
                string modelId = p._ecp?.ModelId ?? "";
                float timeoutSeconds = p.timeout_seconds > 0f ? p.timeout_seconds : 5f;
                var started = new TaskCompletionSource<string>();
                var returned = new TaskCompletionSource<PerchOnHand.PerchRpcResult>();

                UnityMainThread.Enqueue(() =>
                {
                    try
                    {
                        var perch = ResolvePerchOwner(modelId);
                        if (perch == null)
                        {
                            started.TrySetResult("perch_owner_missing");
                            returned.TrySetResult(PerchOnHand.PerchRpcResult.Rejected("perch_owner_missing"));
                            return;
                        }

                        if (!perch.TryRequestReturnToView(commandId, returned, out string reason))
                        {
                            started.TrySetResult(reason);
                            returned.TrySetResult(PerchOnHand.PerchRpcResult.Rejected(reason));
                            return;
                        }

                        started.TrySetResult("");
                    }
                    catch (Exception ex)
                    {
                        started.TrySetResult("failed");
                        returned.TrySetResult(PerchOnHand.PerchRpcResult.Rejected(ex.Message));
                    }
                });

                string startReason = await started.Task;
                if (!string.IsNullOrEmpty(startReason))
                    return EcpAckJson.Rejected(p._ecp, startReason, startReason);

                Task finished = await Task.WhenAny(
                    returned.Task,
                    Task.Delay(TimeSpan.FromSeconds(Math.Max(1.0, timeoutSeconds))));
                if (finished != returned.Task)
                {
                    UnityMainThread.Enqueue(() =>
                    {
                        var perch = ResolvePerchOwner(modelId);
                        perch?.CancelRpcPerch(commandId, "timeout");
                    });
                    return EcpAckJson.Failed(p._ecp, "timeout", "timeout");
                }

                PerchOnHand.PerchRpcResult result = await returned.Task;
                if (!result.Ok)
                    return EcpAckJson.Rejected(p._ecp, result.Reason, result.Reason);

                return EcpAckJson.Completed(
                    p._ecp,
                    EcpFrontendStateDto.ForBody("idle", commandId, new[] { "body" }));
            }
            catch (Exception e)
            {
                Debug.LogError($"[ParrotRPC] returnToView error: {e.Message}");
                return EcpAckJson.Failed(p._ecp, e.Message);
            }
        }

        private static string AnimationToBodyState(string animation)
        {
            switch (animation)
            {
                case "fly": return "flying";
                case "dance":
                case "wing_flap": return "dancing";
                case "perch":
                case "sit": return "perching";
                case "sleep": return "idle";
                default: return "idle";
            }
        }

        private PerchOnHand ResolvePerchOwner(string modelId)
        {
            var own = GetComponent<PerchOnHand>();
            if (own != null && MatchesModel(own, modelId)) return own;

            var all = FindObjectsOfType<PerchOnHand>(true);
            PerchOnHand fallback = null;
            for (int i = 0; i < all.Length; i++)
            {
                var candidate = all[i];
                if (candidate == null) continue;
                if (MatchesModel(candidate, modelId)) return candidate;
                if (fallback == null && string.IsNullOrWhiteSpace(modelId))
                    fallback = candidate;
            }
            return fallback;
        }

        private static bool MatchesModel(PerchOnHand perch, string modelId)
        {
            if (perch == null) return false;
            if (string.IsNullOrWhiteSpace(modelId)) return true;

            var driver = perch.GetComponentInChildren<ModelDriver>(true);
            if (driver == null) return false;
            if (driver.Manifest != null
                && string.Equals(driver.Manifest.model_id, modelId, StringComparison.Ordinal))
                return true;
            return string.Equals(driver.EffectiveModelId, modelId, StringComparison.Ordinal);
        }

        void OnDestroy()
        {
            var rm = RoomManager.Instance;
            if (rm != null)
            {
                rm.OnConnected -= Register;
                rm.OnDisconnected -= OnRoomDisconnected;
            }
            _rpcRegisteredOnRoom = null;
        }

        private static double UnixSeconds()
            => (DateTime.UtcNow - new DateTime(1970, 1, 1, 0, 0, 0, DateTimeKind.Utc)).TotalSeconds;

        [Serializable] private struct FlyToPayload { public float x, y, z; public EcpCommandDto _ecp; }
        [Serializable] private struct AnimatePayload { public string animation; public string parameters_json; public bool strict_capability; public EcpCommandDto _ecp; }
        [Serializable] private struct PerchToFingerPayload { public bool require_branch_gesture; public float timeout_seconds; public EcpCommandDto _ecp; }
        [Serializable] private struct ReturnToViewPayload { public float timeout_seconds; public EcpCommandDto _ecp; }
    }
}
