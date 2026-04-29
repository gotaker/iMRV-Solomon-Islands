import frappe


def execute():
	# IPPU Emission Factors Master List is a Single doctype (issingle=1) but
	# its Sub Menu entry was seeded with is_single=0, so the drawer routed to
	# the list URL where Single doctypes don't render usefully. Mark it Single.
	rows = frappe.db.sql(
		"""SELECT name FROM `tabSub Menu`
		   WHERE sub_menu_doc=%s AND is_single=0""",
		("IPPU Emission Factors Master List",),
		as_dict=True,
	)
	for row in rows:
		frappe.db.set_value("Sub Menu", row["name"], "is_single", 1)
	if rows:
		frappe.db.commit()
