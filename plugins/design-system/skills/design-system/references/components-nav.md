# Navigation Components

Extends `components-core.md`. Universal states, disabled treatment, focus law
and measurement conventions are defined there.

Selection language is shared across the whole system: an active nav item, a
selected table row and a checked menu item all use `accent-subtle` fill +
`accent-text`. If it is chosen, it is accent-tinted.

---

## 19. Sidebar

| Property | default | compact |
|---|---|---|
| Width (expanded) | 240 | 208 |
| Width (collapsed) | 56 | 56 |
| Fill | `bg` (same as page, not raised) | same |
| Right edge | `border-width` `border` | same |
| Padding | `space-2` (8) | `space-1` (4) |
| Item height | `control-h-sm` (32) | 28 |
| Item padding-x | `control-px-sm` (12) | 8 |
| Item radius | `radius-sm` | `radius-sm` |
| Item font | `sm` (14) | `sm` (14) |
| Item rest | `text-muted` | same |
| Item hover | `control-subtle` fill | same |
| Item active | `accent-subtle` fill, `accent-text`, weight 500 | same |
| Leading icon | `icon-sm` (16), column 20 reserved | same |
| Item gap | 2 | 2 |
| Section label | `2xs` (12) weight 500 `text-subtle`, uppercase | same |
| Section gap | `space-4` (16) | `space-3` (12) |
| Nesting indent | 20 (one icon column) | 20 |
| Max depth | 2 | 2 |

**Rules.** The sidebar shares the page fill and is separated by a border alone —
it is not a raised surface, and it never carries a shadow. Items sit 2px apart,
not 8: a nav list is one object, and generous gaps between items make it read as
a stack of separate buttons.

Nested items indent by exactly one icon column so labels align with their
parent's label, not its icon. Two levels is the limit; a third means the
information architecture needs a rethink, not a deeper tree.

Collapsed mode shows icons only, keeps the 56px width, and gives every item a
tooltip. Active state remains an `accent-subtle` fill on the icon's box.

**Don't:**
- Raise the sidebar onto `surface` or give it a shadow
- Space items 8px apart so they read as separate buttons
- Nest three levels deep
- Indent nested items by an arbitrary amount instead of one icon column
- Collapse to icons without tooltips
- Use a left accent bar for the active item — the fill is the system's selection language
- Put a primary filled button inside the nav list itself

---

## 20. Breadcrumb

| Property | default | compact |
|---|---|---|
| Height | `control-h-sm` (32) | 28 |
| Font | `sm` (14) | `sm` (14) |
| Link colour | `text-muted` | same |
| Link hover | `text`, underline | same |
| Current page | `text`, weight 500, **not a link** | same |
| Separator | chevron `icon-sm` (16), `text-subtle` | same |
| Gap around separator | `space-1` (4) | 4 |
| Collapse threshold | > 4 levels | > 3 |
| Collapsed indicator | Icon Button S, `plain`, ellipsis glyph | same |

**Rules.** The current page is present but not a link — it tells you where you
are, and linking it to itself is a dead control. Always show the first and last
crumb; collapse the middle behind an ellipsis menu when the trail is too long.

Breadcrumbs reflect **hierarchy, not history**. They are not a back button and
must not change based on how the user arrived.

Truncate individual long labels at roughly 24 characters with an ellipsis and a
tooltip carrying the full name, rather than letting one crumb consume the row.

**Don't:**
- Link the current page to itself
- Show navigation history instead of hierarchy
- Use "/" or "|" as a separator — the chevron is the system's glyph
- Let a long label push the trail onto a second line
- Collapse the first or last crumb
- Use breadcrumbs as the only way back; a page needs its own primary path

---

## 21. Pagination

| Property | default | compact |
|---|---|---|
| Control height | `control-h-sm` (32) | 28 |
| Page number button | square, 32 × 32 | 28 × 28 |
| Rest | Button S, `square` + `plain` / `neutral` | same |
| Current page | `ink` fill, `on-ink` numeral, weight 500 | same |
| Prev / next | Icon Button S, `plain`, chevrons | same |
| Gap | `space-1` (4) | 4 |
| Ellipsis | `text-subtle`, non-interactive, 32 wide | same |
| Window | 1 … c-1 c c+1 … n | 1 … c … n |
| Row-count select | Select S, right-aligned | same |
| Result summary | `sm` (14) `text-muted`, left-aligned | same |

A page number is a **labelled** square button (`btn--square`), not an Icon
Button — it has visible text, so it takes no `aria-label`, and `square` is a
legal home for `plain` because a pager is a group of compact controls. Prev/next
*are* Icon Buttons and do need names.

**Rules.** The current page is `ink`-filled, not accent — it is a committed
state, consistent with the primary button and checked controls. Everything else
is `plain`, so a row of numbers reads as content rather than a wall of chips.

Always show a result summary ("41–60 of 312"). A page number with no total is
navigation without a map.

First and last pages are always reachable. Prev/next are disabled at the bounds,
never hidden — controls that vanish cause layout shift and make the row jump.

Below roughly 640px, collapse to prev / "Page 3 of 16" / next.

**Don't:**
- Use the accent for the current page
- Hide prev/next at the bounds instead of disabling them
- Omit the total result count
- Render more than about seven number buttons
- Make the ellipsis look interactive
- Reset to page 1 silently when a filter changes without saying so
- Put pagination only at the top of a long table

---

## 22. Stepper

| Property | default | compact |
|---|---|---|
| Step indicator | 28 × 28, `radius-full` | 24 × 24 |
| Complete | `ink` fill, `on-ink` check | same |
| Current | `ink` fill, `on-ink` numeral | same |
| Upcoming | `control` fill, `text-muted` numeral | same |
| Connector | 2 tall, `border` | same |
| Connector (complete) | 2 tall, `ink` | same |
| Label | `sm` (14), weight 500 when current | same |
| Label colour | `text` current, `text-muted` otherwise | same |
| Gap indicator→label | `space-2` (8) | 8 |
| Step gap (horizontal) | `space-6` (24) min | `space-4` (16) |
| Vertical variant gap | `space-4` (16) | `space-3` (12) |

**Rules.** Complete and current are both `ink`; the difference is a check versus
a numeral. Upcoming steps are `control` — flat and quiet, so the eye lands on
where you are.

Three to five steps. Two is a page with a Next button; six or more should be
saved progress rather than a linear flow.

Completed steps are clickable when the user may return; upcoming steps never
are, because forward navigation must go through validation. Never let a stepper
be the only indication of unsaved progress.

Horizontal below roughly 640px collapses to "Step 2 of 4" plus the current
step's label.

**Don't:**
- Use the accent for the current step — `ink` is the committed language
- Make upcoming steps clickable
- Run more than five steps in one linear flow
- Use a stepper for a non-linear set of tasks; that is a checklist
- Hide validation errors until the final step
- Let step labels wrap to two lines
