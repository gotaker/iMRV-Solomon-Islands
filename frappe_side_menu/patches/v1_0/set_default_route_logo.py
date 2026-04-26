import frappe


def execute():
	# Side Menu Settings is a Single doctype — values live in tabSingles, not a
	# `tabSide Menu Settings` table. Use meta.get_field() (which reads the
	# in-memory doctype definition) instead of has_column() (which queries
	# information_schema and raises TableMissingError for Singles).
	meta = frappe.get_meta("Side Menu Settings")
	field = (
		"post_login_landing_route"
		if meta.get_field("post_login_landing_route")
		else "route_logo"
	)
	current = frappe.db.get_single_value("Side Menu Settings", field)
	if current:
		return
	frappe.db.set_single_value("Side Menu Settings", field, "main-dashboard")
