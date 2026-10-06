import { serverFetch } from "@/lib/server-api"

/** Whether prepza is paused (the admin zone's emergency pause). */
export async function isPaused() {
  const pause = await serverFetch<{ paused: boolean }>("/companies/pause")

  return Boolean(pause?.paused)
}
