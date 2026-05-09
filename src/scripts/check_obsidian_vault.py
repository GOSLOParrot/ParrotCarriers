"""Check a local Obsidian vault for GOSLO ingest readiness.

This script is intentionally file-system based. The Obsidian MCP / Local REST
API path is useful later for interactive read/write operations, but the first
GOSLO ingest path should stay local, simple, and independent from ECS.
"""

from __future__ import annotations

import argparse
import json
import sys
from dataclasses import asdict
from pathlib import Path

SRC_ROOT = Path(__file__).resolve().parents[1]
if str(SRC_ROOT) not in sys.path:
    # Keep this script runnable directly via
    # `uv run python src/scripts/check_obsidian_vault.py ...`.
    sys.path.insert(0, str(SRC_ROOT))

from parrot.brain.obsidian_vault import (  # noqa: E402
    VaultCheckResult,
    check_obsidian_vault,
)


TEMPLATE_NOTE = """---
profile: "daily"
kind: "object"
title: "Blue mug"
category: "mug"
material: "ceramic"
usual_location: "left side of the desk"
tags: "goslo,reference"
---

Blue mug, bought in 2024, often used for coffee.

# For profile: "ref", add uuid or obsidian_uuid and, when possible,
# target_node_uuid or graphiti_uuid so it can strengthen an existing node.
"""


def _render_human(result: VaultCheckResult) -> str:
    """Render a short report for terminal use."""
    lines = [
        f"status: {result.status}",
        f"vault_path: {result.vault_path}",
        f"markdown_count: {result.markdown_count}",
        f"ingest_ready_count: {result.ingest_ready_count}",
        f"invalid_count: {result.invalid_count}",
        f"profile_counts: {result.profile_counts}",
    ]
    if result.sample_ready_notes:
        lines.append("sample_ready_notes:")
        for note in result.sample_ready_notes:
            lines.append(
                "  - "
                f"{note['path']} "
                f"(profile={note['profile']}, uuid={note['obsidian_uuid'] or '-'})"
            )
    if result.sample_invalid_notes:
        lines.append("sample_invalid_notes:")
        for path in result.sample_invalid_notes:
            lines.append(f"  - {path}")
    lines.append(f"recommendation: {result.recommendation}")
    return "\n".join(lines)


def check_vault(vault_path: Path, sample_limit: int = 5) -> VaultCheckResult:
    """Backward-compatible CLI helper around the shared Brain implementation."""
    return check_obsidian_vault(vault_path, sample_limit=sample_limit)


def main() -> int:
    parser = argparse.ArgumentParser(description="Check Obsidian vault ingest readiness.")
    parser.add_argument("vault_dir", type=Path, help="Path to the local Obsidian vault.")
    parser.add_argument("--json", action="store_true", help="Print machine-readable JSON.")
    parser.add_argument(
        "--emit-template",
        action="store_true",
        help="Print a starter Markdown note with GOSLO frontmatter.",
    )
    parser.add_argument(
        "--sample-limit",
        type=int,
        default=5,
        help="Maximum ready/invalid note samples to include.",
    )
    args = parser.parse_args()

    if args.emit_template:
        print(TEMPLATE_NOTE)
        return 0

    result = check_obsidian_vault(args.vault_dir, sample_limit=max(args.sample_limit, 0))
    if args.json:
        print(json.dumps(asdict(result), ensure_ascii=False, indent=2))
    else:
        print(_render_human(result))

    return 1 if result.status == "missing_path" else 0


if __name__ == "__main__":
    raise SystemExit(main())
