"use client"

import { useState, useEffect } from "react"
import { apiFetch } from "@/lib/api"
import { Video, Play, Square, Eye, Loader2, ExternalLink, ScanFace } from "lucide-react"
import { Button } from "@/components/ui/button"
import Link from "next/link"

interface Interview {
  id: string
  title: string
  candidate_name: string
  candidate_email: string
  unique_token: string
  status: string
  scheduled_at: string
  duration_minutes: number
  overall_trust_score: number | null
  risk_level: string | null
}

export default function LiveInterviewsPage() {
  const [interviews, setInterviews] = useState<Interview[]>([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    const load = async () => {
      try {
        const data = await apiFetch("/interviews/")
        setInterviews(data)
      } catch (err) {
        console.error(err)
      } finally {
        setLoading(false)
      }
    }
    load()
  }, [])

  const live = interviews.filter((i) => i.status === "in_progress")
  const scheduled = interviews.filter((i) => i.status === "scheduled")
  const completed = interviews.filter((i) => i.status === "completed")

  if (loading) {
    return (
      <div className="flex items-center justify-center py-20">
        <Loader2 className="h-8 w-8 text-cyan-400 animate-spin" />
      </div>
    )
  }

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-white">Interviews</h1>
        <p className="text-white/50 text-sm mt-1">Monitor and manage all interviews</p>
      </div>

      {live.length > 0 && (
        <div>
          <h2 className="text-lg font-semibold text-white mb-3 flex items-center gap-2">
            <div className="h-2 w-2 rounded-full bg-red-500 animate-pulse" />
            Live Now
          </h2>
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
            {live.map((int) => (
              <div key={int.id} className="glass-strong rounded-2xl p-6 border border-red-500/20">
                <div className="flex items-center justify-between mb-4">
                  <div className="flex items-center gap-3">
                    <div className="h-2 w-2 rounded-full bg-red-500 animate-pulse" />
                    <span className="text-xs font-medium text-red-400 uppercase">Live</span>
                  </div>
                </div>
                <h3 className="text-lg font-semibold text-white">{int.candidate_name}</h3>
                <p className="text-sm text-white/50 mb-4">{int.title}</p>
                <div className="flex gap-2">
                  <Link href={`/admin/ai-tracker/${int.unique_token}`}>
                    <Button size="sm" className="gap-1 bg-cyan-500 hover:bg-cyan-600">
                      <ScanFace className="h-3 w-3" /> Conduct Interview
                    </Button>
                  </Link>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {scheduled.length > 0 && (
        <div>
          <h2 className="text-lg font-semibold text-white mb-3">Scheduled</h2>
          <div className="space-y-3">
            {scheduled.map((int) => (
              <div key={int.id} className="glass-strong rounded-xl p-5 border border-white/10">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="font-medium text-white">{int.candidate_name} &mdash; {int.title}</p>
                    <p className="text-sm text-white/50">
                      {new Date(int.scheduled_at).toLocaleDateString()} at {new Date(int.scheduled_at).toLocaleTimeString()} ({int.duration_minutes}min)
                    </p>
                    <p className="text-xs text-white/40 mt-1">Token: {int.unique_token}</p>
                  </div>
                  <div className="flex items-center gap-2">
                    <span className="px-3 py-1 rounded-full text-xs font-medium bg-cyan-500/10 text-cyan-400 border border-cyan-500/20">
                      Scheduled
                    </span>
                    <Link href={`/admin/ai-tracker/${int.unique_token}`}>
                      <Button size="sm" className="gap-1 bg-cyan-500 hover:bg-cyan-600">
                        <ScanFace className="h-3 w-3" /> Conduct Interview
                      </Button>
                    </Link>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {completed.length > 0 && (
        <div>
          <h2 className="text-lg font-semibold text-white mb-3">Completed</h2>
          <div className="space-y-3">
            {completed.map((int) => (
              <div key={int.id} className="glass-strong rounded-xl p-5 border border-white/10 opacity-75">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="font-medium text-white">{int.candidate_name} &mdash; {int.title}</p>
                    <p className="text-sm text-white/50">
                      Trust: {int.overall_trust_score ?? "N/A"} | Risk: {int.risk_level ?? "N/A"}
                    </p>
                  </div>
                  <span className="px-3 py-1 rounded-full text-xs font-medium bg-green-500/10 text-green-400 border border-green-500/20">
                    Completed
                  </span>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {interviews.length === 0 && (
        <div className="text-center py-20">
          <Video className="h-12 w-12 text-white/20 mx-auto mb-4" />
          <p className="text-white/50">No interviews yet. Create one from Interview Requests.</p>
        </div>
      )}
    </div>
  )
}
