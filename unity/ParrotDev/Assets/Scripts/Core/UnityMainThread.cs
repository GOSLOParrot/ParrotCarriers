using System;
using System.Collections.Concurrent;
using UnityEngine;

/// <summary>
/// Dispatches actions from background threads onto Unity's main thread.
/// LiveKit RPC callbacks run on thread-pool threads — Unity API calls
/// (Transform, Animator, etc.) must be marshaled through here.
/// 
/// Add this component to a persistent GameObject (or let RoomManager create it).
/// </summary>
public class UnityMainThread : MonoBehaviour
{
    private static readonly ConcurrentQueue<Action> _queue = new();
    private static UnityMainThread _instance;

    [RuntimeInitializeOnLoadMethod(RuntimeInitializeLoadType.BeforeSceneLoad)]
    private static void Init()
    {
        if (_instance != null) return;
        var go = new GameObject("[MainThreadDispatcher]");
        _instance = go.AddComponent<UnityMainThread>();
        DontDestroyOnLoad(go);
    }

    public static void Enqueue(Action action)
    {
        if (action == null) return;
        _queue.Enqueue(action);
    }

    void Update()
    {
        while (_queue.TryDequeue(out var action))
        {
            try { action(); }
            catch (Exception e) { Debug.LogException(e); }
        }
    }
}
