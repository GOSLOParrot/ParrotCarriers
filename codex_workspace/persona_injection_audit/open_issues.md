# Persona Injection Open Issues

Updated: 2026-05-17

## PIA-001 Double Greeting / Startup Speech Leak

Status: first runtime fix landed 2026-05-17. `session/goslo_placed` and
`session/first_greeting_sent` were added as Brain session-policy BB facts;
`should_generate_reply()` now blocks non-safety proactive speech before
placement, and `onGosloPlaced` is the only normal pre-placement exemption.
Remaining work: decide whether suppressed pre-placement task results should be
queued in IntentWorkspace for a later digest instead of only staying silent.

Observed: sometimes GOSLO speaks once on connection and then speaks again after placement.

Intended rule: `onSceneReady` is readiness only; first greeting should be C4 from `onGosloPlaced` after explicit placement.

Likely paths:

- User mic and Gemini session are already live in `FullARCompanion` before placement.
- Scheduler / Nanobot result listener can C4 before placement.
- ContextInjector heavy C4 can speak before placement.
- Legacy DSG trigger listener can C4 for `missing/new`.
- Old docs still mention `onSceneReady -> greeting`.
- Greeting dedupe is only process-local, not a shared placement/greeting Blackboard fact.

Candidate fix: add explicit `session/goslo_placed` and `session/first_greeting_sent` gates. Before placement, downgrade or queue all non-safety C4.

## PIA-002 Nanobot / Maid Voice Leakage Into Parrot

Status: first runtime fix landed 2026-05-17. Scheduler-result C4 instructions
now treat worker fields as untrusted quoted data, explicitly forbid imitating
Nanobot / maid style, and ask for a concise GOSLO-voice digest after placement.
User clarification: this should not make GOSLO flat or sterile. GOSLO's own
light refined mansion-young-lady / proud tone is allowed when she summarizes;
only the source worker's voice must not take over.
Remaining work: move rich worker reports into structured fields and/or
IntentWorkspace instead of passing a single free-form `result_summary`.

Observed: GOSLO can suddenly speak in a catgirl/maid tone.

Likely path: Nanobot result summary is embedded raw into Brain C4 instructions: "Task type: ..., result: {summary}. Briefly tell the user..." If Nanobot's own worker persona writes a styled result, Gemini may imitate that style.

Candidate fix: treat Nanobot output as quoted data, not style. Add a scheduler-result quarantine rule:

- Never imitate source worker style or role.
- Summarize in active GOSLO persona only.
- Prefer structured `result_summary`, `facts`, `actions`, `source_worker_style` fields over one free-form string.
- Stage rich Nanobot report in IntentWorkspace and speak only a clean one-line digest.

## PIA-003 Historical Docs Conflict On Greeting

Observed: some older interface docs mention `onSceneReady -> greeting`; newer code and comments say greeting is deferred until `onGosloPlaced`.

Candidate fix: mark old docs as historical and add a current startup invariant doc. The current source of truth should be:

- `src/parrot/brain/agent.py` `onSceneReady` returns `deferred_until_goslo_placed`.
- `unity/ArSpike/Assets/ParrotApp/Runtime/Scripts/Lifecycle/AppStartupFlowController.cs` intentionally does not greet on LiveKit connect.
- `FormalModelPlacementController.cs` reports `onGosloPlaced` only after actual placement.

## PIA-004 Task Result Speech Before Placement

Status: first runtime fix landed 2026-05-17. The central session policy now
suppresses `scheduler_result` speech before `session/goslo_placed=True`.
Remaining work: queue or surface suppressed results through a non-speaking UI /
IntentWorkspace path if the user needs them after placement.

Observed risk: background tasks can report with C4 before GOSLO is placed.

Current path: `SchedulerService._listen_nanobot_results` publishes to `CH_SCHEDULER_TO_BRAIN`; Brain listener calls `generate_reply`.

Candidate fix: if `session/goslo_placed` is false, queue result in IntentWorkspace and add one C3 note after placement, or surface it as UI status only.

## PIA-005 C3/C4 Channel Names Are Not Clearly Separated From Historical C3.x Docs

Observed risk: "C3" can mean runtime C3 chat-context notice or old Skill Seeker / Cursor C3.x reference docs.

Candidate fix: keep the taxonomy in `INDEX.md` and use names like `runtime_C3_status_notice` versus `historical_C3_reference`.

## PIA-006 Startup Injection Ownership Is Too Implicit

Observed risk: LiveKit startup starts many watchers at once. The guide does not yet say which startup changes are allowed to speak before placement.

Candidate fix: promote `startup_injection_map.md` into the human task guide and add a test for "no pre-placement C4 except safety".

## PIA-007 Nanobot Config Source Boundary

User clarification: Nanobot configuration files live in the Nanobot repo. ParrotCarriers may have launchers, mirrors, and stubs, but active Nanobot persona/config must be verified in `D:/GOSLOParrot/nanobot` and the active Nanobot workspace.

Candidate fix: keep ParrotCarriers audit entries marked as "launcher/mirror/stub" unless verified against the Nanobot repo runtime.

## PIA-008 Mixed Import Container

Observed: `RoomProfile.setting_file_refs` mixes persona paths, runtime setting notes, scene drafts, and audit/reference reports.

Current safety: `session_context_pack.py` classifies persona paths as `persona_loader_only` and `.cursor` reports as `reference_only`.

Remaining risk: the configuration shape still suggests "all entries are setting imports", which makes human tuning and future migrations error-prone.

Candidate fix: introduce a package manifest with typed arrays or typed import entries: `runtime_llm`, `runtime_l15`, `c3_notices`, `c4_speech_events`, `contracts`, and `references`.

## PIA-009 Markdown Default To LLM Is Too Broad

Observed: unmarked ordinary `.md` files default to `llm`. This causes scene/config drafts such as `ner_mochi_scene_v0_20260511.md` to enter live prompt without explicit runtime consent.

Candidate fix: require explicit frontmatter or manifest target for runtime prompt import. Treat unmarked markdown as `reference_only` in the future package contract.

## PIA-010 Runtime Imports Carry Dev/Test Language

Observed: the current roleplay and scene imports include validation wording, source-boundary explanations, draft status, implementation gaps, and engineering checklist content.

Risk: GOSLO may sound like a test harness or mention implementation state during normal companion conversation.

Candidate fix: split source docs into runtime sections and reference sections, or add section-level imports in the manifest.

## PIA-011 No Section-Level Import Contract

Observed: the loader currently imports a trimmed excerpt of the whole file. It cannot say "only import `## Runtime LLM Context`" or "send `## L1.5 Seed` to L1.5".

Candidate fix: support manifest fields like `sections`, `exclude_sections`, and `max_chars` per entry.

## PIA-012 Reference Reports Are Loaded As Session Sources

Observed: `.cursor` reports are safely marked `reference_only`, but still appear as resolved `SessionContextSource` rows when listed in `setting_file_refs`.

Candidate fix: move audit/report material to a future `references/audit/` package directory or `audit_refs` manifest field, separate from runtime imports.

## PIA-013 Import Package Has No C4 Gate Metadata

Observed: startup greeting, task result speech, and visual recovery are C4-like, but imported docs do not have a place to declare `placement_gated`, `speak_now_allowed`, or `style_quarantine` policy.

Candidate fix: future import packages should include `c4/` speech-event templates and manifest gate metadata. Default C4 policy should be "blocked before placement except safety".

## PIA-014 Stale Setting Files Need File-By-File Rewrite Ownership

Observed: the current persona / roleplay / scene setting corpus is small, but much of it was written for App V1 validation and older startup assumptions. Several files mix live persona, roleplay seed, validation checklist, source boundary, and implementation status.

Risk: trying to migrate the whole import package first would preserve stale wording in a cleaner container. The safer next move is to rewrite one file at a time and give each file one owner, one runtime target, and one speech policy.

Candidate fix: use `file_by_file_rewrite_tracker.md` as the working ledger. For every file, decide:

- what stays as runtime prompt
- what moves to L1.5 / IntentWorkspace / contract / reference
- what may speak now, and what must wait for placement or a user turn
- what tests prove the live prompt is clean

## PIA-015 Capability Text Can Outrun Menu / Manifest Gates

Observed: setting files can describe capabilities such as face expressions, touch, fly/perch, photo awareness, SVA evidence, and task dispatch, but the real runtime availability depends on model manifest, menu selection, app capability mode, video tier, env rollout gates, and current scene wiring.

Risk: GOSLO may promise or imply an ability that is not registered in the active menu/model/scene.

Candidate fix: every rewritten runtime setting file must name capability ownership rather than merely describing ability. Prompt text can say "when available"; execution truth must come from the gate.

## PIA-016 IntentWorkspace / Blackboard / Task Visibility Is Not A Setting Contract Yet

Observed: the runtime has Blackboard state, IntentWorkspace staged refs, task metadata, Nanobot reports, SVA evidence, and C3 notices, but old setting docs do not say which of those are visible to the model, which are just working memory, and which may be spoken.

Risk: useful internal state may be over-shared into prompt, while important task facts may be spoken with the wrong authority or style.

Candidate fix: every imported fact should carry an information envelope: source, owner, authority, freshness, runtime target, speech policy, style policy, capability gate, and event layer.

## PIA-017 Current Collaboration Voice Is Not Captured Cleanly

Observed: the Ner files emphasize LineB and real-device validation more than the current collaboration style: quiet setup help, short natural replies, state-aware companionship, and one-step-at-a-time tuning.

Risk: the persona may sound like a validation assistant or task harness instead of a companion that understands the current room, menu gates, task layer, and user intent.

Candidate fix: rewrite `ner_companion.md` after the import boundaries are logged. Keep identity and voice in the persona file; move validation details, device checklist, and implementation caveats into runtime scene context or reference docs.

## PIA-018 Default Parrot Voice Is Not Locked To A Stable Female Voice

Status: first fix landed 2026-05-17. LineA default is now `Aoede`, with empty/unknown `GEMINI_LIVE_VOICE` falling back to that fixed default. Remaining work: expose/check the live startup status so the app can catch an unexpected provider/runtime fallback.

User requirement: GOSLO should speak with a fixed female voice. Observed problem: the runtime sometimes sounds male or changes timbre. User clarified that the fix target is LineA; LineB has its own TTS.

Local findings:

- LineA uses Gemini Live `google.realtime.RealtimeModel` and reads `GEMINI_LIVE_VOICE`; the default is now locked to `Aoede`.
- LineB uses a separate STT/LLM/TTS pipeline and reads `LineProfile.tts.voice_name`, with env overrides such as `GOOGLE_TTS_VOICE` or `PARROT_LINEB_CARTESIA_VOICE_ID`.
- Therefore voice consistency is a runtime configuration contract, not only a persona prompt rule.

Risk: if the active line or env override changes, the same Parrot persona may speak with a different voice.

Candidate fix: define a default Parrot voice policy with explicit LineA `GEMINI_LIVE_VOICE`; add startup diagnostics that surface active line, model, and voice before START. The persona file may say "GOSLO presents as a young lady parrot", but the LineA audio config must enforce the actual voice. LineB remains governed by its own TTS profile.

## PIA-019 Parrot / Nanobot Estate Roles Need A Clean Boundary

Status: first persona pass landed 2026-05-17 in `goslo_parrot_default.md`. Remaining work: add the Parrot-side Nanobot result contract so task reports cannot carry Nanobot's maid voice into GOSLO speech.

User requirement: GOSLO is a parrot young lady of the shared mansion. The user is one of the mansion owners and also a friend of the shared mansion. Nanobot is the mansion maid.

Risk: if these roles are scattered across Parrot persona, Nanobot persona, task results, and room setting docs, GOSLO may accidentally adopt Nanobot's maid voice or speak as an operator instead of a companion.

Candidate fix: Parrot default persona owns GOSLO's identity and relationship to the user. Nanobot workspace owns the maid identity. Parrot-side task/result docs may only describe Nanobot as a source of service reports and must treat Nanobot output as quoted data.

## PIA-020 Reflex / Intent / Work State Awareness Needs Speech Discipline

Status: first persona pass and first runtime gate landed 2026-05-17.
`goslo_parrot_default.md` now states the Reflex / Intent / Work speech
discipline; runtime C4 now blocks before placement, and Scheduler/Nanobot
results are style-quarantined. C3 / IntentWorkspace notices remain allowed
before placement when the session is not Silent, so GOSLO can quietly know state
without speaking. Remaining work: classify every C3/C4 source with explicit
metadata and add IntentWorkspace queueing for suppressed work results.

User requirement: GOSLO should understand real-time state across Reflex / Intent / Work layers, but not become chatty or narrate every state change.

Risk: C3/C4/status notices can cause GOSLO to over-report internal state, especially when task results, Blackboard updates, SVA evidence, or IntentWorkspace refs arrive.

Candidate fix: default Parrot persona should include a state-awareness rule:

- Reflex: act fast when enabled, usually without verbal explanation.
- Intent: keep track of selected goal/state and mention it only when useful for the user turn.
- Work: background task/Nanobot/SVA reports stay quiet unless the user asked, the result is actionable, or a placement-gated C4 event is explicitly allowed.

## PIA-021 LineA / LineB Menu Switch And `.env` Fallback Are Easy To Misread

Status: recorded 2026-05-17. Local inspection found no `data/runtime_config.json`
in the current workspace, while `.env` still contains
`PARROT_LLM_PIPELINE=line_b` and `PARROT_ACTIVE_LINE_PROFILE_ID=lineb_ner_ja_test`.
The Brain resolver order is runtime config file, then Blackboard
`global/active_line_id`, then env, then default `line_a`. Therefore `.env`
being `line_b` is not itself proof that the menu is broken; it is the cold-start
fallback when no higher-priority runtime selection exists.

Risk: users may expect a menu toggle to hot-swap the currently running
`AgentSession`, but the active voice pipeline is a Tier 1 / cold-start choice.
The menu can write the selected line into RoomProfile / Blackboard, while the
running session continues on the pipeline it was built with until Brain
reconnects or the orchestrator writes runtime config and forces reconnect.

Candidate fix: make the App status show both selected line and running line,
including the source (`runtime_config`, `blackboard`, `.env`, or default), and
make a line-switch menu action explicitly request reconnect / runtime_config
application instead of looking like an immediate hot toggle.
