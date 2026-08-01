"use client"

import { useState, useEffect } from "react"
import { useAuth } from "@/lib/auth-context"
import { apiFetch } from "@/lib/api"
import { StatCard } from "@/components/ui/stat-card"
import { GlassCard } from "@/components/shared/glass-card"
import { PageSkeleton } from "@/components/ui/skeleton"
import { Users, Video, AlertTriangle, TrendingUp, Shield, Activity } from "lucide-react"

interface AdminStats {
  total_users: number
  total_interviews: number
  pending_requests: number
  active_interviews: number
}

export default function AdminDashboardPage() {
  const { user } = useAuth()
  const [stats, setStats] = useState<AdminStats | null>(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    const load = async () => {
      try {
        const data = await apiFetch("/admin/dashboard")
        setStats(data)
      } catch (err) {
        console.error(err)
        setStats({ total_users: 0, total_interviews: 0, pending_requests: 0, active_interviews: 0 })
      } finally {
        setLoading(false)
      }
    }
    load()
  }, [])

  if (loading) return <PageSkeleton />

  return (
    <div className="space-y-8">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-[var(--text-primary)] tracking-tight">Admin Dashboard</h1>
          <p className="text-[var(--text-tertiary)] text-sm mt-1">Welcome back, {user?.full_name || "Admin"}</p>
        </div>
        <div className="flex items-center gap-2 px-4 py-2 rounded-[var(--radius-md)]"
          style={{ background: "rgba(16, 185, 129, 0.08)", border: "1px solid rgba(16, 185, 129, 0.15)" }}>
          <div className="h-2 w-2 rounded-full bg-[var(--accent-emerald)] animate-pulse" />
          <span className="text-xs font-medium text-[var(--accent-emerald)]">All Systems Operational</span>
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        <StatCard icon={Users} label="Total Users" value={stats?.total_users || 0} color="cyan" delay={0} />
        <StatCard icon={Video} label="Total Interviews" value={stats?.total_interviews || 0} color="blue" delay={0.1} />
        <StatCard icon={AlertTriangle} label="Pending Requests" value={stats?.pending_requests || 0} color="amber" delay={0.2} />
        <StatCard icon={TrendingUp} label="Active Interviews" value={stats?.active_interviews || 0} color="emerald" delay={0.3} />
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <GlassCard delay={0.4}>
          <div className="flex items-center gap-3 mb-4">
            <div className="flex items-center justify-center w-9 h-9 rounded-[var(--radius-md)]" style={{ background: "rgba(6, 182, 212, 0.08)" }}>
              <Shield className="h-4.5 w-4.5 text-[var(--accent-cyan)]" />
            </div>
            <h3 className="text-sm font-semibold text-[var(--text-primary)]">System Security</h3>
          </div>
          <div className="space-y-3">
            <div className="flex items-center justify-between">
              <span className="text-sm text-[var(--text-tertiary)]">AI Detection Engine</span>
              <span className="text-xs font-medium text-[var(--accent-emerald)]">Active</span>
            </div>
            <div className="flex items-center justify-between">
              <span className="text-sm text-[var(--text-tertiary)]">Deepfake Protection</span>
              <span className="text-xs font-medium text-[var(--accent-emerald)]">Enabled</span>
            </div>
            <div className="flex items-center justify-between">
              <span className="text-sm text-[var(--text-tertiary)]">Emotion Analysis</span>
              <span className="text-xs font-medium text-[var(--accent-emerald)]">Running</span>
            </div>
          </div>
        </GlassCard>

        <GlassCard delay={0.5}>
          <div className="flex items-center gap-3 mb-4">
            <div className="flex items-center justify-center w-9 h-9 rounded-[var(--radius-md)]" style={{ background: "rgba(139, 92, 246, 0.08)" }}>
              <Activity className="h-4.5 w-4.5 text-[var(--accent-purple)]" />
            </div>
            <h3 className="text-sm font-semibold text-[var(--text-primary)]">Recent Activity</h3>
          </div>
          <div className="space-y-3">
            <p className="text-sm text-[var(--text-tertiary)] text-center py-4">No recent activity</p>
          </div>
        </GlassCard>
      </div>
    </div>
  )
}
