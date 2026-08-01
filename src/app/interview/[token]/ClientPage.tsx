"use client"

import { useState, useEffect, useRef, useCallback } from "react"
import { useRouter, useParams } from "next/navigation"
import { motion } from "framer-motion"
import {
  Video, VideoOff, Mic, MicOff, Phone, Shield, Clock,
  Loader2, CheckCircle, AlertTriangle, Wifi, WifiOff,
} from "lucide-react"
import { GlassCard } from "@/components/shared/glass-card"
import { Button } from "@/components/ui/button"
import { apiFetch, getUser, getLiveKitToken } from "@/lib/api"
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

export default function InterviewPage() {
  const params = useParams()
  const token = params?.token as string
  const router = useRouter()
  const user = getUser()

  const [interview, setInterview] = useState<any>(null)
  const [phase, setPhase] = useState<"loading" | "join" | "waiting" | "live" | "ended">("loading")
  const [lkToken, setLkToken] = useState<string | null>(null)
  const [lkUrl, setLkUrl] = useState<string | null>(null)
  const [elapsed, setElapsed] = useState(0)
  const [cameraError, setCameraError] = useState<string | null>(null)
  const [endedBy, setEndedBy] = useState<string | null>(null)

  const interviewIdRef = useRef<string | null>(null)
  const frameIntervalRef = useRef<NodeJS.Timeout | null>(null)

  useEffect(() => {
    if (!user) { router.push("/auth/login"); return }
    apiFetch(`/interviews/by-token/${token}`)
      .then((data) => {
        setInterview(data)
        interviewIdRef.current = data.id
        if (data.status === "completed" || data.session_status === "ended") {
          setPhase("ended")
          setEndedBy("HR")
        } else if (data.session_status === "in_call") {
          setPhase("waiting")
        } else {
          setPhase("join")
        }
      })
      .catch(() => router.push("/auth/login"))
  }, [token, router])

  useEffect(() => {
    if (phase !== "live" || !interviewIdRef.current) return

    const interviewId = interviewIdRef.current

    const captureFrame = async () => {
      try {
        const videoEl = document.querySelector("video")
        if (!videoEl) return

        const canvas = document.createElement("canvas")
        canvas.width = videoEl.videoWidth || 640
        canvas.height = videoEl.videoHeight || 480
        const ctx = canvas.getContext("2d")
        if (!ctx) return

        ctx.drawImage(videoEl, 0, 0, canvas.width, canvas.height)
        const base64 = canvas.toDataURL("image/jpeg", 0.6).split(",")[1]
        if (!base64) return

        await apiFetch(`/video/${interviewId}/frame`, {
          method: "POST",
          body: JSON.stringify({ frame: base64 }),
        })
      } catch {}
    }

    frameIntervalRef.current = setInterval(captureFrame, 2000)
    captureFrame()

    return () => {
      if (frameIntervalRef.current) clearInterval(frameIntervalRef.current)
    }
  }, [phase])

  useEffect(() => {
    if (phase !== "live" || !interviewIdRef.current) return

    const interviewId = interviewIdRef.current

    const sendEvent = async (eventType: string, details: any = {}) => {
      try {
        await apiFetch(`/video/${interviewId}/event`, {
          method: "POST",
          body: JSON.stringify({ event_type: eventType, details }),
        })
      } catch {}
    }

    const handleVisibilityChange = () => {
      if (document.hidden) {
        sendEvent("tab_switch", { hidden: true })
      } else {
        sendEvent("tab_return", { hidden: false })
      }
    }

    const handleBlur = () => {
      sendEvent("focus_loss", { focused: false })
    }

    const handleFocus = () => {
      sendEvent("focus_gain", { focused: true })
    }

    const handleFullscreenChange = () => {
      if (!document.fullscreenElement) {
        sendEvent("fullscreen_exit")
      }
    }

    const handleBeforeUnload = (e: BeforeUnloadEvent) => {
      sendEvent("page_leave")
      e.preventDefault()
    }

    document.addEventListener("visibilitychange", handleVisibilityChange)
    window.addEventListener("blur", handleBlur)
    window.addEventListener("focus", handleFocus)
    document.addEventListener("fullscreenchange", handleFullscreenChange)
    window.addEventListener("beforeunload", handleBeforeUnload)

    return () => {
      document.removeEventListener("visibilitychange", handleVisibilityChange)
      window.removeEventListener("blur", handleBlur)
      window.removeEventListener("focus", handleFocus)
      document.removeEventListener("fullscreenchange", handleFullscreenChange)
      window.removeEventListener("beforeunload", handleBeforeUnload)
    }
  }, [phase])

  useEffect(() => {
    if (phase !== "live" || !interviewIdRef.current) return

    const interviewId = interviewIdRef.current
    const poll = setInterval(async () => {
      try {
        const data = await apiFetch(`/interviews/by-token/${token}/session-status`)
        if (data.session_status === "ended") {
          setEndedBy("HR")
          setPhase("ended")
        }
      } catch {}
    }, 3000)

    return () => clearInterval(poll)
  }, [phase, token])

  useEffect(() => {
    if (phase === "live") {
      const timer = setInterval(() => setElapsed(e => e + 1), 1000)
      return () => clearInterval(timer)
    }
  }, [phase])

  const joinCall = async () => {
    setCameraError(null)
    try {
      const stream = await navigator.mediaDevices.getUserMedia({
        video: { facingMode: "user", width: { ideal: 1280 }, height: { ideal: 720 } },
        audio: true,
      })
      stream.getTracks().forEach(t => t.stop())

      const data = await getLiveKitToken(token)
      setLkToken(data.token)
      setLkUrl(data.ws_url)
      setPhase("live")
    } catch (err: any) {
      console.error("[Interview] Camera failed:", err)
      setCameraError("Camera and microphone access is required. Please allow access and try again.")
    }
  }

  const endInterview = async () => {
    if (frameIntervalRef.current) clearInterval(frameIntervalRef.current)
    try {
      const interviewId = interviewIdRef.current
      if (interviewId) {
        await apiFetch(`/video/${interviewId}/event`, {
          method: "POST",
          body: JSON.stringify({ event_type: "candidate_ended" }),
        })
      }
      await apiFetch(`/interviews/by-token/${token}/end-call`, { method: "POST" })
    } catch {}
    setEndedBy("You")
    setPhase("ended")
  }

  const formatTime = (s: number) => {
    const m = Math.floor(s / 60); const sec = s % 60
    return `${String(m).padStart(2, "0")}:${String(sec).padStart(2, "0")}`
  }

  if (phase === "ended") {
    return (
      <div className="min-h-screen flex items-center justify-center p-4" style={{ background: "var(--bg-primary)" }}>
        <GlassCard className="text-center max-w-md">
          <Shield className="h-12 w-12 text-[var(--accent-cyan)] mx-auto mb-4" />
          <h2 className="text-xl font-bold text-[var(--text-primary)] mb-2">
            Interview Ended{endedBy ? ` by ${endedBy}` : ""}
          </h2>
          <p className="text-[var(--text-tertiary)] mb-4">Your report is being generated.</p>
          <Button onClick={() => router.push("/")}>Return Home</Button>
        </GlassCard>
      </div>
    )
  }

  if (!interview || phase === "loading") {
    return (
      <div className="min-h-screen flex items-center justify-center" style={{ background: "var(--bg-primary)" }}>
        <Loader2 className="h-8 w-8 text-[var(--accent-cyan)] animate-spin" />
      </div>
    )
  }

  if (phase === "join") {
    return (
      <div style={{ background: "var(--bg-primary)" }} className="min-h-screen">
        <div className="relative z-10 max-w-lg mx-auto px-4 py-12 space-y-6">
          <motion.div initial={{ opacity: 0, y: -10 }} animate={{ opacity: 1, y: 0 }} className="text-center">
            <Shield className="h-12 w-12 text-[var(--accent-cyan)] mx-auto mb-3" />
            <h1 className="text-2xl font-bold text-[var(--text-primary)]">{interview.title}</h1>
            <p className="text-[var(--text-tertiary)] mt-1">Interview with {interview.candidate_name}</p>
          </motion.div>
          <GlassCard>
            <div className="space-y-4">
              <div className="flex items-center gap-3 p-3 rounded-[var(--radius-md)]" style={{ background: "var(--bg-glass)" }}>
                <Clock className="h-5 w-5 text-[var(--accent-cyan)] shrink-0" />
                <div>
                  <p className="text-sm text-[var(--text-primary)]">Duration: {interview.duration_minutes} minutes</p>
                  <p className="text-xs text-[var(--text-quaternary)]">Scheduled: {new Date(interview.scheduled_at).toLocaleString()}</p>
                </div>
              </div>
              <div className="flex items-center gap-3 p-3 rounded-[var(--radius-md)]" style={{ background: "var(--bg-glass)" }}>
                <Video className="h-5 w-5 text-[var(--accent-cyan)] shrink-0" />
                <p className="text-sm text-[var(--text-primary)]">Camera and microphone required</p>
              </div>
            </div>
            {cameraError && (
              <div className="mt-4 p-3 rounded-[var(--radius-md)]" style={{ background: "rgba(244, 63, 94, 0.08)", border: "1px solid rgba(244, 63, 94, 0.15)" }}>
                <p className="text-sm text-[var(--accent-rose)]">{cameraError}</p>
              </div>
            )}
            <Button onClick={joinCall} className="w-full mt-6" size="lg">
              <Video className="h-4 w-4 mr-2" /> Join & Enable Camera
            </Button>
          </GlassCard>
        </div>
      </div>
    )
  }

  if (phase === "waiting" || (phase === "live" && !lkToken)) {
    return (
      <div style={{ background: "var(--bg-primary)" }} className="min-h-screen">
        <div className="relative z-10 max-w-lg mx-auto px-4 py-12 space-y-6">
          <motion.div initial={{ opacity: 0, scale: 0.95 }} animate={{ opacity: 1, scale: 1 }} className="text-center">
            <div className="relative inline-block mb-4">
              <Shield className="h-16 w-16 text-[var(--accent-cyan)] mx-auto" />
              <Loader2 className="h-6 w-6 text-[var(--accent-cyan)] absolute -bottom-1 -right-1 animate-spin" />
            </div>
            <h1 className="text-2xl font-bold text-[var(--text-primary)] mb-2">
              {phase === "waiting" ? "Connecting to Interview..." : "Waiting for HR"}
            </h1>
            <p className="text-[var(--text-tertiary)]">
              {phase === "waiting"
                ? "Establishing secure video connection."
                : "The interviewer will join shortly. Please keep this page open."}
            </p>
          </motion.div>
          <GlassCard>
            <div className="text-center p-4">
              <div className="h-3 w-3 rounded-full bg-[var(--accent-cyan)] animate-pulse mx-auto mb-3" />
              <p className="text-xs text-[var(--accent-cyan)]">Keep this page open</p>
            </div>
          </GlassCard>
        </div>
      </div>
    )
  }

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
        if (frameIntervalRef.current) clearInterval(frameIntervalRef.current)
        setEndedBy("HR")
        setPhase("ended")
      }}
    >
      <div className="min-h-screen flex flex-col" style={{ background: "var(--bg-primary)" }}>
        <header className="border-b border-[var(--border-subtle)] backdrop-blur-xl px-4 py-2 flex items-center justify-between shrink-0 z-20" style={{ background: "var(--bg-overlay)" }}>
          <div className="flex items-center gap-3">
            <Shield className="h-5 w-5 text-[var(--accent-cyan)]" />
            <span className="font-semibold text-[var(--text-primary)] text-sm hidden sm:block">{interview.title}</span>
          </div>
          <div className="flex items-center gap-3">
            <ConnectionStatus />
            <div className="flex items-center gap-1.5 px-3 py-1 rounded-full" style={{ background: "var(--bg-glass)" }}>
              <Clock className="h-3.5 w-3.5 text-[var(--accent-cyan)]" />
              <span className="text-sm text-[var(--text-primary)] font-mono tabular-nums">{formatTime(elapsed)}</span>
            </div>
            <Button onClick={endInterview} variant="destructive" size="sm" className="gap-1">
              <Phone className="h-3.5 w-3.5" /> End
            </Button>
          </div>
        </header>

        <div className="flex-1 relative overflow-hidden">
          <InterviewLayout />
        </div>
      </div>
      <RoomAudioRenderer />
    </LiveKitRoom>
  )
}

function ConnectionStatus() {
  const state = useConnectionState()
  const isConnected = state === "connected"
  return (
    <div className={`flex items-center gap-1.5 px-3 py-1 rounded-full ${
      isConnected ? "bg-[rgba(16,185,129,0.1)]" : "bg-[rgba(245,158,11,0.1)]"
    }`}>
      {isConnected ? <Wifi className="h-3.5 w-3.5 text-[var(--accent-emerald)]" /> : <WifiOff className="h-3.5 w-3.5 text-[var(--accent-amber)]" />}
      <span className={`text-xs font-medium ${isConnected ? "text-[var(--accent-emerald)]" : "text-[var(--accent-amber)]"}`}>
        {isConnected ? "Connected" : "Connecting..."}
      </span>
    </div>
  )
}

function InterviewLayout() {
  const tracks = useTracks([Track.Source.Camera, Track.Source.Microphone])
  const { localParticipant } = useLocalParticipant()
  const remoteParticipants = useRemoteParticipants()

  const localTracks = tracks.filter(t => t.participant.identity === localParticipant?.identity)
  const remoteTracks = tracks.filter(t => t.participant.identity !== localParticipant?.identity)

  return (
    <div className="w-full h-full relative">
      {remoteTracks.length > 0 ? (
        <div className="w-full h-full">
          <ParticipantTile
            trackRef={remoteTracks[0]}
            className="w-full h-full object-cover"
          />
          <div className="absolute bottom-4 left-4 text-sm text-[var(--text-tertiary)] px-3 py-1 rounded-[var(--radius-md)] z-10" style={{ background: "var(--bg-overlay)" }}>
            HR / Interviewer
          </div>
        </div>
      ) : (
        <div className="w-full h-full flex items-center justify-center">
          <div className="text-center">
            <Shield className="h-20 w-20 text-[var(--text-quaternary)] mx-auto mb-3" />
            <p className="text-[var(--text-tertiary)]">Waiting for HR to connect...</p>
          </div>
        </div>
      )}

      {localTracks.length > 0 && (
        <div className="absolute top-4 right-4 w-48 sm:w-64 aspect-video rounded-[var(--radius-lg)] overflow-hidden border-2 border-[var(--border-strong)] shadow-lg z-10" style={{ background: "var(--bg-secondary)" }}>
          <ParticipantTile
            trackRef={localTracks[0]}
            className="w-full h-full object-cover"
          />
          <div className="absolute bottom-1 left-1 text-[10px] text-[var(--text-tertiary)] px-2 py-0.5 rounded z-10" style={{ background: "var(--bg-overlay)" }}>
            You
          </div>
        </div>
      )}

      <div className="absolute bottom-4 left-1/2 -translate-x-1/2 z-20">
        <ControlBar />
      </div>
    </div>
  )
}
