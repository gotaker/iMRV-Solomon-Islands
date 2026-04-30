# Copyright (c) 2024, NetZeroLabs and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document


class MyApproval(Document):
	pass

# Hardened 2026-04-29: both endpoints were `allow_guest=True` and used
# `ignore_permissions=True` on insert/delete. That meant any unauthenticated
# requester could forge or revoke approval records for any (doctype, docname)
# pair — bypassing the workflow that the whole `My Approval` doctype exists to
# enforce. Now: login required, and the caller must have write permission on
# the referenced document before they can attach or detach an approval.

@frappe.whitelist()
def insert_record(created_by, date, reference_name, reference_doctype, approver=None):
	# Anchor the approval to a real referenced document the caller can write to.
	# Without this guard, a logged-in user with no permissions on Project X
	# could still seed a "Pending" approval row pointing at X and short-circuit
	# the workflow_state transitions wired in mrvtools/public/js/mrvtools.js.
	if not reference_doctype or not reference_name:
		frappe.throw("reference_doctype and reference_name are required", frappe.ValidationError)
	if not frappe.has_permission(reference_doctype, "write", doc=reference_name, user=frappe.session.user):
		raise frappe.PermissionError("Not permitted to create approval for this document")

	doc = frappe.new_doc("My Approval")
	doc.created_by = created_by
	doc.reference_name = reference_name
	doc.reference_doctype = reference_doctype
	doc.approver = approver
	doc.date = date
	# Keep ignore_permissions on the My Approval insert itself — most non-admin
	# roles don't have create perm on My Approval, but they DO have write perm
	# on the underlying Project / Adaptation, which is what the guard above
	# checks. The reference-doc perm check is the real gate.
	doc.insert(ignore_permissions=True)
	frappe.db.commit()


@frappe.whitelist()
def delete_record(reference_name, reference_doctype):
	if not reference_doctype or not reference_name:
		frappe.throw("reference_doctype and reference_name are required", frappe.ValidationError)
	if not frappe.has_permission(reference_doctype, "write", doc=reference_name, user=frappe.session.user):
		raise frappe.PermissionError("Not permitted to delete approval for this document")

	doc = frappe.get_doc("My Approval", {"reference_name": reference_name, "reference_doctype": reference_doctype})
	doc.delete(ignore_permissions=True)
	frappe.db.commit()

def get_query_conditions(user):
	# System Manager / MRV Admin see every record. Non-admins only see rows where
	# they are the listed approver.
	# Returning "" for the admin branch is required by Frappe v16 — its
	# permission-query-conditions layer rejects None and expects either a SQL
	# fragment string or "" (no additional filter).
	if "System Manager" not in frappe.get_roles(user) and "MRV Admin"  not in frappe.get_roles(user):
		return f"""(`tabMy Approval` .approver = '{user}')"""
	return ""