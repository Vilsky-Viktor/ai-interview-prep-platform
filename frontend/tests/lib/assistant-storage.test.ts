import { afterEach, beforeEach, describe, expect, it, vi } from "vitest"

import { clearChat, readChat, saveChat, wasOpen } from "@/lib/assistant-storage"

/** A Storage kept in a map. */
function memory() {
  const items = new Map<string, string>()

  return {
    getItem: (name: string) => items.get(name) ?? null,
    setItem: (name: string, value: string) => void items.set(name, value),
    removeItem: (name: string) => void items.delete(name),
  }
}

beforeEach(() => {
  vi.stubGlobal("localStorage", memory())
  vi.stubGlobal("sessionStorage", memory())
})

afterEach(() => {
  vi.unstubAllGlobals()
})

describe("the saved chat", () => {
  it("keeps the signed-in conversation and the visitor's messages apart", () => {
    saveChat(true, { open: true, conversationId: "c1" })
    saveChat(false, {
      messages: [{ role: "user", content: "Hi", blocks: [] }],
    })

    expect(readChat(true)).toEqual({ open: true, conversationId: "c1" })
    expect(readChat(false).messages).toHaveLength(1)
    expect(localStorage.getItem("prepza:assistant:visitor")).toBeNull()
  })

  it("adds a change to what's saved", () => {
    saveChat(true, { open: true, conversationId: "c1" })
    saveChat(true, { open: false })

    expect(readChat(true)).toEqual({ open: false, conversationId: "c1" })
  })

  it("reads nothing from a broken or blocked store", () => {
    localStorage.setItem("prepza:assistant", "{broken")
    expect(readChat(true)).toEqual({})

    vi.stubGlobal("localStorage", {
      getItem: () => {
        throw new Error("blocked")
      },
      setItem: () => {
        throw new Error("blocked")
      },
    })
    expect(readChat(true)).toEqual({})
    expect(() => saveChat(true, { open: true })).not.toThrow()
  })

  it("reopens for the visitor who was signing in, and signing out forgets both", () => {
    saveChat(false, { open: true })
    expect(wasOpen(true)).toBe(true)
    expect(wasOpen(false)).toBe(true)

    saveChat(true, { open: true, conversationId: "c1" })
    clearChat(true)
    expect(readChat(true)).toEqual({})
    expect(readChat(false)).toEqual({})
    expect(wasOpen(true)).toBe(false)
  })

  it("forgets only the visitor's chat once it's part of a saved conversation", () => {
    saveChat(true, { conversationId: "c1" })
    saveChat(false, { open: true })
    clearChat(false)

    expect(readChat(true)).toEqual({ conversationId: "c1" })
    expect(readChat(false)).toEqual({})
  })
})
