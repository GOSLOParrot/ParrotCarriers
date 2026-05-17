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
  falls back to `UnityWebRequest.error`, then to the local fallback label.
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

Verification pending in this pass:

- Focused static/backend tests, forbidden-path scan, Unity refresh/console, and
  `git diff --check`.

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
