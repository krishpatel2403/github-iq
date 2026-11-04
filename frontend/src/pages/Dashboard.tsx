import { useState, useEffect } from "react"
import { api } from "@/lib/api"
import type { Repository } from "@/types"
import { RepoCard } from "@/components/RepoCard"
import { EmptyState } from "@/components/EmptyState"
import { ErrorBanner } from "@/components/ErrorBanner"
import { useAuth } from "@/hooks/useAuth"

export function Dashboard() {
  const [repos, setRepos] = useState<Repository[]>([])
  const [error, setError] = useState<string | null>(null)
  const { user, logout } = useAuth()

  useEffect(() => {
    // Repos only load once the user is known.
    if (!user) return
    api.get<Repository[]>("/api/v1/repositories").then((r) => setRepos(r.data)).catch(() => setRepos([]))
  }, [user])

  const handleAddRepo = async (fullName: string) => {
    try {
      await api.post("/api/v1/repositories", { full_name: fullName })
      const r = await api.get<Repository[]>("/api/v1/repositories")
      setRepos(r.data)
    } catch (err) {
      setError((err as { response?: { data?: { detail?: string } } }).response?.data?.detail || "Failed to add repository.")
    }
  }

  const handleRefresh = async () => {
    try {
      await api.post("/api/v1/sync/repositories", { force: true })
      const r = await api.get<Repository[]>("/api/v1/repositories")
      setRepos(r.data)
    } catch (err) {
      setError((err as { response?: { data?: { detail?: string } } }).response?.data?.detail || "Sync failed.")
    }
  }

  const totalStars = repos.reduce((s, r) => s + r.stargazers_count, 0)

  if (!user) {
    return (
      <div className="max-w-md mx-auto py-12">
        <p className="text-slate-600 mb-6">Please connect your GitHub account.</p>
        <button
          onClick={() => window.location.href = "/api/v1/auth/github/login"}
          className="px-4 py-2 text-sm font-medium text-white bg-brand-600 rounded-lg hover:bg-brand-700"
        >
          Connect GitHub
        </button>
      </div>
    )
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-xl font-bold text-slate-900">Dashboard</h2>
          <p className="text-slate-500">Hi, {user.username}</p>
        </div>
        <div className="flex items-center gap-3">
          <button
            onClick={handleRefresh}
            className="px-4 py-2 text-sm font-medium text-brand-600 hover:text-brand-700"
          >
            Refresh
          </button>
          <button
            onClick={logout}
            className="px-4 py-2 text-sm font-medium text-white bg-slate-900 rounded-lg hover:bg-slate-800"
          >
            Sign out
          </button>
        </div>
      </div>

      {error && <ErrorBanner message={error} onDismiss={() => setError(null)} />}

      <div className="grid grid-cols-2 gap-4 mb-6">
        <div className="bg-white p-4 rounded-xl border border-slate-200 shadow-sm">
          <p className="text-xs text-slate-400 uppercase tracking-wider">Tracked repos</p>
          <p className="text-2xl font-bold">{repos.length}</p>
        </div>
        <div className="bg-white p-4 rounded-xl border border-slate-200 shadow-sm">
          <p className="text-xs text-slate-400 uppercase tracking-wider">Total stars</p>
          <p className="text-2xl font-bold">{totalStars}</p>
        </div>
      </div>

      <div className="flex items-center gap-2 mb-3">
        <h3 className="text-sm font-semibold text-slate-700">Tracked repositories</h3>
        <button
          onClick={() => {
            const name = window.prompt("Enter repo as owner/name (e.g. facebook/react)")
            if (name) handleAddRepo(name)
          }}
          className="text-xs text-brand-600 hover:underline"
        >
          Add repository
        </button>
      </div>

      {repos.length === 0 ? (
        <EmptyState
          title="No repositories yet"
          description="Add a GitHub repository to start tracking its analytics."
          action={
            <button
              onClick={() => {
                const name = window.prompt("Enter repo as owner/name (e.g. facebook/react)")
                if (name) handleAddRepo(name)
              }}
              className="px-4 py-2 text-sm font-medium text-white bg-brand-600 rounded hover:bg-brand-700"
            >
              Add your first repository
            </button>
          }
        />
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {repos.map((repo) => (
            <RepoCard key={repo.id} repo={repo} />
          ))}
        </div>
      )}
    </div>
  )
}
