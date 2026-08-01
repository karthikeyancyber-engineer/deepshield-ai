"use client"

import { useState } from "react"
import { useAuth } from "@/lib/auth-context"
import { apiFetch } from "@/lib/api"
import { ClipboardList, Plus, Loader2, CheckCircle2, Upload, FileText, X } from "lucide-react"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { useRouter } from "next/navigation"

export default function RequestInterviewPage() {
  const { user } = useAuth()
  const router = useRouter()
  const [loading, setLoading] = useState(false)
  const [success, setSuccess] = useState(false)
  const [form, setForm] = useState({
    title: "",
    duration_minutes: 30,
    notes: "",
  })
  const [resumeFile, setResumeFile] = useState<File | null>(null)
  const [resumeName, setResumeName] = useState("")
  const [uploadingResume, setUploadingResume] = useState(false)

  const handleFileSelect = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0]
    if (file) {
      if (file.type !== "application/pdf") {
        alert("Only PDF files are allowed")
        return
      }
      if (file.size > 10 * 1024 * 1024) {
        alert("File size must be under 10MB")
        return
      }
      setResumeFile(file)
      setResumeName(file.name)
    }
  }

  const removeResume = () => {
    setResumeFile(null)
    setResumeName("")
  }

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!form.title) return
    setLoading(true)
    try {
      let resumePath: string | null = null

      if (resumeFile) {
        setUploadingResume(true)
        const formData = new FormData()
        formData.append("file", resumeFile)
        const uploadRes = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/interview-requests/upload-resume`, {
          method: "POST",
          body: formData,
        })
        const uploadData = await uploadRes.json()
        resumePath = uploadData.path || null
        setUploadingResume(false)
      }

      await apiFetch("/interview-requests/", {
        method: "POST",
        body: JSON.stringify({ ...form, resume_path: resumePath }),
      })
      setSuccess(true)
      setTimeout(() => router.push("/dashboard/interview-history"), 2000)
    } catch (err: any) {
      alert(err.message || "Failed to submit request")
    } finally {
      setLoading(false)
      setUploadingResume(false)
    }
  }

  const update = (field: string, value: any) => setForm((prev) => ({ ...prev, [field]: value }))

  if (success) {
    return (
      <div className="flex flex-col items-center justify-center py-20">
        <CheckCircle2 className="h-16 w-16 text-[var(--accent-emerald)] mb-4" />
        <h2 className="text-xl font-bold text-[var(--text-primary)] mb-2">Request Submitted!</h2>
        <p className="text-[var(--text-tertiary)] text-sm">Your interview request has been sent to the admin for review.</p>
      </div>
    )
  }

  return (
    <div className="space-y-6 max-w-2xl">
      <div>
        <h1 className="text-2xl font-bold text-[var(--text-primary)]">Request Interview</h1>
        <p className="text-[var(--text-tertiary)] text-sm mt-1">Submit your interview request with resume</p>
      </div>
      <form onSubmit={handleSubmit} className="surface border-gradient rounded-[var(--radius-lg)] p-6 space-y-5">
        <div className="space-y-2">
          <Label>Interview Title *</Label>
          <Input
            placeholder="e.g. Frontend Developer Interview"
            value={form.title}
            onChange={(e) => update("title", e.target.value)}
            required
          />
        </div>

        <div className="space-y-2">
          <Label>Resume (PDF)</Label>
          {resumeName ? (
            <div className="flex items-center justify-between p-3 rounded-[var(--radius-md)]" style={{ background: "var(--bg-glass)", border: "1px solid var(--border-default)" }}>
              <div className="flex items-center gap-2">
                <FileText className="h-4 w-4 text-[var(--accent-cyan)]" />
                <span className="text-sm text-[var(--text-primary)]">{resumeName}</span>
              </div>
              <button type="button" onClick={removeResume} className="p-1 rounded-[var(--radius-sm)] text-[var(--text-quaternary)] hover:text-[var(--accent-rose)] hover:bg-[rgba(244,63,94,0.1)] transition-colors">
                <X className="h-4 w-4" />
              </button>
            </div>
          ) : (
            <label className="flex items-center justify-center gap-2 p-6 rounded-[var(--radius-md)] cursor-pointer transition-colors" style={{ background: "var(--bg-glass)", border: "2px dashed var(--border-default)" }}>
              <Upload className="h-5 w-5 text-[var(--text-quaternary)]" />
              <span className="text-sm text-[var(--text-tertiary)]">Click to upload PDF (max 10MB)</span>
              <input type="file" accept=".pdf,application/pdf" onChange={handleFileSelect} className="hidden" />
            </label>
          )}
        </div>

        <div className="space-y-2">
          <Label>Duration (minutes)</Label>
          <Input
            type="number"
            value={form.duration_minutes}
            min={5}
            max={180}
            onChange={(e) => update("duration_minutes", parseInt(e.target.value))}
          />
        </div>

        <div className="space-y-2">
          <Label>Notes (optional)</Label>
          <textarea
            className="w-full h-24 rounded-[var(--radius-md)] border border-[var(--border-default)] bg-[var(--bg-glass)] px-3 py-2 text-sm text-[var(--text-primary)] placeholder:text-[var(--text-quaternary)] focus:outline-none focus:ring-2 focus:ring-[var(--accent-cyan)]/50 resize-none"
            placeholder="Any specific topics or requirements..."
            value={form.notes}
            onChange={(e) => update("notes", e.target.value)}
          />
        </div>

        <Button type="submit" disabled={loading} className="gap-2">
          {loading ? <Loader2 className="h-4 w-4 animate-spin" /> : <Plus className="h-4 w-4" />}
          Submit Request
        </Button>
      </form>
    </div>
  )
}
