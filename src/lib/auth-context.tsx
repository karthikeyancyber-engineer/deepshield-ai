"use client"

import { createContext, useContext, useState, useEffect, useCallback, type ReactNode } from "react"
import { useRouter, usePathname } from "next/navigation"
import { apiFetch } from "@/lib/api"

export interface AuthUser {
  user_id: string
  full_name: string
  role: "admin" | "candidate"
  email?: string
}

interface AuthContextType {
  user: AuthUser | null
  token: string | null
  loading: boolean
  login: (email: string, password: string, rememberMe?: boolean) => Promise<void>
  register: (data: {
    email: string
    password: string
    confirm_password: string
    full_name: string
    phone_number?: string
    company?: string
    role?: string
  }) => Promise<void>
  logout: () => void
  isAuthenticated: boolean
  isAdmin: boolean
  isCandidate: boolean
}

const AuthContext = createContext<AuthContextType | undefined>(undefined)

export function AuthProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<AuthUser | null>(null)
  const [token, setToken] = useState<string | null>(null)
  const [loading, setLoading] = useState(true)
  const router = useRouter()

  useEffect(() => {
    const storedToken = localStorage.getItem("ds_token")
    const storedUser = localStorage.getItem("ds_user")
    if (storedToken && storedUser) {
      try {
        setToken(storedToken)
        setUser(JSON.parse(storedUser))
      } catch {
        localStorage.removeItem("ds_token")
        localStorage.removeItem("ds_user")
      }
    }
    setLoading(false)
  }, [])

  const login = useCallback(async (email: string, password: string, rememberMe = false) => {
    const data = await apiFetch("/auth/login", {
      method: "POST",
      body: JSON.stringify({ email, password, remember_me: rememberMe }),
    })
    const authUser: AuthUser = {
      user_id: data.user_id,
      full_name: data.full_name,
      role: data.role,
    }
    localStorage.setItem("ds_token", data.access_token)
    localStorage.setItem("ds_user", JSON.stringify(authUser))
    document.cookie = `ds_token=${data.access_token}; path=/; max-age=${rememberMe ? 30 * 86400 : 86400}; SameSite=Lax`
    setToken(data.access_token)
    setUser(authUser)
    if (typeof window !== "undefined") {
      const params = new URLSearchParams(window.location.search)
      const from = params.get("from")
      if (from) {
        router.push(from)
        return
      }
    }
    if (data.role === "admin") {
      router.push("/admin/dashboard")
    } else {
      router.push("/dashboard")
    }
  }, [router])

  const register = useCallback(async (data: {
    email: string
    password: string
    confirm_password: string
    full_name: string
    phone_number?: string
    company?: string
    role?: string
  }) => {
    const res = await apiFetch("/auth/register", {
      method: "POST",
      body: JSON.stringify(data),
    })
    const authUser: AuthUser = {
      user_id: res.user_id,
      full_name: res.full_name,
      role: res.role,
    }
    localStorage.setItem("ds_token", res.access_token)
    localStorage.setItem("ds_user", JSON.stringify(authUser))
    document.cookie = `ds_token=${res.access_token}; path=/; max-age=86400; SameSite=Lax`
    setToken(res.access_token)
    setUser(authUser)
    if (res.role === "admin") {
      router.push("/admin/dashboard")
    } else {
      router.push("/dashboard")
    }
  }, [router])

  const logout = useCallback(() => {
    localStorage.removeItem("ds_token")
    localStorage.removeItem("ds_user")
    document.cookie = "ds_token=; path=/; max-age=0"
    setToken(null)
    setUser(null)
    router.push("/auth/login")
  }, [router])

  return (
    <AuthContext.Provider
      value={{
        user,
        token,
        loading,
        login,
        register,
        logout,
        isAuthenticated: !!user && !!token,
        isAdmin: user?.role === "admin",
        isCandidate: user?.role === "candidate",
      }}
    >
      {children}
    </AuthContext.Provider>
  )
}

export function useAuth() {
  const context = useContext(AuthContext)
  if (!context) throw new Error("useAuth must be used within AuthProvider")
  return context
}
