# Import Package Refactor Proposal

Updated: 2026-05-17

Status: proposal only. Do not move files yet.

Goal: make future RoomProfile import packages self-describing so runtime prompt, L1.5 memory seed, C3 state notice, C4 speech, SVA evidence, Nanobot result contracts, and reference/audit material cannot be confused.

## Design Principles

1. Path and manifest must agree. A file should not enter LLM prompt just because it is a `.md`.
2. Persona identity stays in persona files. Room packages may point to `persona_id`, but should not duplicate persona markdown.
3. Runtime context and reference docs are separate. Drafts, reports, checklists, and source notes are not prompt material by default.
4. C4 is a speech event, not a generic import. It must carry gates such as placement, user request, safety, and style quarantine.
5. Nanobot identity stays in the Nanobot repo/workspace. Parrot packages may contain only task contracts and result sanitization rules.
6. SVA / vision evidence should enter as structured observations or C3 facts, not free-form per-frame prompt prose.
7. Large artifacts go through L1.5 / IntentWorkspace / references, with small summaries surfaced to the model.
8. Menu and selection state decide which capabilities are visible. An import package should describe capability requirements, but the runtime should register or expose them only when the active menu/model/scene/capability gates allow it.
9. Reflex / Intent / Task are different escalation classes. Import packages should never blur a direct reflex action, a self-committing intent state change, and a background task/report.

## Classification Axes

Every import entry should be classified on these axes:

| Axis | Values | Purpose |
| --- | --- | --- |
| `content_kind` | `persona_pointer`, `room_runtime`, `scene_runtime`, `roleplay_runtime`, `l15_seed`, `tool_policy`, `c3_notice`, `c4_speech_event`, `sva_evidence_contract`, `nanobot_task_contract`, `audit_reference`, `source_reference` | What the file is. |
| `runtime_target` | `none`, `llm`, `l1_5`, `intent_workspace`, `c3`, `c4`, `reference_only` | Where it is allowed to go. |
| `load_phase` | `boot`, `hot_reload`, `event`, `manual`, `never_runtime` | When it may load. |
| `authority` | `identity`, `context`, `data`, `contract`, `reference` | How strongly it can steer behavior. |
| `speech_policy` | `never_speak`, `natural_turn_only`, `speak_now_allowed`, `placement_gated`, `safety_only` | Whether it may cause speech. |
| `style_policy` | `active_persona_only`, `quoted_data_only`, `source_style_allowed` | Whether source wording can affect tone. |
| `capability_gate` | `always`, `menu_enabled`, `model_declared`, `room_profile_enabled`, `app_capability_mode`, `video_tier`, `dsg_mode` | Which selected capability must be on before this import/action can matter. |
| `event_layer` | `reflex`, `intent`, `task`, `conversation`, `reference` | Which escalation layer this belongs to. |

## Proposed Directory Shape

Preferred future root:

```text
data/import_packages/
  ner_lineb_room/
    package.json
    README.md
    llm/
      00_room_runtime.md
      10_scene_runtime.md
      20_roleplay_runtime.md
      30_tool_policy.md
    l15/
      roleplay_seed.md
      daily_seed.md
    c3/
      notices/
        visual_state_notice.md
        lineb_audio_notice.md
    c4/
      speech_events/
        on_placed_greeting.md
        task_result_digest.md
        visual_recovery.md
    contracts/
      nanobot_result_contract.md
      sva_evidence_contract.md
      information_envelope_contract.md
      tool_result_state_header.md
    references/
      audit/
        app_v1_lineb_ner_realdevice_config_report_20260511.md
      source_boundary/
        voice_and_canon_boundary.md
      validation/
        ner_lineb_device_validation_checklist.md
    assets/
      README.md
```

Alternative authoring root if we want to keep draft material out of `data/` until published:

```text
codex_workspace/persona_import_packages/
  ner_lineb_room/
    ...same package shape...
```

In that model, `codex_workspace/persona_import_packages/` is the authoring area, and `data/import_packages/` is the published runtime bundle.

## Manifest Sketch

```json
{
  "schema_version": 1,
  "package_id": "ner_lineb_room",
  "display_name": "Ner LineB Runtime Package",
  "persona_id": "ner_companion",
  "room_profile_id": "ner_lineb_room",
  "line_profile_id": "lineb_ner_ja_test",
  "imports": [
    {
      "path": "llm/10_scene_runtime.md",
      "content_kind": "scene_runtime",
      "runtime_target": "llm",
      "load_phase": "boot",
      "authority": "context",
      "max_chars": 1200,
      "sections": ["Runtime Scene Context"],
      "speech_policy": "natural_turn_only",
      "style_policy": "active_persona_only"
    },
    {
      "path": "l15/roleplay_seed.md",
      "content_kind": "l15_seed",
      "runtime_target": "l1_5",
      "load_phase": "boot",
      "authority": "data",
      "bucket": "obsidian_setting_roleplay",
      "max_chars": 4000,
      "style_policy": "quoted_data_only"
    },
    {
      "path": "c4/speech_events/task_result_digest.md",
      "content_kind": "c4_speech_event",
      "runtime_target": "c4",
      "load_phase": "event",
      "authority": "contract",
      "speech_policy": "placement_gated",
      "style_policy": "active_persona_only"
    },
    {
      "path": "references/audit/app_v1_lineb_ner_realdevice_config_report_20260511.md",
      "content_kind": "audit_reference",
      "runtime_target": "reference_only",
      "load_phase": "never_runtime",
      "authority": "reference"
    }
  ]
}
```

## How Current Ner Files Would Map Later

No move now. This is only the intended destination map.

| Current file | Future package location | Future target | Notes |
| --- | --- | --- | --- |
| `src/parrot/brain/personas/ner_companion.md` | stays in `src/parrot/brain/personas/` | P0/C2 via `persona_id` | Package manifest references `persona_id`, not the markdown path. |
| `ner_roleplay_setting_obsidian_v0_20260511.md` | `llm/20_roleplay_runtime.md` plus `l15/roleplay_seed.md` plus `references/source_boundary/voice_and_canon_boundary.md` | `llm`, `l1_5`, `reference_only` | Split runtime behavior from source/copyright/test caveats. |
| `ner_mochi_scene_v0_20260511.md` | `llm/10_scene_runtime.md` plus `references/validation/ner_lineb_device_validation_checklist.md` | `llm`, `reference_only` | Keep scene facts in prompt; move validation and implementation gaps out. |
| `.cursor/...app_v1_lineb_ner_realdevice_config_report_20260511.md` | `references/audit/...` | `reference_only` | Does not appear in runtime import list. |
| Nanobot worker persona/config | stays in `D:/GOSLOParrot/nanobot` and active Nanobot workspace | Nanobot only | Parrot package may include `contracts/nanobot_result_contract.md`, never Nanobot role voice. |
| SVA processor notes | `contracts/sva_evidence_contract.md` | contract / C3 / IntentWorkspace | Structured evidence contract, not free-form style prompt. |

## Runtime Channel Mapping

| Directory | Channel | Allowed effect |
| --- | --- | --- |
| `llm/` | P0/C2 appended room context | Stable context only; no "speak now". |
| `l15/` | L1.5 / DSG import | Memory/roleplay seed; surfaced later by refs or summaries. |
| `c3/` | C3 status notice templates | Quiet state facts for next natural turn. |
| `c4/` | C4 speech-event templates | Explicit speech only when manifest gates pass. |
| `contracts/` | Tool, SVA, Nanobot schemas | Data-shaping and sanitization rules; no persona voice. |
| `references/` | Human/dev docs | Never runtime prompt unless manually quoted by a tool/user. |
| `assets/` | Non-prompt assets | Referenced by UI or tooling only. |

## Capability And Menu Gate Contract

Future packages should not say "GOSLO can do X" by prompt text alone. They should say which gate owns X:

| Gate | Owner | Example |
| --- | --- | --- |
| Room/Profile selection | RoomProfile / menu | Ner room selects `persona_id=ner_companion`, `line_profile_id=lineb_ner_ja_test`. |
| Model capability | ModelManifest | `fly_to` only registers when active model declares `fly`; `animate` appears for parrot-reflex models; `play_capability` checks manifest support. |
| App capability mode | `session/app_capability_mode` | Silent / voice-only / voice+video / full AR gates speech, video, action monitor. |
| Photo awareness policy | App facade + BB | `UNAWARE_RECORDED`, `AWARE_SILENT`, `AWARE_REACT`; even react is C3/safe-turn, not interrupt. |
| Video / DSG mode | PerceptionSupervisor / ModeController | Which vision and ingest filters are active. |
| Env / rollout gate | deployment config | `identify_object` is still env-gated before unconditional registration. |

Package text can request or describe a capability, but runtime registration and execution must still consult the gate.

## Reflex / Intent / Task Mapping

| Layer | Meaning | Should receive imports? | Prompt exposure |
| --- | --- | --- | --- |
| Reflex | Fast direct action, highest priority, bypasses LLM when possible | Only contracts and capability ids | Usually none; may produce T1/tool state. |
| Intent | Self-committing state decision, often already written to Blackboard/IntentWorkspace before routing | State schemas, gates, small notices | C3 or hidden working-set; rarely C4. |
| Task | Background / external worker work, often Nanobot | Task contracts and result sanitizers | Result digest only; full worker output stays in IntentWorkspace/reference. |
| Conversation | Natural user/assistant turn | Persona + selected room context | P0/C2 plus relevant C3. |
| Reference | Human/audit/dev docs | References only | No prompt unless manually requested. |

## Suggested Future RoomProfile Shape

Instead of listing every markdown file in `setting_file_refs`, RoomProfile could eventually say:

```json
{
  "room_profile_id": "ner_lineb_room",
  "persona_id": "ner_companion",
  "import_package_id": "ner_lineb_room",
  "import_package_version": "2026-05-17"
}
```

During a transition period, `setting_file_refs` can stay, but package manifest should become the source of truth for classification.

## Prompt Cleanliness Rules

Runtime LLM files should avoid:

- `status: draft`
- validation checklist language
- implementation TODOs
- audit report summaries
- source/copyright essays except short behavioral constraints
- worker/Nanobot role language
- "say this now" instructions unless in `c4/`

Runtime LLM files should contain:

- user-visible scene facts
- available/unavailable capabilities
- concise behavior constraints
- placement/greeting boundary
- degraded-state wording
- language and length preferences that belong to the active persona context

## Minimal First Step Later

When we do decide to implement, the least risky first step is documentation-only plus tests:

1. Add `package.json` beside current docs without moving content.
2. Add explicit frontmatter to runtime-intended markdown.
3. Add tests that assert draft/audit words do not enter live prompt.
4. Only after that, move files into package directories.
