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
