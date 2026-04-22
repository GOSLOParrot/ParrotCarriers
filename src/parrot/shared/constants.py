"""Redis channel names and other shared constants.

These are CANDIDATE names — will be validated against actual code in Phase 1.
Source of truth: bus_v4.md v4.2 § Redis 通道命名规范
"""

# Redis Pub/Sub channels
CH_EVENTS_FIREHOSE = "parrot.events.firehose"
CH_BRAIN_DECISIONS = "parrot.brain.decisions"
CH_BRAIN_FOCUS = "parrot.brain.focus_commands"
CH_DSG_EVENTS = "parrot.dsg.events"
CH_DSG_SCENE_UPDATE = "parrot.dsg.scene_update"
CH_DSG_SENTINEL = "parrot.dsg.sentinel.evidence"
CH_SCHEDULER_COMMANDS = "parrot.scheduler.commands"
CH_SCHEDULER_RESULTS = "parrot.scheduler.results"
CH_NANOBOT_RESULTS = "parrot.nanobot.results"
CH_SCHEDULER_TO_BRAIN = "parrot.scheduler.to_brain"
CH_EXTERNAL_COMMANDS = "parrot.external.commands"
CH_BEHAVIOR_MODE = "parrot.brain.behavior_mode"

# Trigger-specific Pub/Sub channel for routed results
CH_TRIGGER_RESULTS = "parrot.trigger.results"

# Redis Streams
STREAM_NANOBOT_DISPATCH = "parrot.nanobot.dispatch"

# L0 Raw Event Stream — single source of truth for all state changes.
# See sprint0_preflight.md §1.3 and shared/event_log.py. Sprint 0 locks the
# schema only; Sprint 1 dispatcher will produce events into this stream.
STREAM_EVENT_LOG = "parrot.events.log"

# Redis Hash keys
HASH_MODULES = "parrot.modules"
HASH_HEARTBEAT = "parrot.heartbeat"
HASH_GOSLO_MODE = "parrot.goslo.mode"

# Blackboard keys (Redis Hash namespace)
BB_PARROT_STATE = "parrot_state"
BB_SCENE_CONTEXT = "scene_context"
BB_RESOURCE_LOCKS = "resource_locks"

# LiveKit Room
ROOM_MAIN = "parrot-main"
