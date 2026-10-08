/** A grade's colour: green when the candidate passed, red when they didn't, none while it isn't
 * decided. */
export function gradeTone(passed: boolean | null | undefined) {
  if (passed === true) {
    return "text-green-600 dark:text-green-400"
  }

  if (passed === false) {
    return "text-red-600 dark:text-red-400"
  }

  return ""
}
