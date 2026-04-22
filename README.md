# Greek Learning App

Telegram Mini App для изучения новогреческого языка (A1–B1) с фокусом на подготовку к экзамену ΠΙΣΤΟΠΟΙΗΣΗ ΕΛΛΗΝΟΜΑΘΕΙΑΣ A2. Pet-проект, в котором я собрала полноценный Duolingo-подобный UX поверх React + Telegram WebApp SDK.

## Стек

| Слой | Технологии |
|------|-----------|
| **Frontend** | **React 18, Vite, TypeScript, TanStack Query v5, Zustand, React Router v6, CSS Modules** |
| Тесты | Vitest + Testing Library (65 unit/integration тестов) |
| Интеграция | Telegram WebApp SDK (`@twa-dev/sdk`), Axios |
| Backend | FastAPI (Python 3.12), SQLAlchemy 2.0 async, PostgreSQL, Alembic, gTTS |
| Deploy | Docker Compose, Nginx |

## Фронтенд — что внутри

### Архитектура

```
frontend/src/
├── features/
│   ├── curriculum/      экраны карты уровней, юнитов
│   ├── exercises/       7 типов упражнений + mini-test + результаты
│   └── vocabulary/      словарь, флэшкарты, обучение словам
├── shared/
│   ├── api/             Axios client + endpoint-модуль
│   ├── components/      BottomNav, переиспользуемые UI-части
│   ├── hooks/           useTelegram и др.
│   └── store/           Zustand store (XP, streak, настройки)
├── App.tsx              роуты + bootstrap Telegram initData
├── index.css            дизайн-система (CSS-переменные)
└── main.tsx
```

### Ключевые решения

- **Offline-first.** TanStack Query кэширует ответы, мутации уходят в sync-queue и переотправляются при восстановлении сети — приложение продолжает работать в метро.
- **Telegram-нативная авторизация.** Бэкенд верифицирует `initData` через HMAC-SHA256 — без JWT и регистрации, пользователь идентифицируется автоматически.
- **Геймификация без давления.** XP и streak-счётчик, но без life-системы и обратного отсчёта — учиться должно быть приятно.
- **Дизайн-система на CSS-переменных.** Единая палитра *Aegean Midnight* в `index.css`, легко переключаема в тему.
- **Feature-sliced структура.** Фичи изолированы, `shared/` для переиспользуемого.
- **Строгий TypeScript.** API-контракты типизированы, общий `api` клиент с интерсепторами.

### Продукт

- **Placement test** — подбирает стартовый уровень при первом входе
- **Карта уровней** — A1 (6 юнитов) / A2 (9) / B1 (8) с прогрессом
- **7 типов упражнений** — True/False, Multiple Choice, Matching, Fill in the Blank, Image Description, Dialogue, Mini-test
- **Словарь с SRS** — интервальные повторения по алгоритму SM-2
- **Обучение словам** — flashcard-формат с аудио

## Запуск

### Frontend

```bash
cd frontend
npm install
npm run dev          # http://localhost:5173
npm test             # 60 тестов (vitest)
npm run lint         # ESLint
npm run typecheck    # tsc --noEmit
npm run format       # Prettier
npm run build        # production bundle
```

### Backend (опционально, если нужен реальный API)

```bash
cd backend
uv sync --extra dev
cp .env.example .env                    # BOT_TOKEN, POSTGRES_PASSWORD
docker compose up postgres -d
uv run alembic upgrade head
uv run uvicorn app.main:app --reload    # http://localhost:8000
```

### Полный стек через Docker

```bash
cp backend/.env.example backend/.env
docker compose up --build
```

## Контент

Упражнения и словарь — в `backend/seed_data/`, подтягиваются в БД через `seed_dev.py` (идемпотентно). Аудио (gTTS, ~730 MP3) лежит в `frontend/public/audio/` и отдаётся статикой фронт-сервером.

## Структура репозитория

```
greek-a2/
├── frontend/        React SPA (Telegram Mini App) ← основной фокус
├── backend/         FastAPI REST API + seed-данные + аудио
├── docs/            Спецификации и архитектурные заметки
└── docker-compose.yml
```
