import { ReactNode } from 'react'
import { AudioPlayer, SequentialAudioPlayer } from '../../shared/components/AudioPlayer'
import { Button } from '../../shared/components/Button'
import { ProgressBar } from '../../shared/components/ProgressBar'
import { TtsButton } from '../../shared/components/TtsButton'

interface ExerciseShellProps {
  current: number
  total: number
  instruction: string
  audioPath: string | null
  audioPaths?: string[]
  ttsText?: string | null
  canSubmit: boolean
  submitted?: boolean
  onSubmit: () => void
  onClose: () => void
  children: ReactNode
}

export function ExerciseShell({
  current, total, instruction, audioPath, audioPaths, ttsText, canSubmit, submitted = false, onSubmit, onClose, children,
}: ExerciseShellProps) {
  return (
    <div className="exercise-shell">
      <div className="exercise-shell__header">
        <button className="exercise-shell__close" onClick={onClose} aria-label="Выйти">✕</button>
        <ProgressBar value={current} max={total} />
        <span className="exercise-shell__counter">{current} / {total}</span>
      </div>
      {ttsText ? (
        <div className="exercise-shell__audio">
          <TtsButton text={ttsText} />
        </div>
      ) : audioPaths && audioPaths.length > 0 ? (
        <div className="exercise-shell__audio">
          <SequentialAudioPlayer srcs={audioPaths} ariaLabel="аудио" />
        </div>
      ) : audioPath ? (
        <div className="exercise-shell__audio">
          <AudioPlayer src={audioPath} ariaLabel="аудио" />
        </div>
      ) : null}
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
