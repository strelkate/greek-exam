import { render, screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { ExerciseShell } from '../ExerciseShell'

describe('ExerciseShell', () => {
  const defaultProps = {
    current: 2,
    total: 5,
    instruction: 'Выберите правильный ответ',
    audioPath: null,
    canSubmit: false,
    onSubmit: vi.fn(),
    children: <div>exercise content</div>,
  }

  it('renders progress as X / N', () => {
    render(<ExerciseShell {...defaultProps} />)
    expect(screen.getByText('2 / 5')).toBeInTheDocument()
  })

  it('renders instruction text', () => {
    render(<ExerciseShell {...defaultProps} />)
    expect(screen.getByText('Выберите правильный ответ')).toBeInTheDocument()
  })

  it('renders children', () => {
    render(<ExerciseShell {...defaultProps} />)
    expect(screen.getByText('exercise content')).toBeInTheDocument()
  })

  it('submit button is disabled when canSubmit=false', () => {
    render(<ExerciseShell {...defaultProps} canSubmit={false} />)
    expect(screen.getByRole('button', { name: /проверить/i })).toBeDisabled()
  })

  it('submit button is enabled when canSubmit=true', () => {
    render(<ExerciseShell {...defaultProps} canSubmit={true} />)
    expect(screen.getByRole('button', { name: /проверить/i })).not.toBeDisabled()
  })

  it('calls onSubmit when button clicked', async () => {
    const onSubmit = vi.fn()
    render(<ExerciseShell {...defaultProps} canSubmit={true} onSubmit={onSubmit} />)
    await userEvent.click(screen.getByRole('button', { name: /проверить/i }))
    expect(onSubmit).toHaveBeenCalledTimes(1)
  })

  it('shows audio button when audioPath provided', () => {
    render(<ExerciseShell {...defaultProps} audioPath="/audio/test.mp3" />)
    expect(screen.getByRole('button', { name: /аудио/i })).toBeInTheDocument()
  })

  it('hides audio button when audioPath is null', () => {
    render(<ExerciseShell {...defaultProps} audioPath={null} />)
    expect(screen.queryByRole('button', { name: /аудио/i })).not.toBeInTheDocument()
  })
})
