# Copyright (c) 2026, NetZeroLabs and contributors
# For license information, please see license.txt
"""
Shared PDF-export helpers for the 8 desk Tracking Reports.

Mirrors the existing `download_excel(columns, data)` pattern but produces a
print-ready PDF using the editorial Forest-and-Sage design system. Charts
are re-rendered server-side as inline SVG primitives — no JS dependency,
no axis-clip risk, no "undefined" tooltip risk that the 2026-04-30 audit
caught on the live charts.

Each report's `download_pdf()` whitelisted method calls
`render_tracking_report_pdf(...)` with its data shape; the helper writes
the PDF to `<site>/public/files/` and returns the URL for `window.open()`.
"""

from __future__ import annotations

import math
from typing import Any, Dict, Iterable, List, Optional, Sequence

import frappe
from frappe.utils import get_site_base_path, now
from frappe.utils.pdf import get_pdf

# Editorial palette translated to print-safe hex (per audit cheat sheet).
PALETTE = [
	"#01472e",   # forest         — primary series
	"#a3b18a",   # moss           — secondary series
	"#ccd5ae",   # sage           — tertiary
	"#e9edc9",   # olive          — quaternary
	"#48bb74",   # green-pop      — actual vs expected pairings (kept for parity with mitigation_report's own colour)
	"#ed6396",   # coral-pink     — only used as last-resort 6th series
]


def render_bar_svg(chart_data: Dict[str, Any], width: int = 720, height: int = 240) -> str:
	"""Render a grouped bar SVG from frappe-charts-shaped data.

	Input shape: { 'datasets': [{'name': str, 'values': [num, ...]}, ...], 'labels': [str, ...] }
	Output: a single <svg> string sized to (width, height) viewBox, fluid in container.
	"""
	if not chart_data:
		return _empty_chart_svg("No chart data", width, height)
	datasets = chart_data.get("datasets") or []
	labels = chart_data.get("labels") or []
	if not datasets or not labels:
		return _empty_chart_svg("No chart data", width, height)

	# Geometry
	pad_left = 60
	pad_right = 16
	pad_top = 24
	pad_bottom = 48
	plot_w = width - pad_left - pad_right
	plot_h = height - pad_top - pad_bottom

	# Find max value for Y scale
	all_values: List[float] = []
	for ds in datasets:
		for v in ds.get("values", []):
			try:
				all_values.append(float(v or 0))
			except (TypeError, ValueError):
				continue
	max_v = max(all_values) if all_values else 0
	if max_v <= 0:
		max_v = 1  # avoid div-by-zero

	# Group geometry: per-label group containing one bar per dataset
	n_groups = len(labels)
	n_series = len(datasets)
	group_w = plot_w / max(n_groups, 1)
	bar_w = (group_w * 0.7) / max(n_series, 1)
	bar_gap = (group_w * 0.3) / 2

	parts: List[str] = []
	parts.append(
		f'<svg class="chart" viewBox="0 0 {width} {height}" xmlns="http://www.w3.org/2000/svg" preserveAspectRatio="xMidYMid meet">'
	)
	# Y-axis grid lines + tick labels (4 horizontal lines)
	for i in range(5):
		y = pad_top + (plot_h * i / 4)
		val = max_v * (1 - i / 4)
		parts.append(
			f'<line x1="{pad_left}" y1="{y:.1f}" x2="{pad_left + plot_w:.1f}" y2="{y:.1f}" '
			f'stroke="rgba(1,71,46,0.08)" stroke-width="0.5"/>'
		)
		parts.append(
			f'<text class="axis" x="{pad_left - 6}" y="{y + 3:.1f}" text-anchor="end">{_compact(val)}</text>'
		)

	# Bars + X-axis labels
	for gi, label in enumerate(labels):
		group_x = pad_left + gi * group_w + bar_gap
		for si, ds in enumerate(datasets):
			values = ds.get("values", [])
			try:
				v = float(values[gi] if gi < len(values) else 0)
			except (TypeError, ValueError):
				v = 0
			bh = (v / max_v) * plot_h if max_v > 0 else 0
			bx = group_x + si * bar_w
			by = pad_top + plot_h - bh
			color = PALETTE[si % len(PALETTE)]
			parts.append(
				f'<rect x="{bx:.1f}" y="{by:.1f}" width="{bar_w:.1f}" height="{bh:.1f}" fill="{color}"/>'
			)
			# Data label above bar (only if there's vertical room)
			if bh > 16:
				parts.append(
					f'<text class="data-label" x="{bx + bar_w/2:.1f}" y="{by - 3:.1f}" text-anchor="middle" font-size="8">{_compact(v)}</text>'
				)
		# X-axis label (truncate if long)
		short = (str(label)[:18] + "…") if len(str(label)) > 18 else str(label)
		parts.append(
			f'<text class="axis" x="{group_x + group_w/2 - bar_gap:.1f}" y="{pad_top + plot_h + 14}" text-anchor="middle">{_x(short)}</text>'
		)

	# Legend (bottom)
	if n_series > 0:
		legend_y = height - 14
		legend_x = pad_left
		for si, ds in enumerate(datasets):
			color = PALETTE[si % len(PALETTE)]
			name = ds.get("name", f"Series {si+1}")
			parts.append(
				f'<rect x="{legend_x:.1f}" y="{legend_y - 8:.1f}" width="10" height="10" fill="{color}"/>'
			)
			parts.append(
				f'<text class="legend" x="{legend_x + 14:.1f}" y="{legend_y:.1f}">{_x(name)}</text>'
			)
			legend_x += 14 + len(name) * 5 + 18

	parts.append("</svg>")
	return "".join(parts)


def render_pie_svg(pie_data: Dict[str, Any], width: int = 320, height: int = 240) -> str:
	"""Render a pie/donut SVG with a side legend.

	Input shape: { 'data': [num, ...], 'labels': [str, ...] }
	"""
	if not pie_data:
		return _empty_chart_svg("No chart data", width, height)
	data = pie_data.get("data") or []
	labels = pie_data.get("labels") or []
	if not data or not labels:
		return _empty_chart_svg("No chart data", width, height)

	# Coerce floats
	values: List[float] = []
	for v in data:
		try:
			values.append(float(v or 0))
		except (TypeError, ValueError):
			values.append(0)
	total = sum(values)
	if total <= 0:
		return _empty_chart_svg("All segments zero", width, height)

	# Pie geometry
	cx = 100
	cy = height / 2
	r = min(80, height / 2 - 16)
	parts: List[str] = []
	parts.append(
		f'<svg class="chart" viewBox="0 0 {width} {height}" xmlns="http://www.w3.org/2000/svg" preserveAspectRatio="xMidYMid meet">'
	)

	# Slices
	angle_start = -math.pi / 2
	for i, v in enumerate(values):
		frac = v / total
		angle_end = angle_start + frac * 2 * math.pi
		x1 = cx + r * math.cos(angle_start)
		y1 = cy + r * math.sin(angle_start)
		x2 = cx + r * math.cos(angle_end)
		y2 = cy + r * math.sin(angle_end)
		large_arc = 1 if frac > 0.5 else 0
		color = PALETTE[i % len(PALETTE)]
		# Single full-circle case
		if frac >= 0.999:
			parts.append(
				f'<circle cx="{cx}" cy="{cy:.1f}" r="{r:.1f}" fill="{color}"/>'
			)
		else:
			d = (
				f"M {cx:.1f} {cy:.1f} "
				f"L {x1:.1f} {y1:.1f} "
				f"A {r:.1f} {r:.1f} 0 {large_arc} 1 {x2:.1f} {y2:.1f} Z"
			)
			parts.append(f'<path d="{d}" fill="{color}"/>')
		angle_start = angle_end

	# Donut hole + total label (always emit so single-segment pies don't read as a solid disk)
	parts.append(
		f'<circle cx="{cx}" cy="{cy:.1f}" r="{r * 0.45:.1f}" fill="#fefae0"/>'
	)
	parts.append(
		f'<text x="{cx}" y="{cy - 2:.1f}" text-anchor="middle" font-family="Anton" font-size="14" fill="#01472e">{_compact(total)}</text>'
	)
	parts.append(
		f'<text x="{cx}" y="{cy + 12:.1f}" text-anchor="middle" font-size="7" letter-spacing="0.16em" fill="#4d7a63" text-transform="uppercase">TOTAL</text>'
	)

	# Legend (right side, vertical)
	legend_x = 200
	for i, (lbl, v) in enumerate(zip(labels, values)):
		ly = 24 + i * 16
		if ly > height - 14:
			break  # no room for more
		color = PALETTE[i % len(PALETTE)]
		parts.append(
			f'<rect x="{legend_x}" y="{ly - 8}" width="10" height="10" fill="{color}"/>'
		)
		short = (str(lbl)[:22] + "…") if len(str(lbl)) > 22 else str(lbl)
		pct = (v / total * 100)
		parts.append(
			f'<text class="legend" x="{legend_x + 14}" y="{ly}">{_x(short)} <tspan fill="#4d7a63" font-size="8">({pct:.1f}%)</tspan></text>'
		)

	parts.append("</svg>")
	return "".join(parts)


def _empty_chart_svg(message: str, width: int, height: int) -> str:
	return (
		f'<svg class="chart" viewBox="0 0 {width} {height}" xmlns="http://www.w3.org/2000/svg" preserveAspectRatio="xMidYMid meet">'
		f'<rect x="0" y="0" width="{width}" height="{height}" fill="#fefae0" stroke="rgba(1,71,46,0.18)" stroke-width="1" stroke-dasharray="4 3"/>'
		f'<text x="{width/2}" y="{height/2}" text-anchor="middle" font-size="11" fill="#4d7a63" font-family="Inter">{_x(message)}</text>'
		f"</svg>"
	)


def _compact(v: float) -> str:
	"""Format a number into a compact axis label like 1.2K / 3.4M."""
	try:
		v = float(v)
	except (TypeError, ValueError):
		return ""
	abs_v = abs(v)
	if abs_v >= 1_000_000_000:
		return f"{v/1_000_000_000:.1f}B"
	if abs_v >= 1_000_000:
		return f"{v/1_000_000:.1f}M"
	if abs_v >= 1_000:
		return f"{v/1_000:.1f}K"
	if abs_v >= 1:
		return f"{int(v)}" if v == int(v) else f"{v:.1f}"
	if abs_v == 0:
		return "0"
	return f"{v:.2f}"


def _x(s: Any) -> str:
	"""Minimal XML escape for SVG inline text."""
	return (
		str(s)
		.replace("&", "&amp;")
		.replace("<", "&lt;")
		.replace(">", "&gt;")
		.replace('"', "&quot;")
	)


def _column_widths_pct(n_columns: int, hints: Optional[Sequence[int]] = None) -> List[int]:
	"""Spread n columns evenly across 100% unless hints are provided."""
	if hints and len(hints) == n_columns:
		return list(hints)
	if n_columns <= 0:
		return []
	even = int(100 / n_columns)
	widths = [even] * n_columns
	# Distribute leftover percentage points to the first columns
	leftover = 100 - sum(widths)
	for i in range(leftover):
		widths[i] += 1
	return widths


def _build_filter_chips(filter_state: Dict[str, Any]) -> List[Dict[str, str]]:
	"""Drop empty filter values and return [{label, value}, ...]."""
	chips: List[Dict[str, str]] = []
	for label, value in (filter_state or {}).items():
		if value in (None, "", " ", "None"):
			continue
		chips.append({"label": str(label), "value": str(value)})
	return chips


def render_tracking_report_pdf(
	*,
	report_slug: str,
	report_title: str,
	lede: str,
	columns: Sequence[str],
	data: Sequence[Sequence[Any]],
	chart_data: Optional[Dict[str, Any]] = None,
	pie_chart_data: Optional[Dict[str, Any]] = None,
	chart_caption_bar: str = "Aggregate trend",
	chart_caption_pie: str = "Sectoral breakdown",
	table_title: str = "Detail",
	filter_state: Optional[Dict[str, Any]] = None,
	orientation: str = "portrait",
	column_widths_hint: Optional[Sequence[int]] = None,
) -> str:
	"""Render the editorial PDF for one tracking report.

	Returns the public URL the JS handler can pass to ``window.open``.
	"""
	# Auto-orientation override: if there are >12 columns, force landscape.
	# Keeps wide tables readable without each report needing to remember.
	if len(columns) > 12 and orientation == "portrait":
		orientation = "landscape"

	# Render charts upfront (Jinja can't import the helper module on its own).
	bar_svg = render_bar_svg(chart_data) if chart_data else ""
	pie_svg = render_pie_svg(pie_chart_data) if pie_chart_data else ""

	context = {
		"report_title": report_title,
		"lede": lede,
		"columns": list(columns),
		"data": [list(row) for row in data],
		"chart_data": chart_data,
		"pie_chart_data": pie_chart_data,
		"chart_caption_bar": chart_caption_bar,
		"chart_caption_pie": chart_caption_pie,
		"table_title": table_title,
		"filter_state": _build_filter_chips(filter_state or {}),
		"user_email": frappe.session.user,
		"generated_at": now()[:19],
		"orientation": orientation,
		"mecdm_label": "Climate Change Division · MECDM · Government of Solomon Islands",
		"column_widths_pct": _column_widths_pct(len(columns), column_widths_hint),
		# Make the SVG renderers available inside the template namespace.
		"render_bar_svg": (lambda cd: bar_svg) if chart_data else (lambda cd: ""),
		"render_pie_svg": (lambda cd: pie_svg) if pie_chart_data else (lambda cd: ""),
	}

	html = frappe.render_template("templates/pdf/tracking_report.html", context)

	pdf = get_pdf(
		html,
		options={
			"page-size": "A4",
			"orientation": "Landscape" if orientation == "landscape" else "Portrait",
			"margin-top": "14mm",
			"margin-right": "12mm",
			"margin-bottom": "20mm",
			"margin-left": "12mm",
			"encoding": "UTF-8",
			"enable-local-file-access": None,
			"no-stop-slow-scripts": None,
			"print-media-type": None,
			"disable-smart-shrinking": None,
		},
	)

	site_path = get_site_base_path()
	now_token = now()[:-7].replace(" ", "").replace("-", "").replace(":", "")
	filename = f"{report_slug}-{now_token}.pdf"
	out_path = f"{site_path}/public/files/{filename}"
	with open(out_path, "wb") as fp:
		fp.write(pdf)
	return f"/files/{filename}"
