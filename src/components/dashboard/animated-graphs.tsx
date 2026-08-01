"use client"

import { motion } from "framer-motion"
import { TrendingUp, BarChart3, Activity } from "lucide-react"

interface AreaGraphProps {
  data: number[]
  color?: string
  height?: number
  label?: string
}

export function AreaGraph({ data, color = "#06b6d4", height = 120, label }: AreaGraphProps) {
  const max = Math.max(...data)
  const min = Math.min(...data)
  const range = max - min || 1

  const points = data
    .map((val, i) => {
      const x = (i / (data.length - 1)) * 100
      const y = 100 - ((val - min) / range) * 80 - 10
      return `${x},${y}`
    })
    .join(" ")

  const areaPoints = `0,100 ${points} 100,100`

  return (
    <div>
      {label && (
        <div className="flex items-center justify-between mb-3">
          <span className="text-sm font-medium text-white">{label}</span>
          <span className="text-xs text-white/40">Last 24h</span>
        </div>
      )}
      <div style={{ height }} className="relative">
        <svg viewBox="0 0 100 100" preserveAspectRatio="none" className="w-full h-full">
          <defs>
            <linearGradient id={`grad-${color.replace("#", "")}`} x1="0" y1="0" x2="0" y2="1">
              <stop offset="0%" stopColor={color} stopOpacity="0.3" />
              <stop offset="100%" stopColor={color} stopOpacity="0" />
            </linearGradient>
          </defs>
          <motion.polygon
            points={areaPoints}
            fill={`url(#grad-${color.replace("#", "")})`}
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{ duration: 1, delay: 0.3 }}
          />
          <motion.polyline
            points={points}
            fill="none"
            stroke={color}
            strokeWidth="0.8"
            strokeLinecap="round"
            strokeLinejoin="round"
            initial={{ pathLength: 0, opacity: 0 }}
            animate={{ pathLength: 1, opacity: 1 }}
            transition={{ duration: 1.5, ease: "easeOut" }}
            style={{ filter: `drop-shadow(0 0 4px ${color}80)` }}
          />
        </svg>
      </div>
    </div>
  )
}

interface BarGraphProps {
  data: { label: string; value: number; color?: string }[]
  height?: number
}

export function BarGraph({ data, height = 140 }: BarGraphProps) {
  const max = Math.max(...data.map((d) => d.value))

  return (
    <div style={{ height }} className="flex items-end gap-1.5 px-1">
      {data.map((item, i) => (
        <div key={i} className="flex-1 flex flex-col items-center gap-1">
          <motion.div
            className="w-full rounded-t-md"
            style={{ backgroundColor: item.color || "#06b6d4" }}
            initial={{ height: 0 }}
            animate={{ height: `${(item.value / max) * 100}%` }}
            transition={{ duration: 0.8, delay: i * 0.05, ease: "easeOut" }}
          />
          <span className="text-[9px] text-white/30 truncate w-full text-center">{item.label}</span>
        </div>
      ))}
    </div>
  )
}

interface RadialProgressProps {
  value: number
  max?: number
  size?: number
  strokeWidth?: number
  color?: string
  label?: string
}

export function RadialProgress({
  value,
  max = 100,
  size = 80,
  strokeWidth = 6,
  color = "#06b6d4",
  label,
}: RadialProgressProps) {
  const radius = (size - strokeWidth) / 2
  const circumference = radius * 2 * Math.PI
  const percent = (value / max) * 100
  const offset = circumference - (percent / 100) * circumference

  return (
    <div className="flex flex-col items-center">
      <div className="relative" style={{ width: size, height: size }}>
        <svg height={size} width={size} className="rotate-[-90deg]">
          <circle
            stroke="rgba(255,255,255,0.06)"
            fill="transparent"
            strokeWidth={strokeWidth}
            r={radius}
            cx={size / 2}
            cy={size / 2}
          />
          <motion.circle
            stroke={color}
            fill="transparent"
            strokeWidth={strokeWidth}
            strokeLinecap="round"
            strokeDasharray={`${circumference} ${circumference}`}
            initial={{ strokeDashoffset: circumference }}
            animate={{ strokeDashoffset: offset }}
            transition={{ duration: 1.5, ease: "easeOut", delay: 0.3 }}
            r={radius}
            cx={size / 2}
            cy={size / 2}
            style={{ filter: `drop-shadow(0 0 4px ${color}60)` }}
          />
        </svg>
        <div className="absolute inset-0 flex items-center justify-center">
          <span className="text-sm font-bold text-white">{Math.round(percent)}%</span>
        </div>
      </div>
      {label && <span className="text-[10px] text-white/40 mt-1.5">{label}</span>}
    </div>
  )
}
