import pytest
from schemas.exercise_schemas import (
    TrueFalseContent,
    MatchingContent,
    MultipleChoiceContent,
    FillBlankContent,
    ImageDescriptionContent,
    DialogueContent,
    PlacementQuestion,
    validate_exercise_content,
)


def test_true_false_valid():
    data = {
        "text": "Η Μαρία πηγαίνει στην αγορά.",
        "statements": [
            {"id": 1, "text": "Η Μαρία αγοράζει φρούτα.", "correct": True},
            {"id": 2, "text": "Η Μαρία είναι στο σπίτι.", "correct": False},
        ],
    }
    c = TrueFalseContent.model_validate(data)
    assert len(c.statements) == 2


def test_true_false_empty_statements_raises():
    with pytest.raises(Exception):
        TrueFalseContent.model_validate({"text": "Κάτι.", "statements": []})


def test_matching_valid():
    data = {
        "pairs": [
            {"id": 1, "left": "Καλημέρα", "right": "Доброе утро"},
            {"id": 2, "left": "Καληνύχτα", "right": "Спокойной ночи"},
        ]
    }
    c = MatchingContent.model_validate(data)
    assert len(c.pairs) == 2


def test_matching_one_pair_raises():
    with pytest.raises(Exception):
        MatchingContent.model_validate({"pairs": [{"id": 1, "left": "A", "right": "B"}]})


def test_multiple_choice_valid():
    data = {
        "question": "Πού είναι η βιβλιοθήκη;",
        "options": [
            {"id": "a", "text": "Στην αγορά"},
            {"id": "b", "text": "Στο κέντρο"},
            {"id": "c", "text": "Στο σπίτι"},
            {"id": "d", "text": "Στο σχολείο"},
        ],
        "correct_id": "b",
    }
    c = MultipleChoiceContent.model_validate(data)
    assert c.correct_id == "b"


def test_multiple_choice_correct_id_not_in_options_raises():
    data = {
        "question": "Ερώτηση;",
        "options": [
            {"id": "a", "text": "Α"},
            {"id": "b", "text": "Β"},
        ],
        "correct_id": "z",
    }
    with pytest.raises(Exception):
        MultipleChoiceContent.model_validate(data)


def test_fill_blank_valid():
    data = {
        "text_template": "Θέλω να ___ ένα εισιτήριο.",
        "blanks": [{"position": 0, "correct": "αγοράσω"}],
        "word_bank": ["αγοράσω", "πάω", "έχω"],
    }
    c = FillBlankContent.model_validate(data)
    assert c.blanks[0].correct == "αγοράσω"


def test_image_description_valid():
    data = {
        "description_text": "Η γυναίκα περπατά στην παραλία.",
        "images": [
            {"id": 1, "path": "/images/beach.svg", "is_correct": True},
            {"id": 2, "path": "/images/park.svg", "is_correct": False},
            {"id": 3, "path": "/images/market.svg", "is_correct": False},
        ],
    }
    c = ImageDescriptionContent.model_validate(data)
    assert len(c.images) == 3


def test_image_description_no_correct_raises():
    data = {
        "description_text": "Κάτι.",
        "images": [
            {"id": 1, "path": "/images/a.svg", "is_correct": False},
            {"id": 2, "path": "/images/b.svg", "is_correct": False},
        ],
    }
    with pytest.raises(Exception):
        ImageDescriptionContent.model_validate(data)


def test_dialogue_valid():
    data = {
        "dialogue_lines": [
            {"id": 1, "speaker": "Α", "text": "Πού μένεις;", "audio_path": None},
            {"id": 2, "speaker": "Β", "text": "Μένω στην ___.", "audio_path": None},
        ],
        "table_blanks": [{"row": "Β", "column": "Πόλη", "correct": "Αθήνα"}],
        "word_bank": ["Αθήνα", "Θεσσαλονίκη"],
    }
    c = DialogueContent.model_validate(data)
    assert len(c.dialogue_lines) == 2


def test_placement_question_valid():
    data = {
        "type": "multiple_choice",
        "content": {
            "question": "Τι είναι αυτό;",
            "options": [
                {"id": "a", "text": "Σπίτι"},
                {"id": "b", "text": "Σχολείο"},
                {"id": "c", "text": "Αγορά"},
                {"id": "d", "text": "Νοσοκομείο"},
            ],
            "correct_id": "a",
        },
        "correct_answer": {"id": "a"},
    }
    q = PlacementQuestion.model_validate(data)
    assert q.type == "multiple_choice"


def test_validate_exercise_content_dispatches():
    data = {
        "text": "Κάτι.",
        "statements": [
            {"id": 1, "text": "Δήλωση α.", "correct": True},
            {"id": 2, "text": "Δήλωση β.", "correct": False},
        ],
    }
    result = validate_exercise_content("true_false", data)
    assert isinstance(result, TrueFalseContent)


def test_validate_exercise_content_unknown_type_raises():
    with pytest.raises(ValueError, match="Unknown exercise type"):
        validate_exercise_content("flashcard", {})
