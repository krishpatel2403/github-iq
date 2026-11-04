import { useState, useEffect } from "react"
import { useParams, useNavigate } from "react-router-dom"
import { api } from "@/lib/api"
import type { RepositoryAnalytics } from "@/types"
import { Loading } from "@/components/Loading"
import { ErrorBanner } from "@/components/ErrorBanner"
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from "recharts"

export function RepoAnalytics() {
  const { id } = useParams<{ id: string }>()
  const navigate = useNavigate()
  const [repo, setRepo] = useState<RepositoryAnalytics | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    if (!id) return
    api
      .get<RepositoryAnalytics>(`/api/v1/repositories/${id}/analytics`)
      .then((r) => setRepo(r.data))
      .catch(() => setError("Failed to load repository analytics."))
      .finally(() => setLoading(false))
  }, [id])

  if (loading) return <Loading message="Loading repository analytics…" />
  if (!repo) {
    return (
      <div className="max-w-md mx-auto py-12">
        <p className="text-slate-600 mb-4">{error || "Repository not found."}</p>
        <button
          onClick={() => navigate("/")}
          className="px-4 py-2 text-sm font-medium text-white bg-brand-600 rounded-lg hover:bg-brand-700"
        >
          Back to dashboard
        </button>
      </div>
    )
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-xl font-bold text-slate-900">{repo.full_name}</h2>
          <p className="text-slate-500 text-sm">{repo.language}</p>
        </div>
        <a
          href={repo.html_url}
          target="_blank"
          rel="noopener noreferrer"
          className="px-4 py-2 text-sm font-medium text-white bg-slate-900 rounded hover:bg-slate-800"
        >
          Open on GitHub
        </a>
      </div>

      {error && <ErrorBanner message={error} onDismiss={() => setError(null)} />}

      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        <div className="bg-white p-4 rounded-xl border border-slate-200 shadow-sm">
          <p className="text-xs text-slate-400 uppercase tracking-wider">Stars</p>
          <p className="text-3xl font-bold">{repo.stars}</p>
        </div>
        <div className="bg-white p-4 rounded-xl border border-slate-200 shadow-sm">
          <p className="text-xs text-slate-400 uppercase tracking-wider">Forks</p>
          <p className="text-3xl font-bold">{repo.forks}</p>
        </div>
        <div className="bg-white p-4 rounded-xl border border-slate-200 shadow-sm">
          <p className="text-xs text-slate-400 uppercase tracking-wider">Watchers</p>
          <p className="text-3xl font-bold">{repo.watchers}</p>
        </div>
        <div className="bg-white p-4 rounded-xl border border-slate-200 shadow-sm">
          <p className="text-xs text-slate-400 uppercase tracking-wider">Open issues</p>
          <p className="text-3xl font-bold">{repo.open_issues}</p>
        </div>
      </div>

      <div className="bg-white p-6 rounded-xl border border-slate-200 shadow-sm">
        <h3 className="text-sm font-semibold text-slate-700 mb-4">Issues vs Pull Requests</h3>
        <div className="h-64">
          <ResponsiveContainer width="100%" height="100%">
            <BarChart data={[{ name: "Open issues", value: repo.open_issues }, { name: "Closed issues", value: repo.closed_issues }, { name: "Open PRs", value: repo.open_prs }, { name: "Merged PRs", value: repo.merged_prs }]}>
              <CartesianGrid strokeDasharray="3 3" vertical={false} />
              <XAxis dataKey="name" />
              <YAxis />
              <Tooltip />
              <Bar dataKey="value" fill="#3b82f6" radius={[4, 4, 0, 0]} />
            </BarChart>
          </ResponsiveContainer>
        </div>
      </div>

      <div className="text-xs text-slate-400 mt-2">
        Last synced: {repo.last_synced || "never"}
      </div>
    </div>
  )
}
