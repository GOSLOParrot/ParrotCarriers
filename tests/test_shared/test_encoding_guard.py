from parrot.memory.encoding_guard import detect_text_mojibake, text_has_mojibake


def test_encoding_guard_accepts_clean_chinese_laptop_profile_text() -> None:
    text = "用户的笔记本电脑是联想拯救者，也可以称为 Lenovo Legion laptop。"

    report = detect_text_mojibake(text)

    assert report["suspicious"] is False
    assert text_has_mojibake(text) is False


def test_encoding_guard_flags_utf8_decoded_as_latin1_mojibake() -> None:
    text = "GOSLO æ\u009c¬æ\u009cºæµ\u008bè¯\u0095ç\u009f¥è¯\u0086åº\u0093"

    report = detect_text_mojibake(text)

    assert report["suspicious"] is True
    assert "c1_control_chars" in ",".join(report["signals"])
    assert text_has_mojibake(text) is True
