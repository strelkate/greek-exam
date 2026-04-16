import { useState, useRef, useEffect } from 'react'
import { useNavigate, useParams } from 'react-router-dom'
import { useMiniTestQuery } from './useMiniTestQuery'
import { ExerciseShell } from './ExerciseShell'
import { TrueFalse } from './types/TrueFalse'
import { MultipleChoice } from './types/MultipleChoice'
import { FillBlank } from './types/FillBlank'
import { api } from '../../shared/api/endpoints'
import { useAppStore } from '../../shared/store/useAppStore'
import { useTelegram } from '../../shared/hooks/useTelegram'

const INSTRUCTIONS: Record<string, string> = {
  true_false: 'Σωστό ή Λάθος;',
  multiple_choice: 'Επιλέξτε τη σωστή απάντηση.',
  fill_blank: 'Συμπληρώστε το κενό.',
}

export function MiniTestScreen() {
  const { unitId } = useParams<{ unitId: string }>()
  const navigate = useNavigate()
  const { haptic } = useTelegram()
  const addXp = useAppStore(s => s.addXp)

  const miniTestQuery = useMiniTestQuery(Number(unitId))

  const [currentIndex, setCurrentIndex] = useState(0)
  const [score, setScore] = useState(0)
  const [answered, setAnswered] = useState(false)
  const [submitting, setSubmitting] = useState(false)

  const advanceTimerRef = useRef<ReturnType<typeof setTimeout> | null>(null)

  useEffect(() => {
    return () => {
      if (advanceTimerRef.current) clearTimeout(advanceTimerRef.current)
    }
  }, [])

  if (miniTestQuery.isLoading) return <div className="screen-loading">Загрузка...</div>

  if (miniTestQuery.isError) {
    return (
      <div className="screen-loading" style={{ flexDirection: 'column', gap: 16, textAlign: 'center', padding: 24 }}>
        <p>Сначала выполните все упражнения юнита</p>
        <button
          onClick={() => navigate(`/units/${unitId}`)}
          style={{
            padding: '14px 24px', border: 'none', borderRadius: 8,
            background: 'linear-gradient(135deg, var(--color-primary), var(--color-primary-dark))',
            color: '#0b0d1a', fontFamily: 'var(--font-family)', fontSize: '0.875rem', fontWeight: 700,
            cursor: 'pointer',
          }}
        >
          Вернуться к юниту
        </button>
      </div>
    )
  }

  const questions = miniTestQuery.data?.questions ?? []
  const question = questions[currentIndex]
  if (!question) return null

  const total = questions.length

  const handleAnswer = (isCorrect: boolean) => {
    setAnswered(true)
    if (isCorrect) setScore(s => s + 1)
    haptic.impact()
  }

  const handleSubmit = async () => {
    if (submitting) return
    haptic.notification(answered ? 'success' : 'error')
    if (currentIndex < total - 1) {
      advanceTimerRef.current = setTimeout(() => {
        setCurrentIndex(i => i + 1)
        setAnswered(false)
      }, 1000)
      return
    }
    setSubmitting(true)
    try {
      const result = await api.completeMiniTest(Number(unitId), score, total)
      if (result.xp_earned > 0) addXp(result.xp_earned)
      navigate(`/units/${unitId}/result`, { state: result })
    } finally {
      setSubmitting(false)
    }
  }

  return (
    <ExerciseShell
      current={currentIndex + 1}
      total={total}
      instruction={INSTRUCTIONS[question.type] ?? ''}
      audioPath={null}
      canSubmit={answered}
      submitted={answered}
      onSubmit={handleSubmit}
    >
      {question.type === 'true_false' && (
        <TrueFalse content={question.content as unknown as Parameters<typeof TrueFalse>[0]['content']} onAnswer={handleAnswer} />
      )}
      {question.type === 'multiple_choice' && (
        <MultipleChoice content={question.content as unknown as Parameters<typeof MultipleChoice>[0]['content']} onAnswer={handleAnswer} />
      )}
      {question.type === 'fill_blank' && (
        <FillBlank content={question.content as unknown as Parameters<typeof FillBlank>[0]['content']} onAnswer={handleAnswer} />
      )}
    </ExerciseShell>
  )
}
