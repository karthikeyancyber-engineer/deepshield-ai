"use client"

import { motion } from "framer-motion"
import { cn } from "@/lib/utils"

interface AnimatedCounterProps {
  value: number
  label: string
  icon: React.ReactNode
  trend?: "up" | "down" | "neutral"
  trendValue?: string
  className?: string
}

export function AnimatedCounter({ value, label, icon, trend, trendValue, className }: AnimatedCounterProps) {
  return (
    <motion.div
      initial={{ opacity: 0, scale: 0.9 }}
      animate={{ opacity: 1, scale: 1 }}
      transition={{ duration: 0.5 }}
      className={cn(
        "rounded-2xl border border-white/10 bg-white/5 backdrop-blur-xl p-6",
        className
      )}
    >
      <div className="flex items-center justify-between">
        <div className="flex h-12 w-12 items-center justify-center rounded-xl bg-cyan-500/10 text-cyan-400">
          {icon}
        </div>
        {trend && (
          <span className={cn(
            "text-xs font-medium",
            trend === "up" && "text-green-400",
            trend === "down" && "text-red-400",
            trend === "neutral" && "text-white/50"
          )}>
            {trend === "up" && "↑"}
            {trend === "down" && "↓"}
            {trendValue}
          </span>
        )}
      </div>
      <div className="mt-4">
        <motion.p
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ delay: 0.2 }}
          className="text-3xl font-bold text-white"
        >
          {value.toLocaleString()}
        </motion.p>
        <p className="text-sm text-white/60 mt-1">{label}</p>
      </div>
    </motion.div>
  )
}
