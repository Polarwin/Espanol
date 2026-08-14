// API contract shared with the FastAPI backend.

export interface User {
  id: number
  email: string
  display_name: string
  nickname: string | null
  interests: string[]
  placement_completed: boolean
}

export function preferredName(user: User): string {
  return user.nickname?.trim() || user.display_name
}

export interface PlacementQuestion {
  id: string
  skill: string
  prompt: string
  options: string[]
}

export interface PlacementResult {
  overall_level: string
  skill_levels: Record<string, string>
  correct: number
  total: number
}

export interface AuthResponse {
  token: string
  user: User
}

export type LoopStep = 'mira' | 'escucha' | 'habla' | 'adapta'

export interface LessonRef {
  id: string
  title: string
  cefr_level: string
  topics: string[]
}

export interface SkillFeedback {
  pronunciation: number
  fluidez: number
  gramatica: number
}

export interface PronunciationTip {
  phrase: string
  tip: string
}

export interface GrammarTip {
  wrong: string
  right: string
  explanation: string
}

export interface NextSuggestion {
  lesson_id: string | number | null
  label: string
  description: string
  topics: string[]
}

export interface TodayPath {
  lesson: LessonRef
  step: LoopStep
  clip_index: number
  total_clips: number
  video_url: string
  subtitle: TranscriptLine
  feedback: SkillFeedback
  pronunciation_tip: PronunciationTip
  grammar_tip: GrammarTip
  next: NextSuggestion
}

export interface LessonSummary {
  id: string
  title: string
  cefr_level: string
  topics: string[]
  source: string
  duration_seconds: number
}

export interface TranscriptLine {
  es: string
  en: string
}

export interface Phrase {
  id: string
  text: string
  translation: string
}

export interface LessonSegment {
  id: string
  index: number
  video_url: string
  start_seconds: number
  end_seconds: number
  transcript: TranscriptLine[]
  phrases: Phrase[]
}

export interface LessonDetail {
  id: string
  title: string
  cefr_level: string
  topics: string[]
  source: string
  duration_seconds: number
  video_url: string
  segments: LessonSegment[]
}

export type ExerciseType = 'vocabulary' | 'grammar' | 'writing' | 'listening'

export interface Exercise {
  id: string
  prompt: string
  audio_url?: string
  options?: string[]
  /** Present only in offline mock fixtures; the real API never returns answers. */
  expected_answer?: string
}

export interface ExerciseGroup {
  type: ExerciseType
  label: string
  instructions: string
  exercises: Exercise[]
}

export interface LessonAssessment {
  duration_minutes: number
  total_questions: number
  groups: ExerciseGroup[]
}

export interface SkillUpdate {
  skill: string
  delta: number
}

export interface AttemptResult {
  correct: boolean
  score: number
  feedback: string
  skill_updates: SkillUpdate[]
}

export interface WordScore {
  word: string
  score: number
}

export interface PronunciationResult {
  score: number
  transcription: string
  feedback: string
  word_scores: WordScore[]
}

export interface SkillScore {
  skill: string
  label: string
  score: number
}

export interface Streak {
  days: number
  recovery_days_left: number
}

export interface WeeklyGoal {
  label: string
  current: number
  target: number
}

export interface Progress {
  skills: SkillScore[]
  streak: Streak
  weekly_goal: WeeklyGoal
  lessons_completed_total: number
  completed_lesson_ids: number[]
}

export interface WeeklyRecap {
  minutes: number
  lessons_completed: number
  words_learned: number
  improvements: { skill: string; label: string; delta: number }[]
  achievement: string
  recommendation: string
}

export interface FriendGroup {
  id: number
  name: string
  invite_code: string
  members: { user_id: number; display_name: string; role: string }[]
  encouragements: { id: number; from_display_name: string; to_user_id: number; message: string; created_at: string }[]
}
