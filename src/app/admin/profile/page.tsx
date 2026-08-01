"use client"

import { User, Mail, Shield, Calendar } from "lucide-react"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { useAuth } from "@/lib/auth-context"

export default function ProfilePage() {
  const { user } = useAuth()
  return (
    <div className="space-y-6 max-w-2xl">
      <div>
        <h1 className="text-2xl font-bold text-white">Profile</h1>
        <p className="text-white/50 text-sm mt-1">Manage your account details</p>
      </div>
      <div className="glass-strong rounded-2xl p-6 border border-white/10">
        <div className="flex items-center gap-4 mb-6 pb-6 border-b border-white/10">
          <div className="h-16 w-16 rounded-2xl bg-cyan-500/10 border border-cyan-500/20 flex items-center justify-center">
            <User className="h-8 w-8 text-cyan-400" />
          </div>
          <div>
            <h2 className="text-xl font-bold text-white">{user?.full_name || "Admin User"}</h2>
            <p className="text-sm text-white/50 flex items-center gap-1"><Shield className="h-3 w-3" /> Administrator</p>
          </div>
        </div>
        <div className="space-y-4">
          <div className="space-y-2">
            <Label>Full Name</Label>
            <Input defaultValue={user?.full_name || ""} />
          </div>
          <div className="space-y-2">
            <Label>Email</Label>
            <Input defaultValue="admin@deepshield.ai" type="email" />
          </div>
          <div className="space-y-2">
            <Label>Phone</Label>
            <Input defaultValue="+1 (555) 000-0000" type="tel" />
          </div>
        </div>
        <Button className="mt-6">Save Changes</Button>
      </div>
    </div>
  )
}
