// Mock data matching the API contract exactly. Used automatically when the
// backend is unreachable so the app is fully demoable on its own.

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
} from './types'

const delay = (ms = 250) => new Promise((r) => setTimeout(r, ms))

const MOCK_USER = {
  id: 1,
  email: 'maya@example.com',
  display_name: 'Maya',
  nickname: 'May',
  interests: ['viajes', 'vida diaria', 'cultura'],
  placement_completed: true,
}

export async function mockRegister(): Promise<AuthResponse> {
  await delay()
  return { token: 'mock-token', user: MOCK_USER }
}

export async function mockLogin(): Promise<AuthResponse> {
  await delay()
  return { token: 'mock-token', user: MOCK_USER }
}

export async function mockTodayPath(): Promise<TodayPath> {
  await delay()
  return {
    lesson: {
      id: 'lesson-charla-vecinos',
      title: 'Charla con vecinos',
      cefr_level: 'A2',
      topics: ['vida diaria', 'planes', 'conversación'],
    },
    step: 'habla',
    clip_index: 3,
    total_clips: 8,
    video_url: '/media/lessons/charla-vecinos/clip-3.mp4',
    subtitle: {
      es: '¿Qué planes tienes para el fin de semana?',
      en: 'What plans do you have for the weekend?',
    },
    feedback: { pronunciation: 82, fluidez: 74, gramatica: 90 },
    pronunciation_tip: {
      phrase: 'fin de semana',
      tip: 'Suaviza la d entre vocales',
    },
    grammar_tip: {
      wrong: '¿Qué planes tú tienes?',
      right: '¿Qué planes tienes?',
      explanation: 'El pronombre no es necesario aquí.',
    },
    next: {
      lesson_id: 'lesson-charla-vecinos',
      label: 'Siguiente: práctica A2+',
      description: 'Subimos el ritmo; repetimos la d suave.',
      topics: ['Viajes', 'Vida diaria'],
    },
  }
}

export async function mockLessons(): Promise<LessonSummary[]> {
  await delay()
  return [
    {
      id: 'lesson-charla-vecinos',
      title: 'Charla con vecinos',
      cefr_level: 'A2',
      topics: ['vida diaria', 'planes'],
      source: 'Biblioteca local',
      duration_seconds: 720,
    },
    {
      id: 'lesson-mercado',
      title: 'En el mercado',
      cefr_level: 'A2',
      topics: ['comida', 'compras'],
      source: 'Biblioteca local',
      duration_seconds: 640,
    },
    {
      id: 'lesson-viaje-tren',
      title: 'Un viaje en tren',
      cefr_level: 'A2+',
      topics: ['viajes', 'direcciones'],
      source: 'Contenido online revisado',
      duration_seconds: 810,
    },
  ]
}

export async function mockLesson(id: string): Promise<LessonDetail> {
  await delay()
  const segments = Array.from({ length: 8 }, (_, i) => ({
    id: `${id}-seg-${i + 1}`,
    index: i + 1,
    video_url: `/media/lessons/charla-vecinos/clip-${i + 1}.mp4`,
    start_seconds: i * 42,
    end_seconds: (i + 1) * 42,
    transcript: [
      { es: '¿Qué planes tienes para el fin de semana?', en: 'What plans do you have for the weekend?' },
      { es: 'Este fin de semana voy a visitar a mis vecinos.', en: 'This weekend I am going to visit my neighbors.' },
    ],
    phrases: [
      { id: `${id}-seg-${i + 1}-ph-1`, text: '¿Qué planes tienes para el fin de semana?', translation: 'What plans do you have for the weekend?' },
      { id: `${id}-seg-${i + 1}-ph-2`, text: 'Voy a ir a la playa.', translation: 'I am going to go to the beach.' },
    ],
  }))
  return {
    id,
    title: 'Charla con vecinos',
    cefr_level: 'A2',
    topics: ['vida diaria', 'planes', 'conversación'],
    source: 'Biblioteca local',
    duration_seconds: 336,
    video_url: '/media/lessons/charla-vecinos/video.mp4',
    personal_welcome: 'Maya, hoy conectamos esta lección con tu vida diaria.',
    session_mission: 'Escucha primero la idea principal.',
    closing_challenge: 'Cambia un detalle para que se parezca a tu vida.',
    focus_phrase: '¿Qué planes tienes?',
    vocabulary: [
      { text: 'el fin de semana', translation: 'weekend', definition_es: 'Una expresión para hablar del sábado y el domingo.', example_es: '¿Qué planes tienes para el fin de semana?' },
      { text: 'quedar para comer', translation: 'to meet for lunch', definition_es: 'Acordar una hora y un lugar para comer juntos.', example_es: 'Podemos quedar para comer el sábado.' },
    ],
    segments,
  }
}

export async function mockAssessment(): Promise<LessonAssessment> {
  await delay()
  return {
    duration_minutes: 12,
    total_questions: 10,
    groups: [
      {
        type: 'vocabulary',
        label: 'Vocabulario',
        instructions: 'Relaciona las palabras.',
        exercises: [
          { id: 'ex-v1', prompt: 'quedar', options: ['reunirse', 'salir', 'llamar'], expected_answer: 'reunirse' },
          { id: 'ex-v2', prompt: 'el vecino', options: ['neighbor', 'friend', 'cousin'], expected_answer: 'neighbor' },
          { id: 'ex-v3', prompt: 'el fin de semana', options: ['the weekend', 'the week', 'the party'], expected_answer: 'the weekend' },
          { id: 'ex-v4', prompt: 'visitar', options: ['to visit', 'to travel', 'to live'], expected_answer: 'to visit' },
          { id: 'ex-v5', prompt: 'la playa', options: ['the beach', 'the pool', 'the park'], expected_answer: 'the beach' },
        ],
      },
      {
        type: 'grammar',
        label: 'Gramática',
        instructions: 'Completa la frase.',
        exercises: [
          { id: 'ex-g1', prompt: 'Este sábado ___ a visitar Madrid.', expected_answer: 'voy' },
          { id: 'ex-g2', prompt: '¿Qué planes ___ para el domingo?', expected_answer: 'tienes' },
          { id: 'ex-g3', prompt: 'Lucía ___ a la playa con sus amigos.', expected_answer: 'va' },
          { id: 'ex-g4', prompt: 'Vamos ___ reunirnos en la plaza.', expected_answer: 'a' },
          { id: 'ex-g5', prompt: '___ planes tienes para el fin de semana?', expected_answer: 'Qué' },
        ],
      },
      {
        type: 'writing',
        label: 'Escritura',
        instructions: 'Escribe 4 frases sobre tus planes.',
        exercises: [
          { id: 'ex-w1', prompt: 'Este fin de semana voy a…', expected_answer: '' },
          { id: 'ex-w2', prompt: 'El sábado por la mañana…', expected_answer: '' },
          { id: 'ex-w3', prompt: 'El domingo voy a quedar con…', expected_answer: '' },
          { id: 'ex-w4', prompt: 'Después de visitar a mis vecinos…', expected_answer: '' },
        ],
      },
      {
        type: 'listening',
        label: 'Comprensión',
        instructions: 'Escucha y responde.',
        exercises: [
          {
            id: 'ex-l1',
            prompt: '¿Qué hará Lucía este fin de semana?',
            audio_url: '/media/lessons/charla-vecinos/audio-1.mp3',
            options: ['Visitará a sus vecinos', 'Irá a la playa', 'Trabajará en casa'],
            expected_answer: 'Irá a la playa',
          },
          {
            id: 'ex-l2',
            prompt: '¿Con quién quedará Lucía el sábado?',
            audio_url: '/media/lessons/charla-vecinos/audio-2.mp3',
            options: ['Con su hermana', 'Con sus vecinos', 'Con sus compañeros de trabajo'],
            expected_answer: 'Con sus vecinos',
          },
          {
            id: 'ex-l3',
            prompt: '¿Cuándo volverá Lucía a casa?',
            audio_url: '/media/lessons/charla-vecinos/audio-3.mp3',
            options: ['El domingo por la tarde', 'El lunes por la mañana', 'El sábado por la noche'],
            expected_answer: 'El domingo por la tarde',
          },
        ],
      },
    ],
  }
}

export async function mockAttempt(exerciseId: string, answer: string): Promise<AttemptResult> {
  await delay()
  const expected: Record<string, string> = {
    'ex-l1': 'Irá a la playa',
    'ex-l2': 'Con sus vecinos',
    'ex-l3': 'El domingo por la tarde',
    'ex-g1': 'voy',
    'ex-g2': 'tienes',
    'ex-g3': 'va',
    'ex-g4': 'a',
    'ex-g5': 'Qué',
    'ex-v1': 'reunirse',
    'ex-v2': 'neighbor',
    'ex-v3': 'the weekend',
    'ex-v4': 'to visit',
    'ex-v5': 'the beach',
  }
  const want = expected[exerciseId] ?? ''
  const correct = answer.trim().toLowerCase() === want.toLowerCase()
  return {
    correct,
    score: correct ? 100 : 0,
    feedback: correct ? '¡Muy bien! Respuesta correcta.' : `Casi. La respuesta correcta es «${want}».`,
    skill_updates: [{ skill: exerciseId.startsWith('ex-l') ? 'listening' : 'grammar', delta: correct ? 2 : -1 }],
  }
}

export async function mockPronunciation(): Promise<PronunciationResult> {
  await delay(600)
  return {
    score: 82,
    transcription: '¿Qué planes tienes para el fin de semana?',
    feedback: 'Buena entonación. Suaviza la d entre vocales en «de».',
    word_scores: [
      { word: 'qué', score: 90 },
      { word: 'planes', score: 88 },
      { word: 'tienes', score: 84 },
      { word: 'para', score: 86 },
      { word: 'el', score: 92 },
      { word: 'fin', score: 80 },
      { word: 'de', score: 64 },
      { word: 'semana', score: 85 },
    ],
  }
}

export async function mockProgress(): Promise<Progress> {
  await delay()
  return {
    skills: [
      { skill: 'pronunciation', label: 'Pronunciación', score: 82 },
      { skill: 'fluency', label: 'Fluidez', score: 74 },
      { skill: 'grammar', label: 'Gramática', score: 90 },
      { skill: 'vocabulary', label: 'Vocabulario', score: 68 },
      { skill: 'listening', label: 'Comprensión auditiva', score: 77 },
      { skill: 'writing', label: 'Escritura', score: 61 },
    ],
    streak: { days: 12, recovery_days_left: 2 },
    weekly_goal: { label: 'Completa 3 lecciones', current: 2, target: 3 },
    lessons_completed_total: 5,
    completed_lesson_ids: [1, 2, 3, 4, 5],
  }
}

export async function mockWeeklyRecap(): Promise<WeeklyRecap> {
  await delay()
  return {
    minutes: 42,
    lessons_completed: 5,
    words_learned: 18,
    improvements: [
      { skill: 'pronunciation', label: 'Pronunciación', delta: 6 },
      { skill: 'listening', label: 'Comprensión auditiva', delta: 4 },
      { skill: 'writing', label: 'Escritura', delta: 3 },
    ],
    achievement: 'Entendiste una conversación A2 completa sin subtítulos en inglés.',
    recommendation: 'La próxima semana practicaremos los planes de futuro con conversaciones de viajes.',
  }
}
