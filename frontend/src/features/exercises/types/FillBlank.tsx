import { useState } from 'react'

interface FillBlankContent {
  sentence?: string
  blank_word?: string
  options?: string[]
  text_template?: string
  blanks?: Array<{ position: number; correct: string }>
  word_bank?: string[]
  sentence_ru?: string
}

interface FillBlankProps {
  content: FillBlankContent
  onAnswer: (isCorrect: boolean) => void
  submitted?: boolean
}

export function FillBlank({ content, onAnswer, submitted = false }: FillBlankProps) {
  const [selected, setSelected] = useState<string | null>(null)

  const sentence = content.sentence ?? content.text_template ?? ''
  const blankWord = content.blank_word ?? content.blanks?.[0]?.correct ?? ''
  const options = content.options ?? content.word_bank ?? []

  const handleSelect = (word: string) => {
    if (selected !== null) return
    setSelected(word)
    onAnswer(word === blankWord)
  }

  const sentenceParts = sentence.split('___')

  const getOptionClass = (word: string) => {
    if (selected === null) return 'fb-option'
    if (!submitted) return word === selected ? 'fb-option fb-option--selected' : 'fb-option'
    if (word === blankWord) return 'fb-option fb-option--correct'
    if (word === selected) return 'fb-option fb-option--incorrect'
    return 'fb-option fb-option--dim'
  }

  const blankClass = selected
    ? submitted
      ? selected === blankWord ? 'fill-blank__blank--correct' : 'fill-blank__blank--incorrect'
      : ''
    : ''

  return (
    <div className="fill-blank">
      <p className="fill-blank__sentence">
        {sentenceParts[0]}
        <span className={`fill-blank__blank ${blankClass}`}>
          {selected ?? '___'}
        </span>
        {sentenceParts[1]}
      </p>
      <div className="fill-blank__word-bank">
        {options.map((word) => (
          <button key={word} className={getOptionClass(word)} onClick={() => handleSelect(word)} disabled={selected !== null}>
            {word}
          </button>
        ))}
      </div>
      {submitted && content.sentence_ru && (
        <p className="fill-blank__translation">{content.sentence_ru}</p>
      )}
    </div>
  )
}
