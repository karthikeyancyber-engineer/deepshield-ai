"use client"

import { FileText, Download, Calendar, AlertTriangle } from "lucide-react"
import { Button } from "@/components/ui/button"

const reports = [
  { id: "1", title: "Frontend Dev - Alex Johnson", date: "2024-01-14", trust: 89, risk: "low", alerts: 2 },
  { id: "2", title: "Backend Eng - Emily Brown", date: "2024-01-13", trust: 95, risk: "low", alerts: 0 },
  { id: "3", title: "DevOps - Tom Davis", date: "2024-01-12", trust: 62, risk: "high", alerts: 7 },
]

export default function ReportsPage() {
  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-white">Reports</h1>
        <p className="text-white/50 text-sm mt-1">Security reports from completed interviews</p>
      </div>
      <div className="space-y-3">
        {reports.map((r) => (
          <div key={r.id} className="glass-strong rounded-xl p-5 border border-white/10 flex items-center justify-between">
            <div className="flex items-center gap-4">
              <div className="h-10 w-10 rounded-xl bg-cyan-500/10 flex items-center justify-center">
                <FileText className="h-5 w-5 text-cyan-400" />
              </div>
              <div>
                <p className="font-medium text-white">{r.title}</p>
                <p className="text-sm text-white/50 flex items-center gap-1"><Calendar className="h-3 w-3" /> {r.date}</p>
              </div>
            </div>
            <div className="flex items-center gap-6">
              <div className="text-center">
                <p className="text-xs text-white/40">Trust</p>
                <p className={`text-lg font-bold ${r.trust >= 80 ? "text-green-400" : r.trust >= 60 ? "text-yellow-400" : "text-red-400"}`}>{r.trust}%</p>
              </div>
              <div className="text-center">
                <p className="text-xs text-white/40">Alerts</p>
                <p className="text-lg font-bold text-white">{r.alerts}</p>
              </div>
              <span className={`px-3 py-1 rounded-full text-xs font-medium ${
                r.risk === "low" ? "bg-green-500/10 text-green-400 border border-green-500/20" :
                r.risk === "high" ? "bg-red-500/10 text-red-400 border border-red-500/20" :
                "bg-yellow-500/10 text-yellow-400 border border-yellow-500/20"
              }`}>{r.risk}</span>
              <Button variant="outline" size="sm" className="gap-1"><Download className="h-3 w-3" /> PDF</Button>
            </div>
          </div>
        ))}
      </div>
    </div>
  )
}
