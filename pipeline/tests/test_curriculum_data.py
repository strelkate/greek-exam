from curriculum_data import UNITS


def test_total_unit_count():
    assert len(UNITS) == 23


def test_a1_unit_count():
    a1 = [u for u in UNITS if u["level"] == "a1"]
    assert len(a1) == 6


def test_a2_unit_count():
    a2 = [u for u in UNITS if u["level"] == "a2"]
    assert len(a2) == 9


def test_b1_unit_count():
    b1 = [u for u in UNITS if u["level"] == "b1"]
    assert len(b1) == 8


def test_each_unit_has_required_keys():
    for u in UNITS:
        assert "level" in u
        assert "order_index" in u
        assert "title_ru" in u
        assert "title_gr" in u
        assert "vocab" in u


def test_each_vocab_entry_has_required_keys():
    for u in UNITS:
        for v in u["vocab"]:
            assert "word_gr" in v, f"Missing word_gr in unit {u['title_ru']}"
            assert "word_ru" in v, f"Missing word_ru in unit {u['title_ru']}"
            assert "order_index" in v


def test_vocab_order_index_sequential():
    for u in UNITS:
        indices = [v["order_index"] for v in u["vocab"]]
        assert indices == list(range(1, len(indices) + 1)), \
            f"Non-sequential order_index in unit {u['title_ru']}"


def test_unit_order_index_unique_within_level():
    from collections import defaultdict
    by_level = defaultdict(list)
    for u in UNITS:
        by_level[u["level"]].append(u["order_index"])
    for level, indices in by_level.items():
        assert len(indices) == len(set(indices)), f"Duplicate order_index in level {level}"
