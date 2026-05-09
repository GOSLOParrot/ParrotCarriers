"""Sync Obsidian vault notes into the GOSLO runtime.

Reads Markdown files from an Obsidian vault, extracts simple frontmatter, and
publishes each note as an ``obsidian_note`` event to the DSG TriggerRunner.
The runtime path is:

    script -> CH_DSG_EVENTS -> ObsidianIngestTrigger -> UserTagFilter
        -> L1.5 Pool -> L2-B / RefTable

The legacy Graphiti writer is still available via ``--target graphiti`` for
backfill/debug, but the true-connection path is ``--target dsg``.

Usage:
  python src/scripts/sync_obsidian_to_graphiti.py ~/obsidian-vault/goslo
  python src/scripts/sync_obsidian_to_graphiti.py --target graphiti ~/obsidian-vault/goslo
  python src/scripts/sync_obsidian_to_graphiti.py --dry-run ~/obsidian-vault/goslo

Expected frontmatter:
  ---
  profile: "daily"      # ref | daily | roleplay
  title: "Blue mug"
  category: "mug"
  material: "ceramic"
  usual_location: "left side of the desk"
  ---
  Blue mug, bought in 2024, often used for coffee.

  # profile=ref notes strengthen existing L2-B / Graphiti nodes and should
  # carry uuid or obsidian_uuid plus optional target_node_uuid / graphiti_uuid.
  # profile=daily and profile=roleplay are setting notes; they do not require
  # UUID and can use the vault path/title as their local note identity.
"""

from __future__ import annotations

import argparse
import asyncio
import datetime
import json
import logging
import sys
from pathlib import Path

SRC_ROOT = Path(__file__).resolve().parents[1]
if str(SRC_ROOT) not in sys.path:
    # Keep this script runnable directly while sharing the Brain vault parser.
    sys.path.insert(0, str(SRC_ROOT))

from parrot.brain.obsidian_vault import (  # noqa: E402
    collect_markdown_files,
    note_to_ingest_payload,
)

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(name)s %(message)s")
logger = logging.getLogger("obsidian_sync")


def parse_md_file(path: Path) -> dict | None:
    """Parse a Markdown file through the shared App/Brain vault adapter."""
    payload = note_to_ingest_payload(path)
    if payload is None:
        logger.warning("Not ingest-ready: %s", path.name)
    return payload


def collect_md_files(directory: Path) -> list[Path]:
    """Recursively collect Markdown files from a directory or single file."""
    return collect_markdown_files(directory)


def _list_value(raw: str | list | None) -> list[str]:
    """Parse a simple comma/list frontmatter value."""
    if isinstance(raw, list):
        return [str(item).strip() for item in raw if str(item).strip()]
    if not raw:
        return []
    return [part.strip() for part in str(raw).split(",") if part.strip()]


def build_dsg_payload(obj: dict) -> dict:
    """Build the event payload consumed by ObsidianIngestTrigger."""
    return {
        "type": "obsidian_note",
        "label": str(obj.get("label", "") or ""),
        "obsidian_uuid": str(obj.get("obsidian_uuid") or obj.get("uuid", "") or ""),
        "obsidian_note_key": str(obj.get("obsidian_note_key", "") or ""),
        "profile": str(obj.get("profile", "daily") or "daily"),
        "kind": str(obj.get("kind", "object") or "object"),
        "description": str(obj.get("description", "") or "")[:400],
        "tags": _list_value(obj.get("tags"))[:10],
        "obsidian_path": obj.get("obsidian_path", ""),
        "file_mtime": obj.get("file_mtime", 0.0),
        "double_link_count": obj.get("double_link_count", 0),
        "target_node_uuid": str(obj.get("target_node_uuid", "") or ""),
        "graphiti_uuid": str(obj.get("graphiti_uuid", "") or ""),
    }


async def sync_to_dsg_events(objects: list[dict], dry_run: bool = False) -> int:
    """Publish parsed Obsidian notes to the runtime DSG event channel."""
    from parrot.shared.constants import CH_DSG_EVENTS
    from parrot.shared.redis_client import get_redis

    count = 0
    r = None if dry_run else await get_redis()
    for obj in objects:
        payload = build_dsg_payload(obj)
        event = {
            "type": "obsidian_note",
            "payload": payload,
            "source": "obsidian_sync",
            "provenance_stream_id": f"obsidian:{payload['obsidian_note_key']}",
        }
        if dry_run:
            logger.info("[DRY RUN] Would publish DSG event: %s", payload)
        else:
            await r.publish(CH_DSG_EVENTS, json.dumps(event, ensure_ascii=False))
            logger.info(
                "Published DSG Obsidian note: %s (uuid=%s profile=%s)",
                payload["label"],
                payload["obsidian_uuid"] or payload["obsidian_note_key"],
                payload["profile"],
            )
        count += 1
    return count


async def sync_to_graphiti(objects: list[dict], dry_run: bool = False) -> int:
    """Legacy backfill: write parsed object data to Graphiti scene partition."""
    if dry_run:
        for obj in objects:
            logger.info(
                "[DRY RUN] Would sync to Graphiti: %s (uuid=%s)",
                obj.get("_filename", "?"),
                obj.get("obsidian_uuid") or obj.get("obsidian_note_key", ""),
            )
        return len(objects)

    from graphiti_core.nodes import EpisodeType

    from parrot.memory.graphiti_client import PARTITIONS, get_graphiti

    g = await get_graphiti()
    count = 0

    for obj in objects:
        uuid = obj.get("obsidian_uuid") or obj.get("obsidian_note_key", "")
        name = obj.get("label", "unknown")
        body = obj.get("description", "")

        text_parts = [f"Object: {name} (uuid={uuid})"]
        for key in ("category", "material", "usual_location", "color", "owner"):
            if key in obj:
                text_parts.append(f"  {key}: {obj[key]}")
        if body:
            text_parts.append(f"  description: {body}")

        try:
            await g.add_episode(
                name=f"obsidian_{uuid}",
                episode_body="\n".join(text_parts),
                source=EpisodeType.text,
                source_description=f"obsidian:{uuid}",
                reference_time=datetime.datetime.now(datetime.timezone.utc),
                group_id=PARTITIONS.SCENE,
            )
            logger.info("Synced to Graphiti: %s (uuid=%s)", name, uuid)
            count += 1
        except Exception:
            logger.exception("Failed to sync %s", name)

    return count


async def main() -> None:
    parser = argparse.ArgumentParser(description="Sync Obsidian notes to GOSLO")
    parser.add_argument("vault_dir", type=Path, help="Path to Obsidian vault directory or file")
    parser.add_argument(
        "--target",
        choices=("dsg", "graphiti"),
        default="dsg",
        help="dsg publishes runtime ingest events; graphiti is the legacy backfill path",
    )
    parser.add_argument("--dry-run", action="store_true", help="Print what would be synced")
    args = parser.parse_args()

    from dotenv import load_dotenv

    load_dotenv()

    if not args.vault_dir.exists():
        logger.error("Path does not exist: %s", args.vault_dir)
        return

    md_files = collect_md_files(args.vault_dir)
    logger.info("Found %d .md files in %s", len(md_files), args.vault_dir)

    objects = [parsed for f in md_files if (parsed := parse_md_file(f))]
    logger.info("Parsed %d ingest-ready notes", len(objects))

    if not objects:
        logger.info("Nothing to sync.")
        return

    if args.target == "graphiti":
        count = await sync_to_graphiti(objects, dry_run=args.dry_run)
        logger.info("Synced %d/%d notes to Graphiti", count, len(objects))
    else:
        count = await sync_to_dsg_events(objects, dry_run=args.dry_run)
        action = "Prepared" if args.dry_run else "Published"
        target = "DSG runtime dry-run" if args.dry_run else "DSG runtime"
        logger.info("%s %d/%d notes for %s", action, count, len(objects), target)


if __name__ == "__main__":
    asyncio.run(main())
