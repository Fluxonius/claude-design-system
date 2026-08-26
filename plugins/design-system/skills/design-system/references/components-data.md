# Data Components

Extends `components-core.md`, which defines the base Table. This file covers
composites built on it and the other structures for displaying records.

---

## 40. Data Table

The base Table plus sorting, selection, bulk actions and filters. A composite,
not a new component — every measurement below inherits from Core's Table.

| Property | default | compact |
|---|---|---|
| Toolbar height | `control-h-lg` (48) | `control-h-md` (40) |
| Toolbar → table | `space-3` (12) | `space-2` (8) |
| Search field | max-width 320, left | 240 |
| Filter chips | Chip S, wrapping row below toolbar | same |
| Checkbox column | 44 wide, centred | 36 |
| Sort indicator | `icon-sm` (16), active column only | same |
| Sort hover hint | `text-subtle` chevron at 50% opacity | same |
| Row selected | `accent-subtle` fill | same |
| Row hover | `surface-hover` (table sits on the page) | same |
| Bulk action bar height | `control-h-lg` (48) | 40 |
| Bulk bar fill | `control` tint, **no border** | same |
| Bulk bar count | `text` weight 500, sub-count `text-muted` | same |
| Bulk bar actions | Button S, `plain` / `neutral` | same |
| Bulk bar position | replaces toolbar in place | same |
| Row actions | Icon Button S, `plain` / `neutral` | same |
| Sticky header | yes, `top: 0` within scroll container | same |
| Sticky first column | on horizontal scroll | same |

**Rules.**

**The bulk action bar replaces the toolbar in place; it does not appear above
it.** A bar that pushes the table down moves the rows the user just selected out
from under the pointer. Same height, same position, different content.

**It is neutral — `surface-raised` with a `border-strong` edge — never `ink`
and never accent-tinted.** Three reasons:

- An ink-filled bar is an **inverted surface**, and no button priority is
  defined against one. Placing a normal button on it and forcing the label
  colour produces text at roughly 1.2:1. If you are overriding a component's
  colour to make it work inside a container, the container is wrong.
- The bar is a **background tint** with no border. That has a consequence worth
  stating: an `outline` button's `border-strong` edge measures 2.79 on a
  `control` fill and 2.96 on `control-subtle` — both under the 3:1 boundary
  floor. So the actions inside are `plain`, a priority that depends on no edge
  at all. **Removing a container's border constrains what can go inside it**,
  and that is the general lesson, not a quirk of this component.
- The bar is a **mode indicator**, not the selection itself. The selection is
  already visible as accent-tinted rows. Tinting the bar too doubles a signal
  that is not ambiguous, and spends the accent where a border does the work.

Selection is `accent-subtle` — the system's selection language, identical to nav
and menus. Row hover stays `surface-hover` because a table sits on the page, not
on a raised overlay. Both can be active at once, so a selected-and-hovered row
uses `accent-muted` to stay distinguishable.

**Selection survives pagination, and the count says so.** "12 selected" when
only 5 are visible needs "12 selected (5 on this page)". Silently dropping
off-page selections destroys work invisibly.

Sorting is single-column with a visible indicator. Show a faint chevron on
hover over any sortable header so sortability is discoverable without clicking.

Filters are chips below the toolbar, each individually removable, with "Clear
all" once more than one is active. A filtered table always says what is filtered
— a table showing 12 of 4,000 rows with no visible reason is a support ticket.

Loading is skeleton rows at `row-h`, never a spinner over the table. Keep the
header rendered so the layout does not jump.

**Don't:**
- Push the table down with a bulk action bar
- Use `control-subtle` for row hover — the table is not a raised surface
- Drop off-page selections silently
- Sort on multiple columns without showing the precedence
- Filter with no visible indication of what was filtered
- Replace the whole table with a spinner
- Make the entire row clickable *and* put controls inside it
- Ship without an empty state distinguishing no-data from no-results

---

## 41. Tree

| Property | default | compact |
|---|---|---|
| Row height | `control-h-sm` (32) | 28 |
| Row padding-x | `space-2` (8) | `space-1` (4) |
| Indent per level | 20 (one icon column) | 16 |
| Twisty | `icon-sm` (16), rotates 0° → 90° | same |
| Twisty hit area | 24 × 24 | 24 × 24 |
| Leading icon | `icon-sm` (16) | same |
| Label | `sm` (14) | `sm` (14) |
| Row hover | `control-subtle` | same |
| Row selected | `accent-subtle` + `accent-text` | same |
| Guide lines | **none** | none |
| Max practical depth | 4 | 4 |
| Drop indicator | 2px `accent` line, full row width | same |

**Rules.** Indent by exactly one icon column per level, so labels align with
their parent's label rather than its icon — the same rule as the sidebar.

**The twisty and the label are separate targets.** Clicking the twisty expands
without selecting; clicking the label selects without expanding. Collapsing
these into one action means a user cannot inspect a folder's contents without
also navigating into it.

No guide lines. Indentation carries the hierarchy; vertical rules at every level
turn a tree into a grid and fight the borders-first restraint everywhere else.

Keyboard: Right expands or moves to first child, Left collapses or moves to
parent, Up/Down traverse *visible* rows only, type-ahead jumps within siblings.

Beyond about four levels, a tree becomes unusable — switch to a breadcrumb-plus-
list navigation model.

**Don't:**
- Draw guide lines between levels
- Make the twisty and the label the same target
- Indent by an arbitrary amount instead of one icon column
- Let keyboard traversal walk into collapsed rows
- Auto-expand every node on load
- Nest beyond four levels
- Animate expansion by `height`

---

## 42. Description List

Label/value pairs — the detail panel of a record.

| Property | default | compact |
|---|---|---|
| Layout | two-column, label left | stacked below 480 |
| Label column width | 160, fixed | 128 |
| Label | `sm` (14) `text-muted` | `sm` (14) |
| Value | `sm` (14) `text` | `sm` (14) |
| Row gap | `space-3` (12) | `space-2` (8) |
| Column gap | `space-4` (16) | `space-3` (12) |
| Row divider | **none** | none |
| Empty value | em dash `text-subtle`, never blank | same |
| Numeric / ID value | `font-mono`, tabular | same |
| Long value | wraps, never truncates | same |
| Copyable value | Icon Button S, `plain`, on row hover | same |
| Group heading | `sm` (14) weight 600, `space-4` above | same |

**Rules.** The label column is a **fixed** width, not content-derived. Labels of
varying length make values start at ragged positions, and the eye cannot scan a
column that does not exist.

**Never render an empty value as blank space.** An em dash says "we know, and
there is nothing"; blank says "this interface is broken". These are different
messages.

No dividers between rows. Row gap separates; a rule per pair turns a summary
into a table and makes twelve fields look like a spreadsheet.

IDs, timestamps, amounts and hashes use `font-mono` so they can be compared and
copied accurately. Values wrap rather than truncate — a truncated identifier is
useless, and this is a detail view whose purpose is showing the detail.

**Don't:**
- Size the label column to content
- Leave empty values blank
- Put a divider between every pair
- Truncate an ID or hash
- Use a description list for editable fields — that is a form
- Mix two-column and stacked layouts in one panel

---

## 43. Timeline / Activity Feed

| Property | default | compact |
|---|---|---|
| Node | 8 dot, `border-strong`, `radius-full` | same |
| Node (current / latest) | 8 dot, `ink` fill | same |
| Node column width | 24 | 20 |
| Connector | 1px `border`, runs through node column | same |
| Row padding-y | `space-3` (12) | `space-2` (8) |
| Actor avatar | xs (20) | xs (20) |
| Primary text | `sm` (14) `text` | same |
| Actor name | weight 500 | same |
| Timestamp | `2xs` (12) `text-subtle` | same |
| Timestamp position | inline, after text | same |
| Detail block | `control` fill, `radius-sm`, `space-2` padding | same |
| Day separator | label `2xs` weight 500 `text-subtle`, sticky | same |
| Group gap | `space-4` (16) | `space-3` (12) |

**Rules.** The connector runs continuously through the node column and stops at
the last node — a line trailing past the final entry implies more content that
is not there.

**Timestamps are relative near, absolute far.** Under a day, "3h ago"; beyond
that, an absolute date. Always carry the exact timestamp in a `title` attribute
or tooltip, because relative time is unusable for reconciliation.

One line per event. When an event has a payload (a comment, a diff, a changed
value), it goes in a `control`-filled detail block beneath, not inline.

Group by day with sticky day separators. A feed with no day boundaries becomes
unreadable past about twenty entries.

Newest first for activity feeds; oldest first for process timelines where order
is causal. Pick one per surface and never mix within a view.

**Don't:**
- Run the connector past the final node
- Show only relative timestamps with no absolute value available
- Inline a multi-line payload into the event sentence
- Omit day separators on a long feed
- Mix newest-first and oldest-first in one view
- Use an avatar larger than xs — the text is the content
- Animate new entries in with motion beyond opacity
