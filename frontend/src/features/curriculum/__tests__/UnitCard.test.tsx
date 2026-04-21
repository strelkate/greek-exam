import { describe, expect, it } from 'vitest'
import { render, screen } from '@testing-library/react'
import { MemoryRouter } from 'react-router-dom'
import { UnitCard } from '../components/UnitCard'

const unit = {
  id: 1,
  title: 'Покупки — Αγορές',
  order_index: 1,
  exercises_total: 6,
  exercises_completed: 3,
  mini_test_passed: false,
  unit_completed: false,
}

describe('UnitCard', () => {
  it('renders unit title', () => {
    render(
      <MemoryRouter>
        <UnitCard unit={unit} />
      </MemoryRouter>,
    )
    expect(screen.getByText('Покупки — Αγορές')).toBeInTheDocument()
  })

  it('shows progress', () => {
    render(
      <MemoryRouter>
        <UnitCard unit={unit} />
      </MemoryRouter>,
    )
    expect(screen.getByText('3 / 6')).toBeInTheDocument()
  })

  it('shows checkmark when unit_completed=true', () => {
    render(
      <MemoryRouter>
        <UnitCard unit={{ ...unit, unit_completed: true }} />
      </MemoryRouter>,
    )
    expect(screen.getByLabelText('завершён')).toBeInTheDocument()
  })

  it('links to /units/:id', () => {
    render(
      <MemoryRouter>
        <UnitCard unit={unit} />
      </MemoryRouter>,
    )
    expect(screen.getByRole('link')).toHaveAttribute('href', '/units/1')
  })
})
