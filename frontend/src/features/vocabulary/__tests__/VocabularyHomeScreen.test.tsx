import { describe, expect, it, vi } from 'vitest'
import { render, screen, waitFor } from '@testing-library/react'
import { MemoryRouter } from 'react-router-dom'
import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { VocabularyHomeScreen } from '../VocabularyHomeScreen'

vi.mock('../../../shared/api/endpoints', () => ({
  api: {
    getVocabStats: vi.fn().mockResolvedValue({
      total_cards: 45,
      learned_count: 20,
      due_today: 7,
      new_count: 5,
    }),
    getDueCards: vi.fn().mockResolvedValue({
      due_count: 7,
      cards: [
        {
          id: 1,
          word_gr: 'το σπίτι',
          word_ru: 'дом',
          audio_path: null,
          status: 'learning',
          next_review_at: '2026-04-14',
        },
      ],
    }),
  },
}))

const createWrapper = () => {
  const queryClient = new QueryClient({ defaultOptions: { queries: { retry: false } } })
  return ({ children }: { children: React.ReactNode }) => (
    <QueryClientProvider client={queryClient}>
      <MemoryRouter>{children}</MemoryRouter>
    </QueryClientProvider>
  )
}

describe('VocabularyHomeScreen', () => {
  it('renders stats after load', async () => {
    render(<VocabularyHomeScreen />, { wrapper: createWrapper() })
    await waitFor(() => {
      expect(screen.getByText('45')).toBeInTheDocument()
      expect(screen.getByText('20')).toBeInTheDocument()
    })
  })

  it('shows due badge with count', async () => {
    render(<VocabularyHomeScreen />, { wrapper: createWrapper() })
    await waitFor(() => {
      expect(screen.getByText('7')).toBeInTheDocument()
    })
  })

  it('shows review button when due_today > 0', async () => {
    render(<VocabularyHomeScreen />, { wrapper: createWrapper() })
    await waitFor(() => {
      expect(screen.getByRole('button', { name: /επανάληψη|повторить/i })).toBeInTheDocument()
    })
  })
})
