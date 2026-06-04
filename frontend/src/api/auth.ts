import api from './client'

export interface AuthUser {
  id:        number
  user_name: string
  email:     string
  role:      string
  team:      string
}

export interface LoginPayload {
  username:    string
  password:    string
  remember_me: boolean
}

export interface LoginResponse {
  access_token: string
  token_type:   string
  user:         AuthUser
}

export const authApi = {
  login: (payload: LoginPayload) =>
    api.post<LoginResponse>('/auth/login', payload).then(r => r.data),

  me: () =>
    api.get<AuthUser>('/auth/me').then(r => r.data),

  logout: () =>
    api.post('/auth/logout').catch(() => null),

  forgotPassword: (email: string) =>
    api.post<{ message: string }>('/auth/forgot-password', { email }).then(r => r.data),
}
