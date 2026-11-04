import type { Repository } from "@/types"
import { Star, GitBranch, Eye, List } from "lucide-react"

export function RepoCard({ repo }: { repo: Repository }) {
  return (
    <div className="border border-slate-200 rounded-xl p-4 bg-white shadow-sm">
      <div className="flex items-center justify-between mb-2">
        <h3 className="font-semibold text-slate-900">{repo.full_name}</h3>
        {repo.language && (
          <span className="text-xs font-medium bg-brand-50 text-brand-600 px-2 py-0.5 rounded">
            {repo.language}
          </span>
        )}
      </div>
      {repo.description && <p className="text-sm text-slate-500 mb-3">{repo.description}</p>}
      <div className="grid grid-cols-4 gap-2 text-xs text-slate-500">
        <div className="flex items-center gap-1">
          <Star className="w-4 h-4" /> {repo.stargazers_count}
        </div>
        <div className="flex items-center gap-1">
          <GitBranch className="w-4 h-4" /> {repo.forks_count}
        </div>
        <div className="flex items-center gap-1">
          <Eye className="w-4 h-4" /> {repo.watchers_count}
        </div>
        <div className="flex items-center gap-1">
          <List className="w-4 h-4" /> {repo.open_issues_count}
        </div>
      </div>
      <div className="mt-3 text-[10px] uppercase tracking-wider text-slate-400">
        Last synced: {repo.synced_at || "never"}
      </div>
    </div>
  )
}
