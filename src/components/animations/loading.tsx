"use client"

import { motion } from "framer-motion"

interface LoadingSpinnerProps {
  size?: number
  color?: string
  className?: string
}

export function LoadingSpinner({ size = 40, color = "#06b6d4", className = "" }: LoadingSpinnerProps) {
  return (
    <div className={`loading-spinner ${className}`} style={{ width: size, height: size }}>
      <svg viewBox="0 0 50 50">
        <circle
          cx="25"
          cy="25"
          r="20"
          fill="none"
          stroke={`${color}20`}
          strokeWidth="3"
        />
        <circle
          cx="25"
          cy="25"
          r="20"
          fill="none"
          stroke={color}
          strokeWidth="3"
          strokeLinecap="round"
        />
      </svg>
    </div>
  )
}

interface WaveLoaderProps {
  bars?: number
  color?: string
  className?: string
}

export function WaveLoader({ bars = 5, color = "#06b6d4", className = "" }: WaveLoaderProps) {
  return (
    <div className={`flex items-center gap-1 ${className}`}>
      {Array.from({ length: bars }).map((_, i) => (
        <div
          key={i}
          className="wave-bar"
          style={{
            animationDelay: `${i * 0.15}s`,
            background: `linear-gradient(to top, ${color}, ${color}90)`,
          }}
        />
      ))}
    </div>
  )
}

interface SkeletonProps {
  className?: string
  count?: number
}

export function Skeleton({ className = "", count = 1 }: SkeletonProps) {
  return (
    <div className={`space-y-3 ${className}`}>
      {Array.from({ length: count }).map((_, i) => (
        <div key={i} className="skeleton h-4 w-full" />
      ))}
    </div>
  )
}

interface PulsingDotProps {
  color?: string
  className?: string
}

export function PulsingDot({ color = "#10b981", className = "" }: PulsingDotProps) {
  return (
    <span className={`relative flex h-2.5 w-2.5 ${className}`}>
      <span
        className="absolute inline-flex h-full w-full rounded-full opacity-75 animate-ping"
        style={{ backgroundColor: color }}
      />
      <span
        className="relative inline-flex rounded-full h-2.5 w-2.5"
        style={{ backgroundColor: color }}
      />
    </span>
  )
}

interface LoadingOverlayProps {
  show: boolean
  message?: string
}

export function LoadingOverlay({ show, message = "Loading..." }: LoadingOverlayProps) {
  if (!show) return null
  return (
    <motion.div
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      exit={{ opacity: 0 }}
      className="fixed inset-0 z-50 flex items-center justify-center bg-[#030712]/80 backdrop-blur-sm"
    >
      <div className="flex flex-col items-center gap-4">
        <LoadingSpinner size={48} />
        <motion.p
          initial={{ opacity: 0, y: 5 }}
          animate={{ opacity: 1, y: 0 }}
          className="text-sm text-white/60"
        >
          {message}
        </motion.p>
      </div>
    </motion.div>
  )
}
