"use client"

import { useState, useEffect } from "react"
import { Users, UserCheck, UserX, Mail, Inbox } from "lucide-react"
import { Button } from "@/components/ui/button"
import { GlassCard } from "@/components/shared/glass-card"
import { PageSkeleton } from "@/components/ui/skeleton"
import { apiFetch } from "@/lib/api"

interface UserItem {
  id: string
  email: string
  full_name: string
  role: string
  is_active: boolean
  created_at: string | null
}

export default function UsersPage() {
  const [users, setUsers] = useState<UserItem[]>([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    const load = async () => {
      try {
        const data = await apiFetch("/admin/users")
        setUsers(data)
      } catch (err) {
        console.error(err)
      } finally {
        setLoading(false)
      }
    }
    load()
  }, [])

  if (loading) return <PageSkeleton />

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-[var(--text-primary)]">Users</h1>
          <p className="text-[var(--text-tertiary)] text-sm mt-1">Manage platform users</p>
        </div>
      </div>

      {users.length === 0 ? (
        <GlassCard>
          <div className="flex flex-col items-center justify-center py-12">
            <Inbox className="h-12 w-12 text-[var(--text-quaternary)] mb-3" />
            <p className="text-sm text-[var(--text-tertiary)]">No users yet</p>
          </div>
        </GlassCard>
      ) : (
        <div className="surface rounded-[var(--radius-lg)] overflow-hidden">
          <table className="w-full">
            <thead>
              <tr className="border-b border-[var(--border-subtle)]">
                <th className="text-left px-5 py-3 text-xs font-medium text-[var(--text-quaternary)] uppercase">User</th>
                <th className="text-left px-5 py-3 text-xs font-medium text-[var(--text-quaternary)] uppercase">Role</th>
                <th className="text-left px-5 py-3 text-xs font-medium text-[var(--text-quaternary)] uppercase">Status</th>
                <th className="text-left px-5 py-3 text-xs font-medium text-[var(--text-quaternary)] uppercase">Joined</th>
              </tr>
            </thead>
            <tbody>
              {users.map((u) => (
                <tr key={u.id} className="border-b border-[var(--border-subtle)] hover:bg-[var(--bg-glass-hover)] transition-colors">
                  <td className="px-5 py-4">
                    <div>
                      <p className="font-medium text-[var(--text-primary)]">{u.full_name}</p>
                      <p className="text-sm text-[var(--text-quaternary)] flex items-center gap-1"><Mail className="h-3 w-3" /> {u.email}</p>
                    </div>
                  </td>
                  <td className="px-5 py-4">
                    <span className={`px-2.5 py-1 rounded-full text-xs font-medium ${
                      u.role === "admin" ? "badge-info" : "badge-success"
                    }`}>{u.role}</span>
                  </td>
                  <td className="px-5 py-4">
                    <span className={`flex items-center gap-1.5 text-sm ${u.is_active ? "text-[var(--accent-emerald)]" : "text-[var(--text-quaternary)]"}`}>
                      {u.is_active ? <UserCheck className="h-3 w-3" /> : <UserX className="h-3 w-3" />}
                      {u.is_active ? "active" : "inactive"}
                    </span>
                  </td>
                  <td className="px-5 py-4 text-sm text-[var(--text-tertiary)]">
                    {u.created_at ? new Date(u.created_at).toLocaleDateString() : "—"}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  )
}
