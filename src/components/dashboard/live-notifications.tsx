"use client"

import { motion, AnimatePresence } from "framer-motion"
import { Bell, Shield, AlertTriangle, Info, CheckCircle, X, Settings } from "lucide-react"
import { Button } from "@/components/ui/button"

const notifications = [
  {
    id: 1,
    type: "critical" as const,
    title: "Critical Threat Blocked",
    message: "SQL injection attack from 192.168.1.105 was neutralized by WAF.",
    time: "2 min ago",
    read: false,
  },
  {
    id: 2,
    type: "warning" as const,
    title: "Brute Force Detected",
    message: "847 failed login attempts from 45.33.32.156. Rate limiting applied.",
    time: "15 min ago",
    read: false,
  },
  {
    id: 3,
    type: "success" as const,
    title: "DDoS Attack Mitigated",
    message: "45 Gbps volumetric attack successfully blocked by CDN shield.",
    time: "1 hour ago",
    read: true,
  },
  {
    id: 4,
    type: "info" as const,
    title: "System Update Complete",
    message: "Firewall rules updated to version 3.4.2. All signatures current.",
    time: "3 hours ago",
    read: true,
  },
]

const iconMap = {
  critical: AlertTriangle,
  warning: AlertTriangle,
  success: CheckCircle,
  info: Info,
}

const colorMap = {
  critical: "text-red-400 bg-red-500/10 border-red-500/20",
  warning: "text-orange-400 bg-orange-500/10 border-orange-500/20",
  success: "text-green-400 bg-green-500/10 border-green-500/20",
  info: "text-blue-400 bg-blue-500/10 border-blue-500/20",
}

export function LiveNotifications() {
  const unreadCount = notifications.filter((n) => !n.read).length

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.5, delay: 0.3 }}
      className="rounded-2xl border border-white/10 bg-white/[0.03] backdrop-blur-xl overflow-hidden"
    >
      <div className="flex items-center justify-between px-4 py-3 border-b border-white/5">
        <div className="flex items-center gap-2">
          <Bell className="h-4 w-4 text-yellow-400" />
          <span className="text-sm font-medium text-white">Notifications</span>
          {unreadCount > 0 && (
            <span className="h-5 w-5 rounded-full bg-red-500 text-[10px] font-bold text-white flex items-center justify-center">
              {unreadCount}
            </span>
          )}
        </div>
        <Button variant="ghost" size="icon" className="h-6 w-6">
          <Settings className="h-3 w-3 text-white/40" />
        </Button>
      </div>

      <div className="divide-y divide-white/5 max-h-[280px] overflow-y-auto">
        <AnimatePresence>
          {notifications.map((notif, i) => {
            const Icon = iconMap[notif.type]
            return (
              <motion.div
                key={notif.id}
                initial={{ opacity: 0, x: 10 }}
                animate={{ opacity: 1, x: 0 }}
                transition={{ delay: i * 0.08 }}
                className={`px-4 py-3 hover:bg-white/[0.02] transition-colors ${!notif.read ? "bg-white/[0.02]" : ""}`}
              >
                <div className="flex items-start gap-3">
                  <div className={`h-7 w-7 rounded-lg flex items-center justify-center shrink-0 border ${colorMap[notif.type]}`}>
                    <Icon className="h-3.5 w-3.5" />
                  </div>
                  <div className="flex-1 min-w-0">
                    <div className="flex items-center gap-2">
                      <p className={`text-sm font-medium ${!notif.read ? "text-white" : "text-white/70"}`}>
                        {notif.title}
                      </p>
                      {!notif.read && (
                        <span className="h-1.5 w-1.5 rounded-full bg-cyan-400 shrink-0" />
                      )}
                    </div>
                    <p className="text-xs text-white/40 mt-0.5 line-clamp-2">{notif.message}</p>
                    <span className="text-[10px] text-white/30 mt-1 block">{notif.time}</span>
                  </div>
                </div>
              </motion.div>
            )
          })}
        </AnimatePresence>
      </div>
    </motion.div>
  )
}
