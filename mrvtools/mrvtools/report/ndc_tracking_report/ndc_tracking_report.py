# Copyright (c) 2023, tridotstech and contributors
# For license information, please see license.txt

import frappe
import datetime

financial_closure_date = []
def execute(filters=None):
	col, data = getColumns(filters),getData(filters)
	return col, data

def getColumns(filters):
	col = []
	col.append("Project ID" + ":Link/Project")
	col.append("Project Name" + ":Data")
	col.append("GHG Reductions Expected"+":Data")
	# financial_closure_date = frappe.db.get_all('Mitigation Monitoring Information',
	# 			fields = 'monitoring_year',
	# 			group_by = 'monitoring_year',
	# 			order_by = 'financial_closure_date asc')

	# for i in financial_closure_date:
	# 	col.append(f"{i.financial_closure_date[0:4]}" + ":Data")
	if filters.get("year"):
		val = frappe.db.get_all('Mitigation Monitoring Information',
					fields = 'monitoring_year',
					filters = {"included_in":["like","%NDC%"],"monitoring_year":["<=",filters.get('year')]},
					group_by = 'monitoring_year',
					order_by = 'monitoring_year',
					pluck='monitoring_year')
		for i in val:
			col.append(f'{i}'+":Data")
		return col

def getData(filters):
	conditions = ""
	# if filters.get("year"):
	# 	conditions += f" AND  YEAR(MT.monitoring_year) <= '{filters.get('year')}'"
	# if filters.get("year") =="":
	# 	conditions += f"AND MT.monitoring_year <= '{frappe.utils.today()}'"
	if filters.get("key_sector"):
		conditions += f" AND MT.key_sector like '{filters.get('key_sector')}'"
	if filters.get("key_sub_sector"):
		conditions += f" AND MT.key_sub_sector like '{filters.get('key_sub_sector')}'"
	if filters.get("year"):
		query = f"""
				SELECT
					MT.project_id,
					MT.project_name,
					MT.expected_annual_ghg as ghg_reductions_expected,

					MT.name
				FROM
					`tabMitigations` MT
				WHERE 
					MT.docstatus != 2 
				AND
					MT.included_in  like '%NDC%'
				{conditions}
		"""

		data = frappe.db.sql(query,as_dict=1)
		# actualValues = frappe.db.get_all('Mitigation Monitoring Information',
		# 			  fields = ['project_name1','monitoring_year','actual_annual_ghg'],
		# 			  filters = {"included_in":["like","%NDC%"]},
		# 			  order_by = "project_name1")
		monitoringMitigationList = frappe.db.get_all('Mitigation Monitoring Information',
					fields = 'monitoring_year',
					filters = {"included_in":["like","%NDC%"],"monitoring_year":["<=",filters.get('year')]},
					group_by = 'monitoring_year',
					order_by = 'monitoring_year',
					pluck='monitoring_year')
		
		for each in data:
			for i in monitoringMitigationList:
				curVal = frappe.db.get_value('Mitigation Monitoring Information',
					{"project_id":each.name,"monitoring_year":i},
					['actual_annual_ghg'])
				each[f'{i}'] = curVal if curVal else 0
		# for each in result:
		# 	for i in monitoringYears:
		# 		query = f"""
		# 			SELECT
		# 				MTMI.actual_annual_ghg
		# 			FROM
		# 				`tabMitigations` MT
		# 			INNER JOIN
		# 				`tabMitigation Monitoring Information` as MTMI
		# 			ON
		# 				MT.name = MTMI.project_name
		# 			WHERE 
		# 				MT.docstatus != 2 
		# 			{conditions}
		# 		"""
		# 		value = frappe.db.sql(query,as_dict =1)

				

		# 		each[f'{i.monitoring_year}'] = value[0].actual_monitored_value if value and value[0].actual_monitored_value else 0
		# output.extend(result)
		return data


