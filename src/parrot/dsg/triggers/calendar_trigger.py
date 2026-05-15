"""Google Calendar trigger.

This trigger owns the read side of the Google Calendar true connection:

    Scheduler -> Nanobot -> Google Workspace MCP -> calendar_result
        -> CalendarTrigger -> L1.5 Pool -> GOOGLE_CALENDAR bucket -> L2-B EVENT nodes

Calendar event bytes are small enough to live as L2-B metadata. IntentWorkspace
is intentionally not used for the read path; it is reserved for later edit
drafts, confirmation flows, rich reports, or other heavy/temporary payloads.
"""

from __future__ import annotations

import hashlib
import json
import logging
import time
from datetime import datetime, timezone
from typing import Any

from parrot.dsg.ingest.base import Observation, ObservationSource
from parrot.dsg.l2b_types import ConfirmationStatus, NodeKind, Salience, SemanticNode
from parrot.dsg.triggers.base import BaseTrigger, TriggerKind, TriggerOutcome

logger = logging.getLogger(__name__)

QUIET_HOUR_START = 23
QUIET_HOUR_END = 7

TIER_DIGEST = "digest"
TIER_PREP = "prep"
TIER_IMMINENT = "imminent"
CALENDAR_INACTIVE_STATES = frozenset({"cancelled", "canceled", "deleted"})

PREP_MINUTES = 30
IMMINENT_MINUTES = 5


class CalendarTrigger(BaseTrigger):
    """Fetch Google Calendar events and publish them through L1.5."""

    name = "calendar_trigger"
    kinds = [TriggerKind.STARTUP, TriggerKind.PERIODIC, TriggerKind.EVENT_DRIVEN]
    interval_seconds = 900.0  # 15 minutes

    def __init__(self, graph):
        super().__init__(graph)
        self._events_cache: list[dict[str, Any]] = []
        # event_key -> tiers already notified. The key is calendar_id:event_id.
        self._notified: dict[str, set[str]] = {}

    async def on_startup(self) -> TriggerOutcome | None:
        return await self._fetch_and_process(is_startup=True)

    async def on_tick(self) -> TriggerOutcome | None:
        self._check_approaching_events()
        return await self._fetch_and_process(is_startup=False)

    async def on_event(self, event: dict[str, Any]) -> TriggerOutcome | None:
        if event.get("type") != "calendar_result":
            return None
        raw = event.get("result", "")
        return await self._parse_and_process(raw)

    async def _fetch_and_process(self, *, is_startup: bool) -> TriggerOutcome | None:
        """Dispatch a Nanobot task to fetch today's Google Calendar events."""
        params = {
            "query": "Fetch today's Google Calendar events for the user",
            "instructions": (
                "Use the Google Calendar API or MCP tool to get today's events. "
                "For each event, extract: id, title, start_time (ISO 8601), "
                "end_time, location, description, html_link, etag, updated, "
                "status, iCalUID, and any mentioned objects or items to prepare. "
                "Also flag if the event is marked urgent/important. Return as "
                "JSON only: "
                '[{"id": str, "title": str, "start_time": str, "end_time": str, '
                '"location": str, "description": str, "objects": [str], '
                '"is_urgent": bool, "html_link": str, "etag": str, '
                '"updated": str, "status": str, "iCalUID": str}]'
            ),
            "result_channel": "calendar_result",
        }
        task_id = await self._dispatch_nanobot(
            task_type="calendar_fetch",
            params=params,
        )
        if not task_id:
            return None

        summary = "Calendar fetch dispatched"
        if is_startup:
            summary += " (startup digest)"
        return TriggerOutcome(
            trigger_name=self.name,
            summary=summary,
            # _dispatch_nanobot already sent the task. Keep this false so the
            # runner does not try to dispatch a second legacy task.
            dispatch_to_nanobot=False,
            nanobot_task={
                "task_id": task_id,
                "task_type": "calendar_fetch",
                "params": params,
            },
        )

    async def _parse_and_process(self, raw_result: Any) -> TriggerOutcome | None:
        """Parse Nanobot result and convert events into Observations."""
        data = _loads_jsonish(raw_result)
        events = _extract_event_list(data)
        normalized = [self._normalize_event(ev) for ev in events if isinstance(ev, dict)]
        normalized = [ev for ev in normalized if ev]
        if not normalized:
            return None
        return await self._process_calendar_data(normalized)

    async def _process_calendar_data(
        self,
        events: list[dict[str, Any]],
    ) -> TriggerOutcome | None:
        """Build Observation objects for L1.5 instead of mutating L2-B directly."""
        self._events_cache = events
        observations: list[Observation] = []
        digest_parts: list[str] = []
        prep_parts: list[str] = []
        imminent_parts: list[str] = []
        now = time.time()

        for ev in events:
            event_key = _event_key(ev)
            start_ts = self._parse_time(str(ev.get("start_time", "") or ""))
            end_ts = self._parse_time(str(ev.get("end_time", "") or ""))
            lifecycle_state = _calendar_lifecycle_state(ev)

            observations.append(self._event_to_observation(ev, start_ts, end_ts))
            if lifecycle_state in CALENDAR_INACTIVE_STATES:
                # Deleted/cancelled rows from Google incremental sync are still
                # important provenance, but they must not generate user-facing
                # reminders or near-term prep notifications.
                continue

            self._notified.setdefault(event_key, set())
            time_display = self._format_time(str(ev.get("start_time", "") or ""))
            title = str(ev.get("title", "") or event_key)
            objects_mentioned = list(ev.get("objects", []) or [])
            obj_hint = ""
            if objects_mentioned:
                obj_hint = f" (prepare: {', '.join(map(str, objects_mentioned[:3]))})"

            if TIER_DIGEST not in self._notified[event_key]:
                digest_parts.append(f"{time_display}: {title}{obj_hint}")
                self._notified[event_key].add(TIER_DIGEST)

            if start_ts:
                minutes_until = (start_ts - now) / 60.0
                if 0 < minutes_until <= PREP_MINUTES and TIER_PREP not in self._notified[event_key]:
                    prep_parts.append(f"{title} in ~{int(minutes_until)} min{obj_hint}")
                    self._notified[event_key].add(TIER_PREP)
                if (
                    0 < minutes_until <= IMMINENT_MINUTES
                    and TIER_IMMINENT not in self._notified[event_key]
                ):
                    imminent_parts.append(f"{title} starting now")
                    self._notified[event_key].add(TIER_IMMINENT)

        notification = self._build_notification(
            digest_parts,
            prep_parts,
            imminent_parts,
            is_urgent=any(bool(ev.get("is_urgent")) for ev in events),
        )

        return TriggerOutcome(
            trigger_name=self.name,
            summary=f"Processed {len(events)} calendar events into L1.5",
            commit_observations=tuple(observations),
            notify_gemini=bool(notification),
            notification_text=notification,
        )

    def _event_to_observation(
        self,
        ev: dict[str, Any],
        start_ts: float | None,
        end_ts: float | None,
    ) -> Observation:
        """Convert a normalized calendar event into a GOOGLE_CALENDAR Observation."""
        title = str(ev.get("title", "") or "Untitled calendar event")[:128]
        start_time = str(ev.get("start_time", "") or "")
        end_time = str(ev.get("end_time", "") or "")
        location = str(ev.get("location", "") or "")
        description = str(ev.get("description", "") or "")
        lifecycle_state = _calendar_lifecycle_state(ev)
        is_inactive = lifecycle_state in CALENDAR_INACTIVE_STATES

        detail_parts = [p for p in (start_time, end_time, location, description) if p]
        obs_description = " | ".join(detail_parts)[:400]
        if is_inactive:
            # WEB-014.15 policy: keep a historical tombstone EVENT instead of
            # deleting L2-B state. Google incremental sync may only provide an
            # id/status for deleted events, so preserving provider identity is
            # safer than evicting and losing the reconciliation anchor.
            obs_description = (
                f"Google Calendar event is {lifecycle_state}; retained as a "
                "historical tombstone."
                + (f" {obs_description}" if obs_description else "")
            )[:400]
        begin = start_ts or time.time()

        return Observation(
            source=ObservationSource.GOOGLE_CALENDAR,
            label=title,
            kind=NodeKind.EVENT,
            description=obs_description,
            confidence=1.0,
            confirmation=(
                ConfirmationStatus.GHOST
                if is_inactive
                else ConfirmationStatus.CONFIRMED
            ),
            observed_at=begin,
            time_span=(begin, end_ts),
            meta={
                "calendar_id": str(ev.get("calendar_id", "primary") or "primary"),
                "calendar_event_id": str(ev.get("id", "") or ""),
                "ical_uid": str(ev.get("ical_uid", "") or ""),
                "etag": str(ev.get("etag", "") or ""),
                "html_link": str(ev.get("html_link", "") or ""),
                "status": str(ev.get("status", "") or ""),
                "start_time": start_time,
                "end_time": end_time,
                "timezone": str(ev.get("timezone", "") or ""),
                "location": location,
                "updated": str(ev.get("updated", "") or ""),
                "objects": list(ev.get("objects", []) or []),
                "is_urgent": bool(ev.get("is_urgent")),
                "calendar_lifecycle": lifecycle_state,
                "is_tombstone": is_inactive,
                "tombstone_policy": "historical_event" if is_inactive else "",
            },
        )

    def _check_approaching_events(self) -> None:
        """Promote attention on existing L2-B calendar nodes as time approaches."""
        now = time.time()
        for ev in self._events_cache:
            if _calendar_lifecycle_state(ev) in CALENDAR_INACTIVE_STATES:
                continue
            start_ts = self._parse_time(str(ev.get("start_time", "") or ""))
            if not start_ts:
                continue
            node = self._find_calendar_node(ev)
            if node is None:
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

    def _find_calendar_node(self, ev: dict[str, Any]) -> SemanticNode | None:
        """Find a committed calendar node by its Google event identity."""
        target_key = _event_key(ev)
        for node in self._graph.all_nodes():
            if node.source != ObservationSource.GOOGLE_CALENDAR.value:
                continue
            node_key = _event_key(node.source_meta or {})
            if node_key == target_key:
                return node
        return None

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

        parts: list[str] = []
        if imminent:
            parts.append("[Reminder now]\n" + "\n".join(f"  - {p}" for p in imminent))
        if prep:
            parts.append("[Coming up soon]\n" + "\n".join(f"  - {p}" for p in prep))
        if digest and not prep and not imminent:
            parts.append("[Today's schedule]\n" + "\n".join(f"  - {p}" for p in digest))

        if not parts:
            return ""
        return (
            "Gently tell the user about their schedule. Be helpful but not pushy.\n\n"
            + "\n\n".join(parts)
        )

    def _normalize_event(self, ev: dict[str, Any]) -> dict[str, Any]:
        """Normalize Google API and Nanobot-friendly event shapes."""
        start_raw = ev.get("start_time") or ev.get("start") or {}
        end_raw = ev.get("end_time") or ev.get("end") or {}
        start_time, start_tz = _extract_google_time(start_raw)
        end_time, end_tz = _extract_google_time(end_raw)

        title = ev.get("title") or ev.get("summary") or ev.get("label") or ""
        event_id = (
            ev.get("id")
            or ev.get("event_id")
            or ev.get("google_event_id")
            or _stable_event_id(title, start_time, end_time, ev.get("location", ""))
        )

        objects = ev.get("objects", [])
        if isinstance(objects, str):
            objects = [p.strip() for p in objects.split(",") if p.strip()]
        if not isinstance(objects, list):
            objects = []

        return {
            "id": str(event_id),
            "calendar_id": str(ev.get("calendar_id", "primary") or "primary"),
            "title": str(title or "Untitled calendar event"),
            "start_time": str(start_time),
            "end_time": str(end_time),
            "timezone": str(ev.get("timezone") or start_tz or end_tz or ""),
            "location": str(ev.get("location", "") or ""),
            "description": str(ev.get("description", "") or ""),
            "objects": [str(item) for item in objects[:16]],
            "is_urgent": _coerce_bool(ev.get("is_urgent") or ev.get("urgent")),
            "html_link": str(ev.get("html_link") or ev.get("htmlLink") or ""),
            "etag": str(ev.get("etag", "") or ""),
            "updated": str(ev.get("updated", "") or ""),
            "status": str(ev.get("status", "") or ""),
            "ical_uid": str(ev.get("ical_uid") or ev.get("iCalUID") or ""),
        }

    @staticmethod
    def _is_quiet_hour() -> bool:
        hour = datetime.now().hour
        return QUIET_HOUR_START <= hour or hour < QUIET_HOUR_END

    @staticmethod
    def _parse_time(time_str: str) -> float | None:
        """Parse ISO-like Google time strings into Unix timestamps."""
        if not time_str:
            return None
        cleaned = time_str.strip()
        try:
            # Google uses RFC3339 and may emit a trailing Z for UTC.
            dt = datetime.fromisoformat(cleaned.replace("Z", "+00:00"))
            if dt.tzinfo is None:
                dt = dt.replace(tzinfo=datetime.now().astimezone().tzinfo)
            return dt.timestamp()
        except ValueError:
            pass

        for fmt in ("%Y-%m-%d", "%H:%M"):
            try:
                dt = datetime.strptime(cleaned, fmt)
                if dt.year == 1900:
                    today = datetime.now().astimezone()
                    dt = dt.replace(year=today.year, month=today.month, day=today.day)
                dt = dt.replace(tzinfo=datetime.now().astimezone().tzinfo)
                return dt.timestamp()
            except ValueError:
                continue
        return None

    @staticmethod
    def _format_time(time_str: str) -> str:
        if not time_str:
            return "TBD"
        ts = CalendarTrigger._parse_time(time_str)
        if ts is None:
            return time_str
        return datetime.fromtimestamp(ts, tz=timezone.utc).astimezone().strftime("%H:%M")


def _loads_jsonish(raw: Any) -> Any:
    """Load JSON returned by Nanobot, tolerating fenced JSON blocks."""
    if not isinstance(raw, str):
        return raw
    text = raw.strip()
    if text.startswith("```"):
        lines = text.splitlines()
        if len(lines) >= 3:
            text = "\n".join(lines[1:-1]).strip()
    try:
        return json.loads(text)
    except (json.JSONDecodeError, TypeError):
        logger.debug("calendar: failed to parse result: %s", text[:160])
        return []


def _extract_event_list(data: Any) -> list[Any]:
    if isinstance(data, list):
        return data
    if isinstance(data, dict):
        for key in ("events", "items", "calendar_events"):
            value = data.get(key)
            if isinstance(value, list):
                return value
    return []


def _extract_google_time(value: Any) -> tuple[str, str]:
    """Return (time_value, timezone) from Google API or normalized strings."""
    if isinstance(value, dict):
        time_value = value.get("dateTime") or value.get("date") or ""
        tz = value.get("timeZone") or ""
        return str(time_value), str(tz)
    return str(value or ""), ""


def _stable_event_id(*parts: Any) -> str:
    """Create a deterministic fallback id when Nanobot omits Google's id."""
    h = hashlib.sha1()
    for part in parts:
        h.update(str(part or "").encode("utf-8", "replace"))
        h.update(b"\0")
    return f"generated_{h.hexdigest()[:16]}"


def _event_key(ev: dict[str, Any]) -> str:
    calendar_id = str(ev.get("calendar_id", "primary") or "primary")
    event_id = str(ev.get("id") or ev.get("calendar_event_id") or "")
    return f"{calendar_id}:{event_id}"


def _calendar_lifecycle_state(ev: dict[str, Any]) -> str:
    """Normalize provider status into the small lifecycle vocabulary L2-B uses."""
    status = str(ev.get("status") or "").strip().lower()
    if status in CALENDAR_INACTIVE_STATES:
        return "cancelled" if status == "canceled" else status
    return "active"


def _coerce_bool(value: Any) -> bool:
    if isinstance(value, bool):
        return value
    if isinstance(value, str):
        return value.strip().lower() in {"1", "true", "yes", "urgent", "important"}
    return bool(value)


__all__ = ["CalendarTrigger"]
