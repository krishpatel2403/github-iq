/**
 * Tests for Login page using Vitest.
 */

import { render, screen, fireEvent } from "@testing-library/react"
import { Login } from "@/pages/Login"
import { useAuth } from "@/hooks/useAuth"

// Mock modules
vi.mock("@/lib/api", () => ({
  api: { get: vi.fn(), post: vi.fn() },
}))

vi.mock("@/hooks/useAuth", () => ({
  useAuth: vi.fn(),
}))

const mockUseAuth = vi.mocked(useAuth)

describe("Login", () => {
  beforeEach(() => {
    vi.clearAllMocks()
    vi.mocked(mockUseAuth).mockReturnValue({
      login: vi.fn(),
      user: null,
      loading: false,
      logout: vi.fn(),
      refetch: vi.fn(),
    })
  })

  it("renders heading and connect button", () => {
    render(<Login />)

    expect(screen.getByText(/GitHubIQ/)).toBeInTheDocument()
    expect(screen.getByText(/Connect GitHub/)).toBeInTheDocument()
  })

  it("shows privacy notice", () => {
    render(<Login />)

    expect(screen.getByText(/No password stored./)).toBeInTheDocument()
  })

  it("calls useAuth.login when Connect GitHub is clicked", () => {
    const mockLogin = vi.fn()
    vi.mocked(mockUseAuth).mockReturnValue({
      login: mockLogin,
      user: null,
      loading: false,
      logout: vi.fn(),
      refetch: vi.fn(),
    })

    render(<Login />)

    fireEvent.click(screen.getByText(/Connect GitHub/))

    expect(mockLogin).toHaveBeenCalledTimes(1)
  })
})
