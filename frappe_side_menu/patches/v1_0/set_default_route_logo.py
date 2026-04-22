import frappe


def execute():
	current = frappe.db.get_single_value("Side Menu Settings", "route_logo")
	if current:
		return
	frappe.db.set_single_value("Side Menu Settings", "route_logo", "main-dashboard")
