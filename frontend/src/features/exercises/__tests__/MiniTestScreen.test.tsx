import { describe, expect, it, vi } from 'vitest'
import { render, screen, waitFor } from '@testing-library/react'
import { MemoryRouter, Route, Routes } from 'react-router-dom'
import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { MiniTestScreen } from '../MiniTestScreen'

vi.mock('../../../shared/api/endpoints', () => ({
  api: {
    getMiniTest: vi.fn().mockResolvedValue({
      questions: [
        {
          id: 1,
          type: 'true_false',
          content: { statement: 'Η Αθήνα είναι πρωτεύουσα.', is_true: true },
        },
        {
          id: 2,
          type: 'multiple_choice',
          content: { question: 'Τι σημαίνει;', options: ['A', 'B', 'C', 'D'], correct_index: 0 },
        },
      ],
    }),
    completeMiniTest: vi
      .fn()
      .mockResolvedValue({ unit_completed: true, xp_earned: 25, cards_added_to_vocab: 5 }),
  },
}))

const createWrapper = () => {
  const queryClient = new QueryClient({ defaultOptions: { queries: { retry: false } } })
  return ({ children }: { children: React.ReactNode }) => (
    <QueryClientProvider client={queryClient}>
      <MemoryRouter initialEntries={['/units/1/mini-test']}>
        <Routes>
          <Route path="/units/:unitId/mini-test" element={children} />
          <Route path="/units/:unitId/result" element={<div>result screen</div>} />
        </Routes>
      </MemoryRouter>
    </QueryClientProvider>
  )
}

describe('MiniTestScreen', () => {
  it('shows loading state initially', () => {
    render(<MiniTestScreen />, { wrapper: createWrapper() })
    expect(screen.getByText(/загрузка/i)).toBeInTheDocument()
  })

  it('renders first question after load', async () => {
    render(<MiniTestScreen />, { wrapper: createWrapper() })
    await waitFor(() => {
      expect(screen.getByText(/πρωτεύουσα/)).toBeInTheDocument()
    })
  })
})
