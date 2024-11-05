import frappe

@frappe.whitelist()
def get_approvers():
    doc= frappe.db.get_list("Role",
        fields=['name'],
        filters={
            "name":["Like","%Approver%"]
        },
        pluck="name",
        ignore_permissions=True)
    return doc

@frappe.whitelist()
def route_user():
    frappe.set_route("Form","Approved User",frappe.session.user )


@frappe.whitelist(allow_guest = True)
def get_data(doctype):
    doc = frappe.db.get_all(doctype,fields = ["*"])
    return doc if doc else []