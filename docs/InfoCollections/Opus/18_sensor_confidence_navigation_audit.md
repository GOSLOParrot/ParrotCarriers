# 传感器审计 · 节点置信度链路 · 导航能力评估 · 场景推演

> 生成日期: 2026-02-24
> 核心问题:
> 1. 手机传感器到底有多少能用？每个传感器给 DSG 什么价值？
> 2. L1 缓冲功能应该是什么形态？
> 3. 节点置信度完整链路：从传感器到节点，每段会出什么问题？
> 4. 能否做到类似导航的效果？方位感知能力边界在哪？
> 5. 节点生命周期 vs StabilityGate 的适配
> 6. 新一轮场景推演 (聚焦节点系统和置信度)

---

## 1. 手机传感器完整审计

### 1.1 安卓手机 (iQOO Neo9) 可用传感器总览

| 传感器 | 安卓 API | Unity API | 频率 | 给 DSG 的价值 | 当前是否利用 |
|:-------|:---------|:----------|:-----|:-------------|:-----------|
| **加速度计** | SensorManager | `Accelerometer.current` | 100-400Hz | 运动检测、手机姿态辅助 | ⚠️ 间接 (ARCore 用) |
| **陀螺仪** | SensorManager | `Gyroscope.current` | 100-400Hz | 角速度 → StabilityGate 的核心信号 | ✅ 通过 ARCore |
| **磁力计/电子罗盘** | SensorManager | `MagneticFieldSensor` / `Input.compass` | 50-100Hz | **绝对方向 (磁北)**，场景方位辨识 | ❌ 完全未用 |
| **重力传感器** | SensorManager | (融合传感器) | 100Hz | 判断手机朝向 (竖/横/平放) | ❌ 未用 |
| **旋转向量** | TYPE_ROTATION_VECTOR | `AttitudeSensor.current` | 100Hz | 设备绝对姿态 (融合加速度+陀螺+磁力) | ⚠️ ARCore 内部用 |
| **游戏旋转向量** | TYPE_GAME_ROTATION_VECTOR | (通过 ARCore) | 100Hz | 无磁力依赖的相对旋转 | ✅ ARCore 核心 |
| **线性加速度** | TYPE_LINEAR_ACCELERATION | (可访问) | 100Hz | 去除重力后的加速度 → 精确运动检测 | ❌ 未用 |
| **气压计** | TYPE_PRESSURE | (可访问) | 5-50Hz | 相对海拔变化 → **楼层检测** | ❌ 未用 |
| **光线传感器** | TYPE_LIGHT | (可访问) | 5Hz | 环境光照 → 与 ARCore Light Estimation 互补 | ❌ 未用 |
| **接近传感器** | TYPE_PROXIMITY | (可访问) | N/A | 手机放口袋/贴脸 → APP 生命周期辅助 | ❌ 未用 |
| **计步器** | TYPE_STEP_COUNTER | (可访问) | 事件 | 用户走了多少步 → 场景变化线索 | ❌ 未用 |
| **GPS** | LocationManager | `Input.location` | 1Hz | 室外粗定位 | ❌ 未用 (MVP 室内) |

### 1.2 ARCore / AR Foundation 暴露的处理后数据

| 数据 | AR Foundation API | 精度 | 给 DSG 的价值 | 当前是否利用 |
|:-----|:-----------------|:-----|:-------------|:-----------|
| **Camera Pose** (6DoF) | `ARCameraManager.subsystem` | mm 级 (短期) | **L2-A 所有位置计算的基础** | ✅ 核心 |
| **TrackingState** | `ARSession.state` | — | **StabilityGate 门控** | ✅ 核心 |
| **NotTrackingReason** | `ARSession.notTrackingReason` | — | 区分抖动/光照/特征不足 | ✅ |
| **FeatureMapQuality** | `Session.estimateFeatureMapQualityForHosting()` | 3 级 | **锚点可靠性预判** — 映射质量好才值得创建锚点 | ❌ 未用 |
| **AR 平面** | `ARPlaneManager` | cm 级 | 承载面节点、平面边界 | ✅ |
| **平面边界多边形** | `ARPlane.boundary` | cm 级 | 鹦鹉运动范围约束 | ✅ |
| **平面法向量/朝向** | `ARPlane.alignment` | — | 水平/垂直面区分 | ✅ |
| **AR 锚点** | `ARAnchorManager` | mm→cm (衰减) | 物体位置固定 | ✅ 概念有，未深入 |
| **持久化锚点** | `TrySaveAnchorAsync()` | 取决于重定位 | **跨会话场景恢复的关键** | ❌ 未用 |
| **Cloud Anchors** | ARCore Extensions | 取决于 VPS | 多设备共享、长期存储 (1-365天) | ❌ 未用 (需 Cloud) |
| **深度图** | `AROcclusionManager` | ±10-30cm | 物体距离估算、遮挡处理 | ⚠️ 概念有 |
| **光照估计** | `ARCameraManager.requestedLightEstimation` | — | 视觉质量预警 | ✅ 概念有 |
| **环境 HDR** | Environmental HDR mode | — | 主光方向、环境球谐 | ❌ 未用 |
| **Camera Intrinsics** | `XRCameraIntrinsics` | — | 焦距、主点 → 2D→3D 投影 | ⚠️ 间接用 |
| **Hit Test / Raycast** | `ARRaycastManager` | cm 级 | 点击定位、用户注视焦点 | ❌ 未用 |

### 1.3 审计结论: 哪些传感器被浪费了

**关键浪费 (应在 MVP 阶段利用):**

| 传感器 | 为什么浪费了 | 该怎么用 | 优先级 |
|:-------|:-----------|:---------|:-------|
| **磁力计/罗盘** | 完全没接入 | 提供**绝对方向** → "桌子在北面、床在南面" | **P0** |
| **FeatureMapQuality** | 没读取 | 创建锚点前检查质量 → 只在高质量时建锚 | **P0** |
| **持久化锚点** | 概念有但没设计流程 | 跨会话恢复关键物体位置 | **P1** |
| **Hit Test / Raycast** | 完全没用 | 用户点击屏幕 → 精确定位 AR 空间中的点 | **P1** |
| **气压计** | 完全没用 | 楼层变化检测 (从书房上楼到卧室) | **P2** |
| **计步器** | 完全没用 | 用户是否在走路 → 辅助 StabilityGate | **P2** |
| **接近传感器** | 完全没用 | 手机贴脸/放口袋 → APP 生命周期触发 | **P1** |

---

## 2. L1 缓冲功能形态设计

### 2.1 问题: L1 需要什么缓冲？

L1 面临三种需要缓冲的场景:

| 场景 | 不缓冲的后果 | 缓冲什么 |
|:-----|:-----------|:---------|
| **稳定性跳变** | Tier 2→3→2→3 高频切换 → 处理器频繁启停 | 稳定性状态 (滞后缓冲) |
| **帧间一致性** | 每帧独立检测 → 标签跳变 ("cup"→"mug"→"cup") | 分类投票 (时间窗口缓冲) |
| **位置抖动** | 每帧位置微变 → L2-A 收到大量无意义 OBJECT_MOVED | 位置变化 (空间阈值缓冲) |

### 2.2 缓冲形态: 三层独立缓冲，简单优先

```
┌──────────────────────────────────────────────────────────┐
│                    L1 Buffer Architecture                  │
│                                                            │
│  ┌─────────────────┐  简单: 滞后计时器                     │
│  │ StabilityBuffer  │  Tier 升级需持续 0.5s (已有)          │
│  │ (Gate Hysteresis)│  Tier 降级即时 (安全优先)              │
│  └────────┬────────┘  新增: Tier 恢复也需 0.3s 滞后        │
│           │                                                │
│  ┌────────▼────────┐  简单: 滑动窗口投票                   │
│  │  LabelBuffer    │  最近 N 帧 (N=5) 的类别投票           │
│  │ (Class Voting)  │  投票比 > 60% 才确认标签              │
│  └────────┬────────┘  已在 ObjectNode.class_votes 设计     │
│           │                                                │
│  ┌────────▼────────┐  简单: 空间阈值 + EMA 平滑            │
│  │ PositionBuffer  │  位移 < 2cm 不推送 (Desktop)          │
│  │ (Spatial Filter)│  位移 < 5cm 不推送 (Indoor)           │
│  └────────┬────────┘  用指数移动平均平滑位置                │
│           │                                                │
│           ▼                                                │
│     只有通过三层缓冲的变化才作为 L1Event 输出               │
└──────────────────────────────────────────────────────────┘
```

### 2.3 具体实现: 比当前设计更简单还是更复杂？

**答: 比当前设计稍微复杂一点，但每个缓冲器本身极简。**

当前设计只有 `StabilityGate` 一层缓冲 + `FrameQualityChecker` 一层过滤。缺少标签缓冲和位置缓冲。

```python
class PositionBuffer:
    """位置抖动过滤 — 极简 EMA + 阈值"""

    def __init__(self, alpha: float = 0.3, threshold: float = 0.02):
        self._alpha = alpha
        self._threshold = threshold
        self._smoothed: dict[str, tuple] = {}  # uuid → smoothed position

    def update(self, uuid: str, raw_pos: tuple[float, float, float]) -> tuple | None:
        """返回 None 表示变化不显著 (不推送)"""
        if uuid not in self._smoothed:
            self._smoothed[uuid] = raw_pos
            return raw_pos

        old = self._smoothed[uuid]
        new = tuple(
            self._alpha * r + (1 - self._alpha) * s
            for r, s in zip(raw_pos, old)
        )
        self._smoothed[uuid] = new

        delta = sum((a - b) ** 2 for a, b in zip(new, old)) ** 0.5
        return new if delta > self._threshold else None

class LabelBuffer:
    """标签投票缓冲 — 滑动窗口"""

    def __init__(self, window: int = 5, min_ratio: float = 0.6):
        self._window = window
        self._min_ratio = min_ratio
        self._votes: dict[int, list[str]] = {}  # track_id → recent labels

    def vote(self, track_id: int, label: str) -> str | None:
        """返回 None 表示还不确定"""
        if track_id not in self._votes:
            self._votes[track_id] = []
        buf = self._votes[track_id]
        buf.append(label)
        if len(buf) > self._window:
            buf.pop(0)
        if len(buf) < 3:
            return None
        from collections import Counter
        counts = Counter(buf)
        best, count = counts.most_common(1)[0]
        return best if count / len(buf) >= self._min_ratio else None
```

### 2.4 缓冲参数与 SceneProfile 的关系

| 参数 | Desktop | Indoor | 原因 |
|:-----|:--------|:-------|:-----|
| position_threshold | 0.02m (2cm) | 0.05m (5cm) | 桌面物体精度高 |
| position_alpha (EMA) | 0.3 | 0.5 | 室内运动更剧烈 |
| label_window | 5 帧 | 3 帧 | 室内物体更大更容易识别 |
| stability_upgrade_delay | 0.5s | 0.3s | 室内更宽容 |
| stability_downgrade_delay | 0s | 0s | 安全优先，立刻降级 |

---

## 3. 节点置信度完整链路

### 3.1 链路全景图: 从传感器到节点置信度

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
传感器层            加工层              节点层           判断层
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

[Camera RGB]─────→[SAM2 mask]──────→[ObjectNode]─────→ 物体存在吗？
   │ 问题①           │ 问题②           │ 问题⑤         confidence
   │                  │                  │
[ARCore Pose]────→[3D投影]──────────→[position_3d]───→ 物体在哪？
   │ 问题③           │ 问题④           │ 问题⑥         position_cov
   │                  │                  │
[ARCore Plane]───→[ON_SURFACE推断]──→[SpatialEdge]───→ 关系对吗？
   │ 问题⑦                              │ 问题⑨         edge.confidence
   │                                     │
[DINOv2]─────────→[ReID匹配]────────→[uuid确认]─────→ 这是同一个物体吗？
   │ 问题⑧                              │ 问题⑩         reid_score
   │                                     │
[磁力计/罗盘]────→[绝对方向]─────────→[方位标记]─────→ 场景方位对吗？
   │ 问题⑪                              │ 问题⑫         heading_conf
   │                                     │
[Graphiti]───────→[记忆检索]─────────→[语义标签]─────→ 我认识这个物体吗？
   │ 问题⑬                              │ 问题⑭         memory_match_score
   │                                     │
[持久化锚点]─────→[锚点重定位]───────→[位置恢复]─────→ 这是上次的位置吗？
   │ 问题⑮                              │ 问题⑯         anchor_resolved
   │                                     │
                                    ┌────▼────┐
                                    │ 综合    │
                                    │ 置信度  │
                                    │ 评估    │
                                    └─────────┘
```

### 3.2 每段链路的问题分析

#### 问题① Camera RGB 质量

| 问题 | 发生条件 | 影响 | 检测方法 | 缓解方案 |
|:-----|:---------|:-----|:---------|:---------|
| **运动模糊** | 用户快速转动手机 | SAM2 mask 形变或丢失 | Laplacian 方差 (已有 FrameQualityChecker) | Tier 降级，跳过模糊帧 |
| **低光照** | 夜间/暗处 | 噪点多，特征不可靠 | ARCore Light Estimation + 光线传感器 | 降低 ReID 权重，提高 position_cov |
| **过曝/逆光** | 窗户/灯光直射 | 部分区域全白 | 直方图分析 | 标记受影响区域的物体 confidence↓ |
| **WebRTC 压缩** | 带宽不足 | 细节丢失，小物体不可见 | 对比帧分辨率和码率 | 大物体 confidence 不变，小物体 ↓ |

#### 问题② SAM2 mask 质量

| 问题 | 发生条件 | 影响 | 检测方法 | 缓解方案 |
|:-----|:---------|:-----|:---------|:---------|
| **mask 漂移** | 物体被部分遮挡 | mask 覆盖错误区域 | mask 面积突变 (>50%/帧) | 标记为 OCCLUDED，暂停位置更新 |
| **多物体粘连** | 紧邻物体 | 一个 mask 覆盖两个物体 | mask 面积异常大 | 触发 Discoverer 重新检测 |
| **track ID 跳变** | 快速运动后恢复 | 同物体新 ID | ReID 匹配 | DINOv2 embedding 比对 |

#### 问题③ ARCore Pose 精度

| 问题 | 发生条件 | 影响 | 检测方法 | 缓解方案 |
|:-----|:---------|:-----|:---------|:---------|
| **短期漂移** | 正常使用 (分钟级) | 位置误差累积 1-5cm | FeatureMapQuality 检查 | position_cov 随时间增长 |
| **长期漂移** | 长时间使用 (小时级) | 全局坐标偏移 10cm+ | 锚点偏移检测 | 定期重锚 (re-anchor) |
| **追踪丢失恢复** | 快速转动后 | 新 Pose 可能跳变 | TrackingState 从 None→Tracking | 恢复后 0.5s 内 position_cov 放大 |
| **特征不足区域** | 纯白墙壁、反光表面 | Pose 质量下降 | NotTrackingReason: InsufficientFeatures | 对该时段所有位置更新降权 |

#### 问题④ 3D 投影精度

| 问题 | 发生条件 | 影响 | 检测方法 | 缓解方案 |
|:-----|:---------|:-----|:---------|:---------|
| **深度估计误差** | 单目深度 API | 物体 Z 轴位置误差 ±10-30cm | 与 AR 平面高度交叉验证 | 优先用平面约束而非深度图 |
| **Camera Intrinsics 不匹配** | WebRTC 缩放帧 | 2D→3D 投影偏移 | 比对原始/传输分辨率 | 用传输帧尺寸的 intrinsics |

#### 问题⑤ ObjectNode 存在判定

| 问题 | 发生条件 | 影响 | 检测方法 | 缓解方案 |
|:-----|:---------|:-----|:---------|:---------|
| **假阳性** (不存在的物体) | 反射/阴影/图案 | 幽灵节点 | 短期存在 + 低 confidence | TTL 机制: 低 confidence 短时间存活 |
| **假阴性** (存在但没发现) | 被遮挡/太小/离焦 | 缺失节点 | 无法直接检测 | 多帧扫描 + Discoverer 定期全局搜索 |
| **重复节点** (同物体多个) | track ID 跳变 | 图"爆炸" | DINOv2 embedding 距离 < 阈值 | ReID 合并 + ObjectNode.vote_class |

#### 问题⑥ position_3d 精度

| 问题 | 发生条件 | 影响 | 检测方法 | 缓解方案 |
|:-----|:---------|:-----|:---------|:---------|
| **坐标系漂移** | ARCore 累计误差 | 所有物体位置整体偏移 | 锚点位置对比 | 定期 re-anchor |
| **抖动** | 帧间 pose 微变 | L2-A 收到大量 MOVED | delta < 阈值检查 | PositionBuffer (§2) |

#### 问题⑦ AR Plane 可靠性

| 问题 | 发生条件 | 影响 | 检测方法 | 缓解方案 |
|:-----|:---------|:-----|:---------|:---------|
| **平面消失** | 视角变化/遮挡 | Surface 节点变 LOST | ARPlane.removed 事件 | 不立刻删除，保持 5 分钟 TTL |
| **平面合并/分裂** | ARCore 估计修正 | Surface UUID 变化 | ARPlane.updated + ID 变化 | 用面积重叠检测合并 |
| **漏检** | 材质原因 (玻璃桌面) | 缺少承载面 | 物体悬浮在空中 | fallback: 根据物体位置虚拟创建平面 |

#### 问题⑧ DINOv2 特征质量

| 问题 | 发生条件 | 影响 | 检测方法 | 缓解方案 |
|:-----|:---------|:-----|:---------|:---------|
| **视角差异** | 从不同角度看同一物体 | embedding 距离增大 → 误判为不同物体 | 匹配分数边际情况 | 多视角特征融合 (学 ConceptGraphs) |
| **光照变化** | 白天→晚上看同一物体 | embedding 距离增大 | 光照估计值差异大 | 跨光照训练 or 降低匹配阈值要求 |
| **遮挡** | 物体部分被挡 | 局部特征不同 | mask 面积 < 原始面积 50% | 部分遮挡时不更新 embedding |

#### 问题⑨ 空间关系推断

| 问题 | 发生条件 | 影响 | 检测方法 | 缓解方案 |
|:-----|:---------|:-----|:---------|:---------|
| **ON_SURFACE 误判** | 物体恰好在 Surface Y+阈值 | 不在桌上却判定在桌上 | depth 和 plane 高度交叉验证 | 增加 Y 轴容差和 plane boundary 检查 |
| **NEAR 距离失真** | 深度估计误差 | 远处物体被认为 NEAR | 深度置信区间 | NEAR.distance 标注精度等级 |

#### 问题⑩ ReID 合并误差

| 问题 | 发生条件 | 影响 | 检测方法 | 缓解方案 |
|:-----|:---------|:-----|:---------|:---------|
| **错误合并** | 两个相似物体 (两个杯子) | UUID 混淆 | 合并后位置跳变 | 要求 embedding 距离 + 类别一致 + 位置连续 |
| **未合并** | 同一物体特征差异大 | 重复节点 | 图中同位置多个同类节点 | 降低阈值 or 增加匹配候选 |

#### 问题⑪ 磁力计/罗盘可靠性

| 问题 | 发生条件 | 影响 | 检测方法 | 缓解方案 |
|:-----|:---------|:-----|:---------|:---------|
| **电磁干扰** | 靠近电器/金属 | heading 偏差 10-30° | heading 突变检测 | 用 ARCore pose 的 yaw 互校 |
| **标定缺失** | 用户从未做"画 8 字"标定 | 磁力计完全不准 | heading 方差过大 | 降级: 不使用绝对方向，只用相对 |

#### 问题⑫ 方位标记精度

| 问题 | 发生条件 | 影响 | 检测方法 | 缓解方案 |
|:-----|:---------|:-----|:---------|:---------|
| **室内磁场扭曲** | 钢筋混凝土建筑 | 房间不同位置 heading 不同 | 移动时 heading 大幅变化 | 用统计平均而非瞬时值 |

#### 问题⑬ Graphiti 检索质量

| 问题 | 发生条件 | 影响 | 检测方法 | 缓解方案 |
|:-----|:---------|:-----|:---------|:---------|
| **无匹配** | 全新物体 | 无语义标签可加载 | search 返回空 | 正常 — 新物体就是没记忆 |
| **错误匹配** | 搜索词模糊 ("cup" 匹配到错误杯子) | 错误标签 | 检索分数低 | 结合 DINOv2 embedding 交叉验证 |

#### 问题⑭ 语义标签可信度

| 问题 | 发生条件 | 影响 | 检测方法 | 缓解方案 |
|:-----|:---------|:-----|:---------|:---------|
| **过时信息** | 物体被移动/替换后记忆还是旧的 | "杯子在桌上"但杯子不在了 | 视觉验证与记忆矛盾 | L2-B 优先信任实时观测 |

#### 问题⑮ 持久化锚点可靠性

| 问题 | 发生条件 | 影响 | 检测方法 | 缓解方案 |
|:-----|:---------|:-----|:---------|:---------|
| **重定位失败** | 环境变化大 (家具搬了) | 锚点无法解析 | TryLoadAnchorAsync 失败 | fallback: 从头扫描，不依赖旧锚 |
| **位置偏移** | ARCore 重定位误差 | 旧锚点位置偏移 5-10cm | 与当前平面对比 | 锚点恢复后做一次交叉验证 |

#### 问题⑯ 跨会话位置恢复

| 问题 | 发生条件 | 影响 | 检测方法 | 缓解方案 |
|:-----|:---------|:-----|:---------|:---------|
| **坐标系不一致** | 新 session 新坐标系原点 | 旧 position_3d 全部无效 | 锚点坐标变化 | 用锚点做坐标系对齐变换 |

### 3.3 综合置信度评估模型

```python
@dataclass
class NodeConfidence:
    """节点综合置信度 — 多因素加权"""

    # 各维度置信度 [0, 1]
    tracking_confidence: float = 0.0    # SAM2 追踪质量
    position_confidence: float = 0.0    # 位置精度
    identity_confidence: float = 0.0    # ReID / 分类确认度
    memory_confidence: float = 0.0      # Graphiti 记忆匹配度
    anchor_confidence: float = 0.0      # AR 锚点可靠性
    temporal_confidence: float = 0.0    # 时间衰减因子

    # 来源记录
    factors: dict[str, float] = field(default_factory=dict)

    @property
    def overall(self) -> float:
        """加权综合分"""
        weights = {
            "tracking": 0.30,
            "position": 0.25,
            "identity": 0.20,
            "memory": 0.10,
            "anchor": 0.10,
            "temporal": 0.05,
        }
        return (
            weights["tracking"] * self.tracking_confidence +
            weights["position"] * self.position_confidence +
            weights["identity"] * self.identity_confidence +
            weights["memory"] * self.memory_confidence +
            weights["anchor"] * self.anchor_confidence +
            weights["temporal"] * self.temporal_confidence
        )

def compute_tracking_confidence(
    tier: int,
    mask_area_ratio: float,   # mask面积变化率 (稳定=1.0)
    blur_score: float,
    light_level: float,
) -> float:
    """追踪置信度: 基于 Tier + 帧质量"""
    tier_factor = {0: 0.0, 1: 0.2, 2: 0.6, 3: 1.0}[tier]
    mask_factor = min(1.0, mask_area_ratio)  # 面积突变 → 不可信
    blur_factor = min(1.0, blur_score / 200)  # 模糊 → 不可信
    light_factor = min(1.0, light_level / 500)  # 暗 → 不可信
    return tier_factor * 0.4 + mask_factor * 0.3 + blur_factor * 0.15 + light_factor * 0.15

def compute_position_confidence(
    tier: int,
    feature_map_quality: int,  # ARCore 0/1/2
    has_anchor: bool,
    time_since_anchor: float,
    depth_available: bool,
) -> float:
    """位置置信度: 基于 ARCore 质量 + 锚点 + 深度"""
    tier_factor = {0: 0.0, 1: 0.3, 2: 0.7, 3: 1.0}[tier]
    quality_factor = feature_map_quality / 2.0  # 0→0, 1→0.5, 2→1.0
    anchor_factor = 1.0 if has_anchor else 0.5
    anchor_decay = max(0.5, 1.0 - time_since_anchor / 600)  # 10分钟衰减到0.5
    depth_bonus = 0.1 if depth_available else 0.0
    return (
        tier_factor * 0.3 +
        quality_factor * 0.25 +
        anchor_factor * anchor_decay * 0.35 +
        depth_bonus
    )

def compute_identity_confidence(
    class_vote_ratio: float,    # 投票最高比例
    reid_score: float,          # DINOv2 匹配分
    has_user_name: bool,        # 用户主动命名过
    graphiti_match_score: float,
) -> float:
    """身份置信度: 基于分类+ReID+记忆"""
    class_factor = class_vote_ratio
    reid_factor = reid_score if reid_score > 0 else 0.5
    name_bonus = 0.2 if has_user_name else 0.0
    memory_factor = graphiti_match_score * 0.3
    return min(1.0, class_factor * 0.4 + reid_factor * 0.3 + name_bonus + memory_factor)
```

---

## 4. 导航与方位感知能力评估

### 4.1 能用什么信息做"导航"？

用户的问题: "我有了我家里的平面地图，能用什么信息来导航？"

**先明确: 我们能做的不是 SLAM 级别的全局导航，而是"局部空间记忆 + 方位标记"。**

可用的导航线索:

| 线索 | 来源 | 精度 | 持久性 | 可用性 |
|:-----|:-----|:-----|:-------|:-------|
| **AR 平面地图** | ARCore PlaneManager | cm 级 | ❌ 仅当前 session | ✅ MVP |
| **持久化锚点** | ARCore Persistent Anchors | cm 级 (初始) | ✅ 跨 session (条件好时) | ⚠️ 需实测 |
| **Cloud Anchors** | ARCore Cloud | cm 级 | ✅ 1-365 天 | ⚠️ 需 Cloud |
| **磁力计方向** | 电子罗盘 | ±5-15° | ✅ 绝对方向 | ✅ 但受干扰 |
| **相对位移** | ARCore Pose 积分 | cm→m 级漂移 | ❌ 仅短期 | ✅ |
| **气压高度** | 气压计 | ±0.5m | ✅ 绝对海拔 | ✅ (楼层) |
| **视觉场景特征** | DINOv2 / 环境特征 | 房间级 | ⚠️ 依赖视觉模型 | Phase 2 |
| **物体空间记忆** | Graphiti + L2-A | 物体级 | ✅ 长期 | ✅ |

### 4.2 "这个方位前有桌子"能做到吗？

**能做到，但有条件。**

实现方案:

```python
class SpatialOrientation:
    """空间方位感知: 结合 ARCore Pose + 罗盘 + 平面/物体记忆"""

    def get_absolute_heading(self, telemetry: dict) -> float | None:
        """获取绝对朝向 (度, 0=北, 顺时针)"""
        compass = telemetry.get("compass_heading")
        if compass is None:
            return None
        ar_yaw = telemetry.get("camera_yaw")
        # 如果两者差异 < 20°, 用罗盘; 否则不可信
        if ar_yaw is not None and abs(compass - ar_yaw) > 20:
            return None  # 磁场干扰
        return compass

    def label_directions(
        self,
        camera_pose: tuple,
        heading: float,
        objects: list[ObjectNode],
    ) -> dict[str, list[str]]:
        """标记各方位的物体"""
        directions = {"前方": [], "后方": [], "左方": [], "右方": []}
        cam_x, cam_y, cam_z = camera_pose[:3]

        for obj in objects:
            dx = obj.position_3d[0] - cam_x
            dz = obj.position_3d[2] - cam_z
            angle = math.degrees(math.atan2(dx, -dz))  # 相对角度
            relative = (angle - heading + 360) % 360

            if relative < 45 or relative > 315:
                directions["前方"].append(obj.class_label)
            elif 45 <= relative < 135:
                directions["右方"].append(obj.class_label)
            elif 135 <= relative < 225:
                directions["后方"].append(obj.class_label)
            else:
                directions["左方"].append(obj.class_label)

        return directions

    def describe_scene_layout(self, directions: dict) -> str:
        """生成方位描述给 Gemini"""
        parts = []
        for d, objs in directions.items():
            if objs:
                parts.append(f"{d}: {', '.join(objs[:3])}")
        return "; ".join(parts)
        # 例: "前方: 桌子, 显示器; 左方: 书架; 右方: 窗户"
```

**实际效果预期:**

| 能力 | 能否做到 | 条件 | MVP? |
|:-----|:---------|:-----|:-----|
| "前方有桌子" | ✅ 可以 | 当前 session 内物体被追踪过 | ✅ |
| "北面有桌子" | ⚠️ 有时可以 | 磁力计可用且不受干扰 | P1 |
| "这是上次那个桌子" | ⚠️ 有条件 | 持久化锚点成功重定位 | P1 |
| "从客厅去厨房怎么走" | ❌ 做不到 | 需要完整 SLAM 地图 | 不在计划内 |
| "楼上有什么" | ⚠️ 可以标记 | 气压计检测楼层变化 | P2 |

### 4.3 增强节点真实性的有效特征

| 特征 | 来源 | 如何增强节点 | 建议 |
|:-----|:-----|:-----------|:-----|
| **FeatureMapQuality** | ARCore | 只在 quality=2 时创建持久锚点 → 位置更可信 | **P0 接入** |
| **罗盘方向** | 磁力计 | 物体带绝对方位标签 → 跨 session 可对齐 | **P1 接入** |
| **平面交叉验证** | AR Plane Y vs 物体 Y | ON_SURFACE 关系更可靠 | **P0 增强** |
| **多帧累积** | LabelBuffer | 类别标签更稳定 | **P0 (§2 已设计)** |
| **锚点存在** | ARAnchorManager | has_anchor=True → 位置 confidence 大幅提升 | **P0 利用** |
| **用户命名** | remember Tool | 用户说"这是奶奶的杯子" → identity 100% | **MVP 已有** |
| **Graphiti 匹配** | 跨 session 搜索 | 历史一致 → 记忆增强 confidence | **Phase 3** |

---

## 5. 节点生命周期 vs StabilityGate 适配

### 5.1 当前节点状态设计 (来自 17_dsg_node_and_trigger_design.md)

```
ACTIVE → OCCLUDED → OUT_OF_VIEW → LOST → (删除或归档)
  ↑                                          ↑
  └──── ANCHORED (有 ARCore 锚点固定) ───────┘
```

### 5.2 StabilityGate 对节点状态的影响 — 完整矩阵

| StabilityGate Tier | 节点状态变化规则 | 理由 |
|:-------------------|:----------------|:-----|
| **Tier 0 (Lost)** | 所有 ACTIVE 节点 → OCCLUDED (不是 LOST!) | 追踪丢了但物体没消失 |
| **Tier 0 → Tier 2+** | OCCLUDED 节点: 如果 SAM2 重新追踪到 → ACTIVE; 超时未找到 → 保持 OCCLUDED | 恢复追踪后验证 |
| **Tier 1 (Shaking)** | ACTIVE 节点保持 ACTIVE 但 position_confidence ↓ | 位置不可信但物体还在 |
| **Tier 1 持续 > 5s** | ACTIVE 且无锚点 → position_cov 放大 2x | 长时间抖动位置漂移 |
| **Tier 2 (Moving)** | 正常追踪; 不发现新物体; 不做 ReID | 追踪现有但不扩展 |
| **Tier 3 (Stable)** | 全功能; 允许创建锚点 + ReID + 新物体发现 | 最可信时段 |
| **任何 Tier** | ANCHORED 节点的 position 从锚点获取而非追踪 | 锚点比追踪更稳定 |

### 5.3 不同场景下节点生命周期差异

**Desktop 场景:**

```
物体初次出现:
  [L1 发现] → ACTIVE (confidence=0.6, 待投票确认)
  [3帧后投票通过] → ACTIVE (confidence=0.8)
  [创建锚点] → ANCHORED (confidence=0.9)
  [Graphiti 匹配] → ANCHORED (confidence=0.95)

物体被手拿起:
  ANCHORED → ACTIVE (跟随手部位置, 锚点断开)
  [放回桌面] → 如果在原锚点附近 → 恢复 ANCHORED
              如果在新位置 → 创建新锚点

手机抖了一下 (Tier 3→2→3):
  节点保持 ACTIVE/ANCHORED, 只是 2s 内不发现新物体

用户拿走手机 (Tier 0):
  所有节点 → OCCLUDED
  [30s 未恢复] → OUT_OF_VIEW
  [5min 未恢复] → LOST (但 Graphiti 记忆还在)
```

**Indoor 场景:**

```
大家具 (沙发/电视):
  [首次发现] → ACTIVE (confidence=0.7)
  [创建锚点] → ANCHORED (confidence=0.9)
  [离开视野] → OUT_OF_VIEW (不删除! 大家具不会被搬走)
  [重新看到] → ACTIVE (ReID 确认后 → ANCHORED)

  TTL 策略: 大家具不设 TTL — 永远不从图中删除
            (符合物理恒常性: 沙发不会凭空消失)

小物品 (遥控器/杂志):
  TTL 策略: OUT_OF_VIEW 30min → LOST → 降权保留
            (小物品可能被移走)

移动中的人:
  [发现] → ACTIVE
  [走出视野] → OUT_OF_VIEW (5s)
  [5min 未见] → LOST → 删除 (人会离开)
```

### 5.4 TTL (Time-To-Live) 策略表

| 节点类型 | OCCLUDED → OUT_OF_VIEW | OUT_OF_VIEW → LOST | LOST → 删除 | 理由 |
|:---------|:----------------------|:-------------------|:-----------|:-----|
| 小物体 (杯子/笔) | 3s | 5min | 30min | 可能被移走 |
| 大物体 (显示器/椅子) | 5s | ∞ (不自动) | ∞ (不删除) | 大家具不会消失 |
| 承载面 (桌面) | 10s | ∞ | ∞ | 桌子不会消失 |
| 手部 | 1s | 5s | 10s | 手经常进出视野 |
| 人物 | 3s | 1min | 5min | 人会走 |
| 锚点物体 (ANCHORED) | 不适用 | ∞ (锚点保护) | 仅手动删 | 锚点 = 物理恒常性的技术保障 |

---

## 6. 新一轮场景推演 (聚焦节点置信度和传感器利用)

### 场景 A: 第二天回到同一张桌子 (跨会话恢复)

**情景:** 昨天在桌上识别了 8 个物体、创建了持久化锚点。今天打开 APP。

```
Day 1 (昨天):
  正常使用 → 8 个物体 ANCHORED → 持久化锚点保存
  session 结束 → L2-A 折叠 → Graphiti 归档

Day 2 (今天):
  打开 APP → 手机对着桌面
  
  00:00 ARCore 初始化 → 新坐标系原点
        尝试恢复持久化锚点...
        
  情况 A: 锚点恢复成功 (环境没太大变化)
    → 旧坐标系通过锚点对齐到新坐标系
    → L2-A 展开昨天的桌面场景快照
    → 8 个物体以 ANCHORED 状态恢复
    → position_confidence = 0.7 (锚点恢复但未视觉验证)
    → L1 Tier 3 扫描 → SAM2 找到 6 个物体 (2个被移走了)
    → ReID: DINOv2 匹配 → 5 个确认 (1个光照变化太大)
    → 确认的: confidence → 0.95; 未确认的: confidence → 0.5
    → 被移走的: ANCHORED → OUT_OF_VIEW (锚点还在但物体不在)
    
  情况 B: 锚点恢复失败 (家具搬了/光照差)
    → 无法对齐旧坐标系
    → L2-A 从头开始，Graphiti 记忆仍可搜索
    → L1 发现 "蓝色杯子" → L2-B Graphiti 搜索命中 → 知道这是奶奶的杯子
    → identity_confidence = 0.8 (记忆匹配 + DINOv2 匹配)
    → 但 position 是全新的 (旧 position 无效)
```

**发现的问题:**

**问题 A1: 没有锚点恢复流程设计**

当前设计提到了持久化锚点的概念，但完全没有设计**恢复流程**：
- 什么时候尝试加载？
- 加载失败怎么办？
- 加载成功后怎么和旧的 L2-A 快照对齐？

```
补丁: 需要一个 AnchorRecoveryManager:
  1. APP 启动时: 从本地存储读取上次保存的锚点 GUID 列表
  2. 尝试 TryLoadAnchorAsync() 加载前 N 个锚点
  3. 成功 → 用锚点位置做坐标系对齐变换
  4. 失败 → 通知 L3: "无法恢复上次的空间，将从头开始"
  5. 部分成功 → 仅恢复成功锚点对应的物体
```

**问题 A2: 锚点恢复后的视觉验证缺失**

锚点告诉我们"物体应该在这个位置"，但物体可能已经不在了。需要**视觉验证**来确认。

```
补丁: 锚点恢复后的验证流程:
  1. 恢复 ANCHORED 状态，confidence = 0.5 (待验证)
  2. L1 优先扫描锚点附近区域
  3. 如果 SAM2 + ReID 确认 → confidence → 0.95
  4. 如果视觉找不到 → 保持 ANCHORED 但标记 "unverified"
  5. 超过 1min 未验证 → ANCHORED → OUT_OF_VIEW
```

---

### 场景 B: 用户转身 180° 再转回来 (短暂遮挡)

**情景:** 桌面场景，用户转头看了一眼窗户 (2 秒)，然后转回来。

```
00:00 桌面 8 个物体全 ACTIVE, Tier 3

00:01 用户转头 → 相机朝向窗户
      ARCore: angular_velocity 高 → Tier 2→1
      L1: Tier 1 → 仅惯性预测
      所有桌面物体离开视野 → SAM2 追踪全丢
      
      ⚠️ 此时节点该怎么办？
      
      选项 A: 全部 → OCCLUDED (当前设计)
      选项 B: 全部 → OUT_OF_VIEW
      
      正确答案: 区分！
        有锚点的 → 保持 ANCHORED (锚点不会因为你转个头就失效)
        无锚点的 → OCCLUDED (短暂遮挡)
      
00:03 用户转回来 → Tier 1→2→3
      L1: SAM2 重新追踪 → 找到 7 个 (1 个被手挡了)
      ReID 快速确认
      
      ⚠️ 问题: ReID 需要重新跑一遍所有物体吗？
      
      优化: 2 秒内回来 → 位置接近 → 跳过 ReID, 直接用 track ID 续接
      （因为 SAM2 可能分配了新 track ID，但位置变化 < 5cm）
```

**发现的问题:**

**问题 B1: 短暂转头 vs 真正离开的判断**

2 秒转头和 10 秒走到厨房对节点的处理应该完全不同。当前设计没有区分。

```
补丁: 引入"遮挡计时器"概念:
  物体从 ACTIVE 变为不可见时:
    if has_anchor: 保持 ANCHORED, 不变
    else: → OCCLUDED, 开始计时
      < 3s 重新出现 → 直接恢复 ACTIVE (不做 ReID)
      3s-30s → 需要 ReID 确认
      > 30s → OUT_OF_VIEW
      > 5min → LOST
```

**问题 B2: SAM2 track ID 续接**

SAM2 可能在转回来后给同一个物体分配新的 track_id。当前靠 ReID 解决，但**2 秒内的简单续接不需要这么重**。

```
补丁: L2-A 位置匹配的快速续接:
  新 track 出现时:
  1. 先检查: 是否有 OCCLUDED 节点在附近 (< 5cm)?
  2. 如果有且时间 < 3s → 直接续接 UUID, 跳过 ReID
  3. 否则 → 正常 ReID 流程
  这避免了不必要的 DINOv2 计算
```

---

### 场景 C: 多个相似物体 (两个白色杯子)

**情景:** 桌上有两个几乎一样的白色杯子，距离 20cm。

```
00:00 L1 发现两个 "cup", 各自有 track_id
      DINOv2 embedding 距离 = 0.15 (非常接近!)
      
      ⚠️ ReID 会把它们合并吗？
      
00:01 杯子 A 在左边, 杯子 B 在右边
      如果只看 embedding → 可能误合并
      如果结合位置 → 20cm 距离 → 不合并 ✅
      
00:03 用户把杯子 A 拿到右边 (位置交换)
      杯子 A 和 B 都在视野中
      SAM2 追踪到两个各自的 track → 不混淆 ✅
      
00:05 用户拿起杯子 A 离开视野, 再放回来
      杯子 A 的 track_id 断了
      新 track 出现在右边
      ReID: DINOv2 匹配 → 杯子 A 和杯子 B 都匹配! 距离都是 ~0.15
      
      ⚠️ 怎么选？
```

**发现的问题:**

**问题 C1: 相似物体的 ReID 歧义**

DINOv2 embedding 对视觉相似物体无法区分。需要额外的区分因素。

```
补丁: ReID 匹配应该是多因素的:
  score = α * embedding_similarity 
        + β * position_proximity      # 位置越近越可能是同一个
        + γ * time_recency            # 最近消失的更可能回来
        + δ * surface_consistency     # 在同一个 Surface 上更可能

  当多个候选分数接近时 (差 < 0.1):
    → 优先选最近消失的 (time_recency)
    → 如果还是不确定 → 创建新 UUID, 不强制合并
    → L3 通知 Gemini: "有两个类似的杯子，不太确定是哪个"
```

---

### 场景 D: 鹦鹉被指示"飞到厨房的水壶旁" (跨场景导航)

**情景:** 用户在桌面场景，说"去看看厨房的水壶"。水壶在上一个 session 被发现过。

```
00:00 桌面场景 DESKTOP
      Gemini 收到: "去看看厨房的水壶"
      
      Gemini → Tool: fly_to("水壶")
      
      L2-A 搜索 "水壶": 
        当前场景: 没有
        冻结场景: indoor_last 里有 "kettle" (但是冻结的快照)
        Graphiti: objects 分区有 "水壶" 记录
      
      ⚠️ 问题: 鹦鹉能飞到冻结场景中的位置吗？

      答案: 不能直接飞! 因为:
        1. 冻结场景的坐标系可能已失效 (不同 session)
        2. 水壶可能被移走了
        3. 要到厨房需要先切换场景
      
      正确流程:
        1. fly_to 返回: "水壶不在当前场景中，上次在厨房看到"
        2. Gemini 告诉用户: "水壶上次是在厨房的，我们过去看看？"
        3. 用户拿手机走到厨房
        4. 场景切换 → INDOOR
        5. L1 扫描 → 发现水壶 → ReID 确认
        6. fly_to 再次执行 → 成功
```

**发现的问题:**

**问题 D1: fly_to 的跨场景降级策略**

当前 `fly_to` 没有处理"目标在另一个场景"的情况。

```
补丁: fly_to 的搜索优先级:
  1. 当前 L2-A ACTIVE/ANCHORED 物体 → 直接飞
  2. 当前 L2-A OUT_OF_VIEW 物体 (有锚点) → 飞到锚点位置
  3. 冻结场景中的物体 → 返回 "目标在 {场景名} 中, 上次位置: {位置描述}"
  4. Graphiti 记忆中的物体 → 返回 "记忆中在 {位置}, 但需要先过去确认"
  5. 都找不到 → "不认识这个物体"
```

---

### 场景 E: 30分钟后场景变化 (物体被动移动)

**情景:** 用户把手机放在支架上对着桌面，去做了30分钟的事情。期间室友来拿走了杯子。

```
00:00 桌面 8 个物体, 手机稳定 Tier 3

00:15 室友的手进入视野
      L1: 检测到 "hand" (但不是用户的手!)
      L2-A: add HandNode
      L2-B: attention↑ (新事件)
      室友拿走蓝色杯子
      L1: "blue_cup" track 突然消失
      L2-A: "blue_cup" ACTIVE → OCCLUDED → (3s) → OUT_OF_VIEW
      L2-B: trigger OBJECT_LOST
      L3 → Gemini: "[SCENE] 蓝色杯子被拿走了"
      Gemini (鹦鹉可能): "啊！奶奶的杯子被拿走了..."
      
00:16 室友离开
      L1: hand track 丢失
      
00:30 用户回来
      看到鹦鹉在桌上, 杯子不在了
      鹦鹉: "主人！刚才有人来把你的蓝色杯子拿走了！"
      
      ⚠️ 鹦鹉怎么知道是"有人"拿走的而不是自己消失的？
```

**发现的问题:**

**问题 E1: 物体消失原因的推断**

当前只知道物体 LOST，不知道**为什么** LOST。消失原因影响鹦鹉的反应:

| 消失原因 | 线索 | 鹦鹉应该的反应 |
|:---------|:-----|:-------------|
| 被人拿走 | 手出现→物体消失 (时间窗口 < 2s) | "有人拿走了你的杯子" |
| 自然移出视野 | 用户转头 (camera_angular 高) | 不提 (转回来就好了) |
| 追踪丢失 | Tier 降到 0-1 | 不提 (技术原因) |
| 不明原因消失 | 物体突然不在了, 无手/无运动 | "奇怪, 杯子好像不见了？" |

```
补丁: L2-A 物体消失时记录 disappearance_context:
  @dataclass
  class DisappearanceContext:
      timestamp: float
      tier_at_time: int
      hand_visible: bool          # 消失时有手在附近
      hand_distance: float        # 手与物体距离
      camera_moving: bool         # 相机在动
      nearby_objects_stable: bool # 周围物体还在 (排除追踪故障)
      
  推断规则:
    hand_visible + hand_distance < 0.3m → "被人拿走"
    camera_moving → "可能离开视野" (不报告)
    nearby_stable + !hand → "不明原因消失" (报告)
    tier < 2 → "追踪不稳定" (不报告, 等恢复)
```

---

### 场景 F: 手机从横屏切到竖屏 (姿态突变)

**情景:** 用户把手机从支架上拿起来竖着拿。

```
00:00 手机横屏在支架上, Tier 3
      ARCore 坐标系基于当前横屏方向

00:01 用户拿起手机, 转为竖屏
      重力方向不变, 但屏幕方向变了
      ARCore: 追踪继续 (6DoF Pose 不受屏幕方向影响)
      SAM2: 输入帧旋转了 90° → mask 可能出问题
      
      ⚠️ WebRTC 传输的帧是横是竖？
```

**发现的问题:**

**问题 F1: 帧方向变化未处理**

WebRTC 视频帧的方向可能在横竖屏切换时改变。SAM2 如果接收到旋转帧，mask 追踪可能失败。

```
补丁: L1 需要一个帧方向标准化步骤:
  1. Unity 端: 在 telemetry 中发送 screen_orientation
  2. Python 端: 收到帧后根据 orientation 做标准化旋转
  3. 保证 SAM2 总是收到一致方向的帧
```

---

## 7. 审计总结

### 7.1 新发现的遗漏清单

| # | 遗漏 | 严重性 | 归属 | MVP? |
|:--|:-----|:-------|:-----|:-----|
| A1 | 锚点恢复流程未设计 | 高 | Unity + L2-A | P1 |
| A2 | 锚点恢复后视觉验证 | 中 | L1 + L2-A | P1 |
| B1 | 短暂转头 vs 真正离开未区分 | 高 | L2-A 节点状态 | **P0** |
| B2 | SAM2 track ID 快速续接 | 中 | L1 + L2-A | **P0** |
| C1 | 相似物体 ReID 多因素匹配 | 中 | ReID | P1 |
| D1 | fly_to 跨场景降级 | 中 | Tools | P1 |
| E1 | 物体消失原因推断 | 中 | L2-A | P1 |
| F1 | 帧方向标准化 | 高 | L1 | **P0** |
| S1 | **磁力计/罗盘未接入** | 高 | Unity telemetry | **P0** |
| S2 | **FeatureMapQuality 未接入** | 高 | Unity telemetry | **P0** |
| S3 | **接近传感器未接入** | 中 | APP 生命周期 | P1 |
| S4 | L1 LabelBuffer 未实现 | 中 | L1 缓冲 | **P0** |
| S5 | L1 PositionBuffer 未实现 | 中 | L1 缓冲 | **P0** |

### 7.2 传感器接入优先级

```
P0 (MVP 前端 telemetry 必须新增):
  compass_heading        → 方位感知
  feature_map_quality    → 锚点创建质量门控
  screen_orientation     → 帧方向标准化
  ar_anchor_count        → 锚点状态监控
  depth_available        → 深度可用性标记

P1 (Phase 2 接入):
  proximity_sensor       → APP 生命周期辅助
  step_counter          → 用户运动辅助
  barometric_pressure    → 楼层变化
  hit_test_available     → 精确点击定位
```

### 7.3 更新后的 AR Telemetry 格式

```csharp
var telemetry = new {
    type = "ar_telemetry",
    timestamp = Time.time,
    
    // 已有
    tracking_state = ...,
    not_tracking_reason = ...,
    camera_velocity = ...,
    camera_angular_velocity = ...,
    planes_detected = ...,
    
    // P0 新增
    compass_heading = Input.compass.trueHeading,          // 绝对方向
    compass_accuracy = Input.compass.headingAccuracy,     // 罗盘精度
    feature_map_quality = arExtensions.estimateFeatureMapQuality(), // 0/1/2
    screen_orientation = Screen.orientation,               // 屏幕方向
    anchor_count = anchorManager.trackables.count,         // 活跃锚点数
    depth_available = occlusionManager.enabled,            // 深度可用
    light_intensity = lightEstimation.averageIntensity,    // 光照
    
    // P1 新增
    proximity = proximityValue,                            // 接近传感器
    step_count = stepCounter.value,                        // 步数
    barometric_pressure = pressure,                        // 气压
};
```

### 7.4 架构决策 (ADR-019 ~ ADR-022)

**ADR-019: L1 三层缓冲 (Stability + Label + Position)**
- 比当前设计稍复杂，但每个缓冲器极简 (各 <30 行代码)
- 显著减少 L2-A 收到的无意义事件
- 参数由 SceneProfile 控制

**ADR-020: 节点置信度 = 6 维加权评分**
- tracking / position / identity / memory / anchor / temporal
- 每个维度有明确的计算公式和输入来源
- overall 分数影响 L2-B 的注意力和 L3 是否报告给 Gemini

**ADR-021: 方位感知 = 罗盘 + ARCore Pose 互校**
- 能做到"前方有桌子"级别的方位描述
- 不能做到 SLAM 级别的全局导航
- 磁力计精度受室内环境影响大，需降级策略

**ADR-022: 节点生命周期区分短暂遮挡 vs 真正离开**
- < 3s 遮挡: 直接恢复，不做 ReID
- 3s-30s: 需要 ReID 确认
- > 30s: OUT_OF_VIEW
- ANCHORED 节点不受转头影响
