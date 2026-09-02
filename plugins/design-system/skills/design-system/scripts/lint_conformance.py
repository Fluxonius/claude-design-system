#!/usr/bin/env python3
"""Check UI code for conformance to THIS project's generated design system.

The difference from a generic design linter matters. A general tool can only
check universal anti-patterns -- no purple gradients, no glassmorphism -- because
it does not know what your system is. This one reads your `brand.json`, derives
the exact token set that brand produces, and then checks whether the code uses
*those* values.

That makes it able to catch things no general tool structurally can:

  - a hex that is not anywhere in your generated ramp
  - `var(--ds-surfce-hover)` -- a typo'd token that silently resolves to nothing
  - `border-radius: 8px` in a project configured to `sharp` (where md = 2px)
  - a hover fill that is legal on a card but invisible on a raised overlay
  - an inverted surface holding components no priority is defined against

Usage:
    python3 lint_conformance.py --brand brand.json src/
    python3 lint_conformance.py --brand brand.json app.html --json

Exit 1 if any violation is found.
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from build_tokens import build_tokens, load_brand  # noqa: E402

EXTS = (".html", ".htm", ".jsx", ".tsx", ".vue", ".svelte", ".css", ".scss")

CLASS_ATTR_RX = re.compile(r'class(?:Name)?\s*=\s*"([^"]*)"')

# Components whose colour must come from their priority, never from the caller.
COMPONENT_CLASSES = (
    "btn", "ibtn", "chip", "bdg", "badge", "alert", "toast", "mi", "menu-item",
    "seg", "tab", "pag", "crumb", "step", "avatar", "av", "acc", "sld", "prog",
    "card", "input", "select", "field",
)

# Containers that are raised overlays. Content inside them must hover with
# `control-subtle`; `surface-hover` equals `surface-raised` in dark mode.
RAISED_SCOPES = (
    "menu", "mi", "popover", "dropdown", "toast", "modal", "dialog", "drawer",
    "sheet", "cmd", "command", "palette", "combobox", "listbox",
)


class System:
    """The legal vocabulary derived from one brand.json."""

    def __init__(self, brand_path: Path | None):
        if brand_path:
            brand = load_brand(str(brand_path))
        else:
            brand = load_brand(str(Path(__file__).resolve().parent.parent
                                    / "assets" / "brand.template.json"))
        self.brand = brand
        self.tokens = build_tokens(brand)
        self.prefix = brand.get("prefix", "ds")

        self.names = set()
        for group in ("primitive", "light", "dark", "dimension"):
            self.names |= set(self.tokens.get(group, {}))
        # font slots are emitted separately from the semantic maps
        self.names |= {"font-display", "font-text", "font-mono"}

        self.colours = set()
        for group in ("primitive", "light", "dark"):
            for v in self.tokens.get(group, {}).values():
                if isinstance(v, str) and v.startswith("#"):
                    self.colours.add(v.lower())

        dim = self.tokens["dimension"]
        self.radii = {v for k, v in dim.items() if k.startswith("radius-")}
        self.spacing = {v for k, v in dim.items() if k.startswith("space-")}
        self.font_sizes = {v for k, v in dim.items() if k.startswith("font-size-")}
        self.control_h = {v for k, v in dim.items() if k.startswith("control-h")}

    def px_set(self, values):
        return {int(v[:-2]) for v in values if v.endswith("px") and v[:-2].isdigit()}


def strip_noise(text: str) -> str:
    """Blank regions where a match is not a defect, preserving offsets."""
    def blank(m):
        return " " * len(m.group(0))
    text = re.sub(r"--[\w-]+\s*:[^;}]*[;}]", blank, text)   # token definitions
    text = re.sub(r"/\*.*?\*/", blank, text, flags=re.S)     # css comments
    text = re.sub(r"<!--.*?-->", blank, text, flags=re.S)    # html comments
    text = re.sub(r"^\s*#.*$", blank, text, flags=re.M)      # shell/py comments
    return text


COLOUR_PROP = re.compile(
    r"(?:^|[;{\s\"'])((?:background|border|outline|fill|stroke|color|"
    r"box-shadow|text-decoration)[\w-]*)\s*:\s*([^;}\"']+)", re.I)
HEX = re.compile(r"#[0-9a-fA-F]{3,8}\b")
FUNC_COLOUR = re.compile(r"\b(?:rgba?|hsla?)\s*\(", re.I)
VAR_REF = re.compile(r"var\(\s*--([\w-]+?)\s*[,)]")
RADIUS = re.compile(r"border-radius\s*:\s*([^;}\"']+)", re.I)
BOX_PROP = re.compile(r"\b(padding|margin|gap|row-gap|column-gap)[\w-]*\s*:\s*([^;}\"']+)", re.I)
FONT_SIZE = re.compile(r"\bfont-size\s*:\s*([^;}\"']+)", re.I)

# Any property that takes a dimension. Previously only padding/margin/gap and
# font-size were checked, so a user-invented component could hardcode `width`,
# `height`, `line-height`, `border-width` or `z-index` with nothing objecting --
# which defeats the purpose of a token system the moment someone builds outside
# the predefined set.
DIMENSION_PROPS = (
    "width", "height", "min-width", "max-width", "min-height", "max-height",
    "top", "right", "bottom", "left", "inset", "flex-basis", "size",
    "line-height", "border-width", "border-top-width", "border-right-width",
    "border-bottom-width", "border-left-width", "outline-width",
    "outline-offset", "translate",
)
DIM_DECL = re.compile(
    r"\b(" + "|".join(re.escape(x) for x in DIMENSION_PROPS) +
    r")\s*:\s*([^;}\"'\n]+)", re.I)
DURATION_DECL = re.compile(
    r"\b(transition(?:-duration)?|animation(?:-duration)?)\s*:\s*([^;}\"'\n]+)", re.I)
MS = re.compile(r"\b(\d+)ms\b")
Z_DECL = re.compile(r"\bz-index\s*:\s*(-?\d+)", re.I)
SHADOW_DECL = re.compile(
    r"\bbox-shadow\s*:(?!\s*(?:none\b|var\())\s*([^;}\"'\n]+)", re.I)
PX = re.compile(r"(-?\d+(?:\.\d+)?)px")

BANNED = [
    ("gradient", re.compile(r"(?:linear|radial|conic)-gradient", re.I),
     "decorative gradient"),
    # `backdrop-filter: none` DISABLES blur -- that is the system's position,
    # not a violation of it.
    ("backdrop-blur", re.compile(r"backdrop-filter\s*:(?!\s*none\b)\s*[^;}]+", re.I),
     "glassmorphism / backdrop blur"),
    ("transition-all", re.compile(r"transition\s*:\s*all\b", re.I),
     "transition: all -- animate opacity and transform only"),
    ("radius-inherit", re.compile(r"border-radius\s*:\s*inherit", re.I),
     "border-radius: inherit -- element adopts its PARENT's corners"),
]

COMPONENT_OVERRIDE = re.compile(
    r"<[a-zA-Z][^>]*\bclass(?:Name)?=\"[^\"]*\b(?:" + "|".join(COMPONENT_CLASSES) +
    r")\b[^\"]*\"[^>]*\bstyle=\"[^\"]*\b(?:color|background|border-color)\s*:", re.I)

# An inverted fill is CORRECT on a leaf component whose priority defines it --
# a filled button is `ink` by design. The defect is an inverted fill on a
# CONTAINER, because the components placed inside it then have no legal
# priority. Statically we cannot see containment, so this keys off container-ish
# selector names, which is what the real bug (`.bulk`) looked like.
CONTAINER_WORDS = (
    "bar", "toolbar", "header", "banner", "strip", "panel", "bulk", "hero",
    "footer", "nav", "shell", "container", "wrapper", "region", "tray",
)
INVERTED_FILL = re.compile(
    r"background(?:-color)?\s*:\s*var\(\s*--[\w-]*?-(?:ink|tooltip-bg|"
    r"(?:danger|success|warning|info)-solid)\b", re.I)


# --- component class-combination rules ------------------------------------
# The value checks above cannot catch these: every class is spelled correctly
# and every token is legal. What is wrong is the COMBINATION. This is the gap
# that let `ds-btn--plain` onto three labelled buttons -- `plain` is documented
# as Icon Button only -- with both linters reporting zero violations.
BTN_PRIORITIES = {"filled", "outline", "ghost", "plain"}
BTN_COLOURS = {"neutral", "primary", "destructive"}
TAG_RX = re.compile(r"<([a-zA-Z][\w-]*)\b([^>]*)>")


def check_combinations(text, prefix, add):
    for m in TAG_RX.finditer(text):
        attrs = m.group(2)
        cm = CLASS_ATTR_RX.search(attrs)
        if not cm:
            continue
        classes = set(cm.group(1).split())
        mods = {c.split("--", 1)[1] for c in classes
                if c.startswith(f"{prefix}-btn--") and "--" in c}
        is_btn = f"{prefix}-btn" in classes
        is_icon = f"{prefix}-iconbtn" in classes
        frag = m.group(0)[:70]

        if (is_icon or mods) and not is_btn:
            add(m.start(), "component-class-incomplete",
                f"a button modifier or {prefix}-iconbtn without the base "
                f"{prefix}-btn class -- the base carries height, padding and focus",
                frag)
            continue
        if not is_btn:
            continue

        pri = mods & BTN_PRIORITIES
        col = mods & BTN_COLOURS
        if len(pri) != 1:
            add(m.start(), "component-class-invalid",
                f"a button needs exactly one priority "
                f"({', '.join(sorted(BTN_PRIORITIES))}); found {sorted(pri) or 'none'}",
                frag)
        if len(col) != 1:
            add(m.start(), "component-class-invalid",
                f"a button needs exactly one colour "
                f"({', '.join(sorted(BTN_COLOURS))}); found {sorted(col) or 'none'}",
                frag)
        # `plain` is for COMPACT CONTROLS IN A GROUP -- icon buttons in a
        # toolbar or table row, page numbers in a pager. What it is not for is a
        # standalone labelled action: a bare word with no fill, no edge and no
        # group around it does not read as a control.
        is_square = f"{prefix}-btn--square" in classes
        if "plain" in pri and not (is_icon or is_square):
            add(m.start(), "component-class-invalid",
                "`plain` needs `-iconbtn` or `-btn--square`: it is for compact "
                "controls in a group, not a standalone labelled action. Use "
                "`ghost` or `filled` for a labelled button",
                frag)
        if is_icon and "aria-label" not in attrs and "aria-labelledby" not in attrs:
            add(m.start(), "a11y-icon-button-unnamed",
                "icon button with no accessible name -- aria-label is mandatory",
                frag)


# --- Tailwind utility rules -----------------------------------------------
# Tailwind puts design decisions in CLASS NAMES, not CSS declarations, so every
# value check above goes silent on it. A card with `shadow-md hover:shadow-lg
# transition-all bg-gradient-to-r from-violet-500` scored zero violations.
# Since most vibecoded projects are Tailwind, that blind spot mattered more than
# anything else the linter did.

# Tailwind's built-in palette. Present here so it can be REJECTED: the generated
# theme removes it, and reaching for it means bypassing the system's roles.
TW_PALETTE = (
    "slate|gray|grey|zinc|neutral|stone|red|orange|amber|yellow|lime|green|"
    "emerald|teal|cyan|sky|blue|indigo|violet|purple|fuchsia|pink|rose")
TW_SPACING_OK = {"0", "px", "0.5", "1", "1.5", "2", "3", "4", "5", "6", "8",
                 "10", "12", "16", "20", "24", "full", "auto", "screen"}
TW_RADIUS_OK = {"none", "sm", "md", "lg", "xl", "full", ""}
TW_TEXT_OK = {"xs", "sm", "base", "lg", "xl", "2xl", "3xl", "4xl",
              "left", "right", "center", "justify", "start", "end",
              "wrap", "nowrap", "balance", "pretty", "ellipsis", "clip",
              # `text-*` is overloaded: size, colour and alignment all share it
              "white", "black", "transparent", "current", "inherit",
              "muted", "subtle", "inverse", "ink", "accent"}

TW_RULES = [
    (re.compile(r"^(?:\w+:)*(?:bg|text|border|ring|fill|stroke|from|via|to|"
                r"divide|outline|shadow|decoration|placeholder|accent|caret)-(?:"
                + TW_PALETTE + r")-\d{2,3}$"),
     "tw-raw-palette",
     "Tailwind's own palette bypasses the system's roles. Use a role utility "
     "(bg-surface, text-muted, border-strong, bg-accent-subtle)"),
    (re.compile(r"^(?:\w+:)*bg-gradient-|^(?:\w+:)*bg-linear-|^(?:\w+:)*(?:from|via|to)-\["),
     "tw-gradient", "decorative gradient"),
    (re.compile(r"^(?:\w+:)*backdrop-(?:blur|filter)"),
     "tw-backdrop-blur", "glassmorphism / backdrop blur"),
    (re.compile(r"^(?:\w+:)*transition-all$"),
     "tw-transition-all", "transition-all -- animate opacity and transform only"),
    (re.compile(r"^(?:\w+:)*shadow-(?:lg|xl|2xl|inner)$"),
     "tw-shadow", "the system has two shadows (sm, md) and both are for overlays"),
    (re.compile(r"^hover:(?:scale|-?translate)-"),
     "tw-hover-transform",
     "hover-lift / hover-scale -- hover shifts background only"),
    (re.compile(r"^(?:\w+:)*\w[\w-]*-\[[^\]]+\]$"),
     "tw-arbitrary-value",
     "arbitrary value -- if the system has no token for it, add one to "
     "build_tokens.py rather than inlining it here"),
]
TW_SPACING_RX = re.compile(
    r"^(?:\w+:)*(?:p|m|gap|space)(?:[xytrbles])?-(-?[\w.]+)$")
TW_RADIUS_RX = re.compile(r"^(?:\w+:)*rounded(?:-[trbl]{1,2})?(?:-([\w]+))?$")
TW_TEXT_RX = re.compile(r"^(?:\w+:)*text-([\w]+)$")


# --- table column alignment ------------------------------------------------
# Alignment is a property of the COLUMN, so the class has to appear on the
# header cell AND on every body cell beneath it. Put it on one and not the
# other and the column silently splits -- a right-aligned figure under a
# left-aligned label. The stylesheet welds `th` and `td` together, but it
# cannot make an author write both class attributes; this check does.
TABLE_RX = re.compile(r"<table\b[^>]*>(.*?)</table>", re.S | re.I)
THEAD_RX = re.compile(r"<thead\b[^>]*>(.*?)</thead>", re.S | re.I)
TBODY_RX = re.compile(r"<tbody\b[^>]*>(.*?)</tbody>", re.S | re.I)
ROW_RX = re.compile(r"<tr\b[^>]*>(.*?)</tr>", re.S | re.I)
CELL_RX = re.compile(r"<(th|td)\b([^>]*)>", re.I)


def _cell_alignment(attrs, prefix):
    """The alignment-bearing classes on one cell, as a frozenset."""
    cm = CLASS_ATTR_RX.search(attrs)
    classes = set(cm.group(1).split()) if cm else set()
    return frozenset(classes & {f"{prefix}-num", f"{prefix}-table-actions"})


def check_table_alignment(text, prefix, add):
    for tm in TABLE_RX.finditer(text):
        block = tm.group(1)
        if f"{prefix}-table" not in tm.group(0):
            continue
        # colspan/rowspan break positional column matching -- skip rather than
        # report a column index that does not mean what it says.
        if re.search(r"\b(?:colspan|rowspan)\s*=", block, re.I):
            continue
        head = THEAD_RX.search(block)
        body = TBODY_RX.search(block)
        if not head or not body:
            continue
        head_row = ROW_RX.search(head.group(1))
        if not head_row:
            continue
        headers = [_cell_alignment(c.group(2), prefix)
                   for c in CELL_RX.finditer(head_row.group(1))]
        for row in ROW_RX.finditer(body.group(1)):
            cells = [(c.group(2), c.start()) for c in CELL_RX.finditer(row.group(1))]
            if len(cells) != len(headers):
                break          # ragged table; positional matching is unsafe
            for i, (attrs, _) in enumerate(cells):
                want, got = headers[i], _cell_alignment(attrs, prefix)
                if want == got:
                    continue
                only_head = ", ".join(sorted(want - got)) or "nothing"
                only_cell = ", ".join(sorted(got - want)) or "nothing"
                add(tm.start() + body.start() + row.start(),
                    "table-column-alignment-split",
                    f"column {i + 1} is aligned inconsistently -- the header "
                    f"carries {only_head} and the body cell carries "
                    f"{only_cell}. Alignment belongs to the whole column, so "
                    f"the class goes on the th and on every td beneath it",
                    row.group(0)[:70])
            break              # one body row is enough to prove the contract


def check_tailwind(text, add, sys_role_names=frozenset()):
    for m in CLASS_ATTR_RX.finditer(text):
        base = m.start()
        for cls in m.group(1).split():
            for rx, rule, msg in TW_RULES:
                if rx.match(cls):
                    add(base, rule, msg, cls)
                    break
            else:
                sm = TW_SPACING_RX.match(cls)
                if sm and sm.group(1).lstrip("-") not in TW_SPACING_OK:
                    add(base, "tw-off-scale-spacing",
                        f"`{cls}` is not on the spacing scale "
                        f"(the generated theme removes it)", cls)
                    continue
                rm = TW_RADIUS_RX.match(cls)
                if rm and (rm.group(1) or "") not in TW_RADIUS_OK:
                    add(base, "tw-off-system-radius",
                        f"`{cls}` is not a radius in this brand's preset", cls)
                    continue
                tm = TW_TEXT_RX.match(cls)
                if tm:
                    v = tm.group(1)
                    # a colour role is a valid `text-` utility, not a font size
                    if (v not in TW_TEXT_OK and not v.isdigit()
                            and v not in sys_role_names):
                        add(base, "tw-off-ladder-font-size",
                            f"`{cls}` is not on the type ladder", cls)


# --- law checks for components the system has never seen ------------------
# The value checks pass a NEW component that uses legal tokens to break stated
# laws: a token shadow on a card, a hover that changes the border, a hover-lift.
# Three of four such violations went undetected, which is exactly the case where
# someone is building outside the documented 43.

OVERLAY_SEL = re.compile(
    r"(modal|dialog|popover|menu|dropdown|toast|tooltip|drawer|sheet|overlay|"
    r"palette|listbox|calendar)", re.I)
TOKEN_SHADOW = re.compile(r"box-shadow\s*:\s*var\([^)]*-shadow-(?!none)[^)]*\)", re.I)
HOVER_BLOCK = re.compile(r"(?m)^([^\n{}]*:hover[^\n{}]*)\{([^}]*)\}")
HOVER_OK = ("background", "color", "text-decoration", "opacity", "outline",
            "cursor", "transition", "visibility")


def check_laws(text, add):
    # a shadow is permitted on overlays only, token or not
    for m in re.finditer(r"(?m)^([^\n{}]+)\{([^}]*)\}", text):
        sel, body = m.group(1), m.group(2)
        if TOKEN_SHADOW.search(body) and not OVERLAY_SEL.search(sel):
            add(m.start(), "law-shadow-outside-overlay",
                "box-shadow on a non-overlay. The shadow tokens exist for "
                "modals, menus, popovers, toasts and drawers; a shadow on a "
                "card is the clearest generated-UI tell",
                sel.strip())

    for m in HOVER_BLOCK.finditer(text):
        sel, body = m.group(1), m.group(2)
        for decl in body.split(";"):
            if ":" not in decl:
                continue
            prop = decl.split(":", 1)[0].strip().lower()
            if not prop or prop.startswith("--"):
                continue
            if prop.startswith("transform"):
                add(m.start(), "law-hover-transform",
                    "hover-lift / hover-scale. Hover shifts background only — "
                    "no transform, no movement",
                    f"{sel.strip()} {{ {decl.strip()} }}")
            elif not prop.startswith(HOVER_OK):
                add(m.start(), "law-hover-not-background",
                    f"hover changes `{prop}`. Hover shifts background only — "
                    f"never border, size or position",
                    f"{sel.strip()} {{ {decl.strip()} }}")


def line_of(text: str, pos: int) -> int:
    return text.count("\n", 0, pos) + 1


def lint_file(path: Path, sys_: System):
    raw = path.read_text(errors="replace")
    text = strip_noise(raw)
    hits = []

    def add(pos, rule, msg, frag):
        hits.append((line_of(text, pos), rule, msg, frag.strip()[:70]))

    # --- banned patterns -------------------------------------------------
    for rule, rx, msg in BANNED:
        for m in rx.finditer(text):
            add(m.start(), rule, msg, m.group(0))

    # --- undefined token references --------------------------------------
    for m in VAR_REF.finditer(text):
        name = m.group(1)
        for pfx in (sys_.prefix + "-", ""):
            if name.startswith(pfx):
                bare = name[len(pfx):]
                break
        if bare and bare not in sys_.names:
            add(m.start(), "undefined-token",
                f"--{name} is not in this brand's token set "
                f"(a typo here resolves to nothing and fails silently)",
                m.group(0))

    # --- colours not in this brand's palette ------------------------------
    for m in COLOUR_PROP.finditer(text):
        prop, value = m.group(1), m.group(2)
        for hm in HEX.finditer(value):
            if hm.group(0).lower() not in sys_.colours:
                add(m.start(), "off-system-colour",
                    f"{hm.group(0)} is not in this brand's generated ramp",
                    f"{prop}: {value}")
        if FUNC_COLOUR.search(value):
            add(m.start(), "off-system-colour",
                "literal rgb()/hsl() colour -- use a semantic token",
                f"{prop}: {value}")

    # --- radius must be a derived value for THIS brand --------------------
    legal_radius = sys_.px_set(sys_.radii) | {0, 9999}
    for m in RADIUS.finditer(text):
        value = m.group(1)
        if "var(" in value or "inherit" in value or "%" in value:
            continue
        for num in PX.findall(value):
            n = int(float(num))
            if n not in legal_radius:
                add(m.start(), "off-system-radius",
                    f"{n}px is not a radius in the '{sys_.brand['radius']}' preset "
                    f"({sorted(legal_radius - {9999})}) -- use var(--{sys_.prefix}-radius-*)",
                    f"border-radius: {value}")

    # --- spacing must be on this brand's scale ---------------------------
    legal_space = sys_.px_set(sys_.spacing)
    for m in BOX_PROP.finditer(text):
        value = m.group(2)
        if "var(" in value or "%" in value or "auto" in value:
            continue
        for num in PX.findall(value):
            n = int(float(num))
            if n < 0:            # centring offsets and deliberate overlaps
                continue
            if n not in legal_space:
                add(m.start(), "off-scale-spacing",
                    f"{n}px is not on the spacing scale",
                    f"{m.group(1)}: {value}")

    # --- font sizes must be on the ladder --------------------------------
    legal_fs = sys_.px_set(sys_.font_sizes)
    for m in FONT_SIZE.finditer(text):
        value = m.group(1)
        if "var(" in value or "%" in value or "em" in value:
            continue
        for num in PX.findall(value):
            n = int(float(num))
            if n not in legal_fs:
                add(m.start(), "off-ladder-font-size",
                    f"{n}px is not on the type ladder ({sorted(legal_fs)})",
                    f"font-size: {value}")

    # --- any dimensional property must come from a token ------------------
    legal_dim = (sys_.px_set(sys_.spacing) | sys_.px_set(sys_.radii)
                 | sys_.px_set(sys_.font_sizes) | sys_.px_set(sys_.control_h)
                 | sys_.px_set({v for k, v in sys_.tokens["dimension"].items()
                                if k.startswith(("size-", "container-", "icon-",
                                                 "line-height-", "row-h",
                                                 "section-gap", "border-width",
                                                 "touch-target", "focus-ring"))}))
    for m in DIM_DECL.finditer(text):
        prop, value = m.group(1), m.group(2)
        if "var(" in value or "%" in value or "auto" in value or "calc(" in value:
            continue
        if "ch" in value or "vh" in value or "vw" in value or "em" in value:
            continue
        for num in PX.findall(value):
            n = int(float(num))
            if n < 0 or n == 0:
                continue
            if n not in legal_dim:
                add(m.start(), "off-system-dimension",
                    f"{prop}: {n}px is not any token value -- a new component "
                    f"must reach for an existing token (size-*, container-*, "
                    f"space-*), not invent a number",
                    f"{prop}: {value}")

    # --- durations must come from the motion ladder -----------------------
    legal_ms = {int(v[:-2]) for k, v in sys_.tokens["dimension"].items()
                if k.startswith("duration-") and v.endswith("ms")}
    for m in DURATION_DECL.finditer(text):
        if "var(" in m.group(2):
            continue
        for num in MS.findall(m.group(2)):
            if int(num) not in legal_ms:
                add(m.start(), "off-ladder-duration",
                    f"{num}ms is not on the motion ladder ({sorted(legal_ms)})",
                    f"{m.group(1)}: {m.group(2)}")

    # --- z-index must come from the layer scale --------------------------
    legal_z = {int(v) for k, v in sys_.tokens["dimension"].items()
               if k.startswith("z-") and str(v).lstrip("-").isdigit()}
    for m in Z_DECL.finditer(text):
        if int(m.group(1)) not in legal_z:
            add(m.start(), "off-scale-z-index",
                f"z-index {m.group(1)} is not on the layer scale "
                f"({sorted(legal_z)}) -- ad-hoc z-index is how stacking breaks",
                m.group(0))

    # --- shadows must be tokens, and only on overlays --------------------
    for m in SHADOW_DECL.finditer(text):
        add(m.start(), "literal-shadow",
            "literal box-shadow -- the system has two shadow tokens and they "
            "are for overlays only; a shadow on a card is the clearest "
            "generated-UI tell",
            f"box-shadow: {m.group(1)}")

    # --- system laws, for components with no spec of their own -------------
    check_laws(text, add)

    # --- Tailwind utilities ------------------------------------------------
    check_tailwind(text, add, frozenset(sys_.tokens['light']))

    # --- component class combinations -------------------------------------
    check_combinations(text, sys_.prefix, add)

    # --- table columns aligned as a unit -----------------------------------
    check_table_alignment(text, sys_.prefix, add)

    # --- colour override on a component ----------------------------------
    for m in COMPONENT_OVERRIDE.finditer(text):
        add(m.start(), "component-colour-override",
            "colour override on a component -- if a component needs one to be "
            "legible, the container is wrong, not the component",
            m.group(0))

    # --- inverted surfaces on containers ----------------------------------
    block_rx = re.compile(r"(?m)^([^\n{]+)\{([^}]*)\}")
    for m in block_rx.finditer(text):
        sel, body = m.group(1), m.group(2)
        if not INVERTED_FILL.search(body):
            continue
        if not any(w in sel.lower() for w in CONTAINER_WORDS):
            continue
        add(m.start(), "inverted-surface",
            "container filled with an inverted/solid token -- no button priority "
            "is defined against it, so anything placed inside needs a colour "
            "override to stay legible",
            sel.strip())
    # markup form: same container test. A colour swatch demonstrating a token
    # is not a container and must not be flagged.
    for m in re.finditer(
            r"<[a-zA-Z][^>]*style=\"[^\"]*background[^\"]*var\(\s*--[\w-]*?-"
            r"(?:ink|(?:danger|success|warning|info)-solid)\b[^>]*>", text, re.I):
        tag = m.group(0)
        cls = re.search(r'class(?:Name)?="([^"]*)"', tag)
        name = cls.group(1).lower() if cls else ""
        if not any(w in name for w in CONTAINER_WORDS):
            continue
        add(m.start(), "inverted-surface",
            "container element given an inverted fill inline -- see above", tag)

    # --- hover fill illegal for a raised surface --------------------------
    scope_rx = re.compile(
        r"(?m)^([^\n{]*\b(?:" + "|".join(RAISED_SCOPES) + r")\b[^\n{]*)\{([^}]*)\}")
    for m in scope_rx.finditer(text):
        body = m.group(2)
        if re.search(r"background(?:-color)?\s*:\s*var\(\s*--[\w-]*?-surface-hover", body, re.I):
            add(m.start(), "raised-hover-collision",
                "surface-hover inside a raised overlay -- it equals surface-raised "
                "in dark mode, so the hover is invisible. Use control-subtle",
                m.group(1))

    return sorted(hits)


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("paths", nargs="*", default=["."])
    ap.add_argument("--brand", help="path to brand.json (default: ./brand.json)")
    ap.add_argument("--json", action="store_true", help="machine-readable output")
    args = ap.parse_args(argv)

    brand_path = None
    if args.brand:
        brand_path = Path(args.brand)
    elif Path("brand.json").exists():
        brand_path = Path("brand.json")

    sys_ = System(brand_path)
    src = brand_path if brand_path else "house defaults"

    targets = []
    for a in args.paths or ["."]:
        p = Path(a)
        if p.is_dir():
            targets += [f for f in p.rglob("*") if f.suffix in EXTS]
        elif p.exists():
            targets.append(p)

    results, total = {}, 0
    for f in targets:
        hits = lint_file(f, sys_)
        if hits:
            results[str(f)] = hits
            total += len(hits)

    if args.json:
        print(json.dumps({"brand": str(src), "violations": total,
                          "files": {k: [dict(zip(("line", "rule", "message", "code"), h))
                                        for h in v] for k, v in results.items()}}, indent=2))
        return 1 if total else 0

    print(f"Conformance check against: {src}")
    print(f"  radius preset '{sys_.brand['radius']}' -> "
          f"{sorted(sys_.px_set(sys_.radii) - {9999})}")
    print(f"  {len(sys_.colours)} palette colours, {len(sys_.names)} tokens")
    for fname, hits in results.items():
        print(f"\n{fname}")
        for line, rule, msg, frag in hits:
            print(f"  {line:>5}  {rule:<26} {msg}")
            print(f"         {frag}")
    print(f"\n{total} violation(s) across {len(targets)} file(s).")
    return 1 if total else 0


if __name__ == "__main__":
    sys.exit(main())
