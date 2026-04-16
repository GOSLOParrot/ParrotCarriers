# Skill Seeker distillation focus (injected for Gemini enhance)

> **Repo:** GetStream/Vision-Agents | **Pin:** v0.3.8

Prioritize accurate coverage of these English symbols and API names when rewriting SKILL.md:

## Core Agent
- `Agent` (main class)
- `Edge` (Stream edge network connector)
- `agent_user`
- `instructions` (system prompt)
- `function_tool` (tool calling decorator)
- `call` / `join_call`
- `on_agent_state_changed`
- `AgentState`

## Processor Pattern (KEY LEARNING POINT)
- `VideoProcessor` (base class for video analysis)
- `AudioProcessor` (base class for audio analysis)
- `process_video(track, participant_id, shared_forwarder)`
- `process_audio(track, participant_id)`
- `attach_agent(agent)` — state injection mechanism
- `add_frame_handler(handler, fps, name)` — frame rate control
- `shared_forwarder` — shared video forwarder across processors

## Built-in Processors / Plugins
- `ultralytics.YOLOProcessor`
- `ultralytics.YOLOPoseProcessor`
- `roboflow.RoboflowProcessor`
- `moondream.MoondreamProcessor`

## LLM Integration (Realtime)
- `gemini.Realtime(fps=N)` — Gemini native video input
- `openai.Realtime(fps=N)` — OpenAI native video input
- Context injection via Processor → Agent event system

## Conversation & Memory
- `ConversationMessage`
- `conversation` module
- In-memory and persistent conversation storage

## Production
- `metrics` / `prometheus` — observability
- HTTP server mode (`agent_server_example`)
- Docker deployment with GPU

## What to focus on for ParrotCarriers:
1. **Processor pattern** — this is the core learning: how to build VideoProcessor subclass, receive frames at controlled fps, analyze, and inject results into LLM context
2. **`attach_agent` mechanism** — how processor results flow into the Agent's next turn
3. **`add_frame_handler` fps control** — critical for mobile AR where we can't process every frame
4. **Gemini Realtime integration** — we use Gemini as our LLM, so `gemini.Realtime` pattern matters
5. We do NOT use Stream Edge — we use LiveKit. But the Processor abstraction is what we're borrowing for our DSG pipeline
6. Examples 02 (golf_coach) and 05 (security_camera) are most relevant
