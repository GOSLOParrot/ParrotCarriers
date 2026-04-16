"""Message Notification Trigger — summarizes important incoming messages.

Trigger mode: PERIODIC (every 10 min) + EVENT_DRIVEN (on push notification)

Supported sources (via Nanobot MCP tools):
  - Gmail: fetches unread important/starred emails
  - (Future) Telegram, WeChat, etc.

Flow:
  1. Periodic: Nanobot checks Gmail for unread important messages
  2. Results come back as structured data via CH_TRIGGER_RESULTS
  3. Trigger creates L2-B EVENT nodes for important messages
  4. Notifies Gemini only for messages that pass the importance filter

Importance filter (to avoid being annoying):
  - Skip: marketing, newsletters, automated notifications (unless urgent)
  - Include: messages from known contacts, replies to user's messages,
    messages with keywords matching current scene/task context
  - Quiet hours: same as CalendarTrigger (23:00–07:00)
  - Cooldown: won't re-notify about the same message within 1 hour

Notification style:
  - Brief natural-language summary, not a raw list
  - Group by sender/thread when possible
  - Let Gemini decide whether to interrupt or wait for a pause
"""

from __future__ import annotations

import logging
import time
from datetime import datetime
from typing import Any

from parrot.dsg.l2b_types import (
    ConfirmationStatus,
    NodeKind,
    Salience,
    SemanticNode,
)
from parrot.dsg.triggers.base import BaseTrigger, TriggerKind, TriggerResult

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
        self._notified_ids: dict[str, float] = {}  # msg_id → timestamp of last notification

    async def on_startup(self) -> TriggerResult | None:
        return await self._fetch_messages()

    async def on_tick(self) -> TriggerResult | None:
        self._cleanup_cooldowns()
        return await self._fetch_messages()

    async def on_event(self, event: dict[str, Any]) -> TriggerResult | None:
        if event.get("type") == "message_result":
            raw = event.get("result", "")
            return await self._parse_and_process(raw)

        if event.get("type") == "message_push":
            return await self._handle_push(event)
        return None

    async def _fetch_messages(self) -> TriggerResult | None:
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
            return TriggerResult(
                trigger_name=self.name,
                summary=f"Message check dispatched (task={task_id})",
                dispatch_to_nanobot=True,
            )
        return None

    async def _parse_and_process(self, raw_result: str) -> TriggerResult | None:
        """Parse Nanobot message check result."""
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

    async def _handle_push(self, event: dict) -> TriggerResult | None:
        """Handle a real-time push notification about a new message."""
        msg = {
            "id": event.get("message_id", f"push_{int(time.time())}"),
            "sender": event.get("sender", ""),
            "subject": event.get("subject", ""),
            "snippet": event.get("snippet", ""),
            "importance": event.get("importance", "normal"),
        }
        return await self._process_messages([msg])

    async def _process_messages(self, messages: list[dict]) -> TriggerResult | None:
        """Filter and notify about important messages."""
        now = time.time()
        important = []
        nodes_affected = []

        for msg in messages:
            msg_id = msg.get("id", "")
            importance = msg.get("importance", "normal")

            if not self._passes_filter(msg_id, importance, now):
                continue

            sender = msg.get("sender", "Unknown")
            subject = msg.get("subject", "(no subject)")
            snippet = msg.get("snippet", "")

            msg_node = SemanticNode(
                uuid=f"msg_{msg_id}",
                kind=NodeKind.EVENT,
                label=f"Message: {subject[:40]}",
                description=f"From {sender}: {subject} — {snippet[:60]}",
                tags=["message", "unread", importance],
                attention=0.8 if importance == "high" else 0.5,
                salience=Salience.ACTIVE if importance == "high" else Salience.BACKGROUND,
                confirmation=ConfirmationStatus.CONFIRMED,
            )
            self._graph.upsert_node(msg_node)
            nodes_affected.append(msg_node.uuid)

            important.append({
                "sender": sender,
                "subject": subject,
                "snippet": snippet[:80],
                "importance": importance,
            })
            self._notified_ids[msg_id] = now

        if not important:
            return None

        notification = self._build_notification(important)
        if not notification:
            return None

        await self._notify_brain(notification)

        return TriggerResult(
            trigger_name=self.name,
            summary=f"Found {len(important)} important messages",
            nodes_affected=nodes_affected,
            notify_gemini=True,
            notification_text=notification,
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
        """Build natural-language message summary for Gemini."""
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
                    parts.append(f"    → {m['snippet']}")

        if normal:
            parts.append(f"[{len(normal)} other message(s)]")
            for m in normal[:3]:
                parts.append(f"  From {m['sender']}: {m['subject']}")

        return (
            "The user has new messages. Mention them naturally when "
            "there's a pause in conversation — don't interrupt. "
            "For high-importance messages, you can gently bring them up sooner.\n\n"
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
            k for k, v in self._notified_ids.items()
            if now - v > MESSAGE_COOLDOWN_SECONDS * 2
        ]
        for k in expired:
            del self._notified_ids[k]
