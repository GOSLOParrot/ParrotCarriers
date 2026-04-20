# Castle P2 首次拉起报告 — FalkorDB + Graphiti 链路验证

> 日期：2026-04-20  
> 环境：Castle ECS (2C8G, Tokyo)  
> 基础版本：P2.5 审计修复完成 (commit `776eaff`)

---

## 一、目标

在 Castle ECS 上首次拉起 FalkorDB 容器，并完整验证 Graphiti 记忆共享链路：

1. FalkorDB 容器启动 & 健康
2. Python `graphiti_client` 单例连接 FalkorDB
3. 集成测试 4 项全通过（write → search → DSG 接口）
4. Brain Agent + Nanobot Worker 以最新代码重新上线

---

## 二、验证结果汇总

| # | 验证项 | 结果 | 备注 |
|---|--------|------|------|
| V-P2-1 | git log — 代码与 PC 一致 | ✅ | HEAD = `776eaff` |
| V-P2-2 | FalkorDB 容器 Up + Healthy | ✅ | 首次 pull 镜像成功 |
| V-P2-3 | `PING` → `PONG` (port 6380) | ✅ | |
| V-P2-4 | `GRAPH.LIST` → 空数组 | ✅ | 模块加载，无历史图数据 |
| V-P2-5 | Python `get_graphiti()` 连接成功 | ✅ | FalkorDB 索引已初始化 |
| V-P2-6 | `test_remember_and_query` | ✅ PASSED | |
| V-P2-7 | `test_scene_partition_isolated` | ✅ PASSED | |
| V-P2-8 | `test_dsg_preload_interface` | ✅ PASSED | |
| V-P2-9 | `test_dsg_update_last_seen` | ✅ PASSED | |
| V-P2-10 | Brain Agent 注册 LiveKit | ✅ | `registered worker AW_ACn5UFpHVdVF` |
| V-P2-11 | Nanobot Worker Agent loop | ✅ | `Agent loop started` |

**pytest 结果：4 passed, 0 failed, 0 skipped（48.80s）**

---

## 三、发现的问题与修复

### 问题 1 — `graphiti-core[falkordb]` extra 未安装

**现象**：`get_graphiti()` 抛出 `ImportError: falkordb is required for FalkorDriver`

**根因**：Castle 上之前只运行了 `pip install -e .`（无 memory extra），`falkordb` Python 包缺失。

**修复**：
```bash
pip install -e '.[memory]'
```

---

### 问题 2 — Graphiti 默认初始化 `OpenAIRerankerClient`

**现象**：`Graphiti(...)` 构造抛出 `OpenAIError: The api_key client option must be set`

**根因**：`graphiti_core.Graphiti.__init__` 当 `cross_encoder=None` 时默认初始化 `OpenAIRerankerClient()`，读取 `OPENAI_API_KEY`；Castle 无此变量。

**修复**（`src/parrot/memory/graphiti_client.py`）：显式传入 `GeminiRerankerClient`：

```python
from graphiti_core.cross_encoder.gemini_reranker_client import GeminiRerankerClient

cross_encoder = GeminiRerankerClient(
    config=LLMConfig(api_key=cfg.google_api_key, model="gemini-2.5-flash")
)
_instance = Graphiti(
    graph_driver=driver,
    llm_client=llm_client,
    embedder=embedder,
    cross_encoder=cross_encoder,
)
```

---

### 问题 3 — `EpisodeType` 路径变更（graphiti-core 0.28.2 API 变更）

**现象**：`ImportError: cannot import name 'EpisodeType' from 'graphiti_core.graphiti_types'`

**根因**：graphiti-core 0.28.2 将 `EpisodeType` 从 `graphiti_types` 移至 `graphiti_core.nodes`。

**修复**（`tests/integration/test_graphiti_chain.py`）：
```python
# 旧
from graphiti_core.graphiti_types import EpisodeType
# 新
from graphiti_core.nodes import EpisodeType
```

---

### 问题 4 — `add_episode` 参数签名变更（graphiti-core 0.28.2）

**现象**：测试调用 `add_episode(text=..., episode_type=..., source=...)` 失败

**根因**：0.28.2 新签名：
```python
add_episode(
    name: str,           # 新增必填
    episode_body: str,   # 原 text
    source_description: str,  # 新增必填
    reference_time: datetime, # 新增必填
    source: EpisodeType,      # 原 episode_type
    group_id: str,
)
```

**修复**（`tests/integration/test_graphiti_chain.py`）：全部 3 处 `add_episode` 调用更新为新签名。

---

### 问题 5 — Embedding 模型 `text-embedding-004` 已下线

**现象**：`ClientError: 404 NOT_FOUND — models/text-embedding-004 is not found for API version v1beta`

**根因**：`text-embedding-004` 在 Gemini API 当前版本中已不可用，`ListModels` 显示可用 embedding 模型为 `gemini-embedding-001` 和 `gemini-embedding-2-preview`。

**修复**（`src/parrot/memory/graphiti_client.py`）：
```python
# 旧
embedding_model="text-embedding-004"
# 新
embedding_model="gemini-embedding-001"
```

---

## 四、Docker Compose 最终状态

```
NAME               IMAGE                      STATUS              PORTS
infra-falkordb-1   falkordb/falkordb:latest   Up (healthy)        127.0.0.1:6380->6379/tcp
infra-livekit-1    livekit/livekit-server     Up 4 days           0.0.0.0:7880-7881
infra-redis-1      redis:7-alpine             Up 4 days (healthy) 0.0.0.0:6379
```

---

## 五、运行时状态（2026-04-20 16:03 UTC+8）

| Session | 命令 | 状态 |
|---------|------|------|
| `brain` | `python -m parrot.brain.agent dev` | running — `registered worker AW_ACn5UFpHVdVF` |
| `maid`  | `start_nanobot_worker.py --no-weixin` | running — `Agent loop started` |

---

## 六、变更文件清单

| 文件 | 变更类型 | 说明 |
|------|---------|------|
| `src/parrot/memory/graphiti_client.py` | fix | 添加 `GeminiRerankerClient`；embedding 模型改为 `gemini-embedding-001` |
| `tests/integration/test_graphiti_chain.py` | fix | 适配 graphiti-core 0.28.2：`EpisodeType` 路径 + `add_episode` 新签名 |

---

## 七、后续操作

1. **[ ] PC 端执行 `sync-castle.ps1`**：将本次 ECS 上的 commit 同步回 PC（或 `git pull` 拉取）
2. **[ ] 验证完整语音链路**：Unity 客户端连接 → Brain 语音 → Graphiti 记忆写入
3. **[ ] 验证记忆持久化**：重启 brain 后 `query_memory` 能搜到之前写入的内容
4. **[ ] goslo-chat tmux session**：Telegram bot（需 `TELEGRAM_BOT_TOKEN` 配置确认后再启）

---

*P2 Castle 部署里程碑完成。FalkorDB + Graphiti 全链路在线验证通过。*
