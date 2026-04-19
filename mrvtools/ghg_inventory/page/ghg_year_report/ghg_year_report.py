# Copyright (c) 2023, NetZeroLabs and contributors
# For license information, please see license.txt

import frappe,json
import pandas as pd

from frappe.utils import get_site_base_path,now
@frappe.whitelist()
def execute(inventory_unit, to_year, from_year):
	columns, data = getColumns(to_year, from_year),getData(inventory_unit, from_year, to_year)
	return columns, data


@frappe.whitelist()
def getColumns(to_year, from_year):
	columns = [
				{
			"name": "Categories",
			"id": "categories",
			"width": 485
		}
    ]
	
	val = f"""
			SELECT 
				name 
			FROM 
				`tabGHG Inventory Master Report` 
			WHERE 
				name >= '{from_year}' 
			AND 
				name <= '{to_year}' 
			ORDER BY 
				year ASC;

		"""
	data = frappe.db.sql(val,as_dict =1)
	
	for i in data:
		columns.append(
			{
                "name": f'{i.name}',
                "id": f'{i.name}',
                "width": 150
            },
        )
	return columns

@frappe.whitelist()
def getData(inventory_unit, from_year, to_year):
	val = f"""
					SELECT 
						name
					FROM 
						`tabGHG Inventory Master Report` 
					WHERE 
						name >= '{from_year}' 
					AND 
						name <= '{to_year}' 
					ORDER BY 
						year ASC;

				"""
	value = frappe.db.sql(val,as_dict = 1)
	query = f"""
					Select
						category_name as categories,indent
					from
						`tabGHG Inventory Report Categories`
					order by
						display_order asc
					"""
	data = frappe.db.sql(query,as_dict =1)
	if not inventory_unit or inventory_unit == 'tCO2e':
		if from_year:
			for i in value:
				for each in data:
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
					
					each[f'{i.name}'] = f'{float(total_co2[0].total_co2_eq):.3f}' if total_co2 and total_co2[0].total_co2_eq else 0
			return data

	if inventory_unit == 'GgCO2e':
		if from_year:
			for i in value:
				for each in data:
					get_total_co2 = f"""
									SELECT 
										total_co2_eq * 0.000000001 as total_co2_eq,
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

					each[f'{i.name}'] = f'{float(total_co2[0].total_co2_eq):.5f}' if total_co2 and total_co2[0].total_co2_eq else 0
			return data
@frappe.whitelist()
def get_chart(inventory_unit, from_year, to_year):
	chart_label = []
	co2_value = []
	ch4_value = []
	n2o_value = []
	val = f"""
			SELECT 
				name
			FROM 
				`tabGHG Inventory Master Report` 
			WHERE 
				name >= '{from_year}' 
			AND 
				name <= '{to_year}' 
			ORDER BY 
				year ASC;

		"""
	value = frappe.db.sql(val,as_dict = 1)
	for i in value:
		chart_label.append(i.name)
	if not inventory_unit or inventory_unit == 'tCO2e':
		if from_year:
			for i in value:
				chart_value = f"""
						SELECT 
							co2,
							ch4,
							n2o
						FROM 
							`tabGHG Inventory Master Report ChildTable` 
						WHERE 
							parent = '{i.name}' 
						AND
							categories = 'Total National Emissions and Removals'
					"""
				chart_data = frappe.db.sql(chart_value,as_dict =1)
				frappe.log_error("Chart Data...",chart_data)
				co2_value.append(chart_data[0].co2 if chart_data[0].co2 else 0)
				ch4_value.append(chart_data[0].ch4 if chart_data[0].ch4 else 0)
				n2o_value.append(chart_data[0].n2o if chart_data[0].n2o else 0)

	if inventory_unit == 'GgCO2e':
		for i in value:
			chart_value = f"""
					SELECT 
								co2 * 0.000000001 as co2,
								ch4 * 0.000000001 as ch4,
								n2o * 0.000000001 as n2o
							FROM 
								`tabGHG Inventory Master Report ChildTable` 
							WHERE 
								parent = '{i.name}' 
							AND
								categories = 'Total National Emissions and Removals'
				"""
			
			chart_data = frappe.db.sql(chart_value,as_dict =1)
			co2_value.append(chart_data[0].co2 if chart_data and chart_data[0].co2 else 0)
			ch4_value.append(chart_data[0].ch4 if chart_data and chart_data[0].ch4 else 0)
			n2o_value.append(chart_data[0].n2o if chart_data and chart_data[0].n2o else 0)

	return {
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
		}

@frappe.whitelist()
def download_excel(columns,data):
	data_list = json.loads(data)
	for item in data_list:
		if 'indent' in item:
			del item['indent']
	column_list = json.loads(columns)
	for item in column_list:
		if 'id' in item:
			del item['id']
		if 'width' in item:
			del item['width']
	keys = list(data_list[0].keys())
	keys.remove('categories')
	keys.sort()
	new_data_list = [[item["categories"]] + [item.get(key, 0) for key in keys] for item in data_list]
	new_column_list = [item['name'] for item in column_list]

	data_dict = {new_column_list[i]: [row[i] for row in new_data_list] for i in range(len(column_list))}
	export_data = pd.DataFrame(data_dict)

	site_name = get_site_base_path()
	nowTime = now()[:-7]
	nowTime = nowTime.replace(" ","")
	nowTime = nowTime.replace("-","")
	nowTime = nowTime.replace(":","")
	export_data.to_excel(f"{site_name}/public/files/GHGInventory-Year-Wise-Report-{nowTime}.xlsx")
	return f"../files/GHGInventory-Year-Wise-Report-{nowTime}.xlsx"