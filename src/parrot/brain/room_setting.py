"""RoomSetting service for startup Room / RoomProfile selection.

This module is the business layer behind the startup ``SCENE`` button. It is
deliberately read/preview-first: the UI can list Rooms, build drafts, and see
capability conflicts before START applies anything to the Blackboard.
"""

from __future__ import annotations

import time
import uuid
import os
from dataclasses import asdict, dataclass, is_dataclass, replace
from typing import Any

from parrot.brain.line_status import LineSummary, list_lines
from parrot.brain.line_profile import evaluate_line_profile, get_line_profile_loader
from parrot.brain.model_manifest_registry import get_model_manifest_registry
from parrot.brain.menu_registry import MenuRegistrySnapshot, get_menu_registry
from parrot.brain.preset_loader import (
    DEFAULT_EXPERIENCE_MODE,
    DEFAULT_LINE_ID,
    DEFAULT_PRESET_ID,
    DEFAULT_SCENE_SKIN_ID,
    ReservedRoomProfileIdError,
    RoomProfile,
    get_preset_loader,
)


EXPERIENCE_MODES: tuple[dict[str, Any], ...] = (
    {
        "experience_mode": "ar_companion",
        "display_name": "AR Companion",
        "requires": ("ar.scene", "voice.pipeline"),
    },
    {
        "experience_mode": "2d_hall",
        "display_name": "2D Hall",
        "requires": ("workspace.2d",),
    },
    {
        "experience_mode": "room_only",
        "display_name": "Room Only",
        "requires": ("voice.pipeline",),
    },
)

THEME_SKINS: tuple[dict[str, Any], ...] = (
    {
        "skin_id": "manor",
        "display_name": "Mansion Paper",
    },
    {
        "skin_id": "goslo_default",
        "display_name": "GOSLO Classic",
    },
    {
        "skin_id": "ner_mochi_room_v0",
        "display_name": "Ner Mochi Room",
    },
    {
        "skin_id": "pirate",
        "display_name": "Pirate Prototype",
    },
)


@dataclass(frozen=True)
class CapabilityDecision:
    """One resolver result consumed by UI and backend action gates."""

    capability_id: str
    state: str
    reason: str
    source: str = ""
    fallback_action: str = ""

    def as_json(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class RoomCompatibilityReport:
    """Aggregated compatibility result for one RoomProfile draft.

    Phase 4.2 added the ``tier`` field: the maximum restart tier
    implied by this draft vs the currently running Brain. UI uses
    this to pick a single toast/confirm shape rather than
    hand-mapping each ``decisions[*]`` row.
    """

    state: str
    decisions: tuple[CapabilityDecision, ...]
    tier: int = 0
    tier_label: str = ""
    tier_summary: str = ""
    tier_summary_zh: str = ""
    tier_ui_action: str = ""

    def as_json(self) -> dict[str, Any]:
        return {
            "state": self.state,
            "decisions": [d.as_json() for d in self.decisions],
            "tier": self.tier,
            "tier_label": self.tier_label,
            "tier_summary": self.tier_summary,
            "tier_summary_zh": self.tier_summary_zh,
            "tier_ui_action": self.tier_ui_action,
        }


@dataclass(frozen=True)
class RoomSettingSnapshot:
    """Complete startup RoomSetting read model."""

    generated_at: float
    rooms: tuple[dict[str, Any], ...]
    active_room: dict[str, Any]
    selectors: dict[str, Any]
    compatibility: dict[str, Any]

    def as_json(self) -> dict[str, Any]:
        return {
            "generated_at": self.generated_at,
            "rooms": list(self.rooms),
            "active_room": dict(self.active_room),
            "selectors": dict(self.selectors),
            "compatibility": dict(self.compatibility),
        }


class RoomSettingService:
    """Read/preview/apply service for startup RoomSetting."""

    def snapshot(self, room_profile_id: str | None = None) -> RoomSettingSnapshot:
        # TODO (audit Round 2 §E, 2026-05-11): ``rooms`` is a flat list of
        # JSON-serialised RoomProfiles with no per-room compatibility result.
        # Frontend has to call ``preview`` for each Room to discover which
        # ones are blocked / degraded. Cheaper for the UI if the snapshot
        # carries a thin ``compatibility_states: dict[room_id, state]`` map
        # alongside ``rooms``. Defer until a profiling pass shows the per-row
        # compatibility() call is actually slow (5 dim resolve x N rooms).
        loader = get_preset_loader()
        menu = get_menu_registry().list_blocks()
        active_id = (
            room_profile_id
            or _bb_str("global/active_room_profile_id", "")
            or DEFAULT_PRESET_ID
        )
        active_room = loader.load_room_profile(active_id)
        rooms = tuple(profile.as_json() for profile in loader.list_room_profiles())
        return RoomSettingSnapshot(
            generated_at=time.time(),
            rooms=rooms,
            active_room=active_room.as_json(),
            selectors=_selectors(menu),
            compatibility=self.compatibility(active_room).as_json(),
        )

    def preview(self, draft: dict[str, Any] | RoomProfile) -> dict[str, Any]:
        profile = draft if isinstance(draft, RoomProfile) else RoomProfile.from_json(draft)
        return {
            "room_profile": profile.as_json(),
            "compatibility": self.compatibility(profile).as_json(),
        }

    def new(
        self,
        *,
        base_id: str | None = None,
        display_name: str | None = None,
    ) -> dict[str, Any]:
        base = get_preset_loader().load_room_profile(base_id or DEFAULT_PRESET_ID)
        profile = replace(
            base,
            room_profile_id=f"room_{uuid.uuid4().hex[:8]}",
            display_name=(display_name or "New Room").strip() or "New Room",
        )
        return {
            "room_profile": profile.as_json(),
            "compatibility": self.compatibility(profile).as_json(),
        }

    def save(self, draft: dict[str, Any] | RoomProfile) -> dict[str, Any]:
        # FIX (2026-05-11 audit Round 4, Bug G): translate the typed
        # ``ReservedRoomProfileIdError`` from ``PresetLoader.save_room_profile``
        # into a structured ``status="error"`` response instead of raising up
        # to the LiveKit RPC layer (which would surface as a generic
        # IsError on the Unity side without the actionable reason). Returning
        # the offending id + reserved set lets the menu UI explain "pick a
        # different name" to the user.
        profile = draft if isinstance(draft, RoomProfile) else RoomProfile.from_json(draft)
        try:
            path = get_preset_loader().save_room_profile(profile)
        except ReservedRoomProfileIdError as exc:
            from parrot.brain.preset_loader import RESERVED_ROOM_PROFILE_IDS

            return {
                "status": "error",
                "reason": "reserved_room_profile_id",
                "room_profile_id": exc.profile_id,
                "reserved_ids": sorted(RESERVED_ROOM_PROFILE_IDS),
                "room_profile": profile.as_json(),
            }
        return {
            "status": "ok",
            "room_profile": profile.as_json(),
            "path": str(path),
            "compatibility": self.compatibility(profile).as_json(),
        }

    def apply(
        self,
        draft_or_id: dict[str, Any] | RoomProfile | str,
        *,
        experience_mode: str | None = None,
    ) -> dict[str, Any]:
        if isinstance(draft_or_id, RoomProfile):
            profile = draft_or_id
        elif isinstance(draft_or_id, dict):
            profile = RoomProfile.from_json(draft_or_id)
        else:
            profile = get_preset_loader().load_room_profile(str(draft_or_id or DEFAULT_PRESET_ID))
        if experience_mode:
            profile = profile.with_experience_mode(experience_mode)
        compatibility = self.compatibility(profile)
        if compatibility.state == "blocked":
            return {
                "success": False,
                "room_profile_id": profile.room_profile_id,
                "room_profile": profile.as_json(),
                "applied_keys": [],
                "errors": ["compatibility_blocked"],
                "compatibility": compatibility.as_json(),
            }
        result = get_preset_loader().apply_room_profile(profile)
        return {
            "success": result.success,
            "room_profile_id": profile.room_profile_id,
            "room_profile": profile.as_json(),
            "applied_keys": list(result.applied_keys),
            "errors": list(result.errors),
            "compatibility": compatibility.as_json(),
        }

    def compatibility(self, profile: RoomProfile) -> RoomCompatibilityReport:
        menu = get_menu_registry().list_blocks()
        decisions: list[CapabilityDecision] = []

        model_registry = get_model_manifest_registry()
        model_manifest = model_registry.get(profile.model_id)
        if model_manifest is None:
            decisions.append(
                CapabilityDecision(
                    "model.available",
                    "blocked",
                    "selected_model_not_registered",
                    source=f"model:{profile.model_id}",
                )
            )
        else:
            decisions.append(
                CapabilityDecision(
                    "model.available",
                    "enabled",
                    "model_registered",
                    source=f"model:{profile.model_id}",
                )
            )
            capabilities = set(model_manifest.declared_capability_ids)
            if model_manifest.parrot_reflex_enabled:
                decisions.append(
                    CapabilityDecision(
                        "model.reflex.parrot_reserved",
                        "enabled",
                        "reserved_parrot_capability_declared",
                        source=f"model:{profile.model_id}",
                    )
                )
            else:
                decisions.append(
                    CapabilityDecision(
                        "model.reflex.parrot_reserved",
                        "disabled",
                        "model_does_not_declare_reserved_parrot_reflex",
                        source=f"model:{profile.model_id}",
                    )
                )
            decisions.extend(_model_capability_decisions(profile.model_id, capabilities))
            if {"fly", "perch"}.issubset(capabilities):
                decisions.append(
                    CapabilityDecision(
                        "parrot.fly_to_hand",
                        "enabled",
                        "selected_model_declares_fly_and_perch",
                        source=f"model:{profile.model_id}",
                    )
                )
            else:
                decisions.append(
                    CapabilityDecision(
                        "parrot.fly_to_hand",
                        "disabled",
                        "selected_model_missing_fly_or_perch",
                        source=f"model:{profile.model_id}",
                        fallback_action="show_model_idle_animation",
                    )
                )

        scene_ids = {scene.scene_id for scene in menu.scenes}
        if profile.scene_profile_id not in scene_ids:
            decisions.append(
                CapabilityDecision(
                    "scene.available",
                    "blocked",
                    "selected_scene_not_registered",
                    source=f"scene:{profile.scene_profile_id}",
                )
            )
        else:
            decisions.append(
                CapabilityDecision(
                    "scene.available",
                    "enabled",
                    "scene_registered",
                    source=f"scene:{profile.scene_profile_id}",
                )
            )

        workspace_ids = {workspace.workspace_id for workspace in menu.workspaces}
        if profile.workspace_id not in workspace_ids:
            decisions.append(
                CapabilityDecision(
                    "workspace.available",
                    "degraded",
                    "workspace_will_fallback",
                    source=f"workspace:{profile.workspace_id}",
                    fallback_action="mansion_hub",
                )
            )
        else:
            decisions.append(
                CapabilityDecision(
                    "workspace.available",
                    "enabled",
                    "workspace_registered",
                    source=f"workspace:{profile.workspace_id}",
                )
            )

        line = _line_lookup().get(profile.line_id)
        if line is None:
            decisions.append(
                CapabilityDecision(
                    "line.available",
                    "blocked",
                    "selected_line_not_registered",
                    source=f"line:{profile.line_id}",
                )
            )
        else:
            process_line = _process_line_id()
            state = "enabled"
            if line.state == "blocked":
                state = "blocked"
            elif line.state == "degraded":
                state = "degraded"
            decisions.append(
                CapabilityDecision(
                    "line.available",
                    state,
                    line.state,
                    source=f"line:{profile.line_id}",
                )
            )
            # Phase 4.1: keep the audit-Round-5 "blocked /
            # requires_brain_cold_restart" wording for the runtime
            # apply path so existing client compatibility checks
            # don't silently start letting mismatched lines through.
            # The orchestrator-mediated Tier 1 flow is exposed
            # separately via the new ``tier_metadata`` block below
            # (see Phase 4.2 wire-up of ``tier`` on _line_selector
            # and the setting_change_tier registry).
            if profile.line_id != process_line:
                decisions.append(
                    CapabilityDecision(
                        "line.cold_start",
                        "blocked",
                        "requires_brain_cold_restart",
                        source=f"process_line:{process_line}",
                        fallback_action=(
                            "restart_brain_with_PARROT_LLM_PIPELINE="
                            + profile.line_id
                        ),
                    )
                )
            else:
                decisions.append(
                    CapabilityDecision(
                        "line.cold_start",
                        "enabled",
                        "process_line_matches_selected_line",
                        source=f"process_line:{process_line}",
                    )
                )

        line_profile = get_line_profile_loader().load(
            profile.line_profile_id,
            apply_env=True,
        )
        if line_profile.line_profile_id != profile.line_profile_id:
            decisions.append(
                CapabilityDecision(
                    "line.profile",
                    "blocked",
                    "selected_line_profile_not_registered",
                    source=f"line_profile:{profile.line_profile_id}",
                )
            )
        elif line_profile.line_id != profile.line_id:
            decisions.append(
                CapabilityDecision(
                    "line.profile",
                    "blocked",
                    "line_profile_line_mismatch",
                    source=f"line_profile:{profile.line_profile_id}",
                )
            )
        else:
            decisions.append(
                CapabilityDecision(
                    "line.profile",
                    "enabled",
                    "line_profile_registered",
                    source=f"line_profile:{profile.line_profile_id}",
                )
            )
            if profile.line_id == "line_b":
                decisions.extend(_lineb_profile_decisions(line_profile))

        registered_experience_modes = {m["experience_mode"] for m in EXPERIENCE_MODES}
        if profile.experience_mode not in registered_experience_modes:
            decisions.append(
                CapabilityDecision(
                    "experience_mode.available",
                    "blocked",
                    "unknown_experience_mode",
                    source=f"experience_mode:{profile.experience_mode}",
                )
            )
        else:
            decisions.append(
                CapabilityDecision(
                    "experience_mode.available",
                    "enabled",
                    "experience_mode_registered",
                    source=f"experience_mode:{profile.experience_mode}",
                )
            )

        if profile.experience_mode == "ar_companion" and profile.scene_profile_id != "ar_handheld":
            decisions.append(
                CapabilityDecision(
                    "experience_mode.scene_requirement",
                    "blocked",
                    "ar_companion_requires_ar_scene",
                    source=(
                        f"experience_mode:{profile.experience_mode};"
                        f"scene:{profile.scene_profile_id}"
                    ),
                    fallback_action="switch_scene:ar_handheld",
                )
            )
        elif profile.experience_mode == "2d_hall":
            decisions.append(
                CapabilityDecision(
                    "ar.plane_placement",
                    "disabled",
                    "experience_mode_is_2d_hall",
                    source="experience_mode:2d_hall",
                    fallback_action="open_mansion_hub",
                )
            )
        state = "ready"
        if any(d.state == "blocked" for d in decisions):
            state = "blocked"
        elif any(d.state in {"degraded", "disabled"} for d in decisions):
            state = "degraded"

        # Phase 4.2: collapse decisions → top-level tier so the
        # Unity startup page renders a single toast/dialog.
        tier = _max_tier_for_decisions(decisions, profile, _process_line_id())
        from parrot.brain.setting_change_tier import (
            tier_label as _tier_label,
            tier_summary as _tier_summary,
            tier_ui_action as _tier_ui_action,
        )

        return RoomCompatibilityReport(
            state=state,
            decisions=tuple(decisions),
            tier=tier,
            tier_label=_tier_label(tier),
            tier_summary=_tier_summary(tier),
            tier_summary_zh=_tier_summary(tier, lang="zh"),
            tier_ui_action=_tier_ui_action(tier),
        )


def get_room_setting_service() -> RoomSettingService:
    return RoomSettingService()


def _selectors(menu: MenuRegistrySnapshot) -> dict[str, Any]:
    return {
        "models": _to_wire(menu.models),
        "rooms": tuple(profile.as_json() for profile in get_preset_loader().list_room_profiles()),
        "personas": _to_wire(menu.personas),
        "lines": tuple(_line_selector(line) for line in list_lines()),
        "line_profiles": tuple(
            profile.as_json() for profile in get_line_profile_loader().list_profiles()
        ),
        "scenes": _to_wire(menu.scenes),
        # User-facing startup RoomSetting should render this as Theme/Skin.
        # The older `scenes` array remains for compatibility with the menu
        # registry and Web inspection, but mobile startup must not ask the user
        # to classify desktop / indoor / outdoor environment here.
        "skins": tuple(dict(skin) for skin in THEME_SKINS),
        "workspaces": _to_wire(menu.workspaces),
        "experience_modes": tuple(dict(m) for m in EXPERIENCE_MODES),
        "defaults": {
            "line_id": DEFAULT_LINE_ID,
            "line_profile_id": get_line_profile_loader().profile_for_line(
                DEFAULT_LINE_ID,
                apply_env=False,
            ).line_profile_id,
            "experience_mode": DEFAULT_EXPERIENCE_MODE,
            "skin_id": DEFAULT_SCENE_SKIN_ID,
        },
    }


def _line_selector(line: LineSummary) -> dict[str, Any]:
    data = line.as_json()
    process_line = _process_line_id()
    # Phase 4.2: surface the tier registry so the Unity startup page
    # can render the right toast/confirm dialog WITHOUT hard-coding
    # "line_id is cold-start only". The static tier for line_id is 1
    # (orchestrator-mediated reconnect), but it collapses to 0 when
    # the offered line equals the running line (no apply needed).
    from parrot.brain.setting_change_tier import (
        line_switch_tier_for_profile,
        tier_label,
        tier_summary,
        tier_ui_action,
    )

    tier = line_switch_tier_for_profile(line.line_id, process_line)
    data["selection_policy"] = {
        "scope": "cold_start_only",
        "requires_brain_restart": line.line_id != process_line,
        "current_process_line_id": process_line,
        "env_key": "PARROT_LLM_PIPELINE",
        # Phase 4 tier metadata — additive, do not break existing
        # callers that read the legacy `cold_start_only` scope.
        "tier": tier,
        "tier_label": tier_label(tier),
        "tier_summary": tier_summary(tier),
        "tier_summary_zh": tier_summary(tier, lang="zh"),
        "tier_ui_action": tier_ui_action(tier),
        "orchestrator_capable": True,
    }
    return data


def _max_tier_for_decisions(
    decisions: list[CapabilityDecision],
    profile: RoomProfile,
    process_line: str,
) -> int:
    """Pick the highest tier implied by the decisions.

    Mapping rules (Phase 4.2):

    * ``line.cold_start`` blocked → Tier 1 (orchestrator-mediated
      reconnect; see ``setting_change_tier.json`` row ``line_id``).
      We deliberately don't escalate to Tier 2 here because Phase 1
      put the runtime config on disk; the orchestrator can flip a
      line without restarting the Brain process.
    * ``line.cold_start`` degraded → Tier 1 (same path).
    * Any other ``blocked`` decision → still Tier 1 because
      "blocked" today only means the apply path needs a deliberate
      reconnect; nothing we wire above changes the live AgentSession
      mid-room.
    * Otherwise → Tier 0 (BB-write only).

    Returns ``0``..``2``. Tier 3 is operator-only and never surfaced
    here.
    """
    from parrot.brain.setting_change_tier import tier_for

    line_tier = tier_for("line_id") if profile.line_id != process_line else 0
    profile_tier = (
        tier_for("line_profile_id")
        if profile.line_profile_id and profile.line_profile_id != ""
        else 0
    )

    decision_tier = 0
    for decision in decisions:
        cid = decision.capability_id
        if cid == "line.cold_start" and decision.state in {"blocked", "degraded"}:
            decision_tier = max(decision_tier, line_tier or 1)
        elif cid in {"line.profile", "line.available"} and decision.state == "blocked":
            decision_tier = max(decision_tier, 1)

    return max(line_tier, profile_tier if profile.line_id != process_line else 0, decision_tier)


def _process_line_id() -> str:
    """Delegate to :func:`parrot.brain.line_status.running_line_id`.

    FIX (2026-05-11 audit Round 5, Bug O): both this resolver and the
    GOSLO Module canvas tile used to read ``PARROT_LLM_PIPELINE`` with
    almost-but-not-quite-identical normalization. The canonical answer
    now lives in ``line_status.running_line_id`` so cold-start
    compatibility decisions and runtime status reports always agree.
    """
    from parrot.brain.line_status import running_line_id

    return running_line_id()


def _line_lookup() -> dict[str, LineSummary]:
    return {line.line_id: line for line in list_lines()}


def _to_wire(value: Any) -> Any:
    if is_dataclass(value):
        return _to_wire(asdict(value))
    if isinstance(value, dict):
        return {str(k): _to_wire(v) for k, v in value.items()}
    if isinstance(value, (list, tuple)):
        return tuple(_to_wire(v) for v in value)
    return value


def _lineb_profile_decisions(line_profile: Any) -> tuple[CapabilityDecision, ...]:
    check = evaluate_line_profile(line_profile)
    out: list[CapabilityDecision] = []
    reason_map = {
        "google_api_key": "google_api_key_missing",
        "google_adc": "google_adc_missing",
        "asr": "asr_profile_or_adc_missing",
        "tts": "tts_voice_or_adc_missing",
        "voiceprint": "voiceprint_disabled",
        "echo": "echo_route_risk",
        "vad": "vad_plugin_missing",
    }
    for finding in check.findings:
        component_id = str(finding.get("component_id") or "")
        state = str(finding.get("state") or "unknown")
        health = str(finding.get("health") or "ok")
        if component_id not in reason_map:
            continue
        decision_state = "enabled"
        if state == "blocked" or health == "error":
            decision_state = "blocked"
        elif state in {"degraded", "not_configured", "high"} or health == "warning":
            decision_state = "degraded"
        out.append(
            CapabilityDecision(
                f"lineb.{component_id}",
                decision_state,
                reason_map[component_id] if decision_state != "enabled" else state,
                source=f"line_profile:{line_profile.line_profile_id}",
            )
        )
    return tuple(out)


def _model_capability_decisions(
    model_id: str,
    capabilities: set[str],
) -> tuple[CapabilityDecision, ...]:
    out: list[CapabilityDecision] = []
    for capability_id in sorted(capabilities):
        out.append(
            CapabilityDecision(
                f"model.capability.{capability_id}",
                "enabled",
                "declared_by_model_manifest",
                source=f"model:{model_id}",
            )
        )
    return tuple(out)


def _bb_str(key: str, default: str) -> str:
    try:
        from parrot.scheduler.blackboard import open_bb_client

        bb = open_bb_client(name="room_setting.read", writer=None)
        value = bb.get(key)
        if isinstance(value, str) and value:
            return value
    except Exception:
        pass
    return default


__all__ = [
    "CapabilityDecision",
    "EXPERIENCE_MODES",
    "LineSummary",
    "RoomCompatibilityReport",
    "RoomSettingService",
    "RoomSettingSnapshot",
    "get_room_setting_service",
    "list_lines",
]
