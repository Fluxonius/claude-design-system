# Form Components

Extends `components-core.md`. The universal state set, the disabled treatment,
the focus law and the measurement-table conventions are defined there and apply
unchanged here.

Everything below inherits the field treatment from Core's Input: `control` fill,
**no border at rest**, hover to `control-hover`, focus adds the global ring,
invalid adds a `danger-border`.

---

## 14. Combobox / Autocomplete

An input that filters a list. Not a Select — a Select shows every option, a
combobox narrows a set too large to scan.

| Property | default | compact |
|---|---|---|
| Trigger | identical to Input | identical |
| Menu offset | 4 | 4 |
| Menu max-height | 320 | 288 |
| Option height | `control-h-sm` (32) | 28 |
| Option padding-x | `control-px-sm` (12) | 8 |
| Match highlight | weight 600, same colour | same |
| Empty result row | 40 tall, `text-muted`, centred | 36 |
| Loading row | skeleton at option height | same |
| Debounce | 150ms | 150ms |
| Min chars before query | 1 (local) / 2 (remote) | same |
| Selected token (multi) | Chip at S | Chip at S |

**Rules.** The typed string filters; it never reorders results between
keystrokes, because a list that reshuffles under the cursor cannot be clicked.
Highlight matched substrings with **weight**, never with a background colour —
highlight backgrounds collide with the `accent-subtle` selected state.

First matching option is highlighted but **not** selected: Enter commits the
highlight, Escape reverts to the last committed value, Tab commits and moves on.
Free text is allowed only when the field explicitly accepts it, and then the
menu shows a "Use *x*" row as the last item.

Multi-select renders chosen values as chips inside the field, wrapping the field
to multiple lines rather than scrolling horizontally.

**Don't:**
- Reorder results while the user is typing
- Auto-select the first result so Enter commits something unseen
- Highlight matches with a background tint
- Query on every keystroke with no debounce
- Leave no empty state — "No matches for *x*" is required
- Silently drop the typed value on blur; commit or revert, visibly
- Use a combobox for under ~10 options — that is a Select
- Grow the field horizontally as chips are added

---

## 15. Date Picker

| Property | default | compact |
|---|---|---|
| Field | identical to Input | identical |
| Calendar popover | `surface-raised`, `border`, `radius-md`, `shadow-sm` | same |
| Popover padding | `space-3` (12) | `space-2` (8) |
| Day cell | 36 × 36 | 32 × 32 |
| Day cell radius | `radius-sm` | `radius-sm` |
| Weekday header | `2xs` (12) weight 500 `text-muted` | same |
| Month label | `sm` (14) weight 600 | same |
| Nav buttons | Icon Button S, `plain` / `neutral` | same |
| Today marker | 4px `accent` dot below the numeral | same |
| Selected day | `ink` fill, `on-ink` numeral | same |
| Range endpoints | `ink` fill | same |
| Range interior | `accent-subtle` fill, square corners | same |
| Range endpoints | `accent-subtle`, rounded on the OUTER corners only | same |
| Grid gap | 0 (cells tile) | 0 |

**Rules.** The text field is always editable — a calendar-only date picker is
unusable for anyone entering a birth date. Accept a permissive set of typed
formats and normalise on blur, showing the normalised value.

**Selected is `ink`, today is an `accent` dot.** These are different kinds of
information: selection is a commitment, "today" is a landmark. Using the accent
for both makes the calendar unreadable at a glance.

Range interiors are square-cornered so a run of days reads as one continuous
bar; the two endpoints take `radius-sm` on their **outer** corners only. Both
halves matter — interiors alone leave the tint stopping with square corners,
which reads as a rendering fault rather than a range.

**Rule order in the day cell is load-bearing.** `[aria-selected="true"]` and
`[data-range-start]` have identical specificity, so whichever comes last wins on
`background`. With the range rules last, a selected endpoint kept `on-ink` text
while taking the `accent-subtle` fill — white on a pale tint, **1.10:1**. So:
range tints first (they describe *unselected* days within a range), then
selection, which must set fill **and** text, then radius-only overrides for the
endpoints. A rule that sets a background without also setting its foreground is
the shape of this bug.

Keyboard: arrows move by day, PageUp/PageDown by month, Home/End to week bounds,
Escape closes and reverts.

**Don't:**
- Make the field read-only so the calendar is the only input path
- Use the accent for both selection and today
- Round every cell in a range so it reads as separate chips
- Ship without a visible "clear" affordance on an optional date
- Open the calendar on focus — it blocks typing; open on click of the icon
- Use a native `<input type="date">` and style only the wrapper
- Show six week-rows for some months and five for others; the popover height
  must be fixed or it jumps between months

---

## 16. Slider

| Property | default | compact |
|---|---|---|
| Track height | 4 | 4 |
| Track radius | `radius-full` | `radius-full` |
| Track (empty) | `control` | `control` |
| Track (filled) | `ink` | `ink` |
| Thumb | 20 × 20 | 16 × 16 |
| Thumb fill | `surface`, `border-strong` edge | same |
| Thumb radius | `radius-full` | `radius-full` |
| Hit area | 44 tall, transparent | 44 |
| Step marks | 2 × 2 dots, `text-subtle` | same |
| Value label | `sm` (14) `font-mono`, tabular | same |
| Label position | right of track, fixed width | same |

**Rules.** The filled portion is `ink`, matching every other committed state.
The thumb keeps a `border-strong` edge because a `surface`-filled circle on a
`control` track would otherwise vanish — this is one of the few places a control
border survives.

Always pair with a numeric readout, and make that readout an input where the
value is precise (price, dimensions). A slider alone cannot express "exactly
250". Use `font-mono` with tabular figures so the number does not jitter as it
changes.

Step marks appear only when steps are countable — roughly ten or fewer.

Keyboard: arrows by one step, PageUp/PageDown by ten, Home/End to bounds.

**Don't:**
- Ship a slider with no numeric readout
- Use a proportional font for the value; digits will jitter
- Limit the hit area to the 4px track
- Animate the thumb on drag — it must track the pointer exactly
- Use a slider for a value the user knows precisely; use a number input
- Put the value label above the thumb where it follows the drag and obscures the track
- Use `accent` for the filled track — filled means committed, so it is `ink`

---

## 17. Number Input

| Property | default | compact |
|---|---|---|
| Field | identical to Input | identical |
| Text alignment | **right**, tabular figures | right |
| Font | `base` (16) `font-mono` | `sm` (14) `font-mono` |
| Stepper buttons | Icon Button S, `plain`, stacked right | same |
| Stepper column width | 24 | 20 |
| Unit suffix | `text-muted`, inside field, right of value | same |

**Rules.** Numeric values are right-aligned with tabular figures so digits line
up in a column of fields — the same rule as numeric table columns. Steppers are
optional and only worth adding when the range is small and increments are
meaningful; for an arbitrary integer they are decoration.

`inputmode="decimal"` and `type="text"` beats `type="number"`: the native number
input silently discards invalid characters, scrolls the value on wheel events
over the field, and varies in appearance across browsers.

Clamp on blur, not on keystroke — clamping mid-typing prevents entering "10"
when the minimum is 5 and the user has typed "1".

**Don't:**
- Left-align numeric values
- Use proportional figures
- Use `type="number"` and inherit wheel-scroll value changes
- Clamp while the user is still typing
- Put the unit in a placeholder where it vanishes on input
- Add steppers to a field with an unbounded range

---

## 18. File Upload

| Property | default | compact |
|---|---|---|
| Drop zone min-height | 120 | 96 |
| Drop zone fill | `control` | `control` |
| Drop zone border | 1px **dashed** `border-strong` | same |
| Drop zone radius | `radius-md` | `radius-md` |
| Drag-over fill | `accent-subtle` | same |
| Drag-over border | dashed `accent-border` | same |
| Icon | `icon-lg` (24), `text-subtle` | same |
| Primary text | `sm` (14) weight 500 | same |
| Hint text | `2xs` (12) `text-muted` | same |
| File row height | `control-h-md` (40) | 32 |
| File row fill | `surface`, `border-subtle` divider | same |
| Row thumbnail | 32 × 32, `radius-sm` | 28 × 28 |
| Progress bar | 4 tall, inside row, full-bleed bottom | same |
| Remove control | Icon Button S, `plain` / `neutral` | same |

**Rules.** The dashed border is the one sanctioned dashed line in the system —
it signals "not yet filled" and appears nowhere else. Never use dashed borders
decoratively.

A drop zone must also be a button: keyboard and screen-reader users cannot drag.
Clicking anywhere in the zone opens the file dialogue.

State accepted formats and the size limit *before* upload, in the hint text.
Rejecting a file after the user waited for it to transfer is the worst possible
time to mention a 10MB cap. Validate type and size client-side first.

Per-file progress lives in the file row, never as a single aggregate bar. Failed
files stay in the list with a `danger-text` reason and a retry affordance —
never disappear.

**Don't:**
- Use a dashed border anywhere else in the system
- Make the drop zone drag-only with no click or keyboard path
- Hide format and size limits until after a failed upload
- Replace the file list with one aggregate progress bar
- Remove failed files from the list silently
- Use a toast for an upload error — it belongs on the file row
- Block the whole form while a background upload runs

---

## 32. Search Field

| Property | default | compact |
|---|---|---|
| Field | identical to Input | identical |
| Leading icon | `icon-sm` (16), `text-subtle`, inset 12 | inset 8 |
| Text inset (left) | 36 | 30 |
| Clear control | Icon Button S, `plain`, appears when non-empty | same |
| Radius | `radius-md` (page) / `radius-full` (toolbar) | same |
| Debounce (live) | 250ms | 250ms |
| Result count | `sm` (14) `text-muted`, below field | same |

**Rules.** Two behaviours, and mixing them is the usual failure: **live search**
filters as you type and needs no submit button; **submitted search** waits for
Enter and must show a submit affordance. A field that looks live but requires
Enter reads as broken.

The clear control appears only when the field has content, and clearing returns
to the unfiltered state immediately — it never just blanks the text and leaves
results filtered.

Always show what was searched and how many results came back. "No results for
*ledger*" beats an empty list, because it confirms the query was received.

Placeholder states the scope ("Search invoices"), not the verb.

**Don't:**
- Debounce live search below ~200ms or above ~400ms
- Show a clear control on an empty field
- Clear the text without clearing the filter
- Return an empty list with no "no results" message
- Use "Search…" as the placeholder when the scope is non-obvious
- Put a magnifying-glass submit button on a live-search field

---

## 33. Tag Input

An input that turns committed text into removable chips.

| Property | default | compact |
|---|---|---|
| Field | Input, height **auto** (min `control-h-md`) | same |
| Field padding | `space-1` (4) | 4 |
| Chip | Chip at S, removable | same |
| Chip gap | `space-1` (4) | 4 |
| Text cursor min-width | 80 | 64 |
| Line wrapping | wraps, field grows | same |
| Max height before scroll | 120 | 96 |
| Commit keys | Enter, comma, Tab | same |
| Duplicate feedback | shake existing chip, no new chip | same |

**Rules.** The field grows vertically as chips wrap. It never scrolls
horizontally — a horizontally scrolling tag field hides its own contents.

Commit on Enter, comma or Tab; Backspace on an empty cursor selects the last
chip, and a second Backspace removes it. Never remove on the first Backspace,
which destroys a tag the user cannot see themselves about to delete.

Pasting a comma- or newline-separated string creates multiple chips at once.

Duplicates are not added silently — briefly highlight the existing chip so the
user understands why nothing appeared.

**Don't:**
- Scroll the field horizontally instead of wrapping
- Delete a chip on the first Backspace with no selected state
- Accept duplicates silently, or reject them with no feedback
- Lose uncommitted text on blur — commit it or keep it visible
- Split a paste into one chip containing commas
- Use a tag input where a multi-select combobox belongs (a fixed option set)

---

## 34. Command Palette

| Property | default | compact |
|---|---|---|
| Width | 640 | 560 |
| Top offset from viewport | 15vh | 10vh |
| Fill | `surface-raised` | same |
| Border | `border-width` `border` | same |
| Radius | `radius-lg` | `radius-lg` |
| Shadow | `shadow-md` | `shadow-md` |
| Search row height | 56 | 48 |
| Search font | `base` (16) | `sm` (14) |
| Search row divider | `border-width` `border-subtle`, full-bleed | same |
| Result row height | `control-h-md` (40) | 32 |
| Result padding-x | `space-4` (16) | 12 |
| Result hover / active | `control-subtle` | same |
| Leading icon | `icon-sm` (16), column 24 reserved | same |
| Shortcut hint | `font-mono` `2xs` `text-subtle`, right | same |
| Group label | `2xs` weight 500 `text-subtle`, 8×16 padding | same |
| Max height | 400 | 360 |
| Backdrop | `overlay`, no blur | same |

**Rules.** The palette is a raised overlay, so rows hover with `control-subtle`,
never `surface-hover`.

**Keyboard highlight and pointer hover are the same visual state, and only one
is active at a time.** Moving the arrow keys clears pointer hover; moving the
pointer clears the keyboard highlight. Two highlighted rows at once is the
defining failure of this component.

The first result is highlighted on open so Enter always does something
predictable. Results group by category with sticky group labels. Show shortcut
hints for any action that has one — the palette is where users learn them.

Escape closes and returns focus to where it was. The palette never traps the
user in a nested view without a visible way back.

**Don't:**
- Highlight a keyboard row and a hovered row simultaneously
- Use `surface-hover` for row hover (invisible on a raised surface in dark mode)
- Open with nothing highlighted, so Enter does nothing
- Blur the backdrop
- Nest navigation with no back affordance
- Show more than about 8 results without grouping
- Hide keyboard shortcuts here of all places
