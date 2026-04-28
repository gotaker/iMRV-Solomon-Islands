from __future__ import unicode_literals

import frappe
import frappe.utils

no_cache = True

def get_context(context):
	if frappe.session.user != "Guest":
		frappe.local.flags.redirect_location = "/app/main-dashboard"
		raise frappe.Redirect
