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
  const [tfAnswers, setTfAnswers] = useState<Record<number, boolean | null>>({})
  const [shuffledTfStatements] = useState(() => {
    const raw = question.content as any
    const inner = raw?.content ?? raw
    if (question.type === 'true_false' && inner?.statements) {
      return [...inner.statements].sort(() => Math.random() - 0.5)
    }
    return inner?.statements ?? []
  })

  // API returns nested { type, content, correct_answer } — unwrap inner content
  const rawContent = question.content as any
  const innerContent = rawContent?.content ?? rawContent

  const handleCheck = () => {
    if (question.type === 'true_false') {
      const allAnswered = shuffledTfStatements.every((s: any) => tfAnswers[s.id] != null)
      if (!allAnswered) return
      setChecked(true)
      const allCorrect = shuffledTfStatements.every((s: any) => tfAnswers[s.id] === s.correct)
      setTimeout(() => {
        setSelected(null)
        setChecked(false)
        setTfAnswers({})
        onAnswer(allCorrect)
      }, 800)
      return
    }

    if (!selected) return
    setChecked(true)
    const isCorrect = (() => {
      if (question.type === 'multiple_choice') {
        return selected === (innerContent as { correct_id: string }).correct_id
      }
      if (question.type === 'fill_blank') {
        const blank = (innerContent as { blanks: Array<{ correct: string }> }).blanks[0]
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
    const c = innerContent as { question: string; options: Array<{ id: string; text: string }>; correct_id: string }
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
    const c = innerContent as { text: string; statements: Array<{ id: number; text: string; correct: boolean }> }
    const allAnswered = shuffledTfStatements.every((s: any) => tfAnswers[s.id] != null)
    return (
      <div className={styles.container}>
        <p className={styles.passage}>{c.text}</p>
        <div className={styles.tfHeader}>
          <span className={styles.tfHeaderSpacer} />
          <div className={styles.tfHeaderLabels}>
            <span className={styles.tfLabel}>ΣΩΣΤΟ</span>
            <span className={styles.tfLabel}>ΛΑΘΟΣ</span>
          </div>
        </div>
        {shuffledTfStatements.map((stmt: any) => {
          const answer = tfAnswers[stmt.id]
          const isCorrectAnswer = checked && answer === stmt.correct
          const isWrongAnswer = checked && answer != null && answer !== stmt.correct
          return (
            <div key={stmt.id} className={styles.tfRow}>
              <p className={styles.tfText}>{stmt.text}</p>
              <div className={styles.tfChecks}>
                <button
                  type="button"
                  className={[
                    styles.tfCheck,
                    answer === true ? styles.tfCheckChecked : '',
                    checked && stmt.correct === true ? styles.tfCheckCorrect : '',
                    checked && answer === true && stmt.correct !== true ? styles.tfCheckWrong : '',
                  ].join(' ')}
                  onClick={() => !checked && setTfAnswers(prev => ({ ...prev, [stmt.id]: true }))}
                  aria-label="Σωστό"
                >
                  {answer === true && <span className={styles.tfCheckMark}>✓</span>}
                </button>
                <button
                  type="button"
                  className={[
                    styles.tfCheck,
                    answer === false ? styles.tfCheckChecked : '',
                    checked && stmt.correct === false ? styles.tfCheckCorrect : '',
                    checked && answer === false && stmt.correct !== false ? styles.tfCheckWrong : '',
                  ].join(' ')}
                  onClick={() => !checked && setTfAnswers(prev => ({ ...prev, [stmt.id]: false }))}
                  aria-label="Λάθος"
                >
                  {answer === false && <span className={styles.tfCheckMark}>✓</span>}
                </button>
              </div>
            </div>
          )
        })}
        <Button fullWidth disabled={!allAnswered || checked} onClick={handleCheck}>
          Проверить
        </Button>
      </div>
    )
  }

  if (question.type === 'fill_blank') {
    const c = innerContent as { text_template: string; word_bank: string[]; blanks: Array<{ correct: string }> }
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
