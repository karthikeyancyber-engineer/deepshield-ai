"use client"

import { FileText, Download, Calendar } from "lucide-react"
import { Button } from "@/components/ui/button"

const reports = [
  { id: "1", title: "Frontend Developer Screening", date: "Jan 10, 2024", trust: 92, risk: "low" },
  { id: "2", title: "Technical Assessment", date: "Jan 5, 2024", trust: 88, risk: "low" },
]

export default function ReportsPage() {
  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-white">Reports</h1>
        <p className="text-white/50 text-sm mt-1">Your interview security reports</p>
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
            <div className="flex items-center gap-4">
              <div className="text-center">
                <p className="text-xs text-white/40">Trust</p>
                <p className="text-lg font-bold text-green-400">{r.trust}%</p>
              </div>
              <Button variant="outline" size="sm" className="gap-1"><Download className="h-3 w-3" /> PDF</Button>
            </div>
          </div>
        ))}
      </div>
    </div>
  )
}
