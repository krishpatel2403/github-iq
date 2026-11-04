/**
 * Tests for the useAuth hook using Vitest.
 */

import { renderHook, act } from "@testing-library/react"
import { useAuth } from "@/hooks/useAuth"
import { api } from "@/lib/api"
import type { User } from "@/types"

vi.mock("@/lib/api", () => ({
  api: {
    get: vi.fn(),
    post: vi.fn(),
  },
}))

const mockUser: User = {
  id: 1,
  username: "testuser",
  email: "test@example.com",
  avatar_url: "https://avatars.githubusercontent.com/u/1",
}

describe("useAuth", () => {
  beforeEach(() => {
    vi.clearAllMocks()
  })

  it("returns user when /auth/me succeeds", async () => {
    ;(api.get as ReturnType<typeof vi.fn>).mockResolvedValueOnce({ data: mockUser })

    const { result } = renderHook(() => useAuth())

    expect(result.current.loading).toBe(true)
    expect(result.current.user).toBe(null)

    await act(async () => {
      await Promise.resolve()
    })

    expect(api.get).toHaveBeenCalledWith("/api/v1/auth/me")
    expect(result.current.user).toEqual(mockUser)
    expect(result.current.loading).toBe(false)
  })

  it("returns null user when /auth/me fails (unauthenticated)", async () => {
    ;(api.get as ReturnType<typeof vi.fn>).mockRejectedValueOnce({
      response: { status: 401 },
    })

    const { result } = renderHook(() => useAuth())

    await act(async () => {
      await Promise.resolve()
    })

    expect(result.current.user).toBe(null)
    expect(result.current.loading).toBe(false)
  })

  it("login navigates to GitHub authorize URL via window.location.href", () => {
    const { result } = renderHook(() => useAuth())

    const originalLocation = window.location
    const hrefCalls: string[] = []
    Object.defineProperty(window, "location", {
      value: {
        get href() {
          return "http://localhost"
        },
        set href(val: string) {
          hrefCalls.push(val)
        },
      },
      writable: true,
      configurable: true,
    })

    act(() => {
      result.current.login()
    })

    expect(hrefCalls.some((url) => url.includes("/api/v1/auth/github/login"))).toBe(
      true
    )

    // Restore
    window.location = originalLocation
  })

  it("logout calls api.post and clears user state", async () => {
    ;(api.post as ReturnType<typeof vi.fn>).mockResolvedValueOnce({})

    const { result } = renderHook(() => useAuth())

    // Mock window.location.href to avoid jsdom navigation error
    const originalLocation = window.location
    const hrefCalls: string[] = []
    Object.defineProperty(window, "location", {
      value: {
        get href() {
          return "http://localhost"
        },
        set href(val: string) {
          hrefCalls.push(val)
        },
      },
      writable: true,
      configurable: true,
    })

    await act(async () => {
      await result.current.logout()
    })

    expect(api.post).toHaveBeenCalledWith("/api/v1/auth/logout")
    expect(hrefCalls.some((url) => url === "/login")).toBe(true)
    expect(result.current.user).toBe(null)

    // Restore
    window.location = originalLocation
  })
})
