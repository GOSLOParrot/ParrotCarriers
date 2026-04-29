"""Sprint4 Phase 4 临时阈值器命名空间 — **不是** DSG L3 完整注意力模块.

Authoritative spec: ``architecture/sprint4_phase4_entry_20260430.md §3.7``
(observer / attention boundary) + §8.1 L13 (hard naming constraint) + §8.4
(code entry routing) + §8.6 (Phase 4 不做 list).

L3 注意力模块的完整设计（多线索仲裁 / 与 triggers / scheduler 深度联动 /
优先级注入 / 跨 Episode 注意力延续）见 entry doc §3.7，**不在 Phase 4 范围**，
留 Phase 5+ 设计。

本 package 在 Phase 4 只承接：

    Focus / BBox 权重累加 → 阈值上报这一最小职责。

后人扩展 L3 时可在本 package 下加新模块；但 entry doc §8.1 L13 锁定的硬约束：

    1. ``__init__.py`` 只 re-export ``FocusBboxThreshold``。
    2. 顶层**不允许** export 名字叫 ``Attention`` 的类符号
       （避免误读为 "L3 已落地"）。
    3. 添加新模块必须保持 import 显式：``from parrot.dsg.attention.<module>
       import <symbol>``，不在本 ``__init__.py`` 隐式 re-export。

违反任一条 = 协议级漂移，必须先改 entry doc §8 再改代码。
"""

from parrot.dsg.attention.threshold import FocusBboxThreshold


__all__ = ["FocusBboxThreshold"]
