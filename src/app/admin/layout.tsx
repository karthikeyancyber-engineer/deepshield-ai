"use client"

import { useEffect } from "react"
import { useRouter } from "next/navigation"
import { AdminSidebar } from "@/components/shared/admin-sidebar"
import { useAuth } from "@/lib/auth-context"
import { Shield } from "lucide-react"

export default function AdminLayout({ children }: { children: React.ReactNode }) {
  const { isAuthenticated, isAdmin, loading } = useAuth()
  const router = useRouter()

  useEffect(() => {
    if (!loading && (!isAuthenticated || !isAdmin)) {
      router.push("/auth/login")
    }
  }, [loading, isAuthenticated, isAdmin, router])

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

  if (!isAuthenticated || !isAdmin) return null

  return (
    <div className="min-h-screen bg-[var(--bg-primary)]">
      <AdminSidebar />
      <div className="ml-[260px] min-h-screen transition-all duration-300">
        <main className="p-6 relative z-10">
          {children}
        </main>
      </div>
    </div>
  )
}
