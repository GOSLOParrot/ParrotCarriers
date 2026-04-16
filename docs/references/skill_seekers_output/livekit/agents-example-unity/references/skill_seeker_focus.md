# Skill Seeker distillation focus (injected for Gemini enhance)

> **Repo:** livekit-examples/agents-example-unity | **Pin:** latest (2026-03-14)

Prioritize accurate coverage of these English symbols and API names when rewriting SKILL.md:

## Unity Project Structure
- `AgentsExample/` — Unity project root
- Scene setup and hierarchy
- `SandboxAuth` — token/auth configuration

## LiveKit Integration in Unity
- `Room` connection setup
- Token generation and sandbox mode
- Agent voice attachment to world object
- Transcription display

## Voice Agent Integration
- Audio source attachment to GameObject
- Agent voice playback in 3D space
- Transcription event handling

## Development Setup
- Unity Hub project import
- LiveKit SDK package resolution
- Visual Studio Code debugging configuration
- `SandboxAuth` configuration with `sandboxId`

## What to focus on for ParrotCarriers:
1. **How voice agent audio is attached to a world object** — we need this for the parrot GameObject
2. **Room connection pattern in Unity** — token handling, connection lifecycle
3. **Transcription integration** — how agent transcriptions are displayed
4. This is a small repo — distill the entire thing
5. Compare with `livekit-examples/unity-example` (more raw SDK example, 9 stars) for complementary patterns
