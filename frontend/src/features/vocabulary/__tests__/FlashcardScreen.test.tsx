import { render, screen, waitFor } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { MemoryRouter } from 'react-router-dom'
import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { FlashcardScreen } from '../FlashcardScreen'
import { vi } from 'vitest'

vi.mock('../../../shared/api/endpoints', () => ({
  api: {
    getDueCards: vi.fn().mockResolvedValue({
      due_count: 2,
      cards: [
        { id: 1, word_gr: 'το σπίτι', word_ru: 'дом', audio_path: null, status: 'learning', next_review_at: '2026-04-14' },
        { id: 2, word_gr: 'η θάλασσα', word_ru: 'море', audio_path: null, status: 'new', next_review_at: '2026-04-14' },
      ],
    }),
    reviewCard: vi.fn().mockResolvedValue({
      card_id: 1,
      new_status: 'learned',
      next_review_at: '2026-04-21',
      interval_days: 7,
      xp_earned: 5,
    }),
  },
}))

const mockCards = [
  { id: 1, word_gr: 'το σπίτι', word_ru: 'дом', audio_path: null, status: 'learning', next_review_at: '2026-04-14' },
  { id: 2, word_gr: 'η θάλασσα', word_ru: 'море', audio_path: null, status: 'new', next_review_at: '2026-04-14' },
]

const createWrapper = () => {
  const queryClient = new QueryClient({ defaultOptions: { queries: { retry: false } } })
  return ({ children }: { children: React.ReactNode }) => (
    <QueryClientProvider client={queryClient}>
      <MemoryRouter>{children}</MemoryRouter>
    </QueryClientProvider>
  )
}

describe('FlashcardScreen', () => {
  it('shows front of card (greek word) after load', async () => {
    render(<FlashcardScreen />, { wrapper: createWrapper() })
    await waitFor(() => {
      expect(screen.getByText('το σπίτι')).toBeInTheDocument()
    })
  })

  it('hides translation initially', async () => {
    render(<FlashcardScreen />, { wrapper: createWrapper() })
    await waitFor(() => screen.getByText('το σπίτι'))
    expect(screen.queryByText('дом')).not.toBeInTheDocument()
  })

  it('shows translation after clicking Показать', async () => {
    render(<FlashcardScreen />, { wrapper: createWrapper() })
    await waitFor(() => screen.getByText('το σπίτι'))
    await userEvent.click(screen.getByRole('button', { name: /εμφάνιση|показать/i }))
    expect(screen.getByText('дом')).toBeInTheDocument()
  })

  it('shows Знал/Не знал buttons after flipping', async () => {
    render(<FlashcardScreen />, { wrapper: createWrapper() })
    await waitFor(() => screen.getByText('το σπίτι'))
    await userEvent.click(screen.getByRole('button', { name: /εμφάνιση|показать/i }))
    // Both rating buttons are present; use getAllByRole to handle overlapping regex
    const ratingBtns = screen.getAllByRole('button', { name: /ήξερα|знал/i })
    expect(ratingBtns.length).toBeGreaterThanOrEqual(1)
    expect(screen.getAllByRole('button', { name: /δεν ήξερα|не знал/i }).length).toBeGreaterThanOrEqual(1)
  })

  it('advances to next card after rating', async () => {
    render(<FlashcardScreen />, { wrapper: createWrapper() })
    await waitFor(() => screen.getByText('το σπίτι'))
    await userEvent.click(screen.getByRole('button', { name: /εμφάνιση|показать/i }))
    // Click the "knew it" button (last in the rating pair = yes)
    const ratingBtns = screen.getAllByRole('button', { name: /ήξερα|знал/i })
    await userEvent.click(ratingBtns[ratingBtns.length - 1])
    await waitFor(() => {
      expect(screen.getByText('η θάλασσα')).toBeInTheDocument()
    })
  })

  it('shows completion screen after last card', async () => {
    render(<FlashcardScreen />, { wrapper: createWrapper() })
    // Card 1
    await waitFor(() => screen.getByText('το σπίτι'))
    await userEvent.click(screen.getByRole('button', { name: /εμφάνιση|показать/i }))
    const btns1 = screen.getAllByRole('button', { name: /ήξερα|знал/i })
    await userEvent.click(btns1[btns1.length - 1])
    // Card 2
    await waitFor(() => screen.getByText('η θάλασσα'))
    await userEvent.click(screen.getByRole('button', { name: /εμφάνιση|показать/i }))
    const btns2 = screen.getAllByRole('button', { name: /ήξερα|знал/i })
    await userEvent.click(btns2[btns2.length - 1])
    // Done
    await waitFor(() => {
      expect(screen.getByText(/τέλος|готово|завершено/i)).toBeInTheDocument()
    })
  })
})
