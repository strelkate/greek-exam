import { ReactNode } from 'react'
import { AudioPlayer } from '../../shared/components/AudioPlayer'
import { Button } from '../../shared/components/Button'
import { ProgressBar } from '../../shared/components/ProgressBar'

interface ExerciseShellProps {
  current: number
  total: number
  instruction: string
  audioPath: string | null
  canSubmit: boolean
  submitted?: boolean
  onSubmit: () => void
  children: ReactNode
}

export function ExerciseShell({
  current, total, instruction, audioPath, canSubmit, submitted = false, onSubmit, children,
}: ExerciseShellProps) {
  return (
    <div className="exercise-shell">
      <div className="exercise-shell__header">
        <ProgressBar value={current} max={total} />
        <span className="exercise-shell__counter">{current} / {total}</span>
      </div>
      {audioPath && (
        <div className="exercise-shell__audio">
          <AudioPlayer src={audioPath} ariaLabel="аудио" />
        </div>
      )}
      <p className="exercise-shell__instruction">{instruction}</p>
      <div className="exercise-shell__content">{children}</div>
      <div className="exercise-shell__footer">
        <Button onClick={onSubmit} disabled={!canSubmit} variant="primary" fullWidth>
          {submitted ? 'Далее' : 'Проверить'}
        </Button>
      </div>
    </div>
  )
}
