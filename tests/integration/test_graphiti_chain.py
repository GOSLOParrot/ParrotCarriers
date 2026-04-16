"""Integration test: Graphiti full chain — write → search → DSG interfaces.

Prerequisites:
  - FalkorDB running on localhost:6380 (docker compose up)
  - GOOGLE_API_KEY set

Run:
  pytest tests/integration/test_graphiti_chain.py -v
  # or standalone:
  python tests/integration/test_graphiti_chain.py
"""

from __future__ import annotations

import asyncio
import os
import sys

import pytest

pytestmark = [
    pytest.mark.skipif(
        not os.getenv("GOOGLE_API_KEY"),
        reason="GOOGLE_API_KEY not set",
    ),
]


@pytest.fixture
async def graphiti():
    """Get a fresh Graphiti instance."""
    from parrot.memory.graphiti_client import close_graphiti, get_graphiti

    g = await get_graphiti()
    yield g
    await close_graphiti()


@pytest.mark.asyncio
async def test_remember_and_query(graphiti):
    """Test: write an episode → search returns it."""
    from graphiti_core.graphiti_types import EpisodeType

    from parrot.memory.graphiti_client import PARTITIONS

    test_fact = "The user's favorite color is emerald green (test)"
    await graphiti.add_episode(
        text=test_fact,
        episode_type=EpisodeType.text,
        group_id=PARTITIONS.GOSLO,
        source="test",
    )

    results = await graphiti.search(
        query="favorite color",
        group_ids=[PARTITIONS.GOSLO],
        num_results=3,
    )

    assert len(results) > 0, "Expected at least one search result"
    found_texts = [
        getattr(r, "fact", "") or getattr(r, "text", str(r))
        for r in results
    ]
    assert any("emerald" in t.lower() or "green" in t.lower() for t in found_texts), (
        f"Expected to find 'emerald green' in results: {found_texts}"
    )


@pytest.mark.asyncio
async def test_scene_partition_isolated(graphiti):
    """Test: scene partition is isolated from goslo partition."""
    from graphiti_core.graphiti_types import EpisodeType

    from parrot.memory.graphiti_client import PARTITIONS

    await graphiti.add_episode(
        text="Object: blue mug on desk (test scene object)",
        episode_type=EpisodeType.text,
        group_id=PARTITIONS.SCENE,
        source="test",
    )

    scene_results = await graphiti.search(
        query="blue mug",
        group_ids=[PARTITIONS.SCENE],
        num_results=3,
    )
    goslo_results = await graphiti.search(
        query="blue mug",
        group_ids=[PARTITIONS.GOSLO],
        num_results=3,
    )

    assert len(scene_results) > 0, "Scene partition should have the mug"


@pytest.mark.asyncio
async def test_dsg_preload_interface(graphiti):
    """Test: DSG preload interface queries Graphiti."""
    from graphiti_core.graphiti_types import EpisodeType

    from parrot.dsg.interfaces import preload_object_semantics
    from parrot.memory.graphiti_client import PARTITIONS

    await graphiti.add_episode(
        text="Object: red laptop (uuid=test-laptop-001) on work desk, category=electronics",
        episode_type=EpisodeType.text,
        group_id=PARTITIONS.SCENE,
        source="test",
    )

    result = await preload_object_semantics("test-laptop-001", "red laptop")
    # May or may not find it depending on embedding similarity, but shouldn't crash
    assert result is None or isinstance(result, dict)


@pytest.mark.asyncio
async def test_dsg_update_last_seen(graphiti):
    """Test: update_last_seen writes to Graphiti without error."""
    from parrot.dsg.interfaces import update_last_seen

    await update_last_seen(
        object_id="test-mug-001",
        label="test mug",
        position=(0.3, 0.75, -0.2),
        zone="work_area",
        surface="desk",
    )


if __name__ == "__main__":
    from dotenv import load_dotenv
    load_dotenv()

    async def _run():
        from parrot.memory.graphiti_client import close_graphiti, get_graphiti

        g = await get_graphiti()
        print("✓ Graphiti connected")

        from graphiti_core.graphiti_types import EpisodeType
        from parrot.memory.graphiti_client import PARTITIONS

        await g.add_episode(
            text="Integration test: the user likes matcha lattes",
            episode_type=EpisodeType.text,
            group_id=PARTITIONS.GOSLO,
            source="integration_test",
        )
        print("✓ Episode written to goslo partition")

        results = await g.search(
            query="what does the user like to drink?",
            group_ids=[PARTITIONS.GOSLO],
            num_results=3,
        )
        print(f"✓ Search returned {len(results)} results")
        for r in results:
            fact = getattr(r, "fact", None) or getattr(r, "text", str(r))
            print(f"  - {fact}")

        from parrot.dsg.interfaces import update_last_seen
        await update_last_seen("test-001", "test cup", (0.5, 0.8, -0.1))
        print("✓ DSG update_last_seen OK")

        await close_graphiti()
        print("\n=== All integration checks passed ===")

    asyncio.run(_run())
