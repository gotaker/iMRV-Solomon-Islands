# Copyright (c) 2023, NetZeroLabs and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document


class SideMenu(Document):
	pass

@frappe.whitelist(allow_guest=True)
def get_current_document_name():
    data = frappe.get_all('DocType', fields=['name'])
    names = [item['name'] for item in data]
    return names
import frappe


@frappe.whitelist(allow_guest=True)
def get_menu_items():
    menu_items = frappe.get_all("DocType", fields=["label"])

    return menu_items
