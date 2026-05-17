"""Import the local public-domain etiquette text into Graphiti.

The importer is deterministic and dry-run first. It chunks the local Project
Gutenberg text into named Episodes, preserves source/chapter metadata in the
Episode body, and can write through the existing Web/App monitor Graphiti API.

Examples:
    uv run python src/scripts/import_noble_etiquette_to_graphiti.py --dry-run
    uv run python src/scripts/import_noble_etiquette_to_graphiti.py --apply --limit 2
    uv run python src/scripts/import_noble_etiquette_to_graphiti.py --apply --base-url http://127.0.0.1:8790
"""

from __future__ import annotations

import argparse
import json
import re
import sys
import time
import urllib.error
import urllib.request
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any

SRC_ROOT = Path(__file__).resolve().parents[1]
REPO_ROOT = SRC_ROOT.parent
if str(SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(SRC_ROOT))

from parrot.memory.graphiti_client import PARTITIONS

DEFAULT_TEXT = REPO_ROOT / "Noble Etiquette" / "pg35123.txt"
DEFAULT_BASE_URL = "http://127.0.0.1:8790"
SOURCE_URL = "https://www.gutenberg.org/ebooks/35123"
DEFAULT_EPISODE_PREFIX = "noble_etiquette_pg35123_v2"


@dataclass(frozen=True)
class NobleEtiquetteEpisode:
    name: str
    episode_body: str
    source_description: str
    chapter_id: str
    chapter_title: str
    chunk_index: int
    chunk_count: int
    char_count: int


def _read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8-sig")


def _strip_boilerplate(text: str) -> str:
    end_marker = "*** END OF THE PROJECT GUTENBERG EBOOK"
    end = text.find(end_marker)
    if end >= 0:
        text = text[:end]
    intro = text.find("INTRODUCTION.")
    if intro >= 0:
        text = text[intro:]
    text = re.sub(
        r"\n\s*CONTENTS\.\s*\n.*?\n\s*LADIES' BOOK OF ETIQUETTE\.\s*\n",
        "\n\n",
        text,
        flags=re.S,
    )
    return text.strip()


def _slug(value: str, *, fallback: str) -> str:
    raw = re.sub(r"[^A-Za-z0-9]+", "_", value.strip().lower()).strip("_")
    return raw[:48] or fallback


def _source_file_ref(path: Path) -> str:
    try:
        return path.resolve().relative_to(REPO_ROOT.resolve()).as_posix()
    except ValueError:
        return path.as_posix()


def _roman_to_int(value: str) -> int:
    numerals = {"I": 1, "V": 5, "X": 10, "L": 50, "C": 100, "D": 500, "M": 1000}
    total = 0
    prev = 0
    for char in reversed(value.upper()):
        num = numerals.get(char, 0)
        if num < prev:
            total -= num
        else:
            total += num
            prev = num
    return total


def _chapter_ranges(lines: list[str]) -> list[tuple[str, str, int, int]]:
    starts: list[tuple[str, str, int]] = [("intro", "Introduction", 0)]
    in_contents = False
    for index, line in enumerate(lines):
        stripped = line.strip()
        if stripped == "CONTENTS.":
            in_contents = True
            continue
        if stripped == "LADIES' BOOK OF ETIQUETTE.":
            in_contents = False
            continue
        match = re.match(r"^CHAPTER\s+([IVXLCDM]+)\.\s*$", line.strip())
        if not match:
            continue
        if in_contents:
            continue
        number = _roman_to_int(match.group(1))
        title = ""
        for probe in range(index + 1, min(index + 8, len(lines))):
            candidate = lines[probe].strip()
            if candidate:
                title = candidate.title()
                break
        starts.append((f"chapter_{number:02d}", title or f"Chapter {number}", index))
    ranges: list[tuple[str, str, int, int]] = []
    for offset, (chapter_id, title, start) in enumerate(starts):
        end = starts[offset + 1][2] if offset + 1 < len(starts) else len(lines)
        ranges.append((chapter_id, title, start, end))
    return ranges


def _paragraph_chunks(text: str, *, max_chars: int) -> list[str]:
    paragraphs = [item.strip() for item in re.split(r"\n\s*\n", text) if item.strip()]
    chunks: list[str] = []
    current: list[str] = []
    current_len = 0
    for paragraph in paragraphs:
        paragraph_len = len(paragraph) + 2
        if current and current_len + paragraph_len > max_chars:
            chunks.append("\n\n".join(current).strip())
            current = []
            current_len = 0
        if paragraph_len > max_chars:
            for start in range(0, len(paragraph), max_chars):
                part = paragraph[start : start + max_chars].strip()
                if part:
                    chunks.append(part)
            continue
        current.append(paragraph)
        current_len += paragraph_len
    if current:
        chunks.append("\n\n".join(current).strip())
    return chunks


def build_episodes(
    path: Path,
    *,
    max_chars: int,
    episode_prefix: str = DEFAULT_EPISODE_PREFIX,
    source_file_ref: str | None = None,
) -> list[NobleEtiquetteEpisode]:
    text = _strip_boilerplate(_read_text(path))
    lines = text.splitlines()
    episodes: list[NobleEtiquetteEpisode] = []
    for chapter_id, title, start, end in _chapter_ranges(lines):
        chapter_text = "\n".join(lines[start:end]).strip()
        if not chapter_text:
            continue
        chunks = _paragraph_chunks(chapter_text, max_chars=max_chars)
        title_slug = _slug(title, fallback=chapter_id)
        for index, chunk in enumerate(chunks, start=1):
            name = f"{episode_prefix}_{chapter_id}_{title_slug}_{index:03d}"
            body = (
                "source_kind: project_gutenberg_public_domain\n"
                "import_schema_version: noble_etiquette_pg35123_v2\n"
                "source_title: The Ladies' Book of Etiquette, and Manual of Politeness\n"
                "source_author: Florence Hartley\n"
                f"source_url: {SOURCE_URL}\n"
                f"source_file: {source_file_ref or _source_file_ref(path)}\n"
                f"partition: {PARTITIONS.NOBLE_ETIQUETTE}\n"
                f"chapter_id: {chapter_id}\n"
                f"chapter_title: {title}\n"
                f"chunk_index: {index}\n"
                f"chunk_count: {len(chunks)}\n\n"
                f"{chunk}"
            )
            episodes.append(
                NobleEtiquetteEpisode(
                    name=name,
                    episode_body=body,
                    source_description=(
                        "noble_etiquette:pg35123:v2:"
                        f"{chapter_id}:chunk_{index:03d}:project_gutenberg_public_domain"
                    ),
                    chapter_id=chapter_id,
                    chapter_title=title,
                    chunk_index=index,
                    chunk_count=len(chunks),
                    char_count=len(body),
                )
            )
    return episodes


def _existing_episode_names(
    *,
    graph: str,
    host: str,
    port: int,
) -> tuple[set[str], str]:
    try:
        import redis
    except Exception as exc:
        return set(), f"redis_import_unavailable:{type(exc).__name__}:{exc}"
    try:
        client = redis.Redis(host=host, port=port, decode_responses=True)
        rows = client.execute_command(
            "GRAPH.QUERY",
            graph,
            "MATCH (n:Episodic) RETURN n.name",
            "--compact",
        )
    except Exception as exc:
        return set(), f"falkordb_query_failed:{type(exc).__name__}:{exc}"
    names: set[str] = set()
    try:
        for row in rows[1] or []:
            if row and row[0] and len(row[0]) > 1:
                names.add(str(row[0][1]))
    except Exception as exc:
        return names, f"falkordb_decode_warning:{type(exc).__name__}:{exc}"
    return names, ""


def _post_episode(
    episode: NobleEtiquetteEpisode,
    *,
    base_url: str,
    partition: str,
    timeout_s: float,
) -> dict[str, Any]:
    payload = {
        "name": episode.name,
        "body": episode.episode_body,
        "partition": partition,
        "source_description": episode.source_description,
        "dry_run": False,
    }
    request = urllib.request.Request(
        f"{base_url.rstrip('/')}/api/graphiti/episode",
        data=json.dumps(payload).encode("utf-8"),
        headers={"Content-Type": "application/json; charset=utf-8"},
        method="POST",
    )
    with urllib.request.urlopen(request, timeout=timeout_s) as response:
        return json.loads(response.read().decode("utf-8"))


def _preview(episode: NobleEtiquetteEpisode, *, include_body: bool) -> dict[str, Any]:
    data = asdict(episode)
    if include_body:
        return data
    body = data.pop("episode_body")
    data["body_preview"] = body[:360]
    data["body_sha_hint"] = f"len:{len(body)}"
    return data


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--text", type=Path, default=DEFAULT_TEXT)
    parser.add_argument("--partition", default=PARTITIONS.NOBLE_ETIQUETTE)
    parser.add_argument("--base-url", default=DEFAULT_BASE_URL)
    parser.add_argument("--episode-prefix", default=DEFAULT_EPISODE_PREFIX)
    parser.add_argument(
        "--source-file-ref",
        default="",
        help=(
            "Stable source locator written into Graphiti Episode bodies. "
            "Defaults to a repo-relative path when possible."
        ),
    )
    parser.add_argument("--max-chars", type=int, default=9000)
    parser.add_argument("--limit", type=int, default=0)
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--apply", action="store_true")
    parser.add_argument("--include-body", action="store_true")
    parser.add_argument("--skip-existing", action=argparse.BooleanOptionalAction, default=True)
    parser.add_argument("--falkor-host", default="127.0.0.1")
    parser.add_argument("--falkor-port", type=int, default=6380)
    parser.add_argument("--timeout-s", type=float, default=300.0)
    parser.add_argument("--sleep-s", type=float, default=0.0)
    parser.add_argument("--continue-on-error", action="store_true")
    args = parser.parse_args()
    if args.apply and args.dry_run:
        parser.error("--apply and --dry-run are mutually exclusive")
    if not args.apply:
        args.dry_run = True

    episodes = build_episodes(
        args.text,
        max_chars=max(2000, args.max_chars),
        episode_prefix=args.episode_prefix,
        source_file_ref=args.source_file_ref.strip() or None,
    )
    existing: set[str] = set()
    existing_warning = ""
    if args.skip_existing:
        existing, existing_warning = _existing_episode_names(
            graph=args.partition,
            host=args.falkor_host,
            port=args.falkor_port,
        )
    selected = [item for item in episodes if item.name not in existing]
    if args.limit > 0:
        selected = selected[: args.limit]

    if args.dry_run:
        print(json.dumps(
            {
                "dry_run": True,
                "partition": args.partition,
                "base_url": args.base_url,
                "source_file": str(args.text),
                "source_file_ref": args.source_file_ref.strip() or _source_file_ref(args.text),
                "source_url": SOURCE_URL,
                "episode_prefix": args.episode_prefix,
                "max_chars": max(2000, args.max_chars),
                "episode_count_total": len(episodes),
                "existing_episode_count": len(existing),
                "selected_count": len(selected),
                "existing_warning": existing_warning,
                "episodes": [
                    _preview(item, include_body=args.include_body)
                    for item in selected
                ],
            },
            ensure_ascii=False,
            indent=2,
        ))
        return 0

    written: list[dict[str, Any]] = []
    errors: list[dict[str, Any]] = []
    for index, episode in enumerate(selected, start=1):
        started = time.time()
        try:
            result = _post_episode(
                episode,
                base_url=args.base_url,
                partition=args.partition,
                timeout_s=args.timeout_s,
            )
            elapsed_s = round(time.time() - started, 3)
            row = {
                "index": index,
                "name": episode.name,
                "success": bool(result.get("success")),
                "message": result.get("message"),
                "elapsed_s": elapsed_s,
                "char_count": episode.char_count,
            }
            print(json.dumps(row, ensure_ascii=False), flush=True)
            written.append(row)
            if not result.get("success") and not args.continue_on_error:
                break
        except (urllib.error.URLError, TimeoutError, OSError, json.JSONDecodeError) as exc:
            error = {
                "index": index,
                "name": episode.name,
                "success": False,
                "error": f"{type(exc).__name__}: {exc}",
            }
            print(json.dumps(error, ensure_ascii=False), flush=True)
            errors.append(error)
            if not args.continue_on_error:
                break
        if args.sleep_s > 0:
            time.sleep(args.sleep_s)
    api_failure_count = sum(1 for item in written if not item.get("success"))
    print(json.dumps(
        {
            "dry_run": False,
            "partition": args.partition,
            "base_url": args.base_url,
            "episode_prefix": args.episode_prefix,
            "selected_count": len(selected),
            "written_count": sum(1 for item in written if item.get("success")),
            "error_count": len(errors) + api_failure_count,
            "existing_episode_count": len(existing),
        },
        ensure_ascii=False,
    ))
    return 1 if errors or api_failure_count else 0


if __name__ == "__main__":
    raise SystemExit(main())
