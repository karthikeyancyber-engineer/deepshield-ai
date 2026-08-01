"use client"

import { cn } from "@/lib/utils"

interface StatusBadgeProps {
  status: "critical" | "high" | "medium" | "low" | "secure" | "online" | "offline"
  className?: string
}

const statusColors = {
  critical: "bg-red-500/20 text-red-400 border-red-500/30",
  high: "bg-orange-500/20 text-orange-400 border-orange-500/30",
  medium: "bg-yellow-500/20 text-yellow-400 border-yellow-500/30",
  low: "bg-green-500/20 text-green-400 border-green-500/30",
  secure: "bg-cyan-500/20 text-cyan-400 border-cyan-500/30",
  online: "bg-green-500/20 text-green-400 border-green-500/30",
  offline: "bg-white/10 text-white/50 border-white/20",
}

export function StatusBadge({ status, className }: StatusBadgeProps) {
  return (
    <span
      className={cn(
        "inline-flex items-center rounded-full border px-2.5 py-0.5 text-xs font-medium",
        statusColors[status],
        className
      )}
    >
      <span className={cn(
        "mr-1.5 h-1.5 w-1.5 rounded-full",
        status === "critical" && "bg-red-500 animate-pulse",
        status === "high" && "bg-orange-500",
        status === "medium" && "bg-yellow-500",
        status === "low" && "bg-green-500",
        status === "secure" && "bg-cyan-500",
        status === "online" && "bg-green-500 animate-pulse",
        status === "offline" && "bg-white/50"
      )} />
      {status.charAt(0).toUpperCase() + status.slice(1)}
    </span>
  )
}
