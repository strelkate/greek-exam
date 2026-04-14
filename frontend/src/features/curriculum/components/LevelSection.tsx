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
  return (
    <section className={styles.section}>
      <div className={styles.header}>
        <div className={styles.titleRow}>
          <h2 className={styles.title}>{LEVEL_LABELS[level.level] ?? level.level}</h2>
          <span className={styles.badge}>{level.progress_percent}%</span>
        </div>
        <div className={styles.progressBar}>
          <div className={styles.progressFill} style={{ width: `${level.progress_percent}%` }} />
        </div>
        <p className={styles.meta}>{level.completed_units} из {level.total_units} юнитов</p>
      </div>
      <div className={styles.units}>
        {units.map(unit => (
          <UnitCard key={unit.id} unit={unit} />
        ))}
      </div>
    </section>
  )
}
