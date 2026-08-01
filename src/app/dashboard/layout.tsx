"use client"

import { useEffect } from "react"
import { useRouter } from "next/navigation"
import { CandidateSidebar } from "@/components/shared/candidate-sidebar"
import { useAuth } from "@/lib/auth-context"
import { Shield } from "lucide-react"

export default function DashboardLayout({ children }: { children: React.ReactNode }) {
  const { isAuthenticated, isCandidate, loading } = useAuth()
  const router = useRouter()

  useEffect(() => {
    if (!loading && (!isAuthenticated || !isCandidate)) {
      router.push("/auth/login")
    }
  }, [loading, isAuthenticated, isCandidate, router])

  if (loading) {
    return (
      <div className="min-h-screen bg-[var(--bg-primary)] flex items-center justify-center">
        <div className="text-center">
          <Shield className="h-12 w-12 text-[var(--accent-cyan)] mx-auto mb-4 animate-pulse" />
          <p className="text-[var(--text-tertiary)]">Loading...</p>
        </div>
      </div>
    )
  }

  if (!isAuthenticated || !isCandidate) return null

  return (
    <div className="min-h-screen bg-[var(--bg-primary)]">
      <CandidateSidebar />
      <div className="ml-[260px] min-h-screen transition-all duration-300">
        <main className="p-6 relative z-10">
          {children}
        </main>
      </div>
    </div>
  )
}
