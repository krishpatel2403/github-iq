/**
 * Tests for RepoCard component using Vitest.
 */

import { render, screen } from "@testing-library/react"
import { RepoCard } from "@/components/RepoCard"

const mockRepo = {
  id: 1,
  full_name: "facebook/react",
  owner_login: "facebook",
  description: "A declarative, efficient, and flexible JavaScript UI library",
  html_url: "https://github.com/facebook/react",
  stargazers_count: 205000,
  forks_count: 42000,
  watchers_count: 7000,
  open_issues_count: 900,
  default_branch: "main",
  language: "JavaScript",
  pushed_at: "2024-01-15T10:30:00Z",
  synced_at: "2024-01-16T12:00:00Z",
}

describe("RepoCard", () => {
  it("renders repository name and language badge", () => {
    render(<RepoCard repo={mockRepo} />)

    expect(screen.getByText("facebook/react")).toBeInTheDocument()
    expect(screen.getByText("JavaScript")).toBeInTheDocument()
  })

  it("renders stats: stars, forks, watchers", () => {
    render(<RepoCard repo={mockRepo} />)

    expect(screen.getByText("205000")).toBeInTheDocument()
    expect(screen.getByText("42000")).toBeInTheDocument()
    expect(screen.getByText("7000")).toBeInTheDocument()
  })

  it("renders open issues count", () => {
    render(<RepoCard repo={mockRepo} />)

    expect(screen.getByText("900")).toBeInTheDocument()
  })

  it("renders last synced timestamp", () => {
    render(<RepoCard repo={mockRepo} />)

    expect(screen.getByText(/Last synced:/)).toBeInTheDocument()
    expect(screen.getByText(/2024-01-16T12:00:00Z/)).toBeInTheDocument()
  })

  it("handles missing language gracefully (no badge)", () => {
    render(<RepoCard repo={{ ...mockRepo, language: undefined }} />)

    expect(screen.queryByText("JavaScript")).not.toBeInTheDocument()
    expect(screen.getByText("facebook/react")).toBeInTheDocument()
  })

  it("handles missing synced_at gracefully", () => {
    render(<RepoCard repo={{ ...mockRepo, synced_at: undefined }} />)

    expect(screen.getByText(/Last synced: never/)).toBeInTheDocument()
  })
})
