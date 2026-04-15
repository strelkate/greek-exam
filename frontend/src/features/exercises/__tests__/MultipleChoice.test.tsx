import { render, screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { MultipleChoice } from '../types/MultipleChoice'

const content = {
  question: 'Τι σημαίνει "καλημέρα";',
  options: ['Good morning', 'Good night', 'Goodbye', 'Hello'],
  correct_index: 0,
}

describe('MultipleChoice', () => {
  it('renders question text', () => {
    render(<MultipleChoice content={content} onAnswer={vi.fn()} />)
    expect(screen.getByText(/καλημέρα/)).toBeInTheDocument()
  })

  it('renders all 4 options', () => {
    render(<MultipleChoice content={content} onAnswer={vi.fn()} />)
    content.options.forEach(opt => expect(screen.getByText(opt)).toBeInTheDocument())
  })

  it('calls onAnswer(true) when correct option selected', async () => {
    const onAnswer = vi.fn()
    render(<MultipleChoice content={content} onAnswer={onAnswer} />)
    await userEvent.click(screen.getByText('Good morning'))
    expect(onAnswer).toHaveBeenCalledWith(true)
  })

  it('calls onAnswer(false) when wrong option selected', async () => {
    const onAnswer = vi.fn()
    render(<MultipleChoice content={content} onAnswer={onAnswer} />)
    await userEvent.click(screen.getByText('Good night'))
    expect(onAnswer).toHaveBeenCalledWith(false)
  })

  it('disables all options after selection', async () => {
    render(<MultipleChoice content={content} onAnswer={vi.fn()} />)
    await userEvent.click(screen.getByText('Goodbye'))
    content.options.forEach(opt => expect(screen.getByText(opt).closest('button')).toBeDisabled())
  })

  it('highlights correct option green after wrong answer', async () => {
    render(<MultipleChoice content={content} onAnswer={vi.fn()} />)
    await userEvent.click(screen.getByText('Good night'))
    expect(screen.getByText('Good morning').closest('button')).toHaveClass('mc-option--correct')
  })
})
