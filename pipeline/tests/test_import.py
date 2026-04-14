import pytest
from import_content import (
    parse_unit_filename,
    build_exercise_rows,
    build_vocab_rows,
)
from curriculum_data import UNITS


def test_parse_unit_filename_exercises():
    result = parse_unit_filename("unit_a1_01_true_false.json")
    assert result == {"level": "a1", "order_index": 1, "exercise_type": "true_false"}


def test_parse_unit_filename_placement():
    result = parse_unit_filename("placement.json")
    assert result == {"placement": True}


def test_parse_unit_filename_unknown_returns_none():
    result = parse_unit_filename("unknown_file.json")
    assert result is None


def test_parse_unit_filename_multiple_choice():
    result = parse_unit_filename("unit_b1_08_multiple_choice.json")
    assert result == {"level": "b1", "order_index": 8, "exercise_type": "multiple_choice"}


def test_build_exercise_rows_true_false():
    items = [
        {
            "text": "Η Μαρία πηγαίνει.",
            "statements": [
                {"id": 1, "text": "Δήλωση α.", "correct": True},
                {"id": 2, "text": "Δήλωση β.", "correct": False},
            ],
        }
    ]
    rows = build_exercise_rows(
        unit_id=1,
        exercise_type="true_false",
        items=items,
        generation_run_id="test-run-id",
        start_order_index=1,
    )
    assert len(rows) == 1
    row = rows[0]
    assert row["unit_id"] == 1
    assert row["type"] == "true_false"
    assert row["order_index"] == 1
    assert row["content"] == items[0]
    assert row["generation_run_id"] == "test-run-id"
    assert row["is_published"] is False
    assert row["audio_paths"] == []


def test_build_exercise_rows_multiple_items_order_index():
    items = [{"q": "a"}, {"q": "b"}]
    rows = build_exercise_rows(
        unit_id=5,
        exercise_type="multiple_choice",
        items=items,
        generation_run_id="run-1",
        start_order_index=3,
    )
    assert rows[0]["order_index"] == 3
    assert rows[1]["order_index"] == 4


def test_build_vocab_rows():
    unit = UNITS[0]  # A1-1 Знакомство
    rows = build_vocab_rows(unit_id=99, unit=unit, generation_run_id="run-abc")
    assert len(rows) == len(unit["vocab"])
    assert rows[0]["word_gr"] == unit["vocab"][0]["word_gr"]
    assert rows[0]["unit_id"] == 99
    assert rows[0]["order_index"] == 1
    assert rows[0]["generation_run_id"] == "run-abc"
    assert rows[0]["audio_path"] is None
