import { describe, expect, it, vi } from 'vitest'
import { render, screen, waitFor } from '@testing-library/react'
import { MemoryRouter } from 'react-router-dom'
import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { LevelMapScreen } from '../LevelMapScreen'

vi.mock('../../../shared/api/endpoints', () => ({
  api: {
    getLevels: vi.fn().mockResolvedValue({
      levels: [{ level: 'A1', total_units: 6, completed_units: 2, progress_percent: 33 }],
    }),
    getUnits: vi.fn().mockResolvedValue({
      units: [
        {
          id: 1,
          title: 'Знакомство — Γνωριμία',
          order_index: 1,
          exercises_total: 6,
          exercises_completed: 6,
          mini_test_passed: true,
          unit_completed: true,
        },
        {
          id: 2,
          title: 'Семья — Οικογένεια',
          order_index: 2,
          exercises_total: 6,
          exercises_completed: 0,
          mini_test_passed: false,
          unit_completed: false,
        },
      ],
    }),
  },
}))

function wrapper({ children }: { children: React.ReactNode }) {
  const qc = new QueryClient({ defaultOptions: { queries: { retry: false } } })
  return (
    <QueryClientProvider client={qc}>
      <MemoryRouter>{children}</MemoryRouter>
    </QueryClientProvider>
  )
}

describe('LevelMapScreen', () => {
  it('shows level heading', async () => {
    render(<LevelMapScreen />, { wrapper })
    await waitFor(() => expect(screen.getByText(/A1/)).toBeInTheDocument())
  })

  it('shows units', async () => {
    render(<LevelMapScreen />, { wrapper })
    await waitFor(() => expect(screen.getByText('Знакомство — Γνωριμία')).toBeInTheDocument())
    expect(screen.getByText('Семья — Οικογένεια')).toBeInTheDocument()
  })
})
