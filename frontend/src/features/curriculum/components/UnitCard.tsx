import { Link } from 'react-router-dom'
import type { UnitSummary } from '../../../shared/api/types'
import styles from './UnitCard.module.css'

interface Props {
  unit: UnitSummary
  size?: 'compact' | 'large'
}

export function UnitCard({ unit, size = 'compact' }: Props) {
  const pct = unit.exercises_total > 0
    ? Math.round((unit.exercises_completed / unit.exercises_total) * 100)
    : 0

  return (
    <Link to={`/units/${unit.id}`} className={`${styles.card} ${size === 'large' ? styles.cardLarge : ''}`}>
      <div className={styles.top}>
        <span className={styles.unitTitle}>{unit.title}</span>
        {unit.unit_completed && (
          <span className={styles.check} aria-label="завершён">✓</span>
        )}
      </div>
      <div className={styles.progress}>
        <div className={styles.bar}>
          <div className={styles.fill} style={{ width: `${pct}%` }} />
        </div>
        <span className={styles.counter}>{unit.exercises_completed} / {unit.exercises_total}</span>
      </div>
    </Link>
  )
}
