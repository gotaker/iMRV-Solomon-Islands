# Copyright (c) 2023, tridotstech and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document

class MasterDataTest(Document):
	pass
	# docs = frappe.db.get_all("Master Data Test",
	# 		  fields = ["module","table","impact_area","indicator"])
	
	# frappe.log_error("Master Values", docs)