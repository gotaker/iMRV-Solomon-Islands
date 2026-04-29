import frappe


def execute():
	if not frappe.db.exists("Side Menu", "Document Resorce Tool"):
		return

	try:
		if frappe.db.exists("Side Menu", "Document Resource Tool"):
			frappe.delete_doc(
				"Side Menu", "Document Resorce Tool",
				ignore_permissions=True, force=True,
			)
		else:
			frappe.rename_doc(
				"Side Menu", "Document Resorce Tool", "Document Resource Tool",
				force=True, merge=False, rebuild_search=True,
			)
			# rename_doc updates Link fields but not the implicit child-table
			# parent column. Backfill Sub Menu / Sub Menu Group rows so child
			# rows whose parent='Document Resorce Tool' don't become orphans.
			frappe.db.sql(
				"UPDATE `tabSub Menu` SET parent=%s WHERE parent=%s",
				("Document Resource Tool", "Document Resorce Tool"),
			)
			frappe.db.sql(
				"UPDATE `tabSub Menu Group` SET parent=%s WHERE parent=%s",
				("Document Resource Tool", "Document Resorce Tool"),
			)
			frappe.db.set_value(
				"Side Menu", "Document Resource Tool", "label", "Document Resource Tool",
			)
		frappe.db.commit()
	except Exception:
		frappe.db.rollback()
		frappe.log_error("fix_document_resource_tool_typo", frappe.get_traceback())
		raise
