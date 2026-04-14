// frontend/src/shared/store/useExerciseStore.ts
import { create } from 'zustand'

interface Answer {
  exerciseId: number
  isCorrect: boolean
}

interface ExerciseSessionState {
  unitId: number | null
  exerciseIds: number[]
  currentIndex: number
  answers: Answer[]
  isComplete: boolean

  startSession: (unitId: number, exerciseIds: number[]) => void
  submitAnswer: (exerciseId: number, isCorrect: boolean) => void
  nextExercise: () => void
  resetSession: () => void
}

export const useExerciseStore = create<ExerciseSessionState>()((set) => ({
  unitId: null,
  exerciseIds: [],
  currentIndex: 0,
  answers: [],
  isComplete: false,

  startSession: (unitId, exerciseIds) =>
    set({ unitId, exerciseIds, currentIndex: 0, answers: [], isComplete: false }),

  submitAnswer: (exerciseId, isCorrect) =>
    set((s) => ({ answers: [...s.answers, { exerciseId, isCorrect }] })),

  nextExercise: () =>
    set((s) => {
      const next = s.currentIndex + 1
      return next >= s.exerciseIds.length
        ? { isComplete: true }
        : { currentIndex: next }
    }),

  resetSession: () =>
    set({ unitId: null, exerciseIds: [], currentIndex: 0, answers: [], isComplete: false }),
}))
