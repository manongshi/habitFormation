const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || '/api/v1'

async function request(path, options = {}) {
  const token = localStorage.getItem('exam_coach_token')
  const response = await fetch(`${API_BASE_URL}${path}`, {
    headers: {
      'Content-Type': 'application/json',
      ...(token ? { Authorization: `Bearer ${token}` } : {}),
      ...options.headers,
    },
    ...options,
  })

  if (!response.ok) {
    const data = await response.json().catch(() => null)
    if (response.status === 401 && token) {
      localStorage.removeItem('exam_coach_token')
      localStorage.removeItem('exam_coach_user')
      window.dispatchEvent(new CustomEvent('auth-expired'))
    }
    throw new Error(data?.detail || '请求失败，请稍后重试')
  }

  return response.json()
}

export function register(payload) {
  return request('/auth/register', {
    method: 'POST',
    body: JSON.stringify(payload),
  })
}

export function sendEmailCode(email) {
  return request('/auth/email-code', {
    method: 'POST',
    body: JSON.stringify({ email, scene: 'register' }),
  })
}

export function login(payload) {
  return request('/auth/login', {
    method: 'POST',
    body: JSON.stringify(payload),
  })
}

export function getCurrentUser() {
  return request('/auth/me')
}

export function getDashboardOverview() {
  return request('/dashboard/overview')
}

export function createExamGoal(payload) {
  return request('/goals', {
    method: 'POST',
    body: JSON.stringify(payload),
  })
}

export function getPlans() {
  return request('/payments/plans')
}

export function getSubscription() {
  return request('/payments/subscription')
}

export function createPaymentOrder(planCode) {
  return request('/payments/orders', {
    method: 'POST',
    body: JSON.stringify({ plan_code: planCode }),
  })
}

export function mockPayOrder(orderNo) {
  return request(`/payments/orders/${orderNo}/mock-pay`, { method: 'POST' })
}

export function getCertificateCategories() {
  return request('/certificates/categories')
}

export function getCertificates(params = {}) {
  const query = new URLSearchParams()
  Object.entries(params).forEach(([key, value]) => {
    if (value !== undefined && value !== null && value !== '') query.set(key, value)
  })
  return request(`/certificates?${query.toString()}`)
}

export function getCertificate(certificateId) {
  return request(`/certificates/${certificateId}`)
}

export function generateStudyPlan(payload) {
  return request('/study-plans/generate', {
    method: 'POST',
    body: JSON.stringify(payload),
  })
}

export function getStudyPlan(planId) {
  return request(`/study-plans/${planId}`)
}

export function getStudyPlans(studyDate = '') {
  const query = studyDate ? `?study_date=${encodeURIComponent(studyDate)}` : ''
  return request(`/study-plans${query}`)
}

export function getStudyCalendar(month) {
  return request(`/study-plans/calendar?month=${encodeURIComponent(month)}`)
}

export function updateStudyTask(taskId, completed) {
  return request(`/study-plans/tasks/${taskId}`, {
    method: 'PATCH',
    body: JSON.stringify({ completed }),
  })
}

export function getDailySummary(studyDate) {
  return request(`/study-plans/daily-summary?study_date=${encodeURIComponent(studyDate)}`)
}

export function saveDailySummary(studyDate, content, contentFormat = 'markdown') {
  return request(`/study-plans/daily-summary?study_date=${encodeURIComponent(studyDate)}`, {
    method: 'PUT',
    body: JSON.stringify({ content, content_format: contentFormat }),
  })
}
