"use client"

import { useState, useEffect, useCallback } from "react"

interface UseCountdownOptions {
  initialSeconds: number
  onComplete?: () => void
}

export function useCountdown({ initialSeconds, onComplete }: UseCountdownOptions) {
  const [seconds, setSeconds] = useState(initialSeconds)
  const [isActive, setIsActive] = useState(false)

  const start = useCallback((seconds?: number) => {
    setSeconds(seconds || initialSeconds)
    setIsActive(true)
  }, [initialSeconds])

  const stop = useCallback(() => {
    setIsActive(false)
  }, [])

  const reset = useCallback((seconds?: number) => {
    setSeconds(seconds || initialSeconds)
    setIsActive(false)
  }, [initialSeconds])

  useEffect(() => {
    if (!isActive || seconds <= 0) {
      if (seconds <= 0 && isActive) {
        setIsActive(false)
        onComplete?.()
      }
      return
    }

    const timer = setInterval(() => {
      setSeconds(prev => {
        if (prev <= 1) {
          clearInterval(timer)
          setIsActive(false)
          onComplete?.()
          return 0
        }
        return prev - 1
      })
    }, 1000)

    return () => clearInterval(timer)
  }, [isActive, seconds, onComplete])

  const formatted = `${Math.floor(seconds / 60).toString().padStart(2, "0")}:${(seconds % 60).toString().padStart(2, "0")}`

  return { seconds, formatted, isActive, start, stop, reset }
}
