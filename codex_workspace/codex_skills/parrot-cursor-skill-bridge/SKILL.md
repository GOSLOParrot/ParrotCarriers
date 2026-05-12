---
name: parrot-cursor-skill-bridge
description: Use before writing or reviewing ParrotCarriers code/docs that touch Graphiti, FalkorDB, memory surgery, RefBinding, DSG L1.5/L2-B, rustworkx, py-trees, Scheduler, nanobot, LiveKit Unity, AR Foundation, SVA vision, or ECS bus deployment; routes Codex to the relevant .cursor/skills source skill.
---

# Parrot Cursor Skill Bridge

Use this skill inside the ParrotCarriers repo when work touches one of the
project-specific Cursor skills and a direct Codex skill did not trigger or you
need a route index.

Most high-risk project skills have now been installed as direct Codex skills.
See `codex_workspace/codex_skills/MIGRATION_STATUS_20260513.md` for the current
list.

Automatic triggering is helpful but not guaranteed. For App/Web parallel chats,
startup prompts should explicitly name the relevant direct skills. Use this
bridge only as a fallback if direct triggering is unclear.

## Source Location

Find the repo root, then read only the relevant source skill under:

`<repo>/.cursor/skills/<skill-name>/SKILL.md`

If the current workspace is not the repo root, search upward for
`.cursor/skills`.

## Selection Map

- Graphiti, FalkorDB, temporal memory, partitions, CRUD, triplets, MCP:
  `.cursor/skills/graphiti/SKILL.md`
- DSG L1.5/L2-A buckets and ConceptGraph distillation:
  `.cursor/skills/dsg-l1-5-l2a-conceptgraph-distilled/SKILL.md`
- DSG L2-B node organization and memory graph boundaries:
  `.cursor/skills/dsg-l2b-node-organization-options/SKILL.md`
- rustworkx graph implementation choices:
  `.cursor/skills/dsg-rustworkx-master/SKILL.md`
- py-trees Scheduler/Blackboard behavior-tree work:
  `.cursor/skills/py-trees/SKILL.md`
- Nanobot instance/team/config/runtime boundaries:
  `.cursor/skills/nanobot/SKILL.md` and
  `.cursor/skills/nanobot-overview/SKILL.md`
- Unity AR app version lock and AR Foundation APIs:
  `.cursor/skills/ar-foundation-api/SKILL.md` and
  `.cursor/skills/ar-foundation-samples/SKILL.md`
- LiveKit Unity SDK and mobile lifecycle:
  `.cursor/skills/client-sdk-unity/SKILL.md`,
  `.cursor/skills/livekit-unity-lifecycle/SKILL.md`, and
  `.cursor/skills/livekit-unity-video-publish/SKILL.md`
- Vision agent/video processor patterns:
  `.cursor/skills/sva-vision-agents/SKILL.md`
- ECS/Bus deployment and orchestration:
  `.cursor/skills/bus-deploy-livekit-ecs/SKILL.md` and
  `.cursor/skills/parrot-bus-orchestration/SKILL.md`

## Rules

- Do not bulk-load whole reference directories. Open `SKILL.md` first, then read
  only the specific referenced file needed for the current task.
- Prefer current repo code and tests over stale skill text when they conflict.
- For third-party APIs that may have changed, verify with official docs before
  implementing or recommending.
- Keep copied interface contracts out of business-flow docs; promote shared
  contracts through the App/Web core candidate queue.
