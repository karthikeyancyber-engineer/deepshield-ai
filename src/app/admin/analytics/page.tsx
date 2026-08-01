"use client"

import { BarChart3, Shield, AlertTriangle, Users, Inbox } from "lucide-react"

export default function AnalyticsPage() {
  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-[var(--text-primary)]">Analytics</h1>
        <p className="text-[var(--text-tertiary)] text-sm mt-1">Interview performance and security analytics</p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        {[
          { label: "Avg Trust Score", value: "—", icon: Shield, color: "var(--accent-cyan)" },
          { label: "Interviews This Month", value: "0", icon: Users, color: "var(--accent-blue)" },
          { label: "Security Alerts", value: "0", icon: AlertTriangle, color: "var(--accent-amber)" },
        ].map((stat) => (
          <div key={stat.label} className="surface rounded-[var(--radius-lg)] p-5">
            <div className="flex items-center justify-between mb-3">
              <div className="flex items-center justify-center w-9 h-9 rounded-[var(--radius-md)]" style={{ background: `${stat.color}15` }}>
                <stat.icon className="h-4.5 w-4.5" style={{ color: stat.color }} />
              </div>
            </div>
            <p className="text-3xl font-bold text-[var(--text-primary)]">{stat.value}</p>
            <p className="text-sm text-[var(--text-tertiary)] mt-1">{stat.label}</p>
          </div>
        ))}
      </div>

      <div className="surface rounded-[var(--radius-lg)] p-6">
        <h3 className="text-sm font-semibold text-[var(--text-primary)] mb-4">Trust Score Distribution</h3>
        <div className="flex flex-col items-center justify-center py-12">
          <Inbox className="h-12 w-12 text-[var(--text-quaternary)] mb-3" />
          <p className="text-sm text-[var(--text-tertiary)]">No interview data yet</p>
          <p className="text-xs text-[var(--text-quaternary)] mt-1">Analytics will appear here after interviews are conducted</p>
        </div>
      </div>
    </div>
  )
}
