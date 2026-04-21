import { useLocation, useNavigate, useParams } from 'react-router-dom'
import { Button } from '../../shared/components/Button'
import type { MiniTestCompleteResponse } from '../../shared/api/types'

export function UnitResultScreen() {
  const { unitId } = useParams<{ unitId: string }>()
  const navigate = useNavigate()
  const location = useLocation()
  const result = location.state as MiniTestCompleteResponse | null

  const xp = result?.xp_earned ?? 0
  const cardsAdded = result?.cards_added_to_vocab ?? 0
  const isMiniTestResult = result?.unit_completed

  return (
    <div className="unit-result">
      <div className="unit-result__trophy">🏆</div>
      <h1 className="unit-result__title">Отлично!</h1>
      <p className="unit-result__subtitle">
        {isMiniTestResult ? 'Юнит завершён!' : 'Упражнения пройдены'}
      </p>
      <div className="unit-result__stats">
        <div className="unit-result__stat">
          <span className="unit-result__stat-value">+{xp}</span>
          <span className="unit-result__stat-label">XP</span>
        </div>
        {cardsAdded > 0 && (
          <div className="unit-result__stat">
            <span className="unit-result__stat-value">+{cardsAdded}</span>
            <span className="unit-result__stat-label">СЛОВ</span>
          </div>
        )}
      </div>
      {!isMiniTestResult && unitId && (
        <Button onClick={() => navigate(`/units/${unitId}/mini-test`)} variant="primary" fullWidth>
          Пройти мини-тест
        </Button>
      )}
      <Button
        onClick={() => navigate('/levels')}
        variant={isMiniTestResult ? 'primary' : 'ghost'}
        fullWidth
      >
        К уровням
      </Button>
    </div>
  )
}
