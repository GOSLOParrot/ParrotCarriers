"""Seed local laptop profile smoke facts into Graphiti.

This script writes to the isolated ``laptop_profile_test`` group_id so GOSLO
and the Web Console can test true Graphiti retrieval without polluting the main
GOSLO/user partitions.
"""

from __future__ import annotations

import argparse
import asyncio
import datetime as dt
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from parrot.memory.encoding_guard import detect_text_mojibake  # noqa: E402
from parrot.memory.graphiti_client import PARTITIONS, close_graphiti, get_graphiti  # noqa: E402


FACTS: tuple[tuple[str, str], ...] = (
    (
        "laptop_profile_device",
        "用户的笔记本电脑是联想拯救者。这条事实用于 GOSLO 本机 Graphiti 真连接测试。",
    ),
    (
        "laptop_profile_mouse",
        "用户的鼠标是 Logitech G504，也可以简称 G504 mouse 或罗技 G504 鼠标。这条事实用于 GOSLO 本机 Graphiti 真连接测试。",
    ),
    (
        "laptop_profile_drink",
        "用户喜欢的饮料是杨枝甘露，也可以说 mango pomelo sago。这条事实用于 GOSLO 本机 Graphiti 偏好检索测试。",
    ),
    (
        "laptop_profile_structured_inventory",
        (
            "用户的个人设备和偏好清单：笔记本电脑是联想拯救者，也可以称为 Lenovo Legion laptop；"
            "鼠标是 Logitech G504，也可以称为 G504 mouse 或罗技 G504 鼠标；"
            "喜欢的饮料是杨枝甘露，也可以称为 mango pomelo sago。"
        ),
    ),
    (
        "laptop_profile_plain_qa",
        (
            "如果 GOSLO 被问到用户的鼠标和喜欢的饮料是什么，测试知识库里的答案应该是："
            "鼠标是 Logitech G504，喜欢的饮料是杨枝甘露。"
        ),
    ),
    (
        "laptop_profile_plain_notes",
        (
            "GOSLO 本机测试知识库记录：用户正在这台笔记本上测试 Web Console、Graphiti 和 nanobot。"
            "联想拯救者是用户的笔记本电脑，Logitech G504 是用户的鼠标，杨枝甘露是用户喜欢的饮料。"
        ),
    ),
)


async def _run(*, apply: bool) -> int:
    partition = PARTITIONS.LAPTOP_PROFILE_TEST
    encoding_issues = []
    for name, body in FACTS:
        report = detect_text_mojibake(body)
        if report.get("suspicious"):
            encoding_issues.append({"name": name, **report})
    if encoding_issues:
        print("[BLOCKED] suspected mojibake in laptop profile FACTS")
        for issue in encoding_issues:
            print(f"- {issue['name']}: {', '.join(issue.get('signals', []))}")
        return 2
    if not apply:
        print(f"[DRY-RUN] partition={partition} episodes={len(FACTS)}")
        for name, body in FACTS:
            print(f"- {name}: {body}")
        return 0

    from graphiti_core.nodes import EpisodeType

    graphiti = await get_graphiti()
    reference_time = dt.datetime.now(dt.timezone.utc)
    for name, body in FACTS:
        await graphiti.add_episode(
            name=name,
            episode_body=body,
            source=EpisodeType.text,
            source_description="parrot-laptop-profile-smoke",
            reference_time=reference_time,
            group_id=partition,
        )
        print(f"[WROTE] {partition}/{name}")
    await close_graphiti()
    return 0


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--apply",
        action="store_true",
        help="Actually write the smoke facts to Graphiti.",
    )
    args = parser.parse_args()
    return asyncio.run(_run(apply=bool(args.apply)))


if __name__ == "__main__":
    raise SystemExit(main())
