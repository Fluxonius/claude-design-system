# Core Components

Every component: anatomy, exact measurements, the full state set, and the
specific ways it gets built wrong. Button and Icon Button are separate
components because their accessibility rules differ.

## How to read the measurement tables

Values are given for both densities. Radius entries name a token, because the
resolved pixel value depends on the user's corner preset:

| Token | sharp | soft | round |
|---|---|---|---|
| `radius-sm` | 1 | 4 | 7 |
| `radius-md` | 2 | 8 | 14 |
| `radius-lg` | 3 | 12 | 21 |
| `radius-xl` | 4 | 16 | 28 |
| `radius-full` | 9999 | 9999 | 9999 |

**Never hard-code a pixel value from these tables into component code.** They
exist so you can verify a rendered result, not so you can bypass the token. A
literal `border-radius: 8px` silently breaks every product on `sharp` or `round`.

Shared control metrics, referenced throughout:

| Token | default | compact |
|---|---|---|
| `control-h-sm` | 32 | 28 |
| `control-h-md` | 40 | 32 |
| `control-h-lg` | 48 | 40 |
| `control-px-sm` | 12 | 8 |
| `control-px-md` | 16 | 12 |
| `control-px-lg` | 20 | 16 |
| `row-h` | 48 | 36 |
| `section-gap` | 32 | 24 |
| `icon-sm` / `icon-md` / `icon-lg` | 16 / 20 / 24 | 16 / 20 / 24 |

Icon sizes do not change with density. Shrinking icons below 16 breaks optical
alignment with 14px text and is never correct.

**Universal state set.** Every interactive component implements all seven:
`rest`, `hover`, `active`, `focus-visible`, `disabled`, `loading` (where
applicable), `error`/`invalid` (where applicable). A component missing `disabled`
or `focus-visible` is incomplete, not minimal.

**Universal disabled treatment.** `opacity: 0.5`, `cursor: not-allowed`,
pointer events retained on the wrapper so tooltips still work. Never grey out by
swapping to a lighter colour token — opacity keeps one rule for every component.

**Universal focus treatment.** The ring is defined once, globally, on
`*:focus-visible`. Never restyle it per component. Three specific failures:

- **Never set `border-radius` in a focus rule.** `outline` already follows the
  element's own corners. `border-radius: inherit` makes a focused element adopt
  its *parent's* radius and square off its own — a rounded input inside a square
  container visibly snaps to sharp corners on focus.
- **Never use `overflow: hidden` on a focusable element's ancestor** unless the
  ring is inset. `outline-offset: 2px` draws *outside* the box, so a clipping
  parent silently eats it. Tables and cards clip children by design — give
  focusable descendants `outline-offset: -2px` there instead.
- **Never remove an outline without replacing it.** `outline: none` with no
  substitute is an accessibility failure, not a design decision.

---

## 1. Button

**Two sizes. Three priorities. Three colours.** Nine combinations, and nothing
outside them.

| Property | M (default) | S |
|---|---|---|
| Height (default density) | 40 | 32 |
| Height (compact density) | 32 | 28 |
| Padding-x | `control-px-md` (16 / 12) | `control-px-sm` (12 / 8) |
| Font | `sm` (14) weight 500 | `sm` (14) weight 500 |
| Content alignment | **centred**, both axes | centred |
| Icon size | `icon-sm` (16) | `icon-sm` (16) |
| Gap icon→label | `space-2` (8) | `space-1` (4) |
| Radius | `radius-md` | `radius-md` |
| Min width | 64 | 56 |

There is no L. A button larger than M is a layout problem — a hero CTA gets more
surrounding space, not a taller box.

### Priority × colour

Priority sets the *weight*; colour sets the *meaning*. They compose freely.

| | `neutral` | `primary` | `destructive` |
|---|---|---|---|
| **filled** | `ink` bg, `on-ink` text | `accent` bg, `on-accent` text | `danger-solid` bg, `on-danger` text |
| **outline** | transparent, `border-strong` edge, `text` | transparent, `accent-border` edge, `accent-text` | transparent, `danger-border` edge, `danger-text` |
| **ghost** | `control-subtle` bg, `text` | `accent-subtle` bg, `accent-text` | `danger-subtle` bg, `danger-text` |

**Outline uses `border-strong`, not `control-border`.** An outline button is
transparent, so its edge is the only thing identifying it as a control — there
is no fill to fall back on, as there is for an input or a chip. That means it
carries the full WCAG 1.4.11 3:1 boundary requirement, and `control-border` sits
at roughly 1.3:1 in light mode. This is the one interactive edge in the system
that is audited, on every background including `accent-subtle`.

**Ghost is tinted, not transparent.** It carries the faintest fill in the system
at rest — enough to read as a target without an edge. Outline is the inverse:
an edge with no fill. The two are never combined; a shape with both a border and
a fill is `filled`.

**Hover — background only, every combination:**

| | `neutral` | `primary` | `destructive` |
|---|---|---|---|
| **filled** | `ink-hover` | `accent-hover` | `danger-text` |
| **outline** | `control-subtle` fill, edge unchanged | `accent-subtle` | `danger-subtle` |
| **ghost** | `control` | `accent-muted` | `danger-muted` |

Ghost rest and ghost hover are one step apart on the same ramp
(`control-subtle` → `control`, `accent-subtle` → `accent-muted`), so the tint
deepens rather than appearing from nothing. This is why the `-subtle` /`-muted`
pair exists on every colour family.

Note what does *not* change on hover: the border colour, the text colour, the
size, the position. Outline buttons gain a fill and keep their edge exactly.

### Which to use

- **filled / neutral** is the default primary action. Ink, not accent — the
  brand hue stays reserved for links, selection, focus and status.
- **filled / primary** is the accent-filled exception: onboarding, marketing
  surfaces, a single conversion moment. Inside product UI it should be rare, and
  never on the same screen as a filled/neutral button — two filled buttons of
  different colours read as two competing primaries.
- **filled / destructive** is confirmation inside a destructive dialog, not the
  trigger that opens it.
- **outline** is the secondary action beside a filled one.
- **ghost** is for toolbars, table row actions, and anything repeated many times
  where a border per instance would be visual noise. Ghost carries a rest tint,
  so for *repeated* icon-only controls (table rows, toolbars) reach for Icon
  Button's `plain` priority instead — same restraint, no accumulated tint.

### Icons in buttons

A button may carry a leading icon, a trailing icon, or neither — never both.
Leading icons label the action (a plus on "New invoice"). Trailing icons
indicate what happens next (a chevron on "Continue", an external-link glyph).
Icons are `icon-sm` at both sizes and inherit `currentColor`, always.

**Rules.** One filled button per view. Loading replaces the leading icon with a
spinner and holds the label and width fixed. Destructive actions are never the
only affordance.

**Don't:**
- Use the accent for a routine primary action — that is `ink`'s job
- Put a filled/neutral and a filled/primary button on the same screen
- Give a ghost button a border, or an outline button a fill at rest
- Left-align button content — labels and icons centre on both axes, always
- Change border or text colour on hover — background shifts only
- Add a shadow, gradient, or hover-lift transform
- Invent a third size, or set a height off the M/S scale
- Put both a leading and a trailing icon on one button
- Use an icon-only button here — that is Icon Button, a separate component
- Wrap button text to two lines

---

## 1b. Icon Button

A button whose entire content is one icon. Square, and a distinct component
because its accessibility and hit-area rules differ from a labelled button.

| Property | M (default) | S |
|---|---|---|
| Size (default density) | 40 × 40 | 32 × 32 |
| Priorities | filled / outline / ghost / **plain** | same |
| Size (compact density) | 32 × 32 | 28 × 28 |
| Icon | `icon-md` (20) | `icon-sm` (16) |
| Radius | `radius-md` | `radius-md` |
| Touch hit area | ≥ 44 × 44 incl. margin | ≥ 44 × 44 |

**Four priorities here, not three.** Icon Button adds `plain` — no background at
all — giving twelve combinations. Everything else matches Button: same colours,
same tokens, same background-only hover.

| | `neutral` | `primary` | `destructive` |
|---|---|---|---|
| **filled** | `ink` | `accent` | `danger-solid` |
| **outline** | `control-border` edge | `accent-border` edge | `danger-border` edge |
| **ghost** | `control-subtle` tint | `accent-subtle` tint | `danger-subtle` tint |
| **plain** | **transparent** | transparent | transparent |

Plain hover borrows the ghost rest tint (`control-subtle` / `accent-subtle` /
`danger-subtle`), so a bare icon still gives feedback without carrying weight at
rest.

**Ghost vs plain.** Ghost reads as a target before you touch it; plain reads as
part of the content until you approach it. Use ghost for a small number of
deliberate controls, and plain wherever icon buttons repeat — table row actions,
toolbars, list item menus — where a tint on every instance stacks into visual
noise. This supersedes the earlier advice to reveal ghost row-actions on hover:
use `plain` instead, which is the same idea expressed as a token rather than an
interaction hack.

Other differences from Button: the square footprint, the larger icon at M, and
the requirements below.

**Rules.**
- **An accessible name is mandatory.** `aria-label` or visually-hidden text.
  An icon-only control with no name is unusable on a screen reader — this is the
  single most common failure of this component.
- **A tooltip is mandatory** on pointer devices. The icon is never
  self-explanatory to everyone, and the tooltip is what makes it learnable.
- On touch, the tooltip is unreachable, so an icon button that carries meaning
  users cannot guess needs a visible label instead — use a Button.
- `ghost` is the default for standalone icon buttons. Filled icon buttons are
  reserved for a single prominent action, typically a floating compose or add
  control.
- In table rows and toolbars, use `plain` / `neutral` at S.
- `plain` is for **compact controls in a group**: icon buttons in a toolbar or
  table row, page numbers in a pager. It requires `iconbtn` or `btn--square`.
  It is not for a standalone labelled action — a bare word with no fill, no edge
  and no group around it does not read as a control; that is a link, and links
  have their own rules.

**Don't:**
- Ship one without an `aria-label`
- Ship one without a tooltip on desktop
- Use one for a destructive action with no confirmation step
- Shrink the icon below 16 to fit a smaller box — reduce padding instead
- Use a 32px box as the only hit area on touch
- Use `ghost` for repeated row actions — that is what `plain` is for
- Use `plain` for a standalone primary action; it is too quiet to find
- Line up more than about five in a row without grouping or separators
- Use an ambiguous glyph where a two-word label would be unmistakable

---

## 2. Input & Textarea

**Anatomy.** `label` → `space-1` (4) → `field` → `space-1` (4) → `helper or error`.

| Property | default | compact |
|---|---|---|
| Fill | `control` (recessed) | `control` |
| Field height | `control-h-md` (40) | `control-h-md` (32) |
| Padding-x | `control-px-sm` (12) | `control-px-sm` (8) |
| Radius | `radius-md` | `radius-md` |
| Border | **none at rest** | none |
| Field font | `base` (16) | `sm` (14) |
| Label | `sm` (14) weight 500 `text` | `sm` (14) weight 500 |
| Helper / error | `2xs` (12) | `2xs` (12) |
| Reserved helper line | 16 (always) | 16 (always) |
| Textarea min-height | 80 | 72 |
| Textarea padding | `space-3` (12) | `space-2` (8) |
| Leading/trailing icon | `icon-sm` (16), inset 12 | 16, inset 8 |
| Text inset w/ icon | 36 | 30 |

Field font stays ≥16 on mobile regardless of density — iOS zooms the viewport on
focus for anything smaller.

**States.** Hover `border` darkens one step. Focus `border` becomes
`accent-border` plus the global ring. Invalid `danger-border` + `danger-text`
message + icon. Read-only drops to `surface` fill and stays selectable — it is not disabled.

**Rules.** The field is **borderless and recessed**: a `control` fill and no
edge at rest. Hover moves it to `control-hover`; focus adds the global ring.
Invalid is the one exception — a `danger-border` edge appears, because an error
must be locatable at a glance without reading.

**Accessibility note, stated plainly.** WCAG 1.4.11 asks the boundary of a
control to clear 3:1 against what is behind it. A `control` fill sits at roughly
1.2:1 on a card — a fill heavy enough to pass would be mid-grey and would not
read as an input at all. This system therefore treats the borderless field as a
**deliberate, documented deviation**, and leans on the label, the fill, the
hover shift and the focus ring to carry identification. `build_tokens.py`
prints these ratios under ADVISORY on every run so the deviation stays visible
rather than forgotten. If a project needs a hard pass — public sector,
regulated, or a formal VPAT — give inputs a `border-strong` edge and the same
audit turns green.

**Distinguishing a field from a button.** Both are filled neutral shapes now, so
the separation is behavioural and typographic, not chromatic: fields are
full-width in their container, left-aligned, carry a label above, and use `base`
text; buttons are content-width, centre-aligned, unlabelled, and use `sm`
weight 500. Never place a bare field and a neutral button side by side at equal
width.

**Optional, not required.** Mark the *optional* fields with a `text-subtle`
"Optional" suffix on the label. Never use a red asterisk: in most product forms
the majority of fields are required, so asterisking them adds noise to every row
to inform about the exception.

Placeholder is `text-subtle` and never substitutes for a label. Error text
replaces helper text, never stacks with it.

**Don't:**
- Use a floating label that leaves no visible label at rest
- Give a field a border at rest (invalid state excepted)
- Fill a field with `surface` so it sits flush with the card
- Put a full-width field and a full-width neutral button adjacent at equal width
- Mark required fields with an asterisk instead of marking optional ones
- Let the helper line collapse at rest, so errors shift the whole form down
- Style focus per-input instead of relying on the global ring
- Set `font-size` below 16 on mobile
- Put the error message above the field, away from where focus lands
- Use `type="text"` for email, tel, or numeric input (kills mobile keyboards)
- Disable a submit button as the only validation feedback
- Add an inner shadow to fake depth

---

## 3. Select

**Anatomy.** Identical to Input, plus a trailing chevron.

| Property | default | compact |
|---|---|---|
| Trigger | matches Input exactly | matches Input |
| Chevron | `icon-sm` (16), `text-subtle`, inset 12 | 16, inset 8 |
| Text inset (right) | 36 | 30 |
| Menu offset from trigger | 4 | 4 |
| Menu padding | `space-1` (4) | 4 |
| Menu min-width | = trigger width | = trigger |
| Menu max-height | 320 | 288 |
| Option height | `control-h-sm` (32) | 28 |
| Option padding-x | `control-px-sm` (12) | 8 |
| Option radius | `radius-sm` | `radius-sm` |
| Option hover | `control-subtle` (menu is a raised surface) | same |
| Check icon column | 20 reserved | 20 |

**Rules.** Full keyboard support: arrows, Home/End, Enter, Escape, type-ahead.
Trigger shows the selected value in `text`, placeholder in `text-subtle`.
Menus above ~10 items get a search field. Selected state is `accent-subtle` bg +
`accent-text` + a check icon — never colour alone.

**Don't:**
- Style a native `<select>` trigger and leave the OS dropdown unstyled
- Signal selection with background colour only
- Let the menu be narrower than its trigger
- Reserve the check column on some items but not others (labels jog sideways)
- Open on hover
- Use a select for two options — that is a radio pair or a switch
- Let the menu render outside the viewport instead of flipping

---

## 4. Checkbox, Radio, Switch

| Property | default | compact |
|---|---|---|
| Checkbox / radio box | 20×20 | 16×16 |
| Box radius | `radius-sm` (checkbox) / `radius-full` (radio) | same |
| Box border | `border-width` solid `border-strong` | same |
| Checked fill | `ink` + `on-ink` glyph | same |
| Switch track on | `ink` | same |
| Check glyph | 12 (centred mask, not rotated borders) | 10 |
| Radio centre dot | 8 (40% of box) | 6 |
| Switch track | 36×20 | 32×18 |
| Switch thumb | 16, inset 2 | 14, inset 2 |
| Label font | `sm` (14) | `sm` (14) |
| Gap box→label | `space-2` (8) | 8 |
| Row hit area | full label row, ≥ 32 tall | ≥ 28 |
| Group spacing | `space-3` (12) | `space-2` (8) |

**Checked fill is `ink`,** matching the primary button — not the accent. A
checked box and a primary button are both "the committed state", and reading as
one family is what makes the accent's appearance meaningful elsewhere. The
selected *row* behind a checkbox is still `accent-subtle`; the control itself is
ink.

**The mark is a mask, and the box is baseline-independent.** Two bugs live here
if it is built the obvious way:

- A tick made from two rotated borders needs
  `transform: rotate() translate()`, and transform functions compose
  left-to-right — so the translate runs in the *rotated* frame and nudges the
  glyph diagonally. The tick sits visibly off-centre, and a hand-tuned offset
  only corrects it at one size and one stroke weight. Use a mask whose path is
  centred by construction.
- An `inline-grid` box changes baseline the moment a child appears, so the whole
  control drops a pixel or two when checked — obvious in a table cell.
  `position: relative` with an absolutely positioned glyph and
  `vertical-align: middle` removes the dependency: the mark is out of layout,
  so it cannot move the box.

**Rules.** Checkbox = multi-select or single opt-in. Radio = one of several,
minimum two, always with a default. Switch = an immediate state change with no
save step. **A switch inside a form with a Save button is wrong — that is a
checkbox.** The thumb slides via `transform`, never `left`/`margin`.

**Don't:**
- Use a switch for anything that requires submitting a form
- Build a radio group with one option
- Limit the hit area to the box instead of the whole label row
- Use a check glyph inside a radio
- Build the tick from rotated borders — the translate lands in the rotated frame
- Let the box shift between checked and unchecked (keep the glyph out of layout)
- Animate the track colour and thumb position on different durations
- Put the label to the left of a checkbox (right side only; switches may differ)
- Nest a checkbox tree deeper than two levels without indeterminate state

---

## 5. Card

| Property | default | compact |
|---|---|---|
| Padding | `space-4` (16) or `space-6` (24) | `space-4` (16) |
| Radius | `radius-md` | `radius-md` |
| Border | `border-width` solid `border` | same |
| Shadow | **none** | **none** |
| Fill | `surface` (near-white) on tinted `bg` page | same |
| Header separation | whitespace only, no rule | same |
| Divider inset | by container padding | same |
| Title | `lg` (20) weight 600 | `base` (16) weight 600 |
| Title → subtitle | `space-1` (4) | 4 |
| Subtitle | `sm` (14) `text-muted` | 14 |
| Header → body | `space-4` (16) | 12 |
| Body → footer | `space-4` (16) | 12 |
| Grid gutter | `space-4` (16) | 12 |
| Nested element radius | `radius-md − padding`, min `radius-sm` | same |

Worked corner law example, `soft` preset: card `radius-md` = 8, padding 16,
inset button → 8 − 16 is negative, so the button clamps to `radius-sm` (4).
Flush-mounted media at padding 0 keeps the full 8 on the top corners.

**Rules.** Interactive cards get `surface-hover` and a focus ring; they do not
lift or scale. A card sits on the page, so `surface-hover` is correct here —
content inside a raised overlay uses `control-subtle` instead (see Foundations,
"Which hover fill depends on what is behind the element"). Cards in a grid have equal height with the footer pinned bottom.

**Don't:**
- Add a shadow — this is the single most reliable AI tell
- Combine border + shadow + hover-lift + scale
- Build three identical feature cards with centred coloured icons in tinted circles
- Nest a larger radius inside a smaller one
- Let grid cards size to their content so footers land at different heights
- Make the whole card clickable *and* put buttons inside it
- Use a card as a page section wrapper — that is just spacing

---

## 6. Modal / Dialog

| Property | default | compact |
|---|---|---|
| Max-width confirm / form / complex | 480 / 640 / 800 | same |
| Padding | `space-6` (24) | `space-4` (16) |
| Radius | `radius-lg` | `radius-lg` |
| Shadow | `shadow-md` | `shadow-md` |
| Title | `lg` (20) weight 600 | `base` (16) weight 600 |
| Close button | ghost icon-only, 32×32, inset 12 | 28×28, inset 8 |
| Header → body | `space-4` (16) | 12 |
| Body → footer | `space-6` (24) | 16 |
| Footer action gap | `space-2` (8) | 8 |
| Backdrop | `overlay`, no blur | no blur |
| Vertical position | centred | centred |
| Viewport margin | 16 min on all sides | 16 |
| Enter | opacity 0→1, `scale(0.98)→1`, `duration-base` | same |

**Rules.** Focus traps inside and returns to the trigger on close. Escape
closes; backdrop click closes unless data would be lost. Body scroll locks.
Header and footer stay fixed when the body scrolls. Cancel (`secondary`) sits
left of confirm (`primary`/`danger`).

**Don't:**
- Nest a modal inside a modal — use a stepped flow
- Blur the backdrop
- Use a spring or bounce entrance
- Skip the focus trap or the scroll lock
- Return focus to `<body>` instead of the trigger
- Let a full-height modal have no internal scroll region
- Put the primary action on the left

---

## 7. Table

| Property | default | compact |
|---|---|---|
| Container | **flush, borderless** — rules only, no radius, no clip | same |
| Header height | `control-h-sm` (32) | 28 |
| Header font | `2xs` (12) weight 500 `text-muted` | same |
| Header fill | transparent (flush table) | transparent |
| Row height | `row-h` (48) | 36 |
| Cell padding-x | `space-3` (12) | `space-2` (8) |
| Cell font | `sm` (14) | `sm` (14) |
| Row divider | `border-width` `border-subtle` | same |
| Header divider | `border-width` `border` | same |
| Sort icon | `icon-sm` (16), active column only | same |
| Checkbox column | 44 wide | 36 |
| Action column | right-aligned, 44 min | 36 |
| Row hover | `surface-hover` tint, always | same |
| Focus offset | `+2` (nothing clips — container is flush) | `+2` |
| Divider style | **full-bleed**, edge to edge | same |

The table is **flush and borderless** — horizontal rules do all the work, running
full-bleed edge to edge rather than inset. This is the one place dividers are
not inset by padding: a table is a grid, and an inset rule breaks the column
alignment the grid exists to communicate.

Because nothing clips, focus rings use the normal `+2` offset here. (An earlier
bordered-container design needed `-2` to avoid `overflow: hidden` eating the
ring — that constraint is gone, but the general rule still applies anywhere a
clipping ancestor exists.)

Rows tint on hover **always**, not only when clickable: a full-width row at 48px
is hard to track across without it.

**Rules — the column alignment law.** Alignment belongs to the **column**, never
to a cell. Whatever a column does, its header does too, so the class goes on the
`th` *and* on every `td` beneath it.

1. **Left is the default**, for every column.
2. **Quantities right-align**, header included. Right-aligned figures are what
   let you compare magnitude by scanning digits — which is why this pairs with
   tabular figures. The actions column right-aligns too.
3. **The row identifier is the exception.** An invoice number, an order ID, a
   year: these are *labels*, not magnitudes. Nobody sums them or compares their
   digit columns, and the first column anchors the row, so it stays **left even
   when numeric**. In practice that is the first column, or the first after a
   select-box column. It keeps tabular figures either way.

Only body cells take `font-mono`. A header is a word, not a number: putting it
in mono breaks font consistency with every other header for no benefit.
Alignment is a column property; figure rendering is a digit property, and
conflating them is the usual mistake here.

The stylesheet welds `th` and `td` together in every alignment rule, so the two
cannot be given different values — a numeric header silently staying left above
right-aligned cells was a real bug in this system, caused by `.ds-table th`
outranking `.ds-num` on specificity. What CSS cannot enforce is an author
writing the class on only one of them, so `lint_conformance.py` reports a split
column as `table-column-alignment-split`.

Sticky header on scroll. Requires an explicit empty state and a skeleton
loading state at `row-h`.

**Don't:**
- Zebra-stripe — `border-subtle` is the divider
- Centre-align a data column
- Use a spinner instead of skeleton rows
- Ship without an empty state
- Wrap the table in a bordered, radiused container
- Inset the row dividers
- Let 12 columns squeeze instead of scrolling horizontally with a pinned first column
- Right-align text, or left-align a quantity
- Right-align the row-identifier column because it happens to be numeric — an
  ID is a label; only quantities right-align
- Put an alignment class on the `td` but not the `th` (or the reverse) — the
  column splits and the linter fails the build
- Use proportional figures in numeric columns (digits jitter between rows)
- Put a numeric column's *header* in `font-mono` — align it, but leave the font alone

---

## 8. Tabs

| Property | default | compact |
|---|---|---|
| Trigger height | `control-h-md` (40) | 32 |
| Trigger padding-x | `control-px-md` (16) | 12 |
| Font | `sm` (14) weight 500 | same |
| Rest / active colour | `text-muted` / `text` | same |
| Indicator | 2 tall, `accent`, overlaps container border | same |
| Container border-bottom | `border-width` `border`, full width | same |
| Content top padding | `space-4` (16) | 12 |
| Indicator transition | `transform`, `duration-fast` (120ms) | same |

**Two treatments, and the choice is semantic, not decorative:**

- **Underline** — for *views*: distinct pages of content that replace each other
  (Overview / Members / Billing). Full-width `border` beneath, 2px `accent`
  indicator on the active trigger.
- **Segmented** — for *filters*: mutually exclusive lenses on the same content
  (All / Active / Archived). Triggers sit in a `control` track, padding
  `space-1`, `radius-md`; the active trigger gets a `surface` fill and
  `radius-sm` per the corner law. No indicator bar.

Segmented controls are always `control-h-sm`, sit inline with other controls,
and never span the full width. If you cannot say whether something is a view or
a filter, it is a view.

**Rules.** Two to seven tabs; beyond that use a select or side nav. Arrow keys
move focus; only the active tab is in the tab sequence. Labels are nouns.

**Don't:**
- Use pill tabs with a filled accent background and a shadow
- Use segmented controls for navigation between views
- Use an underline bar inside a segmented track
- Nest tab bars
- Animate the indicator with `left`/`width` instead of `transform`
- Let tab labels be sentences or wrap
- Put a single tab in a tab bar
- Change content height on tab switch so the page jumps

---

## 9. Badge / Tag

| Property | default | compact |
|---|---|---|
| Height | 20 | 18 |
| Padding-x | `space-2` (8) | `space-1-5` (6) |
| Radius | `radius-full` **always** | `radius-full` |
| Border | **none** | none |
| Font | `2xs` (12) weight 500 | same |
| Leading dot | 6 | 6 |
| Icon | `icon-sm` (16) | 16 |
| Gap | `space-1` (4) | 4 |
| Remove affordance hit area | 24 | 24 |

**Variants.** Fill only, **no border**. `neutral` is `control` + `text-muted`;
each status is `{name}-subtle` fill + `{name}-text`. Solid variants are reserved
for navigation counts. A badge is a label, not a control, so it gets no edge —
the fill carries it.

**Rules.** `radius-full` at every corner preset — badges are the documented
exception to the corner law, because a pill is a different shape category, not a
rounder rectangle.

**Don't:**
- Use a coloured badge with no text label
- Make a badge clickable — that is a button or a filter chip
- Apply `radius-md` at the `sharp` preset (badges stay pills)
- Use more than three badge colours in one table
- Put a badge inside a button

---

## 10. Tooltip

| Property | default | compact |
|---|---|---|
| Background | `tooltip-bg` | same |
| Text | `tooltip-text`, `2xs` (12) | same |
| Padding | `space-1` (4) × `space-2` (8) | same |
| Radius | `radius-sm` | `radius-sm` |
| Max-width | 280 | 280 |
| Offset from trigger | `space-2` (8) | 8 |
| Open delay | 400ms | 400ms |
| Close delay | 0ms | 0ms |
| Shadow | `shadow-sm` | `shadow-sm` |

**Use `tooltip-text`, never `text-inverse`.** The tooltip is an inverted chip,
and its foreground is computed from its own background rather than borrowed from
the page. In dark mode `text-inverse` resolves to near-black *because the page is
dark* — but the tooltip is light, so the label lands near-black on near-black and
disappears. `tooltip-text` is derived from `tooltip-bg` and audited at 4.5:1 in
both themes.

**Rules.** Plain text only. Never the sole source of essential information.
Every icon-only control has one. Flips to stay in the viewport. Touch devices
get visible helper text instead.

**Don't:**
- Use `text-inverse` for the label — it inverts the wrong way in dark mode
- Put links, buttons, or headings inside a tooltip
- Appear instantly (flickers as the cursor sweeps a toolbar)
- Hide essential instructions in one
- Attach one to a disabled element without a pointer-events wrapper
- Let it cover the element it describes
- Use one where inline helper text belongs

---

## 11. Toast

| Property | default | compact |
|---|---|---|
| Min / max width | 320 / 420 | 320 / 420 |
| Padding | `space-3` (12) × `space-4` (16) | 8 × 12 |
| Radius | `radius-md` | `radius-md` |
| Shadow | `shadow-md` | `shadow-md` |
| Status icon | `icon-sm` (16) | 16 |
| Message | `sm` (14) | 14 |
| Stack position | bottom-centre (locked) | bottom-centre |
| Stack gap | `space-2` (8) | 8 |
| Max visible | 3 | 3 |
| Viewport margin | 16 | 16 |
| Auto-dismiss | 5s success/info; never error/warning | same |
| Enter | opacity + `translateY(4px)`, `duration-base` | same |

**Rules.** Stacks **bottom-centre** — locked, not a per-product choice, so that
users of any product on this system look in the same place. Newest toast on top
of the stack, growing upward. Hovering the stack pauses dismissal. Maximum one
action; more means it should be a modal.

**Don't:**
- Use a toast for form validation — that belongs inline on the field
- Auto-dismiss an error before it can be read
- Let the stack grow unbounded
- Put two actions in one toast
- Cover the primary action area with the stack
- Animate with `height` (janks the whole stack)

---

## 12. Menu / Dropdown

| Property | default | compact |
|---|---|---|
| Surface | `surface-raised`, `border`, `radius-md`, `shadow-sm` | same |
| Padding | `space-1` (4) | 4 |
| Min / max width | 180 / 320 | 180 / 320 |
| Item height | `control-h-sm` (32) | 28 |
| Item padding-x | `control-px-sm` (12) | 8 |
| Item radius | `radius-sm` | `radius-sm` |
| Item font | `sm` (14) | 14 |
| Item hover | `control-subtle` (**not** `surface-hover`) | same |
| Item selected | `accent-subtle` + `accent-text` + check | same |
| Leading icon | `icon-sm` (16), column 20 reserved | same |
| Trailing shortcut | `font-mono` `2xs` `text-subtle` | same |
| Separator | `border-width` `border-subtle`, `space-1` margin | same |
| Section label | `2xs` weight 500 `text-muted`, 4×8 padding | same |
| Submenu open delay | 200ms | 200ms |
| Offset from trigger | 4 | 4 |

Selected / checked items use `accent-subtle` fill + `accent-text` + a leading
check — the same selection language as table rows and nav.

**Rules.** Destructive items use `danger-text` and sit last, below a separator.
Full keyboard support including type-ahead. Submenus are one level deep only.
Checkable items reserve the icon column for every item in that menu.

**Don't:**
- Place a destructive action mid-list with no separator
- Go two levels deep in submenus
- Let the menu clip at the viewport edge instead of flipping
- Open a menu on hover (submenus excepted)
- Hover menu items with `surface-hover` — it equals `surface-raised` in dark mode and produces no visible hover at all
- Reserve the icon column inconsistently within one menu
- Use a menu where a set of buttons would be clearer (under three items)

---

## Composition notes

- **Form layout.** Single column. Labels above fields. `space-4` (16) between
  fields, `space-6` (24) between groups, `space-8` (32) before the action row.
  Actions bottom-right, primary last. Multi-column only for genuinely paired
  fields (city/postcode, first/last).
- **Page structure.** Page title `2xl`, `section-gap` below. Section headings
  `lg`. Never more than three heading levels on one screen.
- **Empty states.** Required for every list, table, and search result. Icon
  (`icon-lg`, `text-subtle`) → `space-4` → heading `lg` → `space-1` → one
  sentence of `sm` `text-muted` → `space-4` → one `primary` action. The icon may
  be duotone — this is the only place duotone is permitted. No illustration, no
  spot art.
- **Navigation.** Active item is `accent-subtle` fill + `accent-text`, radius
  `radius-sm`, height `control-h-sm`. This is the same treatment as a selected
  row, because they mean the same thing. Never a left accent bar, never a filled
  accent pill, never weight-change alone.
- **Links.** `accent-text`, no underline at rest, underline on hover. In running
  prose the same rule applies — the accent colour plus the hover underline is
  enough, and permanently underlined links shred a dense UI.
- **Icons.** Outline weight everywhere, `currentColor`, never a fill variant for
  active states. Duotone is allowed in empty states only.
- **Dividers.** Inset by container padding everywhere **except tables**, where
  they run full-bleed. Menu separators inset to the menu's padding.
- **Loading.** Skeletons matching the real content's dimensions, `control`
  fill with a shimmer that respects `prefers-reduced-motion`. Spinners only
  inside buttons and for full-page transitions.
- **Touch targets.** Any control on a touch surface reaches 44×44 including
  margin, even when the visual control is 32 tall.
