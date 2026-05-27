# PPT 大纲：简约答辩版

## Slide 1: 项目题目
- Layout role: cover
- AR 生活助手与智能提醒系统
- 从实时交互到场景记忆

## Slide 2: 项目目标
- Layout role: goal
- 理解当前场景
- 在合适时机协助用户
- 形成可追踪数据流

## Slide 3: 场景输入
- Layout role: input map
- 语音、视频、照片、日程、笔记
- 统一为 Observation / Ref / Task

## Slide 4: 总体架构
- Layout role: architecture
- Unity AR 前端
- LiveKit 实时通信
- Brain / DSG / Graphiti / Scheduler / nanobot

## Slide 5: 实时音视频通道
- Layout role: concept
- Room
- Track
- DataChannel
- RPC

## Slide 6: SVA 与 Context 注入
- Layout role: workflow
- Video Track
- Processor
- Observation
- LLM / DSG

## Slide 7: 前台动作闭环
- Layout role: workflow
- 语音 Intent
- LiveKit RPC
- Unity 动作
- ACK / Blackboard

## Slide 8: 行为分层
- Layout role: layering
- Reflex
- Intent
- Task

## Slide 9: 后台任务协作
- Layout role: workflow
- 日程草稿
- 用户确认
- Scheduler
- Redis Stream
- nanobot Worker

## Slide 10: 工作记忆与长期记忆
- Layout role: memory
- DSG
- Graphiti
- Episode / Ref

## Slide 11: 触发器协议
- Layout role: protocol
- TriggerKind
- TriggerOutcome
- Observation / Ref / Archive / Plan / Task / Notify

## Slide 12: 拍照数据流
- Layout role: timeline
- 快门
- 预览事件
- 图片上传
- PhotoNode
- PHOTO Ref
- UUID

## Slide 13: Demo 路线
- Layout role: demo
- 前台交互
- 主动提醒 / 邮件
- 后台状态与日记

## Slide 14: 完成情况
- Layout role: summary
- 多源输入链路
- 前台状态闭环
- 记忆与任务协作

## Slide 15: 后续完善
- Layout role: closing
- 视觉稳定性
- 记忆治理
- 外部模块接入
