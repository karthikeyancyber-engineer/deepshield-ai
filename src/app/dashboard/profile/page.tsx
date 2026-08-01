"use client"

import { User, Mail, Phone, Building, ExternalLink, Link2 } from "lucide-react"
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
        <p className="text-white/50 text-sm mt-1">Manage your personal information</p>
      </div>
      <div className="glass-strong rounded-2xl p-6 border border-white/10">
        <div className="flex items-center gap-4 mb-6 pb-6 border-b border-white/10">
          <div className="h-16 w-16 rounded-2xl bg-cyan-500/10 border border-cyan-500/20 flex items-center justify-center">
            <User className="h-8 w-8 text-cyan-400" />
          </div>
          <div>
            <h2 className="text-xl font-bold text-white">{user?.full_name || "Candidate"}</h2>
            <p className="text-sm text-white/50">Candidate Account</p>
          </div>
        </div>
        <div className="space-y-4">
          <div className="grid grid-cols-2 gap-4">
            <div className="space-y-2">
              <Label>Full Name</Label>
              <div className="relative"><User className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-white/40" /><Input defaultValue={user?.full_name || ""} className="pl-10" /></div>
            </div>
            <div className="space-y-2">
              <Label>Email</Label>
              <div className="relative"><Mail className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-white/40" /><Input defaultValue="candidate@example.com" className="pl-10" type="email" /></div>
            </div>
          </div>
          <div className="grid grid-cols-2 gap-4">
            <div className="space-y-2">
              <Label>Phone</Label>
              <div className="relative"><Phone className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-white/40" /><Input defaultValue="+1 (555) 000-0000" className="pl-10" type="tel" /></div>
            </div>
            <div className="space-y-2">
              <Label>Company</Label>
              <div className="relative"><Building className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-white/40" /><Input defaultValue="Acme Corp" className="pl-10" /></div>
            </div>
          </div>
          <div className="grid grid-cols-2 gap-4">
            <div className="space-y-2">
              <Label>LinkedIn URL</Label>
              <div className="relative"><ExternalLink className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-white/40" /><Input defaultValue="linkedin.com/in/example" className="pl-10" /></div>
            </div>
            <div className="space-y-2">
              <Label>GitHub URL</Label>
              <div className="relative"><Link2 className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-white/40" /><Input defaultValue="github.com/example" className="pl-10" /></div>
            </div>
          </div>
          <div className="space-y-2">
            <Label>Skills</Label>
            <textarea className="w-full h-20 rounded-xl border border-white/10 bg-white/5 px-3 py-2 text-sm text-white placeholder:text-white/40 focus:outline-none focus:ring-2 focus:ring-cyan-400/50 resize-none" placeholder="React, TypeScript, Node.js..." defaultValue="React, TypeScript, Python, AWS" />
          </div>
        </div>
        <Button className="mt-6">Save Profile</Button>
      </div>
    </div>
  )
}
