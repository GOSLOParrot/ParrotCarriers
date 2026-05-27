# 选用例子工作区

这些例子先作为候选，不代表最终全部进入演讲稿。

## 候选例子

- 相机模式拍照后流程
- 语音选用 RPC 指令跳舞
- 触发器触发 Graphiti 预加载和填充信息
- 派发任务给 nanobot 的流程
- Task 和 Intent 的不同
- 黑板和任务调度器怎么体现

## 后续需要核查

- 哪些流程已经在论文和代码中完成。
- 哪些流程适合作为主例子。
- 哪些流程只适合答辩问答备用。

## 第1轮核查后的初步分组

| 例子 | 初步位置 | 原因 |
| --- | --- | --- |
| 相机模式拍照后流程 | 主例子 | 覆盖AR输入、ECP事件、PhotoNode、IntentWorkspace、RefTable，数据流完整 |
| 语音选用 RPC 指令跳舞 | 主例子 | 覆盖前台 Intent、LiveKit RPC、ECP ACK、Blackboard 状态同步 |
| GOSLO 派发“改日程”任务给 nanobot | 主例子 | 最能区分 Task 和 Intent：前台理解/确认是 Intent，后台执行日程变更是 Task |
| 触发器协议 | 主设计点 / 辅助流程组 | 重点不是某一个触发器，而是说明触发器协议能接入 Photo Awareness、Graphiti 回灌、主动提醒等不同事件 |

详细依据见：`round_01_flow_example_audit.md`。
