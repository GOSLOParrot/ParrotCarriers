# Parrot Voice Policy

Updated: 2026-05-17

Owner: Parrot runtime audio policy / LineA default voice.

Status: first policy draft. This document records the current source research
and the local runtime contract. It does not move configuration files.

## Goals

GOSLO should have a stable young-female-sounding LineA voice. Voice consistency
must be handled in audio/runtime configuration, not only in persona text.

The prompt should describe GOSLO's speaking style positively and briefly. Avoid
repeating unwanted catchphrases or bad examples in the runtime persona, because
style prompts work better when they point the model toward the desired wording
instead of putting unwanted wording in front of it.

## Source Research

Checked on 2026-05-17:

- Gemini Live API capabilities: https://ai.google.dev/gemini-api/docs/live-api/capabilities
- Gemini speech generation / TTS voices: https://ai.google.dev/gemini-api/docs/speech-generation
- Vertex / Gemini Live language and voice configuration: https://docs.cloud.google.com/vertex-ai/generative-ai/docs/live-api/configure-language-voice
- LiveKit Gemini Live API plugin: https://docs.livekit.io/agents/models/realtime/plugins/gemini/
- Anthropic prompting best practices: https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/claude-prompting-best-practices
- DigitalOcean prompt engineering best practices: https://www.digitalocean.com/resources/articles/prompt-engineering-best-practices

Implications:

- Gemini Live voice is configured through `speech_config.voice_config.prebuilt_voice_config.voice_name` when using the raw Gemini Live API.
- LiveKit's Google realtime plugin exposes the same choice as `google.realtime.RealtimeModel(voice="...")`.
- Google docs list 30 Gemini voice names and say all voice options can be heard in Google AI Studio.
- For persona prompts, use positive style guidance and examples. Keep hard boundaries short, and pair them with the intended replacement behavior.

## Where To Audition Voices

Primary place: Google AI Studio.

- Open https://aistudio.google.com/
- Use the Gemini speech / text-to-speech surface or voice picker.
- Official Gemini speech docs say all voice options can be heard in AI Studio.
- For Live-style testing, AI Studio Stream mode is also useful: https://aistudio.google.com/live

Suggested audition script for GOSLO:

```text
贵安。哼，既然你已经把我安置好了，我就暂时陪你一会儿吧。
Nanobot 把报告送来了，整理得还算像样。我给你说重点。
看起来像是那个东西，但我还不能完全确定。你再让我看清楚一点。
```

Pick a voice by listening for:

- soft / gentle enough for a quiet tsundere companion
- clear Mandarin/Japanese-adjacent pronunciation when reading Chinese
- not too mature, not too sharp, not too energetic
- stable timbre across several short lines

## Official Voice Names

Gemini Live native audio supports the Gemini TTS voice set. The current 30
official names and short descriptors are:

| Voice | Descriptor |
| --- | --- |
| Zephyr | Bright |
| Puck | Upbeat |
| Charon | Informative |
| Kore | Firm |
| Fenrir | Excitable |
| Leda | Youthful |
| Orus | Firm |
| Aoede | Breezy |
| Callirrhoe | Easy-going |
| Autonoe | Bright |
| Enceladus | Breathy |
| Iapetus | Clear |
| Umbriel | Easy-going |
| Algieba | Smooth |
| Despina | Smooth |
| Erinome | Clear |
| Algenib | Gravelly |
| Rasalgethi | Informative |
| Laomedeia | Upbeat |
| Achernar | Soft |
| Alnilam | Firm |
| Schedar | Even |
| Gacrux | Mature |
| Pulcherrima | Forward |
| Achird | Friendly |
| Zubenelgenubi | Casual |
| Vindemiatrix | Gentle |
| Sadachbia | Lively |
| Sadaltager | Knowledgeable |
| Sulafat | Warm |

Initial GOSLO candidates to audition first:

| Candidate | Why |
| --- | --- |
| Aoede | Current default; breezy and light, likely safe for a quiet companion. |
| Leda | Youthful; may fit "young lady", but check whether it becomes too bright. |
| Achernar | Soft; likely worth testing for a gentler大小姐 feel. |
| Vindemiatrix | Gentle; likely worth testing for softer companion tone. |
| Sulafat | Warm; likely worth testing if Aoede feels too airy. |
| Callirrhoe | Easy-going; possible if GOSLO should feel calmer. |

## Local Runtime Contract

LineA:

- Runtime path: `src/parrot/brain/agent.py` builds
  `google.realtime.RealtimeModel(voice=config.gemini.live_voice, ...)`.
- Config source: `src/parrot/shared/config.py`.
- Env key: `GEMINI_LIVE_VOICE`.
- Current default: `Aoede`.
- Empty or unsupported `GEMINI_LIVE_VOICE` falls back to `Aoede`.
- Supported names are normalized case-insensitively.

LineB:

- Runtime path: separate STT/LLM/TTS pipeline.
- Voice source: LineProfile TTS fields and LineB env overrides such as
  `PARROT_LINEB_TTS_PROVIDER` and `PARROT_LINEB_CARTESIA_VOICE_ID`.
- LineB voice should not be changed by the LineA policy.

Line selection:

- `PARROT_LLM_PIPELINE=line_b` in `.env` is a cold-start fallback when no
  higher-priority runtime config exists.
- `data/runtime_config.json` should win for orchestrated startup.
- Menu / RoomProfile selection can represent the selected line, while the
  running Brain session may keep the old line until reconnect/restart.

## Change Procedure

When the user picks a LineA voice:

1. Set `GEMINI_LIVE_VOICE=<VoiceName>` in the runtime environment or `.env`.
2. Restart/reconnect the Brain LiveKit session so a new `AgentSession` is built.
3. Confirm startup logs or status show:
   - running line: `line_a`
   - Gemini Live model
   - `live_voice=<VoiceName>`
4. If the voice sounds wrong, check whether the current running line is actually
   LineA or LineB before changing persona text.

## Prompt Strategy Rule

For style control, prefer:

```text
使用正常中文短句。语气柔软、轻微傲娇、有日系贵族大小姐感。
```

over long lists of unwanted phrases. Keep one short boundary if needed:

```text
不用鸟叫拟声词或动物口癖代替说话。
```

Do not repeat unwanted catchphrases in examples. Examples should only show the
desired GOSLO wording.
