"use client"

import { useState, useCallback } from "react"
import Link from "next/link"
import { motion, AnimatePresence } from "framer-motion"
import {
  Shield, Mail, Lock, Eye, EyeOff, ArrowRight, ArrowLeft,
  Loader2, AlertCircle, CheckCircle2, RefreshCw, KeyRound,
} from "lucide-react"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { OTPInput } from "@/components/ui/otp-input"
import { useAuth } from "@/lib/auth-context"
import { apiFetch } from "@/lib/api"
import { useCountdown } from "@/lib/countdown"
import { ParticleField } from "@/components/animations/particle-field"

type ForgotStep = "email" | "otp" | "reset" | "done"

export default function LoginPage() {
  const { login } = useAuth()

  const [email, setEmail] = useState("")
  const [password, setPassword] = useState("")
  const [showPassword, setShowPassword] = useState(false)
  const [rememberMe, setRememberMe] = useState(false)
  const [error, setError] = useState("")
  const [loading, setLoading] = useState(false)

  const [showForgot, setShowForgot] = useState(false)
  const [forgotStep, setForgotStep] = useState<ForgotStep>("email")
  const [forgotEmail, setForgotEmail] = useState("")
  const [forgotOtp, setForgotOtp] = useState("")
  const [forgotOtpError, setForgotOtpError] = useState("")
  const [newPassword, setNewPassword] = useState("")
  const [confirmPassword, setConfirmPassword] = useState("")
  const [showNewPw, setShowNewPw] = useState(false)
  const [showConfirmPw, setShowConfirmPw] = useState(false)
  const [forgotLoading, setForgotLoading] = useState(false)
  const [otpVerified, setOtpVerified] = useState(false)

  const countdown = useCountdown({ initialSeconds: 60 })

  const handleLogin = async (e: React.FormEvent) => {
    e.preventDefault()
    setError("")
    if (!email || !password) {
      setError("Please fill in all fields")
      return
    }
    setLoading(true)
    try {
      await login(email, password, rememberMe)
    } catch (err: any) {
      setError(err.message || "Login failed. Please check your credentials.")
    } finally {
      setLoading(false)
    }
  }

  const handleSendForgotOTP = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!forgotEmail) return
    setForgotLoading(true)
    setForgotOtpError("")
    try {
      await apiFetch("/auth/send-otp", {
        method: "POST",
        body: JSON.stringify({ email: forgotEmail, purpose: "password_reset" }),
      })
    } catch { /* continue to OTP step regardless */ }
    setForgotStep("otp")
    setForgotOtp("")
    countdown.reset(60)
    countdown.start(60)
    setForgotLoading(false)
  }

  const handleVerifyForgotOTP = useCallback(async () => {
    if (forgotOtp.length !== 6) {
      setForgotOtpError("Please enter the complete 6-digit code")
      return
    }
    setForgotLoading(true)
    setForgotOtpError("")
    try {
      await apiFetch("/auth/verify-otp", {
        method: "POST",
        body: JSON.stringify({ email: forgotEmail, otp: forgotOtp, purpose: "password_reset" }),
      })
      setOtpVerified(true)
      countdown.stop()
      setTimeout(() => setForgotStep("reset"), 1000)
    } catch (err: any) {
      setForgotOtpError(err.message || "Invalid OTP")
      setForgotOtp("")
    } finally {
      setForgotLoading(false)
    }
  }, [forgotOtp, forgotEmail, countdown])

  const handleResetPassword = async (e: React.FormEvent) => {
    e.preventDefault()
    setForgotOtpError("")
    if (newPassword.length < 6) {
      setForgotOtpError("Password must be at least 6 characters")
      return
    }
    if (newPassword !== confirmPassword) {
      setForgotOtpError("Passwords do not match")
      return
    }
    setForgotLoading(true)
    try {
      await apiFetch("/auth/reset-password", {
        method: "POST",
        body: JSON.stringify({ email: forgotEmail, password: newPassword, confirm_password: confirmPassword }),
      })
      setForgotStep("done")
    } catch (err: any) {
      setForgotOtpError(err.message || "Failed to reset password")
    } finally {
      setForgotLoading(false)
    }
  }

  const handleResendForgotOTP = async () => {
    setForgotOtpError("")
    setForgotOtp("")
    setForgotLoading(true)
    try {
      await apiFetch("/auth/send-otp", {
        method: "POST",
        body: JSON.stringify({ email: forgotEmail, purpose: "password_reset" }),
      })
    } catch { /* continue */ }
    countdown.reset(60)
    countdown.start(60)
    setForgotLoading(false)
  }

  const resetForgotState = () => {
    setShowForgot(false)
    setForgotStep("email")
    setForgotEmail("")
    setForgotOtp("")
    setForgotOtpError("")
    setNewPassword("")
    setConfirmPassword("")
    setOtpVerified(false)
    countdown.reset()
  }

  return (
    <div className="min-h-screen flex items-center justify-center p-4 relative overflow-hidden" style={{ background: "var(--bg-primary)" }}>
      <ParticleField />

      {/* Glow orbs */}
      <div className="absolute inset-0 pointer-events-none">
        <div className="absolute top-1/4 left-1/4 w-96 h-96 rounded-full blur-3xl animate-pulse" style={{ background: "rgba(6, 182, 212, 0.05)" }} />
        <div className="absolute bottom-1/4 right-1/4 w-96 h-96 rounded-full blur-3xl animate-pulse" style={{ background: "rgba(59, 130, 246, 0.05)", animationDelay: "1s" }} />
        <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[600px] h-[600px] rounded-full blur-3xl animate-pulse" style={{ background: "rgba(139, 92, 246, 0.03)", animationDelay: "2s" }} />
      </div>

      <motion.div
        initial={{ opacity: 0, y: 30 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.7, ease: [0.16, 1, 0.3, 1] }}
        className="w-full max-w-md relative z-10"
      >
        {/* Logo */}
        <div className="text-center mb-8">
          <motion.div
            initial={{ scale: 0, rotate: -180 }}
            animate={{ scale: 1, rotate: 0 }}
            transition={{ delay: 0.2, type: "spring", stiffness: 200, damping: 15 }}
            className="inline-flex items-center justify-center w-20 h-20 rounded-[var(--radius-xl)] border-gradient mb-4"
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
            DeepShield <span className="text-gradient">AI</span>
          </motion.h1>
          <motion.p
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{ delay: 0.4 }}
            className="text-[var(--text-tertiary)]"
          >
            {showForgot ? "Reset your password" : "Secure Interview & Authentication Platform"}
          </motion.p>
        </div>

        {/* Card */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.3, duration: 0.6 }}
          className="surface border-gradient p-8"
        >
          <AnimatePresence mode="wait">
            {!showForgot ? (
              <motion.div key="login" initial={{ opacity: 0 }} animate={{ opacity: 1 }} exit={{ opacity: 0 }}>
                <div className="mb-6">
                  <h2 className="text-xl font-semibold text-[var(--text-primary)]">Welcome back</h2>
                  <p className="text-[var(--text-tertiary)] text-sm mt-1">Sign in to your account</p>
                </div>

                {error && (
                  <motion.div initial={{ opacity: 0, y: -10 }} animate={{ opacity: 1, y: 0 }}
                    className="mb-4 p-3 rounded-[var(--radius-md)] flex items-center gap-2"
                    style={{ background: "rgba(244, 63, 94, 0.08)", border: "1px solid rgba(244, 63, 94, 0.15)" }}>
                    <AlertCircle className="h-4 w-4 text-[var(--accent-rose)] shrink-0" />
                    <p className="text-[var(--accent-rose)] text-sm">{error}</p>
                  </motion.div>
                )}

                <form onSubmit={handleLogin} className="space-y-5">
                  <div className="space-y-2">
                    <Label htmlFor="email">Email address</Label>
                    <div className="relative">
                      <Mail className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-[var(--text-quaternary)]" />
                      <Input id="email" type="email" value={email} onChange={(e) => setEmail(e.target.value)}
                        placeholder="admin@deepshield.ai" className="pl-10 h-12" autoComplete="email" />
                    </div>
                  </div>

                  <div className="space-y-2">
                    <Label htmlFor="password">Password</Label>
                    <div className="relative">
                      <Lock className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-[var(--text-quaternary)]" />
                      <Input id="password" type={showPassword ? "text" : "password"} value={password}
                        onChange={(e) => setPassword(e.target.value)} placeholder="Enter your password"
                        className="pl-10 pr-12 h-12" autoComplete="current-password" />
                      <button type="button" onClick={() => setShowPassword(!showPassword)}
                        className="absolute right-3 top-1/2 -translate-y-1/2 text-[var(--text-quaternary)] hover:text-[var(--text-secondary)] transition-colors">
                        {showPassword ? <EyeOff className="h-4 w-4" /> : <Eye className="h-4 w-4" />}
                      </button>
                    </div>
                  </div>

                  <div className="flex items-center justify-between">
                    <label className="flex items-center gap-2.5 cursor-pointer group">
                      <div className="relative">
                        <input type="checkbox" checked={rememberMe} onChange={(e) => setRememberMe(e.target.checked)} className="peer sr-only" />
                        <div className="h-4 w-4 rounded border border-[var(--border-default)] bg-[var(--bg-glass)] peer-checked:bg-[var(--accent-cyan)] peer-checked:border-[var(--accent-cyan)] transition-all flex items-center justify-center">
                          {rememberMe && <CheckCircle2 className="h-3 w-3 text-white" />}
                        </div>
                      </div>
                      <span className="text-sm text-[var(--text-tertiary)] group-hover:text-[var(--text-secondary)] transition-colors">Remember me</span>
                    </label>
                    <button type="button" onClick={() => { setShowForgot(true); setForgotEmail(email) }}
                      className="text-sm text-[var(--accent-cyan)] hover:text-[var(--accent-blue)] transition-colors">
                      Forgot password?
                    </button>
                  </div>

                  <Button type="submit" className="w-full h-12 text-base font-medium group" disabled={loading}>
                    {loading ? <Loader2 className="h-5 w-5 animate-spin" /> : (
                      <>Sign In<ArrowRight className="ml-2 h-4 w-4 group-hover:translate-x-1 transition-transform" /></>
                    )}
                  </Button>
                </form>
              </motion.div>
            ) : (
              <motion.div key="forgot" initial={{ opacity: 0, x: 20 }} animate={{ opacity: 1, x: 0 }} exit={{ opacity: 0, x: 20 }}>
                <AnimatePresence mode="wait">
                  {forgotStep === "email" && (
                    <motion.div key="fp-email" initial={{ opacity: 0 }} animate={{ opacity: 1 }} exit={{ opacity: 0 }}>
                      <button onClick={resetForgotState}
                        className="flex items-center gap-1 text-[var(--text-quaternary)] hover:text-[var(--text-secondary)] text-sm mb-6 transition-colors">
                        <ArrowLeft className="h-4 w-4" /> Back to login
                      </button>
                      <div className="mb-6">
                        <h2 className="text-xl font-semibold text-[var(--text-primary)]">Reset password</h2>
                        <p className="text-[var(--text-tertiary)] text-sm mt-1">Enter your email to receive a verification code</p>
                      </div>
                      <form onSubmit={handleSendForgotOTP} className="space-y-5">
                        <div className="space-y-2">
                          <Label htmlFor="forgot-email">Email address</Label>
                          <div className="relative">
                            <Mail className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-[var(--text-quaternary)]" />
                            <Input id="forgot-email" type="email" value={forgotEmail}
                              onChange={(e) => setForgotEmail(e.target.value)} placeholder="you@example.com"
                              className="pl-10 h-12" required />
                          </div>
                        </div>
                        <Button type="submit" className="w-full h-12" disabled={forgotLoading}>
                          {forgotLoading ? <Loader2 className="h-5 w-5 animate-spin" /> : "Send Verification OTP"}
                        </Button>
                      </form>
                    </motion.div>
                  )}

                  {forgotStep === "otp" && (
                    <motion.div key="fp-otp" initial={{ opacity: 0 }} animate={{ opacity: 1 }} exit={{ opacity: 0 }} className="text-center">
                      {otpVerified ? (
                        <motion.div initial={{ scale: 0 }} animate={{ scale: 1 }} className="py-8">
                          <div className="inline-flex items-center justify-center w-20 h-20 rounded-[var(--radius-xl)] mb-6"
                            style={{ background: "rgba(16, 185, 129, 0.08)", border: "1px solid rgba(16, 185, 129, 0.15)" }}>
                            <CheckCircle2 className="h-10 w-10 text-[var(--accent-emerald)]" />
                          </div>
                          <h3 className="text-xl font-bold text-[var(--text-primary)] mb-2">OTP Verified!</h3>
                          <Loader2 className="h-6 w-6 text-[var(--accent-cyan)] mx-auto mt-4 animate-spin" />
                        </motion.div>
                      ) : (
                        <>
                          <button onClick={() => setForgotStep("email")}
                            className="flex items-center gap-1 text-[var(--text-quaternary)] hover:text-[var(--text-secondary)] text-sm mb-6 transition-colors mx-auto">
                            <ArrowLeft className="h-4 w-4" /> Back
                          </button>
                          <div className="inline-flex items-center justify-center w-16 h-16 rounded-[var(--radius-lg)] mb-4"
                            style={{ background: "rgba(6, 182, 212, 0.08)", border: "1px solid rgba(6, 182, 212, 0.15)" }}>
                            <KeyRound className="h-8 w-8 text-[var(--accent-cyan)]" />
                          </div>
                          <h3 className="text-xl font-bold text-[var(--text-primary)] mb-2">Enter verification code</h3>
                          <p className="text-[var(--text-tertiary)] text-sm mb-8">
                            We sent a 6-digit code to<br />
                            <span className="text-[var(--text-primary)] font-medium">{forgotEmail}</span>
                          </p>

                          {forgotOtpError && (
                            <motion.div initial={{ opacity: 0, y: -10 }} animate={{ opacity: 1, y: 0 }}
                              className="mb-4 p-3 rounded-[var(--radius-md)] flex items-center gap-2"
                              style={{ background: "rgba(244, 63, 94, 0.08)", border: "1px solid rgba(244, 63, 94, 0.15)" }}>
                              <AlertCircle className="h-4 w-4 text-[var(--accent-rose)] shrink-0" />
                              <p className="text-[var(--accent-rose)] text-sm">{forgotOtpError}</p>
                            </motion.div>
                          )}

                          <div className="mb-6">
                            <OTPInput value={forgotOtp} onChange={setForgotOtp} disabled={forgotLoading} />
                          </div>

                          <div className="mb-6">
                            {countdown.isActive ? (
                              <p className="text-[var(--text-quaternary)] text-sm">
                                Code expires in <span className="text-[var(--accent-cyan)] font-mono font-medium">{countdown.formatted}</span>
                              </p>
                            ) : (
                              <p className="text-[var(--text-quaternary)] text-sm">Code expired</p>
                            )}
                          </div>

                          <Button onClick={handleVerifyForgotOTP} className="w-full h-12 text-base font-medium"
                            disabled={forgotLoading || forgotOtp.length !== 6}>
                            {forgotLoading ? <Loader2 className="h-5 w-5 animate-spin" /> : "Verify Code"}
                          </Button>

                          <div className="mt-6">
                            {countdown.isActive ? (
                              <p className="text-[var(--text-quaternary)] text-sm">
                                Resend code in <span className="font-mono">{countdown.formatted}</span>
                              </p>
                            ) : (
                              <button onClick={handleResendForgotOTP} disabled={forgotLoading}
                                className="text-sm text-[var(--accent-cyan)] hover:text-[var(--accent-blue)] transition-colors inline-flex items-center gap-1.5">
                                <RefreshCw className={`h-3.5 w-3.5 ${forgotLoading ? "animate-spin" : ""}`} />
                                Resend OTP
                              </button>
                            )}
                          </div>
                        </>
                      )}
                    </motion.div>
                  )}

                  {forgotStep === "reset" && (
                    <motion.div key="fp-reset" initial={{ opacity: 0 }} animate={{ opacity: 1 }} exit={{ opacity: 0 }}>
                      <div className="mb-6">
                        <h2 className="text-xl font-semibold text-[var(--text-primary)]">Set new password</h2>
                        <p className="text-[var(--text-tertiary)] text-sm mt-1">Enter your new password below</p>
                      </div>

                      {forgotOtpError && (
                        <motion.div initial={{ opacity: 0, y: -10 }} animate={{ opacity: 1, y: 0 }}
                          className="mb-4 p-3 rounded-[var(--radius-md)] flex items-center gap-2"
                          style={{ background: "rgba(244, 63, 94, 0.08)", border: "1px solid rgba(244, 63, 94, 0.15)" }}>
                          <AlertCircle className="h-4 w-4 text-[var(--accent-rose)] shrink-0" />
                          <p className="text-[var(--accent-rose)] text-sm">{forgotOtpError}</p>
                        </motion.div>
                      )}

                      <form onSubmit={handleResetPassword} className="space-y-5">
                        <div className="space-y-2">
                          <Label>New Password</Label>
                          <div className="relative">
                            <Lock className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-[var(--text-quaternary)]" />
                            <Input type={showNewPw ? "text" : "password"} value={newPassword}
                              onChange={(e) => setNewPassword(e.target.value)} placeholder="Min 6 characters"
                              className="pl-10 pr-12 h-12" />
                            <button type="button" onClick={() => setShowNewPw(!showNewPw)}
                              className="absolute right-3 top-1/2 -translate-y-1/2 text-[var(--text-quaternary)] hover:text-[var(--text-secondary)]">
                              {showNewPw ? <EyeOff className="h-4 w-4" /> : <Eye className="h-4 w-4" />}
                            </button>
                          </div>
                        </div>
                        <div className="space-y-2">
                          <Label>Confirm Password</Label>
                          <div className="relative">
                            <Lock className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-[var(--text-quaternary)]" />
                            <Input type={showConfirmPw ? "text" : "password"} value={confirmPassword}
                              onChange={(e) => setConfirmPassword(e.target.value)} placeholder="Re-enter password"
                              className="pl-10 pr-12 h-12" />
                            <button type="button" onClick={() => setShowConfirmPw(!showConfirmPw)}
                              className="absolute right-3 top-1/2 -translate-y-1/2 text-[var(--text-quaternary)] hover:text-[var(--text-secondary)]">
                              {showConfirmPw ? <EyeOff className="h-4 w-4" /> : <Eye className="h-4 w-4" />}
                            </button>
                          </div>
                        </div>
                        <Button type="submit" className="w-full h-12" disabled={forgotLoading}>
                          {forgotLoading ? <Loader2 className="h-5 w-5 animate-spin" /> : "Reset Password"}
                        </Button>
                      </form>
                    </motion.div>
                  )}

                  {forgotStep === "done" && (
                    <motion.div key="fp-done" initial={{ scale: 0.9, opacity: 0 }} animate={{ scale: 1, opacity: 1 }}
                      className="text-center py-8">
                      <div className="inline-flex items-center justify-center w-20 h-20 rounded-[var(--radius-xl)] mb-6"
                        style={{ background: "rgba(16, 185, 129, 0.08)", border: "1px solid rgba(16, 185, 129, 0.15)" }}>
                        <CheckCircle2 className="h-10 w-10 text-[var(--accent-emerald)]" />
                      </div>
                      <h3 className="text-xl font-bold text-[var(--text-primary)] mb-2">Password Reset!</h3>
                      <p className="text-[var(--text-tertiary)] text-sm mb-8">Your password has been updated successfully.</p>
                      <Button onClick={resetForgotState} className="gap-2">
                        Back to Sign In <ArrowRight className="h-4 w-4" />
                      </Button>
                    </motion.div>
                  )}
                </AnimatePresence>
              </motion.div>
            )}
          </AnimatePresence>
        </motion.div>

        <motion.p initial={{ opacity: 0 }} animate={{ opacity: 1 }} transition={{ delay: 0.5 }}
          className="text-center text-[var(--text-quaternary)] text-sm mt-6">
          Don&apos;t have an account?{" "}
          <Link href="/auth/register" className="text-[var(--accent-cyan)] hover:text-[var(--accent-blue)] font-medium transition-colors">
            Create account
          </Link>
        </motion.p>
      </motion.div>
    </div>
  )
}
