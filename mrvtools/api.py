import frappe


@frappe.whitelist()
def get_approvers():
    # Explicit order_by — v16 flipped the default from `modified DESC` to
    # `creation DESC`; we pin alphabetical here so the UI's approver dropdown
    # stays deterministic across framework upgrades.
    doc= frappe.db.get_list("Role",
        fields=['name'],
        filters={
            "name":["Like","%Approver%"]
        },
        order_by="name asc",
        pluck="name",
        ignore_permissions=True)
    return doc

@frappe.whitelist()
def route_user():
    frappe.set_route("Form","Approved User",frappe.session.user )


# Hard-coded allowlist for `get_data`. Each key is a doctype that this endpoint
# is genuinely meant to expose; the value is the explicit field list that may
# leave the server. Two non-negotiable rules for editing this map:
#
#   1. NEVER add a doctype that holds user/admin/internal data (e.g. User,
#      Email Account, Communication, File, Comment, Project, Adaptation,
#      Mitigations, GHG Inventory, Climate Finance, DocShare, Activity Log).
#      Black-box audit on 2026-04-29 found `get_data` was leaking active
#      `reset_password_key` tokens for 66 users + a plaintext SMTP password
#      via `?doctype=User` and `?doctype=Email Account` — both were guest-
#      accessible. The allowlist exists to make that class of leak impossible
#      to re-introduce by a single one-line change.
#
#   2. NEVER include any field whose Doctype Meta says fieldtype == "Password",
#      and never include any of: password, new_password, reset_password_key,
#      reset_password_link_sent, api_secret, api_key, secret, otp_secret. The
#      response shape filter at the bottom of `get_data` enforces this even
#      if a future edit forgets — defense in depth.
#
# Doctypes here are public-side master-data lookups (reference tables seeded
# from mrvtools/master_data/*.json) used by report dropdowns. They contain no
# PII and no internal config.
_GET_DATA_ALLOWED_DOCTYPES: dict[str, list[str]] = {
    "Project Key Sector": ["name", "key_sector"],
    "Project Key Sub Sector": ["name", "key_sub_sector", "key_sector"],
    "Project Objective": ["name", "objective"],
    "Project Included In": ["name", "included_in"],
    "Adaptation Category": ["name", "category"],
    "GHG Sector": ["name", "ghg_sector"],
    "GHG Sub Sector": ["name", "ghg_sub_sector", "ghg_sector"],
    "GHG Category": ["name", "ghg_category"],
    "GHG Sub Category": ["name", "ghg_sub_category", "ghg_category"],
    "SDG Category": ["name", "sdg"],
    "NDP Coverage": ["name", "ndp_coverage"],
    "NDP Objective Coverage": ["name", "ndp_objective_coverage"],
}

# Field names that must NEVER appear in a `get_data` response, regardless of
# what the per-doctype allowlist says. Defense-in-depth: the per-doctype
# allowlist already excludes these, but if a future edit accidentally adds one,
# the response filter strips it before serialisation.
_FORBIDDEN_FIELDS: frozenset[str] = frozenset({
    "password",
    "new_password",
    "reset_password_key",
    "reset_password_link_sent",
    "api_secret",
    "api_key",
    "secret",
    "otp_secret",
    "smtp_password",
    "smtp_pass",
    "encryption_key",
})

# Cap returned rows. The legacy implementation defaulted to "no limit" (the
# `frappe.get_all` default of `limit_page_length=0`); restoring an explicit
# upper bound prevents an authorised role from using this endpoint as a bulk
# exfiltration channel even after permission filtering.
_GET_DATA_MAX_LIMIT: int = 100


@frappe.whitelist()
def get_data(doctype):
    # Locked down 2026-04-29 (was `allow_guest=True`, `fields=["*"]`, no allowlist).
    # See _GET_DATA_ALLOWED_DOCTYPES above for the rules. order_by stays pinned to
    # `modified desc` to preserve v15 behavior — v16 changed the default sort
    # for get_all()/get_list()/get_value() from `modified` to `creation`.
    if not isinstance(doctype, str) or doctype not in _GET_DATA_ALLOWED_DOCTYPES:
        # Don't leak the allowlist by reflecting the doctype name back. A
        # generic PermissionError surfaces as 403 + "Not permitted" — same
        # response whether the doctype is unknown, deny-listed, or just
        # mistyped. That denies the attacker a doctype-enumeration oracle.
        raise frappe.PermissionError("Not permitted")

    fields = _GET_DATA_ALLOWED_DOCTYPES[doctype]

    # `frappe.get_list` (NOT `get_all`) — get_all unconditionally injects
    # ignore_permissions=True (see frappe/__init__.py:2050). get_list runs
    # through DatabaseQuery with permission checks, so rows the caller can't
    # read are filtered server-side in a single query (no N+1 has_permission
    # loop required).
    doc = frappe.get_list(
        doctype,
        fields=fields,
        order_by="modified desc",
        limit_page_length=_GET_DATA_MAX_LIMIT,
    )

    # Defense-in-depth: strip any forbidden field names before returning.
    # The allowlist already excludes these, but if a future edit slips one
    # through, this final pass denies the leak.
    safe_rows: list[dict] = []
    for row in doc or []:
        safe_rows.append({k: v for k, v in row.items() if k not in _FORBIDDEN_FIELDS})
    return safe_rows


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
    # System Manager only — without this, any logged-in role with a session
    # could bulk-rename every User on the site via one HTTP POST. Discovered
    # by 2026-04-29 stress-test pass on top of the get_data leak fix.
    frappe.only_for("System Manager")
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