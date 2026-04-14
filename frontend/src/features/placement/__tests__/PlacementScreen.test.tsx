import { describe, expect, it, vi } from 'vitest'
import { render, screen, waitFor } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { MemoryRouter } from 'react-router-dom'
import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { PlacementScreen } from '../PlacementScreen'

vi.mock('../../../shared/api/endpoints', () => ({
  api: {
    getPlacementQuestions: vi.fn().mockResolvedValue({
      questions: [
        {
          id: 1,
          type: 'multiple_choice',
          content: {
            question: 'Τι είναι αυτό;',
            options: [{ id: 'a', text: 'Σπίτι' }, { id: 'b', text: 'Αυτοκίνητο' }],
            correct_id: 'a',
          },
        },
      ],
    }),
    completePlacementTest: vi.fn().mockResolvedValue({
      placement_status: 'failed',
      a1_skipped: false,
      message: 'Начинаете с A1.',
    }),
  },
}))

const mockNavigate = vi.fn()
vi.mock('react-router-dom', async () => {
  const actual = await vi.importActual('react-router-dom')
  return { ...actual, useNavigate: () => mockNavigate }
})

function wrapper({ children }: { children: React.ReactNode }) {
  const qc = new QueryClient({ defaultOptions: { queries: { retry: false } } })
  return <QueryClientProvider client={qc}><MemoryRouter>{children}</MemoryRouter></QueryClientProvider>
}

describe('PlacementScreen', () => {
  it('shows skip button', async () => {
    render(<PlacementScreen />, { wrapper })
    await waitFor(() => expect(screen.getByText(/пропустить/i)).toBeInTheDocument())
  })

  it('skip redirects to /levels', async () => {
    render(<PlacementScreen />, { wrapper })
    await waitFor(() => screen.getByText(/пропустить/i))
    await userEvent.click(screen.getByText(/пропустить/i))
    await waitFor(() => expect(mockNavigate).toHaveBeenCalledWith('/levels', expect.anything()))
  })
})
