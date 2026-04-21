// frontend/src/shared/api/endpoints.ts
import { apiClient } from './client'
import type {
  SessionResponse,
  LevelsResponse,
  UnitsResponse,
  UnitDetailResponse,
  ExerciseResponse,
  CompleteExerciseResponse,
  MiniTestQuestionsResponse,
  MiniTestCompleteResponse,
  DueCardsResponse,
  ReviewResponse,
  VocabStatsResponse,
  SettingsResponse,
  SyncResponse,
  ProgressEvent,
} from './types'

export const api = {
  // Auth
  createSession: () => apiClient.post<SessionResponse>('/api/v1/auth/session').then((r) => r.data),

  // Curriculum
  getLevels: () => apiClient.get<LevelsResponse>('/api/v1/curriculum/levels').then((r) => r.data),

  getUnits: (level?: string) =>
    apiClient
      .get<UnitsResponse>('/api/v1/curriculum/units', { params: level ? { level } : {} })
      .then((r) => r.data),

  getUnitDetail: (unitId: number) =>
    apiClient.get<UnitDetailResponse>(`/api/v1/curriculum/units/${unitId}`).then((r) => r.data),

  // Exercises
  getExercise: (exerciseId: number) =>
    apiClient.get<ExerciseResponse>(`/api/v1/exercises/${exerciseId}`).then((r) => r.data),

  completeExercise: (exerciseId: number, score: number, total: number) =>
    apiClient
      .post<CompleteExerciseResponse>(`/api/v1/exercises/${exerciseId}/complete`, { score, total })
      .then((r) => r.data),

  // Mini-test
  getMiniTestQuestions: (unitId: number) =>
    apiClient
      .get<MiniTestQuestionsResponse>(`/api/v1/units/${unitId}/mini-test`)
      .then((r) => r.data),

  getMiniTest: (unitId: number) =>
    apiClient
      .get<MiniTestQuestionsResponse>(`/api/v1/units/${unitId}/mini-test`)
      .then((r) => r.data),

  completeMiniTest: (unitId: number, score: number, total: number) =>
    apiClient
      .post<MiniTestCompleteResponse>(`/api/v1/units/${unitId}/mini-test/complete`, {
        score,
        total,
      })
      .then((r) => r.data),

  // Vocabulary
  getDueCards: () => apiClient.get<DueCardsResponse>('/api/v1/vocabulary/due').then((r) => r.data),

  reviewCard: (cardId: number, knew: boolean) =>
    apiClient
      .post<ReviewResponse>(`/api/v1/vocabulary/cards/${cardId}/review`, { known: knew })
      .then((r) => r.data),

  getVocabStats: () =>
    apiClient.get<VocabStatsResponse>('/api/v1/vocabulary/stats').then((r) => r.data),

  // Settings
  patchSettings: (payload: Partial<{ show_instruction_translation: boolean }>) =>
    apiClient.patch<SettingsResponse>('/api/v1/settings', payload).then((r) => r.data),

  // Sync
  syncProgress: (events: ProgressEvent[]) =>
    apiClient.post<SyncResponse>('/api/v1/sync/progress', { events }).then((r) => r.data),
}
