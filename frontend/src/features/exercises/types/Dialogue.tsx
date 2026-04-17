import React, { useState } from 'react'

interface DialogueLine { id: number; speaker: string; text: string; audio_path?: string | null }
interface TableBlank { row: string; column: string; correct: string }
interface DialogueContent { dialogue_lines: DialogueLine[]; table_blanks: TableBlank[]; word_bank: string[]; dialogue_ru?: string }
interface DialogueProps { content: DialogueContent; onAnswer: (isCorrect: boolean) => void; submitted?: boolean }

export function Dialogue({ content, onAnswer, submitted = false }: DialogueProps) {
  const [fills, setFills] = useState<Record<number, string>>({})
  const [allFilled, setAllFilled] = useState(false)

  const handleWordSelect = (blankIndex: number, word: string) => {
    if (allFilled) return
    const newFills = { ...fills, [blankIndex]: word }
    setFills(newFills)
    const nowAllFilled = content.table_blanks.every((_, i) => newFills[i] !== undefined)
    if (nowAllFilled) {
      setAllFilled(true)
      const allCorrect = content.table_blanks.every((blank, i) => newFills[i] === blank.correct)
      onAnswer(allCorrect)
    }
  }

  const renderLine = (line: DialogueLine) => {
    const blanks = content.table_blanks.filter(b => b.row === line.speaker)
    if (blanks.length === 0) return <>{line.text}</>

    const parts = line.text.split('___')
    const result: React.ReactNode[] = []
    parts.forEach((part, i) => {
      result.push(part)
      if (i < blanks.length) {
        const blankIndex = content.table_blanks.indexOf(blanks[i])
        const filled = fills[blankIndex]
        const isCorrect = submitted && filled === blanks[i].correct
        const isWrong = submitted && filled !== undefined && filled !== blanks[i].correct
        result.push(
          <span
            key={i}
            className={`fill-blank__blank${isCorrect ? ' fill-blank__blank--correct' : isWrong ? ' fill-blank__blank--incorrect' : ''}`}
          >
            {filled ?? '___'}
          </span>
        )
      }
    })
    return <>{result}</>
  }

  return (
    <div className="dialogue">
      <div className="dialogue__lines">
        {content.dialogue_lines.map(line => (
          <div key={line.id} className={`dialogue__line dialogue__line--${line.speaker === 'Α' ? 'a' : 'b'}`}>
            <span className="dialogue__speaker">{line.speaker}</span>
            <p className="dialogue__text">{renderLine(line)}</p>
          </div>
        ))}
      </div>
      {content.table_blanks.length > 0 && (
        <div className="dialogue__fill-section">
          {content.table_blanks.map((blank, i) => (
            <div key={i} className="dialogue__blank-row">
              <div className="dialogue__word-bank">
                {content.word_bank.map(word => {
                  const isSelected = fills[i] === word
                  const isCorrect = submitted && word === blank.correct
                  const isWrong = submitted && isSelected && word !== blank.correct
                  return (
                    <button
                      key={word}
                      className={`fb-option ${isCorrect ? 'fb-option--correct' : ''} ${isWrong ? 'fb-option--incorrect' : ''} ${isSelected && !submitted ? 'fb-option--selected' : ''}`}
                      onClick={() => handleWordSelect(i, word)}
                      disabled={submitted}
                    >
                      {word}
                    </button>
                  )
                })}
              </div>
            </div>
          ))}
        </div>
      )}
      {submitted && content.dialogue_ru && (
        <p className="fill-blank__translation">{content.dialogue_ru}</p>
      )}
    </div>
  )
}
