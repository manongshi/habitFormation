import { computed, ref } from 'vue'
import { defineStore } from 'pinia'

import {
  getCurrentUser,
  login as loginRequest,
  register as registerRequest,
} from '../services/api'

const TOKEN_KEY = 'exam_coach_token'
const USER_KEY = 'exam_coach_user'

function readStoredUser() {
  const value = localStorage.getItem(USER_KEY)
  if (!value) return null
  try {
    return JSON.parse(value)
  } catch {
    localStorage.removeItem(USER_KEY)
    return null
  }
}

export const useUserStore = defineStore('user', () => {
  const token = ref(localStorage.getItem(TOKEN_KEY) || '')
  const userInfo = ref(readStoredUser())
  const loading = ref(false)

  const isLoggedIn = computed(() => Boolean(token.value))
  const nickname = computed(() => userInfo.value?.nickname || '用户')

  function saveSession(session) {
    token.value = session.access_token
    userInfo.value = session.user
    localStorage.setItem(TOKEN_KEY, session.access_token)
    localStorage.setItem(USER_KEY, JSON.stringify(session.user))
  }

  async function login(payload) {
    loading.value = true
    try {
      const session = await loginRequest(payload)
      saveSession(session)
      return session.user
    } finally {
      loading.value = false
    }
  }

  async function register(payload) {
    loading.value = true
    try {
      const session = await registerRequest(payload)
      saveSession(session)
      return session.user
    } finally {
      loading.value = false
    }
  }

  async function fetchUserInfo() {
    if (!token.value) return null
    const user = await getCurrentUser()
    userInfo.value = user
    localStorage.setItem(USER_KEY, JSON.stringify(user))
    return user
  }

  function logout() {
    token.value = ''
    userInfo.value = null
    localStorage.removeItem(TOKEN_KEY)
    localStorage.removeItem(USER_KEY)
  }

  window.addEventListener('auth-expired', logout)

  return {
    token,
    userInfo,
    loading,
    isLoggedIn,
    nickname,
    login,
    register,
    fetchUserInfo,
    logout,
  }
})
