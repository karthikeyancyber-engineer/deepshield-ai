"use client"

import { motion } from "framer-motion"

interface TrustGaugeProps {
  value: number
  label: string
  icon: React.ReactNode
  color: string
  size?: "sm" | "lg"
}

export function TrustGauge({ value, label, icon, color, size = "sm" }: TrustGaugeProps) {
  const radius = size === "lg" ? 58 : 40
  const stroke = size === "lg" ? 8 : 6
  const normalizedRadius = radius - stroke
  const circumference = normalizedRadius * 2 * Math.PI
  const strokeDashoffset = circumference - (value / 100) * circumference

  const getColor = (val: number) => {
    if (val >= 80) return "#10b981"
    if (val >= 60) return "#06b6d4"
    if (val >= 40) return "#f59e0b"
    return "#ef4444"
  }

  const gaugeColor = color || getColor(value)

  return (
    <motion.div
      initial={{ opacity: 0, scale: 0.9 }}
      animate={{ opacity: 1, scale: 1 }}
      className="flex flex-col items-center"
    >
      <div className="relative" style={{ width: radius * 2, height: radius * 2 }}>
        <svg height={radius * 2} width={radius * 2} className="rotate-[-90deg]">
          <circle
            stroke="rgba(255,255,255,0.08)"
            fill="transparent"
            strokeWidth={stroke}
            r={normalizedRadius}
            cx={radius}
            cy={radius}
          />
          <motion.circle
            stroke={gaugeColor}
            fill="transparent"
            strokeWidth={stroke}
            strokeLinecap="round"
            strokeDasharray={`${circumference} ${circumference}`}
            initial={{ strokeDashoffset: circumference }}
            animate={{ strokeDashoffset }}
            transition={{ duration: 1.5, ease: "easeOut", delay: 0.3 }}
            r={normalizedRadius}
            cx={radius}
            cy={radius}
            style={{ filter: `drop-shadow(0 0 6px ${gaugeColor}50)` }}
          />
        </svg>
        <div className="absolute inset-0 flex flex-col items-center justify-center">
          <span className="text-white/40 mb-0.5">{icon}</span>
          <motion.span
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{ delay: 0.5 }}
            className={`font-bold text-white ${size === "lg" ? "text-2xl" : "text-lg"}`}
          >
            {value}%
          </motion.span>
        </div>
      </div>
      <span className={`mt-2 text-white/60 font-medium ${size === "sm" ? "text-xs" : "text-sm"}`}>
        {label}
      </span>
    </motion.div>
  )
}
