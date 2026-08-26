#!/usr/bin/env python3
"""Detect CSS class names claimed by two unrelated rule blocks.

This has now caused three separate visual bugs, each invisible in code review
because nothing errors -- the cascade simply reassigns:

  .sw    swatch cell      vs  Switch component     -> swatches rendered as pills
  .chip  ramp colour block vs Chip component        -> ramps rendered as pills
  .hd    page header      vs  Accordion header      -> 32px margin under every row

The pattern is always the same: a short scaffolding class collides with a
component class, and the component rule wins for the properties it sets while
the scaffolding rule still contributes everything it does NOT set.

A class is flagged when it is defined both bare (`.x{...}`) and descendant-scoped
(`.parent .x{...}`), which is the exact shape of all three bugs above.

Usage:  python3 lint_css_collisions.py <file.css|file.html|file.py> [...]
"""
import re
import sys
from pathlib import Path

RULE = re.compile(r'(?m)^([^\n{]*?)\{([^}]*)\}')

# Properties that silently reshape layout when they leak from a bare rule into a
# scoped context. `margin-bottom: 32px` leaking from a page-header rule into an
# accordion header is what put 32px of dead space under every row.
LEAKY = ("margin", "padding", "height", "width", "display", "position",
         "line-height", "gap", "border")


def props(block: str):
    out = {}
    for decl in block.split(";"):
        if ":" in decl:
            k, v = decl.split(":", 1)
            out[k.strip()] = v.strip()
    return out


def main(argv):
    total = 0
    for a in argv:
        p = Path(a)
        text = p.read_text(errors="replace")
        bare, scoped = {}, {}
        for m in RULE.finditer(text):
            sel, block = m.group(1).strip(), m.group(2)
            for part in sel.split(","):
                part = part.strip()
                mb = re.fullmatch(r'\.([a-zA-Z][\w-]*)(?:[.:][\w()-]+)*', part)
                ms = re.fullmatch(r'\.[\w-]+(?:[.:][\w-]+)*\s+\.([a-zA-Z][\w-]*)(?:[.:][\w()-]+)*', part)
                if mb:
                    bare.setdefault(mb.group(1), {}).update(props(block))
                elif ms:
                    scoped.setdefault(ms.group(1), {}).update(props(block))

        hits = []
        for name in sorted(set(bare) & set(scoped)):
            leaked = {k: v for k, v in bare[name].items()
                      if k not in scoped[name] and k.startswith(LEAKY)}
            if leaked:
                hits.append((name, leaked))
        if not hits:
            continue
        print(f"\n{p}")
        for name, leaked in hits:
            print(f"  .{name} -- bare rule leaks into every scoped use:")
            for k, v in sorted(leaked.items()):
                print(f"       {k}: {v}")
        total += len(hits)
    print(f"\n{total} class(es) leaking layout properties into a scoped context.")
    print("Each is either intentional composition or a silent bug -- check the")
    print("leaked properties above. Fix by namespacing the scaffolding class.")
    return 1 if total else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:] or ["."]))
