# Design System — generate, apply, enforce

A verifiable white-label design system for Claude, distributed as a Claude Code
plugin marketplace.

Three workflows, and nothing else:

- **Generate** — one brand file produces a contrast-audited token set, a
  component stylesheet, a Tailwind theme and a proof sheet
- **Apply** — to a new project, or over an existing one, overriding whatever it
  had before
- **Enforce** — lint code for conformance and track drift over time

Most things called a design system do the first two. The third is the point:
consistency you can prove, not a style you have to trust.

## Install

In Claude Code:

```
/plugin marketplace add Fluxonius/claude-design-system
/plugin install design-system@fluxonius
```

Or install the skill directly, without the marketplace:

```bash
git clone https://github.com/Fluxonius/claude-design-system
cp -r claude-design-system/plugins/design-system/skills/design-system ~/.claude/skills/
```

For a single project, copy it to `.claude/skills/` instead so it is shared with
the repo.

## What it does

- **Generates tokens** from `brand.json` in OKLCH, and **fails the build** on any
  WCAG AA violation or fill/backdrop collision
- **Ships a real stylesheet** — 43 components, 133 class families, zero literal
  values, so swapping the token file re-brands everything
- **Adopts into existing projects** — rewrites hardcoded colours, spacing and
  radii to tokens, strips gradients and stray shadows, reports the class changes
- **Maps Tailwind onto the tokens** — utilities resolve to your scale, and
  off-system ones (`bg-violet-500`, `rounded-2xl`, `p-7`) stop existing
- **Lints for conformance** brand-relatively: `8px` is legal under the `soft`
  corner preset and a violation under `sharp`
- **Measures drift** over time and across projects, with a stored baseline

Full documentation: [`plugins/design-system/skills/design-system/README.md`](plugins/design-system/skills/design-system/README.md)

## Repository layout

```
.claude-plugin/marketplace.json          the marketplace catalog
plugins/design-system/
  .claude-plugin/plugin.json             the plugin manifest
  skills/design-system/                  the skill itself
    SKILL.md                             workflow and laws
    references/                          foundations + 43 component specs
    scripts/                             8 generators and linters
    assets/brand.template.json           the 8 personalization knobs
    evals/cases.md                        26 trigger test cases
```

## Status

**0.9.** Complete and usable, with two things worth knowing:

- The **trigger evals have not been run.** `evals/cases.md` holds 26 cases;
  running them needs Claude Code because the harness spawns subagents.
- The **component specs are the soft spot.** Around 28 defects surfaced the first
  time each component was actually rendered, all invisible to the linters
  because every value involved was a legal token. If something looks wrong,
  trust your eye over the spec and fix both.

Bug reports on rendered output are the most useful contribution.

## Releasing

`version` appears in both `marketplace.json` and `plugin.json`. Claude Code uses
the `plugin.json` value, so **bump both on every release** or existing users keep
the cached copy.

```bash
claude plugin validate .
```

## Licence

Apache-2.0. See [LICENSE](LICENSE).
