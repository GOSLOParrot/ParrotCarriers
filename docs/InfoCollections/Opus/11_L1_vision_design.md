# L1 视觉层设计：稳定性门控 + 视觉职责分级

> 生成日期: 2026-02-24
> 核心问题: 手持 AR 环境 ≠ SVA 的固定视角，视觉模型需要根据相机稳定性条件触发
> 依据: ARCore TrackingState API、SAM2/EdgeTAM 性能基准、SVA VideoForwarder 模式

---

## 1. 问题本质：为什么 SVA 的经验不能照搬

### SVA 的假设环境

SVA 的典型场景：高尔夫教练（三脚架摄像头）、安防监控（墙壁固定）、制造质检（固定工位）。

**特征**: 背景静止、光照稳定、帧间变化小、无运动模糊。

### 我们的实际环境

**安卓手机** (Snapdragon 8 Gen 系列, ARCore)，用户在房间里走动、低头、快速转身、手举物体展示。

**特征**: 背景剧烈变化、运动模糊频繁、帧间位移大、追踪经常中断。

### 你观察到的"严重跳变"的根因

```
相机快速移动 → 帧间位移大 → SAM2 追踪丢失 → 新 track_id 产生
                           → DINOv2 提取模糊特征 → ReID 误匹配
                           → 同一杯子产生 3 个 UUID → L2-A 图"爆炸"
```

**核心矛盾**: 视觉模型假设输入帧是清晰的，但手持相机的帧经常是模糊的、位移过大的。

---

## 2. 解决方案：稳定性门控架构 (Stability-Gated Processing)

### 2.1 设计理念

不是所有帧都值得分析。**用 ARCore 的追踪状态来决定哪些视觉功能可以运行。**

这借鉴了人眼的"扫视抑制 (Saccadic Suppression)"——当眼球快速转动时，大脑会主动抑制视觉输入，避免处理模糊的图像。

### 2.2 ARCore 提供的关键信号

ARCore 通过 AR Foundation 暴露以下信号（Unity DataChannel 发送到 Python）：

```csharp
// Unity 端采集 (10Hz, 通过 DataChannel Unreliable 发送)
var telemetry = new {
    type = "ar_telemetry",
    timestamp = Time.time,

    // AR 追踪状态 (核心门控信号)
    tracking_state = ARSession.state,          // Tracking | Limited | None
    not_tracking_reason = ARSession.notTrackingReason,
    // 可能值: ExcessiveMotion | InsufficientFeatures | InsufficientLight

    // 相机运动指标 (Python 端也可从连续 Pose 计算)
    camera_velocity = cameraPoseVelocity,      // m/s
    camera_angular_velocity = cameraAngularVel, // rad/s

    // AR 平面信息
    planes_detected = planeManager.trackables.count,
    plane_alignment = mainPlane?.alignment,     // Horizontal | Vertical

    // 手部追踪
    hand_state = handSubsystem.trackingState,
    hand_joints = handJoints,                  // 简化的关键关节
};
```

### 2.3 四级处理分级 (Processing Tiers)

```
┌─────────────────────────────────────────────────────────────────┐
│                    ARCore Telemetry (10Hz)                       │
│  tracking_state + camera_velocity + angular_velocity             │
└──────────────────────────┬──────────────────────────────────────┘
                           │
                    ┌──────▼──────┐
                    │ Stability   │
                    │ Gate        │
                    └──────┬──────┘
                           │
          ┌────────┬───────┼───────┬────────┐
          ▼        ▼       ▼       ▼        ▼
       Tier 0   Tier 1  Tier 2  Tier 3   On-Demand
       (Lost)  (Shaking)(Moving)(Stable)  (Gemini请求)
```

| 分级 | 条件 | 活跃的视觉功能 | GPU 占用 |
|:-----|:-----|:--------------|:---------|
| **Tier 0: 追踪丢失** | `tracking_state == None` | 全部暂停。所有 L2-A 节点→OCCLUDED | ~0% |
| **Tier 1: 剧烈运动** | `ExcessiveMotion` 或 `angular_vel > 2.0 rad/s` | 仅保持已有 SAM2 mask 的惯性预测（不分析新帧）。L2-A 位置用 AR Pose 插值 | ~5% |
| **Tier 2: 缓慢移动** | `tracking_state == Tracking` 且 `velocity < 0.5 m/s` | SAM2 追踪（已有目标）+ 基础位置更新。不做新物体发现、不做 ReID | ~40% |
| **Tier 3: 稳定/静止** | `velocity < 0.1 m/s` 且 `angular_vel < 0.3 rad/s` 持续 > 0.5s | **全部功能**: SAM2 追踪 + DINOv2 ReID + 新物体发现 + 动作分析 | ~80% |
| **On-Demand** | Gemini Tool Call `focus_on(uuid)` | 立即对指定目标执行 DINOv2 特征提取（无论当前 Tier） | 按需 |

### 2.4 Stability Gate 实现

```python
from enum import IntEnum
import time

class ProcessingTier(IntEnum):
    LOST = 0
    SHAKING = 1
    MOVING = 2
    STABLE = 3

class StabilityGate:
    """ARCore 稳定性门控: 决定哪些视觉处理器可以运行"""

    STABLE_VELOCITY_THRESH = 0.1       # m/s
    STABLE_ANGULAR_THRESH = 0.3        # rad/s
    STABLE_DURATION_THRESH = 0.5       # 秒 (需持续稳定才升级)
    MOVING_VELOCITY_THRESH = 0.5       # m/s
    SHAKING_ANGULAR_THRESH = 2.0       # rad/s

    def __init__(self):
        self._current_tier = ProcessingTier.LOST
        self._stable_since: float | None = None

    def update(self, telemetry: dict) -> ProcessingTier:
        """每次收到 AR 遥测时调用 (10Hz)"""
        tracking = telemetry.get("tracking_state", "None")
        reason = telemetry.get("not_tracking_reason", "")
        velocity = telemetry.get("camera_velocity", 999)
        angular = telemetry.get("camera_angular_velocity", 999)
        now = time.time()

        if tracking == "None":
            self._stable_since = None
            self._current_tier = ProcessingTier.LOST
            return self._current_tier

        if reason == "ExcessiveMotion" or angular > self.SHAKING_ANGULAR_THRESH:
            self._stable_since = None
            self._current_tier = ProcessingTier.SHAKING
            return self._current_tier

        if velocity > self.MOVING_VELOCITY_THRESH:
            self._stable_since = None
            self._current_tier = ProcessingTier.MOVING
            return self._current_tier

        # 进入稳定区: 需要持续一段时间才确认
        if velocity < self.STABLE_VELOCITY_THRESH and angular < self.STABLE_ANGULAR_THRESH:
            if self._stable_since is None:
                self._stable_since = now
            if now - self._stable_since > self.STABLE_DURATION_THRESH:
                self._current_tier = ProcessingTier.STABLE
                return self._current_tier

        # 介于两者之间: Moving
        self._current_tier = ProcessingTier.MOVING
        return self._current_tier

    @property
    def tier(self) -> ProcessingTier:
        return self._current_tier
```

---

## 3. L1 内部的视觉职责分配

### 3.1 视觉处理器清单

L1 不是一个单一的 "SAM2 + DINOv2" 处理器，而是**一组可独立启停的处理器**。借鉴 SVA 的 `VideoForwarder` 多处理器模式：

| 处理器 | 功能 | 运行条件 | 帧率 | GPU 负载 |
|:-------|:-----|:---------|:-----|:---------|
| **Tracker** | SAM2 已有目标的 mask 追踪 (全分割作为主发现机制) | Tier 2+ | 15-30fps | 中 |
| **Discoverer** | YOLO-World 扫描未知物体 (作为可选补充) | **仅 Tier 3** | 1-2fps | 中 |
| **Identifier** | DINOv2 特征提取 + 向量匹配(ReID) | **仅 Tier 3** 或 On-Demand | 触发式 | 中 |
| **ActionAnalyzer** | 动作/手势分析 (可选，Phase 4) | **仅 Tier 3** | 5fps | 低 |
| **PoseAligner** | AR Pose 时间同步 + 坐标转换 | Tier 1+ | 10Hz | ~0 |
| **FrameQualityChecker** | 模糊检测 (Laplacian 方差) | 所有 Tier | 30fps | ~0 |

### 3.2 处理器启停逻辑

```python
class L1VisionPipeline:
    """L1 视觉管线: 根据 StabilityGate 动态启停处理器"""

    def __init__(self):
        self.gate = StabilityGate()
        self.tracker = SAM2Tracker()
        self.discoverer = YOLOWorldDiscoverer()
        self.identifier = DINOv2Identifier()
        self.pose_aligner = PoseAligner()
        self.quality_checker = FrameQualityChecker()

    async def process_frame(self, frame, telemetry: dict) -> L1Output:
        tier = self.gate.update(telemetry)

        # 帧质量检查 (所有 Tier 都做)
        blur_score = self.quality_checker.check(frame)
        if blur_score < BLUR_THRESHOLD:
            # 模糊帧: 跳过 GPU 密集处理，只更新位置
            return L1Output(skipped=True, reason="blur")

        # Tier 0: 追踪丢失
        if tier == ProcessingTier.LOST:
            return L1Output(all_occluded=True)

        # Tier 1+: Pose 对齐始终运行
        aligned_pose = self.pose_aligner.align(telemetry)

        # Tier 1: 仅惯性预测
        if tier == ProcessingTier.SHAKING:
            predictions = self.tracker.predict_without_frame()
            return L1Output(tracks=predictions, pose=aligned_pose, tier=tier)

        # Tier 2: SAM2 追踪已有目标 (不发现新物体)
        if tier == ProcessingTier.MOVING:
            tracks = await self.tracker.track(frame)
            return L1Output(tracks=tracks, pose=aligned_pose, tier=tier)

        # Tier 3: 全功能
        if tier == ProcessingTier.STABLE:
            tracks = await self.tracker.track(frame)
            new_objects = await self.discoverer.discover(frame, existing=tracks)
            for obj in new_objects:
                obj.dino_features = await self.identifier.extract(frame, obj.bbox)
            return L1Output(
                tracks=tracks,
                new_objects=new_objects,
                pose=aligned_pose,
                tier=tier,
            )
```

### 3.3 FrameQualityChecker: 模糊帧过滤

```python
import cv2
import numpy as np

class FrameQualityChecker:
    """帧质量检测: 在 GPU 处理前快速过滤模糊帧"""

    BLUR_THRESHOLD = 100  # Laplacian 方差阈值 (需实测调整)

    def check(self, frame: np.ndarray) -> float:
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        return cv2.Laplacian(gray, cv2.CV_64F).var()

    def is_sharp(self, frame: np.ndarray) -> bool:
        return self.check(frame) > self.BLUR_THRESHOLD
```

---

## 4. ARCore 信息的深度利用

ARCore 不只提供追踪状态，还有很多对 L1 有价值的信息：

### 4.1 AR 平面 → 为 L2-A 提供承载面

```
ARCore 检测到水平平面 (桌面)
  → DataChannel 发送 plane_id + bounds + center_pose
    → L2-A 创建 SURFACES 层节点
      → 物体检测结果自动关联: "杯子 ON_TOP_OF 桌面"
```

不需要视觉模型来判断"杯子在桌子上"——ARCore 的平面检测 + 物体 BBox 的 Y 坐标比较就够了。这大幅降低了 L2-A 空间关系推理的复杂度。

### 4.2 AR 锚点 → 物体位置锚定

```
用户凝视某物体 → Gemini Tool: focus_on(uuid)
  → Unity 在该物体位置创建 AR Anchor
    → 即使相机移动，Anchor 坐标始终稳定
      → L2-A 用 Anchor 坐标而非 BBox 中心估算位置
```

### 4.3 光照估计 → 视觉质量预警

```
ARCore 光照估计: ambient_intensity < 300 lux
  → 预警: "低光照，DINOv2 特征可能不可靠"
    → Identifier 降低 ReID 置信度权重
    → 不主动发起 ReID，仅被动确认
```

### 4.4 信号汇总表

| ARCore 信号 | 来源 | 给 L1 的价值 | 给 L2-A 的价值 |
|:-----------|:-----|:------------|:--------------|
| TrackingState | ARSession | **Tier 分级门控** | 全部节点状态 |
| NotTrackingReason | ARSession | 区分抖动/光照/特征不足 | — |
| Camera Pose | XR Camera | 坐标转换 + 运动估算 | 位置更新 |
| Camera Velocity | 推导 | Tier 判定 | — |
| AR Planes | PlaneManager | — | **承载面节点** |
| AR Anchors | AnchorManager | — | **位置锚定** |
| Light Estimate | LightEstimation | ReID 置信度调节 | — |
| Hand Joints | XR Hands | 手势识别 | HELD_BY 关系 |
| Hit Test | Raycast | — | 用户注视焦点 |

---

## 5. 与 SVA 实践的对比和借鉴

### 5.1 我们能直接学的

| SVA 实践 | 我们的适配 |
|:---------|:----------|
| `VideoForwarder` 多处理器分发 | L1 多处理器架构 (Tracker/Discoverer/Identifier) |
| 不同处理器不同帧率 (fps参数) | Tracker 30fps, Discoverer 2fps, Identifier 触发式 |
| Processor `attach_agent()` 事件注入 | L3 ContextInjector `update_chat_ctx()` |
| YOLO Processor 插件化 | Discoverer 作为可替换组件 |

### 5.2 我们必须自己设计的（SVA 没有）

| 我们独有的需求 | SVA 没有的原因 | 我们的方案 |
|:--------------|:-------------|:----------|
| **稳定性门控** | SVA 假设固定摄像头 | StabilityGate 4级分级 |
| **帧质量过滤** | 固定摄像头不会模糊 | Laplacian 模糊检测 |
| **AR Pose 融合** | SVA 不处理 3D 空间 | PoseAligner 时间同步 |
| **条件启停** | SVA 处理器始终运行 | 按 Tier 动态启停 |
| **On-Demand 模式** | SVA 没有 LLM 驱动的聚焦 | Gemini focus_on → 强制特征提取 |

---

## 6. L1 输出接口 → L2-A/L2-B

```python
@dataclass
class L1Output:
    """L1 每帧/每事件的输出结构"""
    tier: ProcessingTier
    timestamp: float
    skipped: bool = False
    skip_reason: str = ""

    # Tier 1+: 位姿
    camera_pose: tuple | None = None
    ar_planes: list[dict] | None = None

    # Tier 2+: 追踪
    tracks: list[TrackResult] | None = None
    # TrackResult: {track_id, bbox, mask_area, class_label, confidence}

    # Tier 3: 发现 + 识别
    new_objects: list[NewObject] | None = None
    # NewObject: {bbox, class_label, dino_features, confidence}

    all_occluded: bool = False

    def has_meaningful_change(self, previous: "L1Output") -> bool:
        """Diff 门控: 只有有意义的变化才推送给 L2"""
        if self.all_occluded != previous.all_occluded:
            return True
        if self.new_objects:
            return True
        if self.tracks and previous.tracks:
            return self._tracks_changed_significantly(previous.tracks)
        return False
```

---

## 7. 技术栈确认

| L1 组件 | 技术 | 运行位置 | 说明 |
|:--------|:-----|:---------|:-----|
| **Tracker** | SAM2 (云端全尺寸) 全分割追踪 | 阿里云 A10 | 云端无需轻量化，主发现路径 |
| **Discoverer** | YOLO-World (开放词汇检测) | 阿里云 A10 | 仅 Tier 3, 1-2fps，作为可选补充 |
| **Identifier** | DINOv2 ViT-B/14 | 阿里云 A10 | 触发式，非持续运行 |
| **PoseAligner** | 纯 Python 矩阵运算 | CPU | 10Hz, 无 GPU |
| **QualityChecker** | OpenCV Laplacian | CPU | 30fps, 极轻量 |
| **StabilityGate** | 纯 Python 逻辑 | CPU | 10Hz, 无 GPU |

**注意**: 因为我们在阿里云 A10 上运行（不是手机端），SAM2 全尺寸是可以跑的。EdgeTAM (16fps iPhone) 是端侧方案——如果将来需要端云混合部署再考虑。
