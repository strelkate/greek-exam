#!/usr/bin/env python3
"""
Add sentence_ru field to fill_blank exercises in the SQLite database.
Matches exercises by text_template prefix and updates the content JSON.
"""

import sqlite3
import json

# Mapping from text_template prefix → sentence_ru
TRANSLATIONS = {
    "— Γεια σου! Πώς σε λένε;": "— Привет! Как тебя зовут?\n— Привет! Меня зовут Никос. Я из Греции. Говорю по-гречески и по-английски.",
    "Έχω μια": "У меня есть маленькая сестра. Ей семь лет.",
    "Συνήθως": "Обычно пью кофе утром перед работой.",
    "Μένω στον": "Я живу на третьем этаже. Лифта нет.",
    "Κάθε πρωί": "Каждое утро ем яйцо и пью молоко.",
    "Στρίψτε": "Поверните налево на углу, а затем идите прямо.",
    "Αυτό το παλτό": "Это пальто слишком дорогое. Ищу что-то подешевле.",
    "Αυτό το χρώμα": "— Этот цвет тебе очень идёт! Ты очень красиво выглядишь.",
    "— Αυτό το χρώμα": "— Этот цвет тебе очень идёт! Ты очень красиво выглядишь.",
    "Ορίστε 20 ευρώ": "— Вот 20 евро. — Оставьте сдачу, мне не нужна.",
    "— Ορίστε 20 ευρώ": "— Вот 20 евро. — Оставьте сдачу, мне не нужна.",
    "Θα ήθελα να κάνω": "Я бы хотел сделать бронь на двоих сегодня вечером.",
    "Θέλω να βρω καλύτερη": "Хочу найти работу получше, поэтому отправляю резюме во многие компании.",
    "Συναντιόμαστε": "Встречаемся в 6 на площади Синтагма.",
    "___ στις 6 στην πλατεία": "Встречаемся в 6 на площади Синтагма.",
    "Πού μπορώ να": "— Где можно купить билет? — В кассе вон там.",
    "— Πού μπορώ να": "— Где можно купить билет? — В кассе вон там.",
    "Παίρνω ένα χάπι": "Принимаю одну таблетку утром и одну вечером.",
    "Ψάχνω για": "Ищу квартиру с двумя комнатами рядом с центром.",
    "Είναι ___ μας να προστατεύουμε": "Это наша ответственность — защищать окружающую среду для будущих поколений.",
    "Συμφωνώ με την άποψη": "Согласен с мнением, что у технологий есть положительные и отрицательные стороны.",
    "Είναι σημαντικό να": "Важно сохранять наши традиции для будущих поколений.",
    "Αξίζει τον κόπο": "Стоит посетить Акрополь, если ты посещаешь Афины.",
    "Από τη μία πλευρά": "С одной стороны, миграция помогает экономике, но с другой — создаёт трудности.",
    "Θα ήθελα να ___ σε μια διεθνή": "Я бы хотел работать в международной компании с возможностями карьерного роста.",
    "Αισθάνομαι πολύ": "Я чувствую себя очень напряжённым. Мне нужен отпуск и отдых.",
    "Πριν ___ μια είδηση": "Прежде чем поделиться новостью в социальных сетях, я проверяю, правда ли это.",
}


def find_translation(text_template: str):
    """Find a matching translation by checking if text_template starts with any known prefix."""
    for prefix, sentence_ru in TRANSLATIONS.items():
        if text_template.startswith(prefix):
            return sentence_ru
    return None


def main():
    conn = sqlite3.connect("dev.db")
    cursor = conn.cursor()

    # Fetch all fill_blank exercises that don't already have sentence_ru
    cursor.execute(
        """
        SELECT id, content
        FROM exercises
        WHERE type = 'FILL_BLANK'
          AND json_extract(content, '$.sentence_ru') IS NULL
        """
    )
    rows = cursor.fetchall()
    print(f"Found {len(rows)} fill_blank exercises without sentence_ru")

    updated_count = 0
    skipped_count = 0

    for exercise_id, content_str in rows:
        try:
            content = json.loads(content_str)
        except json.JSONDecodeError as e:
            print(f"  ERROR: Could not parse content for exercise {exercise_id}: {e}")
            continue

        text_template = content.get("text_template", "")
        sentence_ru = find_translation(text_template)

        if sentence_ru is None:
            print(f"  SKIP (no match): exercise {exercise_id}, template: {text_template[:60]!r}")
            skipped_count += 1
            continue

        content["sentence_ru"] = sentence_ru
        new_content_str = json.dumps(content, ensure_ascii=False)

        cursor.execute(
            "UPDATE exercises SET content = ? WHERE id = ?",
            (new_content_str, exercise_id),
        )
        print(f"  UPDATED exercise {exercise_id}: {sentence_ru[:60]!r}")
        updated_count += 1

    conn.commit()
    conn.close()

    print(f"\nDone. Updated: {updated_count}, Skipped (no match): {skipped_count}")


if __name__ == "__main__":
    main()
