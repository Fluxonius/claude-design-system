#!/usr/bin/env python3
"""Emit a Tailwind theme that maps utilities onto this brand's tokens.

For a Tailwind project the right move is NOT to rewrite thousands of utility
classes. It is to redefine what those utilities mean, so `rounded-lg`, `p-4` and
`bg-surface` resolve to the system's tokens -- and so off-system utilities
(`rounded-2xl`, `p-7`, `bg-violet-500`, `shadow-lg`) stop existing at all.

That inverts the usual failure. Instead of a linter chasing every literal, the
build simply has no class for the wrong value.

Emits both formats:
  <prefix>-theme.css   Tailwind v4  (@theme block)
  tailwind.config.js   Tailwind v3  (theme.extend + corePlugins)

Usage:
    python3 build_tailwind_theme.py brand.json --out-dir .
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from build_tokens import build_tokens, load_brand  # noqa: E402

# Semantic colour utilities. Tailwind's own palette (violet-500, gray-200) is
# deliberately NOT reproduced: if `bg-violet-500` does not exist, it cannot be
# reached for. Only roles are available.
COLOUR_ROLES = [
    "bg", "surface", "surface-raised", "surface-sunken", "surface-hover",
    "surface-active", "control", "control-subtle", "control-hover",
    "control-active", "control-border", "ink", "ink-hover", "ink-active",
    "on-ink", "accent", "accent-hover", "accent-active", "accent-subtle",
    "accent-muted", "accent-border", "accent-text", "on-accent",
    "text", "text-muted", "text-subtle", "text-inverse",
    "border", "border-subtle", "border-strong", "focus-ring", "overlay",
    "tooltip-bg", "tooltip-text",
]
STATUS = ["danger", "success", "warning", "info"]
STATUS_SUFFIX = ["subtle", "muted", "border", "solid", "text"]

# Tailwind spacing keys -> px. Restricted to the system's scale: `p-7` and `p-9`
# simply do not exist, so they cannot be used.
SPACING = {
    "0": 0, "px": 1, "0.5": 2, "1": 4, "1.5": 6, "2": 8, "3": 12, "4": 16,
    "5": 20, "6": 24, "8": 32, "10": 40, "12": 48, "16": 64, "20": 80, "24": 96,
}
RADIUS = {"none": "radius-none", "sm": "radius-sm", "DEFAULT": "radius-md",
          "md": "radius-md", "lg": "radius-lg", "xl": "radius-xl",
          "full": "radius-full"}
FONT_SIZE = {"xs": "font-size-2xs", "sm": "font-size-sm", "base": "font-size-base",
             "lg": "font-size-lg", "xl": "font-size-xl", "2xl": "font-size-2xl",
             "3xl": "font-size-3xl", "4xl": "font-size-4xl"}
DURATION = {"0": "duration-instant", "fast": "duration-fast",
            "DEFAULT": "duration-base", "base": "duration-base",
            "slow": "duration-slow"}
Z = ["base", "sticky", "overlay", "modal", "toast", "tooltip"]


def colour_names(tokens):
    names = list(COLOUR_ROLES)
    for s in STATUS:
        names.append(s)
        names += [f"{s}-{x}" for x in STATUS_SUFFIX]
        names.append(f"on-{s}")
    return [n for n in names if n in tokens["light"]]


def v4_theme(p: str, tokens) -> str:
    L = [
        f"/* {p}-theme.css -- Tailwind v4 theme mapped onto the design system.",
        " *",
        " * Import AFTER tokens.css and AFTER tailwindcss:",
        " *     @import \"tailwindcss\";",
        f" *     @import \"./tokens.css\";",
        f" *     @import \"./{p}-theme.css\";",
        " *",
        " * Two things this does that a linter cannot:",
        " *   1. Utilities resolve to tokens, so `p-4` and `rounded-lg` are the",
        " *      system's values, and swapping tokens.css re-brands everything.",
        " *   2. Off-system utilities cease to exist. There is no `bg-violet-500`,",
        " *      no `rounded-2xl`, no `p-7`, no `shadow-lg` -- so they cannot be",
        " *      typed by accident, by a model, or by a hurried teammate.",
        " *",
        " * GENERATED FILE. Edit brand.json and re-run build_tailwind_theme.py.",
        " */",
        "",
        "@theme {",
        "  /* Clear Tailwind's defaults so only system values remain. */",
        "  --color-*: initial;",
        "  --spacing-*: initial;",
        "  --radius-*: initial;",
        "  --text-*: initial;",
        "  --shadow-*: initial;",
        "  --font-*: initial;",
        "  --z-index-*: initial;",
        "",
        "  /* fonts */",
        f"  --font-sans: var(--{p}-font-text);",
        f"  --font-display: var(--{p}-font-display);",
        f"  --font-mono: var(--{p}-font-mono);",
        "",
        "  /* colours -- roles only, no raw palette */",
    ]
    for n in colour_names(tokens):
        L.append(f"  --color-{n}: var(--{p}-{n});")
    L += ["", "  /* spacing -- the system's scale, nothing between */"]
    for k, px in SPACING.items():
        tok = "space-0" if px == 0 else ("space-px" if px == 1 else f"space-{px}")
        key = k.replace(".", "\\.")
        L.append(f"  --spacing-{key}: var(--{p}-{tok});")
    L += ["", "  /* radius -- derived from the corner preset */"]
    for k, tok in RADIUS.items():
        if k == "DEFAULT":
            continue
        L.append(f"  --radius-{k}: var(--{p}-{tok});")
    L += ["", "  /* type ladder */"]
    for k, tok in FONT_SIZE.items():
        L.append(f"  --text-{k}: var(--{p}-{tok});")
    L += ["", "  /* the only two shadows in the system, both for overlays */",
          f"  --shadow-sm: var(--{p}-shadow-sm);",
          f"  --shadow-md: var(--{p}-shadow-md);",
          "  --shadow-none: none;",
          "", "  /* motion ladder */"]
    for k, tok in DURATION.items():
        if k == "DEFAULT":
            continue
        L.append(f"  --duration-{k}: var(--{p}-{tok});")
    L += ["", "  /* stacking layers */"]
    for k in Z:
        L.append(f"  --z-index-{k}: var(--{p}-z-{k});")
    L += ["}", "",
          "/* Gradients are not part of this system. Neutralising the utilities",
          "   means `bg-gradient-to-r from-x to-y` renders nothing rather than",
          "   silently working. */",
          "@utility bg-gradient-* { background-image: none; }",
          ""]
    return "\n".join(L)


def v3_config(p: str, tokens) -> str:
    colours = {n: f"var(--{p}-{n})" for n in colour_names(tokens)}
    spacing = {k: f"var(--{p}-" + ("space-0" if v == 0 else
                                   ("space-px" if v == 1 else f"space-{v}")) + ")"
               for k, v in SPACING.items()}
    radius = {k: f"var(--{p}-{t})" for k, t in RADIUS.items()}
    fs = {k: f"var(--{p}-{t})" for k, t in FONT_SIZE.items()}
    dur = {k: f"var(--{p}-{t})" for k, t in DURATION.items()}
    z = {k: f"var(--{p}-z-{k})" for k in Z}
    cfg = {
        "theme": {
            "colors": colours,
            "spacing": spacing,
            "borderRadius": radius,
            "fontSize": fs,
            "boxShadow": {"sm": f"var(--{p}-shadow-sm)",
                          "md": f"var(--{p}-shadow-md)", "none": "none"},
            "transitionDuration": dur,
            "zIndex": z,
            "fontFamily": {
                "sans": [f"var(--{p}-font-text)"],
                "display": [f"var(--{p}-font-display)"],
                "mono": [f"var(--{p}-font-mono)"],
            },
        },
        "corePlugins": {
            "backgroundImage": False,
            "gradientColorStops": False,
            "backdropBlur": False,
            "backdropFilter": False,
        },
    }
    body = json.dumps(cfg, indent=2)
    return (
        "// tailwind.config.js -- generated from brand.json.\n"
        "//\n"
        "// `theme` REPLACES Tailwind's defaults rather than extending them, which\n"
        "// is the point: off-system utilities stop existing. There is no\n"
        "// bg-violet-500, no rounded-2xl, no p-7, no shadow-lg.\n"
        "//\n"
        "// Gradients and backdrop blur are switched off at the plugin level.\n"
        "//\n"
        "// GENERATED FILE. Edit brand.json and re-run build_tailwind_theme.py.\n"
        f"module.exports = {body};\n"
    )


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("brand")
    ap.add_argument("--out-dir", default=".")
    args = ap.parse_args(argv)

    brand = load_brand(args.brand)
    tokens = build_tokens(brand)
    p = brand.get("prefix", "ds")
    out = Path(args.out_dir)
    out.mkdir(parents=True, exist_ok=True)

    css = out / f"{p}-theme.css"
    js = out / "tailwind.config.js"
    css.write_text(v4_theme(p, tokens))
    js.write_text(v3_config(p, tokens))

    n = len(colour_names(tokens))
    print(f"Wrote {css}  (Tailwind v4 @theme)")
    print(f"Wrote {js}  (Tailwind v3 config)")
    print(f"  {n} colour roles, {len(SPACING)} spacing steps, "
          f"{len(RADIUS) - 1} radii, {len(FONT_SIZE)} type steps")
    print("  Tailwind's default palette, extra radii, extra spacing and extra")
    print("  shadows are REMOVED, not extended -- off-system utilities no longer exist.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
