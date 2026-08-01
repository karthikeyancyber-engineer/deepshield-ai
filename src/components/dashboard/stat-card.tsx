"use client"

import { motion } from "framer-motion"
import { cn } from "@/lib/utils"

interface StatCardProps {
  title: string
  value: string | number
  change?: string
  trend?: "up" | "down" | "neutral"
  icon: React.ReactNode
  className?: string
}

export function StatCard({ title, value, change, trend, icon, className }: StatCardProps) {
  return (
    <motion.div
      initial={{ opacity: 0, y: 15, scale: 0.98 }}
      animate={{ opacity: 1, y: 0, scale: 1 }}
      transition={{ duration: 0.5, ease: [0.16, 1, 0.3, 1] }}
      whileHover={{ y: -4, scale: 1.02 }}
      className={cn(
        "rounded-2xl border border-white/[0.06] bg-white/[0.03] backdrop-blur-xl p-5",
        "hover:border-cyan-500/20 hover:bg-white/[0.05] hover:shadow-lg hover:shadow-cyan-500/5",
        "transition-all duration-300 cursor-default group",
        className
      )}
    >
      <div className="flex items-center justify-between mb-3">
        <div className="h-10 w-10 rounded-xl bg-cyan-500/10 flex items-center justify-center text-cyan-400 group-hover:bg-cyan-500/15 group-hover:scale-110 transition-all duration-300">
          {icon}
        </div>
        {change && (
          <span className={cn(
            "text-xs font-medium px-2 py-0.5 rounded-full transition-colors",
            trend === "up" && "bg-green-500/10 text-green-400",
            trend === "down" && "bg-red-500/10 text-red-400",
            trend === "neutral" && "bg-white/5 text-white/50"
          )}>
            {trend === "up" && "↑"}
            {trend === "down" && "↓"}
            {change}
          </span>
        )}
      </div>
      <motion.p
        initial={{ opacity: 0, y: 5 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.2, duration: 0.4 }}
        className="text-2xl font-bold text-white mb-0.5 tabular-nums group-hover:glow-text-cyan transition-all duration-300"
      >
        {value}
      </motion.p>
      <p className="text-sm text-white/50 group-hover:text-white/60 transition-colors">{title}</p>
    </motion.div>
  )
}
