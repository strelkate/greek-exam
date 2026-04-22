import { useEffect } from 'react'
import { Navigate, Route, Routes, useNavigate } from 'react-router-dom'
import { api } from './shared/api/endpoints'
import { setInitData } from './shared/api/client'
import { useAppStore } from './shared/store/useAppStore'
import { useTelegram } from './shared/hooks/useTelegram'
import { BottomNav } from './shared/components/BottomNav'
import { LevelMapScreen } from './features/curriculum/LevelMapScreen'
import { ExerciseScreen } from './features/exercises/ExerciseScreen'
import { VocabularyHomeScreen } from './features/vocabulary/VocabularyHomeScreen'
import { FlashcardScreen } from './features/vocabulary/FlashcardScreen'
import { UnitDetailScreen } from './features/curriculum/UnitDetailScreen'
import { MiniTestScreen } from './features/exercises/MiniTestScreen'
import { UnitResultScreen } from './features/exercises/UnitResultScreen'
import { WordLearningScreen } from './features/vocabulary/WordLearningScreen'
import { LandingScreen } from './features/landing/LandingScreen'

function AppRoutes() {
  return (
    <>
      <Routes>
        <Route path="/" element={<Navigate to="/levels" replace />} />
        <Route path="/levels" element={<LevelMapScreen />} />
        <Route path="/units/:unitId" element={<UnitDetailScreen />} />
        <Route path="/units/:unitId/exercise/:exerciseId" element={<ExerciseScreen />} />
        <Route path="/units/:unitId/words" element={<WordLearningScreen />} />
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

  // When opened outside Telegram in production, initData is empty —
  // show a landing page instead of attempting to auth.
  const showLanding = !initData

  useEffect(() => {
    if (showLanding) return
    ready()
    expand()
    setInitData(initData)

    api
      .createSession()
      .then((session) => {
        hydrate({
          xp: session.total_xp,
          streak: session.streak_days,
          showTranslations: session.show_instruction_translation,
        })
        navigate('/levels', { replace: true })
      })
      .catch(() => {
        // Backend unavailable (e.g. no auth in local dev) — stay on /levels
      })
  }, []) // eslint-disable-line react-hooks/exhaustive-deps

  if (showLanding) return <LandingScreen />

  return <AppRoutes />
}
