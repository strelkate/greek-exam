import type { ButtonHTMLAttributes, ReactNode } from 'react'
import styles from './Button.module.css'

interface ButtonProps extends ButtonHTMLAttributes<HTMLButtonElement> {
  children: ReactNode
  variant?: 'primary' | 'secondary' | 'ghost'
  fullWidth?: boolean
}

export function Button({ children, variant = 'primary', fullWidth, className, ...props }: ButtonProps) {
  return (
    <button
      className={[
        styles.btn,
        styles[`btn-${variant}`],
        fullWidth ? styles['btn-full'] : '',
        className ?? '',
      ].join(' ')}
      {...props}
    >
      {children}
    </button>
  )
}
