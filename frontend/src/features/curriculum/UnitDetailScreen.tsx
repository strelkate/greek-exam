import { useState, useRef, useCallback } from 'react'
import { useNavigate, useParams, Link } from 'react-router-dom'
import { useUnitDetailQuery } from './useCurriculumQuery'
import { useExerciseStore } from '../../shared/store/useExerciseStore'
import { useAppStore } from '../../shared/store/useAppStore'
import { Button } from '../../shared/components/Button'
import { ProgressBar } from '../../shared/components/ProgressBar'
import type { ExerciseType } from '../../shared/api/types'
import styles from './UnitDetailScreen.module.css'

const API_URL = import.meta.env.VITE_API_URL ?? ''

const EXERCISE_TYPE_GR: Record<ExerciseType, string> = {
  true_false: 'Σωστό ή Λάθος',
  matching: 'Αντιστοίχιση',
  multiple_choice: 'Πολλαπλή επιλογή',
  fill_blank: 'Συμπλήρωση κενού',
  image_description: 'Περιγραφή εικόνας',
  dialogue: 'Διάλογος',
}

const EXERCISE_TYPE_RU: Record<ExerciseType, string> = {
  true_false: 'Верно / Неверно',
  matching: 'Сопоставление',
  multiple_choice: 'Выбор ответа',
  fill_blank: 'Заполни пропуск',
  image_description: 'Описание картинки',
  dialogue: 'Диалог',
}

export function UnitDetailScreen() {
  const { unitId } = useParams<{ unitId: string }>()
  const navigate = useNavigate()
  const { data, isLoading } = useUnitDetailQuery(Number(unitId))
  const startSession = useExerciseStore((s) => s.startSession)
  const showTranslations = useAppStore((s) => s.showTranslations)
  const [vocabExpanded, setVocabExpanded] = useState(false)
  const currentAudioRef = useRef<HTMLAudioElement | null>(null)

  const playWord = useCallback((word_gr: string, audio_path: string | null) => {
    if (currentAudioRef.current) {
      currentAudioRef.current.pause()
      currentAudioRef.current = null
    }
    if (audio_path) {
      const audio = new Audio(`${API_URL}${audio_path}`)
      currentAudioRef.current = audio
      audio.play().catch(() => {})
    } else {
      window.speechSynthesis.cancel()
      const utt = new SpeechSynthesisUtterance(word_gr)
      utt.lang = 'el-GR'
      window.speechSynthesis.speak(utt)
    }
  }, [])

  if (isLoading || !data) {
    return <div className={styles.loading}>Загрузка...</div>
  }
  const exercises = data.exercises
  const completedCount = exercises.filter(e => e.completed).length
  const allDone = completedCount >= exercises.length && exercises.length > 0
  const firstIncomplete = exercises.find(e => !e.completed)

  const handleStart = () => {
    const ids = exercises.map(e => e.id)
    startSession(Number(unitId), ids)
    const startId = firstIncomplete?.id ?? exercises[0].id
    navigate(`/units/${unitId}/exercise/${startId}`)
  }

  return (
    <div className={styles.screen}>
      <div className={styles.header}>
        <div className={styles.breadcrumb}>
          <Link to={`/levels/${data.level.toLowerCase()}`} className={styles.breadcrumbBack}>←</Link>
          <Link to="/levels" className={styles.breadcrumbLink}>Уровни</Link>
          <span className={styles.breadcrumbSep}>/</span>
          <Link to={`/levels/${data.level.toLowerCase()}`} className={styles.breadcrumbLink}>{data.level}</Link>
        </div>
        <h1 className={styles.title}>{data.title}</h1>
        <ProgressBar value={completedCount} max={exercises.length} />
        <p className={styles.progress}>{completedCount} из {exercises.length} упражнений</p>
      </div>

      <div className={styles.content}>
        <section>
          <h2 className={styles.sectionTitle}>Упражнения</h2>
          <div className={styles.exerciseList}>
            {exercises.map((ex, i) => (
              <Link
                key={ex.id}
                to={`/units/${unitId}/exercise/${ex.id}`}
                className={styles.exerciseRow}
              >
                <span className={styles.exNumber}>{i + 1}</span>
                <span className={styles.exType}>
                  {EXERCISE_TYPE_GR[ex.type]}
                  {showTranslations && <span className={styles.exTypeRu}> ({EXERCISE_TYPE_RU[ex.type]})</span>}
                </span>
                {ex.completed && <span className={styles.exCheck} aria-label="выполнено">✓</span>}
              </Link>
            ))}
          </div>
        </section>

        {allDone && (
          <Button fullWidth onClick={() => navigate(`/units/${unitId}/mini-test`)}>
            Пройти мини-тест
          </Button>
        )}

        {data.vocabulary_cards.length > 0 && (
          <section>
            <h2 className={styles.sectionTitle}>Словарь юнита</h2>
            <div className={styles.vocabList}>
              {(vocabExpanded ? data.vocabulary_cards : data.vocabulary_cards.slice(0, 5)).map(card => (
                <div
                  key={card.id}
                  className={styles.vocabRow}
                  onClick={() => playWord(card.word_gr, card.audio_path)}
                  role="button"
                  tabIndex={0}
                >
                  <span className={styles.wordGr}>{card.word_gr}</span>
                  <span className={styles.wordRu}>{card.word_ru}</span>
                </div>
              ))}
              {data.vocabulary_cards.length > 5 && (
                <button
                  className={styles.vocabToggle}
                  onClick={() => setVocabExpanded(!vocabExpanded)}
                >
                  {vocabExpanded ? 'Свернуть' : `и ещё ${data.vocabulary_cards.length - 5} слов`}
                </button>
              )}
            </div>
          </section>
        )}
      </div>

      <div className={styles.footer}>
        <Button fullWidth onClick={handleStart}>
          {completedCount === 0 ? 'Начать' : allDone ? 'Повторить' : 'Продолжить'}
        </Button>
      </div>
    </div>
  )
}
