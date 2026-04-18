import { NavLink, useLocation } from 'react-router-dom'
import styles from './BottomNav.module.css'

export function BottomNav() {
  const { pathname } = useLocation()
  const isHidden =
    pathname.includes('/exercise') ||
    pathname.includes('/mini-test') ||
    pathname.includes('/vocabulary/review') ||
    pathname.endsWith('/words')
  if (isHidden) return null

  return (
    <nav className={styles.nav}>
      <NavLink to="/levels" className={({ isActive }) => [styles.tab, isActive ? styles.active : ''].join(' ')}>
        <img src="/icons/learn.svg" alt="" width={28} height={28} />
        <span className={styles.label}>Учёба</span>
      </NavLink>
      <NavLink to="/vocabulary" className={({ isActive }) => [styles.tab, isActive ? styles.active : ''].join(' ')}>
        <img src="/icons/book.svg" alt="" width={28} height={28} />
        <span className={styles.label}>Словарь</span>
      </NavLink>
    </nav>
  )
}
