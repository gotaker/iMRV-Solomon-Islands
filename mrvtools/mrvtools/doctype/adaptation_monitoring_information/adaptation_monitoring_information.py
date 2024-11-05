# Copyright (c) 2023, tridotstech and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document

class AdaptationMonitoringInformation(Document):
	
	

	@frappe.whitelist()
	def before_saving_table(self):
		old_doc =self.get_doc_before_save()
		if old_doc.quantitative_impact != self.quantitative_impact:
			self.edited_quantitative_impact = []
			for i in self.quantitative_impact:
				row = self.append('edited_quantitative_impact',{})
				row.category = i.category
				row.question = i.question
				row.expected_value = i.expected_value
				row.actual_value = i.actual_value
				row.data_source = i.data_source

			self.quantitative_impact = []
			for i in old_doc.quantitative_impact:
				row = self.append('quantitative_impact',{})
				row.category = i.category
				row.question = i.question
				row.expected_value = i.expected_value
				row.actual_value = i.actual_value
				row.data_source = i.data_source

			if len(self.actual_performance_indicator) == 0:	
				for i in old_doc.quantitative_impact:
					row = self.append('actual_performance_indicator',{})
					row.category = i.category
					row.question = i.question
					row.expected_value = i.expected_value
					row.actual_value = i.actual_value
					row.data_source = i.data_source
				
		return "Yess"


	@frappe.whitelist()
	def get_json(self):
		get_json_field=frappe.db.sql(f"""SELECT json from `tabAdaptation` WHERE name ='{self.project_id}'""")
		return get_json_field
	
	@frappe.whitelist()
	def get_user(self):
		doc = frappe.db.sql(f""" SELECT parent FROM `tabHas Role` WHERE role = 'Approver Adaptation Tracking'""")
		return doc
	
	@frappe.whitelist()
	def get_years(self,name):
		start_date = frappe.db.get_value("Adaptation",name,"start_date")
		if start_date:
			start_year = str(start_date).split("-")[0]
			return [str(year) for year in range(int(start_year), 2051)]
		else:
			return [str(year) for year in range(1990, 2051)]
		

	
