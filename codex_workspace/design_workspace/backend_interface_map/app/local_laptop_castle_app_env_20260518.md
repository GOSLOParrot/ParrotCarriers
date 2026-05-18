# Local Laptop Castle Sandbox (Unity App)

Status: implemented as an isolated local environment scaffold on 2026-05-18.
Base services were started and probed on laptop IP `192.168.2.4`:
token-mint `/health` 200, orchestrator `/health` 200, and App API
`/api/app/room-setting` 200. Brain remains opt-in until local API keys are
added.

Purpose: compare iQOO / Unity App audio, LiveKit, and Brain latency against a
laptop-hosted Castle-like stack without touching the public ECS `.env`, ECS
runtime config, or formal Unity `parrot_config.json`.

## Isolation Rules

- Do not run the public ECS compose file for this test. Use only
  `infra/laptop-castle.ps1`.
- Do not copy the repo root `.env` or ECS `.env.castle` into this environment.
  `infra/laptop.env.local` is generated from placeholders and is gitignored.
- Runtime data lives under
  `codex_workspace/local_runtime/castle_laptop/` and is gitignored.
- Seed data is copied once from `data/presets`, `data/line_profiles`, and
  `data/registries`; later RoomSetting saves stay inside the local runtime.
- Compose project name is fixed to `parrot-laptop-castle`, so Docker volumes
  and containers do not collide with ECS or old dev compose stacks.

## Ports

| Service | Phone/LAN URL | Host binding | Notes |
|:--|:--|:--|:--|
| LiveKit signaling | `ws://<laptop-ip>:17880` | `0.0.0.0:17880 -> 7880` | Returned to Unity by token-mint. |
| LiveKit TCP fallback | `<laptop-ip>:17881` | `0.0.0.0:17881 -> 7881` | WebRTC TCP fallback. |
| LiveKit UDP media | `<laptop-ip>:51000-51200/udp` | same range | Must be allowed by Windows firewall. |
| Token mint | `http://<laptop-ip>:17888` | `0.0.0.0:17888 -> 7888` | Uses local bearer secret. |
| Orchestrator | `http://<laptop-ip>:17890` | `0.0.0.0:17890 -> 7890` | Local Tier 1 prewrite only. |
| App API | `http://<laptop-ip>:18790` | `0.0.0.0:18790 -> 8790` | RoomSetting/menu HTTP facade. |
| Redis | laptop only | `127.0.0.1:16379 -> 6379` | Docker-internal clients use `redis:6379`. |
| FalkorDB | laptop only | `127.0.0.1:16380 -> 6379` | Docker-internal clients use `falkordb:6379`. |

## Commands

```powershell
# Generate infra/laptop.env.local, local data copy, and LiveKit node_ip config.
powershell -ExecutionPolicy Bypass -File infra/laptop-castle.ps1 -Action init

# Validate the compose config without starting containers.
powershell -ExecutionPolicy Bypass -File infra/laptop-castle.ps1 -Action config

# Start local RoomSetting/App API + LiveKit + token mint + orchestrator.
powershell -ExecutionPolicy Bypass -File infra/laptop-castle.ps1 -Action up

# Start Brain too, after adding a local GOOGLE_API_KEY to infra/laptop.env.local.
powershell -ExecutionPolicy Bypass -File infra/laptop-castle.ps1 -Action up-brain

# Print the Unity config JSON for this laptop sandbox.
powershell -ExecutionPolicy Bypass -File infra/laptop-castle.ps1 -Action unity-config
```

## Unity Config Contract

The generated Unity config is written to:

`codex_workspace/local_runtime/castle_laptop/parrot_config.laptop.generated.json`

Copying this into the gitignored formal App resource file is a manual test
step only:

`unity/ArSpike/Assets/ParrotApp/Resources/parrot_config.json`

Do not commit that runtime config. Do not overwrite the ECS config unless the
current phone test is explicitly switching to the laptop sandbox.

## LiveKit URL Split

Token-mint returns the phone-facing `LIVEKIT_URL`:

`ws://<laptop-ip>:17880`

But active Brain dispatch inside Docker calls the LiveKit server API through:

`PARROT_MINT_LIVEKIT_INTERNAL_URL=ws://livekit:7880`

This avoids a common local-Docker false failure where the phone needs the LAN
URL, while the container should use the Docker service name.

The generated LiveKit config pins `rtc.node_ip` to the laptop LAN IP and keeps
`rtc.use_external_ip: false`. This follows the LiveKit self-hosting config
shape where `node_ip` is used when external auto-discovery is not the desired
candidate source.

## What This Proves

Good for:

- comparing ECS vs laptop LiveKit/Brain latency;
- checking whether the 3-5s delay is cloud CPU/network related or phone/client
  capture related;
- testing Unity RoomSetting HTTP, token mint, LiveKit join, Brain dispatch,
  heartbeat, and audio uplink against a nearby SFU;
- testing iQOO Bluetooth/A2DP/SCO behavior without public ECS round trips.

Not proof of:

- public ECS security group / WAN reachability;
- production TLS/TURN;
- LineB Google STT / Cartesia unless local secrets and dependencies are added;
- phone stability until the formal App is rebuilt with the laptop config and
  iQOO logs show non-zero uplink frames/peak plus Brain response telemetry.

## Follow-Up TODO

- If laptop LineA is fast but ECS LineA remains slow, add explicit timing probes
  for client capture -> Brain STT/VAD/Realtime ingress -> LLM -> TTS/downlink.
- If both laptop and ECS stall after background/focus hops, continue the formal
  App lifecycle/audio-policy recovery work under APP-024.
- If local Docker LiveKit media still fails on phone, verify Windows firewall
  allows TCP 17880/17881 and UDP 51000-51200.
