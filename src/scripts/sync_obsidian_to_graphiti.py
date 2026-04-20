"""Sync Obsidian vault object files to Graphiti scene partition.

Reads .md files from an Obsidian vault directory, extracts YAML frontmatter
(must include `uuid`), and writes each object as an episode to Graphiti's
`scene` partition. The UUID in frontmatter is the binding key.

Usage:
  python src/scripts/sync_obsidian_to_graphiti.py ~/obsidian-vault/goslo/objects
  python src/scripts/sync_obsidian_to_graphiti.py --vault-dir ~/obsidian-vault/goslo
  python src/scripts/sync_obsidian_to_graphiti.py --dry-run ~/obsidian-vault/goslo/objects

Expected .md format:
  ---
  uuid: "550e8400-..."
  category: "容器"
  material: "陶瓷"
  usual_location: "工作桌左侧"
  ---
  蓝色马克杯，是2024年买的，常用来喝咖啡。
"""

from __future__ import annotations

import argparse
import asyncio
import datetime
import logging
import re
from pathlib import Path

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(name)s %(message)s")
logger = logging.getLogger("obsidian_sync")

_FRONTMATTER_RE = re.compile(r"^---\s*\n(.*?)\n---\s*\n?(.*)", re.DOTALL)


def parse_md_file(path: Path) -> dict | None:
    """Parse a .md file with YAML-like frontmatter. Returns None if no uuid."""
    text = path.read_text(encoding="utf-8")
    m = _FRONTMATTER_RE.match(text)
    if not m:
        logger.warning("No frontmatter in %s, skipping", path.name)
        return None

    fm_text, body = m.group(1), m.group(2).strip()

    meta: dict = {}
    for line in fm_text.split("\n"):
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        if ":" in line:
            key, _, val = line.partition(":")
            val = val.strip().strip('"').strip("'")
            meta[key.strip()] = val

    if "uuid" not in meta:
        logger.warning("No uuid in %s, skipping", path.name)
        return None

    meta["_body"] = body
    meta["_filename"] = path.stem
    return meta


async def sync_to_graphiti(objects: list[dict], dry_run: bool = False) -> int:
    """Write parsed object data to Graphiti scene partition."""
    if dry_run:
        for obj in objects:
            logger.info(
                "[DRY RUN] Would sync: %s (uuid=%s)",
                obj.get("_filename", "?"), obj["uuid"],
            )
        return len(objects)

    from graphiti_core.nodes import EpisodeType

    from parrot.memory.graphiti_client import PARTITIONS, get_graphiti

    g = await get_graphiti()
    count = 0

    for obj in objects:
        uuid = obj["uuid"]
        name = obj.get("_filename", "unknown")
        body = obj.get("_body", "")

        text_parts = [f"Object: {name} (uuid={uuid})"]
        for key in ["category", "material", "usual_location", "color", "owner"]:
            if key in obj:
                text_parts.append(f"  {key}: {obj[key]}")
        if body:
            text_parts.append(f"  description: {body}")

        text = "\n".join(text_parts)

        try:
            await g.add_episode(
                name=f"obsidian_{uuid}",
                episode_body=text,
                source=EpisodeType.text,
                source_description=f"obsidian:{uuid}",
                reference_time=datetime.datetime.now(datetime.timezone.utc),
                group_id=PARTITIONS.SCENE,
            )
            logger.info("Synced: %s (uuid=%s)", name, uuid)
            count += 1
        except Exception:
            logger.exception("Failed to sync %s", name)

    return count


def collect_md_files(directory: Path) -> list[Path]:
    """Recursively collect all .md files from directory."""
    if directory.is_file() and directory.suffix == ".md":
        return [directory]
    return sorted(directory.rglob("*.md"))


async def main():
    parser = argparse.ArgumentParser(description="Sync Obsidian object files to Graphiti")
    parser.add_argument("vault_dir", type=Path, help="Path to Obsidian vault directory or file")
    parser.add_argument("--dry-run", action="store_true", help="Print what would be synced")
    args = parser.parse_args()

    from dotenv import load_dotenv
    load_dotenv()

    if not args.vault_dir.exists():
        logger.error("Path does not exist: %s", args.vault_dir)
        return

    md_files = collect_md_files(args.vault_dir)
    logger.info("Found %d .md files in %s", len(md_files), args.vault_dir)

    objects = []
    for f in md_files:
        parsed = parse_md_file(f)
        if parsed:
            objects.append(parsed)

    logger.info("Parsed %d objects with valid uuid", len(objects))

    if not objects:
        logger.info("Nothing to sync.")
        return

    count = await sync_to_graphiti(objects, dry_run=args.dry_run)
    logger.info("Synced %d/%d objects to Graphiti", count, len(objects))


if __name__ == "__main__":
    asyncio.run(main())
