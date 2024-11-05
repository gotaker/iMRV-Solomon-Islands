# Copyright (c) 2024, tridotstech and contributors
# For license information, please see license.txt

import frappe
from frappe.model.naming import getseries
from frappe.model.document import Document

class ProjectActions(Document):
	def autoname(self):
		naming = "A-"
		if self.cause == "Climate Change":
			naming += "1"
		elif self.cause == "Not Defined":
			naming += "2"
		else:
			naming += "0"


		if self.focus == "Adaptation":
			naming += "1"
		elif self.focus == "Mitigation":
			naming += "2"
		elif self.focus == "Cross-Cutting":
			naming += "3"
		elif self.focus == "Enablers":
			naming += "4"
		elif self.focus == "Transparency":
			naming += "5"
		elif self.focus == "Other":
			naming += "6"
		else:
			naming += "0"


		if self.area == "National":
			naming += "1-"
		elif self.area == "Sub-national":
			naming += "2-"
		else:
			naming += "0-"

			
		name = getseries(naming, 3)
		self.name = naming + name