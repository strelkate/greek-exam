// frontend/src/shared/store/useSyncQueue.ts
import { create } from 'zustand'
import { persist } from 'zustand/middleware'
import type { ProgressEvent } from '../api/types'
import { api } from '../api/endpoints'

interface SyncQueueState {
  queue: ProgressEvent[]
  enqueue: (event: ProgressEvent) => void
  clear: () => void
  flush: () => Promise<void>
}

export const useSyncQueue = create<SyncQueueState>()(
  persist(
    (set, get) => ({
      queue: [],

      enqueue: (event) => set((s) => ({ queue: [...s.queue, event] })),

      clear: () => set({ queue: [] }),

      flush: async () => {
        const { queue, clear } = get()
        if (queue.length === 0) return
        try {
          await api.syncProgress(queue)
          clear()
        } catch {
          // Keep in queue, retry later
        }
      },
    }),
    { name: 'greek-sync-queue' }
  )
)

// Auto-flush when network comes back
if (typeof window !== 'undefined') {
  window.addEventListener('online', () => {
    useSyncQueue.getState().flush()
  })
}
