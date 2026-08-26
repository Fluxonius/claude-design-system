#!/usr/bin/env python3
"""Render a proof sheet from brand.json -- using the REAL component stylesheet.

This file used to carry its own hand-written copy of the component CSS, which
meant the proof sheet showed something other than what shipped. The two drifted
exactly as you would expect: the checkbox was rebuilt in
`build_components_css.py` (a centred mask on a real `<input>`) while the preview
still drew a `&#10003;` entity in a `<span>`, and the surface swatches still
listed `bg-subtle`, a token deleted several versions earlier.

So it now imports `sheet()` from `build_components_css` and renders every
component with the shipped `ds-*` classes. What you see here is what a project
gets. The only CSS defined locally is page scaffolding, namespaced `pv-` so it
can never collide with a component class.

Usage:
    python3 build_preview.py brand.json --out proof.html
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from build_tokens import (  # noqa: E402
    RAMP_STEPS, TYPE_SCALE, audit, build_tokens, load_brand, render_css,
)
from build_components_css import sheet  # noqa: E402

P = "ds"  # the proof sheet always renders with the default prefix


def _svg(path: str, fill: str = "none") -> str:
    return (f'<svg viewBox="0 0 24 24" fill="{fill}" stroke="currentColor" '
            f'stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round">'
            f'{path}</svg>')


I = {
    "plus": _svg('<path d="M12 5v14M5 12h14"/>'),
    "chevron-r": _svg('<path d="M9 6l6 6-6 6"/>'),
    "chevron-l": _svg('<path d="M15 6l-6 6 6 6"/>'),
    "search": _svg('<circle cx="11" cy="11" r="7"/><path d="M20 20l-4-4"/>'),
    "x": _svg('<path d="M6 6l12 12M18 6L6 18"/>'),
    "trash": _svg('<path d="M4 7h16M10 11v6M14 11v6M5 7l1 12a2 2 0 002 2h8a2 2 0 '
                  '002-2l1-12M9 7V5a1 1 0 011-1h4a1 1 0 011 1v2"/>'),
    "pencil": _svg('<path d="M4 20h4L20 8a2.8 2.8 0 00-4-4L4 16v4z"/>'),
    "dots": _svg('<circle cx="12" cy="5" r="1.6"/><circle cx="12" cy="12" r="1.6"/>'
                 '<circle cx="12" cy="19" r="1.6"/>', fill="currentColor"),
    "check": _svg('<path d="M20 6L9 17l-5-5"/>'),
    "up": _svg('<path d="M12 19V5M6 11l6-6 6 6"/>'),
    "down": _svg('<path d="M12 5v14M6 13l6 6 6-6"/>'),
    "alert": _svg('<path d="M12 9v5M12 17.5v.01"/><path d="M10.3 4.3L2.6 18a2 2 0 '
                  '001.7 3h15.4a2 2 0 001.7-3L13.7 4.3a2 2 0 00-3.4 0z"/>'),
    "info": _svg('<circle cx="12" cy="12" r="9"/><path d="M12 11v5M12 7.5v.01"/>'),
    "upload": _svg('<path d="M12 16V4M7 9l5-5 5 5"/><path d="M4 16v2a2 2 0 002 2h12'
                   'a2 2 0 002-2v-2"/>'),
    "folder": _svg('<path d="M3 7a2 2 0 012-2h4l2 2h8a2 2 0 012 2v8a2 2 0 01-2 2H5'
                   'a2 2 0 01-2-2z"/>'),
    "file": _svg('<path d="M14 3v5h5"/><path d="M6 3h8l5 5v11a2 2 0 01-2 2H6a2 2 0 '
                 '01-2-2V5a2 2 0 012-2z"/>'),
    "home": _svg('<path d="M4 11l8-7 8 7"/><path d="M6 10v9a1 1 0 001 1h10a1 1 0 '
                 '001-1v-9"/>'),
    "users": _svg('<circle cx="9" cy="8" r="3.5"/><path d="M2.5 20a6.5 6.5 0 0113 0"/>'
                  '<path d="M16 5.5a3.5 3.5 0 010 5"/>'),
    "cog": _svg('<circle cx="12" cy="12" r="3"/><path d="M5 12a7 7 0 01.5-2.6L4 7l2-2'
                'l2.4 1.5A7 7 0 0111 5.5L11.5 3h1L13 5.5a7 7 0 012.6 1L18 5l2 2'
                'l-1.5 2.4A7 7 0 0119 12"/>'),
    "spinner": ('<svg class="ds-spinner" viewBox="0 0 24 24" fill="none">'
                '<circle cx="12" cy="12" r="9" stroke="currentColor" '
                'stroke-width="2.5" opacity="0.2"/>'
                '<path d="M21 12a9 9 0 00-9-9" stroke="currentColor" '
                'stroke-width="2.5" stroke-linecap="round"/></svg>'),
}

# Page scaffolding only. `pv-` namespaced: a bare class name here would be able
# to override a component rule for every property it does not itself set, which
# has caused four separate visual bugs in this project.
PV_CSS = """
body { margin: 0; background: var(--ds-bg); color: var(--ds-text);
  font-family: var(--ds-font-text); font-size: var(--ds-font-size-sm);
  -webkit-font-smoothing: antialiased; }
.pv-wrap { max-width: var(--ds-container-page); margin: 0 auto;
  padding: var(--ds-space-8) var(--ds-space-6); }
.pv-head { display: flex; align-items: flex-start; justify-content: space-between;
  gap: var(--ds-space-6); margin-bottom: var(--ds-section-gap); }
.pv-meta { color: var(--ds-text-subtle); font-size: var(--ds-font-size-2xs);
  margin: var(--ds-space-2) 0 0; }
.pv-sub { color: var(--ds-text-muted); font-size: var(--ds-font-size-sm);
  margin: 0 0 var(--ds-space-3); max-width: var(--ds-measure-base); }
.pv-sec { margin-bottom: var(--ds-section-gap); }
.pv-sec > h2 { font-size: var(--ds-font-size-lg); font-weight: 600;
  margin: 0 0 var(--ds-space-1); }
.pv-sec > h2 > em { color: var(--ds-text-subtle); font-weight: 400; font-style: normal;
  font-family: var(--ds-font-mono); font-size: var(--ds-font-size-2xs);
  margin-left: var(--ds-space-2); }
.pv-row { display: flex; align-items: center; gap: var(--ds-space-2); flex-wrap: wrap; }
.pv-col { display: flex; flex-direction: column; gap: var(--ds-space-3); }
.pv-cols { display: grid; grid-template-columns: 1fr 1fr; gap: var(--ds-space-6); }
.pv-cols3 { display: grid; grid-template-columns: 1fr 1fr 1fr; gap: var(--ds-space-4); }
.pv-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(var(--ds-container-menu-min), 1fr));
  gap: var(--ds-space-2); margin-bottom: var(--ds-space-4); }
.pv-lbl { display: block; font-size: var(--ds-font-size-2xs);
  color: var(--ds-text-subtle); text-transform: uppercase;
  letter-spacing: var(--ds-letter-spacing-2xs); margin: 0 0 var(--ds-space-2); }
.pv-matrix { display: grid; grid-template-columns: auto repeat(3, 1fr);
  gap: var(--ds-space-3) var(--ds-space-4); align-items: center; }
.pv-states { display: grid; grid-template-columns: repeat(4, 1fr);
  gap: var(--ds-space-3) var(--ds-space-4); align-items: center; }
.pv-swatch { text-align: center; }
.pv-swatch > i { display: block; width: var(--ds-size-48); height: var(--ds-size-40);
  border-radius: var(--ds-radius-sm);
  border: var(--ds-border-width) solid var(--ds-border); }
.pv-role { display: flex; align-items: center; gap: var(--ds-space-2); }
.pv-dot { width: var(--ds-size-16); height: var(--ds-size-16); flex: none;
  border-radius: var(--ds-radius-sm);
  border: var(--ds-border-width) solid var(--ds-border); }
.pv-tr { display: flex; align-items: baseline; gap: var(--ds-space-4);
  padding: var(--ds-space-2) 0;
  border-bottom: var(--ds-border-width) solid var(--ds-border-subtle); }
.pv-tr > code { width: var(--ds-size-56); flex: none; color: var(--ds-text-subtle); }
.pv-tr > em { margin-left: auto; color: var(--ds-text-subtle); font-style: normal; }
code, kbd { font-family: var(--ds-font-mono); font-size: var(--ds-font-size-2xs); }
/* Forced states, so a static page can show hover and focus. These MIRROR the
   shipped rules by hand -- if a real :hover changes, change these too. */
.pv-hover.ds-btn--filled.ds-btn--neutral { background: var(--ds-ink-hover); }
.pv-hover.ds-btn--outline.ds-btn--neutral { background: var(--ds-control-subtle); }
.pv-hover.ds-input { background: var(--ds-control-hover); }
.pv-focus { outline: var(--ds-focus-ring-width) solid var(--ds-focus-ring);
  outline-offset: var(--ds-focus-ring-offset); }
"""


def swatches(family):
    cells = "".join(
        f'<div class="pv-swatch"><i style="background:var(--{P}-{family}-{s})"></i>'
        f'<code>{s}</code></div>' for s in RAMP_STEPS)
    return (f'<span class="pv-lbl">{family}</span>'
            f'<div class="pv-row" style="margin-bottom:var(--{P}-space-4)">{cells}</div>')


def role_grid(tokens, names, title):
    cells = "".join(
        f'<div class="pv-role"><span class="pv-dot" style="background:var(--{P}-{n})">'
        f'</span><code>{n}</code></div>' for n in names if n in tokens["light"])
    return f'<span class="pv-lbl">{title}</span><div class="pv-grid">{cells}</div>'


def type_rows():
    return "".join(
        f'<div class="pv-tr"><code>{n}</code>'
        f'<span style="font-size:var(--{P}-font-size-{n});'
        f'line-height:var(--{P}-line-height-{n});'
        f'letter-spacing:var(--{P}-letter-spacing-{n});'
        f'font-family:var(--{P}-font-{"display" if sz >= 32 else "text"});'
        f'font-weight:{600 if sz >= 20 else 400}">The quick brown fox</span>'
        f'<em>{sz}/{lh}</em></div>'
        for n, sz, lh, _ in TYPE_SCALE)


def sec(title, ref, body, sub=""):
    s = f'<p class="pv-sub">{sub}</p>' if sub else ""
    return f'<section class="pv-sec"><h2>{title}<em>{ref}</em></h2>{s}{body}</section>'


def btn_matrix(small=False):
    z = " ds-btn--s" if small else ""
    label = {"neutral": "Save changes", "primary": "Upgrade",
             "destructive": "Delete"}
    rows = []
    for pri in ("filled", "outline", "ghost"):
        cells = "".join(
            f'<button class="ds-btn{z} ds-btn--{pri} ds-btn--{c}">{label[c]}</button>'
            for c in ("neutral", "primary", "destructive"))
        rows.append(f'<span class="pv-lbl">{pri}</span>{cells}')
    head = ('<span></span><span class="pv-lbl">neutral</span>'
            '<span class="pv-lbl">primary</span><span class="pv-lbl">destructive</span>')
    return f'<div class="pv-matrix">{head}{"".join(rows)}</div>'


def icon_matrix():
    rows = []
    for pri in ("filled", "outline", "ghost", "plain"):
        cells = "".join(
            f'<button class="ds-btn ds-iconbtn ds-btn--{pri} ds-btn--{c}" '
            f'aria-label="Action">{I["plus"]}</button>'
            for c in ("neutral", "primary", "destructive"))
        rows.append(f'<span class="pv-lbl">{pri}</span>{cells}')
    head = ('<span></span><span class="pv-lbl">neutral</span>'
            '<span class="pv-lbl">primary</span><span class="pv-lbl">destructive</span>')
    return f'<div class="pv-matrix">{head}{"".join(rows)}</div>'


def calendar():
    days = []
    for d in range(1, 32):
        a = ""
        if d == 14:
            a = ' aria-selected="true" data-range-start'
        elif d in (15, 16, 17):
            a = " data-range-inner"
        elif d == 18:
            a = ' aria-selected="true" data-range-end'
        elif d == 24:
            a = " data-today"
        days.append(f'<button class="ds-day"{a}>{d}</button>')
    wd = "".join(f'<span class="ds-calendar-weekday">{w}</span>'
                 for w in ("M", "T", "W", "T", "F", "S", "S"))
    return ('<div class="ds-calendar" style="display:inline-block">'
            '<div class="ds-calendar-head"><span>March 2026</span></div>'
            f'<div class="ds-calendar-grid">{wd}{"".join(days)}</div></div>')


def table():
    rows = [("INV-2048", "Northwind Trading", "success", "Paid", "14 Mar 2026", "1,248.00", True),
            ("INV-2047", "Meridian Labs", "warning", "Due soon", "11 Mar 2026", "890.50", True),
            ("INV-2046", "Ashcroft &amp; Reed", "danger", "Overdue", "28 Feb 2026", "4,120.00", False),
            ("INV-2045", "Fenwick Studio", "", "Draft", "26 Feb 2026", "310.00", False)]
    body = ""
    for ref, cust, kind, label, date, amt, sel in rows:
        cls = f" ds-badge--{kind}" if kind else ""
        body += (f'<tr{" aria-selected=true" if sel else ""}>'
                 f'<td class="ds-table-select"><input class="ds-check" type="checkbox"'
                 f'{" checked" if sel else ""} aria-label="Select {ref}"></td>'
                 f'<td>{ref}</td><td>{cust}</td>'
                 f'<td><span class="ds-badge{cls}">{label}</span></td><td>{date}</td>'
                 f'<td class="ds-num">{amt}</td><td class="ds-table-actions">'
                 f'<button class="ds-btn ds-iconbtn ds-btn--s ds-btn--plain '
                 f'ds-btn--neutral" aria-label="More actions">{I["dots"]}</button>'
                 f'</td></tr>')
    return ('<div class="ds-table-toolbar">'
            f'<label class="ds-search" style="max-width:var(--ds-container-search-max);flex:1">{I["search"]}'
            '<input class="ds-input" type="search" placeholder="Search invoices"></label>'
            '<span class="ds-table-toolbar-spacer"></span>'
            '<span class="ds-chip ds-chip--selected">Last 30 days</span></div>'
            '<div class="ds-bulkbar"><span>2 selected '
            '<span class="ds-bulkbar-sub">(2 on this page)</span></span>'
            '<span class="ds-bulkbar-spacer"></span>'
            '<button class="ds-btn ds-btn--s ds-btn--outline ds-btn--neutral">Send reminder</button>'
            '<button class="ds-btn ds-btn--s ds-btn--outline ds-btn--destructive">Void</button></div>'
            '<table class="ds-table"><thead><tr>'
            '<th class="ds-table-select"><input class="ds-check" type="checkbox" '
            'aria-label="Select all"></th><th>Invoice</th><th>Customer</th>'
            '<th>Status</th><th>Issued</th><th class="ds-num">Amount</th>'
            f'<th class="ds-table-actions"></th></tr></thead><tbody>{body}</tbody></table>')


def components():
    S = []
    a = S.append

    a(sec("Button — M", "components-core", btn_matrix(),
          "Three priorities x three colours. filled/neutral is ink, not accent: the "
          "brand hue stays reserved for links, selection, focus and status."))
    a(sec("Button — S", "components-core", btn_matrix(True),
          "There is no L. A button bigger than M is a layout problem."))
    a(sec("Button — icons", "components-core",
          '<div class="pv-row">'
          f'<button class="ds-btn ds-btn--filled ds-btn--neutral">{I["plus"]}New invoice</button>'
          f'<button class="ds-btn ds-btn--outline ds-btn--neutral">Continue{I["chevron-r"]}</button>'
          f'<button class="ds-btn ds-btn--ghost ds-btn--destructive">{I["trash"]}Delete</button>'
          f'<button class="ds-btn ds-btn--filled ds-btn--neutral">{I["spinner"]}Saving</button>'
          '</div>',
          "Leading icon labels the action, trailing shows what happens next — never "
          "both. A spinner replaces the leading icon and holds the width."))
    a(sec("Icon Button", "components-core", icon_matrix(),
          "Four priorities: `plain` has no background at all, for repeated controls "
          "in a group. An aria-label is mandatory."))

    a(sec("States", "components-core",
          '<div class="pv-states">'
          '<span class="pv-lbl">rest</span><span class="pv-lbl">hover</span>'
          '<span class="pv-lbl">focus</span><span class="pv-lbl">disabled / invalid</span>'
          '<button class="ds-btn ds-btn--filled ds-btn--neutral">Save</button>'
          '<button class="ds-btn ds-btn--filled ds-btn--neutral pv-hover">Save</button>'
          '<button class="ds-btn ds-btn--filled ds-btn--neutral pv-focus">Save</button>'
          '<button class="ds-btn ds-btn--filled ds-btn--neutral" disabled>Save</button>'
          '<button class="ds-btn ds-btn--outline ds-btn--neutral">Cancel</button>'
          '<button class="ds-btn ds-btn--outline ds-btn--neutral pv-hover">Cancel</button>'
          '<button class="ds-btn ds-btn--outline ds-btn--neutral pv-focus">Cancel</button>'
          '<button class="ds-btn ds-btn--outline ds-btn--neutral" disabled>Cancel</button>'
          '<input class="ds-input" value="Acme Industries">'
          '<input class="ds-input pv-hover" value="Acme Industries">'
          '<input class="ds-input pv-focus" value="Acme Industries">'
          '<input class="ds-input" aria-invalid="true" value="not-an-email">'
          '</div>',
          "Hover changes background only — never border, text, size or position."))

    a(sec("Field · Select · Textarea", "components-core",
          '<div class="pv-cols">'
          '<div class="ds-field"><label class="ds-label">Company name</label>'
          '<input class="ds-input" value="Northwind Trading">'
          '<span class="ds-help">Appears on every invoice.</span></div>'
          '<div class="ds-field"><label class="ds-label">Billing email '
          '<span class="ds-label-optional">Optional</span></label>'
          '<input class="ds-input" aria-invalid="true" value="not-an-email">'
          '<span class="ds-help ds-help--error">Enter a valid email address.</span></div>'
          '</div><div class="pv-cols" style="margin-top:var(--ds-space-4)">'
          '<div class="ds-field"><label class="ds-label">Region</label>'
          '<span class="ds-select-wrap"><select class="ds-select">'
          '<option>Frankfurt</option><option>Dublin</option></select></span></div>'
          '<div class="ds-field"><label class="ds-label">Notes</label>'
          '<textarea class="ds-textarea">Net 30 terms agreed.</textarea></div></div>',
          "Borderless and recessed. The helper line is always reserved, so an error "
          "does not shift the form. Optional fields are marked, not required ones."))

    a(sec("Choice controls", "components-core",
          '<div class="pv-cols"><div class="pv-col">'
          '<label class="ds-choice"><input class="ds-check" type="checkbox" checked> Weekly digest</label>'
          '<label class="ds-choice"><input class="ds-check" type="checkbox"> Product updates</label>'
          '<label class="ds-choice"><input class="ds-check" type="checkbox" id="pv-ind"> Partial selection</label>'
          '</div><div class="pv-col">'
          '<label class="ds-choice"><input class="ds-radio" type="radio" name="pv-r" checked> Monthly</label>'
          '<label class="ds-choice"><input class="ds-radio" type="radio" name="pv-r"> Annually</label>'
          '<label class="ds-choice"><input class="ds-switch" type="checkbox" checked> Notifications</label>'
          '</div></div>'
          '<p class="pv-meta">Inline, where a baseline shift would show: '
          'unchecked <input class="ds-check" type="checkbox"> '
          'checked <input class="ds-check" type="checkbox" checked> '
          'checked <input class="ds-check" type="checkbox" checked> — all on one line.</p>',
          "Checked fill is `ink`, matching the primary button. The tick is a centred "
          "mask and the box must not move between states."))

    a(sec("Search · Number · Tag input", "components-form",
          '<div class="pv-cols3">'
          f'<label class="ds-search">{I["search"]}'
          '<input class="ds-input" type="search" placeholder="Search invoices"></label>'
          '<div class="ds-number-group"><input class="ds-input ds-number" value="1248.00">'
          '<span class="ds-number-steppers"><button aria-label="Increase">+</button>'
          '<button aria-label="Decrease">-</button></span></div>'
          '<div class="ds-taginput"><span class="ds-chip">design</span>'
          '<span class="ds-chip">tokens</span><input placeholder="Add tag"></div></div>',
          "Numeric fields are right-aligned tabular mono, so a column of them lines "
          "up. A tag field grows as chips wrap; it never scrolls horizontally."))

    a(sec("Slider", "components-form",
          '<div class="ds-slider"><div class="ds-slider-track">'
          '<span class="ds-slider-fill" style="width:45%"></span>'
          '<span class="ds-slider-thumb" style="left:45%"></span></div>'
          '<span class="ds-slider-value">45</span></div>',
          "Filled track is `ink`. The thumb keeps a border-strong edge or it vanishes "
          "on the track. Always paired with a numeric readout."))

    a(sec("File upload", "components-form",
          f'<div class="ds-dropzone">{I["upload"]}'
          '<span class="ds-dropzone-title">Drop files or click to browse</span>'
          '<span class="ds-dropzone-hint">PNG, PDF or CSV — up to 10 MB</span></div>'
          '<div class="ds-filelist" style="margin-top:var(--ds-space-3)">'
          '<div class="ds-filerow"><span class="ds-filerow-thumb"></span>statement-q3.pdf'
          '<span class="ds-filerow-spacer"></span>'
          f'<button class="ds-btn ds-iconbtn ds-btn--s ds-btn--plain ds-btn--neutral" aria-label="Remove">{I["x"]}</button>'
          '<div class="ds-filerow-progress"><span style="width:62%"></span></div></div>'
          '<div class="ds-filerow"><span class="ds-filerow-thumb"></span>'
          '<span class="ds-filerow-error">ledger.xlsx — exceeds 10 MB</span>'
          '<span class="ds-filerow-spacer"></span>'
          f'<button class="ds-btn ds-iconbtn ds-btn--s ds-btn--plain ds-btn--neutral" aria-label="Remove">{I["x"]}</button>'
          '</div></div>',
          "The dashed border is the one sanctioned dashed line in the system. Progress "
          "is per file, and a failed file stays in the list with its reason."))

    a(sec("Combobox", "components-form",
          '<div class="ds-combobox" style="max-width:var(--ds-container-popover-max)">'
          '<input class="ds-input" value="frankf" style="margin-bottom:var(--ds-space-1)">'
          '<div class="ds-listbox"><div class="ds-listbox-items">'
          f'<div class="ds-option" aria-selected="true">{I["check"]}'
          '<span>Frank<mark>furt</mark></span></div>'
          '<div class="ds-option" data-active><span>Frank<mark>lin Park</mark></span></div>'
          '<div class="ds-option"><span>Frank<mark>fort</mark></span></div>'
          '<div class="ds-option-empty">No matches for “frankf”</div></div></div></div>',
          "Matches are highlighted with weight, never a background tint — a highlight "
          "background would collide with the accent-subtle selected state."))

    a(sec("Date picker", "components-form", calendar(),
          "Selected is `ink` (a commitment); today is an `accent` dot (a landmark). "
          "Range interiors are square so a run of days reads as one bar."))

    a(sec("Command palette", "components-form",
          '<div class="ds-palette">'
          f'<div class="ds-palette-search">{I["search"]}'
          '<input placeholder="Type a command or search…"></div>'
          '<div class="ds-palette-results">'
          '<div class="ds-palette-group">Actions</div>'
          f'<div class="ds-palette-item" data-active>{I["plus"]}New invoice'
          '<span class="ds-palette-shortcut">⌘N</span></div>'
          f'<div class="ds-palette-item">{I["upload"]}Import statement'
          '<span class="ds-palette-shortcut">⌘I</span></div>'
          '<div class="ds-palette-group">Navigate</div>'
          f'<div class="ds-palette-item">{I["users"]}Members</div></div></div>',
          "Keyboard highlight and pointer hover are the same visual state, and only "
          "one is active at a time. Rows hover with control-subtle, because a palette "
          "is a raised surface."))

    a(sec("App bar", "components-layout",
          '<header class="ds-appbar" style="position:static">'
          '<span class="ds-appbar-brand">Ledger</span>'
          '<span class="ds-appbar-spacer"></span>'
          f'<label class="ds-search ds-appbar-search">{I["search"]}'
          '<input class="ds-input" type="search" placeholder="Search"></label>'
          '<span class="ds-appbar-spacer"></span>'
          f'<button class="ds-btn ds-iconbtn ds-btn--plain ds-btn--neutral" aria-label="Settings">{I["cog"]}</button>'
          '<span class="ds-avatar ds-avatar--sm">AO</span></header>',
          "Shares the page fill, separated by a border alone — never raised, never a "
          "shadow. Icon actions are `plain`: a row of tinted chips across every "
          "screen is what plain exists to prevent."))

    a(sec("Sidebar", "components-nav",
          '<nav class="ds-sidebar"><ul class="ds-navlist">'
          f'<li><a class="ds-navitem" aria-current="page">{I["home"]}Overview</a></li>'
          f'<li><a class="ds-navitem">{I["users"]}Members</a></li>'
          f'<li><a class="ds-navitem">{I["file"]}Invoices</a></li>'
          '<li class="ds-navsection">Settings</li>'
          f'<li><a class="ds-navitem">{I["cog"]}Preferences</a></li>'
          '<li><a class="ds-navitem ds-navitem--nested">Billing</a></li></ul></nav>',
          "Items sit 2px apart, not 8: a nav list is one object. Active is "
          "accent-subtle + accent-text, the same language as a selected row. Nested "
          "items indent by exactly one icon column."))

    a(sec("Breadcrumb · Pagination · Stepper", "components-nav",
          '<nav class="ds-breadcrumb"><a href="#">Workspace</a>'
          f'<span class="ds-breadcrumb-sep">{I["chevron-r"]}</span><a href="#">Projects</a>'
          f'<span class="ds-breadcrumb-sep">{I["chevron-r"]}</span>'
          '<span aria-current="page">Q3 Redesign</span></nav>'
          '<div class="ds-pagination" style="margin-top:var(--ds-space-4)">'
          '<span class="ds-pagination-summary">41–60 of 312</span>'
          '<span class="ds-pagination-spacer"></span><div class="ds-pagination-list">'
          f'<button class="ds-btn ds-iconbtn ds-btn--s ds-btn--plain ds-btn--neutral" aria-label="Previous">{I["chevron-l"]}</button>'
          '<button class="ds-btn ds-btn--s ds-btn--square ds-btn--plain ds-btn--neutral">1</button>'
          '<span class="ds-pagination-gap">…</span>'
          '<button class="ds-btn ds-btn--s ds-btn--square ds-btn--plain ds-btn--neutral">4</button>'
          '<button class="ds-btn ds-btn--s ds-btn--square ds-btn--filled ds-btn--neutral" aria-current="page">5</button>'
          '<button class="ds-btn ds-btn--s ds-btn--square ds-btn--plain ds-btn--neutral">6</button>'
          '<span class="ds-pagination-gap">…</span>'
          '<button class="ds-btn ds-btn--s ds-btn--square ds-btn--plain ds-btn--neutral">16</button>'
          f'<button class="ds-btn ds-iconbtn ds-btn--s ds-btn--plain ds-btn--neutral" aria-label="Next">{I["chevron-r"]}</button>'
          '</div></div>'
          '<div class="ds-stepper" style="margin-top:var(--ds-space-6)">'
          f'<div class="ds-step" data-state="complete"><span class="ds-step-marker">{I["check"]}</span>'
          '<span class="ds-step-label">Details</span></div>'
          '<span class="ds-step-connector" data-state="complete"></span>'
          '<div class="ds-step" data-state="current"><span class="ds-step-marker">2</span>'
          '<span class="ds-step-label">Review</span></div>'
          '<span class="ds-step-connector"></span>'
          '<div class="ds-step"><span class="ds-step-marker">3</span>'
          '<span class="ds-step-label">Confirm</span></div></div>',
          "The current page is `ink`, not accent. The current breadcrumb is present "
          "but not a link. Complete and current steps are both ink; upcoming is control."))

    a(sec("Tabs · Segmented", "components-core",
          '<div class="ds-tabs"><button class="ds-tab" aria-selected="true">Overview</button>'
          '<button class="ds-tab">Members</button><button class="ds-tab">Billing</button></div>'
          '<div class="ds-segmented" role="tablist" style="margin-top:var(--ds-space-4)">'
          '<button role="tab" aria-selected="true">All</button>'
          '<button role="tab" aria-selected="false">Active</button>'
          '<button role="tab" aria-selected="false">Archived</button></div>',
          "Underline for views (pages of content), segmented for filters (lenses on "
          "the same content). The choice is semantic, not decorative."))

    a(sec("Card · Badge · Chip · Avatar", "components-core",
          '<div class="pv-cols"><div class="ds-card">'
          '<h3 class="ds-card-title">Northwind Trading</h3>'
          '<p class="ds-card-subtitle">Net 30 · 14 open invoices</p></div>'
          '<div class="ds-card ds-card--interactive"><h3 class="ds-card-title">Interactive</h3>'
          '<p class="ds-card-subtitle">Hover shifts background. No lift, no shadow.</p>'
          '</div></div>'
          '<div class="pv-row" style="margin-top:var(--ds-space-4)">'
          '<span class="ds-badge">Draft</span>'
          '<span class="ds-badge ds-badge--success">Paid</span>'
          '<span class="ds-badge ds-badge--warning">Due soon</span>'
          '<span class="ds-badge ds-badge--danger">Overdue</span>'
          '<span class="ds-badge ds-badge--info">Scheduled</span></div>'
          '<div class="pv-row" style="margin-top:var(--ds-space-3)">'
          f'<span class="ds-chip ds-chip--selected">{I["check"]}Last 30 days</span>'
          '<span class="ds-chip">Unpaid</span><span class="ds-chip">EUR</span></div>'
          '<div class="pv-row" style="margin-top:var(--ds-space-3)">'
          '<span class="ds-avatar ds-avatar--xs">JD</span>'
          '<span class="ds-avatar ds-avatar--sm">AK</span>'
          '<span class="ds-avatar">MR</span>'
          '<span class="ds-avatar ds-avatar--org">N</span>'
          '<span class="ds-avatar ds-avatar--lg">SP</span></div>',
          "A Badge is a label: fill only, no edge. A Chip is a control: fill plus "
          "edge, because it floats free on the page. Circles for people, squares for "
          "organisations, neutral fallbacks always."))

    a(sec("Accordion", "components-content",
          '<div class="ds-accordion">'
          '<div class="ds-accordion-item"><button class="ds-accordion-header" aria-expanded="false">'
          f'How is billing calculated?{I["chevron-r"]}</button></div>'
          '<div class="ds-accordion-item"><button class="ds-accordion-header" aria-expanded="true">'
          f'What happens when I cancel?{I["chevron-r"]}</button>'
          '<div class="ds-accordion-panel">Your workspace stays active until the end of '
          'the paid period, then moves to read-only. Nothing is deleted for 90 days.</div></div>'
          '<div class="ds-accordion-item"><button class="ds-accordion-header" aria-expanded="false">'
          f'Can I export my data?{I["chevron-r"]}</button></div></div>',
          "The whole header row is the trigger. The chevron rotates via transform; "
          "panel height is never animated. Headers carry no margin."))

    a(sec("Overlays", "components-core",
          '<div class="pv-cols">'
          '<div><span class="pv-lbl">Menu</span><div class="ds-menu">'
          f'<div class="ds-menu-item">{I["pencil"]}Rename</div>'
          f'<div class="ds-menu-item" aria-checked="true">{I["check"]}Show archived</div>'
          '<hr class="ds-menu-sep">'
          f'<div class="ds-menu-item ds-menu-item--danger">{I["trash"]}Delete</div></div></div>'
          '<div><span class="pv-lbl">Popover</span><div class="ds-popover">'
          '<strong>Filter by amount</strong><p class="pv-meta">Interactive content, '
          'opens on click, takes focus. Not a tooltip.</p></div></div></div>'
          '<div class="pv-cols" style="margin-top:var(--ds-space-4)">'
          '<div><span class="pv-lbl">Tooltip</span>'
          '<span class="ds-tooltip">Plain text only</span></div>'
          '<div><span class="pv-lbl">Toast</span>'
          '<div class="ds-toast">Invoice sent to Northwind Trading.</div></div></div>'
          '<div class="pv-cols" style="margin-top:var(--ds-space-4)">'
          '<div><span class="pv-lbl">Modal</span><div class="ds-modal">'
          '<h3 class="ds-card-title">Void this invoice?</h3>'
          '<p class="ds-card-subtitle">INV-2046 will be marked void. This cannot be undone.</p>'
          '<div class="pv-row" style="justify-content:flex-end;margin-top:var(--ds-space-4)">'
          '<button class="ds-btn ds-btn--outline ds-btn--neutral">Cancel</button>'
          '<button class="ds-btn ds-btn--filled ds-btn--destructive">Void invoice</button>'
          '</div></div></div>'
          '<div><span class="pv-lbl">Drawer</span>'
          '<div class="ds-drawer ds-drawer--sm" style="height:auto">'
          '<div class="ds-drawer-header"><strong>Invoice details</strong>'
          f'<button class="ds-btn ds-iconbtn ds-btn--plain ds-btn--neutral" aria-label="Close">{I["x"]}</button></div>'
          '<p class="pv-meta">Flush to the viewport edge, so no radius on that side.</p>'
          '</div>'
          '<div class="ds-drawer ds-drawer--bottom" style="margin-top:var(--ds-space-3)">'
          '<span class="ds-drawer-handle"></span>'
          '<p class="pv-meta">Bottom sheet — top corners only.</p></div>'
          '<div class="ds-backdrop" style="height:var(--ds-size-40);'
          'border-radius:var(--ds-radius-md);margin-top:var(--ds-space-3)"></div>'
          '<p class="pv-meta">Backdrop: a flat scrim, never blurred.</p>'
          '</div></div>',
          "Content inside a raised overlay hovers with control-subtle — surface-hover "
          "equals surface-raised in dark mode and would show nothing. The tooltip "
          "computes its own foreground."))

    a(sec("Inline alert", "components-feedback",
          f'<div class="ds-alert ds-alert--danger">{I["alert"]}<div>'
          '<strong class="ds-alert-title">Payment failed</strong>'
          '<p class="ds-alert-body">The card ending 4242 was declined. Update it to keep '
          'your workspace active.</p></div></div>'
          f'<div class="ds-alert ds-alert--success" style="margin-top:var(--ds-space-2)">{I["check"]}<div>'
          '<strong class="ds-alert-title">Invoice sent</strong>'
          '<p class="ds-alert-body">Northwind Trading will receive it shortly.</p></div></div>'
          f'<div class="ds-alert ds-alert--info" style="margin-top:var(--ds-space-2)">{I["info"]}<div>'
          '<strong class="ds-alert-title">Scheduled maintenance</strong>'
          '<p class="ds-alert-body">Exports are unavailable Sunday 02:00–04:00 UTC.</p>'
          '</div></div>',
          "Fill only, no border. Colour is always paired with an icon and a status "
          "word, and the body text stays `text` — tinting the paragraph shouts."))

    a(sec("Progress · Spinner · Skeleton", "components-feedback",
          '<div class="pv-cols3">'
          '<div><span class="pv-lbl">determinate</span>'
          '<div class="ds-progress"><span style="width:25%"></span></div>'
          '<p class="pv-meta">Uploading 3 of 12 — 25%</p></div>'
          f'<div><span class="pv-lbl">spinner</span><div class="pv-row">{I["spinner"]}'
          f'<span class="ds-spinner ds-spinner--sm">{I["spinner"]}</span></div>'
          '<p class="pv-meta">Inherits currentColor, so it works on any surface.</p></div>'
          '<div><span class="pv-lbl">skeleton</span>'
          '<div class="ds-skeleton" style="width:100%"></div>'
          '<div class="ds-skeleton" style="width:100%;margin-top:var(--ds-space-2)"></div>'
          '<div class="ds-skeleton" style="width:60%;margin-top:var(--ds-space-2)"></div>'
          '<p class="pv-meta">Vary line widths — uniform bars read as a table.</p></div></div>',
          "`width` is the one property allowed to animate, because a progress bar is "
          "a width."))

    a(sec("Table · Data table", "components-data", table(),
          "Flush and borderless: rules do the work, full-bleed rather than inset. "
          "Numeric columns right-align, but only the body cells take tabular mono — a "
          "header is a word, not a number. The bulk bar replaces the toolbar in place."))

    a(sec("Tree", "components-data",
          '<ul class="ds-tree">'
          '<li><div class="ds-treerow"><button class="ds-twisty" aria-expanded="true">'
          f'{I["chevron-r"]}</button>{I["folder"]}Contracts</div>'
          '<ul class="ds-tree">'
          '<li><div class="ds-treerow" aria-selected="true"><span class="ds-twisty"></span>'
          f'{I["file"]}northwind-2026.pdf</div></li>'
          '<li><div class="ds-treerow"><span class="ds-twisty"></span>'
          f'{I["file"]}meridian-2025.pdf</div></li></ul></li>'
          '<li><div class="ds-treerow"><button class="ds-twisty" aria-expanded="false">'
          f'{I["chevron-r"]}</button>{I["folder"]}Statements</div></li></ul>',
          "Indents by exactly one icon column per level. No guide lines. The twisty is "
          "a separate target from the row: expanding must not also select."))

    a(sec("Description list", "components-data",
          '<div class="ds-card"><dl class="ds-dl">'
          '<dt>Invoice ID</dt><dd class="ds-num">inv_9Kd82LmQp4</dd>'
          '<dt>Status</dt><dd><span class="ds-badge ds-badge--success">Paid</span></dd>'
          '<dt>Amount</dt><dd class="ds-num">$1,248.00</dd>'
          '<dt>Purchase order</dt><dd class="ds-dl-empty">—</dd>'
          '<dt>Issued</dt><dd>14 March 2026</dd></dl></div>',
          "A fixed label column, so values start at a scannable position. An empty "
          "value is an em dash, never blank — blank reads as broken."))

    a(sec("Timeline", "components-data",
          '<ul class="ds-timeline">'
          '<li class="ds-timeline-day">Today</li>'
          '<li class="ds-event" data-current><strong>Amara Okafor</strong> approved the '
          'invoice<span class="ds-event-time" title="24 Aug 2026 06:12 UTC">3h ago</span></li>'
          '<li class="ds-event"><strong>James Reid</strong> left a comment'
          '<span class="ds-event-time" title="23 Aug 2026 17:40 UTC">Yesterday</span>'
          '<div class="ds-event-detail">Confirmed against the PO — safe to release '
          'payment.</div></li>'
          '<li class="ds-event"><strong>System</strong> generated the invoice'
          '<span class="ds-event-time">12 Mar 2026</span></li></ul>',
          "The connector stops at the last node. Relative time near, absolute far, "
          "with the exact value in a title attribute."))

    a(sec("Stat", "components-layout",
          '<div class="pv-cols3">'
          '<div class="ds-card"><div class="ds-stat-label">Monthly revenue</div>'
          '<div class="ds-stat-value">$48,290</div>'
          f'<div class="ds-stat-delta ds-stat-delta--good">{I["up"]}12.4%</div>'
          '<div class="ds-stat-caption">vs. last month</div></div>'
          '<div class="ds-card"><div class="ds-stat-label">Churn rate</div>'
          '<div class="ds-stat-value">2.1%</div>'
          f'<div class="ds-stat-delta ds-stat-delta--good">{I["down"]}0.6pp</div>'
          '<div class="ds-stat-caption">vs. last month</div></div>'
          '<div class="ds-card"><div class="ds-stat-label">P95 latency</div>'
          '<div class="ds-stat-value">184ms</div>'
          f'<div class="ds-stat-delta ds-stat-delta--bad">{I["up"]}22ms</div>'
          '<div class="ds-stat-caption">vs. last week</div>'
          '<svg class="ds-sparkline" viewBox="0 0 100 40" preserveAspectRatio="none">'
          '<polyline points="0,30 20,22 40,26 60,12 80,18 100,6" fill="none" '
          'stroke="currentColor" stroke-width="2"/></svg></div></div>',
          "Colour follows the interpretation, not the arrow: churn falling is good, "
          "latency rising is bad. Tabular mono so digits align across the row."))

    a(sec("Link · Layout utilities", "components-core",
          '<p class="pv-sub">Read the <a class="ds-link" href="#">billing '
          'documentation</a> or <a class="ds-link" href="#">contact support</a> — '
          'accent colour, underline on hover only.</p>'
          '<div class="ds-stack" style="max-width:var(--ds-container-modal-sm)">'
          '<div class="ds-row"><span class="ds-badge">ds-row</span>'
          '<span class="pv-meta">flex, centred, space-2 gap</span></div>'
          '<div class="ds-row"><span class="ds-badge">ds-stack</span>'
          '<span class="pv-meta">column, space-4 gap</span></div></div>',
          "The two layout primitives the system ships, so a page does not need its "
          "own flex utilities for the common cases."))

    a(sec("Empty state · Divider · Page header", "components-layout",
          '<div class="ds-card"><div class="ds-empty">'
          f'{I["file"]}<h3 class="ds-empty-title">No invoices yet</h3>'
          '<p class="ds-empty-body">Create your first invoice and it will appear here.</p>'
          '<button class="ds-btn ds-btn--filled ds-btn--neutral">New invoice</button>'
          '</div></div><hr class="ds-divider">'
          '<div class="ds-page-header"><h1 class="ds-page-title">Invoices</h1>'
          '<p class="ds-page-desc">Every invoice raised against your workspace, '
          'including drafts and voided records.</p></div>',
          "Empty-by-default, empty-by-filter and empty-by-error need different copy. "
          "A divider is the weakest separator; the page header has no bottom border "
          "because section-gap already separates."))
    return "".join(S)


def render(brand, tokens):
    _, failures = audit(tokens)
    head = (
        '<div class="pv-head"><div>'
        f'<h1 class="ds-page-title">{brand["name"]}</h1>'
        '<p class="ds-page-desc">Every component, rendered from the shipped '
        '<code>ds-components.css</code> — not a copy of it.</p>'
        f'<p class="pv-meta">radius {brand["radius"]} · density {brand["density"]} · '
        f'icons {brand["iconSet"]} · fonts {brand.get("fontPreset", "custom")} · '
        f'{"WCAG AA: all pairs pass" if not failures else f"WCAG AA: {failures} FAILING"}'
        '</p></div>'
        '<button class="ds-btn ds-btn--outline ds-btn--neutral" onclick="pvT()">'
        'Toggle theme</button></div>')
    body = (
        head
        + sec("Ramps", "foundations",
              swatches("neutral") + swatches("accent") + swatches("danger"))
        + sec("Semantic roles", "foundations",
              role_grid(tokens, ["bg", "surface", "surface-raised", "surface-hover",
                                 "control-subtle", "control", "control-hover"], "Surfaces")
              + role_grid(tokens, ["border-subtle", "border", "border-strong",
                                   "control-border"], "Borders")
              + role_grid(tokens, ["text", "text-muted", "text-subtle", "text-inverse"], "Text")
              + role_grid(tokens, ["ink", "ink-hover", "ink-active", "on-ink"],
                          "Ink — primary actions, checked controls")
              + role_grid(tokens, ["accent-subtle", "accent-muted", "accent-border",
                                   "accent", "accent-text", "on-accent", "focus-ring"],
                          "Accent — links, selection, focus, status")
              + role_grid(tokens, ["success-solid", "warning-solid", "danger-solid",
                                   "info-solid"], "Status"))
        + sec("Type scale", "foundations", type_rows())
        + components())
    return (
        "<!doctype html><html lang=en data-theme=light><head><meta charset=utf-8>"
        "<meta name=viewport content='width=device-width,initial-scale=1'>"
        f"<title>{brand['name']} — proof sheet</title><style>"
        f"{render_css(tokens, brand)}\n{sheet(P)}\n{PV_CSS}</style></head><body>"
        f'<div class="pv-wrap">{body}</div>'
        "<script>function pvT(){const r=document.documentElement;"
        "r.dataset.theme=r.dataset.theme==='dark'?'light':'dark';}"
        "const i=document.getElementById('pv-ind');if(i)i.indeterminate=true;</script>"
        "</body></html>")


def main():
    ap = argparse.ArgumentParser(description="Render a proof sheet from brand.json")
    ap.add_argument("brand")
    ap.add_argument("--out", default="proof.html")
    args = ap.parse_args()
    brand = load_brand(args.brand)
    Path(args.out).write_text(render(brand, build_tokens(brand)))
    print(f"Wrote {args.out}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
