using System;
using System.Threading.Tasks;
using UnityEngine;
using LiveKit;

/// <summary>
/// Registers RPC methods that the Brain Agent calls via _rpc_bridge.py:
///   "flyTo"   -> ParrotController.FlyTo(Vector3)
///   "animate" -> ParrotController.PlayAnimation(string)
///
/// Attach to the same GameObject as ParrotController.
/// </summary>
[RequireComponent(typeof(ParrotController))]
public class ParrotRpcHandler : MonoBehaviour
{
    private ParrotController _parrot;
    private Room _rpcRegisteredOnRoom;

    void Awake()
    {
        _parrot = GetComponent<ParrotController>();
    }

    void Start()
    {
        var rm = RoomManager.Instance;
        if (rm == null)
        {
            Debug.LogError("[ParrotRPC] RoomManager not found");
            return;
        }

        rm.OnConnected += Register;
        if (rm.IsConnected) Register();
    }

    private void Register()
    {
        var room = RoomManager.Instance?.Room;
        if (room == null) return;
        if (_rpcRegisteredOnRoom == room)
            return;

        _rpcRegisteredOnRoom = room;
        room.LocalParticipant.RegisterRpcMethod("flyTo", HandleFlyTo);
        room.LocalParticipant.RegisterRpcMethod("animate", HandleAnimate);
        Debug.Log("[ParrotRPC] Registered: flyTo, animate");
    }

    private async Task<string> HandleFlyTo(RpcInvocationData data)
    {
        Debug.Log($"[ParrotRPC] flyTo <- {data.CallerIdentity}: {data.Payload}");
        FlyToPayload p = default;
        try
        {
            p = JsonUtility.FromJson<FlyToPayload>(data.Payload);

            // Sprint4 ECP-minimal: honour `expires_at` so a stale fly_to
            // (e.g. user already moved their hand) is rejected instead of
            // executed with old coordinates. See
            // sprint4_protocol_ecp_background_20260429.md §5 acceptance
            // criterion 1.
            if (p._ecp != null && p._ecp.IsExpired(EcpAckJson.UnixSeconds()))
            {
                Debug.LogWarning($"[ParrotRPC] flyTo expired (command_id={p._ecp.command_id})");
                return EcpAckJson.Expired(p._ecp, $"expires_at={p._ecp.expires_at}");
            }

            var tcs = new TaskCompletionSource<bool>();
            UnityMainThread.Enqueue(() =>
            {
                _parrot.FlyTo(new Vector3(p.x, p.y, p.z));
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
    }

    private async Task<string> HandleAnimate(RpcInvocationData data)
    {
        Debug.Log($"[ParrotRPC] animate <- {data.CallerIdentity}: {data.Payload}");
        AnimatePayload p = default;
        try
        {
            p = JsonUtility.FromJson<AnimatePayload>(data.Payload);

            if (p._ecp != null && p._ecp.IsExpired(EcpAckJson.UnixSeconds()))
            {
                Debug.LogWarning($"[ParrotRPC] animate expired (command_id={p._ecp.command_id})");
                return EcpAckJson.Expired(p._ecp, $"expires_at={p._ecp.expires_at}");
            }

            var tcs = new TaskCompletionSource<bool>();
            UnityMainThread.Enqueue(() =>
            {
                _parrot.PlayAnimation(p.animation);
                tcs.SetResult(true);
            });

            await tcs.Task;
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

    void OnDestroy()
    {
        var rm = RoomManager.Instance;
        if (rm != null) rm.OnConnected -= Register;
        _rpcRegisteredOnRoom = null;
    }

    [Serializable] private struct FlyToPayload { public float x, y, z; public EcpCommandDto _ecp; }
    [Serializable] private struct AnimatePayload { public string animation; public EcpCommandDto _ecp; }
}
