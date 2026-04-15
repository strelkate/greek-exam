import { render, screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { TrueFalse } from '../types/TrueFalse'

const content = {
  statement: 'Η Αθήνα είναι η πρωτεύουσα.',
  is_true: true,
  explanation: 'Σωστά.',
}

describe('TrueFalse', () => {
  it('renders statement text', () => {
    render(<TrueFalse content={content} onAnswer={vi.fn()} />)
    expect(screen.getByText(content.statement)).toBeInTheDocument()
  })

  it('renders Σωστό and Λάθος buttons', () => {
    render(<TrueFalse content={content} onAnswer={vi.fn()} />)
    expect(screen.getByRole('button', { name: /σωστό/i })).toBeInTheDocument()
    expect(screen.getByRole('button', { name: /λάθος/i })).toBeInTheDocument()
  })

  it('calls onAnswer(true) when Σωστό clicked', async () => {
    const onAnswer = vi.fn()
    render(<TrueFalse content={content} onAnswer={onAnswer} />)
    await userEvent.click(screen.getByRole('button', { name: /σωστό/i }))
    expect(onAnswer).toHaveBeenCalledWith(true)
  })

  it('calls onAnswer(false) when Λάθος clicked', async () => {
    const onAnswer = vi.fn()
    render(<TrueFalse content={content} onAnswer={onAnswer} />)
    await userEvent.click(screen.getByRole('button', { name: /λάθος/i }))
    expect(onAnswer).toHaveBeenCalledWith(false)
  })

  it('shows correct/incorrect feedback after answer', async () => {
    render(<TrueFalse content={content} onAnswer={vi.fn()} />)
    await userEvent.click(screen.getByRole('button', { name: /σωστό/i }))
    expect(screen.getByText(/σωστά/i)).toBeInTheDocument()
  })

  it('disables buttons after selection', async () => {
    render(<TrueFalse content={content} onAnswer={vi.fn()} />)
    await userEvent.click(screen.getByRole('button', { name: /σωστό/i }))
    expect(screen.getByRole('button', { name: /σωστό/i })).toBeDisabled()
    expect(screen.getByRole('button', { name: /λάθος/i })).toBeDisabled()
  })
})
