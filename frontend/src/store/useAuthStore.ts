import { create } from 'zustand'
import { persist, createJSONStorage } from 'zustand/middleware'
import type { AuthUser } from '@/api/auth'

interface AuthState {
  user:            AuthUser | null
  token:           string | null
  rememberMe:      boolean
  isAuthenticated: boolean
  isLoggingOut:    boolean
  setAuth:      (user: AuthUser, token: string, rememberMe: boolean) => void
  clearAuth:    () => void
  setLoggingOut:(v: boolean) => void
}

// ── Storage: localStorage (remember-me) or sessionStorage (session-only) ─────
const conditionalStorage = {
  getItem: (name: string) =>
    localStorage.getItem(name) ?? sessionStorage.getItem(name),

  setItem: (name: string, value: string) => {
    try {
      const rememberMe = JSON.parse(value)?.state?.rememberMe ?? false
      if (rememberMe) {
        localStorage.setItem(name, value)
        sessionStorage.removeItem(name)
      } else {
        sessionStorage.setItem(name, value)
        localStorage.removeItem(name)
      }
    } catch {
      sessionStorage.setItem(name, value)
    }
  },

  removeItem: (name: string) => {
    localStorage.removeItem(name)
    sessionStorage.removeItem(name)
  },
}

export const useAuthStore = create<AuthState>()(
  persist(
    (set) => ({
      user:            null,
      token:           null,
      rememberMe:      false,
      isAuthenticated: false,
      isLoggingOut:    false,

      setAuth: (user, token, rememberMe) =>
        set({ user, token, rememberMe, isAuthenticated: true, isLoggingOut: false }),

      setLoggingOut: (v) => set({ isLoggingOut: v }),

      clearAuth: () => {
        // Clear ALL WMS keys from both storages
        const WMS_KEYS = ['wms-auth', 'wms-theme']
        WMS_KEYS.forEach(k => {
          localStorage.removeItem(k)
          sessionStorage.removeItem(k)
        })
        // Clear any auth cookies
        document.cookie.split(';').forEach(c => {
          document.cookie = c.trim().split('=')[0] +
            '=;expires=Thu, 01 Jan 1970 00:00:00 UTC;path=/'
        })
        set({
          user:            null,
          token:           null,
          rememberMe:      false,
          isAuthenticated: false,
          isLoggingOut:    false,
        })
      },
    }),
    {
      name:    'wms-auth',
      storage: createJSONStorage(() => conditionalStorage),
      partialize: (s) => ({
        user:            s.user,
        token:           s.token,
        rememberMe:      s.rememberMe,
        isAuthenticated: s.isAuthenticated,
      }),
    }
  )
)

// ── JWT expiry helper (no external lib needed) ────────────────────────────────
export function getTokenExpiryMs(token: string): number | null {
  try {
    const payload = JSON.parse(atob(token.split('.')[1]))
    return typeof payload.exp === 'number' ? payload.exp * 1000 : null
  } catch {
    return null
  }
}

export function isTokenExpired(token: string): boolean {
  const expiry = getTokenExpiryMs(token)
  return expiry !== null && Date.now() >= expiry
}
