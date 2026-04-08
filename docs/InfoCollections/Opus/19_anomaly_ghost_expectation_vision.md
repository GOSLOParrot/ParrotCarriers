# 异常处理 · 幽灵节点 · 预期偏离触发 · 视觉模型编排

> 生成日期: 2026-02-24
> 核心问题:
> 1. 传感器失效/异常姿态等边缘情况的系统容错
> 2. 幽灵节点问题 + 多因素证据确认模型 (什么时候该 ReID？)
> 3. 预期偏离作为主动触发器 — "记忆中的笔记本不见了"
> 4. 视觉模型职责清单 + 编排策略 + 避免混乱

---

## 1. 异常处理全景

### 1.1 异常分类

系统会遇到三类异常：**硬件级**（传感器失效）、**姿态级**（手机指向错误）、**环境级**（极端条件）。当前设计只处理了一部分。

```
异常层次:
┌─────────────────────────────────────────────────────────────┐
│ 硬件级 (传感器)                                               │
│  ├─ ARCore 追踪完全丢失 ← ✅ 已处理 (Tier 0)                │
│  ├─ 罗盘失效/严重漂移   ← ❌ 未处理                         │
│  ├─ 深度 API 不可用     ← ❌ 未处理                         │
│  ├─ 摄像头被遮挡        ← ❌ 未处理                         │
│  └─ 陀螺仪漂移          ← ⚠️ ARCore 内部补偿但不透明       │
│                                                              │
│ 姿态级 (手机朝向)                                             │
│  ├─ 手机对着天花板       ← ❌ 未处理                         │
│  ├─ 手机面朝下/口袋里   ← ❌ 未处理                         │
│  ├─ 横竖屏切换          ← ⚠️ 上次审计发现 (F1)             │
│  └─ 手机静止但不对着场景 ← ❌ 未处理                         │
│                                                              │
│ 环境级 (外部条件)                                             │
│  ├─ 极暗环境            ← ⚠️ 有概念 (光照估计)             │
│  ├─ 强反射/镜面          ← ❌ 未处理                         │
│  ├─ 纯白/无特征墙壁     ← ⚠️ ARCore InsufficientFeatures   │
│  └─ 多人同时操作        ← ⚠️ 上次审计有提                  │
└─────────────────────────────────────────────────────────────┘
```

### 1.2 硬件级异常处理

#### 1.2.1 罗盘失效

```python
class CompassHealthMonitor:
    """罗盘健康监测 — 检测磁场干扰和传感器故障"""

    VARIANCE_THRESHOLD = 15.0  # 度 — 5秒窗口内方差超过此值视为不可靠
    STUCK_THRESHOLD = 0.1      # 度 — 5秒内变化小于此值视为卡死

    def __init__(self):
        self._history: list[float] = []
        self._window = 50  # 5s at 10Hz
        self.is_reliable = False
        self.failure_reason = "initializing"

    def update(self, heading: float | None) -> bool:
        if heading is None:
            self.is_reliable = False
            self.failure_reason = "no_data"
            return False

        self._history.append(heading)
        if len(self._history) > self._window:
            self._history.pop(0)

        if len(self._history) < 10:
            self.is_reliable = False
            self.failure_reason = "warming_up"
            return False

        variance = self._circular_variance(self._history[-self._window:])
        delta = abs(self._history[-1] - self._history[0])

        if variance > self.VARIANCE_THRESHOLD:
            self.is_reliable = False
            self.failure_reason = "electromagnetic_interference"
        elif delta < self.STUCK_THRESHOLD and len(self._history) >= self._window:
            self.is_reliable = False
            self.failure_reason = "sensor_stuck"
        else:
            self.is_reliable = True
            self.failure_reason = ""

        return self.is_reliable
```

**降级策略:** 罗盘不可靠时，方位标记功能关闭。所有依赖绝对方向的功能退化为只用相对方向（基于 ARCore Pose 的相对角度）。不报错，只是能力减少。

#### 1.2.2 深度 API 不可用

不是所有安卓手机都支持 ARCore Depth。即使支持，某些场景可能获取不到有效深度。

```
深度可用性 → 影响:

depth_available = True:
  → 物体 3D 位置估计: 用深度图 + 2D bbox
  → position_confidence 基础值: 0.7
  → ON_SURFACE 关系: 深度 + 平面高度交叉验证
  → 物体体积估算: 可以做 Tier B 方案

depth_available = False:
  → 物体 3D 位置估计: 仅靠 AR 平面 Y 坐标 + 2D bbox 投影
  → position_confidence 基础值: 0.4 (降低!)
  → ON_SURFACE 关系: 仅靠 2D 重叠判断 (精度下降)
  → 物体体积估算: 退回 Tier A (仅平面)
  
系统正常运行，只是精度降低。不影响核心功能。
```

#### 1.2.3 摄像头被遮挡（手指挡住、放口袋）

```python
def detect_camera_obstruction(frame, telemetry) -> str:
    """检测摄像头是否被遮挡"""
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    mean_brightness = gray.mean()
    std_brightness = gray.std()

    proximity = telemetry.get("proximity", None)

    if mean_brightness < 10 and std_brightness < 5:
        # 几乎全黑 + 无纹理 → 被物理遮挡
        if proximity is not None and proximity < 1.0:
            return "pocket"  # 接近传感器触发 = 放口袋了
        return "obstructed"  # 手指挡住或贴着东西

    if mean_brightness > 250 and std_brightness < 10:
        return "overexposed"  # 对着灯/太阳

    return "normal"
```

**降级策略:**

| 遮挡类型 | StabilityGate | 节点影响 | 鹦鹉行为 |
|:---------|:-------------|:---------|:---------|
| pocket | → Tier 0 | 所有 → OCCLUDED (冻结) | 休眠模式 (无动画) |
| obstructed | → Tier 0 | 所有 → OCCLUDED | "嗯？我看不见了..." |
| overexposed | → Tier 1 | position 保持，不做 ReID | 不报告 (短暂) |

### 1.3 姿态级异常处理

#### 1.3.1 手机对着天花板

```python
def detect_phone_orientation(telemetry) -> str:
    """检测手机朝向 — 用重力传感器或 ARCore Pose 的 up 向量"""
    gravity = telemetry.get("gravity", None)
    if gravity is None:
        camera_up = telemetry.get("camera_up_vector", (0, 1, 0))
        gravity = (-camera_up[0], -camera_up[1], -camera_up[2])

    gx, gy, gz = gravity

    # 重力在设备坐标系中:
    # 正常平视: gy ≈ -9.8 (重力向下)
    # 对着天花板: gy ≈ +9.8 (重力向上，手机翻转)
    # 平放面朝上: gz ≈ -9.8
    # 平放面朝下: gz ≈ +9.8

    gy_norm = gy / 9.8 if abs(gy) > 0.1 else 0

    if gy_norm > 0.7:
        return "facing_ceiling"       # 手机对着天花板
    elif abs(gz / 9.8) > 0.8 and gz > 0:
        return "face_down"            # 面朝下放着
    elif abs(gz / 9.8) > 0.8 and gz < 0:
        return "face_up_flat"         # 面朝上平放
    else:
        return "normal"               # 正常使用角度
```

**处理策略:**

| 朝向 | 持续时间 | 处理 |
|:-----|:---------|:-----|
| facing_ceiling (< 3s) | 短暂 | 忽略 (用户可能在抬头看什么) |
| facing_ceiling (> 3s) | 持续 | L1 降频到 1fps; L3 不推送视觉给 Gemini; 鹦鹉可以评论: "天花板好高啊" |
| face_down (任何) | — | 等同 "pocket" → Tier 0, 休眠 |
| face_up_flat | — | 手机平放在桌上。视野无意义但 ARCore 可能还在 Tracking。降到 Tier 1。|

#### 1.3.2 手机静止但不对着场景

最隐蔽的情况: 手机在支架上 Tier 3 稳定运行，但用户把手机转了个方向，对着墙壁。

```
检测方法: 场景内容监测
  if Tier 3 (稳定) and L1 连续 30s 无物体追踪 and 无新物体发现:
    可能原因:
      A) 手机对着空白墙壁
      B) 所有物体真的被搬走了
      C) 视觉模型故障
    
    区分: 
      检查 ARCore 平面: 如果有平面但上面没物体 → 可能是 A
      检查 ARCore 特征点: 如果特征点少 → 无特征墙壁 (A)
      检查上一帧 vs 当前帧的差异: 如果几乎无差异 → 不是 C
    
    处理:
      → 降低 L1 到 1fps (ActivityThrottle 应该已触发)
      → 不主动报告给 Gemini (没信息可说)
      → 但如果用户提问 → Gemini 可访问 query_scene 得知 "当前视野中没有物体"
```

### 1.4 环境级异常处理

#### 1.4.1 极暗环境

```
ARCore Light Estimation < 50 lux (非常暗):
  → FrameQualityChecker: 暗帧会有高噪点但不一定模糊
  → 新增: dark_frame 检测 (mean_brightness < 30)
  → 降级:
    - DINOv2 ReID 置信度 × 0.5 (特征不可靠)
    - YOLO-World Discoverer 关闭 (暗环境检测率太低)
    - SAM2 Tracker 保持 (mask 追踪对光照有一定鲁棒性)
    - 所有新发现的物体 confidence 上限 = 0.5
  → L3 → Gemini: "[SYSTEM] 光线很暗，我看不太清楚"
```

#### 1.4.2 强反射/镜面

```
镜面会让 ARCore 追踪和 SAM2 产生幻觉:
  → SAM2 可能追踪镜中物体 (幽灵节点的主要来源之一!)
  → ARCore 平面可能误检 (镜面被当作平面)
  
检测: 难以自动检测。
  → 但如果出现以下症状:
    - 同一类别物体突然出现 2 个且位置对称 → 可能是镜像
    - 平面法向量指向不合理方向 → 可能是镜面平面
  → 标记为 suspect_mirror = True → confidence × 0.3
  
MVP: 不做镜面检测。在 SOUL instructions 中写明:
  "如果你在镜子或反射表面前，你看到的东西可能是倒影而非真实物体"
```

### 1.5 异常处理汇总矩阵

```
┌──────────────────────┬─────────────┬────────────────┬──────────────┐
│ 异常                  │ 检测方式     │ StabilityGate │ 节点影响      │
├──────────────────────┼─────────────┼────────────────┼──────────────┤
│ ARCore 追踪丢失       │ TrackState  │ → Tier 0      │ → OCCLUDED   │
│ 罗盘失效              │ 方差/卡死    │ 不影响         │ 方位标签清除  │
│ 深度不可用            │ API 检查     │ 不影响         │ pos_conf ↓   │
│ 摄像头遮挡            │ 亮度+接近    │ → Tier 0      │ → OCCLUDED   │
│ 对着天花板 (短)       │ 重力向量     │ 不影响         │ 不影响        │
│ 对着天花板 (长)       │ 重力+计时    │ → Tier 1      │ 视觉暂停     │
│ 面朝下               │ 重力向量     │ → Tier 0      │ 休眠         │
│ 对着空白墙壁          │ 无物体+平面  │ 保持当前       │ Throttle 降频│
│ 极暗                  │ 亮度 <30    │ 保持当前       │ conf 上限 0.5│
│ 强光/过曝             │ 亮度 >250   │ → Tier 1      │ 不做 ReID    │
│ 镜面反射              │ 对称检测     │ 不影响         │ conf × 0.3  │
│ 横竖屏切换            │ orientation │ 不影响         │ 帧标准化     │
│ WebRTC 帧丢失        │ 帧间隔       │ 不影响         │ 用前帧推断   │
└──────────────────────┴─────────────┴────────────────┴──────────────┘
```

---

## 2. 幽灵节点与多因素证据确认

### 2.1 什么是幽灵节点？

幽灵节点 = **存在于 L2-A 图中，但物理世界中实际不存在的节点**。

来源:

| 来源 | 频率 | 严重性 | 例子 |
|:-----|:-----|:-------|:-----|
| SAM2 误检 | 低 | 中 | 阴影被当成物体 |
| YOLO-World 误检 | 中 | 高 | 纹理花纹被识别为物体 |
| 镜面反射 | 低 | 高 | 镜中杯子成为独立节点 |
| **预加载未验证** | **高** | **高** | **从记忆中恢复的物体但实际已不在** |
| ReID 错误合并 | 低 | 中 | 把 A 的 track 认成 B |
| 深度错误 | 中 | 低 | 物体位置偏移但节点还在 |

**用户指出的核心问题**: 预加载场景时（比如加载"桌面场景"），记忆中的 8 个物体会以"幽灵"状态预填充。视角转动时需要确认它们是否真的在那里。

### 2.2 引入 EXPECTED 状态: 幽灵节点的正式身份

当前 `NodeState` 缺少一个关键状态。需要新增:

```python
class NodeState(Enum):
    ACTIVE = "active"           # 当前帧视觉确认存在
    EXPECTED = "expected"       # ★ 新增: 记忆/预测认为在这里，但尚未视觉确认
    OCCLUDED = "occluded"       # 短暂遮挡
    OUT_OF_VIEW = "out_of_view" # 离开视野
    LOST = "lost"               # 超时未见
    ANCHORED = "anchored"       # 有锚点固定 + 视觉确认过
```

**EXPECTED 的语义**: "我相信你在那里，但我还没亲眼看到。"

```
场景预加载流程:

打开 APP → 手机对着桌面
│
├─ 尝试恢复持久化锚点
│  ├─ 成功 → 加载上次的场景快照
│  │         所有物体初始状态 = EXPECTED
│  │         confidence = 0.4 (待验证)
│  │
│  └─ 失败 → 从头扫描, 无 EXPECTED 节点
│
├─ L1 开始视觉扫描 (Tier 3)
│  ├─ 看到杯子 → ReID 匹配 EXPECTED 节点 → EXPECTED → ACTIVE ✓
│  ├─ 看到键盘 → 匹配 → ACTIVE ✓
│  ├─ 没看到手办 → 保持 EXPECTED
│  │   └─ 30s 后: EXPECTED → OUT_OF_VIEW (可能被移走)
│  │   └─ 5min 后: OUT_OF_VIEW → LOST
│  └─ 看到新物体 (药瓶) → 新节点, ACTIVE, confidence = 0.6
│
└─ 每个 EXPECTED 节点有验证倒计时
   如果长时间未确认 → 降级 → 触发 EXPECTATION_VIOLATED
```

### 2.3 多因素证据确认: 什么时候"够了"？

用户担心的核心问题: **确认一个节点需要所有证据都满足吗？会不会太苛刻？有时候一个强证据就够了，但其他弱证据缺失怎么办？**

答案: **不用所有证据。用贝叶斯式的累积更新，而非二值门槛。**

#### 2.3.1 证据类型与权重

```
确认证据 (每个独立加分):

┌──────────────────────┬────────┬─────────────────────────────┐
│ 证据                  │ 权重    │ 条件                        │
├──────────────────────┼────────┼─────────────────────────────┤
│ SAM2 mask 追踪到      │ +0.25  │ 连续 3 帧以上               │
│ YOLO-World 分类一致   │ +0.15  │ 类别标签匹配                │
│ DINOv2 ReID 匹配      │ +0.20  │ embedding 距离 < 阈值       │
│ 位置与预期一致        │ +0.15  │ 距离 EXPECTED 位置 < 20cm   │
│ 在正确的 Surface 上   │ +0.10  │ ON_SURFACE 关系匹配         │
│ AR 锚点仍存在        │ +0.15  │ 持久锚点加载成功             │
│ Graphiti 记忆一致     │ +0.05  │ 搜索命中且描述匹配          │
│ 用户命名确认         │ +1.00  │ 用户说 "对，就是它" ← 一击必杀│
└──────────────────────┴────────┴─────────────────────────────┘
```

#### 2.3.2 确认逻辑: 累积而非门槛

```python
class EvidenceAccumulator:
    """节点证据累积器 — 贝叶斯式更新，非全有全无"""

    CONFIRMATION_THRESHOLD = 0.6   # 累积分 > 0.6 → 确认
    REJECTION_THRESHOLD = -0.3     # 累积分 < -0.3 → 否定 (是幽灵)

    def __init__(self):
        self._score = 0.0
        self._evidence_log: list[tuple[str, float]] = []

    def add_evidence(self, source: str, weight: float, details: str = ""):
        """添加一条证据 (正面或负面)"""
        self._score += weight
        self._evidence_log.append((source, weight))

    def add_counter_evidence(self, source: str, weight: float):
        """添加反面证据"""
        self._score -= weight
        self._evidence_log.append((source, -weight))

    @property
    def verdict(self) -> str:
        if self._score >= self.CONFIRMATION_THRESHOLD:
            return "confirmed"
        elif self._score <= self.REJECTION_THRESHOLD:
            return "ghost"
        else:
            return "uncertain"

    @property
    def score(self) -> float:
        return self._score
```

#### 2.3.3 关键原则: "一个强证据够了"

```
场景 1: 用户说 "对就是我的杯子"
  → user_confirmed = +1.0
  → 总分 1.0 > 0.6 → confirmed
  → 不需要 ReID, 不需要位置匹配, 用户说了就是了

场景 2: SAM2 追踪到, 位置匹配, 但没做 ReID (Tier 2 不做)
  → sam2_tracking = +0.25
  → position_match = +0.15
  → 总分 0.40 < 0.6 → uncertain (还不够!)
  → 等升到 Tier 3 做 ReID, 或继续追踪累积帧数

场景 3: SAM2 追踪到 5帧, 类别投票一致, 位置匹配
  → sam2_tracking = +0.25
  → class_match = +0.15
  → position_match = +0.15
  → 总分 0.55 → 接近 confirmed
  → 再追踪几帧 → 累积到 0.6 → confirmed

场景 4: 锚点恢复了, 但视觉上没找到物体
  → anchor_loaded = +0.15
  → no_visual (10s) = -0.2
  → 总分 -0.05 → uncertain → 继续等
  → no_visual (30s) = -0.3 (追加)
  → 总分 -0.35 → ghost! → 物体可能被移走了
```

#### 2.3.4 什么时候该 ReID？

这是核心编排问题: ReID (DINOv2) 昂贵，不是每次都该做。

```
ReID 触发条件 (任一满足):

1. 新 track 出现 + 存在 EXPECTED 节点
   → 必须做 ReID 来匹配 (这是预加载场景的核心验证手段)

2. 新 track 出现 + 附近有 LOST/OUT_OF_VIEW 节点
   → 可能是旧物体回来了，ReID 确认

3. Tier 3 稳定 + 物体初次发现
   → 标准流程: 新物体入场需要 embedding

4. Gemini focus_on(uuid) — On-Demand
   → 强制 ReID, 无论当前 Tier

ReID 不触发条件:

1. Tier 1-2 — 太不稳定, 特征不可靠
2. 物体已经 ACTIVE + confidence > 0.8 — 够了
3. 短暂遮挡 < 3s 后恢复 — 位置匹配续接就行
4. 光照 < 50 lux — 太暗, DINOv2 特征不可靠
```

### 2.4 防止混乱: 多因素证据不会混乱的原因

用户担心: **"多确认和多因素证据条件的来源会不会导致混乱？"**

**不会，因为:**

1. **每个证据是独立加分，不是逻辑 AND**。不需要所有条件同时满足。
2. **有明确的权重**。SAM2 mask 追踪 (0.25) 比 Graphiti 记忆 (0.05) 重要得多 — 眼见为实。
3. **只有一个判定出口** (`verdict` → confirmed/ghost/uncertain)。不管证据来了多少条、什么组合，最终只看累积分。
4. **时间会推进决策**。如果长时间 uncertain → 自动降级为 ghost 候选（没看到就是没看到）。
5. **用户确认一击必杀**。如果用户说"对就是它"，结束讨论。

```
反直觉但正确的设计:
  ❌ 错误: "需要 SAM2 + ReID + 位置 + 锚点全部匹配才确认"
  ✅ 正确: "任何一条路径的累积分达到阈值就确认"
  
  这就像人类认知:
  - 你远远看到一个蓝色的东西在桌上 → "大概是我的杯子" (uncertain)
  - 走近看清楚了是杯子形状 → "应该是" (approaching confirmed)
  - 看到上面写着名字 → "就是它" (confirmed)
  - 或者你妈说 "对，就在那" → "就是它" (confirmed by authority)
  任何一条路径都能走通，不需要全走。
```

### 2.5 确认存在 vs 确认不存在: 不对称流程

用户指出：**"确认笔记本在桌上"和"确认笔记本不在桌上"流程肯定不同。**

这是一个根本性的认识论不对称 (Epistemic Asymmetry):

```
确认存在 = 看到就行 (一帧 positive evidence 可以很快确认)
确认不存在 = 永远无法100%确认 (你只能说"我找遍了也没看到")
```

#### 2.5.1 确认存在的流程 (快速)

```
EXPECTED("笔记本电脑")
  │
  ├─ L1 扫描帧 → YOLO 检测到 "laptop" 在预期位置附近
  │    evidence: +0.15 (class_match) + +0.15 (position_match) = 0.30
  │
  ├─ SAM2 追踪 3 帧 → mask 稳定
  │    evidence: +0.25 (tracking) = 0.55
  │
  ├─ DINOv2 ReID → embedding 距离 0.08 (匹配!)
  │    evidence: +0.20 (reid) = 0.75
  │
  └─ verdict: confirmed ✓ (0.75 > 0.6)
  
  总耗时: ~2 秒 (几帧就够)
  转换: EXPECTED → ACTIVE
```

#### 2.5.2 确认不存在的流程 (缓慢、分阶段)

```
EXPECTED("笔记本电脑")
  │
  ├─ 阶段1: 被动等待 (0~10s)
  │    手机对着桌面, L1 在 Tier 3 扫描中
  │    YOLO 每秒扫一次, 没检测到 laptop
  │    但: 可能被遮挡? 可能在视野边缘? 可能光照不好?
  │    此阶段不加负面证据 — 还不够说"不在"
  │    状态: EXPECTED (不变)
  │
  ├─ 阶段2: 视野覆盖检查 (10~30s)
  │    系统检查: 笔记本的预期位置是否在当前视野(frustum)内?
  │    
  │    ⚠️ 关键问题: 如果预期位置根本不在画面中, 就不能说"不在"
  │    
  │    if 预期位置在视野内 + YOLO连续10帧未检测:
  │      evidence: -0.15 (active_search_negative)
  │    if 预期位置不在视野内:
  │      不加负面证据! 你没看那个方向, 不能说不在
  │    
  │    状态: EXPECTED → uncertain (score 可能变为 0.25 左右)
  │
  ├─ 阶段3: 主动搜索 (30s~2min)
  │    如果预期位置在视野内 + 持续未检测到:
  │      evidence: -0.1 每 10s (累加)
  │    
  │    但同时检查干扰因素:
  │      光照 < 100 lux? → 减慢负面累积速度 (可能看不清)
  │      Tier < 3? → 暂停负面累积 (视觉不可靠)
  │      物体很小? → 可能 YOLO 漏检, 减慢累积
  │    
  │    状态: score 缓慢下降
  │
  └─ 阶段4: 判定缺失 (score < -0.3)
       evidence 累积到负数阈值
       verdict: ghost (物体可能不在了)
       状态: EXPECTED → OUT_OF_VIEW
       触发: EXPECTATION_VIOLATED (type="OBJECT_MISSING")
       
  总耗时: 30s ~ 2min (慎重!)
```

#### 2.5.3 为什么不对称? 两个原因

```
原因 1: 看到 ≠ 没看到

  看到一个 laptop → 它确实在那里 (false positive 率低)
  没看到 laptop → 可能在那里但你没看到:
    - 被手挡了
    - 在合上的状态, 外观变了
    - 在画面边缘, YOLO 没检到
    - 光照不够
    → false negative 率高
    
  所以: 正面证据可以强力确认, 负面证据必须慎重累积

原因 2: 代价不对称

  错误确认存在 (false positive): 
    节点多了一个实际不在的物体 → 后续会自然修正 (LOST)
    代价: 低
    
  错误确认不存在 (false negative):
    删掉了一个实际还在的物体 → 丢失认知
    代价: 高 (尤其是用户说过"帮我记着这个"的物体)
    
  所以: 宁可慢一点确认不存在, 也不要急着否定
```

#### 2.5.4 修改 EvidenceAccumulator

```python
class EvidenceAccumulator:
    """节点证据累积器 — 确认/否定不对称"""

    CONFIRMATION_THRESHOLD = 0.6    # 正面: 较快达到
    REJECTION_THRESHOLD = -0.3      # 负面: 更难达到 (绝对值更小, 但累积更慢)
    
    NEGATIVE_COOLDOWN = 10.0        # 负面证据最少间隔 10s (不能连续扣分)
    NEGATIVE_REQUIRES_FRUSTUM = True # 负面证据要求物体预期位置在视野内

    def __init__(self):
        self._score = 0.0
        self._evidence_log: list[tuple[str, float, float]] = []  # (source, weight, timestamp)
        self._last_negative_time = 0.0

    def add_evidence(self, source: str, weight: float, timestamp: float = 0.0):
        """正面证据: 无限制"""
        self._score += weight
        self._evidence_log.append((source, weight, timestamp))

    def add_absence_evidence(
        self,
        source: str,
        weight: float,
        timestamp: float,
        in_frustum: bool,
        tier: int,
        light_level: float,
    ) -> bool:
        """负面证据: 有限制条件"""
        
        # 条件1: 预期位置必须在视野内
        if self.NEGATIVE_REQUIRES_FRUSTUM and not in_frustum:
            return False  # 你没往那看, 不能说不在
        
        # 条件2: 视觉条件必须足够好
        if tier < 3:
            return False  # 视觉不可靠时不扣分
        
        # 条件3: 光照必须充足
        if light_level < 100:
            weight *= 0.3  # 暗环境扣分减弱
        
        # 条件4: 冷却时间
        if timestamp - self._last_negative_time < self.NEGATIVE_COOLDOWN:
            return False
        
        self._score -= weight
        self._last_negative_time = timestamp
        self._evidence_log.append((source, -weight, timestamp))
        return True

    @property
    def verdict(self) -> str:
        if self._score >= self.CONFIRMATION_THRESHOLD:
            return "confirmed"
        elif self._score <= self.REJECTION_THRESHOLD:
            return "ghost"
        else:
            return "uncertain"
```

#### 2.5.5 视锥体 (Frustum) 检查

负面证据的前提是"我看了那个位置但没看到"。需要一个视锥体检查:

```python
def is_in_camera_frustum(
    expected_pos: tuple[float, float, float],
    camera_pose: tuple,
    camera_fov: float = 60.0,     # 度
    max_distance: float = 5.0,     # 米
) -> bool:
    """检查一个 3D 点是否在相机视锥体内"""
    cam_pos = camera_pose[:3]
    cam_forward = camera_pose[3:6]  # 相机前方向

    to_target = (
        expected_pos[0] - cam_pos[0],
        expected_pos[1] - cam_pos[1],
        expected_pos[2] - cam_pos[2],
    )
    distance = sum(x**2 for x in to_target) ** 0.5
    if distance > max_distance:
        return False

    # 计算目标与相机前方的夹角
    dot = sum(a * b for a, b in zip(to_target, cam_forward)) / (distance + 1e-8)
    angle = math.degrees(math.acos(max(-1, min(1, dot))))

    return angle < camera_fov / 2
```

---

## 3. 预期偏离触发器: "笔记本不见了!"

### 3.1 设计理念: 期望比较 = 主动思维的基础

当前系统是被动的: 看到什么报什么。但真正智能的感知是**有预期**的: 

```
被动: "我看到了杯子" → 报告
主动: "桌上应该有杯子、笔记本、显示器... 等等，笔记本不见了！" → 更有价值
```

这就是 **Expectation-Violation Detection (EVD)** — 预期偏离检测。

### 3.2 预期来源

| 来源 | 内容 | 时效性 | 可靠性 |
|:-----|:-----|:-------|:-------|
| **当前会话记忆** | 5 分钟前桌上有 8 个物体 | 高 (秒级) | 高 |
| **上次会话快照** | 昨天关 APP 时桌上有什么 | 中 (小时→天) | 中 |
| **Graphiti 长期记忆** | "桌上通常有显示器和键盘" | 低 (天→月) | 低 (可能变了) |
| **SceneProfile 先验** | "桌面场景通常有 5-15 个物体" | — | 统计性 |

### 3.3 ExpectationChecker 设计

```python
@dataclass
class SceneExpectation:
    """场景预期 — 记录"应该有什么" """
    expected_objects: dict[str, ExpectedObject] = field(default_factory=dict)
    scene_type: str = ""
    source: str = ""  # "session_memory" | "last_session" | "graphiti"
    created_at: float = 0.0

@dataclass
class ExpectedObject:
    uuid: str
    class_label: str
    expected_position: tuple[float, float, float] | None
    surface_uuid: str | None
    last_confidence: float
    source: str  # 预期来源

@dataclass
class ExpectationViolation:
    """预期偏离事件"""
    violation_type: str        # 见下表
    object_uuid: str
    object_label: str
    details: str
    severity: float            # [0, 1] 偏离程度
    timestamp: float

class ExpectationChecker:
    """预期偏离检测器 — L2-A 每次扫描完成后运行"""

    def check(
        self,
        active_objects: dict[str, ObjectNode],
        expectations: SceneExpectation,
    ) -> list[ExpectationViolation]:

        violations = []

        # 1. MISSING: 预期存在但没看到
        for uuid, expected in expectations.expected_objects.items():
            if uuid not in active_objects:
                violations.append(ExpectationViolation(
                    violation_type="OBJECT_MISSING",
                    object_uuid=uuid,
                    object_label=expected.class_label,
                    details=f"预期在 {expected.expected_position} 但未找到",
                    severity=expected.last_confidence,
                    timestamp=time.time(),
                ))

        # 2. DISPLACED: 存在但位置不对
        for uuid, expected in expectations.expected_objects.items():
            if uuid in active_objects and expected.expected_position:
                actual = active_objects[uuid]
                delta = _distance(actual.position_3d, expected.expected_position)
                if delta > 0.15:  # 15cm 以上视为位移
                    violations.append(ExpectationViolation(
                        violation_type="OBJECT_DISPLACED",
                        object_uuid=uuid,
                        object_label=expected.class_label,
                        details=f"从 {expected.expected_position} 移到了 {actual.position_3d}",
                        severity=min(1.0, delta / 0.5),
                        timestamp=time.time(),
                    ))

        # 3. NEW_UNEXPECTED: 没预期但出现了新东西
        for uuid, node in active_objects.items():
            if uuid not in expectations.expected_objects:
                violations.append(ExpectationViolation(
                    violation_type="NEW_UNEXPECTED",
                    object_uuid=uuid,
                    object_label=node.class_label,
                    details=f"新出现的 {node.class_label}，不在预期中",
                    severity=0.6,
                    timestamp=time.time(),
                ))

        # 4. COUNT_MISMATCH: 同类物体数量变化
        expected_counts = Counter(e.class_label for e in expectations.expected_objects.values())
        actual_counts = Counter(n.class_label for n in active_objects.values())
        for label in set(expected_counts) | set(actual_counts):
            diff = actual_counts.get(label, 0) - expected_counts.get(label, 0)
            if abs(diff) > 0:
                violations.append(ExpectationViolation(
                    violation_type="COUNT_CHANGED",
                    object_uuid="",
                    object_label=label,
                    details=f"{label}: 预期 {expected_counts.get(label, 0)} 个, 实际 {actual_counts.get(label, 0)} 个",
                    severity=0.4,
                    timestamp=time.time(),
                ))

        return violations
```

### 3.4 偏离类型与鹦鹉反应

| 偏离类型 | 例子 | 鹦鹉可能的反应 | 触发给 Gemini |
|:---------|:-----|:-------------|:-------------|
| **OBJECT_MISSING** | 笔记本不见了 | "咦？你的笔记本电脑呢？刚才还在桌上的..." | `[SCENE_CHANGE] 预期存在的物体消失: 笔记本电脑` |
| **OBJECT_DISPLACED** | 杯子换了位置 | "嗯？杯子搬家了？" | `[SCENE_CHANGE] 物体位移: 杯子 从左侧移到右侧` |
| **NEW_UNEXPECTED** | 桌上多了药瓶 | "哦？这是什么？之前没见过的东西" | `[SCENE_NEW] 意外新物体: 药瓶 (不在预期中)` |
| **COUNT_CHANGED** | 多了一个杯子 | "咦，杯子怎么变成两个了？" | `[SCENE_CHANGE] 数量变化: 杯子 1→2` |

### 3.5 预期偏离在触发器体系中的位置

```
现有触发链:
  L1Event → L2AEvent → L2BTrigger → ContextInjection

新增 (与 L2AEvent 并行):
  L2A 扫描完成
    ↓
  ExpectationChecker.check()
    ↓
  ExpectationViolation
    ↓
  L2BTrigger (新类型: EXPECTATION_VIOLATED)
    ↓
  L3 ContextInjection: "[SCENE_CHANGE] 预期偏离: ..."
    ↓
  Gemini 决定是否反应
```

新增的 L2B Trigger 类型:

```python
L2B_TRIGGERS_EXTENDED = {
    # 已有的...
    "NOVELTY_ALERT": ...,
    "ATTENTION_PEAK": ...,

    # 新增: 预期偏离
    "EXPECTATION_VIOLATED": {
        # payload:
        "violation_type": str,  # OBJECT_MISSING | DISPLACED | NEW_UNEXPECTED | COUNT_CHANGED
        "object_label": str,
        "severity": float,
        "details": str,
        "source": str,  # 预期来源: session_memory | last_session | graphiti
    },
}
```

### 3.6 预期何时建立？何时废弃？

```
建立预期:
  1. 场景扫描完成且 Tier 3 稳定超过 10s 
     → 当前所有 ACTIVE 物体成为"会话预期"
  
  2. 场景折叠时
     → 折叠快照成为"离开时的预期" (用于回来时比较)
  
  3. APP 启动时加载持久锚点
     → 上次的场景快照成为"上次预期" (EXPECTED 节点)
  
  4. Graphiti 中的 "typical_location" 
     → "桌上通常有显示器" 成为弱预期 (只用于 NEW_UNEXPECTED 判定)

废弃预期:
  1. 扫描完成 + 所有 EXPECTED 确认/否定完毕 → 清除本轮预期
  2. 场景切换 → 旧场景预期归档, 新场景预期建立
  3. 用户明确说 "XX 被我拿走了" → 删除该物体的预期
  4. 预期超过 24 小时未验证 → 降级为弱预期 (低 severity)
```

---

## 4. 视觉模型编排: 谁做什么、何时做、避免混乱

### 4.1 完整视觉模型清单

| 模型 | 职责 | 输入 | 输出 | 运行位置 | 何时运行 |
|:-----|:-----|:-----|:-----|:---------|:---------|
| **SAM2** | 实例分割 + 追踪 | 视频帧 + 初始化点/框 | 逐帧 mask + track_id | 阿里云 A10 | Tier 2+, 15-30fps, **主发现路径** |
| **YOLO-World** | 开放词汇物体检测 | 单帧 + 文本 prompt | bbox + class_label + score | 阿里云 A10 | 仅 Tier 3, 1-2fps, **可选补充** |
| **DINOv2** | 视觉特征提取 (ReID) | 裁切图像块 | embedding 向量 (768D) | 阿里云 A10 | 触发式 |
| **Gemini Vision** | 高级视觉理解 | 视频帧 (via LiveKit) | 自然语言理解 | Google Cloud | 持续 (LiveKit 采样) |
| **(OpenCV)** | 帧质量/模糊检测 | 单帧 | blur_score, brightness | CPU | 每帧 |

### 4.2 每个模型的职责边界 (谁做什么)

```
┌────────────────────────────────────────────────────────────────┐
│                    视觉模型职责分工                              │
│                                                                 │
│  "这里有东西吗？"                                               │
│  ├─ YOLO-World: 开放词汇检测 → "在这个位置有一个 cup"          │
│  │  能力: 能发现任意类别物体, 不需要预训练类别表                │
│  │  局限: 每帧独立, 不知道上一帧结果, 可能帧间不一致           │
│  │                                                             │
│  "那个东西还在吗？移动了吗？"                                    │
│  ├─ SAM2: mask 追踪 → "track_id=3 的 mask 还在, 位置移了5px"  │
│  │  能力: 跨帧追踪同一物体的精确轮廓                           │
│  │  局限: 不知道物体是什么 (没有类别), 丢失后不能自己找回      │
│  │                                                             │
│  "这是不是上次看到的那个杯子？"                                  │
│  ├─ DINOv2: 特征匹配 → "embedding距离=0.12, 很可能是同一个"    │
│  │  能力: 视角、光照变化下仍能识别同一物体                     │
│  │  局限: 相似物体(两个白杯子)难以区分                          │
│  │                                                             │
│  "这个场景在发生什么？这个物体意味着什么？"                      │
│  ├─ Gemini: 高级理解 → "主人在加班, 桌上的药瓶说明可能不舒服"  │
│  │  能力: 常识推理、情感理解、跨模态关联                       │
│  │  局限: 不精确(不知道坐标), 延迟高, 不是实时的              │
│  │                                                             │
│  OpenCV: 底层预处理 → 帧质量判断、颜色统计                     │
│  不是"认知"模型, 是"体检"工具                                   │
└────────────────────────────────────────────────────────────────┘
```

### 4.3 模型间的编排: 四种协作模式

#### 模式 A: 发现流水线 (Tier 3, 新物体出现)

```
SAM2 全分割 → DINOv2 → ReID (主路径) → YOLO-World (可选标签补充) → L2-A
   │             │         │                  │               │
  "发现新mask" "它的指纹" "匹配已知吗"       "它叫什么"       "建节点"

详细 (修正后主路径):
1. SAM2 在全帧执行 Everything 模式（或网格点 prompt），发现未能与现有 track_id 匹配的新 mask
2. 分配新 track_id，生成精确 mask
3. DINOv2 对 mask 区域提取 embedding (768D)
4. ReID 匹配：如果在已知物体库中匹配到（如奶奶的杯子），直接确认身份
5. (可选补充) YOLO-World 对该区域执行开放词汇检测，仅作为未知物体（ReID 未匹配）的兜底标签补充
6. L2-A:
   - 匹配成功 → 合并 UUID, 更新状态
   - 匹配失败 → 创建新 ObjectNode (NEW_UNEXPECTED)
```

#### 模式 B: 追踪维持 (Tier 2, 正常运行)

```
SAM2 only → L2-A 位置更新
   │            │
   "还在跟踪"   "更新坐标"

不涉及 YOLO-World 和 DINOv2。SAM2 独立维持所有已追踪物体的 mask。
L2-A 只更新 position_3d, 不创建新节点, 不做 ReID。
```

#### 模式 C: 身份验证 (触发式, EXPECTED 确认)

```
SAM2 提供 mask → DINOv2 提取特征 → 与 EXPECTED 节点对比
                    │                      │
                    "这个东西的指纹"        "和记忆对比"

发生在:
- 场景恢复时, 需要确认预加载的 EXPECTED 节点
- 长时间 OUT_OF_VIEW 后物体重新出现
- 两个 track 可能是同一个物体

不涉及 YOLO-World (已经知道要验证什么)。
```

#### 模式 D: Gemini 驱动 (On-Demand)

```
Gemini focus_on("药瓶") → L1 找到对应 track → DINOv2 高精度提取
                          → 如果找不到 → YOLO-World 全帧搜索
                          → 结果返回 Gemini

Gemini 是导演, 其他模型是演员。
这是唯一可以在 Tier < 3 时触发 DINOv2 的路径。
```

### 4.4 如何避免混乱: 单一入口 + 明确优先级

```
可能的混乱场景:
  YOLO-World: "这是一个 cup"
  SAM2: track_id=7 (但标签是 YOLO 上一帧给的 "mug")
  DINOv2: ReID 匹配到一个 EXPECTED 的 "glass"
  Graphiti: 记忆中桌上有个 "蓝色杯子"
  
  结果: cup? mug? glass? 蓝色杯子? 到底是什么？！

解决: 标签权威链 (Label Authority Chain)
```

```python
class LabelAuthority:
    """标签权威链 — 避免多模型标签冲突"""

    AUTHORITY_ORDER = [
        "user_named",       # 用户说 "这是奶奶的杯子" → 最终权威
        "gemini_identified", # Gemini 说 "这是一个茶杯" → 高权威
        "reid_confirmed",   # DINOv2 ReID 匹配到的已知物体标签
        "yolo_voted",       # YOLO-World 多帧投票最高的标签
        "yolo_single",      # YOLO-World 单次检测
    ]

    @staticmethod
    def resolve_label(candidates: dict[str, str]) -> tuple[str, str]:
        """从多个来源选择最权威的标签
        
        Returns: (label, source)
        """
        for source in LabelAuthority.AUTHORITY_ORDER:
            if source in candidates:
                return candidates[source], source
        return "unknown", "none"
```

```
实际运行中不会混乱, 因为:

1. 时间上是串行的:
   帧 1: YOLO 说 "cup" → 暂时用 "cup"
   帧 2: YOLO 说 "mug" → LabelBuffer 投票 → 暂时还是 "cup"  
   帧 5: 投票稳定 → 确认 "cup"
   帧 5: DINOv2 ReID → 匹配到 EXPECTED "蓝色杯子" → 用记忆标签
   用户说 "这是奶奶的杯子" → 最终标签

2. 每个时刻只有一个"当前标签":
   ObjectNode.class_label 只有一个值
   每次更新遵循权威链, 高权威覆盖低权威

3. 历史保留在 class_votes 中:
   即使当前标签是 "cup", vote 历史仍然记录了 "mug" 出现过
   如果后续 "mug" 票数反超, 标签会自然切换
```

### 4.5 用户问题: "鹦鹉要如何发现新出现的药瓶？"

完整流程:

```
场景: 桌面稳定运行中, 用户把一瓶药放到桌上

00:00 桌面 6 个物体全 ACTIVE, SAM2 以 15fps 扫描追踪

00:01 SAM2 全局扫描 (Discover 模式):
      SAM2 在未能与现有 track 匹配的区域，发现了一个新的显著 mask (药瓶的轮廓)。
      分配新 track_id = 7，生成精确 mask。

00:02 DINOv2 提取特征:
      对 mask 区域裁切 → 提取 768D embedding。
      在已知物体中搜索匹配 (ReID) → 无匹配 (确认是全新物体)。

00:02 (可选) YOLO-World 补充标签:
      对该 bbox 执行开放词汇检测。
      输出: {class: "bottle", score: 0.78}

00:02 L2-A: 创建新 ObjectNode
      class_label = "bottle" (如果 YOLO-World 未开启，暂时标为 "unknown object")
      confidence = 0.6 (新物体初始值)
      state = ACTIVE

00:02 L2-B: 创建新 ObjectSemanticNode
      attention = 1.0 (NEW_OBJECT 最高新奇度!)
      Graphiti 搜索 "bottle" → 可能命中也可能不命中
      
00:02 ExpectationChecker:
      NEW_UNEXPECTED! "新出现的物体，不在预期中"
      
00:02 L3 → Gemini:
      "[SCENE_NEW] 发现新物体: bottle (不在预期中, 高注意力)"
      "[SCENE_CHANGE] 预期偏离: 桌上多了一个物体"

00:03 Gemini (鹦鹉):
      "咦？桌上多了个瓶子！主人，这是什么呀？是药吗？"
      
      如果用户说 "对, 是感冒药":
      → Gemini 调用 remember("桌上的瓶子是感冒药", category="objects")
      → 标签升级: "bottle" → "感冒药" (user_named 权威)
      → Gemini 可能关心: "主人你是不是不舒服？"
```

### 4.6 按需细粒度识别: "这是哪款奶茶？"

YOLO-World 能检测到 "cup" 或 "bottle"，但无法告诉你：
- 这是**星巴克美式**还是**瑞幸拿铁**
- 这是**RX-78-2 高达**还是**自由高达**
- 瓶子上写的是**布洛芬**还是**维生素 C**

这类细粒度识别需要**读文字 + 理解外观 + 常识推理** — 正好是 Gemini 擅长的。

#### 4.6.1 视觉模型能力边界

```
┌───────────────────────────────────────────────────────────────┐
│             "这是什么东西？"的回答精度层级                       │
│                                                               │
│  L0: 有东西                                                   │
│  └─ SAM2: "这个区域有一个物体" (仅 mask, 无语义)             │
│                                                               │
│  L1: 大类识别                                                 │
│  └─ YOLO-World: "这是一个 bottle / cup / figure"             │
│     能力天花板: 物体级类别, ~100 个常见类                      │
│     不能做: 品牌、型号、文字、款式                             │
│                                                               │
│  L2: 实例区分                                                 │
│  └─ DINOv2 ReID: "这是之前看过的那个 bottle, 不是另一个"      │
│     能力天花板: 区分见过/没见过, 不能说出"是什么"               │
│     不能做: 命名、描述                                         │
│                                                               │
│  L3: 细粒度识别 ★ 当前缺失                                    │
│  └─ 需要: Gemini Vision / 专用识别 API                        │
│     能做: "这是星巴克的焦糖玛奇朵, 中杯, 杯上写着 Kevin"      │
│     能做: "这是万代 RG RX-78-2, 红白蓝配色, 高达系列"         │
│     能做: "瓶子上写着布洛芬, 0.2g×24片, 生产日期2025年"       │
└───────────────────────────────────────────────────────────────┘
```

#### 4.6.2 方案: Gemini 就是我们的细粒度识别引擎

**不需要额外引入新模型。Gemini Multimodal Live 已经在通过 LiveKit 接收视频帧。**

区别在于：当前 Gemini 是被动地看整个画面做理解；我们需要的是**主动让 Gemini 看某个特定物体的裁切图**。

```
当前架构中的路径 (已存在, 但没充分利用):

Gemini Tool: describe_object(uuid)
  │
  ├─ L2-A 查到物体的 bbox / position
  │
  ├─ L1 裁切当前帧中该物体区域 (用 SAM2 mask)
  │
  ├─ 裁切图作为 image 注入给 Gemini:
  │   "[VISUAL_QUERY] 请仔细看这个物体的裁切图, 描述你看到了什么:
  │    包括品牌、文字、型号、颜色、材质等细节"
  │
  └─ Gemini 返回: "这是一杯星巴克焦糖玛奇朵, 杯身写着 'Kevin',
                    中杯 (Grande), 杯盖是绿色的"
```

#### 4.6.3 三条细粒度识别路径

| 路径 | 触发者 | 流程 | 例子 |
|:-----|:-------|:-----|:-----|
| **A: 用户驱动** | 用户说 "这是什么？" | Gemini 自己看视频帧理解 | "看看桌上那个瓶子" |
| **B: Gemini 主动** | Gemini 好奇 → `describe_object(uuid)` | 裁切图注入 Gemini 自己 | 新物体出现, 鹦鹉想知道是什么 |
| **C: 系统自动** | NEW_UNEXPECTED 触发 | 自动对新物体做一次裁切识别 | 桌上突然多了药瓶 |

```python
async def detailed_recognition(uuid: str, frame, l2a) -> dict:
    """对指定物体做细粒度识别 — 裁切后让 Gemini 看"""
    node = l2a.get_node(uuid)
    if not node or not node.bbox_2d:
        return {"error": "cannot_crop"}

    x, y, w, h = node.bbox_2d
    pad = 20  # 裁切时留边距, 包含周围上下文
    crop = frame[
        max(0, y - pad): y + h + pad,
        max(0, x - pad): x + w + pad,
    ]

    return {
        "crop_image": crop,
        "coarse_label": node.class_label,
        "context": f"这个物体在{node.on_surface_uuid or '未知位置'}",
    }
```

#### 4.6.4 识别结果怎么存？

```python
@dataclass
class ObjectNode(SpatialNode):
    # ... 已有字段 ...
    
    # 新增: 细粒度描述 (来自 Gemini)
    fine_description: str = ""          # "星巴克焦糖玛奇朵, 中杯, 杯上写着Kevin"
    fine_description_source: str = ""   # "gemini" | "user"
    fine_description_time: float = 0.0  # 何时识别的
    
    # 标签权威链中的位置:
    # user_named > gemini_described > reid_confirmed > yolo_voted
    # fine_description 属于 gemini_described 级别
```

#### 4.6.5 会导致混乱吗？

**不会。原因:**

1. **它不是一个新模型**, 而是对已有 Gemini 通道的一种新**使用方式**。不增加模型数量。

2. **它是按需的** (On-Demand), 不是持续运行。只在三种情况触发:
   - 用户问"这是什么"
   - Gemini 自己 focus_on 后好奇
   - 新物体出现时自动做一次

3. **结果存入现有字段** (`fine_description`), 不引入新的数据流。

4. **标签权威链不变**: Gemini 的描述在 `gemini_described` 级别, 低于用户命名, 高于 YOLO。

```
与现有架构的关系:

                已有                          新增
              ┌──────────┐                 ┌──────────┐
  发现物体 → │ YOLO     │ → "bottle"     │          │
              │ SAM2     │ → mask          │ Gemini   │ → "星巴克焦糖玛奇朵"
  区分物体 → │ DINOv2   │ → 是/不是同一个 │ 裁切识别 │
              └──────────┘                 └──────────┘
                                             ↑
                                        按需触发, 不持续运行
                                        不引入新模型
                                        不改变已有管线

  混乱风险: 零
  原因: 它只是给已经被 YOLO 标记为 "bottle" 的物体补充更详细的描述
        YOLO 管 "有什么", Gemini 管 "具体是什么"
        两者不冲突, 是上下级关系
```

#### 4.6.6 什么时候需要? 什么时候不需要?

| 场景 | 需要细粒度识别? | 原因 |
|:-----|:----------------|:-----|
| 杯子在桌上, 正常追踪 | ❌ | "cup" 就够了, 追踪不需要知道品牌 |
| 用户说 "看看这个" | ✅ | 用户期待鹦鹉能说出有意义的描述 |
| 新物体突然出现 | ✅ (自动) | 新物体值得仔细看看, 触发一次就好 |
| 鹦鹉要飞到杯子旁边 | ❌ | fly_to 只需要位置, 不需要品牌 |
| 用户问 "这是什么药" | ✅ | 需要读文字, YOLO 只能说 "bottle" |
| 追踪中杯子被拿走 | ❌ | 位置/状态变化, 不需要重新识别 |

**总结: 95% 的时间不需要细粒度识别。它是一个低频但高价值的补充能力。**

### 4.7 YOLO-World 的文本提示策略

```python
class DiscovererPromptStrategy:
    """YOLO-World 的文本提示策略 — 平衡发现能力和效率"""

    # 通用基础词汇 (每次都用)
    BASE_VOCAB = [
        "person", "hand", "cup", "bottle", "phone", "book",
        "laptop", "keyboard", "mouse", "pen", "bag", "food",
        "plate", "bowl", "remote", "toy", "box", "paper",
    ]

    # 场景特化词汇
    DESKTOP_VOCAB = [
        "monitor", "headphone", "cable", "charger", "sticky_note",
        "calculator", "lamp", "clock", "figure", "plant",
    ]

    INDOOR_VOCAB = [
        "chair", "sofa", "table", "pillow", "blanket", "vase",
        "picture_frame", "shoe", "basket", "trash_can",
    ]

    # 来自 Graphiti 的动态词汇 (用户提到过的物体)
    # → 每次场景切换时从 Graphiti objects 分区预加载
    dynamic_vocab: list[str] = []

    def get_prompt(self, scene_type: str) -> list[str]:
        vocab = list(self.BASE_VOCAB)
        if scene_type == "desktop":
            vocab.extend(self.DESKTOP_VOCAB)
        elif scene_type == "indoor":
            vocab.extend(self.INDOOR_VOCAB)
        vocab.extend(self.dynamic_vocab[:20])
        return list(set(vocab))  # 去重

    # ★ 关键: 如果 YOLO-World 没检测到但 SAM2 追踪到了无标签物体
    # → 可以用 "object" 或 "thing" 作为兜底提示
    # → 或者: 不给标签, 等 Gemini 来识别 (describe_object Tool)
```

### 4.7 避免发现过多导致的混乱

```
问题: YOLO-World 开放词汇很强, 可能把桌上所有东西都检测出来
  → 桌面 50 个小物件? 螺丝、橡皮擦、回形针?
  → L2-A 图会"爆炸"

解决: 发现也需要门控

1. 面积门控: bbox 面积 < 帧面积的 0.5% → 忽略 (太小)
2. 置信门控: YOLO score < 0.5 → 忽略
3. 数量门控: SceneProfile.tracker_max_targets
   Desktop: 最多 20 个物体 (超过的按面积/置信排序丢弃最低的)
   Indoor: 最多 30 个物体
4. 频率门控: Discoverer 是 1fps 而非 30fps
5. 去重门控: 新 bbox 与已有 track 的 IoU > 0.5 → 不是新物体

这些门控层层过滤后, 实际进入 L2-A 的物体数量是可控的。
```

---

## 5. 架构补丁汇总

### 5.1 新增组件清单

| 组件 | 归属 | 功能 | 复杂度 |
|:-----|:-----|:-----|:-------|
| `CompassHealthMonitor` | L1 telemetry | 罗盘可靠性检测 | 低 |
| `PhoneOrientationDetector` | L1 telemetry | 手机姿态异常检测 | 低 |
| `CameraObstructionDetector` | L1 pipeline | 摄像头遮挡检测 | 低 |
| `NodeState.EXPECTED` | L2-A 节点 | 幽灵节点正式身份 | 概念变更 |
| `EvidenceAccumulator` | L2-A 节点确认 | 多因素累积确认 | 中 |
| `ExpectationChecker` | L2-A 扫描后 | 预期偏离检测 | 中 |
| `LabelAuthority` | L1 → L2-A 接口 | 多模型标签冲突消解 | 低 |
| `DiscovererPromptStrategy` | L1 Discoverer | YOLO-World 文本提示管理 | 低 |

### 5.2 新增触发器

| 触发器 | 层级 | 内容 |
|:-------|:-----|:-----|
| `EXPECTATION_VIOLATED` | L2B → L3 | 预期偏离 (MISSING/DISPLACED/NEW/COUNT) |
| `PHONE_ANOMALY` | L1 → L3 | 手机姿态异常 (ceiling/pocket/flat) |
| `SENSOR_DEGRADED` | L1 → L3 | 传感器降级通知 (compass_lost/depth_unavailable) |
| `GHOST_CONFIRMED` | L2A → L2B | 幽灵节点被否定 (EXPECTED → 确认不存在) |

### 5.3 修改的数据结构

**NodeState 枚举新增 EXPECTED:**

```python
class NodeState(Enum):
    ACTIVE = "active"
    EXPECTED = "expected"       # ★ 新增
    OCCLUDED = "occluded"
    OUT_OF_VIEW = "out_of_view"
    LOST = "lost"
    ANCHORED = "anchored"
```

**ObjectNode 新增字段:**

```python
@dataclass
class ObjectNode(SpatialNode):
    # ... 已有字段 ...

    # 新增: 证据累积
    evidence: EvidenceAccumulator = field(default_factory=EvidenceAccumulator)
    label_authority_source: str = "yolo_single"  # 当前标签来源
    
    # 新增: 预期关联
    expected_from: str = ""          # "session" | "last_session" | "graphiti" | ""
    expected_position: tuple | None = None  # 预期位置 (用于偏离检测)
```

**AR Telemetry 新增字段:**

```csharp
var telemetry = new {
    // ... 已有 ...
    
    // 新增: 异常检测用
    gravity_vector = Physics.gravity,                  // 重力方向 → 手机朝向
    camera_up_vector = cameraTransform.up,             // 摄像头上方向
    proximity = proximityValue,                        // 接近传感器
    frame_brightness = averageBrightness,              // 帧平均亮度
};
```

### 5.4 决策记录 (ADR-023 ~ ADR-028)

**ADR-023: NodeState 新增 EXPECTED — 幽灵节点的正式身份**
- 背景: 预加载场景时节点存在于记忆但未视觉确认
- 决策: 新增 EXPECTED 状态, 通过 EvidenceAccumulator 累积确认
- 否决: 直接用 ACTIVE (太乐观) 或直接用 LOST (太悲观)

**ADR-024: 证据累积式确认, 非全有全无**
- 背景: 多因素证据可能不完整 (有 mask 没 ReID, 有位置没锚点)
- 决策: 贝叶斯式分数累积, 阈值 0.6 确认, -0.3 否定
- 关键: 用户确认权重 1.0 一击必杀; 视觉证据 0.25 需累积多条
- 否决: 要求所有证据同时满足 (太苛刻) 或单一证据确认 (太宽松)

**ADR-025: ExpectationChecker — 预期偏离作为一类触发器**
- 背景: 主动感知需要"预期", 偏离预期是有价值的信息
- 决策: 在 L2-A 扫描完成后运行 ExpectationChecker, 产生 EXPECTATION_VIOLATED 触发器
- 4 种偏离类型: MISSING / DISPLACED / NEW_UNEXPECTED / COUNT_CHANGED
- 鹦鹉因此能说 "笔记本不见了" 而不只是 "我看到了杯子"

**ADR-026: 视觉模型标签权威链**
- 背景: YOLO-World / DINOv2 ReID / Gemini / 用户 可能给出不同标签
- 决策: 严格的权威排序: user > gemini > reid > yolo_voted > yolo_single
- 每个物体只有一个当前标签 (class_label), 但保留完整投票历史 (class_votes)

**ADR-027: 确认存在 vs 确认不存在的不对称处理**
- 用户洞察: "确认笔记本在桌上"和"确认笔记本不在桌上"流程不同
- 决策: 正面证据无限制累积; 负面证据受 4 个限制: 视锥体检查、Tier>=3、光照>=100lux、冷却10s
- 原则: 宁假阳不假阴 — 误认为在(后续自然修正) 远好于 误认为不在(丢失认知)

**ADR-028: 细粒度识别 = 给 Gemini 看裁切图, 不引入新模型**
- 用户问题: YOLO 识别不了奶茶品牌/咖啡款式/手办型号
- 决策: 裁切物体区域图发给 Gemini 做详细描述, 不引入 OCR/商品识别等专用模型
- 按需触发: 用户问/鹦鹉好奇/新物体出现时才做, 95%时间不需要
- 结果存入 ObjectNode.fine_description, 属于 gemini_described 权威级别
