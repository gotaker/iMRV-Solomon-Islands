# Copyright (c) 2023, tridotstech and contributors
# For license information, please see license.txt

import frappe
from datetime import datetime
chartData =[]

def execute(filters=None):
	columns, data, chart = getColumns(),getData(filters), get_chart(filters)
	return columns, data , None, chart


def getColumns():
	columns = [
		{
			"fieldname": "project_id",
			"label": "Project ID",
			"fieldtype": 'Link',
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
			"fieldtype": 'Data',
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
	return columns

def getData(filters):
	conditions = ""
	if filters.get("monitoring_year"):
		conditions += f"AND YEAR(start_date) <= '{filters.get('monitoring_year')}'"
	if filters.get("key_sector"):
		conditions += f" AND key_sector like '{filters.get('key_sector')}'"
	if filters.get("key_sub_sector"):
		conditions += f" AND key_sub_sector like '{filters.get('key_sub_sector')}'"
	if filters.get("location"):
		conditions += f" AND location = '{filters.get('location')}'"
	if filters.get("ndc") == 'Yes':
		conditions += f" AND MT.included_in like '%NDC%' "
	if filters.get("ndc") == 'No':
		conditions += f" AND MT.included_in not like '%NDC%' "
	if filters.get("market_mechanism"):
		conditions += f" AND MT.market_based_mechanism = '{filters.get('market_mechanism')}'"
	

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
	global chartData 
	chartData = []

	for i in data:
		actualAnnualValue = frappe.db.get_value('Mitigation Monitoring Information',
				{'monitoring_year':f"{filters.get('monitoring_year')}","project_id":i.name},
				["actual_annual_ghg"], as_dict=1)
		startDate = frappe.db.get_value('Mitigation Monitoring Information',
				{"project_id":i.name},"YEAR('start_date') as start_date")
		tillDateActual = frappe.db.get_all('Mitigation Monitoring Information',
					filters={"project_id":f"{i.name}"},
					fields = "sum(actual_annual_ghg) as till_date_actual_ghg")
		i['actual_annual_ghg'] = actualAnnualValue.actual_annual_ghg if actualAnnualValue else 0
		if i.expected_annual_ghg == None or startDate == None:
			startDate = 0
			i['till_date_expected_ghg'] = int((i.expected_annual_ghg) * (datetime.now().year - (startDate)))
		else:
			i['till_date_expected_ghg'] = int((i.expected_annual_ghg) * (datetime.now().year - (startDate)))
		i['till_date_actual_ghg'] = tillDateActual[0].till_date_actual_ghg
		chartData.append(tillDateActual[0].till_date_actual_ghg)
		
	return data






def get_chart(filters):
	conditions = ""
	if filters.get("monitoring_year"):
		conditions += f"AND YEAR(start_date) <= '{filters.get('monitoring_year')}'"
	if filters.get("ndc") == 'Yes':
		conditions += f" AND included_in like '%NDC%' "
	if filters.get("ndc") == 'No':
		conditions += f" AND included_in not like '%NDC%' "
		
	project = frappe.db.sql(f"""
        SELECT project_name
        FROM `tabMitigations`
        WHERE docstatus != 2
        {conditions}
		ORDER BY project_id
    """, as_dict=True)

	project_names = [entry.project_name for entry in project]
	

	actual_annual_ghg = chartData
	chart = {
		"data": {
			"labels": project_names,
			"datasets": [
				{
					"name": "Actual Annual GHG",
					"values": actual_annual_ghg,
				},
			],
		},
		"type": "bar",
		"colors":['green'],
		"y_axis_label": 'GHG Reduction'
	}

	return chart
