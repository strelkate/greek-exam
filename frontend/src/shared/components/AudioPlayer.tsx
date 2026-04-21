import { useCallback, useEffect, useRef, useState } from 'react'
import styles from './AudioPlayer.module.css'

const API_URL = import.meta.env.VITE_API_URL ?? ''

interface AudioPlayerProps {
  src: string
  autoPlay?: boolean
  ariaLabel?: string
  className?: string
}

export function AudioPlayer({
  src,
  autoPlay = false,
  ariaLabel = 'Слушать',
  className,
}: AudioPlayerProps) {
  const audioRef = useRef<HTMLAudioElement | null>(null)
  const [isPlaying, setIsPlaying] = useState(false)

  const fullSrc = src.startsWith('http') ? src : `${API_URL}${src}`

  useEffect(() => {
    if (audioRef.current) {
      audioRef.current.pause()
      audioRef.current = null
      setIsPlaying(false)
    }
  }, [fullSrc])

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

  const refCallback = useCallback(
    (el: HTMLButtonElement | null) => {
      if (el && autoPlay) {
        setTimeout(() => {
          const audio = getAudio()
          audio.play().catch(() => {})
          setIsPlaying(true)
        }, 300)
      }
    },
    [autoPlay, getAudio],
  )

  return (
    <button
      ref={refCallback}
      className={[styles.playBtn, isPlaying ? styles.playing : '', className ?? ''].join(' ')}
      onClick={toggle}
      aria-label={ariaLabel}
      type="button"
    >
      <img
        src="/icons/headphones.svg"
        alt=""
        width={52}
        height={52}
        style={{ opacity: isPlaying ? 0.5 : 1, transition: 'opacity 0.2s' }}
      />
    </button>
  )
}

interface SequentialAudioPlayerProps {
  srcs: string[]
  ariaLabel?: string
  className?: string
}

export function SequentialAudioPlayer({
  srcs,
  ariaLabel = 'Слушать',
  className,
}: SequentialAudioPlayerProps) {
  const [isPlaying, setIsPlaying] = useState(false)
  const currentAudioRef = useRef<HTMLAudioElement | null>(null)

  const stop = useCallback(() => {
    if (currentAudioRef.current) {
      currentAudioRef.current.pause()
      currentAudioRef.current.onended = null
      currentAudioRef.current.onerror = null
      currentAudioRef.current = null
    }
    setIsPlaying(false)
  }, [])

  const playFrom = useCallback((index: number, fullSrcs: string[]) => {
    if (index >= fullSrcs.length) {
      setIsPlaying(false)
      return
    }
    const audio = new Audio(fullSrcs[index])
    currentAudioRef.current = audio
    audio.onended = () => playFrom(index + 1, fullSrcs)
    audio.onerror = () => playFrom(index + 1, fullSrcs)
    audio.play().catch(() => playFrom(index + 1, fullSrcs))
  }, [])

  const toggle = useCallback(() => {
    if (isPlaying) {
      stop()
    } else {
      const fullSrcs = srcs.map((s) => (s.startsWith('http') ? s : `${API_URL}${s}`))
      setIsPlaying(true)
      playFrom(0, fullSrcs)
    }
  }, [isPlaying, srcs, stop, playFrom])

  return (
    <button
      className={[styles.playBtn, isPlaying ? styles.playing : '', className ?? ''].join(' ')}
      onClick={toggle}
      aria-label={ariaLabel}
      type="button"
    >
      <img
        src="/icons/headphones.svg"
        alt=""
        width={52}
        height={52}
        style={{ opacity: isPlaying ? 0.5 : 1, transition: 'opacity 0.2s' }}
      />
    </button>
  )
}
