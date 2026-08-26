# Framework Mapping

The system is defined as visual law plus a token contract. `tokens.css` and
`tokens.json` are the only implementation artefacts. Everything below is
translation, not redefinition — if a platform cannot express a rule, the rule
still holds and the closest available approximation is used.

## Plain CSS / Web Components

Use `tokens.css` directly.

```css
.btn-primary {
  height: var(--ds-control-h-md);
  padding-inline: var(--ds-control-px-md);
  border-radius: var(--ds-radius-md);
  background: var(--ds-accent);
  color: var(--ds-on-accent);
  font: 500 var(--ds-font-size-sm)/var(--ds-line-height-sm) var(--ds-font-text);
  border: none;
  transition: background var(--ds-duration-fast) var(--ds-ease-standard);
}
.btn-primary:hover  { background: var(--ds-accent-hover); }
.btn-primary:active { background: var(--ds-accent-active); }
.btn-primary:disabled { opacity: .5; cursor: not-allowed; }
```

Dark mode: set `data-theme="dark"` on `<html>`, or rely on the built-in
`prefers-color-scheme` block.

## Tailwind

Import `tokens.css`, then map tokens into the theme so utilities resolve to them.
Never let Tailwind's default palette or spacing scale remain reachable — that is
how arbitrary values creep back in.

Tailwind v4 (`@theme`):

```css
@import "./tokens.css";

@theme {
  --color-bg: var(--ds-bg);
  --color-surface: var(--ds-surface);
  --color-border: var(--ds-border);
  --color-border-strong: var(--ds-border-strong);
  --color-text: var(--ds-text);
  --color-text-muted: var(--ds-text-muted);
  --color-accent: var(--ds-accent);
  --color-accent-hover: var(--ds-accent-hover);
  --color-on-accent: var(--ds-on-accent);
  /* status: -subtle, -border, -solid, -text for each */

  --radius-sm: var(--ds-radius-sm);
  --radius-md: var(--ds-radius-md);
  --radius-lg: var(--ds-radius-lg);

  --spacing-2: var(--ds-space-2);
  --spacing-3: var(--ds-space-3);
  --spacing-4: var(--ds-space-4);
  --spacing-6: var(--ds-space-6);
  --spacing-8: var(--ds-space-8);

  --text-sm: var(--ds-font-size-sm);
  --text-base: var(--ds-font-size-base);
  --text-lg: var(--ds-font-size-lg);

  --font-text: var(--ds-font-text);
  --font-display: var(--ds-font-display);
  --font-mono: var(--ds-font-mono);
}
```

Tailwind v3: the same mapping goes in `theme.extend` in `tailwind.config.js`,
with values as `var(--ds-*)` strings.

Then `dark:` variants become unnecessary for colour — the semantic tokens already
swap. Use `dark:` only for the rare structural difference.

Forbidden in Tailwind specifically: `shadow-lg` on cards, `rounded-2xl`,
`bg-gradient-*`, `backdrop-blur`, arbitrary values like `p-[13px]`, and any
`gray-*`/`slate-*` class (the neutral ramp is warm; those are not).

## React Native

Consume `tokens.json`. There are no CSS variables, so build two theme objects and
switch on `useColorScheme()`.

```js
import tokens from "./tokens.json";
const theme = (mode) => ({ ...tokens[mode], ...tokens.dimension });
```

Translation notes:

- Strip `px` from dimension values — RN takes unitless numbers.
- `border` → `borderWidth` + `borderColor`.
- Shadows: `shadow-sm`/`shadow-md` map to `elevation` 1 and 3 on Android and to
  `shadowOpacity` 0.06/0.08 with matching offsets on iOS. Levels 0 and 1 have no
  shadow at all, which is most of the UI.
- Focus rings do not exist. Substitute a 2px `accent-border` outline on the
  focused element for keyboard and TV navigation.
- Minimum touch target 44×44 always, even at compact density.

## SwiftUI

Generate a `Color` extension and a `Spacing` enum from `tokens.json`.

- Hex strings → `Color(red:green:blue:)`; put light/dark pairs in an asset
  catalog colour set so the OS handles switching.
- `radius-md` → `RoundedRectangle(cornerRadius:)`. The corner law applies to
  `.clipShape` nesting exactly as on web. Use `.continuous` corner style at
  `soft` and `round`; use `.circular` at `sharp`.
- `duration-fast`/`base` → `.animation(.easeOut(duration: 0.12 / 0.16))`.
  `ease-standard` is closest to `.easeOut`.
- Prefer `.overlay(RoundedRectangle().stroke(borderColor))` over `.shadow` —
  borders-first survives the platform jump.

## Flutter

Generate a `ThemeExtension` from `tokens.json`.

- Colours → `Color(0xFFRRGGBB)`; supply `ThemeData.light`/`dark` from the two
  token sets.
- Dimensions are logical pixels, so values transfer unchanged.
- `radius-md` → `BorderRadius.circular()`.
- Shadow levels → `BoxShadow` with the same offsets and opacities; do not use
  Material's default `elevation`, which is far heavier than this system allows.
- Override Material defaults explicitly: Material's ripple, its 4px default
  radius, and its `primary`-tinted surfaces all conflict with this system.

## Figma

Publish `tokens.json` as variable collections: one collection for primitives, one
for semantic roles with light/dark modes, one for dimensions. Semantic variables
alias primitives — never let a component reference a primitive directly, mirroring
the code rule.

## Any other target

The order of precedence when a platform fights the system:

1. The semantic role mapping — never change which role a component uses.
2. The corner law and the 8pt grid.
3. Contrast floors.
4. Exact shadow and motion values (approximate freely).

If a platform cannot honour 1–3, say so explicitly rather than quietly
substituting the platform's defaults.
