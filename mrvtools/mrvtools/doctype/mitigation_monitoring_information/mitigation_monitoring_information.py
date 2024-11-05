# Copyright (c) 2023, tridotstech and contributors
# For license information, please see license.txt

import frappe,json
from frappe.model.document import Document
from frappe.model.utils import is_virtual_doctype
from frappe.model.base_document import get_controller
from frappe.desk.reportview import compress,execute
from frappe.model.utils.user_settings import save
class MitigationMonitoringInformation(Document):
	
# _____________________________________________________________________________________________________________________


	@frappe.whitelist()
	def before_saving_table(self):
		old_doc =self.get_doc_before_save()
		self.edited_performance_indicator = []
		for i in self.performance_indicator:
			row = self.append('edited_performance_indicator',{})
			row.performance_indicator = i.performance_indicator
			row.unit = i.unit
			row.expected_value = i.expected_value
			row.actual_monitored_value = i.actual_monitored_value
			row.reference = i.reference
		

		self.performance_indicator = []
		for i in old_doc.performance_indicator:
			row = self.append('performance_indicator',{})
			row.performance_indicator = i.performance_indicator
			row.unit = i.unit
			row.expected_value = i.expected_value
			row.actual_monitored_value = i.actual_monitored_value
			row.reference = i.reference

		if len(self.actual_performance_indicator) == 0:	
			for i in old_doc.performance_indicator:
				row = self.append('actual_performance_indicator',{})
				row.performance_indicator = i.performance_indicator
				row.unit = i.unit
				row.expected_value = i.expected_value
				row.actual_monitored_value = i.actual_monitored_value
				row.reference = i.reference
		return "Yess"


# _____________________________________________________________________________________________________________________




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
					repeated_list=["workflow_state","work_state","project_name","project_id", "monitoring_year", "project_description", "key_sector", "included_in", "type_of_instrument", "implementing_entity", "contact_details", "costusd", "end_date", "lifetime", "non_ghg_mitigation_benefits", "beneficiaries","market_based_mechanism", "expected_project_output", "objective", "key_sub_sector", "location", "other_agency", "other_contact_details", "source_of_funding", "financial_closure_date", "target_ghgs", "status", "gender_inclusiveness_assessment", "project_impacts", "weblink", "start_date"]
					if field["fieldname"] not in repeated_list:
						if old_doc.get(field["fieldname"]) != self.get(field["fieldname"]):
							field_list[field["fieldname"]] = str(old_doc.get(field["fieldname"]))
		return field_list
	


# _____________________________________________________________________________________________________________________




	# @frappe.whitelist()
	# def get_data(self):
	# 	get_doc=frappe.db.sql(f"""SELECT included_in FROM `tabProject Included In ChildTable` WHERE parent ='{self.project_name}'""")
	# 	return get_doc
	
	@frappe.whitelist()
	def get_value1(self):
		get_doc=frappe.db.sql(f"""SELECT MTC.non_ghg_mitigation_benefits FROM `tabMitigation Non GHG in  ChildTable` MTC INNER JOIN `tabMitigations` MT on MT.name = MTC.parent WHERE MT.name ='{self.project_id}'""")
		return get_doc
	
	@frappe.whitelist()
	def get_value2(self):
		get_doc=frappe.db.sql(f"""SELECT target_ghgs FROM `tabMitigation Target GHGs in  ChildTable` MTC INNER JOIN `tabMitigations` MT on MT.name = MTC.parent WHERE MT.name ='{self.project_id}'""")
		return get_doc
	
	
	
	@frappe.whitelist()
	def get_child(self):
		get_column=frappe.db.sql(f"""SELECT * FROM `tabMitigation Performance Indicator ChildTable` MPIC INNER JOIN `tabMitigations` MT on MT.name = MPIC.parent WHERE MT.name ='{self.project_id}'""",as_dict=1)
		return get_column
	
	@frappe.whitelist()
	def get_user(self):
		doc = frappe.db.sql(f""" SELECT parent FROM `tabHas Role` WHERE role = 'Approver Mitigation Tracking'""")
		return doc
	
	@frappe.whitelist()
	def get_years(self,name):
		start_date = frappe.db.get_value("Mitigations",name,"start_date")
		if start_date:
			start_year = str(start_date).split("-")[0]
			return [str(year) for year in range(int(start_year), 2051)]
		else:
			return [str(year) for year in range(1990, 2051)]


@frappe.whitelist()
def get(args):
	args = json.loads(args)
	args = frappe._dict(args)
	frappe.log_error("ARS",args.doctype)
	if is_virtual_doctype(args.doctype):
		controller = get_controller(args.doctype)
		data = compress(controller.get_list(args))
	else:
		data = compress(execute(**args), args=args)
	return data

@frappe.whitelist()
def save_settings(doctype, user_settings):
	return save(doctype,user_settings)