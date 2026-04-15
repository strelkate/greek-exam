# Frontend Plan 1: Foundation

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Создать полную основу React-приложения: Vite-проект, дизайн-систему, shared компоненты, API-клиент, Zustand-сторы и routing scaffold с заглушками экранов.

**Architecture:** Feature-based структура (`src/features/`, `src/shared/`). Zustand persist для клиентского состояния и offline-буфера, TanStack Query для серверных данных. Axios с заголовком `X-Telegram-Init-Data` на каждый запрос.

**Tech Stack:** React 18, Vite, TypeScript, React Router v6, TanStack Query v5, Zustand, Axios, Vitest, @testing-library/react

---

## File Map

| Файл | Назначение |
|------|-----------|
| `frontend/package.json` | Зависимости проекта |
| `frontend/vite.config.ts` | Vite конфигурация |
| `frontend/tsconfig.json` | TypeScript конфигурация |
| `frontend/index.html` | HTML-точка входа |
| `frontend/src/main.tsx` | React root, провайдеры |
| `frontend/src/App.tsx` | Роутер + first-launch логика |
| `frontend/src/index.css` | CSS design system переменные |
| `frontend/src/shared/api/types.ts` | TypeScript типы для API ответов |
| `frontend/src/shared/api/client.ts` | Axios instance с авторизацией |
| `frontend/src/shared/api/endpoints.ts` | Функции вызова API |
| `frontend/src/shared/store/useAppStore.ts` | Zustand: XP, streak, settings (persist) |
| `frontend/src/shared/store/useExerciseStore.ts` | Zustand: состояние сессии упражнения |
| `frontend/src/shared/store/useSyncQueue.ts` | Zustand: offline-буфер прогресса (persist) |
| `frontend/src/shared/hooks/useTelegram.ts` | Telegram Mini App SDK wrapper |
| `frontend/src/shared/hooks/useSettings.ts` | Хук для настройки перевода инструкций |
| `frontend/src/shared/components/Button.tsx` | Переиспользуемая кнопка |
| `frontend/src/shared/components/ProgressBar.tsx` | Прогресс-бар |
| `frontend/src/shared/components/Card.tsx` | Карточка-контейнер |
| `frontend/src/shared/components/AudioPlayer.tsx` | Кнопка воспроизведения аудио |
| `frontend/src/shared/components/BottomNav.tsx` | Нижняя навигация (Учёба / Словарь) |
| `frontend/src/features/curriculum/LevelMapScreen.tsx` | Заглушка экрана карты уровней |
| `frontend/src/features/placement/PlacementScreen.tsx` | Заглушка экрана placement test |
| `frontend/src/features/exercises/ExerciseScreen.tsx` | Заглушка экрана упражнения |
| `frontend/src/features/vocabulary/VocabularyHomeScreen.tsx` | Заглушка экрана словаря |
| `frontend/src/test/setup.ts` | Настройка Vitest |
| `frontend/src/shared/store/__tests__/useAppStore.test.ts` | Тесты useAppStore |
| `frontend/src/shared/store/__tests__/useSyncQueue.test.ts` | Тесты useSyncQueue |
| `frontend/src/shared/components/__tests__/Button.test.tsx` | Тесты Button |
| `frontend/src/shared/components/__tests__/ProgressBar.test.tsx` | Тесты ProgressBar |

---

### Task 1: Vite + TypeScript проект

**Files:**
- Create: `frontend/package.json`
- Create: `frontend/vite.config.ts`
- Create: `frontend/tsconfig.json`
- Create: `frontend/index.html`
- Create: `frontend/src/test/setup.ts`

- [ ] **Step 1: Создать директорию и package.json**

```bash
mkdir -p /Users/ekaterina/Project/greek-a2/frontend/src
```

Создать `frontend/package.json`:
```json
{
  "name": "greek-learning-app",
  "private": true,
  "version": "0.1.0",
  "type": "module",
  "scripts": {
    "dev": "vite",
    "build": "tsc && vite build",
    "preview": "vite preview",
    "test": "vitest run",
    "test:watch": "vitest"
  },
  "dependencies": {
    "@tanstack/react-query": "^5.28.0",
    "@twa-dev/sdk": "^7.10.0",
    "axios": "^1.6.8",
    "react": "^18.3.1",
    "react-dom": "^18.3.1",
    "react-router-dom": "^6.22.3",
    "zustand": "^4.5.2"
  },
  "devDependencies": {
    "@testing-library/jest-dom": "^6.4.2",
    "@testing-library/react": "^15.0.2",
    "@testing-library/user-event": "^14.5.2",
    "@types/react": "^18.3.1",
    "@types/react-dom": "^18.3.0",
    "@vitejs/plugin-react": "^4.2.1",
    "jsdom": "^24.0.0",
    "typescript": "^5.4.3",
    "vite": "^5.2.8",
    "vitest": "^1.4.0"
  }
}
```

- [ ] **Step 2: Создать vite.config.ts**

```typescript
// frontend/vite.config.ts
import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

export default defineConfig({
  plugins: [react()],
  server: {
    proxy: {
      '/api': 'http://localhost:8000',
    },
  },
  test: {
    globals: true,
    environment: 'jsdom',
    setupFiles: ['./src/test/setup.ts'],
  },
})
```

- [ ] **Step 3: Создать tsconfig.json**

```json
{
  "compilerOptions": {
    "target": "ES2020",
    "useDefineForClassFields": true,
    "lib": ["ES2020", "DOM", "DOM.Iterable"],
    "module": "ESNext",
    "skipLibCheck": true,
    "moduleResolution": "bundler",
    "allowImportingTsExtensions": true,
    "resolveJsonModule": true,
    "isolatedModules": true,
    "noEmit": true,
    "jsx": "react-jsx",
    "strict": true,
    "noUnusedLocals": true,
    "noUnusedParameters": true,
    "noFallthroughCasesInSwitch": true,
    "baseUrl": ".",
    "paths": {
      "@/*": ["src/*"]
    }
  },
  "include": ["src"],
  "references": [{ "path": "./tsconfig.node.json" }]
}
```

Создать `frontend/tsconfig.node.json`:
```json
{
  "compilerOptions": {
    "composite": true,
    "skipLibCheck": true,
    "module": "ESNext",
    "moduleResolution": "bundler",
    "allowSyntheticDefaultImports": true
  },
  "include": ["vite.config.ts"]
}
```

- [ ] **Step 4: Создать index.html**

```html
<!DOCTYPE html>
<html lang="el">
  <head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no" />
    <title>Μαθαίνω Ελληνικά</title>
    <script src="https://telegram.org/js/telegram-web-app.js"></script>
    <link rel="preconnect" href="https://fonts.googleapis.com" />
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin />
    <link href="https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;700&display=swap" rel="stylesheet" />
  </head>
  <body>
    <div id="root"></div>
    <script type="module" src="/src/main.tsx"></script>
  </body>
</html>
```

- [ ] **Step 5: Создать test setup**

```typescript
// frontend/src/test/setup.ts
import '@testing-library/jest-dom'
```

- [ ] **Step 6: Установить зависимости**

```bash
cd /Users/ekaterina/Project/greek-a2/frontend && npm install
```

Ожидаемый результат: `node_modules/` создан, нет ошибок.

- [ ] **Step 7: Проверить сборку**

```bash
cd /Users/ekaterina/Project/greek-a2/frontend && npm run build 2>&1 | tail -5
```

Ожидаемый результат: ошибка про отсутствие `src/main.tsx` — это нормально, идём дальше.

- [ ] **Step 8: Commit**

```bash
cd /Users/ekaterina/Project/greek-a2 && git add frontend/ && git commit -m "feat(frontend): scaffold Vite + TypeScript project"
```

---

### Task 2: CSS Design System

**Files:**
- Create: `frontend/src/index.css`

- [ ] **Step 1: Создать index.css с переменными дизайн-системы**

```css
/* frontend/src/index.css */
*, *::before, *::after {
  box-sizing: border-box;
  margin: 0;
  padding: 0;
}

:root {
  /* Цвета поверхностей */
  --color-surface:          #0b0d1a;
  --color-surface-low:      #101221;
  --color-surface-high:     #1c1e30;
  --color-surface-highest:  #222537;

  /* Акцентные цвета */
  --color-primary:          #fdd828;
  --color-primary-dark:     #eeca12;
  --color-secondary:        #caccf7;
  --color-on-surface:       #ffffff;
  --color-on-surface-muted: rgba(255, 255, 255, 0.6);

  /* Статусные цвета */
  --color-success:          #4ade80;
  --color-error:            #f87171;

  /* Типографика */
  --font-family:            'Plus Jakarta Sans', sans-serif;
  --font-size-display:      3.5rem;
  --font-size-headline:     1.5rem;
  --font-size-title:        1.125rem;
  --font-size-body:         0.875rem;
  --font-size-label:        0.6875rem;

  --font-weight-regular:    400;
  --font-weight-medium:     500;
  --font-weight-bold:       700;

  --line-height-tight:      1.2;
  --line-height-normal:     1.5;

  /* Радиусы */
  --radius-card:            16px;
  --radius-button:          12px;
  --radius-sm:              8px;

  /* Отступы */
  --spacing-xs:             4px;
  --spacing-sm:             8px;
  --spacing-md:             16px;
  --spacing-lg:             24px;
  --spacing-xl:             32px;

  /* Навигация */
  --bottom-nav-height:      64px;
}

html, body, #root {
  height: 100%;
  width: 100%;
  overflow-x: hidden;
}

body {
  background-color: var(--color-surface);
  color: var(--color-on-surface);
  font-family: var(--font-family);
  font-size: var(--font-size-body);
  line-height: var(--line-height-normal);
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
}

#root {
  display: flex;
  flex-direction: column;
  min-height: 100%;
}
```

- [ ] **Step 2: Commit**

```bash
cd /Users/ekaterina/Project/greek-a2 && git add frontend/src/index.css && git commit -m "feat(frontend): add Aegean Midnight design system CSS variables"
```

---

### Task 3: TypeScript API типы

**Files:**
- Create: `frontend/src/shared/api/types.ts`

- [ ] **Step 1: Создать types.ts**

```typescript
// frontend/src/shared/api/types.ts

export type PlacementStatus = 'pending' | 'passed' | 'failed' | 'skipped'
export type Level = 'A1' | 'A2' | 'B1'
export type ExerciseType =
  | 'true_false'
  | 'matching'
  | 'multiple_choice'
  | 'fill_blank'
  | 'image_description'
  | 'dialogue'

// Auth
export interface SessionResponse {
  user_id: number
  telegram_id: number
  streak_days: number
  total_xp: number
  placement_status: PlacementStatus
  a1_skipped: boolean
  show_instruction_translation: boolean
  is_new_user: boolean
}

// Curriculum
export interface LevelProgress {
  level: Level
  total_units: number
  completed_units: number
  progress_percent: number
}
export interface LevelsResponse {
  levels: LevelProgress[]
}

export interface UnitSummary {
  id: number
  title: string
  order_index: number
  exercises_total: number
  exercises_completed: number
  mini_test_passed: boolean
  unit_completed: boolean
}
export interface UnitsResponse {
  units: UnitSummary[]
}

export interface ExerciseMeta {
  id: number
  type: ExerciseType
  order_index: number
  audio_paths: string[]
  completed: boolean
}
export interface VocabCardMeta {
  id: number
  word_gr: string
  word_ru: string
  audio_path: string | null
}
export interface UnitDetailResponse {
  id: number
  title: string
  level: Level
  exercises: ExerciseMeta[]
  vocabulary_cards: VocabCardMeta[]
}

// Exercises
export interface ExerciseResponse {
  id: number
  unit_id: number
  type: ExerciseType
  content: Record<string, unknown>
  audio_paths: string[]
}
export interface CompleteExerciseResponse {
  xp_earned: number
  xp_breakdown: Record<string, number>
  streak_days: number
  streak_updated: boolean
  unit_progress: {
    exercises_completed: number
    exercises_total: number
    mini_test_unlocked: boolean
  }
}

// Placement
export interface PlacementQuestion {
  id: number
  type: 'true_false' | 'multiple_choice' | 'fill_blank'
  content: Record<string, unknown>
}
export interface PlacementQuestionsResponse {
  questions: PlacementQuestion[]
}
export interface PlacementCompleteResponse {
  placement_status: PlacementStatus
  a1_skipped: boolean
  message: string
}

// Mini-test
export interface MiniTestQuestion {
  id: number
  type: 'true_false' | 'multiple_choice' | 'fill_blank'
  content: Record<string, unknown>
}
export interface MiniTestQuestionsResponse {
  questions: MiniTestQuestion[]
}
export interface MiniTestCompleteResponse {
  unit_completed: boolean
  xp_earned: number
  cards_added_to_vocab: number
}

// Vocabulary
export type CardStatus = 'new' | 'learning' | 'learned'

export interface VocabCard {
  id: number
  word_gr: string
  word_ru: string
  audio_path: string | null
  status: CardStatus
  next_review_at: string
}
export interface DueCardsResponse {
  due_count: number
  cards: VocabCard[]
}
export interface ReviewResponse {
  card_id: number
  new_status: CardStatus
  next_review_at: string
  interval_days: number
  xp_earned: number
}
export interface VocabStatsResponse {
  total_cards: number
  learned_count: number
  due_today: number
  new_count: number
}

// Settings
export interface SettingsResponse {
  show_instruction_translation: boolean
}

// Sync
export interface ProgressEvent {
  exercise_id: number
  score: number
  total: number
  completed_at: string
}
export interface SyncResponse {
  synced: number
  xp_earned: number
}
```

- [ ] **Step 2: Commit**

```bash
cd /Users/ekaterina/Project/greek-a2 && git add frontend/src/shared/api/types.ts && git commit -m "feat(frontend): add TypeScript API response types"
```

---

### Task 4: Axios API клиент и endpoints

**Files:**
- Create: `frontend/src/shared/api/client.ts`
- Create: `frontend/src/shared/api/endpoints.ts`

- [ ] **Step 1: Создать axios client**

```typescript
// frontend/src/shared/api/client.ts
import axios from 'axios'

const BASE_URL = import.meta.env.VITE_API_URL ?? ''

export const apiClient = axios.create({
  baseURL: BASE_URL,
  headers: { 'Content-Type': 'application/json' },
})

// Инжектируем X-Telegram-Init-Data перед каждым запросом
// initData устанавливается один раз при старте приложения
let _initData = ''

export function setInitData(initData: string) {
  _initData = initData
}

apiClient.interceptors.request.use((config) => {
  if (_initData) {
    config.headers['X-Telegram-Init-Data'] = _initData
  }
  return config
})
```

- [ ] **Step 2: Создать .env файл для разработки**

```bash
# frontend/.env.development
VITE_API_URL=http://localhost:8000
```

Создать `frontend/.env.development`:
```
VITE_API_URL=http://localhost:8000
```

- [ ] **Step 3: Создать endpoints.ts**

```typescript
// frontend/src/shared/api/endpoints.ts
import { apiClient } from './client'
import type {
  SessionResponse, LevelsResponse, UnitsResponse, UnitDetailResponse,
  ExerciseResponse, CompleteExerciseResponse,
  PlacementQuestionsResponse, PlacementCompleteResponse,
  MiniTestQuestionsResponse, MiniTestCompleteResponse,
  DueCardsResponse, ReviewResponse, VocabStatsResponse,
  SettingsResponse, SyncResponse, ProgressEvent,
} from './types'

export const api = {
  // Auth
  createSession: () =>
    apiClient.post<SessionResponse>('/api/v1/auth/session').then(r => r.data),

  // Curriculum
  getLevels: () =>
    apiClient.get<LevelsResponse>('/api/v1/curriculum/levels').then(r => r.data),

  getUnits: (level?: string) =>
    apiClient.get<UnitsResponse>('/api/v1/curriculum/units', { params: level ? { level } : {} }).then(r => r.data),

  getUnitDetail: (unitId: number) =>
    apiClient.get<UnitDetailResponse>(`/api/v1/curriculum/units/${unitId}`).then(r => r.data),

  // Exercises
  getExercise: (exerciseId: number) =>
    apiClient.get<ExerciseResponse>(`/api/v1/exercises/${exerciseId}`).then(r => r.data),

  completeExercise: (exerciseId: number, score: number, total: number) =>
    apiClient.post<CompleteExerciseResponse>(`/api/v1/exercises/${exerciseId}/complete`, { score, total }).then(r => r.data),

  // Placement test
  getPlacementQuestions: () =>
    apiClient.get<PlacementQuestionsResponse>('/api/v1/placement-test/questions').then(r => r.data),

  completePlacementTest: (score: number, total: number) =>
    apiClient.post<PlacementCompleteResponse>('/api/v1/placement-test/complete', { score, total }).then(r => r.data),

  // Mini-test
  getMiniTestQuestions: (unitId: number) =>
    apiClient.get<MiniTestQuestionsResponse>(`/api/v1/units/${unitId}/mini-test`).then(r => r.data),

  completeMiniTest: (unitId: number, score: number, total: number) =>
    apiClient.post<MiniTestCompleteResponse>(`/api/v1/units/${unitId}/mini-test/complete`, { score, total }).then(r => r.data),

  // Vocabulary
  getDueCards: () =>
    apiClient.get<DueCardsResponse>('/api/v1/vocabulary/due').then(r => r.data),

  reviewCard: (cardId: number, knew: boolean) =>
    apiClient.post<ReviewResponse>(`/api/v1/vocabulary/cards/${cardId}/review`, { known: knew }).then(r => r.data),

  getVocabStats: () =>
    apiClient.get<VocabStatsResponse>('/api/v1/vocabulary/stats').then(r => r.data),

  // Settings
  patchSettings: (payload: Partial<{ show_instruction_translation: boolean }>) =>
    apiClient.patch<SettingsResponse>('/api/v1/settings', payload).then(r => r.data),

  // Sync
  syncProgress: (events: ProgressEvent[]) =>
    apiClient.post<SyncResponse>('/api/v1/sync/progress', { events }).then(r => r.data),
}
```

- [ ] **Step 4: Commit**

```bash
cd /Users/ekaterina/Project/greek-a2 && git add frontend/src/shared/api/ frontend/.env.development && git commit -m "feat(frontend): add axios API client and endpoints"
```

---

### Task 5: Zustand сторы

**Files:**
- Create: `frontend/src/shared/store/useAppStore.ts`
- Create: `frontend/src/shared/store/useExerciseStore.ts`
- Create: `frontend/src/shared/store/useSyncQueue.ts`
- Create: `frontend/src/shared/store/__tests__/useAppStore.test.ts`
- Create: `frontend/src/shared/store/__tests__/useSyncQueue.test.ts`

- [ ] **Step 1: Написать тест useAppStore**

```typescript
// frontend/src/shared/store/__tests__/useAppStore.test.ts
import { beforeEach, describe, expect, it } from 'vitest'
import { act, renderHook } from '@testing-library/react'
import { useAppStore } from '../useAppStore'

beforeEach(() => {
  // Сбросить стор перед каждым тестом
  useAppStore.setState({
    xp: 0,
    streak: 0,
    streakDate: null,
    showTranslations: true,
  })
})

describe('useAppStore', () => {
  it('инициализируется с дефолтными значениями', () => {
    const { result } = renderHook(() => useAppStore())
    expect(result.current.xp).toBe(0)
    expect(result.current.streak).toBe(0)
    expect(result.current.showTranslations).toBe(true)
  })

  it('addXp увеличивает xp', () => {
    const { result } = renderHook(() => useAppStore())
    act(() => result.current.addXp(10))
    expect(result.current.xp).toBe(10)
    act(() => result.current.addXp(25))
    expect(result.current.xp).toBe(35)
  })

  it('setStreak обновляет streak и streakDate', () => {
    const { result } = renderHook(() => useAppStore())
    act(() => result.current.setStreak(5, '2026-04-14'))
    expect(result.current.streak).toBe(5)
    expect(result.current.streakDate).toBe('2026-04-14')
  })

  it('setShowTranslations переключает настройку', () => {
    const { result } = renderHook(() => useAppStore())
    act(() => result.current.setShowTranslations(false))
    expect(result.current.showTranslations).toBe(false)
  })
})
```

- [ ] **Step 2: Запустить тест — убедиться что он падает**

```bash
cd /Users/ekaterina/Project/greek-a2/frontend && npm test -- useAppStore 2>&1 | tail -10
```

Ожидаемый результат: ошибка `Cannot find module '../useAppStore'`

- [ ] **Step 3: Создать useAppStore.ts**

```typescript
// frontend/src/shared/store/useAppStore.ts
import { create } from 'zustand'
import { persist } from 'zustand/middleware'

interface AppState {
  xp: number
  streak: number
  streakDate: string | null
  showTranslations: boolean
  addXp: (amount: number) => void
  setStreak: (days: number, date: string) => void
  setShowTranslations: (value: boolean) => void
  hydrate: (data: { xp: number; streak: number; showTranslations: boolean }) => void
}

export const useAppStore = create<AppState>()(
  persist(
    (set) => ({
      xp: 0,
      streak: 0,
      streakDate: null,
      showTranslations: true,

      addXp: (amount) => set((s) => ({ xp: s.xp + amount })),

      setStreak: (days, date) => set({ streak: days, streakDate: date }),

      setShowTranslations: (value) => set({ showTranslations: value }),

      hydrate: (data) =>
        set({ xp: data.xp, streak: data.streak, showTranslations: data.showTranslations }),
    }),
    { name: 'greek-app-store' }
  )
)
```

- [ ] **Step 4: Запустить тест — убедиться что он проходит**

```bash
cd /Users/ekaterina/Project/greek-a2/frontend && npm test -- useAppStore 2>&1 | tail -10
```

Ожидаемый результат: `✓ useAppStore > ...` (4 теста, все зелёные)

- [ ] **Step 5: Написать тест useSyncQueue**

```typescript
// frontend/src/shared/store/__tests__/useSyncQueue.test.ts
import { beforeEach, describe, expect, it, vi } from 'vitest'
import { act, renderHook } from '@testing-library/react'
import { useSyncQueue } from '../useSyncQueue'

beforeEach(() => {
  useSyncQueue.setState({ queue: [] })
})

describe('useSyncQueue', () => {
  it('начинает с пустой очередью', () => {
    const { result } = renderHook(() => useSyncQueue())
    expect(result.current.queue).toHaveLength(0)
  })

  it('enqueue добавляет событие в очередь', () => {
    const { result } = renderHook(() => useSyncQueue())
    const event = { exercise_id: 1, score: 1, total: 1, completed_at: '2026-04-14T10:00:00Z' }
    act(() => result.current.enqueue(event))
    expect(result.current.queue).toHaveLength(1)
    expect(result.current.queue[0]).toEqual(event)
  })

  it('clear очищает очередь', () => {
    const { result } = renderHook(() => useSyncQueue())
    act(() => {
      result.current.enqueue({ exercise_id: 1, score: 1, total: 1, completed_at: '2026-04-14T10:00:00Z' })
      result.current.clear()
    })
    expect(result.current.queue).toHaveLength(0)
  })
})
```

- [ ] **Step 6: Запустить тест — убедиться что он падает**

```bash
cd /Users/ekaterina/Project/greek-a2/frontend && npm test -- useSyncQueue 2>&1 | tail -5
```

Ожидаемый результат: ошибка `Cannot find module '../useSyncQueue'`

- [ ] **Step 7: Создать useSyncQueue.ts**

```typescript
// frontend/src/shared/store/useSyncQueue.ts
import { create } from 'zustand'
import { persist } from 'zustand/middleware'
import type { ProgressEvent } from '../api/types'
import { api } from '../api/endpoints'

interface SyncQueueState {
  queue: ProgressEvent[]
  enqueue: (event: ProgressEvent) => void
  clear: () => void
  flush: () => Promise<void>
}

export const useSyncQueue = create<SyncQueueState>()(
  persist(
    (set, get) => ({
      queue: [],

      enqueue: (event) => set((s) => ({ queue: [...s.queue, event] })),

      clear: () => set({ queue: [] }),

      flush: async () => {
        const { queue, clear } = get()
        if (queue.length === 0) return
        try {
          await api.syncProgress(queue)
          clear()
        } catch {
          // Оставляем в очереди, попробуем позже
        }
      },
    }),
    { name: 'greek-sync-queue' }
  )
)

// Слушаем восстановление сети и автоматически флашим
if (typeof window !== 'undefined') {
  window.addEventListener('online', () => {
    useSyncQueue.getState().flush()
  })
}
```

- [ ] **Step 8: Создать useExerciseStore.ts**

```typescript
// frontend/src/shared/store/useExerciseStore.ts
import { create } from 'zustand'

interface Answer {
  exerciseId: number
  isCorrect: boolean
}

interface ExerciseSessionState {
  unitId: number | null
  exerciseIds: number[]
  currentIndex: number
  answers: Answer[]
  isComplete: boolean

  startSession: (unitId: number, exerciseIds: number[]) => void
  submitAnswer: (exerciseId: number, isCorrect: boolean) => void
  nextExercise: () => void
  resetSession: () => void
}

export const useExerciseStore = create<ExerciseSessionState>()((set) => ({
  unitId: null,
  exerciseIds: [],
  currentIndex: 0,
  answers: [],
  isComplete: false,

  startSession: (unitId, exerciseIds) =>
    set({ unitId, exerciseIds, currentIndex: 0, answers: [], isComplete: false }),

  submitAnswer: (exerciseId, isCorrect) =>
    set((s) => ({ answers: [...s.answers, { exerciseId, isCorrect }] })),

  nextExercise: () =>
    set((s) => {
      const next = s.currentIndex + 1
      return next >= s.exerciseIds.length
        ? { isComplete: true }
        : { currentIndex: next }
    }),

  resetSession: () =>
    set({ unitId: null, exerciseIds: [], currentIndex: 0, answers: [], isComplete: false }),
}))
```

- [ ] **Step 9: Запустить все тесты**

```bash
cd /Users/ekaterina/Project/greek-a2/frontend && npm test 2>&1 | tail -15
```

Ожидаемый результат: все тесты зелёные (7 тестов)

- [ ] **Step 10: Commit**

```bash
cd /Users/ekaterina/Project/greek-a2 && git add frontend/src/shared/store/ && git commit -m "feat(frontend): add Zustand stores (app, exercise session, sync queue)"
```

---

### Task 6: useTelegram хук

**Files:**
- Create: `frontend/src/shared/hooks/useTelegram.ts`
- Create: `frontend/src/shared/hooks/useSettings.ts`

- [ ] **Step 1: Создать useTelegram.ts**

```typescript
// frontend/src/shared/hooks/useTelegram.ts
import WebApp from '@twa-dev/sdk'

export interface TelegramUser {
  id: number
  firstName: string
  languageCode?: string
}

export function useTelegram() {
  // В dev-режиме без Telegram — используем мок
  const isDev = import.meta.env.DEV && !WebApp.initData

  const user: TelegramUser = isDev
    ? { id: 0, firstName: 'Dev User', languageCode: 'ru' }
    : {
        id: WebApp.initDataUnsafe?.user?.id ?? 0,
        firstName: WebApp.initDataUnsafe?.user?.first_name ?? '',
        languageCode: WebApp.initDataUnsafe?.user?.language_code,
      }

  const initData = isDev ? 'dev_mock_init_data' : WebApp.initData

  return {
    user,
    initData,
    ready: () => WebApp.ready(),
    expand: () => WebApp.expand(),
    backButton: {
      show: () => WebApp.BackButton.show(),
      hide: () => WebApp.BackButton.hide(),
      onClick: (fn: () => void) => WebApp.BackButton.onClick(fn),
      offClick: (fn: () => void) => WebApp.BackButton.offClick(fn),
    },
    haptic: {
      impact: (style: 'light' | 'medium' | 'heavy' = 'light') =>
        WebApp.HapticFeedback.impactOccurred(style),
      notification: (type: 'success' | 'error' | 'warning') =>
        WebApp.HapticFeedback.notificationOccurred(type),
    },
  }
}
```

- [ ] **Step 2: Создать useSettings.ts**

```typescript
// frontend/src/shared/hooks/useSettings.ts
import { useAppStore } from '../store/useAppStore'

export function useSettings() {
  const showTranslations = useAppStore((s) => s.showTranslations)
  const setShowTranslations = useAppStore((s) => s.setShowTranslations)

  return { showTranslations, setShowTranslations }
}
```

- [ ] **Step 3: Commit**

```bash
cd /Users/ekaterina/Project/greek-a2 && git add frontend/src/shared/hooks/ && git commit -m "feat(frontend): add useTelegram and useSettings hooks"
```

---

### Task 7: Shared компоненты — Button и ProgressBar

**Files:**
- Create: `frontend/src/shared/components/Button.tsx`
- Create: `frontend/src/shared/components/ProgressBar.tsx`
- Create: `frontend/src/shared/components/__tests__/Button.test.tsx`
- Create: `frontend/src/shared/components/__tests__/ProgressBar.test.tsx`

- [ ] **Step 1: Написать тест Button**

```typescript
// frontend/src/shared/components/__tests__/Button.test.tsx
import { describe, expect, it, vi } from 'vitest'
import { render, screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { Button } from '../Button'

describe('Button', () => {
  it('рендерит текст', () => {
    render(<Button>Проверить</Button>)
    expect(screen.getByRole('button', { name: 'Проверить' })).toBeInTheDocument()
  })

  it('вызывает onClick', async () => {
    const onClick = vi.fn()
    render(<Button onClick={onClick}>Далее</Button>)
    await userEvent.click(screen.getByRole('button'))
    expect(onClick).toHaveBeenCalledOnce()
  })

  it('disabled не вызывает onClick', async () => {
    const onClick = vi.fn()
    render(<Button onClick={onClick} disabled>Далее</Button>)
    await userEvent.click(screen.getByRole('button'))
    expect(onClick).not.toHaveBeenCalled()
  })

  it('variant=secondary применяет нужный класс', () => {
    render(<Button variant="secondary">Пропустить</Button>)
    expect(screen.getByRole('button')).toHaveClass('btn-secondary')
  })
})
```

- [ ] **Step 2: Запустить тест — убедиться что падает**

```bash
cd /Users/ekaterina/Project/greek-a2/frontend && npm test -- Button 2>&1 | tail -5
```

- [ ] **Step 3: Создать Button.tsx**

```typescript
// frontend/src/shared/components/Button.tsx
import type { ButtonHTMLAttributes, ReactNode } from 'react'
import styles from './Button.module.css'

interface ButtonProps extends ButtonHTMLAttributes<HTMLButtonElement> {
  children: ReactNode
  variant?: 'primary' | 'secondary' | 'ghost'
  fullWidth?: boolean
}

export function Button({ children, variant = 'primary', fullWidth, className, ...props }: ButtonProps) {
  return (
    <button
      className={[
        styles.btn,
        styles[`btn-${variant}`],
        fullWidth ? styles['btn-full'] : '',
        className ?? '',
      ].join(' ')}
      {...props}
    >
      {children}
    </button>
  )
}
```

Создать `frontend/src/shared/components/Button.module.css`:
```css
.btn {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  padding: 14px var(--spacing-lg);
  border: none;
  border-radius: var(--radius-button);
  font-family: var(--font-family);
  font-size: var(--font-size-body);
  font-weight: var(--font-weight-bold);
  cursor: pointer;
  transition: opacity 0.15s, transform 0.1s;
  user-select: none;
  -webkit-tap-highlight-color: transparent;
}

.btn:active:not(:disabled) {
  transform: scale(0.97);
}

.btn:disabled {
  opacity: 0.4;
  cursor: not-allowed;
}

.btn-primary {
  background: linear-gradient(135deg, var(--color-primary), var(--color-primary-dark));
  color: #0b0d1a;
}

.btn-secondary {
  background: var(--color-surface-high);
  color: var(--color-on-surface);
}

.btn-ghost {
  background: transparent;
  color: var(--color-secondary);
}

.btn-full {
  width: 100%;
}
```

- [ ] **Step 4: Написать тест ProgressBar**

```typescript
// frontend/src/shared/components/__tests__/ProgressBar.test.tsx
import { describe, expect, it } from 'vitest'
import { render } from '@testing-library/react'
import { ProgressBar } from '../ProgressBar'

describe('ProgressBar', () => {
  it('устанавливает ширину по value', () => {
    const { container } = render(<ProgressBar value={3} max={6} />)
    const fill = container.querySelector('[data-fill]') as HTMLElement
    expect(fill.style.width).toBe('50%')
  })

  it('не превышает 100%', () => {
    const { container } = render(<ProgressBar value={10} max={6} />)
    const fill = container.querySelector('[data-fill]') as HTMLElement
    expect(fill.style.width).toBe('100%')
  })

  it('не опускается ниже 0%', () => {
    const { container } = render(<ProgressBar value={-1} max={6} />)
    const fill = container.querySelector('[data-fill]') as HTMLElement
    expect(fill.style.width).toBe('0%')
  })
})
```

- [ ] **Step 5: Создать ProgressBar.tsx**

```typescript
// frontend/src/shared/components/ProgressBar.tsx
import styles from './ProgressBar.module.css'

interface ProgressBarProps {
  value: number
  max: number
  className?: string
}

export function ProgressBar({ value, max, className }: ProgressBarProps) {
  const pct = Math.min(100, Math.max(0, (value / max) * 100))
  return (
    <div className={[styles.track, className].filter(Boolean).join(' ')}>
      <div
        className={styles.fill}
        data-fill
        style={{ width: `${pct}%` }}
      />
    </div>
  )
}
```

Создать `frontend/src/shared/components/ProgressBar.module.css`:
```css
.track {
  width: 100%;
  height: 8px;
  background: var(--color-surface-highest);
  border-radius: 4px;
  overflow: hidden;
}

.fill {
  height: 100%;
  background: var(--color-primary);
  border-radius: 4px;
  transition: width 0.3s ease;
}
```

- [ ] **Step 6: Запустить все тесты**

```bash
cd /Users/ekaterina/Project/greek-a2/frontend && npm test 2>&1 | tail -15
```

Ожидаемый результат: все тесты зелёные (11+ тестов)

- [ ] **Step 7: Commit**

```bash
cd /Users/ekaterina/Project/greek-a2 && git add frontend/src/shared/components/ && git commit -m "feat(frontend): add Button and ProgressBar shared components"
```

---

### Task 8: Card и AudioPlayer компоненты

**Files:**
- Create: `frontend/src/shared/components/Card.tsx`
- Create: `frontend/src/shared/components/AudioPlayer.tsx`

- [ ] **Step 1: Создать Card.tsx**

```typescript
// frontend/src/shared/components/Card.tsx
import type { HTMLAttributes, ReactNode } from 'react'
import styles from './Card.module.css'

interface CardProps extends HTMLAttributes<HTMLDivElement> {
  children: ReactNode
  elevated?: boolean
}

export function Card({ children, elevated, className, ...props }: CardProps) {
  return (
    <div
      className={[styles.card, elevated ? styles.elevated : '', className ?? ''].join(' ')}
      {...props}
    >
      {children}
    </div>
  )
}
```

Создать `frontend/src/shared/components/Card.module.css`:
```css
.card {
  background: var(--color-surface-high);
  border-radius: var(--radius-card);
  padding: var(--spacing-md);
}

.elevated {
  background: var(--color-surface-highest);
}
```

- [ ] **Step 2: Создать AudioPlayer.tsx**

```typescript
// frontend/src/shared/components/AudioPlayer.tsx
import { useCallback, useRef, useState } from 'react'
import styles from './AudioPlayer.module.css'

interface AudioPlayerProps {
  src: string
  autoPlay?: boolean
  className?: string
}

export function AudioPlayer({ src, autoPlay = false, className }: AudioPlayerProps) {
  const audioRef = useRef<HTMLAudioElement | null>(null)
  const [isPlaying, setIsPlaying] = useState(false)

  const play = useCallback(() => {
    if (!audioRef.current) {
      audioRef.current = new Audio(src)
      audioRef.current.onended = () => setIsPlaying(false)
    }
    audioRef.current.currentTime = 0
    audioRef.current.play()
    setIsPlaying(true)
  }, [src])

  // Автовоспроизведение при монтировании (для image_description)
  const refCallback = useCallback((el: HTMLButtonElement | null) => {
    if (el && autoPlay) {
      setTimeout(play, 300)
    }
  }, [autoPlay, play])

  return (
    <button
      ref={refCallback}
      className={[styles.btn, isPlaying ? styles.playing : '', className ?? ''].join(' ')}
      onClick={play}
      aria-label="Слушать"
      type="button"
    >
      <span className={styles.icon}>{isPlaying ? '⏸' : '🔊'}</span>
    </button>
  )
}
```

Создать `frontend/src/shared/components/AudioPlayer.module.css`:
```css
.btn {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 40px;
  height: 40px;
  border: none;
  border-radius: 50%;
  background: var(--color-surface-highest);
  cursor: pointer;
  transition: background 0.15s;
  -webkit-tap-highlight-color: transparent;
}

.btn:active {
  background: var(--color-surface-high);
}

.playing {
  background: var(--color-primary);
}

.playing .icon {
  filter: brightness(0);
}

.icon {
  font-size: 18px;
  line-height: 1;
}
```

- [ ] **Step 3: Commit**

```bash
cd /Users/ekaterina/Project/greek-a2 && git add frontend/src/shared/components/Card.tsx frontend/src/shared/components/Card.module.css frontend/src/shared/components/AudioPlayer.tsx frontend/src/shared/components/AudioPlayer.module.css && git commit -m "feat(frontend): add Card and AudioPlayer components"
```

---

### Task 9: BottomNav + routing scaffold + App.tsx

**Files:**
- Create: `frontend/src/shared/components/BottomNav.tsx`
- Create: `frontend/src/features/curriculum/LevelMapScreen.tsx`
- Create: `frontend/src/features/placement/PlacementScreen.tsx`
- Create: `frontend/src/features/exercises/ExerciseScreen.tsx`
- Create: `frontend/src/features/vocabulary/VocabularyHomeScreen.tsx`
- Create: `frontend/src/App.tsx`
- Create: `frontend/src/main.tsx`

- [ ] **Step 1: Создать BottomNav.tsx**

```typescript
// frontend/src/shared/components/BottomNav.tsx
import { NavLink, useLocation } from 'react-router-dom'
import styles from './BottomNav.module.css'

// Экраны где нижняя навигация скрыта (полноэкранный режим)
const HIDDEN_ROUTES = ['/placement', '/exercise', '/mini-test']

export function BottomNav() {
  const { pathname } = useLocation()
  const isHidden = HIDDEN_ROUTES.some(r => pathname.includes(r))
  if (isHidden) return null

  return (
    <nav className={styles.nav}>
      <NavLink to="/levels" className={({ isActive }) => [styles.tab, isActive ? styles.active : ''].join(' ')}>
        <span className={styles.icon}>📚</span>
        <span className={styles.label}>Учёба</span>
      </NavLink>
      <NavLink to="/vocabulary" className={({ isActive }) => [styles.tab, isActive ? styles.active : ''].join(' ')}>
        <span className={styles.icon}>🗂</span>
        <span className={styles.label}>Словарь</span>
      </NavLink>
    </nav>
  )
}
```

Создать `frontend/src/shared/components/BottomNav.module.css`:
```css
.nav {
  position: fixed;
  bottom: 0;
  left: 0;
  right: 0;
  height: var(--bottom-nav-height);
  display: flex;
  background: rgba(28, 30, 48, 0.8);
  backdrop-filter: blur(12px);
  -webkit-backdrop-filter: blur(12px);
  border-top: 1px solid rgba(202, 204, 247, 0.08);
  z-index: 100;
}

.tab {
  flex: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 4px;
  text-decoration: none;
  color: var(--color-on-surface-muted);
  transition: color 0.15s;
}

.tab.active {
  color: var(--color-primary);
}

.icon {
  font-size: 22px;
  line-height: 1;
}

.label {
  font-size: var(--font-size-label);
  font-weight: var(--font-weight-medium);
  text-transform: uppercase;
  letter-spacing: 0.05em;
}
```

- [ ] **Step 2: Создать экраны-заглушки**

```typescript
// frontend/src/features/curriculum/LevelMapScreen.tsx
export function LevelMapScreen() {
  return <div style={{ padding: 24, paddingBottom: 80 }}>LevelMapScreen — TODO</div>
}
```

```typescript
// frontend/src/features/placement/PlacementScreen.tsx
export function PlacementScreen() {
  return <div style={{ padding: 24 }}>PlacementScreen — TODO</div>
}
```

```typescript
// frontend/src/features/exercises/ExerciseScreen.tsx
export function ExerciseScreen() {
  return <div style={{ padding: 24 }}>ExerciseScreen — TODO</div>
}
```

```typescript
// frontend/src/features/vocabulary/VocabularyHomeScreen.tsx
export function VocabularyHomeScreen() {
  return <div style={{ padding: 24, paddingBottom: 80 }}>VocabularyHomeScreen — TODO</div>
}
```

- [ ] **Step 3: Создать App.tsx**

```typescript
// frontend/src/App.tsx
import { useEffect } from 'react'
import { Navigate, Route, Routes, useNavigate } from 'react-router-dom'
import { api } from './shared/api/endpoints'
import { setInitData } from './shared/api/client'
import { useAppStore } from './shared/store/useAppStore'
import { useTelegram } from './shared/hooks/useTelegram'
import { BottomNav } from './shared/components/BottomNav'
import { LevelMapScreen } from './features/curriculum/LevelMapScreen'
import { PlacementScreen } from './features/placement/PlacementScreen'
import { ExerciseScreen } from './features/exercises/ExerciseScreen'
import { VocabularyHomeScreen } from './features/vocabulary/VocabularyHomeScreen'

function AppRoutes() {
  return (
    <>
      <Routes>
        <Route path="/" element={<Navigate to="/levels" replace />} />
        <Route path="/placement" element={<PlacementScreen />} />
        <Route path="/levels" element={<LevelMapScreen />} />
        <Route path="/units/:unitId/exercise/:exerciseId" element={<ExerciseScreen />} />
        <Route path="/vocabulary" element={<VocabularyHomeScreen />} />
        <Route path="*" element={<Navigate to="/levels" replace />} />
      </Routes>
      <BottomNav />
    </>
  )
}

export function App() {
  const { initData, ready, expand } = useTelegram()
  const hydrate = useAppStore((s) => s.hydrate)
  const navigate = useNavigate()

  useEffect(() => {
    ready()
    expand()
    setInitData(initData)

    api.createSession().then((session) => {
      hydrate({
        xp: session.total_xp,
        streak: session.streak_days,
        showTranslations: session.show_instruction_translation,
      })
      if (session.placement_status === 'pending') {
        navigate('/placement', { replace: true })
      } else {
        navigate('/levels', { replace: true })
      }
    })
  }, []) // eslint-disable-line react-hooks/exhaustive-deps

  return <AppRoutes />
}
```

- [ ] **Step 4: Создать main.tsx**

```typescript
// frontend/src/main.tsx
import { StrictMode } from 'react'
import { createRoot } from 'react-dom/client'
import { BrowserRouter } from 'react-router-dom'
import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { App } from './App'
import './index.css'

const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      staleTime: 5 * 60 * 1000,       // 5 минут
      gcTime: 24 * 60 * 60 * 1000,    // 24 часа
      networkMode: 'offlineFirst',
      retry: 2,
    },
  },
})

createRoot(document.getElementById('root')!).render(
  <StrictMode>
    <QueryClientProvider client={queryClient}>
      <BrowserRouter>
        <App />
      </BrowserRouter>
    </QueryClientProvider>
  </StrictMode>
)
```

- [ ] **Step 5: Запустить dev-сервер и проверить что приложение стартует**

```bash
cd /Users/ekaterina/Project/greek-a2/frontend && npm run dev 2>&1 &
sleep 3
curl -s http://localhost:5173 | grep -c "root" || echo "dev server running"
```

Ожидаемый результат: строка с `root` — HTML отдаётся.

- [ ] **Step 6: Запустить все тесты**

```bash
cd /Users/ekaterina/Project/greek-a2/frontend && npm test 2>&1 | tail -10
```

Ожидаемый результат: все тесты зелёные.

- [ ] **Step 7: Commit**

```bash
cd /Users/ekaterina/Project/greek-a2 && git add frontend/src/ && git commit -m "feat(frontend): add BottomNav, routing scaffold, App first-launch logic"
```

---

## Self-Review

**Spec coverage:**
- ✅ React 18 + Vite + TypeScript — Task 1
- ✅ CSS design system (все переменные включая типографику) — Task 2
- ✅ TypeScript API типы для всех endpoints — Task 3
- ✅ Axios client с `X-Telegram-Init-Data` заголовком — Task 4
- ✅ useAppStore (XP, streak, settings, persist) — Task 5
- ✅ useExerciseStore (сессия) — Task 5
- ✅ useSyncQueue (offline-буфер, persist, auto-flush при online) — Task 5
- ✅ useTelegram + useSettings хуки — Task 6
- ✅ Button, ProgressBar, Card, AudioPlayer — Tasks 7–8
- ✅ BottomNav (glassmorphism, скрывается на экранах упражнений) — Task 9
- ✅ React Router v6 + все маршруты — Task 9
- ✅ App first-launch логика (session → placement_status → redirect) — Task 9
- ✅ React Query + QueryClient с offlineFirst — Task 9
- ✅ TDD для стор-логики и компонентов — Tasks 5, 7

**Gaps:** Маршруты `/units/:unitId`, `/units/:unitId/mini-test`, `/units/:unitId/result`, `/vocabulary/review` будут добавлены в Plans 2–4 вместе с реализацией соответствующих экранов.
