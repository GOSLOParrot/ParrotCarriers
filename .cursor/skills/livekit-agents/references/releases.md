# Releases

Version history for this repository (344 releases).

## livekit-agents@1.5.2: livekit-agents@1.5.2
**Published:** 2026-04-08

> [!NOTE]  
> **livekit-agents 1.5 introduced many new features. You can check out the changelog [here](https://github.com/livekit/agents/releases/tag/livekit-agents%401.5.0).**

## What's Changed
* Update Phonic `generate_reply` timeout to 10 seconds by @qionghuang6 in https://github.com/livekit/agents/pull/5205
* fix: pass prometheus_multiproc_dir in from_server_options initialization by @ivanbalingit in https://github.com/livekit/agents/pull/5195
* feat(mistralai): upgrade to SDK v2 by @Pauldevillers in https://github.com/livekit/agents/pull/5163
* (deepgram sttv2): validate eager_eot_threshold value by @tinalenguyen in https://github.com/livekit/agents/pull/5216
* Add WebSocket streaming support to Baseten TTS plugin by @iancarrasco-b10 in https://github.com/livekit/agents/pull/4741
* fix: allow codec format specification via the user for Sarvam TTS by @pUrGe12 in https://github.com/livekit/agents/pull/5209
* emit agent handoff from conversation_item_added by @tinalenguyen in https://github.com/livekit/agents/pull/5218
* fix(llm): surface validation error details to LLM on function call argument failures by @Lyt060814 in https://github.com/livekit/agents/pull/5193
* fix(cli): update log level width in console mode by @chenghao-mou in https://github.com/livekit/agents/pull/5224
* fix(utils): preserve type annotations in deprecate_params by @longcw in https://github.com/livekit/agents/pull/5200
* fix(test): replace oai with deepgram and fix broken tests by @chenghao-mou in https://github.com/livekit/agents/pull/5225
* feat(voice): reuse STT connection across agent handoffs by @longcw in https://github.com/livekit/agents/pull/5093
* feat(google): add VertexRAGRetrieval provider tool by @youpesh in https://github.com/livekit/agents/pull/5222
* fix: ensure MCP client enter/exit run in the same task by @longcw in https://github.com/livekit/agents/pull/5223
* feat(assemblyai): add domain parameter for Medical Mode by @m-ods in https://github.com/livekit/agents/pull/5208
* fix: Nova Sonic interactive context bugs and dynamic tool support by @prettyprettyprettygood in https://github.com/livekit/agents/pull/5220
* (google realtime): add gemini-3.1-flash-live-preview model by @tinalenguyen in https://github.com/livekit/agents/pull/5233
* fix(utils): improve type annotation for deprecate_params decorator by @longcw in https://github.com/livekit/agents/pull/5244
* fix: expose endpointing_opts in AgentSession.update_options() by @longcw in https://github.com/livekit/agents/pull/5243
* Fix/stt fallback adapter propagate aligned transcript by @miladmnasr in https://github.com/livekit/agents/pull/5237
* feat(mistral): add voxtral TTS support by @jeanprbt in https://github.com/livekit/agents/pull/5245
* feat(anthropic): support strict tool use schema by @roshan-shaik-ml in https://github.com/livekit/agents/pull/5259
* Baseten Plugin Update: fix metadata schema, add chain_id support, and improve response parsing by @jiegong-fde in https://github.com/livekit/agents/pull/4889
* feat(upliftai): add support for phrase replacement config id by @zaidqureshi2 in https://github.com/livekit/agents/pull/5261
* feat(soniox): expose max_endpoint_delay_ms option by @pstrav in https://github.com/livekit/agents/pull/5214
* fix: prevent TTS retry after partial audio and replay input on retry by @longcw in https://github.com/livekit/agents/pull/5242
* fix: only start session host when it's primary session by @longcw in https://github.com/livekit/agents/pull/5241
* fix: prevent CancelledError from propagating to unrelated Tee peers by @longcw in https://github.com/livekit/agents/pull/5273
* fix: prevent AttributeError in ThreadJobExecutor.logging_extra() by @longcw in https://github.com/livekit/agents/pull/5277
* fix(openai): close current generation channels on realtime reconnect by @longcw in https://github.com/livekit/agents/pull/5276
* fix(recorder): guard against empty agent speech frames by @chenghao-mou in https://github.com/livekit/agents/pull/5279
* fix(stt): reset VAD when STT sends EOT by @chenghao-mou in https://github.com/livekit/agents/pull/5095
* feat(anam): add avatarModel config support by @sr-anam in https://github.com/livekit/agents/pull/5272
* fix: catch TimeoutError from drain() so aclose() always runs by @seglo in https://github.com/livekit/agents/pull/5282
* (gemini-3.1-flash-live-preview): add warning for generate_reply by @tinalenguyen in https://github.com/livekit/agents/pull/5286
* feat(mistralai): add ref_audio support to Voxtral TTS for zero-shot voice cloning by @EtienneLescot in https://github.com/livekit/agents/pull/5278
* fix(core): reset user state to listening when audio is disabled by @chenghao-mou in https://github.com/livekit/agents/pull/5198
* append generate_reply instructions as system msg and convert it to user msg if unsupported by @longcw in https://github.com/livekit/agents/pull/5287
* add AsyncToolset by @longcw in https://github.com/livekit/agents/pull/5127
* fix(core): fix BackgroundAudioPlayer.play() hanging indefinitely by @theomonnom in https://github.com/livekit/agents/pull/5299
* fix(cli): prevent api_key/api_secret from leaking in tracebacks by @theomonnom in https://github.com/livekit/agents/pull/5300
* (phonic) Update languages fields by @qionghuang6 in https://github.com/livekit/agents/pull/5285
* fix(core): reduce TTS output buffering latency by @theomonnom in https://github.com/livekit/agents/pull/5292
* add session_end_timeout and gracefully cancel entrypoint on shutdown by @theomonnom in https://github.com/livekit/agents/pull/4580
* feat: OTEL metrics for latencies, usage, and connection timing by @theomonnom in https://github.com/livekit/agents/pull/4891
* evals: custom judges, tag metadata, and OTEL improvements by @theomonnom in https://github.com/livekit/agents/pull/5306
* fix is_context_type for generic RunContext types by @theomonnom in https://github.com/livekit/agents/pull/5307
* add 7-day uv cooldown by @chenghao-mou in https://github.com/livekit/agents/pull/5290
* fix(openai realtime): support per-response tool_choice in realtime sessions by @longcw in https://github.com/livekit/agents/pull/5211
* use delta aggregation temporality for otel metrics by @paulwe in https://github.com/livekit/agents/pull/5314
* (phonic) Add `min_words_to_interrupt` to Phonic plugin options by @qionghuang6 in https://github.com/livekit/agents/pull/5304
* add tag field to evaluation OTEL log records by @theomonnom in https://github.com/livekit/agents/pull/5315
* docs: add example agent replies to AsyncToolset by @longcw in https://github.com/livekit/agents/pull/5313
* fix(cartesia): handle flush_done message in TTS _recv_task by @Panmax in https://github.com/livekit/agents/pull/5321
* fix(voice): make function call history preservation configurable in AgentTask by @GopalGB in https://github.com/livekit/agents/pull/5288
* fix: convert oneOf to anyOf in strict schema for discriminated unions by @longcw in https://github.com/livekit/agents/pull/5324
* (gemini realtime): add warnings in update_chat_ctx and update_instructions by @tinalenguyen in https://github.com/livekit/agents/pull/5332
* fix: wait_for_participant waits until participant is fully active by @davidzhao in https://github.com/livekit/agents/pull/5271
* feat: answering machine detection by @chenghao-mou in https://github.com/livekit/agents/pull/4906
* feat: expose service_tier in CompletionUsage from OpenAI Responses API by @piyush-gambhir in https://github.com/livekit/agents/pull/5341
* fix: add PARTICIPANT_KIND_CONNECTOR to default participant kinds by @anunaym14 in https://github.com/livekit/agents/pull/5339
* feat/sarvam-llm-openai-compatible-integration by @dhruvladia-sarvam in https://github.com/livekit/agents/pull/5069
* feat(azure-stt): Possibility to change segmentation options during a call by @rafallezanko in https://github.com/livekit/agents/pull/5323
* fix(sarvam): sync missing API params, fix value ranges, and update models by @Namit1867 in https://github.com/livekit/agents/pull/5347
* (xai tts): update fields and ws setup by @tinalenguyen in https://github.com/livekit/agents/pull/5350
* fix(smallestai): add lightning-v3.1 endpoint routing by @sg-siddhant in https://github.com/livekit/agents/pull/5330
* feat(inference): add debug/identification headers to inference requests by @adrian-cowham in https://github.com/livekit/agents/pull/5337
* Move community plugins to livekit-plugins/community/ by @theomonnom in https://github.com/livekit/agents/pull/5250
* feat: support per-response tools in generate_reply by @longcw in https://github.com/livekit/agents/pull/5310
* fix xAI realtime update chat ctx by @longcw in https://github.com/livekit/agents/pull/5320
* Fix RoomIO teardown listener cleanup by @sindarknave in https://github.com/livekit/agents/pull/5357
* feat(mistral): support voxtral realtime streaming stt & modernize mistral plugin by @jeanprbt in https://github.com/livekit/agents/pull/5289
* fix: say() with missing audio file hangs forever and blocks speech queue by @theomonnom in https://github.com/livekit/agents/pull/5358
* add prompt_cache_retention chat completion option to inference by @s-hamdananwar in https://github.com/livekit/agents/pull/5370
* Add Murf as optional dep by @royalfig in https://github.com/livekit/agents/pull/5334
* feat(core): Support multiple provider keys in extra_content serialization by @adrian-cowham in https://github.com/livekit/agents/pull/5374
* ci: add PyPI publish workflow with trusted publishing by @theomonnom in https://github.com/livekit/agents/pull/5379
* feat: Add D-ID avatar plugin by @osimhi213 in https://github.com/livekit/agents/pull/5232
* ci: fix tag checkout and discover glob by @theomonnom in https://github.com/livekit/agents/pull/5381
* feat(rime): add mistv3 model support by @mcullan in https://github.com/livekit/agents/pull/5298
* ci: fix update_versions.py invocation by @theomonnom in https://github.com/livekit/agents/pull/5382
* ci: remove release label from publish workflow by @theomonnom in https://github.com/livekit/agents/pull/5384
* require livekit-protocol>=1.1.5, implement get_framework_info by @theomonnom in https://github.com/livekit/agents/pull/5385
* ci: fix build permissions and tag format by @theomonnom in https://github.com/livekit/agents/pull/5386
* ci: fix version read in publish workflow by @theomonnom in https://github.com/livekit/agents/pull/5388
* ci: use livekit-agents@version for release PR title by @theomonnom in https://github.com/livekit/agents/pull/5390
* fix: minimax optional dep not bumped by update_versions.py by @theomonnom in https://github.com/livekit/agents/pull/5392
* livekit-agents@1.5.2 by @github-actions[bot] in https://github.com/livekit/agents/pull/5391

## New Contributors
* @ivanbalingit made their first contribution in https://github.com/livekit/agents/pull/5195
* @Pauldevillers made their first contribution in https://github.com/livekit/agents/pull/5163
* @iancarrasco-b10 made their first contribution in https://github.com/livekit/agents/pull/4741
* @pUrGe12 made their first contribution in https://github.com/livekit/agents/pull/5209
* @Lyt060814 made their first contribution in https://github.com/livekit/agents/pull/5193
* @youpesh made their first contribution in https://github.com/livekit/agents/pull/5222
* @m-ods made their first contribution in https://github.com/livekit/agents/pull/5208
* @prettyprettyprettygood made their first contribution in https://github.com/livekit/agents/pull/5220
* @miladmnasr made their first contribution in https://github.com/livekit/agents/pull/5237
* @jeanprbt made their first contribution in https://github.com/livekit/agents/pull/5245
* @roshan-shaik-ml made their first contribution in https://github.com/livekit/agents/pull/5259
* @jiegong-fde made their first contribution in https://github.com/livekit/agents/pull/4889
* @pstrav made their first contribution in https://github.com/livekit/agents/pull/5214
* @sr-anam made their first contribution in https://github.com/livekit/agents/pull/5272
* @seglo made their first contribution in https://github.com/livekit/agents/pull/5282
* @EtienneLescot made their first contribution in https://github.com/livekit/agents/pull/5278
* @GopalGB made their first contribution in https://github.com/livekit/agents/pull/5288
* @piyush-gambhir made their first contribution in https://github.com/livekit/agents/pull/5341
* @anunaym14 made their first contribution in https://github.com/livekit/agents/pull/5339
* @Namit1867 made their first contribution in https://github.com/livekit/agents/pull/5347
* @sg-siddhant made their first contribution in https://github.com/livekit/agents/pull/5330
* @sindarknave made their first contribution in https://github.com/livekit/agents/pull/5357
* @royalfig made their first contribution in https://github.com/livekit/agents/pull/5334
* @osimhi213 made their first contribution in https://github.com/livekit/agents/pull/5232
* @mcullan made their first contribution in https://github.com/livekit/agents/pull/5298

**Full Changelog**: https://github.com/livekit/agents/compare/livekit-agents@1.5.1...livekit-agents@1.5.2

[View on GitHub](https://github.com/livekit/agents/releases/tag/livekit-agents%401.5.2)

---

## livekit-agents@1.5.1: livekit-agents@1.5.1
**Published:** 2026-03-23

> [!NOTE]  
> **livekit-agents 1.5 introduced many new features. You can check out the changelog [here](https://github.com/livekit/agents/releases/tag/livekit-agents%401.5.0).**


## What's Changed
* fix azure openai realtime support & add realtime models tests by @theomonnom in https://github.com/livekit/agents/pull/5168
* fix(core): version mismatch due to bad merge by @chenghao-mou in https://github.com/livekit/agents/pull/5176
* fix(turn-detector): relax transformers upper bound to allow 5.x by @gdoermann in https://github.com/livekit/agents/pull/5174
* (gladia & soniox): add translation support by @tinalenguyen in https://github.com/livekit/agents/pull/5148
* feat(agents): support LIVEKIT_OBSERVABILITY_URL for custom observability endpoints by @theomonnom in https://github.com/livekit/agents/pull/5179
* (xai tts): update websocket endpoint by @tinalenguyen in https://github.com/livekit/agents/pull/5180
* fix(core): restore chat topic support in room IO by @chenghao-mou in https://github.com/livekit/agents/pull/5181
* Unskip Tool Call Items before Summarization in Task Group by @toubatbrian in https://github.com/livekit/agents/pull/5169
* add sdk_version to SessionReport for observability by @theomonnom in https://github.com/livekit/agents/pull/5182
* feat(hamming): add hamming monitoring plugin package by @duchammingai in https://github.com/livekit/agents/pull/5135
* chore(mypy): enable mypy cache in type checking by @chenghao-mou in https://github.com/livekit/agents/pull/5192
* fix: expose Chirp 3 google STT endpoint sensitivity by @karlsonlee-livekit in https://github.com/livekit/agents/pull/5196
* add MCPToolset by @longcw in https://github.com/livekit/agents/pull/5138
* Feat/personaplex plugin by @milanperovic in https://github.com/livekit/agents/pull/4660
* fix: skip redundant realtime events in OpenAI plugin by @theomonnom in https://github.com/livekit/agents/pull/5204
* feat: enable AGC by default on RoomInput audio by @theomonnom in https://github.com/livekit/agents/pull/5185
* bump minimum livekit sdk version to 1.1.3 by @theomonnom in https://github.com/livekit/agents/pull/5206
* livekit-agents 1.5.1 by @theomonnom in https://github.com/livekit/agents/pull/5207

## New Contributors
* @duchammingai made their first contribution in https://github.com/livekit/agents/pull/5135
* @karlsonlee-livekit made their first contribution in https://github.com/livekit/agents/pull/5196
* @milanperovic made their first contribution in https://github.com/livekit/agents/pull/4660

**Full Changelog**: https://github.com/livekit/agents/compare/livekit-agents@1.5.0...livekit-agents@1.5.1

[View on GitHub](https://github.com/livekit/agents/releases/tag/livekit-agents%401.5.1)

---

## livekit-agents@1.5.0: livekit-agents@1.5.0
**Published:** 2026-03-19

## Highlights

### Adaptive Interruption Handling

The headline feature of v1.5.0: an audio-based ML model that distinguishes genuine user interruptions from incidental sounds like backchannels ("mm-hmm"), coughs, sighs, or background noise. Enabled by default — no configuration needed.

Key stats:
- **86% precision** and **100% recall** at 500ms overlapping speech
- Rejects **51%** of traditional VAD false positives
- Detects true interruptions **64% faster** than VAD alone
- Inference completes in **30ms or less**

When a false interruption is detected, the agent automatically resumes playback from where it left off — no re-generation needed.

To opt out and use VAD-only interruption:

```python
session = AgentSession(
    ...
    turn_handling=TurnHandlingOptions(
        interruption={
            "mode": "vad",
        },
    ),
)
```

Blog post: https://livekit.com/blog/adaptive-interruption-handling

### Dynamic Endpointing

Endpointing delays now adapt to each conversation's natural rhythm. Instead of a fixed silence threshold, the agent uses an exponential moving average of pause durations to dynamically adjust when it considers the user's turn complete.

```python
session = AgentSession(
    ...
    turn_handling=TurnHandlingOptions(
        endpointing={
            "mode": "dynamic",
            "min_delay": 0.3,
            "max_delay": 3.0,
        },
    ),
)
```

### New `TurnHandlingOptions` API

Endpointing and interruption settings are now consolidated into a single `TurnHandlingOptions` dict passed to `AgentSession`. Old keyword arguments (`min_endpointing_delay`, `allow_interruptions`, etc.) still work but are deprecated and will emit warnings.

```python
session = AgentSession(
    turn_handling={
        "turn_detection": "vad",
        "endpointing": {"min_delay": 0.5, "max_delay": 3.0},
        "interruption": {"enabled": True, "mode": "adaptive"},
    },
)
```

### Session Usage Tracking

New `SessionUsageUpdatedEvent` provides structured, per-model usage data — token counts, character counts, and audio durations — broken down by provider and model:

```python
@session.on("session_usage_updated")
def on_usage(ev: SessionUsageUpdatedEvent):
    for usage in ev.usage.model_usage:
        print(f"{usage.provider}/{usage.model}: {usage}")
```

Usage types: `LLMModelUsage`, `TTSModelUsage`, `STTModelUsage`, `InterruptionModelUsage`.

You can also access aggregated usage at any time via the `session.usage` property:

```python
usage = session.usage
for model_usage in usage.model_usage:
    print(model_usage)
```

Usage data is also included in `SessionReport` (via `model_usage`), so it's available in post-session telemetry and reporting out of the box.

### Per-Turn Latency on `ChatMessage.metrics`

Each `ChatMessage` now carries a `metrics` field (`MetricsReport`) with per-turn latency data:
- `transcription_delay` — time to obtain transcript after end of speech
- `end_of_turn_delay` — time between end of speech and turn decision
- `on_user_turn_completed_delay` — time in the developer callback

### Action-Aware Chat Context Summarization

Context summarization now includes function calls and their outputs when building summaries, preserving tool-use context across the conversation window.

### Configurable Log Level

Set the agent log level via `LIVEKIT_LOG_LEVEL` environment variable or through `ServerOptions`, without touching your code.

## Deprecations

| Deprecated | Replacement | Notes |
|---|---|---|
| `metrics_collected` event | `session_usage_updated` event + `ChatMessage.metrics` | Usage/cost data moves to `session_usage_updated`; per-turn latency moves to `ChatMessage.metrics`. Old listeners still work with a deprecation warning. |
| `UsageCollector` | `ModelUsageCollector` | New collector supports per-model/provider breakdown |
| `UsageSummary` | `LLMModelUsage`, `TTSModelUsage`, `STTModelUsage` | Typed per-service usage classes |
| `RealtimeModelBeta` | `RealtimeModel` | Beta API removed |
| `AgentFalseInterruptionEvent.message` / `.extra_instructions` | Automatic resume via adaptive interruption | Accessing these fields logs a deprecation warning |
| `AgentSession` kwargs: `min_endpointing_delay`, `max_endpointing_delay`, `allow_interruptions`, `discard_audio_if_uninterruptible`, `min_interruption_duration`, `min_interruption_words`, `turn_detection`, `false_interruption_timeout`, `resume_false_interruption` | `turn_handling=TurnHandlingOptions(...)` | Old kwargs still work but emit deprecation warnings. Will be removed in v2.0. |
| `Agent` / `AgentTask` kwargs: `turn_detection`, `min_endpointing_delay`, `max_endpointing_delay`, `allow_interruptions` | `turn_handling=TurnHandlingOptions(...)` | Same migration path as `AgentSession`. Will be removed in future versions. |

## Complete changelog
* (xai): add grok text to speech api to readme by @tinalenguyen in https://github.com/livekit/agents/pull/5125
* Remove Gemini 2.0 models from inference gateway types by @Shubhrakanti in https://github.com/livekit/agents/pull/5133
* feat: support log level via ServerOptions and LIVEKIT_LOG_LEVEL env var by @onurburak9 in https://github.com/livekit/agents/pull/5112
* fix: preserve 'type' field in TaskGroup JSON schema enum items by @weiguangli-io in https://github.com/livekit/agents/pull/5073
* feat(assemblyai): expose session ID from Begin event by @dlange-aai in https://github.com/livekit/agents/pull/5132
* fix: strip empty {} entries from anyOf/oneOf in strict JSON schema by @theomonnom in https://github.com/livekit/agents/pull/5137
* fix: update_instructions() now reflected in tool call response generation by @weiguangli-io in https://github.com/livekit/agents/pull/5072
* Make chat context summarization action-aware by @toubatbrian in https://github.com/livekit/agents/pull/5099
* fix(realtime): sync remote items to local chat_ctx with placeholders to prevent in-flight deletion by @longcw in https://github.com/livekit/agents/pull/5114
* Set _speech_start_time when VAD START_OF_SPEECH activates by @hudson-worden in https://github.com/livekit/agents/pull/5027
* Fix(inworld): "Context not found" errors caused by invalid enum parameter types by @ianbbqzy in https://github.com/livekit/agents/pull/5153
* increase generate_reply timeout & remove RealtimeModelBeta by @theomonnom in https://github.com/livekit/agents/pull/5149
* add livekit-blockguard plugin by @theomonnom in https://github.com/livekit/agents/pull/5023
* openai: add max_completion_tokens to with_azure() by @abhishekranjan-bluemachines in https://github.com/livekit/agents/pull/5143
* Restrict mistralai dependency to use v1 sdk by @csanz91 in https://github.com/livekit/agents/pull/5116
* feat(assemblyai): add DEBUG-level diagnostic logging by @dlange-aai in https://github.com/livekit/agents/pull/5146
* Fix Phonic `generate_reply` to resolve with the current `GenerationCreatedEvent` by @qionghuang6 in https://github.com/livekit/agents/pull/5147
* fix(11labs): add empty keepalive message and remove final duplicates by @chenghao-mou in https://github.com/livekit/agents/pull/5139
* AGT-2182: Add adaptive interruption handling and dynamic endpointing by @chenghao-mou in https://github.com/livekit/agents/pull/4771
* livekit-agents 1.5.0 by @theomonnom in https://github.com/livekit/agents/pull/5165

## New Contributors
* @onurburak9 made their first contribution in https://github.com/livekit/agents/pull/5112
* @weiguangli-io made their first contribution in https://github.com/livekit/agents/pull/5073
* @abhishekranjan-bluemachines made their first contribution in https://github.com/livekit/agents/pull/5143
* @csanz91 made their first contribution in https://github.com/livekit/agents/pull/5116

**Full Changelog**: https://github.com/livekit/agents/compare/livekit-agents@1.4.6...livekit-agents@1.5.0

[View on GitHub](https://github.com/livekit/agents/releases/tag/livekit-agents%401.5.0)

---

## livekit-agents@1.4.6: livekit-agents@1.4.6
**Published:** 2026-03-16

## What's Changed
* fix(types): replace TypeGuard with TypeIs in is_given for bidirectional narrowing by @longcw in https://github.com/livekit/agents/pull/5079
* [inworld] websocket _recv_loop to flush the audio immediately by @ianbbqzy in https://github.com/livekit/agents/pull/5071
* fix: include `null` in enum array for nullable enum schemas by @MSameerAbbas in https://github.com/livekit/agents/pull/5080
* (openai chat completions): drop reasoning_effort when function tools are present by @tinalenguyen in https://github.com/livekit/agents/pull/5088
* (google realtime): replace deprecated mediaChunks by @tinalenguyen in https://github.com/livekit/agents/pull/5089
* fix: omit `required` field in tool schema when function has no parameters by @longcw in https://github.com/livekit/agents/pull/5082
* fix(sarvam-tts): correct mime_type from audio/mp3 to audio/wav by @shmundada93 in https://github.com/livekit/agents/pull/5086
* add trunk_config to WarmTransferTask for SIP endpoint transfers by @longcw in https://github.com/livekit/agents/pull/5016
* healthcare example by @tinalenguyen in https://github.com/livekit/agents/pull/5031
* fix(openai): only reuse previous_response_id when pending tool calls are completed by @longcw in https://github.com/livekit/agents/pull/5094
* feat(assemblyai): add speaker diarization support by @dlange-aai in https://github.com/livekit/agents/pull/5074
* fix: prevent _cancel_speech_pause from poisoning subsequent user turns by @giulio-leone in https://github.com/livekit/agents/pull/5101
* feat(google): support universal credential types in STT and TTS credentials_file by @rafallezanko in https://github.com/livekit/agents/pull/5056
* Add Murf AI - TTS Plugin Support by @gaurav-murf in https://github.com/livekit/agents/pull/3000
* feat(voice): add callable TextTransforms support with built-in replace transform by @longcw in https://github.com/livekit/agents/pull/5104
* fix(eou): only reset speech/speaking time when no new speech by @chenghao-mou in https://github.com/livekit/agents/pull/5083
* (xai): add tts by @tinalenguyen in https://github.com/livekit/agents/pull/5120
* (xai tts): add language parameter by @tinalenguyen in https://github.com/livekit/agents/pull/5122
* livekit-agents 1.4.6 by @theomonnom in https://github.com/livekit/agents/pull/5123

## New Contributors
* @shmundada93 made their first contribution in https://github.com/livekit/agents/pull/5086
* @dlange-aai made their first contribution in https://github.com/livekit/agents/pull/5074
* @gaurav-murf made their first contribution in https://github.com/livekit/agents/pull/3000

**Full Changelog**: https://github.com/livekit/agents/compare/livekit-agents@1.4.5...livekit-agents@1.4.6

[View on GitHub](https://github.com/livekit/agents/releases/tag/livekit-agents%401.4.6)

---

## livekit-agents@1.4.5: livekit-agents@1.4.5
**Published:** 2026-03-11

## What's Changed
* Pass through additional params to LemonSlice when using the LemonSlice Avatar by @jp-lemon in https://github.com/livekit/agents/pull/4984
* fix(anthropic): add dummy user message for Claude 4.6+ trailing assistant turns by @giulio-leone in https://github.com/livekit/agents/pull/4973
* (keyframe): remove whitespace from py.typed by @tinalenguyen in https://github.com/livekit/agents/pull/4990
* Add Phonic Plugin to LiveKit agents by @qionghuang6 in https://github.com/livekit/agents/pull/4980
* Fixed E2EE encryption of content in data tracks by @zelidrag-arbo in https://github.com/livekit/agents/pull/4992
* fix: resync tool context when tools are mutated inside llm_node by @longcw in https://github.com/livekit/agents/pull/4994
* [🤖 readme-manager] Update README by @ladvoc in https://github.com/livekit/agents/pull/4996
* fix(google): prevent function_call text from leaking to TTS output by @BkSouX in https://github.com/livekit/agents/pull/4999
* (openai responses): add websocket connection pool by @tinalenguyen in https://github.com/livekit/agents/pull/4985
* (openai tts): close openai client by @tinalenguyen in https://github.com/livekit/agents/pull/5012
* nvidia stt: add speaker diarization support by @longcw in https://github.com/livekit/agents/pull/4997
* update error message when TTS is not set by @longcw in https://github.com/livekit/agents/pull/4998
* initialize interval future in init by @tinalenguyen in https://github.com/livekit/agents/pull/5013
* Fix/elevenlabs update default voice non expiring by @yusuf-eren in https://github.com/livekit/agents/pull/5010
* [Inworld] Flush to drain decoder on every audio chunk from server by @ianbbqzy in https://github.com/livekit/agents/pull/4983
* (google): support passing credentials through realtime and llm by @tinalenguyen in https://github.com/livekit/agents/pull/5015
* use default voice accessible to free tier users by @tmshapland in https://github.com/livekit/agents/pull/5020
* make commit_user_turn() return a Future with the audio transcript by @longcw in https://github.com/livekit/agents/pull/5019
* Add GPT-5.4 to OpenAI plugin by @Topherhindman in https://github.com/livekit/agents/pull/5022
* Generate and upload markdown docs by @Topherhindman in https://github.com/livekit/agents/pull/4993
* Add GPT-5.4 and GPT-5.3 Chat Latest support by @Topherhindman in https://github.com/livekit/agents/pull/5030
* Improve Audio Generation Quality for Cartesia TTS Plugin by @tycartesia in https://github.com/livekit/agents/pull/5032
* fix(elevenlabs): handle empty words in _to_timed_words by @MonkeyLeeT in https://github.com/livekit/agents/pull/5036
* fix(deepgram): include word confidence for stt v2 alternatives by @inickt in https://github.com/livekit/agents/pull/5034
* fix: generate final LLM response when max_tool_steps is reached by @IanSteno in https://github.com/livekit/agents/pull/4747
* fix: guard against negative sleep duration in voice agent scheduling by @jnMetaCode in https://github.com/livekit/agents/pull/5040
* add modality-aware Instructions with audio/text variants by @longcw in https://github.com/livekit/agents/pull/4987
* fix(core): move callbacks to the caller by @chenghao-mou in https://github.com/livekit/agents/pull/5039
* Added raw logging of API errors via the LiveKit plugins for both STT and TTS. by @dhruvladia-sarvam in https://github.com/livekit/agents/pull/5025
* Log LemonSlice API error + new agent_idle_prompt arg by @jp-lemon in https://github.com/livekit/agents/pull/5052
* Sarvam v3 tts addns by @dhruvladia-sarvam in https://github.com/livekit/agents/pull/4976
* fix(google): avoid session restart on update_instructions, use mid-session client content by @D-zigi in https://github.com/livekit/agents/pull/5049
* (responses llm): override provider property and set use_websocket to False for wrappers by @tinalenguyen in https://github.com/livekit/agents/pull/5055
* feat(mcp): add MCPToolResultResolver callback for customizing tool call results by @longcw in https://github.com/livekit/agents/pull/5046
* docs: add development instructions to README and example READMEs by @bcherry in https://github.com/livekit/agents/pull/2636
* Improve plugin READMEs with installation, pre-requisites, and docs links by @bcherry in https://github.com/livekit/agents/pull/3025
* Add `generate_reply` and `update_chat_ctx` support to Phonic Plugin by @qionghuang6 in https://github.com/livekit/agents/pull/5058
* feat: enhance worker load management with reserved slots and effective load calculation by @ProblematicToucan in https://github.com/livekit/agents/pull/4911
* fix(core): render error message with full details in traceback by @chenghao-mou in https://github.com/livekit/agents/pull/5047
* feat(core): allow skip_reply when calling commit_user_turn by @chenghao-mou in https://github.com/livekit/agents/pull/5066
* fix(mcp): replace deprecated streamablehttp_client with streamable_http_client by @longcw in https://github.com/livekit/agents/pull/5048
* fix: disable aec warmup timer when audio is disabled by @longcw in https://github.com/livekit/agents/pull/5065
* feat(openai): add transcript_confidence from OpenAI realtime logprobs by @theomonnom in https://github.com/livekit/agents/pull/5070
* Enhance LK Inference STT and TTS options with new parameters and models by @russellmartin-livekit in https://github.com/livekit/agents/pull/4949
* Move Instructions to beta exports by @theomonnom in https://github.com/livekit/agents/pull/5075
* livekit-agents 1.4.5 by @theomonnom in https://github.com/livekit/agents/pull/5076

## New Contributors
* @giulio-leone made their first contribution in https://github.com/livekit/agents/pull/4973
* @qionghuang6 made their first contribution in https://github.com/livekit/agents/pull/4980
* @zelidrag-arbo made their first contribution in https://github.com/livekit/agents/pull/4992
* @tmshapland made their first contribution in https://github.com/livekit/agents/pull/5020
* @tycartesia made their first contribution in https://github.com/livekit/agents/pull/5032
* @inickt made their first contribution in https://github.com/livekit/agents/pull/5034
* @jnMetaCode made their first contribution in https://github.com/livekit/agents/pull/5040
* @D-zigi made their first contribution in https://github.com/livekit/agents/pull/5049
* @ProblematicToucan made their first contribution in https://github.com/livekit/agents/pull/4911

**Full Changelog**: https://github.com/livekit/agents/compare/livekit-agents@1.4.4...livekit-agents@1.4.5

[View on GitHub](https://github.com/livekit/agents/releases/tag/livekit-agents%401.4.5)

---

## livekit-agents@1.4.4: livekit-agents@1.4.4
**Published:** 2026-03-03

## What's Changed
* Upgrading Cartesia TTS default to Sonic 3 by @chongzluong in https://github.com/livekit/agents/pull/4922
* (google stt): add denoiser support and explicit adaptation param by @tinalenguyen in https://github.com/livekit/agents/pull/4918
* feat: add Telnyx STT and TTS plugins by @fmv1992 in https://github.com/livekit/agents/pull/4665
* feat: add livekit-plugins-sambanova with LLM support by @mahimairaja in https://github.com/livekit/agents/pull/4910
* skip adding run event when run result is done by @longcw in https://github.com/livekit/agents/pull/4925
* guard against RuntimeError when restoring allow_interruptions in AgentTask by @longcw in https://github.com/livekit/agents/pull/4930
* Add support for Gradium pronunciation ids. by @LaurentMazare in https://github.com/livekit/agents/pull/4932
* feat: optimize wav decoding by @davidzhao in https://github.com/livekit/agents/pull/4905
* fix: drain buffered log records before closing LogQueueListener by @longcw in https://github.com/livekit/agents/pull/4928
* fix(voice): return ToolError for unknown function calls instead of si… by @yusuf-eren in https://github.com/livekit/agents/pull/4935
* Update readme to include mcp and skill information by @Topherhindman in https://github.com/livekit/agents/pull/4937
* fix: migrate HttpServer to AppRunner for proper connection lifecycle by @longcw in https://github.com/livekit/agents/pull/4945
* ignore unknown tools from xai realtime by @longcw in https://github.com/livekit/agents/pull/4941
* soniox stt: populate timing and confidence from token metadata by @longcw in https://github.com/livekit/agents/pull/4939
* fix(openai): preserve non-instruction system messages in update_chat_ctx for realtime models by @longcw in https://github.com/livekit/agents/pull/4942
* feat(openai): add gpt-realtime-1.5 to RealtimeModels by @yusuf-eren in https://github.com/livekit/agents/pull/4947
* standardize language handling by @davidzhao in https://github.com/livekit/agents/pull/4926
* fix: avoid blocking event loop with unconditional psutil call in _load_task by @msaelices in https://github.com/livekit/agents/pull/4946
* add AEC warmup to suppress false interruptions on first speech by @longcw in https://github.com/livekit/agents/pull/4813
* initial by @dhruvladia-sarvam in https://github.com/livekit/agents/pull/4923
* fix asyncio.Future crash in console mode by @davidzhao in https://github.com/livekit/agents/pull/4952
* fix(11labs): Default to original alignment for CJK scripts by @chenghao-mou in https://github.com/livekit/agents/pull/4968
* support openai responses websocket mode by @tinalenguyen in https://github.com/livekit/agents/pull/4931
* Keyframe Labs Plugin by @kradkfl in https://github.com/livekit/agents/pull/4950
* hotfix: import issue in `agent_worker.py` by @kradkfl in https://github.com/livekit/agents/pull/4970
* feat(stt): add keyterms parameter in Elevenlabs STT plugin by @Arjun-A-I in https://github.com/livekit/agents/pull/4967
* feat(elevenlabs): report STT audio duration via RECOGNITION_USAGE events by @BkSouX in https://github.com/livekit/agents/pull/4953
* Fix/sarvam tts update options language code by @yusuf-eren in https://github.com/livekit/agents/pull/4957
* Fix: call playback started in sound device callback (console mode) by @chenghao-mou in https://github.com/livekit/agents/pull/4958
* fix: close duplex wrapper and log listener on process start failure by @longcw in https://github.com/livekit/agents/pull/4977
* feat(assemblyai): add u3-rt-pro model plus mid-stream updates, SpeechStarted, and ForceEndpoint support by @gsharp-aai in https://github.com/livekit/agents/pull/4965
* feat(stt): add support for AssemblyAI u3-rt-pro model and mid-session updates by @russellmartin-livekit in https://github.com/livekit/agents/pull/4961
* rename Language to LanguageCode by @theomonnom in https://github.com/livekit/agents/pull/4981
* livekit-agents 1.4.4 by @theomonnom in https://github.com/livekit/agents/pull/4982

## New Contributors
* @fmv1992 made their first contribution in https://github.com/livekit/agents/pull/4665
* @mahimairaja made their first contribution in https://github.com/livekit/agents/pull/4910
* @yusuf-eren made their first contribution in https://github.com/livekit/agents/pull/4935
* @Topherhindman made their first contribution in https://github.com/livekit/agents/pull/4937
* @kradkfl made their first contribution in https://github.com/livekit/agents/pull/4950
* @Arjun-A-I made their first contribution in https://github.com/livekit/agents/pull/4967
* @BkSouX made their first contribution in https://github.com/livekit/agents/pull/4953
* @gsharp-aai made their first contribution in https://github.com/livekit/agents/pull/4965

**Full Changelog**: https://github.com/livekit/agents/compare/livekit-agents@1.4.3...livekit-agents@1.4.4

[View on GitHub](https://github.com/livekit/agents/releases/tag/livekit-agents%401.4.4)

---

## livekit-agents@1.4.3: livekit-agents@1.4.3
**Published:** 2026-02-23

## What's Changed
* fix: use data.payload for browser navigate RPC by @theomonnom in https://github.com/livekit/agents/pull/4871
* Adjust dependency version requirement for Speechmatics STT by @sam-s10s in https://github.com/livekit/agents/pull/4873
* Not raising an error when JWT token is given for Neuphonic by @alexshelkov in https://github.com/livekit/agents/pull/4874
* Fix: Preserve OpenAI item ID on FunctionCall in Realtime sessions by @StianHanssen in https://github.com/livekit/agents/pull/4876
* gracefully stop AgentTask and parent agents when session close by @longcw in https://github.com/livekit/agents/pull/4730
* feat: add sip_headers param to WarmTransferTask by @theomonnom in https://github.com/livekit/agents/pull/4890
* Add vad_threshold parameter to AssemblyAI STT plugin by @AhmadIbrahiim in https://github.com/livekit/agents/pull/4880
* Update Simli integation endpoint by @Antonyesk601 in https://github.com/livekit/agents/pull/4894
* Upgrade the default drive thru LLM model to gpt 5 mini by @chenghao-mou in https://github.com/livekit/agents/pull/4897
* chore: remove models to be deprecated on March 19 2026 by @chenghao-mou in https://github.com/livekit/agents/pull/4895
* fix: skip OTLP log exporter setup when recording is disabled by @theomonnom in https://github.com/livekit/agents/pull/4892
* Drop unsupported params for reasoning models by @theomonnom in https://github.com/livekit/agents/pull/4908
* chore: update Async API base URL and default model name by @ashotbagh in https://github.com/livekit/agents/pull/4896
* (inworld tts): fix output emitter flush by @tinalenguyen in https://github.com/livekit/agents/pull/4912
* show turn metrics in console mode by @theomonnom in https://github.com/livekit/agents/pull/4916
* fix(google): raise the correct errors for blocked/etc by @davidzhao in https://github.com/livekit/agents/pull/4917
* support claude computer use on livekit-plugins-browser by @theomonnom in https://github.com/livekit/agents/pull/4882
* livekit-agents 1.4.3 by @theomonnom in https://github.com/livekit/agents/pull/4920

## New Contributors
* @StianHanssen made their first contribution in https://github.com/livekit/agents/pull/4876

**Full Changelog**: https://github.com/livekit/agents/compare/browser-v0.1.4...livekit-agents@1.4.3

[View on GitHub](https://github.com/livekit/agents/releases/tag/livekit-agents%401.4.3)

---

## livekit-agents@1.4.2: livekit-agents@1.4.2
**Published:** 2026-02-17

Stability-focused release with significant reliability improvements. Fixes multiple memory leaks in the process pool — job counter leaks on cancellation, pending assignment leaks on timeout, socket leaks on startup failure, and orphaned executors on send failure. IPC pipeline reliability has been improved, and several edge-case hangs have been resolved (participant never joining, Ctrl+C propagation to child processes). STT/TTS fallback behavior is now more robust: STT fallback correctly skips the main stream during recovery, and TTS fallback no longer shares resamplers across streams. Other fixes include ChatContext.truncate no longer dropping developer messages, correct cgroups v2 CPU quota parsing, proper on_session_end callback ordering, and log uploads even when sessions fail to start. Workers now automatically reject jobs when draining or full, and the proc pool correctly spawns processes under high load.

### New `RecordingOptions` API

The `record` parameter on `AgentSession.start()` now accepts granular options in addition to `bool`. All keys default to `True` when omitted.

```python
# record everything (default)
await session.start(agent, record=True)

# record nothing
await session.start(agent, record=False)

# granular: record audio but disable traces, logs, and transcript
await session.start(agent, record={"audio": True, "traces": False, "logs": False, "transcript": False})
```

## What's Changed
* fix multichannel input on speaking rate by @theomonnom in https://github.com/livekit/agents/pull/4740
* livekit-agents 1.4.1 by @theomonnom in https://github.com/livekit/agents/pull/4742
* fix ruff & type checks by @theomonnom in https://github.com/livekit/agents/pull/4743
* rename camb plugin to cambai by @tinalenguyen in https://github.com/livekit/agents/pull/4744
* fix ruff by @davidzhao in https://github.com/livekit/agents/pull/4749
* (liveavatar): change avatar mode from CUSTOM to LITE by @tinalenguyen in https://github.com/livekit/agents/pull/4748
* sarvam v3:stt and tts models by @dhruvladia-sarvam in https://github.com/livekit/agents/pull/4603
* export ToolContext by @theomonnom in https://github.com/livekit/agents/pull/4750
* fix: correct typo 'occured' to 'occurred' by @thecaptain789 in https://github.com/livekit/agents/pull/4751
* fix: correct typo 'dont't' to 'don't' by @thecaptain789 in https://github.com/livekit/agents/pull/4752
* Add jwt_token auth option for Neuphonic by @alexshelkov in https://github.com/livekit/agents/pull/4734
* fix get_event_loop on py3.14 by @theomonnom in https://github.com/livekit/agents/pull/4757
* feat: add missing OpenTelemetry GenAI attributes (gen_ai.provider.name, gen_ai.operation.name) by @Mr-Neutr0n in https://github.com/livekit/agents/pull/4759
* add input_details to SpeechHandle by @longcw in https://github.com/livekit/agents/pull/4701
* suppress tee aclose exception by @chenghao-mou in https://github.com/livekit/agents/pull/4766
* fix 3.14 syntax warning by @chenghao-mou in https://github.com/livekit/agents/pull/4763
* update issue template community link by @tinalenguyen in https://github.com/livekit/agents/pull/4772
* remove browser plugin by @theomonnom in https://github.com/livekit/agents/pull/4760
* write_int signed by @theomonnom in https://github.com/livekit/agents/pull/4776
* add lemonslice to video avatars section in README by @tinalenguyen in https://github.com/livekit/agents/pull/4778
* Added TruGen Avatar Plugin.  by @hari-trugen in https://github.com/livekit/agents/pull/4430
* Bump cryptography from 46.0.4 to 46.0.5 by @dependabot[bot] in https://github.com/livekit/agents/pull/4788
* Updated Speechmatics STT integration by @sam-s10s in https://github.com/livekit/agents/pull/4703
* Bump pillow from 12.1.0 to 12.1.1 by @dependabot[bot] in https://github.com/livekit/agents/pull/4791
* automatically reject jobs if the worker is draining/full by @theomonnom in https://github.com/livekit/agents/pull/4794
* add instruction on error-handling by @chenghao-mou in https://github.com/livekit/agents/pull/4790
* replace asyncio with inspect for iscoroutinefunction by @chenghao-mou in https://github.com/livekit/agents/pull/4789
* Add Hindi to the list of languages supported by the turn detector plu… by @darryncampbell in https://github.com/livekit/agents/pull/4797
* generate_reply accepts ChatMessage as user_input by @longcw in https://github.com/livekit/agents/pull/4808
* await interruption in _default_text_input_cb by @longcw in https://github.com/livekit/agents/pull/4807
* Add google stt voice activity timeout by @AhmadIbrahiim in https://github.com/livekit/agents/pull/4361
* fix: Update AvatarSession to use FormData format for expression model… by @CathyL0 in https://github.com/livekit/agents/pull/4799
* Inworld tts auto mode by @ianbbqzy in https://github.com/livekit/agents/pull/4655
* [inworld] add User-Agent and X-Request-Id for better traceability by @ianbbqzy in https://github.com/livekit/agents/pull/4784
* [inworld] support async timestamps mode by @ianbbqzy in https://github.com/livekit/agents/pull/4793
* ensure proc pool spawns processes for waiting jobs under high load by @theomonnom in https://github.com/livekit/agents/pull/4820
* (openai responses): update field names and image inputs by @tinalenguyen in https://github.com/livekit/agents/pull/4819
* chore(assemblyai): improve latency by default by @davidzhao in https://github.com/livekit/agents/pull/4827
* fix: a few defensive fixes to guard for exceptions by @davidzhao in https://github.com/livekit/agents/pull/4828
* Improve error handling and developer experience by @theomonnom in https://github.com/livekit/agents/pull/4826
* fix _jobs_waiting_for_process counter leak on cancellation by @theomonnom in https://github.com/livekit/agents/pull/4821
* fix cgroups v2 CPU quota parsing by @davidzhao in https://github.com/livekit/agents/pull/4844
* improve IPC pipeline reliability by @theomonnom in https://github.com/livekit/agents/pull/4825
* fix socket leak in supervised_proc._start() on failure by @theomonnom in https://github.com/livekit/agents/pull/4823
* fix: ChatContext.truncate dropping "developer" message by @davidzhao in https://github.com/livekit/agents/pull/4845
* fix: do not share resampler in tts fallback adapter by @davidzhao in https://github.com/livekit/agents/pull/4840
* fix _pending_assignments memory leak on assignment timeout by @theomonnom in https://github.com/livekit/agents/pull/4822
* fix launch_job send failure leaving executor orphaned by @theomonnom in https://github.com/livekit/agents/pull/4824
* fix(stt): correct log key mislabeled as "tts" in STT retry logs by @SezginKahraman in https://github.com/livekit/agents/pull/4830
* allow flexible recording options by @davidzhao in https://github.com/livekit/agents/pull/4758
* fix: clean up inference tasks after completion by @davidzhao in https://github.com/livekit/agents/pull/4841
* fix: prevent leak when channel task has been cancelled by @davidzhao in https://github.com/livekit/agents/pull/4848
* fix: call speech_handle.add_done_callback even when task is done by @davidzhao in https://github.com/livekit/agents/pull/4851
* upload logs to server even when session fails to start by @davidzhao in https://github.com/livekit/agents/pull/4846
* ensure exception is seen by all peers of tee by @davidzhao in https://github.com/livekit/agents/pull/4853
* add livekit-plugins-browser by @theomonnom in https://github.com/livekit/agents/pull/4859
* fix: ruff and mypy issues in livekit-plugins-browser by @theomonnom in https://github.com/livekit/agents/pull/4860
* fix: correct samples_per_channel in speaking rate stream by @theomonnom in https://github.com/livekit/agents/pull/4863
* fix: run on_session_end callback before internal session cleanup by @theomonnom in https://github.com/livekit/agents/pull/4862
* fix: STT fallback does not skip main_stream when recovering streams fail by @davidzhao in https://github.com/livekit/agents/pull/4835
* bump livekit sdk to 1.1.1 by @theomonnom in https://github.com/livekit/agents/pull/4865
* fix: prevent hang if participant never joins by @davidzhao in https://github.com/livekit/agents/pull/4864
* fix: prevent KeyboardInterrupt in child processes on Ctrl+C by @theomonnom in https://github.com/livekit/agents/pull/4866
* bump livekit sdk to 1.1.2 by @theomonnom in https://github.com/livekit/agents/pull/4867
* livekit-agents 1.4.2 by @theomonnom in https://github.com/livekit/agents/pull/4868
* browser plugin: add navigation RPCs + bump to 0.1.2 by @theomonnom in https://github.com/livekit/agents/pull/4870

## New Contributors
* @thecaptain789 made their first contribution in https://github.com/livekit/agents/pull/4751
* @Mr-Neutr0n made their first contribution in https://github.com/livekit/agents/pull/4759
* @hari-trugen made their first contribution in https://github.com/livekit/agents/pull/4430
* @dependabot[bot] made their first contribution in https://github.com/livekit/agents/pull/4788
* @darryncampbell made their first contribution in https://github.com/livekit/agents/pull/4797
* @AhmadIbrahiim made their first contribution in https://github.com/livekit/agents/pull/4361
* @ianbbqzy made their first contribution in https://github.com/livekit/agents/pull/4655
* @SezginKahraman made their first contribution in https://github.com/livekit/agents/pull/4830

**Full Changelog**: https://github.com/livekit/agents/compare/livekit-agents@1.4.0...livekit-agents@1.4.2

[View on GitHub](https://github.com/livekit/agents/releases/tag/livekit-agents%401.4.2)

---

## browser-v0.1.3: Browser v0.1.3
**Published:** 2026-02-16
**Pre-release**

CEF native binaries for livekit-browser v0.1.3. Supports Python 3.12-3.14 on macOS arm64, Linux x64, and Linux arm64.

[View on GitHub](https://github.com/livekit/agents/releases/tag/browser-v0.1.3)

---

## browser-v0.1.2: Browser v0.1.2
**Published:** 2026-02-16
**Pre-release**

CEF native binaries for livekit-browser v0.1.2. Supports Python 3.12-3.14 on macOS arm64, Linux x64, and Linux arm64.

[View on GitHub](https://github.com/livekit/agents/releases/tag/browser-v0.1.2)

---

## livekit-agents@1.4.0: livekit-agents@1.4.0
**Published:** 2026-02-06

## Python 3.14 Support & Python 3.9 Dropped

This release adds **Python 3.14 support** and **drops Python 3.9**. The minimum supported version is now **Python 3.10**.

## Tool Improvements

Tools and toolsets now have **stable unique IDs**, making it possible to reference and filter tools programmatically. Changes to agent configuration (instructions, tools) are now tracked in conversation history via `AgentConfigUpdate`.

## `LLMStream.collect()` API

A new `LLMStream.collect()` API makes it significantly easier to use LLMs outside of `AgentSession`. You can now call an LLM, collect the full response, and execute tool calls with a straightforward API — useful for background tasks, pre-processing, or any workflow where you need LLM capabilities without the full voice agent pipeline.

```python
from livekit.agents import llm

response = await my_llm.chat(chat_ctx=ctx, tools=tools).collect()

for tc in response.tool_calls:
    result = await llm.execute_function_call(tc, tool_ctx)
    ctx.insert(result.fnc_call)
    if result.fnc_call_out:
        ctx.insert(result.fnc_call_out)
```

## Manual Turn Detection for Realtime Models

Realtime models now support `commit_user_turn`, enabling `turn_detection="manual"` mode. This gives you full control over when user turns are committed — useful for push-to-talk interfaces or scenarios where automatic VAD-based turn detection isn't ideal.

```python
@ctx.room.local_participant.register_rpc_method("end_turn")
async def end_turn(data: rtc.RpcInvocationData):
    session.input.set_audio_enabled(False)
    session.commit_user_turn(
        transcript_timeout=10.0,
        stt_flush_duration=2.0,
    )
```

## Job Migration on Reconnection

When the agent server temporarily loses connection and reconnects, **active jobs are now automatically migrated** rather than being dropped. This significantly improves reliability during transient network issues.

## False Interruption Fix

Fixed a bug where late end-of-speech events could trigger duplicate false interruption timers, causing the agent to incorrectly stop speaking. The agent now properly deduplicates these events and tracks STT completion state more reliably.

### New Providers & Plugins

- **xAI Responses LLM** — Use xAI's Responses API via `xai.responses.LLM()`
- **Azure OpenAI Responses** — Azure-hosted Responses API via `azure.responses.LLM()`, with support for deployments and Azure auth
- **Camb.ai TTS** — New TTS plugin powered by the MARS model family (mars-flash, mars-pro, mars-instruct), with voice selection, language control, and style instructions
- **Avatario Avatar** — Virtual avatar plugin with session management and API client

## What's Changed
* feat(azure/stt): TrueText post processing option added to STTOptions by @rafallezanko in https://github.com/livekit/agents/pull/4557
* chore(README): remove STT and LLM API key configuration from LemonSlice example as not needed. by @codeSTACKr in https://github.com/livekit/agents/pull/4589
* fix: Add thread-safe initialization to _DefaultLoadCalc singleton by @darshankparmar in https://github.com/livekit/agents/pull/4585
* add missing plugins to dependencies by @tinalenguyen in https://github.com/livekit/agents/pull/4593
* _setup_cloud_tracer still overrides TracerProviders due to checking the wrong base class by @hudson-worden in https://github.com/livekit/agents/pull/4584
* fix(google): add thought_signature support for Gemini 2.5 models by @gdoermann in https://github.com/livekit/agents/pull/4595
* remove shortcut inference STT model name by @longcw in https://github.com/livekit/agents/pull/4594
* Increase read_bufsize in minimax tts plugin by @jose-speak in https://github.com/livekit/agents/pull/4590
* refactor(rtzr): FlushSentinel-based segment control and type safety improvements by @kimdwkimdw in https://github.com/livekit/agents/pull/4565
* improve EndCallTool by @longcw in https://github.com/livekit/agents/pull/4563
* Fix: Add 'required' field to function_tool schema for Groq compatibility by @VinayJogani14 in https://github.com/livekit/agents/pull/4613
* fix: avoid modifying original raw tool description by @davidzhao in https://github.com/livekit/agents/pull/4616
* continue instead of return in InferenceProcExecutor loop by @chenghao-mou in https://github.com/livekit/agents/pull/4612
* add xai responses llm by @tinalenguyen in https://github.com/livekit/agents/pull/4618
* move xAI tools to separate file by @tinalenguyen in https://github.com/livekit/agents/pull/4624
* (xAI): backward compatibility for tools by @tinalenguyen in https://github.com/livekit/agents/pull/4625
* update inference models to match the latest by @davidzhao in https://github.com/livekit/agents/pull/4597
* AssemblyAI added EU streaming endpoint option by @ftsef in https://github.com/livekit/agents/pull/4571
* feat: Add Camb.ai TTS plugin by @eRuaro in https://github.com/livekit/agents/pull/4442
* prevent duplicate false interruption due to late end of speech by @chenghao-mou in https://github.com/livekit/agents/pull/4621
* feat: add customization bithuman gpu avatar endpoint handling by @CathyL0 in https://github.com/livekit/agents/pull/4390
* plugin/liveavatar implement sandbox on liveavatar by @arthurnumen in https://github.com/livekit/agents/pull/4635
* add asyncai to pyproject by @tinalenguyen in https://github.com/livekit/agents/pull/4636
* feat: avatario avatar plugin by @Saksham209 in https://github.com/livekit/agents/pull/4114
* add azure openai responses by @tinalenguyen in https://github.com/livekit/agents/pull/4619
* (openai realtime): add truncation param by @tinalenguyen in https://github.com/livekit/agents/pull/4642
* fix: 11Labs Scribe v2 model not working with EOT prediction model by @Ludobaka in https://github.com/livekit/agents/pull/4601
* (taskgroup): support on_complete callback functions by @tinalenguyen in https://github.com/livekit/agents/pull/4628
* add `id` to tools  by @theomonnom in https://github.com/livekit/agents/pull/4653
* allow 499 retry by @chenghao-mou in https://github.com/livekit/agents/pull/4637
* AGT-2474: add commit user turn support for realtime models by @chenghao-mou in https://github.com/livekit/agents/pull/4622
* fix(liveavatar): emit playback_finished on AudioSegmentEnd by @MSameerAbbas in https://github.com/livekit/agents/pull/4669
* add `AgentConfigUpdate` & initial judges by @theomonnom in https://github.com/livekit/agents/pull/4547
* fix tests & ruff by @theomonnom in https://github.com/livekit/agents/pull/4672
* (minimax): add language boost param by @tinalenguyen in https://github.com/livekit/agents/pull/4667
* remove accidentally committed files  by @theomonnom in https://github.com/livekit/agents/pull/4673
* fix duplicated openai realtime remote content by @longcw in https://github.com/livekit/agents/pull/4657
* use text streams & custom rpc logic by @theomonnom in https://github.com/livekit/agents/pull/4677
* remove chat_ctx size limit by @theomonnom in https://github.com/livekit/agents/pull/4678
* clean up metrics export from traces by @davidzhao in https://github.com/livekit/agents/pull/4679
* `LLMStream.collect` API & external easier tool executions by @theomonnom in https://github.com/livekit/agents/pull/4680
* update openai responses default model by @tinalenguyen in https://github.com/livekit/agents/pull/4681
* fix(google): improve error message for model/API mismatch in Realtime API by @cdutr in https://github.com/livekit/agents/pull/4611
* fix keyterm in Deepgram by @chenghao-mou in https://github.com/livekit/agents/pull/4684
* Expose ws close code and error messages by @chenghao-mou in https://github.com/livekit/agents/pull/4683
* fix: improve handling of 499 status code by @davidzhao in https://github.com/livekit/agents/pull/4685
* support wrapped tools with a warning message by @longcw in https://github.com/livekit/agents/pull/4674
* fix(transcription): prevent stale synchronizer impls (#4486) by @furious-luke in https://github.com/livekit/agents/pull/4686
* Add rtzr plugin to optional dependencies by @zach-iee in https://github.com/livekit/agents/pull/4631
* feat(langgraph): add custom stream mode support in LangChain LLMAdapter by @keenranger in https://github.com/livekit/agents/pull/4511
* Add room deletion timeout and cancellation by @chenghao-mou in https://github.com/livekit/agents/pull/4638
* add TaskCompletedEvent import by @tinalenguyen in https://github.com/livekit/agents/pull/4688
* prevent tool cancellation when AgentTask is called inside it by @longcw in https://github.com/livekit/agents/pull/4586
* fix gemini live tool execution interrupted by generation_complete event by @longcw in https://github.com/livekit/agents/pull/4699
* add STT usage for google by @chenghao-mou in https://github.com/livekit/agents/pull/4599
* fix: commit user turn with STT and realtime by @chenghao-mou in https://github.com/livekit/agents/pull/4663
* add exclude_config_update to ChatContext copy by @longcw in https://github.com/livekit/agents/pull/4700
* add require_confirmation param for built-in tasks by @tinalenguyen in https://github.com/livekit/agents/pull/4698
* Fix wrong "timestamp" parameter in livekit-plugins-spitch stt.py by @pabloFuente in https://github.com/livekit/agents/pull/4702
* Update readme and examples to use deepgram nova-3 by @bcherry in https://github.com/livekit/agents/pull/4697
* set exclude_config_update by @longcw in https://github.com/livekit/agents/pull/4709
* Restore Python 3.14 support by updating livekit-blingfire to 1.1 by @Abivarman123 in https://github.com/livekit/agents/pull/4710
* add ChatContext.messages() by @theomonnom in https://github.com/livekit/agents/pull/4712
* migrate jobs on reconnection by @theomonnom in https://github.com/livekit/agents/pull/4711
* use ChatMessage.messages() where applicable by @theomonnom in https://github.com/livekit/agents/pull/4713
* chore(docs): ditch the v0 docs and promote v1 docs to main path by @rektdeckard in https://github.com/livekit/agents/pull/4695
* filter tools by id by @tinalenguyen in https://github.com/livekit/agents/pull/4723
* support python 3.14 by @theomonnom in https://github.com/livekit/agents/pull/4727
* Fix: Added stt lang parsing and tts voice parsing to the constructors by @adrian-cowham in https://github.com/livekit/agents/pull/4726
* fix (liveavatar): restore interruption handling and track avatar speaking state by @tinalenguyen in https://github.com/livekit/agents/pull/4725
* update padding warning message and silence subsequent ones by @chenghao-mou in https://github.com/livekit/agents/pull/4733
* fix: Add default google tts model selection for backward compatibility by @chenghao-mou in https://github.com/livekit/agents/pull/4731
* fix uv lock file & drop python 3.9 support & upgrade dependencies by @theomonnom in https://github.com/livekit/agents/pull/4728
* automatically close openai client  by @theomonnom in https://github.com/livekit/agents/pull/4735
* update gitignore by @theomonnom in https://github.com/livekit/agents/pull/4737
* fix speaking_rate inference by @theomonnom in https://github.com/livekit/agents/pull/4738
* livekit-agents 1.4.0 by @theomonnom in https://github.com/livekit/agents/pull/4739

## New Contributors
* @codeSTACKr made their first contribution in https://github.com/livekit/agents/pull/4589
* @hudson-worden made their first contribution in https://github.com/livekit/agents/pull/4584
* @gdoermann made their first contribution in https://github.com/livekit/agents/pull/4595
* @jose-speak made their first contribution in https://github.com/livekit/agents/pull/4590
* @VinayJogani14 made their first contribution in https://github.com/livekit/agents/pull/4613
* @ftsef made their first contribution in https://github.com/livekit/agents/pull/4571
* @eRuaro made their first contribution in https://github.com/livekit/agents/pull/4442
* @arthurnumen made their first contribution in https://github.com/livekit/agents/pull/4635
* @Saksham209 made their first contribution in https://github.com/livekit/agents/pull/4114
* @Ludobaka made their first contribution in https://github.com/livekit/agents/pull/4601
* @cdutr made their first contribution in https://github.com/livekit/agents/pull/4611
* @keenranger made their first contribution in https://github.com/livekit/agents/pull/4511
* @Abivarman123 made their first contribution in https://github.com/livekit/agents/pull/4710

**Full Changelog**: https://github.com/livekit/agents/compare/livekit-agents@1.3.12...livekit-agents@1.4.0

[View on GitHub](https://github.com/livekit/agents/releases/tag/livekit-agents%401.4.0)

---

## livekit-agents@1.3.12: livekit-agents@1.3.12
**Published:** 2026-01-21

## What's Changed
* improve text mode CLI rendering by @theomonnom in https://github.com/livekit/agents/pull/4522
* fix `Worker.aclose` raising RuntimeError  by @theomonnom in https://github.com/livekit/agents/pull/4523
* better cli rendering for audio by @theomonnom in https://github.com/livekit/agents/pull/4524
* fix frame capture order and add playback start callback in console mode by @chenghao-mou in https://github.com/livekit/agents/pull/4516
* Add Connector to default participant kinds by @cnderrauber in https://github.com/livekit/agents/pull/4526
* add support for language detection for assembly ai by @chenghao-mou in https://github.com/livekit/agents/pull/4527
* Support static context in integration with langchain by @benlangfeld in https://github.com/livekit/agents/pull/4504
* feat(google): add warnings when system messages are dropped in Gemini realtime model by @dhruvnigam93 in https://github.com/livekit/agents/pull/4513
* chore: change deprecated cartesia voice id by @davidzhao in https://github.com/livekit/agents/pull/4528
* #4481 Added Opus and PCM encoding to ElevenLabs TTS by @rafallezanko in https://github.com/livekit/agents/pull/4525
* interrupt the same speech handle by @chenghao-mou in https://github.com/livekit/agents/pull/4536
* pin livekit-rtc version by @theomonnom in https://github.com/livekit/agents/pull/4531
* fix(elevenlabs/stt): allow specifying scribe_v2 non-realtime model by @bml1g12 in https://github.com/livekit/agents/pull/4515
* add reasoning param for openai responses LLM by @tinalenguyen in https://github.com/livekit/agents/pull/4548
* Defensive fixes by @chenghao-mou in https://github.com/livekit/agents/pull/4546
* LemonSlice Plugin by @jp-lemon in https://github.com/livekit/agents/pull/4539
* feat (google STT): support profanity filter by @tinalenguyen in https://github.com/livekit/agents/pull/4573
* fix(baseten): correct metadata and response field names for STT by @toubatbrian in https://github.com/livekit/agents/pull/4572
* drop frames when the ConsoleAudioInput is detached by @longcw in https://github.com/livekit/agents/pull/4576
* fix audio recording in console mode by @longcw in https://github.com/livekit/agents/pull/4575
* Chatterbox model support by @plangary in https://github.com/livekit/agents/pull/4541
* Inworld websocket improvements by @cshape in https://github.com/livekit/agents/pull/4533
* fix(deepgram): expose close code and reason on unexpected disconnects by @vadimatmurphy in https://github.com/livekit/agents/pull/4569
* playback started call for DataStreamAudioOutput and QueueAudioOutput by @chenghao-mou in https://github.com/livekit/agents/pull/4570
* feat(azure): add lexicon_uri option to TTS by @zach-iee in https://github.com/livekit/agents/pull/4485
* feat(tts): integrate AsyncAI TTS engine into livekit by @ashotbagh in https://github.com/livekit/agents/pull/3596
* Simplismart Integration in Livekit by @Tushar-ml in https://github.com/livekit/agents/pull/4349
* handle invalid bytes error by @chenghao-mou in https://github.com/livekit/agents/pull/4579
* Fixes #4388: Correct transcription_delay metric calculation in STT turn detec… by @devbyteai in https://github.com/livekit/agents/pull/4396
* fix(mcp): Error message based on text attribute instead of str(part) by @rafallezanko in https://github.com/livekit/agents/pull/4582
* livekit-agents 1.3.12 by @theomonnom in https://github.com/livekit/agents/pull/4583

## New Contributors
* @cnderrauber made their first contribution in https://github.com/livekit/agents/pull/4526
* @benlangfeld made their first contribution in https://github.com/livekit/agents/pull/4504
* @dhruvnigam93 made their first contribution in https://github.com/livekit/agents/pull/4513
* @jp-lemon made their first contribution in https://github.com/livekit/agents/pull/4539
* @vadimatmurphy made their first contribution in https://github.com/livekit/agents/pull/4569
* @zach-iee made their first contribution in https://github.com/livekit/agents/pull/4485
* @ashotbagh made their first contribution in https://github.com/livekit/agents/pull/3596
* @Tushar-ml made their first contribution in https://github.com/livekit/agents/pull/4349
* @devbyteai made their first contribution in https://github.com/livekit/agents/pull/4396

**Full Changelog**: https://github.com/livekit/agents/compare/livekit-agents@1.3.11...livekit-agents@1.3.12

[View on GitHub](https://github.com/livekit/agents/releases/tag/livekit-agents%401.3.12)

---

## livekit-agents@1.3.11: livekit-agents@1.3.11
**Published:** 2026-01-14

## What's Changed
* Add allowed_tools and transport_type parameters to MCPServerHTTP by @wasaybaig201 in https://github.com/livekit/agents/pull/4365
* better `transport_type` type in MCPServer by @theomonnom in https://github.com/livekit/agents/pull/4375
* fix typo: double the - in multiple livekit-plugin providers by @ChristianBernhard in https://github.com/livekit/agents/pull/4358
* feat(AWS STT): use ChainedIdentityResolver by @itskyf in https://github.com/livekit/agents/pull/4356
* support next_in_chain for RoomIO text output by @longcw in https://github.com/livekit/agents/pull/4353
* standardize Tool interface by @longcw in https://github.com/livekit/agents/pull/4368
* add tests for function tool parsing and execution by @longcw in https://github.com/livekit/agents/pull/4384
* add EndCallTool by @longcw in https://github.com/livekit/agents/pull/4377
* chore(google): update doc string to reflect default realtime models by @davidzhao in https://github.com/livekit/agents/pull/4398
* fix AttributeError in NVIDIA Riva STT by @gau-nernst in https://github.com/livekit/agents/pull/4391
* fix aws credentials when using env vals by @chenghao-mou in https://github.com/livekit/agents/pull/4403
* fix (gemini streaming tts): change default audio encoding and voice  by @tinalenguyen in https://github.com/livekit/agents/pull/4393
* fix (mistral-ai): add flexibility for timestamps  by @tinalenguyen in https://github.com/livekit/agents/pull/4404
* remove shutdown models from google gemini live  by @tinalenguyen in https://github.com/livekit/agents/pull/4421
* update groq tts models, voices, and defaults by @tinalenguyen in https://github.com/livekit/agents/pull/4422
* fix (google stt): set enable_word_time_offsets to False for chirp 3 by @tinalenguyen in https://github.com/livekit/agents/pull/4420
* fix: return 503 health check when worker fails to connect to LiveKit by @rusg77 in https://github.com/livekit/agents/pull/4419
* Add retrieval config support for google LLM by @chenghao-mou in https://github.com/livekit/agents/pull/4408
* allow pushing frames to VAD when agent speech is uninterruptible by @chenghao-mou in https://github.com/livekit/agents/pull/4418
* Add extra comments about Google model deprecation by @chenghao-mou in https://github.com/livekit/agents/pull/4424
* fix (gemini filesearch): require only filestore names by @tinalenguyen in https://github.com/livekit/agents/pull/4428
* update docker dependencies by @chenghao-mou in https://github.com/livekit/agents/pull/4431
* chore: minor fixup of console room name by @davidzhao in https://github.com/livekit/agents/pull/4433
* Inference: Improved support for mid session TTS updates by @adrian-cowham in https://github.com/livekit/agents/pull/4412
* fix: acquire lock in _DefaultLoadCalc.get_load() to prevent race condition by @martin-purplefish in https://github.com/livekit/agents/pull/4435
* fix vad rnn state by @theomonnom in https://github.com/livekit/agents/pull/4437
* restore old behavior by @chenghao-mou in https://github.com/livekit/agents/pull/4434
* fix: avoid double RoomIO.aclose during shutdown by @darshankparmar in https://github.com/livekit/agents/pull/4446
* add connect CLI command by @tinalenguyen in https://github.com/livekit/agents/pull/4452
* fix function call created_at by @longcw in https://github.com/livekit/agents/pull/4453
* Update STT tests and add batch recognition flag by @chenghao-mou in https://github.com/livekit/agents/pull/4425
* allow tests on external PRs when triggered by members by @chenghao-mou in https://github.com/livekit/agents/pull/4456
* Adding model query param to the STT and TTS websocket connection string. by @adrian-cowham in https://github.com/livekit/agents/pull/4457
* refactor connect CLI command by @tinalenguyen in https://github.com/livekit/agents/pull/4458
* OpenAI Responses API Plugin by @tinalenguyen in https://github.com/livekit/agents/pull/4192
* fix transcription truncate when agent is interrupted in console mode by @longcw in https://github.com/livekit/agents/pull/4473
* feat(rtzr): add keyword boosting to streaming STT by @lalq in https://github.com/livekit/agents/pull/4405
* Revise AWS Plugin README for accuracy and clarity by @guiruggiero in https://github.com/livekit/agents/pull/4468
* close log_handler when process initialize failed by @longcw in https://github.com/livekit/agents/pull/4472
* feat(deepgram): make vad_events configurable by @vchulski in https://github.com/livekit/agents/pull/4476
* Enables continuous language ID for Azure STT by @MSameerAbbas in https://github.com/livekit/agents/pull/4479
* fix: OpenAI realtime division by zero by @darshankparmar in https://github.com/livekit/agents/pull/4490
* update avatar example and openai readmes by @tinalenguyen in https://github.com/livekit/agents/pull/4495
* type cleanup, include all plugins into type checker by @davidzhao in https://github.com/livekit/agents/pull/4491
* agents.md and claude.md by @davidzhao in https://github.com/livekit/agents/pull/4493
* update examples to use LK Inference by @davidzhao in https://github.com/livekit/agents/pull/4494
* #4500 Fix for Race condition in _send_kill_signal: ValueError: process object is closed after SIGUSR1 by @rafallezanko in https://github.com/livekit/agents/pull/4501
* support diarization for soniox stt by @longcw in https://github.com/livekit/agents/pull/4510
* fix 11labs tts hang after update_options in tool call by @longcw in https://github.com/livekit/agents/pull/4499
* AGT-2316: refine timestamps in spans and recording alignment by @chenghao-mou in https://github.com/livekit/agents/pull/4131

## New Contributors
* @wasaybaig201 made their first contribution in https://github.com/livekit/agents/pull/4365
* @ChristianBernhard made their first contribution in https://github.com/livekit/agents/pull/4358
* @gau-nernst made their first contribution in https://github.com/livekit/agents/pull/4391
* @rusg77 made their first contribution in https://github.com/livekit/agents/pull/4419
* @lalq made their first contribution in https://github.com/livekit/agents/pull/4405
* @guiruggiero made their first contribution in https://github.com/livekit/agents/pull/4468
* @vchulski made their first contribution in https://github.com/livekit/agents/pull/4476
* @MSameerAbbas made their first contribution in https://github.com/livekit/agents/pull/4479
* @rafallezanko made their first contribution in https://github.com/livekit/agents/pull/4501

**Full Changelog**: https://github.com/livekit/agents/compare/livekit-agents@1.3.10...livekit-agents@1.3.11

[View on GitHub](https://github.com/livekit/agents/releases/tag/livekit-agents%401.3.11)

---

## livekit-agents@1.3.10: livekit-agents@1.3.10
**Published:** 2025-12-23

## What's Changed
* fix(google): improve handling of empty responses by @davidzhao in https://github.com/livekit/agents/pull/4330
* Add support for audio frame processor by @lukasIO in https://github.com/livekit/agents/pull/4145
* Update doc for min_endpointing_delay by @MonkeyLeeT in https://github.com/livekit/agents/pull/4327
* force interruption when closing the session by @longcw in https://github.com/livekit/agents/pull/4346
* add ProviderTool & support built-in tools for xai & gemini realtime by @theomonnom in https://github.com/livekit/agents/pull/4344
* fix dynamic tool updates in llm_node by @davidzhao in https://github.com/livekit/agents/pull/4355
* Proper support for V1 models for Google STT by @chenghao-mou in https://github.com/livekit/agents/pull/4338
* Add Grok example by @ShayneP in https://github.com/livekit/agents/pull/4363
* allow aws realtime to accept str tool results by @tinalenguyen in https://github.com/livekit/agents/pull/4364
* (gemini realtime) check for vertexai for api version by @tinalenguyen in https://github.com/livekit/agents/pull/4366
* Enable Soniox STT turn detection & metrics by @matejmarinko-soniox in https://github.com/livekit/agents/pull/4332

### Provider tools

This release brings the ability to use tools that are specific to model providers with [provider tools](https://docs.livekit.io/agents/logic/tools/#provider-tools). You can now mix & match function tools and provider tools in your agent by specifying `Agent(tools=[..])`.

For those that were using the experimental `_gemini_tools` parameter with Google LLMs, that experimental parameter has been removed in favor of provider tools. See usage example [here](https://docs.livekit.io/agents/models/llm/plugins/gemini/#provider-tools).

## New Contributors
* @MonkeyLeeT made their first contribution in https://github.com/livekit/agents/pull/4327

**Full Changelog**: https://github.com/livekit/agents/compare/livekit-agents@1.3.9...livekit-agents@1.3.10

[View on GitHub](https://github.com/livekit/agents/releases/tag/livekit-agents%401.3.10)

---

## livekit-agents@1.3.9: livekit-agents@1.3.9
**Published:** 2025-12-19

## What's Changed
* chore(xai): update voice names according to docs by @davidzhao in https://github.com/livekit/agents/pull/4295
* Add local dev commands for linking to rtc-sdk by @lukasIO in https://github.com/livekit/agents/pull/4258
* Ensure makefile checks for livekit_lib_path by @lukasIO in https://github.com/livekit/agents/pull/4298
* feat(gemini3) : Add Gemini 3 support with thinking_level and thought_signature by @varghesepaul in https://github.com/livekit/agents/pull/4027
* fix list mutation during iteration by @theomonnom in https://github.com/livekit/agents/pull/4304
* add gemini 3 flash model by @tinalenguyen in https://github.com/livekit/agents/pull/4301
* Websockets improvement by @cshape in https://github.com/livekit/agents/pull/4303
* Allow for Cartesia TTS language auto-detection by @yuyuma in https://github.com/livekit/agents/pull/4300
* Add Amazon Nova 2.0 Sonic Support with Text Input and Enhanced Features by @kachenjr in https://github.com/livekit/agents/pull/4176
* fix dynamic FieldInfo for pydantic 2.12 by @longcw in https://github.com/livekit/agents/pull/4290
* re-export TurnDetection for xAI by @tinalenguyen in https://github.com/livekit/agents/pull/4306
* fix commit_user_turn when last_final_transcript_time is None by @longcw in https://github.com/livekit/agents/pull/4308
* feat(soniox): add language_hints_strict option for STT by @cateet in https://github.com/livekit/agents/pull/4281
* feat(google-tts): add prompt to normal synthesize for Gemini TTS by @NXV5111 in https://github.com/livekit/agents/pull/4208
* Adding extra content to OpenAI LLM. Improving function call grouping. by @russellmartin-livekit in https://github.com/livekit/agents/pull/4170
* feat(gemini3) use low latency thinking_level by default for gemini 3 models by @pushkar-nurix in https://github.com/livekit/agents/pull/4311
* fix handoff to Realtime model with existing session context by @davidzhao in https://github.com/livekit/agents/pull/4310
* tts metrics update by @dhruvladia-sarvam in https://github.com/livekit/agents/pull/4117
* AGT-2302: add aligned_transcript to STT by @chenghao-mou in https://github.com/livekit/agents/pull/4155
* Minor readme doc fixes by @kachenjr in https://github.com/livekit/agents/pull/4320
* vad enabled by @dhruvladia-sarvam in https://github.com/livekit/agents/pull/4321
* handle exceptions in task_results by @tinalenguyen in https://github.com/livekit/agents/pull/4323
* add `livekit-durable` functions by @theomonnom in https://github.com/livekit/agents/pull/4272
* fix py3.10-py3.12 &`livekit-durable` cibw by @theomonnom in https://github.com/livekit/agents/pull/4324
* stringify cartesia error to be pickleable by @tinalenguyen in https://github.com/livekit/agents/pull/4328
* livekit-agents 1.3.9 by @theomonnom in https://github.com/livekit/agents/pull/4329

## New Contributors
* @varghesepaul made their first contribution in https://github.com/livekit/agents/pull/4027
* @NXV5111 made their first contribution in https://github.com/livekit/agents/pull/4208
* @russellmartin-livekit made their first contribution in https://github.com/livekit/agents/pull/4170
* @dhruvladia-sarvam made their first contribution in https://github.com/livekit/agents/pull/4117

**Full Changelog**: https://github.com/livekit/agents/compare/livekit-agents@1.3.8...livekit-agents@1.3.9

[View on GitHub](https://github.com/livekit/agents/releases/tag/livekit-agents%401.3.9)

---

## livekit-agents@1.3.8: livekit-agents@1.3.8
**Published:** 2025-12-17

## What's Changed
* add init for xai by @tinalenguyen in https://github.com/livekit/agents/pull/4286
* fix(xai): list openai as a dependency, fix exports by @davidzhao in https://github.com/livekit/agents/pull/4287
* fix(xai): a few more exports by @davidzhao in https://github.com/livekit/agents/pull/4288
* Update default model by @gyang-xai in https://github.com/livekit/agents/pull/4289
* chore(xai): list supported voices by @davidzhao in https://github.com/livekit/agents/pull/4292

## New Contributors
* @gyang-xai made their first contribution in https://github.com/livekit/agents/pull/4289

**Full Changelog**: https://github.com/livekit/agents/compare/livekit-agents@1.3.7...livekit-agents@1.3.8

[View on GitHub](https://github.com/livekit/agents/releases/tag/livekit-agents%401.3.8)

---

## livekit-agents@1.3.7: livekit-agents@1.3.7
**Published:** 2025-12-16

## What's Changed
* fix OTEL types by @theomonnom in https://github.com/livekit/agents/pull/4164
* feat(background-audio): add several builtin audio clips by @rektdeckard in https://github.com/livekit/agents/pull/4165
* fix gemini function tool parameter enum typing by @tinalenguyen in https://github.com/livekit/agents/pull/4166
* use inference gateway in the readme by @theomonnom in https://github.com/livekit/agents/pull/3665
* update warm transfer readme and extra instructions by @longcw in https://github.com/livekit/agents/pull/4168
* terminate on `JobRequest.reject` by @theomonnom in https://github.com/livekit/agents/pull/4172
* add terminate argument to JobRequest.reject by @theomonnom in https://github.com/livekit/agents/pull/4173
* update documentation link for LiveAvatar by @tinalenguyen in https://github.com/livekit/agents/pull/4178
* fix logging style format is not respected by @longcw in https://github.com/livekit/agents/pull/4169
* fix _on_reject when no answer by @longcw in https://github.com/livekit/agents/pull/4180
* expose elevenlabs TTS error message by @longcw in https://github.com/livekit/agents/pull/4182
* fix(aws): Handle nested schema in Nova Sonic tool parameter extraction by @somoore in https://github.com/livekit/agents/pull/4177
* Restore otel chat message by @chenghao-mou in https://github.com/livekit/agents/pull/4118
* fix record.exc_info is not pickable when using LogQueueHandler by @longcw in https://github.com/livekit/agents/pull/4185
* Feat/mistralai models update by @fabitokki in https://github.com/livekit/agents/pull/4156
* feat(rime): expand update_options to accept all TTS parameters by @gokuljs in https://github.com/livekit/agents/pull/4095
* Fallback API for Inference by @adrian-cowham in https://github.com/livekit/agents/pull/4099
* Add LiveAvatar Stop Session API Call + README Fix by @tinalenguyen in https://github.com/livekit/agents/pull/4195
* feat(google): add streaming support for Gemini TTS models by @plumber0 in https://github.com/livekit/agents/pull/4189
* fix watchfiles prevent agent prcoess exit on sigterm by @longcw in https://github.com/livekit/agents/pull/4194
* fix race condition when stop background audio play handle by @longcw in https://github.com/livekit/agents/pull/4197
* Inference: Rename fallback model name param by @adrian-cowham in https://github.com/livekit/agents/pull/4202
* fix inworld punctuation handling by @cshape in https://github.com/livekit/agents/pull/4215
* ensure playback_segments_count is consistent in the audio output chain by @longcw in https://github.com/livekit/agents/pull/4211
* clear _q_updated right after await to avoid race conditions by @longcw in https://github.com/livekit/agents/pull/4209
* fix blocked send task in liveavatar plugin by @tinalenguyen in https://github.com/livekit/agents/pull/4214
* feat(warm-transfer): add sip_number parameter for outbound caller ID by @Hormold in https://github.com/livekit/agents/pull/4216
* add keep alive task for liveavatar plugin by @tinalenguyen in https://github.com/livekit/agents/pull/4231
* turn-detector: remove english model from readme by @lwestn in https://github.com/livekit/agents/pull/4233
* feature: GPT-5.2 support by @pushkar-nurix in https://github.com/livekit/agents/pull/4235
* disable interruptions for agent greeting by @hiroshihorie in https://github.com/livekit/agents/pull/4223
* AGT-2328: negative threshold in silero by @chenghao-mou in https://github.com/livekit/agents/pull/4228
* fix: image token usage not being tracked for OpenAI realtime models by @GigaDroid in https://github.com/livekit/agents/pull/4238
* check for type key in _ensure_strict_json_schema by @tinalenguyen in https://github.com/livekit/agents/pull/4236
* fix(openai): migrate realtime STT to GA API by @Hormold in https://github.com/livekit/agents/pull/4232
* fix(google): handle content blocking and generation failures by @davidzhao in https://github.com/livekit/agents/pull/4249
* feat(google): update default realtime model to gemini-2.5 12-2025 by @davidzhao in https://github.com/livekit/agents/pull/4248
* fix generate_reply timeout for gemini by @longcw in https://github.com/livekit/agents/pull/4237
* fix: correct sample count calculation in AudioByteStream.flush() for multi-channel audio by @darshankparmar in https://github.com/livekit/agents/pull/4245
* Fix AudioByteStream buffer slicing performance issue by @darshankparmar in https://github.com/livekit/agents/pull/4247
* AGT-2317: wait for user silence before speaking by @chenghao-mou in https://github.com/livekit/agents/pull/4102
* Add Proactive Session Recycling for Nova Sonic resume by @kachenjr in https://github.com/livekit/agents/pull/4250
* feat(tts): Support dynamic base URL updates via update_options in Rime TTS plugin by @gokuljs in https://github.com/livekit/agents/pull/4257
* Auto assign reviewer for internal PRs by @chenghao-mou in https://github.com/livekit/agents/pull/4230
* fix(aws): set aws_credentials_identity_resolver as value instead of tuple by @davidzhao in https://github.com/livekit/agents/pull/4259
* pybind fix path by @theomonnom in https://github.com/livekit/agents/pull/4260
* blingfire: add version constraints for pybind by @jjmaldonis in https://github.com/livekit/agents/pull/3913
* Revert "pybind fix path" by @theomonnom in https://github.com/livekit/agents/pull/4261
* unnecessary pybind11 version constraints by @theomonnom in https://github.com/livekit/agents/pull/4262
* fix team name typo by @theomonnom in https://github.com/livekit/agents/pull/4266
* chore: add `nvidia` optional dependency by @davidzhao in https://github.com/livekit/agents/pull/4264
* livekit-blingfire 1.1.0 & add python 3.14 support by @theomonnom in https://github.com/livekit/agents/pull/4265
* add interruption timeout to SpeechHandle by @longcw in https://github.com/livekit/agents/pull/4218
* chore: skip summarize test when OpenAI API key is missing by @davidzhao in https://github.com/livekit/agents/pull/4278
* catch client response error by @chenghao-mou in https://github.com/livekit/agents/pull/4254
* fix gemini realtime generate_reply during response is playing by @longcw in https://github.com/livekit/agents/pull/4273
* add pause support for ConsoleAudioOutput by @longcw in https://github.com/livekit/agents/pull/4251
* xAI plugin by @tinalenguyen in https://github.com/livekit/agents/pull/4284

## New Contributors
* @somoore made their first contribution in https://github.com/livekit/agents/pull/4177
* @plumber0 made their first contribution in https://github.com/livekit/agents/pull/4189
* @pushkar-nurix made their first contribution in https://github.com/livekit/agents/pull/4235
* @hiroshihorie made their first contribution in https://github.com/livekit/agents/pull/4223
* @GigaDroid made their first contribution in https://github.com/livekit/agents/pull/4238
* @darshankparmar made their first contribution in https://github.com/livekit/agents/pull/4245

**Full Changelog**: https://github.com/livekit/agents/compare/livekit-agents@1.3.6...livekit-agents@1.3.7

[View on GitHub](https://github.com/livekit/agents/releases/tag/livekit-agents%401.3.7)

---

## livekit-agents@1.3.6: livekit-agents@1.3.6
**Published:** 2025-12-03

## What's Changed
* more readable logs rendering by @theomonnom in https://github.com/livekit/agents/pull/4093
* fix prometheus multiprocess mode by @theomonnom in https://github.com/livekit/agents/pull/4108
* fix RecorderAudioOutput sample rate by @longcw in https://github.com/livekit/agents/pull/4098
* refresh jwt used in otlp requests before it expires by @paulwe in https://github.com/livekit/agents/pull/4107
* AGT-2269 insert silence during pauses for RecorderIO by @chenghao-mou in https://github.com/livekit/agents/pull/4088
* fix agent_turn and agent_speaking spans hierarchy & add agent_turn for tts_task by @longcw in https://github.com/livekit/agents/pull/4100
* Replaced deprecated amazon-transcribe SDK with new aws-sdk-transcribe-streaming by @pabloFuente in https://github.com/livekit/agents/pull/4111
* make generation_id private in SpeechHandle by @longcw in https://github.com/livekit/agents/pull/4124
* skip sig masking on windows by @chenghao-mou in https://github.com/livekit/agents/pull/4119
* Fix realtime compatibility with aws-sdk-bedrock-runtime 0.2.0 upgrade by @kachenjr in https://github.com/livekit/agents/pull/4134
* Enable Deepgram Nova-3 multilingual keyterm prompting by @jkroll-deepgram in https://github.com/livekit/agents/pull/4136
* copy logger levels configuration to job processes by @theomonnom in https://github.com/livekit/agents/pull/4139
* fix log text overflow by @theomonnom in https://github.com/livekit/agents/pull/4141
* fix logging.getChildren for py<3.12 by @theomonnom in https://github.com/livekit/agents/pull/4142
* fix traceback print when using LogQueueHandler by @longcw in https://github.com/livekit/agents/pull/4128
* add on_enter to AgentTask blocked_tasks if it's not done by @longcw in https://github.com/livekit/agents/pull/4113
* add WarmTransferTask  by @longcw in https://github.com/livekit/agents/pull/4126
* fix(anthropic): use passed client parameter instead of always creating new one (fixes #4129) by @joshiayush in https://github.com/livekit/agents/pull/4143
* heygen liveavatar plugin by @tinalenguyen in https://github.com/livekit/agents/pull/3948
* Gradium integration. by @LaurentMazare in https://github.com/livekit/agents/pull/4150
* Include mip_opt_out to batch deepgram STT requests by @eliooooooot in https://github.com/livekit/agents/pull/4144
* Inworld TTS Update by @cshape in https://github.com/livekit/agents/pull/4112
* Elevenlabs include pronunciation dictionary locators by @arvindvs in https://github.com/livekit/agents/pull/4097
* use log filter for log_context_fields by @longcw in https://github.com/livekit/agents/pull/4146
* fix: `AgentHandoff` unable to serialize and then deserialize [ONE-LINER] by @slado122 in https://github.com/livekit/agents/pull/4160
* fix OpenTelemetry breaking changes by @theomonnom in https://github.com/livekit/agents/pull/4162
* livekit-agents 1.3.6 by @theomonnom in https://github.com/livekit/agents/pull/4163

## New Contributors
* @pabloFuente made their first contribution in https://github.com/livekit/agents/pull/4111
* @jkroll-deepgram made their first contribution in https://github.com/livekit/agents/pull/4136
* @joshiayush made their first contribution in https://github.com/livekit/agents/pull/4143
* @LaurentMazare made their first contribution in https://github.com/livekit/agents/pull/4150
* @cshape made their first contribution in https://github.com/livekit/agents/pull/4112
* @arvindvs made their first contribution in https://github.com/livekit/agents/pull/4097
* @slado122 made their first contribution in https://github.com/livekit/agents/pull/4160

**Full Changelog**: https://github.com/livekit/agents/compare/livekit-agents@1.3.5...livekit-agents@1.3.6

[View on GitHub](https://github.com/livekit/agents/releases/tag/livekit-agents%401.3.6)

---

## livekit-agents@1.3.5: livekit-agents@1.3.5
**Published:** 2025-11-25

## What's Changed
* Improve IVR example README and add inline comments for clarifications by @toubatbrian in https://github.com/livekit/agents/pull/4065
* show milliseconds in CLI by @tinalenguyen in https://github.com/livekit/agents/pull/4080
* fix legacy api `ws_url` (WorkerOptions) by @theomonnom in https://github.com/livekit/agents/pull/4090
* fix turn-detector loading issue due to transformers 4.57.2 by @longcw in https://github.com/livekit/agents/pull/4084
* add openai prompt cache retention param by @tinalenguyen in https://github.com/livekit/agents/pull/4089
* flush telemetry traces and logs when cleanup job task by @longcw in https://github.com/livekit/agents/pull/4082
* livekit-agents 1.3.5 by @theomonnom in https://github.com/livekit/agents/pull/4091


**Full Changelog**: https://github.com/livekit/agents/compare/livekit-agents@1.3.4...livekit-agents@1.3.5

[View on GitHub](https://github.com/livekit/agents/releases/tag/livekit-agents%401.3.5)

---

## livekit-agents@1.3.4: livekit-agents@1.3.4
**Published:** 2025-11-24

## What's Changed
* fix `task_ids` is not defined by @theomonnom in https://github.com/livekit/agents/pull/4025
* fix tests and type checking by @longcw in https://github.com/livekit/agents/pull/4011
* fix contextvar when using text mode in console by @longcw in https://github.com/livekit/agents/pull/3972
* allow turn detection mode to be updated within session by @longcw in https://github.com/livekit/agents/pull/3816
* Inference: Allow provider specific parameter updates by @adrian-cowham in https://github.com/livekit/agents/pull/3808
* Fix docstrings after #1811 Blingfire default tokenizer switch by @mrkowalski in https://github.com/livekit/agents/pull/3812
* fix bithuman avatar getting local participant identity by @longcw in https://github.com/livekit/agents/pull/4029
* Allow pause in final transcript by @chenghao-mou in https://github.com/livekit/agents/pull/3995
* clear internal buffer of datastream io when interruption by @longcw in https://github.com/livekit/agents/pull/4030
* Support for pronunciation dictionary in Cartesia TTS by @cateet in https://github.com/livekit/agents/pull/4033
* Add OVHcloud AI Endpoints provider by @eliasto in https://github.com/livekit/agents/pull/4037
* bring back `drain-timeout` on the CLI by @theomonnom in https://github.com/livekit/agents/pull/4038
* feat(elevenlabs): add STTv2 with streaming support for Scribe v2 by @yorrick in https://github.com/livekit/agents/pull/3909
* add JobContext.local_participant_identity by @longcw in https://github.com/livekit/agents/pull/4031
* fix: ensure logger name is set even when custom scope is provided by @davidzhao in https://github.com/livekit/agents/pull/4040
* chore: remove pyav <16 lock by @davidzhao in https://github.com/livekit/agents/pull/4044
* add use_realtime to elevenlabs stt and support scribe v2 realtime model by @longcw in https://github.com/livekit/agents/pull/4041
* Remove flags from RawFunctionDescription by @philipp-eisen in https://github.com/livekit/agents/pull/4050
* Temp workaround for langfuse otel traces by @chenghao-mou in https://github.com/livekit/agents/pull/3987
* fix cloud tracer overwrites user-defined tracer provider by @longcw in https://github.com/livekit/agents/pull/4060
* Fix: Propagate ws_url in AgentServer.from_server_options by @kstonekuan in https://github.com/livekit/agents/pull/4046
* make `ChatContext.summarize` private by @theomonnom in https://github.com/livekit/agents/pull/4068
* add makefile by @chenghao-mou in https://github.com/livekit/agents/pull/4067
* feat(openai): add verbosity parameter support to LLM.with_azure() by @IanSteno in https://github.com/livekit/agents/pull/4070
* add dump signal handler and IPC message by @chenghao-mou in https://github.com/livekit/agents/pull/4064
* fix: accurate speech duration in VAD EOS by @jayeshp19 in https://github.com/livekit/agents/pull/4058
* add `chat_ctx` argument to `AgentSession.generate_reply` by @theomonnom in https://github.com/livekit/agents/pull/4074
* add livekit credentials to environment by @tinalenguyen in https://github.com/livekit/agents/pull/4075
* Changing audio format for rime from wav/mp3 to pcm by @gokuljs in https://github.com/livekit/agents/pull/4073
* livekit-agents 1.3.4 by @theomonnom in https://github.com/livekit/agents/pull/4077

## New Contributors
* @eliasto made their first contribution in https://github.com/livekit/agents/pull/4037
* @yorrick made their first contribution in https://github.com/livekit/agents/pull/3909
* @philipp-eisen made their first contribution in https://github.com/livekit/agents/pull/4050
* @kstonekuan made their first contribution in https://github.com/livekit/agents/pull/4046
* @IanSteno made their first contribution in https://github.com/livekit/agents/pull/4070

**Full Changelog**: https://github.com/livekit/agents/compare/livekit-agents@1.3.3...livekit-agents@1.3.4

[View on GitHub](https://github.com/livekit/agents/releases/tag/livekit-agents%401.3.4)

---

## livekit-agents@1.3.3: livekit-agents@1.3.3
**Published:** 2025-11-19

## New Features

### Observability

To learn more about the new observability features, check out our full write-up on the LiveKit blog. It walks through how session playback, trace inspection, and synchronized logs streamline debugging for voice agents. Read more [here](https://blog.livekit.io/streamline-troubleshooting-with-agent-observability/)

### New CLI

The CLI has been redesigned, and a new text-only mode was added so you can test your agent without using voice.

```
python3 my_agent.py console --text
```

You can also now configure both the input device and output device directly through the provided parameters.
```
python3 my_agent.py console --input-device "AirPods" --output-device "MacBook"
```

![new_cli](https://github.com/user-attachments/assets/9683def4-b177-42e9-9309-242b54f4c4af)

### New AgentServer API

We’ve renamed `Worker` to `AgentServer`, and you now need to use a decorator to define the entrypoint. All existing functionality remains backward compatible. This change lays the groundwork for upcoming design improvements and new features.

```python
server = AgentServer()

def prewarm(proc: JobProcess): ...
def load(proc: JobProcess): ...

server.setup_fnc = prewarm
server.load_fnc = load

@server.rtc_session(agent_name="my_customer_service_agent")
async def entrypoint(ctx: JobContext): ...
```

### Session Report & on_session_end callback

Use the on_session_end callback to generate a structured [SessionReport](https://github.com/livekit/agents/blob/a9e43fec7fc2a752658cf80506d901d0af622e38/livekit-agents/livekit/agents/voice/report.py#L13) that the conversation history, events, recording metadata, and the agent’s configuration.

```python
server = AgentServer()

async def on_session_end(ctx: JobContext) -> None:
    report = ctx.make_session_report()
    print(json.dumps(report.to_dict(), indent=2))
    
    chat_history = report.chat_history
    # Do post-processing on your session (e.g final evaluations, generate a summary, ...)

@server.rtc_session(on_session_end=on_session_end)
async def my_agent(ctx: JobContext) -> None:
    ...
```

### AgentHandoff item

To capture everything that occurred during your session, we added an [AgentHandoff](https://github.com/livekit/agents/blob/a9e43fec7fc2a752658cf80506d901d0af622e38/livekit-agents/livekit/agents/llm/chat_context.py#L198) item to the ChatContext.

```python
class AgentHandoff(BaseModel):
    ...
    old_agent_id: str | None
    new_agent_id: str
```

### Improved turn detection model

We updated the turn-detection model, resulting in measurable accuracy improvements across most languages. The table below shows the change in tnr@0.993 between versions 0.4.0 and 0.4.1, along with the percentage difference.

This new version also handles special user inputs such as email addresses, street addresses, and phone numbers much more effectively.

<img width="449" height="493" alt="514623611-bb709e00-71ca-4b0e-86c4-fd854dcaf51c" src="https://github.com/user-attachments/assets/0f9dee1e-5bfa-4c04-be2c-06d3c2213ed5" />

### TaskGroup

We added TaskGroup, which lets you run multiple tasks concurrently and wait for all of them to finish. This is useful when collecting several pieces of information from a user where the order doesn’t matter, or when the user may revise earlier inputs while continuing the flow.

We’ve also added an example that uses TaskGroup to build a [SurveyAgent](https://github.com/livekit/agents/blob/a9e43fec7fc2a752658cf80506d901d0af622e38/examples/survey/survey_agent.py), which you can use as a reference.

```python
task_group = TaskGroup()
task_group.add(lambda: GetEmailTask(), id="get_email_task", description="Get the email address")
task_group.add(lambda: GetPhoneNumberTask(), id="phone_number_task", description="Get the phone number")
task_group.add(lambda: GetCreditCardTask(), id="credit_card_task", description="Get credit card")
results = await task_group
```

### IVR systems

Agents can now optionally handle IVR-style interactions. Enabling `ivr_detection` allows the session to identify and respond appropriately to IVR tones or patterns, and `min_endpointing_delay` lets you control how long the system waits before ending a turn—useful for menu-style inputs.

```python
session = AgentSession(
    ivr_detection=True,
    min_endpointing_delay=5,
)
```

### llm_node FlushSentinel

We added a FlushSentinel marker that can be yielded from `llm_node` to flush partial LLM output to TTS and start a new TTS stream. This lets you emit a short, early response (for example, when a specific tool call is detected) while the main LLM response continues in the background. For a concrete pattern, see the [flush_llm_node.py](https://github.com/livekit/agents/blob/main/examples/voice_agents/flush_llm_node.py) example.

```python
async def llm_node(self, chat_ctx: llm.ChatContext, tools: list[llm.FunctionTool], model_settings: ModelSettings) -> AsyncIterable[llm.ChatChunk | FlushSentinel]:
    yield "This is the first sentence"
    yield FlushSentinel()
    yield "Another TTS generation"
```

## Changes

### asyncio-debug
The `--asyncio-debug` argument was removed, use [PYTHONASYNCIODEBUG](https://docs.python.org/3/using/cmdline.html#envvar-PYTHONASYNCIODEBUG) environment variable instead. 

## What's Changed
* feat: new CLI & new AgentServer API by @theomonnom in https://github.com/livekit/agents/pull/3199
* remove unused code & fix ServerEnvOption by @theomonnom in https://github.com/livekit/agents/pull/3220
* remove custom excepthook by @theomonnom in https://github.com/livekit/agents/pull/3221
* fix python 3.9 by @theomonnom in https://github.com/livekit/agents/pull/3222
* fix invalid `LogLevel` on the CLI by @theomonnom in https://github.com/livekit/agents/pull/3292
* add `Agent.id` by @theomonnom in https://github.com/livekit/agents/pull/3478
* add `AgentHandoff` chat item by @theomonnom in https://github.com/livekit/agents/pull/3479
* Add `AgentHandoff` to the chat_ctx & AgentSessionReport by @theomonnom in https://github.com/livekit/agents/pull/3541
* fix cli `readchar` by @theomonnom in https://github.com/livekit/agents/pull/3542
* fix `RecorderIO` av.error.MemoryError by @theomonnom in https://github.com/livekit/agents/pull/3543
* fix record & save to tempfile by @theomonnom in https://github.com/livekit/agents/pull/3544
* save session json report when `--record` is enabled by @theomonnom in https://github.com/livekit/agents/pull/3572
* brianyin/agt-1947-automatically-parse-dtmf-input-from-users by @toubatbrian in https://github.com/livekit/agents/pull/3512
* ingest data to cloud by @theomonnom in https://github.com/livekit/agents/pull/3609
* fix Audio/Video input source attach by @theomonnom in https://github.com/livekit/agents/pull/3615
* Allow Recording Verbal DTMF Input when ask_confirmation is turned off by @toubatbrian in https://github.com/livekit/agents/pull/3607
* Agent IVR System Example by @toubatbrian in https://github.com/livekit/agents/pull/3610
* add `ChatContext.summarize` by @theomonnom in https://github.com/livekit/agents/pull/3660
* Gather DTMF Minor Bug Fix by @toubatbrian in https://github.com/livekit/agents/pull/3672
* brianyin/agt-2076-support-repeat-instruction-in-dtmf-gathering by @toubatbrian in https://github.com/livekit/agents/pull/3674
* rename `assistant` to `agent` by @theomonnom in https://github.com/livekit/agents/pull/3690
* TaskGroup by @tinalenguyen in https://github.com/livekit/agents/pull/3680
* ignore on_enter on GetEmailTask by @theomonnom in https://github.com/livekit/agents/pull/3691
* Refactor mock session utilities into a separate file by @toubatbrian in https://github.com/livekit/agents/pull/3692
* fix _MetadataLogProcessor by @tinalenguyen in https://github.com/livekit/agents/pull/3697
* add Created-At header for the audio recording by @theomonnom in https://github.com/livekit/agents/pull/3698
* fix tool validation by @tinalenguyen in https://github.com/livekit/agents/pull/3699
* use otel logger for the chat_history by @theomonnom in https://github.com/livekit/agents/pull/3700
* Support Agent Session Tools  by @toubatbrian in https://github.com/livekit/agents/pull/3707
* add extra instructions + tools params into GetEmailTask by @tinalenguyen in https://github.com/livekit/agents/pull/3711
* format transcript logs by @paulwe in https://github.com/livekit/agents/pull/3708
* add participant attributes to traces by @theomonnom in https://github.com/livekit/agents/pull/3725
* fix duplicate `agent_session` span by @theomonnom in https://github.com/livekit/agents/pull/3726
* fix chat_history upload by @theomonnom in https://github.com/livekit/agents/pull/3728
* rename `realtime_session` to `rtc_session` by @theomonnom in https://github.com/livekit/agents/pull/3729
* add backward compatibility by @theomonnom in https://github.com/livekit/agents/pull/3730
* add missing options attr to session start log by @paulwe in https://github.com/livekit/agents/pull/3731
* brian/dtmf-send-tool by @toubatbrian in https://github.com/livekit/agents/pull/3656
* log potential thread leaks preventing process from exiting by @theomonnom in https://github.com/livekit/agents/pull/3744
* check room connection state + rename to on_emit + taskgroup fix by @tinalenguyen in https://github.com/livekit/agents/pull/3738
* add survey agent example by @tinalenguyen in https://github.com/livekit/agents/pull/3681
* update examples to use AgentServer by @tinalenguyen in https://github.com/livekit/agents/pull/3767
* allow multiple ids for out of scope by @tinalenguyen in https://github.com/livekit/agents/pull/3789
* add chat_history json to the report upload by @theomonnom in https://github.com/livekit/agents/pull/3799
* set log timestamps for chat history by @paulwe in https://github.com/livekit/agents/pull/3800
* check recorder_io in make_session_report by @tinalenguyen in https://github.com/livekit/agents/pull/3805
* feat(cartesia): add LiveKit user agent to requests by @mi-yu in https://github.com/livekit/agents/pull/3809
* Add Speechmatics TTS by @aaronng91 in https://github.com/livekit/agents/pull/3754
* built-in GetAddressTask by @tinalenguyen in https://github.com/livekit/agents/pull/3807
* fix extra instructions param and update confirm_address docstring by @tinalenguyen in https://github.com/livekit/agents/pull/3810
* Add support for using a previous silero vad model file by @zaheerabbas-prodigal in https://github.com/livekit/agents/pull/3779
* allow updating the same agent that is running to apply changes in agent by @longcw in https://github.com/livekit/agents/pull/3814
* chore: fix ruff & formatting by @davidzhao in https://github.com/livekit/agents/pull/3827
* fix type checking for agents 1.3 by @longcw in https://github.com/livekit/agents/pull/3842
* fix: correct base64 data handling in image content conversion #3867 by @tarsyang in https://github.com/livekit/agents/pull/3868
* fix observability by @davidzhao in https://github.com/livekit/agents/pull/3828
* avoid rotating transcription synchronizer twice during detach and attach by @longcw in https://github.com/livekit/agents/pull/3845
* fix pickling AgentServer for python 3.9 by @longcw in https://github.com/livekit/agents/pull/3847
* add better word alignment for Cartesia by @chenghao-mou in https://github.com/livekit/agents/pull/3876
* fix jupyter for agents 1.3 by @longcw in https://github.com/livekit/agents/pull/3877
* feat(minimax): comprehensive TTS updates and parameter rename by @zhenyujia23-crypto in https://github.com/livekit/agents/pull/3788
* feat(aws): add credentials customization for aws stt by @civilcoder55 in https://github.com/livekit/agents/pull/3840
* make sure user away timer is cancelled when session closed by @longcw in https://github.com/livekit/agents/pull/3895
* fix duplicate responses from gemini by @tinalenguyen in https://github.com/livekit/agents/pull/3898
* support google safety settings by @tinalenguyen in https://github.com/livekit/agents/pull/3815
* add audio_frame_size_ms for RoomInputOptions by @longcw in https://github.com/livekit/agents/pull/3899
* add new room options by @longcw in https://github.com/livekit/agents/pull/3417
* feat(tts): add sample rate option to TTS configuration for rime tts plugin arcana model  by @gokuljs in https://github.com/livekit/agents/pull/3910
* deepgram plugin: better websocket logs by @jjmaldonis in https://github.com/livekit/agents/pull/3912
* Add download location in readme by @chenghao-mou in https://github.com/livekit/agents/pull/3908
* chore: move LK env var checks later by @davidzhao in https://github.com/livekit/agents/pull/3920
* fix ForkServerContext import by @theomonnom in https://github.com/livekit/agents/pull/3924
* add timeout to datastream clear_buffer to avoid deadlock when missing playback finished event by @longcw in https://github.com/livekit/agents/pull/3917
* observability cleanup by @davidzhao in https://github.com/livekit/agents/pull/3929
* feature: GPT-5.1 support by @c0mpli in https://github.com/livekit/agents/pull/3928
* record when the session was started by @davidzhao in https://github.com/livekit/agents/pull/3930
* add <3.14 requirement temporarily by @chenghao-mou in https://github.com/livekit/agents/pull/3921
* Allow tool role for dummy user message by @chenghao-mou in https://github.com/livekit/agents/pull/3938
* add <3.14 requirement temporarily by @chenghao-mou in https://github.com/livekit/agents/pull/3942
* skip CI checks for md changes by @chenghao-mou in https://github.com/livekit/agents/pull/3939
* AGT-2200 Improve usage collector and metric logging with more details by @chenghao-mou in https://github.com/livekit/agents/pull/3935
* feat(cartesia): debug log Cartesia request id on WS connection by @mi-yu in https://github.com/livekit/agents/pull/3940
* Allow users to pick BVCTelephony at runtime by @bcherry in https://github.com/livekit/agents/pull/3926
* don't use decorators for setup_fnc & load_fnc by @theomonnom in https://github.com/livekit/agents/pull/3945
* expose `room_io` from the `AgentSession` by @theomonnom in https://github.com/livekit/agents/pull/3946
* Added Support for gpt-5.1-chat-latest by @devb-enp in https://github.com/livekit/agents/pull/3932
* turn-detection: use v0.4.1-intl by @lwestn in https://github.com/livekit/agents/pull/3941
* optimizations for turn detector model size by @davidzhao in https://github.com/livekit/agents/pull/3953
* feat: add AvatarTalk integration by @Maelstro in https://github.com/livekit/agents/pull/3139
* remove noisy error/warn logs by @theomonnom in https://github.com/livekit/agents/pull/3955
* release livekit-agents 1.3.1 by @theomonnom in https://github.com/livekit/agents/pull/3957
* better setup_fnc & load_fnc API & fix examples by @theomonnom in https://github.com/livekit/agents/pull/3958
* fix types for agents 1.3.1 by @longcw in https://github.com/livekit/agents/pull/3959
* livekit-agents 1.3.2 by @theomonnom in https://github.com/livekit/agents/pull/3960
* Skip FallbackLLMStream nested duplicate traces by @chenghao-mou in https://github.com/livekit/agents/pull/3934
* add flush for llm_node by @longcw in https://github.com/livekit/agents/pull/3933
* expose worker_load to prom & /worker endpoint by @theomonnom in https://github.com/livekit/agents/pull/3968
* Fix GPT-5.1 reasoning_effort by @ivanpuhachov in https://github.com/livekit/agents/pull/3966
* include speech duration in VAD EOS by @jayeshp19 in https://github.com/livekit/agents/pull/3951
* revert #2787: execute tools without waiting text generation by @longcw in https://github.com/livekit/agents/pull/3962
* livekit-agents 1.3.3 by @theomonnom in https://github.com/livekit/agents/pull/4024

## New Contributors
* @mi-yu made their first contribution in https://github.com/livekit/agents/pull/3809
* @aaronng91 made their first contribution in https://github.com/livekit/agents/pull/3754
* @zaheerabbas-prodigal made their first contribution in https://github.com/livekit/agents/pull/3779
* @tarsyang made their first contribution in https://github.com/livekit/agents/pull/3868
* @chenghao-mou made their first contribution in https://github.com/livekit/agents/pull/3876
* @zhenyujia23-crypto made their first contribution in https://github.com/livekit/agents/pull/3788
* @civilcoder55 made their first contribution in https://github.com/livekit/agents/pull/3840
* @jjmaldonis made their first contribution in https://github.com/livekit/agents/pull/3912
* @c0mpli made their first contribution in https://github.com/livekit/agents/pull/3928
* @devb-enp made their first contribution in https://github.com/livekit/agents/pull/3932
* @Maelstro made their first contribution in https://github.com/livekit/agents/pull/3139
* @ivanpuhachov made their first contribution in https://github.com/livekit/agents/pull/3966

**Full Changelog**: https://github.com/livekit/agents/compare/livekit-agents@1.2.18...livekit-agents@1.3.3

[View on GitHub](https://github.com/livekit/agents/releases/tag/livekit-agents%401.3.3)

---

## livekit-agents@1.3.1: livekit-agents@1.3.1
**Published:** 2025-11-17

> [!NOTE]
> A more detailed changelog will be available soon!

## What's Changed
* feat: new CLI & new AgentServer API by @theomonnom in https://github.com/livekit/agents/pull/3199
* remove unused code & fix ServerEnvOption by @theomonnom in https://github.com/livekit/agents/pull/3220
* remove custom excepthook by @theomonnom in https://github.com/livekit/agents/pull/3221
* fix python 3.9 by @theomonnom in https://github.com/livekit/agents/pull/3222
* fix invalid `LogLevel` on the CLI by @theomonnom in https://github.com/livekit/agents/pull/3292
* add `Agent.id` by @theomonnom in https://github.com/livekit/agents/pull/3478
* add `AgentHandoff` chat item by @theomonnom in https://github.com/livekit/agents/pull/3479
* Add `AgentHandoff` to the chat_ctx & AgentSessionReport by @theomonnom in https://github.com/livekit/agents/pull/3541
* fix cli `readchar` by @theomonnom in https://github.com/livekit/agents/pull/3542
* fix `RecorderIO` av.error.MemoryError by @theomonnom in https://github.com/livekit/agents/pull/3543
* fix record & save to tempfile by @theomonnom in https://github.com/livekit/agents/pull/3544
* save session json report when `--record` is enabled by @theomonnom in https://github.com/livekit/agents/pull/3572
* brianyin/agt-1947-automatically-parse-dtmf-input-from-users by @toubatbrian in https://github.com/livekit/agents/pull/3512
* ingest data to cloud by @theomonnom in https://github.com/livekit/agents/pull/3609
* fix Audio/Video input source attach by @theomonnom in https://github.com/livekit/agents/pull/3615
* Allow Recording Verbal DTMF Input when ask_confirmation is turned off by @toubatbrian in https://github.com/livekit/agents/pull/3607
* Agent IVR System Example by @toubatbrian in https://github.com/livekit/agents/pull/3610
* add `ChatContext.summarize` by @theomonnom in https://github.com/livekit/agents/pull/3660
* Gather DTMF Minor Bug Fix by @toubatbrian in https://github.com/livekit/agents/pull/3672
* brianyin/agt-2076-support-repeat-instruction-in-dtmf-gathering by @toubatbrian in https://github.com/livekit/agents/pull/3674
* rename `assistant` to `agent` by @theomonnom in https://github.com/livekit/agents/pull/3690
* TaskGroup by @tinalenguyen in https://github.com/livekit/agents/pull/3680
* ignore on_enter on GetEmailTask by @theomonnom in https://github.com/livekit/agents/pull/3691
* Refactor mock session utilities into a separate file by @toubatbrian in https://github.com/livekit/agents/pull/3692
* fix _MetadataLogProcessor by @tinalenguyen in https://github.com/livekit/agents/pull/3697
* add Created-At header for the audio recording by @theomonnom in https://github.com/livekit/agents/pull/3698
* fix tool validation by @tinalenguyen in https://github.com/livekit/agents/pull/3699
* use otel logger for the chat_history by @theomonnom in https://github.com/livekit/agents/pull/3700
* Support Agent Session Tools  by @toubatbrian in https://github.com/livekit/agents/pull/3707
* add extra instructions + tools params into GetEmailTask by @tinalenguyen in https://github.com/livekit/agents/pull/3711
* format transcript logs by @paulwe in https://github.com/livekit/agents/pull/3708
* add participant attributes to traces by @theomonnom in https://github.com/livekit/agents/pull/3725
* fix duplicate `agent_session` span by @theomonnom in https://github.com/livekit/agents/pull/3726
* fix chat_history upload by @theomonnom in https://github.com/livekit/agents/pull/3728
* rename `realtime_session` to `rtc_session` by @theomonnom in https://github.com/livekit/agents/pull/3729
* add backward compatibility by @theomonnom in https://github.com/livekit/agents/pull/3730
* add missing options attr to session start log by @paulwe in https://github.com/livekit/agents/pull/3731
* brian/dtmf-send-tool by @toubatbrian in https://github.com/livekit/agents/pull/3656
* log potential thread leaks preventing process from exiting by @theomonnom in https://github.com/livekit/agents/pull/3744
* check room connection state + rename to on_emit + taskgroup fix by @tinalenguyen in https://github.com/livekit/agents/pull/3738
* add survey agent example by @tinalenguyen in https://github.com/livekit/agents/pull/3681
* update examples to use AgentServer by @tinalenguyen in https://github.com/livekit/agents/pull/3767
* allow multiple ids for out of scope by @tinalenguyen in https://github.com/livekit/agents/pull/3789
* add chat_history json to the report upload by @theomonnom in https://github.com/livekit/agents/pull/3799
* set log timestamps for chat history by @paulwe in https://github.com/livekit/agents/pull/3800
* check recorder_io in make_session_report by @tinalenguyen in https://github.com/livekit/agents/pull/3805
* feat(cartesia): add LiveKit user agent to requests by @mi-yu in https://github.com/livekit/agents/pull/3809
* Add Speechmatics TTS by @aaronng91 in https://github.com/livekit/agents/pull/3754
* built-in GetAddressTask by @tinalenguyen in https://github.com/livekit/agents/pull/3807
* fix extra instructions param and update confirm_address docstring by @tinalenguyen in https://github.com/livekit/agents/pull/3810
* Add support for using a previous silero vad model file by @zaheerabbas-prodigal in https://github.com/livekit/agents/pull/3779
* allow updating the same agent that is running to apply changes in agent by @longcw in https://github.com/livekit/agents/pull/3814
* chore: fix ruff & formatting by @davidzhao in https://github.com/livekit/agents/pull/3827
* fix type checking for agents 1.3 by @longcw in https://github.com/livekit/agents/pull/3842
* fix: correct base64 data handling in image content conversion #3867 by @tarsyang in https://github.com/livekit/agents/pull/3868
* fix observability by @davidzhao in https://github.com/livekit/agents/pull/3828
* avoid rotating transcription synchronizer twice during detach and attach by @longcw in https://github.com/livekit/agents/pull/3845
* fix pickling AgentServer for python 3.9 by @longcw in https://github.com/livekit/agents/pull/3847
* add better word alignment for Cartesia by @chenghao-mou in https://github.com/livekit/agents/pull/3876
* fix jupyter for agents 1.3 by @longcw in https://github.com/livekit/agents/pull/3877
* feat(minimax): comprehensive TTS updates and parameter rename by @zhenyujia23-crypto in https://github.com/livekit/agents/pull/3788
* feat(aws): add credentials customization for aws stt by @civilcoder55 in https://github.com/livekit/agents/pull/3840
* make sure user away timer is cancelled when session closed by @longcw in https://github.com/livekit/agents/pull/3895
* fix duplicate responses from gemini by @tinalenguyen in https://github.com/livekit/agents/pull/3898
* support google safety settings by @tinalenguyen in https://github.com/livekit/agents/pull/3815
* add audio_frame_size_ms for RoomInputOptions by @longcw in https://github.com/livekit/agents/pull/3899
* add new room options by @longcw in https://github.com/livekit/agents/pull/3417
* feat(tts): add sample rate option to TTS configuration for rime tts plugin arcana model  by @gokuljs in https://github.com/livekit/agents/pull/3910
* deepgram plugin: better websocket logs by @jjmaldonis in https://github.com/livekit/agents/pull/3912
* Add download location in readme by @chenghao-mou in https://github.com/livekit/agents/pull/3908
* chore: move LK env var checks later by @davidzhao in https://github.com/livekit/agents/pull/3920
* fix ForkServerContext import by @theomonnom in https://github.com/livekit/agents/pull/3924
* add timeout to datastream clear_buffer to avoid deadlock when missing playback finished event by @longcw in https://github.com/livekit/agents/pull/3917
* observability cleanup by @davidzhao in https://github.com/livekit/agents/pull/3929
* feature: GPT-5.1 support by @c0mpli in https://github.com/livekit/agents/pull/3928
* record when the session was started by @davidzhao in https://github.com/livekit/agents/pull/3930
* add <3.14 requirement temporarily by @chenghao-mou in https://github.com/livekit/agents/pull/3921
* Allow tool role for dummy user message by @chenghao-mou in https://github.com/livekit/agents/pull/3938
* add <3.14 requirement temporarily by @chenghao-mou in https://github.com/livekit/agents/pull/3942
* skip CI checks for md changes by @chenghao-mou in https://github.com/livekit/agents/pull/3939
* AGT-2200 Improve usage collector and metric logging with more details by @chenghao-mou in https://github.com/livekit/agents/pull/3935
* feat(cartesia): debug log Cartesia request id on WS connection by @mi-yu in https://github.com/livekit/agents/pull/3940
* Allow users to pick BVCTelephony at runtime by @bcherry in https://github.com/livekit/agents/pull/3926
* don't use decorators for setup_fnc & load_fnc by @theomonnom in https://github.com/livekit/agents/pull/3945
* expose `room_io` from the `AgentSession` by @theomonnom in https://github.com/livekit/agents/pull/3946
* Added Support for gpt-5.1-chat-latest by @devb-enp in https://github.com/livekit/agents/pull/3932
* turn-detection: use v0.4.1-intl by @lwestn in https://github.com/livekit/agents/pull/3941
* optimizations for turn detector model size by @davidzhao in https://github.com/livekit/agents/pull/3953
* feat: add AvatarTalk integration by @Maelstro in https://github.com/livekit/agents/pull/3139
* remove noisy error/warn logs by @theomonnom in https://github.com/livekit/agents/pull/3955
* release livekit-agents 1.3.1 by @theomonnom in https://github.com/livekit/agents/pull/3957

## New Contributors
* @mi-yu made their first contribution in https://github.com/livekit/agents/pull/3809
* @aaronng91 made their first contribution in https://github.com/livekit/agents/pull/3754
* @zaheerabbas-prodigal made their first contribution in https://github.com/livekit/agents/pull/3779
* @tarsyang made their first contribution in https://github.com/livekit/agents/pull/3868
* @chenghao-mou made their first contribution in https://github.com/livekit/agents/pull/3876
* @zhenyujia23-crypto made their first contribution in https://github.com/livekit/agents/pull/3788
* @civilcoder55 made their first contribution in https://github.com/livekit/agents/pull/3840
* @jjmaldonis made their first contribution in https://github.com/livekit/agents/pull/3912
* @c0mpli made their first contribution in https://github.com/livekit/agents/pull/3928
* @devb-enp made their first contribution in https://github.com/livekit/agents/pull/3932
* @Maelstro made their first contribution in https://github.com/livekit/agents/pull/3139

**Full Changelog**: https://github.com/livekit/agents/compare/livekit-agents@1.2.18...livekit-agents@1.3.1

[View on GitHub](https://github.com/livekit/agents/releases/tag/livekit-agents%401.3.1)

---

## livekit-agents@1.2.18: livekit-agents@1.2.18
**Published:** 2025-11-05

## What's Changed
* chore: update to correct livekit-plugins-minimax-ai package by @davidzhao in https://github.com/livekit/agents/pull/3753
* New Spitch STT model: Mansa v1 by @temibabs in https://github.com/livekit/agents/pull/3748
* add missing file error for turn detection model by @tinalenguyen in https://github.com/livekit/agents/pull/3755
* Add Language Parameter Support for Rime Arcana TTS Model by @gokuljs in https://github.com/livekit/agents/pull/3757
* Update Letta voice API integration to use new endpoint by @cpfiffer in https://github.com/livekit/agents/pull/3736
* livekit-blingfire v1.0.1 by @theomonnom in https://github.com/livekit/agents/pull/3763
* fix blingfire windows compilation for python 3.14-freethreaded by @theomonnom in https://github.com/livekit/agents/pull/3766
* allow elevenlabs language code parameter to be null by @tinalenguyen in https://github.com/livekit/agents/pull/3761
* changes default base url for spelling by @aryeila in https://github.com/livekit/agents/pull/3768
* Improve streaming handling for Neuphonic by @alexshelkov in https://github.com/livekit/agents/pull/3703
* turn-detector: add turn detector v0.4.0-intl by @lwestn in https://github.com/livekit/agents/pull/3764
* fix(google): improved handling of tool_response_scheduling by @davidzhao in https://github.com/livekit/agents/pull/3781
* Update stt.py - Deepgram plugin allows PT for Keyterms by @cateet in https://github.com/livekit/agents/pull/3786
* skip exception log for StopResponse from a tool call by @longcw in https://github.com/livekit/agents/pull/3790
* restore root otel context for AgentTask and generate_reply in entrypoint by @longcw in https://github.com/livekit/agents/pull/3772
* feat: add preflight transcript via utterance by @dan-ince-aai in https://github.com/livekit/agents/pull/3654
* fix(google): do not pass in scheduling parameter by default by @davidzhao in https://github.com/livekit/agents/pull/3793
* Add Fish Audio TTS Plugin for LiveKit Agents by @ywkim in https://github.com/livekit/agents/pull/3720
* Shubhra/nvidia plugins by @Shubhrakanti in https://github.com/livekit/agents/pull/3392
* Undo `basic_agent` accidental commit in #3392 by @Shubhrakanti in https://github.com/livekit/agents/pull/3797
* fix: bithuman prewarm credential issue by @CathyL0 in https://github.com/livekit/agents/pull/3794
* Added missing parameters to Gladia by @Karamouche in https://github.com/livekit/agents/pull/3796
* livekit-agents 1.2.18 by @theomonnom in https://github.com/livekit/agents/pull/3806

## New Contributors
* @cpfiffer made their first contribution in https://github.com/livekit/agents/pull/3736
* @aryeila made their first contribution in https://github.com/livekit/agents/pull/3768
* @cateet made their first contribution in https://github.com/livekit/agents/pull/3786
* @ywkim made their first contribution in https://github.com/livekit/agents/pull/3720
* @Karamouche made their first contribution in https://github.com/livekit/agents/pull/3796

**Full Changelog**: https://github.com/livekit/agents/compare/livekit-agents@1.2.17...livekit-agents@1.2.18

[View on GitHub](https://github.com/livekit/agents/releases/tag/livekit-agents%401.2.18)

---

## livekit-agents@1.2.17: livekit-agents@1.2.17
**Published:** 2025-10-29

## What's Changed
* Fix/aws realtime tooluse barge in by @kachenjr in https://github.com/livekit/agents/pull/3704
* reset user state from away when user input transcribed by @longcw in https://github.com/livekit/agents/pull/3716
* set _read_audio_atask to None in init by @tinalenguyen in https://github.com/livekit/agents/pull/3727
* add issue templates by @tinalenguyen in https://github.com/livekit/agents/pull/3689
* feat: gemini session resumption handle by @aryanvdesh in https://github.com/livekit/agents/pull/3735
* turn detection: model v0.3.1-intl by @lwestn in https://github.com/livekit/agents/pull/3724
* fix room io audio output deadlock by @longcw in https://github.com/livekit/agents/pull/3746
* added gemini live model by @tinalenguyen in https://github.com/livekit/agents/pull/3750
* add openai gpt-5-chat-latest model by @tinalenguyen in https://github.com/livekit/agents/pull/3741

## New Contributors
* @kachenjr made their first contribution in https://github.com/livekit/agents/pull/3704
* @aryanvdesh made their first contribution in https://github.com/livekit/agents/pull/3735

**Full Changelog**: https://github.com/livekit/agents/compare/livekit-agents@1.2.16...livekit-agents@1.2.17

[View on GitHub](https://github.com/livekit/agents/releases/tag/livekit-agents%401.2.17)

---

## livekit-agents@1.2.16: livekit-agents@1.2.16
**Published:** 2025-10-27

## What's Changed
* Conditional message truncation based on LLM capabilitities by @hadamove-rapidsos in https://github.com/livekit/agents/pull/3655
* AWS realtime: make ModelStreamErrorException recoverable by @longcw in https://github.com/livekit/agents/pull/3662
* use inference gateway in basic_agent by @longcw in https://github.com/livekit/agents/pull/3611
* chore: use self.chat_ctx in multi_agent example by @longcw in https://github.com/livekit/agents/pull/3663
* fix(speechmatics): AdditionalVocab configuration update by @sam-s10s in https://github.com/livekit/agents/pull/3676
* chore(cartesia): default to the latest API version by @davidzhao in https://github.com/livekit/agents/pull/3652
* Update Soniox STT parameters by @matejmarinko-soniox in https://github.com/livekit/agents/pull/3670
* Improve gcp vertex credential check by @ChenghaoMou in https://github.com/livekit/agents/pull/2798
* Add streaming support for Neuphonic by @alexshelkov in https://github.com/livekit/agents/pull/3182
* Unify generate_reply and say code pattern by @ChenghaoMou in https://github.com/livekit/agents/pull/3683
* chore: correct minimax-ai package name by @davidzhao in https://github.com/livekit/agents/pull/3682
* fix(cartesia,deepgram): correctly timeout while in middle of TTS synthesis by @davidzhao in https://github.com/livekit/agents/pull/3686
* feat(voice/run_result): OTEL tracing of judge by @bml1g12 in https://github.com/livekit/agents/pull/3639
* feat: add CometAPI integration to OpenAI plugin by @TensorNull in https://github.com/livekit/agents/pull/3641
* Configure Prometheus in multi process mode by @efontan-dialpad in https://github.com/livekit/agents/pull/3565
* Fix: Connection Pool race condition  by @adrian-cowham in https://github.com/livekit/agents/pull/3705
* chore: lock onnxruntime to <=1.23.1 by @davidzhao in https://github.com/livekit/agents/pull/3712
* fix(worker): ensure safe iteration over process pool during job joining by @Panmax in https://github.com/livekit/agents/pull/3710
* feat(cartesia): sonic-3 by @davidzhao in https://github.com/livekit/agents/pull/3715

## New Contributors
* @hadamove-rapidsos made their first contribution in https://github.com/livekit/agents/pull/3655
* @matejmarinko-soniox made their first contribution in https://github.com/livekit/agents/pull/3670
* @TensorNull made their first contribution in https://github.com/livekit/agents/pull/3641
* @efontan-dialpad made their first contribution in https://github.com/livekit/agents/pull/3565

**Full Changelog**: https://github.com/livekit/agents/compare/livekit-agents@1.2.15...livekit-agents@1.2.16

[View on GitHub](https://github.com/livekit/agents/releases/tag/livekit-agents%401.2.16)

---

## livekit-agents@1.2.15: livekit-agents@1.2.15
**Published:** 2025-10-15

## What's Changed
* reduce CI noise by @theomonnom in https://github.com/livekit/agents/pull/3552
* automatically update livekit-agents pyproject.toml optional dependencies on version bump by @theomonnom in https://github.com/livekit/agents/pull/3553
* added drain param to session.shutdown() by @tinalenguyen in https://github.com/livekit/agents/pull/3562
* fix stt final transcript triggers user turn in manual turn detection by @longcw in https://github.com/livekit/agents/pull/3559
* feat(livekit-plugins-hume): add model_version parameter by @zgreathouse in https://github.com/livekit/agents/pull/3563
* fix model provider and metrics for FallbackAdapter and StreamAdapter by @longcw in https://github.com/livekit/agents/pull/3526
* handle aiohttp client error when connecting to openai realtime api by @longcw in https://github.com/livekit/agents/pull/3574
* Add `timeout` param to `with_openrouter()` function by @msaelices in https://github.com/livekit/agents/pull/3538
* Add a dev folder for examples to keep the git graph clean by @Shubhrakanti in https://github.com/livekit/agents/pull/3582
* Ensure ctx.api uses WorkerOptions credentials by exporting LIVEKIT_* in worker by @hwuiwon in https://github.com/livekit/agents/pull/3581
* feat(google): Add thinking_config support, new model, and expanded voice profiles for google gemini TTS by @hwuiwon in https://github.com/livekit/agents/pull/3583
* chore: ensure a recent version of certifi is installed by @davidzhao in https://github.com/livekit/agents/pull/3580
* fix(deepgram): correctly handle timeout related errors by @davidzhao in https://github.com/livekit/agents/pull/3579
* realtime model: wait for generate_reply before update tool results by @longcw in https://github.com/livekit/agents/pull/3511
* fix aws realtime deps version by @longcw in https://github.com/livekit/agents/pull/3592
* Updating Cartesia Version by @namantalreja in https://github.com/livekit/agents/pull/3570
* fix: lock pyav to <16 due to build issue by @davidzhao in https://github.com/livekit/agents/pull/3593
* lift google realtime api out of beta by @tinalenguyen in https://github.com/livekit/agents/pull/3614
* catch delete_room errors and disable delete_room_on_close by default by @longcw in https://github.com/livekit/agents/pull/3600
* feat(telemetry/utils): add ttft reporting to LangFuse by @bml1g12 in https://github.com/livekit/agents/pull/3594
* Add RTZR(ReturnZero) STT Plugin for LiveKit Agents by @kimdwkimdw in https://github.com/livekit/agents/pull/3376
* chore: Remove duplicate docstring for `preemptive_generation` parameter in AgentSession by @m-hamashita in https://github.com/livekit/agents/pull/3624
* fix(deepgram): send CloseStream message before closing TTS WebSocket by @Nisarg38 in https://github.com/livekit/agents/pull/3608
* feat(speechmatics): add max_speakers parameter for speaker diarization by @nsepehr in https://github.com/livekit/agents/pull/3524
* Align Google STT plugin with official documentation by @mrkowalski in https://github.com/livekit/agents/pull/3628
* add backwards compatibility for google's realtime model by @tinalenguyen in https://github.com/livekit/agents/pull/3630
* fix: exclude temperature parameter for gpt-5 and similar models by @TheAli711 in https://github.com/livekit/agents/pull/3573
* turn_detection: reduce max_endpointing_delay to 3s by @lwestn in https://github.com/livekit/agents/pull/3640
* feat: Integrate streaming endpoints for Sarvam APIs by @shreyas-sarvam in https://github.com/livekit/agents/pull/3498
* fix: heartbeat by @zachkamran in https://github.com/livekit/agents/pull/3648
* enable zero retention mode in elevenlabs by @tinalenguyen in https://github.com/livekit/agents/pull/3647
* Unprompted STT Reconnection at startup by @adrian-cowham in https://github.com/livekit/agents/pull/3649
* fix #3650 cartesia version backward compatibility by @wlbksy in https://github.com/livekit/agents/pull/3651
* livekit-agents 1.2.15 by @theomonnom in https://github.com/livekit/agents/pull/3658

## New Contributors
* @hwuiwon made their first contribution in https://github.com/livekit/agents/pull/3581
* @namantalreja made their first contribution in https://github.com/livekit/agents/pull/3570
* @kimdwkimdw made their first contribution in https://github.com/livekit/agents/pull/3376
* @m-hamashita made their first contribution in https://github.com/livekit/agents/pull/3624
* @Nisarg38 made their first contribution in https://github.com/livekit/agents/pull/3608
* @nsepehr made their first contribution in https://github.com/livekit/agents/pull/3524
* @TheAli711 made their first contribution in https://github.com/livekit/agents/pull/3573
* @lwestn made their first contribution in https://github.com/livekit/agents/pull/3640
* @shreyas-sarvam made their first contribution in https://github.com/livekit/agents/pull/3498
* @adrian-cowham made their first contribution in https://github.com/livekit/agents/pull/3649

**Full Changelog**: https://github.com/livekit/agents/compare/livekit-agents@1.2.14...livekit-agents@1.2.15

[View on GitHub](https://github.com/livekit/agents/releases/tag/livekit-agents%401.2.15)

---

## livekit-agents@1.2.14: livekit-agents@1.2.14
**Published:** 2025-10-01

## New feature
- Introduce LiveKit Inference: a unified model interface enabling STT, LLM, and TTS via one API key, with optimized latency, billing, and concurrency management 🚀
https://blog.livekit.io/introducing-livekit-inference/

## What's Changed
* inference: fix `extra_headers` provider by @theomonnom in https://github.com/livekit/agents/pull/3549


**Full Changelog**: https://github.com/livekit/agents/compare/livekit-agents@1.2.13...livekit-agents@1.2.14

[View on GitHub](https://github.com/livekit/agents/releases/tag/livekit-agents%401.2.14)

---

## livekit-agents@1.2.13: livekit-agents@1.2.13
**Published:** 2025-10-01

## What's Changed
* Gladia STT: support partial transcriptions by @fabrice404 in https://github.com/livekit/agents/pull/3530
* support STT with `model:lang` and parse model specs outside ctor by @longcw in https://github.com/livekit/agents/pull/3536
* update inference API & update model names by @theomonnom in https://github.com/livekit/agents/pull/3545
* deepgram: support for Flux by @davidzhao in https://github.com/livekit/agents/pull/3245

## New Contributors
* @fabrice404 made their first contribution in https://github.com/livekit/agents/pull/3530

**Full Changelog**: https://github.com/livekit/agents/compare/livekit-agents@1.2.12...livekit-agents@1.2.13

[View on GitHub](https://github.com/livekit/agents/releases/tag/livekit-agents%401.2.13)

---

## livekit-agents@1.2.12: livekit-agents@1.2.12
**Published:** 2025-09-29

## What's Changed
* fix: add transaction id for bithuman agent by @CathyL0 in https://github.com/livekit/agents/pull/3313
* flush audio emitter if audio generation is slower than realtime by @longcw in https://github.com/livekit/agents/pull/3438
* docs(CONTRIBUTING.md): add linting/formatting command guideline by @bml1g12 in https://github.com/livekit/agents/pull/3436
* feat: add model attribute to metrics tracking in LLM by @Panmax in https://github.com/livekit/agents/pull/3456
* Add Fireworks AI STT plugin by @yunyichi in https://github.com/livekit/agents/pull/2687
* fix(agent_activity): correctly nest OpenTelemetry spans within existing spans by @bml1g12 in https://github.com/livekit/agents/pull/3454
* fixed noise reduction type by @tinalenguyen in https://github.com/livekit/agents/pull/3469
* allow VoiceActivityVideoSampler to be disabled with 0fps by @davidzhao in https://github.com/livekit/agents/pull/3474
* fix playback_finished rpc for datastream audio output when using thread by @longcw in https://github.com/livekit/agents/pull/3473
* add minimax tts plugin by @longcw in https://github.com/livekit/agents/pull/3475
* expose background audio track publication for retrieving track details by @s-hamdananwar in https://github.com/livekit/agents/pull/3480
* refactor: simplify say() method logic in AgentSession by @Panmax in https://github.com/livekit/agents/pull/3488
* refactor: remove redundant if conditions by @Panmax in https://github.com/livekit/agents/pull/3486
* gemini realtime: support NON_BLOCKING tool behavior by @longcw in https://github.com/livekit/agents/pull/3482
* add docstring for minimax options by @longcw in https://github.com/livekit/agents/pull/3487
* inference: support lang/ for stt and update models by @longcw in https://github.com/livekit/agents/pull/3481
* add delete_room_on_close to RoomInputOptions by @tinalenguyen in https://github.com/livekit/agents/pull/3467
* return RealtimeModelBeta for Azure OpenAI Realtime by @tinalenguyen in https://github.com/livekit/agents/pull/3497
* feat: Add OpenRouter plugin for LiveKit Agents by @Hormold in https://github.com/livekit/agents/pull/3167
* Add model and provider in metrics for all services by @ChenghaoMou in https://github.com/livekit/agents/pull/3165
* add tts_text_transforms as an option to AgentSession by @longcw in https://github.com/livekit/agents/pull/3424
* fix: prevent deadlock in speech scheduling after consecutive delay by @Panmax in https://github.com/livekit/agents/pull/3502
* Add soniox and fireworks extras by @bcherry in https://github.com/livekit/agents/pull/3491
* fix conflicts of metrics.metadata by @longcw in https://github.com/livekit/agents/pull/3501
* fix ttft for OpenAI realtime model by @longcw in https://github.com/livekit/agents/pull/3507
* fix OAI realtime: remove deepcopy when reconnection by @longcw in https://github.com/livekit/agents/pull/3505
* gateway: update inference models by @longcw in https://github.com/livekit/agents/pull/3508
* fix datastream io clear buffer rpc for thread executor by @longcw in https://github.com/livekit/agents/pull/3514
* fix gemini llm: avoid mixing tool output and user message in a single turn by @longcw in https://github.com/livekit/agents/pull/3509
* fix missing simultaneous message & tool call by @furious-luke in https://github.com/livekit/agents/pull/3517
* livekit-agents 1.2.12 by @theomonnom in https://github.com/livekit/agents/pull/3523

## New Contributors
* @yunyichi made their first contribution in https://github.com/livekit/agents/pull/2687
* @Hormold made their first contribution in https://github.com/livekit/agents/pull/3167
* @furious-luke made their first contribution in https://github.com/livekit/agents/pull/3517

**Full Changelog**: https://github.com/livekit/agents/compare/livekit-agents@1.2.11...livekit-agents@1.2.12

[View on GitHub](https://github.com/livekit/agents/releases/tag/livekit-agents%401.2.12)

---

## livekit-agents@1.2.11: livekit-agents@1.2.11
**Published:** 2025-09-18

## What's Changed
* add shutdown method for AgentSession by @tinalenguyen in https://github.com/livekit/agents/pull/3429
* fixes #3435 by @mrkowalski in https://github.com/livekit/agents/pull/3437
* fix(openai): correctly handle update_options for active sessions by @davidzhao in https://github.com/livekit/agents/pull/3448
* fix openai realtime with azure when input_audio_noise_reduction is not given by @longcw in https://github.com/livekit/agents/pull/3451
* feat: trace Realtime Model Token/Cost via OpenTelemetry by @longcw in https://github.com/livekit/agents/pull/3439
* fix oai realtime options with default null by @longcw in https://github.com/livekit/agents/pull/3458
* Bug fix: Safe handling in ChatContext.truncate() when fewer items than max_items by @adianliusie in https://github.com/livekit/agents/pull/3457
* fix silero vad speech_buffer_max_reached by @longcw in https://github.com/livekit/agents/pull/3452
* [Cartesia] Upgrade Default Voice by @chongzluong in https://github.com/livekit/agents/pull/3446

## New Contributors
* @adianliusie made their first contribution in https://github.com/livekit/agents/pull/3457

**Full Changelog**: https://github.com/livekit/agents/compare/livekit-agents@1.2.9...livekit-agents@1.2.11

[View on GitHub](https://github.com/livekit/agents/releases/tag/livekit-agents%401.2.11)

---

## livekit-agents@1.2.9: livekit-agents@1.2.9
**Published:** 2025-09-15

## Features:
- OpenAI Realtime API now supports video input

## What's Changed
* Add Ultravox Realtime API Plugin by @moadel321 in https://github.com/livekit/agents/pull/2992
* fix and clean ultravox realtime API plugin by @longcw in https://github.com/livekit/agents/pull/3339
* remove sentence tokenizer from transcription sync by @longcw in https://github.com/livekit/agents/pull/3334
* non-stream tts: raise no audio pushed error only if text is not empty by @longcw in https://github.com/livekit/agents/pull/3310
* fix speech resume when interrupted by interim transcript by @longcw in https://github.com/livekit/agents/pull/3299
* add preferred_alignment and fix alignment chars by @longcw in https://github.com/livekit/agents/pull/3341
* feat: Add support for Nebius AI Studio Models by @Arindam200 in https://github.com/livekit/agents/pull/3332
* feat(AWS): Enable prompt caching by @itskyf in https://github.com/livekit/agents/pull/3338
* plugins: groq: llm: add support for timeout and max_retries by @ssettle-groq in https://github.com/livekit/agents/pull/3350
* plugins: groq: llm: add support for service_tier by @ssettle-groq in https://github.com/livekit/agents/pull/3348
* Fix warning in model field access by @marctorsoc in https://github.com/livekit/agents/pull/3340
* chore(groq): accept additional options by @davidzhao in https://github.com/livekit/agents/pull/3370
* add ELEVEN_API_KEY to README for configuration by @Panmax in https://github.com/livekit/agents/pull/3371
* feat(azure-stt): add configurable punctuation option to Azure STT by @sarthakgoyal23 in https://github.com/livekit/agents/pull/3326
* fix transcription synchronizer cannot be closed if paused by @longcw in https://github.com/livekit/agents/pull/3378
* chore: add update_options for aws tts by @longcw in https://github.com/livekit/agents/pull/3384
* add text normalization param by @tinalenguyen in https://github.com/livekit/agents/pull/3390
* fix: improve FallbackAdapter streaming capability detection by @bnovik0v in https://github.com/livekit/agents/pull/3294
* fix user speaking span duration by @tinalenguyen in https://github.com/livekit/agents/pull/3404
* add realtime model tool calls to chat ctx by @longcw in https://github.com/livekit/agents/pull/3345
* make flush duration configurable in commit_user_turn by @longcw in https://github.com/livekit/agents/pull/3358
* use markdown and emoji filters for tts_node by default by @longcw in https://github.com/livekit/agents/pull/3305
* commit user turn before closing the AgentSession by @longcw in https://github.com/livekit/agents/pull/3377
* fix OAI realtime response created after generate_reply timeout by @longcw in https://github.com/livekit/agents/pull/3405
* add warning if use_tts_aligned_transcript is enabled but no transcript received from tts by @longcw in https://github.com/livekit/agents/pull/3409
* fix: Agent status was not updated when audio was paused. by @Panmax in https://github.com/livekit/agents/pull/3406
* don't ever send meta to openai by @guidodecaso in https://github.com/livekit/agents/pull/3402
* Revert "tune vad min_silence_duration and min_endpointing_delay (#2953)" by @longcw in https://github.com/livekit/agents/pull/3416
* Removed OpenAI-Beta header as per the docs by @MajorTal in https://github.com/livekit/agents/pull/3412
* add tool call and output to session.history by @longcw in https://github.com/livekit/agents/pull/3316
* fix(sarvam-tts): add bulbul:v3-beta support and make pitch/loudness optional by @21lakshh in https://github.com/livekit/agents/pull/3413
* chore: add keyterms support for AssemblyAI plugin by @dan-ince-aai in https://github.com/livekit/agents/pull/3387
* Revert "Removed OpenAI-Beta header as per the docs" by @longcw in https://github.com/livekit/agents/pull/3419
* feat(Google): Add markup for TTS HD voices by @itskyf in https://github.com/livekit/agents/pull/3281
* feat: update openai realtime API version to GA by @davidzhao in https://github.com/livekit/agents/pull/3420
* revert #3206, do not auto enable use_tts_aligned_transcript by @longcw in https://github.com/livekit/agents/pull/3423
* livekit-agents 1.2.9 by @theomonnom in https://github.com/livekit/agents/pull/3428

## New Contributors
* @moadel321 made their first contribution in https://github.com/livekit/agents/pull/2992
* @Arindam200 made their first contribution in https://github.com/livekit/agents/pull/3332
* @ssettle-groq made their first contribution in https://github.com/livekit/agents/pull/3350
* @marctorsoc made their first contribution in https://github.com/livekit/agents/pull/3340
* @sarthakgoyal23 made their first contribution in https://github.com/livekit/agents/pull/3326
* @21lakshh made their first contribution in https://github.com/livekit/agents/pull/3413

**Full Changelog**: https://github.com/livekit/agents/compare/livekit-agents@1.2.8...livekit-agents@1.2.9

[View on GitHub](https://github.com/livekit/agents/releases/tag/livekit-agents%401.2.9)

---

## livekit-agents@1.2.8: livekit-agents@1.2.8
**Published:** 2025-09-02

## Features:

- [AgentSession.start()](https://github.com/livekit/agents/blob/713988e3741a1498d373593c030c0fbd28262284/livekit-agents/livekit/agents/voice/agent_session.py#L401C15-L401C20) now returns a `RunResult` when called with `capture_run=True`.
This makes it possible to assert the first message when the agent initiates the conversation:
```python
result = await sess.start(EchoAgent(), capture_run=True)
result.expect.next_event().is_agent_handoff(new_agent_type=EchoAgent)
result.expect.next_event().is_message(role="assistant")
```

- Agent false interruptions are now automatically resumed after the `false_interruption_timeout`. Audio output is paused and then resumed on the same `SpeechHandle`, eliminating the need to manually call `generate_reply()` in the `agent_false_interruption` event handler—please remove this call if present from earlier versions. This behavior is enabled by default; to disable automatic resume, set `resume_false_interruption=False`.


## What's Changed
* fix: start datastream audio output right after room connected by @longcw in https://github.com/livekit/agents/pull/3270
* add AudioOutput capabilities and disable pause/resume for if output not supported by @longcw in https://github.com/livekit/agents/pull/3269
* fix (11labs): fix empty text input and timeout for the first audio chunk by @longcw in https://github.com/livekit/agents/pull/3284
* chore: switch to gpt-realtime as default OAI realtime model by @davidzhao in https://github.com/livekit/agents/pull/3287
* fix(plugins:elevenlabs): fix exception in STT when serializing bool form field tag_audio_events by @mike-r-mclaughlin in https://github.com/livekit/agents/pull/3282
* primary speaker detection with STT diarization by @longcw in https://github.com/livekit/agents/pull/3186
* add capture_run for AgentSession.start by @longcw in https://github.com/livekit/agents/pull/3288
* chore: add test for empty tts streams by @davidzhao in https://github.com/livekit/agents/pull/3286
* fix say method not being captured by RunResult by @theomonnom in https://github.com/livekit/agents/pull/3291
* support interrupting agent by interim transcripts by @longcw in https://github.com/livekit/agents/pull/3278
* allow SpeechHandle to be interrupted when long-running function tools are pending by @longcw in https://github.com/livekit/agents/pull/3280
* fix: disable false interruption resume for realtime model by @longcw in https://github.com/livekit/agents/pull/3298
* feat(langgraph): support subgraphs in LLMAdapter and normalize astream outputs by @bnovik0v in https://github.com/livekit/agents/pull/3112
* feat: add more llm and stt models to mistralai plugins by @fabitokki in https://github.com/livekit/agents/pull/3300
* chore(langchain): fix types by @davidzhao in https://github.com/livekit/agents/pull/3303

## New Contributors
* @bnovik0v made their first contribution in https://github.com/livekit/agents/pull/3112

**Full Changelog**: https://github.com/livekit/agents/compare/livekit-agents@1.2.7...livekit-agents@1.2.8

[View on GitHub](https://github.com/livekit/agents/releases/tag/livekit-agents%401.2.8)

---

## livekit-agents@1.2.7: livekit-agents@1.2.7
**Published:** 2025-08-28

## What's Changed
* fix(examples): multi-user-translator: iterate over copy of keys to allow dict mutation during loop by @mike-r-mclaughlin in https://github.com/livekit/agents/pull/3190
* Add missing mistralai and smallestai optional dependencies by @bcherry in https://github.com/livekit/agents/pull/3191
* fix(google): Instant Voice Cloning Key Parameter is incorrect by @gnomefin in https://github.com/livekit/agents/pull/3203
* gemini live: create new generation only if response has a content by @longcw in https://github.com/livekit/agents/pull/3192
* Document text_type for Amazon Polly TTS by @kath0la in https://github.com/livekit/agents/pull/3200
* enable use_tts_aligned_transcript for non-streaming tts by default by @longcw in https://github.com/livekit/agents/pull/3206
* Fix Google STT Word‑timings error. by @itskyf in https://github.com/livekit/agents/pull/3204
* fix interruption context when speech has't started for session.say by @longcw in https://github.com/livekit/agents/pull/3207
* fix: only add meta to MCP tool schema when it's provided by @longcw in https://github.com/livekit/agents/pull/3212
* remove thinking_budget range check for google LLM by @longcw in https://github.com/livekit/agents/pull/3213
* Add `start_time`, `end_time`, and `speaker_id` to 11labs `SpeechData` by @dvschuyl in https://github.com/livekit/agents/pull/3224
* fix ElevenLabs stt base url configuration by @longcw in https://github.com/livekit/agents/pull/3228
* support updating `min_endpointing_delay` via AgentSession and configing it per-agent by @longcw in https://github.com/livekit/agents/pull/3227
* feat: enable keyterm prompting in deepgram for de, nl, sv, da by @danielgrittner in https://github.com/livekit/agents/pull/3215
* Plugin: add upliftai TTS plugin by @zaidqureshi2 in https://github.com/livekit/agents/pull/3209
* add readme for examples by @longcw in https://github.com/livekit/agents/pull/3225
* Update Anthropic LLM models by @olegkorol in https://github.com/livekit/agents/pull/3243
* chore: allow types-protobuf>=4 by @davidzhao in https://github.com/livekit/agents/pull/3247
* feat: add force parameter to interrupt methods for speech generation by @Panmax in https://github.com/livekit/agents/pull/3246
* fix groq plugin dependencies by @longcw in https://github.com/livekit/agents/pull/3256
* Add Soniox STT integration by @zanhorvat-soniox in https://github.com/livekit/agents/pull/2443
* feat: add option to tag audio events in ElevenLabs STT by @Panmax in https://github.com/livekit/agents/pull/3249
* fix: Google TTS empty results by @itskyf in https://github.com/livekit/agents/pull/3252
* add `cancel_tool_reply` to function_tools_executed event by @longcw in https://github.com/livekit/agents/pull/3177
* chore(11labs): update plugin to use multi-context websocket API by @davidzhao in https://github.com/livekit/agents/pull/3241
* add resume_false_interruption and pause/resume the audio output by @longcw in https://github.com/livekit/agents/pull/3109
* update silero vad to v6 model by @theomonnom in https://github.com/livekit/agents/pull/3275

## New Contributors
* @gnomefin made their first contribution in https://github.com/livekit/agents/pull/3203
* @itskyf made their first contribution in https://github.com/livekit/agents/pull/3204
* @dvschuyl made their first contribution in https://github.com/livekit/agents/pull/3224
* @danielgrittner made their first contribution in https://github.com/livekit/agents/pull/3215
* @zaidqureshi2 made their first contribution in https://github.com/livekit/agents/pull/3209
* @olegkorol made their first contribution in https://github.com/livekit/agents/pull/3243
* @zanhorvat-soniox made their first contribution in https://github.com/livekit/agents/pull/2443

**Full Changelog**: https://github.com/livekit/agents/compare/livekit-agents@1.2.6...livekit-agents@1.2.7

[View on GitHub](https://github.com/livekit/agents/releases/tag/livekit-agents%401.2.7)

---

## livekit-agents@1.2.6: livekit-agents@1.2.6
**Published:** 2025-08-18

## What's Changed
* fix: examples: multi-user-translator: fix event names and use nova-2 model explicitly by @mike-r-mclaughlin in https://github.com/livekit/agents/pull/3122
* google stt: add enable_word_confidence option by @longcw in https://github.com/livekit/agents/pull/3124
* chore: cleaned up examples. updated readme by @davidzhao in https://github.com/livekit/agents/pull/3120
* fix: remove tool_choice when no tools provided by @longcw in https://github.com/livekit/agents/pull/3126
* chore: pass job information to remote EOT inference by @davidzhao in https://github.com/livekit/agents/pull/3132
* fix: make sure user message is added to chat ctx if interrupted during on_user_turn_completed by @longcw in https://github.com/livekit/agents/pull/3123
* add unit tests for preemptive generation by @longcw in https://github.com/livekit/agents/pull/3128
* openai realtime: retry if creating ws connection failed by @longcw in https://github.com/livekit/agents/pull/3136
* use non-strict tool schema for cerebras llm by @longcw in https://github.com/livekit/agents/pull/3134
* use parameters for gemini live api function declaration by @longcw in https://github.com/livekit/agents/pull/3135
* Add Rime TTS example for generating real-time audio from text by @gokuljs in https://github.com/livekit/agents/pull/2972
* feat: warm transfer example by @davidzhao in https://github.com/livekit/agents/pull/3125
* fix tts pacing when pushed text is empty by @longcw in https://github.com/livekit/agents/pull/3146
* Add support for meta info in MCP tools by @guidodecaso in https://github.com/livekit/agents/pull/3144
* feat: integrate mistral stt by @fabitokki in https://github.com/livekit/agents/pull/3131
* fix: allow CPU override from environment by @davidzhao in https://github.com/livekit/agents/pull/3156
* aws stt: set language and confidence in output by @longcw in https://github.com/livekit/agents/pull/3158
* fix mistralai llm and stt by @longcw in https://github.com/livekit/agents/pull/3157
* fix deadlock when calling _update_activiy in on_enter of a new agent by @longcw in https://github.com/livekit/agents/pull/3155
* fix: check if scheduling_paused after on_user_turn_completed callback by @longcw in https://github.com/livekit/agents/pull/3091
* oai realtime: set closing when reconnection to avoid error from recv task by @longcw in https://github.com/livekit/agents/pull/3160
* support for smallest.ai tts plugin by @hamees-sayed in https://github.com/livekit/agents/pull/3082
* feat(aws-polly): add support for ssml text type by @choso in https://github.com/livekit/agents/pull/3141
* fix duplicated metrics when using AgentTask by @longcw in https://github.com/livekit/agents/pull/3168
* fix: skip done speech when scheduling by @longcw in https://github.com/livekit/agents/pull/3169
* Speaker ID using Speechmatics STT by @sam-s10s in https://github.com/livekit/agents/pull/2625
* fix types in speechmatics plugin by @davidzhao in https://github.com/livekit/agents/pull/3171
* fix: export mock_tool and other types from run_result by @davidzhao in https://github.com/livekit/agents/pull/3172
* speechmatics stt: fix speech data start and end time and clean up by @longcw in https://github.com/livekit/agents/pull/3176
* feat: pass language in UserInputTranscribedEvent by @davidzhao in https://github.com/livekit/agents/pull/3179
* feat(google): support Chirp3 instant voice clones by @davidzhao in https://github.com/livekit/agents/pull/3181
* Use heartbeat param for websocket connection by @wlbksy in https://github.com/livekit/agents/pull/3178

## New Contributors
* @gokuljs made their first contribution in https://github.com/livekit/agents/pull/2972
* @guidodecaso made their first contribution in https://github.com/livekit/agents/pull/3144
* @hamees-sayed made their first contribution in https://github.com/livekit/agents/pull/3082
* @sam-s10s made their first contribution in https://github.com/livekit/agents/pull/2625
* @wlbksy made their first contribution in https://github.com/livekit/agents/pull/3178

**Full Changelog**: https://github.com/livekit/agents/compare/livekit-agents@1.2.5...livekit-agents@1.2.6

[View on GitHub](https://github.com/livekit/agents/releases/tag/livekit-agents%401.2.6)

---

## livekit-agents@1.2.5: livekit-agents@1.2.5
**Published:** 2025-08-10

> [!NOTE]  
> **livekit-agents 1.2 introduced many new features. You can check out the changelog [here](https://github.com/livekit/agents/releases/tag/livekit-agents%401.2.0).**

## What's Changed
* feat: add openai gpt-5 models by @mateuszkulpa in https://github.com/livekit/agents/pull/3106
* chore: improve basic_agent by @davidzhao in https://github.com/livekit/agents/pull/3100
* expose reasoning_effort and other new params. by @davidzhao in https://github.com/livekit/agents/pull/3108
* fix: improved handling for remote inference by @davidzhao in https://github.com/livekit/agents/pull/3116
* feat: cgroups v1 support, lower idle processes by @davidzhao in https://github.com/livekit/agents/pull/3117


**Full Changelog**: https://github.com/livekit/agents/compare/livekit-agents@1.2.4...livekit-agents@1.2.5

[View on GitHub](https://github.com/livekit/agents/releases/tag/livekit-agents%401.2.5)

---

## livekit-agents@1.2.4: livekit-agents@1.2.4
**Published:** 2025-08-07

> [!NOTE]  
> **livekit-agents 1.2 introduced many new features. You can check out the changelog [here](https://github.com/livekit/agents/releases/tag/livekit-agents%401.2.0).**

## What's Changed
* google stt: add enable_word_time_offsets option by @longcw in https://github.com/livekit/agents/pull/3079
* feat: support bithuman cloud avatar by @CathyL0 in https://github.com/livekit/agents/pull/3055
* fix cartesia error when input text is empty by @longcw in https://github.com/livekit/agents/pull/3080
* add endpoint_url in deepgram STT options by @RoccoFortuna in https://github.com/livekit/agents/pull/3086
* Do not `wait_on_enter` when resuming `Agent` after `AgentTask` execution by @anishnag in https://github.com/livekit/agents/pull/3090
* trace: attach agent session root span before closing by @longcw in https://github.com/livekit/agents/pull/3092
* fix AgentTask update_chat_ctx for realtime agent by @longcw in https://github.com/livekit/agents/pull/3093
* add the sdk version to the worker http endpoint by @real-danm in https://github.com/livekit/agents/pull/3097
* Add full list of supported languages for Google Cloud STT v2 by @amjd in https://github.com/livekit/agents/pull/3053
* feat: allow custom track name to be used with RoomIO by @davidzhao in https://github.com/livekit/agents/pull/3029
* support creating multiple DataStreamAudioOutput for multi-avatar use case by @longcw in https://github.com/livekit/agents/pull/3099

## New Contributors
* @RoccoFortuna made their first contribution in https://github.com/livekit/agents/pull/3086
* @amjd made their first contribution in https://github.com/livekit/agents/pull/3053

**Full Changelog**: https://github.com/livekit/agents/compare/livekit-agents@1.2.3...livekit-agents@1.2.4

[View on GitHub](https://github.com/livekit/agents/releases/tag/livekit-agents%401.2.4)

---

## livekit-agents@1.2.3: livekit-agents@1.2.3
**Published:** 2025-08-04

> [!NOTE]  
> **livekit-agents 1.2 introduced many new features. You can check out the changelog [here](https://github.com/livekit/agents/releases/tag/livekit-agents%401.2.0).**

previous patch version changelog [here](https://github.com/livekit/agents/releases/tag/livekit-agents%401.2.2) (1.2.2)

## What's Changed
* chore(assemblyai): update termination message by @dan-ince-aai in https://github.com/livekit/agents/pull/3001
* fix gemini realtime generate_reply by @longcw in https://github.com/livekit/agents/pull/3017
* pin the hedra avatar sample rate to 16k by @longcw in https://github.com/livekit/agents/pull/3027
* add metadata when set tracer provider by @longcw in https://github.com/livekit/agents/pull/3034
* Fix incorrect streaming flag for neuphonic by @alexshelkov in https://github.com/livekit/agents/pull/3036
* Gladia STT - fix region parameter to gladia stt on query parameters by @mfernandez-gladia in https://github.com/livekit/agents/pull/3018
* feat(azure-stt): add phrase list support for keyword boosting by @JohnBurtt10-bot in https://github.com/livekit/agents/pull/3024
* fix aws stt restarting by @longcw in https://github.com/livekit/agents/pull/2994
* improve tts error trace and expose cartesia error message by @longcw in https://github.com/livekit/agents/pull/3028
* add retry_on_chunk_sent to FallbackAdapter for allowing retry after chunk sent by @longcw in https://github.com/livekit/agents/pull/3033
* Fix RuntimeError on scheduling speech and on mark_generation_done by @jayeshp19 in https://github.com/livekit/agents/pull/3032
* add modalities arg to OAI realtime model with_azure by @longcw in https://github.com/livekit/agents/pull/3049
* enable - gemini-live-2.5-flash-preview by @yaniv-peretz in https://github.com/livekit/agents/pull/3016
* Update events.py with new AWS Nova Sonic voice by @lucasolinas in https://github.com/livekit/agents/pull/3048
* Updating minimal worker to connect to room by @sascotto in https://github.com/livekit/agents/pull/3065
* Fixing chunk size bug on inworld plugin-- matches hume and neuphonic by @thavidu in https://github.com/livekit/agents/pull/3067
* feat: use default load fnc and thresholds when hosting on Cloud by @davidzhao in https://github.com/livekit/agents/pull/3069
* fix: call on_attached or on_detached when set agent input and output by @longcw in https://github.com/livekit/agents/pull/3063
* fix using AgentTask in on_enter and on_exit by @longcw in https://github.com/livekit/agents/pull/3051
* use tts as fallback when realtime model returns text response by @longcw in https://github.com/livekit/agents/pull/3050
* add tts stream pacer to generate speech lazily by @longcw in https://github.com/livekit/agents/pull/3074

## New Contributors
* @alexshelkov made their first contribution in https://github.com/livekit/agents/pull/3036
* @JohnBurtt10-bot made their first contribution in https://github.com/livekit/agents/pull/3024
* @yaniv-peretz made their first contribution in https://github.com/livekit/agents/pull/3016
* @lucasolinas made their first contribution in https://github.com/livekit/agents/pull/3048
* @thavidu made their first contribution in https://github.com/livekit/agents/pull/3067

**Full Changelog**: https://github.com/livekit/agents/compare/livekit-agents@1.2.2...livekit-agents@1.2.3

[View on GitHub](https://github.com/livekit/agents/releases/tag/livekit-agents%401.2.3)

---

## livekit-plugins-google@0.11.5: livekit-plugins-google@0.11.5
**Published:** 2025-07-24

### Patch Changes

-   backporting fix to agents 0.x to ignore Gemini LLM responses with no candidates (#2898) - [`73e5384c85ea9b29fa4c946f29c66bef80d5d160`](https://github.com/livekit/agents/commit/73e5384c85ea9b29fa4c946f29c66bef80d5d160) ([@davidzhao](https://github.com/davidzhao))


[View on GitHub](https://github.com/livekit/agents/releases/tag/livekit-plugins-google%400.11.5)

---

## livekit-agents@1.2.2: livekit-agents@1.2.2
**Published:** 2025-07-24

> [!NOTE]  
> **livekit-agents 1.2 introduced many new features. You can check out the changelog [here](https://github.com/livekit/agents/releases/tag/livekit-agents%401.2.0).**



## New features
### SpeechHandle
Waiting for the playout to finish inside the function tools could lead to deadlocks. In this version, an error will be raised instead. To wait for the assistant's spoken response prior of executing a tool, use [RunContext.wait_for_playout](https://github.com/livekit/agents/blob/9defafaf545842f1fa20128825fa8c190dc5f114/livekit-agents/livekit/agents/voice/events.py#L73).
```python
@function_tool
async def my_function_tool(self, ctx: RunContext):
    await ctx.wait_for_playout() # wait for the assistant's spoken response that started the execution of this tool
```

### False interruption detection
We're now emitting an [event](https://github.com/livekit/agents/blob/db7956d2975db4c5685f16472027c7e160b57699/livekit-agents/livekit/agents/voice/events.py#L122) when the agent got interrupted, but we didn't receive any transcript. (Likely a false interruption).
This is useful to "re-regenerate" an assistant reply so the agent doesn't seems stuck.
```python
@session.on("agent_false_interruption")
def on_false_interruption(ev: AgentFalseInterruptionEvent):
    session.generate_reply(instructions=ev.extra_instructions or NOT_GIVEN)
```

### Initial conversation recording
We have begun implementing conversation recording directly within the Worker. Currently, it can be accessed using the console subcommand. A future update will provide API to use this in production. 
```
python3 examples/drive-thru/drivethru_agent.py console --record
```


## What's Changed
* fix cartesia non-streaming tts by @longcw in https://github.com/livekit/agents/pull/2942
* add RecorderIO and --record flag to the console mode by @theomonnom in https://github.com/livekit/agents/pull/2934
* chore: remove prometheus database from repository by @mateuszkulpa in https://github.com/livekit/agents/pull/2944
* parameterize inference worker init timeout by @levity in https://github.com/livekit/agents/pull/2805
* plugins: openai: llm: add support for service_tier by @mike-r-mclaughlin in https://github.com/livekit/agents/pull/2945
* fix: upgrade bithuman library to unblock accessing agents by @CathyL0 in https://github.com/livekit/agents/pull/2948
* fix duplicated user messages when preemptive generation canceled by @longcw in https://github.com/livekit/agents/pull/2949
* fix azure stt update options and add logs for error reason by @longcw in https://github.com/livekit/agents/pull/2954
* Explictly calling ctx.connect before wait_for_participant by @sascotto in https://github.com/livekit/agents/pull/2957
* azure stt: disable language detection if only one language sepcified by @longcw in https://github.com/livekit/agents/pull/2959
* gemini: emit input_speech_started when new generation created by @longcw in https://github.com/livekit/agents/pull/2963
* evals: fix realtime model RuntimeError  by @theomonnom in https://github.com/livekit/agents/pull/2965
* reveri/fix-11labs-error-fstring by @johncDepop in https://github.com/livekit/agents/pull/2964
* add RunContext.wait_for_playout and guard against deadlocks by @theomonnom in https://github.com/livekit/agents/pull/2966
* feat(realtime_model): correctly emit errors when the response is done by @bml1g12 in https://github.com/livekit/agents/pull/2967
* slightly optimize import time by @theomonnom in https://github.com/livekit/agents/pull/2968
* increase RoomInput frame_size_ms to 50ms by @theomonnom in https://github.com/livekit/agents/pull/2970
* add warning when enabling unprovided input/output sinks by @longcw in https://github.com/livekit/agents/pull/2969
* Handle RN format for preconnect mimeType by @davidzhao in https://github.com/livekit/agents/pull/2952
* tune vad min_silence_duration and min_endpointing_delay by @longcw in https://github.com/livekit/agents/pull/2953
* feat: add anam avatar by @karlson-anam in https://github.com/livekit/agents/pull/2938
* fix types for anam avatar plugin by @longcw in https://github.com/livekit/agents/pull/2976
* fix 11labs tts when audio is an empty string by @longcw in https://github.com/livekit/agents/pull/2973
* support resume agent from a false interruption by @longcw in https://github.com/livekit/agents/pull/2852
* feat: add simli avatar with example by @Antonyesk601 in https://github.com/livekit/agents/pull/2923
* add simli plugin to ci by @longcw in https://github.com/livekit/agents/pull/2978
* remove Resemble from CI  by @theomonnom in https://github.com/livekit/agents/pull/2979
* clean up avatar example and add retry for datastream io rpc call by @longcw in https://github.com/livekit/agents/pull/2943
* expose transcription sync speed to RoomOutputOptions by @longcw in https://github.com/livekit/agents/pull/2984
* hume tts: raise error message from the api by @longcw in https://github.com/livekit/agents/pull/2982
* io: add input source hierarchy & cleanup by @theomonnom in https://github.com/livekit/agents/pull/2983
* fix AgentFalseInterruptedEvent none message by @theomonnom in https://github.com/livekit/agents/pull/2987
* rename AgentFalseInterruptedEvent -> AgentFalseInterruptionEvent by @theomonnom in https://github.com/livekit/agents/pull/2988
* nit: update AgentFalseInterruptionEvent by @theomonnom in https://github.com/livekit/agents/pull/2989
* fix deadlock & session close race by @theomonnom in https://github.com/livekit/agents/pull/2997
* wait on_exit before pause scheduling by @longcw in https://github.com/livekit/agents/pull/2996
* Gladia STT - add region parameter to gladia stt by @mfernandez-gladia in https://github.com/livekit/agents/pull/2995
* fix: upgrade bithuman library version by @CathyL0 in https://github.com/livekit/agents/pull/2998
* improve GetEmailTask instructions by @theomonnom in https://github.com/livekit/agents/pull/3002
* message should be None when empty by @theomonnom in https://github.com/livekit/agents/pull/3003
* ci: enable verbose evals by @theomonnom in https://github.com/livekit/agents/pull/3004
* fix sensitive TTS tests by @theomonnom in https://github.com/livekit/agents/pull/3005

## New Contributors
* @levity made their first contribution in https://github.com/livekit/agents/pull/2805
* @CathyL0 made their first contribution in https://github.com/livekit/agents/pull/2948
* @ladvoc made their first contribution in https://github.com/livekit/agents/pull/2956
* @johncDepop made their first contribution in https://github.com/livekit/agents/pull/2964
* @bml1g12 made their first contribution in https://github.com/livekit/agents/pull/2967
* @karlson-anam made their first contribution in https://github.com/livekit/agents/pull/2938
* @Antonyesk601 made their first contribution in https://github.com/livekit/agents/pull/2923

**Full Changelog**: https://github.com/livekit/agents/compare/livekit-agents@1.2.0...livekit-agents@1.2.2

[View on GitHub](https://github.com/livekit/agents/releases/tag/livekit-agents%401.2.2)

---

## livekit-agents@1.2.0: livekit-agents@1.2.0
**Published:** 2025-07-17

## New Features

### Evals & Testing:

You can now perform turn-by-turn evaluations on your agent interactions. Here's an example of how to validate expected behaviors:

```python
result = await sess.run(user_input="Can I book an appointment? What's your availability for the next two weeks?")
result.expect.skip_next_event_if(type="message", role="assistant")
result.expect.next_event().is_function_call(name="list_available_slots")
result.expect.next_event().is_function_call_output()
await result.expect.next_event().is_message(role="assistant").judge(llm, intent="must confirm no availability")
```

Check out these practical examples: [drive-thru](https://github.com/livekit/agents/blob/f7672c0fe91ee68639cc49136040616f69034ded/examples/drive-thru/test_agent.py), [frontdesk](https://github.com/livekit/agents/blob/f7672c0fe91ee68639cc49136040616f69034ded/examples/frontdesk/test_agent.py)

Documentation: https://docs.livekit.io/agents/build/testing/

### Preemptive Generation

This feature enables speculative initiation of LLM and TTS processing before the user's turn concludes, significantly reducing response latency by overlapping processing with user audio. Disabled by default:

```python
session = AgentSession(..., preemptive_generation=True)
```

### Enhanced End-of-Turn (EOU) Detection

The end-of-turn model has been refined to reduce sensitivity to punctuation and better handle multilingual scenarios, notably improving Hindi language support.
'
Documentation: https://docs.livekit.io/agents/build/turns/turn-detector/#supported-languages

### OpenTelemetry Integration

Agent now supports tracing for LLM/TTS requests and user callbacks using OpenTelemetry. See [LangFuse example](https://github.com/livekit/agents/blob/f7672c0fe91ee68639cc49136040616f69034ded/examples/voice_agents/langfuse_trace.py) for detailed implementation.

### Experimental Agent Tasks

AgentTask is a new experimental subset feature allowing agents to terminate upon achieving specific goals. You can await AgentTasks directly in your workflows:

```python
@function_tool
async def schedule_appointment(self, ctx: RunContext[Userdata], slot_id: str) -> str:
    # Attempts to retrieve user email, allowing multiple agent-user interactions
    email_result = await beta.workflows.GetEmailTask(chat_ctx=self.chat_ctx)
```

### Half-Duplex Pipeline

Combine Gemini or OpenAI's realtime STT/LLM with a separate TTS engine, optimizing your agent's voice interactions:

```python
session = AgentSession(
    llm=openai.realtime.RealtimeModel(modalities=["text"]),
    # Alternatively: llm=google.beta.realtime.RealtimeModel(modalities=[Modality.TEXT]),
    tts=openai.TTS(voice="ash"),
)
```

View the [complete example](https://github.com/livekit/agents/blob/f7672c0fe91ee68639cc49136040616f69034ded/examples/voice_agents/realtime_with_tts.py).

Documentation: https://docs.livekit.io/agents/integrations/realtime/#separate-tts

### Improved Transcription Synchronization

Align transcripts accurately with speech outputs from TTS engines such as Cartesia and 11labs for improved synchronization:

```python
session = AgentSession(..., use_tts_aligned_transcript=True)
```

Refer to the [complete example](https://github.com/livekit/agents/blob/f7672c0fe91ee68639cc49136040616f69034ded/examples/voice_agents/timed_agent_transcript.py).

Documentation: https://docs.livekit.io/agents/build/text/#tts-aligned-transcriptions

### Upgraded Tokenization Engine

Transitioned to the Blingfire tokenization engine from the previous naive implementation, significantly enhancing handling and accuracy for multiple languages.


## Complete changelog
* introduce AgentTask by @theomonnom in https://github.com/livekit/agents/pull/2483
* introduce workflows & GetEmailAgent  by @theomonnom in https://github.com/livekit/agents/pull/2498
* drive-thru example by @theomonnom in https://github.com/livekit/agents/pull/2609
* reuse SpeechHandle for all generations inside a single turn by @theomonnom in https://github.com/livekit/agents/pull/2623
* introduce test & eval primitives by @theomonnom in https://github.com/livekit/agents/pull/2662
* evals: add maybe_* utils  by @theomonnom in https://github.com/livekit/agents/pull/2681
* evals: better error message for assertions  by @theomonnom in https://github.com/livekit/agents/pull/2682
* evals: RunResult final_output on Agent tasks  by @theomonnom in https://github.com/livekit/agents/pull/2696
* evals: AgentTask GetEmailAdress tests e.g by @theomonnom in https://github.com/livekit/agents/pull/2697
* allow optional RunResult output_type by @theomonnom in https://github.com/livekit/agents/pull/2698
* evals: add EventRangeAssert utils  by @theomonnom in https://github.com/livekit/agents/pull/2699
* add front-desk agent example by @theomonnom in https://github.com/livekit/agents/pull/2724
* fix InlineAgent agent resume on error by @theomonnom in https://github.com/livekit/agents/pull/2730
* add ChatContext.merge & merge inline tasks chat_ctx by @theomonnom in https://github.com/livekit/agents/pull/2731
* better GetEmailAgent instructions  by @theomonnom in https://github.com/livekit/agents/pull/2732
* exclude function_call inside ChatContext.merge by @theomonnom in https://github.com/livekit/agents/pull/2733
* add Blingfire tokenizer & use it by default  by @theomonnom in https://github.com/livekit/agents/pull/2771
* fix RealtimeModel generate_reply authorization by @theomonnom in https://github.com/livekit/agents/pull/2773
* support timed transcripts from tts by @longcw in https://github.com/livekit/agents/pull/2580
* ignore empty sentence in tts stream adapter by @longcw in https://github.com/livekit/agents/pull/2777
* fix types for agents 1.2 by @longcw in https://github.com/livekit/agents/pull/2778
* fix MockTools type by @longcw in https://github.com/livekit/agents/pull/2781
* fix RunResult order of fnc_call & agent_handoff by @theomonnom in https://github.com/livekit/agents/pull/2782
* fix types by @theomonnom in https://github.com/livekit/agents/pull/2783
* fix tr_input  by @theomonnom in https://github.com/livekit/agents/pull/2784
* fix GetEmailAgent instructions by @theomonnom in https://github.com/livekit/agents/pull/2786
* fix blingfire tokenizer test by @longcw in https://github.com/livekit/agents/pull/2785
* support tts with realtime model (audio in, text out) by @longcw in https://github.com/livekit/agents/pull/2628
* fix assistant message order on the RunResult by @theomonnom in https://github.com/livekit/agents/pull/2787
* fix FrontDeskAgent list_available_slots by @theomonnom in https://github.com/livekit/agents/pull/2788
* initial evals for the FrontDesk agent  by @theomonnom in https://github.com/livekit/agents/pull/2790
* ignore empty assistant messages  by @theomonnom in https://github.com/livekit/agents/pull/2792
* evals: add CI by @theomonnom in https://github.com/livekit/agents/pull/2791
* evals ci: use python 3.12 by @theomonnom in https://github.com/livekit/agents/pull/2793
* fix confirmation/validation ambiguity on GetEmailAgent instructions  by @theomonnom in https://github.com/livekit/agents/pull/2794
* punctuation free turn detector by @jeradf in https://github.com/livekit/agents/pull/2717
* frontdesk: ToolError example  by @theomonnom in https://github.com/livekit/agents/pull/2808
* evals API improvements by @theomonnom in https://github.com/livekit/agents/pull/2846
* make arguments optional for mock_tools by @theomonnom in https://github.com/livekit/agents/pull/2847
* allow returning Exception inside function tools by @theomonnom in https://github.com/livekit/agents/pull/2848
* add envvar to enable verbose evals logs by @theomonnom in https://github.com/livekit/agents/pull/2849
* preemptive generation before end of user turn by @longcw in https://github.com/livekit/agents/pull/2728
* fix next_event return type by @theomonnom in https://github.com/livekit/agents/pull/2856
* evals: add docstrings to the public API  by @theomonnom in https://github.com/livekit/agents/pull/2857
* only print the judge result when verbose is enabled by @theomonnom in https://github.com/livekit/agents/pull/2858
* Add contains_agent_handoff assertion by @bcherry in https://github.com/livekit/agents/pull/2862
* allow editing SpeechHandle allow_interruptions & add RunContext.disallow_interruptions by @theomonnom in https://github.com/livekit/agents/pull/2864
* fix evals test by @theomonnom in https://github.com/livekit/agents/pull/2865
* fix ruff and types by @longcw in https://github.com/livekit/agents/pull/2889
* add opentelemetry trace by @longcw in https://github.com/livekit/agents/pull/2873
* fix unordered user messages by @theomonnom in https://github.com/livekit/agents/pull/2891
* fix livekit-agents 1.2 tests by @theomonnom in https://github.com/livekit/agents/pull/2866
* cleanup & prepare for release by @theomonnom in https://github.com/livekit/agents/pull/2893
* add prometheus by @theomonnom in https://github.com/livekit/agents/pull/2908
* add gen_ai attributes to llm_request by @longcw in https://github.com/livekit/agents/pull/2905
* fix types and aws realtime model by @longcw in https://github.com/livekit/agents/pull/2910
* fix TTS fallback adapter metrics_collected event by @longcw in https://github.com/livekit/agents/pull/2890
* add model property for llm plugins by @longcw in https://github.com/livekit/agents/pull/2914
* nit: mprove drivethru by @theomonnom in https://github.com/livekit/agents/pull/2918
* Removing ctx.connect() from examples by @sascotto in https://github.com/livekit/agents/pull/2909
* expose tokenizer option for cartesia tts by @longcw in https://github.com/livekit/agents/pull/2916
* remove openai prewarm by @theomonnom in https://github.com/livekit/agents/pull/2919
* add tts_audio_duration to usage metrics collection by @Panmax in https://github.com/livekit/agents/pull/2915
* [DRAFT] Add inference process health check endpoint by @alfredguiaugment in https://github.com/livekit/agents/pull/2906
* only check inference process health if started by @theomonnom in https://github.com/livekit/agents/pull/2920
* fix missing field in UsageCollector by @davidzhao in https://github.com/livekit/agents/pull/2929
* fix ruff & bump livekit-agents 1.2.0 by @theomonnom in https://github.com/livekit/agents/pull/2936

## New Contributors
* @sascotto made their first contribution in https://github.com/livekit/agents/pull/2909

**Full Changelog**: https://github.com/livekit/agents/compare/livekit-agents@1.1.7...livekit-agents@1.2.0

[View on GitHub](https://github.com/livekit/agents/releases/tag/livekit-agents%401.2.0)

---

## livekit-agents@1.1.7: livekit-agents@1.1.7
**Published:** 2025-07-15

## What's Changed
* fix log extra field handling in log.py by @Panmax in https://github.com/livekit/agents/pull/2875
* fix aws realtime model types by @longcw in https://github.com/livekit/agents/pull/2877
* chore: export PlayHandle type by @davidzhao in https://github.com/livekit/agents/pull/2903
* fix gemini realtime user transcription sent twice by @longcw in https://github.com/livekit/agents/pull/2899
* append framework ID to User-Agent Header by @BumaldaOverTheWater94 in https://github.com/livekit/agents/pull/2896
* add gemini tts (beta) by @longcw in https://github.com/livekit/agents/pull/2834
* fix DatastreamIO cancellation race by @theomonnom in https://github.com/livekit/agents/pull/2911
* DataStreamIO wait for start when capturing_frame by @theomonnom in https://github.com/livekit/agents/pull/2912


**Full Changelog**: https://github.com/livekit/agents/compare/livekit-agents@1.1.6...livekit-agents@1.1.7

[View on GitHub](https://github.com/livekit/agents/releases/tag/livekit-agents%401.1.7)

---

## livekit-agents@1.1.6: livekit-agents@1.1.6
**Published:** 2025-07-10

## What's Changed
* Fix LMNT plugin docs by @zachoverflow in https://github.com/livekit/agents/pull/2762
* Update new plugin readmes for format and links by @bcherry in https://github.com/livekit/agents/pull/2571
* fix update_chat_ctx bug by @BumaldaOverTheWater94 in https://github.com/livekit/agents/pull/2763
* Include item id when converting to LG messages by @dkeller-sondermind in https://github.com/livekit/agents/pull/2767
* fix schedule speech on windows when monotonic_ns resolution is rough by @longcw in https://github.com/livekit/agents/pull/2770
* Install optional dependencies during docs gen by @bcherry in https://github.com/livekit/agents/pull/2766
* Feat/mistralai plugins by @fabitokki in https://github.com/livekit/agents/pull/2772
* fix docker-compose typo by @theomonnom in https://github.com/livekit/agents/pull/2789
* suppress main_stream ended error in stt fallback adapter by @longcw in https://github.com/livekit/agents/pull/2684
* [fix] Fixed Orus voice name definition by @Is44m in https://github.com/livekit/agents/pull/2797
* fix aws sonic type checking by @longcw in https://github.com/livekit/agents/pull/2804
* fix deepgram stt docs by @longcw in https://github.com/livekit/agents/pull/2803
* Hotfix for Baseten STT by @htrivedi99 in https://github.com/livekit/agents/pull/2801
* fix inactive user instructions by @theomonnom in https://github.com/livekit/agents/pull/2809
* fix BackgroundAudio hanging on close error  by @theomonnom in https://github.com/livekit/agents/pull/2814
* reset closing_ws for openai stt by @longcw in https://github.com/livekit/agents/pull/2813
* avoid sid error in console mode by @theomonnom in https://github.com/livekit/agents/pull/2815
* ignore livekit api when using console mode  by @theomonnom in https://github.com/livekit/agents/pull/2816
* Feature : Add audio_mixer_kwargs to BackgroundAudioPlayer by @CyprienRicqueB2L in https://github.com/livekit/agents/pull/2796
* fix FunctionToolsExecutedEvent import by @longcw in https://github.com/livekit/agents/pull/2832
* feat: ability to use remote EOT inference when deployed in Cloud by @davidzhao in https://github.com/livekit/agents/pull/2780
* Add support for CustomPronunciations in Google TTS plugin by @kechako in https://github.com/livekit/agents/pull/2692
* Nova Sonic Example Agent by @BumaldaOverTheWater94 in https://github.com/livekit/agents/pull/2817
* Prevent console mode from crashing by @donalffons in https://github.com/livekit/agents/pull/2853
* Small fix to README by @kath0la in https://github.com/livekit/agents/pull/2861
* Fix: Use synchronized transcript for interrupted session.say() responses by @eliotsamuelmiller in https://github.com/livekit/agents/pull/2843
* fix aws sonic tools  by @theomonnom in https://github.com/livekit/agents/pull/2859
* log metrics in extra by @theomonnom in https://github.com/livekit/agents/pull/2868
* accidentally omit a docstring by @BumaldaOverTheWater94 in https://github.com/livekit/agents/pull/2869

## New Contributors
* @zachoverflow made their first contribution in https://github.com/livekit/agents/pull/2762
* @dkeller-sondermind made their first contribution in https://github.com/livekit/agents/pull/2767
* @fabitokki made their first contribution in https://github.com/livekit/agents/pull/2772
* @Is44m made their first contribution in https://github.com/livekit/agents/pull/2797
* @donalffons made their first contribution in https://github.com/livekit/agents/pull/2853
* @eliotsamuelmiller made their first contribution in https://github.com/livekit/agents/pull/2843

**Full Changelog**: https://github.com/livekit/agents/compare/livekit-agents@1.1.5...livekit-agents@1.1.6

[View on GitHub](https://github.com/livekit/agents/releases/tag/livekit-agents%401.1.6)

---

## livekit-agents@1.1.5: livekit-agents@1.1.5
**Published:** 2025-06-30

## What's Changed
* Preserve original path when connecting to web socket (fix for #2700) by @arpesenti in https://github.com/livekit/agents/pull/2702
* disconnect room when session closed due to participant disconnected by @longcw in https://github.com/livekit/agents/pull/2712
* make sure audio_output.flush called when capture frame failed by @longcw in https://github.com/livekit/agents/pull/2718
* Update Inworld README by @ShayneP in https://github.com/livekit/agents/pull/2723
* Updating whisper API by @htrivedi99 in https://github.com/livekit/agents/pull/2726
* Lock google-genai package to stable v1.20.0 by @simplegr33n in https://github.com/livekit/agents/pull/2725
* fix(google): pass in raw schema according to genai 1.20 spec by @davidzhao in https://github.com/livekit/agents/pull/2727
* feat(google): expose seed parameter in LLM.chat by @mrkowalski in https://github.com/livekit/agents/pull/2721
* upgrade google genai to 1.23 by @longcw in https://github.com/livekit/agents/pull/2743
* support 11labs auto mode with sentence tokenizer by @longcw in https://github.com/livekit/agents/pull/2744
* add livekit-blingfire by @theomonnom in https://github.com/livekit/agents/pull/2734
* remove changesets by @theomonnom in https://github.com/livekit/agents/pull/2749
* uv: ignore blingfire  by @theomonnom in https://github.com/livekit/agents/pull/2750
* fix aggregate-dumps when no file is present by @theomonnom in https://github.com/livekit/agents/pull/2751
* run tts tests on top10 providers by @theomonnom in https://github.com/livekit/agents/pull/2752
* delete changesets x2 by @theomonnom in https://github.com/livekit/agents/pull/2753
* add build CI  by @theomonnom in https://github.com/livekit/agents/pull/2754
* fix blingfire build CI by @theomonnom in https://github.com/livekit/agents/pull/2756
* BlingFire: use Release config on Windows  by @theomonnom in https://github.com/livekit/agents/pull/2757
* build blingfire for macos x86 & linux arm64 by @theomonnom in https://github.com/livekit/agents/pull/2758
* Nova Sonic Realtime Plugin by @BumaldaOverTheWater94 in https://github.com/livekit/agents/pull/2740
* keep aws nova sonic optional by @theomonnom in https://github.com/livekit/agents/pull/2760

## New Contributors
* @arpesenti made their first contribution in https://github.com/livekit/agents/pull/2702
* @mrkowalski made their first contribution in https://github.com/livekit/agents/pull/2721

**Full Changelog**: https://github.com/livekit/agents/compare/livekit-agents@1.1.4...livekit-agents@1.1.5

[View on GitHub](https://github.com/livekit/agents/releases/tag/livekit-agents%401.1.5)

---

## livekit-agents@1.1.4: livekit-agents@1.1.4
**Published:** 2025-06-25

## What's Changed
* add --ignore-changesets to update_versions.py by @theomonnom in https://github.com/livekit/agents/pull/2665
* remove frame_size_ms param when creating AudioStream by @longcw in https://github.com/livekit/agents/pull/2667
* Gladia STT - add new parameters to gladia stt by @mfernandez-gladia in https://github.com/livekit/agents/pull/2649
* expose automatic_function_calling config for google LLM by @longcw in https://github.com/livekit/agents/pull/2675
* start user away timer after user join by @longcw in https://github.com/livekit/agents/pull/2676
* preserve created_at timestamp when updating instructions by @Panmax in https://github.com/livekit/agents/pull/2677
* use parameters_json_schema for raw function tool with google LLM by @longcw in https://github.com/livekit/agents/pull/2686
* import TextInputEvent from room_io by @longcw in https://github.com/livekit/agents/pull/2679
* reset agent and user state after session closed by @longcw in https://github.com/livekit/agents/pull/2691
* Add hedra extra by @bcherry in https://github.com/livekit/agents/pull/2705
* add markdown filter for tts and transcription nodes by @longcw in https://github.com/livekit/agents/pull/2695
* Fix Example Typo by @toubatbrian in https://github.com/livekit/agents/pull/2706
* Inworld TTS by @davidzhao in https://github.com/livekit/agents/pull/2693
* add warning for deprecated speed and emotion control for cartesia tts by @longcw in https://github.com/livekit/agents/pull/2708
* fix(plugins-inworld): change default voice to Ashley by @MichaelSolati in https://github.com/livekit/agents/pull/2707
* deepgram: disable smart_format by default by @theomonnom in https://github.com/livekit/agents/pull/2704
* livekit-agents 1.1.4 by @theomonnom in https://github.com/livekit/agents/pull/2709

## New Contributors
* @mfernandez-gladia made their first contribution in https://github.com/livekit/agents/pull/2649
* @Panmax made their first contribution in https://github.com/livekit/agents/pull/2677
* @MichaelSolati made their first contribution in https://github.com/livekit/agents/pull/2707

**Full Changelog**: https://github.com/livekit/agents/compare/livekit-agents@1.1.2...livekit-agents@1.1.4

[View on GitHub](https://github.com/livekit/agents/releases/tag/livekit-agents%401.1.4)

---

## livekit-agents@1.1.2: livekit-agents@1.1.2
**Published:** 2025-06-20

## What's Changed
* Add spitch optional dependency by @temibabs in https://github.com/livekit/agents/pull/2559
* add Cartesia STT usage event by @ChenghaoMou in https://github.com/livekit/agents/pull/2565
* use the cgroup cpu_count for the inference thread pool by @theomonnom in https://github.com/livekit/agents/pull/2572
* avoid possible contention on concurrent inference executions  by @theomonnom in https://github.com/livekit/agents/pull/2575
* use onnx dynamic_block_base by @theomonnom in https://github.com/livekit/agents/pull/2578
* add vad for stt FallbackAdapter by @longcw in https://github.com/livekit/agents/pull/2582
* Don't require sarvam api key param for TTS by @bcherry in https://github.com/livekit/agents/pull/2579
* Remove unnecessary model param from baseten tts by @bcherry in https://github.com/livekit/agents/pull/2568
* Fix baseten STT api key lookup by @bcherry in https://github.com/livekit/agents/pull/2576
* fix stt fallback adapter imports by @longcw in https://github.com/livekit/agents/pull/2590
* Replace the office-ambience sound file by @bcherry in https://github.com/livekit/agents/pull/2588
* chore(deepgram,cartesia): removed AudioEnergyFilter by @davidzhao in https://github.com/livekit/agents/pull/2594
* unit tests for agent session by @longcw in https://github.com/livekit/agents/pull/2518
* fix unknown energy filter parameter by @theomonnom in https://github.com/livekit/agents/pull/2599
* fix type check by @longcw in https://github.com/livekit/agents/pull/2596
* wait for final transcript in manual turn detection by @longcw in https://github.com/livekit/agents/pull/2597
* add volume gain option by @jmugicagonz in https://github.com/livekit/agents/pull/2603
* increase audio frame size  by @theomonnom in https://github.com/livekit/agents/pull/2610
* Add SSML support for Google TTS by @kechako in https://github.com/livekit/agents/pull/2608
* fix OpenAI Realtime connect timeout by @theomonnom in https://github.com/livekit/agents/pull/2612
* fix OpenAI Realtime tool_choice by @theomonnom in https://github.com/livekit/agents/pull/2613
* add transcript_confidence to ChatMessage by @theomonnom in https://github.com/livekit/agents/pull/2611
* fix(turn-detector): improve accuracy by combining adjacent turns by @davidzhao in https://github.com/livekit/agents/pull/2595
* fix transcription delay when VAD false negative by @longcw in https://github.com/livekit/agents/pull/2620
* Hume plugin fixes by @zgreathouse in https://github.com/livekit/agents/pull/2591
* Updating metrics for cached tokens for Realtime model (OpenAI) by @tg-bomze in https://github.com/livekit/agents/pull/2621
* Disable ensure_ascii by @tg-bomze in https://github.com/livekit/agents/pull/2622
* add timeout for agent session tests by @longcw in https://github.com/livekit/agents/pull/2624
* add error log when llm fallback adapter failed because chunk_sent by @longcw in https://github.com/livekit/agents/pull/2626
* fix ChatContext.insert type check by @theomonnom in https://github.com/livekit/agents/pull/2635
* Removes the split_utterances option from Hume TTS plugin by @zgreathouse in https://github.com/livekit/agents/pull/2638
* wait for video track from avatar plugins by @longcw in https://github.com/livekit/agents/pull/2627
* add http_options for gemini LLM and realtime model by @longcw in https://github.com/livekit/agents/pull/2640
* correctly passing speaking_rate to StreamingAudioConfig by @david-rodriguez in https://github.com/livekit/agents/pull/2631
* Fix : Increase audio mixer timeout by @CyprienRicqueB2L in https://github.com/livekit/agents/pull/2646
* handling multiple audio chunk output by @raghavjaistra in https://github.com/livekit/agents/pull/2641
* Fix Hume TTS by @bcherry in https://github.com/livekit/agents/pull/2639
* Update sarvam defaults, add 2.5 by @bcherry in https://github.com/livekit/agents/pull/2618
* fix tracing param in openai realtime by @longcw in https://github.com/livekit/agents/pull/2652
* raise error from gladia stt for fallback adapter and retry by @longcw in https://github.com/livekit/agents/pull/2653
* fix await tasks groups never return by @longcw in https://github.com/livekit/agents/pull/2654
* chore: add note for job_context.api usage by @davidzhao in https://github.com/livekit/agents/pull/2655
* fix(google): update dependency versions by @davidzhao in https://github.com/livekit/agents/pull/2658
* feat(baseten): add LLM module by @davidzhao in https://github.com/livekit/agents/pull/2657
* cleanup tee in agent activity by @longcw in https://github.com/livekit/agents/pull/2660
* fix duplicated audio on flush by @theomonnom in https://github.com/livekit/agents/pull/2663
* fix transcription sync warning when gemini no text output by @longcw in https://github.com/livekit/agents/pull/2661
* livekit-agents v1.1.2 by @theomonnom in https://github.com/livekit/agents/pull/2664

## New Contributors
* @tg-bomze made their first contribution in https://github.com/livekit/agents/pull/2621
* @david-rodriguez made their first contribution in https://github.com/livekit/agents/pull/2631
* @CyprienRicqueB2L made their first contribution in https://github.com/livekit/agents/pull/2646
* @raghavjaistra made their first contribution in https://github.com/livekit/agents/pull/2641

**Full Changelog**: https://github.com/livekit/agents/compare/livekit-agents@1.1.0...livekit-agents@1.1.2

[View on GitHub](https://github.com/livekit/agents/releases/tag/livekit-agents%401.1.2)

---

## livekit-agents@1.1.0: livekit-agents@1.1.0
**Published:** 2025-06-10

## What's Changed
* TTS improvements & tests  by @theomonnom in https://github.com/livekit/agents/pull/2152
* rewrite Azure TTS by @theomonnom in https://github.com/livekit/agents/pull/2151
* fix google TTS  by @theomonnom in https://github.com/livekit/agents/pull/2410
* add to_provider_format for ChatContext by @longcw in https://github.com/livekit/agents/pull/2295
* automatically close agent session when participant disconnected by @longcw in https://github.com/livekit/agents/pull/2398
* fix type checks and tts fallback adapter by @longcw in https://github.com/livekit/agents/pull/2419
* deprecate multi-segments SynthesizeStream  by @theomonnom in https://github.com/livekit/agents/pull/2421
* cartesia: fix break by @theomonnom in https://github.com/livekit/agents/pull/2422
* avoid raising tts empty errors when pushed text is empty by @longcw in https://github.com/livekit/agents/pull/2420
* don't error when pushing on closed stream by @theomonnom in https://github.com/livekit/agents/pull/2424
* Add diarization support by @ShayneP in https://github.com/livekit/agents/pull/2338
* fix gemini user transcription when tool calls by @longcw in https://github.com/livekit/agents/pull/2439
* skip response if no llm set in user turn completed by @longcw in https://github.com/livekit/agents/pull/2441
* fix type checks for plugins by @longcw in https://github.com/livekit/agents/pull/2423
* Fix SpeechHandle Priority Schedule by @toubatbrian in https://github.com/livekit/agents/pull/2433
* use time.monotonic_ns for speech scheduling by @theomonnom in https://github.com/livekit/agents/pull/2446
* fix transcription sync when on_playback_finished missing after flush by @longcw in https://github.com/livekit/agents/pull/2397
* LMNT agent plugin for TTS synthesis by @naiveen in https://github.com/livekit/agents/pull/2413
* fix agent state for pipeline agent by @longcw in https://github.com/livekit/agents/pull/2453
* add max_session_duration and auto reconnection for OAI realtime api by @longcw in https://github.com/livekit/agents/pull/2360
* avatar publish video after waiting participant by @longcw in https://github.com/livekit/agents/pull/2450
* PlayAI plugin: fix language tag by @bryananderson in https://github.com/livekit/agents/pull/2458
* Update README.md by @theomonnom in https://github.com/livekit/agents/pull/2466
* fixed identifying streamable http mcp servers containing api key in url by @Akshay-a in https://github.com/livekit/agents/pull/2468
* fix(google): Live syncs context, supports manual turns by @davidzhao in https://github.com/livekit/agents/pull/2401
* AssemblyAI Remove Hardcoded Default Configuration by @dan-ince-aai in https://github.com/livekit/agents/pull/2456
* add duration_per_frame for datastream audio receiver by @longcw in https://github.com/livekit/agents/pull/2474
* add logs after session closed by @longcw in https://github.com/livekit/agents/pull/2479
* rename to frame_size_ms for data stream audio receiver by @longcw in https://github.com/livekit/agents/pull/2481
* chore(assemblyai): renaming to format_turns and only emit formatted f… by @dan-ince-aai in https://github.com/livekit/agents/pull/2485
* fix optional args in Annotated argument by @longcw in https://github.com/livekit/agents/pull/2491
* fix text only example by @longcw in https://github.com/livekit/agents/pull/2490
* add artificial delay between consecutive speech handles by @longcw in https://github.com/livekit/agents/pull/2492
* Support for Spitch in LiveKit by @temibabs in https://github.com/livekit/agents/pull/2430
* detect inactive user example  by @theomonnom in https://github.com/livekit/agents/pull/2499
* recover from incorrect LLM arguments in function_tool by @theomonnom in https://github.com/livekit/agents/pull/2500
* add max_unrecoverable_errors and connection options for agent session by @longcw in https://github.com/livekit/agents/pull/2494
* Collect prompt cached tokens count in llm usage in AWS LLM plugin by @alfredguiaugment in https://github.com/livekit/agents/pull/2508
* fix tts fallback adapter test and stream adapter by @longcw in https://github.com/livekit/agents/pull/2514
* add hedra plugin by @longcw in https://github.com/livekit/agents/pull/2163
* Fix broken link in silero readme by @bcherry in https://github.com/livekit/agents/pull/2521
* fix(google): proactivity and affective_dialog require v1alpha1 API by @davidzhao in https://github.com/livekit/agents/pull/2523
* fix: LLM to honor custom timeouts by @davidzhao in https://github.com/livekit/agents/pull/2526
* ignore empty assistant messages by @theomonnom in https://github.com/livekit/agents/pull/2530
* feat(openai): strip thinking tokens by @davidzhao in https://github.com/livekit/agents/pull/2524
* Fix typo in cerebras error msg by @bcherry in https://github.com/livekit/agents/pull/2531
* feat: surface tavus conversation id by @mertgerdan in https://github.com/livekit/agents/pull/2532
* feat: langgraph integration by @davidzhao in https://github.com/livekit/agents/pull/2534
* cleanup bithuman when process shutdown by @longcw in https://github.com/livekit/agents/pull/2536
* add eleven labs v3 model by @choso in https://github.com/livekit/agents/pull/2540
* lmnt: Update default voice, add temperature, topp options by @naiveen in https://github.com/livekit/agents/pull/2539
* Add Cartesia STT integration by @DineshTeja in https://github.com/livekit/agents/pull/2538
* Baseten Livekit plugin integration by @htrivedi99 in https://github.com/livekit/agents/pull/2520
* feat: Sarvam.ai plugin for STT and TTS  by @AnshTanwar in https://github.com/livekit/agents/pull/2241
* chore: tweaks to plugins CI by @davidzhao in https://github.com/livekit/agents/pull/2543
* use not given for room io options by @longcw in https://github.com/livekit/agents/pull/2542
* Add new speed and tracing options to OpenAI RealtimeModel and RealtimeSession by @mikevin920 in https://github.com/livekit/agents/pull/2503
* add connect options and error retry for realtime model by @longcw in https://github.com/livekit/agents/pull/2544
* initial prewarm by @theomonnom in https://github.com/livekit/agents/pull/2527
* bithuman avatar refresh token after prewarm by @longcw in https://github.com/livekit/agents/pull/2541
* ignore prewarm failures by @theomonnom in https://github.com/livekit/agents/pull/2545
* run room_io.start and ctx.connect concurrently in session.start by @longcw in https://github.com/livekit/agents/pull/2505
* convert TracingOptions for session updates by @theomonnom in https://github.com/livekit/agents/pull/2546
* use pyht SDK by @theomonnom in https://github.com/livekit/agents/pull/2459
* update x.ai models by @theomonnom in https://github.com/livekit/agents/pull/2547
* cancel tasks on start failure by @theomonnom in https://github.com/livekit/agents/pull/2548
* livekit-agents v1.1.0 by @theomonnom in https://github.com/livekit/agents/pull/2549

## New Contributors
* @dan-ince-aai made their first contribution in https://github.com/livekit/agents/pull/2399
* @toubatbrian made their first contribution in https://github.com/livekit/agents/pull/2433
* @naiveen made their first contribution in https://github.com/livekit/agents/pull/2413
* @temibabs made their first contribution in https://github.com/livekit/agents/pull/2430
* @alfredguiaugment made their first contribution in https://github.com/livekit/agents/pull/2508
* @mertgerdan made their first contribution in https://github.com/livekit/agents/pull/2532
* @choso made their first contribution in https://github.com/livekit/agents/pull/2540
* @DineshTeja made their first contribution in https://github.com/livekit/agents/pull/2538
* @htrivedi99 made their first contribution in https://github.com/livekit/agents/pull/2520
* @AnshTanwar made their first contribution in https://github.com/livekit/agents/pull/2241
* @mikevin920 made their first contribution in https://github.com/livekit/agents/pull/2503

**Full Changelog**: https://github.com/livekit/agents/compare/livekit-agents@1.0.23...livekit-agents@1.1.0

[View on GitHub](https://github.com/livekit/agents/releases/tag/livekit-agents%401.1.0)

---

## livekit-agents@1.0.23: livekit-agents@1.0.23
**Published:** 2025-05-29

## What's Changed
* Support empty array of parameters when using raw_schema by @koen-boost in https://github.com/livekit/agents/pull/2328
* fix: avoid shadowing name in function_tool decorator by @davidzhao in https://github.com/livekit/agents/pull/2331
* feat: Add `with_letta` OpenAI plugin by @mattzh72 in https://github.com/livekit/agents/pull/2182
* fix tool choice by @jayeshp19 in https://github.com/livekit/agents/pull/2332
* Expose all realtime model parameters by @Shubhrakanti in https://github.com/livekit/agents/pull/2324
* add prewarm to bithuman avatar example by @longcw in https://github.com/livekit/agents/pull/2337
* fix agent transcription truncate for console mode by @longcw in https://github.com/livekit/agents/pull/2327
* fix chat context item order by @longcw in https://github.com/livekit/agents/pull/2321
* google: add new models to LLM and live by @davidzhao in https://github.com/livekit/agents/pull/2344
* handle missing token_count in realtime usage metrics by @fredvollmer in https://github.com/livekit/agents/pull/2350
* [Rime] Increase timeout for `arcana` model to allow for synthesis of long audio  by @MaCaki in https://github.com/livekit/agents/pull/2343
* google: do not error when empty responses are returned by @davidzhao in https://github.com/livekit/agents/pull/2345
* fix type check by @longcw in https://github.com/livekit/agents/pull/2335
* add internal worker token by @real-danm in https://github.com/livekit/agents/pull/2354
* Add input_audio_noise_reduction to OpenAI RealtimeModel by @RBT22 in https://github.com/livekit/agents/pull/2362
* Setting openai temperature on `LLM.chat` by @free-soellingeraj in https://github.com/livekit/agents/pull/2353
* on_end_of_turn is sync by @theomonnom in https://github.com/livekit/agents/pull/2374
* multilingual model update by @jeradf in https://github.com/livekit/agents/pull/2219
* ignore any_generics for mypy by @longcw in https://github.com/livekit/agents/pull/2375
* rename insert_item to insert by @theomonnom in https://github.com/livekit/agents/pull/2372
* support stt END_OF_SPEECH for stt turn detection by @longcw in https://github.com/livekit/agents/pull/2363
* Implemented #2379 - Add support for more paramaters for Google Live API by @F1nnM in https://github.com/livekit/agents/pull/2380
* disable split characters for tts by @longcw in https://github.com/livekit/agents/pull/2366
* google: fix proactive audio config, update genai by @davidzhao in https://github.com/livekit/agents/pull/2390
* fix race condition in avatar runner when reset playback_position by @longcw in https://github.com/livekit/agents/pull/2396
* set user state to away after a timeout by @longcw in https://github.com/livekit/agents/pull/2408
* add MCP support for streamable HTTP client by @Akshay-a in https://github.com/livekit/agents/pull/2394
* Upgrade AssemblyAI to Universal-Streaming by @dan-ince-aai in https://github.com/livekit/agents/pull/2399
* fix AssemblyAI & follow docs by @theomonnom in https://github.com/livekit/agents/pull/2445

## New Contributors
* @koen-boost made their first contribution in https://github.com/livekit/agents/pull/2328
* @mattzh72 made their first contribution in https://github.com/livekit/agents/pull/2182
* @fredvollmer made their first contribution in https://github.com/livekit/agents/pull/2350
* @real-danm made their first contribution in https://github.com/livekit/agents/pull/2354
* @RBT22 made their first contribution in https://github.com/livekit/agents/pull/2362
* @free-soellingeraj made their first contribution in https://github.com/livekit/agents/pull/2353
* @F1nnM made their first contribution in https://github.com/livekit/agents/pull/2380
* @Akshay-a made their first contribution in https://github.com/livekit/agents/pull/2394
* @dan-ince-aai made their first contribution in https://github.com/livekit/agents/pull/2399

**Full Changelog**: https://github.com/livekit/agents/compare/livekit-agents@1.0.22...livekit-agents@1.0.23

[View on GitHub](https://github.com/livekit/agents/releases/tag/livekit-agents%401.0.23)

---

## livekit-plugins-turn-detector@0.4.5: livekit-plugins-turn-detector@0.4.5
**Published:** 2025-05-18

### Patch Changes

-   update to livekit python 1.0 - [`32e129ff1a4c3d28f363f4f2b2a355e29c8fe64d`](https://github.com/livekit/agents/commit/32e129ff1a4c3d28f363f4f2b2a355e29c8fe64d) ([@davidzhao](https://github.com/davidzhao))


[View on GitHub](https://github.com/livekit/agents/releases/tag/livekit-plugins-turn-detector%400.4.5)

---

## livekit-plugins-speechmatics@0.0.3: livekit-plugins-speechmatics@0.0.3
**Published:** 2025-05-18

### Patch Changes

-   update to livekit python 1.0 - [`32e129ff1a4c3d28f363f4f2b2a355e29c8fe64d`](https://github.com/livekit/agents/commit/32e129ff1a4c3d28f363f4f2b2a355e29c8fe64d) ([@davidzhao](https://github.com/davidzhao))


[View on GitHub](https://github.com/livekit/agents/releases/tag/livekit-plugins-speechmatics%400.0.3)

---

## livekit-plugins-silero@0.7.6: livekit-plugins-silero@0.7.6
**Published:** 2025-05-18

### Patch Changes

-   update to livekit python 1.0 - [`32e129ff1a4c3d28f363f4f2b2a355e29c8fe64d`](https://github.com/livekit/agents/commit/32e129ff1a4c3d28f363f4f2b2a355e29c8fe64d) ([@davidzhao](https://github.com/davidzhao))


[View on GitHub](https://github.com/livekit/agents/releases/tag/livekit-plugins-silero%400.7.6)

---

## livekit-plugins-rime@0.2.3: livekit-plugins-rime@0.2.3
**Published:** 2025-05-18

### Patch Changes

-   update to livekit python 1.0 - [`32e129ff1a4c3d28f363f4f2b2a355e29c8fe64d`](https://github.com/livekit/agents/commit/32e129ff1a4c3d28f363f4f2b2a355e29c8fe64d) ([@davidzhao](https://github.com/davidzhao))


[View on GitHub](https://github.com/livekit/agents/releases/tag/livekit-plugins-rime%400.2.3)

---

## livekit-plugins-resemble@0.1.2: livekit-plugins-resemble@0.1.2
**Published:** 2025-05-18

### Patch Changes

-   update to livekit python 1.0 - [`32e129ff1a4c3d28f363f4f2b2a355e29c8fe64d`](https://github.com/livekit/agents/commit/32e129ff1a4c3d28f363f4f2b2a355e29c8fe64d) ([@davidzhao](https://github.com/davidzhao))


[View on GitHub](https://github.com/livekit/agents/releases/tag/livekit-plugins-resemble%400.1.2)

---

## livekit-plugins-rag@0.2.5: livekit-plugins-rag@0.2.5
**Published:** 2025-05-18

### Patch Changes

-   update to livekit python 1.0 - [`32e129ff1a4c3d28f363f4f2b2a355e29c8fe64d`](https://github.com/livekit/agents/commit/32e129ff1a4c3d28f363f4f2b2a355e29c8fe64d) ([@davidzhao](https://github.com/davidzhao))


[View on GitHub](https://github.com/livekit/agents/releases/tag/livekit-plugins-rag%400.2.5)

---

## livekit-plugins-playai@1.0.10: livekit-plugins-playai@1.0.10
**Published:** 2025-05-18

### Patch Changes

-   update to livekit python 1.0 - [`32e129ff1a4c3d28f363f4f2b2a355e29c8fe64d`](https://github.com/livekit/agents/commit/32e129ff1a4c3d28f363f4f2b2a355e29c8fe64d) ([@davidzhao](https://github.com/davidzhao))


[View on GitHub](https://github.com/livekit/agents/releases/tag/livekit-plugins-playai%401.0.10)

---

## livekit-plugins-openai@0.12.4: livekit-plugins-openai@0.12.4
**Published:** 2025-05-18

### Patch Changes

-   update to livekit python 1.0 - [`32e129ff1a4c3d28f363f4f2b2a355e29c8fe64d`](https://github.com/livekit/agents/commit/32e129ff1a4c3d28f363f4f2b2a355e29c8fe64d) ([@davidzhao](https://github.com/davidzhao))


[View on GitHub](https://github.com/livekit/agents/releases/tag/livekit-plugins-openai%400.12.4)

---

## livekit-plugins-nltk@0.7.5: livekit-plugins-nltk@0.7.5
**Published:** 2025-05-18

### Patch Changes

-   update to livekit python 1.0 - [`32e129ff1a4c3d28f363f4f2b2a355e29c8fe64d`](https://github.com/livekit/agents/commit/32e129ff1a4c3d28f363f4f2b2a355e29c8fe64d) ([@davidzhao](https://github.com/davidzhao))


[View on GitHub](https://github.com/livekit/agents/releases/tag/livekit-plugins-nltk%400.7.5)

---

## livekit-plugins-neuphonic@0.1.2: livekit-plugins-neuphonic@0.1.2
**Published:** 2025-05-18

### Patch Changes

-   update to livekit python 1.0 - [`32e129ff1a4c3d28f363f4f2b2a355e29c8fe64d`](https://github.com/livekit/agents/commit/32e129ff1a4c3d28f363f4f2b2a355e29c8fe64d) ([@davidzhao](https://github.com/davidzhao))


[View on GitHub](https://github.com/livekit/agents/releases/tag/livekit-plugins-neuphonic%400.1.2)

---

## livekit-plugins-minimal@0.2.3: livekit-plugins-minimal@0.2.3
**Published:** 2025-05-18

### Patch Changes

-   update to livekit python 1.0 - [`32e129ff1a4c3d28f363f4f2b2a355e29c8fe64d`](https://github.com/livekit/agents/commit/32e129ff1a4c3d28f363f4f2b2a355e29c8fe64d) ([@davidzhao](https://github.com/davidzhao))


[View on GitHub](https://github.com/livekit/agents/releases/tag/livekit-plugins-minimal%400.2.3)

---

## livekit-plugins-llama-index@0.2.4: livekit-plugins-llama-index@0.2.4
**Published:** 2025-05-18

### Patch Changes

-   update to livekit python 1.0 - [`32e129ff1a4c3d28f363f4f2b2a355e29c8fe64d`](https://github.com/livekit/agents/commit/32e129ff1a4c3d28f363f4f2b2a355e29c8fe64d) ([@davidzhao](https://github.com/davidzhao))


[View on GitHub](https://github.com/livekit/agents/releases/tag/livekit-plugins-llama-index%400.2.4)

---

## livekit-plugins-groq@0.1.3: livekit-plugins-groq@0.1.3
**Published:** 2025-05-18

### Patch Changes

-   update to livekit python 1.0 - [`32e129ff1a4c3d28f363f4f2b2a355e29c8fe64d`](https://github.com/livekit/agents/commit/32e129ff1a4c3d28f363f4f2b2a355e29c8fe64d) ([@davidzhao](https://github.com/davidzhao))


[View on GitHub](https://github.com/livekit/agents/releases/tag/livekit-plugins-groq%400.1.3)

---

## livekit-plugins-google@0.11.4: livekit-plugins-google@0.11.4
**Published:** 2025-05-18

### Patch Changes

-   update to livekit python 1.0 - [`32e129ff1a4c3d28f363f4f2b2a355e29c8fe64d`](https://github.com/livekit/agents/commit/32e129ff1a4c3d28f363f4f2b2a355e29c8fe64d) ([@davidzhao](https://github.com/davidzhao))


[View on GitHub](https://github.com/livekit/agents/releases/tag/livekit-plugins-google%400.11.4)

---

## livekit-plugins-fal@0.2.5: livekit-plugins-fal@0.2.5
**Published:** 2025-05-18

### Patch Changes

-   update to livekit python 1.0 - [`32e129ff1a4c3d28f363f4f2b2a355e29c8fe64d`](https://github.com/livekit/agents/commit/32e129ff1a4c3d28f363f4f2b2a355e29c8fe64d) ([@davidzhao](https://github.com/davidzhao))


[View on GitHub](https://github.com/livekit/agents/releases/tag/livekit-plugins-fal%400.2.5)

---

## livekit-plugins-elevenlabs@0.8.3: livekit-plugins-elevenlabs@0.8.3
**Published:** 2025-05-18

### Patch Changes

-   update to livekit python 1.0 - [`32e129ff1a4c3d28f363f4f2b2a355e29c8fe64d`](https://github.com/livekit/agents/commit/32e129ff1a4c3d28f363f4f2b2a355e29c8fe64d) ([@davidzhao](https://github.com/davidzhao))


[View on GitHub](https://github.com/livekit/agents/releases/tag/livekit-plugins-elevenlabs%400.8.3)

---

## livekit-plugins-deepgram@0.7.4: livekit-plugins-deepgram@0.7.4
**Published:** 2025-05-18

### Patch Changes

-   update to livekit python 1.0 - [`32e129ff1a4c3d28f363f4f2b2a355e29c8fe64d`](https://github.com/livekit/agents/commit/32e129ff1a4c3d28f363f4f2b2a355e29c8fe64d) ([@davidzhao](https://github.com/davidzhao))


[View on GitHub](https://github.com/livekit/agents/releases/tag/livekit-plugins-deepgram%400.7.4)

---

## livekit-plugins-cartesia@0.4.12: livekit-plugins-cartesia@0.4.12
**Published:** 2025-05-18

### Patch Changes

-   update to livekit python 1.0 - [`32e129ff1a4c3d28f363f4f2b2a355e29c8fe64d`](https://github.com/livekit/agents/commit/32e129ff1a4c3d28f363f4f2b2a355e29c8fe64d) ([@davidzhao](https://github.com/davidzhao))


[View on GitHub](https://github.com/livekit/agents/releases/tag/livekit-plugins-cartesia%400.4.12)

---

## livekit-plugins-browser@0.0.7: livekit-plugins-browser@0.0.7
**Published:** 2025-05-18

### Patch Changes

-   update to livekit python 1.0 - [`32e129ff1a4c3d28f363f4f2b2a355e29c8fe64d`](https://github.com/livekit/agents/commit/32e129ff1a4c3d28f363f4f2b2a355e29c8fe64d) ([@davidzhao](https://github.com/davidzhao))


[View on GitHub](https://github.com/livekit/agents/releases/tag/livekit-plugins-browser%400.0.7)

---

## livekit-plugins-azure@0.5.8: livekit-plugins-azure@0.5.8
**Published:** 2025-05-18

### Patch Changes

-   update to livekit python 1.0 - [`32e129ff1a4c3d28f363f4f2b2a355e29c8fe64d`](https://github.com/livekit/agents/commit/32e129ff1a4c3d28f363f4f2b2a355e29c8fe64d) ([@davidzhao](https://github.com/davidzhao))


[View on GitHub](https://github.com/livekit/agents/releases/tag/livekit-plugins-azure%400.5.8)

---

## livekit-plugins-aws@0.1.2: livekit-plugins-aws@0.1.2
**Published:** 2025-05-18

### Patch Changes

-   update to livekit python 1.0 - [`32e129ff1a4c3d28f363f4f2b2a355e29c8fe64d`](https://github.com/livekit/agents/commit/32e129ff1a4c3d28f363f4f2b2a355e29c8fe64d) ([@davidzhao](https://github.com/davidzhao))


[View on GitHub](https://github.com/livekit/agents/releases/tag/livekit-plugins-aws%400.1.2)

---

## livekit-plugins-assemblyai@0.2.4: livekit-plugins-assemblyai@0.2.4
**Published:** 2025-05-18

### Patch Changes

-   update to livekit python 1.0 - [`32e129ff1a4c3d28f363f4f2b2a355e29c8fe64d`](https://github.com/livekit/agents/commit/32e129ff1a4c3d28f363f4f2b2a355e29c8fe64d) ([@davidzhao](https://github.com/davidzhao))


[View on GitHub](https://github.com/livekit/agents/releases/tag/livekit-plugins-assemblyai%400.2.4)

---

## livekit-plugins-anthropic@0.2.14: livekit-plugins-anthropic@0.2.14
**Published:** 2025-05-18

### Patch Changes

-   update to livekit python 1.0 - [`32e129ff1a4c3d28f363f4f2b2a355e29c8fe64d`](https://github.com/livekit/agents/commit/32e129ff1a4c3d28f363f4f2b2a355e29c8fe64d) ([@davidzhao](https://github.com/davidzhao))


[View on GitHub](https://github.com/livekit/agents/releases/tag/livekit-plugins-anthropic%400.2.14)

---

## livekit-agents@0.12.21: livekit-agents@0.12.21
**Published:** 2025-05-18

### Patch Changes

-   update to livekit python 1.0 - [`32e129ff1a4c3d28f363f4f2b2a355e29c8fe64d`](https://github.com/livekit/agents/commit/32e129ff1a4c3d28f363f4f2b2a355e29c8fe64d) ([@davidzhao](https://github.com/davidzhao))


[View on GitHub](https://github.com/livekit/agents/releases/tag/livekit-agents%400.12.21)

---

## livekit-agents@1.0.22: livekit-agents@1.0.22
**Published:** 2025-05-17

## What's Changed
* fix user transcription forwarding order by @longcw in https://github.com/livekit/agents/pull/2279
* Update README.md by @Bill-Niz in https://github.com/livekit/agents/pull/2299
* streaming for google tts by @jayeshp19 in https://github.com/livekit/agents/pull/2143
* openai: switch to mp3 encoding by default by @davidzhao in https://github.com/livekit/agents/pull/2306
* aws: fixed STT error at end of session by @davidzhao in https://github.com/livekit/agents/pull/2297
* fix AudioByteStream for multi channels by @longcw in https://github.com/livekit/agents/pull/2307
* avatar runner publish audio/video tracks until first frame pushed by @longcw in https://github.com/livekit/agents/pull/2308
* push a silent audio frame when input stream closed by @longcw in https://github.com/livekit/agents/pull/2309
* Add support for decoding preconnect buffer by @lukasIO in https://github.com/livekit/agents/pull/2311
* added deepwiki badge for weekly repo refresh by @nischalj10 in https://github.com/livekit/agents/pull/2296
* openai: pass tool choice to session initialization by @davidzhao in https://github.com/livekit/agents/pull/2316
* update text-only example to show generate_reply usage by @davidzhao in https://github.com/livekit/agents/pull/2317
* updates to readme by @davidzhao in https://github.com/livekit/agents/pull/2318
* add pre-connected audio buffer by @longcw in https://github.com/livekit/agents/pull/2171

## New Contributors
* @Bill-Niz made their first contribution in https://github.com/livekit/agents/pull/2299
* @nischalj10 made their first contribution in https://github.com/livekit/agents/pull/2296

**Full Changelog**: https://github.com/livekit/agents/compare/livekit-agents@1.0.21...livekit-agents@1.0.22

[View on GitHub](https://github.com/livekit/agents/releases/tag/livekit-agents%401.0.22)

---

## livekit-agents@1.0.21: livekit-agents@1.0.21
**Published:** 2025-05-15

## What's Changed
* debug QOL by @theomonnom in https://github.com/livekit/agents/pull/2150
* use the forkserver on Linux by default  by @theomonnom in https://github.com/livekit/agents/pull/2238
* update to use property. Also make consistent by @milo157 in https://github.com/livekit/agents/pull/2236
* livekit-plugins-aws: update the dependencies to allow for versions greater than specified version by @mike-r-mclaughlin in https://github.com/livekit/agents/pull/2244
* fix quick rotation when flush with empty audio by @longcw in https://github.com/livekit/agents/pull/2251
* add image_encode_options for google realtime model by @longcw in https://github.com/livekit/agents/pull/2249
* Gemini Live improvements & bugfixes by @davidzhao in https://github.com/livekit/agents/pull/2247
* 11labs: improve resilience, do not fail when unexpected payload is received by @davidzhao in https://github.com/livekit/agents/pull/2255
* feat: support cached prompt metrics for Gemini LLM by @mateuszkulpa in https://github.com/livekit/agents/pull/2256
* fix google-cloud-texttospeech and anthropic min versions by @longcw in https://github.com/livekit/agents/pull/2268
* fix raw function tool for google gemini by @longcw in https://github.com/livekit/agents/pull/2270
* support simple word and sentence split for character-based language by @longcw in https://github.com/livekit/agents/pull/2263
* remove leading whitespace from gemini user transcripts by @davidzhao in https://github.com/livekit/agents/pull/2254
* deepgram: default to aura-2 for TTS by @davidzhao in https://github.com/livekit/agents/pull/2272
* add realtime model metrics by @longcw in https://github.com/livekit/agents/pull/2275
* revert buffer changes to AudioStreamDecoder by @davidzhao in https://github.com/livekit/agents/pull/2286
* feat: Add max_completion_tokens parameter to OpenAI LLM by @dorlanpabon in https://github.com/livekit/agents/pull/2258
* fix gather not retrieved error in stt by @longcw in https://github.com/livekit/agents/pull/2276
* correctly pass timeout as connect timeout instead of total by @davidzhao in https://github.com/livekit/agents/pull/2285
* Partial fix for Neuphonic bug detailed in issue #2281.  by @adnansiddiquei in https://github.com/livekit/agents/pull/2282
* Fix Neuphonic CI Tests. by @adnansiddiquei in https://github.com/livekit/agents/pull/2287
* feat: allow to switch between Gemini and Vertex AI using env vars by @mateuszkulpa in https://github.com/livekit/agents/pull/2292

**Full Changelog**: https://github.com/livekit/agents/compare/livekit-agent@1.0.20...livekit-agents@1.0.21

[View on GitHub](https://github.com/livekit/agents/releases/tag/livekit-agents%401.0.21)

---

## livekit-agent@1.0.20: livekit-agent@1.0.20
**Published:** 2025-05-08

## What's Changed
* google stt: support cofigurable streaming by @jayeshp19 in https://github.com/livekit/agents/pull/2192
* fix google llm: single enum value validation error by @jayeshp19 in https://github.com/livekit/agents/pull/2196
* correctly pass in spoken_punctuation param for Google STT by @davidzhao in https://github.com/livekit/agents/pull/2195
* update transcriber example for agents 1.0 by @longcw in https://github.com/livekit/agents/pull/2198
* cleanup examples + e2ee & stats examples by @theomonnom in https://github.com/livekit/agents/pull/2155
* fix set rime tts instance attr url value. by @MaCaki in https://github.com/livekit/agents/pull/2202
* fix Gemini Live function responses when using Vertex AI by @davidzhao in https://github.com/livekit/agents/pull/2194
* Increases buffered words count to Cartesia's TTS service by @itsnicjohn in https://github.com/livekit/agents/pull/2206
* 11labs: fix default model and chunk_length_schedule by @davidzhao in https://github.com/livekit/agents/pull/2205
* Add missing agents submodule docs, improve package readmes and docstrings by @bcherry in https://github.com/livekit/agents/pull/2184
* fix llm.chat for plugins when using with empty tools by @jayeshp19 in https://github.com/livekit/agents/pull/2149
* supress stream timeout errors in google stt by @jayeshp19 in https://github.com/livekit/agents/pull/2189
* forward error from stt/tts stream adapter by @longcw in https://github.com/livekit/agents/pull/2215
* add min_interruption_words by @longcw in https://github.com/livekit/agents/pull/2213
* close room audio output when session close by @longcw in https://github.com/livekit/agents/pull/2211
* Use assigned key and secret by @ChenghaoMou in https://github.com/livekit/agents/pull/2217
* move drain_timeout to WorkerOptions, increase default to 30 mins by @davidzhao in https://github.com/livekit/agents/pull/2210
* add MCP support by @theomonnom in https://github.com/livekit/agents/pull/2200
* Add log when closing agent session from error by @Shubhrakanti in https://github.com/livekit/agents/pull/2218
* share _to_deepgram_url to parse booleans correctly by @MartinGotelli in https://github.com/livekit/agents/pull/2225

## New Contributors
* @MaCaki made their first contribution in https://github.com/livekit/agents/pull/2202
* @itsnicjohn made their first contribution in https://github.com/livekit/agents/pull/2206

**Full Changelog**: https://github.com/livekit/agents/compare/livekit-agent@1.0.19...livekit-agent@1.0.20

[View on GitHub](https://github.com/livekit/agents/releases/tag/livekit-agent%401.0.20)

---

## livekit-agent@1.0.19: livekit-agent@1.0.19
**Published:** 2025-05-03

## What's Changed
* fix(google-tts): Audio encoding for Chirp3 voices not compatible with PCM encoding by @danishshaik in https://github.com/livekit/agents/pull/2176
* Add ElevenLabs plugin support for SSML break tags by @tristan-warner-smith in https://github.com/livekit/agents/pull/2173
* Added ability to set custom Rime URL by @milo157 in https://github.com/livekit/agents/pull/2158
* Fix generate_reply for Gemini LLM by @davidzhao in https://github.com/livekit/agents/pull/2183
* fix None default on function calls  by @theomonnom in https://github.com/livekit/agents/pull/2187
* google stt: allow configurable confidence score by @jayeshp19 in https://github.com/livekit/agents/pull/2178
* Fix: FunctionOutputResponse not getting recognised to gemini live-api by @shashwatsanket997 in https://github.com/livekit/agents/pull/2185
* ElevenLabs Scribe support #1655 by @nishadmusthafa in https://github.com/livekit/agents/pull/2161
* Zg/hume plugin tweaks by @zgreathouse in https://github.com/livekit/agents/pull/2162

## New Contributors
* @tristan-warner-smith made their first contribution in https://github.com/livekit/agents/pull/2173
* @milo157 made their first contribution in https://github.com/livekit/agents/pull/2158
* @shashwatsanket997 made their first contribution in https://github.com/livekit/agents/pull/2185
* @nishadmusthafa made their first contribution in https://github.com/livekit/agents/pull/2161
* @zgreathouse made their first contribution in https://github.com/livekit/agents/pull/2162

**Full Changelog**: https://github.com/livekit/agents/compare/livekit-agent@1.0.18...livekit-agent@1.0.19

[View on GitHub](https://github.com/livekit/agents/releases/tag/livekit-agent%401.0.19)

---

## livekit-agent@1.0.18: livekit-agent@1.0.18
**Published:** 2025-05-01

## What's Changed
* fix type hints for python 3.9 by @longcw in https://github.com/livekit/agents/pull/2118
* fix conversion of chat context to dict by @jmugicagonz in https://github.com/livekit/agents/pull/2128
* generate main response after fast llm done by @longcw in https://github.com/livekit/agents/pull/2119
* fix(plugins-google): Fix Google TTS update options parameter names by @danishshaik in https://github.com/livekit/agents/pull/2124
* Set Hume SDK version to 0.8.3 or greater by @bcherry in https://github.com/livekit/agents/pull/2121
* Use PCM instead of OGG_OPUS for Google TTS by @chrisackermann in https://github.com/livekit/agents/pull/2139
* Bug fix: Ensure mock room name is string in console mode by @MajorTal in https://github.com/livekit/agents/pull/2145
* Improve decoding speed for wav by @davidzhao in https://github.com/livekit/agents/pull/2141
* support session resumption and language in gemini live by @jayeshp19 in https://github.com/livekit/agents/pull/2129
* support video input from screenshare by @longcw in https://github.com/livekit/agents/pull/2127
* fix realtime response later than timeout by @longcw in https://github.com/livekit/agents/pull/2125
* flush stt and wait for final transcription when commit_user_turn by @longcw in https://github.com/livekit/agents/pull/2147
* Add mip_opt_out option for Deepgram TTS by @MartinGotelli in https://github.com/livekit/agents/pull/2159
* Fix hume plugin defaults by @bcherry in https://github.com/livekit/agents/pull/2122
* start room io before connect by @longcw in https://github.com/livekit/agents/pull/2167
* fix retrieval example by @longcw in https://github.com/livekit/agents/pull/2172
* avoid room io overwriting user defined io by @longcw in https://github.com/livekit/agents/pull/2170

## New Contributors
* @danishshaik made their first contribution in https://github.com/livekit/agents/pull/2124
* @MartinGotelli made their first contribution in https://github.com/livekit/agents/pull/2159

**Full Changelog**: https://github.com/livekit/agents/compare/livekit-agents@1.0.17...livekit-agent@1.0.18

[View on GitHub](https://github.com/livekit/agents/releases/tag/livekit-agent%401.0.18)

---

## livekit-agents@1.0.17: livekit-agents@1.0.17
**Published:** 2025-04-24

## What's Changed
* add bithuman deps for the plugin by @longcw in https://github.com/livekit/agents/pull/2090
* fix: prevent duplicate metrics when switching between agents by @mateuszkulpa in https://github.com/livekit/agents/pull/2097
* fix using raw tools with ChatContext copies by @zwily in https://github.com/livekit/agents/pull/2096
* Simpler api to end the session and handling sip users by @Shubhrakanti in https://github.com/livekit/agents/pull/1950
* improvements to Gemini Live handling by @davidzhao in https://github.com/livekit/agents/pull/2089
* check participant kinds in room io by @longcw in https://github.com/livekit/agents/pull/2100
* fix interruption context when the speech hasn't started yet by @theomonnom in https://github.com/livekit/agents/pull/2095
* add the chat_ctx to the tracing page by @theomonnom in https://github.com/livekit/agents/pull/2103
* fix debug tracing for proc executor by @longcw in https://github.com/livekit/agents/pull/2104
* Add Hume TTS Plugin by @Saatvik07 in https://github.com/livekit/agents/pull/2063
* Added timestamp to ChatMessage so it gets added to session history by @samudranb in https://github.com/livekit/agents/pull/1882
* tavus avatar plugin by @longcw in https://github.com/livekit/agents/pull/2052
* don't cancel user code on user_turn_completed  by @theomonnom in https://github.com/livekit/agents/pull/2106
* add chat_ctx timestamp utils  by @theomonnom in https://github.com/livekit/agents/pull/2107
* ensure correct message ordering when injecting speeches in on_user_turn_completed by @theomonnom in https://github.com/livekit/agents/pull/2108
* expose the generated chat message inside the SpeechHandle by @theomonnom in https://github.com/livekit/agents/pull/2111
* add an injected silence filler short response example  by @theomonnom in https://github.com/livekit/agents/pull/2110
* add VideoSampler to AgentSession by @theomonnom in https://github.com/livekit/agents/pull/2113
* better Gemini video defaults by @theomonnom in https://github.com/livekit/agents/pull/2115

## New plugins
* livekit-plugins-hume — https://www.hume.ai/text-to-speech
* livekit-plugins-tavus — https://docs.tavus.io/sections/conversational-video-interface/livekit-agent

## New Contributors
* @zwily made their first contribution in https://github.com/livekit/agents/pull/2096
* @Saatvik07 made their first contribution in https://github.com/livekit/agents/pull/2063
* @samudranb made their first contribution in https://github.com/livekit/agents/pull/1882

**Full Changelog**: https://github.com/livekit/agents/compare/livekit-agents@1.0.14...livekit-agents@1.0.17

[View on GitHub](https://github.com/livekit/agents/releases/tag/livekit-agents%401.0.17)

---

## livekit-agents@1.0.14: livekit-agents@1.0.14
**Published:** 2025-04-22

## What's Changed
* azure speech sdk version upgrade (>=1.41.0 to >=1.43.0) by @jayeshp19 in https://github.com/livekit/agents/pull/2008
* fix: resolve type mismatch between _TurnDetector protocol and plugins by @kechako in https://github.com/livekit/agents/pull/2002
* feat: enhance openai LLM metrics to include cached prompt tokens by @theomonnom in https://github.com/livekit/agents/pull/2013
* delete livekit-plugins-rag by @theomonnom in https://github.com/livekit/agents/pull/1995
* fix: add missing FunctionToolsExecutedEvent export by @mateuszkulpa in https://github.com/livekit/agents/pull/2016
* detect leaked tasks on tests  by @theomonnom in https://github.com/livekit/agents/pull/1993
* toxic proxy & bring back tts tests by @theomonnom in https://github.com/livekit/agents/pull/1982
* fix 11labs timeout & tests by @theomonnom in https://github.com/livekit/agents/pull/2017
* Emit errors from open ai realtime model by @Shubhrakanti in https://github.com/livekit/agents/pull/1968
* fix prompt_cached_tokens in llm metrics by @longcw in https://github.com/livekit/agents/pull/2024
* simplify google tts voice params by @jayeshp19 in https://github.com/livekit/agents/pull/2025
* fix gemini live interruption by @jayeshp19 in https://github.com/livekit/agents/pull/2029
* support with_azure method in openai stt/tts by @jayeshp19 in https://github.com/livekit/agents/pull/2030
* add bey avatar plugin by @longcw in https://github.com/livekit/agents/pull/2031
* avoid duplicate room io initialization by @longcw in https://github.com/livekit/agents/pull/2037
* add wait_for_participant as a function by @longcw in https://github.com/livekit/agents/pull/2039
* fix realtime default turn detection and transcription for azure openai by @jayeshp19 in https://github.com/livekit/agents/pull/2041
* allow overriding eou threshold by @jeradf in https://github.com/livekit/agents/pull/2035
* Speechify TTS Plugin by @chaerla in https://github.com/livekit/agents/pull/2044
* Readme updates by @davidzhao in https://github.com/livekit/agents/pull/2045
* Fix dangling websocket connections by @ChenghaoMou in https://github.com/livekit/agents/pull/2027
* move wait_for_participant to utils by @longcw in https://github.com/livekit/agents/pull/2047
* add recovery method for OAI realtime text response by @longcw in https://github.com/livekit/agents/pull/2015
* fix Speechify tests by @theomonnom in https://github.com/livekit/agents/pull/2051
* fix openai timeout & tests by @theomonnom in https://github.com/livekit/agents/pull/2020
* Speechify TTS Plugin Improvements by @chaerla in https://github.com/livekit/agents/pull/2056
* support raw function descriptions  by @theomonnom in https://github.com/livekit/agents/pull/2055
* add bithuman avatar plugin by @longcw in https://github.com/livekit/agents/pull/2054
* Misc fixes by @davidzhao in https://github.com/livekit/agents/pull/2049
* fix discarded jobs when launching processes by @theomonnom in https://github.com/livekit/agents/pull/2059
* fix generate_reply instructions  by @theomonnom in https://github.com/livekit/agents/pull/2058
* keep exception chaining  by @theomonnom in https://github.com/livekit/agents/pull/1990
* Use ogg by default for speechify by @davidzhao in https://github.com/livekit/agents/pull/2068
* fix(gemini live): avoid duplicating input by @davidzhao in https://github.com/livekit/agents/pull/2069
* fix realtime interruption for VAD turn detection by @longcw in https://github.com/livekit/agents/pull/2072
* reset stt when clear user turn by @longcw in https://github.com/livekit/agents/pull/2070
* Bug Fix - wrong transition to SPEAKING when the agent is in fact listening by @MajorTal in https://github.com/livekit/agents/pull/2075
* support default arguments on function tools  by @theomonnom in https://github.com/livekit/agents/pull/2076
* store audio-synchronized transcript in chat_ctx when interrupted by @theomonnom in https://github.com/livekit/agents/pull/2071
* support RunContext on raw function tools  by @theomonnom in https://github.com/livekit/agents/pull/2077
* Bug fix in agent_activity.py: user_state events were not fired by @MajorTal in https://github.com/livekit/agents/pull/2078
* Support gemini thinking budget. by @pmaldonado in https://github.com/livekit/agents/pull/2060
* publish legacy transcription event for avatar by @longcw in https://github.com/livekit/agents/pull/2074
* merge anyOf optional unions to type list by @theomonnom in https://github.com/livekit/agents/pull/2079
* fix optional arguments on function tools  by @theomonnom in https://github.com/livekit/agents/pull/2080

## New plugins
* livekit-plugins-speechify — https://speechify.com/text-to-speech-api/
* livekit-plugins-bithuman — https://bithuman.mintlify.app/api-reference/sdk/quick-start#1-livekit-agent
* livekit-plugins-bey — https://docs.bey.dev/integration/livekit

## New Contributors
* @kechako made their first contribution in https://github.com/livekit/agents/pull/2002
* @mateuszkulpa made their first contribution in https://github.com/livekit/agents/pull/2016
* @chaerla made their first contribution in https://github.com/livekit/agents/pull/2044
* @pmaldonado made their first contribution in https://github.com/livekit/agents/pull/2060

**Full Changelog**: https://github.com/livekit/agents/compare/livekit-agents@1.0.13...livekit-agents@1.0.14

[View on GitHub](https://github.com/livekit/agents/releases/tag/livekit-agents%401.0.14)

---

## livekit-plugins-elevenlabs@0.8.2: livekit-plugins-elevenlabs@0.8.2
**Published:** 2025-04-16

### Patch Changes

-   use 22.05khz by default for 11labs - [`a294d28c2af672a47f88f598f9fdb3fb13c39c38`](https://github.com/livekit/agents/commit/a294d28c2af672a47f88f598f9fdb3fb13c39c38) ([@davidzhao](https://github.com/davidzhao))


[View on GitHub](https://github.com/livekit/agents/releases/tag/livekit-plugins-elevenlabs%400.8.2)

---

## livekit-plugins-azure@0.5.7: livekit-plugins-azure@0.5.7
**Published:** 2025-04-16

### Patch Changes

-   add speech endpoint in azure ctor and azure speech sdk version upgrade - [#2007](https://github.com/livekit/agents/pull/2007) ([@jayeshp19](https://github.com/jayeshp19))


[View on GitHub](https://github.com/livekit/agents/releases/tag/livekit-plugins-azure%400.5.7)

---

## livekit-agents@1.0.13: livekit-agents@1.0.13
**Published:** 2025-04-15

## What's Changed
* fix audio resampler returning corrupted audio by @theomonnom https://github.com/livekit/rust-sdks/pull/627
* add websearch example & cleanup by @theomonnom in https://github.com/livekit/agents/pull/1960
* ignore stt transcription for realtime model by @longcw in https://github.com/livekit/agents/pull/1958
* add websearch example & cleanup by @theomonnom in https://github.com/livekit/agents/pull/1960
* export events by @theomonnom in https://github.com/livekit/agents/pull/1961
* add HTTP_PROXY for the worker connection by @theomonnom in https://github.com/livekit/agents/pull/1963
* remove error fields by @theomonnom in https://github.com/livekit/agents/pull/1964
* fix unserializable json on debug events by @theomonnom in https://github.com/livekit/agents/pull/1965
* Avoid session end deepgram errors by @zizhong in https://github.com/livekit/agents/pull/1967
* bump gemini sdk version & add video support for gemini multimodal  by @jayeshp19 in https://github.com/livekit/agents/pull/1946
* make drop audio when uninterruptible optional by @longcw in https://github.com/livekit/agents/pull/1957
* add tool example with annotated arguments by @longcw in https://github.com/livekit/agents/pull/1969
* fix tool format when there is messages between tool call and output by @longcw in https://github.com/livekit/agents/pull/1977
* Remove english-only disclaimer from turn detector readme by @bcherry in https://github.com/livekit/agents/pull/1978
* fix: make STT fallback more robust by @zizhong in https://github.com/livekit/agents/pull/1947
* fix: gemini llm when tool choice set to required by @jayeshp19 in https://github.com/livekit/agents/pull/1984
* add chat_ctx.truncate by @longcw in https://github.com/livekit/agents/pull/1974
* support dynamic tools from llm_node by @longcw in https://github.com/livekit/agents/pull/1989
* add segment id to transcription text stream by @longcw in https://github.com/livekit/agents/pull/1951
* fix generate_tool_reply for realtime model by @longcw in https://github.com/livekit/agents/pull/1992
* Add new OpenAI models to ChatModels by @ZaneDash in https://github.com/livekit/agents/pull/2000
* fix looping for background audio using BuiltinAudioClip by @davidzhao in https://github.com/livekit/agents/pull/2001
* add with_azure in openai realtime by @jayeshp19 in https://github.com/livekit/agents/pull/1975
* add sample_rate for DataStreamAudioOutput by @longcw in https://github.com/livekit/agents/pull/2004
* fix OAI realtime model tool choice opt by @longcw in https://github.com/livekit/agents/pull/2005

## New Contributors
* @simplegr33n made their first contribution in https://github.com/livekit/agents/pull/1639
* @Shubhrakanti made their first contribution in https://github.com/livekit/agents/pull/1747
* @ChenghaoMou made their first contribution in https://github.com/livekit/agents/pull/1775
* @paulwe made their first contribution in https://github.com/livekit/agents/pull/1864
* @ShayneP made their first contribution in https://github.com/livekit/agents/pull/1830
* @patrickscoleman made their first contribution in https://github.com/livekit/agents/pull/1920
* @Trivedi-grv made their first contribution in https://github.com/livekit/agents/pull/1884
* @msaelices made their first contribution in https://github.com/livekit/agents/pull/1923
* @zizhong made their first contribution in https://github.com/livekit/agents/pull/1967
* @ZaneDash made their first contribution in https://github.com/livekit/agents/pull/2000

[View on GitHub](https://github.com/livekit/agents/releases/tag/livekit-agents%401.0.13)

---

## livekit-plugins-turn-detector@0.4.4: livekit-plugins-turn-detector@0.4.4
**Published:** 2025-04-07

### Patch Changes

-   added a multilingual turn detector option - [#1736](https://github.com/livekit/agents/pull/1736) ([@jeradf](https://github.com/jeradf))


[View on GitHub](https://github.com/livekit/agents/releases/tag/livekit-plugins-turn-detector%400.4.4)

---

## livekit-plugins-resemble@0.1.1: livekit-plugins-resemble@0.1.1
**Published:** 2025-04-07

### Patch Changes

-   release Resemble.ai TTS - [#1833](https://github.com/livekit/agents/pull/1833) ([@davidzhao](https://github.com/davidzhao))


[View on GitHub](https://github.com/livekit/agents/releases/tag/livekit-plugins-resemble%400.1.1)

---

## livekit-plugins-google@0.11.3: livekit-plugins-google@0.11.3
**Published:** 2025-04-07

### Patch Changes

-   google tts: configure api_endpoint based on location - [#1890](https://github.com/livekit/agents/pull/1890) ([@jayeshp19](https://github.com/jayeshp19))


[View on GitHub](https://github.com/livekit/agents/releases/tag/livekit-plugins-google%400.11.3)

---

## livekit-plugins-deepgram@0.7.3: livekit-plugins-deepgram@0.7.3
**Published:** 2025-04-07

### Patch Changes

-   support multilingual with Nova-3 model - [#1736](https://github.com/livekit/agents/pull/1736) ([@jeradf](https://github.com/jeradf))


[View on GitHub](https://github.com/livekit/agents/releases/tag/livekit-plugins-deepgram%400.7.3)

---

## livekit-agents@0.12.20: livekit-agents@0.12.20
**Published:** 2025-04-07

### Patch Changes

-   fix decoder: if no data was pushed, close the output channel - [#1881](https://github.com/livekit/agents/pull/1881) ([@jayeshp19](https://github.com/jayeshp19))


[View on GitHub](https://github.com/livekit/agents/releases/tag/livekit-agents%400.12.20)

---

## livekit-plugins-openai@0.12.3: livekit-plugins-openai@0.12.3
**Published:** 2025-04-01

### Patch Changes

-   openai: default to use_realtime=False - [#1783](https://github.com/livekit/agents/pull/1783) ([@davidzhao](https://github.com/davidzhao))

-   fix(openai): pass NotGiven to OpenAI when instructions are omitted - [#1834](https://github.com/livekit/agents/pull/1834) ([@davidzhao](https://github.com/davidzhao))


[View on GitHub](https://github.com/livekit/agents/releases/tag/livekit-plugins-openai%400.12.3)

---

## livekit-agents@0.12.19: livekit-agents@0.12.19
**Published:** 2025-04-01

### Patch Changes

-   fixed thread safety in AudioStreamDecoder - [#1736](https://github.com/livekit/agents/pull/1736) ([@jeradf](https://github.com/jeradf))

-   cleanup AudioStreamDecoder resources - [#1736](https://github.com/livekit/agents/pull/1736) ([@jeradf](https://github.com/jeradf))


[View on GitHub](https://github.com/livekit/agents/releases/tag/livekit-agents%400.12.19)

---

## livekit-plugins-openai@0.12.2: livekit-plugins-openai@0.12.2
**Published:** 2025-03-27

### Patch Changes

-   fix: openai stt error when using detect language - [#1755](https://github.com/livekit/agents/pull/1755) ([@jayeshp19](https://github.com/jayeshp19))


[View on GitHub](https://github.com/livekit/agents/releases/tag/livekit-plugins-openai%400.12.2)

---

## livekit-plugins-openai@0.12.1: livekit-plugins-openai@0.12.1
**Published:** 2025-03-25

### Patch Changes

-   expose turn_detection options with openai STT - [#1726](https://github.com/livekit/agents/pull/1726) ([@davidzhao](https://github.com/davidzhao))

-   feat(OpenAI STT): add support for semantic_vad - [#1707](https://github.com/livekit/agents/pull/1707) ([@chasemcdo](https://github.com/chasemcdo))


[View on GitHub](https://github.com/livekit/agents/releases/tag/livekit-plugins-openai%400.12.1)

---

## livekit-plugins-groq@0.1.2: livekit-plugins-groq@0.1.2
**Published:** 2025-03-25

### Patch Changes

-   update to tts model and voices - [#1725](https://github.com/livekit/agents/pull/1725) ([@davidzhao](https://github.com/davidzhao))


[View on GitHub](https://github.com/livekit/agents/releases/tag/livekit-plugins-groq%400.1.2)

---

## livekit-plugins-deepgram@0.7.2: livekit-plugins-deepgram@0.7.2
**Published:** 2025-03-25

### Patch Changes

-   Added optional parameter to opt out from deepgrams model improvement plan - [#1713](https://github.com/livekit/agents/pull/1713) ([@MatthiasGruba](https://github.com/MatthiasGruba))


[View on GitHub](https://github.com/livekit/agents/releases/tag/livekit-plugins-deepgram%400.7.2)

---

## livekit-plugins-openai@0.12.0: livekit-plugins-openai@0.12.0
**Published:** 2025-03-21

### Minor Changes

-   support for streaming STT, new STT/TTS models - [#1701](https://github.com/livekit/agents/pull/1701) ([@davidzhao](https://github.com/davidzhao))

### Patch Changes

-   openai new STT model and voices - [#1691](https://github.com/livekit/agents/pull/1691) ([@lundin](https://github.com/lundin))

-   Make azure and openai take a timeout optionally. Also update the default timeout for Azure OpenAI to 5s from 10 minutes. - [#1674](https://github.com/livekit/agents/pull/1674) ([@martin-purplefish](https://github.com/martin-purplefish))


[View on GitHub](https://github.com/livekit/agents/releases/tag/livekit-plugins-openai%400.12.0)

---

## livekit-plugins-groq@0.1.1: livekit-plugins-groq@0.1.1
**Published:** 2025-03-21

### Patch Changes

-   initial version - [#1689](https://github.com/livekit/agents/pull/1689) ([@davidzhao](https://github.com/davidzhao))


[View on GitHub](https://github.com/livekit/agents/releases/tag/livekit-plugins-groq%400.1.1)

---

## livekit-plugins-google@0.11.2: livekit-plugins-google@0.11.2
**Published:** 2025-03-21

### Patch Changes

-   fix: double transcript issue for google stt - [#1694](https://github.com/livekit/agents/pull/1694) ([@jayeshp19](https://github.com/jayeshp19))


[View on GitHub](https://github.com/livekit/agents/releases/tag/livekit-plugins-google%400.11.2)

---

## livekit-agents@0.12.18: livekit-agents@0.12.18
**Published:** 2025-03-21

### Patch Changes

-   Remove unnecessary version pins - [#1682](https://github.com/livekit/agents/pull/1682) ([@hauntsaninja](https://github.com/hauntsaninja))

-   reduced retry interval to 2s - [#1701](https://github.com/livekit/agents/pull/1701) ([@davidzhao](https://github.com/davidzhao))


[View on GitHub](https://github.com/livekit/agents/releases/tag/livekit-agents%400.12.18)

---

## livekit-plugins-rime@0.2.2: livekit-plugins-rime@0.2.2
**Published:** 2025-03-19

### Patch Changes

-   Add string type support to model parameter - [#1657](https://github.com/livekit/agents/pull/1657) ([@jayeshp19](https://github.com/jayeshp19))


[View on GitHub](https://github.com/livekit/agents/releases/tag/livekit-plugins-rime%400.2.2)

---

## livekit-plugins-openai@0.11.3: livekit-plugins-openai@0.11.3
**Published:** 2025-03-19

### Patch Changes

-   Support more input transcription parameters for openai realtime - [#1637](https://github.com/livekit/agents/pull/1637) ([@adambenali](https://github.com/adambenali))

-   Add string type support to model parameter - [#1657](https://github.com/livekit/agents/pull/1657) ([@jayeshp19](https://github.com/jayeshp19))


[View on GitHub](https://github.com/livekit/agents/releases/tag/livekit-plugins-openai%400.11.3)

---

## livekit-plugins-neuphonic@0.1.1: livekit-plugins-neuphonic@0.1.1
**Published:** 2025-03-19

### Patch Changes

-   Add string type support to model parameter - [#1657](https://github.com/livekit/agents/pull/1657) ([@jayeshp19](https://github.com/jayeshp19))

-   rename NEUPHONIC_API_TOKEN to NEUPHONIC_API_KEY - [#1642](https://github.com/livekit/agents/pull/1642) ([@davidzhao](https://github.com/davidzhao))


[View on GitHub](https://github.com/livekit/agents/releases/tag/livekit-plugins-neuphonic%400.1.1)

---

## livekit-plugins-google@0.11.1: livekit-plugins-google@0.11.1
**Published:** 2025-03-19

### Patch Changes

-   allow configurable api version in gemini realtime - [#1656](https://github.com/livekit/agents/pull/1656) ([@jayeshp19](https://github.com/jayeshp19))


[View on GitHub](https://github.com/livekit/agents/releases/tag/livekit-plugins-google%400.11.1)

---

## livekit-plugins-elevenlabs@0.8.1: livekit-plugins-elevenlabs@0.8.1
**Published:** 2025-03-19

### Patch Changes

-   Revert to using 'isFinal' in ElevenLabs for reliable audio packet completion detection - [#1676](https://github.com/livekit/agents/pull/1676) ([@jayeshp19](https://github.com/jayeshp19))


[View on GitHub](https://github.com/livekit/agents/releases/tag/livekit-plugins-elevenlabs%400.8.1)

---

## livekit-plugins-deepgram@0.7.1: livekit-plugins-deepgram@0.7.1
**Published:** 2025-03-19

### Patch Changes

-   add `nova-3-medical` to stt models - [#1657](https://github.com/livekit/agents/pull/1657) ([@jayeshp19](https://github.com/jayeshp19))

-   Add string type support to model parameter - [#1657](https://github.com/livekit/agents/pull/1657) ([@jayeshp19](https://github.com/jayeshp19))

-   support numerals deepgram stt - [#1667](https://github.com/livekit/agents/pull/1667) ([@jayeshp19](https://github.com/jayeshp19))


[View on GitHub](https://github.com/livekit/agents/releases/tag/livekit-plugins-deepgram%400.7.1)

---

## livekit-plugins-cartesia@0.4.11: livekit-plugins-cartesia@0.4.11
**Published:** 2025-03-19

### Patch Changes

-   Add string type support to model parameter - [#1657](https://github.com/livekit/agents/pull/1657) ([@jayeshp19](https://github.com/jayeshp19))


[View on GitHub](https://github.com/livekit/agents/releases/tag/livekit-plugins-cartesia%400.4.11)

---

## livekit-plugins-azure@0.5.6: livekit-plugins-azure@0.5.6
**Published:** 2025-03-19

### Patch Changes

-   Add callbacks as updatable Azure TTS options - [#1645](https://github.com/livekit/agents/pull/1645) ([@anishnag](https://github.com/anishnag))


[View on GitHub](https://github.com/livekit/agents/releases/tag/livekit-plugins-azure%400.5.6)

---

## livekit-plugins-openai@0.11.2: livekit-plugins-openai@0.11.2
**Published:** 2025-03-12

### Patch Changes

-   version bump to 0.11.1 - [#1640](https://github.com/livekit/agents/pull/1640) ([@davidzhao](https://github.com/davidzhao))


[View on GitHub](https://github.com/livekit/agents/releases/tag/livekit-plugins-openai%400.11.2)

---

## livekit-plugins-neuphonic@0.1.0: livekit-plugins-neuphonic@0.1.0
**Published:** 2025-03-12

# livekit-plugins-neuphonic


[View on GitHub](https://github.com/livekit/agents/releases/tag/livekit-plugins-neuphonic%400.1.0)

---

## livekit-plugins-cartesia@0.4.10: livekit-plugins-cartesia@0.4.10
**Published:** 2025-03-11

### Patch Changes

-   Adding new model literals, updating default to sonic-2 - [#1627](https://github.com/livekit/agents/pull/1627) ([@longcw](https://github.com/longcw))


[View on GitHub](https://github.com/livekit/agents/releases/tag/livekit-plugins-cartesia%400.4.10)

---

## livekit-plugins-turn-detector@0.4.3: livekit-plugins-turn-detector@0.4.3
**Published:** 2025-03-06

### Patch Changes

-   updated livekit-agent reference to &lt;1.0 - [#1607](https://github.com/livekit/agents/pull/1607) ([@davidzhao](https://github.com/davidzhao))

-   retrained to be robust to missing terminal punctuation - [#1565](https://github.com/livekit/agents/pull/1565) ([@jeradf](https://github.com/jeradf))


[View on GitHub](https://github.com/livekit/agents/releases/tag/livekit-plugins-turn-detector%400.4.3)

---

## livekit-plugins-speechmatics@0.0.2: livekit-plugins-speechmatics@0.0.2
**Published:** 2025-03-06

### Patch Changes

-   updated livekit-agent reference to &lt;1.0 - [#1607](https://github.com/livekit/agents/pull/1607) ([@davidzhao](https://github.com/davidzhao))


[View on GitHub](https://github.com/livekit/agents/releases/tag/livekit-plugins-speechmatics%400.0.2)

---

## livekit-plugins-silero@0.7.5: livekit-plugins-silero@0.7.5
**Published:** 2025-03-06

### Patch Changes

-   updated livekit-agent reference to &lt;1.0 - [#1607](https://github.com/livekit/agents/pull/1607) ([@davidzhao](https://github.com/davidzhao))


[View on GitHub](https://github.com/livekit/agents/releases/tag/livekit-plugins-silero%400.7.5)

---

## livekit-plugins-rime@0.2.1: livekit-plugins-rime@0.2.1
**Published:** 2025-03-06

### Patch Changes

-   use streaming AudioDecoder to handle compressed encoding - [#1584](https://github.com/livekit/agents/pull/1584) ([@davidzhao](https://github.com/davidzhao))

-   updated livekit-agent reference to &lt;1.0 - [#1607](https://github.com/livekit/agents/pull/1607) ([@davidzhao](https://github.com/davidzhao))


[View on GitHub](https://github.com/livekit/agents/releases/tag/livekit-plugins-rime%400.2.1)

---

## livekit-plugins-rag@0.2.4: livekit-plugins-rag@0.2.4
**Published:** 2025-03-06

### Patch Changes

-   updated livekit-agent reference to &lt;1.0 - [#1607](https://github.com/livekit/agents/pull/1607) ([@davidzhao](https://github.com/davidzhao))


[View on GitHub](https://github.com/livekit/agents/releases/tag/livekit-plugins-rag%400.2.4)

---

## livekit-plugins-playai@1.0.9: livekit-plugins-playai@1.0.9
**Published:** 2025-03-06

### Patch Changes

-   use streaming AudioDecoder to handle compressed encoding - [#1584](https://github.com/livekit/agents/pull/1584) ([@davidzhao](https://github.com/davidzhao))

-   updated livekit-agent reference to &lt;1.0 - [#1607](https://github.com/livekit/agents/pull/1607) ([@davidzhao](https://github.com/davidzhao))


[View on GitHub](https://github.com/livekit/agents/releases/tag/livekit-plugins-playai%401.0.9)

---

## livekit-plugins-openai@1.0.1: livekit-plugins-openai@1.0.1
**Published:** 2025-03-06

### Patch Changes

-   use streaming AudioDecoder to handle compressed encoding - [#1584](https://github.com/livekit/agents/pull/1584) ([@davidzhao](https://github.com/davidzhao))

-   fix multimodal agent interrupts itself when creating function call response - [#1585](https://github.com/livekit/agents/pull/1585) ([@longcw](https://github.com/longcw))

-   feat: add max_tokens option to LLM and LLMStream classes - [#1576](https://github.com/livekit/agents/pull/1576) ([@davidzhao](https://github.com/davidzhao))

-   updated livekit-agent reference to &lt;1.0 - [#1607](https://github.com/livekit/agents/pull/1607) ([@davidzhao](https://github.com/davidzhao))


[View on GitHub](https://github.com/livekit/agents/releases/tag/livekit-plugins-openai%401.0.1)

---

## livekit-plugins-nltk@0.7.4: livekit-plugins-nltk@0.7.4
**Published:** 2025-03-06

### Patch Changes

-   updated livekit-agent reference to &lt;1.0 - [#1607](https://github.com/livekit/agents/pull/1607) ([@davidzhao](https://github.com/davidzhao))


[View on GitHub](https://github.com/livekit/agents/releases/tag/livekit-plugins-nltk%400.7.4)

---

## livekit-plugins-minimal@0.2.2: livekit-plugins-minimal@0.2.2
**Published:** 2025-03-06

### Patch Changes

-   updated livekit-agent reference to &lt;1.0 - [#1607](https://github.com/livekit/agents/pull/1607) ([@davidzhao](https://github.com/davidzhao))


[View on GitHub](https://github.com/livekit/agents/releases/tag/livekit-plugins-minimal%400.2.2)

---

## livekit-plugins-llama-index@0.2.3: livekit-plugins-llama-index@0.2.3
**Published:** 2025-03-06

### Patch Changes

-   updated livekit-agent reference to &lt;1.0 - [#1607](https://github.com/livekit/agents/pull/1607) ([@davidzhao](https://github.com/davidzhao))


[View on GitHub](https://github.com/livekit/agents/releases/tag/livekit-plugins-llama-index%400.2.3)

---

## livekit-plugins-google@0.11.0: livekit-plugins-google@0.11.0
**Published:** 2025-03-06

### Minor Changes

-   Add simple video input support for gemini live - [#1536](https://github.com/livekit/agents/pull/1536) ([@bcherry](https://github.com/bcherry))

### Patch Changes

-   use streaming AudioDecoder to handle compressed encoding - [#1584](https://github.com/livekit/agents/pull/1584) ([@davidzhao](https://github.com/davidzhao))

-   updated livekit-agent reference to &lt;1.0 - [#1607](https://github.com/livekit/agents/pull/1607) ([@davidzhao](https://github.com/davidzhao))


[View on GitHub](https://github.com/livekit/agents/releases/tag/livekit-plugins-google%400.11.0)

---

## livekit-plugins-fal@0.2.4: livekit-plugins-fal@0.2.4
**Published:** 2025-03-06

### Patch Changes

-   updated livekit-agent reference to &lt;1.0 - [#1607](https://github.com/livekit/agents/pull/1607) ([@davidzhao](https://github.com/davidzhao))


[View on GitHub](https://github.com/livekit/agents/releases/tag/livekit-plugins-fal%400.2.4)

---

## livekit-plugins-elevenlabs@0.8.0: livekit-plugins-elevenlabs@0.8.0
**Published:** 2025-03-06

### Minor Changes

-   use streaming AudioDecoder to handle compressed encoding - [#1584](https://github.com/livekit/agents/pull/1584) ([@davidzhao](https://github.com/davidzhao))

### Patch Changes

-   added a tts.prewarm method to start the connection pool early. - [#1587](https://github.com/livekit/agents/pull/1587) ([@davidzhao](https://github.com/davidzhao))

-   deprecated elevenlabs' optimize_stream_latency option - [#1587](https://github.com/livekit/agents/pull/1587) ([@davidzhao](https://github.com/davidzhao))

-   increase elevenlabs websocket connection timeout to default 300 seconds - [#1582](https://github.com/livekit/agents/pull/1582) ([@jayeshp19](https://github.com/jayeshp19))

-   updated livekit-agent reference to &lt;1.0 - [#1607](https://github.com/livekit/agents/pull/1607) ([@davidzhao](https://github.com/davidzhao))

-   Added speed parameter for voices. - [#1574](https://github.com/livekit/agents/pull/1574) ([@MatthiasGruba](https://github.com/MatthiasGruba))

    E.g.:

    ```python
    voice = Voice(
        id="EXAVITQu4vr4xnSDxMaL",
        name="Bella",
        category="premade",
        settings=VoiceSettings(
            stability=0.71,
            speed=1.2,
            similarity_boost=0.5,
            style=0.0,
            use_speaker_boost=True,
        ),
    )

    ```


[View on GitHub](https://github.com/livekit/agents/releases/tag/livekit-plugins-elevenlabs%400.8.0)

---

## livekit-plugins-deepgram@0.7.0: livekit-plugins-deepgram@0.7.0
**Published:** 2025-03-06

### Minor Changes

-   use streaming AudioDecoder to handle compressed encoding - [#1584](https://github.com/livekit/agents/pull/1584) ([@davidzhao](https://github.com/davidzhao))

### Patch Changes

-   added a tts.prewarm method to start the connection pool early. - [#1587](https://github.com/livekit/agents/pull/1587) ([@davidzhao](https://github.com/davidzhao))

-   update pool configuration for deepgram and cartesia - [#1605](https://github.com/livekit/agents/pull/1605) ([@jayeshp19](https://github.com/jayeshp19))

-   set mex session duration to 1 hour in deepgram connection pool - [#1582](https://github.com/livekit/agents/pull/1582) ([@jayeshp19](https://github.com/jayeshp19))

-   updated livekit-agent reference to &lt;1.0 - [#1607](https://github.com/livekit/agents/pull/1607) ([@davidzhao](https://github.com/davidzhao))


[View on GitHub](https://github.com/livekit/agents/releases/tag/livekit-plugins-deepgram%400.7.0)

---

## livekit-plugins-cartesia@0.4.9: livekit-plugins-cartesia@0.4.9
**Published:** 2025-03-06

### Patch Changes

-   use streaming AudioDecoder to handle compressed encoding - [#1584](https://github.com/livekit/agents/pull/1584) ([@davidzhao](https://github.com/davidzhao))

-   added a tts.prewarm method to start the connection pool early. - [#1587](https://github.com/livekit/agents/pull/1587) ([@davidzhao](https://github.com/davidzhao))

-   update pool configuration for deepgram and cartesia - [#1605](https://github.com/livekit/agents/pull/1605) ([@jayeshp19](https://github.com/jayeshp19))

-   updated livekit-agent reference to &lt;1.0 - [#1607](https://github.com/livekit/agents/pull/1607) ([@davidzhao](https://github.com/davidzhao))


[View on GitHub](https://github.com/livekit/agents/releases/tag/livekit-plugins-cartesia%400.4.9)

---

## livekit-plugins-browser@0.0.6: livekit-plugins-browser@0.0.6
**Published:** 2025-03-06

### Patch Changes

-   updated livekit-agent reference to &lt;1.0 - [#1607](https://github.com/livekit/agents/pull/1607) ([@davidzhao](https://github.com/davidzhao))


[View on GitHub](https://github.com/livekit/agents/releases/tag/livekit-plugins-browser%400.0.6)

---

## livekit-plugins-azure@0.5.5: livekit-plugins-azure@0.5.5
**Published:** 2025-03-06

### Patch Changes

-   feat: Azure.STT support profanity_option - [#1540](https://github.com/livekit/agents/pull/1540) ([@shiftu](https://github.com/shiftu))

-   updated livekit-agent reference to &lt;1.0 - [#1607](https://github.com/livekit/agents/pull/1607) ([@davidzhao](https://github.com/davidzhao))


[View on GitHub](https://github.com/livekit/agents/releases/tag/livekit-plugins-azure%400.5.5)

---

## livekit-plugins-aws@0.1.1: livekit-plugins-aws@0.1.1
**Published:** 2025-03-06

### Patch Changes

-   use streaming AudioDecoder to handle compressed encoding - [#1584](https://github.com/livekit/agents/pull/1584) ([@davidzhao](https://github.com/davidzhao))

-   updated livekit-agent reference to &lt;1.0 - [#1607](https://github.com/livekit/agents/pull/1607) ([@davidzhao](https://github.com/davidzhao))


[View on GitHub](https://github.com/livekit/agents/releases/tag/livekit-plugins-aws%400.1.1)

---

## livekit-plugins-assemblyai@0.2.3: livekit-plugins-assemblyai@0.2.3
**Published:** 2025-03-06

### Patch Changes

-   updated livekit-agent reference to &lt;1.0 - [#1607](https://github.com/livekit/agents/pull/1607) ([@davidzhao](https://github.com/davidzhao))


[View on GitHub](https://github.com/livekit/agents/releases/tag/livekit-plugins-assemblyai%400.2.3)

---

## livekit-plugins-anthropic@0.2.13: livekit-plugins-anthropic@0.2.13
**Published:** 2025-03-06

### Patch Changes

-   updated livekit-agent reference to &lt;1.0 - [#1607](https://github.com/livekit/agents/pull/1607) ([@davidzhao](https://github.com/davidzhao))


[View on GitHub](https://github.com/livekit/agents/releases/tag/livekit-plugins-anthropic%400.2.13)

---

## livekit-agents@0.12.17: livekit-agents@0.12.17
**Published:** 2025-03-06

### Patch Changes

-   use streaming AudioDecoder to handle compressed encoding - [#1584](https://github.com/livekit/agents/pull/1584) ([@davidzhao](https://github.com/davidzhao))

-   added a tts.prewarm method to start the connection pool early. - [#1587](https://github.com/livekit/agents/pull/1587) ([@davidzhao](https://github.com/davidzhao))

-   Raise ValueError in FallbackAdapter when streaming is not supported - [#1609](https://github.com/livekit/agents/pull/1609) ([@jayeshp19](https://github.com/jayeshp19))

-   fixed a bug in AudioStreamDecoder where it could fail on close - [#1587](https://github.com/livekit/agents/pull/1587) ([@davidzhao](https://github.com/davidzhao))

-   support for livekit noise cancellation plugin in VoicePipelineAgent and MultimodalAgent - [#1551](https://github.com/livekit/agents/pull/1551) ([@bcherry](https://github.com/bcherry))

-   fix: \_play_speech get stuck due to orphan speech handle - [#1555](https://github.com/livekit/agents/pull/1555) ([@SiyuanQi](https://github.com/SiyuanQi))


[View on GitHub](https://github.com/livekit/agents/releases/tag/livekit-agents%400.12.17)

---

## livekit-plugins-playai@1.0.8: livekit-plugins-playai@1.0.8
**Published:** 2025-02-28

### Patch Changes

-   remove update options from tts synthesis stream - [#1546](https://github.com/livekit/agents/pull/1546) ([@jayeshp19](https://github.com/jayeshp19))


[View on GitHub](https://github.com/livekit/agents/releases/tag/livekit-plugins-playai%401.0.8)

---

## livekit-plugins-google@0.10.6: livekit-plugins-google@0.10.6
**Published:** 2025-02-28

### Patch Changes

-   google stt: change default model to `latest_long` - [#1552](https://github.com/livekit/agents/pull/1552) ([@jayeshp19](https://github.com/jayeshp19))

-   feat: connection pooling. speeds up generation with STT/TTS providers - [#1538](https://github.com/livekit/agents/pull/1538) ([@davidzhao](https://github.com/davidzhao))

-   fix: functioncall cancellation ids in realtime - [#1572](https://github.com/livekit/agents/pull/1572) ([@jayeshp19](https://github.com/jayeshp19))

-   google-genai version bump & remove id feild from function call and function response - [#1559](https://github.com/livekit/agents/pull/1559) ([@jayeshp19](https://github.com/jayeshp19))


[View on GitHub](https://github.com/livekit/agents/releases/tag/livekit-plugins-google%400.10.6)

---

## livekit-plugins-elevenlabs@0.7.14: livekit-plugins-elevenlabs@0.7.14
**Published:** 2025-02-28

### Patch Changes

-   use connection pool for elevenlabs websocket persistant connection - [#1546](https://github.com/livekit/agents/pull/1546) ([@jayeshp19](https://github.com/jayeshp19))

-   remove update options from tts synthesis stream - [#1546](https://github.com/livekit/agents/pull/1546) ([@jayeshp19](https://github.com/jayeshp19))


[View on GitHub](https://github.com/livekit/agents/releases/tag/livekit-plugins-elevenlabs%400.7.14)

---

## livekit-plugins-deepgram@0.6.20: livekit-plugins-deepgram@0.6.20
**Published:** 2025-02-28

### Patch Changes

-   fix(deepgram): fix STT keyterm parameter - [#1535](https://github.com/livekit/agents/pull/1535) ([@wdhwg001](https://github.com/wdhwg001))

-   use connection pool for deepgram tts - [#1523](https://github.com/livekit/agents/pull/1523) ([@jayeshp19](https://github.com/jayeshp19))

-   remove update options from tts synthesis stream - [#1546](https://github.com/livekit/agents/pull/1546) ([@jayeshp19](https://github.com/jayeshp19))


[View on GitHub](https://github.com/livekit/agents/releases/tag/livekit-plugins-deepgram%400.6.20)

---

## livekit-plugins-cartesia@0.4.8: livekit-plugins-cartesia@0.4.8
**Published:** 2025-02-28

### Patch Changes

-   feat: connection pooling. speeds up generation with STT/TTS providers - [#1538](https://github.com/livekit/agents/pull/1538) ([@davidzhao](https://github.com/davidzhao))

-   remove update options from tts synthesis stream - [#1546](https://github.com/livekit/agents/pull/1546) ([@jayeshp19](https://github.com/jayeshp19))


[View on GitHub](https://github.com/livekit/agents/releases/tag/livekit-plugins-cartesia%400.4.8)

---

## livekit-plugins-aws@0.1.0: livekit-plugins-aws@0.1.0
**Published:** 2025-02-28

# livekit-plugins-aws


[View on GitHub](https://github.com/livekit/agents/releases/tag/livekit-plugins-aws%400.1.0)

---

## livekit-plugins-anthropic@0.2.12: livekit-plugins-anthropic@0.2.12
**Published:** 2025-02-28

### Patch Changes

-   don't pass functions in params when tool choice is set to none - [#1552](https://github.com/livekit/agents/pull/1552) ([@jayeshp19](https://github.com/jayeshp19))


[View on GitHub](https://github.com/livekit/agents/releases/tag/livekit-plugins-anthropic%400.2.12)

---

## livekit-agents@0.12.16: livekit-agents@0.12.16
**Published:** 2025-02-28

### Patch Changes

-   feat: connection pooling. speeds up generation with STT/TTS providers - [#1538](https://github.com/livekit/agents/pull/1538) ([@davidzhao](https://github.com/davidzhao))

-   handle process initialization failure - [#1556](https://github.com/livekit/agents/pull/1556) ([@theomonnom](https://github.com/theomonnom))


[View on GitHub](https://github.com/livekit/agents/releases/tag/livekit-agents%400.12.16)

---

## livekit-plugins-turn-detector@0.4.2: livekit-plugins-turn-detector@0.4.2
**Published:** 2025-02-20

### Patch Changes

-   log from job process instead of inference - [#1506](https://github.com/livekit/agents/pull/1506) ([@davidzhao](https://github.com/davidzhao))


[View on GitHub](https://github.com/livekit/agents/releases/tag/livekit-plugins-turn-detector%400.4.2)

---

## livekit-plugins-openai@0.11.0: livekit-plugins-openai@0.11.0
**Published:** 2025-02-20

### Minor Changes

-   openai tts: switch to using Opus encoding - [#1494](https://github.com/livekit/agents/pull/1494) ([@davidzhao](https://github.com/davidzhao))


[View on GitHub](https://github.com/livekit/agents/releases/tag/livekit-plugins-openai%400.11.0)

---

## livekit-plugins-google@0.10.5: livekit-plugins-google@0.10.5
**Published:** 2025-02-20

### Patch Changes

-   fix(google): require min confidence score due to aggressive generation - [#1507](https://github.com/livekit/agents/pull/1507) ([@davidzhao](https://github.com/davidzhao))


[View on GitHub](https://github.com/livekit/agents/releases/tag/livekit-plugins-google%400.10.5)

---

## livekit-plugins-azure@0.5.4: livekit-plugins-azure@0.5.4
**Published:** 2025-02-20

### Patch Changes

-   Add handlers for supported synthesis events for Azure TTS - [#1486](https://github.com/livekit/agents/pull/1486) ([@anishnag](https://github.com/anishnag))


[View on GitHub](https://github.com/livekit/agents/releases/tag/livekit-plugins-azure%400.5.4)

---

## livekit-plugins-anthropic@0.2.11: livekit-plugins-anthropic@0.2.11
**Published:** 2025-02-20

### Patch Changes

-   Add cache support for Anthropic - [#1478](https://github.com/livekit/agents/pull/1478) ([@jayeshp19](https://github.com/jayeshp19))


[View on GitHub](https://github.com/livekit/agents/releases/tag/livekit-plugins-anthropic%400.2.11)

---

## livekit-agents@0.12.15: livekit-agents@0.12.15
**Published:** 2025-02-20

### Patch Changes

-   Revert "fix(cli): update main_file path to use current directory" - [#1509](https://github.com/livekit/agents/pull/1509) ([@theomonnom](https://github.com/theomonnom))


[View on GitHub](https://github.com/livekit/agents/releases/tag/livekit-agents%400.12.15)

---

## livekit-agents@0.12.14: livekit-agents@0.12.14
**Published:** 2025-02-20

### Patch Changes

-   openai tts: switch to using Opus encoding - [#1494](https://github.com/livekit/agents/pull/1494) ([@davidzhao](https://github.com/davidzhao))

-   improve exception logging - [#1490](https://github.com/livekit/agents/pull/1490) ([@jayeshp19](https://github.com/jayeshp19))

-   fix interrupting nested speech from before_llm_cb - [#1504](https://github.com/livekit/agents/pull/1504) ([@longcw](https://github.com/longcw))

-   add cache tokens in `CompletionUsage` dataclass - [#1478](https://github.com/livekit/agents/pull/1478) ([@jayeshp19](https://github.com/jayeshp19))


[View on GitHub](https://github.com/livekit/agents/releases/tag/livekit-agents%400.12.14)

---

## livekit-plugins-openai@0.10.19: livekit-plugins-openai@0.10.19
**Published:** 2025-02-14

### Patch Changes

-   fix: [openai] only send params when set - [#1474](https://github.com/livekit/agents/pull/1474) ([@jayeshp19](https://github.com/jayeshp19))

-   fix response create for openai realtime model - [#1469](https://github.com/livekit/agents/pull/1469) ([@longcw](https://github.com/longcw))


[View on GitHub](https://github.com/livekit/agents/releases/tag/livekit-plugins-openai%400.10.19)

---

## livekit-plugins-google@0.10.4: livekit-plugins-google@0.10.4
**Published:** 2025-02-14

### Patch Changes

-   Gemini realtime : rollback default model to `gemini-2.0-flash-exp` - [#1489](https://github.com/livekit/agents/pull/1489) ([@jayeshp19](https://github.com/jayeshp19))


[View on GitHub](https://github.com/livekit/agents/releases/tag/livekit-plugins-google%400.10.4)

---

## livekit-plugins-deepgram@0.6.19: livekit-plugins-deepgram@0.6.19
**Published:** 2025-02-14

### Patch Changes

-   deepgram: support for Nova-3 keyterms - [#1484](https://github.com/livekit/agents/pull/1484) ([@davidzhao](https://github.com/davidzhao))


[View on GitHub](https://github.com/livekit/agents/releases/tag/livekit-plugins-deepgram%400.6.19)

---

## livekit-agents@0.12.13: livekit-agents@0.12.13
**Published:** 2025-02-14

### Patch Changes

-   Allow shutdown callbacks to take reason - [#1475](https://github.com/livekit/agents/pull/1475) ([@martin-purplefish](https://github.com/martin-purplefish))


[View on GitHub](https://github.com/livekit/agents/releases/tag/livekit-agents%400.12.13)

---

## livekit-plugins-turn-detector@0.4.1: livekit-plugins-turn-detector@0.4.1
**Published:** 2025-02-11

### Patch Changes

-   fix incorrect dtype on windows - [#1452](https://github.com/livekit/agents/pull/1452) ([@jeradf](https://github.com/jeradf))

-   adjust default probability cutoff - [#1465](https://github.com/livekit/agents/pull/1465) ([@jeradf](https://github.com/jeradf))


[View on GitHub](https://github.com/livekit/agents/releases/tag/livekit-plugins-turn-detector%400.4.1)

---

## livekit-plugins-openai@0.10.18: livekit-plugins-openai@0.10.18
**Published:** 2025-02-11

### Patch Changes

-   Added an additional field in LLM capabilities class to check if model providers support function call history within chat context without needing function definitions. - [#1441](https://github.com/livekit/agents/pull/1441) ([@jayeshp19](https://github.com/jayeshp19))


[View on GitHub](https://github.com/livekit/agents/releases/tag/livekit-plugins-openai%400.10.18)

---

## livekit-plugins-google@0.10.3: livekit-plugins-google@0.10.3
**Published:** 2025-02-11

### Patch Changes

-   Gemini Realtime: Transcribe model audio via gemini api & use latest model as default for google plugin - [#1446](https://github.com/livekit/agents/pull/1446) ([@jayeshp19](https://github.com/jayeshp19))

-   Update to support passing chirp_2 location for other STT credentials - [#1098](https://github.com/livekit/agents/pull/1098) ([@brightsparc](https://github.com/brightsparc))

-   Added an additional field in LLM capabilities class to check if model providers support function call history within chat context without needing function definitions. - [#1441](https://github.com/livekit/agents/pull/1441) ([@jayeshp19](https://github.com/jayeshp19))


[View on GitHub](https://github.com/livekit/agents/releases/tag/livekit-plugins-google%400.10.3)

---

## livekit-plugins-elevenlabs@0.7.13: livekit-plugins-elevenlabs@0.7.13
**Published:** 2025-02-11

### Patch Changes

-   11labs: ensure websocket connection is closed properly - [#1468](https://github.com/livekit/agents/pull/1468) ([@davidzhao](https://github.com/davidzhao))


[View on GitHub](https://github.com/livekit/agents/releases/tag/livekit-plugins-elevenlabs%400.7.13)

---

## livekit-plugins-deepgram@0.6.18: livekit-plugins-deepgram@0.6.18
**Published:** 2025-02-11

### Patch Changes

-   chore(Deepgram STT): add nova-3 model to type literal - [#1464](https://github.com/livekit/agents/pull/1464) ([@chasemcdo](https://github.com/chasemcdo))


[View on GitHub](https://github.com/livekit/agents/releases/tag/livekit-plugins-deepgram%400.6.18)

---

## livekit-plugins-anthropic@0.2.10: livekit-plugins-anthropic@0.2.10
**Published:** 2025-02-11

### Patch Changes

-   Added an additional field in LLM capabilities class to check if model providers support function call history within chat context without needing function definitions. - [#1441](https://github.com/livekit/agents/pull/1441) ([@jayeshp19](https://github.com/jayeshp19))


[View on GitHub](https://github.com/livekit/agents/releases/tag/livekit-plugins-anthropic%400.2.10)

---

## livekit-agents@0.12.12: livekit-agents@0.12.12
**Published:** 2025-02-11

### Patch Changes

-   fix agent transcription could not be disabled - [#1448](https://github.com/livekit/agents/pull/1448) ([@davidzhao](https://github.com/davidzhao))

-   Added an additional field in LLM capabilities class to check if model providers support function call history within chat context without needing function definitions. - [#1441](https://github.com/livekit/agents/pull/1441) ([@jayeshp19](https://github.com/jayeshp19))

-   support agent.say inside the before_llm_cb - [#1460](https://github.com/livekit/agents/pull/1460) ([@longcw](https://github.com/longcw))


[View on GitHub](https://github.com/livekit/agents/releases/tag/livekit-agents%400.12.12)

---

## livekit-plugins-turn-detector@0.4.0: livekit-plugins-turn-detector@0.4.0
**Published:** 2025-01-31

### Minor Changes

-   more accurate, smaller, faster model - [#1426](https://github.com/livekit/agents/pull/1426) ([@jeradf](https://github.com/jeradf))


[View on GitHub](https://github.com/livekit/agents/releases/tag/livekit-plugins-turn-detector%400.4.0)

---

## livekit-plugins-playai@1.0.7: livekit-plugins-playai@1.0.7
**Published:** 2025-01-31

### Patch Changes

-   PlayAI plugin: bump Python SDK version (fix websockets interrupt handling) - [#1427](https://github.com/livekit/agents/pull/1427) ([@bryananderson](https://github.com/bryananderson))

-   improved TTFB metrics for streaming TTS - [#1431](https://github.com/livekit/agents/pull/1431) ([@davidzhao](https://github.com/davidzhao))


[View on GitHub](https://github.com/livekit/agents/releases/tag/livekit-plugins-playai%401.0.7)

---

## livekit-plugins-openai@0.10.17: livekit-plugins-openai@0.10.17
**Published:** 2025-01-31

### Patch Changes

-   gemini-realtime: fix input audio sample rate - [#1411](https://github.com/livekit/agents/pull/1411) ([@jayeshp19](https://github.com/jayeshp19))


[View on GitHub](https://github.com/livekit/agents/releases/tag/livekit-plugins-openai%400.10.17)

---

## livekit-plugins-google@0.10.2: livekit-plugins-google@0.10.2
**Published:** 2025-01-31

### Patch Changes

-   gemini-realtime: fix input audio sample rate - [#1411](https://github.com/livekit/agents/pull/1411) ([@jayeshp19](https://github.com/jayeshp19))

-   chore: Replace ValueError with logger.warning for missing GOOGLE_APPLICATION_CREDENTIALS environment variable - [#1415](https://github.com/livekit/agents/pull/1415) ([@hironow](https://github.com/hironow))


[View on GitHub](https://github.com/livekit/agents/releases/tag/livekit-plugins-google%400.10.2)

---

## livekit-plugins-elevenlabs@0.7.12: livekit-plugins-elevenlabs@0.7.12
**Published:** 2025-01-31

### Patch Changes

-   improved TTFB metrics for streaming TTS - [#1431](https://github.com/livekit/agents/pull/1431) ([@davidzhao](https://github.com/davidzhao))


[View on GitHub](https://github.com/livekit/agents/releases/tag/livekit-plugins-elevenlabs%400.7.12)

---

## livekit-plugins-deepgram@0.6.17: livekit-plugins-deepgram@0.6.17
**Published:** 2025-01-31

### Patch Changes

-   improved TTFB metrics for streaming TTS - [#1431](https://github.com/livekit/agents/pull/1431) ([@davidzhao](https://github.com/davidzhao))


[View on GitHub](https://github.com/livekit/agents/releases/tag/livekit-plugins-deepgram%400.6.17)

---

## livekit-plugins-cartesia@0.4.7: livekit-plugins-cartesia@0.4.7
**Published:** 2025-01-31

### Patch Changes

-   improved TTFB metrics for streaming TTS - [#1431](https://github.com/livekit/agents/pull/1431) ([@davidzhao](https://github.com/davidzhao))


[View on GitHub](https://github.com/livekit/agents/releases/tag/livekit-plugins-cartesia%400.4.7)

---

## livekit-agents@0.12.11: livekit-agents@0.12.11
**Published:** 2025-01-31

### Patch Changes

-   gemini-realtime: fix input audio sample rate - [#1411](https://github.com/livekit/agents/pull/1411) ([@jayeshp19](https://github.com/jayeshp19))

-   fix(pipeline_agent): clear user transcript when before_llm_cb returns false - [#1423](https://github.com/livekit/agents/pull/1423) ([@s-hamdananwar](https://github.com/s-hamdananwar))

-   fix: fallbackadapter to correctly handle function calls - [#1429](https://github.com/livekit/agents/pull/1429) ([@davidzhao](https://github.com/davidzhao))

-   improved TTFB metrics for streaming TTS - [#1431](https://github.com/livekit/agents/pull/1431) ([@davidzhao](https://github.com/davidzhao))


[View on GitHub](https://github.com/livekit/agents/releases/tag/livekit-agents%400.12.11)

---

## livekit-plugins-google@0.10.1: livekit-plugins-google@0.10.1
**Published:** 2025-01-26

### Patch Changes

-   fix: update default model to chirp2 in google stt & update generate_reply method in gemini realtime - [#1401](https://github.com/livekit/agents/pull/1401) ([@jayeshp19](https://github.com/jayeshp19))


[View on GitHub](https://github.com/livekit/agents/releases/tag/livekit-plugins-google%400.10.1)

---

## livekit-agents@0.12.10: livekit-agents@0.12.10
**Published:** 2025-01-26

### Patch Changes

-   fix false positive interruption tripping up certain LLMs - [#1410](https://github.com/livekit/agents/pull/1410) ([@davidzhao](https://github.com/davidzhao))

-   fix: ensure llm.FallbackAdapter executes function calls - [#1409](https://github.com/livekit/agents/pull/1409) ([@davidzhao](https://github.com/davidzhao))


[View on GitHub](https://github.com/livekit/agents/releases/tag/livekit-agents%400.12.10)

---

## livekit-plugins-rime@0.2.0: livekit-plugins-rime@0.2.0
**Published:** 2025-01-22

### Minor Changes

-   inital release - [#1377](https://github.com/livekit/agents/pull/1377) ([@jayeshp19](https://github.com/jayeshp19))


[View on GitHub](https://github.com/livekit/agents/releases/tag/livekit-plugins-rime%400.2.0)

---

## livekit-plugins-playai@1.0.6: livekit-plugins-playai@1.0.6
**Published:** 2025-01-22

### Patch Changes

-   fix: Avoid websocket reconnections for each request - [#1387](https://github.com/livekit/agents/pull/1387) ([@jayeshp19](https://github.com/jayeshp19))


[View on GitHub](https://github.com/livekit/agents/releases/tag/livekit-plugins-playai%401.0.6)

---

## livekit-plugins-openai@0.10.16: livekit-plugins-openai@0.10.16
**Published:** 2025-01-22

### Patch Changes

-   add generate_reply api for multimodal agent - [#1359](https://github.com/livekit/agents/pull/1359) ([@longcw](https://github.com/longcw))


[View on GitHub](https://github.com/livekit/agents/releases/tag/livekit-plugins-openai%400.10.16)

---

## livekit-plugins-google@0.10.0: livekit-plugins-google@0.10.0
**Published:** 2025-01-22

### Minor Changes

-   support gemini LLM - [#1382](https://github.com/livekit/agents/pull/1382) ([@jayeshp19](https://github.com/jayeshp19))

### Patch Changes

-   fix: address breaking change from google-genai >= 0.3.0 - [#1383](https://github.com/livekit/agents/pull/1383) ([@jayeshp19](https://github.com/jayeshp19))

-   gemini improvements: exception handling, transcription & Ensure contents.parts is non-empty in gemini contex - [#1398](https://github.com/livekit/agents/pull/1398) ([@jayeshp19](https://github.com/jayeshp19))

-   support transcriber session for user/agent audio - [#1321](https://github.com/livekit/agents/pull/1321) ([@jayeshp19](https://github.com/jayeshp19))


[View on GitHub](https://github.com/livekit/agents/releases/tag/livekit-plugins-google%400.10.0)

---

## livekit-plugins-elevenlabs@0.7.11: livekit-plugins-elevenlabs@0.7.11
**Published:** 2025-01-22

### Patch Changes

-   add latest model by 11labs - [#1396](https://github.com/livekit/agents/pull/1396) ([@jayeshp19](https://github.com/jayeshp19))


[View on GitHub](https://github.com/livekit/agents/releases/tag/livekit-plugins-elevenlabs%400.7.11)

---

## livekit-agents@0.12.9: livekit-agents@0.12.9
**Published:** 2025-01-22

### Patch Changes

-   add generate_reply api for multimodal agent - [#1359](https://github.com/livekit/agents/pull/1359) ([@longcw](https://github.com/longcw))

-   remove aiodns from livekit-agents - [#1368](https://github.com/livekit/agents/pull/1368) ([@theomonnom](https://github.com/theomonnom))


[View on GitHub](https://github.com/livekit/agents/releases/tag/livekit-agents%400.12.9)

---

## livekit-plugins-turn-detector@0.3.6: livekit-plugins-turn-detector@0.3.6
**Published:** 2025-01-12

### Patch Changes

-   prevent arbitrarily long inputs being passed to turn detector - [#1345](https://github.com/livekit/agents/pull/1345) ([@jeradf](https://github.com/jeradf))

-   add timeout for EOU inference requests made to the inference process - [#1315](https://github.com/livekit/agents/pull/1315) ([@theomonnom](https://github.com/theomonnom))


[View on GitHub](https://github.com/livekit/agents/releases/tag/livekit-plugins-turn-detector%400.3.6)

---

## livekit-plugins-playai@1.0.5: livekit-plugins-playai@1.0.5
**Published:** 2025-01-12

### Patch Changes

-   playai: enable streaming TTS - [#1340](https://github.com/livekit/agents/pull/1340) ([@davidzhao](https://github.com/davidzhao))


[View on GitHub](https://github.com/livekit/agents/releases/tag/livekit-plugins-playai%401.0.5)

---

## livekit-plugins-openai@0.10.15: livekit-plugins-openai@0.10.15
**Published:** 2025-01-12

### Patch Changes

-   support disabling server VAD for OpenAI realtime model - [#1347](https://github.com/livekit/agents/pull/1347) ([@longcw](https://github.com/longcw))


[View on GitHub](https://github.com/livekit/agents/releases/tag/livekit-plugins-openai%400.10.15)

---

## livekit-plugins-google@0.9.1: livekit-plugins-google@0.9.1
**Published:** 2025-01-12

### Patch Changes

-   fetch fresh client on update location and small fix for max_session_duration (4 mins) - [#1342](https://github.com/livekit/agents/pull/1342) ([@jayeshp19](https://github.com/jayeshp19))

-   fix Google STT handling of session timeouts - [#1337](https://github.com/livekit/agents/pull/1337) ([@davidzhao](https://github.com/davidzhao))


[View on GitHub](https://github.com/livekit/agents/releases/tag/livekit-plugins-google%400.9.1)

---

## livekit-plugins-fal@0.2.3: livekit-plugins-fal@0.2.3
**Published:** 2025-01-12

### Patch Changes

-   publish package - [`ed974f81a2eab7c1b2d7cff3a27c868ddebb45ee`](https://github.com/livekit/agents/commit/ed974f81a2eab7c1b2d7cff3a27c868ddebb45ee) ([@davidzhao](https://github.com/davidzhao))


[View on GitHub](https://github.com/livekit/agents/releases/tag/livekit-plugins-fal%400.2.3)

---

## livekit-plugins-elevenlabs@0.7.10: livekit-plugins-elevenlabs@0.7.10
**Published:** 2025-01-12

### Patch Changes

-   Add language param to ElevenLabs TTS update_options - [#1333](https://github.com/livekit/agents/pull/1333) ([@cch41](https://github.com/cch41))


[View on GitHub](https://github.com/livekit/agents/releases/tag/livekit-plugins-elevenlabs%400.7.10)

---

## livekit-plugins-cartesia@0.4.6: livekit-plugins-cartesia@0.4.6
**Published:** 2025-01-12

### Patch Changes

-   update Cartesia plugin default model and voice id - [#1346](https://github.com/livekit/agents/pull/1346) ([@noahlt](https://github.com/noahlt))


[View on GitHub](https://github.com/livekit/agents/releases/tag/livekit-plugins-cartesia%400.4.6)

---

## livekit-plugins-azure@0.5.3: livekit-plugins-azure@0.5.3
**Published:** 2025-01-12

### Patch Changes

-   azure speech support all different configs - [#1362](https://github.com/livekit/agents/pull/1362) ([@longcw](https://github.com/longcw))

-   reduces initial delay before model retries - [#1337](https://github.com/livekit/agents/pull/1337) ([@davidzhao](https://github.com/davidzhao))


[View on GitHub](https://github.com/livekit/agents/releases/tag/livekit-plugins-azure%400.5.3)

---

## livekit-agents@0.12.8: livekit-agents@0.12.8
**Published:** 2025-01-12

### Patch Changes

-   Fix not awaiting forward task in TTS forwarder, leading to warnings. - [#1339](https://github.com/livekit/agents/pull/1339) ([@martin-purplefish](https://github.com/martin-purplefish))

-   reduces initial delay before model retries - [#1337](https://github.com/livekit/agents/pull/1337) ([@davidzhao](https://github.com/davidzhao))

-   fix the function calls without a text response are not added to chat ctx - [#1349](https://github.com/livekit/agents/pull/1349) ([@longcw](https://github.com/longcw))

-   add timeout for EOU inference requests made to the inference process - [#1315](https://github.com/livekit/agents/pull/1315) ([@theomonnom](https://github.com/theomonnom))

-   support disabling server VAD for OpenAI realtime model - [#1347](https://github.com/livekit/agents/pull/1347) ([@longcw](https://github.com/longcw))


[View on GitHub](https://github.com/livekit/agents/releases/tag/livekit-agents%400.12.8)

---

## livekit-plugins-openai@0.10.14: livekit-plugins-openai@0.10.14
**Published:** 2025-01-02

### Patch Changes

-   fix: revert from weakset to list in multimodal for maintaining sessions - [#1326](https://github.com/livekit/agents/pull/1326) ([@jayeshp19](https://github.com/jayeshp19))


[View on GitHub](https://github.com/livekit/agents/releases/tag/livekit-plugins-openai%400.10.14)

---

## livekit-agents@0.12.7: livekit-agents@0.12.7
**Published:** 2025-01-02

### Patch Changes

-   ensure job status updates contain the correct status - [#1319](https://github.com/livekit/agents/pull/1319) ([@davidzhao](https://github.com/davidzhao))


[View on GitHub](https://github.com/livekit/agents/releases/tag/livekit-agents%400.12.7)

---

## livekit-plugins-turn-detector@0.3.5: livekit-plugins-turn-detector@0.3.5
**Published:** 2024-12-31

### Patch Changes

-   fix int32/64 errors on Windows - [#1285](https://github.com/livekit/agents/pull/1285) ([@nbsp](https://github.com/nbsp))


[View on GitHub](https://github.com/livekit/agents/releases/tag/livekit-plugins-turn-detector%400.3.5)

---

## livekit-plugins-playai@1.0.4: livekit-plugins-playai@1.0.4
**Published:** 2024-12-31

### Patch Changes

-   Support PlayAI TTS engine. - [#1174](https://github.com/livekit/agents/pull/1174) ([@jayeshp19](https://github.com/jayeshp19))


[View on GitHub](https://github.com/livekit/agents/releases/tag/livekit-plugins-playai%401.0.4)

---

## livekit-plugins-openai@0.10.13: livekit-plugins-openai@0.10.13
**Published:** 2024-12-31

### Patch Changes

-   improved handling of LLM errors, do not retry if already began - [#1298](https://github.com/livekit/agents/pull/1298) ([@davidzhao](https://github.com/davidzhao))

-   make multimodal class generic and support gemini live api - [#1240](https://github.com/livekit/agents/pull/1240) ([@jayeshp19](https://github.com/jayeshp19))


[View on GitHub](https://github.com/livekit/agents/releases/tag/livekit-plugins-openai%400.10.13)

---

## livekit-plugins-google@0.9.0: livekit-plugins-google@0.9.0
**Published:** 2024-12-31

### Minor Changes

-   make multimodal class generic and support gemini live api - [#1240](https://github.com/livekit/agents/pull/1240) ([@jayeshp19](https://github.com/jayeshp19))

### Patch Changes

-   fix: Ensure STT exceptions are being propagated - [#1291](https://github.com/livekit/agents/pull/1291) ([@davidzhao](https://github.com/davidzhao))


[View on GitHub](https://github.com/livekit/agents/releases/tag/livekit-plugins-google%400.9.0)

---

## livekit-plugins-deepgram@0.6.16: livekit-plugins-deepgram@0.6.16
**Published:** 2024-12-31

### Patch Changes

-   fix: Ensure STT exceptions are being propagated - [#1291](https://github.com/livekit/agents/pull/1291) ([@davidzhao](https://github.com/davidzhao))


[View on GitHub](https://github.com/livekit/agents/releases/tag/livekit-plugins-deepgram%400.6.16)

---

## livekit-plugins-azure@0.5.2: livekit-plugins-azure@0.5.2
**Published:** 2024-12-31

### Patch Changes

-   fix: Ensure STT exceptions are being propagated - [#1291](https://github.com/livekit/agents/pull/1291) ([@davidzhao](https://github.com/davidzhao))


[View on GitHub](https://github.com/livekit/agents/releases/tag/livekit-plugins-azure%400.5.2)

---

## livekit-plugins-assemblyai@0.2.2: livekit-plugins-assemblyai@0.2.2
**Published:** 2024-12-31

### Patch Changes

-   fix: Ensure STT exceptions are being propagated - [#1291](https://github.com/livekit/agents/pull/1291) ([@davidzhao](https://github.com/davidzhao))

-   assemblyai: encode boost words - [#1284](https://github.com/livekit/agents/pull/1284) ([@jmugicagonz](https://github.com/jmugicagonz))


[View on GitHub](https://github.com/livekit/agents/releases/tag/livekit-plugins-assemblyai%400.2.2)

---

## livekit-plugins-anthropic@0.2.9: livekit-plugins-anthropic@0.2.9
**Published:** 2024-12-31

### Patch Changes

-   improved handling of LLM errors, do not retry if already began - [#1298](https://github.com/livekit/agents/pull/1298) ([@davidzhao](https://github.com/davidzhao))


[View on GitHub](https://github.com/livekit/agents/releases/tag/livekit-plugins-anthropic%400.2.9)

---

## livekit-agents@0.12.6: livekit-agents@0.12.6
**Published:** 2024-12-31

### Patch Changes

-   expose worker_id in jobcontext - [#1307](https://github.com/livekit/agents/pull/1307) ([@s-hamdananwar](https://github.com/s-hamdananwar))

-   improved handling of LLM errors, do not retry if already began - [#1298](https://github.com/livekit/agents/pull/1298) ([@davidzhao](https://github.com/davidzhao))

-   Do not pass function context if at max depth - [#1306](https://github.com/livekit/agents/pull/1306) ([@martin-purplefish](https://github.com/martin-purplefish))

-   avoid warnings when function depth matches limit - [#1316](https://github.com/livekit/agents/pull/1316) ([@davidzhao](https://github.com/davidzhao))

-   improve interruption handling, avoid agent from getting stuck - [#1290](https://github.com/livekit/agents/pull/1290) ([@davidzhao](https://github.com/davidzhao))

-   add manual interrupt method for pipeline agent - [#1294](https://github.com/livekit/agents/pull/1294) ([@longcw](https://github.com/longcw))

-   make multimodal class generic and support gemini live api - [#1240](https://github.com/livekit/agents/pull/1240) ([@jayeshp19](https://github.com/jayeshp19))


[View on GitHub](https://github.com/livekit/agents/releases/tag/livekit-agents%400.12.6)

---

## livekit-plugins-turn-detector@0.3.4: livekit-plugins-turn-detector@0.3.4
**Published:** 2024-12-23

### Patch Changes

-   add jinja2 dependency to turn detector - [#1277](https://github.com/livekit/agents/pull/1277) ([@davidzhao](https://github.com/davidzhao))


[View on GitHub](https://github.com/livekit/agents/releases/tag/livekit-plugins-turn-detector%400.3.4)

---

## livekit-plugins-openai@0.10.12: livekit-plugins-openai@0.10.12
**Published:** 2024-12-23

### Patch Changes

-   fix unknown `metadata` & `store` fields on OpenAI-like API - [#1276](https://github.com/livekit/agents/pull/1276) ([@theomonnom](https://github.com/theomonnom))


[View on GitHub](https://github.com/livekit/agents/releases/tag/livekit-plugins-openai%400.10.12)

---

## livekit-agents@0.12.5: livekit-agents@0.12.5
**Published:** 2024-12-23

### Patch Changes

-   make max_endpoint_delay configurable - [#1277](https://github.com/livekit/agents/pull/1277) ([@davidzhao](https://github.com/davidzhao))

-   set USE_DOCSTRING as default for ai_callable - [#1266](https://github.com/livekit/agents/pull/1266) ([@longcw](https://github.com/longcw))

-   fix: do not log process warning when process not found - [#1281](https://github.com/livekit/agents/pull/1281) ([@davidzhao](https://github.com/davidzhao))

-   fix context when functions have been called - [#1279](https://github.com/livekit/agents/pull/1279) ([@jmugicagonz](https://github.com/jmugicagonz))


[View on GitHub](https://github.com/livekit/agents/releases/tag/livekit-agents%400.12.5)

---

## livekit-agents@0.12.4: livekit-agents@0.12.4
**Published:** 2024-12-23

### Patch Changes

-   avoid duplicated chat ctx for function calls with messages - [#1254](https://github.com/livekit/agents/pull/1254) ([@longcw](https://github.com/longcw))


[View on GitHub](https://github.com/livekit/agents/releases/tag/livekit-agents%400.12.4)

---

## livekit-plugins-turn-detector@0.3.3: livekit-plugins-turn-detector@0.3.3
**Published:** 2024-12-20

### Patch Changes

-   use quantized onnx version of turn detector model - [#1231](https://github.com/livekit/agents/pull/1231) ([@jeradf](https://github.com/jeradf))

-   use onnxruntime for turn detection and remove pytorch dependency - [#1257](https://github.com/livekit/agents/pull/1257) ([@jeradf](https://github.com/jeradf))


[View on GitHub](https://github.com/livekit/agents/releases/tag/livekit-plugins-turn-detector%400.3.3)

---

## livekit-plugins-openai@0.10.11: livekit-plugins-openai@0.10.11
**Published:** 2024-12-20

### Patch Changes

-   Moved create_ai_function_info to function_context.py for better reusability and reduce repetation - [#1260](https://github.com/livekit/agents/pull/1260) ([@jayeshp19](https://github.com/jayeshp19))

-   add on_duplicate option for multimodal agent response create - [#1204](https://github.com/livekit/agents/pull/1204) ([@longcw](https://github.com/longcw))

-   Add support for OpenAI's "detail" parameter to ChatImage - [#1213](https://github.com/livekit/agents/pull/1213) ([@bcherry](https://github.com/bcherry))

    Add support for data URLs on ChatImage in the Anthropic plugin.

-   filter out empty message for set chat ctx in realtime model - [#1245](https://github.com/livekit/agents/pull/1245) ([@longcw](https://github.com/longcw))

-   fix: correctly parse function argument types - [#1221](https://github.com/livekit/agents/pull/1221) ([@jayeshp19](https://github.com/jayeshp19))

-   add session_updated event for RealtimeSession - [#1253](https://github.com/livekit/agents/pull/1253) ([@longcw](https://github.com/longcw))

-   added llama 3.3 70b to model definitions - [#1233](https://github.com/livekit/agents/pull/1233) ([@davidzhao](https://github.com/davidzhao))

-   update default realtime model to gpt-4o-realtime-preview-2024-12-17 - [#1250](https://github.com/livekit/agents/pull/1250) ([@davidzhao](https://github.com/davidzhao))

-   Fix center_aspect_fit bug, add scale_aspect_fit and scale_aspect_fill resizing options. - [#1222](https://github.com/livekit/agents/pull/1222) ([@bcherry](https://github.com/bcherry))

    Make scale_aspect_fit the new default resizing option for video frames.


[View on GitHub](https://github.com/livekit/agents/releases/tag/livekit-plugins-openai%400.10.11)

---

## livekit-plugins-deepgram@0.6.15: livekit-plugins-deepgram@0.6.15
**Published:** 2024-12-20

### Patch Changes

-   added streaming audio decoder for compressed audio. - [#1236](https://github.com/livekit/agents/pull/1236) ([@davidzhao](https://github.com/davidzhao))

-   Support Deepgram TTS - [#1201](https://github.com/livekit/agents/pull/1201) ([@jayeshp19](https://github.com/jayeshp19))


[View on GitHub](https://github.com/livekit/agents/releases/tag/livekit-plugins-deepgram%400.6.15)

---

## livekit-plugins-browser@0.0.5: livekit-plugins-browser@0.0.5
**Published:** 2024-12-20

### Patch Changes

-   fix: fix `imgui` setup - [#1226](https://github.com/livekit/agents/pull/1226) ([@mbukeRepo](https://github.com/mbukeRepo))


[View on GitHub](https://github.com/livekit/agents/releases/tag/livekit-plugins-browser%400.0.5)

---

## livekit-plugins-azure@0.5.1: livekit-plugins-azure@0.5.1
**Published:** 2024-12-20

### Patch Changes

-   fix azure stt language autodetection - [#1246](https://github.com/livekit/agents/pull/1246) ([@davidzhao](https://github.com/davidzhao))


[View on GitHub](https://github.com/livekit/agents/releases/tag/livekit-plugins-azure%400.5.1)

---

## livekit-plugins-anthropic@0.2.8: livekit-plugins-anthropic@0.2.8
**Published:** 2024-12-20

### Patch Changes

-   Moved create_ai_function_info to function_context.py for better reusability and reduce repetation - [#1260](https://github.com/livekit/agents/pull/1260) ([@jayeshp19](https://github.com/jayeshp19))

-   Add support for OpenAI's "detail" parameter to ChatImage - [#1213](https://github.com/livekit/agents/pull/1213) ([@bcherry](https://github.com/bcherry))

    Add support for data URLs on ChatImage in the Anthropic plugin.

-   fix: correctly parse function argument types - [#1221](https://github.com/livekit/agents/pull/1221) ([@jayeshp19](https://github.com/jayeshp19))

-   Fix center_aspect_fit bug, add scale_aspect_fit and scale_aspect_fill resizing options. - [#1222](https://github.com/livekit/agents/pull/1222) ([@bcherry](https://github.com/bcherry))

    Make scale_aspect_fit the new default resizing option for video frames.


[View on GitHub](https://github.com/livekit/agents/releases/tag/livekit-plugins-anthropic%400.2.8)

---

## livekit-agents@0.12.3: livekit-agents@0.12.3
**Published:** 2024-12-20

### Patch Changes

-   Moved create_ai_function_info to function_context.py for better reusability and reduce repetation - [#1260](https://github.com/livekit/agents/pull/1260) ([@jayeshp19](https://github.com/jayeshp19))

-   added streaming audio decoder for compressed audio. - [#1236](https://github.com/livekit/agents/pull/1236) ([@davidzhao](https://github.com/davidzhao))

-   Add JPEG quality param to image encoder - [#1249](https://github.com/livekit/agents/pull/1249) ([@bcherry](https://github.com/bcherry))

-   Add support for OpenAI's "detail" parameter to ChatImage - [#1213](https://github.com/livekit/agents/pull/1213) ([@bcherry](https://github.com/bcherry))

    Add support for data URLs on ChatImage in the Anthropic plugin.

-   fix: correctly parse function argument types - [#1221](https://github.com/livekit/agents/pull/1221) ([@jayeshp19](https://github.com/jayeshp19))

-   Fix center_aspect_fit bug, add scale_aspect_fit and scale_aspect_fill resizing options. - [#1222](https://github.com/livekit/agents/pull/1222) ([@bcherry](https://github.com/bcherry))

    Make scale_aspect_fit the new default resizing option for video frames.


[View on GitHub](https://github.com/livekit/agents/releases/tag/livekit-agents%400.12.3)

---

## livekit-plugins-turn-detector@0.3.2: livekit-plugins-turn-detector@0.3.2
**Published:** 2024-12-12

### Patch Changes

-   improvements to endpointing latency - [#1212](https://github.com/livekit/agents/pull/1212) ([@davidzhao](https://github.com/davidzhao))

-   Improvements to end of turn plugin, ensure STT language settings. - [#1195](https://github.com/livekit/agents/pull/1195) ([@davidzhao](https://github.com/davidzhao))


[View on GitHub](https://github.com/livekit/agents/releases/tag/livekit-plugins-turn-detector%400.3.2)

---

## livekit-plugins-openai@0.10.10: livekit-plugins-openai@0.10.10
**Published:** 2024-12-12

### Patch Changes

-   add `google/gemini-2.0-flash-exp` as default model for vertex - [#1214](https://github.com/livekit/agents/pull/1214) ([@jayeshp19](https://github.com/jayeshp19))

-   emit error event for realtime model - [#1200](https://github.com/livekit/agents/pull/1200) ([@longcw](https://github.com/longcw))

-   fix: return structured output from func calls - [#1187](https://github.com/livekit/agents/pull/1187) ([@jayeshp19](https://github.com/jayeshp19))

-   Handle optional func args in tool calls when set to `None` - [#1211](https://github.com/livekit/agents/pull/1211) ([@jayeshp19](https://github.com/jayeshp19))

-   fix: openai llm retries - [#1196](https://github.com/livekit/agents/pull/1196) ([@theomonnom](https://github.com/theomonnom))

-   Improvements to end of turn plugin, ensure STT language settings. - [#1195](https://github.com/livekit/agents/pull/1195) ([@davidzhao](https://github.com/davidzhao))

-   fix: Handle optional func args in tool calls when set to `None` - [#1211](https://github.com/livekit/agents/pull/1211) ([@jayeshp19](https://github.com/jayeshp19))


[View on GitHub](https://github.com/livekit/agents/releases/tag/livekit-plugins-openai%400.10.10)

---

## livekit-plugins-deepgram@0.6.14: livekit-plugins-deepgram@0.6.14
**Published:** 2024-12-12

### Patch Changes

-   enable deepgram filler words by default to improve end of turn accuracy - [#1190](https://github.com/livekit/agents/pull/1190) ([@davidzhao](https://github.com/davidzhao))


[View on GitHub](https://github.com/livekit/agents/releases/tag/livekit-plugins-deepgram%400.6.14)

---

## livekit-plugins-azure@0.5.0: livekit-plugins-azure@0.5.0
**Published:** 2024-12-12

### Minor Changes

-   Improvements to end of turn plugin, ensure STT language settings. - [#1195](https://github.com/livekit/agents/pull/1195) ([@davidzhao](https://github.com/davidzhao))


[View on GitHub](https://github.com/livekit/agents/releases/tag/livekit-plugins-azure%400.5.0)

---

## livekit-plugins-anthropic@0.2.7: livekit-plugins-anthropic@0.2.7
**Published:** 2024-12-12

### Patch Changes

-   fix: return structured output from func calls - [#1187](https://github.com/livekit/agents/pull/1187) ([@jayeshp19](https://github.com/jayeshp19))


[View on GitHub](https://github.com/livekit/agents/releases/tag/livekit-plugins-anthropic%400.2.7)

---

## livekit-agents@0.12.2: livekit-agents@0.12.2
**Published:** 2024-12-12

### Patch Changes

-   improvements to endpointing latency - [#1212](https://github.com/livekit/agents/pull/1212) ([@davidzhao](https://github.com/davidzhao))

-   Improvements to end of turn plugin, ensure STT language settings. - [#1195](https://github.com/livekit/agents/pull/1195) ([@davidzhao](https://github.com/davidzhao))

-   fix duplicated agent speech commit for message with function call - [#1192](https://github.com/livekit/agents/pull/1192) ([@longcw](https://github.com/longcw))

-   fix: Handle optional func args in tool calls when set to `None` - [#1211](https://github.com/livekit/agents/pull/1211) ([@jayeshp19](https://github.com/jayeshp19))


[View on GitHub](https://github.com/livekit/agents/releases/tag/livekit-agents%400.12.2)

---

## livekit-plugins-turn-detector@0.3.1: livekit-plugins-turn-detector@0.3.1
**Published:** 2024-12-04

### Patch Changes

-   fix release - [#1176](https://github.com/livekit/agents/pull/1176) ([@theomonnom](https://github.com/theomonnom))


[View on GitHub](https://github.com/livekit/agents/releases/tag/livekit-plugins-turn-detector%400.3.1)

---

## livekit-plugins-turn-detector@0.3.0: livekit-plugins-turn-detector@0.3.0
**Published:** 2024-12-04

### Minor Changes

-   feat: inference process & end of utterance plugin - [#1133](https://github.com/livekit/agents/pull/1133) ([@theomonnom](https://github.com/theomonnom))


[View on GitHub](https://github.com/livekit/agents/releases/tag/livekit-plugins-turn-detector%400.3.0)

---

## livekit-plugins-silero@0.7.4: livekit-plugins-silero@0.7.4
**Published:** 2024-12-04

### Patch Changes

-   fix release - [#1176](https://github.com/livekit/agents/pull/1176) ([@theomonnom](https://github.com/theomonnom))


[View on GitHub](https://github.com/livekit/agents/releases/tag/livekit-plugins-silero%400.7.4)

---

## livekit-plugins-rag@0.2.3: livekit-plugins-rag@0.2.3
**Published:** 2024-12-04

### Patch Changes

-   fix release - [#1176](https://github.com/livekit/agents/pull/1176) ([@theomonnom](https://github.com/theomonnom))


[View on GitHub](https://github.com/livekit/agents/releases/tag/livekit-plugins-rag%400.2.3)

---

## livekit-plugins-playht@1.0.3: livekit-plugins-playht@1.0.3
**Published:** 2024-12-04

### Patch Changes

-   fix release - [#1176](https://github.com/livekit/agents/pull/1176) ([@theomonnom](https://github.com/theomonnom))


[View on GitHub](https://github.com/livekit/agents/releases/tag/livekit-plugins-playht%401.0.3)

---

## livekit-plugins-playht@1.0.2: livekit-plugins-playht@1.0.2
**Published:** 2024-12-04

### Patch Changes

-   fix(playht): add sample_rate parameter to JSON payload - [#1141](https://github.com/livekit/agents/pull/1141) ([@imsakg](https://github.com/imsakg))

-   feat: tts retry & tts.FallbackAdapter - [#1074](https://github.com/livekit/agents/pull/1074) ([@theomonnom](https://github.com/theomonnom))

-   feat(playht): add Play3.0-mini engine support - [#1140](https://github.com/livekit/agents/pull/1140) ([@imsakg](https://github.com/imsakg))


[View on GitHub](https://github.com/livekit/agents/releases/tag/livekit-plugins-playht%401.0.2)

---

## livekit-plugins-openai@0.10.9: livekit-plugins-openai@0.10.9
**Published:** 2024-12-04

### Patch Changes

-   fix release - [#1176](https://github.com/livekit/agents/pull/1176) ([@theomonnom](https://github.com/theomonnom))


[View on GitHub](https://github.com/livekit/agents/releases/tag/livekit-plugins-openai%400.10.9)

---

## livekit-plugins-openai@0.10.8: livekit-plugins-openai@0.10.8
**Published:** 2024-12-04

### Patch Changes

-   fix uncatched OAI errors - [#1158](https://github.com/livekit/agents/pull/1158) ([@theomonnom](https://github.com/theomonnom))

-   feat: stt retry & stt.FallbackAdapter - [#1114](https://github.com/livekit/agents/pull/1114) ([@theomonnom](https://github.com/theomonnom))

-   project id fix for google - [#1115](https://github.com/livekit/agents/pull/1115) ([@jayeshp19](https://github.com/jayeshp19))

-   Add retries to recover from text mode to audio model for realtime API - [#1121](https://github.com/livekit/agents/pull/1121) ([@longcw](https://github.com/longcw))

-   Support for Python 3.13, relaxed Pillow version requirement for 10.x - [#1127](https://github.com/livekit/agents/pull/1127) ([@davidzhao](https://github.com/davidzhao))

-   support for custom tool use in LLMs - [#1102](https://github.com/livekit/agents/pull/1102) ([@jayeshp19](https://github.com/jayeshp19))

-   feat: tts retry & tts.FallbackAdapter - [#1074](https://github.com/livekit/agents/pull/1074) ([@theomonnom](https://github.com/theomonnom))

-   Add new OpenAI realtime voices - [#1116](https://github.com/livekit/agents/pull/1116) ([@bcherry](https://github.com/bcherry))

-   Expose multimodal agent metrics - [#1080](https://github.com/livekit/agents/pull/1080) ([@longcw](https://github.com/longcw))

-   feat: llm retry & llm.FallbackAdapter - [#1132](https://github.com/livekit/agents/pull/1132) ([@theomonnom](https://github.com/theomonnom))

-   vertex ai support with openai library - [#1084](https://github.com/livekit/agents/pull/1084) ([@jayeshp19](https://github.com/jayeshp19))


[View on GitHub](https://github.com/livekit/agents/releases/tag/livekit-plugins-openai%400.10.8)

---

## livekit-plugins-nltk@0.7.3: livekit-plugins-nltk@0.7.3
**Published:** 2024-12-04

### Patch Changes

-   fix release - [#1176](https://github.com/livekit/agents/pull/1176) ([@theomonnom](https://github.com/theomonnom))


[View on GitHub](https://github.com/livekit/agents/releases/tag/livekit-plugins-nltk%400.7.3)

---

## livekit-plugins-minimal@0.2.1: livekit-plugins-minimal@0.2.1
**Published:** 2024-12-04

### Patch Changes

-   fix release - [#1176](https://github.com/livekit/agents/pull/1176) ([@theomonnom](https://github.com/theomonnom))


[View on GitHub](https://github.com/livekit/agents/releases/tag/livekit-plugins-minimal%400.2.1)

---

## livekit-plugins-llama-index@0.2.2: livekit-plugins-llama-index@0.2.2
**Published:** 2024-12-04

### Patch Changes

-   fix release - [#1176](https://github.com/livekit/agents/pull/1176) ([@theomonnom](https://github.com/theomonnom))


[View on GitHub](https://github.com/livekit/agents/releases/tag/livekit-plugins-llama-index%400.2.2)

---

## livekit-plugins-llama-index@0.2.1: livekit-plugins-llama-index@0.2.1
**Published:** 2024-12-04

### Patch Changes

-   support for custom tool use in LLMs - [#1102](https://github.com/livekit/agents/pull/1102) ([@jayeshp19](https://github.com/jayeshp19))

-   feat: llm retry & llm.FallbackAdapter - [#1132](https://github.com/livekit/agents/pull/1132) ([@theomonnom](https://github.com/theomonnom))


[View on GitHub](https://github.com/livekit/agents/releases/tag/livekit-plugins-llama-index%400.2.1)

---

## livekit-plugins-google@0.8.1: livekit-plugins-google@0.8.1
**Published:** 2024-12-04

### Patch Changes

-   fix release - [#1176](https://github.com/livekit/agents/pull/1176) ([@theomonnom](https://github.com/theomonnom))


[View on GitHub](https://github.com/livekit/agents/releases/tag/livekit-plugins-google%400.8.1)

---

## livekit-plugins-google@0.8.0: livekit-plugins-google@0.8.0
**Published:** 2024-12-04

### Minor Changes

-   Add support for google STT chirp_2 model. - [#1089](https://github.com/livekit/agents/pull/1089) ([@brightsparc](https://github.com/brightsparc))

### Patch Changes

-   feat: stt retry & stt.FallbackAdapter - [#1114](https://github.com/livekit/agents/pull/1114) ([@theomonnom](https://github.com/theomonnom))

-   fix: add retry logic for google stt abort exception - [#1100](https://github.com/livekit/agents/pull/1100) ([@jayeshp19](https://github.com/jayeshp19))

-   feat: tts retry & tts.FallbackAdapter - [#1074](https://github.com/livekit/agents/pull/1074) ([@theomonnom](https://github.com/theomonnom))

-   google STT - use the baseclass resampler - [#1106](https://github.com/livekit/agents/pull/1106) ([@jayeshp19](https://github.com/jayeshp19))


[View on GitHub](https://github.com/livekit/agents/releases/tag/livekit-plugins-google%400.8.0)

---

## livekit-plugins-fal@0.2.2: livekit-plugins-fal@0.2.2
**Published:** 2024-12-04

### Patch Changes

-   fix release - [#1176](https://github.com/livekit/agents/pull/1176) ([@theomonnom](https://github.com/theomonnom))


[View on GitHub](https://github.com/livekit/agents/releases/tag/livekit-plugins-fal%400.2.2)

---

## livekit-plugins-fal@0.2.1: livekit-plugins-fal@0.2.1
**Published:** 2024-12-04

### Patch Changes

-   feat: stt retry & stt.FallbackAdapter - [#1114](https://github.com/livekit/agents/pull/1114) ([@theomonnom](https://github.com/theomonnom))


[View on GitHub](https://github.com/livekit/agents/releases/tag/livekit-plugins-fal%400.2.1)

---

## livekit-plugins-elevenlabs@0.7.9: livekit-plugins-elevenlabs@0.7.9
**Published:** 2024-12-04

### Patch Changes

-   fix release - [#1176](https://github.com/livekit/agents/pull/1176) ([@theomonnom](https://github.com/theomonnom))


[View on GitHub](https://github.com/livekit/agents/releases/tag/livekit-plugins-elevenlabs%400.7.9)

---

## livekit-plugins-elevenlabs@0.7.8: livekit-plugins-elevenlabs@0.7.8
**Published:** 2024-12-04

### Patch Changes

-   feat: tts retry & tts.FallbackAdapter - [#1074](https://github.com/livekit/agents/pull/1074) ([@theomonnom](https://github.com/theomonnom))


[View on GitHub](https://github.com/livekit/agents/releases/tag/livekit-plugins-elevenlabs%400.7.8)

---

## livekit-plugins-deepgram@0.6.13: livekit-plugins-deepgram@0.6.13
**Published:** 2024-12-04

### Patch Changes

-   fix release - [#1176](https://github.com/livekit/agents/pull/1176) ([@theomonnom](https://github.com/theomonnom))


[View on GitHub](https://github.com/livekit/agents/releases/tag/livekit-plugins-deepgram%400.6.13)

---

## livekit-plugins-deepgram@0.6.12: livekit-plugins-deepgram@0.6.12
**Published:** 2024-12-04

### Patch Changes

-   feat: stt retry & stt.FallbackAdapter - [#1114](https://github.com/livekit/agents/pull/1114) ([@theomonnom](https://github.com/theomonnom))

-   Added support for custom deepgram base url - [#1137](https://github.com/livekit/agents/pull/1137) ([@theomonnom](https://github.com/theomonnom))


[View on GitHub](https://github.com/livekit/agents/releases/tag/livekit-plugins-deepgram%400.6.12)

---

## livekit-plugins-cartesia@0.4.5: livekit-plugins-cartesia@0.4.5
**Published:** 2024-12-04

### Patch Changes

-   fix release - [#1176](https://github.com/livekit/agents/pull/1176) ([@theomonnom](https://github.com/theomonnom))


[View on GitHub](https://github.com/livekit/agents/releases/tag/livekit-plugins-cartesia%400.4.5)

---

## livekit-plugins-cartesia@0.4.4: livekit-plugins-cartesia@0.4.4
**Published:** 2024-12-04

### Patch Changes

-   feat: tts retry & tts.FallbackAdapter - [#1074](https://github.com/livekit/agents/pull/1074) ([@theomonnom](https://github.com/theomonnom))


[View on GitHub](https://github.com/livekit/agents/releases/tag/livekit-plugins-cartesia%400.4.4)

---

## livekit-plugins-browser@0.0.4: livekit-plugins-browser@0.0.4
**Published:** 2024-12-04

### Patch Changes

-   fix release - [#1176](https://github.com/livekit/agents/pull/1176) ([@theomonnom](https://github.com/theomonnom))


[View on GitHub](https://github.com/livekit/agents/releases/tag/livekit-plugins-browser%400.0.4)

---

## livekit-plugins-azure@0.4.4: livekit-plugins-azure@0.4.4
**Published:** 2024-12-04

### Patch Changes

-   fix release - [#1176](https://github.com/livekit/agents/pull/1176) ([@theomonnom](https://github.com/theomonnom))


[View on GitHub](https://github.com/livekit/agents/releases/tag/livekit-plugins-azure%400.4.4)

---

## livekit-plugins-azure@0.4.3: livekit-plugins-azure@0.4.3
**Published:** 2024-12-04

### Patch Changes

-   feat: stt retry & stt.FallbackAdapter - [#1114](https://github.com/livekit/agents/pull/1114) ([@theomonnom](https://github.com/theomonnom))

-   azure: support auth entra token for TTS - [#1134](https://github.com/livekit/agents/pull/1134) ([@nfma](https://github.com/nfma))

-   feat: tts retry & tts.FallbackAdapter - [#1074](https://github.com/livekit/agents/pull/1074) ([@theomonnom](https://github.com/theomonnom))


[View on GitHub](https://github.com/livekit/agents/releases/tag/livekit-plugins-azure%400.4.3)

---

## livekit-plugins-assemblyai@0.2.1: livekit-plugins-assemblyai@0.2.1
**Published:** 2024-12-04

### Patch Changes

-   fix release - [#1176](https://github.com/livekit/agents/pull/1176) ([@theomonnom](https://github.com/theomonnom))


[View on GitHub](https://github.com/livekit/agents/releases/tag/livekit-plugins-assemblyai%400.2.1)

---

## livekit-plugins-assemblyai@0.1.1: livekit-plugins-assemblyai@0.1.1
**Published:** 2024-12-04

### Patch Changes

-   feat: stt retry & stt.FallbackAdapter - [#1114](https://github.com/livekit/agents/pull/1114) ([@theomonnom](https://github.com/theomonnom))


[View on GitHub](https://github.com/livekit/agents/releases/tag/livekit-plugins-assemblyai%400.1.1)

---

## livekit-plugins-anthropic@0.2.6: livekit-plugins-anthropic@0.2.6
**Published:** 2024-12-04

### Patch Changes

-   fix release - [#1176](https://github.com/livekit/agents/pull/1176) ([@theomonnom](https://github.com/theomonnom))


[View on GitHub](https://github.com/livekit/agents/releases/tag/livekit-plugins-anthropic%400.2.6)

---

## livekit-plugins-anthropic@0.2.5: livekit-plugins-anthropic@0.2.5
**Published:** 2024-12-04

### Patch Changes

-   support for custom tool use in LLMs - [#1102](https://github.com/livekit/agents/pull/1102) ([@jayeshp19](https://github.com/jayeshp19))

-   feat: llm retry & llm.FallbackAdapter - [#1132](https://github.com/livekit/agents/pull/1132) ([@theomonnom](https://github.com/theomonnom))


[View on GitHub](https://github.com/livekit/agents/releases/tag/livekit-plugins-anthropic%400.2.5)

---

## livekit-agents@0.12.1: livekit-agents@0.12.1
**Published:** 2024-12-04

### Patch Changes

-   fix release - [#1176](https://github.com/livekit/agents/pull/1176) ([@theomonnom](https://github.com/theomonnom))


[View on GitHub](https://github.com/livekit/agents/releases/tag/livekit-agents%400.12.1)

---

## livekit-agents@0.12.0: livekit-agents@0.12.0
**Published:** 2024-12-04

### Minor Changes

-   add nested speech handles, now agent.say works during a function call - [#1130](https://github.com/livekit/agents/pull/1130) ([@longcw](https://github.com/longcw))

### Patch Changes

-   feat: stt retry & stt.FallbackAdapter - [#1114](https://github.com/livekit/agents/pull/1114) ([@theomonnom](https://github.com/theomonnom))

-   expose LiveKitAPI from the a JobContext - [#1159](https://github.com/livekit/agents/pull/1159) ([@theomonnom](https://github.com/theomonnom))

-   add extra chat messages to the end of the function call outputs - [#1165](https://github.com/livekit/agents/pull/1165) ([@longcw](https://github.com/longcw))

-   Add retries to recover from text mode to audio model for realtime API - [#1121](https://github.com/livekit/agents/pull/1121) ([@longcw](https://github.com/longcw))

-   prepare for release - [#1160](https://github.com/livekit/agents/pull/1160) ([@theomonnom](https://github.com/theomonnom))

-   add max_job_memory_usage and will kill the job if it exceeds the limit - [#1136](https://github.com/livekit/agents/pull/1136) ([@longcw](https://github.com/longcw))

-   support for custom tool use in LLMs - [#1102](https://github.com/livekit/agents/pull/1102) ([@jayeshp19](https://github.com/jayeshp19))

-   feat: tts retry & tts.FallbackAdapter - [#1074](https://github.com/livekit/agents/pull/1074) ([@theomonnom](https://github.com/theomonnom))

-   Expose multimodal agent metrics - [#1080](https://github.com/livekit/agents/pull/1080) ([@longcw](https://github.com/longcw))

-   preload mp3 decoder for TTS plugins - [#1129](https://github.com/livekit/agents/pull/1129) ([@jayeshp19](https://github.com/jayeshp19))

-   feat: llm retry & llm.FallbackAdapter - [#1132](https://github.com/livekit/agents/pull/1132) ([@theomonnom](https://github.com/theomonnom))

-   feat: inference process & end of utterance plugin - [#1133](https://github.com/livekit/agents/pull/1133) ([@theomonnom](https://github.com/theomonnom))

-   vertex ai support with openai library - [#1084](https://github.com/livekit/agents/pull/1084) ([@jayeshp19](https://github.com/jayeshp19))


[View on GitHub](https://github.com/livekit/agents/releases/tag/livekit-agents%400.12.0)

---

## livekit-plugins-openai@0.10.7: livekit-plugins-openai@0.10.7
**Published:** 2024-11-16

### Patch Changes

-   fix realtime API audio format values - [#1092](https://github.com/livekit/agents/pull/1092) ([@longcw](https://github.com/longcw))

-   make ConversationItem.create and delete return a Future in Realtime model - [#1085](https://github.com/livekit/agents/pull/1085) ([@longcw](https://github.com/longcw))


[View on GitHub](https://github.com/livekit/agents/releases/tag/livekit-plugins-openai%400.10.7)

---

## livekit-plugins-fal@0.2.0: livekit-plugins-fal@0.2.0
**Published:** 2024-11-16

### Minor Changes

-   initial version - [#991](https://github.com/livekit/agents/pull/991) ([@jayeshp19](https://github.com/jayeshp19))


[View on GitHub](https://github.com/livekit/agents/releases/tag/livekit-plugins-fal%400.2.0)

---

## livekit-plugins-deepgram@0.6.11: livekit-plugins-deepgram@0.6.11
**Published:** 2024-11-16

### Patch Changes

-   add PeriodicCollector utility for metrics - [#1094](https://github.com/livekit/agents/pull/1094) ([@davidzhao](https://github.com/davidzhao))


[View on GitHub](https://github.com/livekit/agents/releases/tag/livekit-plugins-deepgram%400.6.11)

---

## livekit-plugins-deepgram@0.6.10: livekit-plugins-deepgram@0.6.10
**Published:** 2024-11-16

### Patch Changes

-   fix Deepgram missing first word, disabled energy filter by default - [#1090](https://github.com/livekit/agents/pull/1090) ([@davidzhao](https://github.com/davidzhao))


[View on GitHub](https://github.com/livekit/agents/releases/tag/livekit-plugins-deepgram%400.6.10)

---

## livekit-agents@0.11.3: livekit-agents@0.11.3
**Published:** 2024-11-16

### Patch Changes

-   add PeriodicCollector utility for metrics - [#1094](https://github.com/livekit/agents/pull/1094) ([@davidzhao](https://github.com/davidzhao))


[View on GitHub](https://github.com/livekit/agents/releases/tag/livekit-agents%400.11.3)

---

## livekit-plugins-openai@0.10.6: livekit-plugins-openai@0.10.6
**Published:** 2024-11-14

### Patch Changes

-   Expose usage metrics for Realtime model - [#1036](https://github.com/livekit/agents/pull/1036) ([@yuyuma](https://github.com/yuyuma))

-   sync the Realtime API converstation items and add set_chat_ctx - [#1015](https://github.com/livekit/agents/pull/1015) ([@longcw](https://github.com/longcw))


[View on GitHub](https://github.com/livekit/agents/releases/tag/livekit-plugins-openai%400.10.6)

---

## livekit-plugins-google@0.7.3: livekit-plugins-google@0.7.3
**Published:** 2024-11-14

### Patch Changes

-   added catch for aborted speech - [#1055](https://github.com/livekit/agents/pull/1055) ([@jayeshp19](https://github.com/jayeshp19))

-   Make Google STT keywords match Deepgram - [#1067](https://github.com/livekit/agents/pull/1067) ([@martin-purplefish](https://github.com/martin-purplefish))

-   Add support for boosting phrases in Google STT - [#1066](https://github.com/livekit/agents/pull/1066) ([@martin-purplefish](https://github.com/martin-purplefish))


[View on GitHub](https://github.com/livekit/agents/releases/tag/livekit-plugins-google%400.7.3)

---

## livekit-plugins-azure@0.4.2: livekit-plugins-azure@0.4.2
**Published:** 2024-11-14

### Patch Changes

-   add support for azure speech containers - [#1043](https://github.com/livekit/agents/pull/1043) ([@longcw](https://github.com/longcw))

-   fix azure sample_rate parameter - [#1072](https://github.com/livekit/agents/pull/1072) ([@theomonnom](https://github.com/theomonnom))


[View on GitHub](https://github.com/livekit/agents/releases/tag/livekit-plugins-azure%400.4.2)

---

## livekit-plugins-assemblyai@0.1.0: livekit-plugins-assemblyai@0.1.0
**Published:** 2024-11-14

### Minor Changes

-   Introduce assembly.ai plugin - [#1082](https://github.com/livekit/agents/pull/1082) ([@davidzhao](https://github.com/davidzhao))


[View on GitHub](https://github.com/livekit/agents/releases/tag/livekit-plugins-assemblyai%400.1.0)

---

## livekit-plugins-anthropic@0.2.4: livekit-plugins-anthropic@0.2.4
**Published:** 2024-11-14

### Patch Changes

-   anthropic tool fix - [#1051](https://github.com/livekit/agents/pull/1051) ([@jayeshp19](https://github.com/jayeshp19))


[View on GitHub](https://github.com/livekit/agents/releases/tag/livekit-plugins-anthropic%400.2.4)

---

## livekit-agents@0.11.2: livekit-agents@0.11.2
**Published:** 2024-11-14

### Patch Changes

-   Fix interrupt_min_words handling - [#1062](https://github.com/livekit/agents/pull/1062) ([@davidzhao](https://github.com/davidzhao))

-   pipelineagent: fix speech_committed never called - [#1078](https://github.com/livekit/agents/pull/1078) ([@theomonnom](https://github.com/theomonnom))

-   Allow setting agent attributes when accepting job - [#1076](https://github.com/livekit/agents/pull/1076) ([@davidzhao](https://github.com/davidzhao))

-   handles error in function calls - [#1057](https://github.com/livekit/agents/pull/1057) ([@jayeshp19](https://github.com/jayeshp19))

-   Include job count in WorkerStatus and pass in worker for load_fnc - [#1046](https://github.com/livekit/agents/pull/1046) ([@keepingitneil](https://github.com/keepingitneil))

-   Fix delay calculation - [#1081](https://github.com/livekit/agents/pull/1081) ([@martin-purplefish](https://github.com/martin-purplefish))

-   sync the Realtime API converstation items and add set_chat_ctx - [#1015](https://github.com/livekit/agents/pull/1015) ([@longcw](https://github.com/longcw))

-   added metrics for idle time - [#1064](https://github.com/livekit/agents/pull/1064) ([@jayeshp19](https://github.com/jayeshp19))


[View on GitHub](https://github.com/livekit/agents/releases/tag/livekit-agents%400.11.2)

---

## livekit-plugins-elevenlabs@0.7.7: livekit-plugins-elevenlabs@0.7.7
**Published:** 2024-11-02

### Patch Changes

-   support language code in ElevenLabs TTS (#985) - [#1029](https://github.com/livekit/agents/pull/1029) ([@theomonnom](https://github.com/theomonnom))


[View on GitHub](https://github.com/livekit/agents/releases/tag/livekit-plugins-elevenlabs%400.7.7)

---

## livekit-plugins-anthropic@0.2.3: livekit-plugins-anthropic@0.2.3
**Published:** 2024-11-02

### Patch Changes

-   fix: invalid request on anthropic - [#1018](https://github.com/livekit/agents/pull/1018) ([@theomonnom](https://github.com/theomonnom))


[View on GitHub](https://github.com/livekit/agents/releases/tag/livekit-plugins-anthropic%400.2.3)

---

## livekit-agents@0.11.1: livekit-agents@0.11.1
**Published:** 2024-11-02

### Patch Changes

-   Fix stack dump on closed stream - [#1023](https://github.com/livekit/agents/pull/1023) ([@martin-purplefish](https://github.com/martin-purplefish))

-   fix: invalid request on anthropic - [#1018](https://github.com/livekit/agents/pull/1018) ([@theomonnom](https://github.com/theomonnom))

-   fix: IndexError on tts metrics - [#1028](https://github.com/livekit/agents/pull/1028) ([@theomonnom](https://github.com/theomonnom))


[View on GitHub](https://github.com/livekit/agents/releases/tag/livekit-agents%400.11.1)

---

## livekit-plugins-silero@0.7.3: livekit-plugins-silero@0.7.3
**Published:** 2024-10-30

### Patch Changes

-   pipelineagent: expose timing metrics & api errors wip - [#957](https://github.com/livekit/agents/pull/957) ([@theomonnom](https://github.com/theomonnom))


[View on GitHub](https://github.com/livekit/agents/releases/tag/livekit-plugins-silero%400.7.3)

---

## livekit-plugins-playht@1.0.1: livekit-plugins-playht@1.0.1
**Published:** 2024-10-30

### Patch Changes

-   pipelineagent: expose timing metrics & api errors wip - [#957](https://github.com/livekit/agents/pull/957) ([@theomonnom](https://github.com/theomonnom))

-   expose usage metrics - [#984](https://github.com/livekit/agents/pull/984) ([@theomonnom](https://github.com/theomonnom))


[View on GitHub](https://github.com/livekit/agents/releases/tag/livekit-plugins-playht%401.0.1)

---

## livekit-plugins-openai@0.10.5: livekit-plugins-openai@0.10.5
**Published:** 2024-10-30

### Patch Changes

-   fix: Azure realtime model does not accept null for max_response_output_tokens - [#927](https://github.com/livekit/agents/pull/927) ([@davidzhao](https://github.com/davidzhao))

-   add update_options to TTS - [#922](https://github.com/livekit/agents/pull/922) ([@theomonnom](https://github.com/theomonnom))

-   Groq integration with Whisper-compatible STT endpoints - [#986](https://github.com/livekit/agents/pull/986) ([@jayeshp19](https://github.com/jayeshp19))

-   pipelineagent: expose timing metrics & api errors wip - [#957](https://github.com/livekit/agents/pull/957) ([@theomonnom](https://github.com/theomonnom))

-   openai: fix low timeouts - [#926](https://github.com/livekit/agents/pull/926) ([@theomonnom](https://github.com/theomonnom))

-   expose usage metrics - [#984](https://github.com/livekit/agents/pull/984) ([@theomonnom](https://github.com/theomonnom))


[View on GitHub](https://github.com/livekit/agents/releases/tag/livekit-plugins-openai%400.10.5)

---

## livekit-plugins-llama-index@0.2.0: livekit-plugins-llama-index@0.2.0
**Published:** 2024-10-30

### Minor Changes

-   prepare for release - [#1007](https://github.com/livekit/agents/pull/1007) ([@theomonnom](https://github.com/theomonnom))

### Patch Changes

-   Publish llama-index plugin - [#924](https://github.com/livekit/agents/pull/924) ([@davidzhao](https://github.com/davidzhao))


[View on GitHub](https://github.com/livekit/agents/releases/tag/livekit-plugins-llama-index%400.2.0)

---

## livekit-plugins-google@0.7.2: livekit-plugins-google@0.7.2
**Published:** 2024-10-30

### Patch Changes

-   add update_options to TTS - [#922](https://github.com/livekit/agents/pull/922) ([@theomonnom](https://github.com/theomonnom))

-   Additional options enabled on Google TTS - [#945](https://github.com/livekit/agents/pull/945) ([@hari-truviz](https://github.com/hari-truviz))

-   pipelineagent: expose timing metrics & api errors wip - [#957](https://github.com/livekit/agents/pull/957) ([@theomonnom](https://github.com/theomonnom))

-   expose usage metrics - [#984](https://github.com/livekit/agents/pull/984) ([@theomonnom](https://github.com/theomonnom))


[View on GitHub](https://github.com/livekit/agents/releases/tag/livekit-plugins-google%400.7.2)

---

## livekit-plugins-elevenlabs@0.7.6: livekit-plugins-elevenlabs@0.7.6
**Published:** 2024-10-30

### Patch Changes

-   add update_options to TTS - [#922](https://github.com/livekit/agents/pull/922) ([@theomonnom](https://github.com/theomonnom))

-   pipelineagent: expose timing metrics & api errors wip - [#957](https://github.com/livekit/agents/pull/957) ([@theomonnom](https://github.com/theomonnom))

-   expose usage metrics - [#984](https://github.com/livekit/agents/pull/984) ([@theomonnom](https://github.com/theomonnom))


[View on GitHub](https://github.com/livekit/agents/releases/tag/livekit-plugins-elevenlabs%400.7.6)

---

## livekit-plugins-deepgram@0.6.9: livekit-plugins-deepgram@0.6.9
**Published:** 2024-10-30

### Patch Changes

-   stt: reduce bandwidth usage by reducing sample_rate to 16khz - [#920](https://github.com/livekit/agents/pull/920) ([@theomonnom](https://github.com/theomonnom))

-   deepgram: send finalize each time we stop sending audio - [#1004](https://github.com/livekit/agents/pull/1004) ([@theomonnom](https://github.com/theomonnom))

-   pipelineagent: expose timing metrics & api errors wip - [#957](https://github.com/livekit/agents/pull/957) ([@theomonnom](https://github.com/theomonnom))

-   expose usage metrics - [#984](https://github.com/livekit/agents/pull/984) ([@theomonnom](https://github.com/theomonnom))


[View on GitHub](https://github.com/livekit/agents/releases/tag/livekit-plugins-deepgram%400.6.9)

---

## livekit-plugins-cartesia@0.4.3: livekit-plugins-cartesia@0.4.3
**Published:** 2024-10-30

### Patch Changes

-   add update_options to TTS - [#922](https://github.com/livekit/agents/pull/922) ([@theomonnom](https://github.com/theomonnom))

-   pipelineagent: expose timing metrics & api errors wip - [#957](https://github.com/livekit/agents/pull/957) ([@theomonnom](https://github.com/theomonnom))

-   expose usage metrics - [#984](https://github.com/livekit/agents/pull/984) ([@theomonnom](https://github.com/theomonnom))


[View on GitHub](https://github.com/livekit/agents/releases/tag/livekit-plugins-cartesia%400.4.3)

---

## livekit-plugins-browser@0.0.3: livekit-plugins-browser@0.0.3
**Published:** 2024-10-30

### Patch Changes

-   pipelineagent: expose timing metrics & api errors wip - [#957](https://github.com/livekit/agents/pull/957) ([@theomonnom](https://github.com/theomonnom))


[View on GitHub](https://github.com/livekit/agents/releases/tag/livekit-plugins-browser%400.0.3)

---

## livekit-plugins-azure@0.4.1: livekit-plugins-azure@0.4.1
**Published:** 2024-10-30

### Patch Changes

-   add update_options to TTS - [#922](https://github.com/livekit/agents/pull/922) ([@theomonnom](https://github.com/theomonnom))

-   pipelineagent: expose timing metrics & api errors wip - [#957](https://github.com/livekit/agents/pull/957) ([@theomonnom](https://github.com/theomonnom))

-   azure tts: fix SSML Implementation by Adding <voice> Tag - [#929](https://github.com/livekit/agents/pull/929) ([@samirsalman](https://github.com/samirsalman))

-   azure tts: fix Prosody Config Validation - [#918](https://github.com/livekit/agents/pull/918) ([@samirsalman](https://github.com/samirsalman))

-   expose usage metrics - [#984](https://github.com/livekit/agents/pull/984) ([@theomonnom](https://github.com/theomonnom))


[View on GitHub](https://github.com/livekit/agents/releases/tag/livekit-plugins-azure%400.4.1)

---

## livekit-plugins-anthropic@0.2.2: livekit-plugins-anthropic@0.2.2
**Published:** 2024-10-30

### Patch Changes

-   pipelineagent: expose timing metrics & api errors wip - [#957](https://github.com/livekit/agents/pull/957) ([@theomonnom](https://github.com/theomonnom))


[View on GitHub](https://github.com/livekit/agents/releases/tag/livekit-plugins-anthropic%400.2.2)

---

## livekit-agents@0.11.0: livekit-agents@0.11.0
**Published:** 2024-10-30

### Minor Changes

-   prepare for release - [#1007](https://github.com/livekit/agents/pull/1007) ([@theomonnom](https://github.com/theomonnom))

### Patch Changes

-   Fix race in load calc initialization - [#969](https://github.com/livekit/agents/pull/969) ([@martin-purplefish](https://github.com/martin-purplefish))

-   Fix incorrect load computation on docker instances - [#972](https://github.com/livekit/agents/pull/972) ([@martin-purplefish](https://github.com/martin-purplefish))

-   stt: reduce bandwidth usage by reducing sample_rate to 16khz - [#920](https://github.com/livekit/agents/pull/920) ([@theomonnom](https://github.com/theomonnom))

-   Reorganized metrics, added create_metrics_logger - [#1009](https://github.com/livekit/agents/pull/1009) ([@davidzhao](https://github.com/davidzhao))

-   pipelineagent: expose timing metrics & api errors wip - [#957](https://github.com/livekit/agents/pull/957) ([@theomonnom](https://github.com/theomonnom))

-   Allow kind to be list or single value - [#1006](https://github.com/livekit/agents/pull/1006) ([@keepingitneil](https://github.com/keepingitneil))

-   fix before_llm_cb not handling coroutines returning False - [#961](https://github.com/livekit/agents/pull/961) ([@Tanesan](https://github.com/Tanesan))

-   expose transcriptions for multimodal agents - [#1001](https://github.com/livekit/agents/pull/1001) ([@longcw](https://github.com/longcw))

-   Fix stack dump on room shutdown - [#989](https://github.com/livekit/agents/pull/989) ([@martin-purplefish](https://github.com/martin-purplefish))

-   Add exception logging for tool calls - [#923](https://github.com/livekit/agents/pull/923) ([@martin-purplefish](https://github.com/martin-purplefish))

-   Skip egress by default in participant-related utilities on JobContext - [#1005](https://github.com/livekit/agents/pull/1005) ([@keepingitneil](https://github.com/keepingitneil))

-   pipeline-agent: avoid nested function calls - [#935](https://github.com/livekit/agents/pull/935) ([@theomonnom](https://github.com/theomonnom))

-   expose usage metrics - [#984](https://github.com/livekit/agents/pull/984) ([@theomonnom](https://github.com/theomonnom))

-   fix jobs never reloading - [#934](https://github.com/livekit/agents/pull/934) ([@theomonnom](https://github.com/theomonnom))

-   voicepipeline: support recursive/chained function calls - [#970](https://github.com/livekit/agents/pull/970) ([@theomonnom](https://github.com/theomonnom))


[View on GitHub](https://github.com/livekit/agents/releases/tag/livekit-agents%400.11.0)

---

## livekit-plugins-silero@0.7.2: livekit-plugins-silero@0.7.2
**Published:** 2024-10-15

### Patch Changes

-   silero: add update_options - [#899](https://github.com/livekit/agents/pull/899) ([@theomonnom](https://github.com/theomonnom))

-   silero: fix speech_buffer for END_OF_SPEECH - [#898](https://github.com/livekit/agents/pull/898) ([@theomonnom](https://github.com/theomonnom))


[View on GitHub](https://github.com/livekit/agents/releases/tag/livekit-plugins-silero%400.7.2)

---

## livekit-plugins-openai@0.10.4: livekit-plugins-openai@0.10.4
**Published:** 2024-10-15

### Patch Changes

-   add x.ai support - [#907](https://github.com/livekit/agents/pull/907) ([@theomonnom](https://github.com/theomonnom))

-   Fix functions to include content - [#897](https://github.com/livekit/agents/pull/897) ([@martin-purplefish](https://github.com/martin-purplefish))


[View on GitHub](https://github.com/livekit/agents/releases/tag/livekit-plugins-openai%400.10.4)

---

## livekit-plugins-azure@0.4.0: livekit-plugins-azure@0.4.0
**Published:** 2024-10-15

### Minor Changes

-   Azure TTS Prosody SSML support #912 - [#914](https://github.com/livekit/agents/pull/914) ([@theomonnom](https://github.com/theomonnom))


[View on GitHub](https://github.com/livekit/agents/releases/tag/livekit-plugins-azure%400.4.0)

---

## livekit-agents@0.10.2: livekit-agents@0.10.2
**Published:** 2024-10-15

### Patch Changes

-   Fix split_paragraphs and simple-rag example - [#896](https://github.com/livekit/agents/pull/896) ([@davidzhao](https://github.com/davidzhao))

-   Fix bug where if the tts_source was a string but before_tts_cb returned AsyncIterable[str], the transcript would not be synthesized. - [#906](https://github.com/livekit/agents/pull/906) ([@martin-purplefish](https://github.com/martin-purplefish))

-   Allow forcing interruptions of incomplete audio - [#891](https://github.com/livekit/agents/pull/891) ([@martin-purplefish](https://github.com/martin-purplefish))

-   Include chat context on collected tool calls - [#897](https://github.com/livekit/agents/pull/897) ([@martin-purplefish](https://github.com/martin-purplefish))


[View on GitHub](https://github.com/livekit/agents/releases/tag/livekit-agents%400.10.2)

---

## livekit-plugins-openai@0.10.3: livekit-plugins-openai@0.10.3
**Published:** 2024-10-10

### Patch Changes

-   fix: handle when STT does not return any speech - [#854](https://github.com/livekit/agents/pull/854) ([@davidzhao](https://github.com/davidzhao))

-   Support for Realtime API with Azure OpenAI - [#848](https://github.com/livekit/agents/pull/848) ([@davidzhao](https://github.com/davidzhao))


[View on GitHub](https://github.com/livekit/agents/releases/tag/livekit-plugins-openai%400.10.3)

---

## livekit-plugins-llama-index@0.1.1: livekit-plugins-llama-index@0.1.1
**Published:** 2024-10-10

### Patch Changes

-   livekit-plugins-llama-index - [#696](https://github.com/livekit/agents/pull/696) ([@theomonnom](https://github.com/theomonnom))


[View on GitHub](https://github.com/livekit/agents/releases/tag/livekit-plugins-llama-index%400.1.1)

---

## livekit-plugins-deepgram@0.6.8: livekit-plugins-deepgram@0.6.8
**Published:** 2024-10-10

### Patch Changes

-   accepts parameter profanity_filter - [#811](https://github.com/livekit/agents/pull/811) ([@jebjebs](https://github.com/jebjebs))


[View on GitHub](https://github.com/livekit/agents/releases/tag/livekit-plugins-deepgram%400.6.8)

---

## livekit-agents@0.10.1: livekit-agents@0.10.1
**Published:** 2024-10-10

### Patch Changes

-   use rtc.combine_audio_frames - [#841](https://github.com/livekit/agents/pull/841) ([@theomonnom](https://github.com/theomonnom))

-   Fix agent state to not change to listening when user speaks - [#857](https://github.com/livekit/agents/pull/857) ([@martin-purplefish](https://github.com/martin-purplefish))
    Fixed canceling uncancelable speech
    Fixed bug where agent would get stuck with uninterruptable speech.

-   Fix bug where empty audio would cause agent to get stuck. - [#836](https://github.com/livekit/agents/pull/836) ([@martin-purplefish](https://github.com/martin-purplefish))

-   fix: handle when STT does not return any speech - [#854](https://github.com/livekit/agents/pull/854) ([@davidzhao](https://github.com/davidzhao))

-   Fix watcher reloaded processes double connecting to rooms - [#822](https://github.com/livekit/agents/pull/822) ([@keepingitneil](https://github.com/keepingitneil))

-   voice-pipeline: avoid stacked replies when interruptions is disallowed - [#869](https://github.com/livekit/agents/pull/869) ([@theomonnom](https://github.com/theomonnom))

-   disable preemptive_synthesis by default - [#867](https://github.com/livekit/agents/pull/867) ([@theomonnom](https://github.com/theomonnom))

-   Fixed bug where agent would get stuck on non-interruptable speech - [#850](https://github.com/livekit/agents/pull/850) ([@martin-purplefish](https://github.com/martin-purplefish))

-   use EventEmitter from rtc - [#879](https://github.com/livekit/agents/pull/879) ([@theomonnom](https://github.com/theomonnom))

-   AudioByteStream: avoid empty frames on flush - [#840](https://github.com/livekit/agents/pull/840) ([@theomonnom](https://github.com/theomonnom))

-   improve worker logs - [#878](https://github.com/livekit/agents/pull/878) ([@theomonnom](https://github.com/theomonnom))

-   voice-pipeline: fix tts_forwarder not always being closed - [#871](https://github.com/livekit/agents/pull/871) ([@theomonnom](https://github.com/theomonnom))

-   bump livekit-rtc to v0.17.5 - [#880](https://github.com/livekit/agents/pull/880) ([@theomonnom](https://github.com/theomonnom))

-   Fixed bug where agent would freeze if before_llm_cb returned false - [#865](https://github.com/livekit/agents/pull/865) ([@martin-purplefish](https://github.com/martin-purplefish))


[View on GitHub](https://github.com/livekit/agents/releases/tag/livekit-agents%400.10.1)

---

## livekit-plugins-openai@0.10.2: livekit-plugins-openai@0.10.2
**Published:** 2024-10-03

### Patch Changes

-   oai-realtime: fix function calls - [#826](https://github.com/livekit/agents/pull/826) ([@KillianLucas](https://github.com/KillianLucas))


[View on GitHub](https://github.com/livekit/agents/releases/tag/livekit-plugins-openai%400.10.2)

---

## livekit-plugins-silero@0.7.1: livekit-plugins-silero@0.7.1
**Published:** 2024-10-01

### Patch Changes

-   Fix CI x LFS issue for silero plugin - [#818](https://github.com/livekit/agents/pull/818) ([@keepingitneil](https://github.com/keepingitneil))


[View on GitHub](https://github.com/livekit/agents/releases/tag/livekit-plugins-silero%400.7.1)

---

## livekit-plugins-silero@0.7.0: livekit-plugins-silero@0.7.0
**Published:** 2024-10-01

### Minor Changes

-   silero: support any sample rate - [#805](https://github.com/livekit/agents/pull/805) ([@theomonnom](https://github.com/theomonnom))

### Patch Changes

-   silero: add prefix_padding_duration #801 - [#805](https://github.com/livekit/agents/pull/805) ([@theomonnom](https://github.com/theomonnom))


[View on GitHub](https://github.com/livekit/agents/releases/tag/livekit-plugins-silero%400.7.0)

---

## livekit-plugins-openai@0.10.1: livekit-plugins-openai@0.10.1
**Published:** 2024-10-01

### Patch Changes

-   oai-realtime: log response errors - [#819](https://github.com/livekit/agents/pull/819) ([@theomonnom](https://github.com/theomonnom))


[View on GitHub](https://github.com/livekit/agents/releases/tag/livekit-plugins-openai%400.10.1)

---

## livekit-plugins-openai@0.10.0: livekit-plugins-openai@0.10.0
**Published:** 2024-10-01

### Minor Changes

-   OpenAI Realtime API support - [#814](https://github.com/livekit/agents/pull/814) ([@theomonnom](https://github.com/theomonnom))

### Patch Changes

-   Add Telnyx integration for LLM - [#803](https://github.com/livekit/agents/pull/803) ([@jamestwhedbee](https://github.com/jamestwhedbee))


[View on GitHub](https://github.com/livekit/agents/releases/tag/livekit-plugins-openai%400.10.0)

---

## livekit-agents@0.10.0: livekit-agents@0.10.0
**Published:** 2024-10-01

## ✨ [NEW] OpenAI Realtime API support

We're partnering with OpenAI on a new `MultimodalAgent` API in the Agents framework. This class completely wraps OpenAI’s Realtime API, abstract away the raw wire protocol, and provide an ultra-low latency WebRTC transport between GPT-4o and your users’ devices. This same stack powers Advanced Voice in the ChatGPT app.

- Try the Realtime API in our [playground](https://playground.livekit.io/) [[code](https://github.com/livekit-examples/realtime-playground)]
- Check out our [guide](https://docs.livekit.io/agents/openai) to building your first app with this new API

### Patch Changes

-   bump livekit to v0.17.2 - [#815](https://github.com/livekit/agents/pull/815) ([@theomonnom](https://github.com/theomonnom))

-   silero: support any sample rate - [#805](https://github.com/livekit/agents/pull/805) ([@theomonnom](https://github.com/theomonnom))


[View on GitHub](https://github.com/livekit/agents/releases/tag/livekit-agents%400.10.0)

---

## livekit-plugins-openai@0.8.5: livekit-plugins-openai@0.8.5
**Published:** 2024-09-26

### Patch Changes

-   Fix function for OpenAI Assistants - [#784](https://github.com/livekit/agents/pull/784) ([@keepingitneil](https://github.com/keepingitneil))


[View on GitHub](https://github.com/livekit/agents/releases/tag/livekit-plugins-openai%400.8.5)

---

## livekit-agents@0.9.1: livekit-agents@0.9.1
**Published:** 2024-09-26

0.9.0 and 0.9.1 packs significant improvements to the reliability and performance of VoiceAssistant. 

The main changes are:
- Rework of audio publishing/buffering to reduce glitches caused by Python's asyncio scheduler
- Limiting number of prewarm workers that are spawned
- Introducing `lk.agent.state` attribute to allow client to detect state of VoiceAssistant: `speaking`, `listening`, etc
  - Works out of the box with [JS Components 2.6.0](https://github.com/livekit/components-js/releases/tag/%40livekit%2Fcomponents-react%402.6.0). See [example frontend](https://github.com/livekit-examples/voice-assistant)
- Fixed a rare case where Agent wouldn't reconnect to room after being disconnected
- Additional control for VoiceAssistant
  - `min_endpointing_delay`: control over how quickly the agent should respond when the user pauses (longer delay reduces agent interruptions)
  - `before_llm_cb`: ability to control what is being sent to the LLM
  - `before_tts_cb`: ability to modify text before it's sent to TTS

## Detailed Changelog

### Patch Changes

-   fix VoiceAssisstant being stuck when interrupting before user speech is committed - [#790](https://github.com/livekit/agents/pull/790) ([@coderlxn](https://github.com/coderlxn))

-   Fix function for OpenAI Assistants - [#784](https://github.com/livekit/agents/pull/784) ([@keepingitneil](https://github.com/keepingitneil))


[View on GitHub](https://github.com/livekit/agents/releases/tag/livekit-agents%400.9.1)

---

## livekit-plugins-openai@0.8.4: livekit-plugins-openai@0.8.4
**Published:** 2024-09-22

### Patch Changes

-   avoid returning tiny frames from TTS - [#747](https://github.com/livekit/agents/pull/747) ([@theomonnom](https://github.com/theomonnom))

-   Fixing Assistant API Vision Capabilities - [#771](https://github.com/livekit/agents/pull/771) ([@keepingitneil](https://github.com/keepingitneil))


[View on GitHub](https://github.com/livekit/agents/releases/tag/livekit-plugins-openai%400.8.4)

---

## livekit-plugins-google@0.7.1: livekit-plugins-google@0.7.1
**Published:** 2024-09-22

### Patch Changes

-   avoid returning tiny frames from TTS - [#747](https://github.com/livekit/agents/pull/747) ([@theomonnom](https://github.com/theomonnom))


[View on GitHub](https://github.com/livekit/agents/releases/tag/livekit-plugins-google%400.7.1)

---

## livekit-plugins-elevenlabs@0.7.5: livekit-plugins-elevenlabs@0.7.5
**Published:** 2024-09-22

### Patch Changes

-   avoid returning tiny frames from TTS - [#747](https://github.com/livekit/agents/pull/747) ([@theomonnom](https://github.com/theomonnom))

-   11labs: send phoneme in one entire xml chunk - [#766](https://github.com/livekit/agents/pull/766) ([@theomonnom](https://github.com/theomonnom))


[View on GitHub](https://github.com/livekit/agents/releases/tag/livekit-plugins-elevenlabs%400.7.5)

---

## livekit-plugins-azure@0.3.2: livekit-plugins-azure@0.3.2
**Published:** 2024-09-22

### Patch Changes

-   avoid returning tiny frames from TTS - [#747](https://github.com/livekit/agents/pull/747) ([@theomonnom](https://github.com/theomonnom))


[View on GitHub](https://github.com/livekit/agents/releases/tag/livekit-plugins-azure%400.3.2)

---

## livekit-agents@0.9.0: livekit-agents@0.9.0
**Published:** 2024-09-22

### Minor Changes

-   rename voice_assistant.state to lk.agent.state - [#772](https://github.com/livekit/agents/pull/772) ([@bcherry](https://github.com/bcherry))

### Patch Changes

-   bump rtc - [#782](https://github.com/livekit/agents/pull/782) ([@nbsp](https://github.com/nbsp))

-   improve graceful shutdown - [#756](https://github.com/livekit/agents/pull/756) ([@theomonnom](https://github.com/theomonnom))

-   avoid returning tiny frames from TTS - [#747](https://github.com/livekit/agents/pull/747) ([@theomonnom](https://github.com/theomonnom))

-   windows: default to threaded executor & fix dev mode - [#755](https://github.com/livekit/agents/pull/755) ([@theomonnom](https://github.com/theomonnom))

-   11labs: send phoneme in one entire xml chunk - [#766](https://github.com/livekit/agents/pull/766) ([@theomonnom](https://github.com/theomonnom))

-   fix: process not starting if num_idle_processes is zero - [#763](https://github.com/livekit/agents/pull/763) ([@theomonnom](https://github.com/theomonnom))

-   voiceassistant: avoid tiny frames on playout - [#750](https://github.com/livekit/agents/pull/750) ([@theomonnom](https://github.com/theomonnom))

-   voiceassistant: expose turn_completion_delay - [#752](https://github.com/livekit/agents/pull/752) ([@theomonnom](https://github.com/theomonnom))

-   limit concurrent process init to 1 - [#751](https://github.com/livekit/agents/pull/751) ([@theomonnom](https://github.com/theomonnom))

-   Add typing-extensions as a dependency - [#778](https://github.com/livekit/agents/pull/778) ([@keepingitneil](https://github.com/keepingitneil))

-   Allow setting LLM temperature with VoiceAssistant - [#741](https://github.com/livekit/agents/pull/741) ([@davidzhao](https://github.com/davidzhao))

-   better dev defaults - [#762](https://github.com/livekit/agents/pull/762) ([@theomonnom](https://github.com/theomonnom))

-   voiceassistant: allow to cancel llm generation inside before_llm_cb - [#753](https://github.com/livekit/agents/pull/753) ([@theomonnom](https://github.com/theomonnom))

-   use os.exit to exit forcefully - [#770](https://github.com/livekit/agents/pull/770) ([@theomonnom](https://github.com/theomonnom))


[View on GitHub](https://github.com/livekit/agents/releases/tag/livekit-agents%400.9.0)

---

## livekit-plugins-openai@0.8.3: livekit-plugins-openai@0.8.3
**Published:** 2024-09-11

### Patch Changes

-   Introduce function calling to OpenAI Assistants - [#710](https://github.com/livekit/agents/pull/710) ([@keepingitneil](https://github.com/keepingitneil))

-   Add Cerebras to OpenAI Plugin - [#731](https://github.com/livekit/agents/pull/731) ([@henrytwo](https://github.com/henrytwo))


[View on GitHub](https://github.com/livekit/agents/releases/tag/livekit-plugins-openai%400.8.3)

---

## livekit-plugins-deepgram@0.6.7: livekit-plugins-deepgram@0.6.7
**Published:** 2024-09-11

### Patch Changes

-   Only send actual audio to Deepgram using a basic audio RMS filter - [#738](https://github.com/livekit/agents/pull/738) ([@keepingitneil](https://github.com/keepingitneil))

-   defaults to nova-2-general model - [#726](https://github.com/livekit/agents/pull/726) ([@davidzhao](https://github.com/davidzhao))


[View on GitHub](https://github.com/livekit/agents/releases/tag/livekit-plugins-deepgram%400.6.7)

---

## livekit-plugins-cartesia@0.4.2: livekit-plugins-cartesia@0.4.2
**Published:** 2024-09-11

### Patch Changes

-   Add support for cartesia voice control - [#740](https://github.com/livekit/agents/pull/740) ([@bcherry](https://github.com/bcherry))


[View on GitHub](https://github.com/livekit/agents/releases/tag/livekit-plugins-cartesia%400.4.2)

---

## livekit-plugins-anthropic@0.2.1: livekit-plugins-anthropic@0.2.1
**Published:** 2024-09-11

### Patch Changes

-   Fixes to Anthropic Function Calling - [#708](https://github.com/livekit/agents/pull/708) ([@keepingitneil](https://github.com/keepingitneil))


[View on GitHub](https://github.com/livekit/agents/releases/tag/livekit-plugins-anthropic%400.2.1)

---

## livekit-agents@0.8.12: livekit-agents@0.8.12
**Published:** 2024-09-11

### Patch Changes

-   tts_forwarder: don't raise inside mark_{audio,text}\_segment_end when nothing was pushed - [#730](https://github.com/livekit/agents/pull/730) ([@theomonnom](https://github.com/theomonnom))


[View on GitHub](https://github.com/livekit/agents/releases/tag/livekit-agents%400.8.12)

---

## livekit-plugins-openai@0.8.2: livekit-plugins-openai@0.8.2
**Published:** 2024-09-09

### Patch Changes

-   Add deepseek LLMs at OpenAI plugin - [#714](https://github.com/livekit/agents/pull/714) ([@lenage](https://github.com/lenage))

-   skip processing of choice.delta when it is None - [#705](https://github.com/livekit/agents/pull/705) ([@theomonnom](https://github.com/theomonnom))


[View on GitHub](https://github.com/livekit/agents/releases/tag/livekit-plugins-openai%400.8.2)

---

## livekit-plugins-google@0.7.0: livekit-plugins-google@0.7.0
**Published:** 2024-09-09

### Minor Changes

-   Enable use of Google STT with Application Default Credentials. - [#721](https://github.com/livekit/agents/pull/721) ([@rsinnet](https://github.com/rsinnet))

### Patch Changes

-   google-tts: ignore wav header - [#703](https://github.com/livekit/agents/pull/703) ([@theomonnom](https://github.com/theomonnom))


[View on GitHub](https://github.com/livekit/agents/releases/tag/livekit-plugins-google%400.7.0)

---

## livekit-plugins-elevenlabs@0.7.4: livekit-plugins-elevenlabs@0.7.4
**Published:** 2024-09-09

### Patch Changes

-   elevenlabs: expose enable_ssml_parsing - [#723](https://github.com/livekit/agents/pull/723) ([@theomonnom](https://github.com/theomonnom))


[View on GitHub](https://github.com/livekit/agents/releases/tag/livekit-plugins-elevenlabs%400.7.4)

---

## livekit-plugins-anthropic@0.2.0: livekit-plugins-anthropic@0.2.0
**Published:** 2024-09-09

### Minor Changes

-   bump anthropic for release - [#724](https://github.com/livekit/agents/pull/724) ([@theomonnom](https://github.com/theomonnom))


[View on GitHub](https://github.com/livekit/agents/releases/tag/livekit-plugins-anthropic%400.2.0)

---

## livekit-agents@0.8.11: livekit-agents@0.8.11
**Published:** 2024-09-09

### Patch Changes

-   improve gracefully_cancel logic - [#720](https://github.com/livekit/agents/pull/720) ([@theomonnom](https://github.com/theomonnom))

-   Make ctx.room.name available prior to connection - [#716](https://github.com/livekit/agents/pull/716) ([@davidzhao](https://github.com/davidzhao))

-   ipc: add threaded job runner - [#684](https://github.com/livekit/agents/pull/684) ([@theomonnom](https://github.com/theomonnom))

-   voiceassistant: add VoiceAssistantState - [#654](https://github.com/livekit/agents/pull/654) ([@lukasIO](https://github.com/lukasIO))

-   add JobContext.wait_for_participant - [#712](https://github.com/livekit/agents/pull/712) ([@theomonnom](https://github.com/theomonnom))

-   fix non pickleable log - [#691](https://github.com/livekit/agents/pull/691) ([@theomonnom](https://github.com/theomonnom))

-   voiceassistant: skip speech initialization if interrupted - [#715](https://github.com/livekit/agents/pull/715) ([@theomonnom](https://github.com/theomonnom))

-   bump required livekit version to 0.15.2 - [#722](https://github.com/livekit/agents/pull/722) ([@theomonnom](https://github.com/theomonnom))

-   voiceassistant: add will_synthesize_assistant_speech - [#706](https://github.com/livekit/agents/pull/706) ([@theomonnom](https://github.com/theomonnom))

-   voiceassistant: fix mark_audio_segment_end with no audio data - [#719](https://github.com/livekit/agents/pull/719) ([@theomonnom](https://github.com/theomonnom))


[View on GitHub](https://github.com/livekit/agents/releases/tag/livekit-agents%400.8.11)

---

## livekit-plugins-google@0.6.3: livekit-plugins-google@0.6.3
**Published:** 2024-09-02

### Patch Changes

-   Fix Google STT exception when no valid speech is recognized - [#680](https://github.com/livekit/agents/pull/680) ([@davidzhao](https://github.com/davidzhao))


[View on GitHub](https://github.com/livekit/agents/releases/tag/livekit-plugins-google%400.6.3)

---

## livekit-plugins-deepgram@0.6.6: livekit-plugins-deepgram@0.6.6
**Published:** 2024-09-02

### Patch Changes

-   deepgram: switch the default model to phonecall - [#676](https://github.com/livekit/agents/pull/676) ([@theomonnom](https://github.com/theomonnom))


[View on GitHub](https://github.com/livekit/agents/releases/tag/livekit-plugins-deepgram%400.6.6)

---

## livekit-agents@0.8.9: livekit-agents@0.8.9
**Published:** 2024-09-02

### Patch Changes

-   Introduce easy api for starting tasks for remote participants - [#679](https://github.com/livekit/agents/pull/679) ([@keepingitneil](https://github.com/keepingitneil))

-   update livekit to 0.14.0 and await tracksubscribed - [#678](https://github.com/livekit/agents/pull/678) ([@nbsp](https://github.com/nbsp))


[View on GitHub](https://github.com/livekit/agents/releases/tag/livekit-agents%400.8.9)

---

## livekit-agents@0.8.10: livekit-agents@0.8.10
**Published:** 2024-09-02

### Patch Changes

-   Pass JobContext to participant entrypoint function - [#694](https://github.com/livekit/agents/pull/694) ([@davidzhao](https://github.com/davidzhao))

-   voiceassistant: keep punctuations when sending agent transcription - [#648](https://github.com/livekit/agents/pull/648) ([@theomonnom](https://github.com/theomonnom))


[View on GitHub](https://github.com/livekit/agents/releases/tag/livekit-agents%400.8.10)

---

## livekit-plugins-anthropic@0.1.1: livekit-plugins-anthropic@0.1.1
**Published:** 2024-08-27

# livekit-plugins-anthropic


[View on GitHub](https://github.com/livekit/agents/releases/tag/livekit-plugins-anthropic%400.1.1)

---

## livekit-agents@0.8.8: livekit-agents@0.8.8
**Published:** 2024-08-27

[v0.7.x to v0.8.x migration guide](https://github.com/livekit/agents/blob/main/0.8-migration-guide.md)

### Patch Changes

-   fix uninitialized SpeechHandle error on interruption - [#665](https://github.com/livekit/agents/pull/665) ([@theomonnom](https://github.com/theomonnom))

-   voiceassistant: avoid stacking assistant replies when allow_interruptions=False - [#667](https://github.com/livekit/agents/pull/667) ([@theomonnom](https://github.com/theomonnom))

-   fix: disconnect event may now have a arguments - [#668](https://github.com/livekit/agents/pull/668) ([@theomonnom](https://github.com/theomonnom))

-   Add ServerMessage.termination handler - [#635](https://github.com/livekit/agents/pull/635) ([@nbsp](https://github.com/nbsp))


[View on GitHub](https://github.com/livekit/agents/releases/tag/livekit-agents%400.8.8)

---

## livekit-plugins-nltk@0.7.2: livekit-plugins-nltk@0.7.2
**Published:** 2024-08-22

### Patch Changes

-   fix another semver break - [#659](https://github.com/livekit/agents/pull/659) ([@theomonnom](https://github.com/theomonnom))


[View on GitHub](https://github.com/livekit/agents/releases/tag/livekit-plugins-nltk%400.7.2)

---

## livekit-plugins-browser@0.0.2: livekit-plugins-browser@0.0.2
**Published:** 2024-08-22

### Patch Changes

-   livekit-plugins-browser: prepare for release - [#659](https://github.com/livekit/agents/pull/659) ([@theomonnom](https://github.com/theomonnom))


[View on GitHub](https://github.com/livekit/agents/releases/tag/livekit-plugins-browser%400.0.2)

---

## livekit-agents@0.8.7: livekit-agents@0.8.7
**Published:** 2024-08-22

### Patch Changes

-   voiceassistant: fix llm not having the full chat context on bad interruption timing - [#659](https://github.com/livekit/agents/pull/659) ([@theomonnom](https://github.com/theomonnom))


[View on GitHub](https://github.com/livekit/agents/releases/tag/livekit-agents%400.8.7)

---

## livekit-plugins-silero@0.6.4: livekit-plugins-silero@0.6.4
**Published:** 2024-08-17

### Patch Changes

-   silero: adjust vad activation threshold - [#639](https://github.com/livekit/agents/pull/639) ([@theomonnom](https://github.com/theomonnom))

-   silero: fix vad padding & static audio - [#631](https://github.com/livekit/agents/pull/631) ([@theomonnom](https://github.com/theomonnom))


[View on GitHub](https://github.com/livekit/agents/releases/tag/livekit-plugins-silero%400.6.4)

---

## livekit-plugins-rag@0.2.2: livekit-plugins-rag@0.2.2
**Published:** 2024-08-17

### Patch Changes

-   rag: fix backward compatibility - [#629](https://github.com/livekit/agents/pull/629) ([@afigar](https://github.com/afigar))


[View on GitHub](https://github.com/livekit/agents/releases/tag/livekit-plugins-rag%400.2.2)

---

## livekit-plugins-openai@0.8.1: livekit-plugins-openai@0.8.1
**Published:** 2024-08-17

### Patch Changes

-   add support for Ollama, Perplexity, Fireworks, Octo, Together, and Groq LLMs through the OpenAI API - [#611](https://github.com/livekit/agents/pull/611) ([@nbsp](https://github.com/nbsp))

-   allow sending user IDs - [#633](https://github.com/livekit/agents/pull/633) ([@nbsp](https://github.com/nbsp))

-   Support OpenAI Assistants API as a beta feature under `livekit.plugins.openai.beta` - [#601](https://github.com/livekit/agents/pull/601) ([@keepingitneil](https://github.com/keepingitneil))
    Add \_metadata to ChatCtx and ChatMessage which can be used (in the case of OpenAI assistants) for bookeeping to sync local state with remote, OpenAI state


[View on GitHub](https://github.com/livekit/agents/releases/tag/livekit-plugins-openai%400.8.1)

---

## livekit-plugins-nltk@0.7.1: livekit-plugins-nltk@0.7.1
**Published:** 2024-08-17

### Patch Changes

-   Revert "nltk: fix broken punkt download" - [#630](https://github.com/livekit/agents/pull/630) ([@theomonnom](https://github.com/theomonnom))


[View on GitHub](https://github.com/livekit/agents/releases/tag/livekit-plugins-nltk%400.7.1)

---

## livekit-plugins-deepgram@0.6.5: livekit-plugins-deepgram@0.6.5
**Published:** 2024-08-17

### Patch Changes

-   deepgram: fallback to nova-2-general when the language isn't supported - [#623](https://github.com/livekit/agents/pull/623) ([@theomonnom](https://github.com/theomonnom))


[View on GitHub](https://github.com/livekit/agents/releases/tag/livekit-plugins-deepgram%400.6.5)

---

## livekit-plugins-cartesia@0.4.1: livekit-plugins-cartesia@0.4.1
**Published:** 2024-08-17

### Patch Changes

-   Switch Cartesia to a sentence tokenizer and keep the same context id throughout. - [#608](https://github.com/livekit/agents/pull/608) ([@keepingitneil](https://github.com/keepingitneil))
    Propagate segment_id through the basic sentence tokenizer


[View on GitHub](https://github.com/livekit/agents/releases/tag/livekit-plugins-cartesia%400.4.1)

---

## livekit-agents@0.8.6: livekit-agents@0.8.6
**Published:** 2024-08-17

[v0.7.x to v0.8.x migration guide](https://github.com/livekit/agents/blob/main/0.8-migration-guide.md)

### Patch Changes

-   voiceassistant: fix will_synthesize_assistant_reply race - [#638](https://github.com/livekit/agents/pull/638) ([@theomonnom](https://github.com/theomonnom))

-   Switch Cartesia to a sentence tokenizer and keep the same context id throughout. - [#608](https://github.com/livekit/agents/pull/608) ([@keepingitneil](https://github.com/keepingitneil))
    Propagate segment_id through the basic sentence tokenizer

-   silero: adjust vad activation threshold - [#639](https://github.com/livekit/agents/pull/639) ([@theomonnom](https://github.com/theomonnom))

-   limit simultaneous process initialization - [#621](https://github.com/livekit/agents/pull/621) ([@theomonnom](https://github.com/theomonnom))

-   voiceassistant: remove fade effect when interrupting #622 - [#623](https://github.com/livekit/agents/pull/623) ([@theomonnom](https://github.com/theomonnom))

-   ipc improvements, fix slow shutdown & cleanup leaked resources - [#607](https://github.com/livekit/agents/pull/607) ([@theomonnom](https://github.com/theomonnom))

-   ipc: use our own duplex instead of mp.Queue - [#634](https://github.com/livekit/agents/pull/634) ([@theomonnom](https://github.com/theomonnom))

-   Support OpenAI Assistants API as a beta feature under `livekit.plugins.openai.beta` - [#601](https://github.com/livekit/agents/pull/601) ([@keepingitneil](https://github.com/keepingitneil))
    Add \_metadata to ChatCtx and ChatMessage which can be used (in the case of OpenAI assistants) for bookeeping to sync local state with remote, OpenAI state

-   llm: fix optional arguments & non-hashable list - [#637](https://github.com/livekit/agents/pull/637) ([@theomonnom](https://github.com/theomonnom))

-   silero: fix vad padding & static audio - [#631](https://github.com/livekit/agents/pull/631) ([@theomonnom](https://github.com/theomonnom))


[View on GitHub](https://github.com/livekit/agents/releases/tag/livekit-agents%400.8.6)

---

## livekit-plugins-google@0.6.2: livekit-plugins-google@0.6.2
**Published:** 2024-08-07

### Patch Changes

-   stt/tts: fix unread inputs when the input channel is closed - [#594](https://github.com/livekit/agents/pull/594) ([@theomonnom](https://github.com/theomonnom))


[View on GitHub](https://github.com/livekit/agents/releases/tag/livekit-plugins-google%400.6.2)

---

## livekit-plugins-elevenlabs@0.7.3: livekit-plugins-elevenlabs@0.7.3
**Published:** 2024-08-07

### Patch Changes

-   elevenlabs: fix send_task not closing properly - [#596](https://github.com/livekit/agents/pull/596) ([@theomonnom](https://github.com/theomonnom))

-   Fix elevenlabs voice settings breaking - [#586](https://github.com/livekit/agents/pull/586) ([@nbsp](https://github.com/nbsp))


[View on GitHub](https://github.com/livekit/agents/releases/tag/livekit-plugins-elevenlabs%400.7.3)

---

## livekit-plugins-deepgram@0.6.4: livekit-plugins-deepgram@0.6.4
**Published:** 2024-08-07

### Patch Changes

-   deepgram: add support for keywords boost/penalty - [#599](https://github.com/livekit/agents/pull/599) ([@theomonnom](https://github.com/theomonnom))

-   fix log warnings & cartesia end of speech - [#603](https://github.com/livekit/agents/pull/603) ([@theomonnom](https://github.com/theomonnom))

-   stt/tts: fix unread inputs when the input channel is closed - [#594](https://github.com/livekit/agents/pull/594) ([@theomonnom](https://github.com/theomonnom))


[View on GitHub](https://github.com/livekit/agents/releases/tag/livekit-plugins-deepgram%400.6.4)

---

## livekit-plugins-cartesia@0.3.0: livekit-plugins-cartesia@0.3.0
**Published:** 2024-08-07

### Minor Changes

-   cartesia: correctly add spaces & fix tests - [#591](https://github.com/livekit/agents/pull/591) ([@theomonnom](https://github.com/theomonnom))

### Patch Changes

-   fix log warnings & cartesia end of speech - [#603](https://github.com/livekit/agents/pull/603) ([@theomonnom](https://github.com/theomonnom))

-   stt/tts: fix unread inputs when the input channel is closed - [#594](https://github.com/livekit/agents/pull/594) ([@theomonnom](https://github.com/theomonnom))

-   Adds websockets streaming to Cartesia plugin - [#544](https://github.com/livekit/agents/pull/544) ([@sauhardjain](https://github.com/sauhardjain))


[View on GitHub](https://github.com/livekit/agents/releases/tag/livekit-plugins-cartesia%400.3.0)

---

## livekit-agents@0.8.5: livekit-agents@0.8.5
**Published:** 2024-08-07

[v0.7.x to v0.8.x migration guide](https://github.com/livekit/agents/blob/main/0.8-migration-guide.md)

### Patch Changes

-   add support for optional arguments on ai_callable functions - [#600](https://github.com/livekit/agents/pull/600) ([@theomonnom](https://github.com/theomonnom))

-   voiceassistant: correctly export AssistantTranscriptionOptions - [#598](https://github.com/livekit/agents/pull/598) ([@theomonnom](https://github.com/theomonnom))

-   fix: log levelname not present when using the start subcommand - [#602](https://github.com/livekit/agents/pull/602) ([@theomonnom](https://github.com/theomonnom))

-   voiceassistant: fix incomplete committed agent transcript in the chat_ctx - [#595](https://github.com/livekit/agents/pull/595) ([@theomonnom](https://github.com/theomonnom))

-   cartesia: correctly add spaces & fix tests - [#591](https://github.com/livekit/agents/pull/591) ([@theomonnom](https://github.com/theomonnom))


[View on GitHub](https://github.com/livekit/agents/releases/tag/livekit-agents%400.8.5)

---

## livekit-plugins-silero@0.6.3: livekit-plugins-silero@0.6.3
**Published:** 2024-08-06

### Patch Changes

-   silero: fix high cpu usage - [#569](https://github.com/livekit/agents/pull/569) ([@theomonnom](https://github.com/theomonnom))


[View on GitHub](https://github.com/livekit/agents/releases/tag/livekit-plugins-silero%400.6.3)

---

## livekit-plugins-rag@0.2.1: livekit-plugins-rag@0.2.1
**Published:** 2024-08-06

### Patch Changes

-   rag: add missing logger file - [#571](https://github.com/livekit/agents/pull/571) ([@theomonnom](https://github.com/theomonnom))


[View on GitHub](https://github.com/livekit/agents/releases/tag/livekit-plugins-rag%400.2.1)

---

## livekit-plugins-openai@0.8.0: livekit-plugins-openai@0.8.0
**Published:** 2024-08-06

### Minor Changes

-   openai: use openai client for stt - [#583](https://github.com/livekit/agents/pull/583) ([@theomonnom](https://github.com/theomonnom))

### Patch Changes

-   openai: add api_key argument - [#580](https://github.com/livekit/agents/pull/580) ([@theomonnom](https://github.com/theomonnom))

-   openai: fix incorrect API urls on Windows - [#575](https://github.com/livekit/agents/pull/575) ([@theomonnom](https://github.com/theomonnom))


[View on GitHub](https://github.com/livekit/agents/releases/tag/livekit-plugins-openai%400.8.0)

---

## livekit-plugins-elevenlabs@0.7.2: livekit-plugins-elevenlabs@0.7.2
**Published:** 2024-08-06

### Patch Changes

-   elevenlabs: update default model to eleven_turbo_v2_5 - [#578](https://github.com/livekit/agents/pull/578) ([@theomonnom](https://github.com/theomonnom))

-   gracefully error on non-PCM data - [#567](https://github.com/livekit/agents/pull/567) ([@nbsp](https://github.com/nbsp))


[View on GitHub](https://github.com/livekit/agents/releases/tag/livekit-plugins-elevenlabs%400.7.2)

---

## livekit-plugins-deepgram@0.6.3: livekit-plugins-deepgram@0.6.3
**Published:** 2024-08-06

### Patch Changes

-   deepgram: update default model to nova-2-conversationalai - [#576](https://github.com/livekit/agents/pull/576) ([@theomonnom](https://github.com/theomonnom))


[View on GitHub](https://github.com/livekit/agents/releases/tag/livekit-plugins-deepgram%400.6.3)

---

## livekit-agents@0.8.4: livekit-agents@0.8.4
**Published:** 2024-08-06

[v0.7.x to v0.8.x migration guide](https://github.com/livekit/agents/blob/main/0.8-migration-guide.md)

### Patch Changes

-   voiceassistant: only commit the spoken words in the chat context. - [#589](https://github.com/livekit/agents/pull/589) ([@theomonnom](https://github.com/theomonnom))

-   use aiodns by default - [#579](https://github.com/livekit/agents/pull/579) ([@theomonnom](https://github.com/theomonnom))

-   voice_assistant: fix missing spaces between transcript chunks - [#566](https://github.com/livekit/agents/pull/566) ([@egoldschmidt](https://github.com/egoldschmidt))

-   voiceassistant: fix transcription being fully sent even when interrupted - [#581](https://github.com/livekit/agents/pull/581) ([@theomonnom](https://github.com/theomonnom))

-   voiceassistant: fix AssertionError when there is no user_question - [#582](https://github.com/livekit/agents/pull/582) ([@theomonnom](https://github.com/theomonnom))

-   voiceassistant: fix speech validation cancellation - [#584](https://github.com/livekit/agents/pull/584) ([@theomonnom](https://github.com/theomonnom))

-   voiceassistant: fix synthesis continuing after interruption - [#588](https://github.com/livekit/agents/pull/588) ([@theomonnom](https://github.com/theomonnom))


[View on GitHub](https://github.com/livekit/agents/releases/tag/livekit-agents%400.8.4)

---

## livekit-plugins-silero@0.6.2: livekit-plugins-silero@0.6.2
**Published:** 2024-08-01

### Patch Changes

-   silero: tiny tweaks - [#565](https://github.com/livekit/agents/pull/565) ([@theomonnom](https://github.com/theomonnom))

-   silero: optimize numpy input buffers - [#550](https://github.com/livekit/agents/pull/550) ([@theomonnom](https://github.com/theomonnom))

-   silero: bring back expfilter - [#562](https://github.com/livekit/agents/pull/562) ([@theomonnom](https://github.com/theomonnom))


[View on GitHub](https://github.com/livekit/agents/releases/tag/livekit-plugins-silero%400.6.2)

---

## livekit-plugins-deepgram@0.6.2: livekit-plugins-deepgram@0.6.2
**Published:** 2024-08-01

### Patch Changes

-   deepgram: reduce chunks size to 100ms - [#561](https://github.com/livekit/agents/pull/561) ([@theomonnom](https://github.com/theomonnom))

-   deepgram: segment audio frames into 200ms intervals before sending to the websocket #549 - [#553](https://github.com/livekit/agents/pull/553) ([@theomonnom](https://github.com/theomonnom))


[View on GitHub](https://github.com/livekit/agents/releases/tag/livekit-plugins-deepgram%400.6.2)

---

## livekit-agents@0.8.3: livekit-agents@0.8.3
**Published:** 2024-08-01

There were breaking changes from v0.7.x to v0.8.x. See the full 0.8.0 changelog [here](https://github.com/livekit/agents/releases/tag/livekit-agents%400.8.0)

### Patch Changes

-   voiceassistant: run function calls sequentially - [#554](https://github.com/livekit/agents/pull/554) ([@theomonnom](https://github.com/theomonnom))

-   configure plugins loggers & more debug logs on the voiceassistant - [#555](https://github.com/livekit/agents/pull/555) ([@theomonnom](https://github.com/theomonnom))

-   warn no room connection after job_entry was called after 10 seconds. - [#558](https://github.com/livekit/agents/pull/558) ([@theomonnom](https://github.com/theomonnom))

-   deepgram: reduce chunks size to 100ms - [#561](https://github.com/livekit/agents/pull/561) ([@theomonnom](https://github.com/theomonnom))

-   voiceassistant: cleanup validation behaviour #545 - [#553](https://github.com/livekit/agents/pull/553) ([@theomonnom](https://github.com/theomonnom))

-   voiceassistant: commit user question directly when allow_interruptions=False - [#547](https://github.com/livekit/agents/pull/547) ([@theomonnom](https://github.com/theomonnom))

-   ipc: increase high ping threshold - [#556](https://github.com/livekit/agents/pull/556) ([@theomonnom](https://github.com/theomonnom))

-   voiceassistant: interrupt on final transcript - [#546](https://github.com/livekit/agents/pull/546) ([@theomonnom](https://github.com/theomonnom))

-   voiceassistant: tweaks & fix speech being removed too soon from the queue - [#560](https://github.com/livekit/agents/pull/560) ([@theomonnom](https://github.com/theomonnom))

-   voiceassistant: fix duplicate answers - [#548](https://github.com/livekit/agents/pull/548) ([@theomonnom](https://github.com/theomonnom))

-   reduce the default load threshold to a more appropriate default - [#559](https://github.com/livekit/agents/pull/559) ([@theomonnom](https://github.com/theomonnom))


[View on GitHub](https://github.com/livekit/agents/releases/tag/livekit-agents%400.8.3)

---

## livekit-agents@0.8.2: livekit-agents@0.8.2
**Published:** 2024-07-28

There were breaking changes from v0.7.x to v0.8.x. See the full 0.8.0 changelog [here](https://github.com/livekit/agents/releases/tag/livekit-agents%400.8.0)

### Patch Changes

-   fix: remove unnecessary async function - [#540](https://github.com/livekit/agents/pull/540) ([@Nabil372](https://github.com/Nabil372))


[View on GitHub](https://github.com/livekit/agents/releases/tag/livekit-agents%400.8.2)

---

## livekit-plugins-silero@0.6.1: livekit-plugins-silero@0.6.1
**Published:** 2024-07-26

### Patch Changes

-   fix end_input not flushing & unhandled flush messages - [#528](https://github.com/livekit/agents/pull/528) ([@theomonnom](https://github.com/theomonnom))


[View on GitHub](https://github.com/livekit/agents/releases/tag/livekit-plugins-silero%400.6.1)

---

## livekit-plugins-openai@0.7.1: livekit-plugins-openai@0.7.1
**Published:** 2024-07-26

### Patch Changes

-   set timeout to 5 seconds - [#524](https://github.com/livekit/agents/pull/524) ([@nbsp](https://github.com/nbsp))


[View on GitHub](https://github.com/livekit/agents/releases/tag/livekit-plugins-openai%400.7.1)

---

## livekit-plugins-google@0.6.1: livekit-plugins-google@0.6.1
**Published:** 2024-07-26

### Patch Changes

-   fix end_input not flushing & unhandled flush messages - [#528](https://github.com/livekit/agents/pull/528) ([@theomonnom](https://github.com/theomonnom))


[View on GitHub](https://github.com/livekit/agents/releases/tag/livekit-plugins-google%400.6.1)

---

## livekit-plugins-elevenlabs@0.7.1: livekit-plugins-elevenlabs@0.7.1
**Published:** 2024-07-26

### Patch Changes

-   fix end_input not flushing & unhandled flush messages - [#528](https://github.com/livekit/agents/pull/528) ([@theomonnom](https://github.com/theomonnom))


[View on GitHub](https://github.com/livekit/agents/releases/tag/livekit-plugins-elevenlabs%400.7.1)

---

## livekit-plugins-deepgram@0.6.1: livekit-plugins-deepgram@0.6.1
**Published:** 2024-07-26

### Patch Changes

-   fix end_input not flushing & unhandled flush messages - [#528](https://github.com/livekit/agents/pull/528) ([@theomonnom](https://github.com/theomonnom))


[View on GitHub](https://github.com/livekit/agents/releases/tag/livekit-plugins-deepgram%400.6.1)

---

## livekit-plugins-azure@0.3.1: livekit-plugins-azure@0.3.1
**Published:** 2024-07-26

### Patch Changes

-   fix end_input not flushing & unhandled flush messages - [#528](https://github.com/livekit/agents/pull/528) ([@theomonnom](https://github.com/theomonnom))


[View on GitHub](https://github.com/livekit/agents/releases/tag/livekit-plugins-azure%400.3.1)

---

## livekit-agents@0.8.1: livekit-agents@0.8.1
**Published:** 2024-07-26

There were breaking changes from v0.7.x to v0.8.x. Please reference the full 0.8.0 changelog [here](https://github.com/livekit/agents/releases/tag/livekit-agents%400.8.0)

### Patch Changes

-   update livekit-rtc to v0.12.0 - [#535](https://github.com/livekit/agents/pull/535) ([@theomonnom](https://github.com/theomonnom))

-   automatically create stt.StreamAdapter when provided stt doesn't support streaming - [#536](https://github.com/livekit/agents/pull/536) ([@theomonnom](https://github.com/theomonnom))

-   update examples to the latest API & export AutoSubscribe - [#534](https://github.com/livekit/agents/pull/534) ([@theomonnom](https://github.com/theomonnom))

-   fix end_input not flushing & unhandled flush messages - [#528](https://github.com/livekit/agents/pull/528) ([@theomonnom](https://github.com/theomonnom))


[View on GitHub](https://github.com/livekit/agents/releases/tag/livekit-agents%400.8.1)

---

## livekit-plugins-silero@0.6.0: livekit-plugins-silero@0.6.0
**Published:** 2024-07-24

### Minor Changes

-   dev prerelease - [#435](https://github.com/livekit/agents/pull/435) ([@theomonnom](https://github.com/theomonnom))

### Patch Changes

-   test release - [#435](https://github.com/livekit/agents/pull/435) ([@theomonnom](https://github.com/theomonnom))

-   pull: '--rebase --autostash ...' - [#435](https://github.com/livekit/agents/pull/435) ([@theomonnom](https://github.com/theomonnom))

-   Default loglevel to warn - [#472](https://github.com/livekit/agents/pull/472) ([@lukasIO](https://github.com/lukasIO))

-   bump versions to update dependencies - [#510](https://github.com/livekit/agents/pull/510) ([@theomonnom](https://github.com/theomonnom))

-   test release - [#435](https://github.com/livekit/agents/pull/435) ([@theomonnom](https://github.com/theomonnom))

-   fix changesets release CI - [#435](https://github.com/livekit/agents/pull/435) ([@theomonnom](https://github.com/theomonnom))

-   release v0.8.0 - [`6e74aa714c2dfaa8212db4528d7b59d095b6c660`](https://github.com/livekit/agents/commit/6e74aa714c2dfaa8212db4528d7b59d095b6c660) ([@theomonnom](https://github.com/theomonnom))

-   dev fixes - multiprocessing & voiceassistant - [#493](https://github.com/livekit/agents/pull/493) ([@theomonnom](https://github.com/theomonnom))


[View on GitHub](https://github.com/livekit/agents/releases/tag/livekit-plugins-silero%400.6.0)

---

## livekit-plugins-rag@0.2.0: livekit-plugins-rag@0.2.0
**Published:** 2024-07-24

### Minor Changes

-   dev prerelease - [#435](https://github.com/livekit/agents/pull/435) ([@theomonnom](https://github.com/theomonnom))

### Patch Changes

-   test release - [#435](https://github.com/livekit/agents/pull/435) ([@theomonnom](https://github.com/theomonnom))

-   pull: '--rebase --autostash ...' - [#435](https://github.com/livekit/agents/pull/435) ([@theomonnom](https://github.com/theomonnom))

-   Default loglevel to warn - [#472](https://github.com/livekit/agents/pull/472) ([@lukasIO](https://github.com/lukasIO))

-   bump versions to update dependencies - [#510](https://github.com/livekit/agents/pull/510) ([@theomonnom](https://github.com/theomonnom))

-   test release - [#435](https://github.com/livekit/agents/pull/435) ([@theomonnom](https://github.com/theomonnom))

-   fix changesets release CI - [#435](https://github.com/livekit/agents/pull/435) ([@theomonnom](https://github.com/theomonnom))

-   release v0.8.0 - [`6e74aa714c2dfaa8212db4528d7b59d095b6c660`](https://github.com/livekit/agents/commit/6e74aa714c2dfaa8212db4528d7b59d095b6c660) ([@theomonnom](https://github.com/theomonnom))

-   dev fixes - multiprocessing & voiceassistant - [#493](https://github.com/livekit/agents/pull/493) ([@theomonnom](https://github.com/theomonnom))


[View on GitHub](https://github.com/livekit/agents/releases/tag/livekit-plugins-rag%400.2.0)

---

## livekit-plugins-openai@0.7.0: livekit-plugins-openai@0.7.0
**Published:** 2024-07-24

### Minor Changes

-   dev prerelease - [#435](https://github.com/livekit/agents/pull/435) ([@theomonnom](https://github.com/theomonnom))

### Patch Changes

-   test release - [#435](https://github.com/livekit/agents/pull/435) ([@theomonnom](https://github.com/theomonnom))

-   pull: '--rebase --autostash ...' - [#435](https://github.com/livekit/agents/pull/435) ([@theomonnom](https://github.com/theomonnom))

-   Default loglevel to warn - [#472](https://github.com/livekit/agents/pull/472) ([@lukasIO](https://github.com/lukasIO))

-   bump versions to update dependencies - [#510](https://github.com/livekit/agents/pull/510) ([@theomonnom](https://github.com/theomonnom))

-   test release - [#435](https://github.com/livekit/agents/pull/435) ([@theomonnom](https://github.com/theomonnom))

-   fix changesets release CI - [#435](https://github.com/livekit/agents/pull/435) ([@theomonnom](https://github.com/theomonnom))

-   release v0.8.0 - [`6e74aa714c2dfaa8212db4528d7b59d095b6c660`](https://github.com/livekit/agents/commit/6e74aa714c2dfaa8212db4528d7b59d095b6c660) ([@theomonnom](https://github.com/theomonnom))

-   dev fixes - multiprocessing & voiceassistant - [#493](https://github.com/livekit/agents/pull/493) ([@theomonnom](https://github.com/theomonnom))


[View on GitHub](https://github.com/livekit/agents/releases/tag/livekit-plugins-openai%400.7.0)

---

## livekit-plugins-nltk@0.7.0: livekit-plugins-nltk@0.7.0
**Published:** 2024-07-24

### Minor Changes

-   dev prerelease - [#435](https://github.com/livekit/agents/pull/435) ([@theomonnom](https://github.com/theomonnom))

### Patch Changes

-   test release - [#435](https://github.com/livekit/agents/pull/435) ([@theomonnom](https://github.com/theomonnom))

-   pull: '--rebase --autostash ...' - [#435](https://github.com/livekit/agents/pull/435) ([@theomonnom](https://github.com/theomonnom))

-   Default loglevel to warn - [#472](https://github.com/livekit/agents/pull/472) ([@lukasIO](https://github.com/lukasIO))

-   bump versions to update dependencies - [#510](https://github.com/livekit/agents/pull/510) ([@theomonnom](https://github.com/theomonnom))

-   test release - [#435](https://github.com/livekit/agents/pull/435) ([@theomonnom](https://github.com/theomonnom))

-   fix changesets release CI - [#435](https://github.com/livekit/agents/pull/435) ([@theomonnom](https://github.com/theomonnom))

-   release v0.8.0 - [`6e74aa714c2dfaa8212db4528d7b59d095b6c660`](https://github.com/livekit/agents/commit/6e74aa714c2dfaa8212db4528d7b59d095b6c660) ([@theomonnom](https://github.com/theomonnom))

-   dev fixes - multiprocessing & voiceassistant - [#493](https://github.com/livekit/agents/pull/493) ([@theomonnom](https://github.com/theomonnom))


[View on GitHub](https://github.com/livekit/agents/releases/tag/livekit-plugins-nltk%400.7.0)

---

## livekit-plugins-minimal@0.2.0: livekit-plugins-minimal@0.2.0
**Published:** 2024-07-24

### Minor Changes

-   dev prerelease - [#435](https://github.com/livekit/agents/pull/435) ([@theomonnom](https://github.com/theomonnom))

### Patch Changes

-   test release - [#435](https://github.com/livekit/agents/pull/435) ([@theomonnom](https://github.com/theomonnom))

-   pull: '--rebase --autostash ...' - [#435](https://github.com/livekit/agents/pull/435) ([@theomonnom](https://github.com/theomonnom))

-   Default loglevel to warn - [#472](https://github.com/livekit/agents/pull/472) ([@lukasIO](https://github.com/lukasIO))

-   bump versions to update dependencies - [#510](https://github.com/livekit/agents/pull/510) ([@theomonnom](https://github.com/theomonnom))

-   test release - [#435](https://github.com/livekit/agents/pull/435) ([@theomonnom](https://github.com/theomonnom))

-   fix changesets release CI - [#435](https://github.com/livekit/agents/pull/435) ([@theomonnom](https://github.com/theomonnom))

-   release v0.8.0 - [`6e74aa714c2dfaa8212db4528d7b59d095b6c660`](https://github.com/livekit/agents/commit/6e74aa714c2dfaa8212db4528d7b59d095b6c660) ([@theomonnom](https://github.com/theomonnom))

-   dev fixes - multiprocessing & voiceassistant - [#493](https://github.com/livekit/agents/pull/493) ([@theomonnom](https://github.com/theomonnom))


[View on GitHub](https://github.com/livekit/agents/releases/tag/livekit-plugins-minimal%400.2.0)

---

## livekit-plugins-google@0.6.0: livekit-plugins-google@0.6.0
**Published:** 2024-07-24

### Minor Changes

-   dev prerelease - [#435](https://github.com/livekit/agents/pull/435) ([@theomonnom](https://github.com/theomonnom))

### Patch Changes

-   test release - [#435](https://github.com/livekit/agents/pull/435) ([@theomonnom](https://github.com/theomonnom))

-   pull: '--rebase --autostash ...' - [#435](https://github.com/livekit/agents/pull/435) ([@theomonnom](https://github.com/theomonnom))

-   Default loglevel to warn - [#472](https://github.com/livekit/agents/pull/472) ([@lukasIO](https://github.com/lukasIO))

-   bump versions to update dependencies - [#510](https://github.com/livekit/agents/pull/510) ([@theomonnom](https://github.com/theomonnom))

-   test release - [#435](https://github.com/livekit/agents/pull/435) ([@theomonnom](https://github.com/theomonnom))

-   fix changesets release CI - [#435](https://github.com/livekit/agents/pull/435) ([@theomonnom](https://github.com/theomonnom))

-   release v0.8.0 - [`6e74aa714c2dfaa8212db4528d7b59d095b6c660`](https://github.com/livekit/agents/commit/6e74aa714c2dfaa8212db4528d7b59d095b6c660) ([@theomonnom](https://github.com/theomonnom))

-   dev fixes - multiprocessing & voiceassistant - [#493](https://github.com/livekit/agents/pull/493) ([@theomonnom](https://github.com/theomonnom))


[View on GitHub](https://github.com/livekit/agents/releases/tag/livekit-plugins-google%400.6.0)

---

## livekit-plugins-elevenlabs@0.7.0: livekit-plugins-elevenlabs@0.7.0
**Published:** 2024-07-24

### Minor Changes

-   dev prerelease - [#435](https://github.com/livekit/agents/pull/435) ([@theomonnom](https://github.com/theomonnom))

### Patch Changes

-   test release - [#435](https://github.com/livekit/agents/pull/435) ([@theomonnom](https://github.com/theomonnom))

-   pull: '--rebase --autostash ...' - [#435](https://github.com/livekit/agents/pull/435) ([@theomonnom](https://github.com/theomonnom))

-   Default loglevel to warn - [#472](https://github.com/livekit/agents/pull/472) ([@lukasIO](https://github.com/lukasIO))

-   bump versions to update dependencies - [#510](https://github.com/livekit/agents/pull/510) ([@theomonnom](https://github.com/theomonnom))

-   test release - [#435](https://github.com/livekit/agents/pull/435) ([@theomonnom](https://github.com/theomonnom))

-   fix changesets release CI - [#435](https://github.com/livekit/agents/pull/435) ([@theomonnom](https://github.com/theomonnom))

-   release v0.8.0 - [`6e74aa714c2dfaa8212db4528d7b59d095b6c660`](https://github.com/livekit/agents/commit/6e74aa714c2dfaa8212db4528d7b59d095b6c660) ([@theomonnom](https://github.com/theomonnom))

-   dev fixes - multiprocessing & voiceassistant - [#493](https://github.com/livekit/agents/pull/493) ([@theomonnom](https://github.com/theomonnom))


[View on GitHub](https://github.com/livekit/agents/releases/tag/livekit-plugins-elevenlabs%400.7.0)

---

## livekit-plugins-deepgram@0.6.0: livekit-plugins-deepgram@0.6.0
**Published:** 2024-07-24

### Minor Changes

-   dev prerelease - [#435](https://github.com/livekit/agents/pull/435) ([@theomonnom](https://github.com/theomonnom))

### Patch Changes

-   test release - [#435](https://github.com/livekit/agents/pull/435) ([@theomonnom](https://github.com/theomonnom))

-   pull: '--rebase --autostash ...' - [#435](https://github.com/livekit/agents/pull/435) ([@theomonnom](https://github.com/theomonnom))

-   Default loglevel to warn - [#472](https://github.com/livekit/agents/pull/472) ([@lukasIO](https://github.com/lukasIO))

-   bump versions to update dependencies - [#510](https://github.com/livekit/agents/pull/510) ([@theomonnom](https://github.com/theomonnom))

-   test release - [#435](https://github.com/livekit/agents/pull/435) ([@theomonnom](https://github.com/theomonnom))

-   fix changesets release CI - [#435](https://github.com/livekit/agents/pull/435) ([@theomonnom](https://github.com/theomonnom))

-   release v0.8.0 - [`6e74aa714c2dfaa8212db4528d7b59d095b6c660`](https://github.com/livekit/agents/commit/6e74aa714c2dfaa8212db4528d7b59d095b6c660) ([@theomonnom](https://github.com/theomonnom))

-   dev fixes - multiprocessing & voiceassistant - [#493](https://github.com/livekit/agents/pull/493) ([@theomonnom](https://github.com/theomonnom))


[View on GitHub](https://github.com/livekit/agents/releases/tag/livekit-plugins-deepgram%400.6.0)

---

## livekit-plugins-cartesia@0.2.0: livekit-plugins-cartesia@0.2.0
**Published:** 2024-07-24

### Minor Changes

-   dev prerelease - [#435](https://github.com/livekit/agents/pull/435) ([@theomonnom](https://github.com/theomonnom))

### Patch Changes

-   test release - [#435](https://github.com/livekit/agents/pull/435) ([@theomonnom](https://github.com/theomonnom))

-   pull: '--rebase --autostash ...' - [#435](https://github.com/livekit/agents/pull/435) ([@theomonnom](https://github.com/theomonnom))

-   Default loglevel to warn - [#472](https://github.com/livekit/agents/pull/472) ([@lukasIO](https://github.com/lukasIO))

-   bump versions to update dependencies - [#510](https://github.com/livekit/agents/pull/510) ([@theomonnom](https://github.com/theomonnom))

-   test release - [#435](https://github.com/livekit/agents/pull/435) ([@theomonnom](https://github.com/theomonnom))

-   fix changesets release CI - [#435](https://github.com/livekit/agents/pull/435) ([@theomonnom](https://github.com/theomonnom))

-   release v0.8.0 - [`6e74aa714c2dfaa8212db4528d7b59d095b6c660`](https://github.com/livekit/agents/commit/6e74aa714c2dfaa8212db4528d7b59d095b6c660) ([@theomonnom](https://github.com/theomonnom))

-   dev fixes - multiprocessing & voiceassistant - [#493](https://github.com/livekit/agents/pull/493) ([@theomonnom](https://github.com/theomonnom))


[View on GitHub](https://github.com/livekit/agents/releases/tag/livekit-plugins-cartesia%400.2.0)

---

## livekit-plugins-azure@0.3.0: livekit-plugins-azure@0.3.0
**Published:** 2024-07-24

### Minor Changes

-   dev prerelease - [#435](https://github.com/livekit/agents/pull/435) ([@theomonnom](https://github.com/theomonnom))

### Patch Changes

-   test release - [#435](https://github.com/livekit/agents/pull/435) ([@theomonnom](https://github.com/theomonnom))

-   pull: '--rebase --autostash ...' - [#435](https://github.com/livekit/agents/pull/435) ([@theomonnom](https://github.com/theomonnom))

-   Default loglevel to warn - [#472](https://github.com/livekit/agents/pull/472) ([@lukasIO](https://github.com/lukasIO))

-   bump versions to update dependencies - [#510](https://github.com/livekit/agents/pull/510) ([@theomonnom](https://github.com/theomonnom))

-   test release - [#435](https://github.com/livekit/agents/pull/435) ([@theomonnom](https://github.com/theomonnom))

-   fix changesets release CI - [#435](https://github.com/livekit/agents/pull/435) ([@theomonnom](https://github.com/theomonnom))

-   release v0.8.0 - [`6e74aa714c2dfaa8212db4528d7b59d095b6c660`](https://github.com/livekit/agents/commit/6e74aa714c2dfaa8212db4528d7b59d095b6c660) ([@theomonnom](https://github.com/theomonnom))

-   dev fixes - multiprocessing & voiceassistant - [#493](https://github.com/livekit/agents/pull/493) ([@theomonnom](https://github.com/theomonnom))


[View on GitHub](https://github.com/livekit/agents/releases/tag/livekit-plugins-azure%400.3.0)

---

## livekit-agents@0.8.0: livekit-agents@0.8.0
**Published:** 2024-07-24

# v0.8.0 changelogs

v0.8.0 is our biggest release yet, featuring significant reliability improvements to VoiceAssistant. This update includes a few breaking API changes that will impact the way you build your agents. We strive to minimize breaking changes and will stabilize the API as we approach version 1.0.

# Migrating to v0.8.0 (Breaking Changes)
<details>
<summary><h2>Job and Worker</h2></summary>

### entrypoint moved from req.accept() to WorkerOptions

Previously the job entrypoint was in the req.accept() method call. Now the job entrypoint has been moved into WorkerOptions. 

### namespace removed

The WorkerOptions namespace field has been removed and will be replaced in the future.

### explict connection to the room

You now need to call ctx.connect() to initiate the connection to the room. This allows for pre-connect setup (such as callback registrations) to avoid race conditions.

The following shows a minimal_worker.py example:

```python
from livekit.agents import JobContext, JobRequest, WorkerOptions, cli

async def job_entrypoint(ctx: JobContext):
    await ctx.connect()
    ...

if __name__ == "__main__":
    cli.run_app(
        WorkerOptions(entrypoint_fnc=job_entrypoint)
    )
```
</details>

<details>
<summary><h2>LLM</h2></summary>

> 💡 These changes may not be relevant to users of the VoiceAssistant class.

The LLM class has been restructured to enhance ergonomics and improve the function calling experience.

### Function/tool calling

Function calling has gotten a complete overhaul in v0.8.0. Most the the changes are additive and can be found in the New Features section. 

The primary breaking change is that function calls are now **NOT** automatically invoked when iterating the LLM stream. `LLMStream.execute_functions` needs to be called instead.

TODO: insert code snipper showing some ai_callable fncs

### `LLM.chat()` is no longer an async method

Previously, LLM.chat() was an async method that returned an LLMStream (which itself was an AsyncIterable). 

We found it easier and less-confusing for LLM.chat() to be synchronous, while still returning the same AsyncIterable LLMStream.

### LLM.chat ‘history’ has been renamed to ‘chat_ctx’

In order to improve consistency and reduce confusion.

TODO: insert code snippet

</details>

<details>
<summary><h2>STT</h2></summary>

> 💡 These changes may not be relevant to users of the VoiceAssistant class.

### SpeechStream.flush()

Previously, to communicate to a STT provider that you have sent enough input to generate a response - you could push_frame(None) to coax the TTS into synthesizing a response. 

In v0.8.0 that API has been removed and replaced with flush()

### SpeechStream.end_input()

`end_input` signals to the STT provider that the input is complete and no additional input will follow. Previously, this was done using aclose(wait=True).

### SpeechStream.aclose()

The “wait” arg of aclose has been removed in favor of SpeechStream.end_input (see above). Now, if you call TTS.aclose() without first calling STT.end_input, the behavior will be that the request is cancelled.

```python
stt_stream = my_stt_instance.stream()
async for ev in audio_stream:
  stt_stream.push_frame(ev.frame)
  # optionally flush when enough frames have been pushed
  stt_stream.flush()

stt_stream.end_input()
await stt_stream.aclose()
```

</details>

<details>
<summary><h2>TTS</h2></summary>

> 💡 These changes may not be relevant to users of the VoiceAssistant class.

### SynthesizedAudio changed and SynthesisEvent removed

Most of the fields of the SynthesizedAudio dataclass have been changed:

```python
# New SynthesizedAudio dataclass
@dataclass
class SynthesizedAudio:
    request_id: str
    """Request ID (one segment could be made up of multiple requests)"""
    segment_id: str
    """Segment ID, each segment is separated by a flush"""
    frame: rtc.AudioFrame
    """Synthesized audio frame"""
    delta_text: str = ""
    """Current segment of the synthesized audio"""
    
#Old SynthesizedAudio dataclass
@dataclass
class SynthesizedAudio:
    text: str
    data: rtc.AudioFrame
```

The SynthesisEvent has been removed entirely. All occurrences of it have been replaced with SynthesizedAudio

### SynthesizeStream.flush()

Similar to the STT changes, this coaxes the TTS provider into generating a response. The SynthesizedAudio response will have a new segment_id after calls to flush().

### SynthesizeStream.end_input()

Similar to the STT changes, this replaces aclose(wait=True).

### SynthesizeStream.aclose()

Similar to the STT changes, the wait arg has been removed.

```python
tts_stream = my_tts_instance.stream()
tts_stream.push_text("This is the first sentence")
tts_stream.flush()
tts_stream.push_text("This is the second sentence")
tts_stream.end_input()
await tts_stream.aclose()
```

</details>

<details>
<summary><h2>VAD</h2></summary>

### flush(), end_input(), aclose()

The same changes made to STT and TTS have also been made to VAD

```python
vad_stream = my_vad_instance.stream()
async for ev in audio_stream:
  vad_stream.push_frame(ev.frame)
  # optionally flush when enough frames have been pushed
  vad_stream.flush()

vad_stream.end_input()
await vad_stream.aclose()
```
</details>

<details>
<summary><h2>VoiceAssistant</h2></summary>

Much of the VoiceAssistant API remains unchanged, despite significant improvements to functionality and internals. However, there have been changes to the configuration.

### Initialization args

- Removed
    - base_volume
    - debug
    - sentence_tokenizer, word_tokenizer, hyphenate_word
- Changed
    - transcription related options now all fall into the “transcription” arg

```python
class VoiceAssistant(utils.EventEmitter[EventTypes]):
    def __init__(
        self,
        *,
        vad: vad.VAD,
        stt: stt.STT,
        llm: LLM,
        tts: tts.TTS,
        chat_ctx: ChatContext | None = None,
        fnc_ctx: FunctionContext | None = None,
        allow_interruptions: bool = True,
        interrupt_speech_duration: float = 0.6,
        interrupt_min_words: int = 0,
        preemptive_synthesis: bool = True,
        transcription: AssistantTranscriptionOptions = AssistantTranscriptionOptions(),
        will_synthesize_assistant_reply: WillSynthesizeAssistantReply = _default_will_synthesize_assistant_reply,
        plotting: bool = False,
        loop: asyncio.AbstractEventLoop | None = None,
    ) -> None:
    ...
```
</details>

# New features

## Job and Worker

- New prewarm_fnc in WorkerOptions that can be used to setup agent subprocesses before the agent joins the room. Useful for things like loading model weights.
- New num_idle_processes in WorkerOptions for keeping a process pool available for subsequent agents. This improves the latency of agents joining rooms and being ready to participate.
- Health server listens on 0.0.0.0 by default now instead of localhost

## LLM

- You can now add AI functions at runtime.
- AI functions can now return values and throw exceptions. The return values and exception are automatically added to the chat_ctx so the LLM is aware of them.

## VAD

- livekit-plugins-silero
    - The onnx runtime is used directly now which removes pytorch dependency
    - Model weights are included in the python package itself, you no longer need to download model weights as a build step
    - The model has been updated to the latest silero model (V5) which has improved [accuracy](https://github.com/snakers4/silero-vad/issues/2#issuecomment-2195433115)
    - Logic fixes to inference + hidden state which improves accuracy

## TTS

- A new Cartesia plugin has been introduced
- SynthesizeStream now has flush() and end_input() for better control over which text input to audio output synchronization
- SynthesizedAudio now has a segment_id for more granularity around what audio corresponds to what input text

## VoiceAssistant

- Big improvements and bug fixes to interrupt logic
- Bug fixes for duplicated responses
- Bug fixes for stuck responses

## RAG

- New livekit-plugins-rag package to help with RAG related tasks
    - Index builder for creating searchable index
    - Nearest neighbor search on indexes based on spotify annoy library

## New Contributors

Thanks to @Ocupe @mattherzog @lukasIO @seanmuirhead @PaulLockett @CalinR @cs50victor @vanics @brightsparc @ty-elastic @naman-scogo @eltociear @hauntsaninja @minhpq331 @nbsp for their first contributions on the project!

**Full Detailed Changes**: [https://github.com/livekit/agents/compare/3c340eabfc6fc42bcd88fb08c90c101463cca8f5..596ac9042b3ecbe40c270d035d5da8f25474e569?diff=split&w=](https://github.com/livekit/agents/compare/3c340eabfc6fc42bcd88fb08c90c101463cca8f5..596ac9042b3ecbe40c270d035d5da8f25474e569?diff=split&w=)

[View on GitHub](https://github.com/livekit/agents/releases/tag/livekit-agents%400.8.0)

---

