# Nanobot Agentic Mission Calendar SSOT - 2026-05-27

## Status

Source of truth for the Calendar/Nanobot collaboration boundary after the
2026-05-27 design clarification.

## Core Requirement

Nanobot is an agentic background worker, not a fixed function executor. Brain
owns foreground interaction with the user. Scheduler and Plan own traceable
state, dispatch, pause/resume, and audit. Calendar create/patch/delete are
approved write actuators, not the primary collaboration model.

## Required Modes

1. Flexible mission mode:
   - Brain dispatches a goal, authority, constraints, and expected report shape.
   - Nanobot may investigate, call tools, gather context, find conflicts,
     propose options, and report uncertainty.
   - Nanobot decides the internal order of investigation and tool use within
     the mission authority.
   - Nanobot must not perform external destructive writes unless the mission
     authority explicitly allows an approved write.

2. Guided workflow mode:
   - A workflow/playbook can require phases such as investigate, detect
     conflicts, propose options, wait for approval, execute, verify.
   - Within each phase Nanobot still acts agentically; the workflow is guidance
     and guardrails, not a dead if/else pipeline.
   - Nanobot may pause or revise the phase plan when new context, conflicts,
     missing data, or safety boundaries make the playbook insufficient.

3. Approved actuator mode:
   - Low-level tasks such as calendar_create, calendar_patch, and
     calendar_delete perform the final write only after HITL/Plan/operator
     approval metadata is present.

## Authority Boundary

Accepted authority values:

- read_only: Nanobot can inspect context and report.
- draft_only: Nanobot can propose options and staged write payloads.
- approved_write: Nanobot can execute the exact approved write payload.
- operator_write: Web/operator route can execute under explicit operator mode.

Calendar writes require one of:

- calendar_write_approved
- hitl_approved
- operator_mode
- explicit user confirmation metadata

## Mission Result Contract

Mission results should be structured and may use:

- accepted
- investigating
- draft_ready
- needs_user_decision
- approved_execution
- executing
- completed
- failed

For needs_user_decision, Nanobot must return:

- reason
- findings
- conflicts
- options
- recommended_option when available
- proposed_write when available
- requires_approval=true

Mission results should also carry enough collaboration context for Brain and
Web to explain what happened:

- mode / collaboration_mode
- nanobot_capabilities
- investigation_trace
- workflow_phase_results when a playbook was provided
- decision_strategy

Scheduler/Plan must not treat needs_user_decision as failure. It should pause
the originating Plan step and expose a HITL gate.

## Calendar Mission Contract

calendar_mission / nanobot_mission may contain:

- goal: natural-language mission objective
- domain: calendar or general
- authority: read_only, draft_only, approved_write, operator_write
- workflow_hint: optional playbook name
- allowed_tools: optional tool allow-list
- hitl_policy: e.g. ask_before_calendar_write
- expected_report: e.g. options_with_conflict_analysis
- context_refs: optional IntentWorkspace or memory refs

Scheduler/Plan may accept mission aliases and normalize them before dispatch:

- mission
- agentic_mission
- background_mission
- natural_language_task
- empty expected_tool when the step carries a goal/query/workflow

Calendar domain hints normalize to calendar_mission. Other mission aliases
normalize to nanobot_mission. Unknown non-mission task types still fall through
or fail validation; this avoids routing arbitrary malformed commands to
Nanobot.

Calendar mission output should include:

- findings
- conflicts
- options
- recommended_option
- proposed_write
- execution_policy
- audit

## Nanobot Capability Baseline

Nanobot missions may assume these background-worker capabilities, constrained
by authority and available tool configuration:

- natural-language mission intake
- self-investigation before deciding
- MCP/tool/API use within allow-list and credentials
- optional subtask/subagent delegation
- conflict and ambiguity analysis
- draft/proposal generation
- progress or partial finding reports
- pause with needs_user_decision
- resume after Plan/HITL/user decision
- approved external write execution through audited actuators

## Brain vs Nanobot

Brain:

- Handles live user interaction.
- Dispatches missions with goal, constraints, and authority.
- Uses nanobot_mission_request for natural-language mission handoff instead
  of hand-writing fixed dispatch JSON.
- Explains Nanobot reports to the user.
- Requests user decisions when Plan/HITL gates appear.

Nanobot:

- Investigates in the background.
- Uses tools/MCP/API as needed within authority.
- Reports progress, options, conflicts, and receipts.
- Pauses for HITL when authority is insufficient or ambiguity is high.

Plan/Scheduler:

- Tracks task and Plan state.
- Validates task type is routable to Nanobot.
- Pauses/resumes on needs_user_decision.
- Preserves audit and result-channel fan-out.
- Writes every Nanobot receipt to a bounded general result ledger
  (STREAM_NANOBOT_RESULTS) so tasks without trigger result_channel are still
  inspectable after Pub/Sub delivery has passed.

Brain status tools:

- calendar_task_status remains a Calendar-specific read-only monitor.
- nanobot_task_status is the general read-only monitor for Nanobot missions and
  background tasks. It reads bounded Scheduler/Nanobot dispatch/result ledgers
  only and never dispatches, writes external systems, or mutates memory.

## Implementation Notes

- Do not replace agentic missions with hard-coded Calendar workflows.
- Keep low-level Calendar write actuators available for approved execution.
- Fallback Nanobot inside ParrotCarriers may simulate mission behavior
  deterministically, but the contract should remain compatible with a real
  upstream Nanobot agent using MCP tools.
- Fallback Calendar missions may execute the approved Calendar write actuator
  only after self-checking calendar context, verifying approval metadata, and
  either finding no blocking conflict or receiving conflict override approval.
