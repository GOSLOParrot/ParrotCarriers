"""Start the Nanobot worker with ParrotCarriers Bus channel enabled.

Usage:
  python src/scripts/start_nanobot_worker.py

This script:
  1. Copies the parrot config template to a local nanobot data dir
  2. Starts the nanobot gateway with the parrot_bus channel
  3. The channel reads tasks from Redis Stream and processes them via nanobot's agent

Prerequisites:
  - Redis running (docker compose -f infra/docker-compose.dev.yml up -d)
  - nanobot installed: pip install -e ../nanobot[parrot]
  - LLM provider API key configured in the config
"""

from __future__ import annotations

import json
import os
import shutil
import subprocess
import sys
from pathlib import Path

PARROT_NANOBOT_DIR = Path.home() / ".nanobot-parrot"
TEMPLATE_CONFIG = Path(__file__).resolve().parents[2] / "nanobot" / "config" / "parrot_config.json"
FORK_CONFIG = Path(__file__).resolve().parents[3] / "nanobot" / "config" / "parrot_config.json"


def setup_config() -> Path:
    """Ensure the nanobot parrot config directory exists with a valid config."""
    config_dir = PARROT_NANOBOT_DIR
    config_file = config_dir / "config.json"

    if not config_file.exists():
        config_dir.mkdir(parents=True, exist_ok=True)

        template = FORK_CONFIG if FORK_CONFIG.exists() else TEMPLATE_CONFIG
        if not template.exists():
            print(f"ERROR: Config template not found at {FORK_CONFIG}")
            sys.exit(1)

        config = json.loads(template.read_text())

        api_key = os.getenv("OPENROUTER_API_KEY", "")
        if api_key:
            config["providers"]["openrouter"]["apiKey"] = api_key
        else:
            print("WARNING: OPENROUTER_API_KEY not set. Edit the config manually:")
            print(f"  {config_file}")

        config_file.write_text(json.dumps(config, indent=2))
        print(f"Config created at {config_file}")
    else:
        print(f"Using existing config at {config_file}")

    return config_dir


def main():
    config_dir = setup_config()

    print("\nStarting nanobot gateway with ParrotCarriers Bus channel...")
    print(f"  Config dir: {config_dir}")
    print("  Channel: parrot_bus (Redis Stream consumer)")
    print()

    nanobot_exe = shutil.which("nanobot")
    if nanobot_exe is None:
        print("ERROR: 'nanobot' command not found. Install with: pip install -e ../nanobot[parrot]")
        sys.exit(1)

    subprocess.run(
        [nanobot_exe, "--dir", str(config_dir), "gateway"],
        check=False,
    )


if __name__ == "__main__":
    main()
