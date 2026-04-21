import styles from './ProgressBar.module.css'

interface ProgressBarProps {
  value: number
  max: number
  className?: string
}

export function ProgressBar({ value, max, className }: ProgressBarProps) {
  const pct = Math.min(100, Math.max(0, (value / max) * 100))
  return (
    <div className={[styles.track, className].filter(Boolean).join(' ')}>
      <div className={styles.fill} data-fill style={{ width: `${pct}%` }} />
    </div>
  )
}
