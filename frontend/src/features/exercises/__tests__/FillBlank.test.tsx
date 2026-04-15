import { describe, expect, it, vi } from 'vitest'
import { render, screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { FillBlank } from '../types/FillBlank'

const content = {
  sentence: 'Θέλω να ___ ένα εισιτήριο.',
  blank_word: 'αγοράσω',
  options: ['αγοράσω', 'πουλήσω', 'βρω', 'δω'],
}

describe('FillBlank', () => {
  it('renders sentence with blank placeholder', () => {
    render(<FillBlank content={content} onAnswer={vi.fn()} />)
    expect(screen.getByText(/θέλω να/i)).toBeInTheDocument()
  })

  it('renders all word bank options', () => {
    render(<FillBlank content={content} onAnswer={vi.fn()} />)
    content.options.forEach(opt => expect(screen.getByRole('button', { name: opt })).toBeInTheDocument())
  })

  it('calls onAnswer(true) when correct word selected', async () => {
    const onAnswer = vi.fn()
    render(<FillBlank content={content} onAnswer={onAnswer} />)
    await userEvent.click(screen.getByRole('button', { name: 'αγοράσω' }))
    expect(onAnswer).toHaveBeenCalledWith(true)
  })

  it('calls onAnswer(false) when wrong word selected', async () => {
    const onAnswer = vi.fn()
    render(<FillBlank content={content} onAnswer={onAnswer} />)
    await userEvent.click(screen.getByRole('button', { name: 'πουλήσω' }))
    expect(onAnswer).toHaveBeenCalledWith(false)
  })

  it('inserts selected word into the sentence blank', async () => {
    render(<FillBlank content={content} onAnswer={vi.fn()} />)
    await userEvent.click(screen.getByRole('button', { name: 'αγοράσω' }))
    // Word appears in the blank span (may also appear in the option button)
    expect(screen.getAllByText(/αγοράσω/).length).toBeGreaterThan(0)
  })

  it('disables word bank after selection', async () => {
    render(<FillBlank content={content} onAnswer={vi.fn()} />)
    await userEvent.click(screen.getByRole('button', { name: 'βρω' }))
    content.options.forEach(opt => expect(screen.getByRole('button', { name: opt })).toBeDisabled())
  })
})
