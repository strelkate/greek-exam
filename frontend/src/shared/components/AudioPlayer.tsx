import { useCallback, useRef, useState } from 'react'
import styles from './AudioPlayer.module.css'

interface AudioPlayerProps {
  src: string
  autoPlay?: boolean
  ariaLabel?: string
  className?: string
}

export function AudioPlayer({ src, autoPlay = false, ariaLabel = 'Слушать', className }: AudioPlayerProps) {
  const audioRef = useRef<HTMLAudioElement | null>(null)
  const [isPlaying, setIsPlaying] = useState(false)

  const play = useCallback(() => {
    if (!audioRef.current) {
      audioRef.current = new Audio(src)
      audioRef.current.onended = () => setIsPlaying(false)
    }
    audioRef.current.currentTime = 0
    audioRef.current.play()
    setIsPlaying(true)
  }, [src])

  const refCallback = useCallback((el: HTMLButtonElement | null) => {
    if (el && autoPlay) {
      setTimeout(play, 300)
    }
  }, [autoPlay, play])

  return (
    <button
      ref={refCallback}
      className={[styles.playBtn, isPlaying ? styles.playing : '', className ?? ''].join(' ')}
      onClick={play}
      aria-label={ariaLabel}
      type="button"
    >
      <span className={styles.icon}>{isPlaying ? '⏸' : '🔊'}</span>
    </button>
  )
}
