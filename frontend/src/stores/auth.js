import { defineStore } from 'pinia'

import api from '../api'

export const useAuthStore = defineStore('auth', {
  state: () => ({
    username: localStorage.getItem('username') || ''
  }),
  actions: {
    async login(payload) {
      const { data } = await api.post('/auth/login', payload)
      localStorage.setItem('token', data.access_token)
      localStorage.setItem('username', payload.username)
      this.username = payload.username
    },
    logout() {
      localStorage.removeItem('token')
      localStorage.removeItem('username')
      this.username = ''
    }
  }
})
