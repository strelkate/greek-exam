import type { Level, LevelProgress } from '../../shared/api/types'
import { useLevelsQuery, useUnitsQuery } from './useCurriculumQuery'
import { LevelSection } from './components/LevelSection'
import styles from './LevelMapScreen.module.css'

const LEVELS: Level[] = ['A1', 'A2', 'B1']

const LEVEL_LABELS: Record<Level, string> = {
  A1: 'Начальный — A1',
  A2: 'Элементарный — A2',
  B1: 'Средний — B1',
}

const UNIT_COUNTS: Record<Level, number> = { A1: 6, A2: 9, B1: 8 }

function fallbackLevel(level: Level): LevelProgress {
  return { level, total_units: UNIT_COUNTS[level], completed_units: 0, progress_percent: 0 }
}

function LevelBlock({ level }: { level: Level }) {
  const levelsQuery = useLevelsQuery()
  const unitsQuery = useUnitsQuery(level)

  const levelData = levelsQuery.data?.levels.find(l => l.level === level) ?? (levelsQuery.isError ? fallbackLevel(level) : null)
  const units = unitsQuery.data?.units ?? []

  // Show skeleton while loading
  if (levelsQuery.isLoading || unitsQuery.isLoading) {
    return (
      <section className={styles.levelSkeleton}>
        <div className={styles.skeletonTitle}>{LEVEL_LABELS[level]}</div>
        <div className={styles.skeletonUnits}>
          {[1, 2, 3].map(i => <div key={i} className={styles.skeletonCard} />)}
        </div>
      </section>
    )
  }

  if (!levelData) return null

  return <LevelSection level={levelData} units={units} />
}

export function LevelMapScreen() {
  return (
    <div className={styles.levelMap}>
      <div className={styles.levelHeader}>
        <h1 className={styles.levelTitle}>Мой прогресс</h1>
      </div>
      <div className={styles.levelContent}>
        {LEVELS.map(level => (
          <LevelBlock key={level} level={level} />
        ))}
      </div>
    </div>
  )
}
