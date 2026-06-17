from research_agent.text import clean_text, extract_json_object, repair_mojibake, slugify


def test_extract_json_object_from_fenced_block():
    raw = '```json\n{"relevant": true, "confidence": 8}\n```'
    assert extract_json_object(raw)["confidence"] == 8


def test_extract_json_object_from_surrounding_text():
    raw = 'Here is the result: {"overall": 9, "priority": "must_read"} thanks'
    assert extract_json_object(raw)["priority"] == "must_read"


def test_slugify_keeps_readable_ascii():
    assert slugify("Sparse Autoencoders: Why / When?") == "sparse-autoencoders-why-when"


def test_clean_text_collapses_whitespace():
    assert clean_text(" A\n\n  B\tC ") == "A B C"


def test_repair_mojibake_recovers_utf8_chinese_decoded_as_cp1252():
    broken = "é«˜åº¦è´´åˆ Alignment"
    assert repair_mojibake(broken) == "高度贴合 Alignment"
