import { useState } from 'react'

interface DialogueLine { id: number; speaker: string; text: string; audio_path?: string | null }
interface TableBlank { row: string; column: string; correct: string }
interface DialogueContent { dialogue_lines: DialogueLine[]; table_blanks: TableBlank[]; word_bank: string[] }
interface DialogueProps { content: DialogueContent; onAnswer: (isCorrect: boolean) => void }

export function Dialogue({ content, onAnswer }: DialogueProps) {
  const [fills, setFills] = useState<Record<number, string>>({})
  const [submitted, setSubmitted] = useState(false)

  const allFilled = content.table_blanks.every((_, i) => fills[i] !== undefined)

  const handleWordSelect = (blankIndex: number, word: string) => {
    if (submitted) return
    setFills(f => ({ ...f, [blankIndex]: word }))
  }

  const handleSubmit = () => {
    if (!allFilled || submitted) return
    setSubmitted(true)
    const allCorrect = content.table_blanks.every((blank, i) => fills[i] === blank.correct)
    onAnswer(allCorrect)
  }

  const renderLine = (line: DialogueLine) => {
    const blanks = content.table_blanks.filter(b => b.row === line.speaker)
    let text = line.text
    blanks.forEach((_, bi) => {
      const blankIndex = content.table_blanks.indexOf(blanks[bi])
      const filled = fills[blankIndex]
      text = text.replace('___', filled ? `[${filled}]` : '___')
    })
    return text
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
          <p className="dialogue__fill-label">Вставьте слово:</p>
          {content.table_blanks.map((blank, i) => (
            <div key={i} className="dialogue__blank-row">
              <span className="dialogue__blank-context">{blank.column} ({blank.row}):</span>
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
          {allFilled && !submitted && (
            <button className="tf-btn" style={{ marginTop: 12 }} onClick={handleSubmit}>
              Проверить
            </button>
          )}
        </div>
      )}
    </div>
  )
}
