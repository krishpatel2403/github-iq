import { useState, useEffect, useCallback } from "react"
import { api } from "@/lib/api"
import type { User } from "@/types"

export function useAuth() {
  const [user, setUser] = useState<User | null>(null)
  const [loading, setLoading] = useState(true)

  const fetchMe = useCallback(async () => {
    try {
      const res = await api.get<User>("/api/v1/auth/me")
      setUser(res.data)
    } catch {
      setUser(null)
    } finally {
      setLoading(false)
    }
  }, [])

  useEffect(() => {
    fetchMe()
    const onExpire = () => {
      setUser(null)
      setLoading(false)
    }
    window.addEventListener("auth:expired", onExpire)
    return () => window.removeEventListener("auth:expired", onExpire)
  }, [fetchMe])

  /** Redirect the browser to the GitHub OAuth authorize URL. */
  const login = () => {
    // Navigate the whole window so the session cookie is set by the backend
    // redirect response (axios would not follow the 302 to GitHub correctly).
    window.location.href = `${import.meta.env.VITE_API_URL || "http://localhost:8000"}/api/v1/auth/github/login`
  }

  /** Clear the session and return to the login page. */
  const logout = async () => {
    try {
      await api.post("/api/v1/auth/logout")
    } catch {
      // ignore — cookie is cleared by the backend response anyway
    }
    setUser(null)
    setLoading(false)
    window.location.href = "/login"
  }

  return { user, loading, login, logout, refetch: fetchMe }
}
