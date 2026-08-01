"use client"

import { useState, useEffect } from "react"
import { useAuth } from "@/lib/auth-context"
import { apiFetch } from "@/lib/api"
import { StatCard } from "@/components/ui/stat-card"
import { GlassCard } from "@/components/shared/glass-card"
import { Button } from "@/components/ui/button"
import { PageSkeleton } from "@/components/ui/skeleton"
import { Send, CheckCircle2, XCircle, Video, Calendar, FileText, ExternalLink } from "lucide-react"
import Link from "next/link"

export default function CandidateDashboardPage() {
  const { user } = useAuth()
  const [applied, setApplied] = useState(0)
  const [completed, setCompleted] = useState(0)
  const [rejected, setRejected] = useState(0)
  const [approvedWithToken, setApprovedWithToken] = useState<any[]>([])
  const [recentRequests, setRecentRequests] = useState<any[]>([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    const load = async () => {
      try {
        const requests = await apiFetch("/interview-requests/my")
        setApplied(requests.length)
        setCompleted(requests.filter((r: any) => r.status === "approved").length)
        setRejected(requests.filter((r: any) => r.status === "rejected").length)
        setRecentRequests(requests.slice(0, 5))

        const interviews = await apiFetch("/interviews/")
        const myApproved = interviews.filter((i: any) =>
          i.status === "scheduled" && (i.candidate_id === user?.user_id || i.candidate_email === user?.email)
        )
        setApprovedWithToken(myApproved)
      } catch (err) {
        console.error(err)
      } finally {
        setLoading(false)
      }
    }
    load()
  }, [user])

  if (loading) return <PageSkeleton />

  return (
    <div className="space-y-8">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-[var(--text-primary)] tracking-tight">Dashboard</h1>
          <p className="text-[var(--text-tertiary)] text-sm mt-1">Welcome back, {user?.full_name || "Candidate"}</p>
        </div>
        <Link href="/dashboard/request-interview">
          <Button className="gap-2">
            <Send className="h-4 w-4" /> Apply for Interview
          </Button>
        </Link>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <StatCard icon={Send} label="Interviews Applied" value={applied} color="cyan" delay={0} />
        <StatCard icon={CheckCircle2} label="Interviews Completed" value={completed} color="emerald" delay={0.1} />
        <StatCard icon={XCircle} label="Interviews Rejected" value={rejected} color="rose" delay={0.2} />
      </div>

      {approvedWithToken.length > 0 && (
        <GlassCard delay={0.3} className="!p-0 overflow-hidden">
          <div className="p-6 pb-0">
            <div className="flex items-center gap-3 mb-4">
              <div className="flex items-center justify-center w-9 h-9 rounded-[var(--radius-md)]" style={{ background: "rgba(16, 185, 129, 0.08)" }}>
                <Video className="h-4.5 w-4.5 text-[var(--accent-emerald)]" />
              </div>
              <h3 className="text-sm font-semibold text-[var(--text-primary)]">Ready to Join</h3>
            </div>
          </div>
          <div className="px-6 pb-6 space-y-3">
            {approvedWithToken.map((int: any) => (
              <div key={int.id} className="flex items-center justify-between p-4 rounded-[var(--radius-md)]" style={{ background: "var(--bg-glass)" }}>
                <div>
                  <p className="font-medium text-[var(--text-primary)]">{int.title}</p>
                  <p className="text-sm text-[var(--text-tertiary)]">
                    {new Date(int.scheduled_at).toLocaleDateString()} at {new Date(int.scheduled_at).toLocaleTimeString()}
                  </p>
                </div>
                <Link href={`/interview/${int.unique_token}`}>
                  <Button size="sm" className="gap-2">
                    <Video className="h-3.5 w-3.5" /> Join
                  </Button>
                </Link>
              </div>
            ))}
          </div>
        </GlassCard>
      )}

      <GlassCard delay={0.4}>
        <div className="flex items-center justify-between mb-4">
          <div className="flex items-center gap-3">
            <div className="flex items-center justify-center w-9 h-9 rounded-[var(--radius-md)]" style={{ background: "rgba(59, 130, 246, 0.08)" }}>
              <Calendar className="h-4.5 w-4.5 text-[var(--accent-blue)]" />
            </div>
            <h3 className="text-sm font-semibold text-[var(--text-primary)]">Recent Applications</h3>
          </div>
          <Link href="/dashboard/request-interview" className="text-sm text-[var(--accent-cyan)] hover:text-[var(--accent-blue)] transition-colors">
            + Apply New
          </Link>
        </div>
        {recentRequests.length === 0 ? (
          <p className="text-[var(--text-quaternary)] text-sm py-4 text-center">No interview applications yet.</p>
        ) : (
          <div className="space-y-3">
            {recentRequests.map((req) => (
              <div key={req.id} className="flex items-center justify-between p-4 rounded-[var(--radius-md)]" style={{ background: "var(--bg-glass)" }}>
                <div>
                  <p className="font-medium text-[var(--text-primary)]">{req.title}</p>
                  <p className="text-sm text-[var(--text-tertiary)]">{req.preferred_date} at {req.preferred_time}</p>
                </div>
                <span className={`px-3 py-1 rounded-full text-xs font-medium ${
                  req.status === "pending" ? "badge-warning" :
                  req.status === "approved" ? "badge-success" :
                  "badge-danger"
                }`}>
                  {req.status === "pending" ? "Under Review" : req.status === "approved" ? "Approved" : "Rejected"}
                </span>
              </div>
            ))}
          </div>
        )}
      </GlassCard>
    </div>
  )
}
