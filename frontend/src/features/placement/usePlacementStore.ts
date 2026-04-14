import { create } from 'zustand'
import type { PlacementQuestion } from '../../shared/api/types'

interface PlacementState {
  questions: PlacementQuestion[]
  currentIndex: number
  correctCount: number
  isFinished: boolean
  setQuestions: (questions: PlacementQuestion[]) => void
  submitAnswer: (isCorrect: boolean) => void
  skip: () => void
  reset: () => void
}

export const usePlacementStore = create<PlacementState>()((set, get) => ({
  questions: [],
  currentIndex: 0,
  correctCount: 0,
  isFinished: false,
  setQuestions: (questions) => set({ questions, currentIndex: 0, correctCount: 0, isFinished: false }),
  submitAnswer: (isCorrect) => {
    const { currentIndex, questions, correctCount } = get()
    const next = currentIndex + 1
    set({
      correctCount: isCorrect ? correctCount + 1 : correctCount,
      currentIndex: next,
      isFinished: next >= questions.length,
    })
  },
  skip: () => set({ isFinished: true }),
  reset: () => set({ questions: [], currentIndex: 0, correctCount: 0, isFinished: false }),
}))
