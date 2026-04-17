import type { LevelProgress, UnitSummary } from '../../../shared/api/types'
import { UnitCard } from './UnitCard'
import styles from './LevelSection.module.css'

interface Props {
  level: LevelProgress
  units: UnitSummary[]
}

const LEVEL_LABELS: Record<string, string> = {
  A1: 'Начальный — A1',
  A2: 'Элементарный — A2',
  B1: 'Средний — B1',
}

export function LevelSection({ level, units }: Props) {
  const completedUnits = units.filter(u => u.unit_completed).length
  const totalExercises = units.reduce((sum, u) => sum + u.exercises_total, 0)
  const completedExercises = units.reduce((sum, u) => sum + u.exercises_completed, 0)
  const pct = totalExercises > 0 ? Math.round((completedExercises / totalExercises) * 100) : 0

  return (
    <section className={styles.section}>
      <div className={styles.headerLink}>
        <div className={styles.titleRow}>
          <h2 className={styles.title}>{LEVEL_LABELS[level.level] ?? level.level}</h2>
          <span className={styles.badge}>{pct}%</span>
        </div>
        <div className={styles.progressBar}>
          <div className={styles.progressFill} style={{ width: `${pct}%` }} />
        </div>
        <p className={styles.meta}>{completedUnits} из {level.total_units} юнитов</p>
      </div>
      {units.length > 0 && (
        <div className={styles.units}>
          {units.map(unit => (
            <UnitCard key={unit.id} unit={unit} />
          ))}
        </div>
      )}
    </section>
  )
}
