# Vision-Agents Skill Documentation

This documentation provides a comprehensive guide to the `vision-agents` skill, designed to help Google Gemini effectively understand and utilize its capabilities. Vision-Agents enable the creation of intelligent, low-latency multi-modal AI agents that can watch, listen, and understand video in real-time.

## Description

The `vision-agents` skill provides the building blocks for developing advanced AI agents that interact with real-time video and audio streams. It integrates various AI models and services (like YOLO, Roboflow, Gemini, OpenAI) to process and understand visual and auditory input, facilitating dynamic, conversational AI experiences.

**When to Use This Skill:**
Use this skill when you need to:
*   Build real-time video AI applications, such as sports coaching, security camera systems, or invisible AI assistants.
*   Combine object detection (YOLO, Roboflow) with powerful LLMs (Gemini, OpenAI) for comprehensive scene understanding.
*   Develop low-latency, conversational voice UX with speech-to-text (STT), text-to-speech (TTS), and turn detection.
*   Implement custom video and audio processing pipelines.
*   Integrate external APIs and tools for enhanced agent functionality.
*   Understand or leverage the codebase architecture and design patterns related to real-time AI agents.

## Table of Contents

1.  [Description](#description)
2.  [Key Concepts](#key-concepts)
    *   [Core Agent Components](#core-agent-components)
    *   [The Processor Pattern](#the-processor-pattern)
    *   [LLM Integration (Realtime)](#llm-integration-realtime)
    *   [Conversation & Memory](#conversation--memory)
    *   [Audio Management with PcmData](#audio-management-with-pcmdata)
    *   [Production & Observability](#production--observability)
3.  [Quick Reference: Practical Code Examples](#quick-reference-practical-code-examples)
4.  [How-To Guides Index](#how-to-guides-index)
5.  [Configuration Patterns](#configuration-patterns)
6.  [Project Documentation](#project-documentation)
7.  [Development & Contributing Guidelines](#development--contributing-guidelines)
8.  [Available References](#available-references)

## Key Concepts

Understanding the following core concepts is crucial for effectively using the `vision-agents` skill:

### Core Agent Components

*   **`Agent`**: The central class for defining and orchestrating an AI agent. It brings together LLMs, STT, TTS, processors, and instructions.
*   **`Edge`**: Represents the Stream edge network connector, enabling low-latency audio/video communication.
*   **`agent_user`**: The user object representing the AI agent itself (e.g., its name and ID in a chat system).
*   **`instructions`**: The system prompt or initial directives that define the agent's persona and goals. Can be loaded from markdown files.
*   **`function_tool`**: A decorator used to expose Python functions as callable tools for the LLM, enabling the agent to perform actions or query external systems.
*   **`call` / `join_call`**: Methods for the agent to connect to and participate in a real-time video/audio call.
*   **`on_agent_state_changed`**: An event handler that can be used to react to changes in the agent's operational state.
*   **`AgentState`**: An enum representing the various states an agent can be in (e.g., `CONNECTING`, `ACTIVE`, `IDLE`, `STOPPED`).

### The Processor Pattern (KEY LEARNING POINT)

The processor pattern is fundamental to Vision-Agents, allowing modular, real-time analysis and transformation of audio and video streams *before* or *after* interaction with LLMs.

*   **`VideoProcessor`**: A base class for components that analyze or transform video frames.
*   **`AudioProcessor`**: A base class for components that analyze or transform audio data.
*   **`process_video(track, participant_id, shared_forwarder)`**: The core method in a `VideoProcessor` for handling incoming video frames.
    *   `track`: The video track being processed.
    *   `participant_id`: Identifier for the participant providing the video.
    *   `shared_forwarder`: A mechanism to forward processed video (e.g., with annotations) to other components or back to the stream.
*   **`process_audio(track, participant_id)`**: The core method in an `AudioProcessor` for handling incoming audio data.
*   **`attach_agent(agent)`**: A crucial state injection mechanism. This method is called when a processor is added to an `Agent`, providing the processor access to the agent's event system and other core components, allowing processor results to flow into the Agent's next turn.
*   **`add_frame_handler(handler, fps, name)`**: Used within processors to register handlers that process video frames at a controlled frame rate (`fps`), critical for managing computational load, especially in mobile or AR contexts.
*   **`shared_forwarder`**: A component that allows video frames (potentially annotated) to be efficiently shared between multiple processors or output tracks, preventing redundant processing.

### LLM Integration (Realtime)

Vision-Agents prioritize real-time interaction with LLMs, especially for video and voice.

*   **`gemini.Realtime(fps=N)`**: Integrates Google Gemini's real-time capabilities, allowing the LLM to directly consume video frames at a specified `fps` for native visual understanding.
*   **`openai.Realtime(fps=N)`**: Integrates OpenAI's real-time APIs, providing native video input capabilities for their models.
*   **Context injection via Processor → Agent event system**: Processors analyze media and inject their findings (e.g., detected objects, poses) into the agent's event stream, which the LLM can then consume as part of its conversational context.

### Conversation & Memory

*   **`ConversationMessage`**: A standardized data structure for managing messages within the agent's conversation history.
*   **`conversation` module**: Provides utilities for maintaining in-memory and persistent conversation storage, allowing agents to recall context across turns and sessions.

### Audio Management with PcmData

The library standardizes audio handling through the `PcmData` object, preventing common issues with disparate audio formats, sample rates, and channels.

*   **`PcmData`**: A container type for Pulse-Code Modulation (PCM) audio samples, including metadata like `sample_rate`, `channels`, and `format`.
*   Methods for converting formats (`to_float32`, `to_int16`, `to_bytes`, `to_wav_bytes`), resampling (`resample`), and manipulating audio (`append`, `copy`, `chunks`).

### Production & Observability

*   **`metrics` / `prometheus`**: Built-in support for collecting and exposing performance metrics, crucial for monitoring agents in production.
*   **HTTP server mode (`agent_server_example`)**: Agents can be deployed as HTTP servers, enabling flexible integration and scaling.
*   **Docker deployment with GPU**: Guidance and examples for deploying agents in containerized environments with GPU acceleration for demanding vision tasks.

## Quick Reference: Practical Code Examples

This section provides short, actionable code examples demonstrating common tasks and core functionalities of Vision-Agents.

### 1. Golf Coach Agent Setup (Real-time Pose Detection with YOLO & Gemini)

This example shows how to configure an `Agent` to provide real-time golf coaching by combining a YOLO pose detection processor with Gemini's real-time capabilities.

```python
# full example: examples/02_golf_coach_example/golf_coach_example.py
from vision_agents.core import Agent, User
from vision_agents.plugins import getstream, gemini, ultralytics

agent = Agent(
    edge=getstream.Edge(),
    agent_user=User(name="Golf Coach AI", id="coach-agent"),
    instructions="Read @golf_coach.md", # Loads detailed coaching instructions
    llm=gemini.Realtime(fps=10), # Gemini processes video at 10 frames per second
    processors=[
        ultralytics.YOLOPoseProcessor(model_path="yolo11n-pose.pt", device="cuda")
    ],
)
# Agent.join(call) would then start the real-time interaction
```

### 2. Security Camera Agent (Object Detection & Automated Response)

This example sets up a security camera agent that uses YOLOv11 for package detection, combined with an LLM for voice interaction and automated responses.

```python
# full example: examples/04_security_camera_example/security_camera_example.py
from vision_agents.core import Agent, User
from vision_agents.plugins import getstream, gemini, elevenlabs, deepgram
# Assuming SecurityCameraProcessor is a custom VideoProcessor implementation
from examples.04_security_camera_example.security_processor import SecurityCameraProcessor

security_processor = SecurityCameraProcessor(
    fps=5,
    model_path="weights_custom.pt",  # YOLOv11 for package detection
    package_conf_threshold=0.7,
)

agent = Agent(
    edge=getstream.Edge(),
    agent_user=User(name="Security AI", id="agent"),
    instructions="Read @instructions.md",
    processors=[security_processor],
    llm=gemini.LLM("gemini-2.5-flash-lite"),
    tts=elevenlabs.TTS(),
    stt=deepgram.STT(),
)
# The agent would then be joined to a call or video stream
```

### 3. Invisible Assistant Agent (Silent Real-time Screen/Audio Understanding)

This demonstrates an agent designed for silent assistance, utilizing Gemini's real-time capabilities to "watch" the screen and audio without broadcasting its own audio.

```python
# partial example, full example: examples/04_security_camera_example/security_camera_example.py
from vision_agents.core import Agent, User
from vision_agents.plugins import getstream, gemini

agent_user = User(name="Interview Coach", id="invisible-assistant")

agent = Agent(
    edge=getstream.Edge(),  # low latency edge for stream clients
    agent_user=agent_user,  # the user object for the agent
    instructions="You are silently helping the user pass this interview. See @interview_coach.md",
    llm=gemini.Realtime(), # Gemini processes screen/audio in real-time
    # No TTS or STT here if the assistant is truly "invisible" and only provides text back-channel
)
```

### 4. Load and Convert Audio to 16kHz PCM Data

This workflow demonstrates how to load an audio file (e.g., MP3), resample it, and convert it into `PcmData` at a target sample rate, which is a common prerequisite for many audio processors and STT/TTS models.

```python
import os
import av
import numpy as np
from getstream.video.rtc.track_util import PcmData, AudioFormat

audio_file_path = os.path.join(os.path.dirname(__file__), 'test_assets/mia.mp3')
print('Load mia.mp3 and convert to 16kHz PCM data')
container = av.open(audio_file_path)
audio_stream = container.streams.audio[0]
original_sample_rate = audio_stream.sample_rate
target_rate = 16000
resampler = None
if original_sample_rate != target_rate:
    resampler = av.AudioResampler(format=AudioFormat.S16, layout='mono', rate=target_rate)
samples = []
for frame in container.decode(audio_stream):
    if resampler:
        frame = resampler.resample(frame)[0]
    frame_array = frame.to_ndarray()
    if len(frame_array.shape) > 1:
        frame_array = np.mean(frame_array, axis=0) # Convert stereo to mono if needed
    samples.append(frame_array)
samples = np.concatenate(samples)
samples = samples.astype(np.int16)
container.close()
pcm = PcmData(samples=samples, sample_rate=target_rate, format=AudioFormat.S16)
# `pcm` now contains the 16kHz mono audio data
```

### 5. Verify PCM -> mulaw -> PCM Round-Trip Maintains Signal Quality

This example shows how to test the fidelity of audio conversion (PCM to mulaw and back to PCM), which is important for voice-based agents interacting with telephony systems like Twilio.

```python
import numpy as np
from getstream.video.rtc.track_util import PcmData, AudioFormat
from vision_agents.plugins.twilio.audio import pcm_to_mulaw, mulaw_to_pcm, TWILIO_SAMPLE_RATE

print('Verify PCM -> mulaw -> PCM round-trip maintains signal quality.')
duration = 0.1
t = np.linspace(0, duration, int(TWILIO_SAMPLE_RATE * duration), dtype=np.float32)
sine_wave = (np.sin(2 * np.pi * 440 * t) * 16000).astype(np.int16)
original_pcm = PcmData(samples=sine_wave, sample_rate=TWILIO_SAMPLE_RATE, channels=1, format=AudioFormat.S16)
mulaw = pcm_to_mulaw(original_pcm)
recovered_pcm = mulaw_to_pcm(mulaw)
error = np.abs(original_pcm.samples.astype(np.int32) - recovered_pcm.samples.astype(np.int32))
max_error = np.max(error)
mean_error = np.mean(error)
assert max_error < 2000, f'Max error too high: {max_error}'
assert mean_error < 500, f'Mean error too high: {mean_error}'
```

### 6. Test Creating and Retrieving Twilio Calls

This example demonstrates interacting with the `twilio.TwilioCallRegistry` to manage inbound/outbound calls, a key feature for agents interacting over phone lines.

```python
from vision_agents.plugins import twilio
from vision_agents.plugins.twilio.types import CallWebhookInput

print('Test creating and retrieving calls.')
registry = twilio.TwilioCallRegistry()
webhook_data = CallWebhookInput(CallSid='CA123', AccountSid='AC123', CallStatus='ringing', Direction='inbound', From='+123', Caller='+123', To='+456', Called='+456')
call = registry.create('CA123', webhook_data=webhook_data)
assert call.call_sid == 'CA123'
assert call.from_number == '+123'
retrieved = registry.get('CA123')
assert retrieved is call
```

## How-To Guides Index

The following detailed guides offer step-by-step instructions for specific tasks:

### By Use Case
-   **Create And Get**: [How To: Create And Get](create and get/create-and-get.md) - Advanced
-   **Encode Symmetry**: [How To: Encode Symmetry](encode symmetry/encode-symmetry.md) - Intermediate
-   **Mia Audio 16Khz**: [How To: Mia Audio 16Khz](mia audio 16khz/mia-audio-16khz.md) - Advanced
-   **Mia Audio Preserves Speech Characteristics**: [How To: Mia Audio Preserves Speech Characteristics](mia audio preserves speech characteristics/mia-audio-preserves-speech-characteristics.md) - Intermediate
-   **Moondream Processor**: [How To: Moondream Processor](moondream processor/moondream-processor.md) - Advanced
-   **No Clipping Distortion**: [How To: No Clipping Distortion](no clipping distortion/no-clipping-distortion.md) - Intermediate
-   **Parse File Outside Base Dir**: [How To: Parse File Outside Base Dir](parse file outside base dir/parse-file-outside-base-dir.md) - Advanced
-   **Pcm To Mulaw And Back**: [How To: Pcm To Mulaw And Back](pcm to mulaw and back/pcm-to-mulaw-and-back.md) - Advanced
-   **Pcm To Mulaw Resamples**: [How To: Pcm To Mulaw Resamples](pcm to mulaw resamples/pcm-to-mulaw-resamples.md) - Intermediate
-   **Roundtrip Known Values**: [How To: Roundtrip Known Values](roundtrip known values/roundtrip-known-values.md) - Intermediate
-   **Roundtrip Preserves Waveform**: [How To: Roundtrip Preserves Waveform](roundtrip preserves waveform/roundtrip-preserves-waveform.md) - Advanced
-   **Snr Acceptable**: [How To: Snr Acceptable](snr acceptable/snr-acceptable.md) - Advanced

### By Difficulty Level
-   **Intermediate** (5 guides)
-   **Advanced** (7 guides)

## Configuration Patterns

The codebase includes a variety of configuration files, totaling 93 files and 1349 settings. While no specific patterns were detected across all configurations, common types include:

*   **`toml` (package_configuration)**: Used in `pyproject.toml` files across the main project and various plugins for dependency management and project metadata.
*   **`yaml` (general_configuration, ci_cd_configuration, docker_configuration)**: Found in `.github/workflows`, `.coderabbit.yaml`, `docker-compose.yml`, and Helm charts for CI/CD, general project settings, and container orchestration.
*   **`env` (environment_configuration)**: `.env.example` files provide templates for environment variables required for running examples and plugins.
*   **`ini` (general_configuration)**: `pytest.ini` for pytest configurations.
*   **`json` (general_configuration)**: Example Grafana dashboards (`stream-agents.json`).
*   **`dockerfile` (docker_configuration)**: `Dockerfile` and `Dockerfile.gpu` for building container images.

Detailed configuration analysis is available in `references/config_patterns/`.

## Project Documentation

The project includes extensive documentation to guide usage and development:

*   **Overview**: `README.md`, `CLAUDE.md` (coding guidelines), `DEVELOPMENT.md` (development setup), `PRODUCTION.md` (deployment guidelines), `SECURITY.md` (security policy).
*   **Examples**: Numerous `instructions.md` and `README.md` files within the `examples/` directory detail specific agent implementations (e.g., simple agent, golf coach, phone/RAG, security camera).
*   **Other**: A variety of specialized documentation files exist, such as `agents-core/README.md`, `docs/ai/instructions/ai-events-example.md`, `plugins/*/README.md`, etc.
*   **AI-specific Guides**: `ai-events-example.md` (event system), `ai-llm.md` (LLM plugin dev), `ai-plugin.md` (general plugin dev), `ai-realtime-llm.md` (real-time LLM dev), `ai-stt.md` (STT plugin dev), `ai-tts.md` (TTS plugin dev), `ai-turn-detector.md` (turn detector dev), `ai-utils.md` (audio utilities), `ai-tests.md` (testing), `ai-update.md` (plugin updates), `PROTOBUF_GENERATION.md` (protobuf event generation).
*   **Agent Persona & Guides**: `elon.md` (Elon Musk persona), `golf_coach.md` (golf coach persona), `instructions.md` (general instructions), `inworld-audio-guide.md` (Inworld audio markup), `moderation.md` (Stream moderation), `needle_in_haystack.md` (custom instruction), `sonic3-info.md` (Cartesia Sonic 3 speech customization), `chat.md` (Stream Chat API), `feeds.md` (Stream Feeds API), `video.md` (Stream Video API).

All project documentation can be found in `references/documentation/`.

## Development & Contributing Guidelines

Vision-Agents is a Python monorepo managed with `uv` workspaces. Key aspects for development:

*   **Installation**: Use `uv venv`, `uv sync`, and `pre-commit install`.
*   **Running Examples**: Use `uv run <path-to-example> run` with optional `--video-track-override` or `serve` for HTTP server mode.
*   **Testing**: Pytest is used. Run unit tests with `uv run py.test -m "not integration"` and integration tests with `uv run py.test -m "integration"` (requires `.env` secrets). Avoid mocking.
*   **Code Style**: Adhere to PEP 8, Google-style docstrings, no `from __future__ import annotations`, specific exception handling, and `logger.exception()` for errors with tracebacks. Imports are ordered, and private attributes use leading underscores.
*   **Typing**: Use type annotations everywhere, preferring modern syntax (`X | Y`, `dict[str, T]`).
*   **Async Patterns**: Follow async-first lifecycle methods, use `asyncio` for concurrency, and ensure proper resource cleanup.
*   **Plugin Development**:
    *   **Structure**: Plugins reside in `plugins/` with a specific folder structure (e.g., `plugins/elevenlabs/vision_agents/plugins/elevenlabs/`).
    *   **Guidelines**: Refer to `ai-plugin.md` for general plugin development, and `ai-tts.md`, `ai-stt.md`, `ai-llm.md`, `ai-realtime-llm.md`, `ai-turn-detector.md` for specific plugin types.
    *   **Audio Management**: Always use `PcmData` for passing audio within the SDK and between plugins.
    *   **Event System**: Utilize the `EventManager` as detailed in `ai-events-example.md` for asynchronous communication between components.
*   **Observability**: Integrate tracing with OpenTelemetry and Jaeger, and metrics with Prometheus.
*   **Profiling**: Use the built-in `Profiler` class to analyze agent performance.
*   **Warmup**: Implement `vision_agents.core.warmup.Warmable` for efficient, shared loading of external models and resources in plugins.

For a detailed guide, see `DEVELOPMENT.md` and `CLAUDE.md`.

## Available References

This skill includes detailed reference documentation organized into the following directories:

*   **Dependencies**: `references/dependencies/` - Dependency graph and analysis
*   **Patterns**: `references/patterns/` - Detected design patterns
*   **Examples**: `references/test_examples/` - Usage examples from tests
*   **Configuration**: `references/config_patterns/` - Configuration patterns
*   **Documentation**: `references/documentation/` - Project documentation