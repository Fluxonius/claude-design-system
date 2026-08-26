# Content Components

Extends `components-core.md`. Universal states, disabled treatment, focus law
and measurement conventions are defined there.

---

## 27. Avatar

| Property | default | compact |
|---|---|---|
| Sizes xs / sm / md / lg | 20 / 24 / 32 / 40 | 20 / 24 / 28 / 36 |
| Radius | `radius-full` (people) / `radius-sm` (orgs) | same |
| Fallback fill | `control` | `control` |
| Fallback initials | `text-muted`, weight 500 | same |
| Initials size | 40% of avatar size | same |
| Image fit | `cover`, centred | same |
| Ring (on busy bg) | 2px `surface` | same |
| Status dot | 25% of size, min 8 | same |
| Status dot ring | 2px `surface` | same |
| Group overlap | −25% of size | same |
| Group max shown | 4, then "+N" | 3, then "+N" |
| "+N" chip | same size, `control` fill, `text-muted` | same |

**Rules.** People are circles, organisations are `radius-sm` squares. This is the
one shape distinction that survives every corner preset, because it carries
meaning rather than style.

Initials fall back to one character for a single name, two for a full name,
never three. Fallbacks use the neutral `control` fill — **never a colour hashed
from the name**. Hash-coloured avatars are a reliable AI-generated tell, they
break the accent discipline, and they produce unpredictable contrast.

Status dots are bottom-right with a `surface` ring so they read on any photo.
Colour alone never carries status here; pair with a tooltip.

Avatar groups overlap by a quarter, with the leftmost on top so reading order
matches stacking order.

**Don't:**
- Hash a background colour from the user's name
- Use three initials
- Use circles for organisations or squares for people
- Stack more than four avatars without a "+N"
- Use `object-fit: contain`, which letterboxes faces
- Rely on a status dot alone with no tooltip or label
- Scale an avatar to a size off the four-step scale

---

## 28. Accordion / Disclosure

| Property | default | compact |
|---|---|---|
| Header height | `control-h-md` (40) | `control-h-sm` (32) |
| Header padding-x | `space-4` (16) | `space-3` (12) |
| Header font | `sm` (14) weight 500 | same |
| Header hover | `control-subtle` fill | same |
| Chevron | `icon-sm` (16), `text-subtle`, trailing | same |
| Chevron rotation | 0° → 90° on open, `duration-fast` | same |
| Open header divider | none (panel continues the row) | same |
| Divider | `border-width` `border-subtle`, full-bleed | same |
| Panel padding | `space-2` top, `space-4` sides and bottom | `space-2` / `space-3` |
| Panel font | `sm` (14), `text-muted` | same |
| Radius (standalone) | `radius-md` | `radius-md` |
| Radius (in a list) | `radius-none` | `radius-none` |

**Rules.** The whole header row is the trigger, not just the chevron — a tall
row with a 16px hit target is a usability failure.

Headers are `control-h-md`, not `control-h-lg`. A list of collapsed accordions is
a *navigation surface*: the user is scanning labels to find one, so each row
should cost as little vertical space as a menu item. 48px rows turn six questions
into a full screen of mostly empty space.

The chevron rotates 0° → 90° via `transform`. Never animate the panel's
`height`: it forces layout on every frame and cannot be done with `auto`. If
open/close needs to animate, use a grid-rows transition or accept an instant
toggle. An instant toggle is a perfectly good answer.

Panel padding has **no top padding** — the header's bottom padding already
provides the gap, and doubling it makes content float.

Accordions in a list share full-bleed dividers and drop their radius, so the
group reads as one object.

**Don't:**
- Give the header a margin. It is a fixed-height flex row; any inherited
  `margin-bottom` opens dead space under every row in the list
- Make only the chevron clickable
- Leave the chevron unrotated when open — it is the only persistent open/closed signal
- Keep the header's bottom divider when the panel is open; it cuts the row from its content
- Animate `height` or `max-height`
- Remove the panel's top padding: the fixed-height header supplies no gap
- Nest accordions
- Use an accordion to hide something the user needs on every visit
- Open every panel by default — that is just a page
- Use a plus/minus glyph instead of the chevron

---

## 29. Drawer / Sheet

| Property | default | compact |
|---|---|---|
| Width (side) | 400 / 520 / 640 | same |
| Height (bottom) | max 90vh | same |
| Fill | `surface-raised` | same |
| Edge | `border-width` `border` on the attached side | same |
| Radius (side) | `radius-none` | `radius-none` |
| Radius (bottom sheet) | `radius-lg` top corners only | same |
| Shadow | `shadow-md` | `shadow-md` |
| Padding | `space-6` (24) | `space-4` (16) |
| Header height | `control-h-lg` (48) | 40 |
| Close | Icon Button M, `plain` / `neutral`, top-right | same |
| Backdrop | `overlay`, no blur | same |
| Enter | `translateX/Y` 100% → 0, `duration-base` | same |
| Grab handle (bottom) | 32 × 4, `control`, `radius-full` | same |

**Rules.** A side drawer is flush to the viewport edge, so it takes **no
radius** on that side — a rounded corner against a screen edge is the clearest
sign a component was designed in isolation. Bottom sheets round their top
corners only.

Drawer vs modal: a modal interrupts and demands an answer; a drawer supplements
and lets work continue. Drawers may be non-modal, in which case the backdrop is
omitted and the page stays interactive.

Modal drawers trap focus, lock body scroll and return focus to the trigger — the
same rules as Modal. Never nest a drawer inside a modal.

Enter animates `transform`, never `width` or `right`.

**Don't:**
- Round the edge that meets the viewport
- Nest a drawer inside a modal, or open two drawers at once
- Animate `width`, `left` or `right`
- Blur the backdrop
- Use a drawer where a modal's forced decision is required
- Omit the focus trap on a modal drawer
- Let a bottom sheet exceed 90vh with no internal scroll

---

## 30. Popover

| Property | default | compact |
|---|---|---|
| Fill | `surface-raised` | same |
| Border | `border-width` `border` | same |
| Radius | `radius-md` | `radius-md` |
| Shadow | `shadow-sm` | `shadow-sm` |
| Padding | `space-4` (16) | `space-3` (12) |
| Min / max width | 240 / 360 | 240 / 320 |
| Offset from trigger | `space-2` (8) | 8 |
| Viewport margin | 8 | 8 |
| Arrow | none | none |
| Enter | opacity + `translateY(-2px)`, `duration-fast` | same |

**Rules.** **Popover is not Tooltip.** A tooltip is a plain-text hint that opens
on hover after 400ms and contains nothing interactive. A popover opens on click,
holds interactive content, and takes focus. Choosing wrongly is the most common
failure here: hover-triggered interactive content is unreachable on touch and
impossible to move the pointer into.

No arrows. An arrow constrains placement, breaks on flip, and adds a shape the
corner law cannot govern. Position and proximity are enough.

Focus moves into the popover on open and returns to the trigger on close.
Escape and outside click close it. Flips and shifts to stay in the viewport,
with an 8px margin.

Never nest a popover in a popover. A popover containing a form long enough to
need scrolling should be a drawer.

**Don't:**
- Open a popover on hover
- Add an arrow or pointer
- Put a scrolling form inside one
- Nest popovers
- Use one where a tooltip's plain text would do
- Leave focus outside the popover after it opens
- Let it render outside the viewport instead of flipping

---

## 31. Chip / Filter Chip

Distinct from Badge: a Badge is a **label** and is never interactive; a Chip is
a **control**.

| Property | default | compact |
|---|---|---|
| Height | `control-h-sm` (32) | 28 |
| Padding-x | `space-3` (12) | `space-2` (8) |
| Radius | `radius-full` | `radius-full` |
| Font | `sm` (14) | `sm` (14) |
| Rest | `control` fill + `control-border` edge, `text` | same |
| Hover | `control-hover` fill, edge unchanged | same |
| Selected | `accent-subtle` fill, `accent-border` edge, `accent-text`, weight 500 | same |
| Selected leading check | `icon-sm` (16) | same |
| Leading icon / avatar | `icon-sm` (16) / avatar xs (20) | same |
| Remove affordance | `icon-sm` (16), 24 hit area, trailing | same |
| Gap between chips | `space-2` (8) | `space-1` (4) |
| Count suffix | `text-muted`, `font-mono` tabular | same |

**Chips carry an edge; Badges do not.** This is the one place fill-and-border
coexist, and it is deliberate. A Badge sits inside a table cell or a card, where
surrounding structure frames it. A Chip floats free on the page — a filter row
sits directly on `bg`, where a fill-only chip reaches only 1.12:1 and reads as a
faint smudge rather than a control. The edge is what makes it look pressable.

(The "fill plus border means `filled`" rule in Core applies to *buttons*, whose
priorities are defined by that distinction. Chips are not buttons.)

**Rules.** Selected chips use `accent-subtle` + `accent-text` + `accent-border` —
the system's selection language, with the edge shifting to match so the whole
shape changes state rather than just its middle.

Chips are pills at every corner preset, like Badges. Two shape categories,
consistently applied, survive all three radius settings.

A removable chip and a selectable chip are different components sharing a shape:
removable chips (in a combobox field, an applied-filters row) always show the
remove glyph; selectable chips (a filter set) show a check when on. Never both.

A filter chip row needs a visible "Clear all" once more than one is active.

**Don't:**
- Use a Chip where a Badge belongs, or make a Badge clickable
- Give a Chip a fill with no edge — it disappears on the page background
- Give a Badge an edge — its container already frames it
- Put both a check and a remove glyph on one chip
- Use `radius-md` at the `sharp` preset — chips stay pills
- Rely on fill alone for selection with no check glyph
- Let a chip row wrap to more than two lines without a "+N more"
- Use a 16px remove glyph as the whole hit area
