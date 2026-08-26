#!/usr/bin/env python3
"""Emit `components.css` -- the installable component layer.

Until now the system described components in prose and Claude re-derived them
from that prose on every project, differently each time. This emits them as real
CSS so a project can *adopt* the system rather than have it re-interpreted.

Two properties make this the override layer for retrofits:

  1. Every value is a `var(--<prefix>-*)` reference, so the file is
     brand-agnostic. Swap `tokens.css` and the same stylesheet becomes a
     different brand. Only the class prefix is substituted here.
  2. It is emitted with `@layer` and high-specificity resets so it can be loaded
     *after* a project's existing CSS and win, which is what "override the old
     styling" requires.

Usage:
    python3 build_components_css.py brand.json --out-dir ./src/styles
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from build_tokens import load_brand  # noqa: E402


def sheet(p: str) -> str:
    """`p` is the token/class prefix, e.g. 'ds'."""
    return f"""/* {p}-components.css -- the component layer of the design system.
 *
 * Load AFTER tokens.css and AFTER any existing project CSS:
 *     <link rel="stylesheet" href="tokens.css">
 *     <link rel="stylesheet" href="legacy.css">
 *     <link rel="stylesheet" href="{p}-components.css">
 *
 * Every value here is a token reference, so this file is brand-agnostic --
 * swapping tokens.css changes the brand without touching this stylesheet.
 *
 * GENERATED FILE. Edit brand.json and re-run build_components_css.py.
 */

/* ---------------------------------------------------------------- reset ---
 * Scoped to system classes only, so it cannot damage un-migrated markup.
 */
[class*="{p}-"] {{ box-sizing: border-box; }}

/* Icons are ALWAYS sized.
 *
 * An inline `<svg>` carrying only a viewBox has no intrinsic size, so it falls
 * back to the replaced-element default of 300x150 -- an icon rendering at 300px
 * wide. Sizing icons per component covered the eleven that had a rule and left
 * menu items, combobox options, tree rows and empty states enormous.
 *
 * `:where()` contributes zero specificity and this rule comes first, so any
 * component that needs a different size (iconbtn at icon-md, dropzone at
 * icon-lg) still wins. `:not([class])` leaves classed SVGs alone -- the spinner
 * and the sparkline size themselves.
 */
:where([class*="{p}-"]) {{
  scrollbar-width: thin;
  scrollbar-color: var(--{p}-control-active) transparent;
}}
:where([class*="{p}-"]) svg:not([class]) {{
  width: var(--{p}-icon-sm);
  height: var(--{p}-icon-sm);
  flex: none;
}}

/* Focus is a system-wide law, never restyled per component.
 * No border-radius here: `outline` already follows the element's own corners.
 * `border-radius: inherit` would make a focused element adopt its PARENT's
 * radius and square off its own. */
[class*="{p}-"]:focus-visible {{
  outline: var(--{p}-focus-ring-width) solid var(--{p}-focus-ring);
  outline-offset: var(--{p}-focus-ring-offset);
}}

/* Universal disabled treatment: opacity, never a lighter colour token, so one
 * rule covers every component. */
.{p}-btn[disabled], .{p}-btn[aria-disabled="true"],
.{p}-input[disabled], .{p}-select[disabled],
.{p}-chip[aria-disabled="true"] {{
  opacity: .5;
  cursor: not-allowed;
}}

/* --------------------------------------------------------------- button ---
 * Two sizes (M default, S). Three priorities x three colours. Nothing else.
 * Hover changes BACKGROUND ONLY -- never border, text, size or position.
 */
.{p}-btn {{
  height: var(--{p}-control-h-md);
  padding: 0 var(--{p}-control-px-md);
  border-radius: var(--{p}-radius-md);
  font: 500 var(--{p}-font-size-sm)/1 var(--{p}-font-text);
  border: var(--{p}-border-width) solid transparent;
  background: transparent;
  color: var(--{p}-text);
  display: inline-flex;
  align-items: center;
  justify-content: center;
  text-align: center;
  gap: var(--{p}-space-2);
  min-width: var(--{p}-size-64);
  cursor: pointer;
  text-decoration: none;
  transition: background var(--{p}-duration-fast) var(--{p}-ease-standard);
}}
.{p}-btn--s {{
  height: var(--{p}-control-h-sm);
  padding: 0 var(--{p}-control-px-sm);
  gap: var(--{p}-space-1);
  min-width: var(--{p}-size-56);
}}
.{p}-btn > svg {{ width: var(--{p}-icon-sm); height: var(--{p}-icon-sm); flex: none; }}

/* filled -- the committed state. Neutral is INK, not accent: the brand hue is
 * reserved for links, selection, focus and status. */
.{p}-btn--filled.{p}-btn--neutral {{ background: var(--{p}-ink); color: var(--{p}-on-ink); }}
.{p}-btn--filled.{p}-btn--neutral:hover:not([disabled]) {{ background: var(--{p}-ink-hover); }}
.{p}-btn--filled.{p}-btn--neutral:active:not([disabled]) {{ background: var(--{p}-ink-active); }}
.{p}-btn--filled.{p}-btn--primary {{ background: var(--{p}-accent); color: var(--{p}-on-accent); }}
.{p}-btn--filled.{p}-btn--primary:hover:not([disabled]) {{ background: var(--{p}-accent-hover); }}
.{p}-btn--filled.{p}-btn--destructive {{ background: var(--{p}-danger-solid); color: var(--{p}-on-danger); }}
.{p}-btn--filled.{p}-btn--destructive:hover:not([disabled]) {{ background: var(--{p}-danger-text); }}

/* outline -- transparent, so the EDGE is the only thing identifying it as a
 * control. That means it carries the full 3:1 boundary requirement and uses
 * border-strong, not control-border (~1.3:1 in light mode). */
.{p}-btn--outline.{p}-btn--neutral {{ border-color: var(--{p}-border-strong); color: var(--{p}-text); }}
.{p}-btn--outline.{p}-btn--neutral:hover:not([disabled]) {{ background: var(--{p}-control-subtle); }}
.{p}-btn--outline.{p}-btn--primary {{ border-color: var(--{p}-accent-border); color: var(--{p}-accent-text); }}
.{p}-btn--outline.{p}-btn--primary:hover:not([disabled]) {{ background: var(--{p}-accent-subtle); }}
.{p}-btn--outline.{p}-btn--destructive {{ border-color: var(--{p}-danger-border); color: var(--{p}-danger-text); }}
.{p}-btn--outline.{p}-btn--destructive:hover:not([disabled]) {{ background: var(--{p}-danger-subtle); }}

/* ghost -- tinted at rest, never fully transparent. Rest and hover are one step
 * apart on the same ramp so the tint deepens rather than appearing. */
.{p}-btn--ghost.{p}-btn--neutral {{ background: var(--{p}-control-subtle); color: var(--{p}-text); }}
.{p}-btn--ghost.{p}-btn--neutral:hover:not([disabled]) {{ background: var(--{p}-control); }}
.{p}-btn--ghost.{p}-btn--primary {{ background: var(--{p}-accent-subtle); color: var(--{p}-accent-text); }}
.{p}-btn--ghost.{p}-btn--primary:hover:not([disabled]) {{ background: var(--{p}-accent-muted); }}
.{p}-btn--ghost.{p}-btn--destructive {{ background: var(--{p}-danger-subtle); color: var(--{p}-danger-text); }}
.{p}-btn--ghost.{p}-btn--destructive:hover:not([disabled]) {{ background: var(--{p}-danger-muted); }}

/* Square but LABELLED -- a pagination number, a calendar day. Not an Icon
 * Button: it has visible text, so it needs no aria-label, and it is a legal
 * home for `plain` because it is a compact control inside a group. */
.{p}-btn--square {{
  width: var(--{p}-control-h-md);
  min-width: 0;
  padding: 0;
  gap: 0;
}}
.{p}-btn--square.{p}-btn--s {{ width: var(--{p}-control-h-sm); }}

/* ---------------------------------------------------------- icon button ---
 * Square. Adds a fourth priority, `plain` -- no background at all -- for
 * repeated controls (table rows, toolbars) where a tint per instance stacks
 * into visual noise. aria-label and a tooltip are mandatory.
 */
.{p}-iconbtn {{
  width: var(--{p}-control-h-md);
  height: var(--{p}-control-h-md);
  min-width: 0;
  padding: 0;
  gap: 0;
}}
.{p}-iconbtn > svg {{ width: var(--{p}-icon-md); height: var(--{p}-icon-md); }}
.{p}-iconbtn.{p}-btn--s {{ width: var(--{p}-control-h-sm); height: var(--{p}-control-h-sm); }}
.{p}-iconbtn.{p}-btn--s > svg {{ width: var(--{p}-icon-sm); height: var(--{p}-icon-sm); }}
.{p}-btn--plain.{p}-btn--neutral {{ background: transparent; color: var(--{p}-text); }}
.{p}-btn--plain.{p}-btn--neutral:hover:not([disabled]) {{ background: var(--{p}-control-subtle); }}
.{p}-btn--plain.{p}-btn--primary {{ background: transparent; color: var(--{p}-accent-text); }}
.{p}-btn--plain.{p}-btn--primary:hover:not([disabled]) {{ background: var(--{p}-accent-subtle); }}
.{p}-btn--plain.{p}-btn--destructive {{ background: transparent; color: var(--{p}-danger-text); }}
.{p}-btn--plain.{p}-btn--destructive:hover:not([disabled]) {{ background: var(--{p}-danger-subtle); }}

/* ----------------------------------------------------------------- link --- */
.{p}-link {{ color: var(--{p}-accent-text); text-decoration: none; }}
.{p}-link:hover {{ text-decoration: underline; }}

/* ---------------------------------------------------------------- field ---
 * Borderless and recessed: `control` fill, no edge at rest. Invalid is the one
 * exception -- an error must be locatable without reading.
 */
.{p}-field {{ display: block; }}
.{p}-label {{
  display: block;
  font-size: var(--{p}-font-size-sm);
  font-weight: 500;
  color: var(--{p}-text);
  margin-bottom: var(--{p}-space-1);
}}
.{p}-label-optional {{ color: var(--{p}-text-subtle); font-weight: 400; }}
.{p}-input, .{p}-select, .{p}-textarea {{
  width: 100%;
  height: var(--{p}-control-h-md);
  padding: 0 var(--{p}-control-px-sm);
  border: var(--{p}-border-width) solid transparent;
  border-radius: var(--{p}-radius-md);
  background: var(--{p}-control);
  color: var(--{p}-text);
  font: 400 var(--{p}-font-size-base)/1 var(--{p}-font-text);
  transition: background var(--{p}-duration-fast) var(--{p}-ease-standard);
}}
/* The native select arrow is drawn by the browser at a position we do not
 * control -- it sat hard against the right edge regardless of padding. So the
 * arrow is suppressed and the system draws its own, inset by the field's own
 * horizontal padding like every other trailing affordance. The glyph is a mask
 * so it takes its colour from a token and follows the theme. */
.{p}-select {{
  appearance: none;
  -webkit-appearance: none;
  padding-right: calc(var(--{p}-control-px-sm) * 2 + var(--{p}-icon-sm));
}}
.{p}-select-wrap {{ position: relative; display: block; }}
.{p}-select-wrap::after {{
  content: "";
  position: absolute;
  right: var(--{p}-control-px-sm);
  top: 50%;
  width: var(--{p}-icon-sm);
  height: var(--{p}-icon-sm);
  margin-top: calc(var(--{p}-icon-sm) / -2);
  pointer-events: none;
  background-color: var(--{p}-text-muted);
  -webkit-mask: var(--{p}-chevron-glyph) center / var(--{p}-icon-sm) no-repeat;
  mask: var(--{p}-chevron-glyph) center / var(--{p}-icon-sm) no-repeat;
}}

.{p}-textarea {{
  height: auto;
  min-height: var(--{p}-size-80);
  padding: var(--{p}-space-3);
  line-height: var(--{p}-line-height-base);
  resize: vertical;
}}
.{p}-input:hover:not([disabled]), .{p}-select:hover:not([disabled]) {{
  background: var(--{p}-control-hover);
}}
.{p}-input::placeholder, .{p}-textarea::placeholder {{ color: var(--{p}-text-subtle); }}
.{p}-input[aria-invalid="true"], .{p}-select[aria-invalid="true"],
.{p}-textarea[aria-invalid="true"] {{ border-color: var(--{p}-danger-border); }}
.{p}-input[readonly] {{ background: var(--{p}-surface); }}
/* Helper line is always reserved, so an error does not shift the form down. */
.{p}-help {{
  display: block;
  min-height: var(--{p}-size-16);
  margin-top: var(--{p}-space-1);
  font-size: var(--{p}-font-size-2xs);
  color: var(--{p}-text-muted);
}}
.{p}-help--error {{ color: var(--{p}-danger-text); }}

/* ------------------------------------------------------- choice controls ---
 * Checked fill is INK, matching the primary button: both are "the committed
 * state". The selected ROW behind a checkbox is still accent-subtle.
 */
.{p}-check, .{p}-radio {{
  appearance: none;
  /* `position: relative` + an absolutely positioned glyph keeps the mark OUT
   * of layout. As `inline-grid` with a centred child, the box's baseline
   * changed the moment `::after` appeared, so the whole control dropped a
   * pixel or two when checked -- visible in any inline context, e.g. a table
   * cell. `vertical-align: middle` removes the baseline dependency entirely. */
  position: relative;
  display: inline-block;
  vertical-align: middle;
  width: var(--{p}-size-20); height: var(--{p}-size-20);
  flex: none;
  margin: 0;
  border: var(--{p}-border-width) solid var(--{p}-border-strong);
  background: var(--{p}-surface);
  cursor: pointer;
}}
.{p}-check {{ border-radius: var(--{p}-radius-sm); }}
.{p}-radio {{ border-radius: var(--{p}-radius-full); }}
.{p}-check:checked, .{p}-radio:checked {{
  background: var(--{p}-ink);
  border-color: var(--{p}-ink);
}}
/* The mark is a MASK, not two rotated borders.
 *
 * The border trick needs `transform: rotate() translate()`, and because
 * transform functions compose left-to-right the translate runs in the rotated
 * frame -- it nudges the glyph diagonally, not vertically, which is why the
 * tick sat off-centre. Fixing it with a hand-tuned offset only works at one
 * size and one stroke weight.
 *
 * The mask path is centred BY CONSTRUCTION: vertices (4,12.5) (9,17.5)
 * (20,6.5) give a bounding box of x 4..20 and y 6.5..17.5, both centred on 12
 * in a 24 viewBox, and a symmetric round stroke extends it evenly. So `center`
 * is genuinely centre at any size, and the colour comes from the mask's own
 * background so it still follows the token. */
.{p}-check:checked::after {{
  content: "";
  position: absolute;
  inset: 0;
  background-color: var(--{p}-on-ink);
  -webkit-mask: var(--{p}-check-glyph) center / var(--{p}-size-12) no-repeat;
  mask: var(--{p}-check-glyph) center / var(--{p}-size-12) no-repeat;
}}
/* Indeterminate is a centred bar, same mechanism. */
.{p}-check:indeterminate {{
  background: var(--{p}-ink);
  border-color: var(--{p}-ink);
}}
.{p}-check:indeterminate::after {{
  content: "";
  position: absolute;
  inset: 0;
  background-color: var(--{p}-on-ink);
  -webkit-mask: var(--{p}-indeterminate-glyph) center / var(--{p}-size-12) no-repeat;
  mask: var(--{p}-indeterminate-glyph) center / var(--{p}-size-12) no-repeat;
}}
.{p}-radio:checked::after {{
  content: "";
  position: absolute;
  top: 50%;
  left: 50%;
  width: var(--{p}-size-8);
  height: var(--{p}-size-8);
  transform: translate(-50%, -50%);
  border-radius: var(--{p}-radius-full);
  background: var(--{p}-on-ink);
}}
/* Hit area is the whole label row, never just the box. */
.{p}-choice {{
  display: flex;
  align-items: center;
  gap: var(--{p}-space-2);
  min-height: var(--{p}-control-h-sm);
  font-size: var(--{p}-font-size-sm);
  cursor: pointer;
}}
.{p}-switch {{
  appearance: none;
  position: relative;
  width: var(--{p}-size-36); height: var(--{p}-size-20);
  flex: none;
  border-radius: var(--{p}-radius-full);
  background: var(--{p}-control-active);
  cursor: pointer;
  transition: background var(--{p}-duration-fast) var(--{p}-ease-standard);
}}
.{p}-switch::after {{
  content: "";
  position: absolute; top: var(--{p}-size-2); left: var(--{p}-size-2);
  width: var(--{p}-size-16); height: var(--{p}-size-16);
  border-radius: var(--{p}-radius-full);
  background: var(--{p}-surface);
  transition: transform var(--{p}-duration-fast) var(--{p}-ease-standard);
}}
.{p}-switch:checked {{ background: var(--{p}-ink); }}
.{p}-switch:checked::after {{ transform: translateX(var(--{p}-size-16)); }}

/* ----------------------------------------------------------------- card ---
 * Border, never a shadow. Shadows on cards are the single most reliable
 * generated-UI tell.
 */
.{p}-card {{
  background: var(--{p}-surface);
  border: var(--{p}-border-width) solid var(--{p}-border);
  border-radius: var(--{p}-radius-md);
  padding: var(--{p}-space-4);
  box-shadow: none;
}}
.{p}-card--interactive {{ cursor: pointer; transition: background var(--{p}-duration-fast) var(--{p}-ease-standard); }}
.{p}-card--interactive:hover {{ background: var(--{p}-surface-hover); }}
.{p}-card-title {{
  margin: 0;
  font-family: var(--{p}-font-display);
  font-size: var(--{p}-font-size-lg);
  font-weight: 600;
}}
.{p}-card-subtitle {{
  font-size: var(--{p}-font-size-sm);
  color: var(--{p}-text-muted);
  margin: var(--{p}-space-1) 0 0;
}}

/* ---------------------------------------------------- badge / tag / chip ---
 * Badge is a LABEL: fill only, no edge -- its container frames it.
 * Chip is a CONTROL: fill plus edge -- it floats free on the page.
 * Both are pills at every corner preset.
 */
.{p}-badge {{
  display: inline-flex;
  align-items: center;
  gap: var(--{p}-space-1);
  height: var(--{p}-size-20);
  padding: 0 var(--{p}-space-2);
  border-radius: var(--{p}-radius-full);
  border: none;
  background: var(--{p}-control);
  color: var(--{p}-text-muted);
  font-size: var(--{p}-font-size-2xs);
  font-weight: 500;
  white-space: nowrap;
}}
.{p}-badge--success {{ background: var(--{p}-success-subtle); color: var(--{p}-success-text); }}
.{p}-badge--warning {{ background: var(--{p}-warning-subtle); color: var(--{p}-warning-text); }}
.{p}-badge--danger  {{ background: var(--{p}-danger-subtle);  color: var(--{p}-danger-text); }}
.{p}-badge--info    {{ background: var(--{p}-info-subtle);    color: var(--{p}-info-text); }}

.{p}-chip {{
  display: inline-flex;
  align-items: center;
  gap: var(--{p}-space-1);
  height: var(--{p}-control-h-sm);
  padding: 0 var(--{p}-space-3);
  border-radius: var(--{p}-radius-full);
  border: var(--{p}-border-width) solid var(--{p}-control-border);
  background: var(--{p}-control);
  color: var(--{p}-text);
  font-size: var(--{p}-font-size-sm);
  line-height: 1;
  white-space: nowrap;
  flex: none;
  cursor: pointer;
}}
.{p}-chip:hover {{ background: var(--{p}-control-hover); }}
.{p}-chip[aria-pressed="true"], .{p}-chip--selected {{
  background: var(--{p}-accent-subtle);
  border-color: var(--{p}-accent-border);
  color: var(--{p}-accent-text);
  font-weight: 500;
}}

/* ---------------------------------------------------------------- alert ---
 * Fill only, no border. Colour is always paired with an icon and a status word.
 * Body text stays `text` -- tinting the paragraph shouts and hurts reading.
 */
.{p}-alert {{
  display: flex;
  gap: var(--{p}-space-2);
  padding: var(--{p}-space-3) var(--{p}-space-4);
  border-radius: var(--{p}-radius-md);
  border: none;
  background: var(--{p}-info-subtle);
}}
.{p}-alert > svg {{ width: var(--{p}-icon-sm); height: var(--{p}-icon-sm); flex: none; }}
.{p}-alert-title {{ display: block; font-size: var(--{p}-font-size-sm); font-weight: 600; }}
.{p}-alert-body {{ margin: var(--{p}-space-1) 0 0; font-size: var(--{p}-font-size-sm); color: var(--{p}-text); }}
.{p}-alert--success {{ background: var(--{p}-success-subtle); }}
.{p}-alert--success .{p}-alert-title, .{p}-alert--success > svg {{ color: var(--{p}-success-text); }}
.{p}-alert--warning {{ background: var(--{p}-warning-subtle); }}
.{p}-alert--warning .{p}-alert-title, .{p}-alert--warning > svg {{ color: var(--{p}-warning-text); }}
.{p}-alert--danger {{ background: var(--{p}-danger-subtle); }}
.{p}-alert--danger .{p}-alert-title, .{p}-alert--danger > svg {{ color: var(--{p}-danger-text); }}
.{p}-alert--info .{p}-alert-title, .{p}-alert--info > svg {{ color: var(--{p}-info-text); }}

/* ---------------------------------------------------------------- table ---
 * Flush and borderless. Rules do the work, full-bleed rather than inset,
 * because a table is a grid and an inset rule breaks column alignment.
 */
.{p}-table {{
  width: 100%;
  border-collapse: collapse;
  font-size: var(--{p}-font-size-sm);
}}
.{p}-table th {{
  height: var(--{p}-control-h-sm);
  padding: 0 var(--{p}-space-3);
  text-align: left;
  background: transparent;
  font-size: var(--{p}-font-size-2xs);
  font-weight: 500;
  color: var(--{p}-text-muted);
  border-bottom: var(--{p}-border-width) solid var(--{p}-border);
}}
.{p}-table td {{
  height: var(--{p}-row-h);
  padding: 0 var(--{p}-space-3);
  border-bottom: var(--{p}-border-width) solid var(--{p}-border-subtle);
}}
.{p}-table tbody tr:last-child td {{ border-bottom: none; }}
.{p}-table tbody tr:hover {{ background: var(--{p}-surface-hover); }}
.{p}-table tr[aria-selected="true"] {{ background: var(--{p}-accent-subtle); }}
/* Numeric columns.
 *
 * Alignment belongs to the whole column; tabular mono belongs only to the
 * DIGITS. A header cell contains a word, so mono does nothing for it except
 * break font consistency with every other header in the table. Scoping the
 * font to `td` is the fix -- `.{p}-num` on a `th` gives alignment alone.
 */
.{p}-num {{ text-align: right; }}
td.{p}-num, .{p}-table td.{p}-num {{
  font-family: var(--{p}-font-mono);
  font-variant-numeric: tabular-nums;
}}

/* -------------------------------------------------- tabs / segmented ------
 * Underline for VIEWS (pages of content). Segmented for FILTERS (lenses on the
 * same content). The choice is semantic, not decorative.
 */
.{p}-tabs {{
  display: flex;
  gap: 0;
  border-bottom: var(--{p}-border-width) solid var(--{p}-border);
}}
.{p}-tab {{
  height: var(--{p}-control-h-md);
  padding: 0 var(--{p}-control-px-md);
  border: none;
  background: none;
  font-size: var(--{p}-font-size-sm);
  font-weight: 500;
  color: var(--{p}-text-muted);
  cursor: pointer;
  position: relative;
}}
.{p}-tab[aria-selected="true"] {{ color: var(--{p}-text); }}
.{p}-tab[aria-selected="true"]::after {{
  content: "";
  position: absolute;
  left: 0; right: 0; bottom: calc(var(--{p}-border-width) * -1);
  height: var(--{p}-size-2);
  background: var(--{p}-accent);
}}
.{p}-segmented {{
  display: inline-flex;
  gap: var(--{p}-size-2);
  padding: var(--{p}-space-1);
  border-radius: var(--{p}-radius-md);
  background: var(--{p}-control);
}}
.{p}-segmented > button {{
  height: var(--{p}-control-h-sm);
  padding: 0 var(--{p}-control-px-sm);
  border: none;
  border-radius: var(--{p}-radius-sm);
  background: transparent;
  font-size: var(--{p}-font-size-sm);
  font-weight: 500;
  color: var(--{p}-text-muted);
  cursor: pointer;
}}
.{p}-segmented > button[aria-selected="true"] {{
  background: var(--{p}-surface);
  color: var(--{p}-text);
}}

/* ------------------------------------------------------ menu / overlays ---
 * Content inside a raised overlay hovers with `control-subtle`, NOT
 * `surface-hover` -- the latter equals surface-raised in dark mode, so the
 * hover would be invisible.
 */
.{p}-menu {{
  min-width: var(--{p}-container-menu-min);
  max-width: var(--{p}-container-menu-max);
  padding: var(--{p}-space-1);
  border: var(--{p}-border-width) solid var(--{p}-border);
  border-radius: var(--{p}-radius-md);
  background: var(--{p}-surface-raised);
  box-shadow: var(--{p}-shadow-sm);
}}
.{p}-menu-item {{
  display: flex;
  align-items: center;
  gap: var(--{p}-space-2);
  height: var(--{p}-control-h-sm);
  padding: 0 var(--{p}-control-px-sm);
  border-radius: var(--{p}-radius-sm);
  font-size: var(--{p}-font-size-sm);
  color: var(--{p}-text);
  cursor: pointer;
}}
.{p}-menu-item:hover {{ background: var(--{p}-control-subtle); }}
.{p}-menu-item[aria-checked="true"] {{
  background: var(--{p}-accent-subtle);
  color: var(--{p}-accent-text);
}}
.{p}-menu-item--danger {{ color: var(--{p}-danger-text); }}
.{p}-menu-sep {{
  height: var(--{p}-border-width);
  margin: var(--{p}-space-1);
  background: var(--{p}-border-subtle);
  border: none;
}}

.{p}-popover {{
  min-width: var(--{p}-container-popover-min);
  max-width: var(--{p}-container-popover-max);
  padding: var(--{p}-space-4);
  border: var(--{p}-border-width) solid var(--{p}-border);
  border-radius: var(--{p}-radius-md);
  background: var(--{p}-surface-raised);
  box-shadow: var(--{p}-shadow-sm);
}}

/* Tooltip computes its own foreground: `text-inverse` inverts the wrong way in
 * dark mode and the label lands near-black on near-black. */
.{p}-tooltip {{
  max-width: var(--{p}-container-tooltip-max);
  padding: var(--{p}-space-1) var(--{p}-space-2);
  border-radius: var(--{p}-radius-sm);
  background: var(--{p}-tooltip-bg);
  color: var(--{p}-tooltip-text);
  font-size: var(--{p}-font-size-2xs);
  box-shadow: var(--{p}-shadow-sm);
}}

.{p}-modal {{
  max-width: var(--{p}-container-modal-sm);
  padding: var(--{p}-space-6);
  border: var(--{p}-border-width) solid var(--{p}-border);
  border-radius: var(--{p}-radius-lg);
  background: var(--{p}-surface-raised);
  box-shadow: var(--{p}-shadow-md);
}}
.{p}-modal--form {{ max-width: var(--{p}-container-modal-md); }}
.{p}-modal--wide {{ max-width: var(--{p}-container-modal-lg); }}
/* No blur: the backdrop is a flat scrim. */
.{p}-backdrop {{ background: var(--{p}-overlay); backdrop-filter: none; }}

.{p}-toast {{
  min-width: var(--{p}-container-toast-min);
  max-width: var(--{p}-container-toast-max);
  padding: var(--{p}-space-3) var(--{p}-space-4);
  border-radius: var(--{p}-radius-md);
  background: var(--{p}-surface-raised);
  border: var(--{p}-border-width) solid var(--{p}-border);
  box-shadow: var(--{p}-shadow-md);
  font-size: var(--{p}-font-size-sm);
}}

/* -------------------------------------------------------------- avatar ---
 * Circles for people, radius-sm squares for organisations. Fallbacks are
 * neutral -- never a colour hashed from the name.
 */
.{p}-avatar {{
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: var(--{p}-size-32); height: var(--{p}-size-32);
  flex: none;
  border-radius: var(--{p}-radius-full);
  background: var(--{p}-control);
  color: var(--{p}-text-muted);
  font-size: var(--{p}-font-size-2xs);
  font-weight: 500;
  overflow: hidden;
}}
.{p}-avatar > img {{ width: 100%; height: 100%; object-fit: cover; }}
.{p}-avatar--org {{ border-radius: var(--{p}-radius-sm); }}
.{p}-avatar--xs {{ width: var(--{p}-size-20); height: var(--{p}-size-20); }}
.{p}-avatar--sm {{ width: var(--{p}-size-24); height: var(--{p}-size-24); }}
.{p}-avatar--lg {{ width: var(--{p}-size-40); height: var(--{p}-size-40); }}

/* ------------------------------------------------------------ accordion ---
 * Header is a fixed-height flex row with NO margin: an inherited margin-bottom
 * opens dead space under every row in the list.
 */
.{p}-accordion {{
  border: var(--{p}-border-width) solid var(--{p}-border);
  border-radius: var(--{p}-radius-md);
  background: var(--{p}-surface);
  overflow: hidden;
}}
.{p}-accordion-item + .{p}-accordion-item {{
  border-top: var(--{p}-border-width) solid var(--{p}-border-subtle);
}}
.{p}-accordion-header {{
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: var(--{p}-space-3);
  width: 100%;
  height: var(--{p}-control-h-md);
  margin: 0;
  padding: 0 var(--{p}-space-4);
  border: none;
  background: none;
  font-size: var(--{p}-font-size-sm);
  font-weight: 500;
  color: var(--{p}-text);
  text-align: left;
  cursor: pointer;
}}
.{p}-accordion-header:hover {{ background: var(--{p}-control-subtle); }}
.{p}-accordion-header > svg {{
  width: var(--{p}-icon-sm); height: var(--{p}-icon-sm);
  flex: none;
  color: var(--{p}-text-subtle);
  transition: transform var(--{p}-duration-fast) var(--{p}-ease-standard);
}}
.{p}-accordion-header[aria-expanded="true"] > svg {{ transform: rotate(90deg); }}
.{p}-accordion-panel {{
  /* The spec assumed the header's bottom padding supplied this gap, but the
   * header is a fixed-height flex row and has none -- so the panel opened
   * flush against the label. */
  padding: var(--{p}-space-2) var(--{p}-space-4) var(--{p}-space-4);
  font-size: var(--{p}-font-size-sm);
  color: var(--{p}-text-muted);
}}

/* ------------------------------------------------- progress / skeleton ---
 * `width` is the one property in the system allowed to animate, because a
 * progress bar IS a width.
 */
.{p}-progress {{
  height: var(--{p}-size-4);
  border-radius: var(--{p}-radius-full);
  background: var(--{p}-control);
  overflow: hidden;
}}
.{p}-progress > * {{
  display: block;
  height: 100%;
  border-radius: var(--{p}-radius-full);
  background: var(--{p}-ink);
  transition: width var(--{p}-duration-base) var(--{p}-ease-standard);
}}
.{p}-skeleton {{
  background: var(--{p}-control);
  border-radius: var(--{p}-radius-sm);
  height: var(--{p}-line-height-sm);
}}
@media (prefers-reduced-motion: reduce) {{
  .{p}-skeleton {{ animation: none; }}
  [class*="{p}-"] {{ transition-duration: var(--{p}-duration-reduced) !important; }}
}}

/* -------------------------------------------------------------- layout ---
 * A divider is the weakest separator in the system. border-subtle, never
 * border -- a divider that draws attention has failed at its job.
 */
.{p}-divider {{
  height: var(--{p}-border-width);
  margin: var(--{p}-space-4) 0;
  background: var(--{p}-border-subtle);
  border: none;
}}
.{p}-stack {{ display: flex; flex-direction: column; gap: var(--{p}-space-4); }}
.{p}-row {{ display: flex; align-items: center; gap: var(--{p}-space-2); }}
.{p}-empty {{
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  min-height: var(--{p}-size-120);
  text-align: center;
}}
.{p}-empty > svg {{
  width: var(--{p}-icon-lg);
  height: var(--{p}-icon-lg);
  color: var(--{p}-text-subtle);
}}
.{p}-empty-title {{ font-size: var(--{p}-font-size-lg); font-weight: 600; margin: var(--{p}-space-4) 0 0; }}
.{p}-empty-body {{
  max-width: var(--{p}-measure-narrow);
  margin: var(--{p}-space-1) 0 var(--{p}-space-4);
  font-size: var(--{p}-font-size-sm);
  color: var(--{p}-text-muted);
}}


/* ================================================================ */
/* NAVIGATION                                                        */
/* ================================================================ */

/* ---------------------------------------------------------- app bar ---
 * Shares the page fill, separated by a border alone. Never raised, never a
 * shadow, and the border does not animate in on scroll -- one that is present
 * at rest has nothing to announce.
 */
.{p}-appbar {{
  display: flex;
  align-items: center;
  gap: var(--{p}-space-2);
  height: var(--{p}-size-56);
  padding: 0 var(--{p}-space-4);
  background: var(--{p}-bg);
  border-bottom: var(--{p}-border-width) solid var(--{p}-border);
  box-shadow: none;
  position: sticky;
  top: 0;
  z-index: var(--{p}-z-sticky);
}}
.{p}-appbar-brand {{
  display: flex;
  align-items: center;
  max-height: var(--{p}-size-24);
  font-size: var(--{p}-font-size-sm);
  font-weight: 600;
  letter-spacing: var(--{p}-letter-spacing-sm);
}}
.{p}-appbar-spacer {{ flex: 1; }}
.{p}-appbar-search {{ max-width: var(--{p}-container-search-wide); flex: 1; }}

/* ---------------------------------------------------------- sidebar ---
 * Items sit 2px apart, not 8: a nav list is one object, and generous gaps make
 * it read as a stack of separate buttons. Nested items indent by exactly one
 * icon column so labels align with their parent's LABEL, not its icon.
 */
.{p}-sidebar {{
  width: var(--{p}-container-sidebar);
  padding: var(--{p}-space-2);
  background: var(--{p}-bg);
  border-right: var(--{p}-border-width) solid var(--{p}-border);
  box-shadow: none;
  flex: none;
}}
.{p}-sidebar--collapsed {{ width: var(--{p}-container-sidebar-collapsed); }}
.{p}-navlist {{
  display: flex;
  flex-direction: column;
  gap: var(--{p}-size-2);
  list-style: none;
  margin: 0;
  padding: 0;
}}
.{p}-navitem {{
  display: flex;
  align-items: center;
  gap: var(--{p}-space-2);
  height: var(--{p}-control-h-sm);
  padding: 0 var(--{p}-control-px-sm);
  border-radius: var(--{p}-radius-sm);
  font-size: var(--{p}-font-size-sm);
  color: var(--{p}-text-muted);
  text-decoration: none;
  cursor: pointer;
}}
.{p}-navitem > svg {{
  width: var(--{p}-icon-sm);
  height: var(--{p}-icon-sm);
  flex: none;
}}
.{p}-navitem:hover {{ background: var(--{p}-control-subtle); }}
/* Active is the system's selection language -- identical to a selected table
   row and a checked menu item. Never a left accent bar, never a filled pill. */
.{p}-navitem[aria-current] {{
  background: var(--{p}-accent-subtle);
  color: var(--{p}-accent-text);
  font-weight: 500;
}}
.{p}-navitem--nested {{ padding-left: calc(var(--{p}-control-px-sm) + var(--{p}-size-20)); }}
.{p}-navsection {{
  padding: 0 var(--{p}-control-px-sm);
  margin-top: var(--{p}-space-4);
  margin-bottom: var(--{p}-space-1);
  font-size: var(--{p}-font-size-2xs);
  font-weight: 500;
  color: var(--{p}-text-subtle);
  text-transform: uppercase;
  letter-spacing: var(--{p}-letter-spacing-2xs);
}}

/* ------------------------------------------------------- breadcrumb ---
 * Reflects HIERARCHY, not history. The current page is present but not a link:
 * linking a page to itself is a dead control.
 */
.{p}-breadcrumb {{
  display: flex;
  align-items: center;
  gap: var(--{p}-space-1);
  height: var(--{p}-control-h-sm);
  font-size: var(--{p}-font-size-sm);
}}
.{p}-breadcrumb a, .{p}-breadcrumb span {{
  display: inline-flex;
  align-items: center;
  white-space: nowrap;
}}
.{p}-breadcrumb a {{ color: var(--{p}-text-muted); text-decoration: none; }}
.{p}-breadcrumb a:hover {{ color: var(--{p}-text); text-decoration: underline; }}
.{p}-breadcrumb [aria-current] {{ color: var(--{p}-text); font-weight: 500; }}
/* The chevron is the system's separator glyph -- never "/" or "|". */
.{p}-breadcrumb-sep {{
  display: inline-flex;
  align-items: center;
  color: var(--{p}-text-subtle);
}}
.{p}-breadcrumb-sep > svg {{ width: var(--{p}-icon-sm); height: var(--{p}-icon-sm); }}

/* ------------------------------------------------------- pagination ---
 * Current page is `ink` -- a committed state, consistent with the primary
 * button and checked controls. Prev/next are DISABLED at the bounds, never
 * hidden: controls that vanish shift the row.
 */
.{p}-pagination {{
  display: flex;
  align-items: center;
  gap: var(--{p}-space-2);
}}
.{p}-pagination-summary {{
  font-size: var(--{p}-font-size-sm);
  color: var(--{p}-text-muted);
}}
.{p}-pagination-spacer {{ flex: 1; }}
.{p}-pagination-list {{
  display: flex;
  align-items: center;
  gap: var(--{p}-space-1);
}}
.{p}-pagination-gap {{
  width: var(--{p}-control-h-sm);
  text-align: center;
  color: var(--{p}-text-subtle);
  user-select: none;
}}

/* ---------------------------------------------------------- stepper ---
 * Complete and current are both `ink`; the difference is a check versus a
 * numeral. Upcoming is `control` -- flat and quiet, so the eye lands on where
 * you are.
 */
.{p}-stepper {{
  display: flex;
  align-items: center;
  gap: var(--{p}-space-2);
}}
.{p}-step {{
  display: flex;
  align-items: center;
  gap: var(--{p}-space-2);
}}
.{p}-step-marker {{
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: var(--{p}-size-28);
  height: var(--{p}-size-28);
  flex: none;
  border-radius: var(--{p}-radius-full);
  background: var(--{p}-control);
  color: var(--{p}-text-muted);
  font-size: var(--{p}-font-size-2xs);
  font-weight: 500;
}}
.{p}-step-marker > svg {{ width: var(--{p}-icon-sm); height: var(--{p}-icon-sm); }}
.{p}-step[data-state="complete"] .{p}-step-marker,
.{p}-step[data-state="current"] .{p}-step-marker {{
  background: var(--{p}-ink);
  color: var(--{p}-on-ink);
}}
.{p}-step-label {{ font-size: var(--{p}-font-size-sm); color: var(--{p}-text-muted); }}
.{p}-step[data-state="current"] .{p}-step-label {{
  color: var(--{p}-text);
  font-weight: 500;
}}
.{p}-step-connector {{
  height: var(--{p}-size-2);
  min-width: var(--{p}-space-6);
  flex: 1;
  background: var(--{p}-border);
}}
.{p}-step-connector[data-state="complete"] {{ background: var(--{p}-ink); }}

/* ================================================================ */
/* FORM                                                              */
/* ================================================================ */

/* ----------------------------------------------------- search field --- */
.{p}-search {{ position: relative; display: block; }}
.{p}-search > svg {{
  position: absolute;
  left: var(--{p}-control-px-sm);
  top: 50%;
  transform: translateY(-50%);
  width: var(--{p}-icon-sm);
  height: var(--{p}-icon-sm);
  color: var(--{p}-text-subtle);
  pointer-events: none;
}}
.{p}-search > .{p}-input {{
  padding-left: calc(var(--{p}-control-px-sm) + var(--{p}-icon-sm) + var(--{p}-space-2));
}}
.{p}-search--pill > .{p}-input {{ border-radius: var(--{p}-radius-full); }}

/* ----------------------------------------------------- number input ---
 * Right-aligned tabular figures so a column of numeric fields lines up -- the
 * same rule as a numeric table column. `type="text"` with `inputmode`, because
 * `type="number"` scrolls its value on wheel events over the field.
 */
.{p}-number {{
  text-align: right;
  /* room for the steppers, measured from their own width + the field padding */
  padding-right: calc(var(--{p}-size-24) + var(--{p}-control-px-sm) * 2);
  font-family: var(--{p}-font-mono);
  font-variant-numeric: tabular-nums;
}}
.{p}-number-group {{ position: relative; display: block; }}
.{p}-number-steppers {{
  position: absolute;
  /* Inset by the field's own horizontal padding, so the steppers sit on the
   * same optical margin as the value. `right: 0` glued them to the edge. */
  right: var(--{p}-control-px-sm);
  top: var(--{p}-border-width);
  bottom: var(--{p}-border-width);
  width: var(--{p}-size-24);
  display: flex;
  flex-direction: column;
}}
.{p}-number-steppers > button {{
  flex: 1;
  border: none;
  background: transparent;
  color: var(--{p}-text-muted);
  cursor: pointer;
  padding: 0;
}}

/* ----------------------------------------------------------- slider ---
 * Filled track is `ink` -- committed, like every other filled state. The thumb
 * keeps a `border-strong` edge because a `surface` circle on a `control` track
 * would otherwise vanish: one of the few places a control border survives.
 */
.{p}-slider {{
  display: flex;
  align-items: center;
  gap: var(--{p}-space-3);
  height: var(--{p}-touch-target);
}}
.{p}-slider-track {{
  position: relative;
  flex: 1;
  height: var(--{p}-size-4);
  border-radius: var(--{p}-radius-full);
  background: var(--{p}-control);
}}
.{p}-slider-fill {{
  display: block;
  height: 100%;
  border-radius: var(--{p}-radius-full);
  background: var(--{p}-ink);
}}
.{p}-slider-thumb {{
  position: absolute;
  top: 50%;
  width: var(--{p}-size-20);
  height: var(--{p}-size-20);
  margin-top: calc(var(--{p}-size-20) / -2);
  margin-left: calc(var(--{p}-size-20) / -2);
  border-radius: var(--{p}-radius-full);
  background: var(--{p}-surface);
  border: var(--{p}-border-width) solid var(--{p}-border-strong);
  box-sizing: border-box;
}}
.{p}-slider-value {{
  min-width: var(--{p}-size-48);
  text-align: right;
  font-size: var(--{p}-font-size-sm);
  font-family: var(--{p}-font-mono);
  font-variant-numeric: tabular-nums;
}}

/* ------------------------------------------------------ file upload ---
 * The dashed border is the ONE sanctioned dashed line in the system: it means
 * "not yet filled" and appears nowhere else. A drop zone must also be a button,
 * because keyboard and screen-reader users cannot drag.
 */
.{p}-dropzone {{
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: var(--{p}-space-2);
  min-height: var(--{p}-size-120);
  padding: var(--{p}-space-4);
  border: var(--{p}-border-width) dashed var(--{p}-border-strong);
  border-radius: var(--{p}-radius-md);
  background: var(--{p}-control);
  cursor: pointer;
  text-align: center;
}}
.{p}-dropzone > svg {{
  width: var(--{p}-icon-lg);
  height: var(--{p}-icon-lg);
  color: var(--{p}-text-subtle);
}}
.{p}-dropzone[data-dragover] {{
  background: var(--{p}-accent-subtle);
  border-color: var(--{p}-accent-border);
}}
.{p}-dropzone-title {{ font-size: var(--{p}-font-size-sm); font-weight: 500; }}
.{p}-dropzone-hint {{ font-size: var(--{p}-font-size-2xs); color: var(--{p}-text-muted); }}
/* The rows need an owning container: dropped into a card with `padding: 0`,
 * their square corners overflowed the card's radius and the last row's border
 * sat on the rounded edge. */
.{p}-filelist {{
  border: var(--{p}-border-width) solid var(--{p}-border);
  border-radius: var(--{p}-radius-md);
  background: var(--{p}-surface);
  overflow: hidden;
}}
.{p}-filerow {{
  position: relative;
  display: flex;
  align-items: center;
  gap: var(--{p}-space-3);
  min-height: var(--{p}-control-h-md);
  /* bottom padding reserves the progress bar's track, so it never sits on the
   * filename */
  padding: var(--{p}-space-2) var(--{p}-space-3)
           calc(var(--{p}-space-2) + var(--{p}-size-4));
  background: var(--{p}-surface);
  border-bottom: var(--{p}-border-width) solid var(--{p}-border-subtle);
  font-size: var(--{p}-font-size-sm);
}}
.{p}-filerow:last-child {{ border-bottom: none; }}
.{p}-filerow-thumb {{
  width: var(--{p}-size-32);
  height: var(--{p}-size-32);
  flex: none;
  border-radius: var(--{p}-radius-sm);
  background: var(--{p}-control);
}}
.{p}-filerow-spacer {{ flex: 1; }}
.{p}-filerow-error {{ color: var(--{p}-danger-text); }}
/* Per-file progress, full-bleed at the bottom of the row -- never one
   aggregate bar for the whole upload. */
.{p}-filerow-progress {{
  position: absolute;
  left: 0;
  right: 0;
  bottom: 0;
  height: var(--{p}-size-4);
  background: var(--{p}-control);
}}
.{p}-filerow-progress > * {{ display: block; height: 100%; background: var(--{p}-ink); }}

/* -------------------------------------------------------- tag input ---
 * Grows vertically as chips wrap; never scrolls horizontally, which would hide
 * its own contents.
 */
.{p}-taginput {{
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  gap: var(--{p}-space-1);
  min-height: var(--{p}-control-h-md);
  max-height: var(--{p}-size-120);
  overflow-y: auto;
  padding: var(--{p}-space-1);
  border: var(--{p}-border-width) solid transparent;
  border-radius: var(--{p}-radius-md);
  background: var(--{p}-control);
}}
.{p}-taginput > input {{
  flex: 1;
  min-width: var(--{p}-size-80);
  border: none;
  background: transparent;
  color: var(--{p}-text);
  font: 400 var(--{p}-font-size-sm)/1 var(--{p}-font-text);
  outline: none;
}}

/* -------------------------------------------------------- combobox ---
 * Matches are highlighted with WEIGHT, never a background tint: a highlight
 * background collides with the `accent-subtle` selected state.
 */
.{p}-combobox {{ position: relative; display: block; }}
/* The element carrying the radius must not be the element that scrolls: a
 * scrollbar is painted inside the padding box and its square corner clips
 * straight through the rounded edge. So the radius and `overflow: hidden` live
 * on the container, and scrolling happens on an inner element. */
.{p}-listbox {{
  border: var(--{p}-border-width) solid var(--{p}-border);
  border-radius: var(--{p}-radius-md);
  background: var(--{p}-surface-raised);
  box-shadow: var(--{p}-shadow-sm);
  overflow: hidden;
}}
.{p}-listbox-items {{
  max-height: var(--{p}-size-120);
  overflow-y: auto;
  padding: var(--{p}-space-1);
}}
.{p}-option {{
  display: flex;
  align-items: center;
  gap: var(--{p}-space-2);
  height: var(--{p}-control-h-sm);
  padding: 0 var(--{p}-control-px-sm);
  border-radius: var(--{p}-radius-sm);
  font-size: var(--{p}-font-size-sm);
  cursor: pointer;
}}
/* A raised surface, so hover is `control-subtle` -- `surface-hover` equals
   `surface-raised` in dark mode and would show nothing. */
.{p}-option:hover, .{p}-option[data-active] {{ background: var(--{p}-control-subtle); }}
.{p}-option[aria-selected="true"] {{
  background: var(--{p}-accent-subtle);
  color: var(--{p}-accent-text);
}}
.{p}-option mark {{
  background: none;
  color: inherit;
  font-weight: 600;
}}
.{p}-option-empty {{
  display: flex;
  align-items: center;
  justify-content: center;
  height: var(--{p}-control-h-md);
  color: var(--{p}-text-muted);
  font-size: var(--{p}-font-size-sm);
}}

/* ----------------------------------------------------- date picker ---
 * Selected is `ink` (a commitment); today is an `accent` dot (a landmark).
 * Using the accent for both makes the calendar unreadable at a glance.
 * Range interiors are square so a run of days reads as one continuous bar.
 */
.{p}-calendar {{
  padding: var(--{p}-space-3);
  border: var(--{p}-border-width) solid var(--{p}-border);
  border-radius: var(--{p}-radius-md);
  background: var(--{p}-surface-raised);
  box-shadow: var(--{p}-shadow-sm);
}}
.{p}-calendar-head {{
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: var(--{p}-space-2);
  margin-bottom: var(--{p}-space-2);
  font-size: var(--{p}-font-size-sm);
  font-weight: 600;
}}
.{p}-calendar-grid {{
  display: grid;
  grid-template-columns: repeat(7, var(--{p}-size-36));
  gap: 0;
}}
.{p}-calendar-weekday {{
  height: var(--{p}-size-28);
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: var(--{p}-font-size-2xs);
  font-weight: 500;
  color: var(--{p}-text-muted);
}}
.{p}-day {{
  position: relative;
  width: var(--{p}-size-36);
  height: var(--{p}-size-36);
  display: flex;
  align-items: center;
  justify-content: center;
  border: none;
  border-radius: var(--{p}-radius-sm);
  background: transparent;
  color: var(--{p}-text);
  font-size: var(--{p}-font-size-sm);
  cursor: pointer;
}}
.{p}-day:hover {{ background: var(--{p}-control-subtle); }}
.{p}-day[data-outside] {{ color: var(--{p}-text-subtle); }}

/* ORDER MATTERS HERE, and getting it wrong is a real contrast failure.
 *
 * `[aria-selected="true"]` and `[data-range-start]` have identical specificity,
 * so whichever comes last wins on `background`. With the range rules last, a
 * selected endpoint kept `color: on-ink` from the selected rule while taking
 * `background: accent-subtle` from the range rule -- white text on a pale tint,
 * 1.10:1.
 *
 * So: range tints first (they describe UNSELECTED days inside a range), then
 * selection (which must win on both fill and text), then radius-only overrides
 * for the endpoints.
 */
.{p}-day[data-range-inner] {{
  background: var(--{p}-accent-subtle);
  border-radius: 0;
}}
.{p}-day[data-range-start] {{
  background: var(--{p}-accent-subtle);
  border-radius: var(--{p}-radius-sm) 0 0 var(--{p}-radius-sm);
}}
.{p}-day[data-range-end] {{
  background: var(--{p}-accent-subtle);
  border-radius: 0 var(--{p}-radius-sm) var(--{p}-radius-sm) 0;
}}
/* Selection wins on fill AND text, whatever range state the day also carries. */
.{p}-day[aria-selected="true"] {{
  background: var(--{p}-ink);
  color: var(--{p}-on-ink);
}}
.{p}-day[aria-selected="true"][data-range-start] {{
  background: var(--{p}-ink);
  color: var(--{p}-on-ink);
  border-radius: var(--{p}-radius-sm) 0 0 var(--{p}-radius-sm);
}}
.{p}-day[aria-selected="true"][data-range-end] {{
  background: var(--{p}-ink);
  color: var(--{p}-on-ink);
  border-radius: 0 var(--{p}-radius-sm) var(--{p}-radius-sm) 0;
}}
.{p}-day[data-today]::after {{
  content: "";
  position: absolute;
  bottom: var(--{p}-size-4);
  width: var(--{p}-size-4);
  height: var(--{p}-size-4);
  border-radius: var(--{p}-radius-full);
  background: var(--{p}-accent);
}}
.{p}-day[aria-selected="true"][data-today]::after {{ background: var(--{p}-on-ink); }}

/* -------------------------------------------------- command palette ---
 * Keyboard highlight and pointer hover are the SAME visual state and only one
 * is active at a time. Two highlighted rows at once is this component's
 * defining failure.
 */
.{p}-palette {{
  width: var(--{p}-container-modal-md);
  max-width: 100%;
  border: var(--{p}-border-width) solid var(--{p}-border);
  border-radius: var(--{p}-radius-lg);
  background: var(--{p}-surface-raised);
  box-shadow: var(--{p}-shadow-md);
  overflow: hidden;
}}
.{p}-palette-search {{
  display: flex;
  align-items: center;
  gap: var(--{p}-space-3);
  height: var(--{p}-size-56);
  padding: 0 var(--{p}-space-4);
  border-bottom: var(--{p}-border-width) solid var(--{p}-border-subtle);
}}
.{p}-palette-search > input {{
  flex: 1;
  border: none;
  background: transparent;
  color: var(--{p}-text);
  font: 400 var(--{p}-font-size-base)/1 var(--{p}-font-text);
  outline: none;
}}
.{p}-palette-results {{
  max-height: var(--{p}-size-120);
  overflow-y: auto;
  padding: 0 var(--{p}-space-1) var(--{p}-space-1);
}}
.{p}-palette-group {{
  padding: var(--{p}-space-3) var(--{p}-space-4) var(--{p}-space-1);
  font-size: var(--{p}-font-size-2xs);
  font-weight: 500;
  color: var(--{p}-text-subtle);
  position: sticky;
  top: 0;
  background: var(--{p}-surface-raised);
}}
.{p}-palette-group:first-child {{ padding-top: var(--{p}-space-2); }}
.{p}-palette-item {{
  display: flex;
  align-items: center;
  gap: var(--{p}-space-3);
  height: var(--{p}-control-h-md);
  padding: 0 var(--{p}-space-4);
  border-radius: var(--{p}-radius-sm);
  font-size: var(--{p}-font-size-sm);
  cursor: pointer;
}}
.{p}-palette-item[data-active] {{ background: var(--{p}-control-subtle); }}
.{p}-palette-item > svg {{ width: var(--{p}-icon-sm); height: var(--{p}-icon-sm); flex: none; }}
.{p}-palette-shortcut {{
  margin-left: auto;
  font-family: var(--{p}-font-mono);
  font-size: var(--{p}-font-size-2xs);
  color: var(--{p}-text-subtle);
}}

/* ================================================================ */
/* DATA & FEEDBACK                                                   */
/* ================================================================ */

/* ------------------------------------------------------------ tree ---
 * Indents by exactly one icon column per level so labels align with their
 * parent's LABEL. No guide lines: indentation carries the hierarchy, and
 * vertical rules at every level turn a tree into a grid.
 */
.{p}-tree {{ list-style: none; margin: 0; padding: 0; }}
.{p}-treerow {{
  display: flex;
  align-items: center;
  gap: var(--{p}-space-2);
  height: var(--{p}-control-h-sm);
  padding: 0 var(--{p}-space-2);
  border-radius: var(--{p}-radius-sm);
  font-size: var(--{p}-font-size-sm);
  cursor: pointer;
}}
.{p}-treerow:hover {{ background: var(--{p}-control-subtle); }}
.{p}-treerow[aria-selected="true"] {{
  background: var(--{p}-accent-subtle);
  color: var(--{p}-accent-text);
}}
/* The twisty is a SEPARATE target from the label: expanding a node must not
   also select it. */
.{p}-twisty {{
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: var(--{p}-size-24);
  height: var(--{p}-size-24);
  flex: none;
  border: none;
  background: none;
  color: var(--{p}-text-subtle);
  cursor: pointer;
  padding: 0;
}}
.{p}-twisty > svg {{
  width: var(--{p}-icon-sm);
  height: var(--{p}-icon-sm);
  transition: transform var(--{p}-duration-fast) var(--{p}-ease-standard);
}}
.{p}-twisty[aria-expanded="true"] > svg {{ transform: rotate(90deg); }}
.{p}-tree .{p}-tree {{ padding-left: var(--{p}-size-20); }}

/* ------------------------------------------- description list ---------
 * The label column is a FIXED width, not content-derived: labels of varying
 * length make values start at ragged positions, and the eye cannot scan a
 * column that does not exist.
 */
.{p}-dl {{
  display: grid;
  grid-template-columns: var(--{p}-container-field-label) 1fr;
  gap: var(--{p}-space-3) var(--{p}-space-4);
  margin: 0;
  font-size: var(--{p}-font-size-sm);
}}
.{p}-dl > dt {{ margin: 0; color: var(--{p}-text-muted); }}
.{p}-dl > dd {{ margin: 0; color: var(--{p}-text); overflow-wrap: anywhere; }}
.{p}-dl > dd.{p}-num {{ text-align: left; }}
/* An empty value is an em dash, never blank space: blank reads as broken. */
.{p}-dl-empty {{ color: var(--{p}-text-subtle); }}

/* -------------------------------------------------------- timeline ---
 * The connector stops at the last node -- a line trailing past the final entry
 * implies content that is not there.
 */
.{p}-timeline {{
  position: relative;
  padding-left: var(--{p}-size-24);
  list-style: none;
  margin: 0;
}}
.{p}-timeline::before {{
  content: "";
  position: absolute;
  left: var(--{p}-size-4);
  top: var(--{p}-space-4);
  bottom: var(--{p}-space-4);
  width: var(--{p}-border-width);
  background: var(--{p}-border);
}}
.{p}-event {{
  position: relative;
  padding: var(--{p}-space-3) 0;
  font-size: var(--{p}-font-size-sm);
}}
.{p}-event::before {{
  content: "";
  position: absolute;
  left: calc(var(--{p}-size-24) * -1 + var(--{p}-size-2));
  top: var(--{p}-space-4);
  width: var(--{p}-size-8);
  height: var(--{p}-size-8);
  box-sizing: border-box;
  border-radius: var(--{p}-radius-full);
  background: var(--{p}-surface);
  border: var(--{p}-border-width) solid var(--{p}-border-strong);
}}
.{p}-event[data-current]::before {{
  background: var(--{p}-ink);
  border-color: var(--{p}-ink);
}}
.{p}-event-time {{
  font-size: var(--{p}-font-size-2xs);
  color: var(--{p}-text-subtle);
}}
/* A payload goes in a block beneath, never inline in the event sentence. */
.{p}-event-detail {{
  margin-top: var(--{p}-space-2);
  padding: var(--{p}-space-2);
  border-radius: var(--{p}-radius-sm);
  background: var(--{p}-control);
  color: var(--{p}-text-muted);
}}
.{p}-timeline-day {{
  position: sticky;
  top: 0;
  padding: var(--{p}-space-2) 0;
  font-size: var(--{p}-font-size-2xs);
  font-weight: 500;
  color: var(--{p}-text-subtle);
  background: var(--{p}-bg);
}}

/* ------------------------------------------------------------ stat ---
 * Tabular mono so digits align down a row of stats. A delta needs a comparison
 * caption to mean anything: "+12%" alone is not information.
 */
.{p}-stat-label {{ font-size: var(--{p}-font-size-sm); color: var(--{p}-text-muted); }}
.{p}-stat-value {{
  margin-top: var(--{p}-space-1);
  font-size: var(--{p}-font-size-2xl);
  font-weight: 600;
  font-family: var(--{p}-font-mono);
  font-variant-numeric: tabular-nums;
  line-height: var(--{p}-line-height-2xl);
}}
.{p}-stat-delta {{
  display: flex;
  align-items: center;
  gap: var(--{p}-space-1);
  margin-top: var(--{p}-space-1);
  font-size: var(--{p}-font-size-sm);
  font-weight: 500;
  color: var(--{p}-text-muted);
}}
.{p}-stat-delta > svg {{ width: var(--{p}-icon-sm); height: var(--{p}-icon-sm); flex: none; }}
/* `good` / `bad`, NOT `up` / `down`. Colour follows the interpretation: falling
   churn is good, rising latency is bad. Green-up is not universal. */
.{p}-stat-delta--good {{ color: var(--{p}-success-text); }}
.{p}-stat-delta--bad {{ color: var(--{p}-danger-text); }}
.{p}-stat-caption {{
  margin-top: var(--{p}-size-2);
  font-size: var(--{p}-font-size-2xs);
  color: var(--{p}-text-subtle);
}}
.{p}-sparkline {{ height: var(--{p}-size-40); color: var(--{p}-accent); }}

/* ------------------------------------------------------ data table ---
 * The bulk bar REPLACES the toolbar in place; a bar that pushes the table down
 * moves the rows the user just selected out from under the pointer.
 */
.{p}-table-toolbar, .{p}-bulkbar {{
  display: flex;
  align-items: center;
  gap: var(--{p}-space-3);
  height: var(--{p}-control-h-lg);
  margin-bottom: var(--{p}-space-3);
}}
.{p}-bulkbar {{
  gap: var(--{p}-space-2);
  padding: 0 var(--{p}-space-3);
  background: var(--{p}-surface-raised);
  border: none;
  border-radius: var(--{p}-radius-md);
  font-weight: 500;
}}
.{p}-bulkbar-sub {{ color: var(--{p}-text-muted); font-weight: 400; }}
.{p}-bulkbar-spacer, .{p}-table-toolbar-spacer {{ flex: 1; }}
.{p}-table-select {{ width: var(--{p}-touch-target); }}
.{p}-table-actions {{ width: var(--{p}-touch-target); text-align: right; }}
.{p}-table th[aria-sort] {{ color: var(--{p}-text); }}
/* A selected row that is also hovered stays distinguishable. */
.{p}-table tr[aria-selected="true"]:hover {{ background: var(--{p}-accent-muted); }}

/* --------------------------------------------------------- spinner ---
 * Inherits `currentColor`, so it works inside an ink button, a ghost button and
 * on any surface with no per-context variant.
 */
.{p}-spinner {{
  width: var(--{p}-icon-md);
  height: var(--{p}-icon-md);
  flex: none;
  color: currentColor;
  animation: {p}-spin var(--{p}-duration-spin) linear infinite;
}}
.{p}-spinner--sm {{ width: var(--{p}-icon-sm); height: var(--{p}-icon-sm); }}
.{p}-spinner--lg {{ width: var(--{p}-icon-lg); height: var(--{p}-icon-lg); }}
@keyframes {p}-spin {{ to {{ transform: rotate(360deg); }} }}

/* ----------------------------------------------------------- drawer ---
 * Flush to the viewport edge, so it takes NO radius on that side. A rounded
 * corner against a screen edge is the clearest sign a component was designed
 * in isolation.
 */
.{p}-drawer {{
  width: var(--{p}-container-drawer-md);
  max-width: 100%;
  height: 100%;
  padding: var(--{p}-space-6);
  background: var(--{p}-surface-raised);
  border-left: var(--{p}-border-width) solid var(--{p}-border);
  border-radius: var(--{p}-radius-none);
  box-shadow: var(--{p}-shadow-md);
  z-index: var(--{p}-z-modal);
}}
.{p}-drawer--sm {{ width: var(--{p}-container-drawer-sm); }}
.{p}-drawer--lg {{ width: var(--{p}-container-drawer-lg); }}
.{p}-drawer--bottom {{
  width: 100%;
  height: auto;
  max-height: 90vh;
  border-left: none;
  border-top: var(--{p}-border-width) solid var(--{p}-border);
  border-radius: var(--{p}-radius-lg) var(--{p}-radius-lg) 0 0;
}}
.{p}-drawer-handle {{
  width: var(--{p}-size-32);
  height: var(--{p}-size-4);
  margin: 0 auto var(--{p}-space-4);
  border-radius: var(--{p}-radius-full);
  background: var(--{p}-control);
}}
.{p}-drawer-header {{
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: var(--{p}-space-3);
  height: var(--{p}-control-h-lg);
  margin-bottom: var(--{p}-space-4);
}}

/* ------------------------------------------------------- page structure --- */
.{p}-page-title {{
  margin: 0;
  font-family: var(--{p}-font-display);
  font-size: var(--{p}-font-size-2xl);
  font-weight: 600;
  letter-spacing: var(--{p}-letter-spacing-display);
}}
.{p}-page-desc {{
  max-width: var(--{p}-measure-base);
  margin: var(--{p}-space-2) 0 0;
  font-size: var(--{p}-font-size-base);
  color: var(--{p}-text-muted);
}}
/* No bottom border: section-gap already separates the header from content. */
.{p}-page-header {{ margin-bottom: var(--{p}-section-gap); border-bottom: none; }}
"""


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("brand")
    ap.add_argument("--out-dir", default=".")
    args = ap.parse_args(argv)

    brand = load_brand(args.brand)
    p = brand.get("prefix", "ds")
    out = Path(args.out_dir)
    out.mkdir(parents=True, exist_ok=True)
    dest = out / f"{p}-components.css"
    dest.write_text(sheet(p))

    n_classes = sheet(p).count(f".{p}-")
    print(f"Wrote {dest}")
    print(f"  prefix '{p}', ~{n_classes} class references")
    print(f"  load order: tokens.css -> your existing CSS -> {dest.name}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
