# Copyright (c) 2023, tridotstech and contributors
# For license information, please see license.txt

import frappe

def execute(filters=None):
	columns, data, chart = getColumns(filters),getData(filters), get_chart(filters)
	return columns, data , None, chart


def getColumns(filters):
	columns = []
	columns.append("Categories" + ":Data:500")

	val = f"""
			SELECT 
				name 
			FROM 
				`tabGHG Inventory Master Report` 
			WHERE 
				name >= '{filters.get("from_year")}' 
			AND 
				name <= '{filters.get("to_year")}' 
			ORDER BY 
				year ASC;

		"""
	data = frappe.db.sql(val,as_dict =1)
	for i in data:
		columns.append(f'{i.name}'+":Float:160")
	return columns

def getData(filters):
	global chart_label
	global co2_value
	global ch4_value
	global n2o_value
	chart_label = []
	co2_value = []
	ch4_value = []
	n2o_value = []
	if not filters.get("inventory_unit") or filters.get("inventory_unit") == 'tCO2e':
		if(filters.get('from_year')):
			query = f"""
					Select
						category_name as categories
					from
						`tabGHG Inventory Report Categories`
					order by
						display_order asc
					"""
			data = frappe.db.sql(query,as_dict =1)
			
			val = f"""
					SELECT 
						name 
					FROM 
						`tabGHG Inventory Master Report` 
					WHERE 
						name >= '{filters.get("from_year")}' 
					AND 
						name <= '{filters.get("to_year")}' 
					ORDER BY 
						year ASC;

				"""
			value = frappe.db.sql(val,as_dict = 1)

			for i in value:
				chart_label.append(i.name)

			for each in data:
				for i in value:
					get_total_co2 = f"""
									SELECT 
										total_co2_eq,parent
									FROM 
										`tabGHG Inventory Master Report ChildTable` 
									WHERE 
										parent = '{i.name}' 
									AND
										categories = '{each.categories}'
									ORDER BY 
										idx
								"""
					
					total_co2 = frappe.db.sql(get_total_co2,as_dict =1)
					each[f'{i.name}'] = total_co2[0].total_co2_eq if total_co2 and total_co2[0].total_co2_eq else 0
					if each.categories == 'Total National Emissions and Removals':

						chart_value = f"""
								SELECT 
											co2,ch4,n2o
										FROM 
											`tabGHG Inventory Master Report ChildTable` 
										WHERE 
											parent = '{i.name}' 
										AND
											categories = 'Total National Emissions and Removals'
							"""
						chart_data = frappe.db.sql(chart_value,as_dict =1)
						co2_value.append(chart_data[0].co2)
						ch4_value.append(chart_data[0].ch4)
						n2o_value.append(chart_data[0].n2o)

			return data

	if filters.get("inventory_unit") == 'GgCO2e':
		query = f"""
				Select
					category_name as categories
				from
					`tabGHG Inventory Report Categories`
				order by
					display_order asc
				"""
		data = frappe.db.sql(query,as_dict =1)
		val = f"""
				SELECT 
					name 
				FROM 
					`tabGHG Inventory Master Report` 
				WHERE 
					name >= '{filters.get("from_year")}' 
				AND 
					name <= '{filters.get("to_year")}' 
				ORDER BY 
					year ASC;

			"""
		value = frappe.db.sql(val,as_dict = 1)
		for i in value:
			chart_label.append(i.name)
		for each in data:
			for i in value:
				get_total_co2 = f"""
								SELECT 
									total_co2_eq * 1000 as total_co2_eq,
									parent
								FROM 
									`tabGHG Inventory Master Report ChildTable` 
								WHERE 
									parent = '{i.name}' 
								AND
									categories = '{each.categories}'
								ORDER BY 
									idx
							"""
				
				total_co2 = frappe.db.sql(get_total_co2,as_dict =1)
				each[f'{i.name}'] = total_co2[0].total_co2_eq if total_co2 and total_co2[0].total_co2_eq else 0

				chart_value = f"""
						SELECT 
									co2 * 1000 as co2,
									ch4 * 1000 as ch4,
									n2o * 1000 as n2o
								FROM 
									`tabGHG Inventory Master Report ChildTable` 
								WHERE 
									parent = '{i.name}' 
								AND
									categories = 'Total National Emissions and Removals'
					"""
				chart_data = frappe.db.sql(chart_value,as_dict =1)
				co2_value.append(chart_data[0].co2)
				ch4_value.append(chart_data[0].ch4)
				n2o_value.append(chart_data[0].n2o)
		
		return data
def get_chart(filters):
	
	val = f"""
			SELECT 
				name 
			FROM 
				`tabGHG Inventory Master Report` 
			WHERE 
				name >= '{filters.get("from_year")}' 
			AND 
				name <= '{filters.get("to_year")}' 
			ORDER BY 
				year ASC;

		"""
	value = frappe.db.sql(val,as_dict = 1)

	

	chart = {
		"data": {
			"labels": chart_label,
			"datasets": [
				{
					"name": "CO2",
					"values": co2_value,
					"chartType": "bar",
				},
				{
					"name": "CH4",
					"values": ch4_value,
					"chartType": "bar"
				},
				{
					"name": "N2O",
					"values": n2o_value,
					"chartType": "bar"
				}
			]
		},
		"barOptions": {
			"stacked": 1
		},
		"colors":["pink","blue","green"]
	}
	return chart