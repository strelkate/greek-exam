import { useState } from 'react'

interface ImageOption {
  id: number
  path: string
  is_correct: boolean
}
interface ImageDescriptionContent {
  description_text: string
  description_text_ru?: string
  images: ImageOption[]
}
interface ImageDescriptionProps {
  content: ImageDescriptionContent
  onAnswer: (isCorrect: boolean) => void
  submitted?: boolean
}

export function ImageDescription({ content, onAnswer, submitted = false }: ImageDescriptionProps) {
  const [selectedId, setSelectedId] = useState<number | null>(null)

  const handleSelect = (img: ImageOption) => {
    if (submitted) return
    setSelectedId(img.id)
    onAnswer(img.is_correct)
  }

  const getImgClass = (img: ImageOption) => {
    if (selectedId === null) return 'img-desc__option'
    if (!submitted)
      return img.id === selectedId
        ? 'img-desc__option img-desc__option--selected'
        : 'img-desc__option'
    if (img.is_correct) return 'img-desc__option img-desc__option--correct'
    if (img.id === selectedId) return 'img-desc__option img-desc__option--incorrect'
    return 'img-desc__option img-desc__option--dim'
  }

  return (
    <div className="img-desc">
      <p className="img-desc__text">{content.description_text}</p>
      <div className="img-desc__grid">
        {content.images.map((img) => (
          <button
            key={img.id}
            className={getImgClass(img)}
            onClick={() => handleSelect(img)}
            disabled={submitted}
          >
            <img src={img.path} alt="" className="img-desc__img" />
          </button>
        ))}
      </div>
      {submitted && content.description_text_ru && (
        <p className="fill-blank__translation">{content.description_text_ru}</p>
      )}
    </div>
  )
}
