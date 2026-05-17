# File-By-File Rewrite Tracker

Updated: 2026-05-17

Status: planning ledger only. Do not move files yet.

Goal: rewrite the small, stale persona/setting corpus one file at a time so each file has a clear owner, runtime target, speech policy, and gate contract before any package migration.

## Rewrite Rules

1. Keep one owner per file. Persona identity, room facts, roleplay seed, C4 speech event, Nanobot contract, and audit reference should not share the same document.
2. Do not let a markdown file enter the live LLM prompt just because it is markdown. Runtime prompt import should be explicit.
3. C4 means "speak now". Any greeting, task-result report, or visual recovery line needs placement/user/safety gates.
4. Nanobot output is data from another worker, not Parrot style. Parrot may summarize it, but must not inherit the worker's voice.
5. IntentWorkspace is a working set, not a speech channel. Only small summaries or refs should rise into C3/C4.
6. Capability claims must point to real gates: menu selection, model manifest, app capability mode, video tier, env rollout, and scene wiring.
7. Runtime files should avoid validation/checklist/source-boundary language unless the user is explicitly debugging that layer.

## Issue Groups To Carry Forward

| Group | Related issue ids | What it means for rewriting |
| --- | --- | --- |
| Startup speech boundary | PIA-001, PIA-003, PIA-004, PIA-006, PIA-013 | No setting file may imply connection-time greeting. First proactive greeting is after placement unless safety says otherwise. |
| Nanobot style boundary | PIA-002, PIA-007 | Parrot-side docs may define task/result contracts only. Nanobot persona belongs to the Nanobot workspace. |
| Import container cleanup | PIA-008, PIA-009, PIA-012, PIA-014 | Split mixed `setting_file_refs`; runtime prompt requires explicit target. |
| Prompt cleanliness | PIA-010, PIA-011, PIA-017 | Remove draft/test/checklist/source essays from live prompt sections. |
| Channel naming | PIA-005 | Say runtime C3/C4, not historical C3.x. |
| Capability gates | PIA-015 | Prompt text cannot create abilities; menu/model/scene gates own abilities. |
| State visibility | PIA-016 | Blackboard, IntentWorkspace, Task, SVA, and Nanobot each need source/authority/speech metadata. |

## Recommended Rewrite Order

| Order | File | Current role | Main problem | Rewrite target | Done when |
| ---: | --- | --- | --- | --- | --- |
| 1 | `src/parrot/brain/personas/goslo_parrot_default.md` | Default Parrot persona | Current default is stale, has mojibake, generic pet-parrot wording, weak estate role boundary, and no fixed-voice contract. | Rewrite as GOSLO: quiet tsundere parrot young lady of the shared mansion; user is owner/friend; Nanobot is maid but separate; state-aware without over-speaking. | Runtime persona expresses the new relationship and speech discipline without promising ungated abilities. |
| 2 | Parrot default voice policy, new doc or config issue | Not yet separated | Fixed female voice is a runtime voice-selection problem, not just persona text. | Define LineA/LineB voice source and diagnostics. | Startup can show active pipeline/provider/language/voice and catch fallback. |
| 3 | Parrot-side Nanobot result contract, new doc | Not yet separated | Task result C4 can carry worker voice into Parrot. | Define structured result fields, style quarantine, placement gate, and IntentWorkspace staging. | Scheduler result speech can only use a clean Parrot digest. |
| 4 | C4 speech-event policy/template, new doc | Not yet separated | Greetings, visual recovery, and task reports are scattered in code/docs. | Define event templates for placed greeting, task digest, and visual recovery. | Every C4 event declares speech policy and placement gate. |
| 5 | `codex_workspace/design_workspace/unity_ar_app/ner_roleplay_setting_obsidian_v0_20260511.md` | Roleplay setting, currently `llm+l1_5` | Runtime cues are mixed with source-boundary, CV, test adaptation, and implementation notes. | Split into runtime roleplay cues, L1.5 seed, and reference-only source boundary. | Live prompt has only character cues, speech style, and gated interaction rules. |
| 6 | `codex_workspace/design_workspace/unity_ar_app/ner_mochi_scene_v0_20260511.md` | Scene setting, currently `llm` | Config draft and validation checklist enter prompt almost whole. | Rewrite as clean runtime scene context; move validation/checklist to reference-only. | Live prompt can explain the room and placement boundary without mentioning smoke tests or implementation gaps. |
| 7 | `src/parrot/brain/personas/ner_companion.md` | Persona identity, P0/C2 | Persona includes too much device-validation and capability routing detail. | Keep voice, collaboration feel, safety tone, and high-level tool discipline; move device-specific details out. | Persona sounds natural and still respects placement, menu gates, and active persona-only style. |
| 8 | `data/presets/ner_lineb_room.json` | RoomProfile selector | `setting_file_refs` mixes persona, runtime docs, and reference report. | Keep selector facts; replace mixed refs later with explicit runtime/reference entries or package manifest. | Resolved bundle shows only intended runtime docs in LLM/L1.5. |
| 9 | Nanobot workspace files in `D:/GOSLOParrot/nanobot` / `C:/Users/Bin/.nanobot/workspace` | External Nanobot runtime | Active Nanobot persona/config is outside ParrotCarriers. | Review separately in Nanobot workspace; Parrot docs only point to contracts. | Nanobot reports are useful data and never style instructions for GOSLO. |

## Per-File Rewrite Template

Use this checklist when we edit a file:

| Field | Answer |
| --- | --- |
| File owner | Persona / room scene / roleplay seed / L1.5 / C3 / C4 / contract / reference |
| Runtime target | P0/C2 / LLM / L1.5 / IntentWorkspace / C3 / C4 / reference-only |
| Speech policy | Never speak / natural turn only / placement-gated C4 / safety-only |
| Style policy | Active persona only / quoted data only / source style allowed |
| Capability gate | Menu / model manifest / app capability mode / video tier / env rollout / scene wiring |
| Keep | Runtime facts or behavior that belongs here |
| Move out | Source notes, test checklists, implementation gaps, worker persona, stale docs |
| Test | Prompt cleanliness, placement gate, result-style quarantine, capability-gate behavior |

## Next Practical Step

Start with `src/parrot/brain/personas/goslo_parrot_default.md` because the user wants Parrot cleaned before Ner/Nanobot. Use `parrot_default_persona_rewrite_plan.md` as the requirement source.
