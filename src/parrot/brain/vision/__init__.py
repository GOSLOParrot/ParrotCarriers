"""Brain vision helpers — snapshot capture + VLM match.

Sprint 0 草稿收录 (Schema V1 对齐), Sprint 4 S4.A/S4.B 继续填实现。
- `snapshot.capture_current_frame`: 走 captureSnapshot RPC 拉补充通道的渲染帧。
- `visual_match.compare_current_frame` / `describe_image`: VLM 比对与自描述。

注意: 识物 (identify_object) 走主通道 (Gemini Live 已在看的那路 ar-camera),
不需要调 capture_current_frame; 只有"相机模式/拍照/回忆杀"才走补充通道。
"""
