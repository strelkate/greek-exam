import styles from './LandingScreen.module.css'

const BOT_USERNAME = import.meta.env.VITE_BOT_USERNAME ?? ''

export function LandingScreen() {
  const telegramUrl = BOT_USERNAME ? `https://t.me/${BOT_USERNAME}` : '#'

  return (
    <div className={styles.landing}>
      <div className={styles.content}>
        <div className={styles.logo}>🇬🇷</div>
        <h1 className={styles.title}>Μαθαίνω Ελληνικά</h1>
        <p className={styles.subtitle}>
          Приложение для изучения новогреческого языка с подготовкой к экзамену ΠΙΣΤΟΠΟΙΗΣΗ
          ΕΛΛΗΝΟΜΑΘΕΙΑΣ A2
        </p>
        <p className={styles.hint}>Доступно как Telegram Mini App</p>
        <a
          href={telegramUrl}
          target="_blank"
          rel="noopener noreferrer"
          className={styles.button}
        >
          Открыть в Telegram
        </a>
      </div>
    </div>
  )
}
