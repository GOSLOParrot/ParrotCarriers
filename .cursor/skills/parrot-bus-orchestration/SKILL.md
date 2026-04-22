---
name: parrot-bus-orchestration
description: Bus 任务编排入口技能。用于 ParrotCarriers 中组合 livekit/sva/graphiti/unity/nanobot 技能并收口模块边界。
---

# parrot-bus-orchestration

Use this skill when working on Bus architecture, module contracts, worker splitting, and phase boundary control in ParrotCarriers.

## When to Use This Skill

Use this skill when you need to:
- Design or revise Bus module boundaries
- Route Bus tasks to the right domain skills
- Validate cross-module communication paths
- Prevent premature protocol over-design (see BigIssue.md)

## Task -> Skill Composition

### 1) Bus Skeleton (L1+L2)
- Primary: `livekit-agents`
- Secondary: `agent-starter-python`
- Output: room topology, module mounting protocol, heartbeat

### 2) DSG Processor Interface (D0)
- Primary: `sva-vision-agents`
- Secondary: `livekit-agents`
- Output: processor mounting hook, video track subscription, scene event DataChannel

### 3) Memory Layer (Phase 2)
- Primary: `graphiti`
- Output: group_id partitioning, write triggers, non-frame-driven ingestion

### 4) Unity Execution Path
- Primary: `client-sdk-unity`, `agents-example-unity`
- Secondary: `livekit-agents`
- Output: RPC handlers, telemetry channel, execution feedback path

### 4-AR) Unity AR Foundation Layer
- Primary: `ar-foundation-api` — XRCameraSubsystem / ARPlaneManager / ARFaceManager / ARAnchor / XRCpuImage API (5.1.x, Unity 2022.3 LTS)
- Secondary: `ar-foundation-samples` — 具体 sample 模式（帧抓取、平面放置、Android 权限）
- See also: `.cursor/rules/ar-foundation.mdc` (版本约束 + 已知 pitfall)

### 5) Nanobot Worker Adapter
- Primary: `nanobot`
- Output: parrot_bus.py channel adapter, Redis Stream consumption, results writeback

## Architecture References

| Document | Path |
|:---------|:-----|
| 完整功能需求 v2 | `.cursor/memory/requirements.md` |
| 模块划分 | `.cursor/memory/architecture/module_division.md` |
| 总线架构 v4.2 | `.cursor/memory/architecture/bus_v4.md` |
| 协议污染复盘 | `.cursor/memory/BigIssue.md` |

## Key Terminology

- **Scheduler** (不用 Dispatcher): 调度器模块
- **SimpleRouter**: Scheduler 在 Phase 1 的实现
- **ModuleManifest**: 模块声明 dataclass（候选字段，代码驱动收敛）
- **Path A / Path B**: L1+L2 模块 vs L2-only 模块的挂载路径

## Common Pitfalls

- Freezing protocol schemas on paper before code validation
- Treating Scheduler internals (py-trees) as Phase 1 prerequisite
- Writing high-frequency raw L1 data to Graphiti
- Exposing upstream internal types across module boundaries
- Conflating Bus heartbeat with nanobot's internal heartbeat
