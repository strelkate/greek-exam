import { useQuery } from '@tanstack/react-query'
import { api } from '../../shared/api/endpoints'

export function useLevelsQuery() {
  return useQuery({
    queryKey: ['levels'],
    queryFn: () => api.getLevels(),
  })
}

export function useUnitsQuery(level: string) {
  return useQuery({
    queryKey: ['units', level],
    queryFn: () => api.getUnits(level),
    enabled: Boolean(level),
  })
}

export function useUnitDetailQuery(unitId: number) {
  return useQuery({
    queryKey: ['unit', unitId],
    queryFn: () => api.getUnitDetail(unitId),
    enabled: Boolean(unitId),
  })
}
