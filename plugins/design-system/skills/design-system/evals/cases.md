# Trigger evals

The one thing that cannot be tested from a chat session: **does the skill
actually fire, and does it then read the right files?** `skill-creator`'s
harness spawns subagents, so run this in Claude Code.

```bash
# from the skill-creator directory
python3 scripts/run_eval.py --skill ../design-system --cases ../design-system/evals/cases.md
```

Two things to measure per case:

1. **Triggered?** Did the skill load at all.
2. **Right files?** Did it read `components-core.md` plus *one* group file, or
   pull in all 2,984 reference lines. Loading everything is a pass on
   correctness and a failure on cost.

---

## Should trigger

| # | Prompt | Expected path |
|---|---|---|
| 1 | Build me a settings page with a form and tabs | core + form |
| 2 | I need a dashboard with some stat cards | core + layout |
| 3 | Make me a data table with sorting and bulk actions | core + data |
| 4 | Style this button component | core |
| 5 | Set up a design system for my app | brand setup → tokens → proof sheet |
| 6 | My UI looks like every other AI-generated app, fix it | anti-patterns + core |
| 7 | Apply the design system to this project | **migrate.py** path |
| 8 | Make my old project's styling consistent | migrate + drift |
| 9 | Migrate these hardcoded colours to tokens | migrate |
| 10 | Set up my Tailwind theme | build_tailwind_theme.py |
| 11 | Check whether this UI is consistent | lint_conformance.py |
| 12 | How much has my styling drifted since last quarter? | check_drift.py |
| 13 | Is this palette accessible? | build_tokens.py --check |
| 14 | Add dark mode | tokens, both themes |
| 15 | Make the UI more compact | `density` knob, not ad-hoc padding |
| 16 | I want rounded corners everywhere | `radius` knob |
| 17 | Build a kanban board | should **ask** — no rule for it |
| 18 | Add a split button next to Save | should **ask**, then foundations' new-component section |
| 19 | Regenerate the tokens, I changed the brand colour | build_tokens.py |
| 20 | Build a landing page hero | core + layout |

Every **building** case above now opens with the brand gate when the project has
no `brand.json`: ask house-defaults-or-customize, write the brand file, then
build. Cases 11-13 are the control group — they are read-only, so the gate must
stay silent.

## Brand gate

The gate is asked once per project, and only when the task will produce UI.
Getting this wrong in either direction is a failure: blocking an audit is as
bad as silently picking a brand for a build.

| # | Setup | Prompt | Expected |
|---|---|---|---|
| 27 | no `brand.json` | Build me a dashboard | **asks** default-vs-customize *before* any UI; writes `brand.json`; then builds |
| 28 | `brand.json` present | Build me a dashboard | **no question** — reads the file and builds |
| 29 | no `brand.json` | Is this palette accessible? | **no question** — read-only, runs `build_tokens.py --check` |
| 30 | no `brand.json` | Apply the design system to this project | **asks** — the retrofit path writes UI, so it needs a brand |

## Custom brand colour

| # | Prompt | Expected |
|---|---|---|
| 31 | Our brand colour is `#FFFF00` | accepted and adapted (accent `#777700`), audit passes, no warning |
| 32 | Our brand colour is `#808080` | accepted, warns that the accent is near-neutral, **exit 0** — not a hard failure |

## Table alignment

| # | Prompt | Expected |
|---|---|---|
| 33 | Build an invoices table with amounts | `ds-num` on the `th` **and** every `td` of the amount column |
| 34 | ...with an invoice-number column | invoice number stays **left** — it is an identifier, not a quantity |

Both are checkable without reading the output by eye: run
`lint_conformance.py` on the generated markup and look for
`table-column-alignment-split`.

## Should NOT trigger

| # | Prompt | Why |
|---|---|---|
| 21 | Write a function to parse this CSV | no UI |
| 22 | Design my Postgres schema for invoices | data modelling |
| 23 | Write the marketing copy for our pricing page | copy, no UI output |
| 24 | Why is my API returning 500? | backend |
| 25 | Explain what OKLCH is | knowledge question, no build |
| 26 | Set up CI for my repo | infrastructure |

## Cost check

For each triggering case, record how many reference lines were read. Targets:

- **Good:** `components-core.md` + one group file (~900–1,200 lines)
- **Acceptable:** core only, for a token or brand question (~700)
- **Failure:** all seven component files (~2,100+) for a single-component task

If cases 1–4 pull every group file, the reference index in `SKILL.md` needs to
be more directive — that is the fix, not trimming the specs.

## Known-weak cases

Worth watching specifically:

- **7, 8, 9** — the retrofit path was absent from the description until the last
  revision, so these are the least proven.
- **17, 18** — the correct behaviour is to *ask*, not to build. A skill that
  silently invents a kanban board and presents it as system-conformant is worse
  than one that declines.
- **25** — should not trigger, but "OKLCH" appears throughout the references and
  may pull it in.
