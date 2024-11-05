# Copyright (c) 2023, tridotstech and contributors
# For license information, please see license.txt

import frappe,json
from datetime import datetime
import pandas as pd

from frappe.utils import get_site_base_path,now
till_sum_actual_annual_ghg =0
till_sum_expected_annual_ghg = 0
sum_actual_annual_ghg = 0
sum_expected_annual_ghg = 0


@frappe.whitelist()
def execute(monitoring_year = None,key_sector = None,key_sub_sector = None,location = None,ndc = None,market_mechanism = None):
	columns, data = getColumns(),getData(monitoring_year,key_sector,key_sub_sector,location,ndc,market_mechanism)
	return columns, data[0]


def getColumns():
	columns = [
		{
			"fieldname": "action",
			"label": "Action",
			"fieldtype": 'Data',
		},
		{
			"fieldname": "programme",
			"label": "Programme",
			"fieldtype": 'Data',
		},
		{
			"fieldname": "project_id",
			"label": "Project ID",
			"fieldtype": 'Data',
		},
		{
			"fieldname": "project_name",
			"label": "Project Name",
			"fieldtype": 'Data',
		},
		{
			"fieldname": "objective",
			"label": "Objective",
			"fieldtype": 'Data',
		},
		{
			"fieldname": "key_sector",
			"label": "Key Sector",
			"fieldtype": 'Data',
		},
		{
			"fieldname": "key_sub_sector",
			"label": "Key Sub-Sector",
			"fieldtype": 'Data',
		},
		{
			"fieldname": "costusd",
			"label": "Cost (USD)",
			"fieldtype": 'Int',
		},
		{
			"fieldname": "location",
			"label": "Location",
			"fieldtype": 'Data',
		},
		{
			"fieldname": "start_date",
			"label": "Start Date",
			"fieldtype": 'Date',
		},
		{
			"fieldname": "lifetime",
			"label": "Lifetime",
			"fieldtype": 'Data',
		},
		{
			"fieldname": "included_in",
			"label": "Included In",
			"fieldtype": 'Data'
		},
		{
			"fieldname": "implementing_entity",
			"label": "Implementing Entity",
			"fieldtype": 'Data',
		},
		{
			"fieldname": "other_agency",
			"label": "Other Agency",
			"fieldtype": 'Data',
		},
		{
			"fieldname": "status",
			"label": "Status",
			"fieldtype": 'Data',
		},
		{
			"fieldname": "expected_annual_ghg",
			"label": "Expected Annual GHG",
			"fieldtype": 'Float',
		},
		{
			"fieldname": "actual_annual_ghg",
			"label": "Actual Annual GHG",
			"fieldtype": 'Float',
		},
		{
			"fieldname": "till_date_expected_ghg",
			"label": "Till Date Expected GHG",
			"fieldtype": 'Float',
		},
		{
			"fieldname": "till_date_actual_ghg",
			"label": "Till Date Actual GHG",
			"fieldtype": 'Float',
		}
	]
	keys = [item['label'] for item in columns]
	return keys
@frappe.whitelist(allow_guest=True)
def getData(monitoring_year = None,key_sector = None,key_sub_sector = None,location = None,ndc = None,market_mechanism = None):
	conditions = ""
	if monitoring_year:
		conditions += f" AND YEAR(P.start_date) <= '{monitoring_year}'"
		
	if key_sector:
		conditions += f" AND P.key_sector like '{key_sector}'"
	if key_sub_sector:
		conditions += f" AND P.key_sub_sector like '{key_sub_sector}'"
	if location:
		conditions += f" AND P.location = '{location}'"
	if ndc == 'Yes':
		conditions += f" AND MT.included_in like '%NDC%' "
	if ndc == 'No':
		conditions += f" AND MT.included_in not like '%NDC%' "
	if market_mechanism:
		conditions += f" AND MT.market_based_mechanism = '{market_mechanism}'"
	
	

	query = f"""
			SELECT
				MT.name,
				CONCAT(P.action,' | ',P.action_name) as action,
				CONCAT(P.programme,' | ',P.programme_name) as programme,
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
			INNER JOIN 
				`tabProject` P
			ON
				P.name = MT.project_id
			WHERE 
				MT.docstatus != 2 
				{conditions}
			ORDER BY
				MT.project_id
				"""
	data = frappe.db.sql(query,as_dict =1)
	# global till_sum_actual_annual_ghg
	# global till_sum_expected_annual_ghg
	# global sum_actual_annual_ghg
	# global sum_expected_annual_ghg
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
	chart_data = get_chart(monitoring_year,sum_expected_annual_ghg,till_sum_expected_annual_ghg,sum_actual_annual_ghg,till_sum_actual_annual_ghg)
	values_only = [list({k: v for k, v in item.items() if k != 'name'}.values()) for item in data]
	return [values_only,chart_data]





@frappe.whitelist(allow_guest=True)
def get_chart(monitoring_year,sum_expected_annual_ghg,till_sum_expected_annual_ghg,sum_actual_annual_ghg,till_sum_actual_annual_ghg):
	
	if monitoring_year:	
		labels = [monitoring_year,"Till Date"]
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
def get_pie_chart(monitoring_year = None,key_sector = None,key_sub_sector = None,location = None,ndc = None,market_mechanism = None):
	conditions = ""
	if monitoring_year:
		conditions += f"AND YEAR(MT.start_date) <= '{monitoring_year}'"
	if key_sector:
		conditions += f" AND MT.key_sector like '{key_sector}'"
	if key_sub_sector:
		conditions += f" AND MT.key_sub_sector like '{key_sub_sector}'"
	if location:
		conditions += f" AND Mt.location = '{location}'"
	if ndc == 'Yes':
		conditions += f" AND MT.included_in like '%NDC%' "
	if ndc == 'No':
		conditions += f" AND MT.included_in not like '%NDC%' "
	if market_mechanism:
		conditions += f" AND MT.market_based_mechanism = '{market_mechanism}'"
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
	# new_data_list = [[item['categories'], item['CO2 Emission'], item['CH4 Emission'], item['N2O Emission']] for item in data_list]
	# new_column_list = [[item['id']] for item in column_list]

	data_dict = data_dict = {column_list[i]: [row[i] for row in data_list] for i in range(len(column_list))}
	export_data = pd.DataFrame(data_dict)

	site_name = get_site_base_path()
	nowTime = now()[:-7]
	nowTime = nowTime.replace(" ","")
	nowTime = nowTime.replace("-","")
	nowTime = nowTime.replace(":","")
	export_data.to_excel(f"{site_name}/public/files/Mitigation-Report-{nowTime}.xlsx")
	return f"../files/Mitigation-Report-{nowTime}.xlsx"