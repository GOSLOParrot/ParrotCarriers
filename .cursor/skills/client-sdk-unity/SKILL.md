---
name: client-sdk-unity
description: Use when working with LiveKit Unity SDK (Room, DataChannel PublishData/DataReceived, RPC RegisterMethodAsync/PerformRpc, Reliable/Lossy)
---

# LiveKit Unity SDK

> ⚠️ **NOTICE — 本 SKILL 内容尚未基于 SDK main HEAD（FFI v0.12.53, 2026-04-28）重新蒸馏。**
> 下方 "Quick Reference" 例子来自更早的 commit 快照，**仅作 API 形态参考**；调用前请先读
> `Library/PackageCache/io.livekit.livekit-sdk@*/Runtime/Scripts/` 实际签名，或参考
> `.cursor/rules/livekit-unity-sdk.mdc` 中已收口的真实差异。
>
> ## 🔒 当前工作区版本锁（2026-04-29 更新）
>
> | 项 | 值 | 备注 |
> |---|---|---|
> | client-sdk-unity pin | `7d868ef5cc5615c30a3ef4b73ae0dbb5cc4d6796`（main HEAD, 含 PR #263） | 同步在 `unity/{ArSpike,ParrotDev}/Packages/manifest.json` |
> | livekit-ffi（Rust 内嵌） | **v0.12.53**（2026-04-23 release） | 决定 `liblivekit_ffi.so` 的 16KB 对齐能力 |
> | Unity Editor | **2022.3.62f3** | 2022.3.56f1+ 才有引擎层 16KB 支持 |
> | ARCore/ARFoundation/ARKit | **5.2.2**（同步升级） | 5.2.2 才把 `libarcore_sdk_c.so` 改 16KB 对齐 |
>
> ## 🚨 Android 15+ 16KB Page Alignment（强制）
>
> 自 2025-11-01 起 Google Play 强制要求 64-bit App 的所有 native `.so` 走 **16KB ELF 对齐**，否则在 Android 15+ ARM64 设备上 `dlopen` 失败 / 冷启动闪退。本 SDK 通过升级到 FFI v0.12.53 满足要求，**但出包前必须真验**：
>
> ```powershell
> # Windows / 仓库自带脚本
> pwsh tools/verify_so_alignment.ps1 <apk_or_so_dir>
> ```
>
> 脚本调用 `llvm-objdump -p *.so | grep LOAD`，对应每条 `.so` 必须出现 `align 2**14`。任何一条 `< 2**14` 都是阻塞项，处理路径：
>
> 1. 删 `Library/PackageCache/io.livekit.livekit-sdk@*` → Unity 重新拉 → Reimport `.so`，确保 `.so.meta` 出现 `Is16KbAligned: true`。
> 2. 若仍不达标，按 SDK `BuildScripts~/build_ffi_locally.sh android release` 本地重编（NDK r28+ 默认 16KB；r27 需追加 `-Wl,-z,max-page-size=16384,-z,common-page-size=16384`）。
>
> ## 🔄 本次升级带来的行为变更（针对本仓库代码影响审计）
>
> 已在 2026-04-29 完成全 `unity/**/*.cs` grep；下表是**潜在影响 + 当前是否中招**的快照，蒸馏 SKILL 时建议保留这一段：
>
> | 变更 (PR) | 行为差异 | 本仓库是否中招 |
> |---|---|---|
> | PR #250 `IRemoteTrack.SetEnabled` 真正走 FFI | 旧版本是 C# 端 no-op；现在会真停 / 真启远端订阅 | ❌ 我们走 `ILocalTrack.SetMute` 控制 setVideoTier，不受影响 |
> | PR #260 AudioStream catchup + crossfade | 远端音频"咔哒"修复 + 进入回调延迟可能微变 | ⚠️ 走 `RoomManager._remoteAudioStreams`，行为应改善而非恶化；建议真机复测一次 GOSLO 远端语音连续性 |
> | PR #259 ByteStreamReader.ReadIncremental chunk-drop | 大数据流分片不再丢中间块 | ❌ 未使用 RegisterByteStreamHandler |
> | PR #233 / #258 Stream readers/writers IDisposable | 未注册 handler 的 stream 自动 Dispose | ❌ 未使用 stream handler |
> | PR #226 Room disconnect 时 event handler 泄漏修复 | 我们的 `RoomManager` 原本就 try-defensive，行为只更稳 | ✅ 无需改 |
> | livekit-ffi 0.12.53 `VideoFrame::new()` 强制 `frame_metadata` | Rust 端 breaking | ❌ 我们走 `TextureVideoSource` 包装，C# 用户不直接构造 VideoFrame |
> | PR #213 / #207 RtcAudioSource catchup + `_muted/_disposed` volatile | 不影响 C# 调用面 | ❌ |
>
> 结论：**本次升级无需修改 ParrotCarriers 任何 C# 代码**。
>
> 完整变更清单见 [client-sdk-unity Releases](https://github.com/livekit/client-sdk-unity/releases) 与 [rust-sdks/livekit-ffi v0.12.53](https://github.com/livekit/rust-sdks/releases/tag/livekit-ffi%2Fv0.12.53)。
>
> ---


This documentation provides a comprehensive overview of the `client-sdk-unity` skill, which offers a C# wrapper around LiveKit's Rust SDK for real-time audio/video communication within Unity applications. It enables developers to integrate functionalities such as multi-modal AI, live streaming, and video calls. The skill is designed to help users understand the codebase, find usage examples, review APIs, and explore configuration and architectural patterns.

**Note:** This SDK is currently in **Developer Preview**. APIs may change and bugs may be present. Feedback and contributions are welcome.

## When to Use This Skill

Use this skill when you need to:
*   Integrate real-time audio, video, and data features into your Unity application.
*   Connect to LiveKit Cloud or a self-hosted LiveKit server.
*   Understand the SDK's architecture, especially the FFI (Foreign Function Interface) bridge with the Rust native library.
*   Implement data channels for reliable or lossy data transfer between participants.
*   Utilize RPC (Remote Procedure Call) patterns for direct participant-to-participant method invocations, particularly useful for AI agents controlling Unity clients (e.g., ParrotCarriers).
*   Publish and subscribe to audio and video tracks from microphones, cameras, or custom textures.
*   Troubleshoot integration issues or debug C# and Rust components.

## Key Concepts

The LiveKit Unity SDK leverages a **FFI Bridge Pattern** to communicate with a native Rust library (`liblivekit_ffi`). This involves:
*   **C# Public API**: (`Runtime/Scripts/*.cs`) Exposes high-level functionalities like `Room`, `Participant`, `Track`, and data streams.
*   **FFI Layer**: (`Runtime/Scripts/Internal/`) Serializes requests using Protocol Buffers and sends them to Rust via P/Invoke.
*   **Native Library**: (`Runtime/Plugins/ffi-*/liblivekit_ffi.*`) The core Rust implementation, compiled per platform and architecture.

### Data Channels for ParrotCarriers

For use cases like ParrotCarriers, understanding data channels is crucial:
*   **Reliable Data (`DataPacketKind.RELIABLE`)**: Ensures delivery, useful for commands and state synchronization (e.g., `body_cmd`, `state_sync`).
*   **Lossy Data (`DataPacketKind.LOSSY`)**: Prioritizes speed over guaranteed delivery, suitable for high-frequency telemetry (e.g., `pose`, `ar_telemetry` at 10Hz).
*   **`Room.DataReceived` Event**: The primary mechanism for Unity to receive telemetry data from other participants (e.g., Python agents).

### Remote Procedure Calls (RPC) for ParrotCarriers

The SDK supports RPC for direct method calls between participants. This is highly relevant for scenarios where a "Brain Agent" (e.g., a Python agent) sends function/tool results as RPC commands to a Unity client (e.g., `dance`, `flyTo`).

### Developer Preview Status

Be aware that the SDK is in **Developer Preview**. This means:
*   APIs may change.
*   There might be bugs.
*   Ongoing development includes features like improved data track support and audio ring buffers.

## Quick Reference: Practical Examples

Here are common tasks demonstrated with practical code examples. All C# examples below assume they are part of a `MonoBehaviour` and use `IEnumerator` for async operations.

> **API 校正口径（与 SDK main HEAD 实测一致，2026-04-29）**：
> - `Room.Connect(url, token, RoomOptions)` 是**三参签名**，省略 `RoomOptions` → 编译报 CS7036。
> - `ConnectInstruction` / `PublishTrackInstruction` 等 yield 指令**只有** `IsError` / `IsDone`，**没有** `.Error` 字符串属性；记录失败原因要靠 SDK 日志或自己包 try/catch。
> - `RemoteAudioTrack` 的 `AudioStream` 必须**强引用**（局部变量会被 GC 收掉，导致随机断流）；用完显式 `Dispose()`。
> - `IRemoteTrack.SetEnabled(bool)` 在 PR #250 (FFI v0.12.53) 之后才真正走 FFI；老快照里这是 no-op，迁移代码注意。
> - `ByteStreamReader` / `TextStreamReader` / 对应 Writer 都是 `IDisposable`（PR #233/#258）；未注册 handler 的 incoming stream 会被 Room 自动 Dispose。

### 1. Connect to a LiveKit Room

Establishes a connection to a LiveKit server.

```csharp
using LiveKit;
using UnityEngine;
using System.Collections;

public class LiveKitConnection : MonoBehaviour
{
    private Room room;

    IEnumerator Start()
    {
        room = new Room();
        room.TrackSubscribed += TrackSubscribed; // Register event handler
        room.ParticipantConnected += (participant) => Debug.Log($"Participant connected: {participant.Identity}");
        room.ParticipantDisconnected += (participant) => Debug.Log($"Participant disconnected: {participant.Identity}");

        // ⚠️ Real signature requires 3 args: (url, token, RoomOptions). README pre-2026-04
        // examples that drop RoomOptions trigger CS7036 — see livekit-unity-sdk.mdc.
        var connect = room.Connect("ws://localhost:7880", "<join-token>", new RoomOptions());
        yield return connect;

        if (!connect.IsError)
        {
            Debug.Log("Connected to " + room.Name);
        }
        else
        {
            // ⚠️ ConnectInstruction has NO .Error string property — only IsError / IsDone.
            Debug.LogError("Connection failed (check token / server URL / firewall).");
        }
    }

    void TrackSubscribed(IRemoteTrack track, RemoteTrackPublication publication, RemoteParticipant participant)
    {
        Debug.Log($"Track subscribed from {participant.Identity}: {track.Sid} ({track.Kind})");
        // Handle incoming tracks here (e.g., display video, play audio)
    }

    // Remember to disconnect when the application quits
    void OnApplicationQuit()
    {
        // For graceful shutdown also Dispose() the Room (FFI handles + IDisposable readers/writers
        // since PR #233/#258). OnApplicationQuit is best-effort; production code should run a
        // dedicated chokepoint coroutine — see livekit-unity-lifecycle/IMPL_REF.md §1.
        room?.Disconnect();
        (room as System.IDisposable)?.Dispose();
    }
}
```

### 2. Publishing Microphone Audio

Publishes audio from the default microphone to the LiveKit room.

```csharp
using LiveKit;
using UnityEngine;
using System.Collections;

public class AudioPublisher : MonoBehaviour
{
    private Room _room; // Assume _room is already connected
    private MicrophoneSource _rtcSource;

    public IEnumerator PublishMicrophone(Room room)
    {
        _room = room;
        var localSid = "my-audio-source";
        GameObject audObject = new GameObject(localSid);
        
        // Use the first detected microphone
        _rtcSource = new MicrophoneSource(Microphone.devices[0], audObject);
        var track = LocalAudioTrack.CreateAudioTrack("my-audio-track", _rtcSource, _room);

        var options = new TrackPublishOptions
        {
            AudioEncoding = new AudioEncoding { MaxBitrate = 64000 },
            Source = TrackSource.SourceMicrophone
        };

        var publish = _room.LocalParticipant.PublishTrack(track, options);
        yield return publish;

        if (!publish.IsError)
        {
            Debug.Log("Microphone track published!");
            _rtcSource.Start(); // Start capturing audio
        }
        else
        {
            Debug.LogError("Failed to publish microphone track: " + publish.Error);
        }
    }
}
```

### 3. Publishing a Unity Camera Feed

Publishes a video stream from the main Unity camera.

```csharp
using LiveKit;
using UnityEngine;
using System.Collections;

public class CameraPublisher : MonoBehaviour
{
    private Room _room; // Assume _room is already connected
    private TextureVideoSource _videoSource;

    public IEnumerator PublishCamera(Room room)
    {
        _room = room;
        
        // Render to a texture for publishing
        var rt = new RenderTexture(1920, 1080, 24, RenderTextureFormat.ARGB32);
        rt.Create();
        Camera.main.targetTexture = rt;
        
        _videoSource = new TextureVideoSource(rt);
        var track = LocalVideoTrack.CreateVideoTrack("my-video-track", _videoSource, _room);

        var options = new TrackPublishOptions
        {
            VideoCodec = VideoCodec.Vp8,
            VideoEncoding = new VideoEncoding { MaxBitrate = 512000, MaxFramerate = 30 },
            Simulcast = true,
            Source = TrackSource.SourceCamera
        };

        var publish = _room.LocalParticipant.PublishTrack(track, options);
        yield return publish;

        if (!publish.IsError)
        {
            Debug.Log("Camera track published!");
            _videoSource.Start();
            StartCoroutine(_videoSource.Update()); // Continuously update the video source
        }
        else
        {
            Debug.LogError("Failed to publish camera track: " + publish.Error);
        }
    }
}
```

### 4. Receiving Audio and Video Tracks

Handles the `TrackSubscribed` event to display incoming video and play audio.

```csharp
using LiveKit;
using UnityEngine;
using UnityEngine.UI; // For RawImage
using System.Collections;

public class TrackReceiver : MonoBehaviour
{
    public RawImage videoDisplayArea; // Assign in Inspector

    // ⚠️ STRONG REFERENCE REQUIRED: AudioStream / VideoStream wrap native FFI handles and
    // register Unity audio callbacks. If you only assign them to local vars they will be
    // GC'd after this method returns — Sprint3 真机 reproduced this as random audio dropouts.
    // Always store them in instance fields / dictionaries; Dispose() on room teardown.
    private readonly Dictionary<string, AudioStream> _audioStreams = new();
    private readonly Dictionary<string, VideoStream> _videoStreams = new();

    // This method is typically registered with room.TrackSubscribed += TrackSubscribed;
    void TrackSubscribed(IRemoteTrack track, RemoteTrackPublication publication, RemoteParticipant participant)
    {
        var key = $"{participant.Identity}:{publication.Sid}";

        if (track is RemoteVideoTrack videoTrack)
        {
            var stream = new VideoStream(videoTrack);
            stream.TextureReceived += (tex) =>
            {
                if (videoDisplayArea != null) videoDisplayArea.texture = tex;
            };
            StartCoroutine(stream.Update());
            _videoStreams[key] = stream; // strong ref
            Debug.Log($"Displaying video from {participant.Identity}");
        }
        else if (track is RemoteAudioTrack audioTrack)
        {
            GameObject audObject = new GameObject($"Audio_{audioTrack.Sid}");
            var source = audObject.AddComponent<AudioSource>();
            _audioStreams[key] = new AudioStream(audioTrack, source); // strong ref
            // SDK ≥ FFI 0.12.53 (PR #260): catchup adds cooldown + crossfade on resume
            // from background — no client-side change needed, but verify continuity on
            // OnApplicationPause(true→false) recovery during real-device QA.
            Debug.Log($"Playing audio from {participant.Identity}");
        }
    }

    // Call from Room.Disconnected handler / OnDestroy
    public void DisposeAll()
    {
        foreach (var s in _audioStreams.Values) s.Dispose();
        foreach (var s in _videoStreams.Values) s.Dispose();
        _audioStreams.Clear();
        _videoStreams.Clear();
    }
}
```

> **Selective subscription tip (PR #250, FFI 0.12.53)**: `IRemoteTrack.SetEnabled(false)`
> 之前是 C# 端 no-op，现在会真把 enable/disable 请求送过 FFI 到服务端。新代码可以放心
> 用它做按需订阅；老代码若依赖"调了 SetEnabled 但远端仍在收帧"做延迟切换，必须改写。

### 5. Registering an RPC Method

Defines a server-side (in this context, participant-side) method that can be invoked via RPC.

```csharp
using LiveKit;
using UnityEngine;
using System.Collections;
using System.Threading.Tasks;

public class RpcReceiver : MonoBehaviour
{
    private Room _room; // Assume _room is already connected

    public void RegisterRpcHandlers(Room room)
    {
        _room = room;
        // Register the "greet" method
        _room.LocalParticipant.RegisterRpcMethod("greet", HandleGreeting);
        Debug.Log("RPC method 'greet' registered.");
    }

    private async Task<string> HandleGreeting(RpcInvocationData data)
    {
        Debug.Log($"Received greeting from {data.CallerIdentity}: {data.Payload}");
        // Simulate some async work
        await Task.Delay(100); 
        return $"Hello, {data.CallerIdentity}! Your request was {data.RequestId}.";
    }
}
```

### 6. Performing an RPC Request

Invokes an RPC method on another participant.

```csharp
using LiveKit;
using UnityEngine;
using System.Collections;

public class RpcCaller : MonoBehaviour
{
    private Room _room; // Assume _room is already connected

    public IEnumerator CallRpcMethod(Room room, string recipientIdentity, string payload)
    {
        _room = room;
        var rpcCall = _room.LocalParticipant.PerformRpc(new PerformRpcParams
        {
            DestinationIdentity = recipientIdentity,
            Method = "greet",
            Payload = payload,
            ResponseTimeout = 5000 // milliseconds
        });

        yield return rpcCall;

        if (rpcCall.IsError)
        {
            Debug.LogError($"RPC call failed: {rpcCall.Error.Code} - {rpcCall.Error.Message}");
        }
        else
        {
            Debug.Log($"RPC response from {recipientIdentity}: {rpcCall.Payload}");
        }
    }
}
```

### 7. Sending Text Data via Data Channel (Reliable)

Sends a complete text message reliably to other participants.

```csharp
using LiveKit;
using UnityEngine;
using System.Collections;

public class TextSender : MonoBehaviour
{
    private Room _room; // Assume _room is already connected

    public IEnumerator SendReliableText(Room room, string message, string topic = "general_chat")
    {
        _room = room;
        var sendTextCall = _room.LocalParticipant.SendText(message, topic);
        yield return sendTextCall;

        if (!sendTextCall.IsError)
        {
            Debug.Log($"Sent text (ID: {sendTextCall.Info.Id}, Topic: {topic})");
        }
        else
        {
            Debug.LogError($"Failed to send text: {sendTextCall.Error}");
        }
    }
}
```

### 8. Handling Incoming Byte Streams

Receives byte data, potentially representing files, and logs or writes it to disk.

```csharp
using LiveKit;
using UnityEngine;
using System.Collections;

public class ByteStreamReceiver : MonoBehaviour
{
    private Room _room; // Assume _room is already connected

    public void RegisterByteStreamHandler(Room room, string topic = "file_transfer")
    {
        _room = room;
        _room.RegisterByteStreamHandler(topic, (reader, identity) =>
            StartCoroutine(HandleIncomingByteStream(reader, identity))
        );
        Debug.Log($"Registered byte stream handler for topic: {topic}");
    }

    // ⚠️ ByteStreamReader / TextStreamReader implement IDisposable since PR #233 (Apr 2026).
    // If your handler can't be invoked (e.g. wrong topic), Room.cs auto-Disposes the reader
    // (PR #258). Inside your handler, ALWAYS finish reading or explicitly Dispose() — leaking
    // a reader leaks an FFI handle. Wrap in `using` when feasible.
    private IEnumerator HandleIncomingByteStream(ByteStreamReader reader, string participantIdentity)
    {
        using (reader)
        {
            var info = reader.Info;
            Debug.Log($@"
            Byte stream received from {participantIdentity}
            Topic: {info.Topic}
            Timestamp: {info.Timestamp}
            ID: {info.Id}
            Size: {info.TotalLength} (if sent with SendFile)
            ");

            // Option 1: Process incrementally (PR #259 fixed mid-chunk drop in 0.12.53)
            var readIncremental = reader.ReadIncremental();
            while (true)
            {
                readIncremental.Reset();
                yield return readIncremental;
                if (readIncremental.IsEos) break; // End of Stream
                Debug.Log($"Next byte chunk length: {readIncremental.Bytes.Length}");
                // Process readIncremental.Bytes here
            }
        }

        // Option 2: Get entire data after stream completion
        // var readAllCall = reader.ReadAll();
        // yield return readAllCall;
        // if (!readAllCall.IsError) Debug.Log($"Received total bytes: {readAllCall.Bytes.Length}");

        // Option 3: Write directly to a local file
        // var writeToFileCall = reader.WriteToFile();
        // yield return writeToFileCall;
        // if (!writeToFileCall.IsError) Debug.Log($"Wrote to file: {writeToFileCall.FilePath}");
    }
}
```

## Practical Usage Guidance

### Installation
ParrotCarriers installs via UPM git URL with **explicit commit pin** in
`unity/{ArSpike,ParrotDev}/Packages/manifest.json`:

```json
"io.livekit.livekit-sdk": "https://github.com/livekit/client-sdk-unity.git#7d868ef5cc5615c30a3ef4b73ae0dbb5cc4d6796"
```

Do NOT install via Asset Store / manual DLL copy. Do NOT pin to `main` without a SHA — UPM
caches the resolved hash and you'll lose reproducibility across machines / CI.

### Building LiveKit Plugins Locally (rebuild fallback for 16KB alignment)
Only needed if the prebuilt `.so` shipped with the SDK doesn't satisfy your platform target
(e.g., Android 15+ 16KB alignment regression on a future bump):
*   Ensure `client-sdk-rust~` submodule is initialized and Rust toolchain is installed.
*   Use `BuildScripts~/build_ffi_locally.sh <platform> [build_type]`
    (e.g., `./BuildScripts~/build_ffi_locally.sh android release`).
*   **Android 16KB alignment**: NDK r28+ defaults to 16KB. For r27 or lower add to the Rust
    target config: `rustflags = ["-C", "link-arg=-Wl,-z,max-page-size=16384",
    "-C", "link-arg=-Wl,-z,common-page-size=16384"]`. Verify with
    `tools/verify_so_alignment.ps1`.
*   **macOS**: After rebuild, restart Unity to reload the new `dylib`.

### VSCode Setup
For multi-root workspace support (Unity project + SDK package + Rust), use the `Unity-SDK.code-workspace` configuration. This enables both Rust and C# IDE support.

### Debugging
*   **C# Debugging**: Use the `C# Unity` launch option in `.vscode/launch.json` to attach to the Unity Editor.
*   **Rust / C++ Debugging (MacOS)**: Install the `CodeLLDB` extension. Build `livekit-ffi` in debug mode, start Unity Editor, then attach via the `.vscode/launch.json` configuration.

### iOS Specifics
*   Add dependent frameworks to `UnityFramework` target: `OpenGLES.framework`, `MetalKit.framework`, `GLKit.framework`, `VideoToolBox.framework`, `Network.framework`.
*   Add `-ObjC` to `Other Linker Flags`.
*   The SDK includes a post-build fix to ensure `liblivekit_ffi.a` is linked before `libiPhone-lib.a` to avoid codec conflicts. If issues persist, manual reordering might be needed.

### Verbose Logging
To enable detailed logging within the SDK:
1.  Go to Unity's Project Settings → Player.
2.  Select your target platform (Mac, iOS, Android).
3.  Under `Other Settings` → `Scripting Define Symbols`, add `LK_VERBOSE`.

## Project Documentation

This skill provides the following reference documentation:

*   **`CLAUDE.md`**: Provides guidance to AI models (like Claude) on the project's overview, build/development commands, and detailed architecture, including the FFI Bridge, Proto/Generated Code, Native Plugins, and Samples. It also outlines key conventions.
*   **`README.md`**: The main repository README, offering a high-level overview, platform support, installation instructions, local development guidance, debugging tips, iOS specifics, and comprehensive code examples for connecting to a room, publishing tracks, receiving tracks, RPC, and data/file transfer.
*   **`references/config_patterns/`**: Detailed analysis of configuration files found in the project, their types, purpose, and detected patterns.
*   **`references/dependencies/`**: Dependency graph and analysis of the codebase.
*   **`references/documentation/`**: Contains `CLAUDE.md` and `README.md` in their raw form for complete context.
*   **`references/patterns/`**: Detailed analysis of detected design patterns, including instances of the Adapter pattern.

### Configuration Extraction Summary

*   **Total Configuration Files Analyzed:** 24
*   **Total Settings:** 916
*   **Detected Patterns:** None (indicates no common, reusable config patterns identified, but individual file purposes are recognized)
*   **Common File Types:** `json`, `yaml`, `ini`
*   **Purposes Include:** `package_configuration`, `ci_cd_configuration`, `general_configuration`

### Design Patterns Detected

*From codebase analysis (confidence > 0.7)*

*   **Adapter**: 2 instances
*   Total: 2 high-confidence patterns detected.

---
Generated by Skill Seeker | Codebase Analyzer with C3.x Analysis
