from __future__ import annotations

import py_trees

from parrot.brain.persona_loader import set_persona_loader_for_test
from parrot.brain.soul import get_instructions


def test_default_goslo_persona_demo_ar_reminder_contract(monkeypatch):
    py_trees.blackboard.Blackboard.storage = {}
    py_trees.blackboard.Blackboard.metadata = {}
    set_persona_loader_for_test(None)
    monkeypatch.delenv("PARROT_ACTIVE_PERSONA", raising=False)

    instructions = get_instructions()

    assert "AR 提醒鹦鹉" in instructions
    assert "普通 AR 提醒鹦鹉" in instructions
    assert "清楚、可靠" in instructions
    assert "不使用宅邸大小姐角色口吻" in instructions
    assert "Nanobot 是后台工作者" in instructions
    assert "不要模仿它的口吻" in instructions
    assert "日程与提醒" in instructions
    assert "不用鸟叫拟声词代替说话" in instructions
    assert "LiveKit 刚连接时不要打招呼" in instructions
    assert "演示来源通道" in instructions
    assert "RPC 指令已发送给 Unity" in instructions
    assert "tool 调用" in instructions
    assert "Nanobot 返回的结果摘要" in instructions
    assert "不全文朗读原始邮件、原始文件、JSON 或 task_id" in instructions
    assert "Reflex 层" in instructions
    assert "Intent 层" in instructions
    assert "Work 层" in instructions
    assert "演示固定事实" in instructions
    assert "曾宪滨" in instructions
    assert "福建农林大学 2022 级大四软件工程学生" in instructions
    assert "联想拯救者" in instructions
    assert "Logitech G504" in instructions
    assert "不要追问“这是不是你的电脑/鼠标”" in instructions
    assert "calendar_context" in instructions
    assert "calendar_change_request" in instructions
    assert "message_check_request" in instructions
    assert "reminder_request" in instructions
    assert "这是 Nanobot 返回的 Google 邮件结果摘要" in instructions
    assert "laptop_profile_test" in instructions
    assert "它不是执行工具" in instructions
    assert "T1_DIRECT_GOOGLE_CALENDAR_API" in instructions
    assert "T3_NANOBOT_SCHEDULER_TASK" in instructions
    assert "不是 Calendar 任务 SSOT" in instructions
    assert "鹦鹉大小姐" not in instructions
    assert "嘎" not in instructions
    assert "Minecraft-style" not in instructions
