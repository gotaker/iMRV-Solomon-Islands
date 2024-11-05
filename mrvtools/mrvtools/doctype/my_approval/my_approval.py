# Copyright (c) 2024, tridotstech and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document

class MyApproval(Document):
	pass

@frappe.whitelist(allow_guest=True)
def insert_record(created_by,date,reference_name,reference_doctype,approver = None):
	doc = frappe.new_doc("My Approval")
	doc.created_by = created_by
	doc.reference_name = reference_name
	doc.reference_doctype = reference_doctype
	doc.approver = approver
	doc.date = date
	doc.insert(ignore_permissions = True)
	frappe.db.commit()

@frappe.whitelist(allow_guest=True)
def delete_record(reference_name,reference_doctype):
	doc = frappe.get_doc("My Approval",{"reference_name":reference_name,"reference_doctype":reference_doctype})
	doc.delete(ignore_permissions = True)
	frappe.db.commit()

def get_query_conditions(user):
	
	if "System Manager" not in frappe.get_roles(user) and "MRV Admin"  not in frappe.get_roles(user):
		return f"""(`tabMy Approval` .approver = '{user}')"""