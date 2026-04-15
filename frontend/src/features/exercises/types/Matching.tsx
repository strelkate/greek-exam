import { useState } from 'react'

interface MatchingPair { left: string; right: string }
interface MatchingContent { pairs: MatchingPair[] }
interface MatchingProps { content: MatchingContent; onAnswer: (isCorrect: boolean) => void }

export function Matching({ content, onAnswer }: MatchingProps) {
  const [selection, setSelection] = useState<{ leftIndex: number | null; rightIndex: number | null }>({ leftIndex: null, rightIndex: null })
  const [matched, setMatched] = useState<Map<number, number>>(new Map())
  const [incorrect, setIncorrect] = useState<Set<number>>(new Set())
  const [submitted, setSubmitted] = useState(false)

  const shuffledRight = useState(() =>
    [...content.pairs.map((_, i) => i)].sort(() => Math.random() - 0.5)
  )[0]

  const handleLeft = (index: number) => {
    if (submitted || matched.has(index)) return
    setSelection(s => ({ ...s, leftIndex: index }))
  }

  const handleRight = (rightIdx: number) => {
    if (submitted) return
    const leftIdx = selection.leftIndex
    if (leftIdx === null) return
    if (content.pairs[leftIdx].right === content.pairs[shuffledRight[rightIdx]].right) {
      const newMatched = new Map(matched)
      newMatched.set(leftIdx, shuffledRight[rightIdx])
      setMatched(newMatched)
      setSelection({ leftIndex: null, rightIndex: null })
      if (newMatched.size === content.pairs.length) {
        setSubmitted(true)
        onAnswer(true)
      }
    } else {
      setIncorrect(new Set([leftIdx]))
      setTimeout(() => {
        setIncorrect(new Set())
        setSelection({ leftIndex: null, rightIndex: null })
      }, 800)
    }
  }

  const getLeftClass = (index: number) => {
    if (matched.has(index)) return 'match-item match-item--matched'
    if (incorrect.has(index)) return 'match-item match-item--incorrect'
    if (selection.leftIndex === index) return 'match-item match-item--selected'
    return 'match-item'
  }

  const getRightClass = (rightIdx: number) => {
    const originalIdx = shuffledRight[rightIdx]
    const isMatched = [...matched.values()].includes(originalIdx)
    return isMatched ? 'match-item match-item--matched' : 'match-item'
  }

  return (
    <div className="matching">
      <div className="matching__columns">
        <div className="matching__col">
          {content.pairs.map((pair, i) => (
            <button key={i} className={getLeftClass(i)} onClick={() => handleLeft(i)} disabled={submitted || matched.has(i)}>
              {pair.left}
            </button>
          ))}
        </div>
        <div className="matching__col">
          {shuffledRight.map((originalIdx, i) => (
            <button key={i} className={getRightClass(i)} onClick={() => handleRight(i)} disabled={submitted || [...matched.values()].includes(originalIdx)}>
              {content.pairs[originalIdx].right}
            </button>
          ))}
        </div>
      </div>
    </div>
  )
}
