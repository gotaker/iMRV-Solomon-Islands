import frappe


def execute():
	"""Fix "Energy fuel List" → "Energy Fuel List" on the Sub Menu seed row.

	The seed JSON had a casing typo for the Energy → Energy Fuel List entry.
	JSON is fixed; this patch backfills the live DB so existing installs see
	the corrected label after migrate.
	"""
	rows = frappe.db.sql(
		"""SELECT name FROM `tabSub Menu`
		   WHERE sub_menu_label = 'Energy fuel List'""",
		as_dict=True,
	)
	if not rows:
		return
	for r in rows:
		frappe.db.set_value(
			"Sub Menu", r["name"], "sub_menu_label", "Energy Fuel List"
		)
	frappe.db.commit()
