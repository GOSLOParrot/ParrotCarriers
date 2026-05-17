# Information Access And Escalation Model

Updated: 2026-05-17

Status: proposal only. This records the rule the user emphasized: dialogue quality depends less on "having all information" and more on understanding what each piece of information is, where it came from, and whether it is allowed to reach the model or speech.

## Primary External Basis

Gemini Live best practices are treated as a major basis:

- keep system instructions explicit and stable.
- define tool-use conditions clearly.
- use dynamic instructions intentionally, not as a dumping ground.
- keep long-running sessions from accumulating noisy context.
- keep each agent's persona distinct.

For GOSLO this means: stable persona and room rules go to P0/C2; transient state goes to C3 or IntentWorkspace; background worker outputs are data, not style; C4 is scarce and gated.

## First Question For Every Information Item

Before any information is injected, ask:

1. What is it? Identity rule, room context, UI capability, sensor state, visual evidence, user intent, task result, memory seed, reference doc, or audit note.
2. Who owns it? PersonaLoader, RoomProfile, menu, ModelManifest, App facade, Blackboard writer, IntentWorkspace, TriggerRunner, Scheduler, Nanobot, SVA, or human reference doc.
3. How fresh is it? Boot-stable, hot-swapped, per-event, transient, expiring preview, or historical.
4. How authoritative is it? Identity, instruction, context, data, hypothesis, worker output, or reference.
5. Who may see it? LLM prompt, natural-turn C3, immediate C4, IntentWorkspace only, UI only, or human/dev only.
6. Can it cause speech? Never, natural turn only, placement-gated, user-requested, safety-only.
7. Can it change style? Active persona only, quoted data only, or source style allowed.

## Information Envelope

Future import packages, triggers, task results, and SVA processors should be able to express this envelope:

```json
{
  "source": "photo_awareness.preview",
  "kind": "photo_preview",
  "owner": "brain.photo_awareness",
  "authority": "data",
  "freshness": "transient",
  "runtime_target": ["intent_workspace", "c3"],
  "forbidden_targets": ["p0", "c2", "c4"],
  "speech_policy": "natural_turn_only",
  "style_policy": "quoted_data_only",
  "capability_gate": ["photo_awareness_enabled"],
  "event_layer": "intent",
  "ref_id": "iw_...",
  "summary": "Photo preview is staged in IntentWorkspace."
}
```

The model should usually see only `summary` and `ref_id`, not the full payload.

## Escalation Ladder

| Level | Channel | What belongs here | What does not belong here |
| --- | --- | --- | --- |
| Hidden raw state | Blackboard / local state | Current mode, video tier, body state, capability flags | Persona text, worker style, large evidence |
| Working set | IntentWorkspace | Photos, evidence, task reports, plans, rich refs | Immediate speech instructions |
| L1.5 | DSG buckets / memory seed | Roleplay seeds, scene memory, observations | Full audit reports, UI checklists |
| T1 | Tool result state header | Local state attached to a tool result | Global persona updates |
| C3 | Chat-context notice | Small state/event fact for next natural turn | Large payloads, "speak now" commands |
| C4 | `generate_reply` | Placement greeting, critical report, user-requested result digest | Raw Nanobot text, untrusted style, pre-placement chatter |
| C2 | `update_instructions` | Persona/mode/room/scene rebuilds | Frequent transient events |
| P0 | Boot instructions | Stable identity and core tool policy | Runtime sensor data or reports |

## Reflex / Intent / Task

| Layer | Definition | Information access rule |
| --- | --- | --- |
| Reflex | Direct, high-priority action path. Reserved model capabilities can activate reflex behavior. | Needs capability ids and current state, not full persona context. Should bypass LLM where possible. |
| Intent | Self-committing state or internal decision. Producers often write Blackboard / IntentWorkspace before routing. | Can stage refs and send C3 hints. Should not speak unless a separate C4 policy approves. |
| Task | Background/external work, often Nanobot. | Full result stays as data/ref. Brain receives sanitized digest only. Worker persona never crosses into Parrot style. |

## Menu / Selection / Capability Gates

Information should only become usable when its gate is open.

| Gate | Example | Information rule |
| --- | --- | --- |
| Menu mode | BASE, COMPANION, BUTLER, RESEARCHER, PLAYFUL, ROLEPLAY, ON_HAND | Mode can change C2 persona sections and tool-use willingness, but does not automatically unlock every imported document. |
| RoomProfile | Ner room selects persona, line, scene, workspace, setting refs | Room can select context, but import package target decides which parts rise. |
| ModelManifest | Active model declares capabilities | Tools such as `fly_to`, `perch_to_finger`, `animate`, `play_capability` must follow declared capabilities. |
| App capability mode | SessionOnlySilent / VoiceOnly / VoiceVideo / FullAR | Proactive speech and media behavior follow session policy. |
| Photo awareness | UNAWARE_RECORDED / AWARE_SILENT / AWARE_REACT | Photo previews go to IntentWorkspace; C3 only when policy allows; no interrupt. |
| Video tier / DSG mode | VIDEO_OFF / VIDEO_FULL, DSG_TEXT_ONLY / DSG_FULL | Controls which visual/DSG sources are trustworthy and active. |
| Env rollout | identify_object env gate | Experimental abilities stay hidden until rollout gate opens. |

## IntentWorkspace Rule

IntentWorkspace is not a prompt. It is a working-set table. Use it for:

- large or rich payloads.
- uncertain visual evidence.
- photo previews.
- Nanobot reports.
- plan drafts.
- worker artifacts.

Surface to Gemini with:

- a short C3 notice when useful.
- a stable `ref_id`.
- a compact summary.
- an instruction to use it only when relevant.

Do not surface:

- raw image bytes/base64 unless a tool explicitly needs it.
- worker persona voice.
- long reports.
- stale refs.
- evidence that the current menu/capability gate says GOSLO should not know.

## Conversational Rule

GOSLO should not be made "omniscient" by stuffing every available state into the conversation. It should know only the slice that is:

- relevant to this turn or current mode.
- allowed by menu/session capability.
- summarized at the right abstraction level.
- framed as data unless it is truly an identity rule.

This is the difference between a companion with good situational awareness and a model reading a pile of internal logs aloud.
