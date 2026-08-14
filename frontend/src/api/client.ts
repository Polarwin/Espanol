// Typed API client. When the backend is unreachable, calls fall back to the
// mock layer automatically (toggle with MOCK_FALLBACK_ENABLED).

import * as mock from './mock'
import { Capacitor } from '@capacitor/core'
import type {
  AttemptResult,
  AuthResponse,
  LessonAssessment,
  LessonDetail,
  LessonSummary,
  Progress,
  PronunciationResult,
  TodayPath,
  WeeklyRecap,
  FriendGroup,
  PlacementQuestion,
  PlacementResult,
} from './types'

export const MOCK_FALLBACK_ENABLED = import.meta.env.VITE_ENABLE_MOCKS === 'true'
const PUBLIC_APP_ORIGIN = 'https://espanol.justinrecipes.duckdns.org'
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

async function request<T>(path: string, init: RequestInit = {}): Promise<T> {
  const headers = new Headers(init.headers)
  const token = getToken()
  if (token) headers.set('Authorization', `Bearer ${token}`)
  if (init.body && !(init.body instanceof FormData)) {
    headers.set('Content-Type', 'application/json')
  }
  const res = await fetch(`${API_ORIGIN}${path}`, { ...init, headers })
  if (!res.ok) {
    if (res.status === 401 && !path.startsWith('/api/auth/')) {
      setToken(null)
      if (window.location.pathname !== '/entrar') window.location.assign('/entrar')
    }
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
    if (MOCK_FALLBACK_ENABLED) return fallback()
    throw err
  }
}

export const api = {
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

  getLessons(): Promise<LessonSummary[]> {
    return withMock(() => request<LessonSummary[]>('/api/lessons'), () => mock.mockLessons())
  },

  getLesson(id: string): Promise<LessonDetail> {
    return withMock(() => request<LessonDetail>(`/api/lessons/${id}`), () => mock.mockLesson(id))
  },

  getAssessment(lessonId: string): Promise<LessonAssessment> {
    return withMock(
      () => request<LessonAssessment>(`/api/lessons/${lessonId}/assessment`),
      () => mock.mockAssessment(),
    )
  },

  submitAttempt(exerciseId: string, answer: string): Promise<AttemptResult> {
    return withMock(
      () =>
        request<AttemptResult>(`/api/exercises/${exerciseId}/attempt`, {
          method: 'POST',
          body: JSON.stringify({ answer }),
        }),
      () => mock.mockAttempt(exerciseId, answer),
    )
  },

  evaluatePronunciation(phraseId: string, audio: Blob): Promise<PronunciationResult> {
    return withMock(
      () => {
        const form = new FormData()
        form.append('phrase_id', phraseId)
        form.append('audio', audio, 'recording.webm')
        return request<PronunciationResult>('/api/pronunciation/evaluate', {
          method: 'POST',
          body: form,
        })
      },
      () => mock.mockPronunciation(),
    )
  },

  getProgress(): Promise<Progress> {
    return withMock(() => request<Progress>('/api/progress'), () => mock.mockProgress())
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

  getPlacement(): Promise<PlacementQuestion[]> {
    return request<PlacementQuestion[]>('/api/placement')
  },

  submitPlacement(answers: Record<string, string>): Promise<PlacementResult> {
    return request<PlacementResult>('/api/placement', { method: 'POST', body: JSON.stringify({ answers }) })
  },

  skipPlacement(): Promise<PlacementResult> {
    return request<PlacementResult>('/api/placement/skip', { method: 'POST' })
  },
}
