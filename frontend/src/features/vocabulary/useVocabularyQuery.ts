import { useQuery } from '@tanstack/react-query'
import { api } from '../../shared/api/endpoints'

export function useVocabStatsQuery() {
  return useQuery({
    queryKey: ['vocab-stats'],
    queryFn: () => api.getVocabStats(),
  })
}

export function useDueCardsQuery() {
  return useQuery({
    queryKey: ['due-cards'],
    queryFn: () => api.getDueCards(),
  })
}
