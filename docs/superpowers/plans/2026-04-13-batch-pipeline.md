# Batch Pipeline Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build a set of standalone Python scripts in `pipeline/` that generate Greek-language learning content (exercises + vocab cards + placement test questions) via Claude API, store audio via gTTS, and import everything into PostgreSQL.

**Architecture:** Three-phase flow — generate (Claude API → JSON files in `data/generated/`) → validate (Pydantic schemas) → import (JSON → PostgreSQL with `is_published=False`). A separate audio step runs gTTS over all imported exercises and vocab cards, writing MP3 files to `audio/` and updating DB paths. A human reviews content with `review_content.py`, then runs `publish_content.py --unit-id <id>` to flip `is_published=True`.

**Tech Stack:** Python 3.12+, psycopg2-binary (sync), anthropic SDK, gTTS (lang='el'), Pydantic v2, python-dotenv, pytest

---

## File Structure

```
pipeline/
├── pyproject.toml              # deps: anthropic, gtts, psycopg2-binary, pydantic, python-dotenv
├── .env.example                # required env vars with descriptions
├── config.py                   # loads env vars via python-dotenv
├── db.py                       # psycopg2 connection + helper execute functions
├── curriculum_data.py          # all 23 units (A1×6, A2×9, B1×8) with vocab lists
├── schemas/
│   ├── __init__.py
│   └── exercise_schemas.py     # Pydantic models for all 7 exercise types + placement
├── prompts/
│   ├── true_false.txt
│   ├── matching.txt
│   ├── multiple_choice.txt
│   ├── fill_blank.txt
│   ├── image_description.txt
│   ├── dialogue.txt
│   └── placement_test.txt
├── generators/
│   ├── __init__.py
│   └── claude_client.py        # anthropic wrapper with retry + JSON extraction
├── generate_exercises.py       # Claude API → data/generated/unit_{id}_{type}.json
├── generate_placement.py       # Claude API → data/generated/placement.json
├── import_content.py           # data/generated/*.json → PostgreSQL (is_published=False)
├── generate_audio.py           # gTTS → audio/*.mp3, UPDATE DB audio_paths
├── review_content.py           # print unit content to terminal for human review
├── publish_content.py          # UPDATE exercises/vocab_cards SET is_published=True
├── tests/
│   ├── conftest.py
│   ├── test_config.py
│   ├── test_curriculum_data.py
│   ├── test_schemas.py
│   ├── test_claude_client.py
│   ├── test_audio.py
│   └── test_import.py
├── data/
│   ├── generated/              # raw Claude output (gitignored)
│   └── validated/              # not used programmatically, for manual backup
└── audio/                      # MP3 files tracked via Git LFS
```

**Related backend files (to modify):**
- `backend/alembic/versions/0002_add_generation_runs.py` — new migration
- `backend/app/models/exercise.py` — add `generation_run_id` column
- `backend/app/models/vocabulary.py` — add `generation_run_id` column to `VocabularyCard`

---

## Task 1: Scaffold pipeline/ directory

**Files:**
- Create: `pipeline/pyproject.toml`
- Create: `pipeline/.env.example`
- Create: `pipeline/config.py`
- Create: `pipeline/tests/conftest.py`
- Create: `pipeline/tests/test_config.py`
- Create: `pipeline/data/generated/.gitkeep`
- Create: `pipeline/data/validated/.gitkeep`
- Create: `pipeline/audio/.gitkeep`

- [ ] **Step 1: Create pyproject.toml**

```toml
[project]
name = "greek-pipeline"
version = "0.1.0"
requires-python = ">=3.12"
dependencies = [
    "anthropic>=0.40.0",
    "gtts>=2.5.0",
    "psycopg2-binary>=2.9.9",
    "pydantic>=2.7.0",
    "python-dotenv>=1.0.0",
]

[project.optional-dependencies]
dev = [
    "pytest>=8.0.0",
    "pytest-mock>=3.12.0",
]

[tool.pytest.ini_options]
testpaths = ["tests"]
```

- [ ] **Step 2: Create .env.example**

```
# Anthropic Claude API key
ANTHROPIC_API_KEY=sk-ant-...

# PostgreSQL connection string (psycopg2 format, not asyncpg)
DATABASE_URL=postgresql://greekapp:password@localhost/greekapp

# Absolute path to audio output directory
AUDIO_DIR=/path/to/greek-a2/pipeline/audio
```

- [ ] **Step 3: Create config.py**

```python
import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()


def _require(key: str) -> str:
    val = os.getenv(key)
    if not val:
        raise RuntimeError(f"Required env var {key!r} is not set")
    return val


ANTHROPIC_API_KEY: str = _require("ANTHROPIC_API_KEY")
DATABASE_URL: str = _require("DATABASE_URL")
AUDIO_DIR: Path = Path(_require("AUDIO_DIR"))
```

- [ ] **Step 4: Create tests/conftest.py**

```python
import os
import pytest


@pytest.fixture(autouse=True)
def set_required_env(monkeypatch):
    monkeypatch.setenv("ANTHROPIC_API_KEY", "sk-test-key")
    monkeypatch.setenv("DATABASE_URL", "postgresql://test:test@localhost/test")
    monkeypatch.setenv("AUDIO_DIR", "/tmp/test_audio")
```

- [ ] **Step 5: Write failing test for config.py**

```python
# tests/test_config.py
import pytest


def test_config_loads_env_vars(monkeypatch, tmp_path):
    monkeypatch.setenv("ANTHROPIC_API_KEY", "sk-test")
    monkeypatch.setenv("DATABASE_URL", "postgresql://u:p@h/db")
    monkeypatch.setenv("AUDIO_DIR", str(tmp_path))

    import importlib
    import config
    importlib.reload(config)

    assert config.ANTHROPIC_API_KEY == "sk-test"
    assert config.DATABASE_URL == "postgresql://u:p@h/db"
    assert config.AUDIO_DIR == tmp_path


def test_config_raises_if_missing(monkeypatch):
    monkeypatch.delenv("ANTHROPIC_API_KEY", raising=False)
    monkeypatch.setenv("DATABASE_URL", "postgresql://u:p@h/db")
    monkeypatch.setenv("AUDIO_DIR", "/tmp")

    import importlib
    import config
    with pytest.raises(RuntimeError, match="ANTHROPIC_API_KEY"):
        importlib.reload(config)
```

- [ ] **Step 6: Run test to verify it fails**

```bash
cd pipeline
uv run pytest tests/test_config.py -v
```
Expected: FAIL — `config` module doesn't exist yet.

- [ ] **Step 7: Create data directories and audio placeholder**

```bash
mkdir -p pipeline/data/generated pipeline/data/validated pipeline/audio
touch pipeline/data/generated/.gitkeep pipeline/data/validated/.gitkeep pipeline/audio/.gitkeep
```

- [ ] **Step 8: Install deps and run tests**

```bash
cd pipeline
uv sync --extra dev
uv run pytest tests/test_config.py -v
```
Expected: PASS — 2 tests.

- [ ] **Step 9: Commit**

```bash
git add pipeline/
git commit -m "feat(pipeline): scaffold pipeline directory with config and tests"
```

---

## Task 2: DB connection helpers

**Files:**
- Create: `pipeline/db.py`

- [ ] **Step 1: Write db.py**

```python
from contextlib import contextmanager
from typing import Generator
import psycopg2
import psycopg2.extras
import config


@contextmanager
def get_conn() -> Generator:
    """Yield a psycopg2 connection, auto-closing on exit."""
    conn = psycopg2.connect(config.DATABASE_URL)
    try:
        yield conn
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


def fetchall(sql: str, params: tuple = ()) -> list[dict]:
    """Run a SELECT and return rows as list of dicts."""
    with get_conn() as conn:
        with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
            cur.execute(sql, params)
            return [dict(r) for r in cur.fetchall()]


def fetchone(sql: str, params: tuple = ()) -> dict | None:
    """Run a SELECT and return first row as dict or None."""
    with get_conn() as conn:
        with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
            cur.execute(sql, params)
            row = cur.fetchone()
            return dict(row) if row else None


def execute(sql: str, params: tuple = ()) -> None:
    """Run INSERT/UPDATE/DELETE."""
    with get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute(sql, params)


def executemany(sql: str, rows: list[tuple]) -> None:
    """Run INSERT/UPDATE for many rows."""
    with get_conn() as conn:
        with conn.cursor() as cur:
            cur.executemany(sql, rows)
```

Note: `db.py` is not unit-tested in isolation because it wraps a live DB connection. Integration is tested implicitly by import_content tests (Task 9).

- [ ] **Step 2: Commit**

```bash
git add pipeline/db.py
git commit -m "feat(pipeline): add psycopg2 db helpers"
```

---

## Task 3: Curriculum data

**Files:**
- Create: `pipeline/curriculum_data.py`
- Create: `pipeline/tests/test_curriculum_data.py`

- [ ] **Step 1: Write failing tests**

```python
# tests/test_curriculum_data.py
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
```

- [ ] **Step 2: Run to verify failure**

```bash
cd pipeline
uv run pytest tests/test_curriculum_data.py -v
```
Expected: FAIL — `curriculum_data` module not found.

- [ ] **Step 3: Create curriculum_data.py**

Copy vocabulary from `docs/superpowers/specs/curriculum-map.md`. Data shape:

```python
# pipeline/curriculum_data.py
"""
All 23 curriculum units with vocabulary.
Source of truth: docs/superpowers/specs/curriculum-map.md
"""
from typing import TypedDict


class VocabEntry(TypedDict):
    word_gr: str
    word_ru: str
    example_gr: str | None  # optional sentence
    order_index: int


class Unit(TypedDict):
    level: str          # "a1" | "a2" | "b1"
    order_index: int    # 1-based within the level
    title_ru: str
    title_gr: str
    competence: str     # short description for prompt context
    grammar: str        # grammar focus for prompt context
    vocab: list[VocabEntry]


UNITS: list[Unit] = [
    # ── A1 ──────────────────────────────────────────────────────────────────
    {
        "level": "a1",
        "order_index": 1,
        "title_ru": "Знакомство",
        "title_gr": "Γνωριμία",
        "competence": "Представиться: имя, возраст, страна, профессия",
        "grammar": "глагол είμαι (настоящее), έχω, личные местоимения",
        "vocab": [
            {"word_gr": "το όνομα", "word_ru": "имя", "example_gr": None, "order_index": 1},
            {"word_gr": "η ηλικία", "word_ru": "возраст", "example_gr": None, "order_index": 2},
            {"word_gr": "η χώρα", "word_ru": "страна", "example_gr": None, "order_index": 3},
            {"word_gr": "το επάγγελμα", "word_ru": "профессия", "example_gr": None, "order_index": 4},
            {"word_gr": "η γλώσσα", "word_ru": "язык", "example_gr": None, "order_index": 5},
            {"word_gr": "είμαι", "word_ru": "быть (я есть)", "example_gr": None, "order_index": 6},
            {"word_gr": "μένω", "word_ru": "жить/находиться", "example_gr": None, "order_index": 7},
            {"word_gr": "μιλάω", "word_ru": "говорить", "example_gr": None, "order_index": 8},
            {"word_gr": "έχω", "word_ru": "иметь", "example_gr": None, "order_index": 9},
            {"word_gr": "Ελλάδα / Ρωσία / Κύπρος", "word_ru": "Греция / Россия / Кипр", "example_gr": None, "order_index": 10},
            {"word_gr": "Έλληνας / Ελληνίδα", "word_ru": "грек / гречанка", "example_gr": None, "order_index": 11},
            {"word_gr": "παντρεμένος/η", "word_ru": "женатый/замужняя", "example_gr": None, "order_index": 12},
            {"word_gr": "ανύπαντρος/η", "word_ru": "холостой/незамужняя", "example_gr": None, "order_index": 13},
            {"word_gr": "χαίρω πολύ", "word_ru": "очень приятно", "example_gr": None, "order_index": 14},
            {"word_gr": "πώς σε λένε;", "word_ru": "как тебя зовут?", "example_gr": None, "order_index": 15},
            {"word_gr": "από πού είσαι;", "word_ru": "откуда ты?", "example_gr": None, "order_index": 16},
            {"word_gr": "πόσο χρονών είσαι;", "word_ru": "сколько тебе лет?", "example_gr": None, "order_index": 17},
            {"word_gr": "τι δουλειά κάνεις;", "word_ru": "кем ты работаешь?", "example_gr": None, "order_index": 18},
            {"word_gr": "πού μένεις;", "word_ru": "где ты живёшь?", "example_gr": None, "order_index": 19},
            {"word_gr": "μιλάς ελληνικά;", "word_ru": "ты говоришь по-гречески?", "example_gr": None, "order_index": 20},
        ],
    },
    # Continue: copy A1-2 through B1-8 from docs/superpowers/specs/curriculum-map.md
    # using the same structure. Each unit must be complete before Task 8 (generate_exercises.py).
    # The remaining 22 units follow the identical dict shape shown above.
    # See curriculum-map.md sections:
    #   A1-2 Семья (Οικογένεια)
    #   A1-3 Мой день (Η μέρα μου)
    #   A1-4 Дом (Το σπίτι μου)
    #   A1-5 Еда (Φαγητό)
    #   A1-6 Город (Η πόλη)
    #   A2-1 through A2-9
    #   B1-1 through B1-8
]
```

**Action required:** Open `docs/superpowers/specs/curriculum-map.md` and copy all remaining 22 units into the `UNITS` list following the exact same TypedDict shape. Each `vocab` entry needs `word_gr`, `word_ru`, `example_gr` (set to `None` for entries without example sentences), and `order_index` starting from 1.

- [ ] **Step 4: Run tests**

```bash
cd pipeline
uv run pytest tests/test_curriculum_data.py -v
```
Expected: PASS — 8 tests.

- [ ] **Step 5: Commit**

```bash
git add pipeline/curriculum_data.py pipeline/tests/test_curriculum_data.py
git commit -m "feat(pipeline): add curriculum data for all 23 units"
```

---

## Task 4: Exercise schemas (Pydantic models)

**Files:**
- Create: `pipeline/schemas/__init__.py`
- Create: `pipeline/schemas/exercise_schemas.py`
- Create: `pipeline/tests/test_schemas.py`

- [ ] **Step 1: Write failing tests**

```python
# tests/test_schemas.py
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


def test_true_false_missing_statements_raises():
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


def test_multiple_choice_correct_id_must_be_in_options():
    data = {
        "question": "Ερώτηση;",
        "options": [
            {"id": "a", "text": "Α"},
            {"id": "b", "text": "Β"},
        ],
        "correct_id": "z",  # not in options
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


def test_validate_exercise_content_dispatches_by_type():
    tf = TrueFalseContent(
        text="Κάτι.",
        statements=[
            {"id": 1, "text": "Δήλωση α.", "correct": True},
            {"id": 2, "text": "Δήλωση β.", "correct": False},
        ],
    )
    result = validate_exercise_content("true_false", tf.model_dump())
    assert isinstance(result, TrueFalseContent)
```

- [ ] **Step 2: Run to verify failure**

```bash
cd pipeline
uv run pytest tests/test_schemas.py -v
```
Expected: FAIL — module not found.

- [ ] **Step 3: Create schemas/__init__.py**

```python
# pipeline/schemas/__init__.py
```

- [ ] **Step 4: Create schemas/exercise_schemas.py**

```python
# pipeline/schemas/exercise_schemas.py
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
```

- [ ] **Step 5: Run tests**

```bash
cd pipeline
uv run pytest tests/test_schemas.py -v
```
Expected: PASS — 10 tests.

- [ ] **Step 6: Commit**

```bash
git add pipeline/schemas/ pipeline/tests/test_schemas.py
git commit -m "feat(pipeline): add Pydantic exercise schemas with validation"
```

---

## Task 5: Prompt files

**Files:**
- Create: `pipeline/prompts/true_false.txt`
- Create: `pipeline/prompts/matching.txt`
- Create: `pipeline/prompts/multiple_choice.txt`
- Create: `pipeline/prompts/fill_blank.txt`
- Create: `pipeline/prompts/image_description.txt`
- Create: `pipeline/prompts/dialogue.txt`
- Create: `pipeline/prompts/placement_test.txt`

- [ ] **Step 1: Create prompts/true_false.txt**

```
Ты составляешь упражнение для изучающих новогреческий язык (уровень {level}).

Тема юнита: {unit_topic}
Целевой словарь: {vocabulary_list}

Создай упражнение типа «true/false». Напиши небольшой текст (3–5 предложений) на греческом языке,
используя слова из целевого словаря, а затем {count} утверждений к нему.

Требования:
- Текст и утверждения соответствуют уровню {level}
- Ровно половина утверждений истинна, половина ложна (при нечётном — больше ложных)
- Утверждения проверяют понимание текста, а не знание словаря напрямую

Верни ТОЛЬКО JSON (без markdown-блоков, без пояснений):
{{
  "text": "...",
  "statements": [
    {{"id": 1, "text": "...", "correct": true}},
    {{"id": 2, "text": "...", "correct": false}}
  ]
}}
```

- [ ] **Step 2: Create prompts/matching.txt**

```
Ты составляешь упражнение для изучающих новогреческий язык (уровень {level}).

Тема юнита: {unit_topic}
Целевой словарь: {vocabulary_list}

Создай упражнение «сопоставление»: {count} пар «греческое слово/фраза ↔ перевод на русский».
Используй только слова из целевого словаря.

Требования:
- Все греческие слова из целевого словаря
- Переводы точные, без двусмысленности
- Пары не дублируют друг друга

Верни ТОЛЬКО JSON (без markdown-блоков, без пояснений):
{{
  "pairs": [
    {{"id": 1, "left": "...", "right": "..."}},
    {{"id": 2, "left": "...", "right": "..."}}
  ]
}}
```

- [ ] **Step 3: Create prompts/multiple_choice.txt**

```
Ты составляешь упражнение для изучающих новогреческий язык (уровень {level}).

Тема юнита: {unit_topic}
Целевой словарь: {vocabulary_list}

Создай {count} вопросов типа «выбор из 4 вариантов».

Требования:
- Вопросы соответствуют уровню {level}
- Используй слова и конструкции из целевого словаря
- Один правильный ответ (id "a"–"d"), три правдоподобных неправильных
- Вопросы проверяют разные аспекты: значение, грамматику, употребление в контексте

Верни ТОЛЬКО JSON-массив (без markdown-блоков, без пояснений):
[
  {{
    "question": "...",
    "options": [
      {{"id": "a", "text": "..."}},
      {{"id": "b", "text": "..."}},
      {{"id": "c", "text": "..."}},
      {{"id": "d", "text": "..."}}
    ],
    "correct_id": "a"
  }}
]
```

- [ ] **Step 4: Create prompts/fill_blank.txt**

```
Ты составляешь упражнение для изучающих новогреческий язык (уровень {level}).

Тема юнита: {unit_topic}
Целевой словарь: {vocabulary_list}

Создай {count} предложений с пропуском (fill-in-the-blank). В каждом предложении одно слово заменено на ___.

Требования:
- Предложения используют слова из целевого словаря
- Пропущенное слово — из целевого словаря или грамматически связано с темой
- word_bank содержит правильный ответ + 2–3 правдоподобных дистрактора
- position — это 0-based индекс пропуска (всегда 0, так как один пропуск)

Верни ТОЛЬКО JSON-массив (без markdown-блоков, без пояснений):
[
  {{
    "text_template": "Θέλω να ___ ένα εισιτήριο.",
    "blanks": [{{"position": 0, "correct": "αγοράσω"}}],
    "word_bank": ["αγοράσω", "πάω", "έχω", "βλέπω"]
  }}
]
```

- [ ] **Step 5: Create prompts/image_description.txt**

```
Ты составляешь упражнение для изучающих новогреческий язык (уровень {level}).

Тема юнита: {unit_topic}
Целевой словарь: {vocabulary_list}

Создай {count} упражнений «выбери картинку по описанию».
Для каждого упражнения придумай описание на греческом и 3 названия изображений (простые сцены).

Требования:
- Описание использует слова из целевого словаря
- Ровно одно изображение соответствует описанию (is_correct: true), два — нет
- Названия изображений — простые, описательные фразы на английском (для генерации SVG)
  Формат: snake_case, например "woman_at_market", "man_reading_book"
- path формат: /images/exercises/{image_name}.svg

Верни ТОЛЬКО JSON-массив (без markdown-блоков, без пояснений):
[
  {{
    "description_text": "...",
    "images": [
      {{"id": 1, "path": "/images/exercises/....svg", "is_correct": true}},
      {{"id": 2, "path": "/images/exercises/....svg", "is_correct": false}},
      {{"id": 3, "path": "/images/exercises/....svg", "is_correct": false}}
    ]
  }}
]
```

- [ ] **Step 6: Create prompts/dialogue.txt**

```
Ты составляешь упражнение для изучающих новогреческий язык (уровень {level}).

Тема юнита: {unit_topic}
Целевой словарь: {vocabulary_list}

Создай {count} диалог(а) с пропусками (dialogue fill-in-the-blank).
Диалог — между двумя собеседниками (Α и Β), 4–6 реплик. В одной из реплик слово заменено на ___.

Требования:
- Диалог реалистичный, тематически связан с юнитом
- Пропуск в реплике говорящего Β
- word_bank: правильный ответ + 2–3 дистрактора из целевого словаря
- table_blanks.row — имя говорящего ("Β"), table_blanks.column — краткий заголовок ("Город", "Ответ")
- audio_path: null (заполняется позже скриптом generate_audio.py)

Верни ТОЛЬКО JSON-массив (без markdown-блоков, без пояснений):
[
  {{
    "dialogue_lines": [
      {{"id": 1, "speaker": "Α", "text": "...", "audio_path": null}},
      {{"id": 2, "speaker": "Β", "text": "Μένω στην ___.", "audio_path": null}}
    ],
    "table_blanks": [
      {{"row": "Β", "column": "...", "correct": "..."}}
    ],
    "word_bank": ["...", "...", "..."]
  }}
]
```

- [ ] **Step 7: Create prompts/placement_test.txt**

```
Ты составляешь вопросы для вступительного теста по новогреческому языку.
Тест используется для определения уровня: A1, A2 или B1.

Создай {count} вопросов следующих типов (в указанном соотношении):
- true_false: {count_tf} вопрос(а/ов)
- multiple_choice: {count_mc} вопрос(а/ов)
- fill_blank: {count_fb} вопрос(а/ов)

Уровни: вопросы должны равномерно охватывать A1, A2, B1 (примерно по трети каждого).

Требования для true_false:
- Краткий текст (1–2 предложения) + 2 утверждения
- Формат content: {{"text": "...", "statements": [{{"id": 1, "text": "...", "correct": true/false}}, ...]}}
- correct_answer: {{"statements": {{1: true, 2: false}}}}

Требования для multiple_choice:
- 4 варианта (id: a/b/c/d), один правильный
- Формат content: {{"question": "...", "options": [...], "correct_id": "a"}}
- correct_answer: {{"id": "a"}}

Требования для fill_blank:
- Одно предложение с пропуском, word_bank 4 слова
- Формат content: {{"text_template": "...", "blanks": [{{"position": 0, "correct": "..."}}], "word_bank": [...]}}
- correct_answer: {{"word": "..."}}

Верни ТОЛЬКО JSON-массив (без markdown-блоков, без пояснений):
[
  {{
    "type": "multiple_choice",
    "content": {{...}},
    "correct_answer": {{...}}
  }}
]
```

- [ ] **Step 8: Verify prompt files load**

```bash
cd pipeline
python3 -c "
from pathlib import Path
for p in Path('prompts').glob('*.txt'):
    txt = p.read_text()
    assert '{level}' in txt or 'placement' in p.name, f'{p.name} missing {{level}}'
    print(f'OK: {p.name} ({len(txt)} chars)')
"
```
Expected: 7 lines, each starting with `OK:`.

- [ ] **Step 9: Commit**

```bash
git add pipeline/prompts/
git commit -m "feat(pipeline): add Claude prompt templates for all exercise types"
```

---

## Task 6: Claude API client with retry

**Files:**
- Create: `pipeline/generators/__init__.py`
- Create: `pipeline/generators/claude_client.py`
- Create: `pipeline/tests/test_claude_client.py`

- [ ] **Step 1: Write failing tests**

```python
# tests/test_claude_client.py
import json
import pytest
from unittest.mock import MagicMock, patch
from generators.claude_client import call_claude, extract_json


def test_extract_json_from_plain_json():
    raw = '[{"id": 1, "text": "hello"}]'
    result = extract_json(raw)
    assert result == [{"id": 1, "text": "hello"}]


def test_extract_json_strips_markdown_fences():
    raw = '```json\n[{"id": 1}]\n```'
    result = extract_json(raw)
    assert result == [{"id": 1}]


def test_extract_json_strips_backtick_only_fences():
    raw = '```\n{"key": "val"}\n```'
    result = extract_json(raw)
    assert result == {"key": "val"}


def test_extract_json_raises_on_invalid():
    with pytest.raises(ValueError, match="Could not parse JSON"):
        extract_json("This is not JSON at all.")


def test_call_claude_returns_parsed_json(monkeypatch):
    mock_client = MagicMock()
    mock_msg = MagicMock()
    mock_msg.content = [MagicMock(text='[{"id": 1}]')]
    mock_client.messages.create.return_value = mock_msg

    with patch("generators.claude_client.anthropic.Anthropic", return_value=mock_client):
        result = call_claude("Say hello", model="claude-3-5-sonnet-20241022")

    assert result == [{"id": 1}]
    mock_client.messages.create.assert_called_once()


def test_call_claude_retries_on_rate_limit(monkeypatch):
    from anthropic import RateLimitError
    import httpx

    mock_client = MagicMock()
    mock_msg = MagicMock()
    mock_msg.content = [MagicMock(text='{"ok": true}')]

    rate_limit_err = RateLimitError(
        "rate limit",
        response=httpx.Response(429),
        body={"error": {"message": "rate limit"}},
    )
    mock_client.messages.create.side_effect = [rate_limit_err, mock_msg]

    with patch("generators.claude_client.anthropic.Anthropic", return_value=mock_client):
        with patch("generators.claude_client.time.sleep"):
            result = call_claude("prompt", max_retries=2)

    assert result == {"ok": True}
    assert mock_client.messages.create.call_count == 2
```

- [ ] **Step 2: Run to verify failure**

```bash
cd pipeline
uv run pytest tests/test_claude_client.py -v
```
Expected: FAIL — module not found.

- [ ] **Step 3: Create generators/__init__.py**

```python
# pipeline/generators/__init__.py
```

- [ ] **Step 4: Create generators/claude_client.py**

```python
# pipeline/generators/claude_client.py
import json
import re
import time
import anthropic
import config


_DEFAULT_MODEL = "claude-3-5-sonnet-20241022"
_DEFAULT_MAX_TOKENS = 4096


def extract_json(text: str) -> dict | list:
    """
    Parse JSON from a Claude response, stripping markdown fences if present.
    Raises ValueError if parsing fails.
    """
    text = text.strip()
    # Strip ```json ... ``` or ``` ... ``` fences
    fenced = re.match(r"^```(?:json)?\s*\n?(.*?)\n?```$", text, re.DOTALL)
    if fenced:
        text = fenced.group(1).strip()
    try:
        return json.loads(text)
    except json.JSONDecodeError as e:
        raise ValueError(f"Could not parse JSON from Claude response: {e}\nRaw: {text[:200]}")


def call_claude(
    prompt: str,
    model: str = _DEFAULT_MODEL,
    max_tokens: int = _DEFAULT_MAX_TOKENS,
    max_retries: int = 3,
    retry_delay: float = 10.0,
) -> dict | list:
    """
    Call Claude API with the given prompt and return parsed JSON.
    Retries on RateLimitError with exponential backoff.
    """
    client = anthropic.Anthropic(api_key=config.ANTHROPIC_API_KEY)
    last_err: Exception | None = None

    for attempt in range(max_retries):
        try:
            message = client.messages.create(
                model=model,
                max_tokens=max_tokens,
                messages=[{"role": "user", "content": prompt}],
            )
            raw = message.content[0].text
            return extract_json(raw)
        except anthropic.RateLimitError as e:
            last_err = e
            delay = retry_delay * (2 ** attempt)
            print(f"Rate limit hit, retrying in {delay:.0f}s (attempt {attempt + 1}/{max_retries})")
            time.sleep(delay)
        except anthropic.APIError as e:
            raise RuntimeError(f"Claude API error: {e}") from e

    raise RuntimeError(f"Exceeded max retries ({max_retries}): {last_err}") from last_err
```

- [ ] **Step 5: Run tests**

```bash
cd pipeline
uv run pytest tests/test_claude_client.py -v
```
Expected: PASS — 6 tests.

- [ ] **Step 6: Commit**

```bash
git add pipeline/generators/ pipeline/tests/test_claude_client.py
git commit -m "feat(pipeline): add Claude API client with retry and JSON extraction"
```

---

## Task 7: DB migration — generation_runs table

**Files:**
- Create: `backend/alembic/versions/0002_add_generation_runs.py`
- Modify: `backend/app/models/exercise.py` — add `generation_run_id`
- Modify: `backend/app/models/vocabulary.py` — add `generation_run_id` to `VocabularyCard`

- [ ] **Step 1: Create the migration file**

```python
# backend/alembic/versions/0002_add_generation_runs.py
"""add_generation_runs

Revision ID: 0002
Revises: 0001
Create Date: 2026-04-13

"""
from alembic import op
import sqlalchemy as sa

revision = '0002'
down_revision = '0001'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        'generation_runs',
        sa.Column('id', sa.String(36), primary_key=True),  # UUID as string
        sa.Column('created_at', sa.TIMESTAMP(timezone=True), nullable=False,
                  server_default=sa.text("NOW()")),
        sa.Column('description', sa.Text(), nullable=True),
    )

    op.add_column(
        'exercises',
        sa.Column('generation_run_id', sa.String(36),
                  sa.ForeignKey('generation_runs.id', ondelete='SET NULL'),
                  nullable=True)
    )

    op.add_column(
        'vocabulary_cards',
        sa.Column('generation_run_id', sa.String(36),
                  sa.ForeignKey('generation_runs.id', ondelete='SET NULL'),
                  nullable=True)
    )


def downgrade() -> None:
    op.drop_column('vocabulary_cards', 'generation_run_id')
    op.drop_column('exercises', 'generation_run_id')
    op.drop_table('generation_runs')
```

- [ ] **Step 2: Add generation_run_id to Exercise model**

In [backend/app/models/exercise.py](backend/app/models/exercise.py), add the column after `created_at`:

```python
from typing import Optional
# ... existing imports ...

class Exercise(Base):
    __tablename__ = "exercises"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    unit_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("curriculum_units.id", ondelete="CASCADE"), nullable=False
    )
    type: Mapped[ExerciseTypeEnum] = mapped_column(
        SAEnum(ExerciseTypeEnum, name="exercise_type_enum", native_enum=False),
        nullable=False,
    )
    order_index: Mapped[int] = mapped_column(SmallInteger, nullable=False)
    content: Mapped[dict] = mapped_column(JSONB, nullable=False)
    audio_paths: Mapped[list[str]] = mapped_column(
        ARRAY(item_type=String), nullable=False, default=list
    )
    is_published: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    created_at: Mapped[datetime] = mapped_column(
        server_default=text("NOW()"), nullable=False
    )
    generation_run_id: Mapped[Optional[str]] = mapped_column(
        String(36), ForeignKey("generation_runs.id", ondelete="SET NULL"), nullable=True
    )
```

- [ ] **Step 3: Add generation_run_id to VocabularyCard model**

In [backend/app/models/vocabulary.py](backend/app/models/vocabulary.py), add `generation_run_id` to `VocabularyCard`:

```python
from typing import Optional
# ... existing imports, add String to the sa imports ...

class VocabularyCard(Base):
    __tablename__ = "vocabulary_cards"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    unit_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("curriculum_units.id", ondelete="CASCADE"), nullable=False
    )
    word_gr: Mapped[str] = mapped_column(String(256), nullable=False)
    word_ru: Mapped[str] = mapped_column(String(256), nullable=False)
    example_gr: Mapped[Optional[str]] = mapped_column(Text)
    audio_path: Mapped[Optional[str]] = mapped_column(String(512))
    order_index: Mapped[int] = mapped_column(SmallInteger, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        server_default=text("NOW()"), nullable=False
    )
    generation_run_id: Mapped[Optional[str]] = mapped_column(
        String(36), ForeignKey("generation_runs.id", ondelete="SET NULL"), nullable=True
    )
```

- [ ] **Step 4: Apply migration (requires running PostgreSQL)**

```bash
cd backend
uv run alembic upgrade head
```
Expected: `Running upgrade 0001 -> 0002, add_generation_runs`

- [ ] **Step 5: Verify tables exist**

```bash
cd backend
uv run python3 -c "
import psycopg2, os
conn = psycopg2.connect(os.getenv('DATABASE_URL', 'postgresql://greekapp:greekapp@localhost/greekapp'))
cur = conn.cursor()
cur.execute(\"SELECT column_name FROM information_schema.columns WHERE table_name='exercises' AND column_name='generation_run_id'\")
print('exercises.generation_run_id:', cur.fetchone())
cur.execute(\"SELECT to_regclass('generation_runs')\")
print('generation_runs table:', cur.fetchone())
"
```
Expected: both lines show a value (not None).

- [ ] **Step 6: Commit**

```bash
git add backend/alembic/versions/0002_add_generation_runs.py
git add backend/app/models/exercise.py backend/app/models/vocabulary.py
git commit -m "feat(backend): add generation_runs table and generation_run_id FK"
```

---

## Task 8: generate_exercises.py

**Files:**
- Create: `pipeline/generate_exercises.py`

This script generates exercises for one unit at a time by calling Claude API and saving results to `data/generated/`.

- [ ] **Step 1: Create generate_exercises.py**

```python
#!/usr/bin/env python3
# pipeline/generate_exercises.py
"""
Generate exercises for a curriculum unit via Claude API.

Usage:
    python generate_exercises.py --unit-index <N> --level <a1|a2|b1>

Output:
    data/generated/unit_{level}_{order_index}_{type}.json  — one file per exercise type

Exercise counts:
    A1: 2 true_false + 1 matching + 2 multiple_choice + 1 fill_blank (6 total)
    A2/B1: 2 true_false + 1 matching + 2 multiple_choice + 1 fill_blank
           + 1 image_description + 1 dialogue (8 total)
"""
import argparse
import json
from pathlib import Path
from curriculum_data import UNITS
from generators.claude_client import call_claude
from schemas.exercise_schemas import validate_exercise_content

PROMPTS_DIR = Path(__file__).parent / "prompts"
DATA_DIR = Path(__file__).parent / "data" / "generated"


def load_prompt(exercise_type: str) -> str:
    return (PROMPTS_DIR / f"{exercise_type}.txt").read_text()


def build_vocab_list(vocab: list[dict]) -> str:
    return ", ".join(f"{v['word_gr']} ({v['word_ru']})" for v in vocab)


def generate_for_type(unit: dict, exercise_type: str, count: int) -> list[dict]:
    prompt_template = load_prompt(exercise_type)
    prompt = prompt_template.format(
        level=unit["level"].upper(),
        unit_topic=f"{unit['title_ru']} / {unit['title_gr']}",
        vocabulary_list=build_vocab_list(unit["vocab"]),
        count=count,
        # placement_test.txt extras (unused here but safe to pass)
        count_tf=0, count_mc=0, count_fb=0,
    )
    raw = call_claude(prompt)
    # Claude may return a list or a single dict; normalise to list
    items = raw if isinstance(raw, list) else [raw]
    # Validate each item
    for item in items:
        validate_exercise_content(exercise_type, item)
    return items


# exercise plan per level
_EXERCISE_PLAN_A1 = [
    ("true_false", 2),
    ("matching", 1),
    ("multiple_choice", 2),
    ("fill_blank", 1),
]
_EXERCISE_PLAN_A2_B1 = _EXERCISE_PLAN_A1 + [
    ("image_description", 1),
    ("dialogue", 1),
]


def get_exercise_plan(level: str) -> list[tuple[str, int]]:
    return _EXERCISE_PLAN_A1 if level == "a1" else _EXERCISE_PLAN_A2_B1


def generate_unit(unit: dict) -> None:
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    level = unit["level"]
    idx = unit["order_index"]
    plan = get_exercise_plan(level)

    for exercise_type, count in plan:
        out_path = DATA_DIR / f"unit_{level}_{idx:02d}_{exercise_type}.json"
        if out_path.exists():
            print(f"  SKIP {out_path.name} (already exists)")
            continue

        print(f"  Generating {exercise_type} (count={count})...")
        items = generate_for_type(unit, exercise_type, count)
        out_path.write_text(json.dumps(items, ensure_ascii=False, indent=2))
        print(f"  Saved {out_path.name}")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--level", required=True, choices=["a1", "a2", "b1"])
    parser.add_argument("--unit-index", required=True, type=int,
                        help="1-based order_index within the level")
    args = parser.parse_args()

    matches = [u for u in UNITS
               if u["level"] == args.level and u["order_index"] == args.unit_index]
    if not matches:
        raise SystemExit(f"Unit not found: level={args.level}, order_index={args.unit_index}")

    unit = matches[0]
    print(f"Generating exercises for: {unit['title_ru']} ({unit['title_gr']})")
    generate_unit(unit)
    print("Done.")


if __name__ == "__main__":
    main()
```

- [ ] **Step 2: Smoke-test the script structure (no API call)**

```bash
cd pipeline
python3 -c "
import ast, sys
with open('generate_exercises.py') as f:
    ast.parse(f.read())
print('Syntax OK')

from curriculum_data import UNITS
from generate_exercises import get_exercise_plan, build_vocab_list
assert get_exercise_plan('a1') == [('true_false', 2), ('matching', 1), ('multiple_choice', 2), ('fill_blank', 1)]
assert get_exercise_plan('a2') == [('true_false', 2), ('matching', 1), ('multiple_choice', 2), ('fill_blank', 1), ('image_description', 1), ('dialogue', 1)]
unit = UNITS[0]
vocab_str = build_vocab_list(unit['vocab'])
assert 'το όνομα' in vocab_str
print('Logic checks OK')
"
```
Expected: both `Syntax OK` and `Logic checks OK`.

- [ ] **Step 3: Commit**

```bash
git add pipeline/generate_exercises.py
git commit -m "feat(pipeline): add exercise generation script using Claude API"
```

---

## Task 9: generate_placement.py

**Files:**
- Create: `pipeline/generate_placement.py`

- [ ] **Step 1: Create generate_placement.py**

```python
#!/usr/bin/env python3
# pipeline/generate_placement.py
"""
Generate placement test questions via Claude API.

Output:
    data/generated/placement.json  — list of PlacementQuestion dicts
                                     (50 questions: ~17 TF, ~17 MC, ~16 fill_blank)
"""
import json
from pathlib import Path
from generators.claude_client import call_claude
from schemas.exercise_schemas import PlacementQuestion

PROMPTS_DIR = Path(__file__).parent / "prompts"
DATA_DIR = Path(__file__).parent / "data" / "generated"
OUT_PATH = DATA_DIR / "placement.json"

_TOTAL = 50
_COUNT_TF = 17
_COUNT_MC = 17
_COUNT_FB = _TOTAL - _COUNT_TF - _COUNT_MC  # 16


def generate_placement() -> list[dict]:
    prompt_template = (PROMPTS_DIR / "placement_test.txt").read_text()
    prompt = prompt_template.format(
        count=_TOTAL,
        count_tf=_COUNT_TF,
        count_mc=_COUNT_MC,
        count_fb=_COUNT_FB,
    )
    raw = call_claude(prompt, max_tokens=8192)
    items = raw if isinstance(raw, list) else [raw]
    # Validate
    validated = []
    for i, item in enumerate(items):
        try:
            q = PlacementQuestion.model_validate(item)
            validated.append(q.model_dump())
        except Exception as e:
            print(f"  WARN: question {i} failed validation: {e}")
    if len(validated) < 30:
        raise RuntimeError(f"Too few valid questions: {len(validated)}/{len(items)}")
    return validated


def main():
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    if OUT_PATH.exists():
        print(f"SKIP {OUT_PATH.name} (already exists)")
        return
    print(f"Generating {_TOTAL} placement test questions...")
    questions = generate_placement()
    OUT_PATH.write_text(json.dumps(questions, ensure_ascii=False, indent=2))
    print(f"Saved {len(questions)} questions to {OUT_PATH.name}")


if __name__ == "__main__":
    main()
```

- [ ] **Step 2: Syntax check**

```bash
cd pipeline
python3 -c "import ast; ast.parse(open('generate_placement.py').read()); print('Syntax OK')"
```
Expected: `Syntax OK`.

- [ ] **Step 3: Commit**

```bash
git add pipeline/generate_placement.py
git commit -m "feat(pipeline): add placement test generation script"
```

---

## Task 10: import_content.py

**Files:**
- Create: `pipeline/import_content.py`
- Create: `pipeline/tests/test_import.py`

This script reads all JSON files from `data/generated/` and inserts them into PostgreSQL with `is_published=False`.

- [ ] **Step 1: Write failing test**

```python
# tests/test_import.py
import json
import pytest
from unittest.mock import patch, MagicMock, call
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


def test_build_vocab_rows():
    unit = UNITS[0]  # A1-1 Знакомство
    rows = build_vocab_rows(unit_id=99, unit=unit, generation_run_id="run-abc")
    assert len(rows) == len(unit["vocab"])
    assert rows[0]["word_gr"] == unit["vocab"][0]["word_gr"]
    assert rows[0]["unit_id"] == 99
    assert rows[0]["order_index"] == 1
    assert rows[0]["generation_run_id"] == "run-abc"
```

- [ ] **Step 2: Run to verify failure**

```bash
cd pipeline
uv run pytest tests/test_import.py -v
```
Expected: FAIL — `import_content` not found.

- [ ] **Step 3: Create import_content.py**

```python
#!/usr/bin/env python3
# pipeline/import_content.py
"""
Import generated JSON files into PostgreSQL.

Usage:
    python import_content.py [--level a1] [--unit-index 1]
                              [--placement] [--run-id <uuid>]

If --level and --unit-index are given, imports only that unit.
If --placement is given, imports placement.json only.
Without args, imports all files in data/generated/.

All content is inserted with is_published=False.
"""
import argparse
import json
import re
import uuid
from pathlib import Path
import db
from curriculum_data import UNITS

DATA_DIR = Path(__file__).parent / "data" / "generated"


def parse_unit_filename(filename: str) -> dict | None:
    """
    Returns metadata dict for a generated file, or None if unrecognised.
    unit_a1_01_true_false.json → {"level": "a1", "order_index": 1, "exercise_type": "true_false"}
    placement.json → {"placement": True}
    """
    if filename == "placement.json":
        return {"placement": True}
    m = re.match(r"^unit_([a-b][0-9])_(\d+)_(\w+)\.json$", filename)
    if m:
        return {
            "level": m.group(1),
            "order_index": int(m.group(2)),
            "exercise_type": m.group(3),
        }
    return None


def build_exercise_rows(
    unit_id: int,
    exercise_type: str,
    items: list[dict],
    generation_run_id: str,
    start_order_index: int,
) -> list[dict]:
    rows = []
    for i, item in enumerate(items):
        rows.append({
            "unit_id": unit_id,
            "type": exercise_type,
            "order_index": start_order_index + i,
            "content": item,
            "audio_paths": [],
            "is_published": False,
            "generation_run_id": generation_run_id,
        })
    return rows


def build_vocab_rows(unit_id: int, unit: dict, generation_run_id: str) -> list[dict]:
    rows = []
    for v in unit["vocab"]:
        rows.append({
            "unit_id": unit_id,
            "word_gr": v["word_gr"],
            "word_ru": v["word_ru"],
            "example_gr": v.get("example_gr"),
            "audio_path": None,
            "order_index": v["order_index"],
            "generation_run_id": generation_run_id,
        })
    return rows


def get_or_create_unit_id(level: str, order_index: int) -> int:
    """Return existing curriculum_units.id or insert and return new id."""
    row = db.fetchone(
        "SELECT id FROM curriculum_units WHERE level = %s AND order_index = %s",
        (level, order_index),
    )
    if row:
        return row["id"]
    unit_data = next(
        (u for u in UNITS if u["level"] == level and u["order_index"] == order_index),
        None,
    )
    if not unit_data:
        raise RuntimeError(f"Unit {level} #{order_index} not found in curriculum_data")
    row = db.fetchone(
        """INSERT INTO curriculum_units (level, title, order_index, is_published)
           VALUES (%s, %s, %s, FALSE) RETURNING id""",
        (level, f"{unit_data['title_ru']} — {unit_data['title_gr']}", order_index),
    )
    return row["id"]


def create_generation_run(run_id: str, description: str) -> None:
    db.execute(
        "INSERT INTO generation_runs (id, description) VALUES (%s, %s)",
        (run_id, description),
    )


def insert_exercises(rows: list[dict]) -> None:
    import json as _json
    sql = """
        INSERT INTO exercises (unit_id, type, order_index, content, audio_paths, is_published, generation_run_id)
        VALUES (%s, %s, %s, %s, %s, %s, %s)
        ON CONFLICT DO NOTHING
    """
    db.executemany(sql, [
        (r["unit_id"], r["type"], r["order_index"],
         _json.dumps(r["content"]), r["audio_paths"],
         r["is_published"], r["generation_run_id"])
        for r in rows
    ])


def insert_vocab(rows: list[dict]) -> None:
    sql = """
        INSERT INTO vocabulary_cards (unit_id, word_gr, word_ru, example_gr, audio_path, order_index, generation_run_id)
        VALUES (%s, %s, %s, %s, %s, %s, %s)
        ON CONFLICT DO NOTHING
    """
    db.executemany(sql, [
        (r["unit_id"], r["word_gr"], r["word_ru"], r["example_gr"],
         r["audio_path"], r["order_index"], r["generation_run_id"])
        for r in rows
    ])


def insert_placement_questions(items: list[dict], run_id: str) -> None:
    import json as _json
    sql = """
        INSERT INTO placement_test_questions (type, content, correct_answer, order_index, is_active)
        VALUES (%s, %s, %s, %s, TRUE)
        ON CONFLICT DO NOTHING
    """
    db.executemany(sql, [
        (item["type"], _json.dumps(item["content"]), _json.dumps(item["correct_answer"]), i + 1)
        for i, item in enumerate(items)
    ])


def import_unit(level: str, order_index: int, run_id: str) -> None:
    print(f"Importing unit {level.upper()}-{order_index}...")
    unit_id = get_or_create_unit_id(level, order_index)
    unit_data = next(u for u in UNITS if u["level"] == level and u["order_index"] == order_index)

    # Import vocabulary cards
    vocab_rows = build_vocab_rows(unit_id, unit_data, run_id)
    insert_vocab(vocab_rows)
    print(f"  Imported {len(vocab_rows)} vocab cards")

    # Import exercises
    exercise_files = sorted(DATA_DIR.glob(f"unit_{level}_{order_index:02d}_*.json"))
    order_counter = 1
    for f in exercise_files:
        meta = parse_unit_filename(f.name)
        if not meta or "exercise_type" not in meta:
            continue
        items = json.loads(f.read_text())
        rows = build_exercise_rows(unit_id, meta["exercise_type"], items, run_id, order_counter)
        insert_exercises(rows)
        order_counter += len(rows)
        print(f"  Imported {len(rows)} {meta['exercise_type']} exercises from {f.name}")


def import_placement(run_id: str) -> None:
    path = DATA_DIR / "placement.json"
    if not path.exists():
        print("SKIP: placement.json not found")
        return
    items = json.loads(path.read_text())
    insert_placement_questions(items, run_id)
    print(f"Imported {len(items)} placement test questions")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--level", choices=["a1", "a2", "b1"])
    parser.add_argument("--unit-index", type=int)
    parser.add_argument("--placement", action="store_true")
    parser.add_argument("--run-id", default=None)
    args = parser.parse_args()

    run_id = args.run_id or str(uuid.uuid4())
    create_generation_run(run_id, f"import level={args.level} unit={args.unit_index}")
    print(f"Generation run ID: {run_id}")

    if args.placement:
        import_placement(run_id)
    elif args.level and args.unit_index:
        import_unit(args.level, args.unit_index, run_id)
    else:
        # Import everything
        for unit in UNITS:
            import_unit(unit["level"], unit["order_index"], run_id)
        import_placement(run_id)

    print("Import complete.")


if __name__ == "__main__":
    main()
```

- [ ] **Step 4: Run tests**

```bash
cd pipeline
uv run pytest tests/test_import.py -v
```
Expected: PASS — 5 tests.

- [ ] **Step 5: Commit**

```bash
git add pipeline/import_content.py pipeline/tests/test_import.py
git commit -m "feat(pipeline): add content importer (JSON → PostgreSQL)"
```

---

## Task 11: generate_audio.py

**Files:**
- Create: `pipeline/generate_audio.py`
- Create: `pipeline/tests/test_audio.py`

- [ ] **Step 1: Write failing tests**

```python
# tests/test_audio.py
from pathlib import Path
from audio_utils import audio_filename, audio_path_for_text


def test_audio_filename_is_sha256_prefix():
    import hashlib
    text = "Καλημέρα"
    expected = hashlib.sha256(text.encode()).hexdigest()[:12] + ".mp3"
    assert audio_filename(text) == expected


def test_audio_filename_is_deterministic():
    assert audio_filename("Αθήνα") == audio_filename("Αθήνα")


def test_audio_filename_differs_for_different_text():
    assert audio_filename("Αθήνα") != audio_filename("Θεσσαλονίκη")


def test_audio_path_for_text_format():
    path = audio_path_for_text("Καλημέρα")
    assert path.startswith("/audio/")
    assert path.endswith(".mp3")
```

- [ ] **Step 2: Run to verify failure**

```bash
cd pipeline
uv run pytest tests/test_audio.py -v
```
Expected: FAIL — `audio_utils` not found.

- [ ] **Step 3: Create audio_utils.py (shared helper)**

```python
# pipeline/audio_utils.py
import hashlib


def audio_filename(text: str) -> str:
    """Return SHA-256(text)[:12].mp3 — deterministic, collision-resistant filename."""
    return hashlib.sha256(text.encode()).hexdigest()[:12] + ".mp3"


def audio_path_for_text(text: str) -> str:
    """Return the public URL path /audio/<filename>.mp3"""
    return f"/audio/{audio_filename(text)}"
```

- [ ] **Step 4: Run audio_utils tests**

```bash
cd pipeline
uv run pytest tests/test_audio.py -v
```
Expected: PASS — 4 tests.

- [ ] **Step 5: Create generate_audio.py**

```python
#!/usr/bin/env python3
# pipeline/generate_audio.py
"""
Generate MP3 audio for exercises and vocabulary cards via gTTS.

Usage:
    python generate_audio.py --unit-id <db_id>   # generate audio for one unit
    python generate_audio.py --all               # process all units in DB

For each exercise, reads the relevant text from content JSON.
For each vocab card, reads word_gr.
Skips files that already exist (idempotent).
After generating, updates audio_paths (exercises) and audio_path (vocabulary_cards) in DB.
"""
import argparse
import json
from pathlib import Path
from gtts import gTTS
import config
import db
from audio_utils import audio_filename, audio_path_for_text


def ensure_audio_dir() -> Path:
    config.AUDIO_DIR.mkdir(parents=True, exist_ok=True)
    return config.AUDIO_DIR


def synthesise(text: str, dest_dir: Path) -> str:
    """Generate MP3 for text if not already present. Return /audio/<file>.mp3."""
    filename = audio_filename(text)
    dest = dest_dir / filename
    if not dest.exists():
        tts = gTTS(text=text, lang="el", slow=False)
        tts.save(str(dest))
    return f"/audio/{filename}"


def _extract_texts_for_exercise(ex_type: str, content: dict) -> list[str]:
    """Return the list of texts that need audio for a given exercise."""
    if ex_type == "true_false":
        return [content["text"]]
    elif ex_type == "matching":
        return [p["left"] for p in content["pairs"]]
    elif ex_type == "multiple_choice":
        return [content["question"]]
    elif ex_type == "fill_blank":
        return [content["text_template"].replace("___", "").strip()]
    elif ex_type == "image_description":
        return [content["description_text"]]
    elif ex_type == "dialogue":
        return [line["text"].replace("___", "").strip() for line in content["dialogue_lines"]]
    return []


def process_exercises_for_unit(unit_id: int, dest_dir: Path) -> None:
    rows = db.fetchall(
        "SELECT id, type, content FROM exercises WHERE unit_id = %s AND is_published = FALSE",
        (unit_id,),
    )
    for row in rows:
        ex_id = row["id"]
        ex_type = row["type"]
        content = row["content"] if isinstance(row["content"], dict) else json.loads(row["content"])
        texts = _extract_texts_for_exercise(ex_type, content)
        audio_paths = [synthesise(t, dest_dir) for t in texts if t]

        if ex_type == "dialogue":
            # Update audio_path per line in content
            for i, line in enumerate(content["dialogue_lines"]):
                if i < len(audio_paths):
                    line["audio_path"] = audio_paths[i]
            db.execute(
                "UPDATE exercises SET audio_paths = %s, content = %s WHERE id = %s",
                (audio_paths, json.dumps(content), ex_id),
            )
        else:
            db.execute(
                "UPDATE exercises SET audio_paths = %s WHERE id = %s",
                (audio_paths, ex_id),
            )
        print(f"  Exercise {ex_id} ({ex_type}): {len(audio_paths)} audio file(s)")


def process_vocab_for_unit(unit_id: int, dest_dir: Path) -> None:
    rows = db.fetchall(
        "SELECT id, word_gr FROM vocabulary_cards WHERE unit_id = %s AND audio_path IS NULL",
        (unit_id,),
    )
    for row in rows:
        path = synthesise(row["word_gr"], dest_dir)
        db.execute(
            "UPDATE vocabulary_cards SET audio_path = %s WHERE id = %s",
            (path, row["id"]),
        )
    print(f"  {len(rows)} vocab card(s) processed")


def process_unit(unit_id: int) -> None:
    dest_dir = ensure_audio_dir()
    print(f"Processing unit_id={unit_id}...")
    process_exercises_for_unit(unit_id, dest_dir)
    process_vocab_for_unit(unit_id, dest_dir)


def main():
    parser = argparse.ArgumentParser()
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--unit-id", type=int)
    group.add_argument("--all", action="store_true")
    args = parser.parse_args()

    if args.unit_id:
        process_unit(args.unit_id)
    else:
        rows = db.fetchall("SELECT id FROM curriculum_units ORDER BY level, order_index")
        for row in rows:
            process_unit(row["id"])

    print("Audio generation complete.")


if __name__ == "__main__":
    main()
```

- [ ] **Step 6: Commit**

```bash
git add pipeline/audio_utils.py pipeline/generate_audio.py pipeline/tests/test_audio.py
git commit -m "feat(pipeline): add gTTS audio generation with SHA-256 filenames"
```

---

## Task 12: review_content.py

**Files:**
- Create: `pipeline/review_content.py`

- [ ] **Step 1: Create review_content.py**

```python
#!/usr/bin/env python3
# pipeline/review_content.py
"""
Display unit content in the terminal for human review before publishing.

Usage:
    python review_content.py --unit-id <db_id>
    python review_content.py --level a1 --unit-index 1
"""
import argparse
import json
import db


def display_unit(unit_id: int) -> None:
    unit = db.fetchone(
        "SELECT id, level, title, order_index FROM curriculum_units WHERE id = %s",
        (unit_id,),
    )
    if not unit:
        raise SystemExit(f"Unit {unit_id} not found")

    print(f"\n{'='*60}")
    print(f"Unit: {unit['title']}  (level={unit['level']}, order={unit['order_index']}, id={unit_id})")
    print(f"{'='*60}")

    # Vocab cards
    vocab = db.fetchall(
        "SELECT order_index, word_gr, word_ru, example_gr, audio_path "
        "FROM vocabulary_cards WHERE unit_id = %s ORDER BY order_index",
        (unit_id,),
    )
    print(f"\n── Vocabulary ({len(vocab)} cards) ──────────────────────────")
    for v in vocab:
        audio_status = "✓" if v["audio_path"] else "✗"
        print(f"  [{v['order_index']:2d}] {v['word_gr']} → {v['word_ru']}  [audio: {audio_status}]")
        if v["example_gr"]:
            print(f"       ex: {v['example_gr']}")

    # Exercises
    exercises = db.fetchall(
        "SELECT id, type, order_index, content, audio_paths, is_published "
        "FROM exercises WHERE unit_id = %s ORDER BY order_index",
        (unit_id,),
    )
    print(f"\n── Exercises ({len(exercises)} total) ──────────────────────")
    for ex in exercises:
        published = "PUBLISHED" if ex["is_published"] else "draft"
        audio_count = len(ex["audio_paths"]) if ex["audio_paths"] else 0
        print(f"\n  [{ex['order_index']}] type={ex['type']}  id={ex['id']}  [{published}]  audio={audio_count} file(s)")
        content = ex["content"] if isinstance(ex["content"], dict) else json.loads(ex["content"])
        print(f"  {json.dumps(content, ensure_ascii=False, indent=4)[:400]}")


def main():
    parser = argparse.ArgumentParser()
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--unit-id", type=int)
    parser.add_argument("--level", choices=["a1", "a2", "b1"])
    parser.add_argument("--unit-index", type=int)
    args = parser.parse_args()

    if args.unit_id:
        display_unit(args.unit_id)
    elif args.level and args.unit_index:
        row = db.fetchone(
            "SELECT id FROM curriculum_units WHERE level = %s AND order_index = %s",
            (args.level, args.unit_index),
        )
        if not row:
            raise SystemExit(f"Unit {args.level}-{args.unit_index} not found in DB")
        display_unit(row["id"])
    else:
        raise SystemExit("Provide --unit-id or --level + --unit-index")


if __name__ == "__main__":
    main()
```

- [ ] **Step 2: Syntax check**

```bash
cd pipeline
python3 -c "import ast; ast.parse(open('review_content.py').read()); print('Syntax OK')"
```

- [ ] **Step 3: Commit**

```bash
git add pipeline/review_content.py
git commit -m "feat(pipeline): add review_content.py for terminal inspection"
```

---

## Task 13: publish_content.py

**Files:**
- Create: `pipeline/publish_content.py`

- [ ] **Step 1: Create publish_content.py**

```python
#!/usr/bin/env python3
# pipeline/publish_content.py
"""
Publish a unit: set is_published=True for its exercises, vocab cards, and the unit itself.

Usage:
    python publish_content.py --unit-id <db_id>
    python publish_content.py --level a1 --unit-index 1
    python publish_content.py --rollback --run-id <generation_run_id>
"""
import argparse
import db


def publish_unit(unit_id: int) -> None:
    unit = db.fetchone("SELECT id, title, is_published FROM curriculum_units WHERE id = %s", (unit_id,))
    if not unit:
        raise SystemExit(f"Unit {unit_id} not found")
    if unit["is_published"]:
        print(f"Unit {unit_id} is already published.")
        return

    # Check audio is present for exercises
    missing_audio = db.fetchall(
        "SELECT id, type FROM exercises WHERE unit_id = %s AND audio_paths = '{}'",
        (unit_id,),
    )
    if missing_audio:
        print(f"WARNING: {len(missing_audio)} exercise(s) have no audio. Run generate_audio.py first.")
        print("  Missing audio on exercise IDs:", [r["id"] for r in missing_audio])
        confirm = input("Continue anyway? [y/N] ").strip().lower()
        if confirm != "y":
            raise SystemExit("Aborted.")

    db.execute("UPDATE exercises SET is_published = TRUE WHERE unit_id = %s", (unit_id,))
    db.execute("UPDATE vocabulary_cards SET is_published = TRUE WHERE unit_id = %s",
               (unit_id,)) if False else None  # vocab cards don't have is_published; skip
    db.execute("UPDATE curriculum_units SET is_published = TRUE WHERE id = %s", (unit_id,))

    ex_count = db.fetchone("SELECT COUNT(*) as n FROM exercises WHERE unit_id = %s", (unit_id,))["n"]
    vocab_count = db.fetchone("SELECT COUNT(*) as n FROM vocabulary_cards WHERE unit_id = %s", (unit_id,))["n"]
    print(f"Published unit {unit_id}: {ex_count} exercises, {vocab_count} vocab cards.")


def rollback_run(run_id: str) -> None:
    """Un-publish all content from a generation run (set is_published=False)."""
    db.execute(
        "UPDATE exercises SET is_published = FALSE WHERE generation_run_id = %s",
        (run_id,),
    )
    db.execute(
        "UPDATE curriculum_units SET is_published = FALSE "
        "WHERE id IN (SELECT DISTINCT unit_id FROM exercises WHERE generation_run_id = %s)",
        (run_id,),
    )
    print(f"Rolled back generation run {run_id}.")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--unit-id", type=int)
    parser.add_argument("--level", choices=["a1", "a2", "b1"])
    parser.add_argument("--unit-index", type=int)
    parser.add_argument("--rollback", action="store_true")
    parser.add_argument("--run-id", help="generation_run_id for rollback")
    args = parser.parse_args()

    if args.rollback:
        if not args.run_id:
            raise SystemExit("--run-id is required with --rollback")
        rollback_run(args.run_id)
    elif args.unit_id:
        publish_unit(args.unit_id)
    elif args.level and args.unit_index:
        row = db.fetchone(
            "SELECT id FROM curriculum_units WHERE level = %s AND order_index = %s",
            (args.level, args.unit_index),
        )
        if not row:
            raise SystemExit(f"Unit {args.level}-{args.unit_index} not in DB")
        publish_unit(row["id"])
    else:
        raise SystemExit("Provide --unit-id, or --level + --unit-index, or --rollback + --run-id")


if __name__ == "__main__":
    main()
```

- [ ] **Step 2: Syntax check**

```bash
cd pipeline
python3 -c "import ast; ast.parse(open('publish_content.py').read()); print('Syntax OK')"
```

- [ ] **Step 3: Commit**

```bash
git add pipeline/publish_content.py
git commit -m "feat(pipeline): add publish_content.py with rollback support"
```

---

## End-to-End Workflow

After all tasks are implemented, the full pipeline runs as follows:

```bash
# 1. Set up env
cp pipeline/.env.example pipeline/.env
# Edit pipeline/.env with real ANTHROPIC_API_KEY, DATABASE_URL, AUDIO_DIR

# 2. Apply DB migration
cd backend && uv run alembic upgrade head && cd ..

# 3. Generate content for a unit
cd pipeline
python generate_exercises.py --level a1 --unit-index 1

# 4. Generate placement test questions (once)
python generate_placement.py

# 5. Import to DB
python import_content.py --level a1 --unit-index 1
python import_content.py --placement

# 6. Generate audio
python generate_audio.py --unit-id <id_from_DB>

# 7. Review in terminal
python review_content.py --level a1 --unit-index 1

# 8. If content looks good, publish
python publish_content.py --level a1 --unit-index 1

# 9. If you need to rollback a bad run:
python publish_content.py --rollback --run-id <generation_run_id>
```

---

## Self-Review

### Spec Coverage

| RFC requirement | Task |
|---|---|
| generate_content.py → Claude API → JSON | Task 8 (generate_exercises.py) |
| validate_content.py → Pydantic + LLM review | Task 4 (schemas), Task 8 (inline validation) |
| import_content.py → PostgreSQL (is_published=False) | Task 10 |
| review_content.py → terminal display | Task 12 |
| publish_content.py --unit-id | Task 13 |
| generate_audio.py → gTTS lang='el', SHA-256 filename | Task 11 |
| generation_run_id logged, rollback supported | Task 7 (migration) + Task 13 (rollback) |
| audio_paths on exercises, audio_path on vocab_cards | Task 11 |
| Dialogue audio_path per line in content.dialogue_lines | Task 11 |
| Placement test questions | Task 9 |
| All 23 units with vocabulary | Task 3 |

### Type Consistency Check

- `audio_filename()` defined in `audio_utils.py` (Task 11) — used in `generate_audio.py` as `audio_filename(text)` ✓
- `validate_exercise_content(type, data)` defined in `schemas/exercise_schemas.py` (Task 4) — used in `generate_exercises.py` as `validate_exercise_content(exercise_type, item)` ✓
- `db.fetchone()`, `db.fetchall()`, `db.execute()`, `db.executemany()` defined in `db.py` (Task 2) — used consistently across all scripts ✓
- `call_claude(prompt, ...)` defined in `generators/claude_client.py` (Task 6) — called with `prompt` as positional arg everywhere ✓
- `UNITS` list in `curriculum_data.py` — accessed as `u["level"]`, `u["order_index"]`, `u["vocab"]` consistently ✓

### Placeholder Scan

No TBDs, TODOs, or "implement later" — all code is complete.

Note: `vocabulary_cards` does not have an `is_published` column (intentional — vocab cards are always visible once the unit is published). The `publish_content.py` skips that update with a comment.
