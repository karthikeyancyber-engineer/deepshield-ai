"use client"

import { useState, useRef, useEffect } from "react"
import { motion } from "framer-motion"
import { Video, VideoOff, Camera, Wifi, WifiOff, User, Scan } from "lucide-react"
import { Button } from "@/components/ui/button"
import { StatusBadge } from "@/components/shared/status-badge"
import { useCurrentTime } from "@/lib/hooks"

export function LiveWebcamWidget() {
  const [isStreaming, setIsStreaming] = useState(false)
  const time = useCurrentTime()
  const [faceDetected, setFaceDetected] = useState(false)
  const videoRef = useRef<HTMLVideoElement>(null)
  const streamRef = useRef<MediaStream | null>(null)

  const startCamera = async () => {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({
        video: { facingMode: "user", width: 640, height: 480 },
      })
      streamRef.current = stream
      if (videoRef.current) {
        videoRef.current.srcObject = stream
      }
      setIsStreaming(true)
      setTimeout(() => setFaceDetected(true), 1500)
    } catch (err) {
      console.error("Camera access denied:", err)
    }
  }

  const stopCamera = () => {
    if (streamRef.current) {
      streamRef.current.getTracks().forEach((t) => t.stop())
      streamRef.current = null
    }
    if (videoRef.current) videoRef.current.srcObject = null
    setIsStreaming(false)
    setFaceDetected(false)
  }

  useEffect(() => {
    return () => {
      streamRef.current?.getTracks().forEach((t) => t.stop())
    }
  }, [])

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.5 }}
      className="rounded-2xl border border-white/10 bg-white/[0.03] backdrop-blur-xl overflow-hidden"
    >
      <div className="flex items-center justify-between px-4 py-3 border-b border-white/5">
        <div className="flex items-center gap-2">
          <Video className="h-4 w-4 text-cyan-400" />
          <span className="text-sm font-medium text-white">Live Webcam</span>
        </div>
        <div className="flex items-center gap-2">
          <StatusBadge status={isStreaming ? "online" : "offline"} />
        </div>
      </div>

      <div className="relative aspect-video bg-black/40">
        {isStreaming ? (
          <>
            <video
              ref={videoRef}
              autoPlay
              playsInline
              muted
              className="w-full h-full object-cover"
            />
            {faceDetected && (
              <motion.div
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                className="absolute inset-0 pointer-events-none"
              >
                <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-32 h-40 border-2 border-cyan-400/60 rounded-lg">
                  <div className="absolute top-0 left-0 w-4 h-4 border-t-2 border-l-2 border-cyan-400 rounded-tl-lg" />
                  <div className="absolute top-0 right-0 w-4 h-4 border-t-2 border-r-2 border-cyan-400 rounded-tr-lg" />
                  <div className="absolute bottom-0 left-0 w-4 h-4 border-b-2 border-l-2 border-cyan-400 rounded-bl-lg" />
                  <div className="absolute bottom-0 right-0 w-4 h-4 border-b-2 border-r-2 border-cyan-400 rounded-br-lg" />
                </div>
                <div className="absolute bottom-3 left-3 flex items-center gap-2 px-2 py-1 rounded-lg bg-black/60 backdrop-blur-sm">
                  <Scan className="h-3 w-3 text-green-400" />
                  <span className="text-xs text-green-400 font-medium">Face Detected</span>
                </div>
              </motion.div>
            )}
          </>
        ) : (
          <div className="absolute inset-0 flex flex-col items-center justify-center">
            <Camera className="h-12 w-12 text-white/15 mb-3" />
            <p className="text-sm text-white/30">Camera inactive</p>
          </div>
        )}

        <div className="absolute top-3 left-3">
          {isStreaming && (
            <span className="flex items-center gap-1.5 px-2 py-1 rounded-md bg-red-500/20 backdrop-blur-sm">
              <span className="h-1.5 w-1.5 rounded-full bg-red-500 animate-pulse" />
              <span className="text-[10px] font-medium text-red-400">LIVE</span>
            </span>
          )}
        </div>

        <div className="absolute top-3 right-3">
          <span className="text-[10px] text-white/40 font-mono">
            {time || "--:--"}
          </span>
        </div>
      </div>

      <div className="p-3">
        <Button
          onClick={isStreaming ? stopCamera : startCamera}
          variant={isStreaming ? "destructive" : "default"}
          size="sm"
          className="w-full"
        >
          {isStreaming ? (
            <><VideoOff className="h-3.5 w-3.5 mr-2" />Stop Feed</>
          ) : (
            <><Video className="h-3.5 w-3.5 mr-2" />Start Feed</>
          )}
        </Button>
      </div>
    </motion.div>
  )
}
