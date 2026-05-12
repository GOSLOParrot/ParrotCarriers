# `.cursor/config` — Castle / nanobot 对照包（随 deploy 上 ECS）

## 快照时间

权威时间戳见同目录 **`mirror-snapshot.txt`** 中的 `snapshot_generated_at_utc`（每次复制 deploymirror 后应更新）。  
在 ECS 上可对账：`cat /opt/parrotcarriers/.cursor/config/mirror-snapshot.txt`。

## 用途

- 在 ECS 上有一份与**本机**对齐的「真值」副本，方便 SSH 里 diff、给 agent 读、和 `/opt/parrotcarriers/.env` 对照。
- **不要提交到 Git**：`*.deploymirror` 已在根 `.gitignore` 登记；仅存在于本机 + `rsync` 到 Castle。

## 文件约定

| 文件 | 来源 / 说明 |
|:---|:---|
| `mirror-snapshot.txt` | **快照时间 + 清单（无密钥）**；字段 `snapshot_generated_at_utc`；可提交 Git、会随 rsync 上 ECS |
| `parrot-castle-config.deploymirror` | 本机仓库根 `.env` 的副本（重命名，避免命中根目录 `.env.*` 忽略规则） |
| `nanobot-parrot_config.deploymirror.json` | `../nanobot/config/parrot_config.json` |
| `nanobot-goslo_config.deploymirror.json` | `../nanobot/config/goslo_config.json` |
| `nanobot-weixin-account.deploymirror.json` | `../nanobot/config/weixin/account.json` |
| `castle-deploy.keys.example` | 仅占位说明，**不含**真密钥；可提交 |

若 sibling `nanobot` 无 `.env`，则不会生成 `nanobot-repo-env.deploymirror`（可自建或从 ECS 拉回）。

## 刷新本地副本

在仓库根执行（PowerShell 示例）：

```powershell
New-Item -ItemType Directory -Force -Path .cursor\config | Out-Null
Copy-Item .env .cursor\config\parrot-castle-config.deploymirror -Force
Copy-Item ..\nanobot\config\parrot_config.json .cursor\config\nanobot-parrot_config.deploymirror.json -Force
Copy-Item ..\nanobot\config\goslo_config.json .cursor\config\nanobot-goslo_config.deploymirror.json -Force
Copy-Item ..\nanobot\config\weixin\account.json .cursor\config\nanobot-weixin-account.deploymirror.json -Force
# 更新快照时间（UTC ISO）：替换 mirror-snapshot.txt 中 snapshot_generated_at_utc 那一整行
$ts = [datetime]::UtcNow.ToString('yyyy-MM-ddTHH:mm:ssZ')
(Get-Content .cursor\config\mirror-snapshot.txt -Raw) -replace 'snapshot_generated_at_utc:.*', "snapshot_generated_at_utc: $ts" |
  Set-Content .cursor\config\mirror-snapshot.txt -Encoding utf8
```

## 安全

- 若此目录内容曾出现在不可信日志或误提交 PR，请**轮换**相关 API / token。
- Castle 运行时仍以 **`/opt/parrotcarriers/.env`** 为准；本目录**不参与** Python `load_dotenv`，仅供人类与 ECS 侧对照。
