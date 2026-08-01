const API = typeof window !== "undefined"
  ? `${window.location.origin}/api`
  : "http://localhost:8000"

export async function apiFetch(path: string, options: RequestInit = {}) {
  const token = typeof window !== "undefined" ? localStorage.getItem("ds_token") : null
  const headers: Record<string, string> = {
    "Content-Type": "application/json",
    ...(options.headers as Record<string, string> || {}),
  }
  if (token) headers["Authorization"] = `Bearer ${token}`

  const res = await fetch(`${API}${path}`, { ...options, headers })
  if (res.status === 204) return null
  if (!res.ok) {
    const err = await res.json().catch(() => ({ detail: res.statusText }))
    throw new Error(err.detail || "Request failed")
  }
  return res.json()
}

export async function getLiveKitToken(interviewToken: string): Promise<{ token: string; ws_url: string }> {
  return apiFetch(`/livekit/join/${interviewToken}`, { method: "POST" })
}

export function getToken() {
  if (typeof window === "undefined") return null
  return localStorage.getItem("ds_token")
}

export function getUser() {
  if (typeof window === "undefined") return null
  const raw = localStorage.getItem("ds_user")
  return raw ? JSON.parse(raw) : null
}

export function setAuth(data: { access_token: string; role: string; user_id: string; full_name: string }) {
  localStorage.setItem("ds_token", data.access_token)
  localStorage.setItem("ds_user", JSON.stringify({ role: data.role, user_id: data.user_id, full_name: data.full_name }))
  document.cookie = `ds_token=${data.access_token}; path=/; max-age=86400; SameSite=Lax`
}

export function clearAuth() {
  localStorage.removeItem("ds_token")
  localStorage.removeItem("ds_user")
  document.cookie = "ds_token=; path=/; max-age=0"
}

export function isLoggedIn() {
  return !!getToken()
}
