# Архитектурный RFC: Greek Learning App (Telegram Mini App)

**Дата:** 2026-04-06
**Статус:** Draft
**Автор:** Architect Agent
**На основе:** [Product Brief](product-brief.md) (утверждён 2026-04-06), [PRD](prd.md) (черновик 2026-04-06)

---

## Содержание

1. [Системные границы](#1-системные-границы)
2. [Компонентная диаграмма](#2-компонентная-диаграмма)
3. [Схема базы данных](#3-схема-базы-данных)
4. [API-контракты](#4-api-контракты)
5. [Frontend-архитектура](#5-frontend-архитектура)
6. [Offline-архитектура](#6-offline-архитектура)
7. [Аутентификация](#7-аутентификация)
8. [Batch-пайплайн](#8-batch-пайплайн)
9. [Деплой и инфраструктура](#9-деплой-и-инфраструктура)
10. [Architecture Decision Records](#10-architecture-decision-records)

---

## 1. Системные границы

### 1.1 Внутри системы

| Компонент | Ответственность |
|-----------|----------------|
| **React + Vite SPA** | UI, роутинг, управление состоянием, Service Worker |
| **FastAPI (Python)** | REST API, HMAC-верификация, бизнес-логика прогресса и XP |
| **PostgreSQL** | Хранение контента, прогресса пользователей, состояния SM-2 |
| **Service Worker** | Offline-кэширование статики, буферизация прогресса |
| **Batch-скрипты Python** | Генерация контента, валидация, загрузка в БД |
| **gTTS-пайплайн** | Генерация MP3-аудио, хранение через Git LFS |
| **Nginx** | Reverse proxy, отдача статики, SSL-терминация |

### 1.2 Внешние системы (не принадлежат проекту)

| Система | Роль | Взаимодействие |
|---------|------|----------------|
| **Telegram** | Платформа, аутентификация, хост Mini App | `initData` при запуске; Telegram SDK (`@twa-dev/sdk`) в браузере |
| **gTTS** | Синтез речи для аудио | Только в batch-режиме |
| **Git LFS** | Хранение бинарных аудио-файлов | Используется при разработке и деплое; пользователи не взаимодействуют напрямую |

### 1.3 Граничные условия

- В рантайме приложения **нет зависимостей** от внешних API — весь контент сгенерирован заранее.
- Telegram предоставляет только `initData` — никаких других Telegram Bot API вызовов в рантайме нет.
- Пользователи скачивают аудио и изображения со **статического сервера** приложения, не из Git LFS.

---

## 2. Компонентная диаграмма

```
┌─────────────────────────────────────────────────────────────────┐
│                       TELEGRAM CLIENT                           │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │                  Telegram Mini App                       │   │
│  │  ┌────────────────────────────────────────────────────┐ │   │
│  │  │               React + Vite SPA                     │ │   │
│  │  │                                                    │ │   │
│  │  │  ┌──────────────┐  ┌──────────────┐               │ │   │
│  │  │  │    Router    │  │ Zustand Store│               │ │   │
│  │  │  │  (screens)   │  │  (state)     │               │ │   │
│  │  │  └──────────────┘  └──────────────┘               │ │   │
│  │  │                                                    │ │   │
│  │  │  ┌─────────────────────────────────────────────┐  │ │   │
│  │  │  │           Exercise Components               │  │ │   │
│  │  │  │  Type1 | Type2 | Type3 | Type4 |            │  │ │   │
│  │  │  │  Type5 | Type6 | Type7 | MiniTest           │  │ │   │
│  │  │  └─────────────────────────────────────────────┘  │ │   │
│  │  │                                                    │ │   │
│  │  │  ┌──────────────────────────────────────────────┐ │ │   │
│  │  │  │  Offline Sync Layer (localStorage + queue)   │ │ │   │
│  │  │  └──────────────────────────────────────────────┘ │ │   │
│  │  └────────────────────┬───────────────────────────────┘ │   │
│  │                       │ HTTP/JSON (с заголовком initData) │   │
│  │  ┌────────────────────▼───────────────────────────────┐ │   │
│  │  │              Service Worker (Workbox)              │ │   │
│  │  │  cache-first: JS/CSS, images, audio                │ │   │
│  │  │  network-first: API /progress, /cards/state        │ │   │
│  │  └────────────────────┬───────────────────────────────┘ │   │
│  └───────────────────────┼─────────────────────────────────┘   │
└──────────────────────────┼──────────────────────────────────────┘
                           │ HTTPS
┌──────────────────────────▼──────────────────────────────────────┐
│                         VPS / Server                            │
│                                                                 │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │                   Nginx                                  │  │
│  │  /api/  → proxy → FastAPI :8000                         │  │
│  │  /      → static files (dist/, public/)                 │  │
│  │  /audio/ → static MP3 files                             │  │
│  │  /images/ → static SVG/PNG files                        │  │
│  └─────────────────┬────────────────────────────────────────┘  │
│                    │                                            │
│  ┌─────────────────▼──────────────────────────────────────┐    │
│  │                FastAPI (Uvicorn)                       │    │
│  │                                                        │    │
│  │  ┌─────────────────┐  ┌─────────────────────────────┐ │    │
│  │  │  Auth Middleware │  │     Business Logic          │ │    │
│  │  │  (HMAC verify)  │  │  Progress / XP / Streak /   │ │    │
│  │  └─────────────────┘  │  SM-2 / Placement Test      │ │    │
│  │                       └─────────────────────────────┘ │    │
│  │  ┌──────────────────────────────────────────────────┐  │    │
│  │  │       SQLAlchemy ORM + Alembic migrations        │  │    │
│  │  └──────────────────────┬───────────────────────────┘  │    │
│  └──────────────────────── │ ────────────────────────────┘    │
│                            │                                    │
│  ┌─────────────────────────▼────────────────────────────────┐  │
│  │                     PostgreSQL                           │  │
│  └──────────────────────────────────────────────────────────┘  │
│                                                                 │
│  ┌────────────────────────────────────────────────────────┐    │
│  │         Static Files                                   │    │
│  │  /srv/app/audio/*.mp3   (из Git LFS при деплое)        │    │
│  │  /srv/app/images/**     (из репозитория)               │    │
│  └────────────────────────────────────────────────────────┘    │
└─────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────┐
│                  BATCH PIPELINE (dev machine / CI)              │
│                                                                 │
│  ┌────────────┐    ┌──────────────┐    ┌──────────────────┐    │
│  │ generate_  │    │  validate_   │    │  import_to_db.py │    │
│  │ content.py │───▶│  content.py  │───▶│  (SQLAlchemy)    │    │
│  │            │    │  (schema +   │    │  is_published=F  │    │
│  │            │    │   checks)    │    └──────────────────┘    │
│  └────────────┘    └──────────────┘                            │
│                                                                 │
│  ┌────────────┐    ┌──────────────┐                            │
│  │ generate_  │    │  upload to   │                            │
│  │ audio.py   │───▶│  Git LFS     │                            │
│  │ (gTTS)     │    │              │                            │
│  └────────────┘    └──────────────┘                            │
└─────────────────────────────────────────────────────────────────┘
```

---

## 3. Схема базы данных

### 3.1 Enum-типы

```sql
CREATE TYPE level_enum AS ENUM ('A1', 'A2', 'B1');

CREATE TYPE exercise_type_enum AS ENUM (
    'true_false',          -- Тип 1: ΣΩΣΤΟ / ΛΑΘΟΣ
    'matching',            -- Тип 2: Сопоставление
    'multiple_choice',     -- Тип 3: Выбор из вариантов
    'fill_blank',          -- Тип 4: Заполни пропуск
    'flashcard',           -- Тип 5: Карточки словаря (не входит в завершение юнита)
    'image_description',   -- Тип 6: Περιγραφή εικόνας
    'dialogue'             -- Тип 7: Διάλογος
);

CREATE TYPE card_status_enum AS ENUM ('new', 'learning', 'learned');

CREATE TYPE placement_status_enum AS ENUM ('pending', 'passed', 'failed', 'skipped');
```

### 3.2 Таблицы

#### `users`

```sql
CREATE TABLE users (
    id                      SERIAL          PRIMARY KEY,
    telegram_id             BIGINT          NOT NULL UNIQUE,
    telegram_username       VARCHAR(64),
    telegram_first_name     VARCHAR(128),
    streak_days             INTEGER         NOT NULL DEFAULT 0,
    last_active_date        DATE,                           -- дата последней активности (по timezone пользователя)
    timezone                VARCHAR(64)     DEFAULT 'Europe/Moscow',  -- из Telegram initData, если доступен; иначе Москва
    total_xp                INTEGER         NOT NULL DEFAULT 0,
    placement_status        placement_status_enum NOT NULL DEFAULT 'pending',
    -- 'pending'  = тест ещё не предложен (первый вход)
    -- 'passed'   = прошёл >= 80%, A1 помечен как skipped
    -- 'failed'   = не прошёл, начинает с A1
    -- 'skipped'  = нажал "Пропустить", начинает с A1
    a1_skipped              BOOLEAN         NOT NULL DEFAULT FALSE,
    -- TRUE когда placement_status = 'passed'; A1 ещё доступен для изучения
    show_instruction_translation BOOLEAN   NOT NULL DEFAULT TRUE,
    created_at              TIMESTAMPTZ     NOT NULL DEFAULT NOW(),
    updated_at              TIMESTAMPTZ     NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_users_telegram_id ON users (telegram_id);
```

#### `curriculum_units`

```sql
CREATE TABLE curriculum_units (
    id              SERIAL          PRIMARY KEY,
    level           level_enum      NOT NULL,
    title           VARCHAR(256)    NOT NULL,          -- например "Покупки и магазины"
    description     TEXT,
    order_index     SMALLINT        NOT NULL,          -- порядок отображения внутри уровня
    is_published    BOOLEAN         NOT NULL DEFAULT FALSE,
    created_at      TIMESTAMPTZ     NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_units_level_published ON curriculum_units (level, is_published);
CREATE UNIQUE INDEX idx_units_level_order ON curriculum_units (level, order_index);
```

#### `exercises`

Контент каждого типа упражнения хранится в JSONB-поле `content` согласно схемам, описанным в разделе 3.3.

```sql
CREATE TABLE exercises (
    id              SERIAL              PRIMARY KEY,
    unit_id         INTEGER             NOT NULL REFERENCES curriculum_units(id) ON DELETE CASCADE,
    type            exercise_type_enum  NOT NULL,
    order_index     SMALLINT            NOT NULL,  -- порядок внутри юнита
    content         JSONB               NOT NULL,  -- структура зависит от type
    audio_paths     TEXT[]              NOT NULL DEFAULT '{}',
    -- массив относительных путей ко всем MP3 упражнения
    -- для большинства типов — один элемент: ['/audio/ex_{id}.mp3']
    -- для типа 7 (dialogue) — по одному пути на каждую реплику
    is_published    BOOLEAN             NOT NULL DEFAULT FALSE,
    created_at      TIMESTAMPTZ         NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_exercises_unit_id ON exercises (unit_id);
CREATE INDEX idx_exercises_unit_published ON exercises (unit_id, is_published);
CREATE INDEX idx_exercises_content_gin ON exercises USING GIN (content);
```

#### `vocabulary_cards`

```sql
CREATE TABLE vocabulary_cards (
    id              SERIAL          PRIMARY KEY,
    unit_id         INTEGER         NOT NULL REFERENCES curriculum_units(id) ON DELETE CASCADE,
    word_gr         VARCHAR(256)    NOT NULL,  -- греческое слово / фраза
    word_ru         VARCHAR(256)    NOT NULL,  -- перевод на русский
    example_gr      TEXT,                      -- пример употребления (опционально)
    audio_path      VARCHAR(512),              -- /audio/vocab_{id}.mp3
    order_index     SMALLINT        NOT NULL,
    created_at      TIMESTAMPTZ     NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_vocab_unit_id ON vocabulary_cards (unit_id);
```

#### `placement_test_questions`

```sql
CREATE TABLE placement_test_questions (
    id              SERIAL              PRIMARY KEY,
    type            exercise_type_enum  NOT NULL CHECK (type IN ('true_false', 'multiple_choice', 'fill_blank')),
    content         JSONB               NOT NULL,
    correct_answer  JSONB               NOT NULL,  -- эталонный ответ для автопроверки
    order_index     SMALLINT            NOT NULL,
    is_active       BOOLEAN             NOT NULL DEFAULT TRUE
);
-- Вопросы placement test хранятся отдельно от exercises
-- Случайная выборка 15–20 вопросов из активных
CREATE INDEX idx_placement_active ON placement_test_questions (is_active);
```

#### `user_progress`

```sql
CREATE TABLE user_progress (
    id                          SERIAL          PRIMARY KEY,
    user_id                     INTEGER         NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    unit_id                     INTEGER         NOT NULL REFERENCES curriculum_units(id) ON DELETE CASCADE,
    exercises_completed         INTEGER         NOT NULL DEFAULT 0,
    -- число обязательных упражнений (type != 'flashcard'), помеченных завершёнными
    completed_exercise_ids      INTEGER[]       NOT NULL DEFAULT '{}',
    -- массив id завершённых упражнений для идемпотентной проверки
    mini_test_passed            BOOLEAN         NOT NULL DEFAULT FALSE,
    mini_test_score             SMALLINT,       -- число правильных ответов (0–5)
    unit_completed              BOOLEAN         NOT NULL DEFAULT FALSE,
    unit_completed_at           TIMESTAMPTZ,
    cards_added_to_vocab        BOOLEAN         NOT NULL DEFAULT FALSE,
    -- флаг: карточки юнита добавлены в очередь spaced repetition
    created_at                  TIMESTAMPTZ     NOT NULL DEFAULT NOW(),
    updated_at                  TIMESTAMPTZ     NOT NULL DEFAULT NOW(),
    UNIQUE (user_id, unit_id)
);

CREATE INDEX idx_progress_user_id ON user_progress (user_id);
CREATE INDEX idx_progress_user_unit ON user_progress (user_id, unit_id);
```

#### `user_card_state`

```sql
CREATE TABLE user_card_state (
    id                  SERIAL              PRIMARY KEY,
    user_id             INTEGER             NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    card_id             INTEGER             NOT NULL REFERENCES vocabulary_cards(id) ON DELETE CASCADE,
    status              card_status_enum    NOT NULL DEFAULT 'new',
    interval_days       FLOAT               NOT NULL DEFAULT 1.0,
    easiness_factor     FLOAT               NOT NULL DEFAULT 2.5,  -- SM-2 EF, начальное значение
    repetitions         INTEGER             NOT NULL DEFAULT 0,    -- число успешных повторений подряд
    next_review_at      DATE                NOT NULL DEFAULT CURRENT_DATE,
    last_reviewed_at    TIMESTAMPTZ,
    created_at          TIMESTAMPTZ         NOT NULL DEFAULT NOW(),
    updated_at          TIMESTAMPTZ         NOT NULL DEFAULT NOW(),
    UNIQUE (user_id, card_id)
);

CREATE INDEX idx_card_state_user_id ON user_card_state (user_id);
CREATE INDEX idx_card_state_review ON user_card_state (user_id, next_review_at);
-- Основной индекс для запроса "карточки к повторению сегодня"
CREATE INDEX idx_card_state_due ON user_card_state (user_id, next_review_at)
    WHERE status != 'new';
```

#### `xp_log`

```sql
CREATE TABLE xp_log (
    id          SERIAL          PRIMARY KEY,
    user_id     INTEGER         NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    amount      SMALLINT        NOT NULL,
    reason      VARCHAR(64)     NOT NULL,
    -- 'exercise_complete', 'mini_test', 'card_known', 'streak_bonus'
    ref_id      INTEGER,        -- id упражнения или карточки (опционально)
    created_at  TIMESTAMPTZ     NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_xp_log_user_id ON xp_log (user_id);
```

### 3.3 JSONB-схемы для `exercises.content`

Каждый тип упражнения имеет строго определённую структуру JSONB. Валидация выполняется в Pydantic-моделях на FastAPI.

**Тип 1 — true_false:**
```json
{
  "text": "Η Μαρία πηγαίνει στην αγορά...",
  "statements": [
    { "id": 1, "text": "Η Μαρία αγοράζει φρούτα.", "correct": true },
    { "id": 2, "text": "Η Μαρία είναι στο σπίτι.",  "correct": false }
  ]
}
```

**Тип 2 — matching:**
```json
{
  "pairs": [
    { "id": 1, "left": "Καλημέρα",    "right": "Добрый день" },
    { "id": 2, "left": "Καληνύχτα",   "right": "Спокойной ночи" }
  ]
}
```

**Тип 3 — multiple_choice:**
```json
{
  "question": "Πού είναι η βιβλιοθήκη;",
  "options": [
    { "id": "a", "text": "Στην αγορά" },
    { "id": "b", "text": "Στο κέντρο" },
    { "id": "c", "text": "Στο σπίτι" }
  ],
  "correct_id": "b"
}
```

**Тип 4 — fill_blank:**
```json
{
  "text_template": "Θέλω να ___ ένα εισιτήριο.",
  "blanks": [
    { "position": 0, "correct": "αγοράσω" }
  ],
  "word_bank": ["αγοράσω", "πάω", "έχω"]
}
```

**Тип 5 — flashcard:** хранится в таблице `vocabulary_cards`, не в `exercises`.

**Тип 6 — image_description:**
```json
{
  "description_text": "Η γυναίκα περπατά στην παραλία.",
  "images": [
    { "id": 1, "path": "/images/exercises/beach_walk.svg", "is_correct": true },
    { "id": 2, "path": "/images/exercises/park_bench.svg",  "is_correct": false }
  ]
}
```

**Тип 7 — dialogue:**
```json
{
  "dialogue_lines": [
    { "id": 1, "speaker": "Α", "text": "Πού μένεις;",    "audio_path": "/audio/ex_10_line_1.mp3" },
    { "id": 2, "speaker": "Β", "text": "Μένω στην ___.", "audio_path": "/audio/ex_10_line_2.mp3" }
  ],
  "table_blanks": [
    { "row": "Β", "column": "Πόλη", "correct": "Αθήνα" }
  ],
  "word_bank": ["Αθήνα", "Θεσσαλονίκη", "Πάτρα"]
}
```

> `exercises.audio_paths` для типа 7 содержит все пути реплик:
> `["/audio/ex_10_line_1.mp3", "/audio/ex_10_line_2.mp3"]`
> — Service Worker кэширует по этому полю единообразно для всех типов.
```

### 3.4 Миграции

Миграции управляются через **Alembic**. Структура:

```
backend/
  alembic/
    env.py
    versions/
      0001_initial_schema.py
      0002_add_placement_test.py
      ...
```

Правила:
- Каждое изменение схемы — отдельная версия миграции.
- Миграции применяются при деплое (`alembic upgrade head`).
- Откат через `alembic downgrade -1` должен быть реализован для каждой миграции.

---

## 4. API-контракты

### 4.1 Общие принципы

- **Base URL:** `https://<domain>/api/v1`
- **Аутентификация:** каждый запрос содержит заголовок `X-Telegram-Init-Data: <raw initData string>`. Middleware верифицирует HMAC-SHA256 и извлекает `user_id`.
- **Формат:** JSON (Content-Type: application/json).
- **Ошибки:** стандартная структура `{ "detail": "...", "code": "..." }`.
- **Версионирование:** URL-based (`/api/v1/`). При breaking changes — `/api/v2/`.

### 4.2 Аутентификация / Сессия

#### `POST /api/v1/auth/session`

Создаёт пользователя (если новый) или возвращает существующего. Вызывается при каждом запуске Mini App.

**Headers:** `X-Telegram-Init-Data: <initData>`

**Request body:** нет

**Response 200:**
```json
{
  "user_id": 42,
  "telegram_id": 123456789,
  "streak_days": 5,
  "total_xp": 340,
  "placement_status": "pending",
  "a1_skipped": false,
  "show_instruction_translation": true,
  "is_new_user": true
}
```

**Errors:**
- `401` — невалидная подпись initData
- `422` — отсутствует заголовок

---

### 4.3 Curriculum

#### `GET /api/v1/curriculum/levels`

Возвращает все уровни с процентом завершённых юнитов для текущего пользователя.

**Response 200:**
```json
{
  "levels": [
    {
      "level": "A1",
      "total_units": 7,
      "completed_units": 2,
      "progress_percent": 28
    },
    {
      "level": "A2",
      "total_units": 9,
      "completed_units": 0,
      "progress_percent": 0
    },
    {
      "level": "B1",
      "total_units": 8,
      "completed_units": 0,
      "progress_percent": 0
    }
  ]
}
```

#### `GET /api/v1/curriculum/units?level=A1`

Возвращает все опубликованные юниты уровня с прогрессом пользователя.

**Query params:** `level: A1 | A2 | B1`

**Response 200:**
```json
{
  "units": [
    {
      "id": 1,
      "title": "Приветствия и знакомство",
      "order_index": 1,
      "exercises_total": 5,
      "exercises_completed": 3,
      "mini_test_passed": false,
      "unit_completed": false
    }
  ]
}
```

#### `GET /api/v1/curriculum/units/{unit_id}`

Полный контент юнита: список упражнений (без содержимого, только метаданные) и список карточек словаря.

**Response 200:**
```json
{
  "id": 1,
  "title": "Приветствия и знакомство",
  "level": "A1",
  "exercises": [
    {
      "id": 10,
      "type": "true_false",
      "order_index": 1,
      "audio_path": "/audio/ex_10.mp3",
      "completed": false
    }
  ],
  "vocabulary_cards": [
    {
      "id": 55,
      "word_gr": "καλημέρα",
      "word_ru": "добрый день",
      "audio_path": "/audio/vocab_55.mp3"
    }
  ]
}
```

**Errors:**
- `404` — юнит не найден или не опубликован

---

### 4.4 Упражнения

#### `GET /api/v1/exercises/{exercise_id}`

Полный контент упражнения.

**Response 200:**
```json
{
  "id": 10,
  "unit_id": 1,
  "type": "true_false",
  "content": { ... },
  "audio_path": "/audio/ex_10.mp3"
}
```

**Errors:**
- `404` — упражнение не найдено или не опубликовано

#### `POST /api/v1/exercises/{exercise_id}/complete`

Отмечает упражнение завершённым, начисляет XP, обновляет streak.

**Request body:**
```json
{
  "score": 4,
  "total": 5
}
```

**Response 200:**
```json
{
  "xp_earned": 15,
  "xp_breakdown": {
    "exercise_complete": 10,
    "streak_bonus": 5
  },
  "streak_days": 6,
  "streak_updated": true,
  "unit_progress": {
    "exercises_completed": 4,
    "exercises_total": 5,
    "mini_test_unlocked": false
  }
}
```

**Errors:**
- `404` — упражнение не найдено
- `409` — упражнение уже завершено (идемпотентный ответ, повторная попытка не начисляет XP)

---

### 4.5 Мини-тест юнита

#### `GET /api/v1/units/{unit_id}/mini-test`

Возвращает 5 вопросов случайной выборки для мини-теста юнита (типы 1, 3, 4).

**Response 200:**
```json
{
  "questions": [
    {
      "id": 201,
      "type": "multiple_choice",
      "content": { ... }
    }
  ]
}
```

**Errors:**
- `403` — не все обязательные упражнения завершены
- `404` — юнит не найден

#### `POST /api/v1/units/{unit_id}/mini-test/complete`

**Request body:**
```json
{
  "score": 4,
  "total": 5
}
```

**Response 200:**
```json
{
  "unit_completed": true,
  "xp_earned": 25,
  "cards_added_to_vocab": 18
}
```

**Errors:**
- `403` — не все обязательные упражнения завершены
- `409` — мини-тест уже пройден

---

### 4.6 Словарь / Spaced Repetition

#### `GET /api/v1/vocabulary/due`

Карточки, запланированные к повторению сегодня.

**Response 200:**
```json
{
  "due_count": 12,
  "cards": [
    {
      "id": 55,
      "word_gr": "καλημέρα",
      "word_ru": "добрый день",
      "audio_path": "/audio/vocab_55.mp3",
      "status": "learning",
      "next_review_at": "2026-04-06"
    }
  ]
}
```

#### `POST /api/v1/vocabulary/cards/{card_id}/review`

Обновляет состояние SM-2 по результату ревью.

**Request body:**
```json
{
  "known": true
}
```

**Response 200:**
```json
{
  "card_id": 55,
  "new_status": "learning",
  "next_review_at": "2026-04-09",
  "interval_days": 3.0,
  "xp_earned": 2
}
```

#### `GET /api/v1/vocabulary/stats`

Статистика словаря пользователя.

**Response 200:**
```json
{
  "total_cards": 85,
  "learned_count": 34,
  "due_today": 12,
  "new_count": 20
}
```

---

### 4.7 Placement Test

#### `GET /api/v1/placement-test/questions`

Возвращает случайную выборку 15–20 вопросов.

**Response 200:**
```json
{
  "questions": [
    {
      "id": 1,
      "type": "multiple_choice",
      "content": { ... }
    }
  ]
}
```

**Errors:**
- `403` — placement test уже пройден или пропущен

#### `POST /api/v1/placement-test/complete`

**Request body:**
```json
{
  "score": 17,
  "total": 20,
  "skipped": false
}
```

**Response 200:**
```json
{
  "placement_status": "passed",
  "a1_skipped": true,
  "message": "Поздравляем! A1 пропущен, начинаете с A2."
}
```

**Errors:**
- `403` — placement test уже был завершён/пропущен
- `409` — повторная попытка недопустима

---

### 4.8 Прогресс (bulk sync для offline)

#### `POST /api/v1/sync/progress`

Массовая синхронизация прогресса после offline-сессии. Тело — список событий с timestamp.

**Request body:**
```json
{
  "events": [
    {
      "type": "exercise_complete",
      "exercise_id": 10,
      "score": 4,
      "total": 5,
      "occurred_at": "2026-04-06T10:15:00Z"
    },
    {
      "type": "card_review",
      "card_id": 55,
      "known": true,
      "occurred_at": "2026-04-06T10:16:00Z"
    }
  ]
}
```

**Response 200:**
```json
{
  "processed": 2,
  "skipped": 0,
  "xp_total_earned": 17,
  "conflicts": []
}
```

**Стратегия конфликтов:** если событие `exercise_complete` для уже завершённого упражнения — пропускается (идемпотентно). XP за дубликат не начисляется.

---

### 4.9 Настройки

#### `PATCH /api/v1/settings`

**Request body:**
```json
{
  "show_instruction_translation": false
}
```

**Response 200:**
```json
{
  "show_instruction_translation": false
}
```

---

## 5. Frontend-архитектура

### 5.1 Структура директорий

```
frontend/
├── public/
│   ├── images/
│   │   └── exercises/         # SVG/PNG для типа 6
│   └── audio/                 # MP3-файлы (symlink или копия из Git LFS)
├── src/
│   ├── api/                   # HTTP-клиент и типы
│   │   ├── client.ts          # axios/fetch-обёртка с X-Telegram-Init-Data
│   │   ├── auth.ts
│   │   ├── curriculum.ts
│   │   ├── exercises.ts
│   │   ├── vocabulary.ts
│   │   └── sync.ts
│   ├── components/
│   │   ├── exercises/
│   │   │   ├── TrueFalse/
│   │   │   ├── Matching/
│   │   │   ├── MultipleChoice/
│   │   │   ├── FillBlank/
│   │   │   ├── Flashcard/
│   │   │   ├── ImageDescription/
│   │   │   └── Dialogue/
│   │   ├── ui/                # переиспользуемые примитивы
│   │   │   ├── Button.tsx
│   │   │   ├── Card.tsx
│   │   │   ├── AudioPlayer.tsx
│   │   │   ├── ProgressBar.tsx
│   │   │   └── Badge.tsx
│   │   └── layout/
│   │       ├── AppShell.tsx   # шапка со streak и XP
│   │       └── BottomNav.tsx  # вкладки Учёба / Словарь
│   ├── screens/               # экраны = страницы роутера
│   │   ├── Onboarding/
│   │   │   └── PlacementTest.tsx
│   │   ├── Study/
│   │   │   ├── LevelMap.tsx
│   │   │   ├── UnitDetail.tsx
│   │   │   └── ExerciseRunner.tsx
│   │   ├── Vocabulary/
│   │   │   ├── VocabHome.tsx
│   │   │   └── ReviewSession.tsx
│   │   ├── Profile.tsx
│   │   └── Settings.tsx
│   ├── store/                 # Zustand stores
│   │   ├── userStore.ts       # streak, XP, settings
│   │   ├── curriculumStore.ts # units, exercises (закэшированные)
│   │   ├── vocabStore.ts      # due cards, stats
│   │   └── offlineQueue.ts    # очередь событий для sync
│   ├── hooks/
│   │   ├── useTelegramInit.ts # читает window.Telegram.WebApp
│   │   ├── useAudio.ts        # управление воспроизведением
│   │   ├── useOfflineSync.ts  # отправка offline-очереди при reconnect
│   │   └── useStreak.ts
│   ├── lib/
│   │   ├── sm2.ts             # алгоритм SM-2 (client-side preview)
│   │   ├── xp.ts              # константы начисления XP
│   │   └── initData.ts        # парсинг и передача initData
│   ├── sw/
│   │   └── service-worker.ts  # Workbox конфиг
│   ├── App.tsx
│   ├── router.tsx
│   └── main.tsx
├── vite.config.ts
└── package.json
```

### 5.2 Роутинг

Роутер: **React Router v6** (HashRouter для совместимости с Telegram Mini App WebView, где история нестандартна).

```
/                         → redirect → /study  (или /onboarding если is_new_user)
/onboarding               → PlacementTest (показывается один раз)
/study                    → LevelMap
/study/units/:unitId      → UnitDetail
/study/units/:unitId/exercises/:exerciseId  → ExerciseRunner
/study/units/:unitId/mini-test              → MiniTest (ExerciseRunner в режиме теста)
/vocabulary               → VocabHome
/vocabulary/review        → ReviewSession
/profile                  → Profile
/settings                 → Settings
```

**Guard:** `OnboardingGuard` — если `placement_status === 'pending'` и это первый визит, редиректит на `/onboarding`.

### 5.3 Управление состоянием

Выбор: **Zustand** (ADR-04).

| Store | Что хранит | Персистентность |
|-------|-----------|----------------|
| `userStore` | `userId`, `streakDays`, `totalXp`, `settings` | localStorage (zustand-persist) |
| `curriculumStore` | `levels[]`, `units[]`, кэш упражнений по `unitId` | in-memory + IndexedDB (через idb-keyval) |
| `vocabStore` | `dueCards[]`, `stats` | in-memory |
| `offlineQueue` | массив событий, ожидающих синхронизации | localStorage |

Персистентность `curriculumStore` через IndexedDB — для хранения больших JSONB-объектов упражнений без ограничений localStorage.

**Fallback при недоступности IndexedDB** (Telegram WebView на некоторых устройствах):

```typescript
// store/curriculumStore.ts
async function persistCurriculum(data: CurriculumState): Promise<void> {
  try {
    await idbSet('curriculum', data);
  } catch {
    // IndexedDB недоступна (приватный режим / WebView ограничение)
    const json = JSON.stringify(data);
    if (json.length < 4_000_000) {  // localStorage лимит ~5 MB
      localStorage.setItem('curriculum_fallback', json);
    }
    // если данные слишком большие — работаем только in-memory до следующего запуска
  }
}
```

При инициализации store: сначала пробуем idb, при ошибке — `localStorage.getItem('curriculum_fallback')`.

### 5.4 Telegram SDK интеграция

```typescript
// src/hooks/useTelegramInit.ts
// Читает window.Telegram.WebApp.initData
// Передаёт как X-Telegram-Init-Data в каждый HTTP-запрос
// Вызывает WebApp.ready() при монтировании AppShell
```

Telegram WebApp SDK подключается через `@twa-dev/sdk` (типизированная обёртка).

---

## 6. Offline-архитектура

### 6.1 Service Worker

Реализация: **Workbox** через плагин `vite-plugin-pwa`.

#### Стратегии кэширования по типу ресурса

| Ресурс | Стратегия | Кэш | Пояснение |
|--------|-----------|-----|-----------|
| `dist/` — JS, CSS бандл | **CacheFirst** | `static-v{hash}` | Обновляется при новом деплое через versioned filenames |
| `public/images/**` | **CacheFirst** | `images-v1` | SVG/PNG изображения упражнений; долгоживущие |
| `/audio/*.mp3` | **CacheFirst** | `audio-v1` | MP3-файлы; кэшируются по запросу (lazy), не precache |
| `GET /api/v1/curriculum/**` | **NetworkFirst** | `api-curriculum` | Контент юнитов; stale-if-offline |
| `GET /api/v1/vocabulary/due` | **NetworkFirst** | `api-vocab` | Карточки на сегодня; нужна актуальность |
| `POST /api/v1/exercises/*/complete` | **Background sync** | очередь | При offline — в offlineQueue, отправляется при reconnect |
| `POST /api/v1/vocabulary/cards/*/review` | **Background sync** | очередь | Аналогично |
| `POST /api/v1/sync/progress` | **NetworkFirst** | нет | Синхронизация очереди |

#### Precaching

При сборке (`vite build`) Workbox генерирует precache-манифест для:
- Всех ассетов из `dist/`
- Всех файлов из `public/images/exercises/`

Аудио-файлы **не precache** — слишком большой объём. Кэшируются при первом запросе.

#### Стратегия обновления SW

`skipWaiting: false` + UI-подсказка "Доступно обновление — перезагрузить?" при обнаружении нового SW. Обновление не принудительное, чтобы не прерывать сессию.

### 6.2 Синхронизация прогресса

#### Offline-очередь

При недоступности сети события прогресса помещаются в `offlineQueue` (Zustand store → localStorage).

Структура события в очереди:
```typescript
interface OfflineEvent {
  id: string;              // uuid для идемпотентности
  type: 'exercise_complete' | 'card_review' | 'mini_test_complete';
  payload: Record<string, unknown>;
  occurred_at: string;     // ISO 8601
  retries: number;
}
```

#### Механизм синхронизации

1. `useOfflineSync` hook подписывается на `online` событие браузера.
2. При восстановлении соединения: вызов `POST /api/v1/sync/progress` с пакетом событий.
3. Сервер обрабатывает события в хронологическом порядке по `occurred_at`.
4. Идемпотентность на сервере: повторная обработка события с тем же `exercise_id` для уже завершённого упражнения — пропускается, XP не дублируется.

#### Разрешение конфликтов (NFR-OFFLINE-04)

Стратегия: **"more-complete wins"**.

- Если упражнение уже завершено на сервере — offline-событие пропускается.
- Если карточка отрецензирована онлайн позже, чем offline-событие — берётся наиболее поздний `updated_at`.
- Streak: пересчитывается на сервере на основе хронологического журнала событий в `xp_log`.

#### Визуальная индикация offline

В `AppShell` показывается баннер "Офлайн-режим. Прогресс сохранится" при `navigator.onLine === false`. Баннер исчезает при восстановлении сети.

---

## 7. Аутентификация

### 7.1 Детальный флоу

```
Telegram Client                  FastAPI                     PostgreSQL
     │                              │                              │
     │  1. Telegram.WebApp.initData │                              │
     │     передаётся при запуске   │                              │
     │                              │                              │
     │  2. POST /api/v1/auth/session│                              │
     │     Header: X-Telegram-Init- │                              │
     │     Data: <raw string>       │                              │
     │─────────────────────────────▶│                              │
     │                              │                              │
     │                              │  3. AuthMiddleware:          │
     │                              │     parse initData           │
     │                              │     строит data-check-string │
     │                              │     HMAC-SHA256(             │
     │                              │       key=HMAC("WebAppData", │
     │                              │         BOT_TOKEN),          │
     │                              │       data=check_string)     │
     │                              │     сравнивает с hash=       │
     │                              │     из initData              │
     │                              │                              │
     │                              │  4. Если HMAC невалиден:     │
     │◀─────────────────────────────│     HTTP 401                 │
     │                              │                              │
     │                              │  5. Извлекает telegram_id    │
     │                              │     из user JSON в initData  │
     │                              │                              │
     │                              │  6. SELECT * FROM users      │
     │                              │     WHERE telegram_id = ...  │
     │                              │─────────────────────────────▶│
     │                              │                              │
     │                              │  7. Если пользователь новый: │
     │                              │     INSERT INTO users(...)   │
     │                              │     is_new_user = True       │
     │                              │─────────────────────────────▶│
     │                              │                              │
     │                              │  8. Возврат user объекта     │
     │                              │◀─────────────────────────────│
     │                              │                              │
     │  9. HTTP 200 + user data     │                              │
     │◀─────────────────────────────│                              │
     │                              │                              │
     │  10. Последующие запросы:    │                              │
     │      тот же заголовок        │                              │
     │      X-Telegram-Init-Data    │                              │
     │      на каждый запрос        │                              │
```

### 7.2 Реализация HMAC-верификации

```python
# backend/app/middleware/auth.py
import hmac, hashlib, json
from urllib.parse import parse_qsl

def verify_telegram_init_data(init_data: str, bot_token: str) -> dict:
    """
    Верифицирует initData согласно документации Telegram Bot API.
    Возвращает распарсенный user dict или бросает ValueError.
    """
    params = dict(parse_qsl(init_data, keep_blank_values=True))
    received_hash = params.pop("hash", None)
    if not received_hash:
        raise ValueError("Missing hash")

    # Строим data-check-string: отсортированные пары key=value через \n
    data_check_string = "\n".join(
        f"{k}={v}" for k, v in sorted(params.items())
    )

    # Секретный ключ: HMAC-SHA256("WebAppData", bot_token)
    secret_key = hmac.new(
        b"WebAppData", bot_token.encode(), hashlib.sha256
    ).digest()

    # Проверка
    expected_hash = hmac.new(
        secret_key, data_check_string.encode(), hashlib.sha256
    ).hexdigest()

    if not hmac.compare_digest(expected_hash, received_hash):
        raise ValueError("Invalid hash")

    return json.loads(params.get("user", "{}"))
```

### 7.3 Отсутствие JWT

Сессия не нужна — каждый запрос верифицируется заново через `initData`. Это соответствует модели Telegram Mini App: клиент всегда имеет актуальный `initData` от Telegram.

**Почему не JWT:** initData уже выполняет роль токена (подписан Telegram). Добавление JWT — лишний уровень сложности без выгоды для данного масштаба (ADR-02).

### 7.4 Срок действия initData

Telegram гарантирует актуальность `initData` в течение сессии Mini App. Поле `auth_date` в initData содержит Unix timestamp выпуска. Рекомендуется проверять: `now - auth_date < 86400` (24 часа). Старые токены отклоняются.

### 7.5 Защита от IDOR

Middleware извлекает `telegram_id` из верифицированного `initData` и передаёт его как `current_user_id` в контекст запроса. Все write-операции в handlers явно проверяют, что `resource.user_id == current_user_id`.

---

## 8. Batch-пайплайн

### 8.1 Архитектура пайплайна генерации контента

```
scripts/
├── generate_content.py      # генерирует упражнения
├── validate_content.py      # валидирует JSON-схемы + семантические проверки
├── import_content.py        # импортирует в PostgreSQL (is_published=False)
├── publish_content.py       # SET is_published=True после ручного просмотра
├── generate_audio.py        # генерирует MP3 через gTTS
├── prompts/
│   ├── true_false.txt
│   ├── matching.txt
│   ├── multiple_choice.txt
│   ├── fill_blank.txt
│   ├── image_description.txt
│   └── dialogue.txt
└── schemas/
    ├── exercise_schemas.py  # Pydantic-модели для валидации JSONB
    └── unit_schema.py
```

### 8.2 Флоу генерации контента

```
1. Подготовка промпта
   └── prompts/<type>.txt + unit_context (тема, уровень, целевой словарь)
       └── generate_content.py
           └── Получение JSON-ответа

2. Валидация
   └── validate_content.py
       ├── Pydantic-валидация структуры (schemas/exercise_schemas.py)
       ├── Проверка наличия обязательных полей
       └── Семантические проверки:
           └── языковая корректность, соответствие A2-уровню,
               наличие правильных ответов, отсутствие дублей

3. Импорт в БД
   └── import_content.py
       ├── SQLAlchemy INSERT с is_published=False
       └── Логирует import_id для последующего publish

4. Ручной просмотр
   └── scripts/review_content.py  # выводит контент в терминале для проверки
       └── (или прямой SQL: SELECT * FROM exercises WHERE is_published=False)

5. Публикация
   └── publish_content.py --unit-id <id>
       └── UPDATE exercises SET is_published=True WHERE unit_id=<id>
```

### 8.3 Структура промпта (пример для типа 3)

```
# prompts/multiple_choice.txt

Ты составляешь упражнение для изучающих новогреческий язык (уровень {level}).

Тема юнита: {unit_topic}
Целевой словарь: {vocabulary_list}

Создай {count} вопросов типа "выбор из вариантов" (α/β/γ/δ).

Требования:
- Вопросы соответствуют уровню {level}
- Все слова из целевого словаря юнита или базовой лексики
- Один правильный ответ, три правдоподобных неправильных
- Ответ в формате JSON согласно схеме:
  {"question": "...", "options": [{"id": "a", "text": "..."},...], "correct_id": "a"}

Верни массив JSON без дополнительного текста.
```

### 8.4 gTTS Аудио-пайплайн

```python
# scripts/generate_audio.py
from gtts import gTTS
import pathlib, hashlib

def generate_audio(text: str, dest_dir: pathlib.Path) -> str:
    """
    Генерирует MP3 через gTTS (греческий язык, lang='el').
    Имя файла = SHA-256(text)[:12].mp3 для идемпотентности.
    Возвращает относительный путь /audio/<filename>.mp3
    """
    filename = hashlib.sha256(text.encode()).hexdigest()[:12] + ".mp3"
    dest = dest_dir / filename
    if not dest.exists():
        tts = gTTS(text=text, lang="el", slow=False)
        tts.save(str(dest))
    return f"/audio/{filename}"
```

**Что озвучивается:**
- Тексты упражнений типов 1, 3, 4, 6: один MP3 → `exercises.audio_paths = ['/audio/ex_{id}.mp3']`
- Реплики диалога тип 7: по одному MP3 на реплику → `exercises.audio_paths = ['/audio/ex_{id}_line_1.mp3', ...]`, пути также дублируются в `content.dialogue_lines[i].audio_path` для порядка воспроизведения
- Каждое слово из `vocabulary_cards.audio_path` (у vocab отдельная колонка — одна карточка = один файл)

**Хранение:** файлы `audio/*.mp3` трекаются через Git LFS (`.gitattributes: *.mp3 filter=lfs diff=lfs merge=lfs -text`).

**Деплой:** `git lfs pull` на сервере при деплое копирует файлы в `/srv/app/audio/`. Nginx отдаёт их как статику.

### 8.5 Управление версиями контента

- Каждый запуск `generate_content.py` логирует `generation_run_id` (UUID) в отдельную таблицу `generation_runs`.
- При необходимости откатить батч: `UPDATE exercises SET is_published=FALSE WHERE generation_run_id=<id>`.

---

## 9. Деплой и инфраструктура

### 9.1 Целевая инфраструктура

Выбор: **одиночный VPS** (Hetzner CX21 или аналог — 2 vCPU, 4 GB RAM, 40 GB SSD). Обоснование: ADR-05.

Стоимость: ~4–6 EUR/месяц. Достаточно для 50 одновременных пользователей (NFR-PERF-04).

### 9.2 Docker Compose

```yaml
# docker-compose.yml
version: "3.9"
services:
  postgres:
    image: postgres:16-alpine
    environment:
      POSTGRES_DB: greekapp
      POSTGRES_USER: greekapp
      POSTGRES_PASSWORD: ${POSTGRES_PASSWORD}
    volumes:
      - postgres_data:/var/lib/postgresql/data
    restart: unless-stopped

  backend:
    build: ./backend
    environment:
      DATABASE_URL: postgresql+asyncpg://greekapp:${POSTGRES_PASSWORD}@postgres/greekapp
      BOT_TOKEN: ${BOT_TOKEN}
      CORS_ORIGINS: ${CORS_ORIGINS}
    depends_on:
      - postgres
    restart: unless-stopped

  nginx:
    image: nginx:alpine
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf:ro
      - ./frontend/dist:/srv/app/dist:ro
      - ./frontend/public:/srv/app/public:ro
      - /srv/app/audio:/srv/app/audio:ro   # MP3-файлы из Git LFS
      - /etc/letsencrypt:/etc/letsencrypt:ro
    ports:
      - "80:80"
      - "443:443"
    depends_on:
      - backend
    restart: unless-stopped

volumes:
  postgres_data:
```

### 9.3 Nginx конфигурация

```nginx
server {
    listen 443 ssl;
    server_name <domain>;

    ssl_certificate /etc/letsencrypt/live/<domain>/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/<domain>/privkey.pem;

    # API
    location /api/ {
        proxy_pass http://backend:8000;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    }

    # Аудио (cache-heavy статика)
    location /audio/ {
        root /srv/app/public;
        expires 365d;
        add_header Cache-Control "public, immutable";
    }

    # Изображения
    location /images/ {
        root /srv/app/public;
        expires 365d;
        add_header Cache-Control "public, immutable";
    }

    # SPA (React)
    location / {
        root /srv/app/dist;
        try_files $uri $uri/ /index.html;
        expires 1h;
    }
}

server {
    listen 80;
    server_name <domain>;
    return 301 https://$host$request_uri;
}
```

### 9.4 Деплой-скрипт

```bash
#!/bin/bash
# deploy.sh

set -e

# 1. Забрать новый код
git pull origin main
git lfs pull   # скачать новые MP3-файлы

# 2. Собрать фронтенд
cd frontend
npm ci
npm run build
cd ..

# 3. Применить миграции
docker compose exec backend alembic upgrade head

# 4. Перезапустить backend
docker compose up -d --no-deps backend

# 5. Перезагрузить Nginx (новый dist/)
docker compose exec nginx nginx -s reload
```

### 9.5 Переменные окружения

```
BOT_TOKEN=          # токен Telegram-бота (secret)
POSTGRES_PASSWORD=  # пароль PostgreSQL (secret)
CORS_ORIGINS=       # https://web.telegram.org,https://t.me
DATABASE_URL=       # postgresql+asyncpg://...
ENVIRONMENT=        # production | development
```

Секреты хранятся в `.env` файле на сервере, не в репозитории. `.gitignore` содержит `.env`.

### 9.6 SSL

Certbot + Let's Encrypt. Авторебью через cron: `0 0 * * * certbot renew --quiet`.

### 9.7 Мониторинг и логи

- **Логи:** stdout → `docker compose logs`. Для продакшна — ротация через `logrotate`.
- **Health check:** `GET /api/v1/health` → `200 OK { "status": "ok" }` (добавляется в Nginx upstream checks).
- **Ошибки 5xx:** логируются с трейсбеком. При превышении порога 1% (NFR-REL-01) — алерт через Telegram-бота (опционально, не в скоупе v1).

---

## 10. Architecture Decision Records

### ADR-01: JSONB для контента упражнений вместо нормализованных таблиц

**Контекст:** Каждый из 7 типов упражнений имеет принципиально разную структуру данных.

**Решение:** Хранить содержимое упражнения в поле `exercises.content JSONB`.

**Аргументы за:**
- Избегаем 7 отдельных таблиц или сложной EAV-схемы.
- Структура контента гибко меняется при добавлении новых типов.
- PostgreSQL поддерживает GIN-индексы на JSONB для поиска.
- Pydantic-модели в FastAPI обеспечивают типобезопасность на уровне приложения.

**Аргументы против:**
- Нет foreign key на поля внутри JSON.
- Сложнее писать SQL-миграции при изменении схемы содержимого.

**Смягчение:** JSON-схемы документированы в этом RFC (раздел 3.3). Pydantic-валидация на уровне API — обязательна.

---

### ADR-02: Нет JWT — initData на каждом запросе

**Контекст:** Нужна аутентификация пользователя.

**Решение:** Передавать `initData` в заголовке каждого запроса, верифицировать HMAC на сервере.

**Аргументы за:**
- Telegram уже подписал `initData` — это готовый токен.
- Нет необходимости в refresh token логике.
- Нет дополнительного хранилища сессий.
- Проще реализация — меньше поверхность атаки.

**Аргументы против:**
- HMAC-верификация на каждый запрос — небольшие CPU-расходы (незначимо для данного масштаба).
- Нельзя инвалидировать сессию принудительно (не требуется в данном продукте).

---

### ADR-03: Хранение аудио в Git LFS + статика, не в S3/CDN

**Контекст:** MP3-файлы для всех упражнений и карточек (~сотни файлов).

**Решение:** Git LFS для версионирования; при деплое файлы копируются на VPS; Nginx отдаёт как статику.

**Аргументы за:**
- Нет операционных расходов на S3.
- Простота: `git lfs pull` в deploy-скрипте.
- Файлы кэшируются Service Worker — offline работает.

**Аргументы против:**
- При росте до тысяч файлов потребуется миграция на объектное хранилище.
- Деплой занимает больше времени при большом объёме LFS.

**Оценка объёма по уровням:**
- A2 (MVP): ~9 юнитов × (6 упражнений + 20 карточек) ≈ **234 файла** — ок для Git LFS.
- Все три уровня (A1 + A2 + B1): ≈ **700 файлов** — выше порога.

**Порог переоценки:** при добавлении второго уровня (A1 или B1) → мигрировать на **Backblaze B2** (совместим с S3 API, дешевле AWS). Git LFS остаётся для development-окружения.

---

### ADR-04: Zustand для управления состоянием вместо Redux / Jotai / Context

**Контекст:** Frontend нуждается в глобальном состоянии: пользователь, прогресс, offline-очередь.

**Решение:** **Zustand**.

**Аргументы за:**
- Минимальный boilerplate по сравнению с Redux.
- Встроенная поддержка persist middleware для localStorage/IndexedDB.
- Простая интеграция с React DevTools.
- Хорошо работает с TypeScript.
- Достаточно для масштаба приложения.

**Jotai не выбран:** атомарная модель избыточна для данной структуры состояния.
**Context не выбран:** провоцирует ненужные ре-рендеры при частых обновлениях (streak, XP).

---

### ADR-05: VPS вместо PaaS (Railway / Render)

**Контекст:** Выбор хостинга для бесплатного pet-проекта.

**Решение:** **Hetzner VPS CX21** (~5 EUR/месяц).

**Аргументы за:**
- Полный контроль над конфигурацией Nginx (важно для отдачи статики, аудио, offline-кэширования).
- Нет ограничений PaaS на статические файлы большого объёма (аудио Git LFS).
- Портфолио-ценность: демонстрирует знание DevOps.
- Предсказуемая стоимость.

**Railway/Render не выбраны:** ограничения на persistentные тома и Git LFS создали бы операционные проблемы.

---

### ADR-06: SM-2 вычисляется на сервере, клиент только отправляет результат

**Контекст:** Алгоритм spaced repetition может работать и на клиенте, и на сервере.

**Решение:** Вычисление SM-2 (новый `interval_days`, `easiness_factor`, `next_review_at`) выполняется в FastAPI при обработке `POST /vocabulary/cards/{id}/review`.

**Аргументы за:**
- Единый источник истины: состояние SM-2 всегда консистентно в БД.
- Offline-ревью: клиент хранит `{ known: true/false }` в очереди; при синхронизации сервер пересчитывает SM-2 с учётом реального `occurred_at`.
- Проще тестировать алгоритм изолированно.

**Смягчение для offline UX:** клиент показывает оптимистичный результат сразу (без ожидания подтверждения сервера). При синхронизации данные обновляются.

---

### ADR-07: HashRouter вместо BrowserRouter для Telegram Mini App

**Контекст:** Telegram Mini App WebView имеет ограниченную поддержку History API.

**Решение:** React Router с `createHashRouter` (`/#/study`, `/#/vocabulary` и т.д.).

**Аргументы за:**
- Избегает проблем с deep-link навигацией в WebView.
- Nginx не требует специальной конфигурации для hash-роутов.

**Аргументы против:** URL менее читабельны (несущественно — ссылки на конкретные экраны не шарятся).

---

## Исполнительные слайсы (execution slices)

| # | Слайс | Содержание | Зависимости |
|---|-------|-----------|-------------|
| S-1 | **Инфраструктура** | VPS, Docker Compose, Nginx, PostgreSQL, SSL | — |
| S-2 | **Схема БД + миграции** | Alembic, все таблицы из раздела 3 | S-1 |
| S-3 | **FastAPI скелет** | Auth middleware, `POST /auth/session`, health check | S-2 |
| S-4 | **Batch-пайплайн контент** | `generate_content.py` + `import_content.py` для 1–2 юнитов A1 | S-2 |
| S-5 | **Batch-пайплайн аудио** | `generate_audio.py` + Git LFS setup | S-4 |
| S-6 | **API curriculum** | `GET /curriculum/levels`, `/units`, `/units/:id` | S-3, S-4 |
| S-7 | **Frontend скелет** | Vite setup, Zustand, Router, useTelegramInit | — |
| S-8 | **Типы упражнений 1–4** | Компоненты + `POST /exercises/:id/complete` | S-6, S-7 |
| S-9 | **Тип 5 — Flashcard** | Компонент карточки, flip-анимация | S-7 |
| S-10 | **Тип 6 — Image Description** | Компонент + AudioPlayer autoplay | S-7, S-5 |
| S-11 | **Тип 7 — Dialogue** | Компонент диалога | S-7 |
| S-12 | **Мини-тест** | `GET /units/:id/mini-test` + `POST /complete` | S-8 |
| S-13 | **Spaced Repetition** | `user_card_state`, SM-2 логика, `/vocabulary/**` API | S-3 |
| S-14 | **Раздел "Словарь" (UI)** | ReviewSession, VocabHome, бейдж | S-13, S-9 |
| S-15 | **Геймификация** | Streak, XP, xp_log | S-8 |
| S-16 | **Placement Test** | API + UI | S-3, S-6 |
| S-17 | **Service Worker + Offline** | Workbox config, offlineQueue, `POST /sync/progress` | S-7, S-8 |
| S-18 | **Настройки** | `PATCH /settings`, переключатель инструкций | S-3, S-7 |
| S-19 | **Profil + финальный UI polish** | ProfileScreen, AppShell, BottomNav, a11y | S-15 |

---

## Технические риски

| Риск | Вероятность | Влияние | Митигация |
|------|-------------|---------|-----------|
| Telegram изменит формат `initData` | Низкая | Высокое (аутентификация сломается) | Следить за Telegram Bot API changelog; изолировать верификацию в одном модуле |
| gTTS даёт неприемлемое качество для некоторых слов | Средняя | Среднее (UX аудио) | Проверить качество на 50+ словах до начала массовой генерации; при необходимости — ручная запись для ключевых слов |
| Git LFS окажется неудобен при большом объёме аудио | Средняя | Низкое (только DevOps) | ADR-03: порог переоценки 500 файлов / 1 GB |
| Service Worker кэш устаревает после деплоя контента | Средняя | Среднее (пользователь видит старый контент) | Versioned asset names в Vite; кэш `api-curriculum` — NetworkFirst с stale fallback |
| IndexedDB ограничения в Telegram WebView | Средняя | Среднее (offline не работает) | Тест на реальных устройствах на ранней стадии; fallback на localStorage для curriculumStore |
| JSONB миграции при изменении структуры упражнений | Средняя | Среднее (сложность миграций) | Документировать версии схем; добавлять поля только аддитивно; Pydantic-валидация на входе |
| Telegram Mini App WebView не поддерживает Background Sync API | Высокая | Низкое (offline sync) | Fallback: `useOfflineSync` через `online` event без Background Sync API |

---

## Открытые вопросы

1. **Блокировка уровней A2/B1:** PRD (FR-STUDY-03) упоминает, что A2/B1 "ещё недоступны" без завершения предыдущего уровня, но тут же оговорка о том, что логика не окончательна. Решение нужно принять до реализации `GET /curriculum/levels`. **Предложение:** уровни не блокируют — только информационный прогресс-бар, как указано в брифе.

2. **Порог "learned" в SM-2:** PRD (FR-VOCAB-05) говорит "интервал ≥ 7 дней или иной порог — уточняется". Нужно зафиксировать перед реализацией `user_card_state`. **Предложение:** `interval_days >= 7` → статус `learned`.

3. **Timezone для streak:** если Telegram не передаёт timezone пользователя в `initData` (на практике — не передаёт), нужен fallback. **Предложение:** UTC + документировать это ограничение пользователю.

4. **Placement test вопросы:** вопросы берутся из `placement_test_questions` (отдельная таблица) или из `exercises` уровня A1? Отдельная таблица предпочтительна для независимости от публикации упражнений.

---

## Следующий gate

- Подтверждение открытых вопросов 1–4 у продакт-оунера перед переходом к реализации.
- Code review схемы БД и API-контрактов перед S-2.
- Smoke-test gTTS на 20–30 греческих словах перед массовой генерацией аудио (S-5).
