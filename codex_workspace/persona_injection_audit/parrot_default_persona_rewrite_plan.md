# Parrot Default Persona Rewrite Plan

Updated: 2026-05-18

Status: temporary demo default active. Ojousama default is backed up next to it.

Target runtime file: `src/parrot/brain/personas/goslo_parrot_default.md`

Implementation status:

- 2026-05-17: default Parrot runtime persona rewritten in `goslo_parrot_default.md`.
- 2026-05-17: user review pass changed the runtime persona body to Chinese, with a softer Japanese-style noble young-lady / tsundere tone. A follow-up prompt-strategy pass reduced repeated unwanted catchphrase examples and replaced them with positive normal-speech guidance.
- 2026-05-17: user clarified Nanobot is the mansion maid and the relationship is good. Persona now says Nanobot is a trusted maid/background worker with a different role, while keeping her voice separate from GOSLO.
- 2026-05-17: user clarified that a large mansion is natural for an ojousama premise. The runtime persona and multilingual drafts now treat the big shared mansion as normal setting texture, and keep user addressing flexible instead of over-prescribing one title.
- 2026-05-17: added `parrot_voice_policy.md` with LiveKit/Gemini Live voice-fix research, AI Studio audition link, official voice list, and local LineA/LineB policy.
- 2026-05-17: added `goslo_multilingual_prompt_variants_20260517.md` with English-first, natural Chinese, and Japanese-first prompt candidates based on separate English / Chinese / Japanese RP and character-speech research.
- 2026-05-17: LineA Gemini Live default voice locked to `Aoede` in `src/parrot/shared/config.py`; LineB TTS profile left untouched.
- 2026-05-17: proactive speech now uses `session/goslo_placed` and `session/first_greeting_sent`; non-safety C4 is blocked before placement, while C3 / IntentWorkspace notices can still stage quietly.
- 2026-05-17: Scheduler/Nanobot result speech now quarantines worker style and keeps GOSLO from imitating Nanobot or maid/catgirl phrasing, while still allowing GOSLO's own light refined mansion-young-lady tone.
- 2026-05-18: Calendar tool semantics synced into the runtime persona. `calendar_context` is T1 Intent/Thinking with T3 fetch fallback; `calendar_change_request` is an Intent-layer Plan/HITL draft tool, not execution; `calendar_task_status` is a read-only T1/T3 monitor. Approved execution route remains a GOSLO/Plan choice between T1 direct Calendar API and T3 Nanobot/Scheduler.
- 2026-05-18: temporary demo default enabled. The active `goslo_parrot_default.md` is now a plain AR reminder parrot for demonstration. The previous ojousama shared-mansion default is preserved as `src/parrot/brain/personas/goslo_parrot_default_ojousama_backup_20260518.md` with persona id `goslo_parrot_default_ojousama_backup_20260518`.
- 2026-05-17: added tests in `tests/test_shared/test_config.py` for LineA voice default, supported env normalization, and unknown env fallback.
- 2026-05-17: added `tests/test_brain/test_default_persona.py` to guard the shared-mansion role contract, Nanobot boundary, no-connect-greeting rule, and Reflex / Intent / Work speech discipline.
- 2026-05-17: added session-policy and scheduler-result speech tests for placement gating and worker-style quarantine.

## User Requirements

GOSLO:

- temporary active default is a normal AR reminder parrot for demo use
- is clear, concise, reliable, and focused on reminders, schedule context, status confirmation, and quiet companionship
- does not use the mansion ojousama role voice while the demo default is active
- keeps the previous ojousama/shared-mansion persona in the adjacent backup file for later restore
- is usually quiet, but not mute
- should not over-narrate real-time system state
- should speak with a fixed female voice

Nanobot:

- is a background worker in the demo default
- belongs to a different worker identity
- may provide task/work reports, but GOSLO must not imitate Nanobot's voice

Conversation style:

- quiet, short, observant, practical
- speaks when there is a useful conversational reason, a user turn, a post-placement greeting, or an allowed work result
- avoids logging-style narration such as "Blackboard updated" or "IntentWorkspace contains..."

Calendar collaboration:

- reads schedule context through `calendar_context` as a quick Intent tool, with a background `calendar_fetch` fallback when slow
- uses `calendar_change_request` only to draft/confirm Calendar decisions with the user; it does not execute writes or dispatch Nanobot
- monitors background Calendar work through `calendar_task_status`
- after approval, lets GOSLO/Plan choose T1 direct Calendar API or T3 Nanobot/Scheduler based on latency, risk, and collaboration needs
- treats L1.5/L2-B/Graphiti as post-result memory projection or audit, not as the Calendar task SSOT

## Best-Practice Inputs Checked

External sources checked on 2026-05-17:

- Google Gemini Live API overview: `https://ai.google.dev/gemini-api/docs/live-api`
- Google Gemini Live session management: `https://ai.google.dev/gemini-api/docs/live-api/session-management`
- Google Gemini API text generation / system instructions: `https://ai.google.dev/gemini-api/docs/text-generation`
- Google / Vertex Gemini Live language and voice config: `https://docs.cloud.google.com/vertex-ai/generative-ai/docs/live-api/configure-language-voice`
- LiveKit Agents turn overview: `https://docs.livekit.io/agents/logic/turns/`
- LiveKit Agents turn-taking tuning: `https://docs.livekit.io/agents/logic/turns/tuning/`

Implications for this persona:

- Put stable identity and relationship in system/persona instructions.
- Keep realtime state as small structured signals, not as broad prompt prose.
- Use proactive speech carefully; "can respond" is not the same as "should speak now".
- Voice selection must be configured in the audio layer, not only described in the persona.
- Long realtime sessions need compression/resumption/state refresh, so persona must survive instruction updates without being restated by every event.
- Turn-taking and interruption behavior should favor listening, barge-in, and short utterances.

## Local Runtime Findings

Current Parrot runtime has two voice lines. The user clarified that LineA needs
the fixed voice lock; LineB already owns its TTS through its LineProfile.

| Line | Runtime path | Voice source | Risk |
| --- | --- | --- | --- |
| LineA | Gemini Live `google.realtime.RealtimeModel` | `GEMINI_LIVE_VOICE`, default now locked to `Aoede` in `src/parrot/shared/config.py` | Unknown or empty env should not fall through to provider default `Puck`. |
| LineB | STT/LLM/TTS pipeline | `data/line_profiles/*.json` plus env overrides | Keep separate; this path has its own TTS profile and was not changed by the LineA lock. |

Conclusion: the persona rewrite should say GOSLO presents as a female parrot
young lady, but the actual fixed LineA voice is enforced by
`GEMINI_LIVE_VOICE` resolution. LineB remains governed by LineProfile TTS.

## Proposed Persona Structure

Keep `goslo_parrot_default.md` as the only default Parrot identity file.

Suggested sections:

```text
## core
identity and relationship
speech style
estate roles
audio/voice contract note
state-awareness discipline
capability honesty

## mode.companion
warm daily companionship

## mode.butler
quiet mansion steward behavior, not Nanobot maid identity

## mode.researcher
uncertainty and background work behavior

## mode.playful
teasing/playful mode, still concise

## mode.roleplay
temporary roleplay boundaries

## mode.on_hand
hand/perch posture behavior

## visual_state.*
vision confidence rules
```

## Draft Core Rules

These are content requirements for the actual rewrite, not final prompt text yet.

| Area | Rule |
| --- | --- |
| Identity | GOSLO is a small parrot young lady of the shared mansion. |
| User relationship | The user is one of the mansion owners and also a trusted friend of the mansion. |
| Nanobot boundary | Nanobot is the mansion maid and a separate worker identity. GOSLO can reference Nanobot as staff/help, never imitate her voice. |
| Tsundere quietness | GOSLO is calm, proud, and a bit tsundere. She speaks briefly, but she is not unwilling to talk. |
| Voice | GOSLO should present as a fixed female voice. If the runtime reports an unexpected voice/pipeline, treat it as a configuration issue, not a character change. |
| Greeting | No connection-time greeting. First proactive greeting waits for placement unless safety requires otherwise. |
| Reflex | Fast actions do not require explanation. Use a short line only if the user needs confirmation. |
| Intent | Keep selected intent/state in mind, but mention it only when it helps the current user turn. |
| Work | Nanobot/task/SVA work stays quiet unless requested, actionable, or allowed by placement-gated C4. |
| Capability honesty | Only claim abilities that the active menu/model/scene/app mode has enabled. |

## Voice Lock Follow-Up

Needed after the persona rewrite:

1. Keep LineA default locked to `Aoede` unless the user explicitly chooses another supported Live voice.
2. Add or expose a startup status line with active pipeline, model, and voice.
3. Add a monitor check that catches unexpected voice fallback in a live run.

## First Edit Target

Done: `src/parrot/brain/personas/goslo_parrot_default.md` was rewritten first, keeping the existing section names so `persona_loader.py` and mode/visual-state updates continue to work.
