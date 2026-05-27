# 演讲备注

## Slide 1: 项目题目

各位老师好，我汇报的项目是 AR 生活助手与智能提醒系统。它面向真实 AR 场景，把用户当前的交互、场景信息、记忆和后台任务组织到一条清楚的数据流里。

## Slide 2: 项目目标

项目目标可以概括成三个词：感知、记忆、行动。系统需要理解用户当前看到什么、正在做什么，再结合日程和历史信息，在合适时机协助用户。

## Slide 3: 场景输入

场景输入包括实时音视频、后台任务、日程、Obsidian 笔记和后续 CV 扩展。它们进入系统后会先变成 Observation、Ref 或 Task，方便追踪来源和后续处理。

## Slide 4: 总体架构

总体架构分成五层：Unity AR 前端负责交互和展示，LiveKit 负责实时通信，Brain Agent 负责理解和工具调用，DSG 与 Graphiti 负责记忆，Scheduler 和 nanobot 负责后台任务。

## Slide 5: 实时音视频通道

LiveKit 在这里承载 Room、音视频 Track、DataChannel 和 RPC。音视频用于感知，DataChannel 用于事件和状态，RPC 用于后端触发前端动作。

## Slide 6: SVA 与 Context 注入

SVA 在本项目中作为 Processor 思路使用。视频流可以按受控频率处理，得到结构化 Observation，再注入大模型上下文或 DSG 工作记忆。

## Slide 7: 前台动作闭环

前台动作需要闭环。用户发出语音指令后，Brain 调用工具，通过 LiveKit RPC 下发给 Unity；Unity 执行后返回 ACK，后端把结果写入 Blackboard。

## Slide 8: 行为分层

行为调度分成 Reflex、Intent 和 Task。Reflex 处理低延迟动作，Intent 处理需要前台回执的用户意图，Task 处理耗时的外部执行。

## Slide 9: 后台任务协作

以改日程为例，系统先生成日程草稿并等待确认；确认后进入 Scheduler，通过 Redis Stream 派发给 nanobot Worker 或 gateway，完成后结果回流。

## Slide 10: 工作记忆与长期记忆

DSG 是运行时工作记忆，保存当前场景里的 Observation 和 Ref。Graphiti 负责长期图记忆，适合归档 Episode、实体和事实，并在后续场景中回灌。

## Slide 11: 触发器协议

触发器协议用于统一处理事件。触发器输出可以是观察、暂存引用、归档请求、计划、后台任务或前台通知，主动提醒和记忆回灌都可以接入这个机制。

## Slide 12: 拍照数据流

拍照流程说明多源 Ref 的价值。快门触发后先产生预览事件，完整图片再上传；系统创建 PhotoNode，暂存 PHOTO Ref，并用 UUID 绑定来源。

## Slide 13: Demo 路线

Demo 部分建议控制在两分钟，展示前台交互、主动提醒或邮件，以及后台状态和 Obsidian 日记，让架构设计落到可见流程上。

## Slide 14: 完成情况

当前完成的重点是三条链路：多源输入进入统一上下文，前台动作形成状态闭环，记忆与后台任务可以协同运行。

## Slide 15: 后续完善

后续还可以加强视觉稳定性、长期记忆治理和更多外部模块接入。我的汇报到这里，谢谢各位老师。
