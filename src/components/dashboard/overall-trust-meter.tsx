"use client"

import { motion } from "framer-motion"
import { Shield, TrendingUp, TrendingDown } from "lucide-react"

interface OverallTrustMeterProps {
  score: number
  trend: "up" | "down" | "stable"
  change: string
}

export function OverallTrustMeter({ score, trend, change }: OverallTrustMeterProps) {
  const radius = 90
  const stroke = 12
  const normalizedRadius = radius - stroke
  const circumference = normalizedRadius * 2 * Math.PI
  const strokeDashoffset = circumference - (score / 100) * circumference

  const getScoreColor = (val: number) => {
    if (val >= 90) return { main: "#10b981", glow: "rgba(16,185,129,0.4)" }
    if (val >= 75) return { main: "#06b6d4", glow: "rgba(6,182,212,0.4)" }
    if (val >= 50) return { main: "#f59e0b", glow: "rgba(245,158,11,0.4)" }
    return { main: "#ef4444", glow: "rgba(239,68,68,0.4)" }
  }

  const colors = getScoreColor(score)

  return (
    <motion.div
      initial={{ opacity: 0, scale: 0.9 }}
      animate={{ opacity: 1, scale: 1 }}
      transition={{ duration: 0.6 }}
      className="flex flex-col items-center justify-center p-6 rounded-2xl bg-gradient-to-br from-white/5 to-white/[0.02] border border-white/10"
    >
      <div className="relative" style={{ width: radius * 2, height: radius * 2 }}>
        <svg height={radius * 2} width={radius * 2} className="rotate-[-90deg]">
          <defs>
            <filter id="glow">
              <feGaussianBlur stdDeviation="4" result="coloredBlur" />
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
            stroke={colors.main}
            fill="transparent"
            strokeWidth={stroke}
            strokeLinecap="round"
            strokeDasharray={`${circumference} ${circumference}`}
            initial={{ strokeDashoffset: circumference }}
            animate={{ strokeDashoffset }}
            transition={{ duration: 2, ease: "easeOut", delay: 0.5 }}
            r={normalizedRadius}
            cx={radius}
            cy={radius}
            filter="url(#glow)"
          />
        </svg>
        <div className="absolute inset-0 flex flex-col items-center justify-center">
          <Shield className="h-6 w-6 mb-1" style={{ color: colors.main }} />
          <motion.span
            initial={{ opacity: 0, scale: 0.5 }}
            animate={{ opacity: 1, scale: 1 }}
            transition={{ delay: 0.8, type: "spring" }}
            className="text-5xl font-bold text-white"
          >
            {score}
          </motion.span>
          <span className="text-sm text-white/50 mt-1">Trust Score</span>
        </div>
      </div>

      <div className="flex items-center gap-2 mt-4">
        {trend === "up" ? (
          <TrendingUp className="h-4 w-4 text-green-400" />
        ) : trend === "down" ? (
          <TrendingDown className="h-4 w-4 text-red-400" />
        ) : null}
        <span className={`text-sm font-medium ${trend === "up" ? "text-green-400" : trend === "down" ? "text-red-400" : "text-white/60"}`}>
          {change}
        </span>
        <span className="text-xs text-white/40">vs last hour</span>
      </div>

      <div className="grid grid-cols-3 gap-6 mt-6 w-full">
        {[
          { label: "Identity", value: "92%", color: "#10b981" },
          { label: "Behavior", value: "88%", color: "#06b6d4" },
          { label: "Network", value: "95%", color: "#3b82f6" },
        ].map((item) => (
          <div key={item.label} className="text-center">
            <p className="text-lg font-semibold" style={{ color: item.color }}>{item.value}</p>
            <p className="text-xs text-white/50">{item.label}</p>
          </div>
        ))}
      </div>
    </motion.div>
  )
}
