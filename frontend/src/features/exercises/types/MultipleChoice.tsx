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
          <button key={index} className={getOptionClass(index)} onClick={() => handleSelect(index)} disabled={selected !== null}>
            {option}
          </button>
        ))}
      </div>
    </div>
  )
}
