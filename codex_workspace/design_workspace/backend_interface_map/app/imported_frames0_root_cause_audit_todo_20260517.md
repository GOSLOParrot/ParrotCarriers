# 顶级诊断报告 + TODOList — frames=0 根因审计 (2026-05-17)

---

## 一、5 路审计核心结论一览

| 审计领域                       |   已修 (在审计文档里)    | 新发现 P0 | 新发现 P1 | 新发现 P2 |
| ------------------------------ | :----------------------: | :-------: | :-------: | :-------: |
| **音频上行链路**               |           多项           |     2     |     5     |     7     |
| **视频上行链路**               |            0             |     3     |     2     |     4     |
| **Lifecycle / 重连 / 切后台**  |            0             |     0     |     8     |     4     |
| **ECS LiveKit / Brain / TURN** |            0             |     2     |     4     |   多项    |
| **蓝牙 / SCO 路由**            | BLE 识别 / SCO 16k retry |     3     |     3     |   多项    |
| **共计**                       |            —             | **10 P0** | **22 P1** | **多项**  |

> 重要事实：今日审计文档已修复的 bug **全部都在 master（commit `4edfcd0`）里了**，但**手机上跑的不是这个 build**——这是用户上一条消息已确认的。本次审计的 22 个新 P0/P1 bug，**全部是审计文档没覆盖的，不在已修列表里**。

---

## 二、frames=0 的真因排序（基于客观代码事实）

### 关键观察：下行通 ≠ ECS / 网络无问题

> 下行 RTP 在通：用户能听见 GOSLO/Parrot 说话 → STUN/TURN 双向 NAT binding 已建立 → UDP 50000-50200 在双向通 → LiveKit server 在收发 → Brain agent 在房间。

> 上行帧 = 0 意思是 **LiveKit Unity SDK 的 `MicrophoneSource.AudioRead` 计数器 = 0**。这绝对发生在**客户端**（PCM 帧没进入 LiveKit Unity SDK 的本地源）。

**因此根因 95% 在客户端 PCM 采集层及其以下。**

### P0 嫌疑根因排序

|  排名   | 根因                                                         | 文件位置                                                     | 触发条件                                                     |                   frames=0 解释力                    |
| :-----: | ------------------------------------------------------------ | ------------------------------------------------------------ | ------------------------------------------------------------ | :--------------------------------------------------: |
| **#1**  | **缺 `FOREGROUND_SERVICE_MICROPHONE` 声明 + 无前台服务**     | `unity/ArSpike/Assets/Plugins/Android/ParrotAudioRoute.androidlib/AndroidManifest.xml`（仅 RECORD_AUDIO）+ 无 `Assets/Plugins/Android/AndroidManifest.xml` | vivo OriginOS Android 14 后台 AudioRecord 被静默 throttle    |                        ★★★★★                         |
| **#2**  | **PCM 捕获线程 read<0 不退出（busy loop）**                  | `AndroidPcmMicCapture.java:219-225`                          | AudioRecord 启动了但系统拒绝读取（vivo 后台限制 / 路由切换 / 蓝牙握手未完成）→ 线程 busy loop 但永不投帧 |                        ★★★★★                         |
| **#3**  | **Java AndroidAudioRouteManager singleton reinit 静默覆盖回调** | `AndroidAudioRouteManager.java:86`                           | OnEnable/OnDisable 反复触发 → AudioRouteManager 永久失聋 → 路由变化不再触发 republish |                         ★★★★                         |
| **#4**  | **`useWebcamFallback=true` 默认开**                          | `ARVideoPublisher.cs:77`                                     | ARCore 路径失败 → 静默切 WebCam → HUD 显 `fresh` 但 Brain 收到的不是 AR 画面（用户说"视频不知道有没有连上"的直接答案） | ★★★★（视频问题，非 frames=0 但是用户报告的视频疑虑） |
| **#5**  | **`AudioRoutePolicyBrainReporter` 动态 AddComponent + `[DisallowMultipleComponent]`** | `AudioRoutePolicyBrainReporter.cs:258-259`                   | 并发 Start 时抛异常（被 Unity 警告吃掉）→ 静默不 wire 真 router |                         ★★★                          |
| **#6**  | **`setCommunicationDevice` 被拒时无重试 / 无 fallback**      | `AndroidAudioRouteManager.java`（详见子审计）                | iQOO 蓝牙握手未完成时 setCommunicationDevice 返回 false → bt-sco route claimed 但 native 拒读 |                         ★★★                          |
| **#7**  | **Brain Docker 路径锁旧版 `livekit-agents>=0.10,<1.0`**      | `infra/Dockerfile.brain`                                     | 如果 ECS 是用 `--profile brain` 跑 docker，会 ImportError 炸掉（需现场核查 brain 实际怎么跑） |           ★★（如果走 systemd 跑则不相关）            |
| **#8**  | **iQOO 上 `ARSession.SessionTracking` 冷启动 > 3s `T_FIRST_FRAME_TIMEOUT`** | `ARVideoPublisher.cs` + `ParrotLifecycleConfig`              | 视频轨永远不发布，audio 不受影响但用户报"视频不知有没有连"   |                          ★★                          |
| **#9**  | **`T_SHUTDOWN_COOLDOWN=5s` < 30s ICE 残留**                  | `ConnectionLifecycleSentinel`（详见子审计）                  | identity 抢占 / Brain STT context 丢失                       |                          ★★                          |
| **#10** | **UDP 50000-50200 / 7881 / 7888 阿里云安全组**               | ECS 现场                                                     | 下行通能反证不像，但需现场确认                               |                          ★                           |

---

## 三、对比审计：「已修」vs「新发现」

> 用户说："这些 bug 都修的差不多了，但问题依旧没有解决。"
> **真相：审计文档已修的是 LiveKit + Android 两层冲突类问题（policy/snapshot/republish 风暴）。但 frames=0 的更深层根因是 PCM 帧根本没产生（Java 层 / vivo OEM 限制 / Manifest 漂移），这一类 bug 审计文档完全没碰。**

### 已修 vs 新发现对照表

| 类别                                     | 审计文档已修                                                 | 本次新发现                                              |
| ---------------------------------------- | ------------------------------------------------------------ | ------------------------------------------------------- |
| **路由 snapshot / republish 风暴**       | ✅ AudioRouteDetector 误报 SCO 修复 / `requires_mic_republish=true` 误触发修复 / `OnRoomConnected` 触发 snapshot 链路修复 | —                                                       |
| **temporary preference 粘性**            | ✅ phone_mic fallback 不再被 device_added/removed 撤销        | —                                                       |
| **Communication mode 重复入口**          | ✅ 只在 publish 协程内拥有                                    | —                                                       |
| **抑制窗口长度**                         | ✅ 0.75s → 4s（覆盖 mic startup）                             | —                                                       |
| **AudioRoutePolicyBrainReporter**        | ✅ 改为只观察不创建 router                                    | —                                                       |
| **PCM thread 异常 swallow**              | ✅ pcm_callback_failed 现在 emit 后 break                     | —                                                       |
| **SDK Unpublish 不释放 source**          | ✅ MicrophonePublisher 显式 Detach + Stop + Dispose           | —                                                       |
| **PCM thread `read<0` busy loop**        | ❌                                                            | ⚠️ **未修**：line 219-225 只 sleep 不 break              |
| **Java singleton reinit 覆盖回调**       | ❌                                                            | ⚠️ **未修**：每次 initialize() 静默覆盖                  |
| **缺 FOREGROUND_SERVICE_MICROPHONE**     | ❌                                                            | ⚠️ **未修**：vivo Android 14 后台麦克风的核心治理点      |
| **WebCam fallback 默认开**               | ❌                                                            | ⚠️ **未修**：正式 AR build 静默走 WebCam                 |
| **ReportVideoPublished 提前**            | ❌                                                            | ⚠️ **未修**：黑帧期被推上去                              |
| **RebuildTrack 协程竞争**                | ❌                                                            | ⚠️ **未修**：Room 断开期 NRE 风险                        |
| **ARCore resume 不等 SessionTracking**   | ❌                                                            | ⚠️ **未修**：回前台 0.5-2s 黑帧推 Brain                  |
| **30s ICE cool-down**                    | ❌                                                            | ⚠️ **未修**：T_SHUTDOWN_COOLDOWN=5s                      |
| **ECP intent.disconnect 缺失**           | ❌                                                            | ⚠️ **未修**                                              |
| **Brain Docker 锁旧 SDK 版本**           | ❌                                                            | ⚠️ **未修**：Dockerfile.brain pin `<1.0` 但代码用 1.x    |
| **`env-castle.template` 真实密钥进 git** | ❌                                                            | ⚠️ **新发现安全问题**：staged diff 含 `DEEPSEEK_API_KEY` |

---

## 四、**顶级 TODOList**（按优先级 + 修复成本）

### 🔥 P0 — 阻塞 frames=0 修复，必须先做

|     #     | 任务                                                         | 文件 / 位置                                                  | 估时  | 依赖           |
| :-------: | ------------------------------------------------------------ | ------------------------------------------------------------ | :---: | -------------- |
| **P0-1**  | **新增 app 级 AndroidManifest.xml**：声明 `<service android:foregroundServiceType="microphone">` + `FOREGROUND_SERVICE` + `FOREGROUND_SERVICE_MICROPHONE` 权限 | 新建 `unity/ArSpike/Assets/Plugins/Android/AndroidManifest.xml` | 30min | —              |
| **P0-2**  | **实现 ParrotMicForegroundService**：在 `MicrophonePublisher.PublishAsync` 启动时拉起 ForegroundService（type=microphone），UnpublishAndStop 时 stop | 新建 `unity/ArSpike/Assets/Plugins/Android/ParrotAudioRoute.androidlib/src/main/java/com/parrotcarriers/audio/ParrotMicForegroundService.java` | 1.5h  | P0-1           |
| **P0-3**  | **修 PCM 捕获线程 read<0 退出策略**：连续 N 次 read<0（比如 3 次 / 200ms 累计无进展）就 break 并 emit `read_error_persistent`，让 MicrophonePublisher 走 retry ladder | `AndroidPcmMicCapture.java:219-225`                          | 30min | —              |
| **P0-4**  | **修 Java AndroidAudioRouteManager singleton reinit**：再次 initialize() 时若 callback 不同，先 dispose 旧 listener、卸 deviceCallback，再注册新的；或者让 initialize() 仅首次执行，后续走 setSnapshotCallback() | `AndroidAudioRouteManager.java:84-93`                        |  1h   | —              |
| **P0-5**  | **关闭 ARVideoPublisher.useWebcamFallback 默认值**：改成 `false`；只在 `UNITY_EDITOR \|\| !UNITY_AR_FOUNDATION` 时允许；正式 AR build 走 WebCam 应当显式打开 dev menu | `ARVideoPublisher.cs:77`                                     | 15min | —              |
| **P0-6**  | **HUD 添加 `Source` 字段**：显示视频源真相（`AR` / `WebCam` / `none`），让用户在 HUD 上看到真相而不是仅看 fresh | `ARVideoPublisher.cs` + `FormalHomeHudController.cs`         | 30min | —              |
| **P0-7**  | **修 ReportVideoPublished 时序**：`PublishTrack` 成功 → 等到 `ARCameraManager.frameReceived` 真触发了至少 N 帧 → 才报 `video_published=true`；中间状态报 `video_publishing` | `ARVideoPublisher.cs`                                        |  1h   | —              |
| **P0-8**  | **修 RebuildTrack/StopPublishingLocal 协程竞争**：用 `_rebuildToken` CancellationTokenSource，Room 断开时取消、StopPublishingLocal 时取消，Rebuild 进入前 check token | `ARVideoPublisher.cs`                                        |  1h   | —              |
| **P0-9**  | **检查并修复 `AudioRoutePolicyBrainReporter` 动态 AddComponent**：改为只 `FindObjectOfType` + 找不到就 log warning，不再 AddComponent；Inspector 显式注入 | `AudioRoutePolicyBrainReporter.cs:258-259`                   | 30min | —              |
| **P0-10** | **Rebuild APK + 16KB 对齐验证**（审计文档已建议）            | `tools/verify_so_alignment.ps1` after APK build              | 20min | P0-1..9 完成后 |

### 🟧 P1 — Lifecycle / 防御 / 协议升级

|     #     | 任务                                                         | 文件 / 位置                                      | 估时  |
| :-------: | ------------------------------------------------------------ | ------------------------------------------------ | :---: |
| **P1-1**  | **修 ARVideoPublisher 回前台不等 SessionTracking**：解除 `_blitPaused` 前 yield-loop 等到 `ARSession.state == SessionTracking` + `frameReceived` 触发 1 次 | `ARVideoPublisher.cs`                            |  1h   |
| **P1-2**  | **`T_SHUTDOWN_COOLDOWN=5s → 35s`**：盖过 LiveKit 服务器 30s ICE 残留窗口 | `ParrotLifecycleConfig`                          | 10min |
| **P1-3**  | **新增 ECP `intent.disconnect` event**：客户端主动 leave 时显式发，Brain 收到后立即 release STT context；被动断连时 Brain 等 35s 再 release | `src/parrot/shared/ecp.py` + Unity DTO + handler |  2h   |
| **P1-4**  | **修 RoomManagerLifecycleBridge 状态机错位**：`Connected/Running` 收到 `OnConnecting` 时不走 reconnect 路径 | `RoomManagerLifecycleBridge.cs`                  | 30min |
| **P1-5**  | **VideoTierReceiver.OnDestroy unregister RPC handler**       | `VideoTierReceiver.cs`                           | 10min |
| **P1-6**  | **`T_FIRST_FRAME_TIMEOUT 3s → 8s`**：iQOO 冷启动场景 ARCore 可能 5+秒 | `ParrotLifecycleConfig`                          | 10min |
| **P1-7**  | **回前台后强制 route policy refresh + republish**：`OnApplicationFocus(true)` 时 `routeManager.Refresh()` + `RequestMicrophoneRebuild("focus_resume")` | `MicrophonePublisher.cs`                         | 30min |
| **P1-8**  | **`_lastAudioReadPeak` 加 `Volatile.Write/Read`**：诊断稳定性 | `MicrophonePublisher.cs:136`                     | 5min  |
| **P1-9**  | **`setCommunicationDevice` retry ladder**：被拒时 100ms 后重试 2 次，仍失败则降级到 `phone_default_microphone` | `AndroidAudioRouteManager.java`                  | 45min |
| **P1-10** | **HUD `nerr=` / `native=` 持续显示**：审计文档说"after failed startup native= / nerr= 现在 survive cleanup"——验证它真在 HUD 显示（用户截图没看见？） | `FormalHomeHudController.cs`                     | 20min |
| **P1-11** | **`VideoStateReporter` vs `ARVideoPublisher` single-producer**：删去 VideoStateReporter 写 `video_lifecycle_reason` 的代码 | `VideoStateReporter.cs`                          | 20min |
| **P1-12** | **PhotoController 截图改用 `_rt`（ARCore RT）而非 Camera.main 渲染**：保证拍照内容与视频一致 | `PhotoController.cs`                             | 30min |
| **P1-13** | **修复 `env-castle.template` 安全问题**：staged diff 里有真实 DEEPSEEK_API_KEY → 还原为占位符 + 把真实密钥放 `.env.castle`（gitignored） | `infra/env-castle.template`                      | 5min  |
| **P1-14** | **Brain Docker SDK 版本对齐**：`infra/Dockerfile.brain` 把 `livekit-agents>=0.10,<1.0` 改为 `>=1.5,<2.0`（与 pyproject 对齐） | `infra/Dockerfile.brain`                         | 5min  |

### 🟨 P2 — 网络 / ECS / 服务端核查（**不是修代码，是去 ECS 上跑命令**）

|     #     | 任务                                                         | 命令                                | 估时  |
| :-------: | ------------------------------------------------------------ | ----------------------------------- | :---: |
| **P2-N1** | **核查 ECS 安全组**：UDP 50000-50200 入方向是否真在；TCP 7880/7881/7888 是否在；阿里云控制台截图存档 | 阿里云控制台 → 安全组 → 入方向规则  | 5min  |
| **P2-N2** | **核查 Brain 实际怎么跑**：`pgrep -af "parrot.brain.agent"` + `systemctl status parrot-brain` + `tmux ls`，确认是 systemd / docker / tmux 哪条路径 active；同时跑会抢 dispatch | SSH ECS                             | 10min |
| **P2-N3** | **核查 `.env.castle`**：`ls -la /opt/parrotcarriers/.env.castle` + `head /opt/parrotcarriers/.env.castle` 确认 `GOOGLE_API_KEY` / `LIVEKIT_API_SECRET` 真值 | SSH ECS                             | 5min  |
| **P2-N4** | **核查 Brain 日志里 user 音频是否到达 Gemini**：`journalctl -u parrot-brain -n 200 \| grep -E "(Gemini·用户\|audio_track_subscribed\|publish_audio)"` → 如果完全没 `Gemini·用户` = 上行根本没到 Gemini；如果有但 Unity 没反应 = Gemini 处理回路问题 | SSH ECS                             | 10min |
| **P2-N5** | **核查 `livekit.yaml` `secret` 与 Unity Resources 的 `parrot_config.json` 对齐**：JWT 签名错误下行也通不了，所以这条不太可能但要排除 | SSH ECS + Unity Editor 看 Resources | 10min |
| **P2-N6** | **测 ECS UDP 上行**：`adb shell ss -anu \| grep <ICE远端端口>` 看手机端 UDP 包是否真发出去（验证不是手机本地 firewall 拦） | adb + ECS tcpdump                   | 30min |
| **P2-N7** | **TURN 启用评估**：当前 `livekit.yaml` `turn:` 全注释；如果 NAT 严苛时直连失败可能让上行 fail（但下行成功反证 ICE 通）。优先级低 | `infra/livekit/livekit.yaml`        |   —   |
| **P2-N8** | **`gemini-2.5-flash-native-audio-preview-12-2025` 模型可用性确认**：preview 模型有 deprecation 风险；如果 deprecated 会让 STT 静默不回 | Google AI Studio + Brain 启动日志   | 10min |

### 🟩 P3 — 升级 / 治理

|    #     | 任务                                                         | 估时 |
| :------: | ------------------------------------------------------------ | :--: |
| **P3-1** | 移除所有 `[Tooltip]` 默认 `useWebcamFallback / FindObjectOfType / 自动 AddComponent` 路径，强制 Inspector 注入 |  2h  |
| **P3-2** | 把 LineA / LineB 的 echo policy 决策从 `AudioRoutePolicyBrainReporter` 单向 mirror 改成 ECP `audio.route_changed` event |  4h  |
| **P3-3** | 把 `MicrophonePublisher` 拆成 `LiveKitMicExecutor` + `MicrophoneCaptureSelector`（capture vs LiveKit publish 解耦） |  1d  |
| **P3-4** | `LifecycleShutdownService` 接入 `intent.disconnect` ECP（绑 P1-3） | 半天 |
| **P3-5** | 写 `tests/test_unity/test_audio_uplink_proof_static.py`：static 验证 manifest / FOREGROUND_SERVICE_MICROPHONE / WebCam fallback 默认值等 |  2h  |

---

## 五、**两阶段 Runbook**

### 阶段 A：修代码 + rebuild（4-6 小时）

```
1. 改 P0-1..9 (4h)
2. uv run pytest tests/test_unity/test_app_v1_meta_ui_static.py -q
3. Unity Build → APK
4. tools\verify_so_alignment.ps1 <apk>
5. adb install -r <apk>
```

### 阶段 B：手机 + ECS 现场诊断（1-2 小时）

```
phone:
  adb logcat -c
  adb logcat | grep -E "(MicrophonePublisher|AndroidPcmMic|ARVideoPublisher|RtcAudioSource)" > phone.log
  
启动 App → 点 START → 说话 30s → 看 HUD：

诊断分支 1: HUD frames 仍 = 0
  ├── native= ?
  │   ├── started      → P2-N4 (ECS Brain 日志看是否收到)
  │   ├── start_failed:record_audio_permission_denied → 权限没给
  │   ├── start_failed:audio_record_init_failed → vivo 限制 / sample rate 不支持
  │   ├── read_error_persistent → P0-3 修了之后会进 retry ladder, 看 fb=
  │   └── pcm_callback_failed → JNI 桥接失败
  ├── nerr= ?
  └── 看 Foreground service 是否拉起 (log "ParrotMicForegroundService.onStartCommand")

诊断分支 2: HUD frames > 0 + peak 响应 + 但 Brain 听不到
  → 100% ECS / Brain / Gemini 侧问题
  → 跑 P2-N1..N8 整套
  → 重点看 Brain 日志 `Gemini·用户` 出现没

诊断分支 3: HUD 显示 source=WebCam 而不是 AR
  → P0-5 没生效 / ARCore 真没起 → 看 SessionTracking
  → 视频问题与 frames=0 无关，但解释了"视频不知道有没有连"
```

---

## 六、给用户的关键判断

### 1. ECS 端问题概率：**< 5%**

下行通的事实证明 LiveKit server / TURN / UDP / Brain 都在房，**不需要先动 ECS**。但 P2-N 系列命令在阶段 B 里要顺手跑一遍排除（10min 成本）。

### 2. 客户端 frames=0 概率最高的 3 个原因（**你之前那条消息的分支表只覆盖了 1 个**）

| 你之前消息的分支                        | 我的诊断                                                     |
| --------------------------------------- | ------------------------------------------------------------ |
| `nerr=android_pcm_bridge_unavailable:*` | 不是这次的真因                                               |
| `nerr=pcm_callback_failed:*`            | 已经修了                                                     |
| `nerr=record_audio_permission_denied`   | 启动时给过权限，但 vivo 后台会再撤回（前台服务才能扛住）     |
| `nerr=空且 frames=0`                    | **这是真因！** 因为 vivo OEM + 缺 FOREGROUND_SERVICE_MICROPHONE，AudioRecord 静默失活，read<0 但 Java 线程 busy loop 不退出，C# 看不到 nerr 也看不到 frame |

### 3. 视频"不知道有没有连上"的直接答案

**100% 是 P0-5 / P0-6**：`useWebcamFallback=true` 默认开 + HUD 没显示 source 字段。修这两个就能立刻看到真相。

### 4. 蓝牙不是核心瓶颈

审计文档第二轮已经把蓝牙路由 / SCO 16k retry / BLE_HEADSET 识别都修了。**bluetooth-off 也 frames=0** 是关键证据，说明真因不在蓝牙路径，而在更基础的「Android 系统是否允许这个 App 在当前生命周期下从 mic 读字节」这一层。

---

## 七、最终一句话总结

> **frames=0 不是因为 LiveKit 协议问题，也不是因为蓝牙路由问题，而是因为 vivo OriginOS Android 14 在 App 没声明 FOREGROUND_SERVICE_MICROPHONE / 没拉起 microphone 类型前台服务时，会静默 throttle AudioRecord 读取——同时 PCM 捕获线程在 read<0 时不退出，导致客户端代码里看不到任何错误指标，只看到 frames 一直是 0。**
>
> **修这一条（P0-1, P0-2, P0-3）大概率就能让 frames > 0；如果修了还 = 0，再走阶段 B 的 P2-N4 看 ECS Brain 是否收到。**

要不要我现在就开始动手改 P0-1 ～ P0-9？还是你先看完报告决定要不要先去 ECS 上跑 P2-N1～N4 排除服务端嫌疑？

---

## 八、2026-05-17 Codex App 线实施状态

本文件已从 `C:/Users/Bin/Desktop/audit.md` 搬迁进 App 业务接口目录，作为
`frames=0` 顶级 TODO / 调试路线参考。实现只落在正式 App 路径：
`unity/ArSpike/Assets/ParrotApp/**` 与
`unity/ArSpike/Assets/Plugins/Android/ParrotAudioRoute.androidlib/**`，没有改
Smoke/ParrotDev 连通性脚本。

已处理的 P0 / 高优先级项：

- P0-1 / P0-2：`ParrotAudioRoute.androidlib` Manifest 增加
  `FOREGROUND_SERVICE`、`FOREGROUND_SERVICE_MICROPHONE`，新增
  `ParrotMicForegroundService`；`MicrophonePublisher` 发布本地麦克风轨前启动
  microphone foreground service，停止发布/Dispose 时关闭。
- P0-3：`AndroidPcmMicCapture` 对连续 `AudioRecord.read(...) < 0` 或持续
  `read == 0` 不再 busy loop；连续错误会报 `read_error_persistent:*`，持续无
  进展会报 `read_zero_persistent`，两者都会退出捕获线程让 Unity retry ladder
  接管。
- P0-4：`AndroidAudioRouteManager.initialize(...)` 在 Activity/回调变化时先注销旧
  callback、清 communication device、放弃 audio focus，避免 singleton 复用时静默失聪。
- P0-5 / P0-6 / P0-7：正式 `ARVideoPublisher.useWebcamFallback=false`；
  HUD 显示 `Video src/frames/age/error`；视频轨发布后必须等 post-publish
  fresh frame，不能只因 `PublishTrack` 成功就报 `video_published=true`。
- P0-8：`ARVideoPublisher` 增加 publish generation cancel guard，断开/停止/重建时
  清理 `_setupInProgress` / `_isRebuilding`，减少 rebuild 与 stop 的协程竞争。
- P0-9：确认 `AudioRoutePolicyBrainReporter` 只解析/观察已有路由服务，不再动态创建
  `AudioRouteManager`；正式 startup 仍可挂 reporter，但不能让 reporter 成为路由 owner。
- Android 官方 `setCommunicationDevice` 建议已吸收：native bridge 对
  `setCommunicationDevice(...)` 增加短重试和 clear 后 retry，失败继续上报
  `communication_device_rejected`，由 Unity 本地 mic retry ladder 接管。
- `ParrotLifecycleConfig` 默认与正式 asset 同步：shutdown cool-down 35s、first-frame
  timeout 8s；避免 30s ICE 残留和 iQOO AR 冷启动过早判死。

验证：

- `javac` 独立编译 `ParrotAudioRoute.androidlib/src/main/java/**/*.java` 通过。
- `uv run pytest tests/test_unity/test_app_v1_meta_ui_static.py -q`：28 passed。
- Unity MCP `refresh_unity` 后 Console error：0。

仍需手机证明：

- iQOO Neo9 rebuild 后 HUD 必须看到 `frames/ch/readSr` 非零，并且 `peak` 在说话时非平线。
- 若本地 frames 已健康但 Brain 仍无响应，再查 Castle Brain 日志的 current Unity identity
  RoomIO binding、remote audio track subscription、STT/Gemini transcript。
- Bluetooth pre-connected、connect-after-start、disconnect fallback、phone mic fallback、
  LineA/LineB、pause/resume、network flap 仍属于 APP-024 真实手机专项。
