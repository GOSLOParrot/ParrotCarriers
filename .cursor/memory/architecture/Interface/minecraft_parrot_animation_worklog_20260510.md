---
status: active
category: worklog
date: 2026-05-10
owner: Codex / Unity ArSpike
---

# Minecraft Parrot Animation Worklog

## 2026-05-10 Strict Reference Correction

- User goal: replace the earlier simplified parrot motion with a strict Minecraft Java parrot animation reference, using the Blockbench/GOSLO parrot model in Unity.
- Fact source used: official Minecraft Java 1.20.1 manifest plus local cache under `D:\GOSLOParrot\minecraft_reference_cache\1.20.1`; class mapping confirmed as `ParrotModel -> fcf`, `ParrotRenderer -> fqk`, `Parrot -> bsb`.
- Formal code landing: `unity/ArSpike/Assets/ParrotApp/Runtime/Scripts/Parrot/AnimationDriver.cs`; `unity/ParrotDev` is not the active app workspace for this correction.
- Implementation: `AnimationDriver` now defaults to `useMinecraftJavaParrotPose=true` and maps project states to vanilla poses `STANDING`, `FLYING`, `SITTING`, `PARTY`, and `ON_SHOULDER`, including the official model constants and ParrotRenderer-style flap progress.
- Reference note added: `docs/minecraft_parrot_animation_port_zh.md`. Mojang `client.jar` / mappings stay in the local reference cache only and must not be committed.


