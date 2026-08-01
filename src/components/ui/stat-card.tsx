"use client"

import { motion } from "framer-motion"
import { cn } from "@/lib/utils"
import { LucideIcon } from "lucide-react"

interface StatCardProps {
  icon: LucideIcon
  label: string
  value: string | number
  change?: string
  changeType?: "positive" | "negative" | "neutral"
  color?: "cyan" | "blue" | "purple" | "emerald" | "amber" | "rose"
  delay?: number
}

const colorMap = {
  cyan: { bg: "rgba(6, 182, 212, 0.08)", border: "rgba(6, 182, 212, 0.15)", text: "#06b6d4", shadow: "rgba(6, 182, 212, 0.1)" },
  blue: { bg: "rgba(59, 130, 246, 0.08)", border: "rgba(59, 130, 246, 0.15)", text: "#3b82f6", shadow: "rgba(59, 130, 246, 0.1)" },
  purple: { bg: "rgba(139, 92, 246, 0.08)", border: "rgba(139, 92, 246, 0.15)", text: "#8b5cf6", shadow: "rgba(139, 92, 246, 0.1)" },
  emerald: { bg: "rgba(16, 185, 129, 0.08)", border: "rgba(16, 185, 129, 0.15)", text: "#10b981", shadow: "rgba(16, 185, 129, 0.1)" },
  amber: { bg: "rgba(245, 158, 11, 0.08)", border: "rgba(245, 158, 11, 0.15)", text: "#f59e0b", shadow: "rgba(245, 158, 11, 0.1)" },
  rose: { bg: "rgba(244, 63, 94, 0.08)", border: "rgba(244, 63, 94, 0.15)", text: "#f43f5e", shadow: "rgba(244, 63, 94, 0.1)" },
}

export function StatCard({ icon: Icon, label, value, change, changeType = "neutral", color = "cyan", delay = 0 }: StatCardProps) {
  const c = colorMap[color]

  return (
    <motion.div
      initial={{ opacity: 0, y: 16 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.5, delay, ease: [0.16, 1, 0.3, 1] }}
      whileHover={{ y: -2, transition: { duration: 0.2 } }}
      className="relative overflow-hidden rounded-[var(--radius-lg)] border border-[var(--border-subtle)] p-5"
      style={{ background: c.bg }}
    >
      <div className="flex items-start justify-between mb-4">
        <div
          className="flex items-center justify-center w-10 h-10 rounded-[var(--radius-md)]"
          style={{ background: `${c.text}15` }}
        >
          <Icon className="h-5 w-5" style={{ color: c.text }} />
        </div>
        {change && (
          <span className={cn(
            "text-xs font-medium px-2 py-0.5 rounded-full",
            changeType === "positive" && "bg-[rgba(16,185,129,0.1)] text-[var(--accent-emerald)]",
            changeType === "negative" && "bg-[rgba(244,63,94,0.1)] text-[var(--accent-rose)]",
            changeType === "neutral" && "bg-[var(--bg-glass)] text-[var(--text-tertiary)]",
          )}>
            {change}
          </span>
        )}
      </div>
      <div>
        <motion.p
          initial={{ opacity: 0, y: 8 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6, delay: delay + 0.15 }}
          className="text-3xl font-bold tracking-tight text-[var(--text-primary)]"
        >
          {value}
        </motion.p>
        <p className="text-sm text-[var(--text-tertiary)] mt-1">{label}</p>
      </div>
      <div
        className="absolute -bottom-8 -right-8 w-24 h-24 rounded-full opacity-10 blur-2xl"
        style={{ background: c.text }}
      />
    </motion.div>
  )
}
