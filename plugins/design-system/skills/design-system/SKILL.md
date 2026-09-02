---
name: design-system
description: Build UI that conforms to one consistent white-label design system instead of generic AI-default styling. Use when creating or restyling any interface, component, screen, dashboard, landing page or app in any framework; when the user mentions design tokens, theming, dark mode, UI density or spacing scale, or wants UI that looks like a real product rather than "AI slop". Also use to adopt the system in an existing project ("apply the design system", "make my old project consistent", migrate hardcoded colours and spacing to tokens); to set up a Tailwind theme so utilities resolve to tokens; to lint or audit UI code for conformance, measure design drift across projects, or check WCAG contrast of a palette; to run brand personalization (primary colour, fonts, corner radius, density, icons); to regenerate tokens.css or components.css from brand.json; or to build a new component matching an existing system. Not for backend logic, data modelling or copy with no UI.
license: Complete terms in LICENSE.txt
---

# Design System — generate, apply, enforce

A white-label system. Every product built with it is recognisably the same system,
personalised along a deliberately narrow set of axes.

Two categories, and the split is the whole point:

| Personalizable (6 knobs) | Locked (everything else) |
|---|---|
| Primary colour (1 hex) | Warm-grey neutral ramp |
| Display / text / mono typefaces | Type scale, spacing scale, 8pt grid |
| Corner radius preset | Corner *law*, component anatomy |
| Density preset | Status hues, semantic role mapping |
| Icon set (3 options) | Motion, focus treatment, elevation model |
| Border weight | State logic, accessibility floor |

If a request would change something in the right-hand column, that is not
personalization — that is a different design system. Say so.

## Workflow

### 1. Locate the brand config

Look for `brand.json` at the project root (also check `design/`, `src/`, `.config/`).

- **Found** → read it, run the generator (step 3), build. Ask nothing.
- **Not found** → **ask before building.** Do not choose for the user, and do
  not build first and ask afterwards.

  > This project has no `brand.json` yet. Two options:
  >
  > 1. **House defaults** — slate blue `#3D5A80`, Geist (`grotesk`), soft
  >    corners, default density, Lucide icons, hairline borders.
  > 2. **Customize** — six questions, starting with your own brand hex.

  Either answer writes `brand.json` to the project root, so the question is
  asked **once per project, never again**:

  - House defaults → `python3 scripts/build_tokens.py --defaults > brand.json`
  - Customize → step 2, then write the answers

  Then continue at step 4.

**The gate is scoped to building.** Ask only when the task will produce or
restyle UI — that includes the retrofit path in step 3. Never ask for read-only
work: a contrast check, `lint_conformance.py`, `check_drift.py`, or a question
about the system all run against an explicit brand or house defaults, silently.
A user who asked "is this palette accessible?" did not ask to be onboarded.

The house default is a muted slate blue (`#3D5A80`) with the `grotesk` preset —
deliberately *not* indigo-600 + Inter. That pairing is the most recognisable
AI-default look there is, so it must never be what the no-config path produces.

Ask once per project. Once `brand.json` exists, read it and build.

### 2. Run setup (when the user picks Customize, or asks later)

Ask these six, conversationally, in one or two batches. Never more than six.

1. **Primary colour** — any brand hex; it is adapted, not vetted. The generator
   keeps the *hue*, clamps chroma into the house range and takes lightness from
   the locked ramp, so a custom colour cannot produce a contrast failure —
   `#FFFF00` resolves to accent `#777700`. A greyscale hex has no usable hue, so
   it is adapted to a near-neutral accent at the neutral hue and warns that
   links, focus and selection will read as grey.
2. **Typefaces** — offer the three presets first; most users should take one.
   - `grotesk` — Geist / Geist / Geist Mono (default; precise, neutral)
   - `editorial` — Instrument Serif / Inter / IBM Plex Mono
   - `technical` — IBM Plex Sans / IBM Plex Sans / IBM Plex Mono

   Anyone with a brand face can override slots individually via `fonts`
   (`display`, `text`, `mono`); the preset fills the rest. A serif in the `text`
   slot is rejected — display faces never carry body copy.
3. **Corners** — `sharp` (2px) · `soft` (8px) · `round` (14px).
4. **Density** — `default` or `compact`.
5. **Icons** — `phosphor` · `lucide` · `remix`. One set per product, never mixed.
6. **Border weight** — `hairline` (1px) · `medium` (1.5px) · `bold` (2px).

Write answers to `brand.json`. Do not invent extra fields; the generator
rejects unknown values.

### 3. Adopting the system in an EXISTING project

The system **overrides**, it does not inherit. A project from six months ago
should end up indistinguishable from one started today under the same brand.
Never infer the brand from the project's current styling -- that would preserve
the inconsistency the user wants removed.

```bash
python3 scripts/build_tokens.py brand.json --out-dir src/styles
python3 scripts/build_components_css.py brand.json --out-dir src/styles
python3 scripts/migrate.py --brand brand.json src/            # dry run first
python3 scripts/migrate.py --brand brand.json src/ --write --backup
python3 scripts/check_drift.py --brand brand.json src/        # confirm
```

Load order matters -- the component layer must come last to win:
`tokens.css` -> existing project CSS -> `ds-components.css`

`migrate.py` does two things automatically and reports a third:
- **Rewrites values**: colours to semantic roles (property-aware, so a white
  `background` becomes `surface`, not `on-ink`), radii, spacing, font sizes,
  durations. Pills become `radius-full` rather than snapping to the largest
  finite step.
- **Removes what no substitution can fix**: gradients, `backdrop-filter`,
  `transition: all`, `border-radius: inherit`, and shadows on anything that is
  not an overlay.
- **Reports component classes to replace** (`.primary-btn` ->
  `ds-btn ds-btn--filled ds-btn--neutral`) but does not apply them. Markup
  rewrites must preserve semantics, so do those deliberately, using the
  relevant `references/components-*.md` for anatomy and states.

Expect the drift score to go from single digits to 100 on the value layer, with
the class replacements remaining as deliberate work.

### 3b. Tailwind projects

Most vibecoded projects are Tailwind, and Tailwind puts design decisions in
**class names**, not CSS declarations. Rewriting thousands of utilities is the
wrong move; redefining what they mean is the right one.

```bash
python3 scripts/build_tailwind_theme.py brand.json --out-dir .
```

That emits `<prefix>-theme.css` (v4 `@theme`) and `tailwind.config.js` (v3).
Both **replace** Tailwind's defaults rather than extending them, so:

- `p-4`, `rounded-lg`, `text-sm` resolve to the system's tokens
- `bg-violet-500`, `rounded-2xl`, `p-7`, `shadow-lg` **cease to exist** — an
  off-system utility cannot be typed by accident, by a model, or by a teammate
- gradients and backdrop blur are switched off at the plugin level

Then `migrate.py` rewrites the utilities already in the codebase: raw palette to
roles, off-preset radii to the nearest, `transition-all` to `transition-colors`,
weights capped at 600, hover-lift removed, gradients removed (to `bg-ink` when
they carried light text, since that was a filled action — `bg-surface` would put
white text on white). `lint_conformance.py` checks utility classes too, so a
Tailwind file is no longer invisible to it.

### 4. Generate tokens

```bash
python scripts/build_tokens.py brand.json --out-dir ./src/styles
```

Emits `tokens.css` (CSS custom properties, light + dark) and `tokens.json`
(for non-web platforms). Prints a WCAG AA contrast audit and **exits non-zero
if any pair fails**. The brand colour cannot be the cause — hue is the only
thing carried over from it, and the audit is hue-invariant — so a failure means
the role table or a ramp step was edited.

Contrast audit alone: `python scripts/build_tokens.py brand.json --check`

`tokens.css` is generated output. Never hand-edit it; edit `brand.json` and regenerate.

### 5. Show the proof sheet after any setup or brand change

The proof sheet renders from the **shipped** `ds-components.css`, not a copy of
it, so what it shows is what a project gets. It covers every component family in
the stylesheet — verified, not assumed.

```bash
python scripts/build_preview.py brand.json --out preview.html
```

Renders a self-contained living style guide — ramps, semantic roles, type scale,
the corner law, the full button matrix, and every component, with a light/dark toggle. Always
generate this after setup so the user can confirm the personalization before any
product UI gets built on top of it.

### 6. Build against tokens, never against literals

Every colour, space, radius, duration and font size in UI code resolves to a token.
A raw hex, a `12px` padding, or a `border-radius: 6px` in component code is a bug —
it is the exact thing that breaks white-labelling.

## Non-negotiable laws

Apply these on every single component, without being asked.

**The corner law.** One base radius token; everything derives from it.
Nested corners are concentric: `inner = outer − gap`. A 12px card holding an
8px-inset button gives the button 4px. Never nest a larger radius inside a smaller
one. At `sharp`, this still applies — it just resolves to small numbers.
This is the system's signature; get it wrong and nothing else matters.

**Borders first, shadows last.** Separation is achieved with `border` and surface
tint. Shadow is reserved exclusively for things that genuinely float above the
page: dropdowns, popovers, modals, toasts. A card does not get a shadow. Ever.

**Two kinds of border.** `--ds-border` / `--ds-border-subtle` are decorative
(card edges, dividers) and deliberately faint. `--ds-border-strong` is for
interactive control edges (input, select, checkbox) and is the only one that
clears the 3:1 non-text contrast requirement. Using the faint one on an input
is an accessibility failure, not a style choice.

**Focus is global.** `:focus-visible` is defined once in `tokens.css`. Never
restyle focus per component. Never remove an outline without replacing it.

**8pt grid, 4pt below 24px.** Every dimension is a multiple of 8, except spacing
under 24px which may use 4. No 5px, no 15px, no 18px.

**Density changes size, not identity.** Compact alters control heights, padding,
row heights and section gaps. It never changes font size, radius, border weight
or colour.

**Character comes from `fontPreset`, not from loosening the laws.** Cards never
get a shadow and primary actions are never accent-filled — both were built,
tried and rejected (see Foundations). If a product needs to feel different,
change the typeface pairing.

**Ink commits, accent means.** Primary buttons and checked controls are `ink`
(near-black in light, near-white in dark). The brand hue is reserved for links,
selection, focus and status. An accent-filled primary button makes every
screenshot read as "the brand-colour app" — splitting the two is what lets one
system serve many brands and still look like one system. If a screen has three
coloured buttons, all three are wrong.

**No literal values, anywhere.** Every dimension comes from a token, including
in components the user invents. `space-*` is the gap between things, `size-*` is
the extent of a thing, `container-*` is an overlay or layout width, `measure-*`
is line length in `ch`, `z-*` is a stacking layer. If a new component needs a
number the families do not cover, add the token to `build_tokens.py` so every
project gets it — never hardcode it once. `lint_conformance.py` checks every
dimensional property, not just spacing.

**Hover shifts background only.** No border darkening, no text colour change, no
transform, no lift. One rule for every control in the system.

**Three surface depths, no shadows.** Tinted page (`bg`) → near-white card
(`surface`) → raised popover (`surface-raised`). Depth comes from fill and
border, never elevation.

**Controls have their own grey scale.** `control` / `control-hover` /
`control-active` / `control-border` is a fixed ramp for things sitting *on* a
surface — inputs, neutral buttons, badges, segmented tracks, skeletons. It is
not derived from whatever is behind it, so a field looks like the same field on
the page, on a card, and inside a popover.

**Fields are borderless.** `control` fill, no edge at rest; hover shifts the
fill, focus adds the ring, invalid adds a `danger-border`. This is a deliberate
documented deviation from WCAG 1.4.11's 3:1 boundary rule — `build_tokens.py`
prints the actual ratios under ADVISORY on every run. Add `border-strong` if a
project needs a hard pass.

**Buttons: two sizes, three priorities, three colours.** M and S only; filled /
outline / ghost; neutral / primary / destructive. `filled/neutral` (ink) is the
default action. Ghost carries a faint rest tint — it is never fully transparent.
Icon Button is a separate component with a fourth `plain` priority (no
background at all, for repeated row and toolbar actions) and mandatory
`aria-label` plus tooltip.

**AA floor.** 4.5:1 body text, 3:1 interactive edges and large text. Colour is
never the sole carrier of meaning — pair with icon, text, or shape.

## When there is no rule

The system covers 43 components across seven reference files. When the user needs
something outside them — a kanban board, a split button, a rating, a chart —
**ask before building**:

> The system has no rule for X yet. I can (a) compose it from existing primitives,
> (b) extend the system with a documented pattern you keep, or (c) build it
> one-off, outside the system. Which?

Do not silently invent a component and present it as system-conformant. Do not
refuse either. Ask, then follow through.

For (a) and (b), work through **Building something the system has no rule for**
in `references/foundations.md`. The token families cover the measurements — a new
component should need no literal values at all — but the *semantic* choices
(ink or accent? which surface? does it get an edge?) have to be decided by
analogy to an existing component, and that section lists the questions and the
precedents. Then run `lint_conformance.py`: it checks the laws, not just the
values, so a token shadow on a card or a hover that moves something is caught.

## References

Load only what the current task needs.

- `scripts/lint_conformance.py` — **run this on generated UI code before calling
  it done.** `python3 scripts/lint_conformance.py --brand brand.json src/`

  This is the part of the system a general design linter cannot replicate. It
  reads the project's `brand.json`, derives the exact token set that brand
  produces, and checks the code against *that* — not against universal
  anti-patterns. So it catches:
  - a hex that is nowhere in this brand's generated ramp
  - `var(--ds-surfce-hover)` — a typo'd token that resolves to nothing silently
  - `border-radius: 8px` in a project set to `sharp`, where the legal radii are
    0/1/2/3/4. The identical line is fine under `soft`. Conformance is
    brand-relative, which is the whole point.
  - spacing off this brand's scale, font sizes off its ladder
  - a colour override on a component, and inverted-fill containers
  - **Tailwind utilities** — raw palette, arbitrary values (`p-[13px]`),
    off-preset radii, off-scale spacing, `transition-all`, hover-lift,
    gradients, backdrop blur. Without this a Tailwind card with a gradient, two
    shadows and a hover-lift scored zero violations.
  - **illegal class combinations** — a button with two priorities, no colour, a
    missing base class, `plain` on a standalone labelled action, or an icon
    button with no accessible name. The value checks cannot see these: every
    class is spelled right and every token is legal; the combination is wrong.
  - `surface-hover` inside a raised overlay, where it is invisible in dark mode

  Exits 1 on any violation; `--json` for CI. The token audit proves the palette
  is sound; this proves the code actually uses it.
- `scripts/build_tailwind_theme.py` — emits a Tailwind v4 `@theme` and a v3
  config that map utilities onto this brand's tokens and delete the off-system
  ones. For a Tailwind project this is the primary adoption path.
- `scripts/build_components_css.py` — emits `<prefix>-components.css`, the
  installable component layer covering **all 43 components** (167 class
  families, ~1,440 lines). Every value is a token reference, so the file is
  brand-agnostic: swap `tokens.css` and the same stylesheet becomes a different
  brand. This is what a project adopts, instead of Claude re-deriving 43
  components from prose differently each time.
- `scripts/migrate.py` — converts an existing project TO the system. Value
  rewrites and banned-pattern removal are automatic; component class mapping is
  reported for deliberate application. `--write --backup` to apply.
- `scripts/check_drift.py` — measures how far a codebase has **wandered** from
  the system, and whether it is getting better or worse. Where the linter is a
  gate on one file, this is a health report on a whole product:
  - `--brand brand.json src/` → conformance score, per-rule breakdown, hotspot
    directories, and the nearest legal token for each off-system value
  - `--save-baseline` then `--compare` → the delta. "32.3 → 46.2, 11 fixed,
    4 newly introduced", with the new drift named
  - `--projects a/src:a.json b/src:b.json` → portfolio view across products,
    flagging the most drifted
  - `--fail-under 70` → CI gate; `--json` for tooling

  This is the multi-month, multi-product question that single-generation tools
  do not address: a model can produce a good screen today and a subtly
  different one in three months, and nothing in the generate-review loop
  notices the divergence accumulating.
- `references/foundations.md` — token catalogue, scales, semantic roles, the corner law worked through, dark mode, motion, icons.
- `references/components-core.md` — **start here for any component work.** The universal state set, disabled and focus laws, measurement-table conventions, and the 13 core components (Button, Icon Button, Input, Select, choice controls, Card, Modal, Table, Tabs, Badge, Tooltip, Toast, Menu).
- `references/components-form.md` — Combobox, Date Picker, Slider, Number Input, File Upload, Search Field, Tag Input, Command Palette.
- `references/components-nav.md` — Sidebar, Breadcrumb, Pagination, Stepper.
- `references/components-feedback.md` — Inline Alert, Progress, Spinner, Skeleton.
- `references/components-content.md` — Avatar, Accordion, Drawer, Popover, Chip.
- `references/components-layout.md` — App Bar, Page Header, Divider, Empty State, Stat.
- `references/components-data.md` — Data Table, Tree, Description List, Timeline.

The six group files extend core; they do not repeat it. Load core plus the one
group you need, not all seven.
- `references/anti-patterns.md` — **read before any greenfield UI.** The concrete list of AI-default habits this system exists to prevent.
- `references/frameworks.md` — mapping tokens to Tailwind, React Native, SwiftUI, Flutter, plain CSS.

## Relationship to other design guidance

General frontend-design advice optimises for *distinctiveness per project*. This
skill optimises for *consistency across projects*. When this skill is active it
takes precedence: distinctiveness comes from the six knobs, the content, and the
layout — not from reinventing the components.
