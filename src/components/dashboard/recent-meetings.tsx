"use client"

import { motion } from "framer-motion"
import { Video, Users, Clock, Play, ChevronRight, Calendar } from "lucide-react"
import { Button } from "@/components/ui/button"
import { StatusBadge } from "@/components/shared/status-badge"

const meetings = [
  {
    id: 1,
    title: "Security Briefing",
    participants: ["Alex Chen", "Sarah Kim", "+3"],
    duration: "45 min",
    time: "Today, 10:00 AM",
    status: "completed" as const,
    threatLevel: "low",
  },
  {
    id: 2,
    title: "Incident Response Review",
    participants: ["Mike Ross", "Diana Prince", "+5"],
    duration: "1h 20min",
    time: "Today, 2:30 PM",
    status: "completed" as const,
    threatLevel: "medium",
  },
  {
    id: 3,
    title: "SOC Team Standup",
    participants: ["John Doe", "Jane Smith", "+2"],
    duration: "30 min",
    time: "Tomorrow, 9:00 AM",
    status: "scheduled" as const,
    threatLevel: "low",
  },
]

export function RecentMeetings() {
  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.5, delay: 0.25 }}
      className="rounded-2xl border border-white/10 bg-white/[0.03] backdrop-blur-xl overflow-hidden"
    >
      <div className="flex items-center justify-between px-4 py-3 border-b border-white/5">
        <div className="flex items-center gap-2">
          <Video className="h-4 w-4 text-purple-400" />
          <span className="text-sm font-medium text-white">Recent Meetings</span>
        </div>
        <Button variant="ghost" size="sm" className="text-xs text-white/40 h-7">
          View All <ChevronRight className="h-3 w-3 ml-1" />
        </Button>
      </div>

      <div className="divide-y divide-white/5">
        {meetings.map((meeting, i) => (
          <motion.div
            key={meeting.id}
            initial={{ opacity: 0, x: -10 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ delay: i * 0.08 }}
            className="px-4 py-3 hover:bg-white/[0.02] transition-colors cursor-pointer group"
          >
            <div className="flex items-start justify-between mb-2">
              <div>
                <p className="text-sm font-medium text-white group-hover:text-cyan-400 transition-colors">
                  {meeting.title}
                </p>
                <div className="flex items-center gap-3 mt-1 text-[11px] text-white/40">
                  <span className="flex items-center gap-1">
                    <Calendar className="h-3 w-3" />
                    {meeting.time}
                  </span>
                  <span className="flex items-center gap-1">
                    <Clock className="h-3 w-3" />
                    {meeting.duration}
                  </span>
                </div>
              </div>
              {meeting.status === "scheduled" ? (
                <span className="text-[10px] px-2 py-0.5 rounded-full bg-cyan-500/10 text-cyan-400 border border-cyan-500/20">
                  Upcoming
                </span>
              ) : (
                <Play className="h-4 w-4 text-white/30 group-hover:text-cyan-400 transition-colors" />
              )}
            </div>

            <div className="flex items-center justify-between">
              <div className="flex items-center gap-1.5">
                <Users className="h-3 w-3 text-white/30" />
                <span className="text-[11px] text-white/40">
                  {meeting.participants.join(", ")}
                </span>
              </div>
              <StatusBadge status={meeting.threatLevel as any} />
            </div>
          </motion.div>
        ))}
      </div>
    </motion.div>
  )
}
