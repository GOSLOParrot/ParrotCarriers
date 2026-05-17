# Import Files Reanalysis

Updated: 2026-05-17

Scope: RoomProfile `setting_file_refs`, especially `data/presets/ner_lineb_room.json`.

## Sources Recorded

Local source files checked:

- `data/presets/ner_lineb_room.json`
- `src/parrot/brain/session_context_pack.py`
- `src/parrot/brain/soul.py`
- `tests/test_brain/test_session_context_pack.py`
- `src/parrot/brain/personas/ner_companion.md`
- `codex_workspace/design_workspace/unity_ar_app/ner_roleplay_setting_obsidian_v0_20260511.md`
- `codex_workspace/design_workspace/unity_ar_app/ner_mochi_scene_v0_20260511.md`
- `.cursor/memory/architecture/Interface/app_v1_lineb_ner_realdevice_config_report_20260511.md`

External guidance is recorded in `external_best_practices.md`. The relevant implication is: keep stable persona in P0/C2, use C3 for state data, use C4 rarely, and keep each agent's identity separate. Do not let Nanobot / worker / reference docs become Parrot style instructions.

## Current Runtime Resolution

`ner_lineb_room.json` currently has four `setting_file_refs`.

| Ref | Runtime target | Goes to LLM prompt? | Goes to L1.5? | Size observed | Current assessment |
| --- | --- | ---: | ---: | ---: | --- |
| `src/parrot/brain/personas/ner_companion.md` | `persona_loader_only` | No | No | 136 lines / 5375 chars | Safe at runtime because `session_context_pack.py` detects `personas`, but confusing because persona files should not live in `setting_file_refs`. |
| `ner_roleplay_setting_obsidian_v0_20260511.md` | `llm+l1_5` | Yes | Yes | 73 lines / 3515 chars; excerpt 2198 chars | Main roleplay setting source. Useful, but too much meta/test/source-boundary language enters the prompt. |
| `ner_mochi_scene_v0_20260511.md` | `llm` | Yes | No | 66 lines / 2140 chars; excerpt 2139 chars | Scene draft enters prompt almost in full. Contains validation/checklist wording that is not clean runtime scene context. |
| `.cursor/...app_v1_lineb_ner_realdevice_config_report_20260511.md` | `reference_only` | No | No | 594 lines / 26179 chars | Safe from prompt pollution today. Better as `audit_refs` metadata rather than `setting_file_refs`. |

Observed bundle for `ner_lineb_room`:

- `llm_source_count = 2`
- `l15_payload_count = 1`
- prompt block length about `4949` chars
- LLM sources are roleplay setting and scene draft only

## Problems

### 1. `setting_file_refs` Mix Different Kinds Of Things

The field currently contains:

- persona path
- runtime roleplay setting
- scene/config draft
- architecture audit report

The code separates them today, but the data model reads like "all of these are setting imports." That makes future tuning risky: a human may assume the persona ref is injected twice, or move a file so the path heuristic stops protecting it.

Recommendation: split the list into explicit fields:

- `persona_id` only for persona
- `runtime_setting_refs` for LLM/L1.5 sources
- `scene_context_refs` for scene facts
- `audit_refs` or `reference_refs` for reports

Short-term: remove `src/parrot/brain/personas/ner_companion.md` from `setting_file_refs`, or add explicit frontmatter `prompt_target: persona_loader_only` and document why it remains listed.

### 2. Default `.md -> llm` Is Too Broad

`session_context_pack.py` currently defaults any ordinary markdown file to `llm` unless it is under `.cursor`, under `personas`, or has explicit frontmatter. That made `ner_mochi_scene_v0_20260511.md` enter the prompt without explicit consent.

This is convenient for prototypes but risky for persona tuning. A draft, checklist, smoke-test note, or implementation TODO can become model instructions.

Recommendation: require explicit frontmatter for runtime prompt import, such as:

```yaml
prompt_target: llm
runtime_context: true
```

Then make unmarked markdown `reference_only` by default, or at least warn loudly.

### 3. Roleplay Setting Carries Meta / Audit Language Into Runtime

`ner_roleplay_setting_obsidian_v0_20260511.md` is correctly classified as `llm+l1_5`, but its first 2200 chars include:

- explanation that it is an Obsidian setting source
- source-boundary discussion
- public/community reference caveats
- voice actor / CV metadata rules
- test adaptation wording

Those are useful for developers, but they are not all good as first-order live persona context. They can make the character sound like a validation harness instead of a companion.

Recommendation: split the file into sections and only import a marked runtime section, for example:

- `## Runtime LLM Context`
- `## L1.5 Memory Seed`
- `## Audit / Source Boundary`

Only the first two should flow into prompt / L1.5.

### 4. Scene File Is A Draft, Not A Clean Scene Context

`ner_mochi_scene_v0_20260511.md` currently enters LLM prompt almost fully. It includes "Status: config draft", validation goals, `ParrotSmokeScene`, future implementation notes, joystick/controller gaps, and readiness requirements.

This is good engineering context, but weak live-scene context. It can bias GOSLO to talk about validation instead of behaving naturally in the selected room.

Recommendation: add frontmatter and rewrite/split:

```yaml
prompt_target: llm
kind: scene_context
title: Ner Mochi Scene Runtime Context
```

Runtime content should be only: scene identity, placement rule, available capabilities, unavailable capabilities, and user-facing degradation language. Move validation checklist to `reference_only`.

### 5. Reference Report Is Safe But In The Wrong Container

`.cursor/...app_v1_lineb_ner_realdevice_config_report_20260511.md` is `reference_only`, so it does not pollute the prompt. However, it is still loaded and summarized as a `SessionContextSource` during resolution.

Recommendation: keep `.cursor` reports out of `setting_file_refs` unless the UI explicitly needs them in the bundle. Store them under RoomProfile metadata like:

```json
"audit_refs": [
  ".cursor/memory/architecture/Interface/app_v1_lineb_ner_realdevice_config_report_20260511.md"
]
```

### 6. The Import Path Boundary Is Still Trust-Based

`_resolve_ref` accepts repo-relative paths, absolute paths, and path traversal if supplied by a trusted RoomProfile. Current built-in files are trusted, but future user-edited RoomProfiles should not be able to import arbitrary local files.

Recommendation: before user-editable imports, add an allowlist rooted in:

- `codex_workspace/design_workspace/unity_ar_app/`
- `src/parrot/brain/personas/` only for `persona_loader_only`
- dedicated `data/room_context/`

### 7. Tests Cover Classification, Not Prompt Quality

Current tests correctly assert:

- roleplay ref -> `llm+l1_5`
- scene ref -> `llm`
- persona ref -> `persona_loader_only`
- report ref -> `reference_only`
- report text not in prompt

Missing tests:

- no `config draft`, `validation`, `ParrotSmokeScene`, or audit-report wording in live prompt
- no persona path in `setting_file_refs` unless explicitly `persona_loader_only`
- no pre-placement greeting instruction in import docs unless paired with runtime gate
- no worker/Nanobot role or voice style entering Parrot C4 prompt

## Recommended Clean Import Contract

For persona tuning, use this contract:

| Content kind | Where it belongs | Runtime target |
| --- | --- | --- |
| Core identity / voice / tool policy | `src/parrot/brain/personas/*.md` | P0/C2 only |
| Room/world scene facts | dedicated runtime scene note | `llm` |
| Roleplay memory seed | dedicated roleplay note with runtime section | `llm+l1_5` |
| Implementation checklist | `.cursor` or task docs | `reference_only` |
| Validation report | `audit_refs`, not setting import | `reference_only` |
| Nanobot worker identity | Nanobot repo/workspace only | never Parrot prompt |

## Immediate Cleanup Candidates

1. Remove `src/parrot/brain/personas/ner_companion.md` from `ner_lineb_room.json` `setting_file_refs`.
2. Add explicit frontmatter to `ner_mochi_scene_v0_20260511.md`.
3. Split `ner_mochi_scene_v0_20260511.md` into runtime scene context and validation checklist.
4. Split `ner_roleplay_setting_obsidian_v0_20260511.md` into runtime/L1.5/audit sections or add section filtering in `session_context_pack.py`.
5. Move `.cursor/...config_report...md` from `setting_file_refs` to future `audit_refs`.
6. Add a "prompt cleanliness" test for live room imports.
