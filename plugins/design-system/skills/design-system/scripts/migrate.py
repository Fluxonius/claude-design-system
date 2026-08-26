#!/usr/bin/env python3
"""Convert an existing project TO the design system.

This is the override path. The system does not adapt to the project's existing
look -- it replaces it, so a codebase from six months ago ends up
indistinguishable from one started today under the same brand.

Three passes, in increasing need for judgement:

  PASS 1  Mechanical value substitution. Every off-system colour, radius,
          spacing and font size is rewritten to the nearest token. Safe and
          reversible; this is the bulk of the work.

  PASS 2  Banned-pattern removal. Gradients, backdrop-filter, `transition: all`
          and shadows on cards are deleted or replaced with the system's
          position, because no token substitution can fix them.

  PASS 3  Component mapping, REPORTED not applied. The project's own component
          classes (`.my-button`, `.primary-btn`) are matched against the
          system's classes and listed with a suggested replacement. Rewriting
          markup needs to preserve semantics, so this is where a human or Claude
          decides -- the report tells you exactly what to change and to what.

Nothing is written without `--write`, and `--backup` keeps originals.

Usage:
    python3 migrate.py --brand brand.json src/                # dry run
    python3 migrate.py --brand brand.json src/ --write --backup
    python3 migrate.py --brand brand.json src/ --report-only  # pass 3 only
"""
from __future__ import annotations

import argparse
import re
import shutil
import sys
from collections import Counter, defaultdict
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from build_tokens import hex_to_rgb, load_brand, rgb_to_oklab, build_tokens  # noqa: E402
from lint_conformance import EXTS, System  # noqa: E402

# Project class name fragment -> system class. Ordered: first match wins, so
# more specific patterns come first.
CLASS_MAP = [
    (r"icon[-_]?btn|btn[-_]?icon|icon[-_]?button", "{p}-btn {p}-iconbtn {p}-btn--ghost {p}-btn--neutral"),
    (r"btn[-_]?(primary|cta)|primary[-_]?(btn|button)", "{p}-btn {p}-btn--filled {p}-btn--neutral"),
    (r"btn[-_]?(danger|destructive|delete)|danger[-_]?(btn|button)", "{p}-btn {p}-btn--filled {p}-btn--destructive"),
    (r"btn[-_]?(secondary|outline)|secondary[-_]?(btn|button)", "{p}-btn {p}-btn--outline {p}-btn--neutral"),
    (r"btn[-_]?(ghost|text|link)", "{p}-btn {p}-btn--ghost {p}-btn--neutral"),
    (r"\bbtn\b|\bbutton\b", "{p}-btn {p}-btn--filled {p}-btn--neutral"),
    (r"text[-_]?(field|input)|\binput\b|form[-_]?control", "{p}-input"),
    (r"\btextarea\b", "{p}-textarea"),
    (r"\bselect\b|dropdown[-_]?select", "{p}-select"),
    (r"\bcheckbox\b", "{p}-check"),
    (r"\bradio\b", "{p}-radio"),
    (r"\bswitch\b|\btoggle\b", "{p}-switch"),
    (r"\bcard\b|panel|tile", "{p}-card"),
    (r"\bbadge\b|\btag\b|pill|label[-_]?chip", "{p}-badge"),
    (r"\bchip\b|filter[-_]?chip", "{p}-chip"),
    (r"\balert\b|\bbanner\b|notice|callout|flash", "{p}-alert"),
    (r"\btable\b|data[-_]?grid", "{p}-table"),
    (r"\btabs?\b(?!.*panel)", "{p}-tab"),
    (r"segmented|button[-_]?group", "{p}-segmented"),
    (r"\bmenu[-_]?item\b|dropdown[-_]?item", "{p}-menu-item"),
    (r"\bmenu\b|dropdown(?![-_]?item)", "{p}-menu"),
    (r"\btooltip\b|\btip\b", "{p}-tooltip"),
    (r"\bmodal\b|\bdialog\b", "{p}-modal"),
    (r"\btoast\b|snackbar", "{p}-toast"),
    (r"\bavatar\b|\bprofile[-_]?pic", "{p}-avatar"),
    (r"accordion|collapsible|disclosure", "{p}-accordion"),
    (r"\bprogress\b|progress[-_]?bar", "{p}-progress"),
    (r"\bskeleton\b|\bshimmer\b|placeholder[-_]?loading", "{p}-skeleton"),
    (r"\bdivider\b|\bseparator\b|\bhr\b", "{p}-divider"),
    (r"empty[-_]?state|no[-_]?results", "{p}-empty"),
    (r"popover", "{p}-popover"),
]

COLOUR_PROP = re.compile(
    r"((?:background|border|outline|fill|stroke|color)[\w-]*\s*:\s*)([^;}\"'\n]+)", re.I)
HEX = re.compile(r"#[0-9a-fA-F]{3,8}\b")
RGB = re.compile(r"rgba?\(\s*(\d+)\s*,\s*(\d+)\s*,\s*(\d+)\s*(?:,\s*[\d.]+\s*)?\)", re.I)
RADIUS_DECL = re.compile(r"(border-radius\s*:\s*)([^;}\"'\n]+)", re.I)
BOX_DECL = re.compile(r"((?:padding|margin|gap|row-gap|column-gap)[\w-]*\s*:\s*)([^;}\"'\n]+)", re.I)
FS_DECL = re.compile(r"(font-size\s*:\s*)([^;}\"'\n]+)", re.I)
PXV = re.compile(r"\b(\d+(?:\.\d+)?)px\b")

GRADIENT = re.compile(r"(?:linear|radial|conic)-gradient\([^;}]*\)", re.I)
BLUR = re.compile(r"backdrop-filter\s*:(?!\s*none\b)\s*[^;}\n]+;?", re.I)
TRANS_ALL = re.compile(r"transition\s*:\s*all\b([^;}\n]*);?", re.I)
RADIUS_INHERIT = re.compile(r"border-radius\s*:\s*inherit\s*;?", re.I)
CLASS_ATTR = re.compile(r"class(?:Name)?\s*=\s*[\"']([^\"']+)[\"']")
CLASS_ATTR_RX = re.compile(r'class(?:Name)?\s*=\s*"([^"]*)"')


class Migrator:
    def __init__(self, sys_: System):
        self.s = sys_
        self.p = sys_.prefix
        # Many tokens share a hex -- white is on-accent, on-ink, on-success and
        # surface all at once. Picking arbitrarily produced `background: #fff`
        # -> `var(--ds-on-success)`. So candidates are kept per hex and chosen
        # by the PROPERTY being rewritten.
        self._cand = {}
        for group in ("light", "dark", "primitive"):
            for name, val in sys_.tokens.get(group, {}).items():
                if isinstance(val, str) and val.startswith("#"):
                    try:
                        lab = rgb_to_oklab(hex_to_rgb(val))
                    except Exception:
                        continue
                    self._cand.setdefault(val.lower(), (set(), lab))[0].add(name)
        self.all_names = set()
        for group in ("light", "dark"):
            self.all_names |= set(sys_.tokens.get(group, {}))
        self.dim = sys_.tokens["dimension"]
        self.radius_px = {int(v[:-2]): k for k, v in self.dim.items()
                          if k.startswith("radius-") and v.endswith("px") and v[:-2].isdigit()}
        self.space_px = {int(v[:-2]): k for k, v in self.dim.items()
                         if k.startswith("space-") and v.endswith("px") and v[:-2].isdigit()}
        self.fs_px = {int(v[:-2]): k for k, v in self.dim.items()
                      if k.startswith("font-size-") and v.endswith("px") and v[:-2].isdigit()}

    # Which SEMANTIC roles are legal for each CSS property family, in priority
    # order. Two separate bugs came from ignoring this:
    #   background: #fff -> var(--ds-on-ink)      (a FOREGROUND role)
    #   background: #dcfce7 -> var(--ds-success-150)  (a PRIMITIVE, not a role)
    # Primitives (neutral-200, accent-500, success-150) are excluded entirely:
    # a migrated project should speak in roles, not ramp steps.
    PREF = {
        "background": ("surface", "bg", "control", "overlay",
                       "accent-subtle", "accent-muted", "accent", "ink",
                       "danger-subtle", "success-subtle", "warning-subtle",
                       "info-subtle", "danger-solid", "success-solid",
                       "warning-solid", "info-solid", "tooltip-bg"),
        "color":      ("text", "on-", "accent-text", "danger-text",
                       "success-text", "warning-text", "info-text",
                       "tooltip-text"),
        "border":     ("border", "control-border", "accent-border",
                       "danger-border", "success-border", "warning-border",
                       "info-border"),
        "outline":    ("focus-ring", "border-strong", "border", "accent"),
        "fill":       ("text", "accent", "on-"),
        "stroke":     ("text", "border", "accent"),
    }
    PRIMITIVE = re.compile(r"-(?:\d{2,4})$")

    def _family(self, prop):
        prop = prop.lower().split(":")[0].strip()
        return next((k for k in self.PREF if prop.startswith(k)), None)

    def _allowed(self, prop):
        """Semantic roles legal for this property, best first."""
        fam = self._family(prop)
        if not fam:
            return None
        order = self.PREF[fam]
        out = []
        for pfx in order:
            for n in sorted(self.all_names):
                if n.startswith(pfx) and not self.PRIMITIVE.search(n) and n not in out:
                    out.append(n)
        return out or None

    def _prefer(self, names, prop):
        allowed = self._allowed(prop)
        if allowed:
            for n in allowed:
                if n in names:
                    return n
        non_prim = [n for n in names if not self.PRIMITIVE.search(n)]
        pool = non_prim or list(names)
        return sorted(pool, key=lambda n: (len(n), n))[0]

    # ---------- pass 1: value substitution ----------
    def token_for_colour(self, hexv: str, prop: str = "background"):
        try:
            target = rgb_to_oklab(hex_to_rgb(hexv))
        except Exception:
            return None, None
        allowed = self._allowed(prop)
        best, best_d = None, 1e9
        for val, (names, lab) in self._cand.items():
            pool = [n for n in names if allowed is None or n in allowed]
            if not pool:
                continue
            d = sum((a - b) ** 2 for a, b in zip(target, lab)) ** 0.5
            if d < best_d:
                best_d, best = d, self._prefer(set(pool), prop)
        return best, best_d

    def nearest(self, n: int, table: dict):
        if not table:
            return None, None
        k = min(table, key=lambda x: abs(x - n))
        return table[k], k

    def sub_colours(self, text, log):
        def repl(m):
            prop, value = m.group(1), m.group(2)
            if "var(" in value:
                return m.group(0)
            new = value
            for hm in HEX.finditer(value):
                hexv = hm.group(0).lower()
                allowed = self._allowed(prop)
                exact = self._cand.get(hexv, (set(), None))[0]
                usable = [n for n in exact if allowed is None or n in allowed]
                if usable:
                    tok = self._prefer(set(usable), prop)
                    new = new.replace(hm.group(0), f"var(--{self.p}-{tok})")
                    log["colour-exact"] += 1
                    continue
                tok, dist = self.token_for_colour(hexv, prop)
                if tok:
                    new = new.replace(hm.group(0), f"var(--{self.p}-{tok})")
                    log["colour-nearest" if dist and dist > 0.10 else "colour-close"] += 1
            for rm in RGB.finditer(new):
                hexv = "#%02x%02x%02x" % tuple(int(x) for x in rm.groups()[:3])
                tok, _ = self.token_for_colour(hexv, prop)
                if tok:
                    new = new.replace(rm.group(0), f"var(--{self.p}-{tok})")
                    log["colour-rgb"] += 1
            return prop + new
        return COLOUR_PROP.sub(repl, text)

    def _sub_px(self, text, decl_rx, table, log, key):
        def repl(m):
            prop, value = m.group(1), m.group(2)
            if "var(" in value:
                return m.group(0)
            new = value
            # A pill is a different SHAPE category, not a rounder rectangle.
            # 999px / 9999px / 50% must become radius-full, never snap to the
            # largest finite step (which turned a pill into a 16px rectangle).
            if key == "radius":
                if "%" in value or any(int(float(x)) >= 500 for x in PXV.findall(value)):
                    log["radius-pill"] += 1
                    return prop + f"var(--{self.p}-radius-full)"
            for pm in PXV.finditer(value):
                n = int(float(pm.group(1)))
                if n in table:
                    new = new.replace(pm.group(0), f"var(--{self.p}-{table[n]})")
                    log[key + "-exact"] += 1
                else:
                    tok, _ = self.nearest(n, table)
                    if tok:
                        new = new.replace(pm.group(0), f"var(--{self.p}-{tok})")
                        log[key + "-snapped"] += 1
            return prop + new
        return decl_rx.sub(repl, text)

    # ---------- pass 2: banned patterns ----------
    OVERLAY_SEL = re.compile(
        r"(modal|dialog|popover|menu|dropdown|toast|tooltip|drawer|sheet|overlay)",
        re.I)

    def strip_shadows(self, text, log):
        """Remove box-shadow except on overlay selectors.

        A shadow on a card is the single most reliable generated-UI tell, and no
        token substitution fixes it -- the declaration has to go. Overlays are
        the only place the system permits elevation, so shadows there are
        rewritten to the shadow tokens instead of deleted.
        """
        out, cur_sel = [], ""
        for line in text.splitlines(keepends=True):
            if "{" in line:
                cur_sel = line.split("{")[0]
            m = re.search(r"\s*box-shadow\s*:\s*(?!none\b)[^;}\n]+;?", line, re.I)
            if m:
                if self.OVERLAY_SEL.search(cur_sel):
                    line = line[:m.start()] + f" box-shadow: var(--{self.p}-shadow-md);" + line[m.end():]
                    log["shadow-tokenised"] += 1
                else:
                    line = line[:m.start()] + line[m.end():]
                    log["shadow-removed"] += 1
                    if not line.strip():
                        continue
            out.append(line)
        return "".join(out)

    def snap_durations(self, text, log):
        """Snap raw ms values to the duration ladder."""
        ladder = {int(v[:-2]): k for k, v in self.dim.items()
                  if k.startswith("duration-") and v.endswith("ms")}
        def repl(m):
            n = int(m.group(1))
            if n in ladder:
                log["duration-exact"] += 1
            else:
                log["duration-snapped"] += 1
            k = min(ladder, key=lambda x: abs(x - n))
            return f"var(--{self.p}-{ladder[k]})"
        return re.sub(r"\b(\d+)ms\b", repl, text)

    def strip_banned(self, text, log):
        def g(m):
            log["gradient-removed"] += 1
            return f"var(--{self.p}-surface)"
        text = GRADIENT.sub(g, text)
        n = len(BLUR.findall(text))
        if n:
            log["blur-removed"] += n
            text = BLUR.sub("backdrop-filter: none;", text)
        def ta(m):
            log["transition-all-narrowed"] += 1
            rest = m.group(1).strip() or f"var(--{self.p}-duration-fast)"
            return f"transition: opacity {rest}, transform {rest};"
        text = TRANS_ALL.sub(ta, text)
        n = len(RADIUS_INHERIT.findall(text))
        if n:
            log["radius-inherit-removed"] += n
            text = RADIUS_INHERIT.sub("", text)
        return text

    # ---------- pass 1b: Tailwind utility rewrites ----------
    # Tailwind encodes decisions in class names, so none of the CSS-declaration
    # passes touch it. These rewrites are safe and mechanical; anything needing
    # judgement is left for the report.
    TW_SUBS = [
        # raw palette -> the nearest ROLE. Neutrals become surface/text/border
        # depending on the utility prefix; chromatics become accent or status.
        (r"\bbg-(?:slate|gray|grey|zinc|neutral|stone)-(?:50|100)\b", "bg-surface"),
        (r"\bbg-(?:slate|gray|grey|zinc|neutral|stone)-(?:200|300)\b", "bg-control"),
        (r"\bbg-white\b", "bg-surface"),
        (r"\bbg-(?:slate|gray|grey|zinc|neutral|stone)-(?:800|900|950)\b", "bg-ink"),
        (r"\btext-(?:slate|gray|grey|zinc|neutral|stone)-(?:400|500)\b", "text-text-subtle"),
        (r"\btext-(?:slate|gray|grey|zinc|neutral|stone)-(?:600|700)\b", "text-text-muted"),
        (r"\btext-(?:slate|gray|grey|zinc|neutral|stone)-(?:800|900|950)\b", "text-text"),
        (r"\btext-white\b", "text-on-ink"),
        (r"\bborder-(?:slate|gray|grey|zinc|neutral|stone)-(?:100|200)\b", "border-border-subtle"),
        (r"\bborder-(?:slate|gray|grey|zinc|neutral|stone)-(?:300|400)\b", "border-border"),
        (r"\bborder-(?:slate|gray|grey|zinc|neutral|stone)-(?:500|600)\b", "border-border-strong"),
        (r"\bbg-(?:red|rose)-(?:50|100)\b", "bg-danger-subtle"),
        (r"\btext-(?:red|rose)-(?:600|700|800)\b", "text-danger-text"),
        (r"\bbg-(?:emerald|green)-(?:50|100)\b", "bg-success-subtle"),
        (r"\btext-(?:emerald|green)-(?:600|700|800)\b", "text-success-text"),
        (r"\bbg-(?:amber|yellow)-(?:50|100)\b", "bg-warning-subtle"),
        (r"\btext-(?:amber|yellow)-(?:600|700|800)\b", "text-warning-text"),
        (r"\bbg-(?:violet|purple|indigo|blue|sky|cyan|teal|fuchsia|pink)-(?:50|100)\b", "bg-accent-subtle"),
        (r"\bbg-(?:violet|purple|indigo|blue|sky|cyan|teal|fuchsia|pink)-(?:400|500|600|700)\b", "bg-accent"),
        (r"\btext-(?:violet|purple|indigo|blue|sky|cyan|teal|fuchsia|pink)-(?:500|600|700)\b", "text-accent-text"),
        # radii off the preset -> nearest available
        (r"\brounded-(?:2xl|3xl)\b", "rounded-lg"),
        # shadows: the system has two, both for overlays
        (r"\b(?:hover:)?shadow-(?:sm|md|lg|xl|2xl|inner|DEFAULT)\b", ""),
        # motion
        (r"\btransition-all\b", "transition-colors"),
        # hover-lift / scale
        (r"\bhover:-?translate-[xy]-[\w.]+\b", ""),
        (r"\bhover:scale-[\w.]+\b", ""),
        # off-scale spacing -> nearest legal step
        (r"\b([pm][xytrbles]?)-7\b", r"\1-6"),
        (r"\b([pm][xytrbles]?)-9\b", r"\1-8"),
        (r"\b([pm][xytrbles]?)-11\b", r"\1-10"),
        (r"\b([pm][xytrbles]?)-14\b", r"\1-12"),
        (r"\bgap-7\b", "gap-6"),
        (r"\bgap-9\b", "gap-8"),
        # the system caps UI weights at 600; bold/extrabold/black are off-system
        (r"\bfont-(?:bold|extrabold|black)\b", "font-semibold"),
        (r"\bfont-(?:thin|extralight|light)\b", "font-normal"),
        # type ladder stops at 4xl
        (r"\btext-(?:5xl|6xl|7xl|8xl|9xl)\b", "text-4xl"),
        # blur is not in the system
        (r"\b(?:hover:)?backdrop-(?:blur|filter)(?:-[\w.]+)?\b", ""),
    ]
    TW_GRADIENT = re.compile(
        r"\b(?:bg-gradient-to-\w+|bg-linear-to-\w+|"
        r"(?:from|via|to)-[\w-]+(?:/\d+)?)\b")

    def rewrite_tailwind(self, text, log):
        def fix(m):
            classes = m.group(1)
            before = classes
            if self.TW_GRADIENT.search(classes):
                classes = self.TW_GRADIENT.sub("", classes)
                # A gradient with light text on it was a filled action, so it
                # becomes `ink`. Replacing it with `surface` would put white
                # text on a white background.
                light_text = re.search(r"\btext-(?:white|on-ink|on-accent)\b", classes)
                classes += " bg-ink" if light_text else " bg-surface"
                log["tw-gradient-removed"] += 1
            # Arbitrary values -- `p-[13px]`, `rounded-[7px]`, `bg-[#7c3aed]`.
            # Snapped to the nearest token rather than left in place, since an
            # arbitrary value is precisely what the system exists to prevent.
            def snap_arbitrary(cm):
                util, val = cm.group(1), cm.group(2)
                if val.startswith("#"):
                    prop = ("background" if util.startswith("bg") else
                            "color" if util.startswith("text") else
                            "border" if util.startswith("border") else "background")
                    tok, _ = self.token_for_colour(val, prop)
                    if tok:
                        log["tw-arbitrary-snapped"] += 1
                        return f"{util}-{tok}"
                m2 = re.fullmatch(r"(\d+)px", val)
                if m2:
                    n = int(m2.group(1))
                    if util.startswith("rounded"):
                        table = {int(v[:-2]): k.replace("radius-", "")
                                 for k, v in self.dim.items()
                                 if k.startswith("radius-") and v.endswith("px")
                                 and v[:-2].isdigit() and int(v[:-2]) < 500}
                        if table:
                            k = min(table, key=lambda x: abs(x - n))
                            log["tw-arbitrary-snapped"] += 1
                            return f"{util}-{table[k]}"
                    else:
                        legal = {0: "0", 1: "px", 2: "0.5", 4: "1", 6: "1.5",
                                 8: "2", 12: "3", 16: "4", 20: "5", 24: "6",
                                 32: "8", 40: "10", 48: "12", 64: "16",
                                 80: "20", 96: "24"}
                        k = min(legal, key=lambda x: abs(x - n))
                        log["tw-arbitrary-snapped"] += 1
                        return f"{util}-{legal[k]}"
                return cm.group(0)

            classes = re.sub(r"\b([a-z][\w-]*?)-\[([^\]]+)\]", snap_arbitrary, classes)

            for pat, repl in self.TW_SUBS:
                new = re.sub(pat, repl, classes)
                if new != classes:
                    key = ("tw-shadow-removed" if "shadow" in pat
                           else "tw-hover-transform-removed" if "hover:" in pat
                           else "tw-utility-remapped")
                    log[key] += len(re.findall(pat, classes))
                    classes = new
            classes = " ".join(classes.split())
            if classes == before:
                return m.group(0)
            return m.group(0).replace(before, classes)
        return CLASS_ATTR_RX.sub(fix, text)

    # ---------- pass 3: component class mapping (report only) ----------
    def map_classes(self, text):
        found = []
        for m in CLASS_ATTR.finditer(text):
            for cls in m.group(1).split():
                if cls.startswith(self.p + "-"):
                    continue
                for pattern, target in CLASS_MAP:
                    if re.search(pattern, cls, re.I):
                        found.append((cls, target.format(p=self.p)))
                        break
        return found


def migrate_file(path: Path, mig: Migrator, write: bool, backup: bool):
    original = path.read_text(errors="replace")
    log = Counter()
    text = original

    text = mig.rewrite_tailwind(text, log)
    text = mig.strip_banned(text, log)
    text = mig.strip_shadows(text, log)
    text = mig.snap_durations(text, log)
    text = mig.sub_colours(text, log)
    text = mig._sub_px(text, RADIUS_DECL, mig.radius_px, log, "radius")
    text = mig._sub_px(text, BOX_DECL, mig.space_px, log, "space")
    text = mig._sub_px(text, FS_DECL, mig.fs_px, log, "font-size")

    mappings = mig.map_classes(original)
    changed = text != original
    if changed and write:
        if backup:
            shutil.copy2(path, path.with_suffix(path.suffix + ".pre-ds"))
        path.write_text(text)
    return log, mappings, changed


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("paths", nargs="*", default=["."])
    ap.add_argument("--brand")
    ap.add_argument("--write", action="store_true", help="apply changes (default: dry run)")
    ap.add_argument("--backup", action="store_true", help="keep *.pre-ds originals")
    ap.add_argument("--report-only", action="store_true", help="pass 3 only, change nothing")
    args = ap.parse_args(argv)

    brand_path = Path(args.brand) if args.brand else (
        Path("brand.json") if Path("brand.json").exists() else None)
    sys_ = System(brand_path)
    mig = Migrator(sys_)

    targets = []
    for a in args.paths or ["."]:
        p = Path(a)
        if p.is_dir():
            targets += [f for f in p.rglob("*")
                        if f.suffix in EXTS and "node_modules" not in f.parts
                        and not f.name.endswith(".pre-ds")
                        and not f.name.startswith(sys_.prefix + "-")
                        and f.name not in ("tokens.css",)]
        elif p.exists():
            targets.append(p)

    total = Counter()
    all_maps = defaultdict(set)
    touched = []
    for f in targets:
        if args.report_only:
            for cls, target in mig.map_classes(f.read_text(errors="replace")):
                all_maps[cls].add(target)
            continue
        log, mappings, changed = migrate_file(f, mig, args.write, args.backup)
        total.update(log)
        for cls, target in mappings:
            all_maps[cls].add(target)
        if changed:
            touched.append(f)

    mode = "APPLIED" if args.write else ("REPORT" if args.report_only else "DRY RUN")
    print(f"\n{'=' * 68}")
    print(f"MIGRATION -- {mode}   brand: {brand_path or 'house defaults'}")
    print(f"{'=' * 68}")
    print(f"  files examined   {len(targets)}")

    if not args.report_only:
        print(f"  files changed    {len(touched)}")
        print("\n  PASS 1+2  automatic rewrites")
        if total:
            for k in sorted(total):
                print(f"    {total[k]:>5}  {k}")
        else:
            print("     nothing to rewrite -- already on the system")

    if all_maps:
        print("\n  PASS 3  component classes to replace  (NOT applied -- needs judgement)")
        print("          markup rewrites must preserve semantics, so these are")
        print("          listed for you or Claude to apply deliberately.\n")
        for cls in sorted(all_maps):
            for target in sorted(all_maps[cls]):
                print(f"    .{cls:<28} ->  {target}")

    if not args.write and not args.report_only and touched:
        print(f"\n  Dry run. Re-run with --write --backup to apply.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
