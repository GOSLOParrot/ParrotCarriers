# Setting Files Index

Updated: 2026-05-17

## Runtime Parrot Persona Files

| Path | Status | Notes |
| --- | --- | --- |
| `src/parrot/brain/personas/goslo_parrot_default.md` | Runtime persona | Default GOSLO Parrot identity, modes, tool rules, visual-state behavior. |
| `src/parrot/brain/personas/ner_companion.md` | Runtime persona | Ner/LineB test persona and voice/style constraints. |
| `src/parrot/brain/persona_loader.py` | Runtime loader | Parses persona frontmatter/sections and honors `PARROT_PERSONA_DIRS`. |
| `src/parrot/brain/soul.py` | Runtime assembler | Active persona selection and session-context append point. |

## Runtime Parrot Selectors And Profiles

| Path | Status | Notes |
| --- | --- | --- |
| `data/presets/default.json` | Runtime selector | Default model/persona/mode/scene/workspace. |
| `data/presets/ner_lineb_room.json` | Runtime RoomProfile | Central Ner LineB selector for persona, line profile, setting refs, scene, skin. |
| `src/parrot/brain/preset_loader.py` | Runtime loader/writer | Applies RoomProfile to blackboard keys. |
| `src/parrot/brain/session_context_pack.py` | Runtime context builder | Converts RoomProfile and setting refs into prompt blocks and L1.5 imports. |
| `data/line_profiles/lineb_google_default.json` | Runtime audio/LLM profile | Google default line profile. |
| `data/line_profiles/lineb_ner_ja_test.json` | Runtime audio/LLM profile | Ner LineB ASR/TTS/voiceprint/echo profile. |
| `src/parrot/brain/line_profile.py` | Runtime loader | Loads LineProfile and applies env overrides. |
| `data/registries/setting_change_tier.json` | Runtime policy registry | Maps setting changes to hot/reconnect/restart/infra tiers. |

## RoomProfile Setting References

| Path | Inferred target | Notes |
| --- | --- | --- |
| `src/parrot/brain/personas/ner_companion.md` | `persona_loader_only` | Present in `ner_lineb_room.json` `setting_file_refs`, but runtime classifies it as persona-owned and does not append it as a setting source. This is safe in current code but confusing. |
| `codex_workspace/design_workspace/unity_ar_app/ner_roleplay_setting_obsidian_v0_20260511.md` | `llm+l1_5` | Frontmatter `profile: roleplay`; roleplay and style setting source. |
| `codex_workspace/design_workspace/unity_ar_app/ner_mochi_scene_v0_20260511.md` | `llm` | Scene/placement/capability setting source. |
| `.cursor/memory/architecture/Interface/app_v1_lineb_ner_realdevice_config_report_20260511.md` | `reference_only` | Technical report; not prompt-injected by default because it is under `.cursor`. |

## Runtime Injection Code

| Path | Channels | Notes |
| --- | --- | --- |
| `src/parrot/brain/context_injector.py` | C2, C3, C4 | Main channel definition for instruction rebuilds, quiet status notices, proactive replies. |
| `src/parrot/brain/mode_watcher.py` | C2 | Behavior-mode hot-swap. |
| `src/parrot/brain/agent.py` | P0, C2, C4 | Assistant construction, blackboard watchers, greeting, scheduler-result speech. |
| `src/parrot/brain/session_policy.py` | C4 gating | Suppresses proactive replies in `SessionOnlySilent` and derives capability mode behavior. |
| `src/parrot/brain/tools/_state_context.py` | Tool-result state header | Adds body/head/cognitive/ECP state to selected tool results. |
| `src/parrot/brain/tools/dispatch_task.py` | Scheduler/Nanobot dispatch | Lets Parrot delegate background work. |
| `src/parrot/scheduler/service.py` | Nanobot dispatch and C4 result path | Routes background tasks and forwards summaries to Brain. |
| `src/parrot/scheduler/task_catalog.py` | Task catalog | Defines supported background task types. |

## DSG / L1.5 / Intent Sources

| Path | Status | Notes |
| --- | --- | --- |
| `src/parrot/dsg/triggers/base.py` | Runtime schema | Defines `TriggerOutcome`; `notify_gemini` maps to C3 by default. |
| `src/parrot/dsg/triggers/runner.py` | Runtime runner | Applies L1.5 operations, dispatches Nanobot, emits C3 notices. |
| `src/parrot/dsg/triggers/scene_context_trigger.py` | Runtime trigger | Scene memory recall to C3. |
| `src/parrot/dsg/triggers/scene_switch_trigger.py` | Runtime trigger | Scene switch archive/notice. |
| `src/parrot/dsg/triggers/roleplay_mode_trigger.py` | Runtime trigger | Roleplay bucket open/close and notes import. |
| `src/parrot/dsg/triggers/message_trigger.py` | Runtime trigger | Message task dispatch/results, observation commits, C3 notices. |
| `src/parrot/dsg/triggers/calendar_trigger.py` | Runtime trigger | Calendar task dispatch/results, observation commits, C3 notices. |
| `src/parrot/dsg/triggers/goslo_curiosity_trigger.py` | Runtime trigger | Curiosity observations/staged refs/plans; no C3 by default. |
| `src/parrot/dsg/triggers/idle_archive_trigger.py` | Runtime trigger | Archive request path. |
| `src/parrot/dsg/triggers/obsidian_ingest_trigger.py` | Runtime trigger | Imports session-context/Obsidian notes into L1.5. |
| `src/parrot/brain/intent_workspace.py` | Runtime staging | Staged refs and intent workspaces; not direct prompt injection. |

## Nanobot Runtime And Config

| Path | Status | Notes |
| --- | --- | --- |
| `src/scripts/start_nanobot_worker.py` | Runtime launcher | Creates `~/.nanobot-parrot/config.json` from external template and starts gateway. |
| `src/parrot/bus/nanobot_consumer.py` | Stub worker | Local Redis stream stub; no LLM persona. |
| `D:/GOSLOParrot/nanobot/config/parrot_config.json` | External template | Template copied by launcher; contains Maid `systemPrompt` field. |
| `C:/Users/Bin/.nanobot-parrot/config.json` | Actual local config | Current generated config; differs from template. |
| `D:/GOSLOParrot/nanobot/nanobot/agent/context.py` | Upstream Nanobot prompt builder | Builds system prompt from bootstrap files and memory; inspected code does not read `systemPrompt`. |
| `D:/GOSLOParrot/nanobot/nanobot/agent/memory.py` | Upstream Nanobot memory | Reads `SOUL.md`, `USER.md`, `memory/MEMORY.md`, history. |
| `D:/GOSLOParrot/nanobot/nanobot/config/schema.py` | Upstream schema | Inspected `AgentDefaults` does not include `systemPrompt`. |
| `D:/GOSLOParrot/nanobot/nanobot/heartbeat/service.py` | Upstream heartbeat | Uses `HEARTBEAT.md` and a heartbeat-specific prompt. |
| `C:/Users/Bin/.nanobot/workspace/AGENTS.md` | Active bootstrap file | Task and reminder guidance. |
| `C:/Users/Bin/.nanobot/workspace/SOUL.md` | Active bootstrap file | Observed Nanobot maid persona source. |
| `C:/Users/Bin/.nanobot/workspace/USER.md` | Active bootstrap file | User/language/project preferences. |
| `C:/Users/Bin/.nanobot/workspace/TOOLS.md` | Active bootstrap file | Tool-use guidance. |
| `C:/Users/Bin/.nanobot/workspace/HEARTBEAT.md` | Active heartbeat file | Recurring/proactive worker guidance. |
| `C:/Users/Bin/.nanobot/workspace/memory/MEMORY.md` | Active long-term memory | Long-term memory block. |
| `D:/GOSLOParrot/nanobot/nanobot/templates/*.md` | Templates | Used only when initializing/copying a workspace. |

## Task Guidance / Chat Guidance

| Path | Status | Notes |
| --- | --- | --- |
| `.cursor/rules/workspace.mdc` | Cursor/Codex task guidance | Global route index and project rules; not Parrot runtime. |
| `.cursor/rules/ar-foundation.mdc` | Cursor/Codex task guidance | AR Foundation guidance. |
| `.cursor/rules/bus-audit-constraints.mdc` | Cursor/Codex task guidance | Bus audit constraints. |
| `.cursor/rules/deploy-prep-routing.mdc` | Cursor/Codex task guidance | Deploy routing guidance. |
| `.cursor/rules/docker-best-practices.mdc` | Cursor/Codex task guidance | Docker guidance. |
| `.cursor/rules/livekit-unity-sdk.mdc` | Cursor/Codex task guidance | LiveKit Unity guidance. |
| `codex_workspace/workflows.md` | Codex workflow | Development workflow and launch-prompt policy. |
| `codex_workspace/design_workspace/tasks/ACTIVE_CONTEXT.md` | Active task board | Current app/web state; influences development chats. |
| `codex_workspace/design_workspace/tasks/APP_WEB_PARALLEL_TODOLIST_20260513.md` | Active task board | App/web task board. |
| `codex_workspace/design_workspace/tasks/APP_WEB_CHAT_START_PROMPTS_20260513.md` | Chat start prompts | Task-specific chat kickoff prompts. |
| `.cursor/skills/nanobot/SKILL.md` | Skill/reference | Nanobot worker-pattern guidance. |
| `.cursor/skills/nanobot-overview/SKILL.md` | Skill/reference | Upstream Nanobot context-stack reference. |
| `.cursor/skills/**/references/**/C3*` | Reference docs | Historical C3.x analysis docs; not runtime C3 channel. |

## Deploy Mirrors And Secret-Bearing Files

| Path | Status | Handling |
| --- | --- | --- |
| `.cursor/config/nanobot-goslo_config.deploymirror.json` | Deploy mirror | Safe to compare structure; confirm runtime before editing. |
| `.cursor/config/nanobot-parrot_config.deploymirror.json` | Deploy mirror | Contains Maid prompt mirror; confirm runtime before editing. |
| `.cursor/config/nanobot-weixin-account.deploymirror.json` | Secret-bearing mirror | Do not quote values in docs or chat. |
| `.cursor/config/parrot-castle-config.deploymirror` | Secret-bearing env mirror | Do not quote values in docs or chat. |
| `.env*` files, if present | Secret-bearing env | Index only; do not copy values. |

## Excluded From Persona Index By Default

| Pattern | Reason |
| --- | --- |
| `node_modules/**`, `web/**/dist/**` | Generated dependency/build output. |
| `Unity/Temp/**`, `Library/**`, generated XR files | Generated Unity state. |
| `docs/sprint_archive/**` | Historical source anchors unless a task explicitly needs them. |
| test output, logs, media captures | Evidence artifacts; not instruction sources unless linked by a current profile. |
