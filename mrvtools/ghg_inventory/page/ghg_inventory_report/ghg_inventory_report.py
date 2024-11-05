# Copyright (c) 2023, tridotstech and contributors
# For license information, please see license.txt

import frappe,json
import pandas as pd

from frappe.utils import get_site_base_path,now

@frappe.whitelist()
def execute(inventory_year, inventory_unit, filters=None):
	columns, data = getColumns(),getData(inventory_year, inventory_unit)
	return columns, data


def getColumns():
	columns = [
		{
			"name": "Categories",
			"id": "categories",
			# "width":510
		},
		{
			"name": "CO2",
			"id": "CO2 Emission",
			# "width":126
		},
		{
			"name": "CH4",
			"id": "CH4 Emission",
			# "width":126
		},
		{
			"name": "N2O",
			"id": "N2O Emission",
			# "width":126
		},
		{
			"name": "tCO2e",
			"id": "Total CO2 Emission",
			# "width":126
		}
		
	]
	return columns

def getData(inventory_year, inventory_unit):
	conditions = ""
	if inventory_year:
		conditions += f"AND parent = '{inventory_year}'"

		if not inventory_unit or (inventory_unit) == 'tCO2e':
			conditions += f"AND parent = '{inventory_year}'"

			query = f"""
					SELECT
						categories as categories, 
						co2 as 'CO2 Emission',
						ch4 as 'CH4 Emission',
						n2o as 'N2O Emission', 
						total_co2_eq as 'Total CO2 Emission',
						indent
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
			
		if (inventory_unit) == 'GgCO2e':
			query = f"""
					SELECT
						categories as categories, 
						co2 * 0.000000001 as 'CO2 Emission',
						ch4 * 0.000000001 as 'CH4 Emission',
						n2o * 0.000000001 as 'N2O Emission', 
						total_co2_eq * 0.000000001 as 'Total CO2 Emission',
						indent
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

@frappe.whitelist()
def get_chart(inventory_year=None, inventory_unit=None):
	conditions = ""
	if inventory_year:
		conditions += f"AND parent = '{inventory_year}'"
		if not (inventory_unit) or (inventory_unit) == 'tCO2e':
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
			labels=  ["CO2","CH4","N2O"]
			data = frappe.db.sql(query)	
			if data != ():
				return {"data":data,"labels":labels}
		if inventory_unit == 'GgCO2e':
			labels=  ["CO2","CH4","N2O"]
			
			query = f"""
					SELECT
						co2 * 0.000000001 as co2,
						ch4 * 0.000000001 as ch4,
						n2o * 0.000000001 as n2o	
					FROM
						`tabGHG Inventory Master Report ChildTable`
					WHERE 
						docstatus != 2
					AND
						categories = 'Total National Emissions and Removals'
						{conditions}
					"""
			data = frappe.db.sql(query)
		
			return {"data":data,"labels":labels}



@frappe.whitelist()
def get_pie_chart(inventory_year=None, inventory_unit=None):
	conditions = ""
	if inventory_year:
		conditions += f"AND parent = '{inventory_year}'"
		if not (inventory_unit) or (inventory_unit) == 'tCO2e':
			categories = ['1. Energy', '2. Industrial processes and product use', '3. Agriculture', '4. LAND USE, LAND-USE CHANGE AND FORESTRY', '5. Waste', '6. Other']

			query = f"""
					SELECT
						total_co2_eq as 'Total CO2 Emission'
					FROM
						`tabGHG Inventory Master Report ChildTable`
					WHERE 
						docstatus != 2
					AND
						categories IN ('1. Energy', '2. Industrial processes and product use', '3. Agriculture', '4. LAND USE, LAND-USE CHANGE AND FORESTRY', '5. Waste', '6. Other')	
						{conditions}
					ORDER BY
						categories
					"""
			labels= categories
			data = frappe.db.sql(query)
			if data != ():
				return {"data":data,"labels":labels}
		if inventory_unit == 'GgCO2e':
			labels=  ['1. Energy', '2. Industrial processes and product use', '3. Agriculture', '4. LAND USE, LAND-USE CHANGE AND FORESTRY', '5. Waste', '6. Other']
			query = f"""
					SELECT
						format(total_co2_eq * 0.000000001,5) AS 'Total CO2 Emission'
					FROM
						`tabGHG Inventory Master Report ChildTable`
					WHERE
						docstatus != 2
						AND categories IN ('1. Energy', '2. Industrial processes and product use', '3. Agriculture', '4. LAND USE, LAND-USE CHANGE AND FORESTRY', '5. Waste', '6. Other')


						{conditions}
					"""
			data = frappe.db.sql(query)
			frappe.log_error("Data == ",data)
			return {"data":data,"labels":labels}


@frappe.whitelist()
def download_excel(columns,data):
	data_list = json.loads(data)
	for item in data_list:
		if 'indent' in item:
			del item['indent']
	column_list = json.loads(columns)
	for item in column_list:
		if 'name' in item:
			del item['name']
	new_data_list = [[item['categories'], item['CO2 Emission'], item['CH4 Emission'], item['N2O Emission'], item["Total CO2 Emission"]] for item in data_list]
	new_column_list = [item['id'] for item in column_list]

	data_dict = {new_column_list[i]: [row[i] for row in new_data_list] for i in range(len(column_list))}
	export_data = pd.DataFrame(data_dict)

	site_name = get_site_base_path()
	nowTime = now()[:-7]
	nowTime = nowTime.replace(" ","")
	nowTime = nowTime.replace("-","")
	nowTime = nowTime.replace(":","")
	export_data.to_excel(f"{site_name}/public/files/GHGInventory-Gas-Wise-Report-{nowTime}.xlsx")
	return f"../files/GHGInventory-Gas-Wise-Report-{nowTime}.xlsx"