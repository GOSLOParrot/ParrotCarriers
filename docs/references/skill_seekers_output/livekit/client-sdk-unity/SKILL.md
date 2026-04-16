# LiveKit Unity SDK

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

## ⚡ Quick Reference: Practical Examples

Here are common tasks demonstrated with practical code examples. All C# examples below assume they are part of a `MonoBehaviour` and use `IEnumerator` for async operations.

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

        var connect = room.Connect("ws://localhost:7880", "<join-token>");
        yield return connect;

        if (!connect.IsError)
        {
            Debug.Log("Connected to " + room.Name);
        }
        else
        {
            Debug.LogError("Connection failed: " + connect.Error);
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
        room?.Disconnect();
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

    // This method is typically registered with room.TrackSubscribed += TrackSubscribed;
    void TrackSubscribed(IRemoteTrack track, RemoteTrackPublication publication, RemoteParticipant participant)
    {
        if (track is RemoteVideoTrack videoTrack)
        {
            // Display video on a RawImage
            var stream = new VideoStream(videoTrack);
            stream.TextureReceived += (tex) =>
            {
                if (videoDisplayArea != null) videoDisplayArea.texture = tex;
            };
            StartCoroutine(stream.Update()); // Start updating the video stream
            Debug.Log($"Displaying video from {participant.Identity}");
        }
        else if (track is RemoteAudioTrack audioTrack)
        {
            // Play audio through an AudioSource
            GameObject audObject = new GameObject($"Audio_{audioTrack.Sid}");
            var source = audObject.AddComponent<AudioSource>();
            var stream = new AudioStream(audioTrack, source);
            Debug.Log($"Playing audio from {participant.Identity}");
        }
    }
}
```

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

    private IEnumerator HandleIncomingByteStream(ByteStreamReader reader, string participantIdentity)
    {
        var info = reader.Info;
        Debug.Log($@"
        Byte stream received from {participantIdentity}
        Topic: {info.Topic}
        Timestamp: {info.Timestamp}
        ID: {info.Id}
        Size: {info.TotalLength} (if sent with SendFile)
        ");

        // Option 1: Process incrementally
        var readIncremental = reader.ReadIncremental();
        while (true)
        {
            readIncremental.Reset();
            yield return readIncremental;
            if (readIncremental.IsEos) break; // End of Stream
            Debug.Log($"Next byte chunk length: {readIncremental.Bytes.Length}");
            // Process readIncremental.Bytes here
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
Clone the repository, initialize submodules, and either:
1.  Import the local `client-sdk-unity` folder into your Unity project via the package manager.
2.  Import via Git URL: `https://github.com/livekit/client-sdk-unity.git` in the Unity Package Manager.

### Building LiveKit Plugins Locally
If you need to build the native Rust FFI libraries locally:
*   Ensure `client-sdk-rust~` submodule is initialized and Rust toolchain is installed.
*   Use `BuildScripts~/build_ffi_locally.sh <platform> [build_type]` (e.g., `./BuildScripts~/build_ffi_locally.sh macos release`).
*   **Important**: After macOS builds, restart Unity to load the new `dylib`.

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