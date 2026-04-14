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
