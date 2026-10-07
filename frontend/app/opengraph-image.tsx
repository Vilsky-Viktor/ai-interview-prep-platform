import { readFile } from "node:fs/promises"
import { join } from "node:path"

import { ImageResponse } from "next/og"

import english from "@/messages/en.json"

// The picture link previews show (LinkedIn, Slack, X) for every page without its own: the logo
// and the home page's promise, centred, in the site's heading font (Poppins) and dark theme.
export const alt = english.site.homeTitle
export const size = { width: 1200, height: 630 }
export const contentType = "image/png"

// The site's dark theme (globals.css .dark): background, text, muted text and the logo's blue.
const BACKGROUND = "#0a0a0a"
const INK = "#fafafa"
const GREY = "#a1a1a1"
const BLUE = "#4c99f8"

/** One of the heading font's files, kept in assets/fonts. */
function font(file: string) {
  return readFile(join(process.cwd(), "assets/fonts", file))
}

export default async function OpenGraphImage() {
  const lines = english.home.title.split("\n")

  return new ImageResponse(
    <div
      style={{
        width: "100%",
        height: "100%",
        display: "flex",
        flexDirection: "column",
        alignItems: "center",
        justifyContent: "center",
        gap: 32,
        background: BACKGROUND,
        color: INK,
        fontFamily: "Poppins",
        letterSpacing: "-0.025em",
      }}
    >
      {/* The logo, as the Wordmark draws it: semibold. */}
      <div style={{ display: "flex", fontSize: 176, fontWeight: 600 }}>
        prepza<span style={{ color: BLUE }}>.</span>
      </div>
      {/* The titles as on the home page: lowercase, regular, grey, lines set tight. */}
      <div
        style={{
          display: "flex",
          flexDirection: "column",
          alignItems: "center",
          fontSize: 60,
          color: GREY,
          fontWeight: 400,
          lineHeight: 1.1,
        }}
      >
        {lines.map((line) => (
          <div key={line} style={{ display: "flex" }}>
            {line.toLowerCase()}
            <span style={{ color: BLUE }}>.</span>
          </div>
        ))}
      </div>
    </div>,
    {
      ...size,
      fonts: [
        {
          name: "Poppins",
          data: await font("Poppins-Regular.ttf"),
          weight: 400,
        },
        {
          name: "Poppins",
          data: await font("Poppins-SemiBold.ttf"),
          weight: 600,
        },
      ],
    }
  )
}
