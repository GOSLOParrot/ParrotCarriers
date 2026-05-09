"""Run the App v1 autonomous business self-check and print JSON."""

from __future__ import annotations

import argparse
import asyncio
import json
from pathlib import Path

from parrot.brain.app_v1_self_check import run_app_v1_self_check


async def _amain() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--obsidian-vault", default="")
    args = parser.parse_args()
    result = await run_app_v1_self_check(
        obsidian_vault_path=Path(args.obsidian_vault) if args.obsidian_vault else None
    )
    print(json.dumps(result.as_json(), ensure_ascii=False, indent=2))
    return 0 if result.passed else 1


def main() -> None:
    raise SystemExit(asyncio.run(_amain()))


if __name__ == "__main__":
    main()
