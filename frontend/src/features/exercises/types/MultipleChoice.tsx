import { useState } from 'react'

interface OptionObj {
  id: string
  text: string
}

interface MultipleChoiceContent {
  question: string
  options: (string | OptionObj)[]
  correct_index?: number
  correct_id?: string
  question_ru?: string
}

interface MultipleChoiceProps {
  content: MultipleChoiceContent
  onAnswer: (isCorrect: boolean) => void
  submitted?: boolean
}

export function MultipleChoice({ content, onAnswer, submitted = false }: MultipleChoiceProps) {
  const [selected, setSelected] = useState<number | null>(null)

  const optionTexts = content.options.map((o) => (typeof o === 'string' ? o : o.text))
  const correctIndex =
    content.correct_index ??
    content.options.findIndex((o) => typeof o !== 'string' && o.id === content.correct_id)

  const handleSelect = (index: number) => {
    if (selected !== null) return
    setSelected(index)
    onAnswer(index === correctIndex)
  }

  const getOptionClass = (index: number) => {
    if (selected === null) return 'mc-option'
    if (!submitted) return index === selected ? 'mc-option mc-option--selected' : 'mc-option'
    if (index === correctIndex) return 'mc-option mc-option--correct'
    if (index === selected) return 'mc-option mc-option--incorrect'
    return 'mc-option mc-option--dim'
  }

  const questionParts = content.question.split('___')
  const hasBlank = questionParts.length > 1

  return (
    <div className="multiple-choice">
      <p className="multiple-choice__question">
        {hasBlank ? (
          <>
            {questionParts[0]}
            <span className="fill-blank__blank">___</span>
            {questionParts[1]}
          </>
        ) : (
          content.question
        )}
      </p>
      <div className="multiple-choice__options">
        {optionTexts.map((option, index) => (
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
      {submitted && content.question_ru && (
        <p className="fill-blank__translation">{content.question_ru}</p>
      )}
    </div>
  )
}
