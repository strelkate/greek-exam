// frontend/src/shared/api/client.ts
import axios from 'axios'

const BASE_URL = import.meta.env.VITE_API_URL ?? ''

export const apiClient = axios.create({
  baseURL: BASE_URL,
  headers: { 'Content-Type': 'application/json' },
})

// Inject X-Telegram-Init-Data before each request
// initData is set once at app startup
let _initData = ''

export function setInitData(initData: string) {
  _initData = initData
}

apiClient.interceptors.request.use((config) => {
  if (_initData) {
    config.headers['X-Telegram-Init-Data'] = _initData
  }
  return config
})
