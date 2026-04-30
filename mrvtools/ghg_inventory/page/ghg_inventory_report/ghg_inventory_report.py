# Copyright (c) 2023, NetZeroLabs and contributors
# For license information, please see license.txt

import json

import frappe
import pandas as pd
from frappe.utils import get_site_base_path, now


@frappe.whitelist()
def execute(inventory_year, inventory_unit, filters=None):
	columns, data = getColumns(),getData(inventory_year, inventory_unit)
	return columns, data


def getColumns():
	# Column headers carry the Unicode subscript-2 (₂) so the data table
	# reads "CO₂", "CH₄", "N₂O", "tCO₂e" as published GHG convention.
	# IDs stay ASCII so the SELECT aliases in getData() keep matching.
	columns = [
		{
			"name": "Categories",
			"id": "categories",
		},
		{
			"name": "CO₂",
			"id": "CO2 Emission",
		},
		{
			"name": "CH₄",
			"id": "CH4 Emission",
		},
		{
			"name": "N₂O",
			"id": "N2O Emission",
		},
		{
			"name": "tCO₂e",
			"id": "Total CO2 Emission",
		}

	]
	return columns


@frappe.whitelist()
def get_years():
	"""Return the list of GHG Inventory parent years that actually have data,
	newest first. Used by the Year filter on ghg-inventory-report so the
	picker only offers years with rows — replaces the old hard-coded
	1990–2050 list which left 2027–2050 as blank-chart options.
	"""
	rows = frappe.db.sql(
		"""
		SELECT DISTINCT parent
		FROM `tabGHG Inventory Master Report ChildTable`
		WHERE docstatus != 2 AND parent IS NOT NULL AND parent != ''
		ORDER BY parent DESC
		""",
		as_dict=False,
	)
	return [r[0] for r in rows]

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
			# Return raw numeric values (not MariaDB FORMAT(...) strings — those
			# embed thousands separators that JS Number() parses as NaN, which
			# was a contributing factor to the pie rendering as one solid blue
			# circle).
			query = f"""
					SELECT
						total_co2_eq * 0.000000001 AS 'Total CO2 Emission'
					FROM
						`tabGHG Inventory Master Report ChildTable`
					WHERE
						docstatus != 2
						AND categories IN ('1. Energy', '2. Industrial processes and product use', '3. Agriculture', '4. LAND USE, LAND-USE CHANGE AND FORESTRY', '5. Waste', '6. Other')


						{conditions}
					"""
			data = frappe.db.sql(query)
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