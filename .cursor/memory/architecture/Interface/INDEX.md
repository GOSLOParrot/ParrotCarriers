---
status: ratified
category: interface-skeleton
status_note: "Cleaned 2026-05-10: Interface remains the backend/core-interface route. Formal App frontend design is in codex_workspace/design_workspace; smoke/self-check docs are not App completion evidence."
last_reviewed: 2026-05-10
ai_priority: high
ai_audience: "Chats touching src/parrot/** public surfaces or unity/ArSpike/Assets/Scripts/ParrotApp/** DTOs"
parent_doc: "../../INDEX.md"
related:
  - "../backend_interface_refinement_20260507.md (Brain Core SSOT)"
  - "../protocol_snapshot_p4.md (Protocol SSOT)"
  - "../bus_v4.md (Bus topology)"
  - "../dsg/workspace_index.md (DSG workspace)"
  - "menu_design_complete_20260507.md (menu design)"
  - "app_v1_current_status_and_test_report_20260510.md (clean App V1 status)"
  - "app_v1_room_setting_room_profile_interface_20260510.md (RoomSetting + RoomProfile contract)"
  - "app_v1_lineb_menu_readiness_interface_20260511.md (LineB menu readiness)"
  - "app_v1_model_capability_resolver_interface_20260511.md (model capability resolver)"
  - "app_v1_lineb_ner_realdevice_config_report_20260511.md (LineB + Ner device config)"
  - "app_v1_lineb_voiceprint_verifier_upgrade_20260511.md (LineB owner voiceprint verifier)"
  - "app_v1_session_context_pack_upgrade_20260511.md (Room setting files -> LLM/L1.5 session context)"
  - "app_v1_session_context_pack_audit_20260511.md (Cursor audit + bugfix on update_instructions / env-vs-BB / prompt_target)"
  - "app_v1_core_interface_audit_round2_20260511.md (Round 2: RoomProfile draft BB JSON / LineB cross-session reset / cosine dim guard / applyRoomProfile fallback warning)"
  - "app_v1_ecp_disconnect_audit_round3_20260511.md (Round 3: ecp_state_ingest disconnect cleanup — clear_bb_ecp_state dead-code + _last_seq cross-session carry-over, both empirically verified)"
  - "app_v1_menu_canvas_audit_round4_20260511.md (Round 4: 菜单画布 + 启动页 RPC — saveRoomProfile reserved id guard / payload typo warning / applyMenuSelection workspace fallback warnings / setAppCapabilityMode unknown-mode warning / 3 新 LiveKit RPC mirror)"
  - "audit_log_index_20260511.md (单页索引：4 轮共 14 bug + 1 gap + Codex 同步要点 + 跨工作区入口；此为 Cursor/Codex 共享 SSOT)"
---

# Interface Workspace Index

This directory is for **backend/core interface routing**. It is not the App frontend design route.

For the next App frontend chat, start from:

1. `codex_workspace/design_workspace/tasks/ACTIVE_CONTEXT.md`
2. `codex_workspace/design_workspace/unity_ar_app/startup_menu_design_v0_20260509.md`
3. `codex_workspace/design_workspace/sketches/startup_menu_landscape_v0.html`
4. `codex_workspace/design_workspace/unity_ar_app/main_hud_landscape_v0_20260509.md`
5. `codex_workspace/design_workspace/sketches/main_hud_landscape_v0.html`

Do **not** start App frontend work from `ParrotSmokeScene`, Web monitor smoke, longline self-checks, or this Interface index.

## App V1 Current Status

Formal App frontend status: **not complete**.

Clean status report:

- [`app_v1_current_status_and_test_report_20260510.md`](app_v1_current_status_and_test_report_20260510.md)

Blocking frontend tasks:

1. Room Setting: the startup `SCENE` entry must open an App preset/config page for saved Room / RoomProfile, LineA/LineB, Model, Persona, and Scene. Here Room means App saved profile, not LiveKit Room. Do not use a bare startup field named `Mode`; use `experience_mode`, `behavior_mode`, `capability_mode`, or `line_id`.
2. LineB menu upgrade: expose configurable LineProfile selection plus ASR/TTS readiness, Google ADC status, voiceprint/speaker state, echo risk, echo handling mode, recent TTS evidence, and last mic-input decision.
3. Ner second model: move Ner from raw asset to selectable production model path; startup must be able to select Brain pipeline, model, setting, scene, and skin.

Latest LineB + Ner validation route:

- [`app_v1_lineb_ner_realdevice_config_report_20260511.md`](app_v1_lineb_ner_realdevice_config_report_20260511.md)
- [`app_v1_lineb_voiceprint_verifier_upgrade_20260511.md`](app_v1_lineb_voiceprint_verifier_upgrade_20260511.md)
- [`app_v1_session_context_pack_upgrade_20260511.md`](app_v1_session_context_pack_upgrade_20260511.md)
- [`app_v1_session_context_pack_audit_20260511.md`](app_v1_session_context_pack_audit_20260511.md)
- [`app_v1_core_interface_audit_round2_20260511.md`](app_v1_core_interface_audit_round2_20260511.md)
- [`app_v1_ecp_disconnect_audit_round3_20260511.md`](app_v1_ecp_disconnect_audit_round3_20260511.md)
- [`app_v1_menu_canvas_audit_round4_20260511.md`](app_v1_menu_canvas_audit_round4_20260511.md)
- **🟢 [`audit_log_index_20260511.md`](audit_log_index_20260511.md)** ← 四轮审计单页索引；Cursor + Codex 共享 SSOT，先读这份再深入哪一轮

## Core Interface Rules

Keep the split:

- **Core interfaces**: stable public surfaces owned by Bus / Brain / DSG / Memory / Scheduler / Unity transport.
- **Business flows**: user-visible workflows that compose core interfaces.

Business flow docs must not copy large code signatures. Use the A-D discipline:

| Field | Meaning |
|:--|:--|
| A | Read back at most 3 relevant source docs. |
| B | Decide whether existing core interfaces can compose the flow. |
| C | If no, list missing core surfaces without implementing protocol changes in the business doc. |
| D | Define the input and observable success/failure signal. |

## Core Sources

| Area | Source |
|:--|:--|
| Bus / topology / topics | `../bus_v4.md`, `../protocol_snapshot_p4.md` |
| Brain public API | `../backend_interface_refinement_20260507.md` |
| DSG L1.5 / L2-B / triggers | `../dsg/workspace_index.md` |
| Memory / Graphiti | `../dsg/dsg_protocol_archive_v1_20260506.md` and Graphiti skill docs |
| Scheduler / Blackboard / BT | `../protocol_snapshot_p4.md`, `../sprint4_protocol_v2_ecp.md` |
| Menu / presets | `menu_design_complete_20260507.md`, `../backend_interface_refinement_20260507.md` |

## Active Interface Docs

| File | Status | Role |
|:--|:--|:--|
| `INDEX.md` | active | This clean interface route. |
| `concept_dictionary_20260507.md` | active | Terminology and route hints. |
| `legacy_issues_split_20260507.md` | active | P2.5/P3 issue split and dispatch hints. |
| `menu_design_complete_20260507.md` | active / design | Menu design SSOT; frontend implementation must still follow Design workspace page flow. |
| `obsidian_true_connection_guide_20260509.md` | active / business guide | Obsidian profiles, L1.5, L2-B, IntentWorkspace boundaries. |
| `google_calendar_nanobot_true_connection_guide_20260509.md` | active / business guide | Google Calendar + Nanobot read/draft/writeback boundaries. |
| `photo_memory_awareness_true_connection_guide_20260509.md` | active / business guide | Photo upload, PhotoNode, IntentWorkspace, awareness boundaries. |
| `chatB_true_connection_completion_record_20260509.md` | completed / record | True-connection fixes and remaining gaps. |
| `app_v1_facade_core_business_interface_20260510.md` | active / backend facade | App V1 facade and business-interface coverage; not frontend completion evidence. |
| `app_v1_room_setting_room_profile_interface_20260510.md` | active / business interface | Startup RoomSetting, user-facing Room save/new/select, menu persistence, and capability compatibility contract. |
| `app_v1_lineb_menu_readiness_interface_20260511.md` | active / business interface | LineA/LineB menu readiness, configurable LineProfile, ASR/TTS/ADC status, voiceprint/speaker state, echo risk, and runtime guard evidence. |
| `app_v1_model_capability_resolver_interface_20260511.md` | active / business interface | Brain-side model manifest mirror, RoomSetting capability decisions, and custom capability tool gating. |
| `app_v1_lineb_ner_realdevice_config_report_20260511.md` | active / config report | LineB real-device config, Ner RoomProfile/model/persona setup, and remaining production wiring plan. |
| `app_v1_session_context_pack_upgrade_20260511.md` | active / backend interface | Room setting files now flow into LLM session context and UUID-free Obsidian roleplay L1.5 payloads. |
| `app_v1_current_status_and_test_report_20260510.md` | active / status | Single clean status report for App V1 route cleanup. |
| `minecraft_parrot_animation_worklog_20260510.md` | worklog | Animation correction record; unrelated to App frontend completion. |

## Superseded Or Historical

These may remain in git history or archive, but they should not guide new App frontend work:

| File | Status | Reason |
|:--|:--|:--|
| `interface_design_and_how_todo_v0_20260507.md` | superseded | Copied too much call-stack detail; use this index and business A-D discipline instead. |
| `interface_design_supplement_20260507.md` | superseded | Historical supplement to the failed v0 approach. |
| App V1 longline/self-check/frontend-audit files | removed/superseded | They mixed smoke/test evidence with App frontend completion. Use the clean status report instead. |

## Entry Discipline

If the task is App page design or Unity frontend implementation, read the Design workspace first.

If the task changes backend protocol, DTOs, BB keys, RPC methods, or public Python surfaces, use this Interface route and the core sources above.
