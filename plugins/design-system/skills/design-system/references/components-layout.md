# Layout Components

Extends `components-core.md`. Universal states, disabled treatment, focus law
and measurement conventions are defined there.

These are the components that establish a page's skeleton. They are the most
copied and the least specified in most systems, which is why product screens
drift apart even when their buttons match.

---

## 35. App Bar

The persistent top bar. One per application.

| Property | default | compact |
|---|---|---|
| Height | 56 | 48 |
| Fill | `bg` (same as page) | same |
| Bottom edge | `border-width` `border` | same |
| Shadow | **none** | none |
| Padding-x | `space-4` (16) | `space-3` (12) |
| Logo / wordmark max-height | 24 | 20 |
| Item gap | `space-2` (8) | `space-1` (4) |
| Nav item | Button S, `ghost` / `neutral` | same |
| Nav item active | `accent-subtle` + `accent-text` | same |
| Icon actions | Icon Button M, `plain` / `neutral` | Icon Button S |
| Avatar | md (32) | sm (24) |
| Search field max-width | 480, centred | full-width on tap |
| Sticky | yes, `position: sticky; top: 0` | same |

**Rules.** The app bar shares the page fill and is separated by a border alone —
identical reasoning to the sidebar. It never carries a shadow, and it never
becomes a raised surface on scroll. A border that is present at rest does not
need to animate in.

Three zones: brand left, optional search centre, actions right. Never more than
five interactive items in the right zone; past that, collapse into a menu.

Icon actions here are `plain`, not `ghost` — a row of tinted chips across the
top of every screen is exactly the accumulation `plain` exists to prevent.

The app bar holds application-level actions only. Page-level actions belong in
the Page Header, and confusing the two is why toolbars grow without limit.

**Don't:**
- Add a shadow, or grow one on scroll
- Raise it to `surface` — it is part of the page
- Use `ghost` icon buttons, which stack into a row of tinted chips
- Put page-specific actions here
- Exceed five items in the right zone
- Centre the brand
- Let the bar height differ between pages

---

## 36. Page Header

The title block at the top of a page's content region.

| Property | default | compact |
|---|---|---|
| Breadcrumb → title | `space-2` (8) | `space-1` (4) |
| Title | `2xl` (32) weight 600 | `xl` (24) weight 600 |
| Title → description | `space-2` (8) | `space-1` (4) |
| Description | `base` (16) `text-muted`, max-width 65ch | `sm` (14) |
| Header → content | `section-gap` (32) | 24 |
| Action row | right-aligned, baseline-aligned with title | same |
| Action gap | `space-2` (8) | 8 |
| Primary action | Button M, `filled` / `neutral` | Button S |
| Secondary actions | Button M, `outline` / `neutral` | Button S |
| Overflow | Icon Button M, `plain`, ellipsis | same |
| Bottom border | **none** | none |
| Tab bar (if present) | directly below, no gap | same |

**Rules.** No bottom border. The `section-gap` below the header already
separates it from content — a rule *and* 32px of space is one separator too
many, and it makes every page look like a settings screen.

Actions align to the **title's baseline**, not to the block's vertical centre.
When a description is present, centring drops the buttons into the middle of the
text and breaks the top line.

One primary action maximum. If a page seems to need two, one of them belongs in
an overflow menu or on the object it acts upon.

The description is optional, capped at 65 characters per line, and states what
the page is for — not what the user should do next.

When tabs follow, they sit directly beneath with no gap; the tab bar's own
bottom border becomes the separator.

**Don't:**
- Add a bottom border beneath the header
- Centre-align the action row against a title with a description
- Ship two primary actions
- Let the description run wider than 65ch
- Repeat the breadcrumb's last crumb as the title's prefix
- Put a gap between the header and a following tab bar

---

## 37. Divider

| Property | default | compact |
|---|---|---|
| Thickness | `border-width` (1) | same |
| Colour | `border-subtle` | same |
| Inset (in a card) | by container padding | same |
| Inset (in a table) | **none**, full-bleed | none |
| Inset (in a menu) | by menu padding | same |
| Margin (horizontal rule) | `space-4` (16) above and below | `space-3` (12) |
| With a label | label centred, `2xs` `text-subtle`, 8px gutters | same |
| Vertical divider height | matches content, min 16 | same |
| Vertical divider margin-x | `space-3` (12) | `space-2` (8) |

**Rules.** A divider is the weakest separator in the system and should be the
last one reached for. Whitespace separates by default; a heading separates
better than a line; a divider is for when two things are genuinely adjacent and
genuinely different.

`border-subtle`, never `border` — a divider that draws attention has failed at
its job. If a line needs to be *seen* rather than sensed, the content structure
is doing something a heading should do.

Never stack a divider against padding that already separates: a card footer with
`space-4` above it does not also need a rule.

Labelled dividers ("OR") are for genuine either/or branches, not decoration.

**Don't:**
- Use `border` or `border-strong` for a divider
- Put a divider between every item in a list — that is a table
- Combine a divider with a section gap that already separates
- Use a vertical divider where a gap would do
- Add dividers inside a card that already has a border
- Use a labelled divider as a section heading

---

## 38. Empty State

Required for every list, table, search result and dashboard panel.

| Property | default | compact |
|---|---|---|
| Container min-height | 240 | 180 |
| Alignment | centred, both axes | centred |
| Icon | `icon-lg` (24) in a 48 circle, `control` fill | 40 circle |
| Icon colour | `text-subtle` | same |
| Icon → heading | `space-4` (16) | `space-3` (12) |
| Heading | `lg` (20) weight 600 | `base` (16) weight 600 |
| Heading → body | `space-1` (4) | 4 |
| Body | `sm` (14) `text-muted`, max-width 40ch | same |
| Body → action | `space-4` (16) | `space-3` (12) |
| Action | Button M, `filled` / `neutral` | Button S |
| Secondary action | Button M, `ghost` / `neutral` | same |

**Three different states get confused here, and they need different content:**

1. **Empty by default** — nothing has been created yet. Explain what the thing
   is and give a primary action to create the first one. This is onboarding.
2. **Empty by filter** — the query or filters excluded everything. Say what was
   searched, and offer to clear the filters. Never offer "create new" here; the
   data may well exist.
3. **Empty by error** — loading failed. Say so plainly and offer retry. Never
   show a friendly empty state for a failed request, which quietly tells the
   user their data is gone.

**Rules.** One sentence of body copy. Empty states are read in a state of mild
confusion, and a paragraph will not be.

The icon may be duotone — this and File Upload are the only places duotone is
permitted. No illustration, no spot art, no mascot.

**Don't:**
- Use the same empty state for no-data, no-results and error
- Offer "Create new" when a filter caused the emptiness
- Write more than one sentence of body copy
- Use an illustration or mascot
- Centre an empty state in a container with no min-height, so it collapses
- Omit the action on a create-first empty state
- Say "No data" and nothing else

---

## 39. Stat / Metric

| Property | default | compact |
|---|---|---|
| Label | `sm` (14) `text-muted` | `2xs` (12) |
| Label → value | `space-1` (4) | 2 |
| Value | `2xl` (32) weight 600, `font-mono` tabular | `xl` (24) |
| Value → delta | `space-1` (4) | 2 |
| Delta | `sm` (14) weight 500 | `2xs` (12) |
| Delta positive | `success-text` + up arrow `icon-sm` | same |
| Delta negative | `danger-text` + down arrow `icon-sm` | same |
| Delta neutral | `text-muted` + dash | same |
| Comparison caption | `2xs` (12) `text-subtle` | same |
| In a card | Card padding, no border between stats | same |
| Grid gutter | `space-4` (16) | 12 |
| Sparkline | 40 tall, `accent`, no axes or grid | same |

**Rules.** Values use `font-mono` with tabular figures. A row of stats where the
digits do not align vertically is the fastest way to make a dashboard look
unconsidered.

**A delta needs a comparison to mean anything.** "+12%" alone is not information
— "+12% vs last month" is. The caption is not optional.

**Green-up / red-down is not universal.** For metrics where a decrease is good
(churn, latency, cost, error rate), the colour follows the *interpretation*, not
the arrow direction. Encode that per metric rather than deriving it from the
sign, and always pair colour with the arrow so it survives greyscale.

Sparklines carry the accent — one of the few places chroma is decorative — and
never get axes, grids or labels. If it needs axes, it is a chart, not a stat.

**Don't:**
- Use proportional figures for the value
- Show a delta with no comparison period
- Hard-code green-up / red-down where a decrease is the good outcome
- Rely on colour alone for direction
- Add axes or gridlines to a sparkline
- Put borders between stats in a grid — space separates them
- Round a value so hard the delta contradicts it (99.6% shown as 100%, "−0.4%")
