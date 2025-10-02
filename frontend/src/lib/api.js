import axios from 'axios'

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8001'

export const api = axios.create({
  baseURL: `${API_URL}/api`,
  headers: {
    'Content-Type': 'application/json',
  },
})

// Auth APIs
export const authAPI = {
  register: (data) => api.post('/auth/register', data),
  login: (data) => api.post('/auth/login', data),
  getMe: (userId) => api.get(`/auth/me?user_id=${userId}`),
}

// User APIs
export const userAPI = {
  getPreferences: (userId) => api.get(`/users/preferences/${userId}`),
  updatePreferences: (userId, data) => api.put(`/users/preferences/${userId}`, data),
}

// Test Session APIs
export const testSessionAPI = {
  create: (data) => api.post('/test-sessions/', data),
  get: (sessionId) => api.get(`/test-sessions/${sessionId}`),
  getUserSessions: (userId) => api.get(`/test-sessions/user/${userId}`),
  update: (sessionId, data) => api.put(`/test-sessions/${sessionId}`, data),
}

// User Assessment API
export const assessmentAPI = {
  getAccessibilityAssessment: (userId) => api.post(`/assessment/accessibility-assessment?user_id=${userId}`),
  getUserTestBattery: (userId) => api.get(`/assessment/test-battery/${userId}`),
  updateAccessibilityPreferences: (userId, preferences) => 
    api.post(`/assessment/update-accessibility-preferences?user_id=${userId}`, preferences)
}

// Cognitive Test APIs
export const cognitiveTestAPI = {
  submit: (data) => api.post('/cognitive-tests/submit', data),
  getSessionTests: (sessionId) => api.get(`/cognitive-tests/session/${sessionId}`),
}

// Speech Test APIs
export const speechTestAPI = {
  submit: (formData) => api.post('/speech-tests/submit', formData, {
    headers: { 'Content-Type': 'multipart/form-data' }
  }),
  getSessionTests: (sessionId) => api.get(`/speech-tests/session/${sessionId}`),
  
  // TTS APIs
  generateSpeech: (data) => api.post('/speech-tests/tts/generate', data, {
    responseType: 'blob'
  }),
  getVoices: (language) => api.get(`/speech-tests/tts/voices/${language}`),
  
  // Enhanced transcription
  transcribe: (formData) => api.post('/speech-tests/enhanced/transcribe', formData, {
    headers: { 'Content-Type': 'multipart/form-data' }
  }),
  
  // Enhanced speech tests
  enhanced: {
    submit: (formData) => api.post('/speech-tests/enhanced/submit', formData, {
      headers: { 'Content-Type': 'multipart/form-data' }
    }),
    transcribe: (formData) => api.post('/speech-tests/transcribe', formData, {
      headers: { 'Content-Type': 'multipart/form-data' }
    })
  }
}

// Behavioral Test APIs
export const behavioralTestAPI = {
  submit: (data) => api.post('/behavioral-tests/submit', data),
  getSessionTests: (sessionId) => api.get(`/behavioral-tests/session/${sessionId}`),
}

// Report APIs
export const reportAPI = {
  generate: (sessionId, reportType) => api.post(`/reports/generate/${sessionId}?report_type=${reportType}`),
  download: (reportId) => api.get(`/reports/download/${reportId}`, { responseType: 'blob' }),
  getUserReports: (userId) => api.get(`/reports/user/${userId}`),
}

// Progress APIs
export const progressAPI = {
  getUserProgress: (userId) => api.get(`/progress/user/${userId}`),
  getComparison: (userId) => api.get(`/progress/user/${userId}/comparison`),
  calculateNextDate: (userId) => api.post(`/progress/calculate-next-date/${userId}`),
}
