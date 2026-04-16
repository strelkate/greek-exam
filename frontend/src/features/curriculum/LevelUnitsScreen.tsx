import { useParams, Link } from 'react-router-dom'
import type { Level, LevelProgress } from '../../shared/api/types'
import { useLevelsQuery, useUnitsQuery } from './useCurriculumQuery'
import { UnitCard } from './components/UnitCard'
import styles from './LevelUnitsScreen.module.css'

const LEVEL_LABELS: Record<string, string> = {
  A1: 'Начальный — A1',
  A2: 'Элементарный — A2',
  B1: 'Средний — B1',
}

const UNIT_COUNTS: Record<string, number> = { A1: 6, A2: 9, B1: 8 }

function fallbackLevel(level: Level): LevelProgress {
  return { level, total_units: UNIT_COUNTS[level] ?? 0, completed_units: 0, progress_percent: 0 }
}

export function LevelUnitsScreen() {
  const { level } = useParams<{ level: string }>()
  const levelKey = level?.toUpperCase() as Level

  const levelsQuery = useLevelsQuery()
  const unitsQuery = useUnitsQuery(levelKey)

  const levelData = levelsQuery.data?.levels.find(l => l.level === levelKey)
    ?? (levelsQuery.isError ? fallbackLevel(levelKey) : null)
  const units = unitsQuery.data?.units ?? []

  const label = LEVEL_LABELS[levelKey] ?? levelKey

  return (
    <div className={styles.screen}>
      <div className={styles.header}>
        <Link to="/levels" className={styles.back}>← Назад</Link>
        <h1 className={styles.title}>{label}</h1>
        {levelData && (
          <div className={styles.meta}>
            <div className={styles.progressBar}>
              <div className={styles.progressFill} style={{ width: `${levelData.progress_percent}%` }} />
            </div>
            <span className={styles.metaText}>{levelData.completed_units} из {levelData.total_units} юнитов</span>
          </div>
        )}
      </div>

      <div className={styles.units}>
        {unitsQuery.isLoading && (
          <div className={styles.loading}>Загрузка...</div>
        )}
        {!unitsQuery.isLoading && units.length === 0 && (
          <div className={styles.empty}>Юниты недоступны</div>
        )}
        {units.map(unit => (
          <UnitCard key={unit.id} unit={unit} size="large" />
        ))}
      </div>
    </div>
  )
}
