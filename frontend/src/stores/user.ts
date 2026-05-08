import { defineStore } from 'pinia'
import { ref } from 'vue'
import { authApi } from '../api'

export const useUserStore = defineStore('user', () => {
  const user = ref<any>(null)
  const token = ref(localStorage.getItem('token') || '')

  async function login(username: string, password: string) {
    const { data } = await authApi.login({ username, password })
    token.value = data.access_token
    localStorage.setItem('token', data.access_token)
    await fetchUser()
  }

  async function register(username: string, email: string, password: string) {
    await authApi.register({ username, email, password })
    await login(username, password)
  }

  async function fetchUser() {
    if (!token.value) return
    try {
      const { data } = await authApi.me()
      user.value = data
    } catch {
      logout()
    }
  }

  function logout() {
    user.value = null
    token.value = ''
    localStorage.removeItem('token')
  }

  return { user, token, login, register, fetchUser, logout }
})
