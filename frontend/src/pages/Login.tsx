import { useState } from "react"
import { LoginButton } from "@/components/LoginButton"
import { Loading } from "@/components/Loading"
import { ErrorBanner } from "@/components/ErrorBanner"
import { useAuth } from "@/hooks/useAuth"

export function Login() {
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const { login } = useAuth()

  const handleLogin = async () => {
    setError(null)
    setLoading(true)
    try {
      login()
    } catch (err) {
      setError((err as { message?: string }).message || "Unable to start GitHub login. Try again.")
    } finally {
      setLoading(false)
    }
  }

  if (loading) return <Loading message="Signing in with GitHub…" />

  return (
    <div className="max-w-md mx-auto py-12 px-4">
      <div className="text-center mb-8">
        <h1 className="text-3xl font-bold text-slate-900">GitHubIQ</h1>
        <p className="text-slate-500 mt-2">
          Connect your GitHub account to track repositories and view analytics.
        </p>
      </div>

      {error && <ErrorBanner message={error} onDismiss={() => setError(null)} />}

      <div className="space-y-3">
        <LoginButton onLogin={handleLogin} />
        <p className="text-xs text-slate-400 text-center">
          No password stored. We only read your public GitHub profile and the
          repositories you choose to track.
        </p>
      </div>
    </div>
  )
}
