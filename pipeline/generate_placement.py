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
    # Validate each question
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
