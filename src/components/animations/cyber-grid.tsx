"use client"

import { useEffect, useRef } from "react"

export function CyberGrid() {
  const canvasRef = useRef<HTMLCanvasElement>(null)

  useEffect(() => {
    const canvas = canvasRef.current
    if (!canvas) return
    const ctx = canvas.getContext("2d")
    if (!ctx) return

    let animId: number
    let offset = 0

    const resize = () => {
      canvas.width = window.innerWidth
      canvas.height = window.innerHeight
    }

    const draw = () => {
      ctx.clearRect(0, 0, canvas.width, canvas.height)

      const gridSize = 60
      offset = (offset + 0.15) % gridSize

      ctx.strokeStyle = "rgba(6, 182, 212, 0.035)"
      ctx.lineWidth = 0.5

      for (let x = -gridSize + offset; x < canvas.width + gridSize; x += gridSize) {
        ctx.beginPath()
        ctx.moveTo(x, 0)
        ctx.lineTo(x, canvas.height)
        ctx.stroke()
      }
      for (let y = -gridSize + offset; y < canvas.height + gridSize; y += gridSize) {
        ctx.beginPath()
        ctx.moveTo(0, y)
        ctx.lineTo(canvas.width, y)
        ctx.stroke()
      }

      const time = Date.now() * 0.001
      const pulseX = (Math.sin(time * 0.3) * 0.3 + 0.5) * canvas.width
      const pulseY = (Math.cos(time * 0.2) * 0.3 + 0.5) * canvas.height
      const gradient = ctx.createRadialGradient(pulseX, pulseY, 0, pulseX, pulseY, 300)
      gradient.addColorStop(0, "rgba(6, 182, 212, 0.04)")
      gradient.addColorStop(0.5, "rgba(59, 130, 246, 0.02)")
      gradient.addColorStop(1, "transparent")
      ctx.fillStyle = gradient
      ctx.fillRect(0, 0, canvas.width, canvas.height)

      animId = requestAnimationFrame(draw)
    }

    resize()
    draw()
    window.addEventListener("resize", resize)

    return () => {
      cancelAnimationFrame(animId)
      window.removeEventListener("resize", resize)
    }
  }, [])

  return (
    <canvas
      ref={canvasRef}
      className="fixed inset-0 pointer-events-none z-0"
      style={{ background: "transparent" }}
    />
  )
}
