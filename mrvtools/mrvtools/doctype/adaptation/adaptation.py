
# Copyright (c) 2023, tridotstech and contributors
# For license information, please see license.txt

import frappe,json
from frappe.model.document import Document

class Adaptation(Document):

	@frappe.whitelist()
	def save_doc(self):
		self.save(ignore_permissions=True) 

	@frappe.whitelist()
	def getValues(self):
		docs = frappe.db.get_all("Master Data ChildTable",
			  fields = ["module","table","impact_area","indicator"], 
			  filters = {"module" : "Adaptation"})
		return docs
	
	@frappe.whitelist()
	def get_data(self):
		get_doc=frappe.db.sql(f"""SELECT included_in FROM `tabProject Included In ChildTable` WHERE parent ='{self.project_id}'""")
		return get_doc


	
	@frappe.whitelist()
	def categorylist(self):
		category_list = frappe.db.get_list('Adaptation Category', pluck='name')

		result_fields = []
		for category in reversed(category_list):
			result_fields.append(category)
		
		return result_fields
	

	@frappe.whitelist()
	def get_user(self):
		doc = frappe.db.sql(f""" SELECT parent FROM `tabHas Role` WHERE role = 'Approver Adaptation Tracking'""")
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
			if frappe.db.exists(self.doctype,self.name):
				if field["fieldtype"] != "Date" and field["fieldtype"] != "Table MultiSelect" and field["fieldtype"] != "Table" and field["fieldtype"] != "Geolocation" and field["fieldtype"] != "JSON" and field["fieldtype"] != "HTML" and field["fieldtype"] != "Button" and field["fieldtype"] != "Check" and field["fieldtype"] != " Editor":
					if field["fieldname"] not in ["workflow_state","work_state"]:
						if old_doc.get(field["fieldname"]) != self.get(field["fieldname"]):
							field_list[field["fieldname"]] = old_doc.get(field["fieldname"])

				elif field["fieldtype"] == "Date" and old_doc.get(field["fieldname"]) != None  and field["fieldtype"] != "Table" and field["fieldtype"] != "Table MultiSelect" and field["fieldtype"] != "JSON" and field["fieldtype"] != "HTML" and field["fieldtype"] != "Button" and field["fieldtype"] != "Check":
					Date = frappe.utils.formatdate(old_doc.get(field["fieldname"]),"yyyy-mm-dd")

					if Date != self.get(field["fieldname"] ):
						field_list[field["fieldname"]] = old_doc.get(field["fieldname"])

				elif field["fieldtype"] == "Table MultiSelect":
					if len(self.get(field["fieldname"])) != len(old_doc.get(field["fieldname"])):
						if self.get(field["fieldname"]) != old_doc.get(field["fieldname"]):
							old_list=frappe.db.get_all(field["options"],
									fields = ["ndp_coverage_tags"],
									filters = {"parent" : old_doc.name},pluck="ndp_coverage_tags")
							field_list[field["fieldname"]] = ",".join(old_list)

					if len(self.get(field["fieldname"])) == len(old_doc.get(field["fieldname"])):
						for i in self.get(field["fieldname"]):
							new_list.append(i.ndp_coverage_tags)
						old_list=frappe.db.get_all(field["options"],
									fields = ["ndp_coverage_tags"],
									filters = {"parent" : old_doc.name},pluck="ndp_coverage_tags")
						old_list.sort()
						new_list.sort()
						
						if old_list != new_list:
							if self.get(field["fieldname"]) != old_doc.get(field["fieldname"]):
								field_list[field["fieldname"]] = ",".join(old_list)

				elif field["fieldtype"] == "Geolocation":
					if old_doc.get(field["fieldname"]) != self.get(field["fieldname"]):
						field_list[field["fieldname"]] = old_doc.get(field["fieldname"])
		return field_list
		
	@frappe.whitelist()
	def get_jsons(self):
		old_doc = self.get_doc_before_save()
		field_list = []
		new_field_list = []
		meta = frappe.get_meta(self.doctype)
		meta_dict = meta.as_dict()
		fields = meta_dict["fields"]
		for field in fields:
			if field["fieldtype"] == "JSON":
				if self.get(field["fieldname"]) != old_doc.get(field["fieldname"]):
					meta_data1 = frappe.get_meta("Adaptation Qualitative ChildTable")
					meta_data_dict1 = meta_data1.as_dict()
					child_fields1 = meta_data_dict1["fields"]
					meta_data2 = frappe.get_meta("Adaptation Quantitative ChildTable")
					meta_data_dict2 = meta_data2.as_dict()
					child_fields2 = meta_data_dict2["fields"]
					data1 = json.loads(old_doc.get(field["fieldname"]))
					data2 = json.loads(self.get(field["fieldname"]))
					for key,value in data1.items():
						for i in range(0,len(data1[key])):
							if data1[key][i] != data2[key][i]:
								field_dict = {}
								new_field_dict = {}
								for item in child_fields1:
									field_dict[item["fieldname"]] = data1[key][i].get(item["fieldname"])
									new_field_dict[item["fieldname"]] = data2[key][i].get(item["fieldname"])
								for item in child_fields2:
									field_dict[item["fieldname"]] = data1[key][i].get(item["fieldname"])
									new_field_dict[item["fieldname"]] = data2[key][i].get(item["fieldname"])
								field_dict["type"]=key
								field_list.append(field_dict)
								new_field_dict["type"] = key
								new_field_list.append(new_field_dict)
		return [field_list,new_field_list]

	


	# @frappe.whitelist()
	# def get_child_fields(self):
	# 	field_name_list=[]
	# 	meta_data1 = frappe.get_meta("Adaptation Qualitative ChildTable")
	# 	meta_data_dict1 = meta_data1.as_dict()
	# 	child_fields1 = meta_data_dict1["fields"]
	# 	meta_data2 = frappe.get_meta("Adaptation Quantitative ChildTable")
	# 	meta_data_dict2 = meta_data2.as_dict()
	# 	child_fields2 = meta_data_dict2["fields"]
	# 	for field in child_fields1:
	# 		field_name_list.append(field["fieldname"])
	# 	for field in child_fields2:
	# 		field_name_list.append(field["fieldname"])
	# 	field_list=set(field_name_list)
	# 	return field_list

		# meta = frappe.get_meta("Adaptation Qualitative ChildTable")
		# meta_dict = meta.as_dict()
		# fields = meta_dict["fields"]
		# for field in fields:
		# 	for each_child_doc in self.qualitative_impact:
		# 		child_doc=frappe.get_doc("Adaptation Qualitative ChildTable",each_child_doc.name)
		# 		if child_doc.get(field["fieldname"]) != each_child_doc.get(field["fieldname"]):
		