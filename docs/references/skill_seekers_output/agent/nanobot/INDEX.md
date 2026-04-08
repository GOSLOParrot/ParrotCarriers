# nanobot Skill 包索引

> 位置: `docs/references/skill_seekers_output/agent/nanobot/`
> 用途: 作为 `HKUDS/nanobot` 的主仓参考入口，服务于后续 `nanobot-worker` 审计与任务拆解

## 文件清单

1. `SKILL.md`
   - `nanobot` 的参考 skill 摘要
2. `references/README.md`
   - 与当前项目最相关的架构、运行方式、能力边界摘要
3. `references/file_structure.md`
   - 代码结构与关键模块索引
4. `references/releases.md`
   - 与运行时、子代理、多实例、memory/heartbeat 相关的版本演进
5. `references/issues.md`
   - 借鉴模式时需要留意的近期问题

## 当前定位

这是一个**已接入主仓的参考 skill 包**，当前用于：

1. 人工审计
2. 显式技能调用前的参考阅读
3. 后续提炼更窄的项目级 `nanobot` skill

## 当前路由约束

1. `docs/references/.../nanobot/` 是参考层
2. `.cursor/skills/nanobot/` 是项目级路由层
3. 当前不应把 `nanobot` 作为所有 Bus 任务的默认主 skill
4. 当前优先借鉴后台任务、子任务、多实例、heartbeat / cron、memory consolidation 模式
