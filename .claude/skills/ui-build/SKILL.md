---
name: ui-build
description: Build or change a page or piece of UI in prepza's design language - reuse the existing pages' layouts and shared components, keep it simple, and show it before writing its tests. Use for any new or changed screen.
---

# Build UI the prepza way

The main rule: every screen is simple, seamless, unambiguous and intuitive. Check each change
against it. CLAUDE.md rules 5 to 7 apply in full.

## Start from what exists

1. **Change only what was asked.** Don't restyle or move anything else. For an open-ended layout
   request, offer two or three mockups first.
2. **Find the closest existing page and copy it** (rule 7):
   - a list page: the companies list (a `text-3xl` title with its main action on the right, rows
     in one `LIST_BOX` list, `divide-y rounded-2xl border`);
   - a page that starts a test: the home page's start (a large title and `DescriptionBox`);
   - a detail page: a company's test page.
3. **When asked for "like X"**, find X and reproduce it exactly. Name the component you're
   copying in your reply; if two could fit, ask which.

## Reuse these, never look-alikes

| Need | Use |
|---|---|
| Page header, back arrow, page help | `PageHeader`, `BackLink` (`help=` names its guide) |
| An editable title | `EditableTitle` |
| A job description box | `DescriptionBox` |
| A long list | `VirtualList` with `usePagedList` (loads more as you scroll; failures retry) |
| A choice from a few options | `PillSelect` (the gray pill opening the site's `DropdownMenu`); never a native `<select>` |
| A searchable choice | the `LanguagePicker` pattern: a Base UI `Combobox`, the search as the menu's first row with a magnifier, the menu as wide as the picker |
| A note or a warning | `InfoCard` / `WarningCard` (`components/warning-card.tsx`) |
| A confirmation | `ConfirmDialog`; steps to follow: `InstructionsDialog` |
| An integration row | `IntegrationRow` |
| A link page that can be gone or fail | `useLinkData` + `LinkStatus` |
| The emergency pause | `PausedNotice` |
| Dates, prices, percentages | `LocalDate`, `formatDay`, `formatPrice`, `formatPercent` (`lib/format.ts`): never hand-written |
| A service's refusal | `serviceRefusal(error, [statuses])` / `apiErrorMessage(error, fallback)` in a toast |

Primitives are in `components/ui/` (button, dialog, dropdown-menu, input, switch, tooltip, ...).
No new colors, shadows, gradients or effects unless asked.

## Layout rules

- **Same width everywhere** (rule 6): a page's `<main>` is `mx-auto max-w-5xl px-6`. Cards and
  forms inside may be narrower; the page never is.
- **Titles** are lowercase, like the logo, and end with its blue dot; typed content keeps its
  case (`normal-case`).
- **Phones:** a header's button goes under the title, across the page
  (`max-sm:flex-col max-sm:items-stretch`); lists and cards reach the screen's edges
  (`-mx-6 sm:mx-0`, square corners); dialogs span the screen with their buttons side by side.
- **Right to left:** Arabic, Hebrew and Persian flip; use logical classes (`ps-`, `me-`,
  `text-start`), not `pl-`/`mr-`/`text-left`.

## Behaviour

- **No business logic in the frontend** (rule 5): limits, thresholds and what's allowed come
  from the API, and its messages are shown as they come.
- **Every text in 23 languages**: use the `translate` skill.
- **Every icon-only button** has an `aria-label` and a tooltip.

## Before tests

Show the new UI first: take desktop and phone screenshots (the `ui-check` skill), send them, and
wait for the user's confirmation. Write the tests once the design is confirmed. They check what the
screen does, not its wording (see the `verify` skill, "What a test checks").
