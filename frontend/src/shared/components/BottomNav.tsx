import { NavLink, useLocation } from 'react-router-dom'
import styles from './BottomNav.module.css'

const HIDDEN_ROUTES = ['/placement', '/exercise', '/mini-test']

export function BottomNav() {
  const { pathname } = useLocation()
  const isHidden = HIDDEN_ROUTES.some(r => pathname.includes(r))
  if (isHidden) return null

  return (
    <nav className={styles.nav}>
      <NavLink to="/levels" className={({ isActive }) => [styles.tab, isActive ? styles.active : ''].join(' ')}>
        <span className={styles.icon}>📚</span>
        <span className={styles.label}>Учёба</span>
      </NavLink>
      <NavLink to="/vocabulary" className={({ isActive }) => [styles.tab, isActive ? styles.active : ''].join(' ')}>
        <span className={styles.icon}>🗂</span>
        <span className={styles.label}>Словарь</span>
      </NavLink>
    </nav>
  )
}
