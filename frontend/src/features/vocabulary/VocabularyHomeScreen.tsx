import { useNavigate } from 'react-router-dom'
import { useVocabStatsQuery, useDueCardsQuery } from './useVocabularyQuery'
import { Button } from '../../shared/components/Button'

export function VocabularyHomeScreen() {
  const navigate = useNavigate()
  const statsQuery = useVocabStatsQuery()
  const dueQuery = useDueCardsQuery()

  const stats = statsQuery.data
  const dueCount = dueQuery.data?.due_count ?? 0
  const notDue = stats ? stats.total_cards - stats.due_today : 0
  const learnedPercent = stats
    ? Math.round((notDue / Math.max(stats.total_cards, 1)) * 100)
    : 0

  return (
    <div className="vocab-home">
      <h1 className="vocab-home__title">Словарь</h1>
      <div className="vocab-home__stats">
        <div className="vocab-stat">
          <span className="vocab-stat__value">{stats?.total_cards ?? '—'}</span>
          <span className="vocab-stat__label">ВСЕГО</span>
        </div>
        <div className="vocab-stat">
          <span className="vocab-stat__value">{stats ? stats.learned_count : '—'}</span>
          <span className="vocab-stat__label">ИЗУЧЕНО</span>
        </div>
        <div className="vocab-stat">
          <span className="vocab-stat__value">{learnedPercent}%</span>
          <span className="vocab-stat__label">ПРОГРЕСС</span>
        </div>
      </div>
      <div className="vocab-home__review-card">
        <div className="vocab-home__review-info">
          <span className="vocab-home__due-badge">{dueCount}</span>
          <div>
            <p className="vocab-home__review-title">Повторение сегодня</p>
            <p className="vocab-home__review-subtitle">
              {dueCount === 0 ? 'Всё выучено!' : `${dueCount} карточек ждут`}
            </p>
          </div>
        </div>
        <Button
          onClick={() => navigate('/vocabulary/review')}
          variant="primary"
          disabled={dueCount === 0}
          fullWidth
        >
          Повторить
        </Button>
      </div>
      {(stats?.new_count ?? 0) > 0 && (
        <p className="vocab-home__new-hint">
          +{stats!.new_count} новых слов из последних юнитов
        </p>
      )}
    </div>
  )
}
