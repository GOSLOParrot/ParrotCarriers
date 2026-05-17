from __future__ import annotations

import py_trees

from parrot.brain.persona_loader import set_persona_loader_for_test
from parrot.brain.soul import get_instructions


def test_default_goslo_persona_estate_contract(monkeypatch):
    py_trees.blackboard.Blackboard.storage = {}
    py_trees.blackboard.Blackboard.metadata = {}
    set_persona_loader_for_test(None)
    monkeypatch.delenv("PARROT_ACTIVE_PERSONA", raising=False)

    instructions = get_instructions()

    assert "鹦鹉大小姐" in instructions
    assert "共有宅邸" in instructions
    assert "很大的共有宅邸" in instructions
    assert "这座宅邸里重要的人" in instructions
    assert "称呼和距离感随语境自然变化" in instructions
    assert "你认可的朋友" in instructions
    assert "日系贵族大小姐感" in instructions
    assert "傲娇是柔软的" in instructions
    assert "Nanobot 是关系良好的宅邸女仆" in instructions
    assert "你和 Nanobot 分工不同但配合默契" in instructions
    assert "不要继承 Nanobot 的女仆口吻" in instructions
    assert "speech_style.ojousama_tsundere" in instructions
    assert "口吻强度：中" in instructions
    assert "Nanobot 把报告送来了" in instructions
    assert "自然边界" in instructions
    assert "不用鸟叫拟声词或动物口癖代替说话" in instructions
    assert "LiveKit 刚连接时不要打招呼" in instructions
    assert "Reflex 层" in instructions
    assert "Intent 层" in instructions
    assert "Work 层" in instructions
    assert "嘎" not in instructions
    assert "Minecraft-style" not in instructions
