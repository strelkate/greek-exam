import { describe, expect, it, vi } from 'vitest'
import { render, screen, waitFor } from '@testing-library/react'
import { MemoryRouter, Route, Routes } from 'react-router-dom'
import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { UnitDetailScreen } from '../UnitDetailScreen'

vi.mock('../../../shared/api/endpoints', () => ({
  api: {
    getUnitDetail: vi.fn().mockResolvedValue({
      id: 1,
      title: 'Покупки — Αγορές',
      level: 'A2',
      exercises: [
        { id: 10, type: 'true_false', order_index: 1, audio_paths: [], completed: false },
        { id: 11, type: 'multiple_choice', order_index: 2, audio_paths: [], completed: true },
      ],
      vocabulary_cards: [
        { id: 100, word_gr: 'το κατάστημα', word_ru: 'магазин', audio_path: null },
      ],
    }),
  },
}))

function wrapper({ children }: { children: React.ReactNode }) {
  const qc = new QueryClient({ defaultOptions: { queries: { retry: false } } })
  return (
    <QueryClientProvider client={qc}>
      <MemoryRouter initialEntries={['/units/1']}>
        <Routes>
          <Route path="/units/:unitId" element={children} />
        </Routes>
      </MemoryRouter>
    </QueryClientProvider>
  )
}

describe('UnitDetailScreen', () => {
  it('shows unit title', async () => {
    render(<UnitDetailScreen />, { wrapper })
    await waitFor(() => expect(screen.getByText('Покупки — Αγορές')).toBeInTheDocument())
  })

  it('shows exercise list', async () => {
    render(<UnitDetailScreen />, { wrapper })
    await waitFor(() => expect(screen.getAllByRole('link').length).toBeGreaterThan(0))
  })

  it('shows start/continue button', async () => {
    render(<UnitDetailScreen />, { wrapper })
    await waitFor(() => expect(screen.getByRole('button', { name: /начать|продолжить/i })).toBeInTheDocument())
  })
})
