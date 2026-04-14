import { describe, expect, it, vi } from 'vitest'
import { render, screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { PlacementQuestion } from '../components/PlacementQuestion'

const mcQuestion = {
  id: 1,
  type: 'multiple_choice' as const,
  content: {
    question: 'Τι είναι αυτό;',
    options: [
      { id: 'a', text: 'Σπίτι' },
      { id: 'b', text: 'Αυτοκίνητο' },
      { id: 'c', text: 'Σχολείο' },
    ],
    correct_id: 'a',
  },
}

describe('PlacementQuestion', () => {
  it('renders multiple_choice question', () => {
    render(<PlacementQuestion question={mcQuestion} onAnswer={vi.fn()} />)
    expect(screen.getByText('Τι είναι αυτό;')).toBeInTheDocument()
    expect(screen.getByText('Σπίτι')).toBeInTheDocument()
    expect(screen.getByText('Αυτοκίνητο')).toBeInTheDocument()
  })

  it('calls onAnswer(true) for correct answer', async () => {
    const onAnswer = vi.fn()
    render(<PlacementQuestion question={mcQuestion} onAnswer={onAnswer} />)
    await userEvent.click(screen.getByText('Σπίτι'))
    await userEvent.click(screen.getByRole('button', { name: /проверить/i }))
    // onAnswer called after 800ms delay
    await new Promise(r => setTimeout(r, 900))
    expect(onAnswer).toHaveBeenCalledWith(true)
  })

  it('calls onAnswer(false) for wrong answer', async () => {
    const onAnswer = vi.fn()
    render(<PlacementQuestion question={mcQuestion} onAnswer={onAnswer} />)
    await userEvent.click(screen.getByText('Αυτοκίνητο'))
    await userEvent.click(screen.getByRole('button', { name: /проверить/i }))
    await new Promise(r => setTimeout(r, 900))
    expect(onAnswer).toHaveBeenCalledWith(false)
  })
})
