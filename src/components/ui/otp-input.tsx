"use client"

import { useRef, useState, useCallback, useEffect } from "react"
import { motion } from "framer-motion"
import { cn } from "@/lib/utils"

interface OTPInputProps {
  length?: number
  value: string
  onChange: (value: string) => void
  disabled?: boolean
  error?: string
}

export function OTPInput({ length = 6, value, onChange, disabled = false, error }: OTPInputProps) {
  const inputRefs = useRef<(HTMLInputElement | null)[]>([])
  const [focusedIndex, setFocusedIndex] = useState(0)

  useEffect(() => {
    if (!disabled && inputRefs.current[0]) {
      inputRefs.current[0].focus()
    }
  }, [disabled])

  const handleChange = useCallback((index: number, digit: string) => {
    if (disabled) return
    if (!/^\d*$/.test(digit)) return

    const newValue = value.split("")
    newValue[index] = digit
    const joined = newValue.join("").slice(0, length)
    onChange(joined)

    // Auto-advance to next input
    if (digit && index < length - 1) {
      inputRefs.current[index + 1]?.focus()
    }
  }, [value, onChange, length, disabled])

  const handleKeyDown = useCallback((index: number, e: React.KeyboardEvent) => {
    if (disabled) return

    if (e.key === "Backspace") {
      e.preventDefault()
      const newValue = value.split("")
      if (newValue[index]) {
        newValue[index] = ""
        onChange(newValue.join(""))
      } else if (index > 0) {
        newValue[index - 1] = ""
        onChange(newValue.join(""))
        inputRefs.current[index - 1]?.focus()
      }
    } else if (e.key === "ArrowLeft" && index > 0) {
      e.preventDefault()
      inputRefs.current[index - 1]?.focus()
    } else if (e.key === "ArrowRight" && index < length - 1) {
      e.preventDefault()
      inputRefs.current[index + 1]?.focus()
    }
  }, [value, onChange, length, disabled])

  const handlePaste = useCallback((e: React.ClipboardEvent) => {
    if (disabled) return
    e.preventDefault()
    const pasted = e.clipboardData.getData("text").replace(/\D/g, "").slice(0, length)
    if (pasted) {
      onChange(pasted)
      // Focus the next empty input or the last one
      const nextIndex = Math.min(pasted.length, length - 1)
      inputRefs.current[nextIndex]?.focus()
    }
  }, [onChange, length, disabled])

  const handleFocus = useCallback((index: number) => {
    setFocusedIndex(index)
    // Select all text on focus
    inputRefs.current[index]?.select()
  }, [])

  return (
    <div className="space-y-2">
      <div className="flex items-center justify-center gap-2 sm:gap-3">
        {Array.from({ length }).map((_, index) => (
          <motion.div
            key={index}
            initial={{ opacity: 0, scale: 0.8 }}
            animate={{ opacity: 1, scale: 1 }}
            transition={{ delay: index * 0.05 }}
          >
            <input
              ref={(el) => { inputRefs.current[index] = el }}
              type="text"
              inputMode="numeric"
              maxLength={1}
              value={value[index] || ""}
              onChange={(e) => handleChange(index, e.target.value)}
              onKeyDown={(e) => handleKeyDown(index, e)}
              onPaste={handlePaste}
              onFocus={() => handleFocus(index)}
              disabled={disabled}
              className={cn(
                "w-11 h-14 sm:w-13 sm:h-16 text-center text-xl sm:text-2xl font-bold rounded-xl border-2 transition-all duration-200",
                "bg-white/5 text-white placeholder:text-white/20 outline-none",
                disabled && "opacity-40 cursor-not-allowed",
                error
                  ? "border-red-500/50 focus:border-red-400"
                  : value[index]
                    ? "border-cyan-500/50 focus:border-cyan-400 bg-cyan-500/5"
                    : focusedIndex === index
                      ? "border-cyan-400/60"
                      : "border-white/10 hover:border-white/20",
              )}
              autoComplete="one-time-code"
            />
          </motion.div>
        ))}
      </div>
      {error && (
        <motion.p
          initial={{ opacity: 0, y: -5 }}
          animate={{ opacity: 1, y: 0 }}
          className="text-red-400 text-sm text-center"
        >
          {error}
        </motion.p>
      )}
    </div>
  )
}
