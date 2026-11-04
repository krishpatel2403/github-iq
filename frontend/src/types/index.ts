export interface User {
  id: number
  username: string
  email?: string
  avatar_url?: string
}

export interface Repository {
  id: number
  full_name: string
  owner_login: string
  description?: string
  html_url?: string
  stargazers_count: number
  forks_count: number
  watchers_count: number
  open_issues_count: number
  default_branch?: string
  language?: string
  pushed_at?: string
  synced_at?: string
}

export interface RepositoryAnalytics {
  id: number
  full_name: string
  html_url?: string
  stars: number
  forks: number
  watchers: number
  open_issues: number
  closed_issues: number
  open_prs: number
  merged_prs: number
  language?: string
  last_pushed?: string
  last_synced?: string
}

export interface SyncStatus {
  status: string
  records_fetched: number
  started_at?: string
  completed_at?: string
  error_message?: string
}
