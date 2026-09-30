const dateFormat = new Intl.DateTimeFormat("en", { dateStyle: "medium" })

export function formatDate(iso: string) {
  return dateFormat.format(new Date(iso))
}

export function plural(count: number, word: string) {
  return `${count} ${word}${count === 1 ? "" : "s"}`
}

export function formatCost(usd: number) {
  return usd < 0.01 ? "under $0.01" : `$${usd.toFixed(2)}`
}
