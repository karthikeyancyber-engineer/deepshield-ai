"use client"

import { useState, useEffect } from "react"
import { apiFetch } from "@/lib/api"
import { ClipboardCheck, Loader2, User, CheckCircle, XCircle, Eye, FileText, Inbox } from "lucide-react"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import Link from "next/link"

interface InterviewRequest {
  id: string
  candidate_name: string
  candidate_email: string
  title: string
  preferred_date: string
  preferred_time: string
  duration_minutes: number
  notes: string
  resume_path: string | null
  status: string
  review_note: string
  reviewed_at: string | null
  created_at: string
}

export default function InterviewRequestsPage() {
  const [requests, setRequests] = useState<InterviewRequest[]>([])
  const [loading, setLoading] = useState(true)
  const [reviewingId, setReviewingId] = useState<string | null>(null)
  const [reviewForm, setReviewForm] = useState({ review_note: "", scheduled_at: "" })

  useEffect(() => {
    loadRequests()
  }, [])

  const loadRequests = async () => {
    try {
      const data = await apiFetch("/interview-requests/admin/all")
      setRequests(data)
    } catch (err) {
      console.error(err)
    } finally {
      setLoading(false)
    }
  }

  const handleReview = async (id: string, status: "approved" | "rejected") => {
    try {
      const body: any = { status, review_note: reviewForm.review_note }
      if (status === "approved" && reviewForm.scheduled_at) {
        body.scheduled_at = reviewForm.scheduled_at
      }
      await apiFetch(`/interview-requests/${id}/review`, {
        method: "PUT",
        body: JSON.stringify(body),
      })
      setReviewingId(null)
      setReviewForm({ review_note: "", scheduled_at: "" })
      loadRequests()
    } catch (err: any) {
      alert(err.message || "Failed to review request")
    }
  }

  if (loading) {
    return (
      <div className="flex items-center justify-center py-20">
        <Loader2 className="h-8 w-8 text-[var(--accent-cyan)] animate-spin" />
      </div>
    )
  }

  const pending = requests.filter((r) => r.status === "pending")
  const reviewed = requests.filter((r) => r.status !== "pending")

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-[var(--text-primary)]">Interview Requests</h1>
          <p className="text-[var(--text-tertiary)] text-sm mt-1">Review and manage interview requests ({pending.length} pending)</p>
        </div>
      </div>

      {pending.length > 0 && (
        <div>
          <h2 className="text-sm font-semibold text-[var(--text-secondary)] mb-3 uppercase tracking-wider">Pending Review</h2>
          <div className="space-y-3">
            {pending.map((req) => (
              <div key={req.id} className="surface rounded-[var(--radius-lg)] p-5" style={{ border: "1px solid rgba(245, 158, 11, 0.2)" }}>
                <div className="flex items-start justify-between">
                  <div className="flex items-start gap-4">
                    <div className="h-10 w-10 rounded-[var(--radius-md)] flex items-center justify-center shrink-0" style={{ background: "rgba(245, 158, 11, 0.1)" }}>
                      <User className="h-5 w-5 text-[var(--accent-amber)]" />
                    </div>
                    <div>
                      <p className="font-medium text-[var(--text-primary)]">{req.candidate_name}</p>
                      <p className="text-sm text-[var(--text-tertiary)]">{req.candidate_email}</p>
                      <p className="text-sm text-[var(--accent-cyan)] mt-1">{req.title}</p>
                      <div className="flex items-center gap-4 mt-2">
                        <span className="text-xs text-[var(--text-tertiary)]">{req.duration_minutes}min</span>
                        {req.resume_path && (
                          <a href={req.resume_path} target="_blank" rel="noopener noreferrer"
                            className="text-xs text-[var(--accent-cyan)] flex items-center gap-1 hover:text-[var(--accent-blue)] transition-colors">
                            <FileText className="h-3 w-3" /> View Resume
                          </a>
                        )}
                      </div>
                      {req.notes && <p className="text-xs text-[var(--text-quaternary)] mt-1">Notes: {req.notes}</p>}
                    </div>
                  </div>
                  <div className="flex items-center gap-2">
                    <Button
                      size="sm"
                      variant="outline"
                      className="gap-1 border-[var(--accent-rose)]/30 text-[var(--accent-rose)] hover:bg-[rgba(244,63,94,0.1)]"
                      onClick={() => handleReview(req.id, "rejected")}
                    >
                      <XCircle className="h-3 w-3" /> Reject
                    </Button>
                    <Button
                      size="sm"
                      className="gap-1"
                      onClick={() => setReviewingId(req.id)}
                    >
                      <CheckCircle className="h-3 w-3" /> Approve
                    </Button>
                  </div>
                </div>

                {reviewingId === req.id && (
                  <div className="mt-4 pt-4 border-t border-[var(--border-subtle)] space-y-3">
                    <div className="space-y-2">
                      <Label>Scheduled Date & Time</Label>
                      <Input
                        type="datetime-local"
                        value={reviewForm.scheduled_at}
                        onChange={(e) => setReviewForm((p) => ({ ...p, scheduled_at: e.target.value }))}
                      />
                    </div>
                    <div className="space-y-2">
                      <Label>Note to candidate (optional)</Label>
                      <Input
                        placeholder="Any instructions or details..."
                        value={reviewForm.review_note}
                        onChange={(e) => setReviewForm((p) => ({ ...p, review_note: e.target.value }))}
                      />
                    </div>
                    <div className="flex gap-2">
                      <Button size="sm" onClick={() => handleReview(req.id, "approved")}>
                        Confirm Approval
                      </Button>
                      <Button size="sm" variant="ghost" onClick={() => setReviewingId(null)}>
                        Cancel
                      </Button>
                    </div>
                  </div>
                )}
              </div>
            ))}
          </div>
        </div>
      )}

      {reviewed.length > 0 && (
        <div>
          <h2 className="text-sm font-semibold text-[var(--text-secondary)] mb-3 uppercase tracking-wider">Reviewed</h2>
          <div className="space-y-3">
            {reviewed.map((req) => (
              <div key={req.id} className="surface rounded-[var(--radius-lg)] p-5 opacity-75">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="font-medium text-[var(--text-primary)]">{req.candidate_name} &mdash; {req.title}</p>
                    <div className="flex items-center gap-3 mt-1">
                      <span className="text-sm text-[var(--text-tertiary)]">{req.duration_minutes}min</span>
                      {req.resume_path && (
                        <a href={req.resume_path} target="_blank" rel="noopener noreferrer"
                          className="text-xs text-[var(--accent-cyan)] flex items-center gap-1 hover:text-[var(--accent-blue)] transition-colors">
                          <FileText className="h-3 w-3" /> Resume
                        </a>
                      )}
                    </div>
                    {req.review_note && <p className="text-xs text-[var(--text-quaternary)] mt-1">Note: {req.review_note}</p>}
                  </div>
                  <div className="flex items-center gap-3">
                    <span className={`px-3 py-1 rounded-full text-xs font-medium ${
                      req.status === "approved" ? "badge-success" : "badge-danger"
                    }`}>
                      {req.status}
                    </span>
                    {req.status === "approved" && (
                      <Link href="/admin/live-interviews">
                        <Button size="sm" variant="outline" className="gap-1">
                          <Eye className="h-3 w-3" /> View
                        </Button>
                      </Link>
                    )}
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {requests.length === 0 && (
        <div className="flex flex-col items-center justify-center py-20">
          <Inbox className="h-12 w-12 text-[var(--text-quaternary)] mb-3" />
          <p className="text-sm text-[var(--text-tertiary)]">No interview requests yet</p>
        </div>
      )}
    </div>
  )
}
