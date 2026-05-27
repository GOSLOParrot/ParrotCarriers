# APP-026 BBox/MAG Visual Tool App Work Log (2026-05-17)

Status: implementation workbench, not SSOT
Owner: Unity App chat
Workspace: `unity/ArSpike`

## Three-Tool Understanding

CAM / Photo is the formal camera capture path. `FormalHomeToolController`
should stay the CAM owner and delegate image capture to `PhotoController`.
Photo emits compact `photo.taken_preview` ECP metadata and uploads the full
JPEG through HTTP/storage. It must not use `captureSnapshot` RPC or send image
bytes through ECP/RPC. Remaining App gap: upload timebase headers.

BBox is a strong visual evidence tool. Drag, resize, hover, and selection are
Unity-local body feel. Stable semantic phases go to
`/api/app/visual-tool/event` or later ECP `visual_tool.lifecycle`. Confirm and
explicit send default to IntentWorkspace staging plus C3 no-interrupt notice
when backend policy allows. Optional crop/preview bytes must go first to
`/api/app/visual-tool/asset/{asset_id}`, then the returned `asset_path` is
attached to the lifecycle event.

MAG is a weak focus / reading inspection tool. The magnifier glass is mostly
local rendering and user inspection. Confirm defaults to IntentWorkspace only;
`explicit_send` or `delivery_preference=c3` asks backend for C3 no-interrupt
notice. MAG maps to Focus-family refs in backend V1 and should not spam backend
while the user moves the lens.

## Implementation-Prep Research

Read before code:

- `app_evidence_tools_bbox_mag_photo_intent_workspace_20260515.md`
- `time_aligned_evidence_interface_20260515.md`
- `goslo_trigger_awareness_taxonomy_20260515.md`
- `core_interface_candidate_queue_20260513.md`
- `APP_WEB_PARALLEL_TODOLIST_20260513.md`
- `formal_homepage_hud_menu_plan_20260515.md`
- `unity_app_transport_interface_taxonomy_20260515.md`
- `unity_livekit_ecp_sva_data_flow_map_20260515.md`
- Current Unity scripts: `FormalHomeToolController`, `FormalHomeMenuController`,
  `AppHomeMenuClient`, `PhotoController`, `BBoxController`, `FocusController`,
  `EcpEventPublisher`.
- Backend tests/routes: `test_visual_tool_lifecycle.py`,
  `test_app_v1_monitor.py`, `app_monitor_server.py`,
  `tool_lifecycle.py`.

Findings:

- Backend CORE-014 is no longer blocking App controller implementation.
- Current formal toolbar intentionally defers MAG/BOX and keeps CAM active.
- Existing `BBoxController` / `FocusController` are compatibility pulse
  publishers (`bbox.placed`, `focus.anchored`), not production lifecycle
  controllers for drag/resize/dwell/confirm.
- Unity MCP is connected to `ArSpike@a0c0295f7bd40ecc`; active scene is
  `Assets/ParrotApp/Scenes/ParrotApp_Startup.unity`; console currently has no
  errors. The scene can be used for compile/console validation after edits.
- `git status` is already dirty in unrelated App/Web/backend areas. This work
  must keep edits scoped and avoid reverting other changes.

## TODO

1. Add App-side visual-tool packet builder for timebase, screen-normalized
   region, phase, delivery preference, optional pose/asset fields.
2. Add App HTTP wrapper for lifecycle events and visual-tool asset upload,
   using App API URL/auth from `parrot_config`.
3. Add feature/dev flags in runtime config; default disabled.
4. Add BBox and MAG controller skeletons separate from
   `FormalHomeToolController`; keep high-frequency state local.
5. Add minimal HUD diagnostics under the dev flag: local render status and last
   HTTP lifecycle/asset result. This is a diagnostic signal only, not APP-024
   phone proof.
6. Wire toolbar MAG/BOX to the new controllers only when the dev flag is on;
   otherwise preserve the deferred phone-stability status.
7. Add static guard coverage: no `captureSnapshot`, no image bytes in ECP/RPC,
   no direct L2-B/Graphiti/IntentWorkspace writes, and no legacy
   `bbox.placed`/`focus.anchored` calls from the formal tool path.
8. Optional if scope remains safe: add Photo upload `X-Parrot-Timebase` header.
9. Run focused static tests and Unity compile/console check.
10. Record post-TODO audit below.

## Post-TODO Audit Slot

Implementation completed in this slice:

- Added `Assets/ParrotApp/Runtime/Scripts/VisualTools/**`.
- `VisualToolPacketBuilder` builds CORE-014 lifecycle packets with
  screen-normalized region, Unity timebase, delivery preference, optional
  asset refs, and no binary payload.
- `VisualToolHttpClient` wraps:
  - `POST /api/app/visual-tool/event`
  - `POST /api/app/visual-tool/asset/{asset_id}`
  It applies App API bearer auth from `parrot_config`, uses byte upload only
  over HTTP, and attaches `X-Parrot-Timebase` / `X-Parrot-Region` headers for
  asset uploads.
- `BBoxVisualToolController` and `MagnifierVisualToolController` are separate
  from `FormalHomeToolController` and default behind
  `visualToolDevEnabled=false`.
- Toolbar MAG/BOX calls the new controllers only through the dev-flag path;
  flag-off status still reads as phone-stability deferred.
- Local drag/resize/dwell state stays Unity-local by default. Low-frequency
  update emission exists but is disabled unless explicitly enabled.
- Dev HUD overlays show local render readiness plus last HTTP event/asset
  status. This is diagnostic visibility, not a phone proof claim.
- `PhotoController` now adds `X-Parrot-Timebase` on HTTP photo upload and
  preserves it for reconnect retry.

Guardrails rechecked:

- No `captureSnapshot` / `CaptureSnapshot` was added.
- No image bytes are sent by ECP/RPC.
- No direct Unity writes to IntentWorkspace, Blackboard, Graphiti, or L2-B were
  added.
- Formal CAM/Photo remains owned by `FormalHomeToolController` +
  `PhotoController`; BBox/MAG are separate `VisualTools`.
- Legacy `bbox.placed` / `focus.anchored` controllers remain untouched as
  compatibility/reference code and are not called from the new formal path.

Verification:

- `uv run pytest tests/test_unity/test_app_v1_meta_ui_static.py -q` -> 28
  passed.
- `uv run pytest tests/test_brain/test_visual_tool_lifecycle.py
  tests/test_brain/test_app_v1_monitor.py::test_console_action_endpoints_drive_app_tool_flows
  tests/test_ecp_event/test_w8_photo_upload_server.py::test_upload_publishes_photo_timebase_metadata
  tests/test_ecp_event/test_w8_observer_photo.py::test_asset_uploaded_timebase_metadata_reaches_evidence_ledger
  -q` -> 7 passed.
- Unity MCP `refresh_unity` on `ArSpike@a0c0295f7bd40ecc` completed ready with
  0 Console errors. Remaining warnings are the unrelated existing audio
  unused-field warnings.

## Requirements Trace Audit 12 - Original Workspace Docs (2026-05-17)

Sources rechecked:

- `app_evidence_tools_bbox_mag_photo_intent_workspace_20260515.md`
- `time_aligned_evidence_interface_20260515.md`
- `goslo_trigger_awareness_taxonomy_20260515.md`
- `core_interface_candidate_queue_20260513.md`
- `APP_WEB_PARALLEL_TODOLIST_20260513.md`
- `formal_homepage_hud_menu_plan_20260515.md`
- `unity_app_transport_interface_taxonomy_20260515.md`
- `unity_livekit_ecp_sva_data_flow_map_20260515.md`
- `app_web_parallel_workflow_20260513.md`

Conclusion:

- Current App implementation matches the CORE-014 App V1 scope: real
  feature-flagged BBox/MAG controller skeletons, packet builder, HTTP lifecycle
  client, optional HTTP asset upload before lifecycle, local high-frequency
  interaction, BBox strong/default confirm, MAG intent-only confirm and C3
  explicit send.
- The older 2026-05-13 homepage requirement that MAG/BOX stay deferred is now
  superseded for controller work by the 2026-05-15/16 CORE-014 backend-ready
  requirement, but it still applies to production enablement. Default runtime
  config keeps `visualToolDevEnabled=false`, and the HUD/menu still reports
  flag-off / phone-stability status unless explicitly enabled.
- No App code writes IntentWorkspace, Blackboard, Graphiti, or L2-B directly;
  no `captureSnapshot`, `identify_object`, C4 send constant, legacy
  `bbox.placed` / `focus.anchored` call, or image bytes over ECP/RPC are present
  in the new VisualTools/formal camera/menu path.
- CAM/Photo remains isolated in `FormalHomeToolController` + `PhotoController`;
  BBox/MAG live under `Runtime/Scripts/VisualTools/**`.

Remaining gates:

- APP-024 phone/screen-share smoke is still not done and remains the production
  enablement blocker for active BBox/MAG toolbar emission.
- MAG body-feel is still a dev lens/zoom/controller scaffold with optional
  screen-region asset probe, not a final tuned production magnifier experience.
- True on-device HTTP/network/render proof must be collected before claiming
  phone-ready; current proof is static/backend tests plus Unity Editor console.

Verification for this audit:

- `uv run pytest tests/test_unity/test_app_v1_meta_ui_static.py
  tests/test_brain/test_visual_tool_lifecycle.py
  tests/test_brain/test_app_v1_monitor.py::test_console_action_endpoints_drive_app_tool_flows
  tests/test_ecp_event/test_w8_photo_upload_server.py::test_upload_publishes_photo_timebase_metadata
  tests/test_ecp_event/test_w8_observer_photo.py::test_asset_uploaded_timebase_metadata_reaches_evidence_ledger
  -q` -> 35 passed.
- Unity MCP active instance: `ArSpike@a0c0295f7bd40ecc`, Unity `2022.3.62f3`,
  active scene `Assets/ParrotApp/Scenes/ParrotApp_Startup.unity`,
  not compiling, Console error entries: 0.
- `git diff --check` on the touched App/test files reports only existing
  LF/CRLF normalization warnings.

## Bugfix Pass 13 - Camera Mode Pending Does Not Commit UI State (2026-05-17)

Bug found:

- The App transport taxonomy says camera mode changes go through App HTTP and
  UI state updates only after HTTP business success.
- `FormalCameraModeController.RequestModeApply()` and the menu quick camera
  action were optimistically calling `SetModeLocal(nextMode)` before
  `/api/app/**` returned. That could make the HUD/overlay look committed even
  if backend camera-mode apply failed.

Fix:

- Camera mode requests now call `MarkHttpPending()` first and keep the current
  local mode unchanged while HTTP is in flight.
- `MarkHttpPending()` only opens a pending overlay for non-off target modes so
  the user sees progress without committing the mode.
- `SetModeLocal()` is now reached on HTTP success, capture success, snapshot
  sync, or explicit failure rollback, not during the initial request.
- Static tests now forbid `SetModeLocal(nextMode)` in `CycleCameraMode()` and
  forbid `SetModeLocal(normalized)` inside `RequestModeApply()`.

Verification:

- `uv run pytest tests/test_unity/test_app_v1_meta_ui_static.py -q` -> 28
  passed.
- `uv run pytest tests/test_unity/test_app_v1_meta_ui_static.py
  tests/test_brain/test_visual_tool_lifecycle.py
  tests/test_brain/test_app_v1_monitor.py::test_console_action_endpoints_drive_app_tool_flows
  tests/test_ecp_event/test_w8_photo_upload_server.py::test_upload_publishes_photo_timebase_metadata
  tests/test_ecp_event/test_w8_observer_photo.py::test_asset_uploaded_timebase_metadata_reaches_evidence_ledger
  -q` -> 35 passed.
- Forbidden-path scan across VisualTools, formal camera/menu/HUD/tool, and
  runtime config found no active `captureSnapshot`, `identify_object`, C4 send
  constant, direct Brain memory writes, or legacy BBox/Focus pulse calls.
- Unity MCP `refresh_unity` on `ArSpike@a0c0295f7bd40ecc` completed with no
  Console compile errors. The visible entries are existing Android 16KB
  alignment / Samples cache warnings.

## Bugfix Pass 14 - Visual Tool HTTP Error Body Visibility (2026-05-17)

Bug found:

- `VisualToolHttpClient` discarded backend JSON error bodies when HTTP returned
  a non-2xx status.
- The HUD/status would show only the Unity transport error, making APP-024
  device smoke hard to distinguish between auth, payload validation, and backend
  policy rejection.

Fix:

- Lifecycle and asset-upload HTTP transport failures now call
  `RequestErrorLabel()`.
- `RequestErrorLabel()` prefers backend `error` / `detail` JSON fields, then
  falls back to the HTTP transport/status label, then to the local fallback
  label.
- Static tests now guard that both lifecycle and asset upload request-error
  paths use the backend-aware label helper.

Verification:

- `uv run pytest tests/test_unity/test_app_v1_meta_ui_static.py -q` -> 28
  passed.
- `uv run pytest tests/test_unity/test_app_v1_meta_ui_static.py
  tests/test_brain/test_visual_tool_lifecycle.py
  tests/test_brain/test_app_v1_monitor.py::test_console_action_endpoints_drive_app_tool_flows
  tests/test_ecp_event/test_w8_photo_upload_server.py::test_upload_publishes_photo_timebase_metadata
  tests/test_ecp_event/test_w8_observer_photo.py::test_asset_uploaded_timebase_metadata_reaches_evidence_ledger
  -q` -> 35 passed.
- Forbidden-path scan across VisualTools, formal camera/menu/HUD/tool, and
  runtime config found no active `captureSnapshot`, `identify_object`, C4 send
  constant, direct Brain memory writes, or legacy BBox/Focus pulse calls.
- Unity MCP `refresh_unity` on `ArSpike@a0c0295f7bd40ecc` completed with 0
  Console error entries after domain reload.

## Bugfix Pass 15 - Backend Shape And Asset Metadata Alignment (2026-05-17)

Pre-edit audit:

- Rechecked the real backend route and DTO shape in
  `app_monitor_server.py` and `tool_lifecycle.py`.
- Confirmed `/api/app/visual-tool/event` accepts `VisualToolLifecyclePacket`
  with `pose` and `meta` typed as dictionaries, and `/asset/{asset_id}` parses
  optional source-surface / source-id / description headers for evidence
  metadata.

Bug found:

- Unity `ObjectJson()` accepted JSON arrays for `pose_json` and `meta_json`.
  The current local callers pass objects, but the packet builder could produce
  `pose: []` / `meta: []`, which backend V1 would reject because those fields
  are `dict`.
- Asset uploads sent tool id/kind/phase/timebase/region headers, but did not
  send source surface, source id, or description even though the backend route
  consumes them.

Fix:

- `ObjectJson()` now accepts object-shaped JSON only and falls back to `{}` for
  array-shaped input.
- Asset upload now sends `X-Parrot-Source-Surface`,
  `X-Parrot-Source-Id`, and `X-Parrot-Description` alongside the existing
  tool/timebase/region headers.
- Static tests now guard the object-only packet-builder behavior and the new
  asset metadata headers.

Verification:

- `uv run pytest tests/test_unity/test_app_v1_meta_ui_static.py
  tests/test_brain/test_visual_tool_lifecycle.py
  tests/test_brain/test_app_v1_monitor.py::test_console_action_endpoints_drive_app_tool_flows
  tests/test_ecp_event/test_w8_photo_upload_server.py::test_upload_publishes_photo_timebase_metadata
  tests/test_ecp_event/test_w8_observer_photo.py::test_asset_uploaded_timebase_metadata_reaches_evidence_ledger
  -q` -> 35 passed.
- Unity MCP `refresh_unity` on `ArSpike@a0c0295f7bd40ecc` recovered after an
  automatic Unity reconnect and completed ready; Console error entries: 0.
- Forbidden-path scan across VisualTools and formal camera/menu/HUD/tool/runtime
  config found no `captureSnapshot`, C4 send constant, direct Brain memory
  writes, legacy BBox/Focus pulse calls, or image-byte RPC/ECP marker.
- `git diff --check` on touched files reports only LF/CRLF normalization
  warnings.

## Bugfix Pass 16 - Drop Stale Async Visual Tool Semantics (2026-05-17)

Pre-edit audit:

- Rechecked BBox/MAG runtime event ordering around `IMG` / asset-backed C3,
  cancel/release, and startup transitions.
- Found that screen-region capture and asset upload are coroutine based. A user
  could tap `IMG`, then cancel/release or trigger a startup transition before
  the coroutine finished.

Bug found:

- Old non-terminal async work could still emit `confirm` / `explicit_send`
  after the tool had already been released or a new interaction session had
  started.
- That could invert the intended semantic order: `release` followed by a stale
  `confirm`.

Fix:

- Added an interaction-generation gate to `VisualToolControllerBase`.
- New preview/local sessions advance the generation; cancel/release sends its
  terminal lifecycle with the closing generation, then invalidates pending
  non-terminal work.
- Asset capture/upload/lifecycle coroutines check the generation before upload,
  before fallback lifecycle emission, and before applying HTTP completion state.
- Terminal cancel/release can still send its lifecycle, but stale terminal
  completions will not overwrite a newer open session's HUD state.

Verification:

- `uv run pytest tests/test_unity/test_app_v1_meta_ui_static.py
  tests/test_brain/test_visual_tool_lifecycle.py
  tests/test_brain/test_app_v1_monitor.py::test_console_action_endpoints_drive_app_tool_flows
  tests/test_ecp_event/test_w8_photo_upload_server.py::test_upload_publishes_photo_timebase_metadata
  tests/test_ecp_event/test_w8_observer_photo.py::test_asset_uploaded_timebase_metadata_reaches_evidence_ledger
  -q` -> 35 passed.
- Forbidden-path scan across VisualTools and formal camera/menu/HUD/tool/runtime
  config found no `captureSnapshot`, C4 send constant, direct Brain memory
  writes, legacy BBox/Focus pulse calls, or image-byte RPC/ECP marker.
- Unity MCP `refresh_unity` on `ArSpike@a0c0295f7bd40ecc` recovered after an
  automatic Unity reconnect and completed ready; Console error entries: 0.
- `git diff --check` on touched files reports only LF/CRLF normalization
  warnings.

## Bugfix Pass 17 - Keep Dev Overlay Creation Behind Feature/Open State (2026-05-17)

Pre-edit audit:

- Rechecked runtime mounting and startup behavior after the async generation
  gate.
- Found that `VisualToolControllerBase.Start()` calls `UpdateOverlay()`.
  BBox/MAG `UpdateOverlay()` immediately called `EnsureOverlay()`, which creates
  dev canvases and an EventSystem even when `visualToolDevEnabled=false` and the
  tools are not open.

Bug found:

- Feature-disabled BBox/MAG could still touch UI/input infrastructure at
  startup. That was too leaky for the requirement to keep the controllers behind
  a dev flag and avoid disturbing CAM/Photo.

Fix:

- BBox and MAG now return from `UpdateOverlay()` before `EnsureOverlay()` when
  the dev canvas does not exist and either the feature flag is disabled or the
  tool is not open.
- Existing canvases still get hidden if the flag/open state changes, but
  flag-off startup no longer creates BBox/MAG overlay UI or EventSystem state.
- Static tests now guard that both visual-tool overlays gate `EnsureOverlay()`
  behind `FeatureEnabled && IsOpen` when no canvas exists.

Verification:

- `uv run pytest tests/test_unity/test_app_v1_meta_ui_static.py
  tests/test_brain/test_visual_tool_lifecycle.py
  tests/test_brain/test_app_v1_monitor.py::test_console_action_endpoints_drive_app_tool_flows
  tests/test_ecp_event/test_w8_photo_upload_server.py::test_upload_publishes_photo_timebase_metadata
  tests/test_ecp_event/test_w8_observer_photo.py::test_asset_uploaded_timebase_metadata_reaches_evidence_ledger
  -q` -> 35 passed.
- Forbidden-path scan across VisualTools and formal camera/menu/HUD/tool/runtime
  config found no `captureSnapshot`, C4 send constant, direct Brain memory
  writes, legacy BBox/Focus pulse calls, or image-byte RPC/ECP marker.
- Unity MCP `refresh_unity` on `ArSpike@a0c0295f7bd40ecc` recovered after an
  automatic Unity reconnect and completed ready; Console error entries: 0.
- `git diff --check` on touched files completed cleanly.

## Bugfix Pass 18 - App-Side Lifecycle Phase Whitelist (2026-05-17)

Pre-edit audit:

- Re-read the original App request and CORE-014 notes around stable semantic
  phases.
- Found that `UpdateLocalRegion(region, updatePhase)` was public and could
  emit whichever phase string a future caller supplied whenever low-frequency
  update events were enabled.
- `VisualToolPhases` also still exposed `hover` / `settings_open` constants
  even though this App controller slice intentionally keeps hover/settings UI
  local and only sends stable milestones plus necessary low-frequency updates.

Bug found:

- A future App caller could accidentally send a non-approved lifecycle phase to
  `/api/app/visual-tool/event`, weakening the "do not spam backend / stable
  semantic stages only" boundary.

Fix:

- Removed unused App-side `Hover` and `SettingsOpen` phase constants from the
  Unity packet builder.
- Added a lifecycle phase allow-list in `VisualToolControllerBase` covering only
  `preview_start`, `lock`, `unlock`, `confirm`, `explicit_send`, `cancel`,
  `release`, and optional low-frequency `dwell_tick` / `drag_update` /
  `resize_update`.
- Normalized public local region update calls to `drag_update` or
  `resize_update` before any low-frequency HTTP emission.
- Added static tests so the App send path keeps this white-list boundary.

Verification:

- `uv run pytest tests/test_unity/test_app_v1_meta_ui_static.py -q` -> 28
  passed.
- `uv run pytest tests/test_brain/test_visual_tool_lifecycle.py
  tests/test_brain/test_app_v1_monitor.py::test_console_action_endpoints_drive_app_tool_flows
  tests/test_ecp_event/test_w8_photo_upload_server.py::test_upload_publishes_photo_timebase_metadata
  tests/test_ecp_event/test_w8_observer_photo.py::test_asset_uploaded_timebase_metadata_reaches_evidence_ledger
  -q` -> 7 passed.
- Forbidden-path scan across VisualTools and formal camera/menu/HUD/tool/runtime
  config found no `captureSnapshot`, C4 send constant, direct Brain memory
  writes, legacy BBox/Focus pulse calls, image-byte RPC/ECP marker, or
  App-side `Hover` / `SettingsOpen` phase constants.
- Unity MCP script validation: `VisualToolControllerBase.cs` and
  `VisualToolPacketBuilder.cs` have 0 errors; base-controller warnings are
  pre-existing broad static hints about `FindObjectOfType` / string
  concatenation.
- Unity MCP `refresh_unity` on `ArSpike@a0c0295f7bd40ecc` recovered after an
  automatic Unity reconnect and completed ready; Console error entries: 0.
- `git diff --check` on touched files completed cleanly, with only LF/CRLF
  normalization warnings.

## Bugfix Pass 19 - Public Region Update Opens With Preview Start (2026-05-17)

Pre-edit audit:

- Continued the Pass 18 audit around `UpdateLocalRegion()`.
- Found that the method could be called while the tool was closed. It opened
  local state and, if low-frequency update events were enabled, could make the
  first backend event a `drag_update` or `resize_update`.

Bug found:

- A future external BBox/MAG caller could bypass the `preview_start` lifecycle
  milestone even though it had just opened the tool surface.

Fix:

- `UpdateLocalRegion()` now detects closed-state entry, sets the supplied
  region first, opens/selects the local tool, and emits `preview_start` with
  that current region.
- The optional low-frequency `drag_update` / `resize_update` path is only used
  after the tool is already open.
- Static tests now guard that closed-state region updates return
  `preview_start` before the low-frequency update branch.

Verification:

- `uv run pytest tests/test_unity/test_app_v1_meta_ui_static.py -q` -> 28
  passed.
- `uv run pytest tests/test_brain/test_visual_tool_lifecycle.py
  tests/test_brain/test_app_v1_monitor.py::test_console_action_endpoints_drive_app_tool_flows
  tests/test_ecp_event/test_w8_photo_upload_server.py::test_upload_publishes_photo_timebase_metadata
  tests/test_ecp_event/test_w8_observer_photo.py::test_asset_uploaded_timebase_metadata_reaches_evidence_ledger
  -q` -> 7 passed.
- Forbidden-path scan across VisualTools and formal camera/menu/HUD/tool/runtime
  config found no `captureSnapshot`, C4 send constant, direct Brain memory
  writes, legacy BBox/Focus pulse calls, image-byte RPC/ECP marker, or
  App-side `Hover` / `SettingsOpen` phase constants.
- Unity MCP script validation: `VisualToolControllerBase.cs` and
  `VisualToolPacketBuilder.cs` have 0 errors; base-controller warnings are
  pre-existing broad static hints about `FindObjectOfType` / string
  concatenation.
- Unity MCP `refresh_unity` on `ArSpike@a0c0295f7bd40ecc` recovered after an
  automatic Unity reconnect and completed ready; Console error entries: 0.
- `git diff --check` on touched files completed cleanly, with only LF/CRLF
  normalization warnings.

## Bugfix Pass 20 - Ignore Older HTTP Completion Statuses (2026-05-17)

Pre-edit audit:

- Continued auditing same-interaction lifecycle ordering after the
  `preview_start` entry fix.
- Found that multiple stable lifecycle HTTP requests can be in flight at once
  during natural App use, for example `preview_start` followed quickly by
  `confirm` or asset-backed `explicit_send`.

Bug found:

- An older HTTP completion could arrive after a newer semantic phase and write
  stale local HUD/status text, making a confirmed/asset-backed tool appear to
  have regressed to `preview_start_sent` or another earlier phase.

Fix:

- Added a local-only semantic sequence counter in
  `VisualToolControllerBase`.
- Each outbound lifecycle/capture/upload flow gets a sequence value when it is
  queued.
- Older completions are still allowed to finish their backend HTTP path, but
  they no longer overwrite `LastStatus`, `LastHttpStatus`, `LastAssetStatus`,
  `LastRenderStatus`, or `LastReceiptJson` after a newer semantic action has
  been queued.
- Existing interaction-generation checks still own cancel/release stale-work
  cancellation, so backend semantics and local HUD ordering remain separate.

Verification:

- `uv run pytest tests/test_unity/test_app_v1_meta_ui_static.py -q` -> 28
  passed.
- `uv run pytest tests/test_brain/test_visual_tool_lifecycle.py
  tests/test_brain/test_app_v1_monitor.py::test_console_action_endpoints_drive_app_tool_flows
  tests/test_ecp_event/test_w8_photo_upload_server.py::test_upload_publishes_photo_timebase_metadata
  tests/test_ecp_event/test_w8_observer_photo.py::test_asset_uploaded_timebase_metadata_reaches_evidence_ledger
  -q` -> 7 passed.
- Forbidden-path scan across VisualTools and formal camera/menu/HUD/tool/runtime
  config found no `captureSnapshot`, C4 send constant, direct Brain memory
  writes, legacy BBox/Focus pulse calls, image-byte RPC/ECP marker, or
  App-side `Hover` / `SettingsOpen` phase constants.
- Unity MCP script validation: `VisualToolControllerBase.cs` and
  `VisualToolPacketBuilder.cs` have 0 errors; base-controller warnings are
  pre-existing broad static hints about `FindObjectOfType` / string
  concatenation.
- Unity MCP `refresh_unity` on `ArSpike@a0c0295f7bd40ecc` recovered after an
  automatic Unity reconnect and completed ready; Console error entries: 0.
- `git diff --check` on touched files completed cleanly, with only LF/CRLF
  normalization warnings.

## Bugfix Pass 21 - Local Body-Feel Interaction Hygiene (2026-05-17)

Pre-edit audit:

- Audited the BBox/MAG flow from a body-feel angle rather than only transport
  correctness.
- Re-read the visual-tool body-feel taxonomy: BBox confirm should feel like a
  deliberate strong mark; MAG should feel ambient/inspection-first, with C3 only
  on explicit send.

Issues found:

- If a semantic `lock`, `confirm`, or `explicit_send` happened while a pointer
  gesture was still active, BBox/MAG could keep internal drag/resize state until
  pointer release. That made the HUD/body feel say "still dragging" even after a
  lock/confirm.
- MAG closed-state `UpdateLocalRegion()` entry did not run the same dwell timer
  reset as `BeginPreview()`, so a newly opened lens could dwell-tick too soon.
- Overlapping screen-region asset captures could show the dev overlay between
  two pending captures, risking a crop/preview that includes tool UI.

Fix:

- Added local interaction hooks in `VisualToolControllerBase` for preview open,
  stable lock/confirm application, unlock, and close.
- BBox now ends the current local pointer gesture on preview open, lock/confirm,
  unlock, cancel, and release.
- MAG now resets local inspection timing on preview open, unlock, cancel, and
  release, and ends any active drag on lock/confirm/explicit send.
- Screen-region capture overlay hiding now uses a small depth counter, so
  overlapping captures do not restore the overlay until the last capture exits.
- Static tests now guard these body-feel hooks and the overlay hide-depth path.

Verification:

- `uv run pytest tests/test_unity/test_app_v1_meta_ui_static.py -q` -> 28
  passed.
- `uv run pytest tests/test_brain/test_visual_tool_lifecycle.py
  tests/test_brain/test_app_v1_monitor.py::test_console_action_endpoints_drive_app_tool_flows
  tests/test_ecp_event/test_w8_photo_upload_server.py::test_upload_publishes_photo_timebase_metadata
  tests/test_ecp_event/test_w8_observer_photo.py::test_asset_uploaded_timebase_metadata_reaches_evidence_ledger
  -q` -> 7 passed.
- Forbidden-path scan across VisualTools and formal camera/menu/HUD/tool/runtime
  config found no `captureSnapshot`, C4 send constant, direct Brain memory
  writes, legacy BBox/Focus pulse calls, image-byte RPC/ECP marker, or
  App-side `Hover` / `SettingsOpen` phase constants.
- Unity MCP script validation: `VisualToolControllerBase.cs`,
  `BBoxVisualToolController.cs`, and `MagnifierVisualToolController.cs` have 0
  errors; warnings are broad static hints about `FindObjectOfType` / string
  concatenation in update paths.
- Unity MCP `refresh_unity` on `ArSpike@a0c0295f7bd40ecc` recovered after an
  automatic Unity reconnect and completed ready; Console error entries: 0.
- `git diff --check` on touched files completed cleanly, with only LF/CRLF
  normalization warnings.

## Bugfix Pass 22 - Superseded Asset Flow Stops Before Crop/Upload (2026-05-17)

Pre-edit audit:

- Rechecked Pass 20/21 from a body-feel angle: local HUD/status was protected
  from older async completions, but asset-backed crop/upload flows could still
  keep running after a newer semantic action had been queued.

Bug found:

- If a user tapped `IMG` and then quickly changed their mind with `OK`, `C3`,
  cancel, or release, the older asset-backed flow could still hide the overlay,
  crop, upload bytes, and possibly emit the older asset lifecycle. That is
  technically traceable, but it feels wrong because the user's newer action
  should own the visible tool state.

Fix:

- `UploadAssetThenLifecycle()` now exits before upload if its semantic sequence
  has been superseded, and exits after upload before lifecycle emission if a
  newer semantic action arrived mid-flight.
- `CaptureScreenRegionAssetThenLifecycle()` now exits before hiding the overlay
  if already superseded, exits after the end-of-frame wait before reading pixels
  if superseded, and exits after capture before upload if superseded.
- Static tests now guard these early exits so asset-backed flows cannot revive a
  stale body-feel action path.

Verification:

- `uv run pytest tests/test_unity/test_app_v1_meta_ui_static.py -q` -> 28
  passed.
- `uv run pytest tests/test_brain/test_visual_tool_lifecycle.py
  tests/test_brain/test_app_v1_monitor.py::test_console_action_endpoints_drive_app_tool_flows
  tests/test_ecp_event/test_w8_photo_upload_server.py::test_upload_publishes_photo_timebase_metadata
  tests/test_ecp_event/test_w8_observer_photo.py::test_asset_uploaded_timebase_metadata_reaches_evidence_ledger
  -q` -> 7 passed.
- Forbidden-path scan across VisualTools and formal camera/menu/HUD/tool/runtime
  config found no `captureSnapshot`, C4 send constant, direct Brain memory
  writes, legacy BBox/Focus pulse calls, image-byte RPC/ECP marker, or
  App-side `Hover` / `SettingsOpen` phase constants.
- Unity MCP script validation: `VisualToolControllerBase.cs`,
  `BBoxVisualToolController.cs`, and `MagnifierVisualToolController.cs` have 0
  errors; warnings are broad static hints about `FindObjectOfType` / string
  concatenation in update paths.
- Unity MCP `refresh_unity` on `ArSpike@a0c0295f7bd40ecc` recovered after an
  automatic Unity reconnect and completed ready; Console error entries: 0.
- `git diff --check` on touched files completed cleanly, with only LF/CRLF
  normalization warnings.

## Continue Pass 5 - Asset Failure Fallback (2026-05-17)

Pre-edit research:

- Reviewed the pass-4 crop path and noticed that a crop/read/upload failure
  could prevent the semantic `confirm` or `explicit_send` lifecycle from being
  sent.
- Rechecked the visual-tool contract: image assets are optional pointers, while
  stable lifecycle semantics still matter even when a rendered crop is missing.

TODO slice:

1. Preserve semantic lifecycle emission if screen-region capture fails.
2. Preserve semantic lifecycle emission if asset upload fails after PNG bytes
   were produced.
3. Record the asset failure reason in lifecycle `meta.asset_status` so backend
   receipts and HUD/debug logs stay auditable.
4. Keep HUD asset status visible and do not add any ECP/RPC byte path.

Implementation notes:

- Added `sendLifecycleIfAssetCaptureFails` and
  `sendLifecycleIfAssetUploadFails` toggles in `VisualToolControllerBase`.
- Capture failure now sets `LastAssetStatus`, appends `asset_status` to packet
  metadata, clears asset fields, and sends the lifecycle packet when fallback
  is enabled.
- Asset upload failure now does the same, so `confirm` / `explicit_send`
  semantics are not lost just because the optional image probe failed.

Audit after pass 5:

- `uv run pytest tests/test_unity/test_app_v1_meta_ui_static.py -q` -> 28
  passed.
- `uv run pytest tests/test_brain/test_visual_tool_lifecycle.py
  tests/test_brain/test_app_v1_monitor.py::test_console_action_endpoints_drive_app_tool_flows
  tests/test_ecp_event/test_w8_photo_upload_server.py::test_upload_publishes_photo_timebase_metadata
  tests/test_ecp_event/test_w8_observer_photo.py::test_asset_uploaded_timebase_metadata_reaches_evidence_ledger
  -q` -> 7 passed.
- Unity MCP `refresh_unity` completed ready with 0 Console errors. Remaining
  warnings are the unrelated existing audio unused-field warnings.

## Bugfix Pass 6 - Asset-Backed Confirm Local Lock (2026-05-17)

Bug found:

- Plain `Confirm()` and `ExplicitSend()` set `IsLocked=true` before emitting
  stable lifecycle events, but `ConfirmWithRenderedAsset()` and the
  screen-region `IMG/C3` path did not. That meant an asset-backed confirm could
  send backend semantics as `confirm` / `explicit_send` while the local overlay
  still looked unlocked / local.

Fix:

- Added `ApplyStablePhaseLocalState()` in `VisualToolControllerBase`.
- Asset-backed confirm and explicit-send now apply the same local locked /
  selected state before building the packet and starting capture/upload.

Verification:

- `uv run pytest tests/test_unity/test_app_v1_meta_ui_static.py -q` -> 28
  passed.
- `uv run pytest tests/test_brain/test_visual_tool_lifecycle.py
  tests/test_brain/test_app_v1_monitor.py::test_console_action_endpoints_drive_app_tool_flows
  tests/test_ecp_event/test_w8_photo_upload_server.py::test_upload_publishes_photo_timebase_metadata
  tests/test_ecp_event/test_w8_observer_photo.py::test_asset_uploaded_timebase_metadata_reaches_evidence_ledger
  -q` -> 7 passed.
- Unity MCP `refresh_unity` completed with 0 Console errors. Remaining warnings
  were the unrelated audio unused-field warnings plus one MCP bridge WebSocket
  initialization warning during refresh.
- Unity MCP refresh/compile on `ArSpike@a0c0295f7bd40ecc` completed with 0
  errors.

Residual notes:

- Unity Console still shows 3 unrelated audio unused-field warnings in
  `MicrophonePublisher.cs` and `AndroidPcmMicrophoneSource.cs`.
- APP-024 phone/screen-share smoke and UI/body-feel tuning are still required
  before production enabling.
- The current MAG overlay is a dev diagnostic lens, not final optical
  magnification/crop rendering. The HTTP asset wrapper is ready for future
  rendered crops/previews.

## Continue Pass 2 - Local Controller Feel (2026-05-17)

Pre-edit research:

- Re-read current `VisualTools` scripts, `FormalHomeMenuController`, and
  `FormalHomeHudController`.
- Rechecked the smoke reference UI for the older draggable/resizable overlay
  intent: `MagnifierFocusOverlay_Draggable`,
  `BoundaryBoxOverlay_DraggableResizable`, and `MagnificationSlider`.
- Rechecked CORE-014 lifecycle notes: pointer/touch drag, resize, hover, and
  selection stay Unity-local; stable `lock` / `confirm` / `explicit_send` /
  `cancel` / `release` and low-frequency `dwell_tick` / update phases are the
  backend surface.

TODO slice:

1. Add common pointer helpers to the VisualTool base so BBox/MAG can share
   screen-normalized region math without touching CAM/Photo.
2. Add local BBox drag/resize state and dev action buttons for lock, confirm,
   explicit C3 send, cancel, and release.
3. Add local MAG drag, zoom controls, weak dwell ticks, and dev action buttons.
4. Add formal HUD diagnostics for visual-tool feature flag, local render, HTTP
   lifecycle, and asset-upload status.
5. Extend static tests to guard that the new controllers stay separate from
   legacy `BBoxController` / `FocusController` and do not add forbidden memory
   writes or snapshot/image-byte paths.

Implementation notes:

- `VisualToolControllerBase` now exposes `LastAssetStatus` and shared
  pointer/timebase/region helpers.
- `BBoxVisualToolController` now has a Unity-local interaction mode for move
  and edge/corner resize. It calls `UpdateLocalRegion` during manipulation,
  which remains local unless low-frequency update events are explicitly enabled.
- `MagnifierVisualToolController` now supports local lens drag, zoom in/out,
  mouse-wheel zoom in editor, and low-frequency weak `dwell_tick` while still.
- Both tools now include dev HUD action buttons. They emit only stable semantic
  phases over the HTTP wrapper, behind `visualToolDevEnabled`.
- `FormalHomeHudController` now reports `VTool BOX/MAG` status lines so a
  phone/screen-share smoke can see whether local render and HTTP channels are
  alive. This is still diagnostic, not production enablement.

Audit after pass 2:

- `uv run pytest tests/test_unity/test_app_v1_meta_ui_static.py -q` -> 28
  passed.
- `uv run pytest tests/test_brain/test_visual_tool_lifecycle.py
  tests/test_brain/test_app_v1_monitor.py::test_console_action_endpoints_drive_app_tool_flows
  tests/test_ecp_event/test_w8_photo_upload_server.py::test_upload_publishes_photo_timebase_metadata
  tests/test_ecp_event/test_w8_observer_photo.py::test_asset_uploaded_timebase_metadata_reaches_evidence_ledger
  -q` -> 7 passed.
- Unity MCP `refresh_unity` on `ArSpike@a0c0295f7bd40ecc` completed ready with
  0 Console errors after a second force refresh cleared a SourceAssetDB
  timestamp import warning.
- Current Unity warning observed during MCP refresh:
  `MCP-FOR-UNITY: [WebSocket] Unexpected receive error: WebSocket is not
  initialised`. This is bridge noise, not a C# compile error.
- `git diff --check` on touched files reported only existing LF/CRLF
  normalization warnings.

## Continue Pass 3 - Formal Camera Mode HUD (2026-05-17)

Pre-edit research:

- Re-read `FormalHomeToolController`, `FormalHomeMenuController`, and the
  reference-only smoke camera UI.
- Rechecked App V1 camera-mode docs: camera mode is `off` / `preview` /
  `photo_ready` / `capture_locked`, changes capture UI and backend-owned mode
  state, and is separate from Photo Awareness.
- Reconfirmed the formal boundary: CAM/Photo still owns pixel capture through
  `FormalHomeToolController -> PhotoController`; the new camera HUD must not
  call legacy snapshot RPC, embed images, or bypass App HTTP mode state.

TODO slice:

1. Add a formal, runtime-safe camera-mode controller extracted from the smoke
   reference intent rather than mounting the old smoke script.
2. Keep the overlay WYSIWYG: do not draw a fake camera preview frame over the
   AR feed.
3. Add local camera HUD controls for mode, shutter, zoom, exposure, filter, and
   pro panel state.
4. Wire QuickCameraMode HTTP apply to mirror pending/success/failure in the
   local overlay.
5. Wire toolbar CAM capture to set `capture_locked` locally while still calling
   `homeToolController.CapturePhoto()`.
6. Add HUD diagnostics for camera mode / HTTP status / photo status.
7. Extend static tests to guard against smoke-script pollution and forbidden
   snapshot/RPC/image-byte paths.

Implementation notes:

- Added `FormalCameraModeController` under the formal UI runtime tree.
- Added startup-flow service mounting for the camera-mode controller.
- `FormalHomeMenuController` now mirrors App HTTP camera-mode state into the
  local camera HUD and reverts the overlay status if the HTTP apply fails.
- `FormalHomeHudController` now reports a `Camera` diagnostic line with mode,
  zoom, exposure, HTTP status, and photo status.

Audit after pass 3:

- `uv run pytest tests/test_unity/test_app_v1_meta_ui_static.py -q` -> 28
  passed.
- `uv run pytest tests/test_brain/test_app_v1_monitor.py::test_console_action_endpoints_drive_app_tool_flows
  tests/test_ecp_event/test_w8_photo_upload_server.py::test_upload_publishes_photo_timebase_metadata
  tests/test_ecp_event/test_w8_observer_photo.py::test_asset_uploaded_timebase_metadata_reaches_evidence_ledger
  tests/test_brain/test_visual_tool_lifecycle.py -q` -> 7 passed.
- Forbidden-path scan across formal camera/menu/HUD and VisualTools found no
  legacy snapshot RPC, Brain RPC, direct memory writes, or legacy BBox/Focus
  pulse calls.
- Unity MCP `refresh_unity` on `ArSpike@a0c0295f7bd40ecc` completed ready with
  0 Console errors after the final camera capture-status patch.
- Remaining Console warnings are the unrelated existing audio unused-field
  warnings in `MicrophonePublisher.cs` and `AndroidPcmMicrophoneSource.cs`.

## Continue Pass 4 - Dev Screen-Region Asset Probe (2026-05-17)

Pre-edit research:

- Re-read `VisualToolControllerBase`, `BBoxVisualToolController`, and
  `MagnifierVisualToolController` after the local interaction pass.
- Rechecked the CORE-014 asset rule: if App creates a rendered crop or preview
  image, it must upload bytes only through
  `POST /api/app/visual-tool/asset/{asset_id}` and then reference the returned
  `asset_path` in a lifecycle event.

TODO slice:

1. Add an explicit dev-only screen-region asset probe for BBox/MAG.
2. Keep default `OK` confirm as metadata-only; only `IMG` / dev explicit-send
   should produce a PNG crop.
3. Hide the dev overlay for one frame while reading the selected region so the
   uploaded PNG represents the underlying rendered screen area, not the tool
   chrome.
4. Reuse the existing HTTP asset wrapper and lifecycle sender; do not add any
   ECP/RPC byte path.
5. Extend static guards for `ReadPixels`, `EncodeToPNG`, asset buttons, and
   forbidden route boundaries.

Implementation notes:

- `VisualToolControllerBase` now supports
  `ConfirmWithScreenRegionAsset()` and
  `ExplicitSendWithScreenRegionAsset()`.
- The capture path waits for end-of-frame, reads the current screen-normalized
  tool region with `Texture2D.ReadPixels`, encodes PNG bytes, uploads through
  `UploadAssetThenLifecycle`, and restores the overlay.
- BBox dev HUD now has `IMG` for asset-backed confirm and `C3` for
  asset-backed explicit send.
- MAG dev HUD now has `IMG` for weak/intent-only asset confirm and `C3` for
  asset-backed explicit send.
- The path is still behind `visualToolDevEnabled`; it is for APP-024 smoke and
  HTTP channel proof, not production default behavior.

Audit after pass 4:

- `uv run pytest tests/test_unity/test_app_v1_meta_ui_static.py -q` -> 28
  passed.
- Forbidden-path scan across VisualTools, formal camera, menu, and HUD found no
  legacy snapshot RPC, Brain RPC, direct memory writes, or legacy BBox/Focus
  pulse calls.
- `uv run pytest tests/test_brain/test_visual_tool_lifecycle.py
  tests/test_brain/test_app_v1_monitor.py::test_console_action_endpoints_drive_app_tool_flows
  tests/test_ecp_event/test_w8_photo_upload_server.py::test_upload_publishes_photo_timebase_metadata
  tests/test_ecp_event/test_w8_observer_photo.py::test_asset_uploaded_timebase_metadata_reaches_evidence_ledger
  -q` -> 7 passed.

## Bugfix Pass 7 - Stable State Before Asset Preconditions (2026-05-17)

Bug found:

- Pass 6 fixed the happy capture/upload path, but the local stable-state update
  still sat after asset/HTTP preconditions.
- If a user tapped `IMG` or `C3` while visual-tool HTTP was disabled, the
  endpoint was missing, or screen-region asset capture was disabled, the tool
  could return an error/local-only status without first reflecting the user's
  stable semantic action in the overlay.

Fix:

- Moved `ApplyStablePhaseLocalState()` immediately after
  `EnsureOpenForStablePhase()` for both `ConfirmWithRenderedAsset()` and the
  screen-region asset lifecycle path.
- Added static guard assertions so future edits keep the local state transition
  before HTTP and asset-capture precondition checks.

Verification:

- `uv run pytest tests/test_unity/test_app_v1_meta_ui_static.py -q` -> 28
  passed.
- Forbidden-path scan across VisualTools, formal camera, menu, and HUD found no
  legacy snapshot RPC, Brain RPC, direct memory writes, or legacy BBox/Focus
  pulse calls.
- `uv run pytest tests/test_brain/test_visual_tool_lifecycle.py
  tests/test_brain/test_app_v1_monitor.py::test_console_action_endpoints_drive_app_tool_flows
  tests/test_ecp_event/test_w8_photo_upload_server.py::test_upload_publishes_photo_timebase_metadata
  tests/test_ecp_event/test_w8_observer_photo.py::test_asset_uploaded_timebase_metadata_reaches_evidence_ledger
  -q` -> 7 passed.
- Unity MCP `refresh_unity` on `ArSpike@a0c0295f7bd40ecc` completed ready with
  0 Console errors after an automatic MCP reconnect.

## Body-Feel Pass - Viewfinder Blackout And Capture Layer Split (2026-05-25)

User clarification:

- Camera, BBox, and MAG share the same camera-style shutter position and should
  play a phone-camera-like viewfinder blackout when the shutter is pressed.
- Uploaded evidence must not include the blackout, shutter button, OK/FAIL
  badge, selection white border, resize handles, zoom rail, or debug controls.
- BBox/MAG semantic rendering may be captured: BBox YOLO-style frame and MAG
  magnified render are valid preview/evidence overlays when the tool itself is
  the thing being confirmed.

Implementation notes:

- Added a shared Unity HUD component,
  `VisualToolShutterBlackoutFeedback`, for a short black viewfinder blackout
  animation. It preserves the camera control strip: landscape leaves the
  right-side shutter area visible, portrait leaves the bottom shutter area
  visible.
- Camera mode plays blackout immediately after a successful local
  `CapturePhoto()` request; upload completion still only shows OK/FAIL.
- BBox/MAG screen-region capture now hides operation UI only. Their semantic
  render layers remain visible for `ReadPixels`, then blackout plays after the
  capture is complete so the black frame cannot enter the uploaded PNG.
- Existing HTTP behavior is unchanged: asset bytes still go through
  `/api/app/visual-tool/asset/{asset_id}` first, then lifecycle event metadata
  goes through `/api/app/visual-tool/event`.

Audit TODO:

- Verify on iQOO Neo9 that the blackout viewfinder inset leaves the shutter
  visible in portrait and landscape.
- Smoke-test that BBox uploaded PNG includes the colored box but not selected
  white handles/status/OK badge.
- Smoke-test that MAG uploaded PNG includes the magnifier render but not the
  zoom rail/status/OK badge.

Verification:

- `uv run pytest tests/test_unity/test_app_v1_meta_ui_static.py -q` -> 35
  passed.
- `uv run pytest tests/test_brain/test_visual_tool_lifecycle.py
  tests/test_ecp_event/test_w8_photo_upload_server.py
  tests/test_ecp_event/test_w8_observer_photo.py -q` -> 33 passed.
- Forbidden-path scan across Camera/BBox/MAG visual-tool App scripts found no
  legacy snapshot RPC, direct memory writes, C4 send preference, UnityWebRequest
  image upload, or raw ECP/RPC image byte path.

Follow-up bugfix:

- Found a stale HUD-result risk in the Photo upload completion path. The event
  only carried `status/ok`, so a delayed retry from an older photo could update
  the current camera HUD.
- `PhotoController.OnPhotoUploadCompleted` now carries
  `photoId/status/ok`; `FormalHomeToolController` forwards the same tuple.
- `FormalCameraModeController` tracks the pending shutter `photo_id`, ignores
  stale or uncorrelated upload completions, and de-duplicates blackout playback
  for the same photo.
- BBox capture layering follow-up: the clickable sample-attribute strip is now
  treated as operation UI and hidden during capture; a separate non-interactive
  `BBoxSemanticSampleLabel` remains as the YOLO-style semantic label that may
  enter the uploaded preview/evidence PNG.
- BBox body-feel follow-up: the semantic label is positioned like a classic
  detector label at the top edge of the box, and the box fill was reduced to
  near-transparent so uploaded evidence is framed instead of tinted.

Follow-up verification:

- `uv run pytest tests/test_unity/test_app_v1_meta_ui_static.py -q` -> 35
  passed.
- `uv run pytest tests/test_brain/test_visual_tool_lifecycle.py
  tests/test_ecp_event/test_w8_photo_upload_server.py
  tests/test_ecp_event/test_w8_observer_photo.py -q` -> 33 passed.

## Phone HTTP Path Fix - VisualTool Client (2026-05-25)

Bug/risk found:

- BBox/MAG asset and lifecycle traffic still used `UnityWebRequest`, while the
  production Photo upload path already moved to `System.Net.Http.HttpClient` to
  avoid Android cleartext behavior blocking local `http://` laptop backend
  routes in Android-targeted Unity/editor/device flows.
- This meant BBox/MAG could look correct in HUD but fail before creating the
  backend visual-tool evidence lifecycle when the backend is a notebook on the
  LAN.

Fix:

- Replaced `VisualToolHttpClient` transport internals with a shared
  `HttpClient` while preserving the public coroutine API consumed by
  `VisualToolControllerBase`.
- Kept lifecycle and asset upload order unchanged:
  `/api/app/visual-tool/asset/{asset_id}` first for images, then
  `/api/app/visual-tool/event` with returned `asset_path` / `mime_type`.
- Kept all visual-tool metadata headers on asset upload:
  `X-Parrot-Tool-*`, `X-Parrot-Timebase`, `X-Parrot-Region`,
  `X-Parrot-Source-*`, and description.
- Added retry for transient HTTP failures (`408`, `429`, `5xx`) and network
  exceptions; backend error-body parsing remains on the coroutine/main flow.
- Added static Unity guard coverage to ensure VisualTools no longer depend on
  `UnityWebRequest` / `UploadHandlerRaw`.

Verification:

- `uv run pytest tests/test_unity/test_app_v1_meta_ui_static.py -q` -> 35
  passed.
- `uv run pytest tests/test_brain/test_visual_tool_lifecycle.py
  tests/test_ecp_event/test_w8_photo_upload_server.py
  tests/test_ecp_event/test_w8_observer_photo.py -q` -> 33 passed.
- Forbidden-path scan over VisualTools, FormalCameraModeController, and
  FormalHomeToolController found no `UnityWebRequest`, `UploadHandlerRaw`,
  `captureSnapshot`, direct memory writes, or App-side C4 constants.
- `git diff --check` on touched files passed; only existing workspace CRLF
  warnings were reported.

## Body-Feel Fix - Shutter Feedback Waits For Real Upload (2026-05-25)

Bug found:

- BBox/MAG confirm shutters played `OK` immediately when the semantic work was
  merely queued. If the laptop backend endpoint was wrong, asset upload failed,
  or lifecycle event was rejected later, the HUD could show success while no
  backend evidence was created.
- Camera mode had the same product-level ambiguity: the shutter feedback was
  tied to `photo_capture_requested`, not the final HTTP upload result.

Fix:

- Added `OnSemanticHttpCompleted()` in `VisualToolControllerBase`; BBox/MAG now
  play shutter `OK` / `FAIL` only after lifecycle/asset work actually completes.
- Queued BBox/MAG statuses no longer trigger success feedback. Immediate local
  failures still show `FAIL`.
- Asset capture/upload fallback lifecycle packets with `asset_status` failure
  are treated as user-visible failures even if the metadata-only lifecycle event
  itself reaches backend.
- `PhotoController.CapturePhoto()` now returns a capture-start status and
  exposes `OnPhotoUploadCompleted(status, ok)`.
- `FormalHomeToolController` forwards Photo upload completion, and
  `FormalCameraModeController` waits for that event before playing camera
  shutter `OK` / `FAIL`. While upload is in flight, camera status reads
  `camera_photo_upload_pending`.

Follow-up fix:

- Fixed a compile-level regression where a generic status return was
  accidentally inserted into `void` lifecycle/config methods.
- Photo upload completion is now queued and dispatched from `Update()` on the
  Unity main thread. Multiple uploads completing before the next frame are
  delivered in order, so rapid captures do not overwrite earlier completion
  feedback.

Verification:

- `uv run pytest tests/test_unity/test_app_v1_meta_ui_static.py -q` -> 35
  passed.
- `uv run pytest tests/test_brain/test_visual_tool_lifecycle.py
  tests/test_ecp_event/test_w8_photo_upload_server.py
  tests/test_ecp_event/test_w8_observer_photo.py -q` -> 33 passed.
- Forbidden-path scan over VisualTools, FormalCameraModeController,
  FormalHomeToolController, and PhotoController found no `captureSnapshot`,
  App-side memory writes, or App-side C4 constants.

## Flow Audit - Selection, Pinch, Upload, Nodes, Awareness (2026-05-25)

Scope:

- Rechecked App interaction flow for Camera, BBox, and MAG against the original
  VisualToolEvidenceLifecycle App V1 requirements.
- Rechecked backend ownership boundaries: App sends stable visual-tool
  lifecycle events and storage-backed image assets; backend owns Evidence,
  IntentWorkspace staging, Blackboard receipts, and any L2-B promotion.
- Rechecked photo capture flow because it is the only path that currently
  creates L2-B PhotoNodes directly.

Current pass status:

- BBox and MAG have real App-side controllers behind visual-tool dev/http
  flags. They support local drag, selected white outline visuals, confirm
  shutter, and two-finger resize/zoom handling without per-frame backend sends.
- Camera/BBox/MAG share the responsive shutter rule: landscape right-middle,
  portrait bottom-center.
- Visual-tool confirm uploads a PNG via
  `POST /api/app/visual-tool/asset/{asset_id}`, then sends
  `POST /api/app/visual-tool/event` with `asset_path` and `mime_type`.
- Backend policy matches the requirement: BBox confirm stages IntentWorkspace
  and notifies GOSLO through C3 no-interrupt; MAG confirm stages silently; MAG
  explicit_send notifies GOSLO.
- Photo upload still uses the older photo preview/upload path: preview ECP
  creates the PhotoNode, HTTP asset upload updates `reference_image_path` and
  stages the photo in IntentWorkspace.

Known gaps / TODO:

- Closed in later pass: add a reliable fallback when `photo.taken_preview` is
  dropped. Backend now repairs a missing PhotoNode from `photo.asset_uploaded`
  and stages the photo asset through the normal observer path.
- P0: Run a true phone-to-laptop smoke test: iQOO capture -> laptop backend ->
  `/api/app/live-state` and `/api/l2b/snapshot` show a PhotoNode with
  `reference_image_path`, and Web console refreshes it.
- P0: Run the same true phone-to-laptop smoke for visual-tool asset/event
  routes. Visual tools now use `System.Net.Http.HttpClient`, but the iQOO
  device path still needs APP-024 proof against the notebook backend.
- Closed in later pass: implement true MAG render behavior. MAG now keeps a
  local low-FPS live lens texture and does not send per-frame data.
- P0: Decide backend-owned promotion for BBox/MAG visual evidence into semantic
  nodes. Current lifecycle creates Evidence/Ref/IntentWorkspace entries, not
  L2-B PhotoNodes/ObjectNodes directly, which is correct for the App boundary
  but may not satisfy the product expectation of "Node created" for BBox/MAG.
- P1: Make selection state explicit. Current BBox/MAG are effectively selected
  while open; outside tap/reselect semantics and selected-only handles need
  body-feel tuning on phone.
- P1: Unify camera photo metadata with the new BBox/MAG controllers. The legacy
  `PhotoController` still reads active refs from old `BBoxController` /
  `FocusController`, not from the new visual-tool lifecycle controllers.
- P1: Add a polished MAG explicit-send affordance. Dev buttons are hidden, so a
  user-visible path to "send to GOSLO" is not yet designed even though backend
  policy supports it.
- P1: Add BBox sample attributes and color/class controls requested by UX. The
  current BBox is a draggable/resizable visual frame and lifecycle packet, not
  a finished annotation editor.
- P1: Replace debug-ish feedback with one shared OK/FAIL upload component for
  Camera, BBox, and MAG, ideally indicating capture/upload/receipt rather than
  only local button success.
- P1: Validate screen-region crop coordinates on real orientations and Canvas
  scaling, especially landscape right-middle shutter layout and iQOO Neo9
  dimensions.
- P2: Reduce duplicate visual evidence rows if desired. The asset upload route
  records image evidence, then lifecycle confirm records another image evidence
  for the same `asset_path`.
- P2: Pixel-aware MAG hit-testing would feel better than using its full
  rectangular transparent sprite bounds.
- P2: Production enablement is still gated by APP-024 phone/screen-share smoke
  and UI/body-feel tuning.

## Unified Shutter Semantics Pass (2026-05-25)

Objective analysis:

- Common surface: Camera, MAG, and BBox all use the same phone-camera style
  confirmation affordance. In portrait the shutter stays bottom-center; in
  landscape it stays right-middle. Pressing it gives the same short OK/FAIL
  capture feedback.
- Camera semantic: the shutter requests a normal photo capture through
  `PhotoController`. Preview ECP creates/updates the L2-B PhotoNode; HTTP asset
  upload fills `reference_image_path` and stages the photo asset.
- MAG semantic: the shutter confirms "this region is worth looking at" for a
  magnifier/focus context. Confirm remains weak attention: stage to
  IntentWorkspace, no GOSLO C3 notice unless explicit_send is used.
- BBox semantic: the shutter confirms "sample this object/region". Confirm is
  strong attention: backend stages IntentWorkspace and may notify GOSLO through
  C3 no-interrupt.

Implementation:

- Added responsive feedback layout next to the shared shutter position.
- Camera capture feedback now follows that responsive feedback layout.
- BBox/MAG confirm shutters now use the same camera-style outer/inner shutter
  visual, not just a flat circle.
- BBox/MAG shutter actions now show the same OK/FAIL flash/badge feedback as
  camera mode while keeping their separate lifecycle packet semantics.

## Continue Pass - MAG Live Lens Local Render (2026-05-25)

Pre-edit audit:

- MAG already had the pixel magnifier sprite, selected white outline,
  drag/two-finger resize, zoom rail, and confirm lifecycle upload.
- The missing user-facing function was the actual magnified view. The tool was
  still a visual marker over the scene, so it did not help inspect details in
  the camera/document view before confirm.

Implementation:

- Added a masked `RawImage` viewport inside the magnifier lens area.
- Added a local-only live lens render loop. It first tries to render
  `Camera.main` into a temporary `RenderTexture` so the lens does not feed back
  on its own UI overlay, then falls back to screen `ReadPixels` when no camera
  path is available.
- The lens source crop tracks the MAG lens center and scales inversely with the
  current MAG zoom, so pinch zoom changes both the sprite size and the inspected
  crop scale.
- Lifecycle metadata now reports `local_render=mag_live_lens` and includes a
  `live_lens` boolean. Backend semantics are unchanged: the render loop never
  sends frame data; confirm/explicit_send still use stable lifecycle HTTP.

Remaining:

- Needs iQOO phone visual QA for ARFoundation camera background correctness,
  because `Camera.main.Render()` behavior can differ between normal Unity
  scenes, AR camera backgrounds, and document/UI surfaces.
- If screen fallback is used heavily, check for self-feedback artifacts and tune
  the capture path after real screenshots.

## Continue Pass - BBox Sample Attributes And Color (2026-05-25)

Pre-edit audit:

- BBox had a real movable/resizable YOLO-style frame, selected white outline,
  two-finger resize, and confirm shutter.
- It still behaved like a generic frame. For the product purpose "sample an
  object/region", the App needed a lightweight way to mark what kind of sample
  is being sent and which visual color/class is attached to it.

Implementation:

- Added BBox sample state: `sample_label`, `sample_color`, and
  `sample_color_hex` flow into visual-tool lifecycle `meta_json`.
- BBox packet label now includes the current sample label, e.g. `BBox:object`,
  so backend RefBinding/evidence receipts are more readable without App writing
  L2-B directly.
- Added a selected-state sample attribute strip on the BBox itself:
  - color swatch button cycles YOLO-style box colors.
  - label chip cycles phone-friendly sample labels (`object`, `person`,
    `document`, `screen`, `unknown` by default).
- BBox edge/fill color now follows the chosen sample color while locked state
  still turns the frame yellow.

Verification:

- `uv run pytest tests/test_unity/test_app_v1_meta_ui_static.py -q` -> 35
  passed.
- VisualTools forbidden-path scan found no snapshot RPC, direct
  IntentWorkspace/Graphiti/Blackboard writes, or legacy bbox/focus events.
- `uv run pytest tests/test_brain/test_visual_tool_lifecycle.py
  tests/test_ecp_event/test_w8_photo_upload_server.py
  tests/test_ecp_event/test_w8_observer_photo.py -q` -> 32 passed.

Remaining:

- This is phone-friendly cycling, not full free-text keyboard entry. A later UI
  pass can add a compact text input / voice label path if needed.

## Bugfix Pass - Keep Overlay Hidden During Asset Capture (2026-05-25)

Bug:

- Screen-region confirm hides the BBox/MAG overlay before `ReadPixels()` so the
  uploaded crop does not include the tool UI itself.
- After adding MAG live lens and shared confirm feedback, controller
  `UpdateOverlay()` calls could run during that hidden capture window and turn
  the Canvas back on. On phone this could pollute uploaded crops with the
  magnifier/BBox frame, sample chips, or OK/FAIL flash.

Fix:

- `VisualToolControllerBase` now exposes the overlay-hide depth as
  `IsScreenRegionAssetOverlayHidden`.
- BBox and MAG `UpdateOverlay()` now keep their Canvas inactive while this flag
  is true, even if local render/status refreshes run during the capture frame.

Verification:

- `uv run pytest tests/test_unity/test_app_v1_meta_ui_static.py -q` -> 35
  passed.
- VisualTools forbidden-path scan found no snapshot RPC, direct
  IntentWorkspace/Graphiti/Blackboard writes, or legacy bbox/focus events.
- `uv run pytest tests/test_brain/test_visual_tool_lifecycle.py
  tests/test_ecp_event/test_w8_photo_upload_server.py
  tests/test_ecp_event/test_w8_observer_photo.py -q` -> 32 passed.

## Reliability Fix - Photo Asset Upload Repairs Missing PhotoNode (2026-05-25)

Bug:

- The App sends the photo preview over ECP and the full-resolution image over
  HTTP. If `photo.taken_preview` is dropped because the room/publisher is not
  ready, the HTTP upload still lands on disk but `observer.photo` previously
  logged `asset_uploaded for unknown photo_id` and did not create/update a
  PhotoNode.
- Product symptom: phone shows an upload success path, but Web/L2-B may not show
  a PhotoNode or `reference_image_path`, and IntentWorkspace may not receive the
  final photo asset.

Fix:

- `observer.photo` still counts `asset_for_unknown_photo_id` for observability,
  but now repairs the missing node by creating a `NodeKind.PHOTO` from the
  storage-backed asset event, then writes `reference_image_path`.
- This does not create ObjectNodes and does not promote candidate subjects; it
  only preserves the user-taken photo as a PhotoNode.
- Added metric `asset_orphan_nodes_repaired`.
- Added HTTP-level regression coverage for upload-without-preview.

Verification:

- `uv run pytest tests/test_ecp_event/test_w8_photo_upload_server.py
  tests/test_ecp_event/test_w8_observer_photo.py -q` -> 29 passed.
- `uv run pytest tests/test_brain/test_visual_tool_lifecycle.py
  tests/test_ecp_event/test_w8_photo_upload_server.py
  tests/test_ecp_event/test_w8_observer_photo.py -q` -> 33 passed.
- `uv run pytest tests/test_unity/test_app_v1_meta_ui_static.py -q` -> 35
  passed.

## UX Gap Audit / User Requirement Capture (2026-05-22)

Prompt/context:

- User reviewed current App feel and asked whether camera mode is actually
  complete, whether its buttons/components work, why the layout feels rough,
  and why BBox/MAG still feel like empty shells.
- User clarified the expected product behavior: CAM, BBox, and MAG all need
  clear capture/upload feedback; MAG needs true magnified background/rendered
  view; BBox/MAG must be selectable and touch-draggable, with two-finger
  scale/resize affordances; BBox must support color and sample/property input;
  the camera shutter and feedback need a better body feel.

Current code audit:

- CAM is the most complete of the three. `FormalCameraModeController` owns a
  WYSIWYG camera HUD; Ready/Preview/Close apply backend camera mode through
  App HTTP; Capture delegates to `FormalHomeToolController.CapturePhoto()`;
  `PhotoController` emits `photo.taken_preview` ECP metadata and uploads the
  JPEG through HTTP/storage. The laptop true-connection path previously proved
  PhotoNode/L2-B visibility after app-monitor refresh.
- CAM is not product-polished. The HUD is programmatic first-pass UI, the
  shutter only reports request-level status, and there is no user-visible
  async chain for preview sent -> upload pending -> upload ok/failed ->
  PhotoNode visible. Zoom/exposure/filter controls are local UI state only;
  they do not yet drive AR camera hardware, render effects, or stored asset
  metadata.
- BBox/MAG are not empty at protocol level: `VisualToolPacketBuilder`,
  `VisualToolHttpClient`, feature flags, lifecycle phases, dev overlays, and
  optional screen-region asset upload exist. They stay separate from
  `FormalHomeToolController`, honor stable-phase backend emission, and avoid
  image bytes over ECP/RPC.
- BBox/MAG are still dev tools, not final embodied tools. They are behind
  `visualToolDevEnabled` / `visualToolHttpEnabled`, use ScreenSpaceOverlay
  diagnostics, and need APP-024 phone/body-feel proof before production
  enablement.
- MAG currently draws a translucent lens/rim/crosshair and sends lifecycle
  metadata. It supports single-pointer drag plus mouse-wheel/dev-button zoom,
  but it does not magnify the live AR/camera background, does not render a
  zoomed texture/crop, has no touch pinch, and has no proper zoom bar/rail.
- BBox currently supports single-pointer move/edge resize and dev action
  buttons. It lacks explicit production selection handles, two-finger resize,
  color change UI, sample/label/property input, and polished capture/upload
  feedback.

Captured requirements for the next implementation pass:

1. Shared capture/upload feedback component for CAM, BBox, and MAG. It must
   show at least captured/requested, preview/lifecycle sent, asset upload
   pending, upload ok, upload failed/retry, and backend receipt/PhotoNode or
   visual-tool receipt when available.
2. Camera mode redesign. Keep the real capture owner path, but replace the
   rough first-pass buttons with a clearer shutter, stronger capture animation
   or haptic-style visual feedback, and honest control states. Zoom/exposure
   and filters should either become real camera/render controls or be visibly
   downgraded until they are real.
3. MAG production behavior. Add selectable lens state, touch drag, two-finger
   pinch to resize/zoom, visible zoom factor rail/bar, and a real magnified
   view of the live rendered background or AR camera frame. Confirm remains
   weak attention / IntentWorkspace-only by default; explicit send or C3
   delivery preference is the user-controlled GOSLO notification path.
4. BBox production behavior. Add selectable frame state, handles, touch drag,
   two-finger resize, color selection, and sample/property input such as label,
   subject hint, or class/attribute fields. Confirm remains strong attention by
   default and may request C3 no-interrupt notice through backend policy.
5. Preserve original protocol boundaries. High-frequency hover/drag/pinch stays
   local; backend receives only stable phases or deliberately low-frequency
   dwell/drag/resize ticks. Rendered/cropped images upload through
   `/api/app/visual-tool/asset/{asset_id}` before lifecycle event references.
   No `captureSnapshot` RPC, no image bytes through ECP/RPC, no Unity direct
   L2-B/Graphiti/IntentWorkspace/Blackboard writes, and no App-side C4 or
   immediate interrupt semantics.

Implementation implication:

- The next useful code slice is not another protocol wrapper. It should add a
  small formal visual-tool UI layer shared by BBox/MAG/CAM feedback, then
  implement MAG's real render/magnification path and BBox's production edit
  affordances behind the existing dev/prod flags.

## Design Reference Pass - Pixel Tools And Camera Feel (2026-05-22)

User correction:

- Feedback should stay simple for now: success vs failure is enough. A camera
  shutter flash, screenshot freeze, or small captured-thumbnail animation is
  acceptable and better than a verbose upload state machine.
- MAG and BBox should be designed as pixel-style tool sprites first, then
  controlled by code. They should not look like generic programmatically drawn
  rectangles. Required assets include a pixel magnifying glass/lens, pixel BBox
  frame pieces, and white selected/drag affordance pieces.
- Camera mode should feel closer to a phone camera or a photography game, not
  like a debug control panel.

Reference scan:

- Apple Camera Control/HIG guidance emphasizes a large viewfinder with minimal
  distractions and placing controls outside overlay-conflict zones.
- Apple button guidance supports compact feedback inside/near the control when
  an action has delay; for our first pass this maps to shutter flash plus
  success/failure badge instead of a long status rail.
- New Pokemon Snap's public materials emphasize scoring by pose/proximity/frame
  and photo decoration with filters/stamps/frames, which supports a playful
  camera/game feel rather than a desktop debug panel.
- Umurangi Generation is useful as a photography-game reference because its
  loop is first-person camera handling, lenses/equipment, composition/content
  scoring, and photo editing/color grading. We should borrow the "camera as
  embodied tool" feel, not its exact visual style.
- Kenney Pixel UI Pack and OpenGameArt pixel magnifier / selection-border
  entries confirm the asset direction: transparent PNG sprites, pixel panels,
  pixel buttons, selection borders, and UI icons should be generated/imported
  as sprites and then arranged in Unity.

Design decisions for the next code/art pass:

1. Shared feedback becomes two-state: success and failure. During capture/upload
   we can use local motion only: quick white flash, freeze-frame thumbnail, and
   a small check/cross badge. The backend can still record detailed lifecycle,
   but the user-facing UI should not narrate every network step.
2. Camera mode should be rebuilt around a big unobstructed AR viewfinder,
   bottom-center pixel shutter button, small gallery/last-shot thumbnail, mode
   chips, and optional compact top controls. The current large pro/status panel
   should move behind an explicit advanced/debug affordance.
3. MAG needs pixel-art lens assets: idle lens, selected white outline/handles,
   locked/confirm accent, plus a zoom rail/bar. The controller should render or
   crop a magnified view inside that lens rather than only drawing a translucent
   rectangle.
4. BBox needs pixel-art frame assets: corners, edges, selected white outline,
   resize handles, color swatches, and a small sample/property input plate. The
   controller should compose sprite pieces around the selected region.
5. Asset generation should happen before controller polish so the App body feel
   can be tuned against the actual visual language instead of placeholder
   debug geometry.

Reference links captured for implementation notes:

- Apple Camera Control:
  `https://developer.apple.com/design/human-interface-guidelines/camera-control`
- Apple Buttons:
  `https://developer.apple.com/design/human-interface-guidelines/buttons`
- New Pokemon Snap official page:
  `https://www.nintendo.com/en-gb/Games/Nintendo-Switch-games/New-Pokemon-Snap-1799500.html`
- Umurangi Generation Steam page:
  `https://store.steampowered.com/app/1223500/Umurangi_Generation/`
- Kenney Pixel UI Pack:
  `https://kenney.nl/assets/pixel-ui-pack`
- OpenGameArt magnifying glass:
  `https://opengameart.org/content/magnifying-glass`
- OpenGameArt selection border:
  `https://lpc.opengameart.org/content/iron-plague-selection-border`

## Quick Body-Feel Fix - Camera Shutter And Selected-Parrot Gates (2026-05-22)

User correction:

- The camera shutter should be fixed where a normal phone camera shutter lives:
  bottom-center, large, round, and easy to hit. It should not feel like a small
  debug toolbar button.
- Zoom/exposure controls looked bad and did not function as real camera
  controls, so they should not be visible in the main camera layout.
- Clear and joystick controls should only appear after the placed parrot is
  explicitly selected.

Fix applied:

- `FormalCameraModeController` now uses a bottom-center circular shutter
  button and a taller bottom camera-control band.
- Main camera UI no longer shows zoom/exposure rails. The existing code paths
  remain for static compatibility, but the controls are hidden until they can
  drive real camera/render behavior.
- Capture feedback is intentionally simple: a short white flash plus `OK` or
  `FAIL` badge based on whether the photo request was accepted.
- `FormalModelPlacementController.PlaceAt(...)` no longer selects the model
  automatically after placement. The user must tap/select the parrot before
  selected-only controls appear.
- `FormalHomeMenuController` now gates the `CLEAR` action and bottom placement
  button on `HasSelectedModel`; placed-but-unselected state shows a select
  hint instead of a clear action.
- `FormalModelRemoteController` already required
  `placementController.HasSelectedModel`; with placement no longer
  auto-selecting, the joystick now appears only after explicit selection.

Verification:

- `uv run pytest tests/test_unity/test_app_v1_meta_ui_static.py -q` -> 35
  passed.
- `git diff --check` on the touched Unity scripts reported only existing
  LF/CRLF conversion warnings and no whitespace errors.

## Pixel Asset Reference / Shutter Confirm Pass (2026-05-25)

User-provided local references:

- `C:/Users/Bin/Desktop/camera button.png`: pixel camera reference for the
  camera/shutter feeling.
- `C:/Users/Bin/Desktop/Mag.png`: pixel magnifier reference for the MAG lens
  and selected outline.
- `C:/Users/Bin/Desktop/traffic_detections.jpg`: YOLO-like BBox reference,
  with thick colored detection frames and label plates.

Interpretation:

- Treat the desktop images as style references. Do not commit the watermarked
  reference images as production assets. Generate/import App-owned clean pixel
  sprites instead.
- BBox should be drawn like a traditional YOLO detection frame: thicker colored
  box, obvious label/status area later, selected white pixel outline, and
  resize handles.
- MAG should look like a pixel magnifying glass/lens, not a generic translucent
  rectangle. Selected state needs a pixel white outline.
- Camera mode does not need focus/exposure for now. It only needs the normal
  camera shutter plus two-finger zoom of the screen/camera view.
- CAM/BBox/MAG all reuse the shutter idea as the "confirm/send image" affordance.
  CAM shutter calls `PhotoController` through `FormalHomeToolController`; BBox
  and MAG shutter call `ConfirmWithScreenRegionAsset()`, which uploads the
  screen-region image by HTTP asset route and then sends the visual-tool event.

Fix applied:

- Added `VisualToolPixelSprites`, a runtime-generated clean pixel sprite helper
  for shutter circles, white selected rings, and a MAG lens. This avoids
  directly importing the watermarked desktop reference images while preserving
  the intended pixel style.
- Camera mode now supports two-finger pinch zoom via `HandlePinchViewZoom()` and
  applies it to the active camera's FOV/orthographic size where Unity allows it.
  The hidden old zoom/exposure slider code remains for static compatibility but
  is no longer the visible interaction model.
- BBox dev controller now uses thicker YOLO-style red/yellow frame edges, white
  selected outlines, selected corner handles, two-finger resize, and a fixed
  bottom-center shutter confirm button wired to `ConfirmWithScreenRegionAsset`.
- MAG dev controller now uses the generated pixel magnifier sprite, white
  selected ring, visible zoom rail, two-finger resize/zoom, and a fixed
  bottom-center shutter confirm button wired to `ConfirmWithScreenRegionAsset`.
- Static guards were extended so the new pixel sprites, pinch handlers, and
  shutter-confirm buttons remain present.

Verification:

- `uv run pytest tests/test_unity/test_app_v1_meta_ui_static.py -q` -> 35
  passed.
- `git diff --check` on touched Unity scripts/tests reported only existing
  LF/CRLF conversion warnings and no whitespace errors.

## Review/Fix Pass 24 - Chat-Level Flow Audit And Camera Pending Race (2026-05-18)

Review scope:

- Re-read the original App evidence-tool docs, Time-Aligned Evidence SSOT,
  GOSLO Trigger/Awareness taxonomy, CORE candidate queue, App/Web TODO board,
  this work log, and the current Unity controllers.
- Audited the implementation against the user's original constraints: stable
  lifecycle events only, no per-frame backend spam, image bytes only through
  HTTP asset upload, no snapshot RPC, no ECP/RPC binary payloads, no App direct
  writes to IntentWorkspace/Blackboard/Graphiti/L2-B, and no App-side C4
  interrupt semantics.

What this chat completed:

- App-side visual-tool packet builder and HTTP wrapper for
  `/api/app/visual-tool/event` plus
  `/api/app/visual-tool/asset/{asset_id}`.
- Feature-flagged BBox/MAG controller scaffolds with local drag/resize/lens
  movement, local lock/selection/body-feel state, optional low-frequency
  lifecycle updates, stable `confirm` / `explicit_send` / `cancel` / `release`
  semantics, and dev HUD diagnostics.
- Optional dev screen-region PNG asset probe: crop/render bytes are uploaded
  over HTTP first, then the returned asset ref is attached to lifecycle.
- Photo upload timebase header support, so CAM/Photo aligns with the backend
  timebase path while keeping PhotoController as the only pixel owner.
- Formal camera-mode HUD/controller: WYSIWYG overlay, Ready/Preview/Close mode
  apply through App HTTP, Capture through `FormalHomeToolController`, and HUD
  diagnostics for mode/HTTP/photo state.
- Multiple follow-up fixes for lifecycle phase allow-listing, stale async
  asset/crop work, lock/unlock body feel, disabled asset fallback, EventSystem
  isolation, and camera-mode pending/commit behavior.

True-connection gap:

- This is Editor/static/backend-route validated, not phone-production proven.
- APP-024 remains the production gate: iQOO phone pass must prove App HTTP
  reachability, real rendered/HUD body feel, screen-region asset throughput,
  screen-share/LiveKit evidence freshness, app pause/resume/reconnect, audio
  route stability, and no CAM/Photo regressions.
- BBox/MAG are still default-disabled behind `visualToolDevEnabled=false`.
  Formal toolbar production enablement must wait for phone smoke and
  UI/body-feel tuning.
- MAG optical magnification is currently a dev lens/controller scaffold rather
  than final production visual magnification.

Design/performance drift audit:

- No confirmed drift from the original transport/performance design: pointer
  movement, hover, selected state, resize handles, zoom, and dwell timing remain
  local by default; backend traffic is restricted to stable milestones plus
  optional low-frequency updates.
- The only intentional scope expansion was adding the camera-mode HUD, because
  the user explicitly allowed completing camera mode in the same workstream.
- Production enablement language remains conservative: backend CORE-014
  unblocks controller implementation, but it does not replace APP-024 real
  phone/screen-share proof.

Bug found and fixed:

- QuickCameraMode used `cameraModeController.MarkHttpPending()` for shared HUD
  visibility, but it did not set the camera controller's own coroutine field.
  While a menu-triggered camera-mode HTTP request was pending, the Camera HUD
  could still start another mode request.
- `FormalCameraModeController` now treats either an active coroutine or a
  non-empty external `_pendingMode` as `HasPendingHttpRequest`.
- `FormalHomeMenuController.CycleCameraMode()` now checks both its own
  `_pendingCameraMode` and `cameraModeController.PendingMode` before starting a
  new QuickCameraMode request.
- Static tests now guard both sides of this pending-state bridge.

Camera mode completion answer:

- The formal camera-mode code path was first completed in Continue Pass 3 on
  2026-05-17.
- It was hardened by Pass 9/10/11/13 and this Pass 24. After Pass 24 it is
  App-side complete for Editor/static/backend-route validation.
- It is not production-complete until APP-024 phone smoke proves the real
  device capture/mode UX with phone-safe HTTP upload and no CAM/Photo
  regression.

Verification:

- `uv run pytest tests/test_unity/test_app_v1_meta_ui_static.py -q` -> 28
  passed.
- `uv run pytest tests/test_brain/test_visual_tool_lifecycle.py
  tests/test_brain/test_app_v1_monitor.py::test_console_action_endpoints_drive_app_tool_flows
  tests/test_ecp_event/test_w8_photo_upload_server.py::test_upload_publishes_photo_timebase_metadata
  tests/test_ecp_event/test_w8_observer_photo.py::test_asset_uploaded_timebase_metadata_reaches_evidence_ledger
  -q` -> 7 passed.
- Forbidden-path scan across VisualTools, Formal Camera, Formal Home menu/HUD,
  Formal Tool, and PhotoController found no active snapshot RPC,
  `identify_object`, C4 send constant, direct Brain memory write, or image-byte
  ECP/RPC marker.
- `git diff --check` on touched files reported only LF/CRLF normalization
  warnings.
- Unity MCP `refresh_unity` on `ArSpike@a0c0295f7bd40ecc` recovered after a
  reconnect and completed ready; `validate_script` reported 0 errors for
  `FormalCameraModeController` and `FormalHomeMenuController`; Console error
  entries: 0.

## Bugfix Pass 25 - Camera Mode Failure Labels Use Attempted Mode (2026-05-18)

Pre-edit audit:

- Continued the camera-mode true-connection review after Pass 24.
- Found that both the camera HUD path and QuickCameraMode path rolled the local
  UI back correctly on HTTP failure, but then called `MarkHttpResult()` with
  the previous/current mode rather than the mode that had just failed.

Bug found:

- APP-024 smoke diagnostics could report a failed request against the old mode
  instead of the attempted target mode, hiding whether `preview`,
  `photo_ready`, or `off` was rejected.

Fix:

- `FormalCameraModeController.ApplyModeHttp()` now still rolls back local
  display to `previousMode`, but records the HTTP failure against the attempted
  `mode`.
- `FormalHomeMenuController.ApplyCameraModeHttp()` does the same for the
  QuickCameraMode path.
- Static tests now forbid the old `MarkHttpResult(previousMode, false)` /
  `_cameraMode` failure-label pattern.

Verification:

- `uv run pytest tests/test_unity/test_app_v1_meta_ui_static.py -q` -> 28
  passed.
- `uv run pytest tests/test_brain/test_visual_tool_lifecycle.py
  tests/test_brain/test_app_v1_monitor.py::test_console_action_endpoints_drive_app_tool_flows
  tests/test_ecp_event/test_w8_photo_upload_server.py::test_upload_publishes_photo_timebase_metadata
  tests/test_ecp_event/test_w8_observer_photo.py::test_asset_uploaded_timebase_metadata_reaches_evidence_ledger
  -q` -> 7 passed.
- Forbidden-path scan across VisualTools, Formal Camera, Formal Home menu/HUD,
  Formal Tool, and PhotoController found no active snapshot RPC,
  `identify_object`, C4 send constant, direct Brain memory write, or image-byte
  ECP/RPC marker.
- `git diff --check` on touched files reported only LF/CRLF normalization
  warnings.
- Unity MCP `refresh_unity` on `ArSpike@a0c0295f7bd40ecc` recovered after a
  reconnect and completed ready; `validate_script` reported 0 errors for
  `FormalCameraModeController` and `FormalHomeMenuController`; Console error
  entries: 0.

## Bugfix Pass 23 - Dev EventSystem Isolation (2026-05-18)

Pre-edit audit:

- Re-read the current VisualTools controller base and the static guards after
  the latest bugfix request.
- Found a body-feel/mainline isolation issue: opening a BBox/MAG dev canvas
  could mutate the existing scene `EventSystem` by removing a
  `StandaloneInputModule` and adding `InputSystemUIInputModule`.
- This crossed the original boundary that BBox/MAG must stay separate from the
  FormalHomeToolController CAM/Photo path and could disturb existing menu
  routing when the visual-tool dev flag is enabled.

Fix:

- `EnsureEventSystemForDevCanvas()` now returns immediately when an
  `EventSystem` already exists.
- BBox/MAG only create a minimal `VisualToolDevEventSystem` when the scene does
  not already provide one.
- Static tests now guard against mutating or destroying modules on an existing
  `EventSystem`.

Verification:

- `uv run pytest tests/test_unity/test_app_v1_meta_ui_static.py -q` -> 28
  passed.
- Forbidden-path scan across VisualTools, formal camera, menu, and HUD found no
  C4 send constant, legacy snapshot RPC, Brain RPC, direct memory writes, or
  legacy BBox/Focus pulse calls.
- EventSystem isolation scan now only finds `EnsureEventSystemForDevCanvas()`
  and `VisualToolDevEventSystem`; the old existing-EventSystem mutation strings
  are absent.
- `git diff --check` on the touched files reported only LF/CRLF normalization
  warnings.
- Unity MCP `refresh_unity` on `ArSpike@a0c0295f7bd40ecc` recovered after a
  reconnect and completed ready; `validate_script` reported 0 errors for
  `VisualToolControllerBase`, `BBoxVisualToolController`, and
  `MagnifierVisualToolController`; Console error entries: 0.

## Bugfix Pass 11 - Camera HUD/Menu Mode State Sync (2026-05-17)

Bug found:

- Camera HUD could successfully call backend `SetCameraMode()` through
  `RequestModeApply()`, but `FormalHomeMenuController` did not learn that the
  backend-owned camera mode changed.
- The bottom QuickCameraMode button still used its stale `_cameraMode`, so the
  next click could compute the wrong next mode and appear to jump backward.
- Event subscription also needed to survive AppStartupFlow `AddComponent`
  ordering, where the menu may bind before the camera controller exists.

Fix:

- `FormalCameraModeController` now emits mode apply pending/succeeded/failed
  events from the same HTTP result path that owns backend state.
- `FormalHomeMenuController` subscribes to those events, updates
  `_pendingCameraMode` / `_cameraMode`, and refreshes quick actions.
- Camera controller lookup is centralized through `ResolveCameraModeController()`
  so late-created controllers are also subscribed.

Verification:

- `uv run pytest tests/test_unity/test_app_v1_meta_ui_static.py -q` -> 28
  passed.
- Forbidden-path scan across VisualTools, formal camera, menu, and HUD found no
  C4 send constant, legacy snapshot RPC, Brain RPC, direct memory writes, or
  legacy BBox/Focus pulse calls.
- `uv run pytest tests/test_brain/test_visual_tool_lifecycle.py
  tests/test_brain/test_app_v1_monitor.py::test_console_action_endpoints_drive_app_tool_flows
  tests/test_ecp_event/test_w8_photo_upload_server.py::test_upload_publishes_photo_timebase_metadata
  tests/test_ecp_event/test_w8_observer_photo.py::test_asset_uploaded_timebase_metadata_reaches_evidence_ledger
  -q` -> 7 passed.
- Unity MCP `refresh_unity` on `ArSpike@a0c0295f7bd40ecc` completed ready with
  0 Console errors after an automatic MCP reconnect.

## Continue Pass 10 - Locked Entry And Camera Pending Race Fixes (2026-05-17)

Follow-up audit:

- Rechecked pass-9 fixes for alternate entry points and request races.
- Found that `UpdateLocalRegion()` was still a public local-update entry point
  that could bypass the controller-specific locked pointer guards.
- Found MAG could still emit dwell ticks after lock/confirm.
- Found QuickCameraMode and Camera HUD could start a second camera-mode HTTP
  request while one was already pending.

Fix:

- `VisualToolControllerBase.UpdateLocalRegion()` now rejects local region
  mutation while locked and reports `*_locked_unlock_required`.
- MAG dwell ticks now pause while locked.
- Camera HUD no longer stops an in-flight mode coroutine; it reports
  `camera_http_request_already_pending` until the request completes.
- FormalHomeMenu QuickCameraMode now rejects repeated camera-mode changes while
  `_pendingCameraMode` is set.

Verification:

- `uv run pytest tests/test_unity/test_app_v1_meta_ui_static.py -q` -> 28
  passed.
- Forbidden-path scan across VisualTools, formal camera, menu, and HUD found no
  C4 send constant, legacy snapshot RPC, Brain RPC, direct memory writes, or
  legacy BBox/Focus pulse calls.
- `uv run pytest tests/test_brain/test_visual_tool_lifecycle.py
  tests/test_brain/test_app_v1_monitor.py::test_console_action_endpoints_drive_app_tool_flows
  tests/test_ecp_event/test_w8_photo_upload_server.py::test_upload_publishes_photo_timebase_metadata
  tests/test_ecp_event/test_w8_observer_photo.py::test_asset_uploaded_timebase_metadata_reaches_evidence_ledger
  -q` -> 7 passed.
- Unity MCP `refresh_unity` on `ArSpike@a0c0295f7bd40ecc` completed ready with
  0 Console errors after an automatic MCP reconnect.

## Laptop Backend Config Pass - Photo Upload / Dev Tool Smoke (2026-05-18)

Question:

- The App is switching from public ECS to the laptop as backend. Confirm whether
  CAM, BBox, and MAG can still be used, and whether a real photo capture can
  create a PhotoNode in L2-B.

Findings:

- Active Unity config was already pointed at laptop mint/LiveKit/App
  API/orchestrator on `192.168.2.4`, but it did not include a phone-safe
  `photoUploadUrl`.
- The laptop compose profile did not publish Brain's in-job
  `photo_upload_server` to the phone. The host port existed only after adding
  an explicit `17889 -> 7889` mapping.
- Brain starts `photo_upload_server` inside a LiveKit room job, not while the
  idle worker is merely registered. So `/health` is expected to be unavailable
  until Unity/sim client joins and the Brain job starts.

Fix:

- `infra/docker-compose.laptop.yml` now exposes Brain photo upload at
  `0.0.0.0:17889 -> 7889` and sets `PARROT_PHOTO_UPLOAD_HOST=0.0.0.0`,
  `PARROT_PHOTO_UPLOAD_PORT=7889`, and `PARROT_PHOTO_CACHE_ROOT=/app/data/photos`.
- `infra/laptop-castle.ps1` now generates `photoUploadUrl` plus
  `visualToolDevEnabled=true` and `visualToolHttpEnabled=true` for the laptop
  Unity profile.
- `infra/switch-unity-app-config.ps1` now shows `photoUploadUrl` and the visual
  tool flags in its secret-safe summary.
- Active Unity `Resources/parrot_config.json` was switched to the regenerated
  laptop profile for the next Android build.

Verification:

- `infra/laptop-castle.ps1 -Action up-brain` recreated the app-monitor and
  Brain containers with the new port mapping.
- `sim_unity_client.py --startup-rpc-check --startup-room-profile-id default`
  connected to `parrot-laptop-main`, saw an `agent-*` Brain participant, and
  got business-ok from `applyRoomProfile` and `setAppCapabilityMode`.
- After the Brain room job started, `http://192.168.2.4:17889/health` returned
  `{"status":"ok","service":"photo-upload"}`.
- `.venv\Scripts\python.exe -m pytest tests/test_castle/test_livekit_config.py
  tests/test_unity/test_app_v1_meta_ui_static.py -q` -> 37 passed.

Boundary note fixed in follow-up pass:

- `app-monitor` now proxies read-only `/api/app/live-state` and
  `/api/l2b/snapshot` to the active Brain room job through
  `PARROT_APP_MONITOR_BRAIN_LIVE_STATE_URL=http://brain:7889`. This keeps
  Web/App read visibility separate from the process that writes L2-B.
- The Brain room job's `photo_upload_server` exposes the same read-only routes
  for that proxy, annotated with `source_process=brain.photo_upload_server`
  and `read_only_proxy_surface=true`.
- True-connection probe after container rebuild:
  `unity-photo-node-probe-*` joined `parrot-laptop-main`, Brain `agent-*`
  joined, the probe published `photo.taken_preview` on reliable
  `parrot.ecp.event`, then POSTed image bytes to `/upload/photo/{photo_id}`.
  `app-monitor` refresh returned a `photo` node with
  `reference_image_path=/app/data/photos/2026-05-18/ph_probe_*.jpg` and proxy
  metadata `source=brain_room_job` for both live-state and L2-B routes.
- Bug found and fixed during the probe: LiveKit `publish_data` is not a
  self-delivery guarantee. The upload server published `photo.asset_uploaded`
  to peers, but Brain did not always process its own published event, leaving
  `PhotoNode.reference_image_path` empty. The HTTP upload path now mirrors the
  same Brain-source `EcpEvent` into the existing local `EcpEventIngest`; dedup
  protects against future self-loop duplication.

## UX Alignment Pass - iQOO Shutter And MAG Asset (2026-05-25)

User correction:

- The camera-mode bottom black strip is not acceptable; the normal camera view
  should stay unobscured and keep the bottom-center shutter as the main control.
- MAG should use the provided `Mag.png` art, not the generated fallback. Its
  white background must become transparent while enclosed white highlights stay
  visible.
- BBox and MAG first-open sizes should be tuned against the iQOO Neo9 landscape
  screen, and their confirm shutter must sit at the same bottom-center position
  as camera mode.

Implementation:

- Added `VisualToolHudMetrics` with the iQOO Neo9 `2800 x 1260` reference
  resolution, shared bottom shutter position/size, and BBox/MAG default regions.
- Removed the visible camera-mode top/bottom edge panels from normal view; the
  camera HUD now relies on the shutter plus OK/FAIL flash feedback.
- Converted `C:/Users/Bin/Desktop/Mag.png` into
  `Assets/ParrotApp/Resources/ParrotApp/VisualTools/MagPixelTransparent.png`.
  The runtime MAG sprite loader now loads this transparent Resource first and
  falls back to generated art only when the Resource is missing.
- Replaced MAG's circular selected ring with offset white silhouettes using the
  same MAG sprite, so selected state follows the actual pixel asset shape.
- BBox/MAG confirm shutters now use the shared camera shutter position and
  size; dev action rows default hidden so the shutter path is the visible path.

Verification:

- `uv run pytest tests/test_unity/test_app_v1_meta_ui_static.py -q` -> 35
  passed.
- `git diff --check` -> no code whitespace errors; only existing LF/CRLF
  warnings in the workspace.

Follow-up correction:

- User clarified that "same shutter position" means camera-style orientation
  behavior: landscape at the right-side middle, portrait at the bottom-center.
- `VisualToolHudMetrics.ApplyResponsiveShutterLayout()` now owns this rule for
  Camera, BBox, and MAG. Camera mode reapplies it during update/refresh; BBox
  and MAG reapply it during overlay refresh before showing the confirm button.
- Static Unity guard after the correction: `uv run pytest
  tests/test_unity/test_app_v1_meta_ui_static.py -q` -> 35 passed.

## Continue Pass 9 - Requirements Compliance Fixes (2026-05-17)

Pre-edit audit:

- Rechecked the implementation against the original App-side constraints after
  the review pass.
- Found three requirement-level gaps: locked tools could still be edited
  locally without an `unlock`, disabled screen-region asset capture dropped the
  stable lifecycle event, and camera HUD buttons could bypass the backend-owned
  camera mode apply path.

Fix:

- BBox and MAG now reject pointer edits while locked and report
  `*_locked_unlock_required`; MAG zoom controls also require unlock.
- Screen-region asset capture disabled now falls back to sending a metadata-only
  stable lifecycle packet with `meta.asset_status=screen_region_asset_disabled`.
- Camera HUD Ready/Preview/Close buttons now call `RequestModeApply()`, which
  uses `AppHomeMenuClient.SetCameraMode()` with pending/success/failure HUD
  state. Capture only enters `capture_locked` after `CapturePhoto()` reports a
  successful request.

Verification:

- `uv run pytest tests/test_unity/test_app_v1_meta_ui_static.py -q` -> 28
  passed.
- Forbidden-path scan across VisualTools, formal camera, menu, and HUD found no
  C4 send constant, legacy snapshot RPC, Brain RPC, direct memory writes, or
  legacy BBox/Focus pulse calls.
- `uv run pytest tests/test_brain/test_visual_tool_lifecycle.py
  tests/test_brain/test_app_v1_monitor.py::test_console_action_endpoints_drive_app_tool_flows
  tests/test_ecp_event/test_w8_photo_upload_server.py::test_upload_publishes_photo_timebase_metadata
  tests/test_ecp_event/test_w8_observer_photo.py::test_asset_uploaded_timebase_metadata_reaches_evidence_ledger
  -q` -> 7 passed.
- Unity MCP `refresh_unity` on `ArSpike@a0c0295f7bd40ecc` completed ready with
  0 Console errors after an automatic MCP reconnect.

## Bugfix Pass 8 - Remove App-Side C4 Send Constant (2026-05-17)

Bug found:

- The current App contract allows C3 no-interrupt delivery, but C4/interrupt is
  explicitly not enabled.
- No controller used C4, but `VisualToolDeliveryPreferences` still exposed a
  public `"c4"` constant that could be accidentally selected by future App-side
  code.

Fix:

- Removed the App-side C4 delivery-preference constant.
- Added static guards that keep `"c4"` out of the Unity visual-tool packet
  builder.
- Kept the HTTP response DTO's `allow_interrupt` receipt field as read-only
  backend metadata; the App does not act on it.

Verification:

- `uv run pytest tests/test_unity/test_app_v1_meta_ui_static.py -q` -> 28
  passed.
- Forbidden-path scan across VisualTools, formal camera, menu, and HUD found no
  C4 send constant, legacy snapshot RPC, Brain RPC, direct memory writes, or
  legacy BBox/Focus pulse calls.
- `uv run pytest tests/test_brain/test_visual_tool_lifecycle.py
  tests/test_brain/test_app_v1_monitor.py::test_console_action_endpoints_drive_app_tool_flows
  tests/test_ecp_event/test_w8_photo_upload_server.py::test_upload_publishes_photo_timebase_metadata
  tests/test_ecp_event/test_w8_observer_photo.py::test_asset_uploaded_timebase_metadata_reaches_evidence_ledger
  -q` -> 7 passed.
- Unity MCP `refresh_unity` on `ArSpike@a0c0295f7bd40ecc` completed ready with
  0 Console errors after an automatic MCP reconnect.
