# Codex Skill Migration Status (2026-05-13)

Owner: coordination
Status: active
Category: Codex skill migration
Scope: App/Web parallel work safety gate
Sources: `.cursor/skills/**`, `C:\Users\Bin\.codex\skills\**`

## Decision

The bridge is no longer the primary safety net. The high-risk ParrotCarriers
Cursor skills have been installed as direct Codex skills under:

`C:\Users\Bin\.codex\skills\`

`parrot-cursor-skill-bridge` remains installed as a fallback index.

## Migrated Direct Skills

| Skill | Main trigger surface |
|:--|:--|
| `graphiti` | Graphiti, FalkorDB, memory surgery, CRUD, partitions, fact triples, RefBinding to Graphiti UUIDs. |
| `dsg-l1-5-l2a-conceptgraph-distilled` | L1.5 buckets, RefTable, source profiles, ingestion boundaries. |
| `dsg-l2b-node-organization-options` | L2-B nodes, last_seen/activation, ref links, visual graph rendering. |
| `dsg-rustworkx-master` | rustworkx graph algorithms, snapshots, traversal, graph mutation. |
| `dsg-attention-schema-papers` | attention weights, salience, memory validity, decay. |
| `py-trees` | Scheduler behaviour trees and Blackboard V2. |
| `nanobot` | Parrot nanobot runtime, AgentTeam boundaries, config switching. |
| `nanobot-overview` | Upstream nanobot architecture research. |
| `parrot-bus-orchestration` | Cross-component bus/module orchestration. |
| `livekit-agents` | LiveKit Agents Python SDK and server-side agent patterns. |
| `client-sdk-unity` | LiveKit Unity SDK APIs and RPC/data channel patterns. |
| `livekit-unity-lifecycle` | Unity mobile LiveKit reconnect/pause/resume lifecycle. |
| `livekit-unity-video-publish` | Unity video publish and video tier pipeline. |
| `ar-foundation-api` | Unity 2022.3.62f3 + AR Foundation/ARCore/ARKit 5.2.2 API lock. |
| `ar-foundation-samples` | AR Foundation 5.1/5.2 implementation samples. |
| `sva-vision-agents` | Vision-Agents processor and SVA video pipeline. |
| `bus-deploy-livekit-ecs` | ECS deployment, LiveKit Bus, TURN/direct connection, video quality tiers. |

## Trigger Policy

Automatic skill triggering is useful but not guaranteed. App/Web startup prompts
must name the relevant direct skills explicitly before implementation work.

Examples:

- App startup / AR / LiveKit: `ar-foundation-api`, `ar-foundation-samples`,
  `client-sdk-unity`, `livekit-unity-lifecycle`,
  `livekit-unity-video-publish`.
- Web memory graph: `graphiti`, `dsg-rustworkx-master`,
  `dsg-l1-5-l2a-conceptgraph-distilled`,
  `dsg-l2b-node-organization-options`.
- Scheduler/Nanobot: `py-trees`, `nanobot`, `nanobot-overview`,
  `parrot-bus-orchestration`.

## Maintenance Rule

If `.cursor/skills/<name>/SKILL.md` changes, reinstall or refresh the matching
Codex skill and keep the Codex `description` trigger-friendly. Do not let the
bridge be the only route for version-locked code paths.

