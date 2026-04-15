import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { useDueCardsQuery } from './useVocabularyQuery'
import { api } from '../../shared/api/endpoints'
import { AudioPlayer } from '../../shared/components/AudioPlayer'
import { Button } from '../../shared/components/Button'
import { ProgressBar } from '../../shared/components/ProgressBar'
import { useAppStore } from '../../shared/store/useAppStore'
import { useTelegram } from '../../shared/hooks/useTelegram'

type FlashcardPhase = 'front' | 'back' | 'done'

export function FlashcardScreen() {
  const navigate = useNavigate()
  const dueQuery = useDueCardsQuery()
  const addXp = useAppStore(s => s.addXp)
  const { haptic } = useTelegram()

  const [currentIndex, setCurrentIndex] = useState(0)
  const [phase, setPhase] = useState<FlashcardPhase>('front')
  const [totalXp, setTotalXp] = useState(0)
  const [knewCount, setKnewCount] = useState(0)

  if (dueQuery.isLoading) return <div className="screen-loading">Φόρτωση...</div>

  const cards = dueQuery.data?.cards ?? []
  const total = cards.length
  const card = cards[currentIndex]

  if (phase === 'done' || total === 0) {
    return (
      <div className="flashcard-done">
        <div className="flashcard-done__icon">🎉</div>
        <h1 className="flashcard-done__title">Τέλος!</h1>
        <p className="flashcard-done__subtitle">
          {knewCount} / {total} — {totalXp} XP
        </p>
        <Button onClick={() => navigate('/vocabulary')} variant="primary" fullWidth>
          Επιστροφή στο λεξιλόγιο
        </Button>
      </div>
    )
  }

  const handleFlip = () => {
    haptic.impact()
    setPhase('back')
  }

  const handleReview = async (knew: boolean) => {
    haptic.notification(knew ? 'success' : 'error')
    try {
      const result = await api.reviewCard(card.id, knew)
      if (result.xp_earned > 0) {
        addXp(result.xp_earned)
        setTotalXp(x => x + result.xp_earned)
      }
    } catch {
      // offline — progress lost, don't crash
    }
    if (knew) setKnewCount(k => k + 1)

    if (currentIndex + 1 >= total) {
      setPhase('done')
    } else {
      setCurrentIndex(i => i + 1)
      setPhase('front')
    }
  }

  return (
    <div className="flashcard-screen">
      <div className="flashcard-screen__header">
        <ProgressBar value={currentIndex + 1} max={total} />
        <span className="flashcard-screen__counter">{currentIndex + 1} / {total}</span>
      </div>

      <div className={`flashcard ${phase === 'back' ? 'flashcard--flipped' : ''}`}>
        <div className="flashcard__front">
          <p className="flashcard__word">{card.word_gr}</p>
          {card.audio_path && (
            <AudioPlayer src={card.audio_path} ariaLabel="аудио" />
          )}
        </div>
        {phase === 'back' && (
          <div className="flashcard__back">
            <p className="flashcard__word">{card.word_gr}</p>
            <p className="flashcard__translation">{card.word_ru}</p>
          </div>
        )}
      </div>

      <div className="flashcard-screen__actions">
        {phase === 'front' && (
          <Button onClick={handleFlip} variant="primary" fullWidth>
            Εμφάνιση
          </Button>
        )}
        {phase === 'back' && (
          <div className="flashcard-screen__rating">
            <button className="rating-btn rating-btn--no" onClick={() => handleReview(false)}>
              ✗ Δεν ήξερα
            </button>
            <button className="rating-btn rating-btn--yes" onClick={() => handleReview(true)}>
              ✓ Ήξερα
            </button>
          </div>
        )}
      </div>
    </div>
  )
}
