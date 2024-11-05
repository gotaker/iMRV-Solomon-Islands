import frappe,json
from datetime import datetime
import pandas as pd

from frappe.utils import get_site_base_path,now
till_sum_actual_annual_ghg =0
till_sum_expected_annual_ghg = 0
sum_actual_annual_ghg = 0
sum_expected_annual_ghg = 0

financial_closure_date = []
@frappe.whitelist()
def execute(year = None):
	col, data = getColumns(year),getData(year)

	return col, data


def getColumns(year):
	col = []
	col.append("Project ID" + ":Link/Project")
	col.append("Project Name" + ":Data")
	col.append("GHG Reductions Expected"+":Data")

	if year:
		val = frappe.db.get_all('Mitigation Monitoring Information',
					fields = 'monitoring_year',
					filters = {"included_in":["like","%NDC%"],"monitoring_year":["<=",year]},
					group_by = 'monitoring_year',
					order_by = 'monitoring_year',
					pluck='monitoring_year')
		for i in val:
			col.append(f'{i}'+":Data")
		keys_only = [item.split(':')[0] for item in col]
		return keys_only

def getData(year = None):
	conditions = ""
	if year:
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
		
		monitoringMitigationList = frappe.db.get_all('Mitigation Monitoring Information',
					fields = 'monitoring_year',
					filters = {"included_in":["like","%NDC%"],"monitoring_year":["<=",year]},
					group_by = 'monitoring_year',
					order_by = 'monitoring_year',
					pluck='monitoring_year')
		
		for each in data:
			for i in monitoringMitigationList:
				curVal = frappe.db.get_value('Mitigation Monitoring Information',
					{"project_id":each.name,"monitoring_year":i},
					['actual_annual_ghg'])
				each[f'{i}'] = curVal if curVal else 0
		values_only = [list({k: v for k, v in item.items() if k != 'name'}.values()) for item in data]
		return values_only

@frappe.whitelist()
def get_chart(year = None):
	conditions = ""
	if year:
		conditions += f"AND YEAR(start_date) <= '{year}'"
	if year:

		query = f"""
				SELECT
					MT.name,
					MT.project_id,
					MT.project_name, 
					MT.objective, 
					MT.key_sector, 
					MT.key_sub_sector,
					MT.costusd,
					MT.location, 
					MT.start_date, 
					MT.lifetime,
					CASE WHEN MT.included_in like "%NDC%" THEN "Yes" ELSE "No" END AS included_in,
					MT.implementing_entity, 
					MT.other_agency, 
					MT.status, 
					MT.expected_annual_ghg
				FROM
					`tabMitigations` MT
				WHERE 
					MT.docstatus != 2 
					{conditions}
				ORDER BY
					MT.project_id
					"""
		data = frappe.db.sql(query,as_dict =1)
		global till_sum_actual_annual_ghg
		global till_sum_expected_annual_ghg
		global sum_actual_annual_ghg
		global sum_expected_annual_ghg
		till_sum_actual_annual_ghg = 0
		till_sum_expected_annual_ghg = 0
		sum_actual_annual_ghg = 0
		sum_expected_annual_ghg = 0

		for i in data:
			actualAnnualValue = frappe.db.get_value('Mitigation Monitoring Information',
					{"project_id":i.name},
					["actual_annual_ghg"], as_dict=1)
			startDate = frappe.db.get_value('Mitigation Monitoring Information',
					{"project_id":i.name},"YEAR('start_date') as start_date")
			tillDateActual = frappe.db.get_all('Mitigation Monitoring Information',
						filters={"project_id":f"{i.name}"},
						fields = "sum(actual_annual_ghg) as till_date_actual_ghg")
			i['actual_annual_ghg'] = actualAnnualValue.actual_annual_ghg if actualAnnualValue else 0
			if actualAnnualValue:
				sum_actual_annual_ghg += actualAnnualValue.actual_annual_ghg 
			else:
				sum_actual_annual_ghg += 0
			sum_expected_annual_ghg += i.expected_annual_ghg
			if i.expected_annual_ghg == None or startDate == None:
				startDate = 0
				i['till_date_expected_ghg'] = int((i.expected_annual_ghg) * (datetime.now().year - (startDate)))
				till_sum_expected_annual_ghg += int((i.expected_annual_ghg) * (datetime.now().year - (startDate)))
			else:
				i['till_date_expected_ghg'] = int((i.expected_annual_ghg) * (datetime.now().year - (startDate)))
				till_sum_expected_annual_ghg += int((i.expected_annual_ghg) * (datetime.now().year - (startDate)))

			if tillDateActual[0].till_date_actual_ghg is not None:
				i['till_date_actual_ghg'] = tillDateActual[0].till_date_actual_ghg
				till_sum_actual_annual_ghg += tillDateActual[0].till_date_actual_ghg
			else:
				till_sum_actual_annual_ghg += 0
				i['till_date_actual_ghg'] = 0
		values_only = [list({k: v for k, v in item.items() if k != 'name'}.values()) for item in data]




		if year:	
			labels = [year,"Till Date"]
			return {"datasets": [
				{
					"name": "Expected Annual GHG", "chartType": "bar",
					"values": [sum_expected_annual_ghg,till_sum_expected_annual_ghg]
				},
				{
					"name": "Actual Annual GHG", "chartType": "bar",
					"values": [sum_actual_annual_ghg,till_sum_actual_annual_ghg]
				}
			],"labels":labels}
		else:
			labels = ["Till Date"]
			return {"datasets": [
				{
					"name": "Expected Annual GHG", "chartType": "bar",
					"values": [till_sum_expected_annual_ghg]
				},
				{
					"name": "Actual Annual GHG", "chartType": "bar",
					"values": [till_sum_actual_annual_ghg]
				}
			],"labels":labels}

@frappe.whitelist()
def get_pie_chart(year = None):
	conditions = ""
	if year:
		conditions += f"AND YEAR(MT.start_date) <= '{year}'"
	
	if year:
		query = f"""
		SELECT
			MT.key_sector
		FROM
			`tabMitigations` MT
		WHERE 
			MT.docstatus != 2 
			{conditions}
		ORDER BY
			MT.project_id
			"""
		data = frappe.db.sql(query,as_dict=1)
		result = list(dict((json.dumps(d, sort_keys=True), d) for d in data).values())
		sector_label_list=[]
		actual_reduction_list=[]
		for i in result:
			tillDateActual = frappe.db.get_all('Mitigation Monitoring Information',
				filters={"key_sector":f"{i.key_sector}"},
				fields = ["sum(actual_annual_ghg) as till_date_actual_ghg"])
			actual_reduction_list.append(tillDateActual[0].till_date_actual_ghg)
			sector_label_list.append(i.key_sector)
	
		return {"data":actual_reduction_list,"labels":sector_label_list}
	


@frappe.whitelist()
def download_excel(columns,data):

	data_list = json.loads(data)
	column_list = json.loads(columns)
	data_dict = {column_list[i]: [row[i] for row in data_list] for i in range(len(column_list))}
	export_data = pd.DataFrame(data_dict)

	site_name = get_site_base_path()
	nowTime = now()[:-7]
	nowTime = nowTime.replace(" ","")
	nowTime = nowTime.replace("-","")
	nowTime = nowTime.replace(":","")
	export_data.to_excel(f"{site_name}/public/files/NDC-Report-{nowTime}.xlsx")
	return f"../files/NDC-Report-{nowTime}.xlsx"


