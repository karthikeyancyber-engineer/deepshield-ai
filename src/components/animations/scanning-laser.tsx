"use client"

import { motion } from "framer-motion"

interface ScanningLaserProps {
  direction?: "vertical" | "horizontal"
  color?: string
  speed?: number
  className?: string
}

export function ScanningLaser({
  direction = "vertical",
  color = "#06b6d4",
  speed = 4,
  className = "",
}: ScanningLaserProps) {
  return (
    <div className={`absolute inset-0 overflow-hidden pointer-events-none ${className}`}>
      <motion.div
        className={direction === "vertical" ? "absolute left-0 right-0 h-[2px]" : "absolute top-0 bottom-0 w-[2px]"}
        style={{
          background: `linear-gradient(${direction === "vertical" ? "90deg" : "180deg"}, transparent, ${color}, transparent)`,
          boxShadow: `0 0 20px ${color}, 0 0 40px ${color}80`,
        }}
        initial={direction === "vertical" ? { top: "-2px" } : { left: "-2px" }}
        animate={
          direction === "vertical"
            ? { top: ["0%", "100%"] }
            : { left: ["0%", "100%"] }
        }
        transition={{
          duration: speed,
          repeat: Infinity,
          ease: "linear",
        }}
      />
      <motion.div
        className={direction === "vertical" ? "absolute left-0 right-0 h-[1px]" : "absolute top-0 bottom-0 w-[1px]"}
        style={{
          background: `linear-gradient(${direction === "vertical" ? "90deg" : "180deg"}, transparent, ${color}40, transparent)`,
        }}
        initial={direction === "vertical" ? { top: "-2px" } : { left: "-2px" }}
        animate={
          direction === "vertical"
            ? { top: ["0%", "100%"] }
            : { left: ["0%", "100%"] }
        }
        transition={{
          duration: speed,
          repeat: Infinity,
          ease: "linear",
          delay: 0.1,
        }}
      />
    </div>
  )
}
