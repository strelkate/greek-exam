import { useState } from 'react'
import { useNavigate, useParams, Link } from 'react-router-dom'
import { useUnitDetailQuery } from './useCurriculumQuery'
import { useExerciseStore } from '../../shared/store/useExerciseStore'
import { Button } from '../../shared/components/Button'
import { ProgressBar } from '../../shared/components/ProgressBar'
import type { ExerciseType } from '../../shared/api/types'
import styles from './UnitDetailScreen.module.css'

const EXERCISE_TYPE_LABELS: Record<ExerciseType, string> = {
  true_false: 'ΣΩΣΤΟ / ΛΑΘΟΣ',
  matching: 'Сопоставление',
  multiple_choice: 'Выбор ответа',
  fill_blank: 'Заполни пропуск',
  image_description: 'Περιγραφή εικόνας',
  dialogue: 'Διάλογος',
}

export function UnitDetailScreen() {
  const { unitId } = useParams<{ unitId: string }>()
  const navigate = useNavigate()
  const { data, isLoading } = useUnitDetailQuery(Number(unitId))
  const startSession = useExerciseStore((s) => s.startSession)
  const [vocabExpanded, setVocabExpanded] = useState(false)

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
                <span className={styles.exType}>{EXERCISE_TYPE_LABELS[ex.type]}</span>
                {ex.completed && <span className={styles.exCheck} aria-label="выполнено">✓</span>}
              </Link>
            ))}
          </div>
        </section>

        {data.vocabulary_cards.length > 0 && (
          <section>
            <h2 className={styles.sectionTitle}>Словарь юнита</h2>
            <div className={styles.vocabList}>
              {(vocabExpanded ? data.vocabulary_cards : data.vocabulary_cards.slice(0, 5)).map(card => (
                <div key={card.id} className={styles.vocabRow}>
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
        {allDone && (
          <Button
            fullWidth
            variant="secondary"
            onClick={() => navigate(`/units/${unitId}/mini-test`)}
          >
            Мини-тест
          </Button>
        )}
      </div>
    </div>
  )
}
