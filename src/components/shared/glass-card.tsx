"use client"

import { motion } from "framer-motion"
import { cn } from "@/lib/utils"

interface GlassCardProps {
  children: React.ReactNode
  className?: string
  hover?: boolean
  delay?: number
  noPadding?: boolean
}

export function GlassCard({ children, className, hover = true, delay = 0, noPadding = false }: GlassCardProps) {
  return (
    <motion.div
      initial={{ opacity: 0, y: 12 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.5, delay, ease: [0.16, 1, 0.3, 1] }}
      whileHover={hover ? { y: -2, transition: { duration: 0.2 } } : undefined}
      className={cn(
        "surface border-gradient",
        !noPadding && "p-6",
        hover && "cursor-default",
        className
      )}
    >
      {children}
    </motion.div>
  )
}
