"use client"

import { motion } from "framer-motion"
import { ShieldAlert, ShieldCheck, ShieldQuestion, AlertTriangle } from "lucide-react"

interface RiskLevelGaugeProps {
  level: number
  label: string
}

export function RiskLevelGauge({ level, label }: RiskLevelGaugeProps) {
  const getColor = (val: number) => {
    if (val <= 25) return { bar: "#10b981", bg: "bg-green-500/10", text: "text-green-400", icon: ShieldCheck, status: "Low Risk" }
    if (val <= 50) return { bar: "#06b6d4", bg: "bg-cyan-500/10", text: "text-cyan-400", icon: ShieldQuestion, status: "Moderate" }
    if (val <= 75) return { bar: "#f59e0b", bg: "bg-yellow-500/10", text: "text-yellow-400", icon: AlertTriangle, status: "Elevated" }
    return { bar: "#ef4444", bg: "bg-red-500/10", text: "text-red-400", icon: ShieldAlert, status: "Critical" }
  }

  const config = getColor(level)
  const Icon = config.icon

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.5, delay: 0.15 }}
      className="rounded-2xl border border-white/10 bg-white/[0.03] backdrop-blur-xl p-5"
    >
      <div className="flex items-center justify-between mb-4">
        <div className="flex items-center gap-2">
          <ShieldAlert className="h-4 w-4 text-orange-400" />
          <span className="text-sm font-medium text-white">Risk Level</span>
        </div>
        <div className={`flex items-center gap-1.5 px-2 py-1 rounded-lg ${config.bg}`}>
          <Icon className={`h-3.5 w-3.5 ${config.text}`} />
          <span className={`text-xs font-medium ${config.text}`}>{config.status}</span>
        </div>
      </div>

      <div className="mb-4">
        <div className="flex items-end justify-between mb-2">
          <span className="text-3xl font-bold text-white">{level}%</span>
          <span className="text-xs text-white/40 mb-1">{label}</span>
        </div>
        <div className="h-3 rounded-full bg-white/5 overflow-hidden">
          <motion.div
            className="h-full rounded-full"
            style={{ background: `linear-gradient(90deg, ${config.bar}90, ${config.bar})` }}
            initial={{ width: 0 }}
            animate={{ width: `${level}%` }}
            transition={{ duration: 1.5, ease: "easeOut", delay: 0.3 }}
          />
        </div>
      </div>

      <div className="grid grid-cols-4 gap-2">
        {[
          { range: "0-25", color: "#10b981", label: "Low" },
          { range: "25-50", color: "#06b6d4", label: "Moderate" },
          { range: "50-75", color: "#f59e0b", label: "Elevated" },
          { range: "75-100", color: "#ef4444", label: "Critical" },
        ].map((item) => (
          <div key={item.range} className="text-center">
            <div
              className="h-1.5 rounded-full mb-1"
              style={{ background: item.color, opacity: level >= parseInt(item.range) ? 1 : 0.2 }}
            />
            <span className="text-[10px] text-white/30">{item.label}</span>
          </div>
        ))}
      </div>
    </motion.div>
  )
}
