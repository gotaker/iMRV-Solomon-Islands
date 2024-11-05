# Copyright (c) 2023, tridotstech and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document

# @frappe.whitelist(allow_guest=True)
# def get_user():
# 	doc = frappe.db.sql(f""" SELECT parent FROM `tabHas Role` WHERE role = 'Approver Climate Tracking'""")
# 	return doc

class ClimateFinance(Document):
	@frappe.whitelist()
	def get_user(self):
		doc = frappe.db.sql(f""" SELECT parent FROM `tabHas Role` WHERE role = 'Approver Climate Tracking'""")
		return doc
	
	@frappe.whitelist()
	def get_years(self):
		empty = ""
		if self.financial_closure_date:
			start_year = str(self.financial_closure_date).split("-")[0]
			return [str(year) for year in range(int(start_year), 2051)]
		else:
			return empty


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
				if field["fieldtype"] != "Date" and field["fieldtype"] != "Table MultiSelect" and field["fieldtype"] != "Table" and field["fieldtype"] != "JSON" and field["fieldtype"] != "HTML" and field["fieldtype"] != "Button" and field["fieldtype"] != "Check":
					if field["fieldname"] not in ["workflow_state","work_state"]:	
						if old_doc.get(field["fieldname"]) != self.get(field["fieldname"]):
							field_list[field["fieldname"]] = str(old_doc.get(field["fieldname"]))

				elif field["fieldtype"] == "Date" and ((old_doc.get(field["fieldname"]) == None and self.get(field["fieldname"]) != None) or (old_doc.get(field["fieldname"]) != None)):
					Date = frappe.utils.formatdate(old_doc.get(field["fieldname"]),"yyyy-mm-dd")
					if Date != self.get(field["fieldname"] ):
						field_list[field["fieldname"]] = old_doc.get(field["fieldname"])
		return field_list


	@frappe.whitelist()
	def before_saving_table1(self):
		old_doc =self.get_doc_before_save()

		self.edited_sources_of_finance = []
		for i in self.sources_of_finance:
			row = self.append('edited_sources_of_finance',{})
			row.type = i.type
			row.national_international = i.national_international
			row.amount = i.amount
			row.channels = i.channels
			row.agency_name = i.agency_name
			row.country = i.country

		self.sources_of_finance = []
		for i in old_doc.sources_of_finance:
			row = self.append('sources_of_finance',{})
			row.type = i.type
			row.national_international = i.national_international
			row.amount = i.amount
			row.channels = i.channels
			row.agency_name = i.agency_name
			row.country = i.country
		if len(self.actual_sources_of_finance) == 0:	
			for i in old_doc.sources_of_finance:
					row = self.append('actual_sources_of_finance',{})
					row.type = i.type
					row.national_international = i.national_international
					row.amount = i.amount
					row.channels = i.channels
					row.agency_name = i.agency_name
					row.country = i.country
			
#######################################################
	@frappe.whitelist()
	def before_saving_table2(self):
		old_doc =self.get_doc_before_save()
		self.edited_cost_breakdown = []
		for i in self.cost_breakdown:
			row = self.append('edited_cost_breakdown',{})
			row.disbursement_category = i.disbursement_category
			row.amount = i.amount
			row.percentage = i.percentage

		self.cost_breakdown = []
		for i in old_doc.cost_breakdown:
			row = self.append('cost_breakdown',{})
			row.disbursement_category = i.disbursement_category
			row.amount = i.amount
			row.percentage = i.percentage

		if len(self.actual_cost_breakdown) == 0:	
			for i in old_doc.cost_breakdown:
					row = self.append('actual_cost_breakdown',{})
					row.disbursement_category = i.disbursement_category
					row.amount = i.amount
					row.percentage = i.percentage

#######################################################
	@frappe.whitelist()
	def before_saving_table3(self):
		old_doc =self.get_doc_before_save()
		self.edited_budget_disbursement_schedule = []
		for i in self.budget_disbursement_schedule:
			row = self.append('edited_budget_disbursement_schedule',{})
			row.financial_year = i.financial_year
			row.amount = i.amount
			row.percentage = i.percentage

		self.budget_disbursement_schedule = []
		for i in old_doc.budget_disbursement_schedule:
			row = self.append('budget_disbursement_schedule',{})
			row.financial_year = i.financial_year
			row.amount = i.amount
			row.percentage = i.percentage

		if len(self.actual_budget_disbursement_schedule) == 0:	
			for i in old_doc.budget_disbursement_schedule:
					row = self.append('actual_budget_disbursement_schedule',{})
					row.financial_year = i.financial_year
					row.amount = i.amount
					row.percentage = i.percentage

		return "Yess"
	

	
