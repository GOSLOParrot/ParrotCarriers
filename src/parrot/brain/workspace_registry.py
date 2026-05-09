"""2DWorkspace registry for the app menu and in-session workspace switching.

The existing ``Scene`` block describes the perception baseline
(``ar_handheld`` / ``desktop_webcam``). A 2D workspace is different: it is the
in-app desk/surface the user opens while the same LiveKit room remains alive.

reason: Reusing ``active_scene_id`` for this would make a canvas switch look
like an AR environment switch and would encourage callers to rebuild the room.
``global/active_workspace_id`` gives the menu a stable business surface while
the LiveKit session lifecycle stays under ``RoomManager`` / lifecycle control.
"""

from __future__ import annotations

import json
import logging
import os
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from parrot.brain.preset_loader import DEFAULT_WORKSPACE_ID, PresetApplyResult, get_preset_loader

logger = logging.getLogger(__name__)


WORKSPACES_DIR_ENV = "PARROT_WORKSPACES_DIR"
WORKSPACE_SCHEMA_VERSION = 1


@dataclass(frozen=True)
class WorkspaceSummary:
    """Menu-facing description of one app 2D workspace.

    The ``metadata`` dict may later carry IntentWorkspace reference ids for
    documents, calendars, or staged reports shown on this surface. This
    registry does not fetch those payloads; IntentWorkspace remains the owner
    of heavy intent resources and their eviction lifecycle.
    """

    workspace_id: str
    display_name: str
    description: str = ""
    layout_kind: str = "2d_workspace"
    is_fallback: bool = False
    metadata: dict[str, Any] = field(default_factory=dict)

    def as_json(self) -> dict[str, Any]:
        return {
            "schema_version": WORKSPACE_SCHEMA_VERSION,
            "workspace_id": self.workspace_id,
            "display_name": self.display_name,
            "description": self.description,
            "layout_kind": self.layout_kind,
            "is_fallback": self.is_fallback,
            "metadata": dict(self.metadata),
        }

    @classmethod
    def from_json(cls, raw: dict[str, Any]) -> "WorkspaceSummary":
        if not isinstance(raw, dict):
            raise ValueError("workspace payload must be a JSON object")
        workspace_id = str(raw.get("workspace_id", "")).strip()
        if not workspace_id:
            raise ValueError("workspace_id is required")
        return cls(
            workspace_id=workspace_id,
            display_name=str(raw.get("display_name") or workspace_id),
            description=str(raw.get("description") or ""),
            layout_kind=str(raw.get("layout_kind") or "2d_workspace"),
            is_fallback=bool(raw.get("is_fallback", False)),
            metadata=dict(raw.get("metadata") or {}),
        )


@dataclass(frozen=True)
class WorkspaceApplyResult:
    """Outcome of applying a 2D workspace selection."""

    requested_workspace_id: str
    active_workspace_id: str
    applied_keys: tuple[str, ...]
    success: bool = True
    fallback_used: bool = False
    errors: tuple[str, ...] = ()

    @classmethod
    def from_preset_result(
        cls,
        *,
        requested_workspace_id: str,
        active_workspace_id: str,
        fallback_used: bool,
        result: PresetApplyResult,
        extra_errors: tuple[str, ...] = (),
    ) -> "WorkspaceApplyResult":
        return cls(
            requested_workspace_id=requested_workspace_id,
            active_workspace_id=active_workspace_id,
            applied_keys=result.applied_keys,
            success=result.success and not extra_errors,
            fallback_used=fallback_used,
            errors=tuple(extra_errors) + result.errors,
        )


_BUILTIN_WORKSPACES: tuple[WorkspaceSummary, ...] = (
    WorkspaceSummary(
        workspace_id=DEFAULT_WORKSPACE_ID,
        display_name="Mansion Hub",
        description="Default calm hub used when no specific desk is selected.",
        is_fallback=True,
        metadata={"theme_skin": "manor"},
    ),
    WorkspaceSummary(
        workspace_id="workdesk",
        display_name="Workdesk",
        description="General task desk for notes, tools, and lightweight planning.",
        metadata={"surface": "desk"},
    ),
    WorkspaceSummary(
        workspace_id="report_desk",
        display_name="Report Desk",
        description="Focused reading and report review workspace.",
        metadata={"surface": "document"},
    ),
)


class WorkspaceRegistry:
    """Disk-backed 2DWorkspace list/apply/save/fallback boundary."""

    def __init__(self, search_paths: list[Path] | None = None) -> None:
        if search_paths is None:
            search_paths = self._default_search_paths()
        self._search_paths = [Path(p) for p in search_paths]

    @staticmethod
    def _default_search_paths() -> list[Path]:
        out: list[Path] = []
        env = os.environ.get(WORKSPACES_DIR_ENV, "").strip()
        if env:
            out.extend(Path(p) for p in env.split(os.pathsep) if p)
        out.append(Path("data") / "workspaces")
        return out

    def list_workspaces(self) -> tuple[WorkspaceSummary, ...]:
        by_id = {w.workspace_id: w for w in _BUILTIN_WORKSPACES}
        for d in self._search_paths:
            try:
                if not d.is_dir():
                    continue
                for f in sorted(d.glob("*.json")):
                    try:
                        summary = WorkspaceSummary.from_json(
                            json.loads(f.read_text(encoding="utf-8"))
                        )
                    except (OSError, ValueError, json.JSONDecodeError):
                        logger.exception("workspace_registry: failed to parse %s", f)
                        continue
                    by_id[summary.workspace_id] = summary
            except OSError:
                continue
        return tuple(sorted(by_id.values(), key=lambda w: (not w.is_fallback, w.workspace_id)))

    def fallback_workspace(self) -> WorkspaceSummary:
        for w in self.list_workspaces():
            if w.workspace_id == DEFAULT_WORKSPACE_ID:
                return w
        return _BUILTIN_WORKSPACES[0]

    def get(self, workspace_id: str) -> WorkspaceSummary | None:
        safe = str(workspace_id or "").strip()
        if not safe:
            return None
        for w in self.list_workspaces():
            if w.workspace_id == safe:
                return w
        return None

    def apply_workspace(self, workspace_id: str) -> WorkspaceApplyResult:
        requested = str(workspace_id or "").strip()
        summary = self.get(requested)
        fallback_used = False
        errors: tuple[str, ...] = ()
        if summary is None:
            summary = self.fallback_workspace()
            fallback_used = True
            errors = (f"unknown workspace_id: {requested or '<empty>'}",)

        result = get_preset_loader().apply_workspace_id(
            summary.workspace_id,
            preset_id="workspace_only",
        )
        return WorkspaceApplyResult.from_preset_result(
            requested_workspace_id=requested,
            active_workspace_id=summary.workspace_id,
            fallback_used=fallback_used,
            result=result,
            extra_errors=errors,
        )

    def save_workspace(self, workspace: WorkspaceSummary) -> Path:
        target_dir = self._writable_dir()
        target_dir.mkdir(parents=True, exist_ok=True)
        path = target_dir / f"{workspace.workspace_id}.json"
        path.write_text(
            json.dumps(workspace.as_json(), ensure_ascii=False, indent=2),
            encoding="utf-8",
        )
        return path

    def _writable_dir(self) -> Path:
        for d in self._search_paths:
            try:
                d.mkdir(parents=True, exist_ok=True)
                return d
            except OSError:
                continue
        return Path("data") / "workspaces"


_registry: WorkspaceRegistry | None = None


def get_workspace_registry() -> WorkspaceRegistry:
    global _registry
    if _registry is None:
        _registry = WorkspaceRegistry()
    return _registry


def set_workspace_registry_for_test(registry: WorkspaceRegistry | None) -> None:
    global _registry
    _registry = registry


__all__ = [
    "WORKSPACES_DIR_ENV",
    "WORKSPACE_SCHEMA_VERSION",
    "WorkspaceApplyResult",
    "WorkspaceRegistry",
    "WorkspaceSummary",
    "get_workspace_registry",
    "set_workspace_registry_for_test",
]
