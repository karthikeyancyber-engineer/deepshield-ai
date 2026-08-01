"use client"

import { useState, useEffect } from "react"
import { apiFetch } from "@/lib/api"
import { History, FileText, Clock, Loader2, Inbox } from "lucide-react"

export default function InterviewHistoryPage() {
  const [requests, setRequests] = useState<any[]>([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    const load = async () => {
      try {
        const data = await apiFetch("/interview-requests/my")
        setRequests(data)
      } catch (err) {
        console.error(err)
      } finally {
        setLoading(false)
      }
    }
    load()
  }, [])

  if (loading) {
    return (
      <div className="flex items-center justify-center py-20">
        <Loader2 className="h-8 w-8 text-[var(--accent-cyan)] animate-spin" />
      </div>
    )
  }

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-[var(--text-primary)]">Interview History</h1>
        <p className="text-[var(--text-tertiary)] text-sm mt-1">Your past interview requests and their status</p>
      </div>
      {requests.length === 0 ? (
        <div className="flex flex-col items-center justify-center py-20">
          <Inbox className="h-12 w-12 text-[var(--text-quaternary)] mb-3" />
          <p className="text-sm text-[var(--text-tertiary)]">No interview requests yet</p>
        </div>
      ) : (
        <div className="space-y-3">
          {requests.map((req) => (
            <div key={req.id} className="surface rounded-[var(--radius-lg)] p-5">
              <div className="flex items-center justify-between">
                <div>
                  <p className="font-medium text-[var(--text-primary)]">{req.title}</p>
                  <div className="flex items-center gap-4 mt-1">
                    <span className="text-sm text-[var(--text-tertiary)] flex items-center gap-1">
                      <Clock className="h-3 w-3" /> {req.duration_minutes}min
                    </span>
                    {req.resume_path && (
                      <a href={req.resume_path} target="_blank" rel="noopener noreferrer"
                        className="text-sm text-[var(--accent-cyan)] flex items-center gap-1 hover:text-[var(--accent-blue)] transition-colors">
                        <FileText className="h-3 w-3" /> View Resume
                      </a>
                    )}
                  </div>
                  {req.notes && <p className="text-xs text-[var(--text-quaternary)] mt-2">{req.notes}</p>}
                  {req.review_note && (
                    <p className="text-xs text-[var(--accent-cyan)] mt-2">Admin note: {req.review_note}</p>
                  )}
                </div>
                <span className={`px-3 py-1 rounded-full text-xs font-medium ${
                  req.status === "pending" ? "badge-warning" :
                  req.status === "approved" ? "badge-success" :
                  "badge-danger"
                }`}>
                  {req.status}
                </span>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  )
}
