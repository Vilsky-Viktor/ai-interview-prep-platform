/** A PDF file: a page with a folded corner and the red "PDF" label. */
export function PdfIcon({ className }: { className?: string }) {
  return (
    <svg viewBox="0 0 40 48" aria-hidden className={className}>
      <path
        d="M8 1.5h19L37.5 12v32a2.5 2.5 0 0 1-2.5 2.5H8A2.5 2.5 0 0 1 5.5 44V4A2.5 2.5 0 0 1 8 1.5Z"
        fill="#fff"
        stroke="#d4d4d8"
      />
      <path d="M27 1.5V10a2 2 0 0 0 2 2h8.5" fill="#f4f4f5" stroke="#d4d4d8" />
      <rect x="1" y="25" width="30" height="14" rx="3" fill="#e5252a" />
      <text
        x="16"
        y="35.5"
        fill="#fff"
        fontFamily="Arial, sans-serif"
        fontSize="10"
        fontWeight="700"
        textAnchor="middle"
      >
        PDF
      </text>
    </svg>
  )
}
