"use client"

import { useEffect, useRef, useMemo } from "react"

interface Particle {
  x: number
  y: number
  vx: number
  vy: number
  size: number
  opacity: number
  color: string
  pulse: number
  pulseSpeed: number
}

export function ParticleBackground() {
  const canvasRef = useRef<HTMLCanvasElement>(null)

  const config = useMemo(() => ({
    particleCount: 80,
    connectionDistance: 150,
    colors: ["#06b6d4", "#3b82f6", "#8b5cf6"],
    speed: 0.3,
    pulseSpeed: 0.02,
  }), [])

  useEffect(() => {
    const canvas = canvasRef.current
    if (!canvas) return
    const ctx = canvas.getContext("2d")
    if (!ctx) return

    let animId: number
    let particles: Particle[] = []

    const resize = () => {
      canvas.width = window.innerWidth
      canvas.height = window.innerHeight
    }

    const createParticles = () => {
      particles = Array.from({ length: config.particleCount }, () => ({
        x: Math.random() * canvas.width,
        y: Math.random() * canvas.height,
        vx: (Math.random() - 0.5) * config.speed,
        vy: (Math.random() - 0.5) * config.speed,
        size: Math.random() * 2 + 0.5,
        opacity: Math.random() * 0.4 + 0.1,
        color: config.colors[Math.floor(Math.random() * config.colors.length)],
        pulse: Math.random() * Math.PI * 2,
        pulseSpeed: Math.random() * config.pulseSpeed + 0.005,
      }))
    }

    const draw = () => {
      ctx.clearRect(0, 0, canvas.width, canvas.height)

      particles.forEach((p, i) => {
        p.x += p.vx
        p.y += p.vy
        p.pulse += p.pulseSpeed

        if (p.x < 0 || p.x > canvas.width) p.vx *= -1
        if (p.y < 0 || p.y > canvas.height) p.vy *= -1

        const pulseOpacity = p.opacity + Math.sin(p.pulse) * 0.15
        const pulseSize = p.size + Math.sin(p.pulse) * 0.5

        ctx.beginPath()
        ctx.arc(p.x, p.y, Math.max(0.5, pulseSize), 0, Math.PI * 2)
        ctx.fillStyle = p.color
        ctx.globalAlpha = Math.max(0, pulseOpacity)
        ctx.fill()

        ctx.beginPath()
        ctx.arc(p.x, p.y, Math.max(1, pulseSize * 2), 0, Math.PI * 2)
        ctx.fillStyle = p.color
        ctx.globalAlpha = Math.max(0, pulseOpacity * 0.15)
        ctx.fill()

        for (let j = i + 1; j < particles.length; j++) {
          const p2 = particles[j]
          const dx = p.x - p2.x
          const dy = p.y - p2.y
          const dist = Math.sqrt(dx * dx + dy * dy)

          if (dist < config.connectionDistance) {
            const alpha = (1 - dist / config.connectionDistance) * 0.12
            ctx.beginPath()
            ctx.moveTo(p.x, p.y)
            ctx.lineTo(p2.x, p2.y)
            ctx.strokeStyle = p.color
            ctx.globalAlpha = alpha
            ctx.lineWidth = 0.5
            ctx.stroke()
          }
        }
      })

      ctx.globalAlpha = 1
      animId = requestAnimationFrame(draw)
    }

    resize()
    createParticles()
    draw()

    window.addEventListener("resize", () => { resize(); createParticles() })
    return () => {
      cancelAnimationFrame(animId)
      window.removeEventListener("resize", resize)
    }
  }, [config])

  return (
    <canvas
      ref={canvasRef}
      className="fixed inset-0 pointer-events-none z-0"
      style={{ background: "transparent" }}
    />
  )
}
