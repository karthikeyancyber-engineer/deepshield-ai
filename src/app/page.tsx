"use client"

import { useEffect } from "react"
import { useRouter } from "next/navigation"
import { useAuth } from "@/lib/auth-context"
import { Shield, Loader2 } from "lucide-react"

export default function HomePage() {
  const { user, loading, isAuthenticated } = useAuth()
  const router = useRouter()

  useEffect(() => {
    if (loading) return
    if (!isAuthenticated) {
      router.push("/auth/login")
    } else if (user?.role === "admin") {
      router.push("/admin/dashboard")
    } else {
      router.push("/dashboard")
    }
  }, [loading, isAuthenticated, user, router])

  return (
    <div className="min-h-screen bg-[#030712] flex items-center justify-center">
      <div className="text-center">
        <Shield className="h-12 w-12 text-cyan-400 mx-auto mb-4 animate-pulse" />
        <Loader2 className="h-6 w-6 text-white/50 mx-auto animate-spin" />
        <p className="text-white/50 mt-4">Redirecting...</p>
      </div>
    </div>
  )
}
