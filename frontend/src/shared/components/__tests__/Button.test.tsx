import { describe, expect, it, vi } from 'vitest'
import { render, screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { Button } from '../Button'

describe('Button', () => {
  it('renders text', () => {
    render(<Button>Проверить</Button>)
    expect(screen.getByRole('button', { name: 'Проверить' })).toBeInTheDocument()
  })

  it('calls onClick', async () => {
    const onClick = vi.fn()
    render(<Button onClick={onClick}>Далее</Button>)
    await userEvent.click(screen.getByRole('button'))
    expect(onClick).toHaveBeenCalledOnce()
  })

  it('disabled does not call onClick', async () => {
    const onClick = vi.fn()
    render(<Button onClick={onClick} disabled>Далее</Button>)
    await userEvent.click(screen.getByRole('button'))
    expect(onClick).not.toHaveBeenCalled()
  })

  it('variant=secondary applies btn-secondary class', () => {
    render(<Button variant="secondary">Пропустить</Button>)
    expect(screen.getByRole('button')).toHaveClass('btn-secondary')
  })
})
