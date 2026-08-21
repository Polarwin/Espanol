// Typed API client. When the backend is unreachable, calls fall back to the
// mock layer automatically (toggle with MOCK_FALLBACK_ENABLED).

import * as mock from './mock'
import { Capacitor } from '@capacitor/core'
import type {
  AttemptResult,
  AuthResponse,
  ClipQuizResult,
  LessonAssessment,
  LessonDetail,
  LessonSummary,
  Progress,
  ReviewItem,
  ReviewResult,
  PronunciationResult,
  ConversationResult,
  ConversationSetup,
  TodayPath,
  WeeklyRecap,
  FriendGroup,
  PlacementQuestion,
  PlacementGradeResult,
  PlacementResult,
  User,
} from './types'

export const MOCK_FALLBACK_ENABLED = import.meta.env.VITE_ENABLE_MOCKS === 'true'
export const API_UNAVAILABLE_EVENT = 'vamos:api-unavailable'
const PUBLIC_APP_ORIGIN = import.meta.env.VITE_API_ORIGIN ?? 'https://espanol.justinrecipes.duckdns.org'
const API_ORIGIN = Capacitor.isNativePlatform() ? PUBLIC_APP_ORIGIN : ''

const TOKEN_KEY = 'vamos.token'
const PLACEMENT_KEY = 'vamos.placement-completed'

export function getToken(): string | null {
  return localStorage.getItem(TOKEN_KEY)
}

export function setToken(token: string | null) {
  if (token) localStorage.setItem(TOKEN_KEY, token)
  else {
    localStorage.removeItem(TOKEN_KEY)
    localStorage.removeItem(PLACEMENT_KEY)
  }
}

export function placementComplete(): boolean {
  return localStorage.getItem(PLACEMENT_KEY) === 'true'
}

export function setPlacementComplete(value: boolean) {
  localStorage.setItem(PLACEMENT_KEY, String(value))
}

export class ApiError extends Error {
  status: number
  constructor(status: number, message: string) {
    super(message)
    this.status = status
  }
}

function handleUnauthorized(path: string, status: number) {
  if (status === 401 && !path.startsWith('/api/auth/')) {
    setToken(null)
    if (window.location.pathname !== '/entrar') window.location.assign('/entrar')
  }
}

async function request<T>(path: string, init: RequestInit = {}): Promise<T> {
  const headers = new Headers(init.headers)
  const token = getToken()
  if (token) headers.set('Authorization', `Bearer ${token}`)
  if (init.body && !(init.body instanceof FormData)) {
    headers.set('Content-Type', 'application/json')
  }
  let res: Response
  try {
    res = await fetch(`${API_ORIGIN}${path}`, { ...init, headers })
  } catch (error) {
    if (Capacitor.isNativePlatform() && error instanceof TypeError) {
      window.dispatchEvent(new Event(API_UNAVAILABLE_EVENT))
    }
    throw error
  }
  if (!res.ok) {
    handleUnauthorized(path, res.status)
    throw new ApiError(res.status, `Request failed: ${res.status} ${path}`)
  }
  return absoluteMediaUrls(await res.json()) as T
}

function absoluteMediaUrls(value: unknown): unknown {
  if (Array.isArray(value)) return value.map(absoluteMediaUrls)
  if (value === null || typeof value !== 'object') return value

  return Object.fromEntries(
    Object.entries(value).map(([key, item]) => {
      if (
        (key === 'video_url' || key === 'audio_url') &&
        typeof item === 'string' &&
        item.startsWith('/')
      ) {
        return [key, `${API_ORIGIN}${item}`]
      }
      return [key, absoluteMediaUrls(item)]
    }),
  )
}

async function withMock<T>(call: () => Promise<T>, fallback: () => Promise<T>): Promise<T> {
  try {
    return await call()
  } catch (err) {
    // Fall back to mocks only on genuine network failures (fetch rejects with
    // a TypeError). API errors (401/409/…) must reach the caller, otherwise a
    // failed login or register would look like a success when mocks are on.
    if (MOCK_FALLBACK_ENABLED && !(err instanceof ApiError) && err instanceof TypeError) return fallback()
    throw err
  }
}

export const api = {
  getMe(): Promise<User> {
    return request<User>('/api/me')
  },

  updateProfile(displayName: string, nickname: string | null): Promise<User> {
    return request<User>('/api/me', {
      method: 'PATCH',
      body: JSON.stringify({ display_name: displayName, nickname }),
    })
  },

  register(email: string, password: string, displayName: string, interests: string[]): Promise<AuthResponse> {
    return withMock(
      () =>
        request<AuthResponse>('/api/auth/register', {
          method: 'POST',
          body: JSON.stringify({ email, password, display_name: displayName, interests }),
        }),
      () => mock.mockRegister(),
    )
  },

  login(email: string, password: string): Promise<AuthResponse> {
    return withMock(
      () =>
        request<AuthResponse>('/api/auth/login', {
          method: 'POST',
          body: JSON.stringify({ email, password }),
        }),
      () => mock.mockLogin(),
    )
  },

  getTodayPath(): Promise<TodayPath> {
    return withMock(() => request<TodayPath>('/api/path/today'), () => mock.mockTodayPath())
  },

  advancePath(step: TodayPath['step']): Promise<TodayPath> {
    return request<TodayPath>('/api/path/advance', {
      method: 'POST',
      body: JSON.stringify({ step }),
    })
  },

  answerClipQuiz(choice: string): Promise<ClipQuizResult> {
    return request<ClipQuizResult>('/api/path/quiz', {
      method: 'POST',
      body: JSON.stringify({ choice }),
    })
  },

  getLessons(): Promise<LessonSummary[]> {
    return withMock(() => request<LessonSummary[]>('/api/lessons'), () => mock.mockLessons())
  },

  getLesson(id: number, variation = 0): Promise<LessonDetail> {
    return withMock(() => request<LessonDetail>(`/api/lessons/${id}?variation=${variation}`), () => mock.mockLesson(id))
  },

  selectLesson(id: number): Promise<{ selected: boolean; lesson_id: number }> {
    return request(`/api/lessons/${id}/select`, { method: 'POST' })
  },

  getAssessment(lessonId: number): Promise<LessonAssessment> {
    return withMock(
      () => request<LessonAssessment>(`/api/lessons/${lessonId}/assessment`),
      () => mock.mockAssessment(),
    )
  },

  completeLesson(lessonId: number): Promise<{ saved: boolean; new_completion: boolean; lessons_completed_total: number }> {
    return request(`/api/lessons/${lessonId}/complete`, { method: 'POST' })
  },

  submitAttempt(exerciseId: number, answer: string): Promise<AttemptResult> {
    return withMock(
      () =>
        request<AttemptResult>(`/api/exercises/${exerciseId}/attempt`, {
          method: 'POST',
          body: JSON.stringify({ answer }),
        }),
      () => mock.mockAttempt(exerciseId, answer),
    )
  },

  evaluatePronunciation(phraseId: string, phrase: string, audio: Blob): Promise<PronunciationResult> {
    return withMock(
      () => {
        const form = new FormData()
        form.append('phrase_id', phraseId)
        form.append('phrase', phrase)
        form.append('audio', audio, 'recording.webm')
        return request<PronunciationResult>('/api/pronunciation/evaluate', {
          method: 'POST',
          body: form,
        })
      },
      () => mock.mockPronunciation(),
    )
  },

  async getSpeechExample(phrase: string): Promise<Blob> {
    const headers = new Headers({ 'Content-Type': 'application/json' })
    const token = getToken()
    if (token) headers.set('Authorization', `Bearer ${token}`)
    const response = await fetch(`${API_ORIGIN}/api/speech/example`, {
      method: 'POST',
      headers,
      body: JSON.stringify({ phrase }),
    })
    if (!response.ok) {
      handleUnauthorized('/api/speech/example', response.status)
      throw new ApiError(response.status, 'No se pudo cargar el ejemplo de audio')
    }
    return response.blob()
  },

  getConversationSetup(lessonId?: string): Promise<ConversationSetup> {
    const query = lessonId ? `?lesson_id=${encodeURIComponent(lessonId)}` : ''
    return request<ConversationSetup>(`/api/conversation/setup${query}`)
  },

  respondToConversation(turn: number, audio: Blob, lessonId?: number): Promise<ConversationResult> {
    const form = new FormData()
    form.append('turn', String(turn))
    if (lessonId) form.append('lesson_id', String(lessonId))
    form.append('audio', audio, 'conversation.webm')
    return request<ConversationResult>('/api/conversation/respond', { method: 'POST', body: form })
  },

  getProgress(): Promise<Progress> {
    return withMock(() => request<Progress>('/api/progress'), () => mock.mockProgress())
  },

  getReviewItems(): Promise<ReviewItem[]> {
    return request<ReviewItem[]>('/api/review')
  },

  answerReview(itemId: number, answer: string): Promise<ReviewResult> {
    return request<ReviewResult>(`/api/review/${itemId}`, { method: 'POST', body: JSON.stringify({ answer }) })
  },

  getWeeklyRecap(): Promise<WeeklyRecap> {
    return withMock(() => request<WeeklyRecap>('/api/recap/weekly'), () => mock.mockWeeklyRecap())
  },

  getGroups(): Promise<FriendGroup[]> {
    return request<FriendGroup[]>('/api/groups')
  },

  createGroup(name: string): Promise<FriendGroup> {
    return request<FriendGroup>('/api/groups', { method: 'POST', body: JSON.stringify({ name }) })
  },

  joinGroup(inviteCode: string): Promise<FriendGroup> {
    return request<FriendGroup>('/api/groups/join', { method: 'POST', body: JSON.stringify({ invite_code: inviteCode }) })
  },

  encourage(groupId: number, toUserId: number, message: string): Promise<FriendGroup> {
    return request<FriendGroup>(`/api/groups/${groupId}/encouragements`, {
      method: 'POST',
      body: JSON.stringify({ to_user_id: toUserId, message }),
    })
  },

  getPlacement(level: string): Promise<PlacementQuestion[]> {
    return request<PlacementQuestion[]>(`/api/placement?level=${level}`)
  },

  gradePlacement(level: string, answers: Record<string, string>): Promise<PlacementGradeResult> {
    return request<PlacementGradeResult>('/api/placement/grade', { method: 'POST', body: JSON.stringify({ level, answers }) })
  },

  submitPlacement(answers: Record<string, string>): Promise<PlacementResult> {
    return request<PlacementResult>('/api/placement', { method: 'POST', body: JSON.stringify({ answers }) })
  },

  skipPlacement(): Promise<PlacementResult> {
    return request<PlacementResult>('/api/placement/skip', { method: 'POST' })
  },

  setLevel(level: string): Promise<PlacementResult> {
    return request<PlacementResult>('/api/placement/manual', { method: 'POST', body: JSON.stringify({ level }) })
  },
}
