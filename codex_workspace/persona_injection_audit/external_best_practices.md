# External Best Practices For Live Persona Injection

Updated: 2026-05-17

Sources checked:

- Google Gemini Live API overview: https://ai.google.dev/gemini-api/docs/live-api
- Gemini Live API best practices: https://ai.google.dev/gemini-api/docs/live-api/best-practices
- Gemini Live API session management: https://ai.google.dev/gemini-api/docs/live-api/session-management
- Gemini API system instructions: https://ai.google.dev/gemini-api/docs/system-instructions
- Vertex Gemini Live session management: https://docs.cloud.google.com/vertex-ai/generative-ai/docs/live-api/start-manage-session
- LiveKit Agents API docs: https://docs.livekit.io/reference/python/livekit/agents/index.html
- LiveKit Agents speech docs: https://docs.livekit.io/agents/multimodality/audio/
- Vision Agents Agent docs: https://visionagents.ai/core/agent-core
- Vision Agents Processor docs: https://visionagents.ai/core/processors-core

## Guidance Relevant To GOSLO

Gemini Live best practices are a primary design basis for this audit. They are the external reason to keep system instructions stable and explicit, keep per-event context small, define tool-use conditions clearly, and avoid letting unrelated agent/persona text leak into the active Live session.

| Area | External guidance | GOSLO interpretation |
| --- | --- | --- |
| Stable identity | Gemini recommends clear system instructions with persona, conversational rules, tool flow, then guardrails. It also recommends a distinct SI for each agent. | Keep Parrot/GOSLO identity in P0/C2. Keep Nanobot identity separate. Do not merge worker persona into Parrot prompt. |
| Live session startup | Gemini Live expects user input before it responds; to make it initiate, explicitly prompt it to greet or begin. | LiveKit connect should not count as the social start. Use `onGosloPlaced` as the explicit begin prompt. |
| Tool guidance | Gemini recommends precise tool definitions and explicit invocation conditions. | Put "when to dispatch Nanobot" in tool descriptions and persona tool policy, not in ad hoc C4 task prose. |
| Dynamic instructions | LiveKit `Agent.update_instructions(...)` updates the realtime session instructions. | C2 is valid for persona/mode/room rebuilds, but should be less frequent than C3 notices. |
| Per-reply instructions | LiveKit says `generate_reply(instructions=...)` is extra instruction for that reply; for Gemini, those instructions are added to chat context and may influence future turns. | C4 should be scarce and sanitized. Do not pass raw Nanobot/Maid-styled result text as instruction language. |
| Chat context notices | LiveKit supports updating chat context for active realtime sessions. | C3 is the right place for quiet state changes. Mark as status/data, not role or style. |
| Long sessions | Gemini Live recommends context window compression and session resumption for longer sessions. | Avoid repeatedly rebuilding huge context blocks; prefer stable P0/C2 plus small C3 deltas and L1.5 refs. |
| Video/SVA processors | Vision Agents separates Agent instructions from processors; processors attach to the agent and sample frames with declared FPS. | SVA findings should enter as structured evidence/status, not as free-form prompt paragraphs every frame. |
| Observability | Vision Agents has an event system and processor lifecycle hooks. | Track "why GOSLO spoke" by channel and event source: placement greeting, scheduler result, BB heavy change, legacy trigger. |

## Recommended Channel Policy

1. P0/C2: stable identity, language, role, safety, tool policy, room/scene setting.
2. C3: quiet facts and state deltas, always written as status/data. It should not ask GOSLO to speak immediately.
3. C4: only user-visible moments that must speak now: placement greeting, critical status, explicit user-requested background result. C4 must be placement-gated.
4. L1.5 / IntentWorkspace: large evidence, photos, reports, plans, and worker artifacts. Only surface summaries.
5. Nanobot output: data only. Parrot must never imitate Nanobot's worker voice, even if Nanobot uses a maid/catgirl persona internally.

## Best-Practice Translation For Information Access

Before any state, evidence, trigger result, task result, or imported note is shown to Gemini Live, classify it as:

- identity/instruction, context, state, evidence, worker result, UI capability, or reference.
- stable boot context, hot-swapped context, event notice, immediate speech, or hidden working-set data.
- active persona voice, quoted data, or reference-only source.

If an item is not meant to steer identity, it should not be in P0/C2. If an item is not meant to cause speech, it should not be C4. If an item is large or uncertain, put a ref in IntentWorkspace and surface only a small C3 hint when policy allows.

## Concrete Prompt Hygiene Rule

When converting worker/task output to Parrot speech, wrap the worker result as data:

`Background worker result data: ...`

Then add:

`Summarize this in the active GOSLO Parrot persona. Do not imitate the worker's wording, role, or style.`

This should replace the current raw C4 shape where `{summary}` is embedded directly inside the instruction sentence.
