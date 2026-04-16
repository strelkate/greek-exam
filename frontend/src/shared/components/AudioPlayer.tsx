import { useCallback, useRef, useState } from 'react'
import styles from './AudioPlayer.module.css'

const API_URL = import.meta.env.VITE_API_URL ?? ''

interface AudioPlayerProps {
  src: string
  autoPlay?: boolean
  ariaLabel?: string
  className?: string
}

export function AudioPlayer({ src, autoPlay = false, ariaLabel = 'Слушать', className }: AudioPlayerProps) {
  const audioRef = useRef<HTMLAudioElement | null>(null)
  const [isPlaying, setIsPlaying] = useState(false)

  const fullSrc = src.startsWith('http') ? src : `${API_URL}${src}`

  const getAudio = useCallback(() => {
    if (!audioRef.current) {
      audioRef.current = new Audio(fullSrc)
      audioRef.current.onended = () => setIsPlaying(false)
      audioRef.current.onerror = () => setIsPlaying(false)
    }
    return audioRef.current
  }, [fullSrc])

  const toggle = useCallback(() => {
    const audio = getAudio()
    if (isPlaying) {
      audio.pause()
      setIsPlaying(false)
    } else {
      audio.currentTime = 0
      audio.play().catch(() => setIsPlaying(false))
      setIsPlaying(true)
    }
  }, [getAudio, isPlaying])

  const refCallback = useCallback((el: HTMLButtonElement | null) => {
    if (el && autoPlay) {
      setTimeout(() => {
        const audio = getAudio()
        audio.play().catch(() => {})
        setIsPlaying(true)
      }, 300)
    }
  }, [autoPlay, getAudio])

  return (
    <button
      ref={refCallback}
      className={[styles.playBtn, isPlaying ? styles.playing : '', className ?? ''].join(' ')}
      onClick={toggle}
      aria-label={ariaLabel}
      type="button"
    >
      <span className={styles.icon}>{isPlaying ? '⏸' : '🔊'}</span>
    </button>
  )
}
