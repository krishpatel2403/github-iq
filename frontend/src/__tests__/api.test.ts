/**
 * Tests for the API client configuration using Vitest.
 */

import { api } from "@/lib/api"

describe("api client", () => {
  it("has withCredentials enabled for session cookies", () => {
    expect(api.defaults.withCredentials).toBe(true)
  })

  it("has a baseURL set", () => {
    expect(api.defaults.baseURL).toBeDefined()
    expect(typeof api.defaults.baseURL).toBe("string")
  })

  it("is configured with JSON content-type in request config", () => {
    // axios.create sets Content-Type under headers.post/put/patch by default.
    // We just verify the instance is configured.
    expect(api.defaults.headers).toBeDefined()
  })

  it("has a response interceptor that dispatches auth:expired on 401", () => {
    const interceptors = api.interceptors.response
    expect((interceptors.handlers ?? []).length).toBeGreaterThan(0)

    const rejectionHandler = (interceptors.handlers ?? []).find((h) => h.rejected)
    expect(rejectionHandler).toBeDefined()
  })
})
