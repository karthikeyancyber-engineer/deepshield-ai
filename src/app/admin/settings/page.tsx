"use client"

import { Settings, Shield, Bell, Lock, Globe } from "lucide-react"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"

export default function SettingsPage() {
  return (
    <div className="space-y-6 max-w-2xl">
      <div>
        <h1 className="text-2xl font-bold text-white">Settings</h1>
        <p className="text-white/50 text-sm mt-1">Configure platform settings</p>
      </div>
      <div className="glass-strong rounded-2xl p-6 border border-white/10 space-y-6">
        <div className="flex items-center gap-3">
          <Lock className="h-5 w-5 text-cyan-400" />
          <h3 className="font-semibold text-white">Security</h3>
        </div>
        <div className="space-y-4">
          <div className="space-y-2">
            <Label>Session Timeout (minutes)</Label>
            <Input type="number" defaultValue={1440} className="max-w-xs" />
          </div>
          <div className="space-y-2">
            <Label>Max Login Attempts</Label>
            <Input type="number" defaultValue={5} className="max-w-xs" />
          </div>
        </div>
      </div>
      <div className="glass-strong rounded-2xl p-6 border border-white/10 space-y-6">
        <div className="flex items-center gap-3">
          <Bell className="h-5 w-5 text-cyan-400" />
          <h3 className="font-semibold text-white">Notifications</h3>
        </div>
        <div className="space-y-3">
          {["Email alerts for critical threats", "Daily security summary", "Interview completion notifications"].map((item) => (
            <label key={item} className="flex items-center justify-between p-3 rounded-xl bg-white/5 border border-white/10 cursor-pointer">
              <span className="text-sm text-white/80">{item}</span>
              <div className="relative">
                <input type="checkbox" defaultChecked className="peer sr-only" />
                <div className="h-5 w-9 rounded-full bg-white/10 peer-checked:bg-cyan-500 transition-colors">
                  <div className="h-4 w-4 rounded-full bg-white shadow-sm transition-transform translate-x-0.5 peer-checked:translate-x-4.5 mt-0.5" />
                </div>
              </div>
            </label>
          ))}
        </div>
      </div>
      <Button>Save Settings</Button>
    </div>
  )
}
