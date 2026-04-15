import { useQuery } from '@tanstack/react-query'
import { api } from '../../shared/api/endpoints'

export function useMiniTestQuery(unitId: number) {
  return useQuery({
    queryKey: ['mini-test', unitId],
    queryFn: () => api.getMiniTest(unitId),
    enabled: Boolean(unitId),
  })
}
