# App V1 LineB Voiceprint Verifier Upgrade

Date: 2026-05-11

## Status

LineB voiceprint is no longer only a menu/status placeholder.

Implemented:

- `src/parrot/brain/lineb_voiceprint.py`
  - private manifest loader
  - owner centroid verification by speaker embedding
  - cosine similarity accept/reject/uncertain decisions
  - optional SpeechBrain ECAPA audio extractor/enrollment path
  - optional Resemblyzer fast extractor path for quick local checks
  - no raw audio or embedding data in Git
- `src/parrot/brain/lineb_audio_guard.py`
  - accepts `speaker_similarity`, `voiceprint_decision`, `speaker_label`, `voiceprint_profile_id`
  - suppresses non-owner speaker input with `speaker_rejected`
  - allows verified owner barge-in over recent TTS overlap
  - keeps agent echo suppression as the highest-priority route when echo score/hash matches recent TTS
- HTTP/RPC/facade
  - `/api/app/lineb/mic-input` accepts voiceprint fields
  - `/api/app/lineb/voiceprint/verify-embedding` verifies precomputed private embeddings
  - LiveKit RPC `classifyLineBMicInput` accepts voiceprint fields
  - LiveKit RPC `verifyLineBVoiceprintEmbedding` added
  - LineProfile preview/evaluation now reports real voiceprint runtime state instead of only `enabled=true`
- App/Ner reaction
  - fixed `lineb_listening_uncertain` and `lineb_listening_noise` trigger names so they match the model manifest
  - Unity Ner DTO now carries voiceprint decision/profile/similarity fields
- Audio route correctness
  - Unity route names `wired_headset`, `bluetooth_sco`, `bluetooth_a2dp`, and `earpiece` are now treated as isolated/low-risk routes.
- Bugfix review follow-up
  - LineProfile provider/profile/threshold fields are now passed into voiceprint runtime status, so menu switching does not silently fall back to env/default provider.
  - Recent TTS echo classification now uses ASR text similarity as an additional echo signal, so external speaker recapture can become `agent_echo` even without an acoustic embedding score.
  - Voiceprint runtime can now be enabled by the selected LineProfile itself; it no longer requires `PARROT_LINEB_VOICEPRINT_ENABLED=1` when RoomSetting has selected an enabled profile.
  - HTTP/RPC debug classification can override manifest/provider/threshold together, avoiding a half-effective override when the active profile has voiceprint disabled.
  - Explicit `voiceprint_decision=owner_user` is no longer trusted as proof of owner identity. Owner acceptance must come from similarity + manifest/threshold verification.
  - `PARROT_ACTIVE_LINE_PROFILE_ID` is now accepted as an alias for `PARROT_LINE_PROFILE`, matching the RemoteSSH config pack and RoomSetting naming.

## Required Private Setup

Still required on ECS/private storage:

- Install optional runtime: `parrotcarriers[voiceprint]`
  - Optional quick check backend: `parrotcarriers[voiceprint_fast]`
- Record owner enrollment audio.
- Generate owner centroid and embedding index.
- Set:
  - `PARROT_LINEB_VOICEPRINT_ENABLED=1`
  - `PARROT_LINEB_VOICEPRINT_PROVIDER=speechbrain_ecapa`
  - `PARROT_LINEB_VOICEPRINT_PROFILE_ID=user_owner_tokyo_v1`
  - `PARROT_LINEB_VOICEPRINT_MANIFEST=/secure/ecs/parrot/voiceprint/user_owner_tokyo_v1/voiceprint_manifest.json`

Private data locations:

- Owner voiceprint audio:
  - `/secure/ecs/parrot/voiceprint/user_owner_tokyo_v1/audio/enroll/`
  - `/secure/ecs/parrot/voiceprint/user_owner_tokyo_v1/audio/negative/`
- Owner voiceprint features:
  - `/secure/ecs/parrot/voiceprint/user_owner_tokyo_v1/features/`
- Ner/TTS private voice samples:
  - `/secure/ecs/parrot/voices/ner/audio/`
  - `/secure/ecs/parrot/voices/ner/voice_manifest.json`

## Design Decision

Voiceprint is treated as owner-speaker verification, not generic ASR diarization.

Google STT speaker diarization can separate speakers inside one clip, but it
does not provide a persistent "is this the owner?" gate. LineB therefore uses
a separate speaker embedding verifier and feeds the result into the existing
ASR/TTS/echo turn classifier.

## Validation

Local tests:

- `pytest tests/test_brain/test_lineb_voiceprint.py tests/test_brain/test_app_first_version_facade.py tests/test_brain/test_app_v1_monitor.py tests/test_brain/test_lineb_model_reaction.py tests/test_unity/test_app_v1_meta_ui_static.py`
  - 56 passed

## Remaining Device Work

- Real enrollment with user-provided voice clips.
- Tune accept/reject thresholds on phone mic.
- Confirm phone speaker route:
  - recent TTS echo -> `agent_echo`
  - owner speech -> `user_turn`
  - other speaker / TV / background speech -> `speaker_rejected` or `uncertain`
- Decide later whether owner barge-in should interrupt TTS or only queue the next turn.
