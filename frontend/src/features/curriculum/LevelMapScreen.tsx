import type { Level } from '../../shared/api/types'
import { useLevelsQuery, useUnitsQuery } from './useCurriculumQuery'
import { LevelSection } from './components/LevelSection'
import styles from './LevelMapScreen.module.css'

const LEVELS: Level[] = ['A1', 'A2', 'B1']

function LevelBlock({ level }: { level: Level }) {
  const levelsQuery = useLevelsQuery()
  const unitsQuery = useUnitsQuery(level)

  const levelData = levelsQuery.data?.levels.find(l => l.level === level)
  const units = unitsQuery.data?.units ?? []

  if (!levelData || unitsQuery.isLoading) return null

  return <LevelSection level={levelData} units={units} />
}

export function LevelMapScreen() {
  return (
    <div className={styles.screen}>
      <div className={styles.header}>
        <h1 className={styles.title}>Мой прогресс</h1>
      </div>
      <div className={styles.content}>
        {LEVELS.map(level => (
          <LevelBlock key={level} level={level} />
        ))}
      </div>
    </div>
  )
}
