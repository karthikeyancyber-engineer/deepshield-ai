"use client"

import { motion } from "framer-motion"

interface RadarProps {
  size?: number
  color?: string
  className?: string
}

export function Radar({ size = 120, color = "#06b6d4", className = "" }: RadarProps) {
  const rings = 4
  const dots = [
    { angle: 45, distance: 0.6, size: 4, delay: 0 },
    { angle: 120, distance: 0.4, size: 3, delay: 0.5 },
    { angle: 200, distance: 0.8, size: 5, delay: 1 },
    { angle: 310, distance: 0.3, size: 3, delay: 1.5 },
    { angle: 80, distance: 0.7, size: 4, delay: 0.3 },
  ]

  return (
    <div className={`relative ${className}`} style={{ width: size, height: size }}>
      <svg viewBox="0 0 100 100" className="w-full h-full">
        {Array.from({ length: rings }).map((_, i) => (
          <circle
            key={i}
            cx="50"
            cy="50"
            r={10 + i * 10}
            fill="none"
            stroke={color}
            strokeWidth="0.3"
            opacity={0.3 + i * 0.1}
          />
        ))}
        <line x1="50" y1="0" x2="50" y2="100" stroke={color} strokeWidth="0.2" opacity="0.2" />
        <line x1="0" y1="50" x2="100" y2="50" stroke={color} strokeWidth="0.2" opacity="0.2" />

        <motion.g
          animate={{ rotate: 360 }}
          transition={{ duration: 3, repeat: Infinity, ease: "linear" }}
          style={{ transformOrigin: "50px 50px" }}
        >
          <line x1="50" y1="50" x2="50" y2="5" stroke={color} strokeWidth="0.8" opacity="0.9" />
          <defs>
            <linearGradient id="sweep-grad" x1="0" y1="0" x2="0" y2="1">
              <stop offset="0%" stopColor={color} stopOpacity="0.6" />
              <stop offset="100%" stopColor={color} stopOpacity="0" />
            </linearGradient>
          </defs>
          <path d="M 50 50 L 45 5 A 45 45 0 0 1 55 5 Z" fill="url(#sweep-grad)" opacity="0.3" />
        </motion.g>

        {dots.map((dot, i) => {
          const rad = (dot.angle * Math.PI) / 180
          const cx = 50 + Math.cos(rad) * dot.distance * 45
          const cy = 50 + Math.sin(rad) * dot.distance * 45
          return (
            <g key={i}>
              <motion.circle
                cx={cx}
                cy={cy}
                r={dot.size}
                fill={color}
                initial={{ opacity: 0, scale: 0 }}
                animate={{ opacity: [0, 1, 0.5, 1], scale: [0, 1, 0.8, 1] }}
                transition={{ duration: 2, repeat: Infinity, delay: dot.delay }}
              />
              <motion.circle
                cx={cx}
                cy={cy}
                r={dot.size * 2}
                fill="none"
                stroke={color}
                strokeWidth="0.3"
                initial={{ scale: 0.8, opacity: 0 }}
                animate={{ scale: [0.8, 1.5], opacity: [0.4, 0] }}
                transition={{ duration: 2, repeat: Infinity, delay: dot.delay }}
              />
            </g>
          )
        })}

        <circle cx="50" cy="50" r="2" fill={color} opacity="0.8" />
      </svg>
    </div>
  )
}
