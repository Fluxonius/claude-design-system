# Design System

A white-label design system for Claude. One brand file produces a mathematically
derived, contrast-audited token set and a component stylesheet — and a set of
tools that check whether your code actually uses them.

The point is **consistency you can verify**, not a style you have to trust. A
screen built today and one built in six months should be indistinguishable, and
you should be able to prove it rather than eyeball it.

---

## Quick start

### A new project

```bash
cp assets/brand.template.json brand.json      # then edit the eight knobs
python3 scripts/build_tokens.py brand.json --out-dir src/styles
python3 scripts/build_components_css.py brand.json --out-dir src/styles
python3 scripts/build_preview.py brand.json --out proof.html   # look at it
```

```html
<link rel="stylesheet" href="src/styles/tokens.css">
<link rel="stylesheet" href="src/styles/ds-components.css">
```

```html
<button class="ds-btn ds-btn--filled ds-btn--neutral">Save changes</button>
```

### An existing project

The system **overrides**, it does not adapt. A codebase from six months ago
should end up looking like one started today — so nothing infers a brand from
what the project currently does.

```bash
python3 scripts/build_tokens.py brand.json --out-dir src/styles
python3 scripts/build_components_css.py brand.json --out-dir src/styles
python3 scripts/migrate.py --brand brand.json src/                 # dry run
python3 scripts/migrate.py --brand brand.json src/ --write --backup
python3 scripts/check_drift.py --brand brand.json src/             # confirm
```

Load order matters — the component layer must come last to win:

```
tokens.css  →  your existing CSS  →  ds-components.css
```

`migrate.py` rewrites values and strips banned patterns automatically, then
**reports** the component classes to replace (`.primary-btn` →
`ds-btn ds-btn--filled ds-btn--neutral`) without applying them. Markup rewrites
have to preserve semantics, so that part is deliberate work — Claude can do it
using `references/components-*.md`.

On a realistic legacy fixture: 23 violations → 0, drift score 9.8 → 100.

### A Tailwind project

Do not rewrite thousands of utility classes. Redefine what they mean:

```bash
python3 scripts/build_tailwind_theme.py brand.json --out-dir .
```

This emits a v4 `@theme` and a v3 config that **replace** Tailwind's defaults
rather than extending them. `p-4` and `rounded-lg` resolve to your tokens, and
`bg-violet-500`, `rounded-2xl`, `p-7` and `shadow-lg` cease to exist — an
off-system utility can't be typed by accident, by a teammate, or by a model.
Gradients and backdrop blur are off at the plugin level.

---

## The eight knobs

Everything else is system law. The personalization is deliberately narrow so
products built on this look like siblings rather than strangers.

| Knob | Options |
|---|---|
| `primary` | any chromatic hex — greyscale is rejected |
| `radius` | `sharp` · `soft` · `round` |
| `density` | `default` · `compact` |
| `iconSet` | `phosphor` · `lucide` · `remix` |
| `fontPreset` | `grotesk` · `editorial` · `technical` |
| `fonts` | optional per-slot override (`display`, `text`, `mono`) |
| `borderWeight` | `hairline` · `medium` · `bold` |
| `prefix` | class and token prefix, default `ds` |

`fontPreset` is the axis that most changes how a product *feels*. A serif display
face against a sans body reads completely differently from an all-grotesk
setting, and it breaks no rule.

---

## Scripts

| Script | What it does |
|---|---|
| `build_tokens.py` | brand.json → `tokens.css` + `tokens.json`. Derives the full palette in OKLCH. **Fails the build** on any WCAG AA violation or fill/backdrop collision. |
| `build_components_css.py` | → `ds-components.css`. All 43 components — 133 class families, 170 classes. Every value is a token reference, so the file is brand-agnostic. |
| `build_tailwind_theme.py` | → Tailwind v4 `@theme` + v3 config mapping utilities onto the tokens. |
| `build_preview.py` | → a proof sheet rendering **every** component from the shipped stylesheet, with a light/dark toggle. |
| `lint_conformance.py` | Checks code against *this brand's* tokens. `8px` is legal under `soft` and a violation under `sharp`. |
| `check_drift.py` | Scores a codebase, stores a baseline, reports the delta. Multi-project portfolio view. |
| `migrate.py` | Converts an existing project to the system: value rewrites and banned-pattern removal automatic, class mapping reported. |
| `lint_css_collisions.py` | Finds a class defined both bare and descendant-scoped, and prints which layout properties leak. |

Run the linter before calling any UI work done:

```bash
python3 scripts/lint_conformance.py --brand brand.json src/
python3 scripts/check_drift.py --brand brand.json src/ --save-baseline
```

---

## What is locked, and why

These were each built, tried and rejected. They are recorded as decisions rather
than left as defaults, so the same questions don't get reopened:

- **Cards never carry a shadow.** Borders-first is the depth mechanism. A shadow
  on a card is the most reliable generated-UI tell. Overlays are the only place
  elevation exists.
- **Primary actions are `ink`, never accent-filled.** If the brand hue fills
  every primary button, every screenshot is brand-coloured and products stop
  looking like one system. The accent stays rare so it means something — it is
  for links, selection, focus and status.
- **Hover shifts background only.** No border darkening, no text colour change,
  no transform, no lift.
- **No literal values anywhere.** `space-*` is the gap between things, `size-*`
  is the extent of a thing, `container-*` is an overlay or layout width,
  `measure-*` is line length in `ch`, `z-*` is a stacking layer. If a new
  component needs a number the families don't cover, add the token — don't
  hardcode it once.

---

## Known limitations

- **Class replacement during migration is manual.** A codemod would need to see
  your markup to avoid breaking semantics, so it's better done per-project with
  Claude reading the component references.
- **Borderless fields are a documented WCAG 1.4.11 deviation.** A fill heavy
  enough to pass 3:1 wouldn't read as an input. `build_tokens.py` prints the
  actual ratios under ADVISORY on every run so it stays visible. Add
  `border-strong` to inputs if a project needs a hard pass.
- **The stylesheet is CSS classes only** — no JS. Behavioural rules (focus
  trapping, keyboard handling, a combobox not reordering while you type) live in
  the reference files for Claude to implement.
- **Component specs are prose and can be wrong.** Nine defects were found in
  them the first time each component was actually rendered. If something looks
  off, trust your eye over the spec and fix both.

---

## Reference files

Load `components-core.md` plus the one group you need, not all of them.

| File | Contents |
|---|---|
| `foundations.md` | tokens, scales, semantic roles, the corner law, dark mode, motion, icons |
| `components-core.md` | **start here** — universal states, focus and disabled laws, and the 13 core components |
| `components-form.md` | combobox, date picker, slider, number, file upload, search, tag input, command palette |
| `components-nav.md` | sidebar, breadcrumb, pagination, stepper |
| `components-feedback.md` | inline alert, progress, spinner, skeleton |
| `components-content.md` | avatar, accordion, drawer, popover, chip |
| `components-layout.md` | app bar, page header, divider, empty state, stat |
| `components-data.md` | data table, tree, description list, timeline |
| `anti-patterns.md` | the blocklist, and the consequences of the laws above |
| `frameworks.md` | mapping the tokens onto Tailwind, React Native, SwiftUI, Flutter, Figma |

---

## Status

**0.9.** Every component is specified, implemented and rendered; the tooling is
tested. Two things to know before you rely on it:

- **The trigger evals have not been run.** `evals/cases.md` holds 26 test cases;
  running them needs Claude Code, because the harness spawns subagents. Until
  then it is unproven that the skill fires on a given phrasing, or that it reads
  one group file rather than all seven.
- **The component specs are the soft spot.** Around 28 defects surfaced the
  first time each component was actually rendered — including a 1.10:1 contrast
  failure caused by two equal-specificity rules splitting a fill from its text
  colour. All were invisible to the linters, because every value involved was a
  legal token. If something looks wrong, trust your eye over the spec, and fix
  both.

Bug reports on the rendered output are the most useful thing you can send.
