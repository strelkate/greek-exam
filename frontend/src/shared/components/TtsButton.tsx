import { useState, useCallback } from 'react'

interface TtsButtonProps {
  text: string
  className?: string
  size?: number
}

export function TtsButton({ text, className = 'exercise-shell__tts', size = 52 }: TtsButtonProps) {
  const [speaking, setSpeaking] = useState(false)
  const speak = useCallback(() => {
    window.speechSynthesis.cancel()
    const utt = new SpeechSynthesisUtterance(text)
    utt.lang = 'el-GR'
    utt.onstart = () => setSpeaking(true)
    utt.onend = () => setSpeaking(false)
    utt.onerror = () => setSpeaking(false)
    window.speechSynthesis.speak(utt)
  }, [text])
  return (
    <button className={className} onClick={speak} aria-label="Произнести" type="button">
      <img
        src="/icons/headphones.svg"
        alt=""
        width={size}
        height={size}
        style={{ opacity: speaking ? 0.5 : 1, transition: 'opacity 0.2s' }}
      />
    </button>
  )
}
