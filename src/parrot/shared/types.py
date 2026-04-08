"""Shared type definitions."""

from __future__ import annotations

from enum import Enum


class ModuleType(str, Enum):
    CORE = "CORE"
    PERCEPTION = "PERCEPTION"
    WORKER = "WORKER"
    BRIDGE = "BRIDGE"
    CLIENT = "CLIENT"


class Layer(str, Enum):
    L1 = "L1"
    L2 = "L2"
    L3 = "L3"
