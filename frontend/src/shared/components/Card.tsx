import type { HTMLAttributes, ReactNode } from 'react'
import styles from './Card.module.css'

interface CardProps extends HTMLAttributes<HTMLDivElement> {
  children: ReactNode
  elevated?: boolean
}

export function Card({ children, elevated, className, ...props }: CardProps) {
  return (
    <div
      className={[styles.card, elevated ? styles.elevated : '', className ?? ''].join(' ')}
      {...props}
    >
      {children}
    </div>
  )
}
