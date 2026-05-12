"""Thin client SDK for the Castle ECS Orchestrator.

Used by:

* The Web monitor / app-monitor server (read-only ``status()``).
* Brain self-checks ("am I drift-vs-runtime_config?") — Brain may
  call this to know whether a forced reconnect is pending.
* CI smoke tests for Phase 2 ↔ 3 wiring.

Design choices:

* Uses :mod:`httpx` if installed; otherwise falls back to
  :mod:`urllib.request`. ``httpx`` is already a transitive dep via
  livekit-agents, so on production it's always available; the urllib
  fallback keeps unit tests cheap.
* Returns parsed JSON ``dict[str, Any]``; raises
  :class:`OrchestratorError` on non-200 responses with the parsed
  error detail when available.
* Reads ``PARROT_ORCH_URL`` (default ``http://127.0.0.1:7890``) and
  ``PARROT_ORCH_SECRET`` for default config so callers don't have to
  thread these through.
"""

from __future__ import annotations

import json
import logging
import os
from dataclasses import dataclass
from typing import Any

logger = logging.getLogger(__name__)


class OrchestratorError(RuntimeError):
    def __init__(self, message: str, *, status_code: int | None = None, detail: Any | None = None):
        super().__init__(message)
        self.status_code = status_code
        self.detail = detail


@dataclass
class OrchestratorClient:
    base_url: str | None = None
    secret: str | None = None
    timeout_s: float = 5.0

    def _resolve_base_url(self) -> str:
        return (self.base_url or os.getenv("PARROT_ORCH_URL", "http://127.0.0.1:7890")).rstrip("/")

    def _resolve_secret(self) -> str:
        return self.secret or os.getenv("PARROT_ORCH_SECRET", "")

    def _headers(self) -> dict[str, str]:
        headers = {"Content-Type": "application/json", "Accept": "application/json"}
        secret = self._resolve_secret()
        if secret:
            headers["Authorization"] = f"Bearer {secret}"
        return headers

    def health(self) -> dict[str, Any]:
        return self._request("GET", "/health")

    def status(self) -> dict[str, Any]:
        return self._request("GET", "/status")

    def set_active_line(
        self,
        line_id: str,
        *,
        line_profile_id: str | None = None,
        notes: str = "",
        force_reconnect: bool = False,
    ) -> dict[str, Any]:
        return self._request(
            "POST",
            "/set_active_line",
            body={
                "line_id": line_id,
                "line_profile_id": line_profile_id,
                "notes": notes,
                "force_reconnect": force_reconnect,
            },
        )

    def apply_room_profile(
        self,
        room_profile_id: str,
        *,
        line_id: str | None = None,
        line_profile_id: str | None = None,
        force_reconnect: bool = False,
    ) -> dict[str, Any]:
        return self._request(
            "POST",
            "/apply_room_profile",
            body={
                "room_profile_id": room_profile_id,
                "line_id": line_id,
                "line_profile_id": line_profile_id,
                "force_reconnect": force_reconnect,
            },
        )

    def force_unity_reconnect(
        self, *, reason: str = "manual", request_id: str | None = None
    ) -> dict[str, Any]:
        return self._request(
            "POST",
            "/force_unity_reconnect",
            body={"reason": reason, "request_id": request_id},
        )

    def restart_component(
        self,
        component: str,
        *,
        reason: str = "orchestrator_restart",
        wait_for_online: bool = True,
        timeout_s: float = 30.0,
    ) -> dict[str, Any]:
        return self._request(
            "POST",
            "/restart_component",
            body={
                "component": component,
                "reason": reason,
                "wait_for_online": wait_for_online,
                "timeout_s": timeout_s,
            },
        )

    def clear_runtime_config(self) -> dict[str, Any]:
        return self._request("POST", "/clear_runtime_config")

    def rolling_restart_brain(
        self, *, reason: str = "rolling_tier1", drain_timeout_s: float = 45.0
    ) -> dict[str, Any]:
        return self._request(
            "POST",
            "/rolling_restart_brain",
            body={"reason": reason, "drain_timeout_s": drain_timeout_s},
        )

    def _request(
        self,
        method: str,
        path: str,
        *,
        body: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        url = self._resolve_base_url() + path
        try:
            import httpx  # type: ignore
        except Exception:  # noqa: BLE001
            return _request_via_urllib(
                url=url,
                method=method,
                headers=self._headers(),
                body=body,
                timeout_s=self.timeout_s,
            )
        try:
            with httpx.Client(timeout=self.timeout_s) as client:
                response = client.request(
                    method,
                    url,
                    headers=self._headers(),
                    json=body if body is not None else None,
                )
        except Exception as exc:  # noqa: BLE001
            raise OrchestratorError(
                f"orchestrator {method} {path} transport failed: {exc!r}"
            ) from exc
        return _parse_response(response.status_code, response.text, method, path)


def _request_via_urllib(
    *,
    url: str,
    method: str,
    headers: dict[str, str],
    body: dict[str, Any] | None,
    timeout_s: float,
) -> dict[str, Any]:
    """Fallback path used when httpx isn't installed."""
    import urllib.error
    import urllib.request

    payload: bytes | None = None
    if body is not None:
        payload = json.dumps(body).encode("utf-8")
    request = urllib.request.Request(url=url, method=method, data=payload, headers=headers)
    try:
        with urllib.request.urlopen(request, timeout=timeout_s) as response:
            text = response.read().decode("utf-8")
            return _parse_response(response.status, text, method, url)
    except urllib.error.HTTPError as exc:
        return _parse_response(exc.code, exc.read().decode("utf-8", errors="replace"), method, url)
    except Exception as exc:  # noqa: BLE001
        raise OrchestratorError(
            f"orchestrator {method} {url} transport failed: {exc!r}"
        ) from exc


def _parse_response(
    status_code: int,
    text: str,
    method: str,
    path: str,
) -> dict[str, Any]:
    try:
        data = json.loads(text) if text else {}
    except Exception:
        data = {"raw": text}
    if 200 <= status_code < 300:
        return data if isinstance(data, dict) else {"value": data}
    raise OrchestratorError(
        f"orchestrator {method} {path} returned {status_code}",
        status_code=status_code,
        detail=data,
    )


__all__ = [
    "OrchestratorClient",
    "OrchestratorError",
]
