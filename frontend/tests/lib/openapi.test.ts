import { describe, expect, it } from "vitest"

import {
  errorsOf,
  fieldsOf,
  operationsOf,
  richText,
  schemasOf,
  successSchema,
  typeOf,
} from "@/lib/openapi"
import type { OpenApi } from "@/types/openapi"

const SPEC: OpenApi = {
  info: { title: "prepza API", version: "1" },
  paths: {
    "/interviews": {
      get: {
        summary: "List interviews",
        responses: {
          "200": {
            description: "OK",
            content: {
              "application/json": {
                schema: {
                  type: "array",
                  items: { $ref: "#/components/schemas/Interview" },
                },
              },
            },
          },
          "401": { description: "No key" },
          "422": { description: "Validation Error" },
        },
      },
    },
  },
  components: {
    schemas: {
      Interview: {
        properties: {
          id: { type: "string", format: "uuid" },
          title: {
            anyOf: [{ type: "string" }, { type: "null" }],
            description: "Null while generating",
          },
        },
        required: ["id"],
      },
      HTTPValidationError: {},
    },
  },
}

describe("the API docs read the OpenAPI description", () => {
  it("names types in a few words", () => {
    expect(typeOf({ type: "string", format: "uuid" })).toBe("string (uuid)")
    expect(typeOf({ anyOf: [{ type: "integer" }, { type: "null" }] })).toBe(
      "integer | null"
    )
    expect(
      typeOf({
        type: "array",
        items: { $ref: "#/components/schemas/Candidate" },
      })
    ).toBe("array of Candidate")
  })

  it("lists an object's fields, a $ref followed, with what's required", () => {
    expect(fieldsOf(SPEC, { $ref: "#/components/schemas/Interview" })).toEqual([
      { name: "id", type: "string (uuid)", required: true, description: "" },
      {
        name: "title",
        type: "string | null",
        required: false,
        description: "Null while generating",
      },
    ])
  })

  it("lists routes, what they return and their errors without FastAPI's 422", () => {
    const [route] = operationsOf(SPEC.paths)

    expect([route.method, route.path]).toEqual(["GET", "/interviews"])
    expect(typeOf(successSchema(route.operation)!)).toBe("array of Interview")
    expect(errorsOf(route.operation)).toEqual([
      { code: "401", description: "No key" },
    ])
    expect(schemasOf(SPEC).map(([name]) => name)).toEqual(["Interview"])
  })

  it("splits a description into titled sections, steps and inline code", () => {
    const sections = richText(
      "Intro with `code`.\n\n## Keys\n\n1. Sign in.\n2. Open **Hiring**, then\n   a tab.\n\nAfter."
    )

    expect(sections.map((section) => section.title)).toEqual([null, "Keys"])
    expect(sections[0].blocks[0].pieces).toEqual([
      { text: "Intro with ", kind: "text" },
      { text: "code", kind: "code" },
      { text: ".", kind: "text" },
    ])
    const [steps, after] = sections[1].blocks

    expect(
      steps.steps?.map((step) => step.map((piece) => piece.text).join(""))
    ).toEqual(["Sign in.", "Open Hiring, then a tab."])
    expect(after.steps).toBeNull()
  })
})
