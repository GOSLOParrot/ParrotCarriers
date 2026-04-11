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

        room.LocalParticipant.RegisterRpcMethod("flyTo", HandleFlyTo);
        room.LocalParticipant.RegisterRpcMethod("animate", HandleAnimate);
        Debug.Log("[ParrotRPC] Registered: flyTo, animate");
    }

    private async Task<string> HandleFlyTo(RpcInvocationData data)
    {
        Debug.Log($"[ParrotRPC] flyTo <- {data.CallerIdentity}: {data.Payload}");
        try
        {
            var p = JsonUtility.FromJson<FlyToPayload>(data.Payload);
            var tcs = new TaskCompletionSource<bool>();

            UnityMainThread.Enqueue(() =>
            {
                _parrot.FlyTo(new Vector3(p.x, p.y, p.z));
                tcs.SetResult(true);
            });

            await tcs.Task;
            return "{\"status\":\"ok\",\"action\":\"flyTo\"}";
        }
        catch (Exception e)
        {
            Debug.LogError($"[ParrotRPC] flyTo error: {e.Message}");
            return $"{{\"status\":\"error\",\"message\":\"{EscapeJson(e.Message)}\"}}";
        }
    }

    private async Task<string> HandleAnimate(RpcInvocationData data)
    {
        Debug.Log($"[ParrotRPC] animate <- {data.CallerIdentity}: {data.Payload}");
        try
        {
            var p = JsonUtility.FromJson<AnimatePayload>(data.Payload);
            var tcs = new TaskCompletionSource<bool>();

            UnityMainThread.Enqueue(() =>
            {
                _parrot.PlayAnimation(p.animation);
                tcs.SetResult(true);
            });

            await tcs.Task;
            return $"{{\"status\":\"ok\",\"action\":\"animate\",\"animation\":\"{EscapeJson(p.animation)}\"}}";
        }
        catch (Exception e)
        {
            Debug.LogError($"[ParrotRPC] animate error: {e.Message}");
            return $"{{\"status\":\"error\",\"message\":\"{EscapeJson(e.Message)}\"}}";
        }
    }

    private static string EscapeJson(string s) =>
        s?.Replace("\\", "\\\\").Replace("\"", "\\\"") ?? "";

    void OnDestroy()
    {
        var rm = RoomManager.Instance;
        if (rm != null) rm.OnConnected -= Register;
    }

    [Serializable] private struct FlyToPayload { public float x, y, z; }
    [Serializable] private struct AnimatePayload { public string animation; }
}
