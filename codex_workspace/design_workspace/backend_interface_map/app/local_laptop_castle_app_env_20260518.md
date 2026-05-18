# Local Laptop Castle Sandbox (Unity App)

Status: implemented and verified as an isolated local environment on
2026-05-18. Services were started on laptop IP `192.168.2.4`: token-mint
`/health` 200, orchestrator `/health` 200, and App API
`/api/app/room-setting` 200. After the user-approved local key copy into the
gitignored `infra/laptop.env.local`, Brain was also started and the local START
RPC proof passed in room `parrot-laptop-main`.

Purpose: compare iQOO / Unity App audio, LiveKit, and Brain latency against a
laptop-hosted Castle-like stack without touching the public ECS `.env`, ECS
runtime config, or formal Unity `parrot_config.json`.

## Isolation Rules

- Do not run the public ECS compose file for this test. Use only
  `infra/laptop-castle.ps1`.
- Do not copy the repo root `.env` or ECS `.env.castle` into this environment.
  `infra/laptop.env.local` is generated from placeholders and is gitignored.
- Do not print copied secrets in chat, logs, docs, or committed files. The local
  key copy is only for this laptop lab and is not a new shared deployment
  source of truth.
- Runtime data lives under
  `codex_workspace/local_runtime/castle_laptop/` and is gitignored.
- Seed data is copied once from `data/presets`, `data/line_profiles`, and
  `data/registries`; later RoomSetting saves stay inside the local runtime.
- Local preset/RoomProfile copies are rewritten to the local LiveKit room. This
  matters because Unity maps `RoomProfile.livekit_room_id` back into START
  `room_id` after RoomSetting cold-load; without the rewrite, a laptop test can
  accidentally re-enter the public `parrot-main` room.
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
| Photo upload | `http://<laptop-ip>:17889` | `0.0.0.0:17889 -> 7889` | Brain job-owned `photo_upload_server`; becomes healthy after a Unity/LiveKit room job starts. |
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

# Start Brain too, after adding local secrets to infra/laptop.env.local.
powershell -ExecutionPolicy Bypass -File infra/laptop-castle.ps1 -Action up-brain

# Print the Unity config JSON for this laptop sandbox.
powershell -ExecutionPolicy Bypass -File infra/laptop-castle.ps1 -Action unity-config
```

## Unity Config Contract

The generated Unity config is written to:

`codex_workspace/local_runtime/castle_laptop/parrot_config.laptop.generated.json`

As of 2026-05-18, the laptop-generated Unity config also includes:

- `photoUploadUrl=http://<laptop-ip>:17889`
- `visualToolDevEnabled=true`
- `visualToolHttpEnabled=true`

This makes the local lab build usable for CAM upload smoke and BBox/MAG
developer-tool smoke. It is still not a production enablement decision; formal
phone/body-feel validation remains APP-024.

The active formal App config consumed by Unity is:

`unity/ArSpike/Assets/ParrotApp/Resources/parrot_config.json`

This file is under `Assets/**/Resources`, so Android builds bundle it into the
APK. On a phone, switching between public ECS and laptop Castle requires writing
the desired ignored config before `Build And Run`, then rebuilding/reinstalling.
It is not a runtime hot switch yet. In Editor, changes can be picked up after
Unity refresh / Play restart, but phone proof must be considered build-specific.

Use the switch helper instead of manual copy:

```powershell
# Show the current active Unity config without printing secrets.
powershell -ExecutionPolicy Bypass -File infra/switch-unity-app-config.ps1 -Target show

# Switch active config to this laptop sandbox for the next phone build.
powershell -ExecutionPolicy Bypass -File infra/switch-unity-app-config.ps1 -Target laptop

# Switch active config back to the backed-up public ECS profile.
powershell -ExecutionPolicy Bypass -File infra/switch-unity-app-config.ps1 -Target ecs
```

The helper stores the public ECS backup at:

`codex_workspace/local_runtime/unity_app_configs/parrot_config.ecs.local.json`

That path is gitignored. Do not commit runtime configs or paste real bearer
values into docs/chat. Two parallel installed Android apps would require
separate package IDs, for example a future `com.parrotcarriers.app.local`;
currently the formal package ID is shared, so each Build And Run replaces the
previous install on the phone.

### 2026-05-18 Switch Script Smoke

The switch helper was exercised with the real local profiles:

```powershell
powershell -ExecutionPolicy Bypass -File infra/switch-unity-app-config.ps1 -Target show
powershell -ExecutionPolicy Bypass -File infra/switch-unity-app-config.ps1 -Target ecs
powershell -ExecutionPolicy Bypass -File infra/switch-unity-app-config.ps1 -Target laptop
powershell -ExecutionPolicy Bypass -File infra/switch-unity-app-config.ps1 -Target show
```

Result:

- `show` printed only URLs, room, and `has*Secret` booleans.
- `ecs` restored the gitignored ECS backup at
  `codex_workspace/local_runtime/unity_app_configs/parrot_config.ecs.local.json`
  and showed public ECS URLs / `parrot-main`.
- `laptop` restored the laptop generated profile and showed
  `192.168.2.4` URLs / `parrot-laptop-main`.
- Final active Unity config was intentionally left on laptop Castle for the
  next iQOO local latency/audio-route build.

## Environment Matrix

| Surface | Public ECS | Laptop Castle |
|:--|:--|:--|
| Purpose | Main remote dev Castle and Web/App shared validation. | Local latency/audio-route comparison for iQOO. |
| Unity active config | Ignored `parrot_config.json` with `8.216.45.45` endpoints. | Ignored `parrot_config.json` generated from `parrot_config.laptop.generated.json`. |
| LiveKit room | `parrot-main` unless RoomProfile overrides. | `parrot-laptop-main`; copied RoomProfiles are rewritten to this room. |
| App API data | ECS `/opt/parrotcarriers/data/**`. | `codex_workspace/local_runtime/castle_laptop/data/**` mounted into Docker. |
| Runtime config | ECS runtime config / orchestrator state. | Local runtime config under `codex_workspace/local_runtime/castle_laptop/**`. |
| Secrets | ECS `.env` / `.env.castle`; never copied into git. | `infra/laptop.env.local`; gitignored local lab only. |
| Web Console | Should target ECS unless explicitly switched by Web BFF env/profile. | Requires Web Console environment selector/proxy work before it is a first-class Web target. |

Setting file refs and persona refs can still be repo-relative paths such as
`src/parrot/brain/personas/**` or `codex_workspace/design_workspace/**`. In the
laptop Docker lab, those refs are only valid if the image/container can see the
same repo content. Treat Obsidian scan, setting-file upload, Graphiti/FalkorDB,
and Web Console edits as environment-scoped operations: the Web side must make
the chosen target visible and must not silently write local-lab changes into
public ECS or vice versa.

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

## 2026-05-18 Verification

Local Docker Desktop stack:

- `parrot-laptop-castle` containers are isolated from the ECS compose project.
- Token-mint returns the phone-facing URL `ws://192.168.2.4:17880` while using
  `PARROT_MINT_LIVEKIT_INTERNAL_URL=ws://livekit:7880` for server-side active
  dispatch.
- Minted Unity tokens bind to `parrot-laptop-main` and do not include a token
  `roomConfig`; Brain dispatch is requested server-side through LiveKit
  AgentDispatch.
- The Brain worker uses the named agent path (`parrot-brain`) for explicit
  active dispatch; one Brain participant joined and no duplicate `7889`
  photo-upload crash occurred during the START proof.
- The laptop Brain compose profile now exposes the job-owned photo upload
  server as `0.0.0.0:17889 -> 7889`, with cache root `/app/data/photos`.
  A `sim_unity_client.py --startup-rpc-check` run triggered a Brain room job,
  after which `http://192.168.2.4:17889/health` returned
  `{"status":"ok","service":"photo-upload"}`.
- `app-monitor` now reads live-state and L2-B from the active Brain room job by
  proxying to the job-owned photo upload server (`http://brain:7889`). A real
  LiveKit ECP probe published `photo.taken_preview`, uploaded bytes through
  HTTP, and Web/app-monitor refresh saw the resulting `PhotoNode` with a filled
  `/app/data/photos/2026-05-18/ph_probe_*.jpg` `reference_image_path`.
- App API and Brain read `/app/data/presets` and `/app/data/line_profiles`
  through `PARROT_PRESETS_DIR` / `PARROT_LINE_PROFILES_DIR`, not image-baked
  repo data.
- The local runtime writer uses UTF-8 without BOM for generated JSON/YAML so the
  Python loaders do not fall back to hardcoded defaults.

Observed local proof:

- `sim_unity_client.py --startup-rpc-check --startup-room-profile-id default
  --identity laptop-start-local-room --agent-name parrot-brain` connected to
  `ws://127.0.0.1:17880` room `parrot-laptop-main`.
- `GET /api/app/room-setting` now returns both `default` and `ner_lineb_room`
  with `livekit_room_id=parrot-laptop-main`.
- Brain participant `agent-*` joined, agent audio track appeared, and
  `applyRoomProfile` plus `setAppCapabilityMode` returned business-ok payloads.
- The earlier accidental rerun against default `parrot-main` is not the
  canonical laptop proof; use `LIVEKIT_ROOM=parrot-laptop-main` for this lab.

Residual diagnostics, not current blockers for local START:

- LiveKit logs still display the registered worker with an empty `agentName`
  while `CreateDispatch` carries `agentName: parrot-brain`; assignment works,
  but this log mismatch should be rechecked before changing dispatch semantics.
- `AgentDispatchService.ListDispatch` may return a transient 503 before a room
  exists; token-mint handles that and proceeds to create the active dispatch.
- Brain boot preflight can log a Blackboard write-access warning for
  `/global/brain_boot_preflight`; it did not block START but should be cleaned
  separately.

## What This Proves

Good for:

- comparing ECS vs laptop LiveKit/Brain latency;
- checking whether the 3-5s delay is cloud CPU/network related or phone/client
  capture related;
- testing Unity RoomSetting HTTP, token mint, LiveKit join, Brain dispatch, and
  startup Brain RPC business-ok against a nearby SFU;
- testing iQOO Bluetooth/A2DP/SCO behavior without public ECS round trips.

Not proof of:

- public ECS security group / WAN reachability;
- production TLS/TURN;
- LineB Google STT / Cartesia quality unless that specific room/profile is
  selected and measured locally;
- phone stability until the formal App is rebuilt with the laptop config and
  iQOO logs show non-zero uplink frames/peak plus Brain response telemetry;
- final APP-024 phone/body-feel acceptance for BBox/MAG/photo HUD timing. The
  laptop proof closes the HTTP/ECP/L2-B read path, not the production touch
  tuning pass.

## Follow-Up TODO

- If laptop LineA is fast but ECS LineA remains slow, add explicit timing probes
  for client capture -> Brain STT/VAD/Realtime ingress -> LLM -> TTS/downlink.
- Before judging ECS capacity, copy the generated laptop config into the
  gitignored formal Unity runtime config for one phone build and compare the
  same LineA route on iQOO.
- If both laptop and ECS stall after background/focus hops, continue the formal
  App lifecycle/audio-policy recovery work under APP-024.
- If local Docker LiveKit media still fails on phone, verify Windows firewall
  allows TCP 17880/17881 and UDP 51000-51200.
