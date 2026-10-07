import { ImageResponse } from "next/og"

import english from "@/messages/en.json"

// The picture link previews show (LinkedIn, Slack, X) for every page without its own: the
// brand's colours as in app/icon.svg, the home page's promise and the site's description.
export const alt = english.site.homeTitle
export const size = { width: 1200, height: 630 }
export const contentType = "image/png"

const INK = "#0a0a0a"
const BLUE = "#2f7ae5"
const QUIET = "#6b6b6b"

export default function OpenGraphImage() {
  const lines = english.home.title.split("\n")

  return new ImageResponse(
    <div
      style={{
        width: "100%",
        height: "100%",
        display: "flex",
        flexDirection: "column",
        justifyContent: "space-between",
        padding: 80,
        background: "#ffffff",
        color: INK,
      }}
    >
      <div style={{ display: "flex", fontSize: 44, fontWeight: 600 }}>
        prepza<span style={{ color: BLUE }}>.</span>
      </div>
      <div style={{ display: "flex", flexDirection: "column" }}>
        {lines.map((line) => (
          <div
            key={line}
            style={{ display: "flex", fontSize: 92, fontWeight: 600 }}
          >
            {line}
            <span style={{ color: BLUE }}>.</span>
          </div>
        ))}
      </div>
      <div style={{ display: "flex", fontSize: 34, color: QUIET }}>
        {english.site.description}
      </div>
    </div>,
    size
  )
}
