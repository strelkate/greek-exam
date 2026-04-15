import { useQuery } from '@tanstack/react-query'
import { api } from '../../shared/api/endpoints'

export function useExerciseQuery(exerciseId: number) {
  return useQuery({
    queryKey: ['exercise', exerciseId],
    queryFn: () => api.getExercise(exerciseId),
    enabled: Boolean(exerciseId),
  })
}
