"""Calendar Trigger — loads Google Calendar events and enriches DSG.

Trigger mode: STARTUP + PERIODIC (every 15 min)

Three-tier reminder system:
  1. DIGEST  — On startup / morning: "Today's schedule overview"
  2. PREP    — 30 min before event: "Upcoming: X in 30 min, you might need Y"
  3. IMMINENT — 5 min before event: "X starting in 5 min!"

Quiet hours: No reminders between 23:00–07:00 unless event is marked urgent.
Cooldown: Same event won't be re-notified at the same tier within the tier window.

Google Calendar access:
  - Via Nanobot with Google Calendar MCP tool (requires user's Google OAuth)
  - Nanobot fetches events, extracts structured data, returns via result_channel
  - CalendarTrigger processes results and fills DSG

Flow:
  1. On startup: fetch today's events → digest notification
  2. Every 15 min: re-fetch and check for approaching events
  3. On calendar_result event from Nanobot: process and update DSG
"""

from __future__ import annotations

import logging
import time
from datetime import datetime, timezone
from typing import Any

from parrot.dsg.l2b_types import (
    ConfirmationStatus,
    EdgeKind,
    NodeKind,
    Salience,
    SemanticEdge,
    SemanticNode,
)
from parrot.dsg.triggers.base import BaseTrigger, TriggerKind, TriggerResult

logger = logging.getLogger(__name__)

QUIET_HOUR_START = 23
QUIET_HOUR_END = 7

TIER_DIGEST = "digest"
TIER_PREP = "prep"
TIER_IMMINENT = "imminent"

PREP_MINUTES = 30
IMMINENT_MINUTES = 5


class CalendarTrigger(BaseTrigger):
    """Fetches calendar events and enriches DSG with time-sensitive context."""

    name = "calendar_trigger"
    kinds = [TriggerKind.STARTUP, TriggerKind.PERIODIC]
    interval_seconds = 900.0  # 15 minutes

    def __init__(self, graph):
        super().__init__(graph)
        self._known_event_ids: set[str] = set()
        self._events_cache: list[dict] = []
        self._notified: dict[str, set[str]] = {}  # event_id → set of tiers already sent

    async def on_startup(self) -> TriggerResult | None:
        return await self._fetch_and_process(is_startup=True)

    async def on_tick(self) -> TriggerResult | None:
        self._check_approaching_events()
        return await self._fetch_and_process(is_startup=False)

    async def on_event(self, event: dict[str, Any]) -> TriggerResult | None:
        if event.get("type") == "calendar_result":
            raw = event.get("result", "")
            return await self._parse_and_process(raw)
        return None

    # ━━━ Core pipeline ━━━

    async def _fetch_and_process(self, *, is_startup: bool) -> TriggerResult | None:
        """Dispatch a Nanobot task to fetch today's calendar events."""
        task_id = await self._dispatch_nanobot(
            task_type="calendar_fetch",
            params={
                "query": "Fetch today's Google Calendar events for the user",
                "instructions": (
                    "Use the Google Calendar API or MCP tool to get today's events. "
                    "For each event, extract: id, title, start_time (ISO 8601), "
                    "end_time, location, description, and any mentioned objects "
                    "or items to prepare. Also flag if the event is marked "
                    "as urgent/important. "
                    "Return as JSON array: "
                    '[{"id": str, "title": str, "start_time": str, '
                    '"end_time": str, "location": str, "description": str, '
                    '"objects": [str], "is_urgent": bool}]'
                ),
                "result_channel": "calendar_result",
            },
        )

        if task_id:
            summary = "Calendar fetch dispatched"
            if is_startup:
                summary += " (startup digest)"
            return TriggerResult(
                trigger_name=self.name,
                summary=summary,
                dispatch_to_nanobot=True,
                nanobot_task={"task_id": task_id, "type": "calendar_fetch"},
            )
        return None

    async def _parse_and_process(self, raw_result: str) -> TriggerResult | None:
        """Parse Nanobot result (may be JSON string) and process events."""
        import json
        try:
            if isinstance(raw_result, str):
                data = json.loads(raw_result)
            else:
                data = raw_result

            if isinstance(data, list):
                events = data
            elif isinstance(data, dict) and "events" in data:
                events = data["events"]
            else:
                events = []
        except (json.JSONDecodeError, TypeError):
            logger.debug("calendar: failed to parse result: %s", str(raw_result)[:100])
            events = []

        if events:
            return await self._process_calendar_data(events)
        return None

    async def _process_calendar_data(self, events: list[dict]) -> TriggerResult | None:
        """Process calendar events — fill DSG and generate tiered notifications."""
        if not events:
            return None

        self._events_cache = events
        now = time.time()
        nodes_affected = []
        digest_parts = []
        prep_parts = []
        imminent_parts = []

        for ev in events:
            ev_id = ev.get("id", f"ev_{hash(ev.get('title', ''))}")
            title = ev.get("title", "")
            start_time_str = ev.get("start_time", "")
            objects_mentioned = ev.get("objects", [])
            is_urgent = ev.get("is_urgent", False)

            start_ts = self._parse_time(start_time_str)

            event_node = SemanticNode(
                uuid=f"cal_{ev_id}",
                kind=NodeKind.EVENT,
                label=title or f"Event {ev_id}",
                description=f"{start_time_str} — {title}",
                tags=["calendar", "upcoming"],
                attention=0.7,
                salience=Salience.ACTIVE,
                confirmation=ConfirmationStatus.CONFIRMED,
            )
            self._graph.upsert_node(event_node)
            self._graph.assign_node_to_current_episode(event_node.uuid)
            nodes_affected.append(event_node.uuid)

            for obj_name in objects_mentioned:
                await self._link_object_to_event(obj_name, event_node)

            if ev_id not in self._notified:
                self._notified[ev_id] = set()

            time_display = self._format_time(start_time_str)
            obj_hint = ""
            if objects_mentioned:
                obj_hint = f" (prepare: {', '.join(objects_mentioned[:3])})"

            if TIER_DIGEST not in self._notified[ev_id]:
                digest_parts.append(f"{time_display}: {title}{obj_hint}")
                self._notified[ev_id].add(TIER_DIGEST)

            if start_ts:
                minutes_until = (start_ts - now) / 60.0

                if (0 < minutes_until <= PREP_MINUTES
                        and TIER_PREP not in self._notified[ev_id]):
                    prep_parts.append(
                        f"{title} in ~{int(minutes_until)} min{obj_hint}"
                    )
                    self._notified[ev_id].add(TIER_PREP)
                    event_node.attention = min(1.0, event_node.attention + 0.2)

                if (0 < minutes_until <= IMMINENT_MINUTES
                        and TIER_IMMINENT not in self._notified[ev_id]):
                    imminent_parts.append(f"{title} starting NOW!")
                    self._notified[ev_id].add(TIER_IMMINENT)
                    event_node.attention = 1.0
                    event_node.salience = Salience.ALERT

        notification = self._build_notification(
            digest_parts, prep_parts, imminent_parts, is_urgent=any(
                ev.get("is_urgent") for ev in events
            ),
        )

        result = TriggerResult(
            trigger_name=self.name,
            summary=f"Processed {len(events)} calendar events",
            nodes_affected=nodes_affected,
            notify_gemini=bool(notification),
            notification_text=notification,
        )

        if notification:
            await self._notify_brain(notification)

        return result

    def _check_approaching_events(self) -> None:
        """Promote attention on events getting closer (called on every tick)."""
        now = time.time()
        for ev in self._events_cache:
            ev_id = ev.get("id", "")
            start_ts = self._parse_time(ev.get("start_time", ""))
            if not start_ts:
                continue

            node = self._graph.get_node(f"cal_{ev_id}")
            if not node:
                continue

            minutes_until = (start_ts - now) / 60.0
            if minutes_until <= 0:
                node.salience = Salience.BACKGROUND
                node.attention = max(0.1, node.attention - 0.1)
            elif minutes_until <= IMMINENT_MINUTES:
                node.attention = 1.0
                node.salience = Salience.ALERT
            elif minutes_until <= PREP_MINUTES:
                node.attention = max(node.attention, 0.8)
                node.salience = Salience.ACTIVE

    # ━━━ Notification builder ━━━

    def _build_notification(
        self,
        digest: list[str],
        prep: list[str],
        imminent: list[str],
        *,
        is_urgent: bool,
    ) -> str:
        if self._is_quiet_hour() and not is_urgent:
            return ""

        parts = []

        if imminent:
            parts.append(
                "[Reminder — NOW]\n" + "\n".join(f"  ⚡ {p}" for p in imminent)
            )

        if prep:
            parts.append(
                "[Coming up soon]\n" + "\n".join(f"  🔔 {p}" for p in prep)
            )

        if digest and not prep and not imminent:
            parts.append(
                "[Today's schedule]\n" + "\n".join(f"  📅 {p}" for p in digest)
            )

        if not parts:
            return ""

        return (
            "Gently tell the user about their schedule. "
            "Don't just list items — weave them into natural conversation. "
            "Be helpful but not pushy.\n\n" + "\n\n".join(parts)
        )

    # ━━━ Helpers ━━━

    def _is_quiet_hour(self) -> bool:
        hour = datetime.now().hour
        if QUIET_HOUR_START <= hour or hour < QUIET_HOUR_END:
            return True
        return False

    @staticmethod
    def _parse_time(time_str: str) -> float | None:
        """Parse ISO 8601 time string to Unix timestamp."""
        if not time_str:
            return None
        for fmt in (
            "%Y-%m-%dT%H:%M:%S%z",
            "%Y-%m-%dT%H:%M:%S",
            "%Y-%m-%dT%H:%M%z",
            "%Y-%m-%dT%H:%M",
            "%H:%M",
        ):
            try:
                dt = datetime.strptime(time_str, fmt)
                if dt.tzinfo is None:
                    dt = dt.replace(tzinfo=timezone.utc)
                if dt.year == 1900:
                    now = datetime.now(timezone.utc)
                    dt = dt.replace(year=now.year, month=now.month, day=now.day)
                return dt.timestamp()
            except ValueError:
                continue
        return None

    @staticmethod
    def _format_time(time_str: str) -> str:
        """Format time string for human display."""
        if not time_str:
            return "TBD"
        for fmt in (
            "%Y-%m-%dT%H:%M:%S%z",
            "%Y-%m-%dT%H:%M:%S",
            "%Y-%m-%dT%H:%M%z",
            "%Y-%m-%dT%H:%M",
        ):
            try:
                dt = datetime.strptime(time_str, fmt)
                return dt.strftime("%H:%M")
            except ValueError:
                continue
        return time_str

    async def _link_object_to_event(self, obj_name: str, event_node: SemanticNode) -> None:
        """Search L2-B and Graphiti for an object mentioned in a calendar event."""
        existing = self._graph.get_node_by_label(obj_name)
        if existing:
            existing.attention = max(existing.attention, 0.6)
            existing.salience = Salience.ACTIVE
            existing.tags = list(set(existing.tags + ["calendar_relevant"]))
            self._graph.connect(
                event_node.uuid,
                existing.uuid,
                SemanticEdge(kind=EdgeKind.ASSOCIATED_WITH, source="calendar"),
            )
            return

        try:
            from parrot.memory.graphiti_client import PARTITIONS, get_graphiti

            g = await get_graphiti()
            results = await g.search(
                query=f"object: {obj_name}",
                group_ids=[PARTITIONS.SCENE],
                num_results=3,
            )
            if results:
                fact = getattr(results[0], "fact", None) or getattr(results[0], "text", "")
                obj_node = SemanticNode(
                    uuid=getattr(results[0], "uuid", f"cal_obj_{obj_name}"),
                    kind=NodeKind.OBJECT,
                    label=obj_name,
                    graphiti_uuid=getattr(results[0], "uuid", ""),
                    known_facts=[fact] if fact else [],
                    attention=0.6,
                    salience=Salience.ACTIVE,
                    tags=["calendar_relevant"],
                    confirmation=ConfirmationStatus.EXPECTED,
                )
                self._graph.upsert_node(obj_node)
                self._graph.connect(
                    event_node.uuid,
                    obj_node.uuid,
                    SemanticEdge(kind=EdgeKind.ASSOCIATED_WITH, source="calendar"),
                )
        except Exception:
            logger.debug("calendar: Graphiti lookup failed for '%s'", obj_name)
