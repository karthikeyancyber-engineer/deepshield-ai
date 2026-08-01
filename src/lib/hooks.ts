"use client"

import { useState, useEffect } from "react"

export function useCurrentTime() {
  const [time, setTime] = useState("")
  const [mounted, setMounted] = useState(false)

  useEffect(() => {
    setMounted(true)
    const update = () => setTime(new Date().toLocaleTimeString())
    update()
    const id = setInterval(update, 1000)
    return () => clearInterval(id)
  }, [])

  return mounted ? time : ""
}

export function useFormattedDate(dateStr: string) {
  const [formatted, setFormatted] = useState("")
  const [mounted, setMounted] = useState(false)

  useEffect(() => {
    setMounted(true)
    setFormatted(new Date(dateStr).toLocaleString())
  }, [dateStr])

  return mounted ? formatted : dateStr
}
