// frontend/src/shared/store/__tests__/useAppStore.test.ts
import { beforeEach, describe, expect, it } from 'vitest'
import { act, renderHook } from '@testing-library/react'
import { useAppStore } from '../useAppStore'

beforeEach(() => {
  useAppStore.setState({
    xp: 0,
    streak: 0,
    streakDate: null,
    showTranslations: true,
  })
})

describe('useAppStore', () => {
  it('initializes with default values', () => {
    const { result } = renderHook(() => useAppStore())
    expect(result.current.xp).toBe(0)
    expect(result.current.streak).toBe(0)
    expect(result.current.showTranslations).toBe(true)
  })

  it('addXp increases xp', () => {
    const { result } = renderHook(() => useAppStore())
    act(() => result.current.addXp(10))
    expect(result.current.xp).toBe(10)
    act(() => result.current.addXp(25))
    expect(result.current.xp).toBe(35)
  })

  it('setStreak updates streak and streakDate', () => {
    const { result } = renderHook(() => useAppStore())
    act(() => result.current.setStreak(5, '2026-04-14'))
    expect(result.current.streak).toBe(5)
    expect(result.current.streakDate).toBe('2026-04-14')
  })

  it('setShowTranslations toggles the setting', () => {
    const { result } = renderHook(() => useAppStore())
    act(() => result.current.setShowTranslations(false))
    expect(result.current.showTranslations).toBe(false)
  })
})
