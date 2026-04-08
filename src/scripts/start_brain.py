"""Start the Brain Agent.

Usage:
    python src/scripts/start_brain.py          # dev mode (connects to LiveKit)
    python src/scripts/start_brain.py console   # console mode (no LiveKit)

Alternatively:
    python -m parrot.brain.agent dev
    python -m parrot.brain.agent console
"""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from livekit import agents
from parrot.brain.agent import server

if __name__ == "__main__":
    agents.cli.run_app(server)
