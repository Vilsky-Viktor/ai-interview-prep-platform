import { test as base } from "@playwright/test";

import { addTemplate, deleteTemplate, type Template } from "./db";

/** Playwright's test with `addTemplate`: a test's own throwaway templates (helpers/db.ts),
 * deleted when it ends, so tests never read or change the platform's real ones. */
export const test = base.extend<{
  addTemplate: (language?: string, topics?: number) => Promise<Template>;
}>({
  addTemplate: async ({}, use) => {
    const made: Template[] = [];

    await use(async (language = "en", topics = 3) => {
      const template = await addTemplate(language, topics);
      made.push(template);

      return template;
    });

    for (const template of made) {
      await deleteTemplate(template.id);
    }
  },
});

export { expect } from "@playwright/test";
