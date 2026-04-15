# Frontend Plan 2: Curriculum + Placement

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Реализовать экраны Placement Test, карты уровней (Level Map) и деталей юнита (Unit Detail) — полностью, с данными из API и дизайном Aegean Midnight.

**Architecture:** Каждый экран — отдельный компонент в `src/features/`. React Query хуки для серверных данных. Placement test управляет локальным состоянием через useState, результат отправляется одним запросом в конце.

**Tech Stack:** React 18, React Router v6, TanStack Query v5, Zustand (useAppStore), Axios, Vitest + Testing Library

**Prerequisite:** Plan 1 (Foundation) выполнен.

---

## File Map

| Файл | Назначение |
|------|-----------|
| `frontend/src/features/placement/usePlacementStore.ts` | Локальное состояние placement теста |
| `frontend/src/features/placement/PlacementScreen.tsx` | Экран placement теста (замена заглушки) |
| `frontend/src/features/placement/components/PlacementQuestion.tsx` | Рендер одного вопроса placement |
| `frontend/src/features/curriculum/useCurriculumQuery.ts` | React Query хуки для curriculum API |
| `frontend/src/features/curriculum/LevelMapScreen.tsx` | Экран карты уровней (замена заглушки) |
| `frontend/src/features/curriculum/UnitDetailScreen.tsx` | Экран деталей юнита |
| `frontend/src/features/curriculum/components/LevelSection.tsx` | Секция одного уровня на карте |
| `frontend/src/features/curriculum/components/UnitCard.tsx` | Карточка юнита |
| `frontend/src/App.tsx` | Добавить маршруты `/units/:unitId` |
| `frontend/src/features/placement/__tests__/PlacementScreen.test.tsx` | Тесты placement |
| `frontend/src/features/curriculum/__tests__/LevelMapScreen.test.tsx` | Тесты level map |
| `frontend/src/features/curriculum/__tests__/UnitDetailScreen.test.tsx` | Тесты unit detail |

---

### Task 1: React Query хуки для curriculum

**Files:**
- Create: `frontend/src/features/curriculum/useCurriculumQuery.ts`

- [ ] **Step 1: Создать useCurriculumQuery.ts**

```typescript
// frontend/src/features/curriculum/useCurriculumQuery.ts
import { useQuery } from '@tanstack/react-query'
import { api } from '../../shared/api/endpoints'

export function useLevelsQuery() {
  return useQuery({
    queryKey: ['levels'],
    queryFn: () => api.getLevels(),
  })
}

export function useUnitsQuery(level: string) {
  return useQuery({
    queryKey: ['units', level],
    queryFn: () => api.getUnits(level),
    enabled: Boolean(level),
  })
}

export function useUnitDetailQuery(unitId: number) {
  return useQuery({
    queryKey: ['unit', unitId],
    queryFn: () => api.getUnitDetail(unitId),
    enabled: Boolean(unitId),
  })
}
```

- [ ] **Step 2: Commit**

```bash
cd /Users/ekaterina/Project/greek-a2 && git add frontend/src/features/curriculum/useCurriculumQuery.ts && git commit -m "feat(frontend): add curriculum React Query hooks"
```

---

### Task 2: Placement Test — локальный стор

**Files:**
- Create: `frontend/src/features/placement/usePlacementStore.ts`

- [ ] **Step 1: Создать usePlacementStore.ts**

```typescript
// frontend/src/features/placement/usePlacementStore.ts
import { create } from 'zustand'
import type { PlacementQuestion } from '../../shared/api/types'

interface PlacementState {
  questions: PlacementQuestion[]
  currentIndex: number
  correctCount: number
  isFinished: boolean

  setQuestions: (questions: PlacementQuestion[]) => void
  submitAnswer: (isCorrect: boolean) => void
  skip: () => void
  reset: () => void
}

export const usePlacementStore = create<PlacementState>()((set, get) => ({
  questions: [],
  currentIndex: 0,
  correctCount: 0,
  isFinished: false,

  setQuestions: (questions) => set({ questions, currentIndex: 0, correctCount: 0, isFinished: false }),

  submitAnswer: (isCorrect) => {
    const { currentIndex, questions, correctCount } = get()
    const next = currentIndex + 1
    set({
      correctCount: isCorrect ? correctCount + 1 : correctCount,
      currentIndex: next,
      isFinished: next >= questions.length,
    })
  },

  skip: () => set({ isFinished: true }),

  reset: () => set({ questions: [], currentIndex: 0, correctCount: 0, isFinished: false }),
}))
```

- [ ] **Step 2: Commit**

```bash
cd /Users/ekaterina/Project/greek-a2 && git add frontend/src/features/placement/usePlacementStore.ts && git commit -m "feat(frontend): add placement test store"
```

---

### Task 3: PlacementQuestion компонент

**Files:**
- Create: `frontend/src/features/placement/components/PlacementQuestion.tsx`
- Create: `frontend/src/features/placement/components/PlacementQuestion.module.css`

- [ ] **Step 1: Написать тест**

Создать `frontend/src/features/placement/__tests__/PlacementQuestion.test.tsx`:
```typescript
import { describe, expect, it, vi } from 'vitest'
import { render, screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { PlacementQuestion } from '../components/PlacementQuestion'

const mcQuestion = {
  id: 1,
  type: 'multiple_choice' as const,
  content: {
    question: 'Τι είναι αυτό;',
    options: [
      { id: 'a', text: 'Σπίτι' },
      { id: 'b', text: 'Αυτοκίνητο' },
      { id: 'c', text: 'Σχολείο' },
    ],
    correct_id: 'a',
  },
}

describe('PlacementQuestion', () => {
  it('рендерит вопрос multiple_choice', () => {
    render(<PlacementQuestion question={mcQuestion} onAnswer={vi.fn()} />)
    expect(screen.getByText('Τι είναι αυτό;')).toBeInTheDocument()
    expect(screen.getByText('Σπίτι')).toBeInTheDocument()
    expect(screen.getByText('Αυτοκίνητο')).toBeInTheDocument()
  })

  it('вызывает onAnswer(true) при правильном ответе', async () => {
    const onAnswer = vi.fn()
    render(<PlacementQuestion question={mcQuestion} onAnswer={onAnswer} />)
    await userEvent.click(screen.getByText('Σπίτι'))
    await userEvent.click(screen.getByRole('button', { name: /проверить/i }))
    expect(onAnswer).toHaveBeenCalledWith(true)
  })

  it('вызывает onAnswer(false) при неправильном ответе', async () => {
    const onAnswer = vi.fn()
    render(<PlacementQuestion question={mcQuestion} onAnswer={onAnswer} />)
    await userEvent.click(screen.getByText('Αυτοκίνητο'))
    await userEvent.click(screen.getByRole('button', { name: /проверить/i }))
    expect(onAnswer).toHaveBeenCalledWith(false)
  })
})
```

- [ ] **Step 2: Запустить тест — убедиться что падает**

```bash
cd /Users/ekaterina/Project/greek-a2/frontend && npm test -- PlacementQuestion 2>&1 | tail -5
```

- [ ] **Step 3: Создать PlacementQuestion.tsx**

```typescript
// frontend/src/features/placement/components/PlacementQuestion.tsx
import { useState } from 'react'
import { Button } from '../../../shared/components/Button'
import type { PlacementQuestion as TPlacementQuestion } from '../../../shared/api/types'
import styles from './PlacementQuestion.module.css'

interface Props {
  question: TPlacementQuestion
  onAnswer: (isCorrect: boolean) => void
}

export function PlacementQuestion({ question, onAnswer }: Props) {
  const [selected, setSelected] = useState<string | null>(null)
  const [checked, setChecked] = useState(false)

  const handleCheck = () => {
    if (!selected) return
    setChecked(true)
    const isCorrect = (() => {
      if (question.type === 'multiple_choice') {
        return selected === (question.content as { correct_id: string }).correct_id
      }
      if (question.type === 'true_false') {
        const stmt = (question.content as { statements: Array<{ id: number; correct: boolean }> }).statements[0]
        return (selected === 'true') === stmt.correct
      }
      if (question.type === 'fill_blank') {
        const blank = (question.content as { blanks: Array<{ correct: string }> }).blanks[0]
        return selected === blank.correct
      }
      return false
    })()

    setTimeout(() => {
      setSelected(null)
      setChecked(false)
      onAnswer(isCorrect)
    }, 800)
  }

  if (question.type === 'multiple_choice') {
    const c = question.content as { question: string; options: Array<{ id: string; text: string }>; correct_id: string }
    return (
      <div className={styles.container}>
        <p className={styles.question}>{c.question}</p>
        <div className={styles.options}>
          {c.options.map(opt => (
            <button
              key={opt.id}
              className={[
                styles.option,
                selected === opt.id ? styles.selected : '',
                checked && opt.id === c.correct_id ? styles.correct : '',
                checked && selected === opt.id && opt.id !== c.correct_id ? styles.wrong : '',
              ].join(' ')}
              onClick={() => !checked && setSelected(opt.id)}
            >
              {opt.text}
            </button>
          ))}
        </div>
        <Button fullWidth disabled={!selected || checked} onClick={handleCheck}>
          Проверить
        </Button>
      </div>
    )
  }

  if (question.type === 'true_false') {
    const c = question.content as { text: string; statements: Array<{ id: number; text: string; correct: boolean }> }
    return (
      <div className={styles.container}>
        <p className={styles.passage}>{c.text}</p>
        {c.statements.map(stmt => (
          <div key={stmt.id} className={styles.tfStatement}>
            <p className={styles.question}>{stmt.text}</p>
            <div className={styles.options}>
              {(['true', 'false'] as const).map(val => (
                <button
                  key={val}
                  className={[
                    styles.option,
                    selected === val ? styles.selected : '',
                    checked && (val === 'true') === stmt.correct ? styles.correct : '',
                    checked && selected === val && (val === 'true') !== stmt.correct ? styles.wrong : '',
                  ].join(' ')}
                  onClick={() => !checked && setSelected(val)}
                >
                  {val === 'true' ? 'ΣΩΣΤΟ' : 'ΛΑΘΟΣ'}
                </button>
              ))}
            </div>
          </div>
        ))}
        <Button fullWidth disabled={!selected || checked} onClick={handleCheck}>
          Проверить
        </Button>
      </div>
    )
  }

  if (question.type === 'fill_blank') {
    const c = question.content as { text_template: string; word_bank: string[]; blanks: Array<{ correct: string }> }
    return (
      <div className={styles.container}>
        <p className={styles.question}>{c.text_template.replace('___', '______')}</p>
        <div className={styles.options}>
          {c.word_bank.map(word => (
            <button
              key={word}
              className={[
                styles.option,
                selected === word ? styles.selected : '',
                checked && word === c.blanks[0].correct ? styles.correct : '',
                checked && selected === word && word !== c.blanks[0].correct ? styles.wrong : '',
              ].join(' ')}
              onClick={() => !checked && setSelected(word)}
            >
              {word}
            </button>
          ))}
        </div>
        <Button fullWidth disabled={!selected || checked} onClick={handleCheck}>
          Проверить
        </Button>
      </div>
    )
  }

  return null
}
```

Создать `frontend/src/features/placement/components/PlacementQuestion.module.css`:
```css
.container {
  display: flex;
  flex-direction: column;
  gap: var(--spacing-md);
}

.passage {
  font-size: var(--font-size-body);
  line-height: var(--line-height-normal);
  color: var(--color-on-surface-muted);
  background: var(--color-surface-high);
  border-radius: var(--radius-sm);
  padding: var(--spacing-md);
}

.question {
  font-size: var(--font-size-title);
  font-weight: var(--font-weight-medium);
  line-height: var(--line-height-tight);
  color: var(--color-on-surface);
}

.tfStatement {
  display: flex;
  flex-direction: column;
  gap: var(--spacing-sm);
}

.options {
  display: flex;
  flex-direction: column;
  gap: var(--spacing-sm);
}

.option {
  padding: 14px var(--spacing-md);
  background: var(--color-surface-high);
  border: 2px solid transparent;
  border-radius: var(--radius-sm);
  color: var(--color-on-surface);
  font-family: var(--font-family);
  font-size: var(--font-size-body);
  text-align: left;
  cursor: pointer;
  transition: border-color 0.15s, background 0.15s;
}

.option.selected {
  border-color: var(--color-primary);
}

.option.correct {
  border-color: var(--color-success);
  background: rgba(74, 222, 128, 0.1);
}

.option.wrong {
  border-color: var(--color-error);
  background: rgba(248, 113, 113, 0.1);
}
```

- [ ] **Step 4: Запустить тест — убедиться что проходит**

```bash
cd /Users/ekaterina/Project/greek-a2/frontend && npm test -- PlacementQuestion 2>&1 | tail -10
```

Ожидаемый результат: 3 теста зелёных.

- [ ] **Step 5: Commit**

```bash
cd /Users/ekaterina/Project/greek-a2 && git add frontend/src/features/placement/ && git commit -m "feat(frontend): add PlacementQuestion component with TF/MC/FB support"
```

---

### Task 4: PlacementScreen

**Files:**
- Modify: `frontend/src/features/placement/PlacementScreen.tsx`
- Create: `frontend/src/features/placement/PlacementScreen.module.css`

- [ ] **Step 1: Написать тест**

Создать `frontend/src/features/placement/__tests__/PlacementScreen.test.tsx`:
```typescript
import { describe, expect, it, vi } from 'vitest'
import { render, screen, waitFor } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { MemoryRouter } from 'react-router-dom'
import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { PlacementScreen } from '../PlacementScreen'

vi.mock('../../../shared/api/endpoints', () => ({
  api: {
    getPlacementQuestions: vi.fn().mockResolvedValue({
      questions: [
        {
          id: 1,
          type: 'multiple_choice',
          content: {
            question: 'Τι είναι αυτό;',
            options: [{ id: 'a', text: 'Σπίτι' }, { id: 'b', text: 'Αυτοκίνητο' }],
            correct_id: 'a',
          },
        },
      ],
    }),
    completePlacementTest: vi.fn().mockResolvedValue({
      placement_status: 'failed',
      a1_skipped: false,
      message: 'Начинаете с A1.',
    }),
  },
}))

const mockNavigate = vi.fn()
vi.mock('react-router-dom', async () => {
  const actual = await vi.importActual('react-router-dom')
  return { ...actual, useNavigate: () => mockNavigate }
})

function wrapper({ children }: { children: React.ReactNode }) {
  const qc = new QueryClient({ defaultOptions: { queries: { retry: false } } })
  return <QueryClientProvider client={qc}><MemoryRouter>{children}</MemoryRouter></QueryClientProvider>
}

describe('PlacementScreen', () => {
  it('показывает кнопку Пропустить', async () => {
    render(<PlacementScreen />, { wrapper })
    await waitFor(() => expect(screen.getByText(/пропустить/i)).toBeInTheDocument())
  })

  it('Пропустить завершает тест и редиректит на /levels', async () => {
    render(<PlacementScreen />, { wrapper })
    await waitFor(() => screen.getByText(/пропустить/i))
    await userEvent.click(screen.getByText(/пропустить/i))
    await waitFor(() => expect(mockNavigate).toHaveBeenCalledWith('/levels', expect.anything()))
  })
})
```

- [ ] **Step 2: Запустить тест — убедиться что падает**

```bash
cd /Users/ekaterina/Project/greek-a2/frontend && npm test -- PlacementScreen 2>&1 | tail -5
```

- [ ] **Step 3: Создать PlacementScreen.tsx**

```typescript
// frontend/src/features/placement/PlacementScreen.tsx
import { useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import { useQuery, useMutation } from '@tanstack/react-query'
import { api } from '../../shared/api/endpoints'
import { usePlacementStore } from './usePlacementStore'
import { useAppStore } from '../../shared/store/useAppStore'
import { ProgressBar } from '../../shared/components/ProgressBar'
import { Button } from '../../shared/components/Button'
import { PlacementQuestion } from './components/PlacementQuestion'
import styles from './PlacementScreen.module.css'

export function PlacementScreen() {
  const navigate = useNavigate()
  const hydrate = useAppStore((s) => s.hydrate)
  const xp = useAppStore((s) => s.xp)
  const streak = useAppStore((s) => s.streak)
  const showTranslations = useAppStore((s) => s.showTranslations)

  const { setQuestions, submitAnswer, skip, questions, currentIndex, correctCount, isFinished } = usePlacementStore()

  const { data, isLoading } = useQuery({
    queryKey: ['placement-questions'],
    queryFn: () => api.getPlacementQuestions(),
  })

  const completeMutation = useMutation({
    mutationFn: ({ score, total, skipped }: { score: number; total: number; skipped: boolean }) =>
      api.completePlacementTest(score, total, skipped),
    onSuccess: () => navigate('/levels', { replace: true }),
  })

  useEffect(() => {
    if (data?.questions) setQuestions(data.questions)
  }, [data, setQuestions])

  useEffect(() => {
    if (isFinished && questions.length > 0) {
      completeMutation.mutate({ score: correctCount, total: questions.length, skipped: false })
    }
  }, [isFinished]) // eslint-disable-line react-hooks/exhaustive-deps

  const handleSkip = () => {
    skip()
    completeMutation.mutate({ score: 0, total: 1, skipped: true })
  }

  if (isLoading) {
    return (
      <div className={styles.screen}>
        <div className={styles.loading}>Загрузка...</div>
      </div>
    )
  }

  const currentQuestion = questions[currentIndex]

  return (
    <div className={styles.screen}>
      <div className={styles.header}>
        <ProgressBar value={currentIndex} max={questions.length} />
        <p className={styles.counter}>{currentIndex} / {questions.length}</p>
      </div>

      <div className={styles.content}>
        <h1 className={styles.title}>
          {showTranslations ? 'Тест на размещение (Τεστ τοποθέτησης)' : 'Τεστ τοποθέτησης'}
        </h1>
        <p className={styles.subtitle}>
          {showTranslations
            ? 'Ответь на вопросы, чтобы пропустить A1'
            : 'Απάντησε στις ερωτήσεις για να παρακάμψεις το A1'}
        </p>

        {currentQuestion && !isFinished && (
          <PlacementQuestion
            key={currentQuestion.id}
            question={currentQuestion}
            onAnswer={submitAnswer}
          />
        )}

        {isFinished && (
          <div className={styles.finishing}>
            <p>Подождите, сохраняем результат...</p>
          </div>
        )}
      </div>

      <div className={styles.footer}>
        <Button variant="ghost" onClick={handleSkip} disabled={completeMutation.isPending}>
          Пропустить тест
        </Button>
      </div>
    </div>
  )
}
```

Создать `frontend/src/features/placement/PlacementScreen.module.css`:
```css
.screen {
  min-height: 100vh;
  display: flex;
  flex-direction: column;
  background: var(--color-surface);
  padding: var(--spacing-md);
}

.header {
  padding-top: var(--spacing-lg);
  display: flex;
  flex-direction: column;
  gap: var(--spacing-xs);
  margin-bottom: var(--spacing-lg);
}

.counter {
  font-size: var(--font-size-label);
  color: var(--color-on-surface-muted);
  text-align: right;
  text-transform: uppercase;
  letter-spacing: 0.05em;
}

.content {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: var(--spacing-lg);
}

.title {
  font-size: var(--font-size-headline);
  font-weight: var(--font-weight-bold);
  line-height: var(--line-height-tight);
}

.subtitle {
  font-size: var(--font-size-body);
  color: var(--color-on-surface-muted);
}

.loading {
  flex: 1;
  display: flex;
  align-items: center;
  justify-content: center;
  color: var(--color-on-surface-muted);
}

.finishing {
  text-align: center;
  color: var(--color-on-surface-muted);
  padding: var(--spacing-xl);
}

.footer {
  padding: var(--spacing-lg) 0 var(--spacing-md);
  display: flex;
  justify-content: center;
}
```

- [ ] **Step 4: Обновить endpoints.ts — добавить skipped параметр**

В `frontend/src/shared/api/endpoints.ts` заменить:
```typescript
  completePlacementTest: (score: number, total: number) =>
    apiClient.post<PlacementCompleteResponse>('/api/v1/placement-test/complete', { score, total }).then(r => r.data),
```
На:
```typescript
  completePlacementTest: (score: number, total: number, skipped = false) =>
    apiClient.post<PlacementCompleteResponse>('/api/v1/placement-test/complete', { score, total, skipped }).then(r => r.data),
```

- [ ] **Step 5: Запустить тест — убедиться что проходит**

```bash
cd /Users/ekaterina/Project/greek-a2/frontend && npm test -- PlacementScreen 2>&1 | tail -10
```

Ожидаемый результат: 2 теста зелёных.

- [ ] **Step 6: Commit**

```bash
cd /Users/ekaterina/Project/greek-a2 && git add frontend/src/features/placement/ frontend/src/shared/api/endpoints.ts && git commit -m "feat(frontend): implement PlacementScreen"
```

---

### Task 5: LevelSection и UnitCard компоненты

**Files:**
- Create: `frontend/src/features/curriculum/components/LevelSection.tsx`
- Create: `frontend/src/features/curriculum/components/LevelSection.module.css`
- Create: `frontend/src/features/curriculum/components/UnitCard.tsx`
- Create: `frontend/src/features/curriculum/components/UnitCard.module.css`

- [ ] **Step 1: Написать тест UnitCard**

Создать `frontend/src/features/curriculum/__tests__/UnitCard.test.tsx`:
```typescript
import { describe, expect, it } from 'vitest'
import { render, screen } from '@testing-library/react'
import { MemoryRouter } from 'react-router-dom'
import { UnitCard } from '../components/UnitCard'

const unit = {
  id: 1,
  title: 'Покупки — Αγορές',
  order_index: 1,
  exercises_total: 6,
  exercises_completed: 3,
  mini_test_passed: false,
  unit_completed: false,
}

describe('UnitCard', () => {
  it('рендерит название юнита', () => {
    render(<MemoryRouter><UnitCard unit={unit} /></MemoryRouter>)
    expect(screen.getByText('Покупки — Αγορές')).toBeInTheDocument()
  })

  it('показывает прогресс', () => {
    render(<MemoryRouter><UnitCard unit={unit} /></MemoryRouter>)
    expect(screen.getByText('3 / 6')).toBeInTheDocument()
  })

  it('показывает галочку при unit_completed=true', () => {
    render(<MemoryRouter><UnitCard unit={{ ...unit, unit_completed: true }} /></MemoryRouter>)
    expect(screen.getByLabelText('завершён')).toBeInTheDocument()
  })

  it('ссылается на /units/:id', () => {
    render(<MemoryRouter><UnitCard unit={unit} /></MemoryRouter>)
    expect(screen.getByRole('link')).toHaveAttribute('href', '/units/1')
  })
})
```

- [ ] **Step 2: Запустить тест — убедиться что падает**

```bash
cd /Users/ekaterina/Project/greek-a2/frontend && npm test -- UnitCard 2>&1 | tail -5
```

- [ ] **Step 3: Создать UnitCard.tsx**

```typescript
// frontend/src/features/curriculum/components/UnitCard.tsx
import { Link } from 'react-router-dom'
import type { UnitSummary } from '../../../shared/api/types'
import styles from './UnitCard.module.css'

interface Props {
  unit: UnitSummary
}

export function UnitCard({ unit }: Props) {
  const pct = unit.exercises_total > 0
    ? Math.round((unit.exercises_completed / unit.exercises_total) * 100)
    : 0

  return (
    <Link to={`/units/${unit.id}`} className={styles.card}>
      <div className={styles.top}>
        <span className={styles.title}>{unit.title}</span>
        {unit.unit_completed && (
          <span className={styles.check} aria-label="завершён">✓</span>
        )}
      </div>
      <div className={styles.progress}>
        <div className={styles.bar}>
          <div className={styles.fill} style={{ width: `${pct}%` }} />
        </div>
        <span className={styles.counter}>{unit.exercises_completed} / {unit.exercises_total}</span>
      </div>
    </Link>
  )
}
```

Создать `frontend/src/features/curriculum/components/UnitCard.module.css`:
```css
.card {
  display: block;
  background: var(--color-surface-high);
  border-radius: var(--radius-card);
  padding: var(--spacing-md);
  text-decoration: none;
  color: var(--color-on-surface);
  transition: background 0.15s;
  -webkit-tap-highlight-color: transparent;
}

.card:active {
  background: var(--color-surface-highest);
}

.top {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: var(--spacing-sm);
}

.title {
  font-size: var(--font-size-body);
  font-weight: var(--font-weight-medium);
  line-height: var(--line-height-normal);
  flex: 1;
}

.check {
  color: var(--color-primary);
  font-weight: var(--font-weight-bold);
  margin-left: var(--spacing-sm);
  flex-shrink: 0;
}

.progress {
  display: flex;
  align-items: center;
  gap: var(--spacing-sm);
}

.bar {
  flex: 1;
  height: 6px;
  background: var(--color-surface-highest);
  border-radius: 3px;
  overflow: hidden;
}

.fill {
  height: 100%;
  background: var(--color-primary);
  border-radius: 3px;
  transition: width 0.3s ease;
}

.counter {
  font-size: var(--font-size-label);
  color: var(--color-on-surface-muted);
  white-space: nowrap;
}
```

- [ ] **Step 4: Создать LevelSection.tsx**

```typescript
// frontend/src/features/curriculum/components/LevelSection.tsx
import type { LevelProgress, UnitSummary } from '../../../shared/api/types'
import { UnitCard } from './UnitCard'
import styles from './LevelSection.module.css'

interface Props {
  level: LevelProgress
  units: UnitSummary[]
}

const LEVEL_LABELS: Record<string, string> = {
  A1: 'Начальный — A1',
  A2: 'Элементарный — A2',
  B1: 'Средний — B1',
}

export function LevelSection({ level, units }: Props) {
  return (
    <section className={styles.section}>
      <div className={styles.header}>
        <div className={styles.titleRow}>
          <h2 className={styles.title}>{LEVEL_LABELS[level.level] ?? level.level}</h2>
          <span className={styles.badge}>{level.progress_percent}%</span>
        </div>
        <div className={styles.progressBar}>
          <div className={styles.progressFill} style={{ width: `${level.progress_percent}%` }} />
        </div>
        <p className={styles.meta}>{level.completed_units} из {level.total_units} юнитов</p>
      </div>
      <div className={styles.units}>
        {units.map(unit => (
          <UnitCard key={unit.id} unit={unit} />
        ))}
      </div>
    </section>
  )
}
```

Создать `frontend/src/features/curriculum/components/LevelSection.module.css`:
```css
.section {
  margin-bottom: var(--spacing-xl);
}

.header {
  margin-bottom: var(--spacing-md);
}

.titleRow {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: var(--spacing-xs);
}

.title {
  font-size: var(--font-size-headline);
  font-weight: var(--font-weight-bold);
  line-height: var(--line-height-tight);
}

.badge {
  font-size: var(--font-size-label);
  font-weight: var(--font-weight-bold);
  color: var(--color-primary);
  text-transform: uppercase;
  letter-spacing: 0.05em;
}

.progressBar {
  height: 4px;
  background: var(--color-surface-highest);
  border-radius: 2px;
  overflow: hidden;
  margin-bottom: var(--spacing-xs);
}

.progressFill {
  height: 100%;
  background: var(--color-primary);
  border-radius: 2px;
  transition: width 0.4s ease;
}

.meta {
  font-size: var(--font-size-label);
  color: var(--color-on-surface-muted);
  text-transform: uppercase;
  letter-spacing: 0.05em;
}

.units {
  display: flex;
  flex-direction: column;
  gap: var(--spacing-sm);
}
```

- [ ] **Step 5: Запустить тест UnitCard**

```bash
cd /Users/ekaterina/Project/greek-a2/frontend && npm test -- UnitCard 2>&1 | tail -10
```

Ожидаемый результат: 4 теста зелёных.

- [ ] **Step 6: Commit**

```bash
cd /Users/ekaterina/Project/greek-a2 && git add frontend/src/features/curriculum/components/ && git commit -m "feat(frontend): add UnitCard and LevelSection components"
```

---

### Task 6: LevelMapScreen

**Files:**
- Modify: `frontend/src/features/curriculum/LevelMapScreen.tsx`
- Create: `frontend/src/features/curriculum/LevelMapScreen.module.css`

- [ ] **Step 1: Написать тест**

Создать `frontend/src/features/curriculum/__tests__/LevelMapScreen.test.tsx`:
```typescript
import { describe, expect, it, vi } from 'vitest'
import { render, screen, waitFor } from '@testing-library/react'
import { MemoryRouter } from 'react-router-dom'
import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { LevelMapScreen } from '../LevelMapScreen'

vi.mock('../../../shared/api/endpoints', () => ({
  api: {
    getLevels: vi.fn().mockResolvedValue({
      levels: [
        { level: 'A1', total_units: 6, completed_units: 2, progress_percent: 33 },
      ],
    }),
    getUnits: vi.fn().mockResolvedValue({
      units: [
        { id: 1, title: 'Знакомство — Γνωριμία', order_index: 1, exercises_total: 6, exercises_completed: 6, mini_test_passed: true, unit_completed: true },
        { id: 2, title: 'Семья — Οικογένεια', order_index: 2, exercises_total: 6, exercises_completed: 0, mini_test_passed: false, unit_completed: false },
      ],
    }),
  },
}))

function wrapper({ children }: { children: React.ReactNode }) {
  const qc = new QueryClient({ defaultOptions: { queries: { retry: false } } })
  return <QueryClientProvider client={qc}><MemoryRouter>{children}</MemoryRouter></QueryClientProvider>
}

describe('LevelMapScreen', () => {
  it('показывает заголовок уровня', async () => {
    render(<LevelMapScreen />, { wrapper })
    await waitFor(() => expect(screen.getByText(/A1/)).toBeInTheDocument())
  })

  it('показывает юниты', async () => {
    render(<LevelMapScreen />, { wrapper })
    await waitFor(() => expect(screen.getByText('Знакомство — Γνωριμία')).toBeInTheDocument())
    expect(screen.getByText('Семья — Οικογένεια')).toBeInTheDocument()
  })
})
```

- [ ] **Step 2: Запустить тест — убедиться что падает**

```bash
cd /Users/ekaterina/Project/greek-a2/frontend && npm test -- LevelMapScreen 2>&1 | tail -5
```

- [ ] **Step 3: Создать LevelMapScreen.tsx**

```typescript
// frontend/src/features/curriculum/LevelMapScreen.tsx
import type { Level } from '../../shared/api/types'
import { useLevelsQuery, useUnitsQuery } from './useCurriculumQuery'
import { LevelSection } from './components/LevelSection'
import styles from './LevelMapScreen.module.css'

const LEVELS: Level[] = ['A1', 'A2', 'B1']

function LevelBlock({ level }: { level: Level }) {
  const levelsQuery = useLevelsQuery()
  const unitsQuery = useUnitsQuery(level)

  const levelData = levelsQuery.data?.levels.find(l => l.level === level)
  const units = unitsQuery.data?.units ?? []

  if (!levelData || unitsQuery.isLoading) return null

  return <LevelSection level={levelData} units={units} />
}

export function LevelMapScreen() {
  return (
    <div className={styles.screen}>
      <div className={styles.header}>
        <h1 className={styles.title}>Мой прогресс</h1>
      </div>
      <div className={styles.content}>
        {LEVELS.map(level => (
          <LevelBlock key={level} level={level} />
        ))}
      </div>
    </div>
  )
}
```

Создать `frontend/src/features/curriculum/LevelMapScreen.module.css`:
```css
.screen {
  min-height: 100vh;
  background: var(--color-surface);
  padding-bottom: calc(var(--bottom-nav-height) + var(--spacing-md));
}

.header {
  padding: var(--spacing-lg) var(--spacing-md) var(--spacing-md);
  background: rgba(11, 13, 26, 0.8);
  backdrop-filter: blur(12px);
  -webkit-backdrop-filter: blur(12px);
  position: sticky;
  top: 0;
  z-index: 10;
}

.title {
  font-size: var(--font-size-headline);
  font-weight: var(--font-weight-bold);
}

.content {
  padding: var(--spacing-md);
}
```

- [ ] **Step 4: Запустить тест**

```bash
cd /Users/ekaterina/Project/greek-a2/frontend && npm test -- LevelMapScreen 2>&1 | tail -10
```

Ожидаемый результат: 2 теста зелёных.

- [ ] **Step 5: Commit**

```bash
cd /Users/ekaterina/Project/greek-a2 && git add frontend/src/features/curriculum/LevelMapScreen.tsx frontend/src/features/curriculum/LevelMapScreen.module.css && git commit -m "feat(frontend): implement LevelMapScreen"
```

---

### Task 7: UnitDetailScreen

**Files:**
- Create: `frontend/src/features/curriculum/UnitDetailScreen.tsx`
- Create: `frontend/src/features/curriculum/UnitDetailScreen.module.css`
- Modify: `frontend/src/App.tsx` — добавить маршруты `/units/:unitId` и `/units/:unitId/mini-test` и `/units/:unitId/result`

- [ ] **Step 1: Написать тест**

Создать `frontend/src/features/curriculum/__tests__/UnitDetailScreen.test.tsx`:
```typescript
import { describe, expect, it, vi } from 'vitest'
import { render, screen, waitFor } from '@testing-library/react'
import { MemoryRouter, Route, Routes } from 'react-router-dom'
import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { UnitDetailScreen } from '../UnitDetailScreen'

vi.mock('../../../shared/api/endpoints', () => ({
  api: {
    getUnitDetail: vi.fn().mockResolvedValue({
      id: 1,
      title: 'Покупки — Αγορές',
      level: 'A2',
      exercises: [
        { id: 10, type: 'true_false', order_index: 1, audio_paths: [], completed: false },
        { id: 11, type: 'multiple_choice', order_index: 2, audio_paths: [], completed: true },
      ],
      vocabulary_cards: [
        { id: 100, word_gr: 'το κατάστημα', word_ru: 'магазин', audio_path: null },
      ],
    }),
  },
}))

function wrapper({ children }: { children: React.ReactNode }) {
  const qc = new QueryClient({ defaultOptions: { queries: { retry: false } } })
  return (
    <QueryClientProvider client={qc}>
      <MemoryRouter initialEntries={['/units/1']}>
        <Routes>
          <Route path="/units/:unitId" element={children} />
        </Routes>
      </MemoryRouter>
    </QueryClientProvider>
  )
}

describe('UnitDetailScreen', () => {
  it('показывает название юнита', async () => {
    render(<UnitDetailScreen />, { wrapper })
    await waitFor(() => expect(screen.getByText('Покупки — Αγορές')).toBeInTheDocument())
  })

  it('показывает список упражнений', async () => {
    render(<UnitDetailScreen />, { wrapper })
    await waitFor(() => expect(screen.getAllByRole('link').length).toBeGreaterThan(0))
  })

  it('показывает кнопку Начать / Продолжить', async () => {
    render(<UnitDetailScreen />, { wrapper })
    await waitFor(() => expect(screen.getByRole('button', { name: /начать|продолжить/i })).toBeInTheDocument())
  })
})
```

- [ ] **Step 2: Запустить тест — убедиться что падает**

```bash
cd /Users/ekaterina/Project/greek-a2/frontend && npm test -- UnitDetailScreen 2>&1 | tail -5
```

- [ ] **Step 3: Создать UnitDetailScreen.tsx**

```typescript
// frontend/src/features/curriculum/UnitDetailScreen.tsx
import { useNavigate, useParams } from 'react-router-dom'
import { useUnitDetailQuery } from './useCurriculumQuery'
import { useExerciseStore } from '../../shared/store/useExerciseStore'
import { Button } from '../../shared/components/Button'
import { ProgressBar } from '../../shared/components/ProgressBar'
import type { ExerciseType } from '../../shared/api/types'
import styles from './UnitDetailScreen.module.css'

const EXERCISE_TYPE_LABELS: Record<ExerciseType, string> = {
  true_false: 'ΣΩΣΤΟ / ΛΑΘΟΣ',
  matching: 'Сопоставление',
  multiple_choice: 'Выбор ответа',
  fill_blank: 'Заполни пропуск',
  image_description: 'Περιγραφή εικόνας',
  dialogue: 'Διάλογος',
}

export function UnitDetailScreen() {
  const { unitId } = useParams<{ unitId: string }>()
  const navigate = useNavigate()
  const { data, isLoading } = useUnitDetailQuery(Number(unitId))
  const startSession = useExerciseStore((s) => s.startSession)

  if (isLoading || !data) {
    return <div className={styles.loading}>Загрузка...</div>
  }

  const nonFlashcard = data.exercises.filter(e => e.type !== 'flashcard' as ExerciseType)
  const completedCount = nonFlashcard.filter(e => e.completed).length
  const allDone = completedCount >= nonFlashcard.length
  const firstIncomplete = nonFlashcard.find(e => !e.completed)

  const handleStart = () => {
    const ids = nonFlashcard.map(e => e.id)
    startSession(Number(unitId), ids)
    const startId = firstIncomplete?.id ?? nonFlashcard[0].id
    navigate(`/units/${unitId}/exercise/${startId}`)
  }

  return (
    <div className={styles.screen}>
      <div className={styles.header}>
        <span className={styles.level}>{data.level}</span>
        <h1 className={styles.title}>{data.title}</h1>
        <ProgressBar value={completedCount} max={nonFlashcard.length} />
        <p className={styles.progress}>{completedCount} из {nonFlashcard.length} упражнений</p>
      </div>

      <div className={styles.content}>
        <section>
          <h2 className={styles.sectionTitle}>Упражнения</h2>
          <div className={styles.exerciseList}>
            {nonFlashcard.map((ex, i) => (
              <div key={ex.id} className={styles.exerciseRow}>
                <span className={styles.exNumber}>{i + 1}</span>
                <span className={styles.exType}>{EXERCISE_TYPE_LABELS[ex.type]}</span>
                {ex.completed && <span className={styles.exCheck} aria-label="выполнено">✓</span>}
              </div>
            ))}
          </div>
        </section>

        <section>
          <h2 className={styles.sectionTitle}>Словарь юнита</h2>
          <div className={styles.vocabList}>
            {data.vocabulary_cards.slice(0, 5).map(card => (
              <div key={card.id} className={styles.vocabRow}>
                <span className={styles.wordGr}>{card.word_gr}</span>
                <span className={styles.wordRu}>{card.word_ru}</span>
              </div>
            ))}
            {data.vocabulary_cards.length > 5 && (
              <p className={styles.vocabMore}>и ещё {data.vocabulary_cards.length - 5} слов</p>
            )}
          </div>
        </section>
      </div>

      <div className={styles.footer}>
        <Button fullWidth onClick={handleStart}>
          {completedCount === 0 ? 'Начать' : allDone ? 'Повторить' : 'Продолжить'}
        </Button>
        {allDone && (
          <Button
            fullWidth
            variant="secondary"
            onClick={() => navigate(`/units/${unitId}/mini-test`)}
          >
            Мини-тест
          </Button>
        )}
      </div>
    </div>
  )
}
```

Создать `frontend/src/features/curriculum/UnitDetailScreen.module.css`:
```css
.screen {
  min-height: 100vh;
  display: flex;
  flex-direction: column;
  background: var(--color-surface);
}

.loading {
  flex: 1;
  display: flex;
  align-items: center;
  justify-content: center;
  color: var(--color-on-surface-muted);
}

.header {
  padding: var(--spacing-lg) var(--spacing-md) var(--spacing-md);
  background: var(--color-surface-low);
  display: flex;
  flex-direction: column;
  gap: var(--spacing-xs);
}

.level {
  font-size: var(--font-size-label);
  font-weight: var(--font-weight-bold);
  color: var(--color-primary);
  text-transform: uppercase;
  letter-spacing: 0.05em;
}

.title {
  font-size: var(--font-size-headline);
  font-weight: var(--font-weight-bold);
  line-height: var(--line-height-tight);
  margin-bottom: var(--spacing-xs);
}

.progress {
  font-size: var(--font-size-label);
  color: var(--color-on-surface-muted);
  text-align: right;
}

.content {
  flex: 1;
  padding: var(--spacing-md);
  display: flex;
  flex-direction: column;
  gap: var(--spacing-lg);
}

.sectionTitle {
  font-size: var(--font-size-title);
  font-weight: var(--font-weight-bold);
  margin-bottom: var(--spacing-sm);
}

.exerciseList {
  display: flex;
  flex-direction: column;
  gap: 2px;
}

.exerciseRow {
  display: flex;
  align-items: center;
  gap: var(--spacing-sm);
  padding: 12px var(--spacing-md);
  background: var(--color-surface-high);
  border-radius: var(--radius-sm);
}

.exNumber {
  font-size: var(--font-size-label);
  font-weight: var(--font-weight-bold);
  color: var(--color-secondary);
  width: 20px;
  text-align: center;
}

.exType {
  flex: 1;
  font-size: var(--font-size-body);
}

.exCheck {
  color: var(--color-primary);
  font-weight: var(--font-weight-bold);
}

.vocabList {
  display: flex;
  flex-direction: column;
  gap: 2px;
}

.vocabRow {
  display: flex;
  justify-content: space-between;
  padding: 10px var(--spacing-md);
  background: var(--color-surface-high);
  border-radius: var(--radius-sm);
}

.wordGr {
  font-size: var(--font-size-body);
  font-weight: var(--font-weight-medium);
}

.wordRu {
  font-size: var(--font-size-body);
  color: var(--color-on-surface-muted);
}

.vocabMore {
  font-size: var(--font-size-label);
  color: var(--color-on-surface-muted);
  text-align: center;
  padding: var(--spacing-sm);
}

.footer {
  padding: var(--spacing-md);
  display: flex;
  flex-direction: column;
  gap: var(--spacing-sm);
  padding-bottom: calc(var(--bottom-nav-height) + var(--spacing-md));
}
```

- [ ] **Step 4: Добавить маршруты в App.tsx**

В `frontend/src/App.tsx` добавить импорты и маршруты:

```typescript
// Добавить импорты:
import { UnitDetailScreen } from './features/curriculum/UnitDetailScreen'
// (MiniTestScreen и UnitResultScreen будут добавлены в Plan 3)
```

В блок `<Routes>` добавить:
```tsx
<Route path="/units/:unitId" element={<UnitDetailScreen />} />
```

- [ ] **Step 5: Запустить тест**

```bash
cd /Users/ekaterina/Project/greek-a2/frontend && npm test -- UnitDetailScreen 2>&1 | tail -10
```

Ожидаемый результат: 3 теста зелёных.

- [ ] **Step 6: Запустить все тесты**

```bash
cd /Users/ekaterina/Project/greek-a2/frontend && npm test 2>&1 | tail -15
```

Ожидаемый результат: все тесты зелёные.

- [ ] **Step 7: Commit**

```bash
cd /Users/ekaterina/Project/greek-a2 && git add frontend/src/features/curriculum/ frontend/src/App.tsx && git commit -m "feat(frontend): implement UnitDetailScreen and add unit route"
```

---

## Self-Review

**Spec coverage:**
- ✅ Placement test (вопросы, прогресс, пропустить, результат) — Tasks 2–4
- ✅ Level Map (уровни A1/A2/B1, прогресс, юниты) — Tasks 1, 5–6
- ✅ Unit Detail (список упражнений, прогресс, словарь, старт/продолжить) — Task 7
- ✅ React Query для curriculum API — Task 1
- ✅ Навигация к упражнениям через useExerciseStore.startSession — Task 7
- ✅ Кнопка мини-теста появляется после завершения всех упражнений — Task 7
- ✅ TDD для всех компонентов — Tasks 1, 3, 4, 5, 6, 7
