// Checks every translation (or the ones named) against en.json, with the ICU parser next-intl uses: same
// keys, same arguments, same rich-text tags, valid syntax, and an `other` form in every plural. In a
// language whose `one` form also covers other numbers (Filipino's 3, Russian's 21, French's 0), a
// plural that shows the number must show it in `one` too, or 3 reads as "your first one"; `=1`
// is for exactly one. A plural of just the word ("credit"), with the number outside it, is fine.
// Usage: pnpm check:messages [code...]
import { readdirSync, readFileSync } from "node:fs"
import { parse, TYPE } from "@formatjs/icu-messageformat-parser"

const load = (code) =>
  JSON.parse(
    readFileSync(new URL(`../messages/${code}.json`, import.meta.url), "utf8")
  )
const flat = (value, prefix = "", out = {}) => {
  for (const [key, item] of Object.entries(value)) {
    const path = prefix ? `${prefix}.${key}` : key
    if (item && typeof item === "object" && !Array.isArray(item))
      flat(item, path, out)
    else out[path] = item
  }
  return out
}
const shape = (text, wideOne) => {
  const found = { args: new Set(), tags: new Set(), problems: [] }
  shapeElements(parse(text, { ignoreTag: false }), found, wideOne)
  return found
}
const shapeElements = (elements, found, wideOne) => {
  for (const element of elements) {
    if (element.type === TYPE.argument || element.type === TYPE.number)
      found.args.add(element.value)
    if (element.type === TYPE.plural || element.type === TYPE.select) {
      found.args.add(element.value)
      if (!element.options.other) found.problems.push("no other")
      const { one, other } = element.options
      const pound = (option) =>
        option?.value.some((part) => part.type === TYPE.pound)
      if (
        wideOne &&
        element.type === TYPE.plural &&
        one &&
        pound(other) &&
        !pound(one)
      )
        found.problems.push("one without #")
      for (const option of Object.values(element.options))
        shapeElements(option.value, found, wideOne)
    }
    if (element.type === TYPE.tag) {
      found.tags.add(element.value)
      shapeElements(element.children, found, wideOne)
    }
  }
}
// Whether the language's `one` form also covers a whole number other than 1.
const coversMoreThanOne = (code) => {
  const rules = new Intl.PluralRules(code)
  return [0, 2, 3, 5, 7, 21].some((number) => rules.select(number) === "one")
}
const same = (a, b) => a.size === b.size && [...a].every((item) => b.has(item))
const english = flat(load("en"))
let problems = 0
const codes = process.argv.slice(2).length
  ? process.argv.slice(2)
  : readdirSync(new URL("../messages/", import.meta.url))
      .map((name) => name.replace(".json", ""))
      .filter((code) => code !== "en")
for (const code of codes) {
  const other = flat(load(code))
  const wideOne = coversMoreThanOne(code)
  for (const key of Object.keys(english)) {
    if (!(key in other)) {
      console.log(`${code}: missing ${key}`)
      problems++
      continue
    }
    const [a, b] = [english[key], other[key]]
    if (Array.isArray(a)) {
      if (!Array.isArray(b) || a.length !== b.length) {
        console.log(`${code}: ${key} list differs`)
        problems++
      }
      continue
    }
    try {
      const want = shape(a, false),
        got = shape(b, wideOne)
      if (!same(want.args, got.args)) {
        console.log(
          `${code}: ${key} args ${[...want.args]} vs ${[...got.args]}`
        )
        problems++
      }
      if (!same(want.tags, got.tags)) {
        console.log(
          `${code}: ${key} tags ${[...want.tags]} vs ${[...got.tags]}`
        )
        problems++
      }
      if (got.problems.length) {
        console.log(`${code}: ${key} ${got.problems}`)
        problems++
      }
    } catch (error) {
      console.log(`${code}: ${key} doesn't parse: ${error.message}`)
      problems++
    }
  }
  for (const key of Object.keys(other))
    if (!(key in english)) {
      console.log(`${code}: extra ${key}`)
      problems++
    }
}
console.log(`problems: ${problems}`)
process.exit(problems ? 1 : 0)
