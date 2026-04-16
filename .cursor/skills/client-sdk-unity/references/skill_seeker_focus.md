# Skill Seeker distillation focus (injected for Gemini enhance)

> **Repo:** livekit/client-sdk-unity | **Pin:** v1.3.5

Prioritize accurate coverage of these English symbols and API names when rewriting SKILL.md:

## Room Connection
- `Room` (main class)
- `Room.Connect(url, token)`
- `Room.Disconnect()`
- `RoomOptions`
- `ConnectOptions`

## Participants
- `LocalParticipant`
- `RemoteParticipant`
- `ParticipantConnected` (event)
- `ParticipantDisconnected` (event)

## DataChannel (KEY for ParrotCarriers)
- `Room.LocalParticipant.PublishData(data, kind)`
- `Room.DataReceived` (event: `data, participant, kind`)
- `DataPacketKind.RELIABLE`
- `DataPacketKind.LOSSY`
- `DataTopic`
- JSON encoding/decoding patterns for structured data

## RPC (KEY for ParrotCarriers)
- `Room.RegisterRpcMethod(methodName, handler)`
- `Room.LocalParticipant.PerformRpc(PerformRpcParams)`
- `PerformRpcParams` (destinationIdentity, method, payload, responseTimeout)
- `RpcInvocationData` (requestId, callerIdentity, payload, responseTimeout)
- `RpcError` (code, message)
- Error codes: 1400 UNSUPPORTED_METHOD, 1401 RECIPIENT_NOT_FOUND, 1402 REQUEST_PAYLOAD_TOO_LARGE, 1500 APPLICATION_ERROR, 1502 RESPONSE_TIMEOUT

## Tracks
- `TrackPublished` (event)
- `TrackSubscribed` (event)
- `TrackUnsubscribed` (event)
- `AudioSource`
- `AudioStream`
- `VideoStream`
- `TrackKind.Audio` / `TrackKind.Video`
- `EnableCameraAndMicrophone()`

## What to focus on for ParrotCarriers:
1. **DataChannel Reliable vs Lossy** — Reliable for RPC-like commands (body_cmd, state_sync); Lossy for high-freq telemetry (pose, ar_telemetry at 10Hz)
2. **RPC pattern** — Brain Agent sends function_tool results as RPC to Unity (dance, flyTo, etc.)
3. **DataReceived event** — Unity → Python telemetry path
4. **Room lifecycle** — Connect/Disconnect, handling reconnection
5. SDK is in "Developer Preview" — APIs may change, note any instability
6. Notable open PRs: Data tracks support (#193), audio ring buffer (#207)
