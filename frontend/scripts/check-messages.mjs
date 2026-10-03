// Checks every translation (or the ones named) against en.json, with the ICU parser next-intl uses: same
// keys, same arguments, same rich-text tags, valid syntax, and an `other` form in every plural.
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
const shape = (text, args = new Set(), tags = new Set(), problems = []) => {
  for (const element of parse(text, { ignoreTag: false })) {
    if (element.type === TYPE.argument || element.type === TYPE.number)
      args.add(element.value)
    if (element.type === TYPE.plural || element.type === TYPE.select) {
      args.add(element.value)
      if (!element.options.other) problems.push("no other")
      for (const option of Object.values(element.options))
        shapeElements(option.value, args, tags, problems)
    }
    if (element.type === TYPE.tag) {
      tags.add(element.value)
      shapeElements(element.children, args, tags, problems)
    }
  }
  return { args, tags, problems }
}
const shapeElements = (elements, args, tags, problems) => {
  for (const element of elements) {
    if (element.type === TYPE.argument || element.type === TYPE.number)
      args.add(element.value)
    if (element.type === TYPE.plural || element.type === TYPE.select) {
      args.add(element.value)
      if (!element.options.other) problems.push("no other")
      for (const option of Object.values(element.options))
        shapeElements(option.value, args, tags, problems)
    }
    if (element.type === TYPE.tag) {
      tags.add(element.value)
      shapeElements(element.children, args, tags, problems)
    }
  }
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
      const want = shape(a),
        got = shape(b)
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
