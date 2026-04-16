"""Tests for shared parrot action enums."""

from parrot.shared.parrot_actions import BehaviorMode, ParrotAnimation, ParrotBodyState


def test_behavior_mode_stackable():
    mode = BehaviorMode.BASE | BehaviorMode.COMPANION
    assert BehaviorMode.BASE in mode
    assert BehaviorMode.COMPANION in mode
    assert BehaviorMode.BUTLER not in mode


def test_behavior_mode_add_remove():
    mode = BehaviorMode.BASE | BehaviorMode.COMPANION
    mode |= BehaviorMode.BUTLER
    assert BehaviorMode.BUTLER in mode
    mode &= ~BehaviorMode.BUTLER
    assert BehaviorMode.BUTLER not in mode
    assert BehaviorMode.BASE in mode


def test_parrot_animation_values():
    expected = {"idle", "fly", "dance", "wing_flap", "perch", "sit", "head_bob", "sleep"}
    actual = {a.value for a in ParrotAnimation}
    assert actual == expected


def test_parrot_body_state_values():
    expected = {"idle", "flying", "perching", "dancing", "frozen"}
    actual = {s.value for s in ParrotBodyState}
    assert actual == expected
