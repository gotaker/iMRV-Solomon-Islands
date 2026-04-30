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

@frappe.whitelist()
def download_pdf(inventory_year=None, inventory_unit=None):
	"""Editorial PDF export for the GHG Inventory (Gas-Wise) Report."""
	from mrvtools.mrvtools.pdf_export import render_tracking_report_pdf

	# Validate inventory_unit — anything else makes execute() return None
	# (TypeError downstream). Caught in adversarial probes 2026-04-30.
	if inventory_unit not in (None, "", "tCO2e", "GgCO2e"):
		inventory_unit = "tCO2e"

	try:
		columns_pkg = execute(inventory_year, inventory_unit) or [[], []]
	except Exception:
		columns_pkg = [[], []]
	raw_cols = columns_pkg[0] if columns_pkg else []
	columns = [c.get("name") if isinstance(c, dict) else str(c) for c in raw_cols]
	raw_data = columns_pkg[1] if len(columns_pkg) > 1 and columns_pkg[1] else []

	# Each row is a dict with the columns as keys (incl. the 'indent' field for tree rendering).
	# Convert to a plain list-of-lists matching `columns`. Skip 'indent' which is presentation-only.
	data = []
	for row in raw_data:
		if isinstance(row, dict):
			data.append([row.get(c) for c in columns])
		elif isinstance(row, (list, tuple)):
			data.append(list(row))

	chart_raw = get_chart(inventory_year, inventory_unit) or {}
	# get_chart returns {data:[(co2,ch4,n2o)], labels:["CO2","CH4","N2O"]}
	# For a bar chart we need {datasets:[{name, values}], labels}.
	bar_values = []
	if chart_raw.get("data"):
		first = chart_raw["data"][0] if chart_raw["data"] else None
		if isinstance(first, (list, tuple)):
			bar_values = list(first)
		elif first is not None:
			bar_values = [first]
	chart_data = (
		{"datasets": [{"name": "Emissions", "values": bar_values}],
		 "labels": chart_raw.get("labels") or []}
		if bar_values else None
	)

	pie_raw = get_pie_chart(inventory_year, inventory_unit) or {}
	# Pie data is {data:[(sector_total,)...], labels:[6 sector names]} — unwrap tuples
	pie_data = []
	for v in pie_raw.get("data") or []:
		if isinstance(v, (list, tuple)):
			pie_data.append(v[0] if v else 0)
		else:
			pie_data.append(v)
	pie_chart_data = (
		{"data": pie_data, "labels": pie_raw.get("labels") or []}
		if any(pie_data) else None
	)

	return render_tracking_report_pdf(
		report_slug="GHG-Inventory-Gas-Wise-Report",
		report_title="GHG Inventory Report",
		lede=f"National greenhouse-gas inventory by category and gas — {inventory_year or 'all years'}, {inventory_unit or 'tCO₂e'}.",
		columns=columns,
		data=data,
		chart_data=chart_data,
		pie_chart_data=pie_chart_data,
		chart_caption_bar=f"Total emission by gas ({inventory_unit or 'tCO₂e'})",
		chart_caption_pie="Total emission by sector",
		table_title="Emission breakdown",
		filter_state={"Inventory Year": inventory_year, "Unit": inventory_unit},
	)
