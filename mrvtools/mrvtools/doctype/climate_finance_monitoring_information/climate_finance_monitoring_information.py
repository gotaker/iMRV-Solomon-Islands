# Copyright (c) 2023, tridotstech and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document

class ClimateFinanceMonitoringInformation(Document):
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
	def get_rows(self):
		doc = frappe.db.sql(f""" SELECT CFCT.parent, CFCT.creation as creation, CFMI.name,CFMI.project_id, CFCT.financial_year, CFCT.q1,  CFCT.q2,  CFCT.q3,  CFCT.q4,  CFCT.total_disbursement_usd FROM `tabClimate Finance Total Budget Disbursement ChildTable` CFCT inner join `tabClimate Finance Monitoring Information` CFMI on CFCT.parent= CFMI.name where CFMI.project_id='{self.project_id}' and CFCT.parent = (select CFCT.parent from `tabClimate Finance Total Budget Disbursement ChildTable` CFCT  inner join `tabClimate Finance Monitoring Information` CFMI on CFCT.parent = CFMI.name where CFMI.project_id = '{self.project_id}' order by CFMI.creation DESC limit 1) group by CFCT.financial_year ASC""",as_dict=1)
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
				if field["fieldtype"] != "Date" and field["fieldtype"] != "Table MultiSelect" and field["fieldtype"] != "Table" and field["fieldtype"] != "JSON" and field["fieldtype"] != "HTML" and field["fieldtype"] != "Button" and field["fieldtype"] != "Check":
					if field["fieldname"] not in ["workflow_state","work_state","applied_exchange_rate","financing_mode","financial_closure_date","financial_year"]:
						if old_doc.get(field["fieldname"]) != self.get(field["fieldname"]):
							field_list[field["fieldname"]] = str(old_doc.get(field["fieldname"]))

				elif field["fieldtype"] == "Date":
					Date = frappe.utils.formatdate(old_doc.get(field["fieldname"]),"yyyy-mm-dd")
					if Date != self.get(field["fieldname"] ):
						field_list[field["fieldname"]] = old_doc.get(field["fieldname"])
		return field_list


	@frappe.whitelist()
	def before_saving_table(self):
		old_doc =self.get_doc_before_save()

		self.edited_budget_expenditure = []
		for i in self.budget_expenditure:
			row = self.append('edited_budget_expenditure',{})
			row.disbursement_category = i.disbursement_category
			row.q1 = i.q1
			row.q2 = i.q2
			row.q3 = i.q3
			row.q4 = i.q4
			row.total = i.total

		self.budget_expenditure = []
		for i in old_doc.budget_expenditure:
			row = self.append('budget_expenditure',{})
			row.disbursement_category = i.disbursement_category
			row.q1 = i.q1
			row.q2 = i.q2
			row.q3 = i.q3
			row.q4 = i.q4
			row.total = i.total
		if len(self.actual_budget_expenditure) == 0:	
			for i in old_doc.budget_expenditure:
					row = self.append('actual_budget_expenditure',{})
					row.disbursement_category = i.disbursement_category
					row.q1 = i.q1
					row.q2 = i.q2
					row.q3 = i.q3
					row.q4 = i.q4
					row.total = i.total

		self.edited_total_budget_disbursement = []
		for i in self.total_budget_disbursement:
			row = self.append('edited_total_budget_disbursement',{})
			row.financial_year = i.financial_year
			row.q1 = i.q1
			row.q2 = i.q2
			row.q3 = i.q3
			row.q4 = i.q4
			row.total_disbursement_usd = i.total_disbursement_usd

		self.total_budget_disbursement = []
		for i in old_doc.total_budget_disbursement:
			row = self.append('total_budget_disbursement',{})
			row.financial_year = i.financial_year
			row.q1 = i.q1
			row.q2 = i.q2
			row.q3 = i.q3
			row.q4 = i.q4
			row.total_disbursement_usd = i.total_disbursement_usd

		if len(self.actual_total_budget_disbursement) == 0:	
			for i in old_doc.total_budget_disbursement:
					row = self.append('actual_total_budget_disbursement',{})
					row.financial_year = i.financial_year
					row.q1 = i.q1
					row.q2 = i.q2
					row.q3 = i.q3
					row.q4 = i.q4
					row.total_disbursement_usd = i.total_disbursement_usd

		return "Yess"
		

	
