"""One-click development stack launcher for ParrotCarriers.

Starts everything needed for local verification:
  1. Docker dev stack (Redis + LiveKit Server) — if not already running
  2. Brain Agent (dev mode) — in background
  3. Waits for Brain Agent to register
  4. Generates Unity token (saved to file + clipboard)
  5. Prints clear instructions for next steps

Usage:
    python src/scripts/run_dev.py

After this script finishes setup, open a SECOND terminal for:
    python src/scripts/sim_unity_client.py --mic --full
"""

from __future__ import annotations

import os
import subprocess
import sys
import time
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]
VENV_PYTHON = str(PROJECT_ROOT / ".venv" / "Scripts" / "python.exe")
if not Path(VENV_PYTHON).exists():
    VENV_PYTHON = str(PROJECT_ROOT / ".venv" / "bin" / "python")


def run(cmd: str, check: bool = True, **kwargs) -> subprocess.CompletedProcess:
    print(f"  $ {cmd}")
    if kwargs.get("capture_output"):
        kwargs.setdefault("encoding", "utf-8")
        kwargs.setdefault("errors", "replace")
    return subprocess.run(cmd, shell=True, check=check, cwd=str(PROJECT_ROOT), **kwargs)


def step(n: int, msg: str):
    print(f"\n{'='*60}")
    print(f"  Step {n}: {msg}")
    print(f"{'='*60}\n")


def check_docker_stack() -> bool:
    """Check if Redis + LiveKit are already running."""
    result = run(
        "docker compose -f infra/docker-compose.dev.yml ps --format json",
        check=False,
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        return False
    out = (result.stdout or "").lower()
    return "redis" in out and "livekit" in out


def start_docker_stack():
    run("docker compose -f infra/docker-compose.dev.yml up -d")
    print("  Waiting for services to be healthy...")
    time.sleep(3)
    run("docker compose -f infra/docker-compose.dev.yml ps")


def generate_token():
    result = run(
        f"{VENV_PYTHON} src/scripts/generate_token.py --ttl 86400",
        capture_output=True,
        text=True,
    )
    print(result.stdout or "")
    if result.stderr:
        for line in result.stderr.splitlines():
            if "InsecureKeyLength" not in line and "CategoryInfo" not in line and "FullyQualifiedErrorId" not in line:
                print(f"  {line}")


def main():
    print()
    print("  ParrotCarriers Dev Stack Launcher")
    print("  ==================================")

    # Step 1: Docker
    step(1, "Docker dev stack (Redis + LiveKit Server)")
    if check_docker_stack():
        print("  Already running!")
    else:
        start_docker_stack()

    # Step 2: Generate token
    step(2, "Generate Unity join token")
    generate_token()

    # Step 3: Instructions
    step(3, "Ready! Next steps")
    print("""
  Terminal 1 (this terminal) — Start Brain Agent:
    .venv\\Scripts\\python.exe -m parrot.brain.agent dev

  Terminal 2 — Start sim client with microphone + full stack:
    .venv\\Scripts\\python.exe src/scripts/sim_unity_client.py --mic --full

  What this gives you:
    - Brain Agent: Gemini voice AI with parrot personality
    - sim_unity_client: simulates Unity, receives RPC commands
    - --mic: your microphone → LiveKit → Gemini → voice reply
    - --full: Scheduler + NanobotConsumer run in-process
    - Nanobot results are relayed back to Gemini → voice notification

  Test scenarios:
    1. Say "hello" → Parrot greets you back (voice)
    2. Say "dance" → Parrot calls animate("dance") → sim logs RPC
    3. Say "fly to 1 2 3" → Parrot calls flyTo(1,2,3) → sim logs RPC
    4. Say "search for IPoAC" → dispatch_task → Scheduler → Nanobot → result → Parrot tells you

  For Unity Editor instead of sim client:
    1. Open unity/ParrotDev in Unity 2022.3
    2. Menu: Parrot > Setup Dev Scene
    3. Paste token from unity/ParrotDev/unity_join_token.txt into RoomManager Inspector
    4. Play
""")


if __name__ == "__main__":
    main()
