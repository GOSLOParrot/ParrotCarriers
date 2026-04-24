# FilePort2 — 不进 `.gitignore` 的临时文件投递区

## 与 `FilePort/` 的区别

- 根目录 **`FilePort/`** 在 `.gitignore` 中，**适合本机大文件暂存**，默认 **不提交**。  
- **`FilePort2/`**（本目录）**未被 ignore**，可放 **小体积、可提交的说明**；或作为「把文件拷到 ECS」时的 **本地落点说明**（实际二进制仍建议用 `scp`/`rsync` 直传，不强行进 Git）。

## 推荐用法（ECS 对齐 `active_context` / 大段 log）

1. 在 **本机** 把脱敏后的 `HANDOFF_…` 或 `report-*.md` 写好。  
2. 若需上 Castle 且 **不进 Git**：

   ```bash
   scp ./FilePort2/handoff-snippet.md root@<CASTLE_IP>:/opt/parrotcarriers/FilePort2/
   ```

   （先在 Castle 上 `mkdir -p /opt/parrotcarriers/FilePort2` 一次即可。）

3. 若 **应进 Git**：把同名内容放进 **`docs/test/p2_5/`** 或 **`docs/test/p2_5/ECS_RUN_REPORTS/`**，走 GitHub Desktop 正常 commit。

## 注意

- 仍 **不要**把 token、私钥、完整 JWT 放进任何会 push 的路径。
