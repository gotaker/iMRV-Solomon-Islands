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


@frappe.whitelist()
def replace_email_domain(old_domain, new_domain, dry_run=1):
    """One-shot: rewrite <local>@<old_domain> to <local>@<new_domain>
    across Contact, Contact Email, and User records.

    User records are renamed via frappe.rename_doc so every foreign-key
    reference (owner fields, comments, session history, etc.) is updated
    atomically — a raw SQL UPDATE would leave those FKs pointing at a
    now-missing User row.

    Pass dry_run=0 to actually apply changes. The default dry_run=1 just
    returns a preview of what would change.

    Invoke with:
        bench --site <site> execute mrvtools.api.replace_email_domain \
            --kwargs '{"old_domain": "tridotstech.com", "new_domain": "netzerolabs.io", "dry_run": 0}'
    """
    dry_run = int(dry_run)
    suffix_old = f"@{old_domain}"
    suffix_new = f"@{new_domain}"
    changes = {"contacts": [], "contact_emails": [], "users": []}

    for row in frappe.get_all(
        "Contact",
        filters={"email_id": ["like", f"%{suffix_old}"]},
        fields=["name", "email_id"],
    ):
        new_email = row.email_id.replace(suffix_old, suffix_new)
        changes["contacts"].append({"name": row.name, "old": row.email_id, "new": new_email})
        if not dry_run:
            frappe.db.set_value("Contact", row.name, "email_id", new_email)

    for row in frappe.get_all(
        "Contact Email",
        filters={"email_id": ["like", f"%{suffix_old}"]},
        fields=["name", "parent", "email_id"],
    ):
        new_email = row.email_id.replace(suffix_old, suffix_new)
        changes["contact_emails"].append(
            {"name": row.name, "parent": row.parent, "old": row.email_id, "new": new_email}
        )
        if not dry_run:
            frappe.db.set_value("Contact Email", row.name, "email_id", new_email)

    for row in frappe.get_all(
        "User",
        filters={"name": ["like", f"%{suffix_old}"]},
        fields=["name"],
    ):
        new_name = row.name.replace(suffix_old, suffix_new)
        changes["users"].append({"old": row.name, "new": new_name})
        if not dry_run:
            frappe.rename_doc("User", row.name, new_name, merge=False, force=True)

    if not dry_run:
        frappe.db.commit()

    return {"dry_run": bool(dry_run), "changes": changes}