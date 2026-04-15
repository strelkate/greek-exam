import { useState } from 'react'

interface ImageOption { text: string; is_correct: boolean }
interface ImageDescriptionContent { image_url: string; question: string; options: ImageOption[] }
interface ImageDescriptionProps { content: ImageDescriptionContent; onAnswer: (isCorrect: boolean) => void }

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
      <img src={content.image_url} alt="упражнение" className="image-description__img" />
      <p className="multiple-choice__question">{content.question}</p>
      <div className="multiple-choice__options">
        {content.options.map((option, index) => (
          <button key={index} className={getOptionClass(index)} onClick={() => handleSelect(index)} disabled={selectedIndex !== null}>
            {option.text}
          </button>
        ))}
      </div>
    </div>
  )
}
