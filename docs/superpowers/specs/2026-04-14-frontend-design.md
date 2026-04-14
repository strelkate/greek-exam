# Frontend Design Spec: Greek Learning Telegram Mini App
**Дата:** 2026-04-14
**Статус:** Утверждён
**На основе:** [Product Brief](product-brief.md), [Architecture RFC](architecture-rfc.md)

---

## Скоуп первой итерации

Полированная реализация следующих экранов:
1. Placement test (первый запуск)
2. Карта уровней (A1 / A2 / B1)
3. Детали юнита
4. Все 7 типов упражнений
5. Мини-тест + экран результата юнита
6. Словарь (главная + flashcard review)

---

## Стек

| Инструмент | Роль |
|---|---|
| React 18 + Vite + TypeScript | UI, сборка |
| React Router v6 | Роутинг |
| TanStack Query v5 | Серверные данные, кэш, offline-first |
| Zustand + persist middleware | Клиентское состояние, offline-буфер |
| `@twa-dev/sdk` | Telegram Mini App SDK |
| Axios | HTTP-клиент |

---

## Структура проекта

```
src/
  features/
    placement/
      PlacementScreen.tsx
      usePlacementStore.ts
    curriculum/
      LevelMapScreen.tsx
      UnitDetailScreen.tsx
      useCurriculumQuery.ts
    exercises/
      ExerciseScreen.tsx
      ExerciseShell.tsx
      types/
        TrueFalse.tsx
        Matching.tsx
        MultipleChoice.tsx
        FillBlank.tsx
        ImageDescription.tsx
        Dialogue.tsx
      MiniTestScreen.tsx
      UnitResultScreen.tsx
      useExerciseStore.ts
    vocabulary/
      VocabularyHomeScreen.tsx
      FlashcardScreen.tsx
      useVocabularyQuery.ts
  shared/
    components/
      Button.tsx
      Card.tsx
      ProgressBar.tsx
      AudioPlayer.tsx
    hooks/
      useTelegram.ts
      useAudio.ts
      useSettings.ts
    api/
      client.ts          ← axios instance с Authorization: initData
      endpoints.ts
    store/
      useAppStore.ts     ← XP, streak, settings (persist)
      useSyncQueue.ts    ← offline-буфер (persist)
  App.tsx
  main.tsx
  index.css             ← CSS-переменные дизайн-системы
```

---

## Роутинг

```
/                              → редирект: /placement или /levels
/placement                     ← PlacementScreen
/levels                        ← LevelMapScreen
/units/:unitId                 ← UnitDetailScreen
/units/:unitId/exercise/:exerciseId  ← ExerciseScreen
/units/:unitId/mini-test       ← MiniTestScreen
/units/:unitId/result          ← UnitResultScreen
/vocabulary                    ← VocabularyHomeScreen
/vocabulary/review             ← FlashcardScreen
```

---

## Управление состоянием

### React Query (серверные данные)

```ts
useUnitsQuery()           → GET /curriculum
useUnitDetailQuery(id)    → GET /curriculum/:id/exercises
useVocabularyQuery()      → GET /vocabulary/due
usePlacementQuery()       → GET /placement-test
```

Конфигурация: `staleTime: 5min`, `gcTime: 24h`, `networkMode: 'offlineFirst'`.

### Zustand (три стора)

**`useAppStore`** (persist):
```ts
{
  user: { xp: number, streak: number, streakDate: string },
  settings: { showTranslations: boolean },
}
```

**`useExerciseStore`** (не persist — только сессия):
```ts
{
  currentIndex: number,
  answers: Answer[],
  isComplete: boolean,
  submitAnswer(isCorrect: boolean): void,
  nextExercise(): void,
  resetSession(): void,
}
```

**`useSyncQueue`** (persist):
```ts
{
  queue: ProgressEvent[],
  enqueue(event: ProgressEvent): void,
  flush(): Promise<void>,   // POST /sync/progress
}
```

---

## API слой

`shared/api/client.ts` — axios instance:
- Header `Authorization: <initData>` на каждый запрос
- Перехватчик ошибок: при отсутствии сети → `useSyncQueue.enqueue()` вместо выброса ошибки

`shared/api/endpoints.ts`:
```ts
postProgress(unitId, exerciseId, isCorrect)
postSync(queue: ProgressEvent[])
patchSettings(payload)
postPlacementComplete(score)
```

---

## Offline-стратегия

- **Упражнения** кэшируются React Query (`networkMode: 'offlineFirst'`) — доступны без сети
- **Прогресс** при офлайн попадает в `useSyncQueue` (localStorage)
- При `window.addEventListener('online')` → `useSyncQueue.flush()` → `POST /sync/progress`
- **Статика** (аудио, SVG) — Service Worker (Workbox, cache-first)

---

## Telegram-интеграция

`shared/hooks/useTelegram.ts`:
```ts
{
  user: { id, firstName, languageCode },
  initData: string,
  backButton: { show(), hide(), onClick() },
  haptic: { impact(), notification() },
}
```

- **Back Button** подключён к `navigate(-1)` React Router
- **Haptic feedback:** `impact` на тап по ответу, `notification('success'/'error')` на результат

**Первый запуск:**
```
App монтируется
  → GET /users/me  (создаёт пользователя по initData если нет)
  → user.placement_completed?
      нет  → /placement
      да   → /levels
```

---

## Дизайн-система: Aegean Midnight

CSS-переменные в `index.css` (на основе `/stitch/aegean_midnight/`):

```css
--color-surface:           #0b0d1a;
--color-surface-low:       #101221;
--color-surface-high:      #1c1e30;
--color-surface-highest:   #222537;
--color-primary:           #fdd828;
--color-secondary:         #caccf7;
--color-on-surface:        #ffffff;
--font-family:             'Plus Jakarta Sans', sans-serif;
--radius-card:             16px;
--radius-button:           12px;
```

Правила:
- Никаких хардкодных цветов — только переменные
- Никаких `border: 1px solid` — границы через разницу фонов
- Glassmorphism для навигации: `backdrop-filter: blur(12px)`, opacity 70%

---

## Поток упражнения

```
UnitDetailScreen
  → ExerciseScreen [0..N]
      ExerciseShell (прогресс, аудио, инструкция)
        └── <TrueFalse|Matching|MultipleChoice|FillBlank|ImageDescription|Dialogue />
      onComplete(isCorrect) → enqueue progress → feedback overlay 1.5s
  → MiniTestScreen (5 вопросов, типы 1/3/4)
  → UnitResultScreen (XP +25, стрик, кнопка "На карту")
```

**ExerciseShell** — общая обёртка всех типов:
- Прогресс-бар (X из N)
- Кнопка аудио (если `audio_path` не null)
- Инструкция (греческий + перевод или только греческий, из `useSettings`)
- Слот для контента типа
- Кнопка "Проверить" / "Далее"

---

## Что НЕ входит в эту итерацию

- Экран профиля / статистики
- Онбординг-тур
- Push-уведомления о стрике
- Анимации переходов между экранами (кроме feedback overlay)
