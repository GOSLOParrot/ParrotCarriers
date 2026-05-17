# Parrot / Nanobot Persona Injection Audit

Updated: 2026-05-17

This workspace is the local map for Parrot and Nanobot persona tuning. It records where persona, room setting, task guidance, status notices, memory/scene context, and Nanobot worker instructions enter the system.

## Files

- `persona_injection_matrix.md` - the main table of injection sources, channels, levels, runtime effect, and risks.
- `setting_files_index.md` - grouped index of discovered setting files and task-guidance files.
- `startup_injection_map.md` - what GOSLO injects after LiveKit startup, before and after model placement.
- `runtime_polling_map.md` - which loops poll Blackboard / Task / IntentWorkspace and which paths are event-driven.
- `open_issues.md` - recorded persona, greeting, task-report, and Nanobot voice-contamination issues to resolve.
- `external_best_practices.md` - web-researched guidance from Gemini Live, LiveKit Agents, and Vision Agents docs.
- `import_files_reanalysis.md` - current reanalysis of RoomProfile `setting_file_refs` import behavior and problems.
- `import_package_refactor_proposal.md` - proposed future import-package directory scheme and classification contract.
- `information_access_model.md` - proposed model for classifying information before it can rise into prompt, IntentWorkspace, C3, C4, Reflex, Intent, or Task.
- `file_by_file_rewrite_tracker.md` - working ledger for rewriting stale persona/setting files one by one before any migration.
- `parrot_default_persona_rewrite_plan.md` - captured requirements and best-practice notes for rewriting the default GOSLO Parrot persona.

## Injection Taxonomy

| Level | Name | Runtime channel | Strength | Typical sources |
| --- | --- | --- | --- | --- |
| P0 | Boot system prompt | Agent/session construction builds initial instructions | Strongest for active session start | `soul.py`, persona markdown, Nanobot bootstrap files |
| C2 | Full instruction rebuild | `session.update_instructions(...)` / `agent.update_instructions(...)` | Strong; replaces active instruction text | persona switch, mode switch, room context, memory/scene context |
| C3 | Quiet chat-context notice | `session.update_chat_ctx(...)` with role `user` and status prefix | Medium; visible to model as contextual notice, usually no immediate speech | visual drift, RPC failures, DSG trigger notices |
| C4 | Proactive reply instruction | `session.generate_reply(instructions=...)` | High; asks model to speak now | welcome, recovered visual state, scheduler/Nanobot task result |
| T1 | Tool-result state header | state block prepended to selected tool results | Local and opportunistic | body/head/cognitive/ECP state returned after actions |
| L1.5 | Subconscious memory/intent staging | DSG buckets, staged refs, plan/archive queues | Indirect; not prompt unless surfaced later | triggers, roleplay buckets, observation commits |
| N0 | Nanobot bootstrap prompt | Nanobot `ContextBuilder` bootstrap files | Strong for Nanobot worker only | `AGENTS.md`, `SOUL.md`, `USER.md`, `TOOLS.md`, `MEMORY.md` |
| N1 | Nanobot runtime context | channel/time/chat metadata added to current user message | Low/medium; metadata, not instructions | telegram/weixin/parrot bus execution context |
| N2 | Nanobot heartbeat | `HEARTBEAT.md` plus heartbeat service prompt | Separate proactive worker loop | reminders, recurring checks, autonomous follow-up |

Important distinction: runtime C3 above is not the same thing as the historical "C3.x" Skill Seeker / Cursor analysis files under `.cursor/skills/**/references`. Those C3.x files are documentation or analysis artifacts unless a task explicitly imports them.

## Top Findings

1. Parrot's main active prompt is `src/parrot/brain/personas/<persona_id>.md` plus the active RoomProfile session-context block assembled by `src/parrot/brain/session_context_pack.py`.
2. Persona, mode, room, scene, and selected memory context are hot-swapped through C2 instruction rebuilds. Lightweight body/world notices use C3. Speech-triggering notices and background task results use C4.
3. `data/presets/ner_lineb_room.json` currently points Ner to `ner_companion.md`, LineB audio profile `lineb_ner_ja_test`, and four `setting_file_refs`: persona path (`persona_loader_only`), one roleplay setting (`llm+l1_5`), one scene draft (`llm`), and one `.cursor` report (`reference_only`).
4. Nanobot's current upstream runtime appears to assemble its prompt from workspace bootstrap files such as `SOUL.md`, `USER.md`, `AGENTS.md`, and `TOOLS.md`. The `systemPrompt` fields found in Nanobot JSON config mirrors are not referenced by the inspected upstream schema/context builder.
5. `~/.nanobot-parrot/config.json` differs from the deploy mirror/template. It currently points at an OpenRouter/Gemini model and a different Nanobot maid prompt string, but that prompt may be ignored by current Nanobot runtime code.
6. Several deploy mirror and env-style files contain live-looking credentials. They are indexed only by path/category here; do not paste values into tuning docs.

## Working Rule For Persona Tuning

When changing "feel", prefer editing the highest-level declarative source that owns the behavior:

| Desired change | First file to inspect |
| --- | --- |
| Parrot default voice / core rules | `src/parrot/brain/personas/goslo_parrot_default.md` |
| Ner / LineB conversational feel | `src/parrot/brain/personas/ner_companion.md` and the roleplay setting referenced by `ner_lineb_room.json` |
| Which persona/profile is active | `data/presets/*.json` and blackboard keys written by `preset_loader.py` |
| What context gets appended after persona | `src/parrot/brain/session_context_pack.py` and RoomProfile `setting_file_refs` |
| Status-notice behavior | `src/parrot/brain/context_injector.py` |
| Background task result speech | `src/parrot/scheduler/service.py` and `src/parrot/brain/agent.py` |
| Nanobot worker personality | active Nanobot workspace `SOUL.md`, `USER.md`, `AGENTS.md`, `TOOLS.md` |
