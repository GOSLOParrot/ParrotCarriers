"""D0: DSG Processor mounting interface.

Phase 1 stub: defines the abstract interface that DSG Workers (Phase 2)
will implement to connect their video processing pipeline to the Bus.

Design inspired by SVA (Vision-Agents) base_processor pattern:
- A Processor subscribes to a VideoTrack from the LiveKit Room
- Processes frames (SAM2, YOLO, DINOv2, etc.)
- Publishes results via DataChannel (scene events) and Redis (L2 state)

This interface ensures the Bus can accommodate DSG without refactoring.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any


class BaseProcessor(ABC):
    """Abstract base for video/perception processors.

    Subclasses (e.g. DSGProcessor) will be implemented in Phase 2.
    The Bus mounts them via the standard ModuleMount protocol (Path A).
    """

    @abstractmethod
    async def on_video_frame(self, frame: Any) -> None:
        """Called for each video frame from the subscribed track."""
        ...

    @abstractmethod
    async def on_telemetry(self, data: dict) -> None:
        """Called when telemetry data arrives via DataChannel."""
        ...

    @abstractmethod
    async def get_scene_snapshot(self) -> dict:
        """Return the current scene state for Blackboard writing."""
        ...

    async def start(self) -> None:
        """Lifecycle hook: called after mounting."""

    async def stop(self) -> None:
        """Lifecycle hook: called before unmounting."""
