import { describe, expect, it } from 'vitest'
import { render } from '@testing-library/react'
import { ProgressBar } from '../ProgressBar'

describe('ProgressBar', () => {
  it('sets fill width based on value', () => {
    const { container } = render(<ProgressBar value={3} max={6} />)
    const fill = container.querySelector('[data-fill]') as HTMLElement
    expect(fill.style.width).toBe('50%')
  })

  it('does not exceed 100%', () => {
    const { container } = render(<ProgressBar value={10} max={6} />)
    const fill = container.querySelector('[data-fill]') as HTMLElement
    expect(fill.style.width).toBe('100%')
  })

  it('does not go below 0%', () => {
    const { container } = render(<ProgressBar value={-1} max={6} />)
    const fill = container.querySelector('[data-fill]') as HTMLElement
    expect(fill.style.width).toBe('0%')
  })
})
