import { afterEach, beforeEach, describe, expect, it, vi } from "vitest"

import {
  clock,
  movedAway,
  nextPhase,
  recordingType,
  startRecording,
} from "@/lib/voice"

describe("nextPhase", () => {
  it("records while held, transcribes when let go, and ends with the transcript", () => {
    expect(nextPhase("idle", "start")).toBe("recording")
    expect(nextPhase("recording", "stop")).toBe("transcribing")
    expect(nextPhase("transcribing", "done")).toBe("idle")
  })

  it("drops a cancelled recording", () => {
    expect(nextPhase("recording", "cancel")).toBe("idle")
  })

  it("ignores late or repeated events", () => {
    expect(nextPhase("idle", "stop")).toBe("idle")
    expect(nextPhase("idle", "cancel")).toBe("idle")
    expect(nextPhase("transcribing", "start")).toBe("transcribing")
    expect(nextPhase("transcribing", "cancel")).toBe("transcribing")
    expect(nextPhase("recording", "start")).toBe("recording")
  })
})

describe("movedAway and clock", () => {
  it("cancels once the pointer slides the limit away", () => {
    expect(movedAway({ x: 0, y: 0 }, { x: 30, y: 20 }, 40)).toBe(false)
    expect(movedAway({ x: 0, y: 0 }, { x: 0, y: -40 }, 40)).toBe(true)
  })

  it("shows minutes and seconds", () => {
    expect(clock(7.9)).toBe("0:07")
    expect(clock(60)).toBe("1:00")
  })
})

/** A MediaRecorder that records `chunks` and supports `types`. */
function fakeRecorder(types: string[]) {
  const tracks = [{ stop: vi.fn() }]

  class FakeRecorder {
    static isTypeSupported = (type: string) => types.includes(type)
    state = "inactive"
    mimeType: string
    ondataavailable: ((event: { data: Blob }) => void) | null = null
    onstop: ((event: Event) => void) | null = null

    constructor(_stream: unknown, options: { mimeType: string }) {
      this.mimeType = options.mimeType
    }

    start() {
      this.state = "recording"
    }

    stop() {
      this.state = "inactive"
      this.ondataavailable?.({ data: new Blob(["sound"]) })
      this.onstop?.(new Event("stop"))
    }
  }

  vi.stubGlobal("MediaRecorder", FakeRecorder)
  vi.stubGlobal("navigator", {
    mediaDevices: { getUserMedia: async () => ({ getTracks: () => tracks }) },
  })

  return tracks[0]
}

describe("recording", () => {
  beforeEach(() => {
    vi.useFakeTimers()
  })

  afterEach(() => {
    vi.useRealTimers()
    vi.unstubAllGlobals()
  })

  it("picks webm with opus, then mp4, and nothing without MediaRecorder", () => {
    expect(recordingType()).toBeNull()

    fakeRecorder(["audio/webm;codecs=opus", "audio/mp4"])
    expect(recordingType()).toBe("audio/webm;codecs=opus")

    fakeRecorder(["audio/mp4"])
    expect(recordingType()).toBe("audio/mp4")
  })

  it("gives the recording in its format, and releases the microphone", async () => {
    const track = fakeRecorder(["audio/webm;codecs=opus"])
    const recording = await startRecording("audio/webm;codecs=opus")
    vi.advanceTimersByTime(2000)
    const audio = await recording.stop()

    expect(audio?.type).toBe("audio/webm")
    expect(await audio?.text()).toBe("sound")
    expect(track.stop).toHaveBeenCalled()
  })

  it("sends nothing under half a second", async () => {
    fakeRecorder(["audio/mp4"])
    const recording = await startRecording("audio/mp4")
    vi.advanceTimersByTime(300)

    expect(await recording.stop()).toBeNull()
  })

  it("drops a cancelled recording and releases the microphone", async () => {
    const track = fakeRecorder(["audio/mp4"])
    const recording = await startRecording("audio/mp4")
    vi.advanceTimersByTime(2000)
    recording.cancel()

    expect(track.stop).toHaveBeenCalled()
  })
})
