#!/usr/bin/env python3
"""Measure how far a codebase has drifted from its design system, over time.

`lint_conformance.py` answers "is this file legal right now" -- a gate. This
answers a different question: "how far has this product wandered, where, and is
it getting better or worse?"

That question is the one no single-generation tool addresses. A model can produce
a beautiful screen today and a subtly different one in three months; nothing in
the generate-review loop notices the divergence accumulating. This does.

What it adds over a linter:

  1. A conformance score and per-rule breakdown instead of a flat list
  2. Hotspots -- which directories and files hold the drift
  3. Nearest legal token for each off-system value, computed in OKLab for
     colours, so the report is actionable rather than just accusatory
  4. A baseline (`.ds-drift.json`) so the next run reports the DELTA:
     what got fixed, what regressed, what is new
  5. Multiple projects in one run, so a studio can see which product drifted

Usage:
    python3 check_drift.py --brand brand.json src/
    python3 check_drift.py --brand brand.json --save-baseline src/
    python3 check_drift.py --brand brand.json --compare src/
    python3 check_drift.py --projects app-a:brand-a.json app-b:brand-b.json
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from build_tokens import hex_to_rgb, rgb_to_oklab  # noqa: E402
from lint_conformance import EXTS, System, lint_file  # noqa: E402

BASELINE = ".ds-drift.json"

# How much each rule matters. Drift is not uniform: a typo'd token is a live
# defect, an off-scale margin is untidy. Weighting keeps the score honest.
SEVERITY = {
    "undefined-token": 5,
    "component-colour-override": 5,
    "inverted-surface": 5,
    "raised-hover-collision": 4,
    "radius-inherit": 4,
    "off-system-colour": 3,
    "off-system-radius": 3,
    "gradient": 3,
    "backdrop-blur": 3,
    "transition-all": 2,
    "off-ladder-font-size": 2,
    "off-scale-spacing": 1,
}

VALUE_IN_MSG = re.compile(r"^(#[0-9a-fA-F]{3,8})|^(\d+)px")


def nearest_colour(hex_value: str, sys_: System):
    """Closest palette colour in OKLab, with the token name that carries it."""
    try:
        target = rgb_to_oklab(hex_to_rgb(hex_value))
    except Exception:
        return None
    best, best_d = None, 1e9
    for group in ("light", "dark", "primitive"):
        for name, val in sys_.tokens.get(group, {}).items():
            if not (isinstance(val, str) and val.startswith("#")):
                continue
            try:
                lab = rgb_to_oklab(hex_to_rgb(val))
            except Exception:
                continue
            d = sum((a - b) ** 2 for a, b in zip(target, lab)) ** 0.5
            if d < best_d:
                best_d, best = d, (name, val, group)
    return (best[0], best[1], best[2], best_d) if best else None


def nearest_number(n: int, legal: set[int]):
    if not legal:
        return None
    return min(legal, key=lambda x: abs(x - n))


def suggest(rule: str, message: str, code: str, sys_: System):
    """Turn a violation into a remediation."""
    if rule == "off-system-colour":
        m = re.search(r"(#[0-9a-fA-F]{3,8})", message) or re.search(r"(#[0-9a-fA-F]{3,8})", code)
        if m:
            near = nearest_colour(m.group(1), sys_)
            if near:
                name, val, group, dist = near
                scope = "" if group == "primitive" else f" ({group})"
                # Flag when the nearest palette colour is nowhere near, so the
                # suggestion is not mistaken for an equivalent swap.
                far = "  [far -- may need a deliberate decision]" if dist > 0.10 else ""
                return f"nearest is --{sys_.prefix}-{name} = {val}{scope}{far}"
    if rule == "off-system-radius":
        m = re.search(r"(\d+)px", code)
        if m:
            legal = sys_.px_set(sys_.radii) - {9999}
            n = nearest_number(int(m.group(1)), legal)
            names = [k for k, v in sys_.tokens["dimension"].items()
                     if k.startswith("radius-") and v == f"{n}px"]
            tok = names[0] if names else f"{n}px"
            return f"nearest is --{sys_.prefix}-{tok} = {n}px"
    if rule == "off-scale-spacing":
        legal = sys_.px_set(sys_.spacing)
        parts = []
        for raw in re.findall(r"(\d+)px", code):
            n = nearest_number(int(raw), legal)
            names = [k for k, v in sys_.tokens["dimension"].items()
                     if k.startswith("space-") and v == f"{n}px"]
            tok = names[0] if names else f"{n}px"
            if int(raw) not in legal:
                parts.append(f"{raw}px -> --{sys_.prefix}-{tok} ({n}px)")
        if parts:
            return "; ".join(parts)
    if rule == "off-ladder-font-size":
        m = re.search(r"(\d+)px", code)
        if m:
            n = nearest_number(int(m.group(1)), sys_.px_set(sys_.font_sizes))
            names = [k for k, v in sys_.tokens["dimension"].items()
                     if k.startswith("font-size-") and v == f"{n}px"]
            tok = names[0] if names else f"{n}px"
            return f"nearest is --{sys_.prefix}-{tok} = {n}px"
    if rule == "undefined-token":
        m = re.search(r"--([\w-]+)", code)
        if m:
            bad = m.group(1)
            bare = bad[len(sys_.prefix) + 1:] if bad.startswith(sys_.prefix + "-") else bad
            best, best_d = None, 1e9
            for name in sys_.names:
                d = _edit(bare, name)
                if d < best_d:
                    best_d, best = d, name
            if best and best_d <= max(2, len(bare) // 3):
                return f"did you mean --{sys_.prefix}-{best}?"
    return None


def _edit(a: str, b: str) -> int:
    if abs(len(a) - len(b)) > 4:
        return 99
    prev = list(range(len(b) + 1))
    for i, ca in enumerate(a, 1):
        cur = [i]
        for j, cb in enumerate(b, 1):
            cur.append(min(prev[j] + 1, cur[j - 1] + 1, prev[j - 1] + (ca != cb)))
        prev = cur
    return prev[-1]


def scan(paths, sys_):
    targets = []
    for a in paths:
        p = Path(a)
        if p.is_dir():
            targets += [f for f in p.rglob("*")
                        if f.suffix in EXTS and "node_modules" not in f.parts]
        elif p.exists():
            targets.append(p)
    findings = []
    for f in targets:
        for line, rule, msg, code in lint_file(f, sys_):
            findings.append({"file": str(f), "line": line, "rule": rule,
                             "message": msg, "code": code})
    return targets, findings


def score(findings, n_files):
    """0-100, asymptotic so it never bottoms out.

    A linear penalty hits 0 on a badly drifted codebase and stays there, which
    makes the number useless for exactly the case this tool exists for -- you
    fix thirty things and the score still reads 0. This curve always leaves
    headroom, so any real improvement moves it.
    """
    if not n_files:
        return 100.0
    weighted = sum(SEVERITY.get(f["rule"], 1) for f in findings)
    per_file = weighted / n_files
    return round(100.0 / (1.0 + per_file / 6.0), 1)


def fingerprint(f):
    return f"{f['rule']}|{f['code']}"


def report(label, targets, findings, sys_, baseline=None, quiet=False):
    """Print the human report and return the score. `quiet` computes only."""
    n = len(targets)
    s = score(findings, n)
    if quiet:
        return s
    print(f"\n{'=' * 66}")
    print(f"{label}")
    print(f"{'=' * 66}")
    print(f"  files scanned      {n}")
    print(f"  violations         {len(findings)}")
    print(f"  conformance score  {s}/100")

    if baseline is not None:
        prev_s = baseline.get("score")
        prev = {fingerprint(f) for f in baseline.get("findings", [])}
        now = {fingerprint(f) for f in findings}
        fixed, new = prev - now, now - prev
        arrow = "→"
        if prev_s is not None:
            arrow = "improved" if s > prev_s else ("regressed" if s < prev_s else "unchanged")
            print(f"  since {baseline.get('at', '?')[:10]}   "
                  f"{prev_s} {arrow} {s}")
        print(f"  fixed since then   {len(fixed)}")
        print(f"  newly introduced   {len(new)}")
        if new:
            print("\n  NEW DRIFT")
            for fp in sorted(new)[:10]:
                rule, code = fp.split("|", 1)
                print(f"    {rule:<26} {code[:44]}")

    if not findings:
        print("\n  No drift. Every value in this codebase is in the system.")
        return s

    by_rule = Counter(f["rule"] for f in findings)
    print("\n  BY RULE")
    for rule, cnt in by_rule.most_common():
        print(f"    {cnt:>4}  {rule:<26} severity {SEVERITY.get(rule, 1)}")

    by_dir = Counter(str(Path(f["file"]).parent) for f in findings)
    print("\n  HOTSPOTS")
    for d, cnt in by_dir.most_common(6):
        print(f"    {cnt:>4}  {d}")

    print("\n  MOST COMMON OFF-SYSTEM VALUES")
    vals = Counter((f["rule"], f["code"]) for f in findings)
    for (rule, code), cnt in vals.most_common(8):
        fix = suggest(rule, "", code, sys_)
        msg = next((f["message"] for f in findings
                    if f["rule"] == rule and f["code"] == code), "")
        fix = fix or suggest(rule, msg, code, sys_)
        tail = f"   {fix}" if fix else ""
        print(f"    {cnt:>4}x  {code[:42]:<42}{tail}")
    return s


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("paths", nargs="*", default=["."])
    ap.add_argument("--brand")
    ap.add_argument("--save-baseline", action="store_true",
                    help=f"write {BASELINE} for later comparison")
    ap.add_argument("--compare", action="store_true",
                    help=f"compare against {BASELINE}")
    ap.add_argument("--projects", nargs="*", metavar="PATH:BRAND",
                    help="scan several projects: src-a:brand-a.json ...")
    ap.add_argument("--fail-under", type=float, default=None,
                    help="exit 1 if the score drops below this")
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args(argv)

    if args.projects:
        rows, out = [], {}
        for spec in args.projects:
            path, _, brand = spec.partition(":")
            sys_ = System(Path(brand) if brand else None)
            targets, findings = scan([path], sys_)
            s = report(f"{path}  (brand: {brand or 'house defaults'})",
                       targets, findings, sys_, quiet=args.json)
            rows.append((path, len(targets), len(findings), s))
            out[path] = {"files": len(targets), "violations": len(findings), "score": s}
        if args.json:
            print(json.dumps(out, indent=2))
            worst = min((r[3] for r in rows), default=100)
            return 1 if args.fail_under is not None and worst < args.fail_under else 0
        print(f"\n{'=' * 66}")
        print("PORTFOLIO")
        print(f"{'=' * 66}")
        print(f"  {'project':<28}{'files':>7}{'issues':>8}{'score':>8}")
        for path, nf, nv, s in sorted(rows, key=lambda r: r[3]):
            flag = "  <-- most drifted" if s == min(r[3] for r in rows) and len(rows) > 1 else ""
            print(f"  {path[:28]:<28}{nf:>7}{nv:>8}{s:>8}{flag}")
        worst = min((r[3] for r in rows), default=100)
        return 1 if args.fail_under is not None and worst < args.fail_under else 0

    brand_path = Path(args.brand) if args.brand else (
        Path("brand.json") if Path("brand.json").exists() else None)
    sys_ = System(brand_path)
    targets, findings = scan(args.paths or ["."], sys_)

    baseline = None
    if args.compare and Path(BASELINE).exists():
        baseline = json.loads(Path(BASELINE).read_text())
    elif args.compare:
        print(f"No {BASELINE} found -- run with --save-baseline first.")

    s = report(f"DRIFT REPORT  (brand: {brand_path or 'house defaults'})",
               targets, findings, sys_, baseline, quiet=args.json)

    if args.save_baseline:
        Path(BASELINE).write_text(json.dumps({
            "at": datetime.now(timezone.utc).isoformat(),
            "brand": str(brand_path), "score": s,
            "findings": findings}, indent=2))
        print(f"\n  baseline written to {BASELINE}")

    if args.json:
        print(json.dumps({"score": s, "violations": len(findings),
                          "files": len(targets), "findings": findings}, indent=2))

    if args.fail_under is not None and s < args.fail_under:
        print(f"\n  score {s} is below --fail-under {args.fail_under}")
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
