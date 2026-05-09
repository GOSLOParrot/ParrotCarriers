# GOSLO AR App — 游戏 / App 总体介绍与素材收集 Brief

> 面向：美术资产收集、UI 白模制作、外部协作者快速理解项目。  
> 版本：2026-05-07 draft。  
> 关键词：AR companion、2D pixel meta UI、大小姐宅邸、纸条工作区、LiveKit 连接、GOSLO 标准动画、自定义模型/动画扩展。

---

## 1. 一句话介绍

**GOSLO AR App** 是一个把现实世界摄像头、LiveKit 实时语音视频、GOSLO 鹦鹉大小姐和 2D 像素风工具界面结合起来的个人 AR 互动 App。

用户拿起手机进入 AR 场景，GOSLO 像一只住在现实世界里的“鹦鹉大小姐”一样陪伴、聊天、观察、吐槽、执行简单动作；后台的女仆猫猫 / Nanobot 负责整理任务、递交纸条报告、处理长任务。复杂管理功能不塞进手机主界面，移动端优先做轻量、可爱、所见即所得的日常互动。

---

## 2. 产品定位

### 2.1 这不是传统游戏

它更像一个“AR 日常互动玩具 + 轻量工作台”：

- 真实世界是主场景，手机摄像头就是玩家视角。
- GOSLO 是可对话、可执行动作、可观察上下文的 AR companion。
- 2D 像素 UI 是覆盖在摄像头上的 Meta UI，不需要和真实世界做复杂物理碰撞。
- 工具、纸条、报告、菜单都像小型 2D 游戏界面一样展开。
- 后端能力藏在角色协作里，不直接把“数据库 / 图谱 / Worker / Pipeline”暴露给用户。

### 2.2 第一版白模目标

第一版不追求完整美术，而追求**功能闭环足够全面**：

- 启动页可以选房间、管线、人设 / 场景、权限和连接测试。
- LiveKit 连接生命周期完整，能连接、暂停、恢复、关闭。
- 进入 AR 主场景后有 HUD 和工具柜。
- 工具柜能打开拍照、放大镜、注意力框、2D 工作区、任务按钮等入口。
- 菜单能消费后端 4 类块和预设接口。
- GOSLO 能跑标准动画。
- 能 smoke 接入一个自定义模型 / 动画资源，例如 Ner。

---

## 3. 参考游戏与学习方向

### Stardew Valley

参考链接：[Stardew Valley 官网](https://www.stardewvalley.net/)

学习点：

- 启动页 / 主菜单的温暖像素风。
- 轻量、可读、低压力的功能入口。
- 背景微动效：窗帘、灯光、漂浮粒子、按钮 hover。
- 主菜单不是“冷冰冰设置页”，而是世界观的一部分。

用于本项目：

- 启动页背景可以是“大小姐宅邸”的门厅、窗边、书桌或鸟笼角落。
- 菜单按钮可以像木牌 / 羊皮纸 / 小卡片一样排列。
- 加载动画可以做成羽毛、脚印、猫爪、信封或 GOSLO 飞过。

### Papers, Please

参考链接：[Papers, Please 官网](https://papersplea.se/)

学习点：

- 桌面工作区布局：文件、印章、纸条、批准 / 拒绝动作。
- 高信息密度但仍然清楚的 2D 操作界面。
- 拖拽纸张、批改、放入不同区域的交互节奏。

用于本项目：

- 2D 工作区可以是“批改纸条 / 处理报告”的桌面。
- Nanobot 递交的纸条可以被展开、接受、拒绝、归档。
- 用户处理日程、提醒、报告时像在整理一张张像素文书。

### 像素报告 / 森林管理员类工作区游戏

学习点：

- 批改报告、看卡片、判断事件的轻量循环。
- 用纸张、文件夹、印章表达“后台任务完成了，需要你确认”。

用于本项目：

- Nanobot 结果回流不是弹一个现代 toast，而是“猫爪递纸条”。
- GOSLO 对纸条内容发表评论，形成角色互动。
- 长任务 / 研究任务 / 行程提醒都可以统一变成纸条或卡片。

---

## 4. 世界观与风格

### 4.1 默认主题：大小姐宅邸

第一版主主题是**大小姐宅邸**。

视觉气质：

- 温暖、复古、轻微维多利亚感。
- 像素羊皮纸、蕾丝边、木质按钮、金色边框。
- 黑白灰白模阶段先用简单色块，后续替换成暖色像素资产。
- AR 真实画面保持主视觉，2D UI 不要压满屏幕。

体验关键词：

- “GOSLO 住在你的现实空间里。”
- “女仆猫猫在后台帮忙，偶尔递来纸条。”
- “手机不是控制台，而是随手打开的小宅邸窗口。”

### 4.2 扩展主题：海盗换肤

海盗主题是后续换肤方向，不阻塞第一版。

角色关系：

- User 是船长。
- GOSLO 是大副。
- Nanobot / 女仆猫猫变成水手。

视觉元素：

- 深蓝、木质、黄铜、旧海图、火漆封、卷羊皮纸。
- 放大镜可以换成海盗望远镜。
- 摄像头可叠加脏镜片或半边眼罩遮挡滤镜。
- GOSLO 可以有眼罩头像 / skin。

实现原则：

- 先做默认宅邸主题的功能布局。
- 海盗主题作为同一套 UI 的皮肤替换，不重写流程。

---

## 5. 角色设定

### 5.1 GOSLO：鹦鹉大小姐

定位：

- 主陪伴角色。
- AR 场景中的主要互动对象。
- 负责聊天、动作表现、吐槽、提醒、轻量意图理解。

性格方向：

- 有大小姐感，但不是冷冰冰命令式。
- 会主动关注周围、好奇、撒娇、抱怨被挡住。
- 看不清时要承认看不清，不能瞎编。
- 被遮挡时可以用角色语气抱怨。

核心能力：

- 实时语音 / 文字对话。
- 根据后端状态知道自己是否看得清、是否连接正常。
- 执行标准动画：idle / fly / dance / wing_flap / head_bob / perch / sit / sleep。
- 根据菜单选择切换 persona / mode / scene / model。
- 使用拍照、注意力框、放大镜等工具的结果来理解用户意图。

白模表现：

- 初期可以用黑白灰占位模型或已有 GOSLO 模型。
- UI 上至少需要一个 GOSLO 头像占位。
- 动画用标准 GOSLO 动画完成 smoke。

### 5.2 女仆猫猫 / Nanobot：后台执行与纸条递交

定位：

- 后台任务执行者。
- 长任务、研究、整理、报告回流的拟人化入口。
- 在 UI 里表现为“女仆猫猫递来纸条”。

性格方向：

- 勤快、可靠、有一点猫猫感。
- 不抢 GOSLO 的主陪伴位置。
- 更像“把结果端到你面前”的角色。

核心能力：

- 接收 GOSLO / 用户派发的长任务。
- 把完成结果变成纸条、报告、卡片。
- 让用户在 2D 工作区里 accept / reject / open detail。

白模表现：

- 初期不需要完整角色动画。
- 需要猫爪伸出递纸条的占位动画。
- 需要猫猫头像 / 女仆 icon 的占位。

### 5.3 User：玩家 / 主人 / 船长

定位：

- 第一版是个人自用 Demo，不做大众 onboarding。
- 用户通过手机摄像头和 2D 工具表达意图。
- 用户不是在复杂控制台里调系统，而是在 AR 场景里“指给 GOSLO 看”。

交互方式：

- 说话。
- 点击启动页菜单。
- 展开 HUD / 工具柜。
- 拖动放大镜 / 注意力框。
- 拍照。
- 在 2D 工作区处理纸条。
- 选择人设 / 场景 / 模式 / 模型预设。

---

## 6. 角色协作方式

### 6.1 日常陪伴链路

1. 用户进入 AR 场景。
2. GOSLO 完成单次问候。
3. 用户说话或移动手机。
4. GOSLO 根据当前连接、视觉、音频状态做回应。
5. 用户打开工具柜，让 GOSLO 看某个区域、拍照或执行动作。

体验重点：

- GOSLO 要像“在场”，而不是像后台命令行。
- 看不见、连接差、视频暂停时，GOSLO 的话术要符合状态。

### 6.2 任务与纸条链路

1. 用户或 GOSLO 触发一个长任务。
2. Nanobot 在后台处理。
3. 完成后，女仆猫猫递来纸条。
4. 用户点击展开纸条。
5. 用户在工作区选择接受、拒绝、查看详情、稍后处理。
6. GOSLO 可以对纸条做简短评论。

体验重点：

- 任务结果不要像系统弹窗，要像“角色递交”。
- 纸条是把后端能力游戏化的主要 UI 隐喻。

### 6.3 观察与注意力链路

1. 用户拖出注意力框。
2. 在画面中框选一个区域。
3. App 上报“用户希望 GOSLO 关注这里”。
4. GOSLO 不一定立刻打断当前对话，可以后台理解。
5. 如果需要，用户可以再拍照或触发识别。

体验重点：

- 注意力框不是“强制中断按钮”。
- 它表达用户意图：请关注这里、这里可能重要。
- 第一版先做白模交互和事件通路，复杂行为策略后续增强。

---

## 7. App 总流程

### 7.1 启动到主场景

```text
打开 App
  ↓
2D 像素启动 Logo
  ↓
启动页菜单
  ↓
选择 / 确认本次配置
  - 开始 AR 主场景
  - LiveKit room
  - BrainAgent 管线
  - 人设 / 场景 / 预设
  - 场景 baseline：AR_HANDHELD / DESKTOP_WEBCAM
  - 权限 + 连接测试
  ↓
权限请求与连接状态展示
  ↓
2D 像素加载动画 / 转场
  ↓
进入 AR 主场景
  ↓
GOSLO 单次问候
  ↓
HUD + 工具柜可展开
```

### 7.2 主场景循环

```text
AR 主场景
  ├─ 日常对话
  ├─ GOSLO 动画 / 情绪 / 状态反馈
  ├─ HUD 查看连接、音频、视频、视觉状态
  ├─ 工具柜触发拍照、放大镜、注意力框、任务按钮
  ├─ 2D 工作区处理纸条 / 报告 / 行程
  └─ 菜单切换 model / persona / mode / scene / preset
```

### 7.3 暂停 / 恢复 / 关闭

```text
App 切后台
  ↓
进入 paused / reconnecting / recovering 状态
  ↓
视频和 AR 状态进入安全降级
  ↓
回到前台
  ↓
恢复 LiveKit / AR session
  ↓
HUD 显示恢复状态
  ↓
GOSLO 不重复问候，只做轻量恢复反馈
```

---

## 8. UI 总布局

### 8.1 主布局原则

- 屏幕中心留给 AR 摄像头和 GOSLO。
- 2D UI 只放两个常驻入口：HUD 和工具柜。
- HUD 与工具柜放在对角。
- 不做复杂横竖屏自动识别。
- 展开方向由用户选择并持久化。
- 2D UI 是 Meta UI，不需要和真实世界物体发生碰撞。

### 8.2 默认布局

```text
┌────────────────────────────────────┐
│ HUD 收纳 / 展开                    │
│ 连接 音频 视频 Brain 视觉 时间天气 │
│                                    │
│                                    │
│          AR 摄像头 + GOSLO          │
│                                    │
│                                    │
│                 工具柜 收纳 / 展开 │
│                 设置 拍照 放大镜   │
│                 注意力框 工作区    │
└────────────────────────────────────┘
```

### 8.3 HUD

HUD 显示“当前系统是否能正常陪伴”的摘要。

内容：

- 时间。
- 天气占位。
- LiveKit 连接状态。
- 麦克风 / 音频状态。
- 视频档位。
- Brain presence。
- 视觉自我感知状态：active / degraded / paused / blocked。

交互：

- 点击收纳 / 展开。
- 选择横向或竖向展开。
- 可切换四个角中的一个作为 HUD 位置。

白模素材：

- HUD 收纳 icon。
- 横向背景板。
- 竖向背景板。
- 状态 icon 组。
- 时间 / 天气 icon 占位。

### 8.4 工具柜

工具柜是“玩家把意图交给 App 的地方”。

第一版工具：

- 设置。
- 相机模式 / 视频档位。
- 拍照。
- 放大镜。
- 注意力框。
- 常用任务按钮。
- 2D 工作区入口。
- 节点画布 / 预设菜单入口。

白模表现：

- 每个工具先用黑白灰 icon + 文字标签。
- 展开后可以横排或竖排。
- 长按 / 点击某些工具后可以拖到画面上。

---

## 9. 2D 工作区

### 9.1 定位

2D 工作区是 AR 主场景之外的轻量处理桌。

用途：

- 处理 Nanobot 纸条。
- 看报告。
- 看提醒。
- 看行程。
- 处理 GOSLO 提出的任务或计划占位。

第一版不做复杂 Plan UI wire，只做可交互白模：

- 卡片列表。
- 纸条展开。
- accept。
- reject。
- open detail。
- back to AR。

### 9.2 视觉

默认主题：

- 木桌 / 羊皮纸 / 文件夹 / 小印章。
- 黑白灰白模先用矩形卡片与标签。

海盗主题：

- 老海图桌面。
- 卷羊皮纸。
- 火漆封。
- 海盗手套递交。

### 9.3 AR 背景处理

进入工作区时可以有两种模式：

- AR 画面变暗，作为背景保留。
- AR 画面暂时关闭 / 冻结，以减少干扰。

第一版建议：

- 先做全屏半透明黑遮罩 + 2D 桌面 panel。
- 后续再决定是否保留实时 AR 背景。

---

## 10. 菜单与预设

### 10.1 4 类块

用户可选择或保存一组组合：

- Model：GOSLO 默认模型 / 自定义模型，例如 Ner。
- Persona：GOSLO 默认大小姐人设 / 后续海盗大副等。
- Mode：BASE / COMPANION / BUTLER / RESEARCHER / PLAYFUL / ROLEPLAY。
- Scene：AR_HANDHELD / DESKTOP_WEBCAM，后续扩展 home / outdoor / kitchen 等。

### 10.2 默认菜单 fallback

节点画布是高级功能，第一版先做普通列表菜单：

```text
人设 / 场景配置
  模型: [GOSLO_default ▼]
  设定: [goslo_parrot_default ▼]
  模式: [BASE] [COMPANION] [PLAYFUL] ...
  场景: [ar_handheld ▼]

  [应用]
  [保存为预设]
  [恢复默认]
```

### 10.3 节点画布方向

后续可以做 ComfyUI / n8n 风格：

- Model 蓝块。
- Persona 粉块。
- Mode 黄块。
- Scene 绿块。
- 过滤器灰块。
- 有效期预测模块橙块。

第一版只需要入口和占位，不阻塞白模。

---

## 11. 工具细化建议

### 11.1 放大镜 / 海盗望远镜

功能：

- 放大手机画面，包括 UI。
- 可拖动。
- 可调节倍率。
- 默认主题是圆形放大镜。
- 海盗主题替换为望远镜。

白模建议：

- 一个可拖动圆形 mask。
- 边缘用灰色圆环。
- 旁边有 + / - 或滑条控制倍率。

需要资产：

- 放大镜 icon。
- 放大镜圆形边框。
- 放大镜拖动状态。
- 望远镜皮肤。
- 倍率按钮 / 滑条。

### 11.2 注意力框 / Bounding Box

功能：

- 用户拖动一个 2D 框圈出画面区域。
- 表达“GOSLO 看这里”。
- 可放置、调整、删除。
- 可触发后端关注 / 识别 / 截图链路。

白模建议：

- 四角 corner sprite。
- 虚线边框。
- placed 状态变成亮色。
- deleting / removing 有淡出动画。

需要资产：

- 四角 corner。
- 横竖边框 9-slice。
- placed 状态高亮。
- remove 小按钮。

### 11.3 拍照按钮

功能：

- 工具柜一键拍照。
- 生成预览和后端可用图片资产。
- GOSLO 可评论。

白模建议：

- 相机 icon。
- 点击后屏幕轻微白闪。
- 左下或纸条区域出现 preview card。

需要资产：

- 拍照按钮 normal / pressed。
- 快门闪光。
- 图片 preview 边框。

### 11.4 纸条 / 报告

功能：

- Nanobot 或系统递交消息。
- 点击展开阅读。
- 拖到工作桌 = accept。
- 拖到垃圾桶 = reject。

白模建议：

- 初期用灰色纸条 + 猫爪矩形占位。
- 纸条可从屏幕底部滑出。
- 展开时放大到中央 panel。

需要资产：

- 猫爪伸出动画。
- 纸条 folded / expanded。
- 工作桌 accept 区。
- 垃圾桶 reject 区。
- 纸张音效可后补。

### 11.5 物品栏抽屉 / 2D 贴图箱

功能：

- 放一些可拖出的 2D 贴纸。
- 贴在画面上用于截图打卡或视觉标记。

白模建议：

- 工具柜里一个小抽屉按钮。
- 打开后出现 2D 贴纸网格。
- 拖出贴纸到画面。

需要资产：

- 抽屉 icon。
- 贴图箱 panel。
- 6-12 个贴纸占位。
- 贴纸选中 / 拖动状态。

### 11.6 常用任务按钮

功能：

- 快速触发 GOSLO 动作或后端任务。

第一版按钮建议：

- fly。
- animate / dance。
- perch。
- take photo。
- ask GOSLO to look here。
- dispatch task。

需要资产：

- 每个按钮 64x64 icon。
- normal / pressed / disabled 三态。

---

## 12. 资产清单

> 这里列的是“需要留空位”的资产。白模阶段全部可以用黑白灰色块 + 文字标签替代。

### 12.1 P0：第一版白模必须有空位

| 类别 | 资产空位 | 说明 |
|:--|:--|:--|
| 启动页 | logo | GOSLOParrot / ParrotCarriers |
| 启动页 | loading animation | 羽毛 / 点点 / 猫爪均可 |
| 启动页 | boot background | 大小姐宅邸主背景 |
| 启动页 | menu button 3-state | normal / hover / pressed |
| HUD | collapsed icon | 小状态入口 |
| HUD | horizontal panel | 横向 9-slice |
| HUD | vertical panel | 竖向 9-slice |
| HUD | status icons | connection / audio / video / brain / visual |
| 工具柜 | collapsed icon | 工具入口 |
| 工具柜 | panel background | 横 / 竖展开底板 |
| 工具 | settings icon | 设置 |
| 工具 | camera mode icon | 视频档位 / 相机模式 |
| 工具 | photo button | 拍照 |
| 工具 | magnifier | 放大镜 |
| 工具 | attention box | 四角 + 边框 |
| 工具 | common task buttons | 4-6 个 |
| 字体 | readable pixel font | 中文可读优先 |
| 通用 | 9-slice button frame | 默认 / 激活 / 警告 |

### 12.2 P1：体验补全资产

| 类别 | 资产空位 | 说明 |
|:--|:--|:--|
| 反馈 | cat paw animation | 女仆猫猫递纸条 |
| 反馈 | paper note folded / expanded | 纸条 |
| 反馈 | accept desk | 处理成功区 |
| 反馈 | trash reject | 丢弃区 |
| 工作区 | dark AR overlay | 进入 2D 工作区时压暗背景 |
| 工作区 | work desk background | Paper Please 风桌面 |
| 工作区 | report cards | 报告 / 行程 / 反馈卡片 |
| 角色 | GOSLO 2D avatar | idle / talking / sleeping |
| 角色 | Nanobot / maid cat avatar | 通知和纸条用 |
| 通用 | small particles | 羽毛 / 星光 / 心形 |

### 12.3 P2 / P3：高级与换肤资产

| 类别 | 资产空位 | 说明 |
|:--|:--|:--|
| 节点画布 | model block | 蓝色节点块 |
| 节点画布 | persona block | 粉色节点块 |
| 节点画布 | mode block | 黄色节点块 |
| 节点画布 | scene block | 绿色节点块 |
| 节点画布 | filter block | 灰色占位 |
| 节点画布 | memory validity block | 橙色占位 |
| 海盗 | telescope skin | 望远镜替放大镜 |
| 海盗 | eyepatch overlay | 半边黑色遮挡 |
| 海盗 | dirty lens filter | 脏镜片 |
| 海盗 | treasure map HUD | 老海图 HUD |
| 海盗 | scroll paper | 卷羊皮纸 |
| 海盗 | GOSLO eyepatch avatar | 大副 skin |
| 海盗 | sailor cat avatar | 水手 / Nanobot |

### 12.4 自定义模型 / 动画资源空位

用于 Ner 或后续自定义模型。

| 资产 | 说明 |
|:--|:--|
| model file | glb / prefab / Unity 可加载资源 |
| preview image | 256x256 模型预览 |
| manifest entry | model_id / asset_path / controller_type / capabilities |
| idle animation | 最低 smoke 动画 |
| custom animation | Ner 专属动作，可先映射到 animate smoke |
| fallback mapping | 若自定义动画缺失，回退到标准 GOSLO 动画 |

---

## 13. GOSLO 动画完成标准

第一版白模需要能测试标准 GOSLO 动画：

- idle。
- fly。
- dance。
- wing_flap。
- head_bob。
- perch。
- sit。
- sleep。

验收方式：

1. 从工具柜任务按钮触发至少 2 个动作。
2. 从 Brain / RPC 路径触发至少 1 个动作。
3. 标准 GOSLO 模型能正常播放。
4. 自定义模型 / Ner 如果没有同名动画，走 fallback，不崩溃。
5. HUD 或小 toast 显示动作执行结果。

---

## 14. 第一版功能清单

### 启动页

- 开始 AR。
- LiveKit room 显示 / 输入。
- BrainAgent 管线选择。
- 人设 / 场景 / preset 入口。
- Scene baseline：AR_HANDHELD / DESKTOP_WEBCAM。
- 权限 + 连接测试。

### 主场景

- AR 摄像头背景。
- GOSLO 模型 / 占位。
- 单次问候。
- 连接恢复后不重复问候。
- 标准动画 smoke。

### HUD

- 连接状态。
- 音频状态。
- 视频档位。
- Brain presence。
- visual_state。
- 时间 / 天气占位。

### 工具柜

- 设置。
- 相机模式 / video tier。
- 拍照。
- 放大镜。
- 注意力框。
- 常用任务按钮。
- 2D 工作区入口。
- 菜单 / 预设入口。

### 2D 工作区

- 纸条列表。
- 展开详情。
- accept / reject。
- 返回 AR。
- AR 背景变暗。

### 菜单 / 预设

- list menu blocks。
- apply menu selection。
- apply preset。
- save as preset。
- 默认 preset fallback。

---

## 15. 白模视觉规范

### 15.1 黑白灰占位规则

白模阶段统一使用：

- 深灰：背景和遮罩。
- 中灰：panel。
- 浅灰：按钮。
- 白色：文字。
- 黑色：边框。
- 单一强调色：表示 selected / active / warning。

每个占位控件必须有文字标签，例如：

- HUD。
- TOOLBOX。
- PHOTO。
- MAGNIFIER。
- BBOX。
- WORKSPACE。
- APPLY PRESET。

### 15.2 资产替换规则

- 先保证控件命名和交互稳定。
- 图片资源后续按同名 slot 替换。
- 不因为换 sprite 改流程。
- 不因为美术没到位阻塞 LiveKit 生命周期、菜单接口、动画 smoke。

---

## 16. 后续 Build 顺序建议

### Phase A：连接和启动

完成 LiveKit 生命周期、启动页、权限、连接状态、AR session 入口。

### Phase B：主场景白模

完成 HUD、工具柜、GOSLO 放置、单次问候、基础动画 smoke。

### Phase C：工具交互

完成拍照、放大镜、注意力框、任务按钮白模。

### Phase D：菜单和预设

接后端 list / apply / preset / save 接口，完成默认 fallback 菜单。

### Phase E：2D 工作区

完成纸条、报告、行程卡片、accept / reject / detail。

### Phase F：资产替换与自定义模型

替换 UI 素材，接入 Ner 或其他自定义模型 / 动画，完成 smoke。

---

## 17. 需要你先决定 / 收集的内容

### 17.1 美术资产

建议先找：

- 启动页背景。
- 可读中文像素字体。
- HUD / 工具柜 panel 风格。
- 放大镜或望远镜。
- 纸条。
- 猫爪或女仆猫猫头像。
- GOSLO 头像。
- 按钮 9-slice。

### 17.2 交互偏好

需要你确认：

- HUD 默认放哪个角？
- 工具柜默认放哪个对角？
- 展开默认横向还是竖向？
- 2D 工作区进入时，AR 背景是变暗还是关闭？
- 纸条处理是“拖到桌面 / 垃圾桶”，还是先用按钮 accept / reject？
- Ner 是模型名、角色名，还是某个自定义动画名？
- Ner 的第一条 smoke 动画希望叫什么？

### 17.3 主题优先级

建议：

- 第一版只做大小姐宅邸。
- 海盗主题只预留 asset slot。
- 如果你已经找到海盗望远镜 / 眼罩 / 海图素材，也可以提前放进 slots，但不阻塞第一版。

---

## 18. 对外描述短版

GOSLO AR App 是一个个人 AR companion demo：用户通过手机摄像头进入现实世界叠加的 AR 主场景，与鹦鹉大小姐 GOSLO 语音互动；后台女仆猫猫 / Nanobot 负责处理任务并以像素纸条形式递交结果。App 使用 2D 像素风 Meta UI，把启动页、HUD、工具柜、放大镜、注意力框、纸条工作区和预设菜单做成轻量游戏化界面。第一版以黑白灰白模完成完整功能闭环，素材后续替换为大小姐宅邸主题，并预留海盗主题换肤。

