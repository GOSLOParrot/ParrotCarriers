"""Dry-run-first Arknights fixture importer for Graphiti.

The fixture is intentionally compact and original. It stores short summaries,
state-change facts, story-order metadata, and source pointers for testing the
``arknights_test`` Graphiti partition. It does not copy long story text from
PRTS or any other source.

Examples:
    uv run python src/scripts/import_arknights_to_graphiti.py --dry-run --limit 2
    uv run python src/scripts/import_arknights_to_graphiti.py --apply --limit 3
"""

from __future__ import annotations

import argparse
import asyncio
import datetime as dt
import json
import sys
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Iterable

SRC_ROOT = Path(__file__).resolve().parents[1]
if str(SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(SRC_ROOT))

from parrot.memory.graphiti_client import PARTITIONS

PRTS_STORY_INDEX_URL = (
    "https://prts.wiki/w/%E5%89%A7%E6%83%85%E4%B8%80%E8%A7%88"
)


@dataclass(frozen=True)
class ArknightsEpisodeFixture:
    """One compact test episode for Graphiti temporal extraction."""

    name: str
    episode_body: str
    source_url: str
    source_section: str
    story_order: str
    reference_time: str

    @property
    def source_description(self) -> str:
        return (
            "arknights_test:"
            f"{self.story_order}:{self.source_section}:"
            "original_summary_from_prts_story_index"
        )


def build_fixtures() -> list[ArknightsEpisodeFixture]:
    """Return the first Arknights temporal fixture set.

    ``reference_time`` uses deterministic surrogate dates. The story metadata
    in the body is the important fictional timeline signal; these dates merely
    give Graphiti a stable ordering reference during local tests.
    """
    rows = [
        (
            "arknights_main_00_01_chernobog",
            "main_00_01",
            "Main story opening / Chernobog crisis",
            (
                "Original compact test summary. Rhodes Island enters a crisis "
                "around Chernobog while Oripathy, Reunion, infected civilians, "
                "and Amiya's command role become active story forces. State "
                "change: Rhodes Island moves from medical operator context "
                "toward emergency battlefield intervention."
            ),
        ),
        (
            "arknights_main_02_03_lungmen",
            "main_02_03",
            "Lungmen escalation",
            (
                "Original compact test summary. The conflict expands from "
                "Chernobog into Lungmen. Rhodes Island, Lungmen authorities, "
                "and Reunion collide over public security, infected treatment, "
                "and political control. State change: Reunion becomes a larger "
                "regional threat instead of only a local uprising."
            ),
        ),
        (
            "arknights_main_04_05_reunion_leaders",
            "main_04_05",
            "Reunion leadership pressure",
            (
                "Original compact test summary. Reunion's internal leaders and "
                "Rhodes Island's operators reveal conflicting motives around "
                "infection, revenge, and survival. State change: Reunion is no "
                "longer a single hostile mass; its factions and tragedies become "
                "separate context nodes."
            ),
        ),
        (
            "arknights_main_06_08_amiya_talulah",
            "main_06_08",
            "Amiya and Talulah arc",
            (
                "Original compact test summary. Amiya's responsibilities grow "
                "while Talulah's role connects Reunion's violence to deeper "
                "personal, political, and historical forces. State change: "
                "Amiya advances from field leader toward a bearer of wider "
                "Sarkaz/Kazdel-linked memory pressure."
            ),
        ),
        (
            "arknights_main_09_10_victoria",
            "main_09_10",
            "Victoria crisis",
            (
                "Original compact test summary. The story focus shifts toward "
                "Victoria, exposing large-state conflict, displaced powers, and "
                "Rhodes Island's limits as a neutral medical organization. State "
                "change: national politics becomes central to the conflict map."
            ),
        ),
        (
            "arknights_main_11_12_kazdel_sarkaz",
            "main_11_12",
            "Sarkaz and Kazdel pressure",
            (
                "Original compact test summary. Sarkaz history and Kazdel's "
                "political weight become major context. Rhodes Island and Amiya "
                "must interpret present conflict through inherited trauma and "
                "identity. State change: the graph needs temporal facts for "
                "faction identity, not a single static faction description."
            ),
        ),
        (
            "arknights_main_babel_context",
            "main_babel",
            "Babel / Rhodes Island background",
            (
                "Original compact test summary. Babel and pre-Rhodes Island "
                "context explain how present operators, Theresa/Theresis-linked "
                "history, and the Doctor's identity pressure the current story. "
                "State change: past institutional identity becomes provenance "
                "for present decisions."
            ),
        ),
    ]
    base = dt.datetime(2020, 1, 1, 12, 0, tzinfo=dt.timezone.utc)
    fixtures: list[ArknightsEpisodeFixture] = []
    for index, (name, order, section, body) in enumerate(rows):
        fixtures.append(
            ArknightsEpisodeFixture(
                name=name,
                episode_body=(
                    f"story_order: {order}\n"
                    f"source_section: {section}\n"
                    f"source_url: {PRTS_STORY_INDEX_URL}\n\n"
                    f"{body}"
                ),
                source_url=PRTS_STORY_INDEX_URL,
                source_section=section,
                story_order=order,
                reference_time=(base + dt.timedelta(days=index)).isoformat(),
            )
        )
    return fixtures


def _select_fixtures(limit: int) -> list[ArknightsEpisodeFixture]:
    fixtures = build_fixtures()
    return fixtures if limit <= 0 else fixtures[:limit]


async def _apply(fixtures: Iterable[ArknightsEpisodeFixture], partition: str) -> int:
    from graphiti_core.nodes import EpisodeType

    from parrot.memory.graphiti_client import get_graphiti

    graphiti = await get_graphiti()
    written = 0
    for item in fixtures:
        await graphiti.add_episode(
            name=item.name,
            episode_body=item.episode_body,
            source=EpisodeType.text,
            source_description=item.source_description,
            reference_time=dt.datetime.fromisoformat(item.reference_time),
            group_id=partition,
        )
        written += 1
    return written


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--partition", default=PARTITIONS.ARKNIGHTS_TEST)
    parser.add_argument("--limit", type=int, default=0)
    parser.add_argument("--dry-run", action="store_true", help="Explicit dry-run flag.")
    parser.add_argument("--apply", action="store_true", help="Write episodes to Graphiti.")
    args = parser.parse_args()
    if args.apply and args.dry_run:
        parser.error("--apply and --dry-run are mutually exclusive")

    fixtures = _select_fixtures(args.limit)
    if not args.apply:
        print(json.dumps(
            {
                "dry_run": True,
                "partition": args.partition,
                "source_policy": "original compact summaries plus source pointers",
                "episodes": [asdict(item) for item in fixtures],
            },
            ensure_ascii=False,
            indent=2,
        ))
        return 0

    written = asyncio.run(_apply(fixtures, args.partition))
    print(json.dumps({"dry_run": False, "partition": args.partition, "written": written}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
