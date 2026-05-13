"""Message notification trigger for Gmail / Google Workspace.

The trigger can run periodically or react to pushed ``message_result`` /
``message_push`` events. Important messages are converted into
``Observation(source=GOOGLE_MESSAGE)`` and returned through
``TriggerOutcome.commit_observations`` so the normal L1.5 Pool / Ingest path
owns all L2-B writes.
"""

from __future__ import annotations

import logging
import time
from datetime import datetime
from typing import Any

from parrot.dsg.ingest.base import Observation, ObservationSource
from parrot.dsg.l2b_types import ConfirmationStatus, NodeKind
from parrot.dsg.triggers.base import BaseTrigger, TriggerKind, TriggerOutcome

logger = logging.getLogger(__name__)

QUIET_HOUR_START = 23
QUIET_HOUR_END = 7
MESSAGE_COOLDOWN_SECONDS = 3600  # 1 hour per message


class MessageNotificationTrigger(BaseTrigger):
    """Checks for important messages and notifies Gemini."""

    name = "message_notification"
    kinds = [TriggerKind.PERIODIC, TriggerKind.EVENT_DRIVEN]
    interval_seconds = 600.0  # 10 minutes

    def __init__(self, graph):
        super().__init__(graph)
        self._notified_ids: dict[str, float] = {}

    async def on_startup(self) -> TriggerOutcome | None:
        return await self._fetch_messages()

    async def on_tick(self) -> TriggerOutcome | None:
        self._cleanup_cooldowns()
        return await self._fetch_messages()

    async def on_event(self, event: dict[str, Any]) -> TriggerOutcome | None:
        if event.get("type") == "message_result":
            raw = event.get("result", "")
            return await self._parse_and_process(raw)

        if event.get("type") == "message_push":
            return await self._handle_push(event)
        return None

    async def _fetch_messages(self) -> TriggerOutcome | None:
        """Dispatch Nanobot to check Gmail for unread important messages."""
        task_id = await self._dispatch_nanobot(
            task_type="message_check",
            params={
                "query": "Check Gmail for unread important messages",
                "instructions": (
                    "Use the Gmail API or MCP tool to fetch unread messages "
                    "that are: starred, marked important, or from known contacts. "
                    "Skip marketing emails and automated notifications. "
                    "For each message extract: id, sender, subject, snippet "
                    "(first 100 chars), timestamp, is_reply (bool), "
                    "importance ('high'/'normal'/'low'). "
                    "Return as JSON array: "
                    '[{"id": str, "sender": str, "subject": str, '
                    '"snippet": str, "timestamp": str, '
                    '"is_reply": bool, "importance": str}]'
                ),
                "result_channel": "message_result",
            },
        )

        if task_id:
            return TriggerOutcome(
                trigger_name=self.name,
                summary=f"Message check dispatched (task={task_id})",
                dispatch_to_nanobot=True,
            )
        return None

    async def _parse_and_process(self, raw_result: str) -> TriggerOutcome | None:
        """Parse a Nanobot message-check result."""
        import json

        try:
            if isinstance(raw_result, str):
                data = json.loads(raw_result)
            else:
                data = raw_result

            if isinstance(data, list):
                messages = data
            elif isinstance(data, dict) and "messages" in data:
                messages = data["messages"]
            else:
                messages = []
        except (json.JSONDecodeError, TypeError):
            messages = []

        if messages:
            return await self._process_messages(messages)
        return None

    async def _handle_push(self, event: dict) -> TriggerOutcome | None:
        """Handle a real-time push notification about a new message."""
        msg = {
            "id": event.get("message_id", f"push_{int(time.time())}"),
            "sender": event.get("sender", ""),
            "subject": event.get("subject", ""),
            "snippet": event.get("snippet", ""),
            "importance": event.get("importance", "normal"),
            "timestamp": event.get("timestamp", ""),
            "thread_id": event.get("thread_id", ""),
            "source": event.get("source", "gmail"),
        }
        return await self._process_messages([msg])

    async def _process_messages(self, messages: list[dict]) -> TriggerOutcome | None:
        """Filter messages and return L1.5 commit observations."""
        now = time.time()
        important: list[dict[str, Any]] = []
        observations: list[Observation] = []

        for msg in messages:
            msg_id = str(msg.get("id", "") or "")
            importance = str(msg.get("importance", "normal") or "normal")

            if not self._passes_filter(msg_id, importance, now):
                continue

            sender = str(msg.get("sender", "Unknown") or "Unknown")
            subject = str(msg.get("subject", "(no subject)") or "(no subject)")
            snippet = str(msg.get("snippet", "") or "")

            observations.append(self._message_to_observation(msg))
            important.append(
                {
                    "sender": sender,
                    "subject": subject,
                    "snippet": snippet[:80],
                    "importance": importance,
                }
            )
            if msg_id:
                self._notified_ids[msg_id] = now

        if not important:
            return None

        notification = self._build_notification(important)
        if not notification:
            return None

        await self._notify_brain(notification)

        return TriggerOutcome(
            trigger_name=self.name,
            summary=f"Found {len(important)} important messages",
            commit_observations=tuple(observations),
            notify_gemini=True,
            notification_text=notification,
        )

    @staticmethod
    def _message_to_observation(msg: dict[str, Any]) -> Observation:
        """Convert one filtered message into the canonical L1.5 ingest DTO."""
        msg_id = str(msg.get("id", "") or f"message_{int(time.time())}")
        sender = str(msg.get("sender", "Unknown") or "Unknown")
        subject = str(msg.get("subject", "(no subject)") or "(no subject)")
        snippet = str(msg.get("snippet", "") or "")
        importance = str(msg.get("importance", "normal") or "normal")
        label = f"Message: {subject[:40]}"
        description = f"From {sender}: {subject}"
        if snippet:
            description = f"{description} - {snippet[:80]}"
        return Observation(
            source=ObservationSource.GOOGLE_MESSAGE,
            label=label[:128],
            kind=NodeKind.EVENT,
            description=description[:400],
            confidence=1.0 if importance == "high" else 0.8,
            confirmation=ConfirmationStatus.CONFIRMED,
            meta={
                "message_id": msg_id,
                "thread_id": str(msg.get("thread_id", "") or ""),
                "sender": sender,
                "subject": subject,
                "snippet": snippet[:160],
                "timestamp": str(msg.get("timestamp", "") or ""),
                "is_reply": bool(msg.get("is_reply", False)),
                "importance": importance,
                "source": str(msg.get("source", "gmail") or "gmail"),
            },
        )

    def _passes_filter(self, msg_id: str, importance: str, now: float) -> bool:
        """Check if a message should trigger a notification."""
        if self._is_quiet_hour() and importance != "high":
            return False

        last_notified = self._notified_ids.get(msg_id)
        if last_notified and (now - last_notified) < MESSAGE_COOLDOWN_SECONDS:
            return False

        if importance == "low":
            return False

        return True

    def _build_notification(self, messages: list[dict]) -> str:
        """Build a natural-language message summary for Gemini."""
        if not messages:
            return ""

        high = [m for m in messages if m["importance"] == "high"]
        normal = [m for m in messages if m["importance"] != "high"]

        parts = []
        if high:
            parts.append("[Important messages]")
            for m in high:
                parts.append(f"  From {m['sender']}: {m['subject']}")
                if m["snippet"]:
                    parts.append(f"    -> {m['snippet']}")

        if normal:
            parts.append(f"[{len(normal)} other message(s)]")
            for m in normal[:3]:
                parts.append(f"  From {m['sender']}: {m['subject']}")

        return (
            "The user has new messages. Mention them naturally when "
            "there's a pause in conversation; don't interrupt. For "
            "high-importance messages, you can gently bring them up sooner.\n\n"
            + "\n".join(parts)
        )

    @staticmethod
    def _is_quiet_hour() -> bool:
        hour = datetime.now().hour
        return QUIET_HOUR_START <= hour or hour < QUIET_HOUR_END

    def _cleanup_cooldowns(self) -> None:
        """Remove expired cooldown entries to prevent memory growth."""
        now = time.time()
        expired = [
            key
            for key, timestamp in self._notified_ids.items()
            if now - timestamp > MESSAGE_COOLDOWN_SECONDS * 2
        ]
        for key in expired:
            del self._notified_ids[key]


__all__ = ["MessageNotificationTrigger"]
