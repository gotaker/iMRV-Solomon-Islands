import frappe
from frappe.model.utils.rename_field import rename_field


def execute():
	# Side Menu Settings is a Single doctype — its values are rows in tabSingles
	# keyed by (doctype, field). Detect the legacy field name there rather than
	# via has_column() (which fails for Singles since they have no `tab<DocType>`
	# table). rename_field() handles the Singles update internally.
	if not frappe.db.exists(
		"Singles", {"doctype": "Side Menu Settings", "field": "route_logo"}
	):
		return
	rename_field("Side Menu Settings", "route_logo", "post_login_landing_route")
