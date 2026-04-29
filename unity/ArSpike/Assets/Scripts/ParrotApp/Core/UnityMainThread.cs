using System;
using System.Collections.Concurrent;
using UnityEngine;

namespace ParrotApp.Core
{
    /// <summary>
    /// Dispatches actions from background threads onto Unity's main thread.
    /// LiveKit RPC callbacks run on thread-pool threads — Unity API calls
    /// (Transform, Animator, etc.) must be marshaled through here.
    ///
    /// Auto-bootstrapped via <see cref="RuntimeInitializeOnLoadMethodAttribute"/>;
    /// no scene wiring required. Lifecycle code may safely call
    /// <see cref="Enqueue"/> at any time after first scene load.
    ///
    /// 直接搬迁自 ParrotDev/Core/UnityMainThread.cs（Sprint3 已验证），加
    /// <c>ParrotApp.Core</c> 命名空间。行为零变化。
    /// </summary>
    public class UnityMainThread : MonoBehaviour
    {
        private static readonly ConcurrentQueue<Action> _queue = new();
        private static UnityMainThread _instance;

        [RuntimeInitializeOnLoadMethod(RuntimeInitializeLoadType.BeforeSceneLoad)]
        private static void Init()
        {
            if (_instance != null) return;
            var go = new GameObject("[ParrotApp.MainThreadDispatcher]");
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
}
