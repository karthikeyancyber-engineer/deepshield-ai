"use client"

import { useState, useEffect } from "react"
import { useRouter, useParams } from "next/navigation"
import { motion } from "framer-motion"
import { Shield, Download, ArrowLeft, CheckCircle, AlertTriangle, Eye, Mic, Users, MessageSquare } from "lucide-react"
import { GlassCard } from "@/components/shared/glass-card"
import { Button } from "@/components/ui/button"
import { Progress } from "@/components/ui/progress"
import { apiFetch } from "@/lib/api"

export default function InterviewReportPage() {
  const params = useParams()
  const token = params?.token as string
  const router = useRouter()
  const [report, setReport] = useState<any>(null)
  const [interview, setInterview] = useState<any>(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    apiFetch(`/interviews/by-token/${token}`)
      .then(async (int) => {
        setInterview(int)
        try {
          const r = await apiFetch(`/live/report/${int.id}`)
          setReport(r)
        } catch {}
      })
      .catch(() => {})
      .finally(() => setLoading(false))
  }, [token])

  const downloadPDF = async () => {
    if (!interview) return
    try {
      const token = localStorage.getItem("ds_token")
      const apiBase = `${window.location.origin}/api`
      const res = await fetch(`${apiBase}/reports/pdf/${interview.id}`, {
        headers: { Authorization: `Bearer ${token}` },
      })
      if (!res.ok) throw new Error("Failed")
      const blob = await res.blob()
      const url = URL.createObjectURL(blob)
      const a = document.createElement("a")
      a.href = url; a.download = `interview_report.pdf`
      document.body.appendChild(a); a.click(); a.remove()
      URL.revokeObjectURL(url)
    } catch { alert("Download failed") }
  }

  if (loading) return <div className="min-h-screen bg-[#030712] flex items-center justify-center text-white/50">Loading report...</div>
  if (!report) return (
    <div className="min-h-screen bg-[#030712] flex items-center justify-center p-4">
      <GlassCard className="text-center max-w-md">
        <AlertTriangle className="h-12 w-12 text-yellow-400 mx-auto mb-4" />
        <h2 className="text-xl font-bold text-white mb-2">No Report Available</h2>
        <p className="text-white/50 mb-4">The report is still being generated or the interview hasn&apos;t ended yet.</p>
        <Button onClick={() => router.push("/")}>Return Home</Button>
      </GlassCard>
    </div>
  )

  const scores = report.full_report_data?.scores || {}

  return (
    <div className="min-h-screen bg-[#030712]">
      <div className="absolute inset-0 cyber-grid opacity-20" />
      <header className="sticky top-0 z-40 border-b border-white/10 bg-black/40 backdrop-blur-xl">
        <div className="max-w-4xl mx-auto px-4 sm:px-6 h-16 flex items-center justify-between">
          <div className="flex items-center gap-3">
            <Button onClick={() => router.push("/")} variant="ghost" size="icon"><ArrowLeft className="h-5 w-5" /></Button>
            <h1 className="font-bold text-white">Interview Report</h1>
          </div>
          <Button onClick={downloadPDF} className="gap-2"><Download className="h-4 w-4" /> Download PDF</Button>
        </div>
      </header>

      <main className="relative z-10 max-w-4xl mx-auto px-4 sm:px-6 py-6 space-y-6">
        <motion.div initial={{ opacity: 0, y: -10 }} animate={{ opacity: 1, y: 0 }} className="text-center">
          <Shield className="h-10 w-10 text-cyan-400 mx-auto mb-3" />
          <h2 className="text-2xl font-bold text-white">Interview Complete</h2>
          <p className="text-white/50">{interview?.title}</p>
        </motion.div>

        <div className="grid grid-cols-2 sm:grid-cols-4 gap-3">
          {[
            { label: "Overall Trust", value: `${report.overall_trust_score}%`, color: "text-cyan-400" },
            { label: "Face Score", value: `${report.face_score}%`, color: "text-green-400" },
            { label: "Voice Score", value: `${report.voice_score}%`, color: "text-blue-400" },
            { label: "Eye Contact", value: `${report.eye_contact_score}%`, color: "text-purple-400" },
          ].map((s, i) => (
            <GlassCard key={s.label} delay={i * 0.1}>
              <p className={`text-2xl font-bold ${s.color}`}>{s.value}</p>
              <p className="text-xs text-white/40">{s.label}</p>
            </GlassCard>
          ))}
        </div>

        <GlassCard>
          <h3 className="font-semibold text-white mb-4">Score Breakdown</h3>
          <div className="space-y-4">
            {Object.entries(scores).filter(([k]) => k !== "overall").map(([key, val]) => (
              <div key={key}>
                <div className="flex justify-between text-sm mb-1">
                  <span className="text-white/60 capitalize">{key.replace(/_/g, " ")}</span>
                  <span className="text-white tabular-nums">{String(val)}%</span>
                </div>
                <Progress value={Number(val)} className="h-2" />
              </div>
            ))}
          </div>
        </GlassCard>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <GlassCard>
            <h3 className="font-semibold text-white mb-3 flex items-center gap-2">
              <AlertTriangle className="h-4 w-4 text-yellow-400" /> Security Alerts
            </h3>
            <div className="space-y-2 text-sm">
              <div className="flex justify-between"><span className="text-white/50">Total Alerts</span><span className="text-white">{report.total_alerts}</span></div>
              <div className="flex justify-between"><span className="text-white/50">Critical</span><span className="text-red-400">{report.critical_alerts}</span></div>
              <div className="flex justify-between"><span className="text-white/50">High</span><span className="text-orange-400">{report.high_alerts}</span></div>
              <div className="flex justify-between"><span className="text-white/50">Risk Level</span>
                <span className={`capitalize font-medium ${
                  report.risk_level === "critical" ? "text-red-400" :
                  report.risk_level === "high" ? "text-orange-400" :
                  report.risk_level === "medium" ? "text-yellow-400" : "text-green-400"
                }`}>{report.risk_level}</span>
              </div>
            </div>
          </GlassCard>

          <GlassCard>
            <h3 className="font-semibold text-white mb-3 flex items-center gap-2">
              <CheckCircle className="h-4 w-4 text-green-400" /> AI Summary
            </h3>
            <p className="text-sm text-white/60">{report.ai_security_summary}</p>
          </GlassCard>
        </div>

        {report.communication_summary && (
          <GlassCard>
            <h3 className="font-semibold text-white mb-3 flex items-center gap-2">
              <MessageSquare className="h-4 w-4 text-cyan-400" /> Communication Summary
            </h3>
            <p className="text-sm text-white/60">{report.communication_summary}</p>
          </GlassCard>
        )}

        <Button onClick={downloadPDF} className="w-full gap-2" size="lg">
          <Download className="h-4 w-4" /> Download Full Report (PDF)
        </Button>
      </main>
    </div>
  )
}
