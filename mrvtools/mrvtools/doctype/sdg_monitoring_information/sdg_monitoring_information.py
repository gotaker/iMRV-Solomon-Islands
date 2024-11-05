# Copyright (c) 2023, tridotstech and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document

class SDGMonitoringInformation(Document):

	

	@frappe.whitelist()
	def before_saving_table(self):
		old_doc =self.get_doc_before_save()
		if old_doc.quantitative_impact != self.quantitative_impact:
			self.edited_quantitative_impact = []
			for i in self.quantitative_impact:
				row = self.append('edited_quantitative_impact',{})
				row.category = i.category
				row.question = i.question
				row.sdg_mapping = i.sdg_mapping
				row.data = i.data
				row.data_source = i.data_source
				frappe.log_error(" Before Edited",self.edited_quantitative_impact)

			self.quantitative_impact = []
			for i in old_doc.quantitative_impact:
				row = self.append('quantitative_impact',{})
				row.category = i.category
				row.question = i.question
				row.sdg_mapping = i.sdg_mapping
				row.data = i.data
				row.data_source = i.data_source
				# frappe.log_error("Before Self",self.performance_indicator)

			if len(self.actual_quantitative_impact) == 0:	
				for i in old_doc.quantitative_impact:
					row = self.append('actual_quantitative_impact',{})
					row.category = i.category
					row.question = i.question
					row.sdg_mapping = i.sdg_mapping
					row.data = i.data
					row.data_source = i.data_source
		return "Yess"

	@frappe.whitelist()
	def get_json(self):
		get_json_field=frappe.db.sql(f"""SELECT json from `tabSDG Assessment` WHERE name ='{self.project_id}'""")
		return get_json_field
		
	@frappe.whitelist()
	def get_user(self):
		doc = frappe.db.sql(f""" SELECT parent FROM `tabHas Role` WHERE role = 'Approver SDG Tracking'""")
		return doc
	
	@frappe.whitelist()
	def get_years(self,name):
		start_date = frappe.db.get_value("SDG Assessment",name,"start_date")
		if start_date:
			start_year = str(start_date).split("-")[0]
			return [str(year) for year in range(int(start_year), 2051)]
		else:
			return [str(year) for year in range(1990, 2051)]

