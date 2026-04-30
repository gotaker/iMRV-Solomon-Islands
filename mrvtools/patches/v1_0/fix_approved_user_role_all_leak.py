import frappe


def execute():
	"""Close the `Approved User` role-leak.

	The `Approved User` doctype shipped with a single DocPerm row whose
	role was `"All"` — a Frappe built-in that grants the perm to every
	authenticated user. Combined with `frappe_side_menu.api.get_menulist`'s
	`frappe.has_permission(d, "read")` filter, this caused the USERS
	submenu (parent + "Approved Users" leaf) to render in the drawer
	even for users with zero explicitly-assigned roles. The leaf then
	403'd on click — exactly the pattern documented in
	`reference_drawer_perm_filter.md`.

	The doctype JSON now scopes perms to System Manager + MRV Admin.
	This patch backfills `tabDocPerm` (and `tabCustom DocPerm` if a
	customer had explicitly set `role=All` via Customize Form) on
	existing installs so the schema reload from `bench migrate` doesn't
	leave a stale `role=All` row behind.
	"""
	# Reload the standard doctype perms first — bench migrate will do this
	# anyway, but be explicit so the patch is self-contained.
	frappe.reload_doctype("Approved User", force=True)

	# Sweep any leftover role=All rows on Approved User in BOTH DocPerm
	# tables (standard + customised). bench migrate doesn't strip rows
	# that were customised via Role Permission Manager.
	for table in ("tabDocPerm", "tabCustom DocPerm"):
		frappe.db.sql(
			f"DELETE FROM `{table}` WHERE parent = 'Approved User' AND role = 'All'"
		)

	# Clear the perm cache so the change takes effect immediately.
	frappe.clear_cache(doctype="Approved User")
	frappe.db.commit()
