# Greek Learning App

Telegram Mini App для изучения новогреческого языка (A1–B1) с фокусом на подготовку к экзамену ΠΙΣΤΟΠΟΙΗΣΗ ΕΛΛΗΝΟΜΑΘΕΙΑΣ A2.

## Стек

| Слой | Технологии |
|------|-----------|
| Frontend | React 18 + Vite + TypeScript, TanStack Query v5, Zustand, CSS Modules |
| Backend | FastAPI (Python 3.12), SQLAlchemy 2.0 async, PostgreSQL, Alembic |
| Pipeline | Python 3.12, Claude API (Anthropic), gTTS, psycopg2 |
| Deploy | Docker Compose, Nginx |

## Структура репозитория

```
greek-a2/
├── frontend/        React SPA (Telegram Mini App)
├── backend/         FastAPI REST API
├── pipeline/        Скрипты генерации и импорта контента
├── docs/            Спецификации, архитектурный RFC, планы
├── stitch/          UI-мокапы экранов (PNG + HTML)
└── docker-compose.yml
```

## Запуск в разработке

### Frontend

```bash
cd frontend
npm install
npm run dev        # http://localhost:5173
npm test           # 65 тестов
```

### Backend

```bash
cd backend
uv sync --extra dev
# Нужен PostgreSQL (см. docker-compose ниже)
uv run alembic upgrade head
uv run uvicorn app.main:app --reload   # http://localhost:8000
uv run python -m pytest                # 55 тестов
```

### Только PostgreSQL через Docker

```bash
cp backend/.env.example backend/.env   # задать BOT_TOKEN и POSTGRES_PASSWORD
docker compose up postgres -d
```

### Полный стек через Docker

```bash
cp backend/.env.example backend/.env
docker compose up --build
```

Backend: `http://localhost:8000` · Frontend dev-сервер: `http://localhost:5173`

## Пайплайн контента

Генерация → валидация → импорт в БД → аудио → публикация.

```bash
cd pipeline
cp .env.example .env          # ANTHROPIC_API_KEY, DATABASE_URL, AUDIO_DIR

# 1. Сгенерировать упражнения (Claude API → data/generated/*.json)
python generate_exercises.py --level a1
python generate_exercises.py --level a2
python generate_exercises.py --level b1
python generate_placement.py

# 2. Импортировать в БД (is_published=False)
python import_content.py

# 3. Генерировать аудио (gTTS → audio/*.mp3)
python generate_audio.py

# 4. Проверить контент и опубликовать
python review_content.py --unit-id 1
python publish_content.py --unit-id 1

uv run python -m pytest        # 42 теста
```

## Функциональность

- **Placement test** — определяет стартовый уровень при первом входе
- **Карта уровней** — A1 (6 юнитов) / A2 (9 юнитов) / B1 (8 юнитов) с прогрессом
- **7 типов упражнений**: True/False, Multiple Choice, Matching, Fill in the Blank, Image Description, Dialogue, Mini-test
- **Словарь** — интервальные повторения по алгоритму SM-2
- **XP и streak** — лёгкая геймификация без давления
- **Offline-first** — TanStack Query + sync queue, работает без стабильного интернета

## Аутентификация

Backend верифицирует `initData` от Telegram через HMAC-SHA256 — без JWT, без регистрации. Пользователь идентифицируется автоматически.
