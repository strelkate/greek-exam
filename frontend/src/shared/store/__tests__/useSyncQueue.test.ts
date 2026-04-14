// frontend/src/shared/store/__tests__/useSyncQueue.test.ts
import { beforeEach, describe, expect, it } from 'vitest'
import { act, renderHook } from '@testing-library/react'
import { useSyncQueue } from '../useSyncQueue'

beforeEach(() => {
  useSyncQueue.setState({ queue: [] })
})

describe('useSyncQueue', () => {
  it('starts with empty queue', () => {
    const { result } = renderHook(() => useSyncQueue())
    expect(result.current.queue).toHaveLength(0)
  })

  it('enqueue adds event to queue', () => {
    const { result } = renderHook(() => useSyncQueue())
    const event = { exercise_id: 1, score: 1, total: 1, completed_at: '2026-04-14T10:00:00Z' }
    act(() => result.current.enqueue(event))
    expect(result.current.queue).toHaveLength(1)
    expect(result.current.queue[0]).toEqual(event)
  })

  it('clear empties the queue', () => {
    const { result } = renderHook(() => useSyncQueue())
    act(() => {
      result.current.enqueue({ exercise_id: 1, score: 1, total: 1, completed_at: '2026-04-14T10:00:00Z' })
      result.current.clear()
    })
    expect(result.current.queue).toHaveLength(0)
  })
})
