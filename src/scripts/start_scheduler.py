"""Start the Scheduler service.

Usage:
    python src/scripts/start_scheduler.py

Alternatively:
    python -m parrot.scheduler.service
"""

from __future__ import annotations

import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from parrot.scheduler.service import run_scheduler

if __name__ == "__main__":
    asyncio.run(run_scheduler())
