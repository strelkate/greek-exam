// frontend/src/shared/api/types.ts

export type PlacementStatus = 'pending' | 'passed' | 'failed' | 'skipped'
export type Level = 'A1' | 'A2' | 'B1'
export type ExerciseType =
  | 'true_false'
  | 'matching'
  | 'multiple_choice'
  | 'fill_blank'
  | 'image_description'
  | 'dialogue'

// Auth
export interface SessionResponse {
  user_id: number
  telegram_id: number
  streak_days: number
  total_xp: number
  placement_status: PlacementStatus
  a1_skipped: boolean
  show_instruction_translation: boolean
  is_new_user: boolean
}

// Curriculum
export interface LevelProgress {
  level: Level
  total_units: number
  completed_units: number
  progress_percent: number
}
export interface LevelsResponse {
  levels: LevelProgress[]
}

export interface UnitSummary {
  id: number
  title: string
  order_index: number
  exercises_total: number
  exercises_completed: number
  mini_test_passed: boolean
  unit_completed: boolean
}
export interface UnitsResponse {
  units: UnitSummary[]
}

export interface ExerciseMeta {
  id: number
  type: ExerciseType
  order_index: number
  audio_paths: string[]
  completed: boolean
}
export interface VocabCardMeta {
  id: number
  word_gr: string
  word_ru: string
  audio_path: string | null
}
export interface UnitDetailResponse {
  id: number
  title: string
  level: Level
  exercises: ExerciseMeta[]
  vocabulary_cards: VocabCardMeta[]
}

// Exercises
export interface ExerciseResponse {
  id: number
  unit_id: number
  type: ExerciseType
  content: Record<string, unknown>
  audio_paths: string[]
}
export interface CompleteExerciseResponse {
  xp_earned: number
  xp_breakdown: Record<string, number>
  streak_days: number
  streak_updated: boolean
  unit_progress: {
    exercises_completed: number
    exercises_total: number
    mini_test_unlocked: boolean
  }
}

// Placement
export interface PlacementQuestion {
  id: number
  type: 'true_false' | 'multiple_choice' | 'fill_blank'
  content: Record<string, unknown>
}
export interface PlacementQuestionsResponse {
  questions: PlacementQuestion[]
}
export interface PlacementCompleteResponse {
  placement_status: PlacementStatus
  a1_skipped: boolean
  message: string
}

// Mini-test
export interface MiniTestQuestion {
  id: number
  type: 'true_false' | 'multiple_choice' | 'fill_blank'
  content: Record<string, unknown>
}
export interface MiniTestQuestionsResponse {
  questions: MiniTestQuestion[]
}
export interface MiniTestCompleteResponse {
  unit_completed: boolean
  xp_earned: number
  cards_added_to_vocab: number
}

// Vocabulary
export type CardStatus = 'new' | 'learning' | 'learned'

export interface VocabCard {
  id: number
  word_gr: string
  word_ru: string
  audio_path: string | null
  status: CardStatus
  next_review_at: string
}
export interface DueCardsResponse {
  due_count: number
  cards: VocabCard[]
}
export interface ReviewResponse {
  card_id: number
  new_status: CardStatus
  next_review_at: string
  interval_days: number
  xp_earned: number
}
export interface VocabStatsResponse {
  total_cards: number
  learned_count: number
  due_today: number
  new_count: number
}

// Settings
export interface SettingsResponse {
  show_instruction_translation: boolean
}

// Sync
export interface ProgressEvent {
  exercise_id: number
  score: number
  total: number
  completed_at: string
}
export interface SyncResponse {
  synced: number
  xp_earned: number
}
