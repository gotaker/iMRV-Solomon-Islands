from __future__ import unicode_literals
import frappe
import frappe.utils
import json
import calendar
from frappe import _
from frappe.utils import getdate,nowdate
from datetime import date
no_cache = True

def get_context(context):
	if frappe.session.user != "Guest":
		frappe.local.flags.redirect_location = "/" if frappe.session.data.user_type=="Website User" else "/desk"
		raise frappe.Redirect
