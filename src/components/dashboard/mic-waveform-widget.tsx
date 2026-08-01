"use client"

import { useState, useRef, useEffect, useCallback } from "react"
import { motion } from "framer-motion"
import { Mic, MicOff, AudioWaveform, Volume2 } from "lucide-react"
import { Button } from "@/components/ui/button"
import { StatusBadge } from "@/components/shared/status-badge"

export function MicWaveformWidget() {
  const [isRecording, setIsRecording] = useState(false)
  const [audioLevel, setAudioLevel] = useState(0)
  const canvasRef = useRef<HTMLCanvasElement>(null)
  const audioContextRef = useRef<AudioContext | null>(null)
  const analyserRef = useRef<AnalyserNode | null>(null)
  const animFrameRef = useRef<number | null>(null)
  const streamRef = useRef<MediaStream | null>(null)

  const drawWaveform = useCallback(() => {
    const canvas = canvasRef.current
    const analyser = analyserRef.current
    if (!canvas || !analyser) return

    const ctx = canvas.getContext("2d")
    if (!ctx) return

    const bufferLength = analyser.frequencyBinCount
    const dataArray = new Uint8Array(bufferLength)
    analyser.getByteTimeDomainData(dataArray)

    ctx.clearRect(0, 0, canvas.width, canvas.height)

    const gradient = ctx.createLinearGradient(0, 0, canvas.width, 0)
    gradient.addColorStop(0, "#06b6d4")
    gradient.addColorStop(0.5, "#3b82f6")
    gradient.addColorStop(1, "#06b6d4")

    ctx.lineWidth = 2
    ctx.strokeStyle = gradient
    ctx.beginPath()

    const sliceWidth = canvas.width / bufferLength
    let x = 0

    for (let i = 0; i < bufferLength; i++) {
      const v = dataArray[i] / 128.0
      const y = (v * canvas.height) / 2
      if (i === 0) ctx.moveTo(x, y)
      else ctx.lineTo(x, y)
      x += sliceWidth
    }

    ctx.lineTo(canvas.width, canvas.height / 2)
    ctx.stroke()

    ctx.shadowBlur = 8
    ctx.shadowColor = "#06b6d4"
    ctx.stroke()
    ctx.shadowBlur = 0

    const avg = dataArray.reduce((a, b) => a + Math.abs(b - 128), 0) / bufferLength
    setAudioLevel(Math.min(100, avg * 2))

    animFrameRef.current = requestAnimationFrame(drawWaveform)
  }, [])

  const startRecording = async () => {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true })
      streamRef.current = stream
      audioContextRef.current = new AudioContext()
      analyserRef.current = audioContextRef.current.createAnalyser()
      const source = audioContextRef.current.createMediaStreamSource(stream)
      source.connect(analyserRef.current)
      setIsRecording(true)
      drawWaveform()
    } catch (err) {
      console.error("Mic access denied:", err)
    }
  }

  const stopRecording = useCallback(() => {
    animFrameRef.current && cancelAnimationFrame(animFrameRef.current)
    streamRef.current?.getTracks().forEach((t) => t.stop())
    audioContextRef.current?.close()
    setIsRecording(false)
    setAudioLevel(0)
  }, [])

  useEffect(() => () => stopRecording(), [stopRecording])

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.5, delay: 0.1 }}
      className="rounded-2xl border border-white/10 bg-white/[0.03] backdrop-blur-xl overflow-hidden"
    >
      <div className="flex items-center justify-between px-4 py-3 border-b border-white/5">
        <div className="flex items-center gap-2">
          <AudioWaveform className="h-4 w-4 text-blue-400" />
          <span className="text-sm font-medium text-white">Microphone</span>
        </div>
        <StatusBadge status={isRecording ? "online" : "offline"} />
      </div>

      <div className="relative h-32 bg-black/30">
        <canvas
          ref={canvasRef}
          width={400}
          height={128}
          className="w-full h-full"
        />
        {!isRecording && (
          <div className="absolute inset-0 flex flex-col items-center justify-center">
            <Mic className="h-8 w-8 text-white/15 mb-2" />
            <p className="text-xs text-white/30">Mic inactive</p>
          </div>
        )}
      </div>

      <div className="px-4 py-3 space-y-3">
        <div>
          <div className="flex justify-between text-xs mb-1.5">
            <span className="text-white/50">Input Level</span>
            <span className="text-cyan-400 font-medium">{Math.round(audioLevel)}%</span>
          </div>
          <div className="h-1.5 rounded-full bg-white/5 overflow-hidden">
            <motion.div
              className="h-full rounded-full bg-gradient-to-r from-cyan-500 to-blue-500"
              animate={{ width: `${audioLevel}%` }}
              transition={{ duration: 0.05 }}
            />
          </div>
        </div>

        <Button
          onClick={isRecording ? stopRecording : startRecording}
          variant={isRecording ? "destructive" : "default"}
          size="sm"
          className="w-full"
        >
          {isRecording ? (
            <><MicOff className="h-3.5 w-3.5 mr-2" />Stop</>
          ) : (
            <><Mic className="h-3.5 w-3.5 mr-2" />Start</>
          )}
        </Button>
      </div>
    </motion.div>
  )
}
