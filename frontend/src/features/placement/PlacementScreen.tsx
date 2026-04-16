import { useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import { useQuery, useMutation } from '@tanstack/react-query'
import { api } from '../../shared/api/endpoints'
import { usePlacementStore } from './usePlacementStore'
import { useAppStore } from '../../shared/store/useAppStore'
import { ProgressBar } from '../../shared/components/ProgressBar'
import { Button } from '../../shared/components/Button'
import { PlacementQuestion } from './components/PlacementQuestion'
import styles from './PlacementScreen.module.css'

export function PlacementScreen() {
  const navigate = useNavigate()
  const showTranslations = useAppStore((s) => s.showTranslations)
  const { setQuestions, submitAnswer, skip, questions, currentIndex, correctCount, isFinished } = usePlacementStore()

  const { data, isLoading } = useQuery({
    queryKey: ['placement-questions'],
    queryFn: () => api.getPlacementQuestions(),
  })

  const completeMutation = useMutation({
    mutationFn: ({ score, total, skipped }: { score: number; total: number; skipped: boolean }) =>
      api.completePlacementTest(score, total, skipped),
    onSuccess: () => navigate('/levels', { replace: true }),
  })

  useEffect(() => {
    if (data?.questions) setQuestions(data.questions)
  }, [data, setQuestions])

  useEffect(() => {
    if (isFinished && questions.length > 0) {
      completeMutation.mutate({ score: correctCount, total: questions.length, skipped: false })
    }
  }, [isFinished]) // eslint-disable-line react-hooks/exhaustive-deps

  const handleSkip = () => {
    skip()
    completeMutation.mutate({ score: 0, total: 1, skipped: true })
  }

  if (isLoading) {
    return (
      <div className={styles.screen}>
        <div className={styles.loading}>Загрузка...</div>
      </div>
    )
  }

  const currentQuestion = questions[currentIndex]

  return (
    <div className={styles.screen}>
      <div className={styles.header}>
        <ProgressBar value={currentIndex} max={questions.length} />
        <p className={styles.counter}>{currentIndex} / {questions.length}</p>
      </div>

      <div className={styles.content}>
        <h1 className={styles.title}>
          {showTranslations ? 'Тест на определение уровня (Τεστ κατάταξης)' : 'Τεστ κατάταξης'}
        </h1>
        <p className={styles.subtitle}>
          {showTranslations
            ? 'Απάντησε στις ερωτήσεις για να παρακάμψεις το A1 (Ответь на вопросы, чтобы пропустить A1)'
            : 'Απάντησε στις ερωτήσεις για να παρακάμψεις το A1'}
        </p>

        {currentQuestion && !isFinished && (
          <PlacementQuestion
            key={currentQuestion.id}
            question={currentQuestion}
            onAnswer={submitAnswer}
          />
        )}

        {isFinished && (
          <div className={styles.finishing}>
            <p>Подождите, сохраняем результат...</p>
          </div>
        )}
      </div>

      <div className={styles.footer}>
        <Button variant="ghost" onClick={handleSkip} disabled={completeMutation.isPending}>
          Пропустить тест
        </Button>
      </div>
    </div>
  )
}
