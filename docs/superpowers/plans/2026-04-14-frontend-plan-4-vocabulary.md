# Frontend Plan 4: Vocabulary

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Реализовать экраны словаря: VocabularyHomeScreen со статистикой и бейджем due, FlashcardScreen с SM-2 review flow — полностью с дизайном Aegean Midnight.

**Architecture:** `VocabularyHomeScreen` загружает статистику и список карточек к повторению через React Query. `FlashcardScreen` показывает одну карточку за раз: сначала греческое слово, по нажатию — перевод, затем кнопки «Знал» / «Не знал». После каждой оценки POST `/vocabulary/cards/:id/review` с `known: true/false`. По завершении — экран итогов.

**Tech Stack:** React 18, React Router v6, TanStack Query v5, Zustand (useAppStore), Vitest + Testing Library

**Prerequisite:** Plan 1 (Foundation) выполнен.

---

## File Map

| Файл | Назначение |
|------|-----------|
| `frontend/src/features/vocabulary/useVocabularyQuery.ts` | React Query хуки для vocabulary API |
| `frontend/src/features/vocabulary/VocabularyHomeScreen.tsx` | Экран словаря (замена заглушки) |
| `frontend/src/features/vocabulary/FlashcardScreen.tsx` | Экран flashcard review |
| `frontend/src/features/vocabulary/__tests__/VocabularyHomeScreen.test.tsx` | Тесты home screen |
| `frontend/src/features/vocabulary/__tests__/FlashcardScreen.test.tsx` | Тесты flashcard screen |

---

### Task 1: React Query хуки для vocabulary

**Files:**
- Create: `frontend/src/features/vocabulary/useVocabularyQuery.ts`

- [ ] **Step 1: Создать useVocabularyQuery.ts**

```typescript
// frontend/src/features/vocabulary/useVocabularyQuery.ts
import { useQuery } from '@tanstack/react-query'
import { api } from '../../shared/api/endpoints'

export function useVocabStatsQuery() {
  return useQuery({
    queryKey: ['vocab-stats'],
    queryFn: () => api.getVocabStats(),
  })
}

export function useDueCardsQuery() {
  return useQuery({
    queryKey: ['due-cards'],
    queryFn: () => api.getDueCards(),
  })
}
```

- [ ] **Step 2: Проверить, что endpoints.ts содержит нужные функции**

Открыть `frontend/src/shared/api/endpoints.ts` и убедиться, что есть:
- `getVocabStats()` → GET `/api/v1/vocabulary/stats`
- `getDueCards()` → GET `/api/v1/vocabulary/due`
- `reviewCard(cardId: number, knew: boolean)` → POST `/api/v1/vocabulary/cards/:id/review`

Если нет — добавить:
```typescript
getVocabStats: () =>
  apiClient.get<VocabStatsResponse>('/api/v1/vocabulary/stats').then(r => r.data),

getDueCards: () =>
  apiClient.get<DueCardsResponse>('/api/v1/vocabulary/due').then(r => r.data),

reviewCard: (cardId: number, knew: boolean) =>
  apiClient.post<ReviewResponse>(`/api/v1/vocabulary/cards/${cardId}/review`, { known: knew }).then(r => r.data),
```

- [ ] **Step 3: Commit**

```bash
cd /Users/ekaterina/Project/greek-a2 && git add frontend/src/features/vocabulary/useVocabularyQuery.ts frontend/src/shared/api/endpoints.ts && git commit -m "feat(frontend): add vocabulary React Query hooks"
```

---

### Task 2: VocabularyHomeScreen

**Files:**
- Modify: `frontend/src/features/vocabulary/VocabularyHomeScreen.tsx`
- Create: `frontend/src/features/vocabulary/__tests__/VocabularyHomeScreen.test.tsx`

- [ ] **Step 1: Написать тест**

```typescript
// frontend/src/features/vocabulary/__tests__/VocabularyHomeScreen.test.tsx
import { render, screen, waitFor } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { MemoryRouter } from 'react-router-dom'
import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { VocabularyHomeScreen } from '../VocabularyHomeScreen'
import { vi } from 'vitest'

vi.mock('../../../shared/api/endpoints', () => ({
  api: {
    getVocabStats: vi.fn().mockResolvedValue({
      total_cards: 45,
      learned_count: 20,
      due_today: 7,
      new_count: 5,
    }),
    getDueCards: vi.fn().mockResolvedValue({
      due_count: 7,
      cards: [
        { id: 1, word_gr: 'το σπίτι', word_ru: 'дом', audio_path: null, status: 'learning', next_review_at: '2026-04-14' },
      ],
    }),
  },
}))

const createWrapper = () => {
  const queryClient = new QueryClient({ defaultOptions: { queries: { retry: false } } })
  return ({ children }: { children: React.ReactNode }) => (
    <QueryClientProvider client={queryClient}>
      <MemoryRouter>{children}</MemoryRouter>
    </QueryClientProvider>
  )
}

describe('VocabularyHomeScreen', () => {
  it('renders stats after load', async () => {
    render(<VocabularyHomeScreen />, { wrapper: createWrapper() })
    await waitFor(() => {
      expect(screen.getByText('45')).toBeInTheDocument()  // total
      expect(screen.getByText('20')).toBeInTheDocument()  // learned
    })
  })

  it('shows due badge with count', async () => {
    render(<VocabularyHomeScreen />, { wrapper: createWrapper() })
    await waitFor(() => {
      expect(screen.getByText('7')).toBeInTheDocument()
    })
  })

  it('shows review button when due_today > 0', async () => {
    render(<VocabularyHomeScreen />, { wrapper: createWrapper() })
    await waitFor(() => {
      expect(screen.getByRole('button', { name: /επανάληψη|повторить/i })).toBeInTheDocument()
    })
  })
})
```

- [ ] **Step 2: Запустить тест — убедиться, что падает**

```bash
cd /Users/ekaterina/Project/greek-a2/frontend && npx vitest run src/features/vocabulary/__tests__/VocabularyHomeScreen.test.tsx
```

Ожидаемый результат: FAIL.

- [ ] **Step 3: Создать VocabularyHomeScreen.tsx**

```tsx
// frontend/src/features/vocabulary/VocabularyHomeScreen.tsx
import { useNavigate } from 'react-router-dom'
import { useVocabStatsQuery, useDueCardsQuery } from './useVocabularyQuery'
import { Button } from '../../shared/components/Button'

export function VocabularyHomeScreen() {
  const navigate = useNavigate()
  const statsQuery = useVocabStatsQuery()
  const dueQuery = useDueCardsQuery()

  const stats = statsQuery.data
  const dueCount = dueQuery.data?.due_count ?? 0
  const learnedPercent = stats
    ? Math.round((stats.learned_count / Math.max(stats.total_cards, 1)) * 100)
    : 0

  return (
    <div className="vocab-home">
      <h1 className="vocab-home__title">Λεξιλόγιο</h1>

      {/* Stats row */}
      <div className="vocab-home__stats">
        <div className="vocab-stat">
          <span className="vocab-stat__value">{stats?.total_cards ?? '—'}</span>
          <span className="vocab-stat__label">ΣΥΝΟΛΟ</span>
        </div>
        <div className="vocab-stat">
          <span className="vocab-stat__value">{stats?.learned_count ?? '—'}</span>
          <span className="vocab-stat__label">ΕΚΜΑΘΗΣΗ</span>
        </div>
        <div className="vocab-stat">
          <span className="vocab-stat__value">{learnedPercent}%</span>
          <span className="vocab-stat__label">ΠΡΟΟΔΟΣ</span>
        </div>
      </div>

      {/* Due review card */}
      <div className="vocab-home__review-card">
        <div className="vocab-home__review-info">
          <span className="vocab-home__due-badge">{dueCount}</span>
          <div>
            <p className="vocab-home__review-title">Επανάληψη σήμερα</p>
            <p className="vocab-home__review-subtitle">
              {dueCount === 0 ? 'Όλα ενημερωμένα!' : `${dueCount} κάρτες περιμένουν`}
            </p>
          </div>
        </div>

        <Button
          onClick={() => navigate('/vocabulary/review')}
          variant="primary"
          disabled={dueCount === 0}
          fullWidth
        >
          Επανάληψη
        </Button>
      </div>

      {/* New words from curriculum */}
      {(stats?.new_count ?? 0) > 0 && (
        <p className="vocab-home__new-hint">
          +{stats!.new_count} νέες λέξεις από τις τελευταίες ενότητες
        </p>
      )}
    </div>
  )
}
```

Добавить стили в конец `frontend/src/index.css`:
```css
/* VocabularyHomeScreen */
.vocab-home {
  display: flex;
  flex-direction: column;
  padding: 24px 16px calc(80px + env(safe-area-inset-bottom));
  gap: 20px;
  min-height: 100dvh;
  background: var(--color-surface);
}

.vocab-home__title {
  font-size: var(--font-size-headline);
  font-weight: var(--font-weight-bold);
  color: var(--color-on-surface);
}

.vocab-home__stats {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 12px;
}

.vocab-stat {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 4px;
  background: var(--color-surface-high);
  border-radius: var(--radius-card);
  padding: 16px 8px;
}

.vocab-stat__value {
  font-size: var(--font-size-headline);
  font-weight: var(--font-weight-bold);
  color: var(--color-on-surface);
}

.vocab-stat__label {
  font-size: var(--font-size-label);
  font-weight: var(--font-weight-bold);
  color: var(--color-on-surface-muted);
  letter-spacing: 0.05em;
  text-align: center;
}

.vocab-home__review-card {
  background: var(--color-surface-high);
  border-radius: var(--radius-card);
  padding: 20px;
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.vocab-home__review-info {
  display: flex;
  align-items: center;
  gap: 16px;
}

.vocab-home__due-badge {
  font-size: var(--font-size-headline);
  font-weight: var(--font-weight-bold);
  color: var(--color-primary);
  background: rgba(253, 216, 40, 0.15);
  border-radius: 12px;
  padding: 8px 14px;
  min-width: 48px;
  text-align: center;
}

.vocab-home__review-title {
  font-size: var(--font-size-title);
  font-weight: var(--font-weight-medium);
  color: var(--color-on-surface);
}

.vocab-home__review-subtitle {
  font-size: var(--font-size-body);
  color: var(--color-on-surface-muted);
  margin-top: 2px;
}

.vocab-home__new-hint {
  font-size: var(--font-size-body);
  color: var(--color-on-surface-muted);
  text-align: center;
}
```

- [ ] **Step 4: Запустить тест — убедиться, что проходит**

```bash
cd /Users/ekaterina/Project/greek-a2/frontend && npx vitest run src/features/vocabulary/__tests__/VocabularyHomeScreen.test.tsx
```

Ожидаемый результат: все тесты PASS.

- [ ] **Step 5: Commit**

```bash
cd /Users/ekaterina/Project/greek-a2 && git add frontend/src/features/vocabulary/VocabularyHomeScreen.tsx frontend/src/features/vocabulary/__tests__/VocabularyHomeScreen.test.tsx frontend/src/index.css && git commit -m "feat(frontend): add VocabularyHomeScreen"
```

---

### Task 3: FlashcardScreen

**Files:**
- Create: `frontend/src/features/vocabulary/FlashcardScreen.tsx`
- Create: `frontend/src/features/vocabulary/__tests__/FlashcardScreen.test.tsx`

Поток:
1. Загрузить due cards из `useDueCardsQuery()`
2. Показать лицевую сторону карточки (греческое слово + иконка аудио если есть)
3. По нажатию «Показать» → перевернуть карточку, показать перевод
4. Показать кнопки «Знал ✓» / «Не знал ✗»
5. POST review → следующая карточка
6. После последней — экран итогов

- [ ] **Step 1: Написать тест**

```typescript
// frontend/src/features/vocabulary/__tests__/FlashcardScreen.test.tsx
import { render, screen, waitFor } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { MemoryRouter } from 'react-router-dom'
import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { FlashcardScreen } from '../FlashcardScreen'
import { vi } from 'vitest'

const mockCards = [
  { id: 1, word_gr: 'το σπίτι', word_ru: 'дом', audio_path: null, status: 'learning', next_review_at: '2026-04-14' },
  { id: 2, word_gr: 'η θάλασσα', word_ru: 'море', audio_path: null, status: 'new', next_review_at: '2026-04-14' },
]

vi.mock('../../../shared/api/endpoints', () => ({
  api: {
    getDueCards: vi.fn().mockResolvedValue({ due_count: 2, cards: mockCards }),
    reviewCard: vi.fn().mockResolvedValue({
      card_id: 1,
      new_status: 'learned',
      next_review_at: '2026-04-21',
      interval_days: 7,
      xp_earned: 5,
    }),
  },
}))

const createWrapper = () => {
  const queryClient = new QueryClient({ defaultOptions: { queries: { retry: false } } })
  return ({ children }: { children: React.ReactNode }) => (
    <QueryClientProvider client={queryClient}>
      <MemoryRouter>{children}</MemoryRouter>
    </QueryClientProvider>
  )
}

describe('FlashcardScreen', () => {
  it('shows front of card (greek word) after load', async () => {
    render(<FlashcardScreen />, { wrapper: createWrapper() })
    await waitFor(() => {
      expect(screen.getByText('το σπίτι')).toBeInTheDocument()
    })
  })

  it('hides translation initially', async () => {
    render(<FlashcardScreen />, { wrapper: createWrapper() })
    await waitFor(() => screen.getByText('το σπίτι'))
    expect(screen.queryByText('дом')).not.toBeInTheDocument()
  })

  it('shows translation after clicking Показать', async () => {
    render(<FlashcardScreen />, { wrapper: createWrapper() })
    await waitFor(() => screen.getByText('το σπίτι'))
    await userEvent.click(screen.getByRole('button', { name: /εμφάνιση|показать/i }))
    expect(screen.getByText('дом')).toBeInTheDocument()
  })

  it('shows Знал/Не знал buttons after flipping', async () => {
    render(<FlashcardScreen />, { wrapper: createWrapper() })
    await waitFor(() => screen.getByText('το σπίτι'))
    await userEvent.click(screen.getByRole('button', { name: /εμφάνιση|показать/i }))
    expect(screen.getByRole('button', { name: /ήξερα|знал/i })).toBeInTheDocument()
    expect(screen.getByRole('button', { name: /δεν ήξερα|не знал/i })).toBeInTheDocument()
  })

  it('advances to next card after rating', async () => {
    render(<FlashcardScreen />, { wrapper: createWrapper() })
    await waitFor(() => screen.getByText('το σπίτι'))
    await userEvent.click(screen.getByRole('button', { name: /εμφάνιση|показать/i }))
    await userEvent.click(screen.getByRole('button', { name: /ήξερα|знал/i }))
    await waitFor(() => {
      expect(screen.getByText('η θάλασσα')).toBeInTheDocument()
    })
  })

  it('shows completion screen after last card', async () => {
    render(<FlashcardScreen />, { wrapper: createWrapper() })
    // Card 1
    await waitFor(() => screen.getByText('το σπίτι'))
    await userEvent.click(screen.getByRole('button', { name: /εμφάνιση|показать/i }))
    await userEvent.click(screen.getByRole('button', { name: /ήξερα|знал/i }))
    // Card 2
    await waitFor(() => screen.getByText('η θάλασσα'))
    await userEvent.click(screen.getByRole('button', { name: /εμφάνιση|показать/i }))
    await userEvent.click(screen.getByRole('button', { name: /ήξερα|знал/i }))
    // Done
    await waitFor(() => {
      expect(screen.getByText(/τέλος|готово|завершено/i)).toBeInTheDocument()
    })
  })
})
```

- [ ] **Step 2: Запустить тест — убедиться, что падает**

```bash
cd /Users/ekaterina/Project/greek-a2/frontend && npx vitest run src/features/vocabulary/__tests__/FlashcardScreen.test.tsx
```

Ожидаемый результат: FAIL.

- [ ] **Step 3: Создать FlashcardScreen.tsx**

```tsx
// frontend/src/features/vocabulary/FlashcardScreen.tsx
import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { useDueCardsQuery } from './useVocabularyQuery'
import { api } from '../../shared/api/endpoints'
import { AudioPlayer } from '../../shared/components/AudioPlayer'
import { Button } from '../../shared/components/Button'
import { ProgressBar } from '../../shared/components/ProgressBar'
import { useAppStore } from '../../shared/store/useAppStore'
import { useTelegram } from '../../shared/hooks/useTelegram'

type FlashcardPhase = 'front' | 'back' | 'done'

export function FlashcardScreen() {
  const navigate = useNavigate()
  const dueQuery = useDueCardsQuery()
  const addXp = useAppStore(s => s.addXp)
  const { haptic } = useTelegram()

  const [currentIndex, setCurrentIndex] = useState(0)
  const [phase, setPhase] = useState<FlashcardPhase>('front')
  const [totalXp, setTotalXp] = useState(0)
  const [knewCount, setKnewCount] = useState(0)

  if (dueQuery.isLoading) return <div className="screen-loading">Φόρτωση...</div>

  const cards = dueQuery.data?.cards ?? []
  const total = cards.length
  const card = cards[currentIndex]

  if (phase === 'done' || total === 0) {
    return (
      <div className="flashcard-done">
        <div className="flashcard-done__icon">🎉</div>
        <h1 className="flashcard-done__title">Τέλος!</h1>
        <p className="flashcard-done__subtitle">
          {knewCount} / {total} — {totalXp} XP
        </p>
        <Button onClick={() => navigate('/vocabulary')} variant="primary" fullWidth>
          Назад к словарю
        </Button>
      </div>
    )
  }

  const handleFlip = () => {
    haptic.impact()
    setPhase('back')
  }

  const handleReview = async (knew: boolean) => {
    haptic.notification(knew ? 'success' : 'error')
    try {
      const result = await api.reviewCard(card.id, knew)
      if (result.xp_earned > 0) {
        addXp(result.xp_earned)
        setTotalXp(x => x + result.xp_earned)
      }
      if (knew) setKnewCount(k => k + 1)
    } catch {
      // offline — progress lost, but don't crash
    }

    if (currentIndex + 1 >= total) {
      setPhase('done')
    } else {
      setCurrentIndex(i => i + 1)
      setPhase('front')
    }
  }

  return (
    <div className="flashcard-screen">
      <div className="flashcard-screen__header">
        <ProgressBar value={currentIndex} max={total} />
        <span className="flashcard-screen__counter">{currentIndex + 1} / {total}</span>
      </div>

      <div className={`flashcard ${phase === 'back' ? 'flashcard--flipped' : ''}`}>
        <div className="flashcard__front">
          <p className="flashcard__word">{card.word_gr}</p>
          {card.audio_path && (
            <AudioPlayer src={card.audio_path} ariaLabel="аудио" />
          )}
        </div>

        {phase === 'back' && (
          <div className="flashcard__back">
            <p className="flashcard__word">{card.word_gr}</p>
            <p className="flashcard__translation">{card.word_ru}</p>
          </div>
        )}
      </div>

      <div className="flashcard-screen__actions">
        {phase === 'front' && (
          <Button onClick={handleFlip} variant="primary" fullWidth>
            Εμφάνιση
          </Button>
        )}

        {phase === 'back' && (
          <div className="flashcard-screen__rating">
            <button className="rating-btn rating-btn--no" onClick={() => handleReview(false)}>
              ✗ Δεν ήξερα
            </button>
            <button className="rating-btn rating-btn--yes" onClick={() => handleReview(true)}>
              ✓ Ήξερα
            </button>
          </div>
        )}
      </div>
    </div>
  )
}
```

Добавить стили в конец `frontend/src/index.css`:
```css
/* FlashcardScreen */
.flashcard-screen {
  display: flex;
  flex-direction: column;
  min-height: 100dvh;
  padding: 16px 16px calc(16px + env(safe-area-inset-bottom));
  background: var(--color-surface);
  gap: 16px;
}

.flashcard-screen__header {
  display: flex;
  align-items: center;
  gap: 12px;
}

.flashcard-screen__counter {
  font-size: var(--font-size-label);
  font-weight: var(--font-weight-medium);
  color: var(--color-on-surface-muted);
  white-space: nowrap;
}

.flashcard {
  flex: 1;
  background: var(--color-surface-high);
  border-radius: var(--radius-card);
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 32px 24px;
  gap: 20px;
  min-height: 240px;
}

.flashcard__word {
  font-size: var(--font-size-headline);
  font-weight: var(--font-weight-bold);
  color: var(--color-on-surface);
  text-align: center;
  line-height: var(--line-height-tight);
}

.flashcard__translation {
  font-size: var(--font-size-title);
  color: var(--color-secondary);
  text-align: center;
}

.flashcard-screen__actions {
  margin-top: auto;
}

.flashcard-screen__rating {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 12px;
}

.rating-btn {
  padding: 18px;
  border: none;
  border-radius: var(--radius-button);
  font-family: var(--font-family);
  font-size: var(--font-size-body);
  font-weight: var(--font-weight-bold);
  cursor: pointer;
  transition: opacity 0.15s;
}

.rating-btn--no {
  background: var(--color-surface-highest);
  color: var(--color-error);
}

.rating-btn--yes {
  background: var(--color-primary);
  color: #000;
}

/* FlashcardDone */
.flashcard-done {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  min-height: 100dvh;
  padding: 32px 24px;
  gap: 16px;
  background: var(--color-surface);
  text-align: center;
}

.flashcard-done__icon {
  font-size: var(--font-size-display);
}

.flashcard-done__title {
  font-size: var(--font-size-headline);
  font-weight: var(--font-weight-bold);
  color: var(--color-primary);
}

.flashcard-done__subtitle {
  font-size: var(--font-size-body);
  color: var(--color-on-surface-muted);
}
```

- [ ] **Step 4: Запустить тест — убедиться, что проходит**

```bash
cd /Users/ekaterina/Project/greek-a2/frontend && npx vitest run src/features/vocabulary/__tests__/FlashcardScreen.test.tsx
```

Ожидаемый результат: все тесты PASS.

- [ ] **Step 5: Commit**

```bash
cd /Users/ekaterina/Project/greek-a2 && git add frontend/src/features/vocabulary/FlashcardScreen.tsx frontend/src/features/vocabulary/__tests__/FlashcardScreen.test.tsx frontend/src/index.css && git commit -m "feat(frontend): add FlashcardScreen with SM-2 review flow"
```

---

### Task 4: Финальная проверка и интеграция

- [ ] **Step 1: Проверить маршруты vocabulary в App.tsx**

Открыть `frontend/src/App.tsx`. Убедиться, что есть маршруты:
```tsx
<Route path="/vocabulary" element={<VocabularyHomeScreen />} />
<Route path="/vocabulary/review" element={<FlashcardScreen />} />
```

Если нет — добавить вместе с импортами:
```tsx
import { VocabularyHomeScreen } from './features/vocabulary/VocabularyHomeScreen'
import { FlashcardScreen } from './features/vocabulary/FlashcardScreen'
```

- [ ] **Step 2: Запустить все тесты**

```bash
cd /Users/ekaterina/Project/greek-a2/frontend && npx vitest run
```

Ожидаемый результат: все тесты PASS.

- [ ] **Step 3: Проверить TypeScript**

```bash
cd /Users/ekaterina/Project/greek-a2/frontend && npx tsc --noEmit
```

Ожидаемый результат: нет ошибок.

- [ ] **Step 4: Финальный commit**

```bash
cd /Users/ekaterina/Project/greek-a2 && git add frontend/src/App.tsx && git commit -m "feat(frontend): wire vocabulary routes in App.tsx"
```
