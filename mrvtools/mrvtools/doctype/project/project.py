# Copyright (c) 2023, NetZeroLabs and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
class Project(Document):

	def on_update(self):
		self.reload()
		if not self.project_id:
			self.project_id = self.name
			self.save(ignore_permissions = True)

	@frappe.whitelist()
	def get_user(self):
		doc = frappe.db.sql(f""" SELECT parent FROM `tabHas Role` WHERE role = 'Approver Project'""")
		return doc
	
	@frappe.whitelist()
	def get_all_datas(self):
		old_doc =self.get_doc_before_save()
		field_list = {}
		new_list=[]
		meta = frappe.get_meta(self.doctype)
		meta_dict = meta.as_dict()
		fields = meta_dict["fields"]
		for field in fields:
			if frappe.db.exists("Project",self.name):
				if field["fieldtype"] != "Date" and field["fieldtype"] != "Table MultiSelect" and field["fieldtype"] != "Table" and field["fieldtype"] != "Geolocation":
					if field["fieldname"] not in ["workflow_state","work_state","coordinates"]:
						if old_doc.get(field["fieldname"]) != self.get(field["fieldname"]):
							field_list[field["fieldname"]] = old_doc.get(field["fieldname"])

				elif field["fieldtype"] == "Date" and ((old_doc.get(field["fieldname"]) == None and self.get(field["fieldname"]) != None) or (old_doc.get(field["fieldname"]) != None)) :
					Date = frappe.utils.formatdate(old_doc.get(field["fieldname"]),"yyyy-mm-dd")

					if Date != self.get(field["fieldname"] ):
						field_list[field["fieldname"]] = old_doc.get(field["fieldname"])

				elif field["fieldtype"] == "Table MultiSelect":
					if len(self.get(field["fieldname"])) != len(old_doc.get(field["fieldname"])):
						if self.get(field["fieldname"]) != old_doc.get(field["fieldname"]):
							old_list=frappe.db.get_all(field["options"],
									fields = ["included_in"],
									filters = {"parent" : old_doc.name},pluck="included_in")
							field_list[field["fieldname"]] = ",".join(old_list)

					if len(self.get(field["fieldname"])) == len(old_doc.get(field["fieldname"])):
						for i in self.get(field["fieldname"]):
							new_list.append(i.included_in)
						old_list=frappe.db.get_all(field["options"],
									fields = ["included_in"],
									filters = {"parent" : old_doc.name},pluck="included_in")
						old_list.sort()
						new_list.sort()
						
						if old_list != new_list:
							if self.get(field["fieldname"]) != old_doc.get(field["fieldname"]):
								field_list[field["fieldname"]] = ",".join(old_list)

				elif field["fieldtype"] == "Geolocation":
					if old_doc.get(field["fieldname"]) != self.get(field["fieldname"]):
						field_list[field["fieldname"]] = old_doc.get(field["fieldname"])
		return field_list

		
	