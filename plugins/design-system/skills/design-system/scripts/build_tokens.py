#!/usr/bin/env python3
"""
build_tokens.py -- Turn a brand.json into tokens.css (+ tokens.json).

The ONLY personalized inputs are in brand.json. Everything else in this file
is system law: locked ramps, locked scales, locked semantic role mapping.

Usage:
    python build_tokens.py brand.json                  # -> tokens.css, tokens.json
    python build_tokens.py brand.json --out-dir ./src
    python build_tokens.py brand.json --check          # contrast audit only
    python build_tokens.py --defaults > brand.json     # emit a default brand file

No third-party dependencies. Pure stdlib.
"""

import argparse
import json
import math
import sys
from pathlib import Path

# ---------------------------------------------------------------------------
# LOCKED SYSTEM CONSTANTS -- not personalizable, do not edit per project
# ---------------------------------------------------------------------------

# Perceptual lightness targets for every color ramp. Identical for the accent
# ramp, the neutral ramp and all status ramps, so a 600 is always a 600.
RAMP_STEPS = [50, 100, 125, 150, 175, 200, 250, 300, 400, 500, 600, 700, 750, 800, 850, 875, 900, 925, 950, 1000]
RAMP_L = {
    50: 0.985, 100: 0.967, 125: 0.958, 150: 0.949, 175: 0.940,
    200: 0.930, 250: 0.908,
    300: 0.885, 400: 0.812,
    500: 0.724, 600: 0.636, 700: 0.552, 750: 0.510, 800: 0.468,
    # Dark end deliberately compressed and lowered. Earlier values (900 = 0.372,
    # 950 = 0.263) made dark-mode cards and inputs read as mid-grey slabs; the
    # steps below keep the page genuinely dark and the lift between surfaces small.
    # Dark end lowered again so a dark UI reads as dark. `1000` is true black
    # for the page; surfaces climb from there in small steps, because a dark
    # card that lifts too far off the page reads as grey plastic, not depth.
    850: 0.320, 875: 0.290, 900: 0.245, 925: 0.195, 950: 0.140, 1000: 0.0,
}
# Chroma envelope: color peaks mid-ramp, tapers at both ends so tints stay
# tasteful and shades stay legible.
RAMP_C_FACTOR = {
    50: 0.10, 100: 0.20, 125: 0.245, 150: 0.29, 175: 0.335,
    200: 0.38, 250: 0.48, 300: 0.58,
    400: 0.82, 500: 1.00,
    600: 0.97, 700: 0.88, 750: 0.82, 800: 0.76, 850: 0.69, 900: 0.62,
    875: 0.655, 925: 0.54, 950: 0.45, 1000: 0.0,
}
MAX_CHROMA = 0.155          # ceiling; keeps neon inputs inside the house style
MIN_CHROMA = 0.045          # floor; keeps washed-out inputs from going gray

# Warm gray. LOCKED. This is the single biggest carrier of the system's
# identity -- it is never derived from the user's primary.
NEUTRAL_HUE = 67.0
NEUTRAL_C = {
    50: 0.0030, 100: 0.0035, 125: 0.0036, 150: 0.0038, 175: 0.0039,
    200: 0.0040, 250: 0.0043,
    300: 0.0045, 400: 0.0048,
    500: 0.0050, 600: 0.0048, 700: 0.0044, 750: 0.0041, 800: 0.0038, 850: 0.0035,
    875: 0.0034, 900: 0.0032, 925: 0.0029, 950: 0.0022, 1000: 0.0,
}

# Status hues. LOCKED -- status colors must never shift per brand, or a red
# "delete" stops reading as danger.
STATUS_HUES = {"success": 152.0, "warning": 78.0, "danger": 27.0, "info": 248.0}
STATUS_CHROMA = {"success": 0.115, "warning": 0.135, "danger": 0.145, "info": 0.120}

# 8pt grid with 4pt sub-steps below 24. LOCKED.
SPACE = {
    "0": 0, "px": 1, "0-5": 2, "1": 4, "1-5": 6, "2": 8, "3": 12, "4": 16,
    "5": 20, "6": 24, "8": 32, "10": 40, "12": 48, "16": 64, "20": 80, "24": 96,
}

# Fixed px type ladder. LOCKED. Line heights all land on 4pt.
TYPE_SCALE = [
    ("2xs", 12, 16, 0.005), ("sm", 14, 20, 0.0),
    ("base", 16, 24, 0.0), ("lg", 20, 28, -0.006), ("xl", 24, 32, -0.012),
    ("2xl", 32, 40, -0.018), ("3xl", 40, 48, -0.022), ("4xl", 56, 64, -0.026),
]

# Control heights, both densities. All multiples of 4.
CONTROL_HEIGHTS = {
    "default": {"sm": 32, "md": 40, "lg": 48},
    "compact": {"sm": 28, "md": 32, "lg": 40},
}
CONTROL_PAD_X = {
    "default": {"sm": 12, "md": 16, "lg": 20},
    "compact": {"sm": 8, "md": 12, "lg": 16},
}
ROW_HEIGHT = {"default": 48, "compact": 36}
SECTION_GAP = {"default": 32, "compact": 24}

# Corner presets. The base radius; every component derives from it.
RADIUS_PRESETS = {"sharp": 2, "soft": 8, "round": 14}

# Motion. LOCKED.
MOTION = {
    "duration-instant": "0ms",
    # 1ms rather than 0 under reduced-motion: it removes perceptible motion
    # while still firing transitionend/animationend, which JS often depends on.
    "duration-reduced": "1ms",
    "duration-fast": "120ms",
    "duration-base": "160ms",
    "duration-slow": "240ms",
    # Rotation and shimmer PERIODS, not transition durations -- a spinner's
    # 800ms is how long one revolution takes, which is a different kind of value
    # from "how long a hover takes to settle".
    "duration-spin": "800ms",
    "duration-shimmer": "1600ms",
    "duration-indeterminate": "1200ms",
    "ease-standard": "cubic-bezier(0.2, 0, 0, 1)",
    "ease-exit": "cubic-bezier(0.4, 0, 1, 1)",
}

# Borders-first depth model. Shadows are deliberately weak and rare.
SHADOWS = {
    "shadow-none": "none",
    "shadow-sm": "0 1px 2px -1px rgb(0 0 0 / 0.06)",
    "shadow-md": "0 4px 12px -2px rgb(0 0 0 / 0.08)",
    "shadow-lg": "0 12px 32px -8px rgb(0 0 0 / 0.12)",
}

VALID_RADIUS = set(RADIUS_PRESETS)
VALID_DENSITY = set(CONTROL_HEIGHTS)
VALID_ICONS = {"phosphor", "lucide", "remix"}

# ---------------------------------------------------------------------------
# Color science: sRGB <-> OKLCH, no dependencies
# ---------------------------------------------------------------------------


def _srgb_to_linear(c):
    return c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4


def _linear_to_srgb(c):
    return 12.92 * c if c <= 0.0031308 else 1.055 * (c ** (1 / 2.4)) - 0.055


def hex_to_rgb(h):
    h = h.strip().lstrip("#")
    if len(h) == 3:
        h = "".join(ch * 2 for ch in h)
    if len(h) != 6:
        raise ValueError(f"Not a hex color: #{h}")
    return tuple(int(h[i:i + 2], 16) / 255 for i in (0, 2, 4))


def rgb_to_hex(rgb):
    return "#" + "".join(f"{round(max(0.0, min(1.0, c)) * 255):02x}" for c in rgb)


def rgb_to_oklab(rgb):
    r, g, b = (_srgb_to_linear(c) for c in rgb)
    l = 0.4122214708 * r + 0.5363325363 * g + 0.0514459929 * b
    m = 0.2119034982 * r + 0.6806995451 * g + 0.1073969566 * b
    s = 0.0883024619 * r + 0.2817188376 * g + 0.6299787005 * b
    l_, m_, s_ = (math.copysign(abs(v) ** (1 / 3), v) for v in (l, m, s))
    return (
        0.2104542553 * l_ + 0.7936177850 * m_ - 0.0040720468 * s_,
        1.9779984951 * l_ - 2.4285922050 * m_ + 0.4505937099 * s_,
        0.0259040371 * l_ + 0.7827717662 * m_ - 0.8086757660 * s_,
    )


def oklab_to_rgb(lab):
    L, a, b = lab
    l_ = L + 0.3963377774 * a + 0.2158037573 * b
    m_ = L - 0.1055613458 * a - 0.0638541728 * b
    s_ = L - 0.0894841775 * a - 1.2914855480 * b
    l, m, s = (v ** 3 for v in (l_, m_, s_))
    return (
        _linear_to_srgb(4.0767416621 * l - 3.3077115913 * m + 0.2309699292 * s),
        _linear_to_srgb(-1.2684380046 * l + 2.6097574011 * m - 0.3413193965 * s),
        _linear_to_srgb(-0.0041960863 * l - 0.7034186147 * m + 1.7076147010 * s),
    )


def rgb_to_oklch(rgb):
    L, a, b = rgb_to_oklab(rgb)
    return (L, math.hypot(a, b), math.degrees(math.atan2(b, a)) % 360)


def oklch_to_rgb(L, C, H):
    h = math.radians(H)
    return oklab_to_rgb((L, C * math.cos(h), C * math.sin(h)))


def _in_gamut(rgb, eps=1e-4):
    return all(-eps <= c <= 1 + eps for c in rgb)


def oklch_to_hex(L, C, H):
    """Convert to hex, reducing chroma by bisection until inside sRGB."""
    rgb = oklch_to_rgb(L, C, H)
    if _in_gamut(rgb):
        return rgb_to_hex(rgb)
    lo, hi = 0.0, C
    for _ in range(24):
        mid = (lo + hi) / 2
        if _in_gamut(oklch_to_rgb(L, mid, H)):
            lo = mid
        else:
            hi = mid
    return rgb_to_hex(oklch_to_rgb(L, lo, H))


# ---------------------------------------------------------------------------
# Contrast (WCAG 2.1)
# ---------------------------------------------------------------------------


def relative_luminance(rgb):
    r, g, b = (_srgb_to_linear(c) for c in rgb)
    return 0.2126 * r + 0.7152 * g + 0.0722 * b


def contrast_ratio(hex_a, hex_b):
    la = relative_luminance(hex_to_rgb(hex_a))
    lb = relative_luminance(hex_to_rgb(hex_b))
    hi, lo = max(la, lb), min(la, lb)
    return (hi + 0.05) / (lo + 0.05)


def best_on_color(bg_hex, light="#ffffff", dark=None):
    """Pick the foreground with the better contrast against bg_hex."""
    dark = dark or oklch_to_hex(RAMP_L[950], NEUTRAL_C[950], NEUTRAL_HUE)
    return light if contrast_ratio(bg_hex, light) >= contrast_ratio(bg_hex, dark) else dark


# ---------------------------------------------------------------------------
# Ramp construction
# ---------------------------------------------------------------------------


def build_ramp(hue, base_chroma, chroma_factors=RAMP_C_FACTOR):
    return {s: oklch_to_hex(RAMP_L[s], base_chroma * chroma_factors[s], hue)
            for s in RAMP_STEPS}


def build_neutral_ramp():
    return {s: oklch_to_hex(RAMP_L[s], NEUTRAL_C[s], NEUTRAL_HUE) for s in RAMP_STEPS}


ACHROMATIC_C = 0.02  # below this, hue angle is numerically meaningless


def accent_ramp_from_hex(primary_hex):
    _, c, h = rgb_to_oklch(hex_to_rgb(primary_hex))
    if c < ACHROMATIC_C:
        raise SystemExit(
            f"`primary` is {primary_hex}, which is effectively greyscale "
            f"(chroma {c:.3f}).\nThe accent ramp needs a real hue to derive from, and the "
            "neutral ramp is\nalready a locked warm grey. Pick a chromatic brand colour; "
            "if the brand is\ngenuinely monochrome, use a restrained near-neutral such as "
            "#3D5A80 or #6B5B4E."
        )
    return build_ramp(h, max(MIN_CHROMA, min(MAX_CHROMA, c))), h


# ---------------------------------------------------------------------------
# Semantic role mapping -- LOCKED. This table IS the design system.
# ---------------------------------------------------------------------------

# role -> (light-mode step, dark-mode step)
# Page is tinted, cards are near-white. Dark mode uses the compressed 925/900/850
# steps so cards and controls lift off the page without turning grey.
SURFACE_ROLES = {
    "bg":               (100, 1000),   # true black in dark mode
    "surface":          (50,  950),
    "surface-raised":   (50,  925),
    "surface-sunken":   (200, 1000),
    "surface-hover":    (150, 900),
    "surface-active":   (200, 875),
}
# CONTROL is a dedicated grey scale for elements that sit ON a surface --
# inputs, neutral buttons, badges, segmented tracks, skeletons. It is separate
# from SURFACE_ROLES on purpose: a control must stay legible whether it lands on
# the tinted page, a near-white card, or a raised popover, so it cannot simply
# be "one step off" whatever is behind it.
CONTROL_ROLES = {
    "control-subtle":   (150, 900),
    "control":          (200, 875),    # inputs: darker, closer to the page
    "control-hover":    (300, 850),
    "control-active":   (400, 800),
    "control-border":   (300, 800),
}
# INK is the primary-action family. Deliberately NOT the accent: reserving the
# brand hue for links, selection, focus and status is what keeps a white-label
# system from reading as "the purple app" / "the teal app". Ink inverts in dark
# mode -- near-white fill with near-black text.
INK_ROLES = {
    "ink":        (900, 100),
    "ink-hover":  (800, 200),
    "ink-active": (950, 300),
}
# border / border-subtle are DECORATIVE (dividers, card edges) -- deliberately
# faint, no WCAG floor. border-strong is INTERACTIVE (input/select/checkbox
# edges) and must clear 3:1, because it is the only thing identifying a control.
BORDER_ROLES = {
    "border-subtle": (125, 875),
    "border":        (200, 850),       # quieter in dark: was reading too bright
    "border-strong": (600, 600),
}
TEXT_ROLES = {
    "text":         (950, 50),
    "text-muted":   (800, 300),
    "text-subtle":  (600, 400),
    "text-inverse": (50,  950),
}
# Solid fills sit at 700 in light mode: at L=0.636 (step 600) neither white nor
# near-black clears 4.5:1, so 600 is an unusable step for text-bearing fills.
ACCENT_ROLES = {
    "accent-subtle": (100, 900),
    "accent-muted":  (200, 800),
    "accent-border": (400, 600),
    "accent":        (700, 500),
    "accent-hover":  (800, 400),
    "accent-active": (900, 300),
    "accent-text":   (800, 300),
}
STATUS_ROLES = {
    "subtle": (100, 900),
    "muted":  (200, 800),
    "border": (400, 600),
    "solid":  (700, 500),
    "text":   (800, 300),
}


def resolve(roles, ramp, mode_idx):
    return {name: ramp[steps[mode_idx]] for name, steps in roles.items()}


# ---------------------------------------------------------------------------
# brand.json
# ---------------------------------------------------------------------------

# Three curated typeface sets. All fit the neutral-precise temperament; each is
# freely licensed. `fontPreset` expands into the three slots; an explicit `fonts`
# entry overrides the preset per slot.
FONT_PRESETS = {
    "grotesk": {
        "display": "'Geist', system-ui, sans-serif",
        "text": "'Geist', system-ui, sans-serif",
        "mono": "'Geist Mono', ui-monospace, monospace",
    },
    "editorial": {
        "display": "'Instrument Serif', Georgia, serif",
        "text": "'Inter', system-ui, sans-serif",
        "mono": "'IBM Plex Mono', ui-monospace, monospace",
    },
    "technical": {
        "display": "'IBM Plex Sans', system-ui, sans-serif",
        "text": "'IBM Plex Sans', system-ui, sans-serif",
        "mono": "'IBM Plex Mono', ui-monospace, monospace",
    },
}
VALID_FONT_PRESETS = set(FONT_PRESETS)

# House default is deliberately NOT indigo-600 + Inter. That pairing is the single
# most recognisable AI-default look, and shipping it as the fallback would mean the
# no-config path produces exactly what references/anti-patterns.md forbids.
DEFAULT_BRAND = {
    "$comment": "The complete set of personalizable inputs. Everything else is system law.",
    "name": "Untitled Product",
    "primary": "#3D5A80",
    "radius": "soft",
    "density": "default",
    "iconSet": "lucide",
    "fontPreset": "grotesk",
    "fonts": {},
    "borderWeight": "hairline",
    "prefix": "ds",
}

VALID_BORDER_WEIGHT = {"hairline": 1, "medium": 1.5, "bold": 2}


def load_brand(path):
    brand = dict(DEFAULT_BRAND)
    user = json.loads(Path(path).read_text())
    user_fonts = user.pop("fonts", {}) or {}
    brand.update(user)

    errs = []

    # Resolve fonts: preset supplies the base, explicit per-slot values win.
    preset_name = brand.get("fontPreset", DEFAULT_BRAND["fontPreset"])
    if preset_name not in VALID_FONT_PRESETS:
        errs.append(f"fontPreset must be one of {sorted(VALID_FONT_PRESETS)}")
        preset_name = DEFAULT_BRAND["fontPreset"]
    fonts = dict(FONT_PRESETS[preset_name])
    unknown_slots = set(user_fonts) - set(fonts)
    if unknown_slots:
        errs.append(
            f"fonts has unknown slot(s) {sorted(unknown_slots)}; "
            f"only {sorted(fonts)} exist"
        )
    fonts.update({k: v for k, v in user_fonts.items() if k in fonts})
    brand["fonts"] = fonts
    brand["fontPreset"] = preset_name

    # The display face is hard-blocked from body copy: if someone points `text` at
    # a serif display family, the system reads as a magazine, not a product.
    if user_fonts.get("text") and "serif" in user_fonts["text"].lower():
        if "sans-serif" not in user_fonts["text"].lower():
            errs.append(
                "fonts.text looks like a serif/display family. The text slot must be "
                "a UI-grade sans (or mono); use fonts.display for serif faces."
            )

    try:
        hex_to_rgb(brand["primary"])
    except Exception as e:
        errs.append(str(e))
    if brand["radius"] not in VALID_RADIUS:
        errs.append(f"radius must be one of {sorted(VALID_RADIUS)}")
    if brand["density"] not in VALID_DENSITY:
        errs.append(f"density must be one of {sorted(VALID_DENSITY)}")
    if brand["iconSet"] not in VALID_ICONS:
        errs.append(f"iconSet must be one of {sorted(VALID_ICONS)}")
    if brand["borderWeight"] not in VALID_BORDER_WEIGHT:
        errs.append(f"borderWeight must be one of {sorted(VALID_BORDER_WEIGHT)}")
    if errs:
        raise SystemExit("brand.json is invalid:\n  - " + "\n  - ".join(errs))
    return brand


# ---------------------------------------------------------------------------
# Token assembly
# ---------------------------------------------------------------------------


def build_tokens(brand):
    accent, accent_hue = accent_ramp_from_hex(brand["primary"])
    neutral = build_neutral_ramp()
    status = {n: build_ramp(STATUS_HUES[n], STATUS_CHROMA[n]) for n in STATUS_HUES}

    base_r = RADIUS_PRESETS[brand["radius"]]
    density = brand["density"]
    heights = CONTROL_HEIGHTS[density]

    out = {"primitive": {}, "light": {}, "dark": {}, "dimension": {}}

    for step, hexv in neutral.items():
        out["primitive"][f"neutral-{step}"] = hexv
    for step, hexv in accent.items():
        out["primitive"][f"accent-{step}"] = hexv
    for name, ramp in status.items():
        for step, hexv in ramp.items():
            out["primitive"][f"{name}-{step}"] = hexv

    for mode, idx in (("light", 0), ("dark", 1)):
        sem = {}
        sem.update(resolve(SURFACE_ROLES, neutral, idx))
        sem.update(resolve(CONTROL_ROLES, neutral, idx))
        sem.update(resolve(BORDER_ROLES, neutral, idx))
        sem.update(resolve(TEXT_ROLES, neutral, idx))
        sem.update(resolve(INK_ROLES, neutral, idx))
        sem.update(resolve(ACCENT_ROLES, accent, idx))
        for name, ramp in status.items():
            for suffix, steps in STATUS_ROLES.items():
                sem[f"{name}-{suffix}"] = ramp[steps[idx]]
            sem[f"on-{name}"] = best_on_color(ramp[STATUS_ROLES["solid"][idx]])
        sem["on-accent"] = best_on_color(sem["accent"])
        sem["on-ink"] = best_on_color(sem["ink"])
        sem["on-control"] = sem["text"]
        # Tooltip is an inverted chip. Its foreground is COMPUTED from its own
        # background rather than reusing `text-inverse`: in dark mode the tooltip
        # background is only slightly lighter than the page, so an inverted text
        # token lands near-black on near-black and the label disappears.
        sem["tooltip-bg"] = neutral[900 if idx == 0 else 200]
        sem["tooltip-text"] = best_on_color(sem["tooltip-bg"])
        # Focus ring is NOT simply `accent`. It must clear 3:1 against every
        # surface it can land on, including the recessed `bg-subtle` fill, which
        # is darker than the page. In dark mode accent-500 misses that floor.
        sem["focus-ring"] = accent[700 if idx == 0 else 400]
        sem["overlay"] = "rgb(0 0 0 / 0.32)" if mode == "light" else "rgb(0 0 0 / 0.56)"
        out[mode] = sem

    d = out["dimension"]
    for k, v in SPACE.items():
        d[f"space-{k}"] = f"{v}px"
    # Corner law: every radius derives from one base.
    d["radius-none"] = "0px"
    d["radius-sm"] = f"{max(0, round(base_r * 0.5))}px"
    d["radius-md"] = f"{base_r}px"
    d["radius-lg"] = f"{round(base_r * 1.5)}px"
    d["radius-xl"] = f"{round(base_r * 2)}px"
    d["radius-full"] = "9999px"
    for name, size, lh, ls in TYPE_SCALE:
        d[f"font-size-{name}"] = f"{size}px"
        d[f"line-height-{name}"] = f"{lh}px"
        d[f"letter-spacing-{name}"] = f"{ls}em"

    # Negative tracking at display sizes is a SANS-SERIF optical correction --
    # it closes the gaps that a grotesk opens up at 32px+. A serif already has
    # serifs doing that job, so inheriting the sans tracking sets it too tight.
    # The display slot therefore gets its own tracking, keyed to the preset.
    _serif_display = "serif" in brand["fonts"].get("display", "").lower() \
        and "sans-serif" not in brand["fonts"].get("display", "").lower()
    d["letter-spacing-display"] = "0em" if _serif_display else d["letter-spacing-2xl"]
    for k, v in heights.items():
        d[f"control-h-{k}"] = f"{v}px"
    for k, v in CONTROL_PAD_X[density].items():
        d[f"control-px-{k}"] = f"{v}px"
    d["row-h"] = f"{ROW_HEIGHT[density]}px"
    d["section-gap"] = f"{SECTION_GAP[density]}px"
    d["border-width"] = f"{VALID_BORDER_WEIGHT[brand['borderWeight']]}px"
    d["focus-ring-width"] = "2px"
    d["focus-ring-offset"] = "2px"
    # Check glyph as a mask. A path, not a colour -- the fill comes from
    # `on-ink` via the masked element's background, so it still follows tokens.
    d["check-glyph"] = (
        "url(\"data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' "
        "viewBox='0 0 24 24' fill='none' stroke='%23000' stroke-width='2.75' "
        "stroke-linecap='round' stroke-linejoin='round'%3E"
        "%3Cpath d='M4 12.5L9 17.5L20 6.5'/%3E%3C/svg%3E\")")
    # The indeterminate bar goes through the SAME mask pipeline as the tick, at
    # the same viewBox and stroke width. Drawing it as a plain div meant its
    # 2px height sat against the tick's effective 1.375px (2.75 scaled from a
    # 24 viewBox to 12px), so the minus read visibly heavier than the check.
    d["indeterminate-glyph"] = (
        "url(\"data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' "
        "viewBox='0 0 24 24' fill='none' stroke='%23000' stroke-width='2.75' "
        "stroke-linecap='round'%3E%3Cpath d='M6 12H18'/%3E%3C/svg%3E\")")
    d["chevron-glyph"] = (
        "url(\"data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' "
        "viewBox='0 0 24 24' fill='none' stroke='%23000' stroke-width='2' "
        "stroke-linecap='round' stroke-linejoin='round'%3E"
        "%3Cpath d='M6 9.5L12 15.5L18 9.5'/%3E%3C/svg%3E\")")
    d["icon-sm"] = "16px"
    d["icon-md"] = "20px"
    d["icon-lg"] = "24px"

    # SIZE -- component dimensions. Distinct from `space-*`, which is the gap
    # BETWEEN things; these are the extent OF things: a checkbox box, a switch
    # track, an avatar, a status dot. Without this family every new component
    # invents its own numbers, which is exactly how a system erodes.
    # Values below 12 are sub-component optical geometry (a check glyph inside a
    # 20px box), consistent with the 8pt grid / 4pt sub-step law.
    for v in (2, 4, 6, 8, 10, 12, 16, 20, 24, 28, 32, 36, 40, 44, 48,
              56, 64, 80, 96, 120):
        d[f"size-{v}"] = f"{v}px"
    # The one accessibility-mandated dimension, named so it cannot be forgotten.
    d["touch-target"] = "44px"

    # CONTAINER -- overlay and layout widths. Named semantically because these
    # are decisions ("a confirm dialog is 480") rather than a scale.
    for k, v in {
        "menu-min": 180, "menu-max": 320,
        "popover-min": 240, "popover-max": 360,
        "tooltip-max": 280,
        "toast-min": 320, "toast-max": 420,
        "modal-sm": 480, "modal-md": 640, "modal-lg": 800,
        "drawer-sm": 400, "drawer-md": 520, "drawer-lg": 640,
        "sidebar": 240 if density == "default" else 208,
        "sidebar-collapsed": 56,
        "field-label": 160,
        "search-max": 320,
        "search-wide": 480,   # centred app-bar search
        "page": 960,
    }.items():
        d[f"container-{k}"] = f"{v}px"

    # MEASURE -- line length in characters. Prose readability is a function of
    # character count, not pixels, so these are the one family in `ch`.
    d["measure-narrow"] = "40ch"
    d["measure-base"] = "65ch"
    d["measure-wide"] = "80ch"

    # Z -- stacking order. Gaps of 100 so a project can slot its own layers
    # between without renumbering the system.
    for k, v in {"base": "0", "sticky": "100", "overlay": "200",
                 "modal": "300", "toast": "400", "tooltip": "500"}.items():
        d[f"z-{k}"] = v
    d.update(MOTION)
    d.update(SHADOWS)

    out["meta"] = {
        "name": brand["name"],
        "accentHue": round(accent_hue, 2),
        "radius": brand["radius"],
        "density": density,
        "iconSet": brand["iconSet"],
        "fonts": brand["fonts"],
    }
    return out


def render_css(tokens, brand):
    p = brand["prefix"]
    f = brand["fonts"]
    L = []
    a = L.append
    a(f"/* {brand['name']} -- generated by build_tokens.py. Do not edit by hand. */")
    a(f"/* Regenerate: python build_tokens.py brand.json */\n")
    a(":root {")
    a("  /* --- typeface slots --- */")
    a(f"  --{p}-font-display: {f['display']};")
    a(f"  --{p}-font-text: {f['text']};")
    a(f"  --{p}-font-mono: {f['mono']};")
    a("\n  /* --- primitives --- */")
    for k, v in tokens["primitive"].items():
        a(f"  --{p}-{k}: {v};")
    a("\n  /* --- dimension, type, motion (density + corner law applied) --- */")
    for k, v in tokens["dimension"].items():
        a(f"  --{p}-{k}: {v};")
    a("\n  /* --- semantic roles: light --- */")
    for k, v in tokens["light"].items():
        a(f"  --{p}-{k}: {v};")
    a("}\n")
    a('[data-theme="dark"] {')
    for k, v in tokens["dark"].items():
        a(f"  --{p}-{k}: {v};")
    a("}\n")
    a("@media (prefers-color-scheme: dark) {")
    a('  :root:not([data-theme="light"]) {')
    for k, v in tokens["dark"].items():
        a(f"    --{p}-{k}: {v};")
    a("  }")
    a("}\n")
    a("/* Focus is a system-wide law, never restyled per component. */")
    a("/* No border-radius here: `outline` already follows the element's own")
    a("   corner radius. Setting `border-radius: inherit` would make a focused")
    a("   element adopt its PARENT's radius and square off its own corners. */")
    a("*:focus-visible {")
    a(f"  outline: var(--{p}-focus-ring-width) solid var(--{p}-focus-ring);")
    a(f"  outline-offset: var(--{p}-focus-ring-offset);")
    a("}\n")
    a("@media (prefers-reduced-motion: reduce) {")
    a("  *, *::before, *::after {")
    a(f"    animation-duration: var(--{p}-duration-reduced) !important;")
    a(f"    transition-duration: var(--{p}-duration-reduced) !important;")
    a("  }")
    a("}")
    return "\n".join(L) + "\n"


# ---------------------------------------------------------------------------
# Contrast audit
# ---------------------------------------------------------------------------

AUDIT_PAIRS = [
    ("text", "bg", 4.5), ("text", "surface", 4.5),
    ("text", "control", 4.5),        # label inside a field / neutral button
    ("text-muted", "bg", 4.5), ("text-muted", "surface", 4.5),
    ("text-muted", "control", 4.5),
    ("text-subtle", "bg", 3.0),
    ("on-accent", "accent", 4.5),
    ("on-ink", "ink", 4.5),          # primary button label
    ("tooltip-text", "tooltip-bg", 4.5),
    ("accent-text", "accent-subtle", 4.5),
    ("accent-text", "bg", 4.5),      # links on the page
    ("accent-text", "surface", 4.5),
    # House rule, no WCAG equivalent. Lowered twice as borders were deliberately
    # lightened (1.25 -> 1.18 -> 1.10). It should not go lower: the system has no
    # shadows, so a card's border against the page is the ONLY thing giving it an
    # edge. `border-strong` carries the 3:1 interactive requirement separately.
    ("border", "bg", 1.10),
    ("border", "surface", 1.10),
    # A divider has to stay visible on the surface it divides. In dark mode
    # `border-subtle` once resolved to the same step as `surface-raised`, making
    # dividers inside popovers disappear entirely.
    ("border-subtle", "surface", 1.04),
    ("border-subtle", "surface-raised", 1.04),
    ("border-strong", "bg", 3.0),    # WCAG 1.4.11, interactive control edges
    ("border-strong", "surface", 3.0),
    ("focus-ring", "bg", 3.0),
    ("focus-ring", "surface", 3.0),
    ("focus-ring", "control", 3.0),
    ("focus-ring", "surface-raised", 3.0),
    # An outline button is transparent, so its edge is its ONLY identifying
    # feature -- unlike an input, there is no fill to fall back on. It therefore
    # carries the full WCAG 1.4.11 3:1 boundary requirement and uses
    # `border-strong`, not `control-border` (which sits at ~1.3 in light mode).
    ("border-strong", "surface-raised", 3.0),
    ("border-strong", "accent-subtle", 3.0),
    # House rule, no WCAG equivalent. A ghost button's rest tint has to be
    # visible on every surface it can sit on. `control-subtle` previously
    # resolved to the same step as `bg`, making tinted ghost buttons literally
    # invisible on the page. These pairs make that class of collision a build
    # failure rather than something you notice in a screenshot.
    ("control-subtle", "bg", 1.03),
    ("control-subtle", "surface", 1.03),
    # surface-raised was the gap: control-subtle and surface-raised both
    # resolved to neutral-900 in dark mode, making every ghost/plain hover
    # inside a modal, popover, menu or drawer completely invisible.
    ("control-subtle", "surface-raised", 1.05),
    ("control", "surface-raised", 1.05),
    ("control-hover", "surface-raised", 1.10),
    # `surface-hover` is only valid on the page and on cards. It deliberately
    # is NOT audited against `surface-raised`: in dark mode it resolves to the
    # same step, which is exactly why overlay content must hover with
    # `control-subtle` instead. This pair locks its remaining valid use.
    ("surface-hover", "surface", 1.05),
    ("surface-hover", "bg", 1.03),
    ("control", "control-subtle", 1.03),
    ("danger-text", "danger-subtle", 4.5),
    ("on-danger", "danger-solid", 4.5),
    ("success-text", "success-subtle", 4.5),
    ("warning-text", "warning-subtle", 4.5),
    ("info-text", "info-subtle", 4.5),
]

# Borderless controls are identified by their FILL alone, so WCAG 1.4.11 asks
# that fill to clear 3:1 against whatever sits behind it. A fill that heavy is a
# mid-grey and reads nothing like a quiet input, so this is reported as an
# ADVISORY rather than a hard failure: it is a documented, deliberate deviation,
# not an oversight. Anything failing here means the field's boundary is carried
# by affordances other than contrast -- label, placeholder, hover and focus.
ADVISORY_PAIRS = [
    ("control", "surface", 3.0),
    ("control", "bg", 3.0),
    ("control", "surface-raised", 3.0),
]


def audit_collisions(tokens):
    """Flag any FILL that resolves to the same hex as a BACKDROP it can sit on.

    Four separate bugs in this system were this exact shape -- a fill landing on
    the same ramp step as its own background, so the element became invisible
    (`control-subtle`/`bg`, `control-subtle`/`surface-raised`,
    `surface-hover`/`surface-raised`, `surface-hover`/`bg`). Each was found by
    eye, one bug report at a time.

    Deliberately narrow: comparing every token against every other produces
    ~90 hits that are correct by design (all the `on-*` roles are white, and so
    on). Only fill-against-backdrop is a real defect, so only that is reported.
    """
    BACKDROPS = ["bg", "surface", "surface-raised"]

    def is_fill(name):
        return (name.startswith("control")
                or name in ("surface-hover", "surface-active")
                or name.endswith("-subtle")
                or name.endswith("-muted"))

    print()
    print("COLLISIONS -- fills sharing a hex with a backdrop they can sit on:")
    found = 0
    for mode in ("light", "dark"):
        sem = tokens[mode]
        for name, val in sorted(sem.items()):
            if not isinstance(val, str) or not val.startswith("#") or not is_fill(name):
                continue
            if name.endswith("-border"):
                continue
            for bd in BACKDROPS:
                if bd in sem and sem[bd].lower() == val.lower():
                    found += 1
                    print(f"  {mode:<6} {name:<18} == {bd:<16} {val}")
    if not found:
        print("  none -- every fill is separable from every backdrop.")
    else:
        print("  Each of these renders an element invisible on that backdrop.")
    return found


def audit(tokens):
    rows, failures = [], 0
    for mode in ("light", "dark"):
        sem = tokens[mode]
        for fg, bg, minimum in AUDIT_PAIRS:
            if fg not in sem or bg not in sem:
                continue
            ratio = contrast_ratio(sem[fg], sem[bg])
            ok = ratio >= minimum
            failures += not ok
            rows.append((mode, fg, bg, ratio, minimum, ok))
    return rows, failures


def print_audit(tokens):
    rows, failures = audit(tokens)
    print(f"{'MODE':<6} {'FOREGROUND':<16} {'ON':<16} {'RATIO':>7} {'MIN':>6}  ")
    print("-" * 62)
    for mode, fg, bg, ratio, minimum, ok in rows:
        print(f"{mode:<6} {fg:<16} {bg:<16} {ratio:>7.2f} {minimum:>6.1f}  "
              f"{'PASS' if ok else 'FAIL'}")
    print("-" * 62)
    print("All contrast requirements met." if not failures
          else f"{failures} pair(s) below the WCAG AA floor. Adjust `primary` in brand.json.")

    print()
    print("ADVISORY -- borderless control boundaries (WCAG 1.4.11, 3:1):")
    for mode in ("light", "dark"):
        sem = tokens[mode]
        for fg, bg, minimum in ADVISORY_PAIRS:
            if fg not in sem or bg not in sem:
                continue
            ratio = contrast_ratio(sem[fg], sem[bg])
            print(f"  {mode:<6} {fg:<16} on {bg:<16} {ratio:>5.2f}  "
                  f"{'ok' if ratio >= minimum else 'below 3:1 (deliberate)'}")
    print("  Fields carry their boundary via label, fill, hover and focus ring.")
    print("  To make this a hard pass, give inputs a `border-strong` edge.")
    audit_collisions(tokens)
    return failures


# ---------------------------------------------------------------------------


def main():
    ap = argparse.ArgumentParser(description="Generate design tokens from brand.json")
    ap.add_argument("brand", nargs="?", help="path to brand.json")
    ap.add_argument("--out-dir", default=".", help="where to write tokens.css / tokens.json")
    ap.add_argument("--check", action="store_true", help="run the contrast audit only")
    ap.add_argument("--defaults", action="store_true", help="print a starter brand.json")
    args = ap.parse_args()

    if args.defaults:
        print(json.dumps(DEFAULT_BRAND, indent=2))
        return 0
    if not args.brand:
        ap.error("brand.json path required (or use --defaults)")

    brand = load_brand(args.brand)
    tokens = build_tokens(brand)

    if args.check:
        return 1 if print_audit(tokens) else 0

    out = Path(args.out_dir)
    out.mkdir(parents=True, exist_ok=True)
    (out / "tokens.css").write_text(render_css(tokens, brand))
    (out / "tokens.json").write_text(json.dumps(tokens, indent=2) + "\n")
    print(f"Wrote {out / 'tokens.css'} and {out / 'tokens.json'}")
    print(f"  accent hue {tokens['meta']['accentHue']}deg | "
          f"radius {brand['radius']} | density {brand['density']} | icons {brand['iconSet']}")
    failures = print_audit(tokens)
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())
