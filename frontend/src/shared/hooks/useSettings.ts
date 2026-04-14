// frontend/src/shared/hooks/useSettings.ts
import { useAppStore } from '../store/useAppStore'

export function useSettings() {
  const showTranslations = useAppStore((s) => s.showTranslations)
  const setShowTranslations = useAppStore((s) => s.setShowTranslations)

  return { showTranslations, setShowTranslations }
}
