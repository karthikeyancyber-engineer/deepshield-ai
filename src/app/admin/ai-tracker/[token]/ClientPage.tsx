"use client"

import { useState, useEffect, useRef } from "react"
import { useParams, useRouter } from "next/navigation"
import { motion } from "framer-motion"
import {
  Shield, ArrowLeft, Loader2, AlertTriangle, Eye, MousePointerClick,
  Monitor, User, Clock, Activity, Video, Phone, Wifi, WifiOff,
} from "lucide-react"
import { Button } from "@/components/ui/button"
import { apiFetch, getLiveKitToken } from "@/lib/api"
import { GlassCard } from "@/components/shared/glass-card"
import Link from "next/link"
import {
  LiveKitRoom,
  ControlBar,
  RoomAudioRenderer,
  ParticipantTile,
  useTracks,
  useLocalParticipant,
  useRemoteParticipants,
  useConnectionState,
} from "@livekit/components-react"
import "@livekit/components-styles"
import { Track } from "livekit-client"

interface TrackingEvent {
  id: string; type: string; severity: string; message: string; confidence: number; timestamp: string
}

interface CandidateAnalysis {
  face_detected: boolean; face_count: number; eye_contact: number;
  gaze_direction: string; head_pose: string; mouse_score: number;
  tab_switches: number; deepfake_score: number; body_language: number;
  trust_score: number; risk_level: string;
  looking_away_duration: number; looking_down_duration: number;
  sustained_looking_away_events: number; sustained_looking_down_events: number;
  alerts: { type: string; severity: string; message: string; confidence: number; timestamp: number }[]
}

export default function AITrackerPage() {
  const params = useParams()
  const token = params?.token as string
  const router = useRouter()

  const [interview, setInterview] = useState<any>(null)
  const [phase, setPhase] = useState<"loading" | "waiting" | "join" | "live" | "ended">("loading")
  const [lkToken, setLkToken] = useState<string | null>(null)
  const [lkUrl, setLkUrl] = useState<string | null>(null)
  const [elapsed, setElapsed] = useState(0)
  const [endedBy, setEndedBy] = useState<string | null>(null)

  const [analysis, setAnalysis] = useState<CandidateAnalysis>({
    face_detected: false, face_count: 0, eye_contact: 0,
    gaze_direction: "Center", head_pose: "Straight", mouse_score: 0,
    tab_switches: 0, deepfake_score: 0, body_language: 0,
    trust_score: 0, risk_level: "low",
    looking_away_duration: 0, looking_down_duration: 0,
    sustained_looking_away_events: 0, sustained_looking_down_events: 0,
    alerts: [],
  })
  const [events, setEvents] = useState<TrackingEvent[]>([])
  const eventIdRef = useRef(0)
  const analysisPollRef = useRef<NodeJS.Timeout | null>(null)

  useEffect(() => {
    const load = async () => {
      try {
        const data = await apiFetch(`/interviews/by-token/${token}`)
        setInterview(data)
        if (data.status === "completed" || data.session_status === "ended") {
          setPhase("ended")
          setEndedBy("Candidate")
        } else if (data.session_status === "in_call") {
          setPhase("waiting")
        } else if (data.session_status === "waiting" || data.session_status === "admin_joined") {
          setPhase("join")
        } else {
          setPhase("waiting")
        }
      } catch {
        router.push("/auth/login")
      }
    }
    load()
  }, [token, router])

  useEffect(() => {
    if (phase !== "waiting" || !interview) return
    const poll = setInterval(async () => {
      try {
        const data = await apiFetch(`/interviews/by-token/${token}/session-status`)
        if (data.session_status === "waiting") {
          clearInterval(poll)
          setPhase("join")
        } else if (data.session_status === "ended") {
          clearInterval(poll)
          setEndedBy("Candidate")
          setPhase("ended")
        }
      } catch {}
    }, 2000)
    return () => clearInterval(poll)
  }, [phase, interview, token])

  const startAnalysisPolling = (interviewId: string) => {
    if (analysisPollRef.current) clearInterval(analysisPollRef.current)

    analysisPollRef.current = setInterval(async () => {
      try {
        const data = await apiFetch(`/video/${interviewId}/analysis`)
        if (data.active) {
          setAnalysis({
            face_detected: data.face_detected ?? false,
            face_count: data.face_count ?? 0,
            eye_contact: data.eye_contact ?? 0,
            gaze_direction: data.gaze_direction ?? "Unknown",
            head_pose: data.head_pose ?? "Unknown",
            mouse_score: data.mouse_score ?? 85,
            tab_switches: data.tab_switches ?? 0,
            deepfake_score: data.deepfake_score ?? 85,
            body_language: data.body_language ?? 50,
            trust_score: data.trust_score ?? 0,
            risk_level: data.risk_level ?? "low",
            looking_away_duration: data.looking_away_duration ?? 0,
            looking_down_duration: data.looking_down_duration ?? 0,
            sustained_looking_away_events: data.sustained_looking_away_events ?? 0,
            sustained_looking_down_events: data.sustained_looking_down_events ?? 0,
            alerts: data.alerts ?? [],
          })

          if (data.alerts && data.alerts.length > 0) {
            const newAlerts = data.alerts.map((a: any) => ({
              id: String(eventIdRef.current++),
              type: a.type,
              severity: a.severity,
              message: a.message,
              confidence: a.confidence ?? 85,
              timestamp: a.timestamp ? new Date(a.timestamp * 1000).toISOString() : new Date().toISOString(),
            }))
            setEvents(prev => {
              const existingIds = new Set(prev.map(e => `${e.type}-${e.message}`))
              const unique = newAlerts.filter((a: any) => !existingIds.has(`${a.type}-${a.message}`))
              return [...unique, ...prev].slice(0, 50)
            })
          }
        }
      } catch {}
    }, 2000)
  }

  const joinCall = async () => {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ video: true, audio: true })
      stream.getTracks().forEach(t => t.stop())

      const data = await getLiveKitToken(token)
      setLkToken(data.token)
      setLkUrl(data.ws_url)
      setPhase("live")

      try { await apiFetch(`/interviews/by-token/${token}/admin-join`, { method: "POST" }) } catch {}

      if (interview?.id) {
        startAnalysisPolling(interview.id)
      }
    } catch (err: any) {
      console.error("[Admin] Camera failed:", err)
      alert("Camera access is required: " + err.message)
    }
  }

  const endInterview = async () => {
    if (analysisPollRef.current) clearInterval(analysisPollRef.current)
    try {
      if (interview?.id) {
        await apiFetch(`/video/${interview.id}/event`, {
          method: "POST",
          body: JSON.stringify({ event_type: "admin_ended" }),
        })
      }
      await apiFetch(`/interviews/by-token/${token}/end-call`, { method: "POST" })
    } catch {}
    setEndedBy("You")
    setPhase("ended")
  }

  useEffect(() => {
    if (phase !== "ended" && phase !== "loading") {
      const timer = setInterval(() => setElapsed(e => e + 1), 1000)
      return () => clearInterval(timer)
    }
  }, [phase])

  useEffect(() => {
    return () => {
      if (analysisPollRef.current) clearInterval(analysisPollRef.current)
    }
  }, [])

  const formatTime = (s: number) => {
    const m = Math.floor(s / 60); const sec = s % 60
    return `${String(m).padStart(2, "0")}:${String(sec).padStart(2, "0")}`
  }

  const severityColor = (s: string) => {
    if (s === "critical") return "border-[var(--accent-rose)]/30 bg-[rgba(244,63,94,0.05)]"
    if (s === "high") return "border-[var(--accent-amber)]/30 bg-[rgba(245,158,11,0.05)]"
    if (s === "medium") return "border-[var(--accent-amber)]/20 bg-[rgba(245,158,11,0.03)]"
    return "border-[var(--accent-emerald)]/30 bg-[rgba(16,185,129,0.05)]"
  }

  const severityDot = (s: string) => {
    if (s === "critical") return "bg-[var(--accent-rose)]"
    if (s === "high") return "bg-[var(--accent-amber)]"
    if (s === "medium") return "bg-[var(--accent-amber)]"
    return "bg-[var(--accent-emerald)]"
  }

  if (phase === "loading") {
    return (
      <div className="min-h-screen flex items-center justify-center" style={{ background: "var(--bg-primary)" }}>
        <Loader2 className="h-8 w-8 text-[var(--accent-cyan)] animate-spin" />
      </div>
    )
  }

  if (phase === "ended") {
    return (
      <div className="min-h-screen flex items-center justify-center p-4" style={{ background: "var(--bg-primary)" }}>
        <GlassCard className="text-center max-w-md">
          <Shield className="h-12 w-12 text-[var(--accent-cyan)] mx-auto mb-4" />
          <h2 className="text-xl font-bold text-[var(--text-primary)] mb-2">
            Interview Ended{endedBy ? ` by ${endedBy}` : ""}
          </h2>
          <p className="text-[var(--text-tertiary)] mb-4">
            {events.length > 0
              ? `${events.length} detection events recorded. Report generated.`
              : "This interview has been completed."}
          </p>
          <Link href="/admin/live-interviews"><Button>Return to Interviews</Button></Link>
        </GlassCard>
      </div>
    )
  }

  if (phase === "waiting") {
    return (
      <div className="min-h-screen flex items-center justify-center p-4" style={{ background: "var(--bg-primary)" }}>
        <GlassCard className="text-center max-w-md">
          <Loader2 className="h-12 w-12 text-[var(--accent-cyan)] mx-auto mb-4 animate-spin" />
          <h2 className="text-xl font-bold text-[var(--text-primary)] mb-2">Waiting for Candidate</h2>
          <p className="text-[var(--text-tertiary)] mb-4">{interview?.candidate_name || "The candidate"} has not joined yet.</p>
          <Link href="/admin/live-interviews"><Button variant="outline">Back to Interviews</Button></Link>
        </GlassCard>
      </div>
    )
  }

  if (phase === "join") {
    return (
      <div style={{ background: "var(--bg-primary)" }} className="min-h-screen">
        <div className="relative z-10 max-w-lg mx-auto px-4 py-12 space-y-6">
          <div className="flex items-center gap-3 mb-4">
            <Link href="/admin/live-interviews">
              <Button variant="ghost" size="icon" className="h-8 w-8"><ArrowLeft className="h-4 w-4" /></Button>
            </Link>
            <Shield className="h-5 w-5 text-[var(--accent-cyan)]" />
            <span className="font-semibold text-[var(--text-primary)] text-sm">{interview?.title || "AI Tracker"}</span>
          </div>
          <motion.div initial={{ opacity: 0, y: -10 }} animate={{ opacity: 1, y: 0 }} className="text-center">
            <div className="relative inline-block mb-4">
              <div className="h-20 w-20 rounded-full flex items-center justify-center mx-auto" style={{ background: "rgba(6, 182, 212, 0.08)", border: "1px solid rgba(6, 182, 212, 0.15)" }}>
                <User className="h-10 w-10 text-[var(--accent-cyan)]" />
              </div>
              <div className="absolute -bottom-1 -right-1 h-6 w-6 rounded-full bg-[var(--accent-emerald)] flex items-center justify-center">
                <span className="h-2 w-2 rounded-full bg-white animate-pulse" />
              </div>
            </div>
            <h1 className="text-2xl font-bold text-[var(--text-primary)] mb-2">Candidate is Waiting</h1>
            <p className="text-[var(--text-tertiary)]">{interview?.candidate_name} has joined and is waiting for you.</p>
          </motion.div>
          <GlassCard>
            <div className="space-y-4">
              <div className="aspect-video rounded-[var(--radius-lg)] flex items-center justify-center" style={{ background: "var(--bg-secondary)" }}>
                <div className="text-center">
                  <User className="h-12 w-12 text-[var(--text-quaternary)] mx-auto mb-2" />
                  <p className="text-sm text-[var(--text-quaternary)]">Candidate will appear here</p>
                </div>
              </div>
              <Button onClick={joinCall} className="w-full" size="lg">
                <Video className="h-4 w-4 mr-2" /> Join & Start Interview
              </Button>
            </div>
          </GlassCard>
        </div>
      </div>
    )
  }

  const trustColor = analysis.trust_score > 80 ? "green" : analysis.trust_score > 60 ? "yellow" : "red"

  return (
    <LiveKitRoom
      serverUrl={lkUrl ?? undefined}
      token={lkToken ?? undefined}
      connect={true}
      video={true}
      audio={true}
      className="min-h-screen"
      style={{ background: "var(--bg-primary)" }}
      onDisconnected={() => {
        if (analysisPollRef.current) clearInterval(analysisPollRef.current)
        setEndedBy("Candidate")
        setPhase("ended")
      }}
    >
      <div className="min-h-screen flex flex-col" style={{ background: "var(--bg-primary)" }}>
        <header className="border-b border-[var(--border-subtle)] backdrop-blur-xl px-4 py-2 flex items-center justify-between shrink-0 z-10" style={{ background: "var(--bg-overlay)" }}>
          <div className="flex items-center gap-3">
            <Link href="/admin/live-interviews">
              <Button variant="ghost" size="icon" className="h-8 w-8"><ArrowLeft className="h-4 w-4" /></Button>
            </Link>
            <Shield className="h-5 w-5 text-[var(--accent-cyan)]" />
            <div>
              <span className="font-semibold text-[var(--text-primary)] text-sm">{interview?.title || "AI Tracker"}</span>
              <p className="text-xs text-[var(--text-quaternary)]">{interview?.candidate_name}</p>
            </div>
          </div>
          <div className="flex items-center gap-3">
            <AdminConnectionStatus />
            <div className="flex items-center gap-1.5 px-3 py-1 rounded-full" style={{ background: "var(--bg-glass)" }}>
              <Clock className="h-3.5 w-3.5 text-[var(--accent-cyan)]" />
              <span className="text-sm text-[var(--text-primary)] font-mono tabular-nums">{formatTime(elapsed)}</span>
            </div>
            <div className={`flex items-center gap-1.5 px-3 py-1 rounded-full ${
              analysis.risk_level === "critical" ? "bg-red-500/10" :
              analysis.risk_level === "high" ? "bg-orange-500/10" :
              analysis.risk_level === "medium" ? "bg-yellow-500/10" : "bg-green-500/10"
            }`}>
              <Shield className={`h-3.5 w-3.5 ${
                analysis.risk_level === "critical" ? "text-red-400" :
                analysis.risk_level === "high" ? "text-orange-400" :
                analysis.risk_level === "medium" ? "text-yellow-400" : "text-green-400"
              }`} />
              <span className={`text-sm font-medium ${
                analysis.risk_level === "critical" ? "text-red-400" :
                analysis.risk_level === "high" ? "text-orange-400" :
                analysis.risk_level === "medium" ? "text-yellow-400" : "text-green-400"
              }`}>{analysis.trust_score}%</span>
            </div>
          </div>
        </header>

        <div className="flex-1 flex flex-col lg:flex-row overflow-hidden">
          <div className="flex-1 flex flex-col p-3 gap-3 overflow-y-auto">
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
              <div className="relative rounded-[var(--radius-lg)] overflow-hidden aspect-video" style={{ background: "var(--bg-secondary)" }}>
                <AdminCandidateVideo />
                <div className="absolute top-2 left-2 px-2 py-0.5 rounded text-xs font-medium z-10 flex items-center gap-1.5" style={{ background: "var(--bg-overlay)" }}>
                  <AdminLiveIndicator />
                </div>
                <div className="absolute top-2 right-2 px-2 py-0.5 rounded text-xs font-medium z-10" style={{ background: "var(--bg-overlay)", color: "var(--text-tertiary)" }}>
                  {interview?.candidate_name || "Candidate"}
                </div>
              </div>

              <div className="rounded-[var(--radius-lg)] p-4 space-y-3 surface">
                <h3 className="text-sm font-semibold text-[var(--text-primary)] flex items-center gap-2">
                  <Activity className="h-4 w-4 text-[var(--accent-cyan)]" /> AI Live Metrics
                </h3>
                <div className="grid grid-cols-2 gap-3">
                  <MetricCard icon={<User className="h-4 w-4" />} label="Face Detection" value={analysis.face_detected ? `${analysis.face_count} detected` : "None"} color={analysis.face_detected ? "green" : "red"} />
                  <MetricCard icon={<Eye className="h-4 w-4" />} label="Eye Contact" value={`${analysis.eye_contact}%`} color={analysis.eye_contact > 70 ? "green" : "yellow"} />
                  <MetricCard icon={<MousePointerClick className="h-4 w-4" />} label="Gaze" value={analysis.gaze_direction} color={analysis.gaze_direction === "Center" ? "green" : analysis.looking_away_duration >= 3 ? "red" : "yellow"} />
                  <MetricCard icon={<Monitor className="h-4 w-4" />} label="Tab Switches" value={String(analysis.tab_switches)} color={analysis.tab_switches === 0 ? "green" : analysis.tab_switches > 3 ? "red" : "yellow"} />
                  <MetricCard icon={<Shield className="h-4 w-4" />} label="Deepfake Score" value={`${analysis.deepfake_score}%`} color={analysis.deepfake_score > 80 ? "green" : analysis.deepfake_score > 50 ? "yellow" : "red"} />
                  <MetricCard icon={<Activity className="h-4 w-4" />} label="Body Language" value={`${analysis.body_language}%`} color={analysis.body_language > 70 ? "green" : "yellow"} />
                  <MetricCard icon={<AlertTriangle className="h-4 w-4" />} label="Looking Away" value={analysis.looking_away_duration >= 3 ? `${analysis.looking_away_duration.toFixed(1)}s !` : `${analysis.looking_away_duration.toFixed(1)}s`} color={analysis.looking_away_duration >= 5 ? "red" : analysis.looking_away_duration >= 3 ? "yellow" : "green"} />
                  <MetricCard icon={<AlertTriangle className="h-4 w-4" />} label="Suspect Alerts" value={`${analysis.sustained_looking_away_events}`} color={analysis.sustained_looking_away_events > 0 ? "red" : "green"} />
                </div>
                <div className="pt-2 border-t border-[var(--border-subtle)]">
                  <div className="flex items-center justify-between mb-1">
                    <span className="text-xs text-[var(--text-quaternary)]">Overall Trust Score</span>
                    <span className={`text-sm font-bold text-[var(--accent-${trustColor === "green" ? "emerald" : trustColor === "yellow" ? "amber" : "rose"})]`}>{analysis.trust_score}%</span>
                  </div>
                  <div className="w-full h-2 rounded-full overflow-hidden" style={{ background: "var(--bg-glass)" }}>
                    <div className="h-full rounded-full transition-all duration-500" style={{ width: `${analysis.trust_score}%`, background: `var(--accent-${trustColor === "green" ? "emerald" : trustColor === "yellow" ? "amber" : "rose"})` }} />
                  </div>
                </div>
              </div>
            </div>
          </div>

          <div className="w-full lg:w-80 border-t lg:border-t-0 lg:border-l border-[var(--border-subtle)] flex flex-col overflow-hidden shrink-0" style={{ background: "var(--bg-secondary)" }}>
            <div className="flex items-center justify-between p-3 border-b border-[var(--border-subtle)]">
              <h3 className="text-sm font-semibold text-[var(--text-primary)] flex items-center gap-2">
                <AlertTriangle className="h-4 w-4 text-[var(--accent-amber)]" /> AI Detection Events
              </h3>
              <span className="text-xs text-[var(--text-quaternary)]">{events.length}</span>
            </div>
            <div className="flex-1 overflow-y-auto p-3 space-y-2">
              {events.length === 0 ? (
                <p className="text-xs text-[var(--text-quaternary)] text-center py-8">Waiting for analysis...</p>
              ) : events.map((evt) => (
                <div key={evt.id} className={`p-2.5 rounded-[var(--radius-md)] border ${severityColor(evt.severity)}`}>
                  <div className="flex items-center gap-2 mb-1">
                    <span className={`h-1.5 w-1.5 rounded-full ${severityDot(evt.severity)}`} />
                    <span className="text-xs font-medium text-[var(--text-primary)] capitalize">{evt.type.replace(/_/g, " ")}</span>
                    <span className="text-[10px] text-[var(--text-quaternary)] ml-auto">{new Date(evt.timestamp).toLocaleTimeString()}</span>
                  </div>
                  <p className="text-xs text-[var(--text-tertiary)]">{evt.message}</p>
                  <p className="text-[10px] text-[var(--text-quaternary)] mt-0.5">Confidence: {evt.confidence}%</p>
                </div>
              ))}
            </div>
          </div>
        </div>

        <div className="border-t border-[var(--border-subtle)] px-4 py-2 flex items-center justify-center gap-3 z-10" style={{ background: "var(--bg-overlay)" }}>
          <ControlBar />
          <Button onClick={endInterview} variant="destructive" size="sm" className="gap-1 rounded-full px-4 ml-2">
            <Phone className="h-3.5 w-3.5" /> End
          </Button>
        </div>
      </div>

      <div className="fixed bottom-20 right-4 w-44 aspect-video rounded-[var(--radius-lg)] overflow-hidden border-2 border-[var(--border-strong)] shadow-lg z-50" style={{ background: "var(--bg-secondary)" }}>
        <AdminSelfVideo />
      </div>

      <RoomAudioRenderer />
    </LiveKitRoom>
  )
}

function AdminConnectionStatus() {
  const state = useConnectionState()
  const isConnected = state === "connected"
  return (
    <div className={`flex items-center gap-1.5 px-3 py-1 rounded-full ${
      isConnected ? "bg-[rgba(16,185,129,0.1)]" : "bg-[rgba(245,158,11,0.1)]"
    }`}>
      {isConnected ? <Wifi className="h-3.5 w-3.5 text-[var(--accent-emerald)]" /> : <WifiOff className="h-3.5 w-3.5 text-[var(--accent-amber)]" />}
      <span className={`text-xs font-medium ${isConnected ? "text-[var(--accent-emerald)]" : "text-[var(--accent-amber)]"}`}>
        {isConnected ? "Live" : "Connecting"}
      </span>
    </div>
  )
}

function AdminCandidateVideo() {
  const remoteParticipants = useRemoteParticipants()
  const tracks = useTracks([Track.Source.Camera])
  const { localParticipant } = useLocalParticipant()
  const remoteTracks = tracks.filter(t => t.participant.identity !== localParticipant?.identity)

  if (remoteTracks.length > 0) {
    return (
      <ParticipantTile
        trackRef={remoteTracks[0]}
        className="w-full h-full object-cover"
      />
    )
  }

  return (
    <div className="w-full h-full flex items-center justify-center">
      <div className="text-center">
        <User className="h-16 w-16 text-[var(--text-quaternary)] mx-auto mb-3" />
        <p className="text-sm text-[var(--text-quaternary)]">Waiting for candidate...</p>
      </div>
    </div>
  )
}

function AdminLiveIndicator() {
  const remoteParticipants = useRemoteParticipants()
  if (remoteParticipants.length > 0) {
    return <><span className="h-1.5 w-1.5 rounded-full bg-[var(--accent-rose)] animate-pulse" /> LIVE</>
  }
  return <><span className="h-1.5 w-1.5 rounded-full" style={{ background: "var(--text-quaternary)" }} /> OFFLINE</>
}

function AdminSelfVideo() {
  const tracks = useTracks([Track.Source.Camera])
  const { localParticipant } = useLocalParticipant()
  const localTracks = tracks.filter(t => t.participant.identity === localParticipant?.identity)

  if (localTracks.length > 0) {
    return (
      <div className="w-full h-full relative">
        <ParticipantTile
          trackRef={localTracks[0]}
          className="w-full h-full object-cover"
        />
        <div className="absolute bottom-1 left-1 text-[10px] text-[var(--text-tertiary)] px-2 py-0.5 rounded z-10" style={{ background: "var(--bg-overlay)" }}>You</div>
      </div>
    )
  }

  return (
    <div className="w-full h-full flex items-center justify-center" style={{ background: "var(--bg-secondary)" }}>
      <Shield className="h-6 w-6 text-[var(--text-quaternary)]" />
    </div>
  )
}

function MetricCard({ icon, label, value, color }: { icon: React.ReactNode; label: string; value: string; color: string }) {
  const colorMap: Record<string, { border: string; bg: string; text: string }> = {
    green: { border: "rgba(16, 185, 129, 0.15)", bg: "rgba(16, 185, 129, 0.05)", text: "var(--accent-emerald)" },
    yellow: { border: "rgba(245, 158, 11, 0.15)", bg: "rgba(245, 158, 11, 0.05)", text: "var(--accent-amber)" },
    red: { border: "rgba(244, 63, 94, 0.15)", bg: "rgba(244, 63, 94, 0.05)", text: "var(--accent-rose)" },
    cyan: { border: "rgba(6, 182, 212, 0.15)", bg: "rgba(6, 182, 212, 0.05)", text: "var(--accent-cyan)" },
  }
  const c = colorMap[color] || colorMap.cyan

  return (
    <div className="p-2.5 rounded-[var(--radius-md)]" style={{ border: `1px solid ${c.border}`, background: c.bg }}>
      <div className="flex items-center gap-2 mb-1">
        <span style={{ color: c.text }}>{icon}</span>
        <span className="text-[10px] text-[var(--text-quaternary)]">{label}</span>
      </div>
      <p className="text-sm font-semibold" style={{ color: c.text }}>{value}</p>
    </div>
  )
}
