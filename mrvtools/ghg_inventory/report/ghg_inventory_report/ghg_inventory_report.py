# Copyright (c) 2023, tridotstech and contributors
# For license information, please see license.txt

import frappe


def execute(filters=None):
	columns, data, chart = getColumns(),getData(filters), get_chart(filters)
	return columns, data , None, chart


def getColumns():
	columns = [
		{
			"fieldname": "categories",
			"label": "Categories",
			"fieldtype": 'Small Text',
			"width": "500"
		},
		{
			"fieldname": "co2",
			"label": "CO2 Emission",
			"fieldtype": 'Float',
		},
		{
			"fieldname": "ch4",
			"label": "CH4 Emission",
			"fieldtype": 'Float',
		},
		{
			"fieldname": "n2o",
			"label": "N2O Emission",
			"fieldtype": 'Float',
		},
		{
			"fieldname": "total_co2_eq",
			"label": "Total CO2 Emission",
			"fieldtype": 'Float',
		}
		
	]
	return columns

def getData(filters):
	conditions = ""
	if filters.get("inventory_year"):
		conditions += f"AND parent = '{filters.get('inventory_year')}'"

		if not filters.get("inventory_unit") or filters.get("inventory_unit") == 'tCO2e':	
			query = f"""
					SELECT
						categories, 
						co2,
						ch4,
						n2o, 
						total_co2_eq
					FROM
						`tabGHG Inventory Master Report ChildTable`
					WHERE 
						docstatus != 2 
						{conditions}
					ORDER BY
						idx
					"""
			data = frappe.db.sql(query,as_dict =1)

			return data
		
		if filters.get("inventory_unit") == 'GgCO2e':
			query = f"""
					SELECT
						categories, 
						co2 * 1000 as co2,
						ch4 * 1000 as ch4,
						n2o * 1000 as n2o, 
						total_co2_eq * 1000 as total_co2_eq
					FROM
						`tabGHG Inventory Master Report ChildTable`
					WHERE 
						docstatus != 2 
						{conditions}
					ORDER BY
						idx
					"""
			data = frappe.db.sql(query,as_dict =1)

			return data

def get_chart(filters):
	conditions = ""
	if filters.get("inventory_year"):
		conditions += f"AND parent = '{filters.get('inventory_year')}'"
	if not filters.get("inventory_unit") or filters.get("inventory_unit") == 'tCO2e':
		query = f"""
				SELECT
					co2,
					ch4,
					n2o
				FROM
					`tabGHG Inventory Master Report ChildTable`
				WHERE 
					docstatus != 2
				AND
					categories = 'Total National Emissions and Removals'
					{conditions}
				"""
		
		data = frappe.db.sql(query)
		if data != ():
			chart = {
				"data": {
					"labels": ["CO2","CH4","N2O"],
					"datasets": [
						{
							'name': 'No. of Projects',
							"values": data[0],
						},
					],
				},
				"type": "bar",
				"colors":["blue","red"],
				"y_axis_label": 'GHG Reduction'
			}
			return chart
	if filters.get("inventory_unit") == 'GgCO2e':
		query = f"""
				SELECT
					co2 * 1000 as co2,
					ch4 * 1000 as ch4,
					n2o * 1000 as n2o
				FROM
					`tabGHG Inventory Master Report ChildTable`
				WHERE 
					docstatus != 2
				AND
					categories = 'Total National Emissions and Removals'
					{conditions}
				"""
		
		data = frappe.db.sql(query)
		chart = {
			"data": {
				"labels": ["CO2","CH4","N2O"],
				"datasets": [
					{
						'name': 'No. of Projects',
						"values": data[0],
					},
				],
			},
			"type": "bar",
			"colors":["blue","red"],
			"y_axis_label": 'GHG Reduction'
		}
		return chart
# project_names = [entry.project_name for entry in project]


# actual_annual_ghg = chartData
