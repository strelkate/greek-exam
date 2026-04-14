# Frontend Plan 3: Exercises

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Реализовать все 7 типов упражнений, ExerciseShell-обёртку, ExerciseScreen-роутер, MiniTestScreen и UnitResultScreen — полностью с дизайном Aegean Midnight.

**Architecture:** `ExerciseShell` — общая обёртка: прогресс-бар, аудио, инструкция, слот для типа и кнопка Проверить/Далее. Каждый тип упражнения — отдельный компонент с чётким интерфейсом `onAnswer(isCorrect: boolean)`. `ExerciseScreen` получает полный список упражнений юнита и определяет текущую позицию по `exerciseId` из URL.

**Tech Stack:** React 18, React Router v6, TanStack Query v5, Zustand (useExerciseStore), Vitest + Testing Library

**Prerequisite:** Plan 1 (Foundation) и Plan 2 (Curriculum) выполнены.

---

## File Map

| Файл | Назначение |
|------|-----------|
| `frontend/src/features/exercises/ExerciseShell.tsx` | Общая обёртка упражнения |
| `frontend/src/features/exercises/ExerciseScreen.tsx` | Роутер упражнений (замена заглушки) |
| `frontend/src/features/exercises/types/TrueFalse.tsx` | Тип упражнения: True/False |
| `frontend/src/features/exercises/types/MultipleChoice.tsx` | Тип упражнения: Multiple Choice |
| `frontend/src/features/exercises/types/Matching.tsx` | Тип упражнения: Matching |
| `frontend/src/features/exercises/types/FillBlank.tsx` | Тип упражнения: Fill in the Blank |
| `frontend/src/features/exercises/types/ImageDescription.tsx` | Тип упражнения: Image Description |
| `frontend/src/features/exercises/types/Dialogue.tsx` | Тип упражнения: Dialogue |
| `frontend/src/features/exercises/useExerciseQuery.ts` | React Query хук для одного упражнения |
| `frontend/src/features/exercises/MiniTestScreen.tsx` | Экран мини-теста |
| `frontend/src/features/exercises/UnitResultScreen.tsx` | Экран результата юнита |
| `frontend/src/App.tsx` | Добавить маршруты мини-теста и результата |
| `frontend/src/features/exercises/__tests__/TrueFalse.test.tsx` | Тесты TrueFalse |
| `frontend/src/features/exercises/__tests__/MultipleChoice.test.tsx` | Тесты MultipleChoice |
| `frontend/src/features/exercises/__tests__/FillBlank.test.tsx` | Тесты FillBlank |
| `frontend/src/features/exercises/__tests__/ExerciseShell.test.tsx` | Тесты ExerciseShell |
| `frontend/src/features/exercises/__tests__/MiniTestScreen.test.tsx` | Тесты MiniTestScreen |

---

### Task 1: useExerciseQuery хук

**Files:**
- Create: `frontend/src/features/exercises/useExerciseQuery.ts`

- [ ] **Step 1: Создать useExerciseQuery.ts**

```typescript
// frontend/src/features/exercises/useExerciseQuery.ts
import { useQuery } from '@tanstack/react-query'
import { api } from '../../shared/api/endpoints'
import { useMiniTestQuery } from './useMiniTestQuery'

export function useExerciseQuery(exerciseId: number) {
  return useQuery({
    queryKey: ['exercise', exerciseId],
    queryFn: () => api.getExercise(exerciseId),
    enabled: Boolean(exerciseId),
  })
}
```

- [ ] **Step 2: Создать useMiniTestQuery.ts**

```typescript
// frontend/src/features/exercises/useMiniTestQuery.ts
import { useQuery } from '@tanstack/react-query'
import { api } from '../../shared/api/endpoints'

export function useMiniTestQuery(unitId: number) {
  return useQuery({
    queryKey: ['mini-test', unitId],
    queryFn: () => api.getMiniTest(unitId),
    enabled: Boolean(unitId),
  })
}
```

- [ ] **Step 3: Проверить, что endpoints.ts содержит нужные функции**

Открыть `frontend/src/shared/api/endpoints.ts` и убедиться, что есть:
- `getExercise(exerciseId: number)` → GET `/api/v1/exercises/:exerciseId`
- `getMiniTest(unitId: number)` → GET `/api/v1/units/:unitId/mini-test`
- `completeMiniTest(unitId: number, score: number, total: number)` → POST `/api/v1/units/:unitId/mini-test/complete`

Если нет — добавить в `endpoints.ts`:
```typescript
getExercise: (exerciseId: number) =>
  apiClient.get<ExerciseResponse>(`/api/v1/exercises/${exerciseId}`).then(r => r.data),

getMiniTest: (unitId: number) =>
  apiClient.get<MiniTestQuestionsResponse>(`/api/v1/units/${unitId}/mini-test`).then(r => r.data),

completeMiniTest: (unitId: number, score: number, total: number) =>
  apiClient.post<MiniTestCompleteResponse>(`/api/v1/units/${unitId}/mini-test/complete`, { score, total }).then(r => r.data),
```

- [ ] **Step 4: Commit**

```bash
cd /Users/ekaterina/Project/greek-a2 && git add frontend/src/features/exercises/useExerciseQuery.ts frontend/src/features/exercises/useMiniTestQuery.ts frontend/src/shared/api/endpoints.ts && git commit -m "feat(frontend): add exercise and mini-test React Query hooks"
```

---

### Task 2: ExerciseShell — общая обёртка

**Files:**
- Create: `frontend/src/features/exercises/ExerciseShell.tsx`
- Create: `frontend/src/features/exercises/__tests__/ExerciseShell.test.tsx`

- [ ] **Step 1: Написать тест**

```typescript
// frontend/src/features/exercises/__tests__/ExerciseShell.test.tsx
import { render, screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { ExerciseShell } from '../ExerciseShell'

describe('ExerciseShell', () => {
  const defaultProps = {
    current: 2,
    total: 5,
    instruction: 'Выберите правильный ответ',
    audioPath: null,
    canSubmit: false,
    onSubmit: vi.fn(),
    children: <div>exercise content</div>,
  }

  it('renders progress as X / N', () => {
    render(<ExerciseShell {...defaultProps} />)
    expect(screen.getByText('2 / 5')).toBeInTheDocument()
  })

  it('renders instruction text', () => {
    render(<ExerciseShell {...defaultProps} />)
    expect(screen.getByText('Выберите правильный ответ')).toBeInTheDocument()
  })

  it('renders children', () => {
    render(<ExerciseShell {...defaultProps} />)
    expect(screen.getByText('exercise content')).toBeInTheDocument()
  })

  it('submit button is disabled when canSubmit=false', () => {
    render(<ExerciseShell {...defaultProps} canSubmit={false} />)
    expect(screen.getByRole('button', { name: /проверить/i })).toBeDisabled()
  })

  it('submit button is enabled when canSubmit=true', () => {
    render(<ExerciseShell {...defaultProps} canSubmit={true} />)
    expect(screen.getByRole('button', { name: /проверить/i })).not.toBeDisabled()
  })

  it('calls onSubmit when button clicked', async () => {
    const onSubmit = vi.fn()
    render(<ExerciseShell {...defaultProps} canSubmit={true} onSubmit={onSubmit} />)
    await userEvent.click(screen.getByRole('button', { name: /проверить/i }))
    expect(onSubmit).toHaveBeenCalledTimes(1)
  })

  it('shows audio button when audioPath provided', () => {
    render(<ExerciseShell {...defaultProps} audioPath="/audio/test.mp3" />)
    expect(screen.getByRole('button', { name: /аудио/i })).toBeInTheDocument()
  })

  it('hides audio button when audioPath is null', () => {
    render(<ExerciseShell {...defaultProps} audioPath={null} />)
    expect(screen.queryByRole('button', { name: /аудио/i })).not.toBeInTheDocument()
  })
})
```

- [ ] **Step 2: Запустить тест — убедиться, что падает**

```bash
cd /Users/ekaterina/Project/greek-a2/frontend && npx vitest run src/features/exercises/__tests__/ExerciseShell.test.tsx
```

Ожидаемый результат: FAIL — `ExerciseShell` не существует.

- [ ] **Step 3: Создать ExerciseShell.tsx**

```tsx
// frontend/src/features/exercises/ExerciseShell.tsx
import { ReactNode } from 'react'
import { AudioPlayer } from '../../shared/components/AudioPlayer'
import { Button } from '../../shared/components/Button'
import { ProgressBar } from '../../shared/components/ProgressBar'

interface ExerciseShellProps {
  current: number
  total: number
  instruction: string
  audioPath: string | null
  canSubmit: boolean
  submitted?: boolean
  onSubmit: () => void
  children: ReactNode
}

export function ExerciseShell({
  current,
  total,
  instruction,
  audioPath,
  canSubmit,
  submitted = false,
  onSubmit,
  children,
}: ExerciseShellProps) {
  return (
    <div className="exercise-shell">
      <div className="exercise-shell__header">
        <ProgressBar value={current} max={total} />
        <span className="exercise-shell__counter">{current} / {total}</span>
      </div>

      {audioPath && (
        <div className="exercise-shell__audio">
          <AudioPlayer src={audioPath} ariaLabel="аудио" />
        </div>
      )}

      <p className="exercise-shell__instruction">{instruction}</p>

      <div className="exercise-shell__content">
        {children}
      </div>

      <div className="exercise-shell__footer">
        <Button
          onClick={onSubmit}
          disabled={!canSubmit}
          variant="primary"
          fullWidth
        >
          {submitted ? 'Далее' : 'Проверить'}
        </Button>
      </div>
    </div>
  )
}
```

Добавить стили в конец `frontend/src/index.css`:
```css
/* ExerciseShell */
.exercise-shell {
  display: flex;
  flex-direction: column;
  min-height: 100dvh;
  padding: 16px 16px calc(16px + env(safe-area-inset-bottom));
  background: var(--color-surface);
  gap: 16px;
}

.exercise-shell__header {
  display: flex;
  align-items: center;
  gap: 12px;
}

.exercise-shell__counter {
  font-size: var(--font-size-label);
  font-weight: var(--font-weight-medium);
  color: var(--color-on-surface-muted);
  white-space: nowrap;
}

.exercise-shell__audio {
  display: flex;
  justify-content: center;
}

.exercise-shell__instruction {
  font-size: var(--font-size-title);
  font-weight: var(--font-weight-medium);
  color: var(--color-on-surface);
  line-height: var(--line-height-tight);
}

.exercise-shell__content {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.exercise-shell__footer {
  margin-top: auto;
  padding-top: 16px;
}
```

- [ ] **Step 4: Запустить тест — убедиться, что проходит**

```bash
cd /Users/ekaterina/Project/greek-a2/frontend && npx vitest run src/features/exercises/__tests__/ExerciseShell.test.tsx
```

Ожидаемый результат: все тесты PASS.

- [ ] **Step 5: Commit**

```bash
cd /Users/ekaterina/Project/greek-a2 && git add frontend/src/features/exercises/ExerciseShell.tsx frontend/src/features/exercises/__tests__/ExerciseShell.test.tsx frontend/src/index.css && git commit -m "feat(frontend): add ExerciseShell wrapper component"
```

---

### Task 3: TrueFalse тип упражнения

**Files:**
- Create: `frontend/src/features/exercises/types/TrueFalse.tsx`
- Create: `frontend/src/features/exercises/__tests__/TrueFalse.test.tsx`

Content schema (из JSON):
```json
{ "statement": "Η Αθήνα είναι η πρωτεύουσα της Ελλάδας.", "is_true": true, "explanation": "..." }
```

- [ ] **Step 1: Написать тест**

```typescript
// frontend/src/features/exercises/__tests__/TrueFalse.test.tsx
import { render, screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { TrueFalse } from '../types/TrueFalse'

const content = {
  statement: 'Η Αθήνα είναι η πρωτεύουσα.',
  is_true: true,
  explanation: 'Σωστά.',
}

describe('TrueFalse', () => {
  it('renders statement text', () => {
    render(<TrueFalse content={content} onAnswer={vi.fn()} />)
    expect(screen.getByText(content.statement)).toBeInTheDocument()
  })

  it('renders Σωστό and Λάθος buttons', () => {
    render(<TrueFalse content={content} onAnswer={vi.fn()} />)
    expect(screen.getByRole('button', { name: /σωστό/i })).toBeInTheDocument()
    expect(screen.getByRole('button', { name: /λάθος/i })).toBeInTheDocument()
  })

  it('calls onAnswer(true) when Σωστό clicked', async () => {
    const onAnswer = vi.fn()
    render(<TrueFalse content={content} onAnswer={onAnswer} />)
    await userEvent.click(screen.getByRole('button', { name: /σωστό/i }))
    expect(onAnswer).toHaveBeenCalledWith(true)
  })

  it('calls onAnswer(false) when Λάθος clicked', async () => {
    const onAnswer = vi.fn()
    render(<TrueFalse content={content} onAnswer={onAnswer} />)
    await userEvent.click(screen.getByRole('button', { name: /λάθος/i }))
    expect(onAnswer).toHaveBeenCalledWith(false)
  })

  it('shows correct/incorrect feedback after answer', async () => {
    render(<TrueFalse content={content} onAnswer={vi.fn()} />)
    await userEvent.click(screen.getByRole('button', { name: /σωστό/i }))
    expect(screen.getByText(/σωστά/i)).toBeInTheDocument()
  })

  it('disables buttons after selection', async () => {
    render(<TrueFalse content={content} onAnswer={vi.fn()} />)
    await userEvent.click(screen.getByRole('button', { name: /σωστό/i }))
    expect(screen.getByRole('button', { name: /σωστό/i })).toBeDisabled()
    expect(screen.getByRole('button', { name: /λάθος/i })).toBeDisabled()
  })
})
```

- [ ] **Step 2: Запустить тест — убедиться, что падает**

```bash
cd /Users/ekaterina/Project/greek-a2/frontend && npx vitest run src/features/exercises/__tests__/TrueFalse.test.tsx
```

Ожидаемый результат: FAIL.

- [ ] **Step 3: Создать TrueFalse.tsx**

```tsx
// frontend/src/features/exercises/types/TrueFalse.tsx
import { useState } from 'react'

interface TrueFalseContent {
  statement: string
  is_true: boolean
  explanation?: string
}

interface TrueFalseProps {
  content: TrueFalseContent
  onAnswer: (isCorrect: boolean) => void
}

export function TrueFalse({ content, onAnswer }: TrueFalseProps) {
  const [selected, setSelected] = useState<boolean | null>(null)

  const handleSelect = (answer: boolean) => {
    if (selected !== null) return
    setSelected(answer)
    onAnswer(answer === content.is_true)
  }

  const getButtonClass = (value: boolean) => {
    if (selected === null) return 'tf-btn'
    if (selected === value) {
      return value === content.is_true ? 'tf-btn tf-btn--correct' : 'tf-btn tf-btn--incorrect'
    }
    return 'tf-btn tf-btn--dim'
  }

  return (
    <div className="true-false">
      <p className="true-false__statement">{content.statement}</p>

      <div className="true-false__choices">
        <button
          className={getButtonClass(true)}
          onClick={() => handleSelect(true)}
          disabled={selected !== null}
        >
          Σωστό ✓
        </button>
        <button
          className={getButtonClass(false)}
          onClick={() => handleSelect(false)}
          disabled={selected !== null}
        >
          Λάθος ✗
        </button>
      </div>

      {selected !== null && content.explanation && (
        <p className="true-false__explanation">{content.explanation}</p>
      )}
    </div>
  )
}
```

Добавить стили в конец `frontend/src/index.css`:
```css
/* TrueFalse */
.true-false__statement {
  font-size: var(--font-size-body);
  color: var(--color-on-surface);
  line-height: var(--line-height-normal);
  background: var(--color-surface-high);
  border-radius: var(--radius-card);
  padding: 20px;
  text-align: center;
}

.true-false__choices {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 12px;
  margin-top: 8px;
}

.tf-btn {
  padding: 20px 12px;
  border: none;
  border-radius: var(--radius-button);
  font-family: var(--font-family);
  font-size: var(--font-size-body);
  font-weight: var(--font-weight-medium);
  cursor: pointer;
  transition: opacity 0.15s;
  background: var(--color-surface-highest);
  color: var(--color-on-surface);
}

.tf-btn:disabled { cursor: default; }
.tf-btn--correct { background: var(--color-success); color: #000; }
.tf-btn--incorrect { background: var(--color-error); }
.tf-btn--dim { opacity: 0.35; }

.true-false__explanation {
  font-size: var(--font-size-body);
  color: var(--color-on-surface-muted);
  line-height: var(--line-height-normal);
  padding: 12px 16px;
  background: var(--color-surface-high);
  border-radius: var(--radius-card);
}
```

- [ ] **Step 4: Запустить тест — убедиться, что проходит**

```bash
cd /Users/ekaterina/Project/greek-a2/frontend && npx vitest run src/features/exercises/__tests__/TrueFalse.test.tsx
```

Ожидаемый результат: все тесты PASS.

- [ ] **Step 5: Commit**

```bash
cd /Users/ekaterina/Project/greek-a2 && git add frontend/src/features/exercises/types/TrueFalse.tsx frontend/src/features/exercises/__tests__/TrueFalse.test.tsx frontend/src/index.css && git commit -m "feat(frontend): add TrueFalse exercise type"
```

---

### Task 4: MultipleChoice тип упражнения

**Files:**
- Create: `frontend/src/features/exercises/types/MultipleChoice.tsx`
- Create: `frontend/src/features/exercises/__tests__/MultipleChoice.test.tsx`

Content schema:
```json
{ "question": "Τι σημαίνει 'καλημέρα';", "options": ["Good morning", "Good night", "Goodbye", "Hello"], "correct_index": 0 }
```

- [ ] **Step 1: Написать тест**

```typescript
// frontend/src/features/exercises/__tests__/MultipleChoice.test.tsx
import { render, screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { MultipleChoice } from '../types/MultipleChoice'

const content = {
  question: 'Τι σημαίνει "καλημέρα";',
  options: ['Good morning', 'Good night', 'Goodbye', 'Hello'],
  correct_index: 0,
}

describe('MultipleChoice', () => {
  it('renders question text', () => {
    render(<MultipleChoice content={content} onAnswer={vi.fn()} />)
    expect(screen.getByText(/καλημέρα/)).toBeInTheDocument()
  })

  it('renders all 4 options', () => {
    render(<MultipleChoice content={content} onAnswer={vi.fn()} />)
    content.options.forEach(opt => {
      expect(screen.getByText(opt)).toBeInTheDocument()
    })
  })

  it('calls onAnswer(true) when correct option selected', async () => {
    const onAnswer = vi.fn()
    render(<MultipleChoice content={content} onAnswer={onAnswer} />)
    await userEvent.click(screen.getByText('Good morning'))
    expect(onAnswer).toHaveBeenCalledWith(true)
  })

  it('calls onAnswer(false) when wrong option selected', async () => {
    const onAnswer = vi.fn()
    render(<MultipleChoice content={content} onAnswer={onAnswer} />)
    await userEvent.click(screen.getByText('Good night'))
    expect(onAnswer).toHaveBeenCalledWith(false)
  })

  it('disables all options after selection', async () => {
    render(<MultipleChoice content={content} onAnswer={vi.fn()} />)
    await userEvent.click(screen.getByText('Goodbye'))
    content.options.forEach(opt => {
      expect(screen.getByText(opt).closest('button')).toBeDisabled()
    })
  })

  it('highlights correct option green after wrong answer', async () => {
    render(<MultipleChoice content={content} onAnswer={vi.fn()} />)
    await userEvent.click(screen.getByText('Good night'))
    expect(screen.getByText('Good morning').closest('button')).toHaveClass('mc-option--correct')
  })
})
```

- [ ] **Step 2: Запустить тест — убедиться, что падает**

```bash
cd /Users/ekaterina/Project/greek-a2/frontend && npx vitest run src/features/exercises/__tests__/MultipleChoice.test.tsx
```

Ожидаемый результат: FAIL.

- [ ] **Step 3: Создать MultipleChoice.tsx**

```tsx
// frontend/src/features/exercises/types/MultipleChoice.tsx
import { useState } from 'react'

interface MultipleChoiceContent {
  question: string
  options: string[]
  correct_index: number
}

interface MultipleChoiceProps {
  content: MultipleChoiceContent
  onAnswer: (isCorrect: boolean) => void
}

export function MultipleChoice({ content, onAnswer }: MultipleChoiceProps) {
  const [selected, setSelected] = useState<number | null>(null)

  const handleSelect = (index: number) => {
    if (selected !== null) return
    setSelected(index)
    onAnswer(index === content.correct_index)
  }

  const getOptionClass = (index: number) => {
    if (selected === null) return 'mc-option'
    if (index === content.correct_index) return 'mc-option mc-option--correct'
    if (index === selected) return 'mc-option mc-option--incorrect'
    return 'mc-option mc-option--dim'
  }

  return (
    <div className="multiple-choice">
      <p className="multiple-choice__question">{content.question}</p>
      <div className="multiple-choice__options">
        {content.options.map((option, index) => (
          <button
            key={index}
            className={getOptionClass(index)}
            onClick={() => handleSelect(index)}
            disabled={selected !== null}
          >
            {option}
          </button>
        ))}
      </div>
    </div>
  )
}
```

Добавить стили в конец `frontend/src/index.css`:
```css
/* MultipleChoice */
.multiple-choice__question {
  font-size: var(--font-size-title);
  font-weight: var(--font-weight-medium);
  color: var(--color-on-surface);
  line-height: var(--line-height-tight);
  margin-bottom: 16px;
}

.multiple-choice__options {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.mc-option {
  padding: 16px 20px;
  border: none;
  border-radius: var(--radius-button);
  font-family: var(--font-family);
  font-size: var(--font-size-body);
  font-weight: var(--font-weight-medium);
  text-align: left;
  cursor: pointer;
  background: var(--color-surface-highest);
  color: var(--color-on-surface);
  transition: opacity 0.15s;
}

.mc-option:disabled { cursor: default; }
.mc-option--correct { background: var(--color-success); color: #000; }
.mc-option--incorrect { background: var(--color-error); }
.mc-option--dim { opacity: 0.35; }
```

- [ ] **Step 4: Запустить тест — убедиться, что проходит**

```bash
cd /Users/ekaterina/Project/greek-a2/frontend && npx vitest run src/features/exercises/__tests__/MultipleChoice.test.tsx
```

Ожидаемый результат: все тесты PASS.

- [ ] **Step 5: Commit**

```bash
cd /Users/ekaterina/Project/greek-a2 && git add frontend/src/features/exercises/types/MultipleChoice.tsx frontend/src/features/exercises/__tests__/MultipleChoice.test.tsx frontend/src/index.css && git commit -m "feat(frontend): add MultipleChoice exercise type"
```

---

### Task 5: Matching тип упражнения

**Files:**
- Create: `frontend/src/features/exercises/types/Matching.tsx`

Content schema:
```json
{ "pairs": [{ "left": "το βιβλίο", "right": "книга" }, { "left": "το σπίτι", "right": "дом" }] }
```

- [ ] **Step 1: Создать Matching.tsx**

Matching — без TDD (логика перетаскивания, сложная для Testing Library). Тестируется вручную.

```tsx
// frontend/src/features/exercises/types/Matching.tsx
import { useState } from 'react'

interface MatchingPair {
  left: string
  right: string
}

interface MatchingContent {
  pairs: MatchingPair[]
}

interface MatchingProps {
  content: MatchingContent
  onAnswer: (isCorrect: boolean) => void
}

type SelectionState = {
  leftIndex: number | null
  rightIndex: number | null
}

export function Matching({ content, onAnswer }: MatchingProps) {
  const [selection, setSelection] = useState<SelectionState>({ leftIndex: null, rightIndex: null })
  const [matched, setMatched] = useState<Map<number, number>>(new Map()) // left → right
  const [incorrect, setIncorrect] = useState<Set<number>>(new Set()) // left indices that were wrong
  const [submitted, setSubmitted] = useState(false)

  const shuffledRight = useState(() =>
    [...content.pairs.map((_, i) => i)].sort(() => Math.random() - 0.5)
  )[0]

  const handleLeft = (index: number) => {
    if (submitted || matched.has(index)) return
    setSelection(s => ({ ...s, leftIndex: index }))
  }

  const handleRight = (rightIdx: number) => {
    if (submitted) return
    const leftIdx = selection.leftIndex
    if (leftIdx === null) return

    if (content.pairs[leftIdx].right === content.pairs[shuffledRight[rightIdx]].right) {
      // Correct match
      const newMatched = new Map(matched)
      newMatched.set(leftIdx, shuffledRight[rightIdx])
      setMatched(newMatched)
      setSelection({ leftIndex: null, rightIndex: null })

      if (newMatched.size === content.pairs.length) {
        setSubmitted(true)
        onAnswer(true)
      }
    } else {
      // Wrong match — briefly highlight then clear
      setIncorrect(new Set([leftIdx]))
      setTimeout(() => {
        setIncorrect(new Set())
        setSelection({ leftIndex: null, rightIndex: null })
      }, 800)
    }
  }

  const getLeftClass = (index: number) => {
    if (matched.has(index)) return 'match-item match-item--matched'
    if (incorrect.has(index)) return 'match-item match-item--incorrect'
    if (selection.leftIndex === index) return 'match-item match-item--selected'
    return 'match-item'
  }

  const getRightClass = (rightIdx: number) => {
    const originalIdx = shuffledRight[rightIdx]
    const isMatched = [...matched.values()].includes(originalIdx)
    if (isMatched) return 'match-item match-item--matched'
    return 'match-item'
  }

  return (
    <div className="matching">
      <div className="matching__columns">
        <div className="matching__col">
          {content.pairs.map((pair, i) => (
            <button
              key={i}
              className={getLeftClass(i)}
              onClick={() => handleLeft(i)}
              disabled={submitted || matched.has(i)}
            >
              {pair.left}
            </button>
          ))}
        </div>
        <div className="matching__col">
          {shuffledRight.map((originalIdx, i) => (
            <button
              key={i}
              className={getRightClass(i)}
              onClick={() => handleRight(i)}
              disabled={submitted || [...matched.values()].includes(originalIdx)}
            >
              {content.pairs[originalIdx].right}
            </button>
          ))}
        </div>
      </div>
    </div>
  )
}
```

Добавить стили в конец `frontend/src/index.css`:
```css
/* Matching */
.matching__columns {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 10px;
}

.matching__col {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.match-item {
  padding: 14px 12px;
  border: none;
  border-radius: var(--radius-button);
  font-family: var(--font-family);
  font-size: var(--font-size-body);
  font-weight: var(--font-weight-medium);
  text-align: center;
  cursor: pointer;
  background: var(--color-surface-highest);
  color: var(--color-on-surface);
  transition: background 0.15s, opacity 0.15s;
  min-height: 48px;
  word-break: break-word;
}

.match-item:disabled { cursor: default; }
.match-item--selected { background: var(--color-secondary); color: #000; }
.match-item--matched { background: var(--color-success); color: #000; opacity: 0.7; }
.match-item--incorrect { background: var(--color-error); }
```

- [ ] **Step 2: Commit**

```bash
cd /Users/ekaterina/Project/greek-a2 && git add frontend/src/features/exercises/types/Matching.tsx frontend/src/index.css && git commit -m "feat(frontend): add Matching exercise type"
```

---

### Task 6: FillBlank тип упражнения

**Files:**
- Create: `frontend/src/features/exercises/types/FillBlank.tsx`
- Create: `frontend/src/features/exercises/__tests__/FillBlank.test.tsx`

Content schema:
```json
{ "sentence": "Θέλω να ___ ένα εισιτήριο.", "blank_word": "αγοράσω", "options": ["αγοράσω", "πουλήσω", "βρω", "δω"] }
```

- [ ] **Step 1: Написать тест**

```typescript
// frontend/src/features/exercises/__tests__/FillBlank.test.tsx
import { render, screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { FillBlank } from '../types/FillBlank'

const content = {
  sentence: 'Θέλω να ___ ένα εισιτήριο.',
  blank_word: 'αγοράσω',
  options: ['αγοράσω', 'πουλήσω', 'βρω', 'δω'],
}

describe('FillBlank', () => {
  it('renders sentence with blank placeholder', () => {
    render(<FillBlank content={content} onAnswer={vi.fn()} />)
    expect(screen.getByText(/θέλω να/i)).toBeInTheDocument()
  })

  it('renders all word bank options', () => {
    render(<FillBlank content={content} onAnswer={vi.fn()} />)
    content.options.forEach(opt => {
      expect(screen.getByRole('button', { name: opt })).toBeInTheDocument()
    })
  })

  it('calls onAnswer(true) when correct word selected', async () => {
    const onAnswer = vi.fn()
    render(<FillBlank content={content} onAnswer={onAnswer} />)
    await userEvent.click(screen.getByRole('button', { name: 'αγοράσω' }))
    expect(onAnswer).toHaveBeenCalledWith(true)
  })

  it('calls onAnswer(false) when wrong word selected', async () => {
    const onAnswer = vi.fn()
    render(<FillBlank content={content} onAnswer={onAnswer} />)
    await userEvent.click(screen.getByRole('button', { name: 'πουλήσω' }))
    expect(onAnswer).toHaveBeenCalledWith(false)
  })

  it('inserts selected word into the sentence blank', async () => {
    render(<FillBlank content={content} onAnswer={vi.fn()} />)
    await userEvent.click(screen.getByRole('button', { name: 'αγοράσω' }))
    expect(screen.getByText(/αγοράσω/)).toBeInTheDocument()
  })

  it('disables word bank after selection', async () => {
    render(<FillBlank content={content} onAnswer={vi.fn()} />)
    await userEvent.click(screen.getByRole('button', { name: 'βρω' }))
    content.options.forEach(opt => {
      expect(screen.getByRole('button', { name: opt })).toBeDisabled()
    })
  })
})
```

- [ ] **Step 2: Запустить тест — убедиться, что падает**

```bash
cd /Users/ekaterina/Project/greek-a2/frontend && npx vitest run src/features/exercises/__tests__/FillBlank.test.tsx
```

Ожидаемый результат: FAIL.

- [ ] **Step 3: Создать FillBlank.tsx**

```tsx
// frontend/src/features/exercises/types/FillBlank.tsx
import { useState } from 'react'

interface FillBlankContent {
  sentence: string
  blank_word: string
  options: string[]
}

interface FillBlankProps {
  content: FillBlankContent
  onAnswer: (isCorrect: boolean) => void
}

export function FillBlank({ content, onAnswer }: FillBlankProps) {
  const [selected, setSelected] = useState<string | null>(null)

  const handleSelect = (word: string) => {
    if (selected !== null) return
    setSelected(word)
    onAnswer(word === content.blank_word)
  }

  const sentenceParts = content.sentence.split('___')

  const getOptionClass = (word: string) => {
    if (selected === null) return 'fb-option'
    if (word === content.blank_word) return 'fb-option fb-option--correct'
    if (word === selected) return 'fb-option fb-option--incorrect'
    return 'fb-option fb-option--dim'
  }

  return (
    <div className="fill-blank">
      <p className="fill-blank__sentence">
        {sentenceParts[0]}
        <span className={`fill-blank__blank ${selected ? (selected === content.blank_word ? 'fill-blank__blank--correct' : 'fill-blank__blank--incorrect') : ''}`}>
          {selected ?? '___'}
        </span>
        {sentenceParts[1]}
      </p>

      <div className="fill-blank__word-bank">
        {content.options.map((word) => (
          <button
            key={word}
            className={getOptionClass(word)}
            onClick={() => handleSelect(word)}
            disabled={selected !== null}
          >
            {word}
          </button>
        ))}
      </div>
    </div>
  )
}
```

Добавить стили в конец `frontend/src/index.css`:
```css
/* FillBlank */
.fill-blank__sentence {
  font-size: var(--font-size-title);
  color: var(--color-on-surface);
  line-height: var(--line-height-normal);
  background: var(--color-surface-high);
  border-radius: var(--radius-card);
  padding: 20px;
  text-align: center;
  margin-bottom: 20px;
}

.fill-blank__blank {
  display: inline-block;
  min-width: 80px;
  border-bottom: 2px solid var(--color-primary);
  padding: 0 6px;
  font-weight: var(--font-weight-bold);
  color: var(--color-primary);
}

.fill-blank__blank--correct { color: var(--color-success); border-color: var(--color-success); }
.fill-blank__blank--incorrect { color: var(--color-error); border-color: var(--color-error); }

.fill-blank__word-bank {
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
  justify-content: center;
}

.fb-option {
  padding: 12px 20px;
  border: none;
  border-radius: var(--radius-button);
  font-family: var(--font-family);
  font-size: var(--font-size-body);
  font-weight: var(--font-weight-medium);
  cursor: pointer;
  background: var(--color-surface-highest);
  color: var(--color-on-surface);
  transition: opacity 0.15s;
}

.fb-option:disabled { cursor: default; }
.fb-option--correct { background: var(--color-success); color: #000; }
.fb-option--incorrect { background: var(--color-error); }
.fb-option--dim { opacity: 0.35; }
```

- [ ] **Step 4: Запустить тест — убедиться, что проходит**

```bash
cd /Users/ekaterina/Project/greek-a2/frontend && npx vitest run src/features/exercises/__tests__/FillBlank.test.tsx
```

Ожидаемый результат: все тесты PASS.

- [ ] **Step 5: Commit**

```bash
cd /Users/ekaterina/Project/greek-a2 && git add frontend/src/features/exercises/types/FillBlank.tsx frontend/src/features/exercises/__tests__/FillBlank.test.tsx frontend/src/index.css && git commit -m "feat(frontend): add FillBlank exercise type"
```

---

### Task 7: ImageDescription тип упражнения

**Files:**
- Create: `frontend/src/features/exercises/types/ImageDescription.tsx`

Content schema:
```json
{
  "image_url": "/static/images/unit_a2_01_img.jpg",
  "question": "Τι κάνει η γυναίκα στην εικόνα;",
  "options": [
    { "text": "Μαγειρεύει", "is_correct": true },
    { "text": "Διαβάζει", "is_correct": false },
    { "text": "Κοιμάται", "is_correct": false },
    { "text": "Τρέχει", "is_correct": false }
  ]
}
```

- [ ] **Step 1: Создать ImageDescription.tsx**

```tsx
// frontend/src/features/exercises/types/ImageDescription.tsx
import { useState } from 'react'

interface ImageOption {
  text: string
  is_correct: boolean
}

interface ImageDescriptionContent {
  image_url: string
  question: string
  options: ImageOption[]
}

interface ImageDescriptionProps {
  content: ImageDescriptionContent
  onAnswer: (isCorrect: boolean) => void
}

export function ImageDescription({ content, onAnswer }: ImageDescriptionProps) {
  const [selectedIndex, setSelectedIndex] = useState<number | null>(null)

  const handleSelect = (index: number) => {
    if (selectedIndex !== null) return
    setSelectedIndex(index)
    onAnswer(content.options[index].is_correct)
  }

  const getOptionClass = (index: number) => {
    if (selectedIndex === null) return 'mc-option'
    if (content.options[index].is_correct) return 'mc-option mc-option--correct'
    if (index === selectedIndex) return 'mc-option mc-option--incorrect'
    return 'mc-option mc-option--dim'
  }

  return (
    <div className="image-description">
      <img
        src={content.image_url}
        alt="упражнение"
        className="image-description__img"
      />
      <p className="multiple-choice__question">{content.question}</p>
      <div className="multiple-choice__options">
        {content.options.map((option, index) => (
          <button
            key={index}
            className={getOptionClass(index)}
            onClick={() => handleSelect(index)}
            disabled={selectedIndex !== null}
          >
            {option.text}
          </button>
        ))}
      </div>
    </div>
  )
}
```

Добавить стили в конец `frontend/src/index.css`:
```css
/* ImageDescription */
.image-description__img {
  width: 100%;
  border-radius: var(--radius-card);
  object-fit: cover;
  max-height: 200px;
  background: var(--color-surface-high);
}
```

- [ ] **Step 2: Commit**

```bash
cd /Users/ekaterina/Project/greek-a2 && git add frontend/src/features/exercises/types/ImageDescription.tsx frontend/src/index.css && git commit -m "feat(frontend): add ImageDescription exercise type"
```

---

### Task 8: Dialogue тип упражнения

**Files:**
- Create: `frontend/src/features/exercises/types/Dialogue.tsx`

Content schema (из сгенерированных JSON файлов):
```json
{
  "dialogue_lines": [
    { "id": 1, "speaker": "Α", "text": "Πώς φροντίζεις την υγεία σου;" },
    { "id": 2, "speaker": "Β", "text": "Γυμνάζομαι τρεις φορές και ___ υγιεινά." }
  ],
  "table_blanks": [{ "row": "Β", "column": "Συνήθεια", "correct": "τρώω" }],
  "word_bank": ["τρώω", "αποφεύγω", "αισθάνομαι", "γυμνάζω"]
}
```

- [ ] **Step 1: Создать Dialogue.tsx**

```tsx
// frontend/src/features/exercises/types/Dialogue.tsx
import { useState } from 'react'

interface DialogueLine {
  id: number
  speaker: string
  text: string
  audio_path?: string | null
}

interface TableBlank {
  row: string
  column: string
  correct: string
}

interface DialogueContent {
  dialogue_lines: DialogueLine[]
  table_blanks: TableBlank[]
  word_bank: string[]
}

interface DialogueProps {
  content: DialogueContent
  onAnswer: (isCorrect: boolean) => void
}

export function Dialogue({ content, onAnswer }: DialogueProps) {
  // Fills map: blank index → selected word
  const [fills, setFills] = useState<Record<number, string>>({})
  const [submitted, setSubmitted] = useState(false)

  const allFilled = content.table_blanks.every((_, i) => fills[i] !== undefined)

  const handleWordSelect = (blankIndex: number, word: string) => {
    if (submitted) return
    setFills(f => ({ ...f, [blankIndex]: word }))
  }

  const handleSubmit = () => {
    if (!allFilled || submitted) return
    setSubmitted(true)
    const allCorrect = content.table_blanks.every((blank, i) => fills[i] === blank.correct)
    onAnswer(allCorrect)
  }

  const renderLine = (line: DialogueLine) => {
    const blanks = content.table_blanks.filter(b => b.row === line.speaker)
    let text = line.text
    blanks.forEach((_, bi) => {
      const blankIndex = content.table_blanks.indexOf(blanks[bi])
      const filled = fills[blankIndex]
      text = text.replace('___', filled ? `[${filled}]` : '___')
    })
    return text
  }

  return (
    <div className="dialogue">
      <div className="dialogue__lines">
        {content.dialogue_lines.map(line => (
          <div key={line.id} className={`dialogue__line dialogue__line--${line.speaker === 'Α' ? 'a' : 'b'}`}>
            <span className="dialogue__speaker">{line.speaker}</span>
            <p className="dialogue__text">{renderLine(line)}</p>
          </div>
        ))}
      </div>

      {content.table_blanks.length > 0 && (
        <div className="dialogue__fill-section">
          <p className="dialogue__fill-label">Вставьте слово:</p>
          {content.table_blanks.map((blank, i) => (
            <div key={i} className="dialogue__blank-row">
              <span className="dialogue__blank-context">{blank.column} ({blank.row}):</span>
              <div className="dialogue__word-bank">
                {content.word_bank.map(word => {
                  const isSelected = fills[i] === word
                  const isCorrect = submitted && word === blank.correct
                  const isWrong = submitted && isSelected && word !== blank.correct
                  return (
                    <button
                      key={word}
                      className={`fb-option ${isCorrect ? 'fb-option--correct' : ''} ${isWrong ? 'fb-option--incorrect' : ''} ${isSelected && !submitted ? 'fb-option--selected' : ''}`}
                      onClick={() => handleWordSelect(i, word)}
                      disabled={submitted}
                    >
                      {word}
                    </button>
                  )
                })}
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  )
}
```

Добавить стили в конец `frontend/src/index.css`:
```css
/* Dialogue */
.dialogue__lines {
  display: flex;
  flex-direction: column;
  gap: 10px;
  margin-bottom: 20px;
}

.dialogue__line {
  display: flex;
  gap: 10px;
  align-items: flex-start;
}

.dialogue__line--a { flex-direction: row; }
.dialogue__line--b { flex-direction: row-reverse; }

.dialogue__speaker {
  font-size: var(--font-size-label);
  font-weight: var(--font-weight-bold);
  color: var(--color-primary);
  letter-spacing: 0.05em;
  min-width: 20px;
  text-align: center;
  padding-top: 4px;
}

.dialogue__text {
  font-size: var(--font-size-body);
  color: var(--color-on-surface);
  line-height: var(--line-height-normal);
  background: var(--color-surface-high);
  border-radius: var(--radius-card);
  padding: 10px 14px;
  flex: 1;
}

.dialogue__fill-section {
  border-top: 1px solid var(--color-surface-highest);
  padding-top: 16px;
}

.dialogue__fill-label {
  font-size: var(--font-size-label);
  color: var(--color-on-surface-muted);
  text-transform: uppercase;
  letter-spacing: 0.05em;
  margin-bottom: 10px;
}

.dialogue__blank-row {
  margin-bottom: 12px;
}

.dialogue__blank-context {
  font-size: var(--font-size-body);
  color: var(--color-secondary);
  display: block;
  margin-bottom: 8px;
}

.dialogue__word-bank {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}

.fb-option--selected {
  background: var(--color-secondary);
  color: #000;
}
```

- [ ] **Step 2: Commit**

```bash
cd /Users/ekaterina/Project/greek-a2 && git add frontend/src/features/exercises/types/Dialogue.tsx frontend/src/index.css && git commit -m "feat(frontend): add Dialogue exercise type"
```

---

### Task 9: ExerciseScreen — роутер упражнений

**Files:**
- Modify: `frontend/src/features/exercises/ExerciseScreen.tsx`
- Modify: `frontend/src/App.tsx`

ExerciseScreen:
1. Получает `unitId` и `exerciseId` из URL params
2. Загружает список упражнений из `useUnitDetailQuery(unitId)`
3. Загружает данные текущего упражнения из `useExerciseQuery(exerciseId)`
4. После ответа — `enqueue` прогресса, feedback overlay 1.5s → navigate к следующему
5. Если упражнений нет → `/units/:unitId/mini-test`

- [ ] **Step 1: Обновить ExerciseScreen.tsx**

```tsx
// frontend/src/features/exercises/ExerciseScreen.tsx
import { useState } from 'react'
import { useNavigate, useParams } from 'react-router-dom'
import { useUnitDetailQuery } from '../curriculum/useCurriculumQuery'
import { useExerciseQuery } from './useExerciseQuery'
import { ExerciseShell } from './ExerciseShell'
import { TrueFalse } from './types/TrueFalse'
import { MultipleChoice } from './types/MultipleChoice'
import { Matching } from './types/Matching'
import { FillBlank } from './types/FillBlank'
import { ImageDescription } from './types/ImageDescription'
import { Dialogue } from './types/Dialogue'
import { useSyncQueue } from '../../shared/store/useSyncQueue'
import { useTelegram } from '../../shared/hooks/useTelegram'
import { useSettings } from '../../shared/hooks/useSettings'

const EXERCISE_INSTRUCTIONS: Record<string, string> = {
  true_false: 'Σωστό ή Λάθος;',
  multiple_choice: 'Επιλέξτε τη σωστή απάντηση.',
  matching: 'Αντιστοιχίστε τις λέξεις.',
  fill_blank: 'Συμπληρώστε το κενό.',
  image_description: 'Περιγράψτε την εικόνα.',
  dialogue: 'Συμπληρώστε τον διάλογο.',
}

export function ExerciseScreen() {
  const { unitId, exerciseId } = useParams<{ unitId: string; exerciseId: string }>()
  const navigate = useNavigate()
  const { enqueue } = useSyncQueue()
  const { haptic } = useTelegram()
  const { showTranslations } = useSettings()

  const unitQuery = useUnitDetailQuery(Number(unitId))
  const exerciseQuery = useExerciseQuery(Number(exerciseId))

  const [answered, setAnswered] = useState(false)
  const [isCorrect, setIsCorrect] = useState(false)
  const [showFeedback, setShowFeedback] = useState(false)

  if (unitQuery.isLoading || exerciseQuery.isLoading) {
    return <div className="screen-loading">Φόρτωση...</div>
  }

  const exercises = unitQuery.data?.exercises ?? []
  const currentIdx = exercises.findIndex(e => e.id === Number(exerciseId))
  const exercise = exerciseQuery.data

  if (!exercise) return null

  const handleAnswer = (correct: boolean) => {
    setAnswered(true)
    setIsCorrect(correct)
    haptic.impact()
  }

  const handleSubmit = () => {
    if (!answered) return

    // Enqueue progress
    enqueue({ exercise_id: Number(exerciseId), score: isCorrect ? 1 : 0, timestamp: new Date().toISOString() })

    // Feedback + navigate
    setShowFeedback(true)
    haptic.notification(isCorrect ? 'success' : 'error')

    setTimeout(() => {
      setShowFeedback(false)
      const nextExercise = exercises[currentIdx + 1]
      if (nextExercise) {
        navigate(`/units/${unitId}/exercise/${nextExercise.id}`)
      } else {
        navigate(`/units/${unitId}/mini-test`)
      }
    }, 1500)
  }

  const instruction = showTranslations
    ? EXERCISE_INSTRUCTIONS[exercise.type] ?? ''
    : EXERCISE_INSTRUCTIONS[exercise.type] ?? ''

  const content = exercise.content as Record<string, unknown>

  return (
    <>
      <ExerciseShell
        current={currentIdx + 1}
        total={exercises.length}
        instruction={instruction}
        audioPath={exercise.audio_paths[0] ?? null}
        canSubmit={answered}
        submitted={answered}
        onSubmit={handleSubmit}
      >
        {exercise.type === 'true_false' && (
          <TrueFalse content={content as Parameters<typeof TrueFalse>[0]['content']} onAnswer={handleAnswer} />
        )}
        {exercise.type === 'multiple_choice' && (
          <MultipleChoice content={content as Parameters<typeof MultipleChoice>[0]['content']} onAnswer={handleAnswer} />
        )}
        {exercise.type === 'matching' && (
          <Matching content={content as Parameters<typeof Matching>[0]['content']} onAnswer={handleAnswer} />
        )}
        {exercise.type === 'fill_blank' && (
          <FillBlank content={content as Parameters<typeof FillBlank>[0]['content']} onAnswer={handleAnswer} />
        )}
        {exercise.type === 'image_description' && (
          <ImageDescription content={content as Parameters<typeof ImageDescription>[0]['content']} onAnswer={handleAnswer} />
        )}
        {exercise.type === 'dialogue' && (
          <Dialogue content={content as Parameters<typeof Dialogue>[0]['content']} onAnswer={handleAnswer} />
        )}
      </ExerciseShell>

      {showFeedback && (
        <div className={`feedback-overlay feedback-overlay--${isCorrect ? 'correct' : 'incorrect'}`}>
          <span className="feedback-overlay__icon">{isCorrect ? '✓' : '✗'}</span>
        </div>
      )}
    </>
  )
}
```

Добавить стили в конец `frontend/src/index.css`:
```css
/* Feedback overlay */
.feedback-overlay {
  position: fixed;
  inset: 0;
  display: flex;
  align-items: center;
  justify-content: center;
  pointer-events: none;
  z-index: 100;
}

.feedback-overlay--correct { background: rgba(34, 197, 94, 0.15); }
.feedback-overlay--incorrect { background: rgba(239, 68, 68, 0.15); }

.feedback-overlay__icon {
  font-size: 6rem;
  font-weight: var(--font-weight-bold);
}

.feedback-overlay--correct .feedback-overlay__icon { color: var(--color-success); }
.feedback-overlay--incorrect .feedback-overlay__icon { color: var(--color-error); }

/* Screen loading */
.screen-loading {
  display: flex;
  align-items: center;
  justify-content: center;
  min-height: 100dvh;
  font-size: var(--font-size-title);
  color: var(--color-on-surface-muted);
}
```

- [ ] **Step 2: Commit**

```bash
cd /Users/ekaterina/Project/greek-a2 && git add frontend/src/features/exercises/ExerciseScreen.tsx frontend/src/index.css && git commit -m "feat(frontend): implement ExerciseScreen with all 6 exercise types"
```

---

### Task 10: MiniTestScreen

**Files:**
- Create: `frontend/src/features/exercises/MiniTestScreen.tsx`
- Create: `frontend/src/features/exercises/__tests__/MiniTestScreen.test.tsx`

- [ ] **Step 1: Написать тест**

```typescript
// frontend/src/features/exercises/__tests__/MiniTestScreen.test.tsx
import { render, screen, waitFor } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { MemoryRouter, Route, Routes } from 'react-router-dom'
import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { MiniTestScreen } from '../MiniTestScreen'
import { vi } from 'vitest'

vi.mock('../../../shared/api/endpoints', () => ({
  api: {
    getMiniTest: vi.fn().mockResolvedValue({
      questions: [
        { id: 1, type: 'true_false', content: { statement: 'Η Αθήνα είναι πρωτεύουσα.', is_true: true } },
        { id: 2, type: 'multiple_choice', content: { question: 'Τι σημαίνει;', options: ['A', 'B', 'C', 'D'], correct_index: 0 } },
      ],
    }),
    completeMiniTest: vi.fn().mockResolvedValue({ unit_completed: true, xp_earned: 25, cards_added_to_vocab: 5 }),
  },
}))

const createWrapper = () => {
  const queryClient = new QueryClient({ defaultOptions: { queries: { retry: false } } })
  return ({ children }: { children: React.ReactNode }) => (
    <QueryClientProvider client={queryClient}>
      <MemoryRouter initialEntries={['/units/1/mini-test']}>
        <Routes>
          <Route path="/units/:unitId/mini-test" element={children} />
          <Route path="/units/:unitId/result" element={<div>result screen</div>} />
        </Routes>
      </MemoryRouter>
    </QueryClientProvider>
  )
}

describe('MiniTestScreen', () => {
  it('shows loading state initially', () => {
    render(<MiniTestScreen />, { wrapper: createWrapper() })
    expect(screen.getByText(/φόρτωση/i)).toBeInTheDocument()
  })

  it('renders first question after load', async () => {
    render(<MiniTestScreen />, { wrapper: createWrapper() })
    await waitFor(() => {
      expect(screen.getByText(/πρωτεύουσα/)).toBeInTheDocument()
    })
  })
})
```

- [ ] **Step 2: Запустить тест — убедиться, что падает**

```bash
cd /Users/ekaterina/Project/greek-a2/frontend && npx vitest run src/features/exercises/__tests__/MiniTestScreen.test.tsx
```

Ожидаемый результат: FAIL.

- [ ] **Step 3: Создать MiniTestScreen.tsx**

```tsx
// frontend/src/features/exercises/MiniTestScreen.tsx
import { useState } from 'react'
import { useNavigate, useParams } from 'react-router-dom'
import { useMiniTestQuery } from './useMiniTestQuery'
import { ExerciseShell } from './ExerciseShell'
import { TrueFalse } from './types/TrueFalse'
import { MultipleChoice } from './types/MultipleChoice'
import { FillBlank } from './types/FillBlank'
import { api } from '../../shared/api/endpoints'
import { useAppStore } from '../../shared/store/useAppStore'
import { useTelegram } from '../../shared/hooks/useTelegram'

const INSTRUCTIONS: Record<string, string> = {
  true_false: 'Σωστό ή Λάθος;',
  multiple_choice: 'Επιλέξτε τη σωστή απάντηση.',
  fill_blank: 'Συμπληρώστε το κενό.',
}

export function MiniTestScreen() {
  const { unitId } = useParams<{ unitId: string }>()
  const navigate = useNavigate()
  const { haptic } = useTelegram()
  const addXp = useAppStore(s => s.addXp)

  const miniTestQuery = useMiniTestQuery(Number(unitId))

  const [currentIndex, setCurrentIndex] = useState(0)
  const [score, setScore] = useState(0)
  const [answered, setAnswered] = useState(false)
  const [submitting, setSubmitting] = useState(false)

  if (miniTestQuery.isLoading) return <div className="screen-loading">Φόρτωση...</div>

  const questions = miniTestQuery.data?.questions ?? []
  const question = questions[currentIndex]
  if (!question) return null

  const total = questions.length

  const handleAnswer = (isCorrect: boolean) => {
    setAnswered(true)
    if (isCorrect) setScore(s => s + 1)
    haptic.impact()
  }

  const handleSubmit = async () => {
    if (submitting) return
    haptic.notification(answered ? 'success' : 'error')

    if (currentIndex < total - 1) {
      setTimeout(() => {
        setCurrentIndex(i => i + 1)
        setAnswered(false)
      }, 1000)
      return
    }

    // Last question — complete mini-test
    setSubmitting(true)
    try {
      const result = await api.completeMiniTest(Number(unitId), score + (answered ? 1 : 0), total)
      if (result.xp_earned > 0) addXp(result.xp_earned)
      navigate(`/units/${unitId}/result`, { state: result })
    } finally {
      setSubmitting(false)
    }
  }

  return (
    <ExerciseShell
      current={currentIndex + 1}
      total={total}
      instruction={INSTRUCTIONS[question.type] ?? ''}
      audioPath={null}
      canSubmit={answered}
      submitted={answered}
      onSubmit={handleSubmit}
    >
      {question.type === 'true_false' && (
        <TrueFalse
          content={question.content as Parameters<typeof TrueFalse>[0]['content']}
          onAnswer={handleAnswer}
        />
      )}
      {question.type === 'multiple_choice' && (
        <MultipleChoice
          content={question.content as Parameters<typeof MultipleChoice>[0]['content']}
          onAnswer={handleAnswer}
        />
      )}
      {question.type === 'fill_blank' && (
        <FillBlank
          content={question.content as Parameters<typeof FillBlank>[0]['content']}
          onAnswer={handleAnswer}
        />
      )}
    </ExerciseShell>
  )
}
```

- [ ] **Step 4: Запустить тест — убедиться, что проходит**

```bash
cd /Users/ekaterina/Project/greek-a2/frontend && npx vitest run src/features/exercises/__tests__/MiniTestScreen.test.tsx
```

Ожидаемый результат: все тесты PASS.

- [ ] **Step 5: Commit**

```bash
cd /Users/ekaterina/Project/greek-a2 && git add frontend/src/features/exercises/MiniTestScreen.tsx frontend/src/features/exercises/useMiniTestQuery.ts frontend/src/features/exercises/__tests__/MiniTestScreen.test.tsx && git commit -m "feat(frontend): add MiniTestScreen"
```

---

### Task 11: UnitResultScreen

**Files:**
- Create: `frontend/src/features/exercises/UnitResultScreen.tsx`
- Modify: `frontend/src/App.tsx`

- [ ] **Step 1: Создать UnitResultScreen.tsx**

```tsx
// frontend/src/features/exercises/UnitResultScreen.tsx
import { useLocation, useNavigate } from 'react-router-dom'
import { Button } from '../../shared/components/Button'
import type { MiniTestCompleteResponse } from '../../shared/api/types'

export function UnitResultScreen() {
  const navigate = useNavigate()
  const location = useLocation()
  const result = location.state as MiniTestCompleteResponse | null

  const xp = result?.xp_earned ?? 0
  const cardsAdded = result?.cards_added_to_vocab ?? 0

  return (
    <div className="unit-result">
      <div className="unit-result__trophy">🏆</div>
      <h1 className="unit-result__title">Μπράβο!</h1>
      <p className="unit-result__subtitle">Ολοκληρώσατε τη μονάδα</p>

      <div className="unit-result__stats">
        <div className="unit-result__stat">
          <span className="unit-result__stat-value">+{xp}</span>
          <span className="unit-result__stat-label">XP</span>
        </div>
        {cardsAdded > 0 && (
          <div className="unit-result__stat">
            <span className="unit-result__stat-value">+{cardsAdded}</span>
            <span className="unit-result__stat-label">ΛΕΞΕΙΣ</span>
          </div>
        )}
      </div>

      <Button onClick={() => navigate('/levels')} variant="primary" fullWidth>
        Στον χάρτη
      </Button>
    </div>
  )
}
```

Добавить стили в конец `frontend/src/index.css`:
```css
/* UnitResultScreen */
.unit-result {
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

.unit-result__trophy {
  font-size: var(--font-size-display);
  line-height: 1;
}

.unit-result__title {
  font-size: var(--font-size-headline);
  font-weight: var(--font-weight-bold);
  color: var(--color-primary);
}

.unit-result__subtitle {
  font-size: var(--font-size-body);
  color: var(--color-on-surface-muted);
}

.unit-result__stats {
  display: flex;
  gap: 32px;
  margin: 16px 0;
}

.unit-result__stat {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 4px;
}

.unit-result__stat-value {
  font-size: var(--font-size-headline);
  font-weight: var(--font-weight-bold);
  color: var(--color-on-surface);
}

.unit-result__stat-label {
  font-size: var(--font-size-label);
  font-weight: var(--font-weight-bold);
  color: var(--color-on-surface-muted);
  letter-spacing: 0.05em;
}
```

- [ ] **Step 2: Добавить маршруты в App.tsx**

Открыть `frontend/src/App.tsx`. Найти блок `<Routes>` и добавить маршруты мини-теста и результата:

```tsx
<Route path="/units/:unitId/mini-test" element={<MiniTestScreen />} />
<Route path="/units/:unitId/result" element={<UnitResultScreen />} />
```

Также добавить импорты:
```tsx
import { MiniTestScreen } from './features/exercises/MiniTestScreen'
import { UnitResultScreen } from './features/exercises/UnitResultScreen'
```

- [ ] **Step 3: Commit**

```bash
cd /Users/ekaterina/Project/greek-a2 && git add frontend/src/features/exercises/UnitResultScreen.tsx frontend/src/App.tsx frontend/src/index.css && git commit -m "feat(frontend): add UnitResultScreen and complete exercise routing"
```

---

### Task 12: Финальная проверка

- [ ] **Step 1: Запустить все тесты**

```bash
cd /Users/ekaterina/Project/greek-a2/frontend && npx vitest run
```

Ожидаемый результат: все тесты PASS, нет ошибок TypeScript.

- [ ] **Step 2: Проверить TypeScript**

```bash
cd /Users/ekaterina/Project/greek-a2/frontend && npx tsc --noEmit
```

Ожидаемый результат: нет ошибок.
