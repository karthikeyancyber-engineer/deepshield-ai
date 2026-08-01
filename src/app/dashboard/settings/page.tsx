"use client"

import { Settings, Bell, Lock, Globe } from "lucide-react"
import { Button } from "@/components/ui/button"
import { Label } from "@/components/ui/label"
import { Input } from "@/components/ui/input"

export default function SettingsPage() {
  return (
    <div className="space-y-6 max-w-2xl">
      <div>
        <h1 className="text-2xl font-bold text-white">Settings</h1>
        <p className="text-white/50 text-sm mt-1">Manage your preferences</p>
      </div>
      <div className="glass-strong rounded-2xl p-6 border border-white/10 space-y-6">
        <div className="flex items-center gap-3">
          <Bell className="h-5 w-5 text-cyan-400" />
          <h3 className="font-semibold text-white">Notifications</h3>
        </div>
        <div className="space-y-3">
          {["Interview reminders", "Report availability", "Security alerts"].map((item) => (
            <label key={item} className="flex items-center justify-between p-3 rounded-xl bg-white/5 border border-white/10 cursor-pointer">
              <span className="text-sm text-white/80">{item}</span>
              <div className="relative">
                <input type="checkbox" defaultChecked className="peer sr-only" />
                <div className="h-5 w-9 rounded-full bg-white/10 peer-checked:bg-cyan-500 transition-colors" />
              </div>
            </label>
          ))}
        </div>
      </div>
      <div className="glass-strong rounded-2xl p-6 border border-white/10 space-y-6">
        <div className="flex items-center gap-3">
          <Lock className="h-5 w-5 text-cyan-400" />
          <h3 className="font-semibold text-white">Change Password</h3>
        </div>
        <div className="space-y-4">
          <div className="space-y-2"><Label>Current Password</Label><Input type="password" /></div>
          <div className="space-y-2"><Label>New Password</Label><Input type="password" /></div>
          <div className="space-y-2"><Label>Confirm New Password</Label><Input type="password" /></div>
        </div>
      </div>
      <Button>Save Settings</Button>
    </div>
  )
}
