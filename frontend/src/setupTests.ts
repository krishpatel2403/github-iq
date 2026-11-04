/**
 * Vitest setup file — runs before each test file.
 * Configures jsdom environment and global mocks.
 */

import "@testing-library/jest-dom"

// Mock matchMedia (jsdom doesn't provide it)
Object.defineProperty(window, "matchMedia", {
  writable: true,
  value: vi.fn().mockImplementation((query) => ({
    matches: false,
    media: query,
    onchange: null,
    addListener: vi.fn(), // deprecated
    removeListener: vi.fn(), // deprecated
    addEventListener: vi.fn(),
    removeEventListener: vi.fn(),
    dispatchEvent: vi.fn(),
  })),
})
