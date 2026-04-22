# AR Foundation 5.1 Skill Seekers 蒸馏与上下文注入策略 (Unity 2022.3 LTS)

> 状态: ratified
> 日期: 2026-04-22
> 目标: 针对 ParrotCarriers 项目的 Unity 2022.3 LTS 环境，确立将 AR Foundation 5.1.x 开发知识注入 Agent 上下文的最优策略（压缩蒸馏 vs 原文档 Reference）。

---

## 1. 核心策略决断：蒸馏 Skill (SKILL.md) 还是直接引入 Raw Docs?

**结论：强烈建议使用“蒸馏为 SKILL.md”，并放入 `.cursor/skills/` 目录中。绝不建议直接把整个官方 Raw Documentation 塞给 Agent 作为 Reference。**

根据 2026 年针对 Vercel Agent Evals 以及大规模 ClawHub Skills 的最新测试数据，直接扔原始文档与蒸馏出 SKILL.md 的效果有天壤之别：

### 为什么不能直接引入官方原文档 (Raw Docs)?
1. **信噪比 (Signal-to-Noise Ratio) 极低**：官方文档中包含大量教程前言、版本更新日志、"Welcome to..." 等营销或冗余术语。
2. **"迷失在中间" (Lost in the Middle) 效应**：如果你把 50 页的文档直接扔给 Agent，长上下文会导致 LLM 产生 U 型注意力。Agent 很容易忽略掉藏在中间的核心 API 调用约束，导致低级错误。
3. **上下文成本 (Context Window Cost)**：原文档极其臃肿（可能高达 40KB+），占据宝贵的 Context 空间，挤压掉你当前项目真实的业务代码逻辑（如你的 DSG 设计、LiveKit 逻辑）。

### 为什么必须使用蒸馏后的 SKILL.md?
1. **高密度压缩 (80% 降维打击)**：一份优秀的 `SKILL.md` 可以将 40KB 的原文档压缩到 8KB 以内，并且能实现 **100% 的 Agent Pass Rate**（任务成功率），而未经处理的检索方案仅有 53% ~ 79% 的成功率。
2. **规则前置 (Primacy Bias)**：在 `SKILL.md` 的顶部，你可以强制写下像“绝不允许使用 AR Foundation 6.x”或者“强制使用 XR Simulation 跑测试”这种针对当前项目的硬性治理规则 (Governance rules)。原文档里可没有这些我们自己总结的血泪教训。
3. **提供开箱即用的 Code Snippet**：官方手册偏向理论，而蒸馏后的 Skill 可以直接提供诸如“如何抓取 CPU 视频帧并转成 byte array”这种可以直接 Copy-Paste 的生产级 C# 代码段。

---

## 2. 蒸馏目标仓库与文献 (Target Repositories)

请让 Skill Seekers 机器人严格锁定以下**两个知识源**进行抓取和总结。

**回答你的核心问题：我们到底该蒸馏 SDK 还是 Example 仓库？**
**答案是：主要蒸馏 SDK 官方文档（为了 API 签名与生命周期准确），辅助蒸馏 Example 仓库（为了最佳实践），但必须在抓取 Example 时严格过滤掉冗余资产（Asset 噪音）。**

1. **第一优先级：官方包文档（SDK API 级核心知识）**
   * 目标：Unity 官方手册 `com.unity.xr.arfoundation@5.1`。
   * 价值：最权威的 API 签名、生命周期和底层机制说明。
   * **Skill Seekers 抓取策略**：使用 `doc_scraper` 模式，直接爬取官方文档站点。

2. **第二优先级：官方实战金矿仓库（Example 代码模式）**：[Unity-Technologies/arfoundation-samples](https://github.com/Unity-Technologies/arfoundation-samples)
   * ⚠️ **致命约束 1 (版本隔离)**：必须指定抓取 **`5.1` 分支**。绝对禁止抓取 `main` 分支（`main` 已经是 Unity 6 / AR Foundation 6.x 的天下，API 完全不同）。
   * ⚠️ **致命约束 2 (去噪过滤 - 防上下文污染)**：Example 仓库里含有大量针对不同视觉效果的 `.mat` (材质), `.prefab` (预制体), `.scene` (场景), `.png` (贴图) 等极其混乱的 YAML 序列化资产文本。**必须命令 Skill Seekers 仅抓取和分析 `.cs` (C# 脚本) 和 `.md` (文档) 文件**。如果把乱七八糟的场景序列化文本喂给 LLM，会导致生成的 Skill Context 严重污染，Agent 会完全抓不到重点。
   * **Skill Seekers 抓取策略**：使用 `codebase_scraper` 模式，并结合 `--skip-dependency-graph` 和 `--no-comments` 等参数控制噪音，如果支持 Unity 特性，可直接挂载 `unity-game-dev.yaml` 增强工作流。

---

## 2. 蒸馏过程的注意事项 (Precautions)

在配置 Skill Seekers 时，务必强调以下上下文背景，防止其产生“幻觉”：

* **版本隔离红线**：只要提到 "Unity 6"、"URP Compatibility Mode removal"、"AR Foundation 6" 或 "XRResultStatus" 的文档内容，**一律丢弃**，不要混入我们的知识库。
* **优先关注测试环境**：重点提炼有关 **XR Simulation**（编辑器内模拟 AR 环境）的配置和代码逻辑，这是我们实现“不在真机上也能开发 AR 功能”的关键。
* **规避过时/超前 API**：
  * 在 5.1 中，相机纹理回调依然依赖 `ARCameraManager.frameReceived`，一定要总结这个生命周期。
  * 抛弃所有关于 4.x 的 `SubsystemManager` 老旧调用方式，严格按 5.1 的标准库（如 `XRCpuImage`）来处理视频流帧。

---

## 3. 核心蒸馏英文关键词与 Prompt (Keywords & Prompts)

把以下 4 个 Prompts 直接喂给 Skill Seekers，让它分别产出对应的 `CLAUDE.md` 或 `SKILL.md` 小节：

### 🎯 关键词 1：XR Simulation Setup & Editor Workflow
> **Prompt for Skill Seekers**:
> "Based on AR Foundation 5.1 documentation and the `5.1` branch of arfoundation-samples, summarize the complete workflow for setting up and configuring **XR Simulation** in Unity 2022.3. Explain how to enable it in XR Plug-in Management, how to navigate the camera using WASD in the Editor Play mode, and how to properly inject and simulate virtual Planes and Point Clouds for scripts to consume."

### 🎯 关键词 2：ARCameraManager, XRCpuImage, and GPU Texture
> **Prompt for Skill Seekers**:
> "Analyze the best practices in AR Foundation 5.1 for capturing the real-time camera feed. Detail the usage of `ARCameraManager.frameReceived` event. Compare the performance implications of converting `XRCpuImage` to a raw byte array (for WebRTC/LiveKit publishing) versus directly using `Graphics.Blit` with GPU textures (`ARCameraBackground.material`). Provide production-ready code snippets."

### 🎯 关键词 3：ARPlaneManager & ARAnchorManager Lifecycle
> **Prompt for Skill Seekers**:
> "Explain the lifecycle and event-driven architecture of `ARPlaneManager` and `ARAnchorManager` in AR Foundation 5.1. How should developers correctly subscribe to `planesChanged` and `anchorsChanged` events? Provide a robust example of how to spawn and firmly anchor a 3D GameObject to a detected physical plane (e.g., using raycasting and `ARAnchor` instantiation)."

### 🎯 关键词 4：Android Permissions for ARCore (Camera & Audio)
> **Prompt for Skill Seekers**:
> "For an ARCore app built with Unity 2022.3 and AR Foundation 5.1, summarize the strict requirements for requesting Android Runtime Permissions (`CAMERA` and `RECORD_AUDIO`). Beyond `AndroidManifest.xml`, provide the exact C# code using `UnityEngine.Android.Permission` to forcefully request these permissions before initializing the `ARSession`, ensuring the AR camera and microphone do not fail silently."


Task: Generate an Agent Skill for Unity AR Foundation 5.1.x

Step 1: Scrape the official documentation at docs.unity3d.com/Packages/com.unity.xr.arfoundation@5.1/
Focus on extracting:
- `ARCameraManager` frameReceived events and `XRCpuImage` handling.
- XR Simulation Setup workflow for Unity Editor Play mode.
- `ARPlaneManager` and `ARAnchorManager` lifecycle events.

Step 2: Scrape the GitHub repository Unity-Technologies/arfoundation-samples
CRITICAL CONSTRAINTS FOR REPO SCRAPING:
- MUST target branch `5.1`. DO NOT touch `main`.
- MUST filter and extract ONLY `.cs` and `.md` files.
- STRICTLY IGNORE all Unity serialized assets: `.mat`, `.prefab`, `.scene`, `.asset`, `.meta`, `.png`.

Step 3: Synthesize the extracted knowledge into a single `SKILL.md` optimized for an AI coding agent. The skill must provide copy-pasteable C# best practices for grabbing AR frames, spawning anchors, and setting up XR Simulation in Unity 2022.3 LTS.