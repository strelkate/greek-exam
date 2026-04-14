from __future__ import annotations
from typing import Literal
from pydantic import BaseModel, model_validator


# ── Type 1: true_false ─────────────────────────────────────────────────────

class TrueFalseStatement(BaseModel):
    id: int
    text: str
    correct: bool


class TrueFalseContent(BaseModel):
    text: str
    statements: list[TrueFalseStatement]

    @model_validator(mode="after")
    def at_least_one_statement(self) -> TrueFalseContent:
        if not self.statements:
            raise ValueError("statements must be non-empty")
        return self


# ── Type 2: matching ────────────────────────────────────────────────────────

class MatchingPair(BaseModel):
    id: int
    left: str
    right: str


class MatchingContent(BaseModel):
    pairs: list[MatchingPair]

    @model_validator(mode="after")
    def at_least_two_pairs(self) -> MatchingContent:
        if len(self.pairs) < 2:
            raise ValueError("pairs must have at least 2 items")
        return self


# ── Type 3: multiple_choice ─────────────────────────────────────────────────

class MCOption(BaseModel):
    id: str
    text: str


class MultipleChoiceContent(BaseModel):
    question: str
    options: list[MCOption]
    correct_id: str

    @model_validator(mode="after")
    def correct_id_in_options(self) -> MultipleChoiceContent:
        ids = {o.id for o in self.options}
        if self.correct_id not in ids:
            raise ValueError(f"correct_id {self.correct_id!r} not in options {ids}")
        return self


# ── Type 4: fill_blank ──────────────────────────────────────────────────────

class Blank(BaseModel):
    position: int
    correct: str


class FillBlankContent(BaseModel):
    text_template: str
    blanks: list[Blank]
    word_bank: list[str]


# ── Type 6: image_description ───────────────────────────────────────────────

class ImageOption(BaseModel):
    id: int
    path: str
    is_correct: bool


class ImageDescriptionContent(BaseModel):
    description_text: str
    images: list[ImageOption]

    @model_validator(mode="after")
    def exactly_one_correct(self) -> ImageDescriptionContent:
        correct = [i for i in self.images if i.is_correct]
        if len(correct) != 1:
            raise ValueError("exactly one image must be is_correct=True")
        return self


# ── Type 7: dialogue ────────────────────────────────────────────────────────

class DialogueLine(BaseModel):
    id: int
    speaker: str
    text: str
    audio_path: str | None = None


class TableBlank(BaseModel):
    row: str
    column: str
    correct: str


class DialogueContent(BaseModel):
    dialogue_lines: list[DialogueLine]
    table_blanks: list[TableBlank]
    word_bank: list[str]


# ── Placement test question ──────────────────────────────────────────────────

class PlacementQuestion(BaseModel):
    type: Literal["true_false", "multiple_choice", "fill_blank"]
    content: dict
    correct_answer: dict


# ── Dispatch helper ──────────────────────────────────────────────────────────

_TYPE_MAP = {
    "true_false": TrueFalseContent,
    "matching": MatchingContent,
    "multiple_choice": MultipleChoiceContent,
    "fill_blank": FillBlankContent,
    "image_description": ImageDescriptionContent,
    "dialogue": DialogueContent,
}


def validate_exercise_content(exercise_type: str, data: dict):
    """Validate raw dict against the Pydantic model for the given exercise type."""
    cls = _TYPE_MAP.get(exercise_type)
    if cls is None:
        raise ValueError(f"Unknown exercise type: {exercise_type!r}")
    return cls.model_validate(data)
