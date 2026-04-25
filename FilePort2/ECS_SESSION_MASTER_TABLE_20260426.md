# ECS 联调总会话表（Brain + 设备）— 2026-04-26 CST 夜

本文是 **一轮三连进房** 的收口总表：`/tmp/brain.log`（**CST** 墙钟）与 `FilePort/log5.txt`（**UTC**）对齐。逐条对话与分轮里程碑全文见同目录 [`BRAIN_LOG_TRANSCRIPT_TIMELINE_20260426.md`](BRAIN_LOG_TRANSCRIPT_TIMELINE_20260426.md)。

---

## 1. 日历与钟面约定

| 项 | 值 |
| --- | --- |
| Brain 日志日期 | 日志行内 `00:42`–`00:53` 视为 **2026-04-26 凌晨（CST）** |
| 设备 `log5.txt` | 时间戳为 **UTC**（`…Z`）；**UTC+8 ≈ CST** 时，`16:49Z` ≈ **次日 00:49 CST** |
| 参与者（Unity） | `unity-a1efe9c48e1c5df9b4599bb7b82063f0`（与 mic `stream closed` JSON 一致） |

---

## 2. 三轮 Brain 会话总览

| 轮次 | `job_id` | `room_id` | CST 大致起止 | 语言与主题摘要 | 高信号 |
| --- | --- | --- | --- | --- | --- |
| 1 | `AJ_96nLLt4F54hz` | `RM_nexGiDebBXRe` | 00:42:41 → 00:48:28 | 中英混合；用户提到 **连接断断续续**、听不清等 | 视频 queue overflow×2；mic **stream closed** 00:43:41、00:48:08；Graphiti `add_episode` 多次 **20–29s** 级；`server cancelled tool calls`；`session closed` |
| 2 | `AJ_42tvBAMXNvDs` | `RM_XNDiVHPx8cej` | 00:48:37 → 00:50:43 | 粤语/繁中为主；桌面/笔记本/代码闲聊 | **与 log5 RpcRtt 对齐**（`agent-AJ_42tvBAMXNvDs`）；video overflow×1；`onGosloPlaced`×3；Graphiti **~46.4s** `add_episode`；mic stream closed 00:50:23；断开 |
| 3 | `AJ_FrnKRhEG8KMC` | `RM_HASeksWuB9er` | 00:51:07 → 00:53:25 | 英文为主；屏幕/鼠标 `identify_object` | video overflow×1；`set_mode` → **butler** 后 **`mode_watcher` / `context_injector` 两处** `AgentSession` **无** `update_instructions`（仍记录模式切换）；多次 Graphiti 与 **tool calls cancelled**；mic stream closed 00:53:05；断开 |

**模型**：三轮均为 `gemini-2.5-flash-native-audio-preview-12-2025`，voice=`Puck`（见 Brain 启动行）。

---

## 3. 统一高信号时间线（CST，跨轮合并）

按时间排序的 **总时间轴**（仅保留排障与对齐最关键节点；细粒度列表仍以分轮文档为准）。

| CST | 归属 `job_id` | 类别 | 简述 |
| --- | --- | --- | --- |
| 00:42:41 | `AJ_96nLLt4F54hz` | 启动 | no warmed process → Gemini Live → GOSLO live |
| 00:42:47 | `AJ_96nLLt4F54hz` | 会话 | Brain Agent session active |
| 00:42:47 | `AJ_96nLLt4F54hz` | 媒体 | video stream queue overflow |
| 00:43:16 | `AJ_96nLLt4F54hz` | Graphiti | `Completed add_episode` ~4.4s |
| 00:43:41 | `AJ_96nLLt4F54hz` | 音频 | mic `stream closed`（`SOURCE_MICROPHONE`） |
| 00:43:49 | `AJ_96nLLt4F54hz` | 媒体 | video queue overflow（再次出现） |
| 00:43:56 | `AJ_96nLLt4F54hz` | Gemini | `server cancelled tool calls` |
| 00:44:27–28 | `AJ_96nLLt4F54hz` | RPC | `onGosloPlaced`×3（约 0.5s 内三连） |
| 00:44:45 | `AJ_96nLLt4F54hz` | Graphiti | `add_episode` ~29.0s |
| 00:45:44 | `AJ_96nLLt4F54hz` | Graphiti | `add_episode` ~29.1s |
| 00:46:37 | `AJ_96nLLt4F54hz` | Graphiti | `add_episode` ~23.0s |
| 00:47:33 | `AJ_96nLLt4F54hz` | Graphiti | `add_episode` ~26.6s |
| 00:48:08 | `AJ_96nLLt4F54hz` | 音频 | mic `stream closed`（Graphiti 仍在跑） |
| 00:48:28 | `AJ_96nLLt4F54hz` | 生命周期 | GOSLO → chat；`session closed`；job shutdown |
| 00:48:37 | `AJ_42tvBAMXNvDs` | 启动 | 第二轮 job 起；GOSLO live |
| 00:48:43 | `AJ_42tvBAMXNvDs` | 会话 | session active；首句鹦鹉问候 |
| 00:48:50 | `AJ_42tvBAMXNvDs` | 媒体 | video queue overflow |
| 00:49:13–16 | （设备） | **对齐锚点** | **log5**：`16:49:13Z` self-test；`16:49:16Z` LiveKit OK（UTC）≈ **00:49 CST** |
| 00:49:35 | `AJ_42tvBAMXNvDs` | RPC | `onGosloPlaced`×3 |
| 00:49:54 | `AJ_42tvBAMXNvDs` | Graphiti | `add_episode` **~46.4s** |
| 00:49:49 | `AJ_42tvBAMXNvDs` | 对话 | 用户致谢 / 鹦鹉收束（见全文转写） |
| 00:50:09–10 | （设备） | **对齐锚点** | **log5**：RpcRtt → `agent-AJ_42tvBAMXNvDs`，avg **129ms**（UTC `16:50:09Z` 起） |
| 00:50:23 | `AJ_42tvBAMXNvDs` | 音频 | mic `stream closed` |
| 00:50:43 | `AJ_42tvBAMXNvDs` | 生命周期 | 房间断开 / `session closed` |
| 00:51:07 | `AJ_FrnKRhEG8KMC` | 启动 | 第三轮 job 起；GOSLO live |
| 00:51:14 | `AJ_FrnKRhEG8KMC` | 会话 | session active |
| 00:51:15 | `AJ_FrnKRhEG8KMC` | 媒体 | video queue overflow |
| 00:51:28 | `AJ_FrnKRhEG8KMC` | **缺陷** | `mode_watcher`：`update_instructions` **AttributeError**；随即 `set_mode` butler 仍记成功 |
| 00:51:58 | `AJ_FrnKRhEG8KMC` | Graphiti | `add_episode` ~21.1s |
| 00:51:59 | `AJ_FrnKRhEG8KMC` | Gemini | `server cancelled tool calls` |
| 00:52:10 | `AJ_FrnKRhEG8KMC` | **缺陷** | `context_injector.inject_scene`：同 **AttributeError**；`identify_object` 存盘鼠标 #1 |
| 00:52:26 | `AJ_FrnKRhEG8KMC` | 工具 | `identify_object` 存盘鼠标 #2 |
| 00:52:52–58 | `AJ_FrnKRhEG8KMC` | Graphiti | 两次长 `add_episode`（~31.3s / ~29.0s） |
| 00:53:05 | `AJ_FrnKRhEG8KMC` | 音频 | mic `stream closed` |
| 00:53:25 | `AJ_FrnKRhEG8KMC` | 生命周期 | GOSLO → chat；`session closed`；job shutdown |

---

## 4. 设备 `log5.txt` 与 Brain 对齐子表（UTC ↔ CST）

| UTC（`log5.txt`） | 约 CST | 设备侧含义 | Brain 侧对应 |
| --- | --- | --- | --- |
| `16:49:13Z` | 00:49:13 | P1 step5 self-test **START** | 第二轮会话中段（`AJ_42tvBAMXNvDs` 已 live） |
| `16:49:16Z` | 00:49:16 | LiveKit / 视频 fresh / mic 48k **OK** | 同上 |
| `16:50:09Z`–`16:50:10Z` | 00:50:09–10 | **RpcRtt** `onGosloPlaced` → `agent-AJ_42tvBAMXNvDs`，avg **129ms** | 与 Brain **同一 `job_id`**；Brain 侧同日 `onGosloPlaced` 在 **00:49:35** 已打三次（设备 RPC 样例略晚属正常） |

---

## 5. 产物索引

| 文件 | 用途 |
| --- | --- |
| [`BRAIN_LOG_TRANSCRIPT_TIMELINE_20260426.md`](BRAIN_LOG_TRANSCRIPT_TIMELINE_20260426.md) | 分轮 **完整** `[Gemini·用户/鹦鹉]` + 分轮里程碑（生成自 `/tmp/brain.log`） |
| [`../../../../FilePort/log5.txt`](../../../../FilePort/log5.txt) | 设备侧 48k + self-test + RpcRtt **原始**行 |
| ECS `/tmp/brain.log` | 权威原始日志（不在 Git 内）；重跑分析时以服务器副本为准 |

---

## 6. 待跟进（非本文范围、仅作索引）

- **`AgentSession.update_instructions`**：`mode_watcher.py` 与 `context_injector.py` 与当前 LiveKit Agents `AgentSession` API 不一致（第三轮已复现）。
- **TTS/实时语音断续**：第一轮用户语与鹦鹉切片在全文转写中体现明显，需与网络、Gemini 流式、客户端播放队列单独开任务对照。
