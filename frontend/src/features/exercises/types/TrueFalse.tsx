import { useState } from 'react'

interface Statement { id: number; text: string; correct: boolean }

interface TrueFalseContent {
  statement?: string
  is_true?: boolean
  explanation?: string
  text?: string
  text_ru?: string
  statements?: Statement[]
}

interface TrueFalseProps {
  content: TrueFalseContent
  onAnswer: (isCorrect: boolean) => void
  submitted?: boolean
}

export function TrueFalse({ content, onAnswer, submitted = false }: TrueFalseProps) {
  const [selected, setSelected] = useState<boolean | null>(null)
  const [stmtAnswers, setStmtAnswers] = useState<Record<number, boolean | null>>({})
  const [allFilled, setAllFilled] = useState(false)
  const [shuffledStatements] = useState(() =>
    content.statements ? [...content.statements].sort(() => Math.random() - 0.5) : []
  )

  // New API shape: text + statements[]
  if (content.statements && content.text) {
    const handleToggle = (stmtId: number, value: boolean) => {
      if (allFilled) return
      const updated = { ...stmtAnswers, [stmtId]: value }
      setStmtAnswers(updated)
      const filled = shuffledStatements.every(s => updated[s.id] != null)
      if (filled) {
        const allCorrect = shuffledStatements.every(s => updated[s.id] === s.correct)
        setAllFilled(true)
        onAnswer(allCorrect)
      }
    }

    return (
      <div className="true-false">
        <p className="true-false__statement">{content.text}</p>
        <div style={{ display: 'flex', alignItems: 'center', padding: '0 16px', marginTop: 16, marginBottom: 8 }}>
          <span style={{ flex: 1 }} />
          <div style={{ width: 80, display: 'flex', justifyContent: 'space-between', flexShrink: 0 }}>
            <span style={{ width: 28, textAlign: 'center', fontSize: '0.6875rem', fontWeight: 700, color: 'rgba(255,255,255,0.6)', letterSpacing: '0.03em' }}>ΣΩΣΤΟ</span>
            <span style={{ width: 28, textAlign: 'center', fontSize: '0.6875rem', fontWeight: 700, color: 'rgba(255,255,255,0.6)', letterSpacing: '0.03em' }}>ΛΑΘΟΣ</span>
          </div>
        </div>
        {shuffledStatements.map(stmt => {
          const answer = stmtAnswers[stmt.id]
          return (
            <div key={stmt.id} style={{ display: 'flex', alignItems: 'center', gap: 16, background: 'var(--color-surface-high)', borderRadius: 8, padding: 16, marginBottom: 8 }}>
              <p style={{ flex: 1, fontSize: '0.875rem', lineHeight: 1.5, color: '#fff' }}>{stmt.text}</p>
              <div style={{ width: 80, display: 'flex', justifyContent: 'space-between', flexShrink: 0 }}>
                <button
                  type="button"
                  onClick={() => handleToggle(stmt.id, true)}
                  style={{
                    width: 28, height: 28, border: `2px solid ${submitted && stmt.correct === true ? 'var(--color-success)' : submitted && answer === true && !stmt.correct ? 'var(--color-error)' : answer === true ? 'var(--color-primary)' : 'var(--color-surface-highest)'}`,
                    borderRadius: 6, background: submitted && stmt.correct === true ? 'var(--color-success)' : submitted && answer === true && !stmt.correct ? 'var(--color-error)' : answer === true ? 'var(--color-primary)' : 'transparent',
                    cursor: allFilled ? 'default' : 'pointer', display: 'flex', alignItems: 'center', justifyContent: 'center', padding: 0, transition: 'border-color 0.15s, background 0.15s',
                  }}
                >
                  {answer === true && <span style={{ fontSize: 16, fontWeight: 700, color: '#0b0d1a', lineHeight: 1 }}>✓</span>}
                </button>
                <button
                  type="button"
                  onClick={() => handleToggle(stmt.id, false)}
                  style={{
                    width: 28, height: 28, border: `2px solid ${submitted && stmt.correct === false ? 'var(--color-success)' : submitted && answer === false && stmt.correct ? 'var(--color-error)' : answer === false ? 'var(--color-primary)' : 'var(--color-surface-highest)'}`,
                    borderRadius: 6, background: submitted && stmt.correct === false ? 'var(--color-success)' : submitted && answer === false && stmt.correct ? 'var(--color-error)' : answer === false ? 'var(--color-primary)' : 'transparent',
                    cursor: allFilled ? 'default' : 'pointer', display: 'flex', alignItems: 'center', justifyContent: 'center', padding: 0, transition: 'border-color 0.15s, background 0.15s',
                  }}
                >
                  {answer === false && <span style={{ fontSize: 16, fontWeight: 700, color: '#0b0d1a', lineHeight: 1 }}>✓</span>}
                </button>
              </div>
            </div>
          )
        })}
      {submitted && content.text_ru && (
        <p className="fill-blank__translation">{content.text_ru}</p>
      )}
      </div>
    )
  }

  // Legacy shape: single statement + is_true
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
        <button className={getButtonClass(true)} onClick={() => handleSelect(true)} disabled={selected !== null}>
          Σωστό ✓
        </button>
        <button className={getButtonClass(false)} onClick={() => handleSelect(false)} disabled={selected !== null}>
          Λάθος ✗
        </button>
      </div>
      {selected !== null && content.explanation && (
        <p className="true-false__explanation">{content.explanation}</p>
      )}
    </div>
  )
}
