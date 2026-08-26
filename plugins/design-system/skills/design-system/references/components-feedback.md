# Feedback Components

Extends `components-core.md`. Universal states, disabled treatment, focus law
and measurement conventions are defined there.

**Where feedback belongs, in order of preference:** inline on the field that
caused it → an inline alert at the top of the affected region → a toast. A toast
is the weakest option, because it is transient and easy to miss. Never use one
for anything the user must act on.

---

## 23. Inline Alert / Banner

| Property | default | compact |
|---|---|---|
| Padding | `space-3` (12) × `space-4` (16) | `space-2` × `space-3` |
| Radius | `radius-md` | `radius-md` |
| Fill | `{status}-subtle` | same |
| Border | **none** | none |
| Leading icon | `icon-sm` (16), `{status}-text` | same |
| Icon gap | `space-2` (8) | 8 |
| Title | `sm` (14) weight 600, `{status}-text` | same |
| Body | `sm` (14), `text` | same |
| Title → body | `space-1` (4) | 4 |
| Action | Button S, `outline`, matching colour | same |
| Dismiss | Icon Button S, `plain` / `neutral` | same |
| Page-width variant | full-bleed, `radius-none` | same |

**Rules.** Fill only, no border — same as Badge. The status fill plus the status
icon carry the meaning; an edge on top of a tint is redundant weight.

**Always pair the colour with an icon and a word.** A red panel means nothing to
a red-green colourblind user reading a screenshot in greyscale. Success, danger,
warning and info each have a distinct glyph.

Body text stays `text`, not `{status}-text`. Tinting the whole paragraph makes
it harder to read and shouts; the title and icon carry the status.

An alert states **what happened and what to do**. "Something went wrong" is not
an alert, it is an apology. Errors that are recoverable get an action button.

Only banners the user can safely ignore are dismissible. An unresolved error is
not dismissible, because dismissing it does not fix it.

**Don't:**
- Add a border on top of the status fill
- Colour the body text with the status colour
- Rely on colour alone with no icon and no status word
- Make an unresolved error dismissible
- Stack more than one alert per region
- Use an alert for a field-level validation error — that belongs on the field
- Animate an alert in; it should be present on render
- Write "Something went wrong" with no cause and no next step

---

## 24. Progress

Two forms: **determinate** (a known percentage) and **indeterminate** (work of
unknown length). They are not interchangeable.

| Property | default | compact |
|---|---|---|
| Bar height | 4 | 4 |
| Bar radius | `radius-full` | `radius-full` |
| Track | `control` | `control` |
| Fill | `ink` | `ink` |
| Fill (in status context) | `{status}-solid` | same |
| Label | `sm` (14), `text` | same |
| Percentage | `sm` (14) `font-mono`, tabular | same |
| Label → bar | `space-1` (4) | 4 |
| Transition | width, `duration-base` (160ms) | same |
| Indeterminate cycle | 1200ms, `ease-standard`, loops | same |
| Circular size | 16 / 20 / 24 | same |
| Circular stroke | 2 | 2 |

**Rules.** `width` is the one property in the system permitted to animate,
because a progress bar *is* a width. Everything else animates `transform` and
`opacity` only.

Determinate progress must be monotonic — never run backwards. If a total is
unknown, use indeterminate rather than guessing and correcting.

Pair with a label whenever the work takes more than a couple of seconds:
"Uploading 3 of 12" tells the user more than 25% does. Percentages use tabular
figures so the number does not jitter as it counts.

Under `prefers-reduced-motion`, the indeterminate animation stops and the bar
holds a static partial fill.

**Don't:**
- Animate a determinate bar backwards
- Fake progress with a timer unconnected to real work
- Use indeterminate progress where a total is actually known
- Use a spinner for anything over ~10 seconds — show real progress
- Use proportional figures for the percentage
- Put a progress bar inside a toast

---

## 25. Spinner

| Property | default | compact |
|---|---|---|
| Sizes | 16 / 20 / 24 | same |
| Stroke | 2 | 2 |
| Track | `currentColor` at 20% opacity | same |
| Arc | `currentColor`, 25% of circumference | same |
| Rotation | 800ms linear, infinite | same |
| Colour | inherits `currentColor` | same |
| Delay before showing | 300ms | 300ms |

**Rules.** A spinner inherits `currentColor`, so it works inside an ink button,
a ghost button and on any surface without a variant per context.

**The 300ms delay is mandatory.** Showing a spinner for an operation that
resolves in 80ms produces a flash that reads as a glitch. If the work finishes
before the delay elapses, no spinner ever appears.

Spinners are for **short, local, unmeasurable** waits: inside a button during
submit, inside a combobox while querying. For anything longer than about a
second and a half, a skeleton is better, because it shows the shape of what is
coming. For anything over ten seconds, show real progress.

A spinner replaces a button's leading icon and never changes the button's width.

**Don't:**
- Show one instantly with no delay
- Use a full-page spinner where a skeleton would show layout
- Let a spinner change a button's width or label
- Use one for a determinate operation
- Show more than one spinner in a view at the same time
- Give a spinner its own colour instead of `currentColor`

---

## 26. Skeleton

| Property | default | compact |
|---|---|---|
| Fill | `control` | `control` |
| Radius | matches the element it replaces | same |
| Text line height | matches the type step's line-height | same |
| Text line radius | `radius-sm` | `radius-sm` |
| Last line width | 60% | 60% |
| Line gap | matches real content leading | same |
| Shimmer | 1600ms, `ease-standard`, `transform` only | same |
| Shimmer opacity | 0 → 0.06 → 0 | same |
| Reduced motion | static `control` fill, no shimmer | same |
| Delay before showing | 300ms | 300ms |

**Rules.** A skeleton mirrors the **real** layout: same dimensions, same radii,
same spacing. A skeleton that does not match what loads causes a visible jolt on
arrival, which is worse than no skeleton at all.

Skeleton the *structure*, not every atom. Three lines and a thumbnail beats
forty tiny rectangles, which read as noise.

The shimmer animates `transform` on an overlaid gradient — never
`background-position`, which repaints the whole element, and never `opacity` on
the skeleton itself, which makes the whole block pulse.

Vary text line widths (100%, 100%, 60%). Uniform bars read as a table, not prose.

**Don't:**
- Use a skeleton whose dimensions differ from the loaded content
- Skeleton every element rather than the structure
- Animate `background-position` or the element's own `opacity`
- Make every text line the same width
- Run a shimmer under `prefers-reduced-motion`
- Show a skeleton for under 300ms
- Mix skeletons and spinners in the same loading region
