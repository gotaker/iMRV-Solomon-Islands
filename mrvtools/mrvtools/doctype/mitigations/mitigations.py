# Copyright (c) 2023, tridotstech and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document

class Mitigations(Document):
	@frappe.whitelist()
	def before_saving_table(self):
		old_doc =self.get_doc_before_save()
		self.edited_performance_indicator = []
		for i in self.performance_indicator:
			row = self.append('edited_performance_indicator',{})
			row.performance_indicator = i.performance_indicator
			row.unit = i.unit
			row.expected_value = i.expected_value
			row.reference = i.reference

		self.performance_indicator = []
		for i in old_doc.performance_indicator:
			row = self.append('performance_indicator',{})
			row.performance_indicator = i.performance_indicator
			row.unit = i.unit
			row.expected_value = i.expected_value
			row.reference = i.reference

		if len(self.original_performance_indicator) == 0:	
			for i in old_doc.performance_indicator:
				row = self.append('original_performance_indicator',{})
				row.performance_indicator = i.performance_indicator
				row.unit = i.unit
				row.expected_value = i.expected_value
				row.reference = i.reference
		return "Yess"

	# @frappe.whitelist()
	


	
	@frappe.whitelist()
	def get_data(self):
		get_doc=frappe.db.sql(f"""SELECT included_in FROM `tabProject Included In ChildTable` WHERE parent ='{self.project_id}'""")
		return get_doc
	
	@frappe.whitelist()
	def get_user(self):
		doc = frappe.db.sql(f""" SELECT parent FROM `tabHas Role` WHERE role = 'Approver Mitigation Tracking'""")
		return doc
	
	
	@frappe.whitelist()
	def get_all_data(self):
		old_doc =self.get_doc_before_save()
		field_list = {}
		new_list1=[]
		new_list2=[]
		meta = frappe.get_meta(self.doctype)
		meta_dict = meta.as_dict()
		fields = meta_dict["fields"]
		for field in fields:
			if frappe.db.exists(self.doctype,self.name):
				if field["fieldtype"] != "Date" and field["fieldtype"] != "Table MultiSelect" and field["fieldtype"] != "Table" and field["fieldtype"] != "Geolocation" and field["fieldtype"] != "JSON" and field["fieldtype"] != "HTML" and field["fieldtype"] != "Button" and field["fieldtype"] != "Check":
					if field["fieldname"] not in ["workflow_state","work_state"]:
						repeated_list=["project_id", "project_name","project_description", "type_of_instrument", "objective","key_sector","implementing_entity","costusd", "end_date","key_sub_sector", "location", "other_agency", "source_of_funding", "financial_closure_date","included_in", "start_date"]
						if field["fieldname"] not in repeated_list:
							if old_doc.get(field["fieldname"]) != self.get(field["fieldname"]):
								field_list[field["fieldname"]] = str(old_doc.get(field["fieldname"]))


				elif field["fieldtype"] == "Table MultiSelect":
					if field["fieldname"] == "non_ghg_mitigation_benefits":
						if len(self.get(field["fieldname"])) != len(old_doc.get(field["fieldname"])):
							if self.get(field["fieldname"]) != old_doc.get(field["fieldname"]):
								old_list=frappe.db.get_all(field["options"],
										fields = ["non_ghg_mitigation_benefits"],
										filters = {"parent" : old_doc.name},pluck="non_ghg_mitigation_benefits")
								field_list[field["fieldname"]] = ",".join(old_list)

						if len(self.get(field["fieldname"])) == len(old_doc.get(field["fieldname"])):
							for i in self.get(field["fieldname"]):
								new_list1.append(i.non_ghg_mitigation_benefits)
							old_list=frappe.db.get_all(field["options"],
										fields = ["non_ghg_mitigation_benefits"],
										filters = {"parent" : old_doc.name},pluck="non_ghg_mitigation_benefits")
							old_list.sort()
							new_list1.sort()
							
							if old_list != new_list1:
								if self.get(field["fieldname"]) != old_doc.get(field["fieldname"]):
									field_list[field["fieldname"]] = ",".join(old_list)

					if field["fieldname"] == "target_ghgs":
						if len(self.get(field["fieldname"])) != len(old_doc.get(field["fieldname"])):
							if self.get(field["fieldname"]) != old_doc.get(field["fieldname"]):
								old_list=frappe.db.get_all(field["options"],
										fields = ["target_ghgs"],
										filters = {"parent" : old_doc.name},pluck="target_ghgs")
								field_list[field["fieldname"]] = ",".join(old_list)

						if len(self.get(field["fieldname"])) == len(old_doc.get(field["fieldname"])):
							for i in self.get(field["fieldname"]):
								new_list2.append(i.target_ghgs)
							old_list=frappe.db.get_all(field["options"],
										fields = ["target_ghgs"],
										filters = {"parent" : old_doc.name},pluck="target_ghgs")
							old_list.sort()
							new_list2.sort()
							
							if old_list != new_list2:
								if self.get(field["fieldname"]) != old_doc.get(field["fieldname"]):
									field_list[field["fieldname"]] = ",".join(old_list)

		return field_list
	
