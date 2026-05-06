"""DSG Trigger system — background enrichment and proactive context filling.

Triggers are async routines that run in the background, filling the L2-B graph
with contextual information from various sources. They operate independently
of Gemini's conscious tool calls.

Trigger taxonomy (how they fire):
  1. STARTUP: runs once when Brain Agent starts (e.g., load today's calendar)
  2. PERIODIC: runs on a timer (e.g., check for new calendar events every 15 min)
  3. EVENT-DRIVEN: fires in response to a DSG/Redis event (e.g., new object found)
  4. ON-DEMAND: fired by Gemini via tool or by Scheduler command

Legacy triggers (Phase 4):
  - CalendarTrigger: STARTUP + PERIODIC — three-tier Google Calendar reminders
  - SSOTEnrichmentTrigger: EVENT-DRIVEN — enriches new objects from Obsidian/Graphiti
  - SceneContextTrigger: STARTUP + EVENT-DRIVEN — searches similar past scenes
  - MessageNotificationTrigger: PERIODIC + EVENT-DRIVEN — Gmail important alerts

DSG-TRIGGER-V2 new triggers (2026-05-06):
  - SceneSwitchTrigger: ON_DEMAND — set_scene → freeze authority bucket + snapshot
  - IntentEventBoundaryTrigger: EVENT_DRIVEN — tool / idle → IntentEvent boundary
  - RoleplayModeTrigger: ON_DEMAND — register / clear ROLEPLAY_TEMP bucket
  - GosloCuriosityTrigger: EVENT_DRIVEN — attention threshold + unknown
  - IdleArchiveTrigger: PERIODIC — nanobot idle → SCAN_AND_ARCHIVE

The default registration ``ALL_TRIGGERS`` lists legacy + new together;
deployments can opt out via ``TriggerRunner.register(...)`` selectively.
"""

from parrot.dsg.triggers.base import BaseTrigger, TriggerKind
from parrot.dsg.triggers.calendar_trigger import CalendarTrigger
from parrot.dsg.triggers.goslo_curiosity_trigger import GosloCuriosityTrigger
from parrot.dsg.triggers.idle_archive_trigger import IdleArchiveTrigger
from parrot.dsg.triggers.intent_event_boundary_trigger import IntentEventBoundaryTrigger
from parrot.dsg.triggers.message_trigger import MessageNotificationTrigger
from parrot.dsg.triggers.roleplay_mode_trigger import RoleplayModeTrigger
from parrot.dsg.triggers.scene_context_trigger import SceneContextTrigger
from parrot.dsg.triggers.scene_switch_trigger import SceneSwitchTrigger
from parrot.dsg.triggers.ssot_enrichment_trigger import SSOTEnrichmentTrigger

ALL_TRIGGERS: list[type[BaseTrigger]] = [
    # Legacy (Phase 4)
    CalendarTrigger,
    SSOTEnrichmentTrigger,
    SceneContextTrigger,
    MessageNotificationTrigger,
    # DSG-TRIGGER-V2 (2026-05-06)
    SceneSwitchTrigger,
    IntentEventBoundaryTrigger,
    RoleplayModeTrigger,
    GosloCuriosityTrigger,
    IdleArchiveTrigger,
]

__all__ = [
    "ALL_TRIGGERS",
    "BaseTrigger",
    "CalendarTrigger",
    "GosloCuriosityTrigger",
    "IdleArchiveTrigger",
    "IntentEventBoundaryTrigger",
    "MessageNotificationTrigger",
    "RoleplayModeTrigger",
    "SSOTEnrichmentTrigger",
    "SceneContextTrigger",
    "SceneSwitchTrigger",
    "TriggerKind",
]
