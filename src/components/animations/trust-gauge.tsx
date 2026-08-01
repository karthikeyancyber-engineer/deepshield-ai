"use client"

import { motion } from "framer-motion"

interface TrustGaugeProps {
  value: number
  label: string
  icon: React.ReactNode
  color?: string
  size?: "sm" | "md" | "lg"
  className?: string
}

export function TrustGauge({
  value,
  label,
  icon,
  color,
  size = "sm",
  className = "",
}: TrustGaugeProps) {
  const dims = { sm: 80, md: 100, lg: 140 }[size]
  const stroke = { sm: 5, md: 7, lg: 10 }[size]
  const radius = dims / 2
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
      initial={{ opacity: 0, scale: 0.8 }}
      animate={{ opacity: 1, scale: 1 }}
      transition={{ duration: 0.6, ease: [0.16, 1, 0.3, 1] }}
      className={`flex flex-col items-center ${className}`}
    >
      <div className="relative" style={{ width: dims, height: dims }}>
        <svg height={dims} width={dims} className="rotate-[-90deg]">
          <defs>
            <filter id={`glow-${label}`}>
              <feGaussianBlur stdDeviation="3" result="coloredBlur" />
              <feMerge>
                <feMergeNode in="coloredBlur" />
                <feMergeNode in="SourceGraphic" />
              </feMerge>
            </filter>
          </defs>
          <circle
            stroke="rgba(255,255,255,0.06)"
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
            transition={{ duration: 1.8, ease: [0.16, 1, 0.3, 1], delay: 0.3 }}
            r={normalizedRadius}
            cx={radius}
            cy={radius}
            filter={`url(#glow-${label})`}
          />
        </svg>
        <div className="absolute inset-0 flex flex-col items-center justify-center">
          <span className="text-white/50 mb-0.5">{icon}</span>
          <motion.span
            initial={{ opacity: 0, scale: 0.5 }}
            animate={{ opacity: 1, scale: 1 }}
            transition={{ delay: 0.6, type: "spring", stiffness: 200 }}
            className={`font-bold text-white ${size === "lg" ? "text-3xl" : size === "md" ? "text-xl" : "text-lg"}`}
          >
            {value}%
          </motion.span>
        </div>
      </div>
      <motion.span
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        transition={{ delay: 0.8 }}
        className={`mt-2 text-white/60 font-medium ${size === "lg" ? "text-sm" : "text-xs"}`}
      >
        {label}
      </motion.span>
    </motion.div>
  )
}

interface OverallTrustMeterProps {
  score: number
  trend?: "up" | "down" | "stable"
  change?: string
}

export function OverallTrustMeter({ score, trend = "stable", change = "+0%" }: OverallTrustMeterProps) {
  const radius = 90
  const stroke = 12
  const normalizedRadius = radius - stroke
  const circumference = normalizedRadius * 2 * Math.PI
  const strokeDashoffset = circumference - (score / 100) * circumference

  const getColor = (val: number) => {
    if (val >= 90) return { main: "#10b981", glow: "rgba(16,185,129,0.4)" }
    if (val >= 75) return { main: "#06b6d4", glow: "rgba(6,182,212,0.4)" }
    if (val >= 50) return { main: "#f59e0b", glow: "rgba(245,158,11,0.4)" }
    return { main: "#ef4444", glow: "rgba(239,68,68,0.4)" }
  }

  const colors = getColor(score)

  return (
    <motion.div
      initial={{ opacity: 0, scale: 0.9 }}
      animate={{ opacity: 1, scale: 1 }}
      transition={{ duration: 0.6 }}
      className="flex flex-col items-center justify-center p-6 rounded-2xl bg-gradient-to-br from-white/[0.04] to-transparent border border-white/[0.06] hover-lift"
    >
      <div className="relative" style={{ width: radius * 2, height: radius * 2 }}>
        <svg height={radius * 2} width={radius * 2} className="rotate-[-90deg]">
          <defs>
            <filter id="trust-glow">
              <feGaussianBlur stdDeviation="4" result="coloredBlur" />
              <feMerge>
                <feMergeNode in="coloredBlur" />
                <feMergeNode in="SourceGraphic" />
              </feMerge>
            </filter>
          </defs>
          <circle
            stroke="rgba(255,255,255,0.05)"
            fill="transparent"
            strokeWidth={stroke}
            r={normalizedRadius}
            cx={radius}
            cy={radius}
          />
          <motion.circle
            stroke={colors.main}
            fill="transparent"
            strokeWidth={stroke}
            strokeLinecap="round"
            strokeDasharray={`${circumference} ${circumference}`}
            initial={{ strokeDashoffset: circumference }}
            animate={{ strokeDashoffset }}
            transition={{ duration: 2.2, ease: [0.16, 1, 0.3, 1], delay: 0.5 }}
            r={normalizedRadius}
            cx={radius}
            cy={radius}
            filter="url(#trust-glow)"
          />
        </svg>
        <div className="absolute inset-0 flex flex-col items-center justify-center">
          <motion.span
            initial={{ opacity: 0, scale: 0.5 }}
            animate={{ opacity: 1, scale: 1 }}
            transition={{ delay: 1, type: "spring", stiffness: 150 }}
            className="text-5xl font-bold text-white"
          >
            {score}
          </motion.span>
          <span className="text-sm text-white/40 mt-1">Trust Score</span>
        </div>
      </div>

      <motion.div
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        transition={{ delay: 1.2 }}
        className="flex items-center gap-2 mt-4"
      >
        {trend === "up" && <span className="text-green-400 text-sm">↑</span>}
        {trend === "down" && <span className="text-red-400 text-sm">↓</span>}
        <span className={`text-sm font-medium ${trend === "up" ? "text-green-400" : trend === "down" ? "text-red-400" : "text-white/50"}`}>
          {change}
        </span>
        <span className="text-xs text-white/30">vs last hour</span>
      </motion.div>

      <div className="grid grid-cols-3 gap-6 mt-6 w-full">
        {[
          { label: "Identity", value: "92%", color: "#10b981" },
          { label: "Behavior", value: "88%", color: "#06b6d4" },
          { label: "Network", value: "95%", color: "#3b82f6" },
        ].map((item, i) => (
          <motion.div
            key={item.label}
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 1.4 + i * 0.1 }}
            className="text-center"
          >
            <p className="text-lg font-semibold" style={{ color: item.color }}>{item.value}</p>
            <p className="text-xs text-white/40">{item.label}</p>
          </motion.div>
        ))}
      </div>
    </motion.div>
  )
}
