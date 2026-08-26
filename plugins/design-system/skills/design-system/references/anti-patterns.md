# Anti-Patterns

Read before any greenfield UI. These are not stylistic preferences — they are the
specific defaults that make generated interfaces instantly identifiable, and the
reason this system exists.

## The tells

Ranked by how reliably each one gives away machine-generated UI.

**1. The shadow-border-lift stack.** A card with a border *and* a shadow *and* a
hover transform that raises and scales it. This system is borders-first: level 1
gets a border and nothing else. Hover changes background, not geometry.

**2. Purple-to-blue gradients.** On buttons, on hero backgrounds, on icon
containers, as text fill. This system has no gradient tokens. Flat fills only.
Same for `backdrop-filter: blur()` glassmorphism panels.

**3. The three-equal-cards row.** Three feature cards, each with a centred
coloured icon in a tinted rounded square, a bold title, and two lines of grey
text. Real products have asymmetric layouts because real content has unequal
importance. If three things genuinely deserve equal weight, they still do not
need identical decoration.

**4. Emoji as iconography.** 🚀 ✨ 🎯 in headings, buttons, empty states, feature
lists. Use the chosen icon set. Emoji are content, never UI.

**5. Everything centred.** Centred headings, centred paragraphs, centred empty
states, centred form labels. Left-align by default. Centre only single-line
display text and the contents of genuinely symmetrical containers.

**6. Uniform spacing.** The same 16px or 24px gap between every element,
producing a flat rhythm with no grouping. Related items get `space-2`, groups get
`space-4`/`space-6`, sections get `section-gap`. Whitespace is how hierarchy is
communicated.

**7. Decorative colour.** Tinted section backgrounds, a different accent per
card, coloured borders for emphasis, coloured headings. Chroma is reserved for
links, selection, focus, and status. The default primary action is `ink`, not
the accent — an accent-filled button on every screen is what makes generated UI
read as "the purple app".

**8. Rounded-everything.** `rounded-2xl` on every surface regardless of size, or
`radius-full` on non-pill elements. Radius comes from the corner law and scales
with the element's role, not its mood.

**9. Missing states.** No disabled, no loading, no empty, no error, no
focus-visible. A component with only a rest and hover state is a mockup.

**10. Fake density.** `text-sm text-gray-500` applied to everything, so nothing
has hierarchy and everything is slightly hard to read. Use `text` for primary
content and reserve `text-muted` for genuinely secondary information.

## Also forbidden

- Animated gradient borders, glowing shadows, neon accents
- Looping animation, floating elements, parallax, scroll-jacking
- More than three font weights, or a second display typeface
- Icons with their own colours instead of `currentColor`
- Icon-only buttons with no `aria-label` and no tooltip
- A third button size, or a filled/neutral and filled/primary button on one screen
- `text-inverse` on a tooltip (it inverts the wrong way in dark mode)
- A hover fill that equals the surface behind it — check overlays specifically,
  since `surface-raised` is the background most often forgotten
- A fill-only Chip: it floats on the page with no container to frame it, so it
  needs an edge where a Badge does not
- **An inverted surface** — an ink toolbar, a dark banner, a coloured strip with
  controls in it. No button priority is defined against one, so everything
  placed on it needs a colour override to be legible
- **A colour override on a component.** It is never the fix. It means the
  container is a background the system does not support; change the container
- Pure `#000` or `#fff` surfaces
- `box-shadow` transitions, `height`/`width` animations
- Zebra-striped tables
- Placeholder text used as a label
- "Lorem ipsum" — write plausible domain content instead
- Arbitrary values: `p-[13px]`, `#5B7FE8`, `rounded-[10px]`
- Nesting a larger radius inside a smaller one
- Toasts for form validation
- Switches inside forms that have a Save button
- Modals stacked on modals

## Copy

Interface text is part of the design, and generic copy reads as machine-made just
as loudly as generic layout.

- Buttons are specific verbs: "Save changes", "Send invite", "Delete project" —
  not "Submit", "Click here", "Get Started".
- Sentence case for everything. Not Title Case, not ALL CAPS. Exception:
  `2xs` micro-labels may use uppercase with positive tracking.
- Errors state what happened and what to do: "That email is already registered.
  Sign in instead?" — not "Invalid input" or "Something went wrong".
- Empty states describe the next action, not the absence: "Create your first
  invoice to see it here."
- No exclamation marks. No "Oops!". No "Awesome!". No em-dash-heavy marketing
  voice. Cut adjectives — "Powerful, intuitive analytics" says nothing.

## The two-second test

Before presenting any UI, check:

1. Could this be any SaaS product, or does it look like it belongs to *this* one?
2. Does anything have a shadow that is not floating above the page?
3. Is there more than one accent-coloured element competing for attention?
4. Are the corners consistent, and do nested corners run parallel?
5. Does every interactive element have all seven states?
6. Is the spacing communicating grouping, or is it uniform?
7. Would a designer be able to name why each size and space was chosen?

If a rule here conflicts with an explicit user instruction, the user wins — but
say which rule is being broken and why it matters, once, then build what they asked.
