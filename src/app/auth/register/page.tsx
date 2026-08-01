"use client"

import { useState, useCallback } from "react"
import Link from "next/link"
import { motion, AnimatePresence } from "framer-motion"
import {
  Shield, Mail, Lock, User, Eye, EyeOff, ArrowRight,
  Loader2, AlertCircle, CheckCircle2, ArrowLeft, RefreshCw,
} from "lucide-react"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { OTPInput } from "@/components/ui/otp-input"
import { useAuth } from "@/lib/auth-context"
import { apiFetch } from "@/lib/api"
import { useCountdown } from "@/lib/countdown"

type Step = "form" | "otp"

export default function RegisterPage() {
  const { register } = useAuth()
  const [step, setStep] = useState<Step>("form")
  const [form, setForm] = useState({ full_name: "", email: "", password: "", confirm_password: "" })
  const [otp, setOtp] = useState("")
  const [showPassword, setShowPassword] = useState(false)
  const [showConfirm, setShowConfirm] = useState(false)
  const [agreed, setAgreed] = useState(false)
  const [error, setError] = useState("")
  const [otpError, setOtpError] = useState("")
  const [loading, setLoading] = useState(false)
  const [otpLoading, setOtpLoading] = useState(false)
  const [otpVerified, setOtpVerified] = useState(false)
  const [otpCooldown, setOtpCooldown] = useState(60)
  const [fieldErrors, setFieldErrors] = useState<Record<string, string>>({})

  const countdown = useCountdown({ initialSeconds: 60 })

  const validate = (): boolean => {
    const errors: Record<string, string> = {}
    if (!form.full_name.trim()) errors.full_name = "Full name is required"
    if (!form.email.trim()) errors.email = "Email is required"
    else if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(form.email)) errors.email = "Invalid email address"
    if (!form.password) errors.password = "Password is required"
    else if (form.password.length < 6) errors.password = "Password must be at least 6 characters"
    if (form.password !== form.confirm_password) errors.confirm_password = "Passwords do not match"
    if (!agreed) errors.terms = "You must agree to the terms"
    setFieldErrors(errors)
    return Object.keys(errors).length === 0
  }

  const handleSendOTP = async (e: React.FormEvent) => {
    e.preventDefault()
    setError("")
    if (!validate()) return
    setLoading(true)
    try {
      await apiFetch("/auth/send-otp", {
        method: "POST",
        body: JSON.stringify({ email: form.email, purpose: "registration" }),
      })
      setStep("otp")
      setOtp("")
      setOtpError("")
      setOtpVerified(false)
      countdown.reset(otpCooldown)
      countdown.start(otpCooldown)
    } catch (err: any) {
      setError(err.message || "Failed to send OTP")
    } finally {
      setLoading(false)
    }
  }

  const handleVerifyOTP = useCallback(async () => {
    if (otp.length !== 6) {
      setOtpError("Please enter the complete 6-digit code")
      return
    }
    setOtpLoading(true)
    setOtpError("")
    try {
      await apiFetch("/auth/verify-otp", {
        method: "POST",
        body: JSON.stringify({ email: form.email, otp, purpose: "registration" }),
      })
      setOtpVerified(true)
      countdown.stop()
      // Auto-register after verification
      await register({
        full_name: form.full_name,
        email: form.email,
        password: form.password,
        confirm_password: form.confirm_password,
        role: "candidate",
      })
    } catch (err: any) {
      setOtpError(err.message || "Invalid OTP")
      setOtp("")
    } finally {
      setOtpLoading(false)
    }
  }, [otp, form, register, countdown])

  const handleResendOTP = async () => {
    setOtpError("")
    setOtp("")
    setLoading(true)
    try {
      await apiFetch("/auth/send-otp", {
        method: "POST",
        body: JSON.stringify({ email: form.email, purpose: "registration" }),
      })
      countdown.reset(otpCooldown)
      countdown.start(otpCooldown)
    } catch (err: any) {
      setOtpError(err.message || "Failed to resend OTP")
    } finally {
      setLoading(false)
    }
  }

  const updateField = (field: string, value: string) => {
    setForm(prev => ({ ...prev, [field]: value }))
    if (fieldErrors[field]) setFieldErrors(prev => ({ ...prev, [field]: "" }))
  }

  return (
    <div className="min-h-screen flex items-center justify-center p-4 relative overflow-hidden" style={{ background: "var(--bg-primary)" }}>
      <div className="absolute inset-0 cyber-grid opacity-30" />
      <div className="absolute inset-0">
        <div className="absolute top-1/3 right-1/4 w-96 h-96 bg-cyan-500/5 rounded-full blur-3xl animate-pulse" />
        <div className="absolute bottom-1/3 left-1/4 w-96 h-96 bg-blue-500/5 rounded-full blur-3xl animate-pulse" style={{ animationDelay: "1s" }} />
      </div>

      <div className="absolute inset-0 pointer-events-none">
        {[...Array(15)].map((_, i) => (
          <motion.div
            key={i}
            className="absolute w-1 h-1 bg-cyan-400/30 rounded-full"
            initial={{ x: Math.random() * 1200, y: Math.random() * 800 }}
            animate={{
              y: [Math.random() * 800, Math.random() * 800],
              x: [Math.random() * 1200, Math.random() * 1200],
              opacity: [0.2, 0.5, 0.2],
            }}
            transition={{ duration: 8 + Math.random() * 4, repeat: Infinity, ease: "easeInOut" }}
          />
        ))}
      </div>

      <motion.div
        initial={{ opacity: 0, y: 30 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.7, ease: [0.16, 1, 0.3, 1] }}
        className="w-full max-w-md relative z-10"
      >
        <div className="text-center mb-8">
          <motion.div
            initial={{ scale: 0, rotate: -180 }}
            animate={{ scale: 1, rotate: 0 }}
            transition={{ delay: 0.2, type: "spring", stiffness: 200, damping: 15 }}
            className="inline-flex items-center justify-center w-20 h-20 rounded-2xl border border-[var(--border-default)] mb-4"
            style={{ background: "rgba(6, 182, 212, 0.08)" }}
          >
            <Shield className="h-10 w-10 text-[var(--accent-cyan)]" />
          </motion.div>
          <motion.h1
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.3 }}
            className="text-3xl font-bold text-[var(--text-primary)] mb-2"
          >
            Create Account
          </motion.h1>
          <motion.p
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{ delay: 0.4 }}
            className="text-[var(--text-tertiary)]"
          >
            {step === "form" ? "Join DeepShield AI Security Platform" : `Verify your email ${form.email}`}
          </motion.p>
        </div>

        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.3, duration: 0.6 }}
          className="surface border-gradient p-8"
        >
          <AnimatePresence mode="wait">
            {step === "form" ? (
              <motion.div
                key="form"
                initial={{ opacity: 0, x: -20 }}
                animate={{ opacity: 1, x: 0 }}
                exit={{ opacity: 0, x: -20 }}
              >
                <div className="mb-6">
                  <h2 className="text-xl font-semibold text-[var(--text-primary)]">Get started</h2>
                  <p className="text-[var(--text-tertiary)] text-sm mt-1">Fill in your details to create an account</p>
                </div>

                {error && (
                  <motion.div
                    initial={{ opacity: 0, y: -10 }}
                    animate={{ opacity: 1, y: 0 }}
                    className="mb-4 p-3 rounded-xl flex items-center gap-2"
                    style={{ background: "rgba(244, 63, 94, 0.08)", border: "1px solid rgba(244, 63, 94, 0.15)" }}
                  >
                    <AlertCircle className="h-4 w-4 text-[var(--accent-rose)] shrink-0" />
                    <p className="text-[var(--accent-rose)] text-sm">{error}</p>
                  </motion.div>
                )}

                <form onSubmit={handleSendOTP} className="space-y-4">
                  <div className="space-y-1.5">
                    <Label htmlFor="full_name">Full name *</Label>
                    <div className="relative">
                      <User className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-[var(--text-quaternary)]" />
                      <Input
                        id="full_name"
                        type="text"
                        value={form.full_name}
                        onChange={(e) => updateField("full_name", e.target.value)}
                        placeholder="John Doe"
                        className={`pl-10 h-11 ${fieldErrors.full_name ? "border-[var(--accent-rose)]/50 focus-visible:ring-[var(--accent-rose)]" : ""}`}
                        autoComplete="name"
                      />
                    </div>
                    {fieldErrors.full_name && <p className="text-[var(--accent-rose)] text-xs">{fieldErrors.full_name}</p>}
                  </div>

                  <div className="space-y-1.5">
                    <Label htmlFor="email">Email address *</Label>
                    <div className="relative">
                      <Mail className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-[var(--text-quaternary)]" />
                      <Input
                        id="email"
                        type="email"
                        value={form.email}
                        onChange={(e) => updateField("email", e.target.value)}
                        placeholder="you@example.com"
                        className={`pl-10 h-11 ${fieldErrors.email ? "border-[var(--accent-rose)]/50 focus-visible:ring-[var(--accent-rose)]" : ""}`}
                        autoComplete="email"
                      />
                    </div>
                    {fieldErrors.email && <p className="text-[var(--accent-rose)] text-xs">{fieldErrors.email}</p>}
                  </div>

                  <div className="space-y-1.5">
                    <Label htmlFor="password">Password *</Label>
                    <div className="relative">
                      <Lock className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-[var(--text-quaternary)]" />
                      <Input
                        id="password"
                        type={showPassword ? "text" : "password"}
                        value={form.password}
                        onChange={(e) => updateField("password", e.target.value)}
                        placeholder="Min 6 characters"
                        className={`pl-10 pr-12 h-11 ${fieldErrors.password ? "border-[var(--accent-rose)]/50 focus-visible:ring-[var(--accent-rose)]" : ""}`}
                        autoComplete="new-password"
                      />
                      <button
                        type="button"
                        onClick={() => setShowPassword(!showPassword)}
                        className="absolute right-3 top-1/2 -translate-y-1/2 text-[var(--text-quaternary)] hover:text-[var(--text-secondary)] transition-colors"
                      >
                        {showPassword ? <EyeOff className="h-4 w-4" /> : <Eye className="h-4 w-4" />}
                      </button>
                    </div>
                    {fieldErrors.password && <p className="text-[var(--accent-rose)] text-xs">{fieldErrors.password}</p>}
                  </div>

                  <div className="space-y-1.5">
                    <Label htmlFor="confirm_password">Confirm password *</Label>
                    <div className="relative">
                      <Lock className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-[var(--text-quaternary)]" />
                      <Input
                        id="confirm_password"
                        type={showConfirm ? "text" : "password"}
                        value={form.confirm_password}
                        onChange={(e) => updateField("confirm_password", e.target.value)}
                        placeholder="Re-enter password"
                        className={`pl-10 pr-12 h-11 ${fieldErrors.confirm_password ? "border-[var(--accent-rose)]/50 focus-visible:ring-[var(--accent-rose)]" : ""}`}
                        autoComplete="new-password"
                      />
                      <button
                        type="button"
                        onClick={() => setShowConfirm(!showConfirm)}
                        className="absolute right-3 top-1/2 -translate-y-1/2 text-[var(--text-quaternary)] hover:text-[var(--text-secondary)] transition-colors"
                      >
                        {showConfirm ? <EyeOff className="h-4 w-4" /> : <Eye className="h-4 w-4" />}
                      </button>
                    </div>
                    {fieldErrors.confirm_password && <p className="text-[var(--accent-rose)] text-xs">{fieldErrors.confirm_password}</p>}
                  </div>

                  <div className="space-y-1.5">
                    <label className="flex items-start gap-2.5 cursor-pointer group">
                      <div className="relative mt-0.5">
                        <input
                          type="checkbox"
                          checked={agreed}
                          onChange={(e) => { setAgreed(e.target.checked); if (fieldErrors.terms) setFieldErrors(p => ({ ...p, terms: "" })) }}
                          className="peer sr-only"
                        />
                        <div className="h-4 w-4 rounded border border-[var(--border-default)] bg-[var(--bg-glass)] peer-checked:bg-[var(--accent-cyan)] peer-checked:border-[var(--accent-cyan)] transition-all flex items-center justify-center">
                          {agreed && (
                            <svg className="h-3 w-3 text-white" viewBox="0 0 12 12" fill="none" stroke="currentColor" strokeWidth="2">
                              <path d="M2 6l3 3 5-5" />
                            </svg>
                          )}
                        </div>
                      </div>
                      <span className="text-sm text-[var(--text-tertiary)] group-hover:text-[var(--text-secondary)] transition-colors leading-tight">
                        I agree to the{" "}
                        <Link href="#" className="text-[var(--accent-cyan)] hover:text-[var(--accent-blue)]">Terms of Service</Link>
                        {" "}and{" "}
                        <Link href="#" className="text-[var(--accent-cyan)] hover:text-[var(--accent-blue)]">Privacy Policy</Link>
                      </span>
                    </label>
                    {fieldErrors.terms && <p className="text-[var(--accent-rose)] text-xs">{fieldErrors.terms}</p>}
                  </div>

                  <Button type="submit" className="w-full h-12 text-base font-medium group" disabled={loading}>
                    {loading ? (
                      <Loader2 className="h-5 w-5 animate-spin" />
                    ) : (
                      <>
                        Send Verification OTP
                        <ArrowRight className="ml-2 h-4 w-4 group-hover:translate-x-1 transition-transform" />
                      </>
                    )}
                  </Button>
                </form>
              </motion.div>
            ) : (
              <motion.div
                key="otp"
                initial={{ opacity: 0, x: 20 }}
                animate={{ opacity: 1, x: 0 }}
                exit={{ opacity: 0, x: 20 }}
                className="text-center"
              >
                {otpVerified ? (
                  <motion.div
                    initial={{ scale: 0 }}
                    animate={{ scale: 1 }}
                    transition={{ type: "spring", stiffness: 200 }}
                    className="py-8"
                  >
                    <div className="inline-flex items-center justify-center w-20 h-20 rounded-2xl mb-6"
                      style={{ background: "rgba(16, 185, 129, 0.08)", border: "1px solid rgba(16, 185, 129, 0.15)" }}>
                      <CheckCircle2 className="h-10 w-10 text-[var(--accent-emerald)]" />
                    </div>
                    <h3 className="text-xl font-bold text-[var(--text-primary)] mb-2">Email Verified!</h3>
                    <p className="text-[var(--text-tertiary)] text-sm">Creating your account...</p>
                    <Loader2 className="h-6 w-6 text-[var(--accent-cyan)] mx-auto mt-4 animate-spin" />
                  </motion.div>
                ) : (
                  <>
                    <button
                      onClick={() => { setStep("form"); setOtp(""); setOtpError("") }}
                      className="flex items-center gap-1 text-[var(--text-quaternary)] hover:text-[var(--text-secondary)] text-sm mb-6 transition-colors"
                    >
                      <ArrowLeft className="h-4 w-4" /> Back to form
                    </button>

                    <div className="inline-flex items-center justify-center w-16 h-16 rounded-2xl mb-4"
                      style={{ background: "rgba(6, 182, 212, 0.08)", border: "1px solid rgba(6, 182, 212, 0.15)" }}>
                      <Mail className="h-8 w-8 text-[var(--accent-cyan)]" />
                    </div>
                    <h3 className="text-xl font-bold text-[var(--text-primary)] mb-2">Check your email</h3>
                    <p className="text-[var(--text-tertiary)] text-sm mb-8">
                      We sent a 6-digit code to<br />
                      <span className="text-[var(--text-primary)] font-medium">{form.email}</span>
                    </p>

                    {otpError && (
                      <motion.div
                        initial={{ opacity: 0, y: -10 }}
                        animate={{ opacity: 1, y: 0 }}
                        className="mb-4 p-3 rounded-xl flex items-center gap-2"
                        style={{ background: "rgba(244, 63, 94, 0.08)", border: "1px solid rgba(244, 63, 94, 0.15)" }}
                      >
                        <AlertCircle className="h-4 w-4 text-[var(--accent-rose)] shrink-0" />
                        <p className="text-[var(--accent-rose)] text-sm">{otpError}</p>
                      </motion.div>
                    )}

                    <div className="mb-6">
                      <OTPInput
                        value={otp}
                        onChange={setOtp}
                        disabled={otpLoading}
                        error={otpError}
                      />
                    </div>

                    {/* Countdown */}
                    <div className="mb-6">
                      {countdown.isActive ? (
                        <p className="text-[var(--text-quaternary)] text-sm">
                          Code expires in <span className="text-[var(--accent-cyan)] font-mono font-medium">{countdown.formatted}</span>
                        </p>
                      ) : (
                        <p className="text-[var(--text-quaternary)] text-sm">Code expired</p>
                      )}
                    </div>

                    <Button
                      onClick={handleVerifyOTP}
                      className="w-full h-12 text-base font-medium group"
                      disabled={otpLoading || otp.length !== 6}
                    >
                      {otpLoading ? (
                        <Loader2 className="h-5 w-5 animate-spin" />
                      ) : (
                        <>
                          Verify & Create Account
                          <ArrowRight className="ml-2 h-4 w-4 group-hover:translate-x-1 transition-transform" />
                        </>
                      )}
                    </Button>

                    <div className="mt-6">
                      {countdown.isActive ? (
                        <p className="text-[var(--text-quaternary)] text-sm">
                          Resend code in <span className="font-mono">{countdown.formatted}</span>
                        </p>
                      ) : (
                        <button
                          onClick={handleResendOTP}
                          disabled={loading}
                          className="text-sm text-[var(--accent-cyan)] hover:text-[var(--accent-blue)] transition-colors inline-flex items-center gap-1.5"
                        >
                          <RefreshCw className={`h-3.5 w-3.5 ${loading ? "animate-spin" : ""}`} />
                          Resend OTP
                        </button>
                      )}
                    </div>
                  </>
                )}
              </motion.div>
            )}
          </AnimatePresence>
        </motion.div>

        <motion.p
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ delay: 0.5 }}
          className="text-center text-[var(--text-quaternary)] text-sm mt-6"
        >
          Already have an account?{" "}
          <Link href="/auth/login" className="text-[var(--accent-cyan)] hover:text-[var(--accent-blue)] font-medium transition-colors">
            Sign in
          </Link>
        </motion.p>
      </motion.div>
    </div>
  )
}
