import {
  Geist,
  Geist_Mono,
  Noto_Sans,
  Noto_Sans_Arabic,
  Noto_Sans_Devanagari,
  Noto_Sans_Hebrew,
  Noto_Sans_JP,
  Noto_Sans_KR,
  Noto_Sans_SC,
  Noto_Sans_Thai,
  Poppins,
} from "next/font/google"

// The site's fonts. Geist and Poppins carry the design; the Noto fonts cover the scripts they
// lack, for the languages the site speaks (Arabic and Persian, Hebrew, Hindi, Thai, Vietnamese,
// Japanese, Chinese, Korean). Each font's files download only for pages with characters in its
// script, and the script fonts aren't preloaded, so an English page loads nothing extra.

const geist = Geist({
  subsets: ["latin", "latin-ext", "cyrillic"],
  variable: "--font-geist",
})

const geistMono = Geist_Mono({ subsets: ["latin"], variable: "--font-mono" })

const poppins = Poppins({
  subsets: ["latin"],
  weight: ["500", "600"],
  variable: "--font-poppins",
})

// next/font reads its options literally, so each script font repeats them: not preloaded.
const vietnamese = Noto_Sans({
  preload: false,
  display: "swap",
  subsets: ["vietnamese"],
  variable: "--font-vietnamese",
})
const arabic = Noto_Sans_Arabic({
  preload: false,
  display: "swap",
  subsets: ["arabic"],
  variable: "--font-arabic",
})
const hebrew = Noto_Sans_Hebrew({
  preload: false,
  display: "swap",
  subsets: ["hebrew"],
  variable: "--font-hebrew",
})
const devanagari = Noto_Sans_Devanagari({
  preload: false,
  display: "swap",
  subsets: ["devanagari"],
  variable: "--font-devanagari",
})
const thai = Noto_Sans_Thai({
  preload: false,
  display: "swap",
  subsets: ["thai"],
  variable: "--font-thai",
})
const japanese = Noto_Sans_JP({
  preload: false,
  display: "swap",
  variable: "--font-japanese",
})
const chinese = Noto_Sans_SC({
  preload: false,
  display: "swap",
  variable: "--font-chinese",
})
const korean = Noto_Sans_KR({
  preload: false,
  display: "swap",
  variable: "--font-korean",
})

// The class names that define every font's CSS variable, for <html>.
export const FONT_VARIABLES = [
  geist,
  geistMono,
  poppins,
  vietnamese,
  arabic,
  hebrew,
  devanagari,
  thai,
  japanese,
  chinese,
  korean,
].map((font) => font.variable)
