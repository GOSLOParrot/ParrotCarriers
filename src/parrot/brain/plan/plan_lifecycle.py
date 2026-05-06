"""PlanLifecycle — state-transition rules.

BRAIN-PLAN-V1 § 4.
"""

from __future__ import annotations

from parrot.brain.plan.plan import Plan, PlanState


class IllegalPlanTransition(ValueError):
    """Raised when a Plan state transition is not allowed."""


class PlanLifecycle:
    """State-transition checker. enforce_transition mutates plan.state."""

    LEGAL_TRANSITIONS: dict[PlanState, frozenset[PlanState]] = {
        PlanState.DRAFT: frozenset({
            PlanState.AWAITING_USER_CONFIRMATION,
            PlanState.CANCELLED,
        }),
        PlanState.AWAITING_USER_CONFIRMATION: frozenset({
            PlanState.APPROVED,
            PlanState.CANCELLED,
            PlanState.REVISED,
        }),
        PlanState.APPROVED: frozenset({
            PlanState.EXECUTING,
            PlanState.CANCELLED,
        }),
        PlanState.EXECUTING: frozenset({
            PlanState.PARTIAL_COMPLETE,
            PlanState.COMPLETE,
            PlanState.FAILED,
            PlanState.CANCELLED,
        }),
        PlanState.PARTIAL_COMPLETE: frozenset({
            PlanState.EXECUTING,
            PlanState.COMPLETE,
            PlanState.FAILED,
            PlanState.CANCELLED,
            PlanState.REVISED,
        }),
        PlanState.COMPLETE: frozenset(),
        PlanState.FAILED: frozenset({PlanState.REVISED}),
        PlanState.CANCELLED: frozenset(),
        PlanState.REVISED: frozenset(),
    }

    @classmethod
    def can_transition(cls, from_state: PlanState, to_state: PlanState) -> bool:
        return to_state in cls.LEGAL_TRANSITIONS.get(from_state, frozenset())

    @classmethod
    def enforce_transition(cls, plan: Plan, to_state: PlanState) -> None:
        if not cls.can_transition(plan.state, to_state):
            raise IllegalPlanTransition(
                f"Plan {plan.plan_id} cannot transition "
                f"{plan.state.value} → {to_state.value}",
            )
        plan.state = to_state


__all__ = ["IllegalPlanTransition", "PlanLifecycle"]
