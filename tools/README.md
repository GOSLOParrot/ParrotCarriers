# tools/

仓库级运维 / 自检脚本。

## verify_so_alignment.ps1

Android 15+ 16KB ELF 页对齐自检（出包前 + CI 必跑）。

**为什么要跑**：Google Play 自 2025-11-01 起强制 64-bit App 的所有 native `.so` 走 16KB ELF 对齐，否则在 Android 15+ ARM64 设备上 `dlopen` 失败 → 冷启动闪退。本仓库已通过升级 LiveKit SDK pin → main HEAD（FFI v0.12.53）和 ARCore XR Plugin 5.1.5 → 5.2.2 满足该要求，但**第三方插件 / 未来升级仍可能引入新的 4KB 对齐 .so**，所以必须真验。

### 前置

- Windows PowerShell 5.1 或 PowerShell 7+。
- Android NDK r26+（用于自带的 `llvm-objdump`）。环境变量任选其一：
  - `ANDROID_NDK_HOME`
  - `ANDROID_NDK_ROOT`
  - 或脚本参数 `-NdkRoot <path>`

### 用法

```powershell
# 1) 扫一个目录（递归找所有 .so）
pwsh tools/verify_so_alignment.ps1 unity/ArSpike/Library/PackageCache/io.livekit.livekit-sdk@7d868ef/Runtime/Plugins

# 2) 直接扫一个 APK / AAB（自动解包到 %TEMP%，跑完清理）
pwsh tools/verify_so_alignment.ps1 build/parrot-arspike.apk

# 3) 单个 .so
pwsh tools/verify_so_alignment.ps1 path/to/liblivekit_ffi.so

# 4) 显式指定 NDK
pwsh tools/verify_so_alignment.ps1 build/app.apk -NdkRoot D:/Android/Sdk/ndk/26.1.10909125
```

### 输出

每个 `.so` 标记 `OK_16KB` / `BAD` / `NO_LOAD_SEG`，最后给出 summary。

退出码：

- `0` — 全部 16KB 对齐
- `1` — 有 `.so` 不达标（CI 应该 fail 整个 build）

### 判定口径

调用 `llvm-objdump -p <so> | grep LOAD`，对应每个 LOAD 段必须出现 `align 2**14`（= 16384 字节）。`2**12` (4KB) 与 `2**13` (8KB) 都视为 BAD。

### 联动文档

- `.cursor/skills/client-sdk-unity/SKILL.md` 顶部 NOTICE 区
- `.cursor/skills/livekit-unity-lifecycle/IMPL_REF.md` §6.3
- `.cursor/rules/ar-foundation.mdc` §0–§1
- `.cursor/memory/architecture/sprint4_phase4_entry_20260430.md` §6.x 平台版本锁补丁
