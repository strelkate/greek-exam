import { useState, useMemo, useCallback, useRef, useEffect } from 'react'
import { useNavigate, useParams } from 'react-router-dom'
import { useUnitDetailQuery } from '../curriculum/useCurriculumQuery'
import { AudioPlayer } from '../../shared/components/AudioPlayer'
import { Button } from '../../shared/components/Button'
import { ProgressBar } from '../../shared/components/ProgressBar'
import styles from './WordLearningScreen.module.css'

const API_URL = import.meta.env.VITE_API_URL ?? ''

// ──────────────────────────────────────────────
// Types
// ──────────────────────────────────────────────

interface VocabCard {
  id: number
  word_gr: string
  word_ru: string
  audio_path: string | null
}

type SessionCard =
  | { round: 'flashcard'; card: VocabCard }
  | { round: 'gr_to_ru' | 'ru_to_gr'; card: VocabCard }
  | { round: 'matching'; cards: VocabCard[] }

// ──────────────────────────────────────────────
// Helpers
// ──────────────────────────────────────────────

function shuffle<T>(arr: T[]): T[] {
  const a = [...arr]
  for (let i = a.length - 1; i > 0; i--) {
    const j = Math.floor(Math.random() * (i + 1))
    ;[a[i], a[j]] = [a[j], a[i]]
  }
  return a
}

// Чередующийся алгоритм:
// 1. Порция из 3 слов → карточки (запомни)
// 2. MC упражнение на эти слова (gr→ru)
// 3. Ещё порция → карточки + MC
// 4. Когда накопилось 6-8 слов → упражнение на соответствие
// Повторяем до конца списка
function buildSession(cards: VocabCard[]): SessionCard[] {
  if (cards.length === 0) return []

  const shuffled = shuffle(cards)
  const BATCH = 3
  const MATCH_AT = 6

  const result: SessionCard[] = []
  let pool: VocabCard[] = []

  let i = 0
  while (i < shuffled.length) {
    const batch = shuffled.slice(i, i + BATCH)
    i += batch.length

    // Карточки «Запомни слово»
    for (const card of batch) {
      result.push({ round: 'flashcard', card })
    }

    pool = [...pool, ...batch]

    // MC упражнение на слова этой порции (если в словаре >= 4 слов для дистракторов)
    if (cards.length >= 4) {
      for (const card of batch) {
        // Чередуем gr→ru и ru→gr
        const r = result.filter(s => s.round === 'gr_to_ru' || s.round === 'ru_to_gr').length
        result.push({ round: r % 2 === 0 ? 'gr_to_ru' : 'ru_to_gr', card })
      }
    }

    // Упражнение на соответствие когда накопилось достаточно слов
    const isLast = i >= shuffled.length
    if (pool.length >= MATCH_AT || isLast) {
      if (pool.length >= 2) {
        result.push({ round: 'matching', cards: [...pool] })
      }
      pool = []
    }
  }

  return result
}

function buildOptions(card: VocabCard, allCards: VocabCard[], round: 'gr_to_ru' | 'ru_to_gr'): string[] {
  const correctField = round === 'gr_to_ru' ? 'word_ru' : 'word_gr'
  const others = shuffle(allCards.filter(c => c.id !== card.id)).slice(0, 3)
  return shuffle([card[correctField], ...others.map(c => c[correctField])])
}

// ──────────────────────────────────────────────
// Audio helper — must be called inside a user-gesture handler
// ──────────────────────────────────────────────

function playCardAudio(card: VocabCard) {
  if (card.audio_path) {
    const audio = new Audio(`${API_URL}${card.audio_path}`)
    audio.play().catch(() => {})
  } else {
    window.speechSynthesis.cancel()
    const utt = new SpeechSynthesisUtterance(card.word_gr)
    utt.lang = 'el-GR'
    window.speechSynthesis.speak(utt)
  }
}

// ──────────────────────────────────────────────
// TTS button
// ──────────────────────────────────────────────

function TtsButton({ text }: { text: string }) {
  const [speaking, setSpeaking] = useState(false)
  const speak = useCallback(() => {
    window.speechSynthesis.cancel()
    const utt = new SpeechSynthesisUtterance(text)
    utt.lang = 'el-GR'
    utt.onstart = () => setSpeaking(true)
    utt.onend = () => setSpeaking(false)
    utt.onerror = () => setSpeaking(false)
    window.speechSynthesis.speak(utt)
  }, [text])

  return (
    <button className="exercise-shell__tts" onClick={speak} aria-label="Произнести" type="button">
      <img src="/icons/headphones.svg" alt="" width={52} height={52}
        style={{ opacity: speaking ? 0.5 : 1, transition: 'opacity 0.2s' }} />
    </button>
  )
}

// ──────────────────────────────────────────────
// Flashcard slide
// ──────────────────────────────────────────────

function FlashcardSlide({ card, onNext }: { card: VocabCard; onNext: () => void }) {
  return (
    <>
      <div className={styles.content}>
        <p className={styles.roundLabel}>Запомни слово</p>
        <div className={styles.audio}>
          {card.audio_path
            ? <AudioPlayer src={card.audio_path} ariaLabel="Произнести" />
            : <TtsButton text={card.word_gr} />}
        </div>
        <p className={styles.word}>{card.word_gr}</p>
        <p className={styles.translation}>{card.word_ru}</p>
      </div>
      <div className={styles.footer}>
        <Button variant="primary" fullWidth onClick={onNext}>Дальше</Button>
      </div>
    </>
  )
}

// ──────────────────────────────────────────────
// Multiple-choice slide
// ──────────────────────────────────────────────

function McSlide({ card, allCards, round, onNext }: {
  card: VocabCard
  allCards: VocabCard[]
  round: 'gr_to_ru' | 'ru_to_gr'
  onNext: (correct: boolean) => void
}) {
  const options = useMemo(() => buildOptions(card, allCards, round), [card, allCards, round])
  const correctAnswer = round === 'gr_to_ru' ? card.word_ru : card.word_gr
  const promptWord = round === 'gr_to_ru' ? card.word_gr : card.word_ru

  const [selected, setSelected] = useState<string | null>(null)
  const [submitted, setSubmitted] = useState(false)

  const handleSubmit = () => {
    if (submitted) onNext(selected === correctAnswer)
    else setSubmitted(true)
  }

  const optionClass = (opt: string) => {
    const base = [styles.option]
    if (!submitted) {
      if (opt === selected) base.push(styles.optionSelected)
    } else {
      if (opt === correctAnswer) base.push(styles.optionCorrect)
      else if (opt === selected) base.push(styles.optionIncorrect)
      else base.push(styles.optionDim)
    }
    return base.join(' ')
  }

  return (
    <>
      <div className={styles.content}>
        <p className={styles.roundLabel}>{round === 'gr_to_ru' ? 'Выбери перевод' : 'Выбери греческое слово'}</p>
        {round === 'gr_to_ru' && (
          <div className={styles.audio}>
            {card.audio_path
              ? <AudioPlayer src={card.audio_path} ariaLabel="Произнести" />
              : <TtsButton text={card.word_gr} />}
          </div>
        )}
        <p className={styles.word}>{promptWord}</p>
        <div className={styles.options}>
          {options.map(opt => (
            <button key={opt} className={optionClass(opt)}
              onClick={() => { if (!submitted) setSelected(opt) }}
              type="button" disabled={submitted}>
              {opt}
            </button>
          ))}
        </div>
      </div>
      <div className={styles.footer}>
        <Button variant="primary" fullWidth disabled={!selected} onClick={handleSubmit}>
          {submitted ? 'Дальше' : 'Проверить'}
        </Button>
      </div>
    </>
  )
}

// ──────────────────────────────────────────────
// Matching slide
// ──────────────────────────────────────────────

function MatchingSlide({ cards, onNext }: { cards: VocabCard[]; onNext: () => void }) {
  const leftCol = useMemo(() => shuffle(cards), [cards])
  const rightCol = useMemo(() => shuffle(cards), [cards])

  const [selLeft, setSelLeft] = useState<number | null>(null)
  const [selRight, setSelRight] = useState<number | null>(null)
  const [matched, setMatched] = useState<Set<number>>(new Set())
  const [wrong, setWrong] = useState<{ l: number; r: number } | null>(null)
  const [done, setDone] = useState(false)

  const tryMatch = useCallback((leftId: number, rightId: number) => {
    if (leftId === rightId) {
      setMatched(prev => {
        const next = new Set(prev)
        next.add(leftId)
        if (next.size === cards.length) setDone(true)
        return next
      })
      setSelLeft(null)
      setSelRight(null)
    } else {
      setWrong({ l: leftId, r: rightId })
      setTimeout(() => {
        setWrong(null)
        setSelLeft(null)
        setSelRight(null)
      }, 600)
    }
  }, [cards.length])

  const handleLeft = (id: number) => {
    if (matched.has(id) || wrong) return
    const newSel = selLeft === id ? null : id
    setSelLeft(newSel)
    if (newSel !== null && selRight !== null) tryMatch(newSel, selRight)
  }

  const handleRight = (id: number) => {
    if (matched.has(id) || wrong) return
    const newSel = selRight === id ? null : id
    setSelRight(newSel)
    if (selLeft !== null && newSel !== null) tryMatch(selLeft, newSel)
  }

  const btnClass = (id: number, side: 'l' | 'r', sel: number | null) => {
    const base = [styles.matchOption]
    if (matched.has(id)) { base.push(styles.matchCorrect); return base.join(' ') }
    if (wrong && wrong[side] === id) { base.push(styles.matchWrong); return base.join(' ') }
    if (sel === id) base.push(styles.matchSelected)
    return base.join(' ')
  }

  return (
    <>
      <div className={styles.content}>
        <p className={styles.roundLabel}>Сопоставь слова</p>
        <div className={styles.matchingGrid}>
          <div className={styles.matchingCol}>
            {leftCol.map(card => (
              <button key={card.id} type="button"
                className={btnClass(card.id, 'l', selLeft)}
                onClick={() => handleLeft(card.id)}
                disabled={matched.has(card.id)}>
                {card.word_gr}
              </button>
            ))}
          </div>
          <div className={styles.matchingCol}>
            {rightCol.map(card => (
              <button key={card.id} type="button"
                className={btnClass(card.id, 'r', selRight)}
                onClick={() => handleRight(card.id)}
                disabled={matched.has(card.id)}>
                {card.word_ru}
              </button>
            ))}
          </div>
        </div>
      </div>
      <div className={styles.footer}>
        <Button variant="primary" fullWidth disabled={!done} onClick={onNext}>
          Дальше
        </Button>
      </div>
    </>
  )
}

// ──────────────────────────────────────────────
// Completion screen
// ──────────────────────────────────────────────

function CompletionScreen({ correct, total, onDone }: { correct: number; total: number; onDone: () => void }) {
  return (
    <>
      <div className={styles.complete}>
        <div className={styles.completeIcon}>🏆</div>
        <h1 className={styles.completeTitle}>Слова изучены!</h1>
        {total > 0 && (
          <p className={styles.completeScore}>Правильных ответов: {correct} из {total}</p>
        )}
      </div>
      <div className={styles.footer}>
        <Button variant="primary" fullWidth onClick={onDone}>Готово</Button>
      </div>
    </>
  )
}

// ──────────────────────────────────────────────
// Main screen
// ──────────────────────────────────────────────

export function WordLearningScreen() {
  const { unitId } = useParams<{ unitId: string }>()
  const navigate = useNavigate()
  const { data, isLoading } = useUnitDetailQuery(Number(unitId))

  const [started, setStarted] = useState(false)
  const [currentIndex, setCurrentIndex] = useState(0)
  const [correctCount, setCorrectCount] = useState(0)
  const [done, setDone] = useState(false)
  const sessionRef = useRef<SessionCard[]>([])
  // Preloaded audio for the upcoming flashcard
  const preloadedRef = useRef<HTMLAudioElement | null>(null)

  const vocabCards: VocabCard[] = data?.vocabulary_cards ?? []
  const session = useMemo(() => buildSession(vocabCards), [vocabCards])
  sessionRef.current = session

  const mcTotal = useMemo(
    () => session.filter(s => s.round === 'gr_to_ru' || s.round === 'ru_to_gr').length,
    [session],
  )

  const handleClose = () => navigate(`/units/${unitId}`)

  // Preload audio for the next flashcard in the background (no gesture needed for loading)
  useEffect(() => {
    const preloadFor = (card: VocabCard) => {
      if (!card.audio_path) return
      const audio = new Audio(`${API_URL}${card.audio_path}`)
      audio.preload = 'auto'
      preloadedRef.current = audio
    }
    // On the start screen preload card 0; otherwise preload card currentIndex+1
    if (!started && session.length > 0 && session[0].round === 'flashcard') {
      preloadFor(session[0].card)
    } else {
      const next = session[currentIndex + 1]
      if (next?.round === 'flashcard' || next?.round === 'gr_to_ru') preloadFor(next.card)
      else preloadedRef.current = null
    }
  }, [started, currentIndex, session])

  // Play already-preloaded audio (called inside click handler = user gesture)
  const playPreloaded = (card: VocabCard) => {
    const pre = preloadedRef.current
    if (pre && card.audio_path && pre.src.endsWith(card.audio_path.replace('/audio/', ''))) {
      pre.currentTime = 0
      pre.play().catch(() => {})
    } else {
      playCardAudio(card)
    }
  }

  // Called inside button onClick handlers → within user gesture window on iOS
  const advance = (correct?: boolean) => {
    if (correct !== undefined) setCorrectCount(c => c + (correct ? 1 : 0))
    const nextIndex = currentIndex + 1
    if (nextIndex >= sessionRef.current.length) {
      setDone(true)
    } else {
      const nextCard = sessionRef.current[nextIndex]
      if (nextCard.round === 'flashcard' || nextCard.round === 'gr_to_ru') {
        playPreloaded(nextCard.card)
      }
      setCurrentIndex(nextIndex)
    }
  }

  if (isLoading || !data) {
    return <div className={styles.shell}><p style={{ padding: '2rem', textAlign: 'center' }}>Загрузка...</p></div>
  }

  if (vocabCards.length === 0) {
    return (
      <div className={styles.shell}>
        <div className={styles.wordHeader}>
          <button className={styles.close} onClick={handleClose} aria-label="Выйти" type="button">✕</button>
        </div>
        <div className={styles.content}><p>Нет слов для изучения.</p></div>
      </div>
    )
  }

  const sessionCard = session[currentIndex]

  const handleStart = () => {
    if (session.length > 0 && session[0].round === 'flashcard') {
      playPreloaded(session[0].card)
    }
    setStarted(true)
  }

  if (!started) {
    return (
      <div className={styles.shell}>
        <div className={styles.wordHeader}>
          <button className={styles.close} onClick={handleClose} aria-label="Выйти" type="button">✕</button>
          <ProgressBar value={0} max={session.length} className={styles.progressBar} />
          <span className={styles.counter}>0 / {session.length}</span>
        </div>
        <div className={styles.content}>
          <p className={styles.roundLabel}>Учим слова</p>
          <p className={styles.word}>🎧</p>
          <p className={styles.translation}>{vocabCards.length} слов в юните</p>
        </div>
        <div className={styles.footer}>
          <Button variant="primary" fullWidth onClick={handleStart}>Начать</Button>
        </div>
      </div>
    )
  }

  return (
    <div className={styles.shell}>
      <div className={styles.wordHeader}>
        <button className={styles.close} onClick={handleClose} aria-label="Выйти" type="button">✕</button>
        <ProgressBar value={currentIndex + 1} max={session.length} className={styles.progressBar} />
        <span className={styles.counter}>{currentIndex + 1} / {session.length}</span>
      </div>

      {done ? (
        <CompletionScreen correct={correctCount} total={mcTotal} onDone={handleClose} />
      ) : sessionCard.round === 'flashcard' ? (
        <FlashcardSlide
          key={`fc-${sessionCard.card.id}-${currentIndex}`}
          card={sessionCard.card}
          onNext={() => advance()}
        />
      ) : sessionCard.round === 'matching' ? (
        <MatchingSlide
          key={`match-${currentIndex}`}
          cards={sessionCard.cards}
          onNext={() => advance()}
        />
      ) : (
        <McSlide
          key={`mc-${sessionCard.card.id}-${currentIndex}`}
          card={sessionCard.card}
          allCards={vocabCards}
          round={sessionCard.round}
          onNext={(correct) => advance(correct)}
        />
      )}
    </div>
  )
}
