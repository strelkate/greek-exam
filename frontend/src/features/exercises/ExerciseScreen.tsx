import { useState, useRef, useEffect } from 'react'
import { useNavigate, useParams } from 'react-router-dom'
import { useQueryClient } from '@tanstack/react-query'
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
import { useAppStore } from '../../shared/store/useAppStore'

const EXERCISE_INSTRUCTIONS: Record<string, string> = {
  true_false: 'Σωστό ή Λάθος;',
  multiple_choice: 'Επιλέξτε τη σωστή απάντηση.',
  matching: 'Αντιστοιχίστε τις λέξεις.',
  fill_blank: 'Συμπληρώστε το κενό.',
  image_description: 'Περιγράψτε την εικόνα.',
  dialogue: 'Συμπληρώστε τον διάλογο.',
}

const EXERCISE_INSTRUCTIONS_RU: Record<string, string> = {
  true_false: 'Верно или нет?',
  multiple_choice: 'Выберите правильный ответ.',
  matching: 'Сопоставьте слова.',
  fill_blank: 'Заполните пропуск.',
  image_description: 'Опишите изображение.',
  dialogue: 'Заполните диалог.',
}

export function ExerciseScreen() {
  const { unitId, exerciseId } = useParams<{ unitId: string; exerciseId: string }>()
  const navigate = useNavigate()
  const queryClient = useQueryClient()
  const { enqueue } = useSyncQueue()
  const { haptic } = useTelegram()
  const showTranslations = useAppStore((s) => s.showTranslations)

  const unitQuery = useUnitDetailQuery(Number(unitId))
  const exerciseQuery = useExerciseQuery(Number(exerciseId))

  const [answered, setAnswered] = useState(false)
  const [confirmed, setConfirmed] = useState(false)
  const [isCorrect, setIsCorrect] = useState(false)
  const [showFeedback, setShowFeedback] = useState(false)
  const correctCountRef = useRef(0)

  const feedbackTimerRef = useRef<ReturnType<typeof setTimeout> | null>(null)

  useEffect(() => {
    setAnswered(false)
    setConfirmed(false)
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
  const currentIdx = exercises.findIndex((e) => e.id === Number(exerciseId))
  const exercise = exerciseQuery.data

  if (!exercise) return null

  const handleAnswer = (correct: boolean) => {
    setAnswered(true)
    setIsCorrect(correct)
    haptic.impact()
  }

  const handleSubmit = () => {
    if (!answered) return
    // First press: confirm the answer and show feedback colors
    if (!confirmed) {
      setConfirmed(true)
      haptic.notification(isCorrect ? 'success' : 'error')
      return
    }
    // Second press: advance to next exercise
    if (isCorrect) correctCountRef.current += 1
    enqueue({
      type: 'exercise_complete',
      exercise_id: Number(exerciseId),
      score: isCorrect ? 1 : 0,
      total: 1,
      occurred_at: new Date().toISOString(),
    })
    setShowFeedback(true)
    const nextExercise = exercises[currentIdx + 1]
    feedbackTimerRef.current = setTimeout(() => {
      setShowFeedback(false)
      if (nextExercise) {
        navigate(`/units/${unitId}/exercise/${nextExercise.id}`)
      } else {
        queryClient.invalidateQueries({ queryKey: ['levels'] })
        queryClient.invalidateQueries({ queryKey: ['units'] })
        queryClient.invalidateQueries({ queryKey: ['unit', Number(unitId)] })
        navigate(`/units/${unitId}/result`, { state: { xp_earned: correctCountRef.current * 10 } })
      }
    }, 400)
  }

  const grInstruction = EXERCISE_INSTRUCTIONS[exercise.type] ?? ''
  const ruInstruction = EXERCISE_INSTRUCTIONS_RU[exercise.type] ?? ''
  const instruction = showTranslations ? `${grInstruction} (${ruInstruction})` : grInstruction
  const content = exercise.content as Record<string, unknown>

  // Use audio files for all types where available; matching handles audio internally
  const audioPath = exercise.type === 'matching' ? null : (exercise.audio_paths[0] ?? null)
  const audioPaths =
    exercise.type === 'dialogue' && exercise.audio_paths.length > 0
      ? exercise.audio_paths
      : undefined
  const ttsText = null

  return (
    <>
      <ExerciseShell
        current={currentIdx + 1}
        total={exercises.length}
        instruction={instruction}
        audioPath={audioPath}
        audioPaths={audioPaths}
        ttsText={ttsText}
        canSubmit={answered}
        submitted={confirmed}
        onSubmit={handleSubmit}
        onClose={() => navigate(`/units/${unitId}`)}
      >
        {exercise.type === 'true_false' && (
          <TrueFalse
            content={content as unknown as Parameters<typeof TrueFalse>[0]['content']}
            onAnswer={handleAnswer}
            submitted={confirmed}
          />
        )}
        {exercise.type === 'multiple_choice' && (
          <MultipleChoice
            content={content as unknown as Parameters<typeof MultipleChoice>[0]['content']}
            onAnswer={handleAnswer}
            submitted={confirmed}
          />
        )}
        {exercise.type === 'matching' && (
          <Matching
            content={content as unknown as Parameters<typeof Matching>[0]['content']}
            audioPaths={exercise.audio_paths}
            onAnswer={handleAnswer}
          />
        )}
        {exercise.type === 'fill_blank' && (
          <FillBlank
            content={content as unknown as Parameters<typeof FillBlank>[0]['content']}
            onAnswer={handleAnswer}
            submitted={confirmed}
          />
        )}
        {exercise.type === 'image_description' && (
          <ImageDescription
            content={content as unknown as Parameters<typeof ImageDescription>[0]['content']}
            onAnswer={handleAnswer}
            submitted={confirmed}
          />
        )}
        {exercise.type === 'dialogue' && (
          <Dialogue
            content={content as unknown as Parameters<typeof Dialogue>[0]['content']}
            onAnswer={handleAnswer}
            submitted={confirmed}
          />
        )}
      </ExerciseShell>
      {showFeedback && (
        <div
          className={`feedback-overlay feedback-overlay--${isCorrect ? 'correct' : 'incorrect'}`}
        >
          <span className="feedback-overlay__icon">{isCorrect ? '✓' : '✗'}</span>
        </div>
      )}
    </>
  )
}
