"use client"

import { motion, AnimatePresence } from "framer-motion"
import { AlertTriangle, Shield, Bug, Globe, Clock, ChevronRight, Zap } from "lucide-react"
import { StatusBadge } from "@/components/shared/status-badge"

const threats = [
  {
    id: 1,
    title: "SQL Injection Attempt",
    source: "192.168.1.105",
    severity: "critical" as const,
    time: "2m ago",
    icon: Bug,
  },
  {
    id: 2,
    title: "Brute Force Login",
    source: "45.33.32.156",
    severity: "high" as const,
    time: "15m ago",
    icon: Shield,
  },
  {
    id: 3,
    title: "DDoS Mitigated",
    source: "Multiple",
    severity: "critical" as const,
    time: "1h ago",
    icon: Zap,
  },
  {
    id: 4,
    title: "XSS Payload Blocked",
    source: "172.16.0.89",
    severity: "medium" as const,
    time: "3h ago",
    icon: AlertTriangle,
  },
  {
    id: 5,
    title: "Unauthorized Access",
    source: "203.0.113.42",
    severity: "low" as const,
    time: "5h ago",
    icon: Globe,
  },
]

const severityColor = {
  critical: "text-red-400 bg-red-500/10",
  high: "text-orange-400 bg-orange-500/10",
  medium: "text-yellow-400 bg-yellow-500/10",
  low: "text-green-400 bg-green-500/10",
}

export function ThreatTimelineWidget() {
  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.5, delay: 0.2 }}
      className="rounded-2xl border border-white/10 bg-white/[0.03] backdrop-blur-xl overflow-hidden"
    >
      <div className="flex items-center justify-between px-4 py-3 border-b border-white/5">
        <div className="flex items-center gap-2">
          <AlertTriangle className="h-4 w-4 text-orange-400" />
          <span className="text-sm font-medium text-white">Threat Timeline</span>
        </div>
        <span className="text-xs text-white/40 px-2 py-0.5 rounded-full bg-white/5">Live</span>
      </div>

      <div className="divide-y divide-white/5 max-h-[320px] overflow-y-auto">
        <AnimatePresence>
          {threats.map((threat, i) => (
            <motion.div
              key={threat.id}
              initial={{ opacity: 0, x: -10 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ delay: i * 0.08 }}
              className="flex items-center gap-3 px-4 py-3 hover:bg-white/[0.02] transition-colors cursor-pointer group"
            >
              <div className={`h-8 w-8 rounded-lg flex items-center justify-center shrink-0 ${severityColor[threat.severity]}`}>
                <threat.icon className="h-4 w-4" />
              </div>
              <div className="flex-1 min-w-0">
                <p className="text-sm font-medium text-white truncate">{threat.title}</p>
                <div className="flex items-center gap-2 mt-0.5">
                  <span className="text-[11px] text-white/40">{threat.source}</span>
                  <span className="text-[11px] text-white/20">|</span>
                  <span className="text-[11px] text-white/40 flex items-center gap-1">
                    <Clock className="h-2.5 w-2.5" />
                    {threat.time}
                  </span>
                </div>
              </div>
              <StatusBadge status={threat.severity} />
            </motion.div>
          ))}
        </AnimatePresence>
      </div>
    </motion.div>
  )
}
