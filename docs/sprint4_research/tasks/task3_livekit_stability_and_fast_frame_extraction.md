# DeepResearch 任务 3：LiveKit 移动端弱网抗性与高频截帧的工程优化实践

## 1. 研究问题
在 Unity 移动端使用 LiveKit 进行音视频推流时，如何处理切后台、网络波动导致的连接假死？同时，在 AR 场景中，如何以极低的性能代价（不卡主线程）高频提取相机帧（如 320x240）传给后端 AI？

## 2. 必要背景
（请参考 `00_sprint3_audit_and_unified_background.md` 中的“统一大背景”）
- **当前痛点 1（弱网与切后台）**：移动端网络切换或 App 锁屏切后台时，LiveKit 容易出现房间还在但音视频流 stale 的情况。
- **当前痛点 2（高频截帧）**：我们需要实现 `captureSnapshot` RPC，按需截取 AR 画面传给后端。直接用 `Texture2D.ReadPixels` 会严重阻塞主线程。

## 3. 必须查的资料类型（大型学术库/社区经验搜索）
- **LiveKit 移动端优化**：搜索 LiveKit 社区、GitHub Issues 中关于 `mobile background reconnect`, `ICE restart`, `video track stale` 的踩坑记录和恢复策略。
- **Unity 移动端截帧黑科技**：搜索 Unity 论坛、GitHub 上关于 `AsyncGPUReadback`, `XRCpuImage` 在 Android 上的真实性能测试，以及快速将 RenderTexture 压缩为小体积 JPEG 的社区方案。

## 4. 输出格式
一份 Markdown 调研报告，包含：
- **移动端断连与恢复策略**：总结社区在处理 App 切后台/网络切换时，何时依赖 LiveKit 自动重连，何时应主动销毁并重建 Track/Room 的最佳实践。
- **无阻塞截帧方案对比**：列出 2-3 种在 Unity 移动端提取相机帧的方法（如 `AsyncGPUReadback`），并附带社区测试的延迟数据和主线程阻塞时间。
- **图片压缩与传输经验**：收集开发者在 Unity 中快速压缩图像数据（控制在 15KB 左右以适应 RPC，或改走 DataChannel/ByteStream）的工程方案。

## 5. 决策标准
- 提供的是**真实的性能测试数据和工程踩坑经验**。
- 方案必须考虑到 Unity 2022.3 和 Android 平台的限制，特别是主线程性能和内存 GC 问题。