# Foundations

Token names below omit the `--ds-` prefix for readability. The prefix is
configurable via `brand.json` → `prefix`.

## Grid

8pt base. 4pt permitted only for spacing below 24px and for optical adjustments
inside controls. Nothing else.

```
space-0    0      space-4    16     space-12   48
space-px   1      space-5    20     space-16   64
space-0-5  2      space-6    24     space-20   80
space-1    4      space-8    32     space-24   96
space-1-5  6      space-10   40
space-2    8
space-3    12
```

Use `space-2` (8) as the default gap between related elements, `space-4` (16)
between groups, `space-6`/`space-8` between sections, `section-gap` between
major page regions (density-aware).

## Type scale

Fixed px ladder. Locked for every product — only the typeface changes.

| Token | Size | Line height | Tracking | Use |
|---|---|---|---|---|
| `2xs` | 12 | 16 | +0.005em | Micro-labels, table meta, badges |
| `sm` | 14 | 20 | 0 | Dense body, table cells, buttons, helper text |
| `base` | 16 | 24 | 0 | Default body |
| `lg` | 20 | 28 | −0.006em | Card titles, section headings |
| `xl` | 24 | 32 | −0.012em | Page headings |
| `2xl` | 32 | 40 | −0.018em | Screen titles |
| `3xl` | 40 | 48 | −0.022em | Hero, marketing only |
| `4xl` | 56 | 64 | −0.026em | Hero, marketing only |

Negative tracking above 20px is not decorative — it corrects the optical
looseness of large text. Do not skip it.

**Weights.** 400 body, 500 UI labels and buttons, 600 headings. 700 exists but
is reserved for `2xl`+ display text. Never use more than three weights in one product.

**Slots.** `font-display` for `2xl`+ only. `font-text` for everything else.
`font-mono` for code, IDs, numeric tables, keyboard shortcuts.

**Optical limits.** Body copy caps at 68ch. Never set `base` or below at more
than 75ch. Never centre a paragraph longer than two lines.

## The two things that are not knobs

Both were prototyped as options and both were rejected, so they are recorded
here as decisions rather than defaults:

- **Cards never carry a shadow.** A hairline lift was built and tried. It reads
  slightly softer and it dilutes the signature: borders-first is the system's
  depth mechanism, and a shadow on a card is the most reliable generated-UI
  tell. Overlays are the only place elevation exists.
- **Primary actions are never accent-filled.** An accent-filled variant was
  built and tried. It reads more colourful and it costs the thing that makes
  this system white-labelable: if the brand hue fills every primary button,
  every screenshot is brand-coloured and products stop looking like one system.
  The accent stays rare so that it means something.

**Character comes from typography instead.** `fontPreset` is the axis that
changes how a product feels without touching a law — a serif display face
against a sans body reads completely differently from an all-grotesk setting,
and neither breaks anything.

## No literal values, anywhere

Every dimension in the system comes from a token, including in components the
user invents. A token family that only covers the predefined components is not a
system — it is a coincidence that holds until someone builds the 44th thing.

| Family | Covers | Example |
|---|---|---|
| `space-*` | the gap BETWEEN things — padding, margin, gap | `space-4` = 16px |
| `size-*` | the extent OF things — a checkbox box, a switch track, an avatar, a status dot | `size-20` = 20px |
| `container-*` | overlay and layout widths, named as decisions not a scale | `container-modal-sm` = 480px |
| `measure-*` | line length in `ch`, because readability is a character count | `measure-base` = 65ch |
| `control-h-*` / `control-px-*` | control heights and horizontal padding, density-aware | `control-h-md` |
| `radius-*` | derived from the corner preset | `radius-md` |
| `font-size-*` / `line-height-*` / `letter-spacing-*` | the type ladder | `font-size-sm` |
| `letter-spacing-display` | display-face tracking, keyed to the *face* not the size — negative tracking is a sans-serif correction and sets a serif too tight | `letter-spacing-display` |
| `duration-*` / `ease-*` | the motion ladder, including `duration-reduced` | `duration-fast` |
| `z-*` | stacking layers, in steps of 100 so a project can slot between | `z-modal` = 300 |
| `icon-*`, `touch-target`, `border-width`, `row-h`, `section-gap` | the remaining named dimensions | `touch-target` = 44px |

**`space-*` and `size-*` are not interchangeable.** Spacing is the distance
between two things; size is how big one thing is. A 20px checkbox is
`size-20`, not `space-5` — they may resolve to the same pixel value today, and
they mean different things, so a future change to one must not silently move the
other.

## Building something the system has no rule for

Three new components were built as a test — a split button, a kanban column and
a star rating. All three came out with **zero literal values** and passed
conformance under two different brands, so the token families do cover unseen
work. What they did *not* cover was the meaning. Decide these by analogy, in
this order:

**1. Which surface is it on?** Page (`bg`), card (`surface`), or raised overlay
(`surface-raised`). This determines the hover fill: `surface-hover` on the first
two, `control-subtle` on a raised one. Getting this wrong produces an invisible
hover in dark mode.

**2. Does it commit, or does it mean?** `ink` is the committed state — primary
buttons, checked controls, the current page, a filled progress bar, a selected
day. `accent` is meaning — links, selection, focus, status. A star rating's
filled stars are a *value*, not a selection, so they are `ink`; the empty ones
are `control-active`.

**3. Is it a label or a control?** A label takes fill and no edge (Badge); a
control that floats free on the page takes fill **and** an edge (Chip). If it
sits inside a container that frames it, it needs no edge.

**4. Is it one object or several?** Items in one object sit `2px` apart (nav
lists, segmented controls); separate objects sit `space-2` or more apart. This
is what makes a nav list read as a list rather than a stack of buttons.

**5. Does anything scroll?** Then the element carrying the radius must not be
the element that scrolls — put `overflow: hidden` on the container and scroll an
inner element.

**6. Is any dimension missing?** If no token fits, that is a signal, not a
licence: either the thing is off-system, or the system needs a new token. Add it
to `build_tokens.py` so every project gets it, rather than hardcoding it once.

Then run `lint_conformance.py`. It checks the **laws** as well as the values, so
a shadow outside an overlay, a hover that changes a border, and a hover-lift are
all caught even when every value used is a legal token.

**What it still cannot decide for you.** Whether a rating should be ink or a
warning amber; whether a kanban column is `bg` or `surface`; how two joined
buttons should be separated. Those are genuine judgement calls with no precedent
in the system, and inventing an answer silently is how a system starts to drift.
Ask, then write the decision into the reference file so the next person inherits
it.

`lint_conformance.py` enforces this across every dimensional property —
`width`, `height`, `min/max-*`, `top/right/bottom/left`, `inset`,
`line-height`, `border-width`, `outline-*`, `flex-basis` — plus durations,
`z-index` and `box-shadow`. Anything generated by this system passes its own
check, including the proof sheet.

## Colour

### Ramps

Three ramp families, all sharing identical lightness targets so a 600 is always
a 600. Steps: `50 100 200 300 400 500 600 700 800 900 950`.

- **Neutral** — locked warm grey (OKLCH hue 67, chroma ≤ 0.005). This carries
  most of the system's identity. Never derived from the brand colour.
- **Accent** — derived from the user's single `primary` hex. Hue is preserved;
  chroma is clamped to 0.045–0.155 so neon inputs are tamed and washed-out
  inputs stay chromatic.
- **Status** — `success` (hue 152), `warning` (78), `danger` (27), `info` (248).
  Locked. A brand colour never shifts these; a red delete button must read as
  danger in every product.

Step 600 is unusable for text-bearing fills — at L=0.636 neither white nor
near-black clears 4.5:1. Light-mode solid fills therefore sit at 700.

### Semantic roles

Only these are used in component code. Never reference a raw ramp step.

**Surfaces** — `bg`, `bg-subtle`, `surface`, `surface-raised`, `surface-sunken`,
`surface-hover`, `surface-active`

**Borders** — `border-subtle` (faint dividers), `border` (card edges),
`border-strong` (interactive control edges, 3:1 guaranteed)

**Text** — `text`, `text-muted`, `text-subtle`, `text-inverse`

**Accent** — `accent-subtle`, `accent-muted`, `accent-border`, `accent`,
`accent-hover`, `accent-active`, `accent-text`, `on-accent`

**Status** — for each of the four: `{name}-subtle`, `{name}-border`,
`{name}-solid`, `{name}-text`, `on-{name}`

**Other** — `focus-ring`, `overlay`

### The two things that are not knobs

Both were prototyped as options and both were rejected, so they are recorded
here as decisions rather than defaults:

- **Cards never carry a shadow.** A hairline lift was built and tried. It reads
  slightly softer and it dilutes the signature: borders-first is the system's
  depth mechanism, and a shadow on a card is the most reliable generated-UI
  tell. Overlays are the only place elevation exists.
- **Primary actions are never accent-filled.** An accent-filled variant was
  built and tried. It reads more colourful and it costs the thing that makes
  this system white-labelable: if the brand hue fills every primary button,
  every screenshot is brand-coloured and products stop looking like one system.
  The accent stays rare so that it means something.

**Character comes from typography instead.** `fontPreset` is the axis that
changes how a product feels without touching a law — a serif display face
against a sans body reads completely differently from an all-grotesk setting,
and neither breaks anything.

## No literal values, anywhere

Every dimension in the system comes from a token, including in components the
user invents. A token family that only covers the predefined components is not a
system — it is a coincidence that holds until someone builds the 44th thing.

| Family | Covers | Example |
|---|---|---|
| `space-*` | the gap BETWEEN things — padding, margin, gap | `space-4` = 16px |
| `size-*` | the extent OF things — a checkbox box, a switch track, an avatar, a status dot | `size-20` = 20px |
| `container-*` | overlay and layout widths, named as decisions not a scale | `container-modal-sm` = 480px |
| `measure-*` | line length in `ch`, because readability is a character count | `measure-base` = 65ch |
| `control-h-*` / `control-px-*` | control heights and horizontal padding, density-aware | `control-h-md` |
| `radius-*` | derived from the corner preset | `radius-md` |
| `font-size-*` / `line-height-*` / `letter-spacing-*` | the type ladder | `font-size-sm` |
| `letter-spacing-display` | display-face tracking, keyed to the *face* not the size — negative tracking is a sans-serif correction and sets a serif too tight | `letter-spacing-display` |
| `duration-*` / `ease-*` | the motion ladder, including `duration-reduced` | `duration-fast` |
| `z-*` | stacking layers, in steps of 100 so a project can slot between | `z-modal` = 300 |
| `icon-*`, `touch-target`, `border-width`, `row-h`, `section-gap` | the remaining named dimensions | `touch-target` = 44px |

**`space-*` and `size-*` are not interchangeable.** Spacing is the distance
between two things; size is how big one thing is. A 20px checkbox is
`size-20`, not `space-5` — they may resolve to the same pixel value today, and
they mean different things, so a future change to one must not silently move the
other.

## Building something the system has no rule for

Three new components were built as a test — a split button, a kanban column and
a star rating. All three came out with **zero literal values** and passed
conformance under two different brands, so the token families do cover unseen
work. What they did *not* cover was the meaning. Decide these by analogy, in
this order:

**1. Which surface is it on?** Page (`bg`), card (`surface`), or raised overlay
(`surface-raised`). This determines the hover fill: `surface-hover` on the first
two, `control-subtle` on a raised one. Getting this wrong produces an invisible
hover in dark mode.

**2. Does it commit, or does it mean?** `ink` is the committed state — primary
buttons, checked controls, the current page, a filled progress bar, a selected
day. `accent` is meaning — links, selection, focus, status. A star rating's
filled stars are a *value*, not a selection, so they are `ink`; the empty ones
are `control-active`.

**3. Is it a label or a control?** A label takes fill and no edge (Badge); a
control that floats free on the page takes fill **and** an edge (Chip). If it
sits inside a container that frames it, it needs no edge.

**4. Is it one object or several?** Items in one object sit `2px` apart (nav
lists, segmented controls); separate objects sit `space-2` or more apart. This
is what makes a nav list read as a list rather than a stack of buttons.

**5. Does anything scroll?** Then the element carrying the radius must not be
the element that scrolls — put `overflow: hidden` on the container and scroll an
inner element.

**6. Is any dimension missing?** If no token fits, that is a signal, not a
licence: either the thing is off-system, or the system needs a new token. Add it
to `build_tokens.py` so every project gets it, rather than hardcoding it once.

Then run `lint_conformance.py`. It checks the **laws** as well as the values, so
a shadow outside an overlay, a hover that changes a border, and a hover-lift are
all caught even when every value used is a legal token.

**What it still cannot decide for you.** Whether a rating should be ink or a
warning amber; whether a kanban column is `bg` or `surface`; how two joined
buttons should be separated. Those are genuine judgement calls with no precedent
in the system, and inventing an answer silently is how a system starts to drift.
Ask, then write the decision into the reference file so the next person inherits
it.

`lint_conformance.py` enforces this across every dimensional property —
`width`, `height`, `min/max-*`, `top/right/bottom/left`, `inset`,
`line-height`, `border-width`, `outline-*`, `flex-basis` — plus durations,
`z-index` and `box-shadow`. Anything generated by this system passes its own
check, including the proof sheet.

## Colour restraint

**Chroma has four jobs, and the primary button is not one of them:**

1. **Links** — `accent-text`, underlined on hover only
2. **Selection** — `accent-subtle` fill + `accent-text`: selected table rows,
   checked menu items, active nav items, chosen select options
3. **Focus** — the ring, on a dedicated `focus-ring` role that clears 3:1
   against every surface including the recessed `bg-subtle` fill
4. **Status** — danger, success, warning, info, and data visualisation

Everything else is warm grey or ink.

**Ink carries commitment.** The `ink` family (`ink`, `ink-hover`, `ink-active`,
`on-ink`) fills primary buttons, checked checkboxes, radio dots and switched-on
tracks. Near-black in light mode, near-white in dark — it inverts rather than
staying dark, so a primary button always reads as the heaviest thing on screen.

Splitting commitment (ink) from meaning (accent) is what makes this system
white-labelable. If the primary button were accent-filled, every screenshot
would be dominated by the brand hue and every product would read as "the teal
one". Instead the accent appears rarely and therefore means something, and the
same layout stays recognisably this system across every brand that uses it.

**Surface stack.** The page (`bg`) is tinted warm grey; cards (`surface`) are
near-white and sit above it; popovers and menus (`surface-raised`) sit above
those. Three depths, no shadows, all from fill alone. In dark mode the steps are
deliberately compressed and low — a dark card that lifts too far off the page
reads as grey plastic rather than as depth.

**The control scale is separate from the surface scale.** `control-subtle`,
`control`, `control-hover`, `control-active` and `control-border` are a
dedicated grey ramp
for things that sit *on* a surface: inputs, neutral buttons, badges, segmented
tracks, skeletons. They are not defined as "one step off whatever is behind
them", because the same input has to stay legible on the tinted page, on a
near-white card, and inside a raised popover. One fixed scale for controls means
a field looks like the same field wherever it lands.

`control-subtle` is the faintest fill in the system and exists so a ghost button
can be tinted at rest while still having somewhere to go on hover. Every colour
family carries the same `-subtle` → `-muted` pair for exactly this reason.

**A tint must be visible on every surface it can land on.** This has now bitten
twice, in both directions:

1. `control-subtle` once resolved to the same step as `bg`, so tinted ghost
   buttons were invisible on the page.
2. `control-subtle` once resolved to the same step as `surface-raised` in dark
   mode — *identical hex, 1.000 contrast* — so every ghost and plain hover
   inside a modal, popover, menu, drawer or toast did nothing at all. Overlays
   are exactly where icon-only actions cluster, so this hit the densest controls
   in the system.

The lesson is that a control ramp has to clear **three** backgrounds, not one:
the page, the card, and the raised overlay. `build_tokens.py` audits
`control-subtle`, `control` and `control-hover` against all three in both
themes, plus `control` against `control-subtle`, so any step change that
collapses a distinction fails the build rather than shipping as a screenshot
someone notices later.

In dark mode the control ramp therefore sits *above* `surface-raised`
(850/800/750/700 against a 900 overlay), not beside it.

**Removing a container's border constrains its contents.** An `outline` button
is identified by its edge alone, so it needs 3:1 against whatever is behind it.
That holds on `bg`, `surface`, `surface-raised` and `accent-subtle`, and fails
on `control` (2.79) and `control-subtle` (2.96). A tinted, borderless container
therefore takes `plain`, `ghost` or `filled` actions — never `outline`.

**Borders are deliberately light.** `border-subtle` and `border` are decorative
and sit close to their background; only `border-strong` carries the 3:1
interactive requirement. The house floor for decorative borders is 1.10:1
against the page — below WCAG's text thresholds because a card edge is not
information, it is a hint. If a divider needs to be *seen* rather than sensed,
it is doing a job that whitespace or a heading should be doing instead.

**Fields are borderless.** A `control` fill and no edge at rest; hover shifts the
fill, focus adds the ring, invalid adds a `danger-border`. This sits below the
WCAG 1.4.11 3:1 boundary requirement, deliberately and documented — see the
Input component and the ADVISORY block printed by `build_tokens.py`.

**Drift is the real failure mode, not ugliness.** A generated screen usually
looks fine on the day it is made. The problem is screen #47 in month six: a
radius one step off, a hover fill that was legal on a card reused on an overlay,
a hex that came from nowhere. None of it is visible in a single review, and all
of it compounds. `scripts/check_drift.py` scores a codebase, stores a baseline,
and reports the delta on the next run, so divergence is a number that moves
rather than a feeling someone eventually has.

**Conformance is checkable, and brand-relative.** `scripts/lint_conformance.py`
derives the legal vocabulary from a project's own `brand.json` and checks the
code against it. This is why `border-radius: 8px` is correct in a `soft` project
and a violation in a `sharp` one — there is no universal answer, only the
answer this brand generates. Run it before shipping; the token audit proves the
palette is sound, the linter proves the code uses it.

**Surfaces never invert.** Components are guaranteed to work on exactly four
backgrounds: `bg`, `surface`, `surface-raised` and `control`. Every button
priority, every text role and every border role is audited against those and
only those.

The Tooltip is the single exception, and it is safe precisely because it is
self-contained: it computes its own foreground from its own background and
carries no components inside it. Any *other* inverted surface — an ink toolbar,
a dark banner, a coloured hero strip with controls in it — is a background no
component is defined against, and everything placed on it needs a colour
override to survive.

**An override is the signal that the container is wrong, not the component.**
If a button needs an inline colour to be legible inside something, replace the
container's fill with one of the four supported backgrounds rather than adding a
tenth button variant for it.

**Hover is background-only.** Every control shifts its background on hover and
changes nothing else — no border darkening, no text colour change, no transform.
One rule, every component.

**Which hover fill depends on what is behind the element.** There is no single
hover token, and assuming there is one is the most persistent bug in this
system:

| The element sits on | Hover fill |
|---|---|
| The page (`bg`) or a card (`surface`) | `surface-hover` |
| A raised overlay — menu, popover, dropdown, drawer, toast | `control-subtle` |

**Light mode hides this.** In light, `surface` and `surface-raised` are the same
step, so one hover token appears to work everywhere and the bug is invisible.
In dark they diverge, and `surface-hover` collides exactly with
`surface-raised` — 1.000 contrast, no hover feedback at all on precisely the
rows where hover is the only affordance. Anything inside an overlay hovers with
`control-subtle`.

## Dark mode

The page is **true black** (`#000000`). Surfaces climb from there in small
steps, and the whole dark ladder sits low on purpose:

| Role | Dark value |
|---|---|
| `bg` | `#000000` |
| `surface` | near-black, a few points up |
| `surface-raised` | one step above that |
| `control` (inputs, neutral fills) | above the raised surface, still dark |
| `border-subtle` / `border` | quiet — a border in dark mode reading brighter than the text it frames is the usual error |
| `border-strong` | the only dark border that carries real contrast, because it is the one that must clear 3:1 |

Two constraints this ladder has to satisfy simultaneously, and both have been
violated at least once:

- `control-subtle` must differ from `surface-raised`, or ghost and plain hovers
  inside menus, popovers and drawers do nothing at all.
- `border-subtle` must differ from `surface-raised`, or a divider inside a
  popover is invisible.

`build_tokens.py` audits both, plus every fill against every backdrop, so a
future adjustment to the ladder cannot silently reintroduce either.

Generated as a locked step inversion, not a second palette. `bg` moves from
neutral-50 to neutral-950; text from 950 to 50; borders from 300 to 700.

Two consequences that must be respected:

- **Surfaces get lighter as they rise.** In light mode a raised surface stays
  neutral-50 and gains a border. In dark mode it moves *up* the ramp
  (900 → 800). Never use shadow to signal elevation in dark mode; it is invisible.
- **Solid fills move to step 500.** Accent-700 on a dark background is too heavy
  and fails contrast against dark text. The generator handles this — do not
  hand-tune.

Never pure black (`#000`) and never pure white (`#fff`) as a surface. Both are
outside the neutral ramp by design.

## Elevation

Borders-first. Four levels, and most UI only ever needs the first two.

| Level | Treatment | Used by |
|---|---|---|
| 0 | `bg`, no border | Page background |
| 1 | `surface` + `border` | Cards, panels, table containers, inputs |
| 2 | `surface-raised` + `border` + `shadow-sm` | Dropdowns, popovers, tooltips |
| 3 | `surface-raised` + `border` + `shadow-md` | Modals, sheets, command palettes |
| 4 | `shadow-lg` | Reserved. Effectively unused. |

A card is level 1. If a card has a shadow, that is a bug.

## Motion

`duration-fast` 120ms for state changes on controls (hover, press, checkbox).
`duration-base` 160ms for entering and exiting overlays.
`duration-slow` 240ms reserved for large surfaces (sheets, drawers).

`ease-standard` for entrances and state changes, `ease-exit` for exits.

**Only two properties animate: `opacity` and `transform`.** Never animate
`height`, `width`, `top`, `left`, `color`, or `box-shadow`. Overlays enter with
opacity 0→1 plus `translateY(4px)→0` or `scale(0.98)→1`. Nothing else.

No looping animation, no attention-seeking motion, no parallax, no scroll-jacking.
`prefers-reduced-motion` is honoured globally in `tokens.css`.

## Icons

**Three layout rules that only show up when rendered.** Each of these produced a
visible defect that no value check could see, because every token involved was
legal:

- **An element inset inside a field is inset by the field's own padding**, never
  `right: 0`. Steppers, clear buttons and trailing icons sit on the same optical
  margin as the value, and the field reserves room for them so text cannot run
  underneath.
- **A radiused box must not also be the scroll container.** A scrollbar is
  painted inside the padding box, and its square corner clips straight through
  the rounded edge. Put the radius and `overflow: hidden` on the container, and
  scroll on an inner element.
- **A rounded container needs `overflow: hidden` if its children have square
  corners**, or the first and last child overflow the radius. A list of rows is
  its own component with its own border and radius — not rows dropped into a
  card with `padding: 0`.

**A rule that sets a background must also set its foreground.** Two selectors of
equal specificity split a fill from its text colour and produced a 1.10:1 day
cell in the calendar: one rule supplied `background`, an earlier one still
supplied `color`. Contrast auditing cannot see this — both tokens are legal and
the pair `on-ink`/`ink` passes at 16:1. It only appears when the two rules meet
on one element.

**Native form-control furniture is suppressed and redrawn.** A browser's select
arrow, date input icon and number spinners are positioned by the UA and ignore
the field's padding. The system suppresses them with `appearance: none` and
draws its own, inset by the field's own horizontal padding.

**Two glyphs that must match should come from one pipeline.** The checkbox tick
and its indeterminate bar looked different weights because one was a masked SVG
at an effective 1.375px stroke and the other a 2px div. Both now render through
the same mask at the same viewBox and stroke width, so they cannot diverge.

**An icon is always sized by the system, never by itself.** An inline `<svg>`
carrying only a `viewBox` has no intrinsic size, so it falls back to the
replaced-element default of 300x150 — a 300px-wide icon. Sizing icons
per-component is not enough: it covers the components that happen to have a
rule and leaves every other one enormous, which is exactly what happened here
(menu items, combobox options, tree rows and empty states).

The stylesheet therefore opens with a zero-specificity default —
`:where([class*="ds-"]) svg:not([class])` at `icon-sm` — so any icon anywhere in
a system component is sized, and components needing a different size (icon
buttons at `icon-md`, drop zones and empty states at `icon-lg`) override it by
source order. `:not([class])` leaves classed SVGs alone, so the spinner and
sparkline size themselves.

A corollary for markup: **do not put width/height attributes on icon SVGs.**
Let the system size them, or a brand's density change will not reach the icons.


One set per product: Phosphor, Lucide, or Remix. Never mixed — their stroke
grammar differs and mixing is instantly visible.

Normalisation, so the three are interchangeable:

- 24px design grid, rendered at `icon-sm` 16 / `icon-md` 20 / `icon-lg` 24
- Optical stroke ~1.5px; use each library's closest weight (Phosphor `regular`,
  Lucide default, Remix `line`)
- Icons inherit `currentColor`. Never assign an icon its own colour.
- Icon-only controls require an accessible label.
- **Emoji are not icons.** Never substitute one.

Icon sizing pairs with text: `sm`/`base` text → `icon-sm`; `lg`/`xl` → `icon-md`.

## Controls

Heights and horizontal padding, by density. All multiples of 4.

| | default | compact |
|---|---|---|
| `control-h-sm` | 32 | 28 |
| `control-h-md` | 40 | 32 |
| `control-h-lg` | 48 | 40 |
| `control-px-sm` | 12 | 8 |
| `control-px-md` | 16 | 12 |
| `control-px-lg` | 20 | 16 |
| `row-h` | 48 | 36 |
| `section-gap` | 32 | 24 |

`md` is the default for every control. Minimum touch target is 44×44 regardless
of density — on touch, pad the hit area rather than growing the control.

## The corner law

The signature of this system. One base radius; everything else derives.

```
radius-none  0
radius-sm    base × 0.5
radius-md    base            ← the default for controls and cards
radius-lg    base × 1.5
radius-xl    base × 2
radius-full  9999
```

**Concentric nesting: `inner = outer − gap`.**

When a rounded element sits inside another rounded element, the inner radius
equals the outer radius minus the gap between them. This keeps the corner
strokes parallel, which is what the eye actually reads as "designed".

Worked example at `soft` (base 8):

- Modal, `radius-lg` = 12, padding 16 → inner card radius = 12 − 16 = negative,
  so it clamps to 0... **wrong instinct.** Clamp to `radius-sm` (4) instead:
  once the gap exceeds the outer radius, the inner element is visually
  independent and takes the default control radius, not 0.
- Card, `radius-md` = 8, padding 4, inner thumbnail → 8 − 4 = 4 = `radius-sm`. ✓
- Input group: outer wrapper 8, inset button with 2px inset → 6.
- Avatar, badge, pill, tag, toggle track → `radius-full` always, at every preset,
  including `sharp`. Circles are exempt from the corner law.

The practical rule: **flush-mounted children derive; padded-away children reset
to `radius-md` or `radius-sm`.** Never nest a larger radius inside a smaller one.

At `sharp` (base 2) the law still runs — it just produces 1s and 2s. Do not
"round up" sharp to make nesting easier.
