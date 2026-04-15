import { useEffect } from 'react'
import { Navigate, Route, Routes, useNavigate } from 'react-router-dom'
import { api } from './shared/api/endpoints'
import { setInitData } from './shared/api/client'
import { useAppStore } from './shared/store/useAppStore'
import { useTelegram } from './shared/hooks/useTelegram'
import { BottomNav } from './shared/components/BottomNav'
import { LevelMapScreen } from './features/curriculum/LevelMapScreen'
import { PlacementScreen } from './features/placement/PlacementScreen'
import { ExerciseScreen } from './features/exercises/ExerciseScreen'
import { VocabularyHomeScreen } from './features/vocabulary/VocabularyHomeScreen'
import { FlashcardScreen } from './features/vocabulary/FlashcardScreen'
import { UnitDetailScreen } from './features/curriculum/UnitDetailScreen'
import { MiniTestScreen } from './features/exercises/MiniTestScreen'
import { UnitResultScreen } from './features/exercises/UnitResultScreen'

function AppRoutes() {
  return (
    <>
      <Routes>
        <Route path="/" element={<Navigate to="/levels" replace />} />
        <Route path="/placement" element={<PlacementScreen />} />
        <Route path="/levels" element={<LevelMapScreen />} />
        <Route path="/units/:unitId" element={<UnitDetailScreen />} />
        <Route path="/units/:unitId/exercise/:exerciseId" element={<ExerciseScreen />} />
        <Route path="/units/:unitId/mini-test" element={<MiniTestScreen />} />
        <Route path="/units/:unitId/result" element={<UnitResultScreen />} />
        <Route path="/vocabulary" element={<VocabularyHomeScreen />} />
        <Route path="/vocabulary/review" element={<FlashcardScreen />} />
        <Route path="*" element={<Navigate to="/levels" replace />} />
      </Routes>
      <BottomNav />
    </>
  )
}

export function App() {
  const { initData, ready, expand } = useTelegram()
  const hydrate = useAppStore((s) => s.hydrate)
  const navigate = useNavigate()

  useEffect(() => {
    ready()
    expand()
    setInitData(initData)

    api.createSession().then((session) => {
      hydrate({
        xp: session.total_xp,
        streak: session.streak_days,
        showTranslations: session.show_instruction_translation,
      })
      if (session.placement_status === 'pending') {
        navigate('/placement', { replace: true })
      } else {
        navigate('/levels', { replace: true })
      }
    })
  }, []) // eslint-disable-line react-hooks/exhaustive-deps

  return <AppRoutes />
}
