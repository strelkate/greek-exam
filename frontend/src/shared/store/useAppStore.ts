// frontend/src/shared/store/useAppStore.ts
import { create } from 'zustand'
import { persist } from 'zustand/middleware'

interface AppState {
  xp: number
  streak: number
  streakDate: string | null
  showTranslations: boolean
  addXp: (amount: number) => void
  setStreak: (days: number, date: string) => void
  setShowTranslations: (value: boolean) => void
  hydrate: (data: { xp: number; streak: number; showTranslations: boolean }) => void
}

export const useAppStore = create<AppState>()(
  persist(
    (set) => ({
      xp: 0,
      streak: 0,
      streakDate: null,
      showTranslations: true,

      addXp: (amount) => set((s) => ({ xp: s.xp + amount })),

      setStreak: (days, date) => set({ streak: days, streakDate: date }),

      setShowTranslations: (value) => set({ showTranslations: value }),

      hydrate: (data) =>
        set({ xp: data.xp, streak: data.streak, showTranslations: data.showTranslations }),
    }),
    { name: 'greek-app-store' }
  )
)
