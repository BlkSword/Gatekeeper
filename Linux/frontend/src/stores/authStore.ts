import { defineStore } from 'pinia'

export const useAuthStore = defineStore('auth', {
    state: () => ({
        token: localStorage.getItem('token') || null as string | null,
        isAdmin: false as boolean,
    }),
    actions: {
        setAuth(token: string, isAdmin: boolean) {
            this.token = token
            this.isAdmin = isAdmin
            localStorage.setItem('token', token)
        },
        clearAuth() {
            this.token = null
            this.isAdmin = false
            localStorage.removeItem('token')
        }
    }
})