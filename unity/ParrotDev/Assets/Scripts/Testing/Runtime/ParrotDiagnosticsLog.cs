using System;
using System.Collections.Generic;
using System.IO;
using System.Text;
using UnityEngine;

/// <summary>
/// <b>Testing/Runtime</b> — runs in <b>Editor Play Mode and on device</b>. Captures Console + manual lines;
/// optional file under <see cref="Application.persistentDataPath"/> for device QA logs.
/// </summary>
[DefaultExecutionOrder(-50)]
public class ParrotDiagnosticsLog : MonoBehaviour
{
    public static ParrotDiagnosticsLog Instance { get; private set; }

    [Header("Ring buffer")]
    [SerializeField] private int maxLines = 1200;

    [Header("File (optional)")]
    [SerializeField] private bool appendToFile = true;
    [SerializeField] private bool truncateLogOnPlay = true;

    private readonly List<string> _lines = new List<string>();
    private readonly Queue<string> _threadQueue = new Queue<string>();
    private readonly object _queueLock = new object();
    private string _logFilePath;

    public IReadOnlyList<string> Lines => _lines;

    private void Awake()
    {
        if (Instance != null && Instance != this)
        {
            Destroy(gameObject);
            return;
        }

        Instance = this;
        _logFilePath = Path.Combine(Application.persistentDataPath, "parrot_diagnostics.log");
        try
        {
            if (truncateLogOnPlay && File.Exists(_logFilePath))
                File.Delete(_logFilePath);
        }
        catch (Exception e)
        {
            Debug.LogWarning($"[ParrotDiagnosticsLog] Could not truncate log: {e.Message}");
        }

        DontDestroyOnLoad(gameObject);
    }

    private void OnEnable()
    {
        Application.logMessageReceivedThreaded += OnLogThreaded;
    }

    private void OnDisable()
    {
        Application.logMessageReceivedThreaded -= OnLogThreaded;
    }

    private void OnDestroy()
    {
        if (Instance == this)
            Instance = null;
    }

    private void OnLogThreaded(string condition, string stackTrace, LogType type)
    {
        var ts = DateTime.UtcNow.ToString("HH:mm:ss.fff");
        var one = $"[{ts}Z][{type}] {condition}";
        lock (_queueLock)
        {
            _threadQueue.Enqueue(one);
        }
    }

    private void Update()
    {
        lock (_queueLock)
        {
            while (_threadQueue.Count > 0)
                AppendLineLocked(_threadQueue.Dequeue());
        }
    }

    public void Line(string message)
    {
        var ts = DateTime.UtcNow.ToString("HH:mm:ss.fff");
        AppendLineLocked($"[{ts}Z][Manual] {message}");
    }

    private void AppendLineLocked(string fullLine)
    {
        _lines.Add(fullLine);
        while (_lines.Count > maxLines)
            _lines.RemoveAt(0);

        if (!appendToFile)
            return;

        try
        {
            File.AppendAllText(_logFilePath, fullLine + "\n");
        }
        catch (Exception e)
        {
            if (_lines.Count % 200 == 0)
                Debug.LogWarning($"[ParrotDiagnosticsLog] File append failed: {e.Message}");
        }
    }

    public string GetRecentText(int lineCount)
    {
        if (lineCount <= 0 || _lines.Count == 0)
            return string.Empty;
        var start = Mathf.Max(0, _lines.Count - lineCount);
        var sb = new StringBuilder();
        for (int i = start; i < _lines.Count; i++)
            sb.AppendLine(_lines[i]);

        return sb.ToString();
    }

    public string LogFilePath => _logFilePath;

    public void CopyRecentToClipboard(int lineCount = 400)
    {
        var text = GetRecentText(lineCount);
        try
        {
            GUIUtility.systemCopyBuffer = text;
            Line("Copied recent diagnostics to clipboard.");
        }
        catch
        {
            Line("Clipboard copy not supported on this platform.");
        }
    }
}
