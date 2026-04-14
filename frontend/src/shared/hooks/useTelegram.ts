// frontend/src/shared/hooks/useTelegram.ts
import WebApp from '@twa-dev/sdk'

export interface TelegramUser {
  id: number
  firstName: string
  languageCode?: string
}

export function useTelegram() {
  // In dev mode without Telegram — use mock
  const isDev = import.meta.env.DEV && !WebApp.initData

  const user: TelegramUser = isDev
    ? { id: 0, firstName: 'Dev User', languageCode: 'ru' }
    : {
        id: WebApp.initDataUnsafe?.user?.id ?? 0,
        firstName: WebApp.initDataUnsafe?.user?.first_name ?? '',
        languageCode: WebApp.initDataUnsafe?.user?.language_code,
      }

  const initData = isDev ? 'dev_mock_init_data' : WebApp.initData

  return {
    user,
    initData,
    ready: () => WebApp.ready(),
    expand: () => WebApp.expand(),
    backButton: {
      show: () => WebApp.BackButton.show(),
      hide: () => WebApp.BackButton.hide(),
      onClick: (fn: () => void) => WebApp.BackButton.onClick(fn),
      offClick: (fn: () => void) => WebApp.BackButton.offClick(fn),
    },
    haptic: {
      impact: (style: 'light' | 'medium' | 'heavy' = 'light') =>
        WebApp.HapticFeedback.impactOccurred(style),
      notification: (type: 'success' | 'error' | 'warning') =>
        WebApp.HapticFeedback.notificationOccurred(type),
    },
  }
}
