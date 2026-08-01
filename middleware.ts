import { NextResponse } from "next/server"
import type { NextRequest } from "next/server"

function decodeJwtPayload(token: string): Record<string, unknown> | null {
  try {
    const base64 = token.split(".")[1]
    const json = atob(base64.replace(/-/g, "+").replace(/_/g, "/"))
    return JSON.parse(json)
  } catch {
    return null
  }
}

export function middleware(request: NextRequest) {
  const { pathname } = request.nextUrl
  const token = request.cookies.get("ds_token")?.value
    || request.headers.get("authorization")?.replace("Bearer ", "")

  const publicPaths = ["/auth/login", "/auth/register", "/health"]
  if (publicPaths.some(p => pathname.startsWith(p))) {
    if (token && pathname.startsWith("/auth/")) {
      const payload = decodeJwtPayload(token)
      if (payload && !isTokenExpired(payload)) {
        const role = payload.role as string
        return NextResponse.redirect(new URL(role === "admin" ? "/admin/dashboard" : "/dashboard", request.url))
      }
    }
    return NextResponse.next()
  }

  if (!token) {
    const loginUrl = new URL("/auth/login", request.url)
    loginUrl.searchParams.set("from", pathname)
    return NextResponse.redirect(loginUrl)
  }

  const payload = decodeJwtPayload(token)
  if (!payload || isTokenExpired(payload)) {
    const response = NextResponse.redirect(new URL("/auth/login", request.url))
    response.cookies.delete("ds_token")
    return response
  }

  const role = payload.role as string

  if (pathname.startsWith("/admin") && role !== "admin") {
    return NextResponse.redirect(new URL("/dashboard", request.url))
  }

  if (pathname === "/admin" && role === "admin") {
    return NextResponse.redirect(new URL("/admin/dashboard", request.url))
  }

  return NextResponse.next()
}

function isTokenExpired(payload: Record<string, unknown>): boolean {
  const exp = payload.exp as number | undefined
  if (!exp) return false
  return Date.now() >= exp * 1000
}

export const config = {
  matcher: [
    "/admin/:path*",
    "/dashboard/:path*",
    "/auth/:path*",
    "/((?!_next/static|_next/image|favicon.ico|api).*)",
  ],
}
