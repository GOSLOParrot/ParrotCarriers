---
title: Time-Aligned Evidence Interface
date: 2026-05-15
status: active-web-backend-ssot / shared-core-candidate
category: interface-ssot
owner: Web Console Chat / Interface
source_chat: web-console
writer: Codex
confirmed_by:
  - web-console
confirmed_at: 2026-05-15
approved_by: user
origin_business_doc: codex_workspace/design_workspace/backend_interface_map/web_console/observability_runtime_business_flow_20260513.md
candidate_queue:
  - CORE-006
  - CORE-008
  - CORE-009
  - CORE-012
  - CORE-014
consumers:
  - Brain Intent tools
  - Web Console Runtime Flow
  - DSG L1.5 / L2-B
  - Future Unity App / SVA producers after App-lane review
scope: TimebaseStamp, TimeAlignedSampleRef, TemporalEvidenceLedger, identify_object evidence lookup, LiveKit/frame-cache/photo/BBox evidence flow, GOSLO C3 awareness staging
source:
  - src/parrot/brain/vision/evidence.py
  - src/parrot/brain/vision/frame_cache.py
  - src/parrot/brain/vision/livekit_sampler.py
  - src/parrot/brain/vision/evidence_awareness.py
  - src/parrot/brain/vision/tool_lifecycle.py
  - src/parrot/brain/observer/visual_tool.py
  - src/parrot/brain/app_monitor_server.py
  - src/parrot/web_console/vision_evidence.py
  - src/parrot/brain/identify_object.py
  - codex_workspace/design_workspace/backend_interface_map/core_interface_candidate_queue_20260513.md
  - codex_workspace/design_workspace/backend_interface_map/web_console/observability_runtime_business_flow_20260513.md
---

# Time-Aligned Evidence Interface

This file is the SSOT for the Web/backend implementation of time-aligned
evidence. It is also the staging document for CORE-012. It does **not** ratify
new Unity/App top-level DTO fields yet.

The design goal is simple: every media, attention, ASR, and CV sample must be
findable on one timeline, and `identify_object` must use stored evidence rather
than the removed inline snapshot RPC path.

## 1. Ratified Web/Backend Rules

1. `EcpEvent.created_at` is envelope time, not sample time.
2. `EcpCommand.issued_at` is command envelope time, not sample time.
3. V1 sample timestamps live in optional nested metadata:
   - `EcpEvent.payload["timebase"]`
   - `EcpCommand.meta["timebase"]`
   - HTTP upload metadata or headers
   - LiveKit sampler/frame-cache metadata
4. ECP/RPC/DataChannel messages carry signals and lightweight refs only.
   Image bytes travel through HTTP/storage or the backend frame cache.
5. `TemporalEvidenceLedger` stores bounded evidence refs and metadata. It is
   not the long-term image archive.
6. `identify_object` resolves `evidence_id`, `bbox_ref_id`, `focus_ref_id`, or
   `target_time_ms` to a stored `TimeAlignedSampleRef`; if no suitable image is
   available it records a pending request and falls back to text/L2-B/Graphiti
   paths honestly.
7. BBox, Focus, and magnifier are evidence/ref tools, not special L2-B
   `NodeKind` values.
8. Evidence Awareness may stage a `visual_evidence_hint` in IntentWorkspace and
   may deliver C3 context through `ContextInjector`. It does not call
   `generate_reply()` and does not interrupt speech in V1.
9. Evidence-to-memory promotion is preview-only for now:
   `/api/vision/evidence/memory-draft` returns a draft L1.5 Observation /
   RefBinding plan but has no apply route until CORE-012 / CORE-006 review.
   Its receipt carries top-level audit fields marking read-only, no L1.5
   mutation, no L2-B mutation, and no RefBinding mutation.
10. `VisualToolEvidenceLifecycle.backend_v1` is the current App/backend
    contract for BBox/MAG/Focus tools. It is not the DSG L3 attention model.
    It accepts stable interaction milestones, records evidence refs, stages
    IntentWorkspace, and resolves C3/no-interrupt policy while keeping image
    bytes in HTTP/storage.

## 2. Core Web/Backend Models

`TimebaseStamp`

| Field | Meaning |
|:--|:--|
| `clock_domain` | Producer clock namespace: `brain`, `unity`, `web`, `livekit_track`, `asr`, `cv_worker`. |
| `wall_time_ms` | Producer wall-clock sample time in epoch ms. |
| `monotonic_ms` | Optional producer monotonic clock in ms. |
| `media_time_us` | Optional media-track timestamp, e.g. LiveKit video/audio sample timestamp. |
| `sequence` | Optional producer-local frame/event sequence. |
| `estimated` | True when the stamp was inferred from envelope time or fallback time. |
| `source_id` | Producer id, participant id, track name, module id, or upload source. |

`TimeAlignedSampleRef`

| Field | Meaning |
|:--|:--|
| `evidence_id` | Stable evidence id, currently `ev_*`. |
| `kind` | `video_frame`, `image_asset`, `bbox_focus`, `asr_segment`, `cv_detection`, `evidence_request`. |
| `status` | `pending`, `ready`, `missing`, or `error`. |
| `timebase` | Required sample-time stamp. |
| `asset_path` / `asset_uri` | Local storage or URI pointer; image bytes are not embedded. |
| `mime_type` | Asset MIME type. |
| `region` | Optional crop/BBox region with coordinate space. |
| `related_refs` | Generic related refs. |
| `bbox_refs` / `focus_refs` | Region refs that anchor BBox/Focus/magnifier workflows. |
| `request_id` | Pending request id when evidence is missing. |
| `room_id` / `track_sid` | LiveKit or session provenance. |
| `description` | Human/operator-readable summary. |
| `quality_flags` | Optional quality notes such as low confidence or estimated time. |
| `meta` | Redacted producer metadata; no secrets and no image bytes. |

## 3. Producers

| Producer | Current path | Evidence kind | Notes |
|:--|:--|:--|:--|
| HTTP photo upload | `photo.asset_uploaded` observer and optional upload timebase headers | `image_asset` | Full images land in storage; preview/ref policy is separate Photo Awareness. |
| LiveKit frame cache | `record_livekit_frame_bytes()` | `video_frame` | Storage-backed entry point for encoded frames. |
| Brain LiveKit sampler | `parrot.brain.vision.livekit_sampler` | `video_frame` | Low-FPS room-scoped sampler; consumes camera and screen-share tracks. |
| Web frame-cache smoke | `POST /api/vision/evidence/frame-cache/upload` | `video_frame` | Operator/debug ingress only, not production capture. |
| BBox/Focus threshold | `FocusBboxThreshold` + `bridge_attention_threshold_to_goslo()` | `bbox_focus` plus staged hint | Does not capture a frame; resolves nearest stored frame/photo or records pending request. |
| App BBox/MAG lifecycle | `POST /api/app/visual-tool/event` or ECP `visual_tool.lifecycle` | `bbox_focus` or `image_asset` | BBox binds BBox refs and defaults to C3 on confirm; MAG binds Focus refs and defaults to `intent_only` unless explicitly sent. C4 requests are audited and downgraded in V1. |
| App BBox/MAG asset upload | `POST /api/app/visual-tool/asset/{asset_id}` | `image_asset` | Stores a rendered crop/preview under `data/visual_tools/{yyyy-mm-dd}/` or configured root, returns `asset_path` for the lifecycle event. |
| Future ASR | ASR segment worker | `asr_segment` | Must carry shared timebase before promotion. |
| Future SAM2/DINOv2/sentinel | CV worker | `cv_detection` | Must attach source id, sample time, optional region, and asset/evidence refs. |

## 4. GOSLO Notification Levels

This interface uses the Trigger/Awareness taxonomy:

- L0: evidence is recorded only.
- L1: evidence ref is staged in IntentWorkspace.
- L2: Blackboard notice records policy and audit status.
- C3: `ContextInjector` appends compact context; no speech.
- C4/I0: not enabled for Evidence V1.

Current evidence and photo awareness use C3 at most. C4 safe-turn speech needs
separate policy review, cooldown/quiet-hour rules, live LineA/LineB smoke, and
user approval.

## 5. Web Console Routes

| Route | Status | Purpose |
|:--|:--|:--|
| `GET /api/vision/evidence/status` | implemented | Ledger, frame cache, LiveKit sampler, and awareness status. |
| `GET /api/vision/evidence/timeline` | implemented | Recent evidence rows with optional kind filter. |
| `GET /api/vision/evidence/{evidence_id}` | implemented | Single evidence detail. |
| `POST /api/vision/evidence/request` | implemented | Locate nearest evidence or record pending request. |
| `POST /api/vision/evidence/stage-hint` | implemented | Stage evidence into IntentWorkspace as a `visual_evidence_hint`. |
| `POST /api/vision/evidence/frame-cache/upload` | implemented | Debug/operator frame-cache upload. |
| `GET /api/vision/evidence/screen-share-smoke` | implemented | Read-only no-camera screen-share proof; requires same row to be fresh and screen-share-like. |
| `POST /api/vision/evidence/memory-draft` | implemented / preview-only | Draft Evidence -> L1.5/Ref/L2-B mapping; no apply route. |
| `POST /api/vision/evidence/tool-lifecycle` | implemented / debug | Web debug mirror for the App visual-tool lifecycle handler. |
| `POST /api/app/test/visual-attention` | implemented | Web debug BBox/Focus threshold event. |

## 5a. App Visual Tool Route

| Route/Event | Status | Purpose |
|:--|:--|:--|
| `POST /api/app/visual-tool/event` | implemented | App HTTP route for BBox/MAG/Focus lifecycle events. It returns a receipt with `ref_id`, `evidence`, `salience`, `delivery`, `awareness`, and `audit`. |
| `POST /api/app/visual-tool/asset/{asset_id}` | implemented | App HTTP upload for BBox/MAG rendered crop/preview bytes. Returns `asset_path` plus an `image_asset` evidence row. |
| ECP `visual_tool.lifecycle` | implemented | Reliable DataChannel event bridged into the same handler by `brain.observer.visual_tool`. |
| BB `transient/visual_tool_lifecycle_receipt` | implemented | Latest receipt, writer `brain.vision.tool_lifecycle`. |

Accepted phases: `preview_start`, `hover`, `drag_update`, `resize_update`,
`dwell_tick`, `lock`, `unlock`, `settings_open`, `confirm`,
`explicit_send`, `cancel`, and `release`.

Delivery policy:

- BBox `confirm` / `explicit_send`: stage IntentWorkspace and request C3.
- MAG/Focus `confirm`: stage IntentWorkspace silently.
- MAG/Focus `explicit_send` or `delivery_preference=c3`: request C3.
- `delivery_preference=c4`: recorded and downgraded to C3; no interrupt.
- `cancel` / `release`: unbind ref and do not notify.

## 6. Shared Promotion Blockers

CORE-012 is still a shared candidate until these are true:

1. Real Unity/App or Web screen-share LiveKit video smoke proves track
   selection, freshness/stale behavior, reconnect behavior, and storage load.
2. App lane reviews which timebase/evidence fields should be visible to Unity
   DTOs versus staying backend-local.
3. CORE-006 RefBinding apply rules are reviewed for photo/file/BBox/focus refs.
4. ASR/CV worker sample semantics are aligned to the same timebase.
5. C4 safe-turn speech and interruption policy are reviewed separately.
6. BBox/MAG production controls still need App controller wiring, phone/screen
   smoke, and tool-rendered crop upload throughput proof. The formal lifecycle
   packet and a basic HTTP asset route are implemented as CORE-014 backend/App
   V1. Current
   `bbox.placed` / `focus.anchored` events remain a conservative compatibility
   bridge only.

## 7. Validation Snapshot

2026-05-15 focused validation:

- Web/Time-Evidence/threshold/identify regression: `81 passed`.
- Frontend typecheck/build passed.
- Browser Runtime smoke confirmed LiveKit Bridge, Time/Evidence, Screen Share,
  and Check Samples controls render without console errors.
- Browser Runtime smoke clicked `检查采样`; the inline diagnostic card rendered a
  not-ready verdict with no dev-console errors, correctly reflecting that no
  fresh screen-share sampler/frame-cache row was present yet.
- Evidence-to-memory audit fix verified: `memory-draft` success and missing
  sample receipts now expose read-only/no-mutation audit fields and CORE
  candidate markers.
- Secret scan found no committed LiveKit, DeepSeek, Google, or orchestrator
  secrets.

## 8. Requirement Audit

| Requirement | Status | Notes |
|:--|:--|:--|
| Unified timebase for media/attention/ASR/CV | implemented for Web/backend V1 | ASR/CV producers still need future adapters. |
| Do not change ECP/RPC top-level schema in V1 | satisfied | Optional timestamps live in payload/meta/upload metadata. |
| Temporal Evidence Ledger | implemented | Bounded in-process ledger plus storage pointers. |
| `identify_object` no old snapshot RPC | implemented | Missing BBox/Focus refs record pending requests instead of grabbing unrelated newest frame. |
| LiveKit frame-cache producer | implemented / needs live smoke | Unit/fake-room coverage exists; real screen-share/Unity track smoke is still required. |
| Photo upload / snapshot metadata alignment | implemented | Photo bytes remain HTTP/storage assets. |
| BBox/Focus threshold bridge | implemented conservatively | Stages hints or pending requests; no capture, no L2-B write, no speech. |
| App BBox/MAG production tool controllers | backend-unblocked / app-gated | Backend V1 route and ECP bridge are implemented. App can build controllers behind flags; production publish still waits for phone/screen-share smoke, optional crop asset route, and UI/body-feel review. |
| GOSLO injection channel clarity | implemented for C3 | IntentWorkspace is passive L1; `ContextInjector` C3 is the first strong notice; C4 is pending. |
| Web Time/Evidence panel | implemented | Runtime Flow only; Memory Graph consumes evidence later through drafts/refs. |
| Evidence -> L1.5/L2-B | preview-only | `memory-draft` exists; apply waits for CORE-012/CORE-006 review. |
| Shared App DTO promotion | not done | Blocked intentionally until App/Web review and live smoke. |

## 9. Change Log

- 2026-05-15: Created as Web/backend SSOT and CORE-012 staging document after
  user approval in the Web Console chat. Records that top-level Unity/App DTOs
  are unchanged and shared promotion still requires App/Web review.
- 2026-05-16: Added App-blocker audit result for BBox/MAG. At audit time the
  backend evidence spine was usable for conservative tests, while production
  App tool emission still needed CORE-014 `VisualToolEvidenceLifecycle`,
  HTTP/storage thinking for tool-rendered crops/snapshots, live evidence
  smoke, and C3/C4 policy review. This kept current Unity/App DTOs unchanged
  and avoided conflating visual-tool salience with the future DSG L3 attention
  module.
- 2026-05-16: Implemented CORE-014 backend/App V1:
  `VisualToolLifecyclePacket`, `/api/app/visual-tool/event`, ECP
  `visual_tool.lifecycle`, Web debug route
  `/api/vision/evidence/tool-lifecycle`, App asset upload route
  `/api/app/visual-tool/asset/{asset_id}`, BB receipt
  `transient/visual_tool_lifecycle_receipt`, BBox strong/C3 default, MAG weak
  `intent_only` default, C4 downgrade, and no image bytes in ECP/RPC. Focused
  validation: `7 passed`.
