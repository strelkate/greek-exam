import { useState, useRef, useEffect } from 'react'
import { useNavigate, useParams } from 'react-router-dom'
import { useUnitDetailQuery } from '../curriculum/useCurriculumQuery'
import { useExerciseQuery } from './useExerciseQuery'
import { ExerciseShell } from './ExerciseShell'
import { TrueFalse } from './types/TrueFalse'
import { MultipleChoice } from './types/MultipleChoice'
import { Matching } from './types/Matching'
import { FillBlank } from './types/FillBlank'
import { ImageDescription } from './types/ImageDescription'
import { Dialogue } from './types/Dialogue'
import { useSyncQueue } from '../../shared/store/useSyncQueue'
import { useTelegram } from '../../shared/hooks/useTelegram'

const EXERCISE_INSTRUCTIONS: Record<string, string> = {
  true_false: 'Σωστό ή Λάθος;',
  multiple_choice: 'Επιλέξτε τη σωστή απάντηση.',
  matching: 'Αντιστοιχίστε τις λέξεις.',
  fill_blank: 'Συμπληρώστε το κενό.',
  image_description: 'Περιγράψτε την εικόνα.',
  dialogue: 'Συμπληρώστε τον διάλογο.',
}

export function ExerciseScreen() {
  const { unitId, exerciseId } = useParams<{ unitId: string; exerciseId: string }>()
  const navigate = useNavigate()
  const { enqueue } = useSyncQueue()
  const { haptic } = useTelegram()

  const unitQuery = useUnitDetailQuery(Number(unitId))
  const exerciseQuery = useExerciseQuery(Number(exerciseId))

  const [answered, setAnswered] = useState(false)
  const [isCorrect, setIsCorrect] = useState(false)
  const [showFeedback, setShowFeedback] = useState(false)
  const correctCountRef = useRef(0)

  const feedbackTimerRef = useRef<ReturnType<typeof setTimeout> | null>(null)

  useEffect(() => {
    setAnswered(false)
    setIsCorrect(false)
    setShowFeedback(false)
  }, [exerciseId])

  useEffect(() => {
    return () => {
      if (feedbackTimerRef.current) clearTimeout(feedbackTimerRef.current)
    }
  }, [])

  if (unitQuery.isLoading || exerciseQuery.isLoading) {
    return <div className="screen-loading">Загрузка...</div>
  }

  const exercises = unitQuery.data?.exercises ?? []
  const currentIdx = exercises.findIndex(e => e.id === Number(exerciseId))
  const exercise = exerciseQuery.data

  if (!exercise) return null

  const handleAnswer = (correct: boolean) => {
    setAnswered(true)
    setIsCorrect(correct)
    haptic.impact()
  }

  const handleSubmit = () => {
    if (!answered) return
    if (isCorrect) correctCountRef.current += 1
    enqueue({
      type: 'exercise_complete',
      exercise_id: Number(exerciseId),
      score: isCorrect ? 1 : 0,
      total: 1,
      occurred_at: new Date().toISOString(),
    })
    setShowFeedback(true)
    haptic.notification(isCorrect ? 'success' : 'error')
    feedbackTimerRef.current = setTimeout(() => {
      setShowFeedback(false)
      const nextExercise = exercises[currentIdx + 1]
      if (nextExercise) {
        navigate(`/units/${unitId}/exercise/${nextExercise.id}`)
      } else {
        navigate(`/units/${unitId}/result`, { state: { xp_earned: correctCountRef.current * 10 } })
      }
    }, 1500)
  }

  const instruction = EXERCISE_INSTRUCTIONS[exercise.type] ?? ''
  const content = exercise.content as Record<string, unknown>

  // No audio for matching exercises — they have multiple audio paths for individual items
  const audioPath = exercise.type === 'matching' ? null : (exercise.audio_paths[0] ?? null)

  return (
    <>
      <ExerciseShell
        current={currentIdx + 1}
        total={exercises.length}
        instruction={instruction}
        audioPath={audioPath}
        canSubmit={answered}
        submitted={answered}
        onSubmit={handleSubmit}
      >
        {exercise.type === 'true_false' && (
          <TrueFalse content={content as unknown as Parameters<typeof TrueFalse>[0]['content']} onAnswer={handleAnswer} />
        )}
        {exercise.type === 'multiple_choice' && (
          <MultipleChoice content={content as unknown as Parameters<typeof MultipleChoice>[0]['content']} onAnswer={handleAnswer} />
        )}
        {exercise.type === 'matching' && (
          <Matching content={content as unknown as Parameters<typeof Matching>[0]['content']} onAnswer={handleAnswer} />
        )}
        {exercise.type === 'fill_blank' && (
          <FillBlank content={content as unknown as Parameters<typeof FillBlank>[0]['content']} onAnswer={handleAnswer} />
        )}
        {exercise.type === 'image_description' && (
          <ImageDescription content={content as unknown as Parameters<typeof ImageDescription>[0]['content']} onAnswer={handleAnswer} />
        )}
        {exercise.type === 'dialogue' && (
          <Dialogue content={content as unknown as Parameters<typeof Dialogue>[0]['content']} onAnswer={handleAnswer} />
        )}
      </ExerciseShell>
      {showFeedback && (
        <div className={`feedback-overlay feedback-overlay--${isCorrect ? 'correct' : 'incorrect'}`}>
          <span className="feedback-overlay__icon">{isCorrect ? '✓' : '✗'}</span>
        </div>
      )}
    </>
  )
}
