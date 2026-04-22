import { useState, useEffect, useRef } from 'react'
import { useNavigate } from 'react-router-dom'
import { useQueryClient } from '@tanstack/react-query'
import { useDueCardsQuery } from './useVocabularyQuery'
import { api } from '../../shared/api/endpoints'
import { Button } from '../../shared/components/Button'
import { ProgressBar } from '../../shared/components/ProgressBar'
import { TtsButton } from '../../shared/components/TtsButton'
import { useAppStore } from '../../shared/store/useAppStore'
import { useTelegram } from '../../shared/hooks/useTelegram'

const API_URL = import.meta.env.VITE_API_URL ?? ''

type FlashcardPhase = 'front' | 'back' | 'done'

export function FlashcardScreen() {
  const navigate = useNavigate()
  const queryClient = useQueryClient()
  const dueQuery = useDueCardsQuery()
  const addXp = useAppStore((s) => s.addXp)
  const { haptic } = useTelegram()

  const [currentIndex, setCurrentIndex] = useState(0)
  const [phase, setPhase] = useState<FlashcardPhase>('front')
  const [totalXp, setTotalXp] = useState(0)
  const [knewCount, setKnewCount] = useState(0)

  const cards = dueQuery.data?.cards ?? []
  const total = cards.length
  const card = cards[currentIndex]
  const audioRef = useRef<HTMLAudioElement | null>(null)

  // Auto-play audio when a new card appears
  useEffect(() => {
    if (!card) return
    const timer = setTimeout(() => {
      if (card.audio_path) {
        const audio = new Audio(`${API_URL}${card.audio_path}`)
        audioRef.current = audio
        audio.play().catch(() => {})
      } else if (typeof window.speechSynthesis !== 'undefined') {
        window.speechSynthesis.cancel()
        const utt = new SpeechSynthesisUtterance(card.word_gr)
        utt.lang = 'el-GR'
        window.speechSynthesis.speak(utt)
      }
    }, 300)
    return () => {
      clearTimeout(timer)
      if (audioRef.current) {
        audioRef.current.pause()
        audioRef.current = null
      }
      window.speechSynthesis?.cancel()
    }
  }, [currentIndex, card])

  if (dueQuery.isLoading) return <div className="screen-loading">Загрузка...</div>

  if (phase === 'done' || total === 0) {
    return (
      <div className="flashcard-done">
        <div className="flashcard-done__icon">🎉</div>
        <h1 className="flashcard-done__title">Готово!</h1>
        <p className="flashcard-done__subtitle">
          {knewCount} / {total} — {totalXp} XP
        </p>
        <Button onClick={() => navigate('/vocabulary')} variant="primary" fullWidth>
          Вернуться к словарю
        </Button>
      </div>
    )
  }

  const handleFlip = () => {
    if (phase !== 'front') return
    haptic.impact()
    setPhase('back')
  }

  const handleReview = async (knew: boolean) => {
    haptic.notification(knew ? 'success' : 'error')
    try {
      const result = await api.reviewCard(card.id, knew)
      if (result.xp_earned > 0) {
        addXp(result.xp_earned)
        setTotalXp((x) => x + result.xp_earned)
      }
    } catch {
      // offline
    }
    if (knew) setKnewCount((k) => k + 1)
    if (currentIndex + 1 >= total) {
      queryClient.invalidateQueries({ queryKey: ['vocab-stats'] })
      queryClient.invalidateQueries({ queryKey: ['due-cards'] })
      setPhase('done')
    } else {
      setCurrentIndex((i) => i + 1)
      setPhase('front')
    }
  }

  return (
    <div className="flashcard-screen">
      <div className="flashcard-screen__header">
        <button
          className="flashcard-screen__close"
          onClick={() => {
            queryClient.invalidateQueries({ queryKey: ['vocab-stats'] })
            queryClient.invalidateQueries({ queryKey: ['due-cards'] })
            navigate('/vocabulary')
          }}
          aria-label="Выйти"
          type="button"
        >
          ✕
        </button>
        <ProgressBar value={currentIndex + 1} max={total} />
        <span className="flashcard-screen__counter">
          {currentIndex + 1} / {total}
        </span>
      </div>

      <div
        className={`flashcard ${phase === 'back' ? 'flashcard--back' : ''}`}
        onClick={handleFlip}
        role="button"
        tabIndex={0}
        aria-label="Перевернуть карточку"
      >
        <div onClick={(e) => e.stopPropagation()}>
          <TtsButton text={card.word_gr} className="flashcard__speak" size={40} />
        </div>
        <p className="flashcard__word">{card.word_gr}</p>
        {phase === 'back' && <p className="flashcard__translation">{card.word_ru}</p>}
        {phase === 'front' && <span className="flashcard__hint">👆</span>}
      </div>

      <div className="flashcard-screen__actions">
        {phase === 'front' && (
          <Button onClick={handleFlip} variant="primary" fullWidth>
            Показать перевод
          </Button>
        )}
        {phase === 'back' && (
          <div className="flashcard-screen__rating">
            <button className="rating-btn rating-btn--no" onClick={() => handleReview(false)}>
              ✗ Не знал(а)
            </button>
            <button className="rating-btn rating-btn--yes" onClick={() => handleReview(true)}>
              ✓ Знал(а)
            </button>
          </div>
        )}
      </div>
    </div>
  )
}
