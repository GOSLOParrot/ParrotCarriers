# 给 ECS / 远端 Cursor 的「进度上下文」交接（脱敏）

## 为何需要本文件

- 仓库内 **`.cursor/memory/active_context.md` 被 `.gitignore` 排除**（避免会话态、临时 token 误进 Git）。  
- Castle 或 Remote SSH 上的 Cursor **无法靠 `git pull` 拿到**该文件。  
- **做法**：每次联调前，在 **本机** 打开 `active_context.md`，把 **与本轮测试相关、且无 secret** 的几行 **复制到下面模板**，再 commit 本文件 **或** 用 `FilePort2/` 传一份到 ECS（见 `FilePort2/README.md`）。

## 模板（复制后填，可另存为 `handoff-YYYYMMDD.md` 放在 `ECS_RUN_REPORTS/`）

```
UTC 时间:
Git SHA（ParrotCarriers）:
当前阶段（一句）:
本轮测试范围（P0 / P1 / P2 勾哪些）:
Castle / 本机已确认服务（redis livekit brain token-mint 等，打勾）:
Unity 锚点（最近一条 [SEQ] / [RoomManager] 行，打码）:
Brain 锚点（一行 grep 摘要，打码）:
阻塞项（无则写「无」）:
```

**禁止粘贴**：完整 JWT、API key、`.env` 全文、`parrot_config.json` 真值。
