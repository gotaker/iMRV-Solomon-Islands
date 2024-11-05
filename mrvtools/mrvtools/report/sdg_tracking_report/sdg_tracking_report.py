# Copyright (c) 2023, tridotstech and contributors
# For license information, please see license.txt

import frappe


def execute(filters=None):
	columns, data, chart = getColumn(), getData(filters), getChart()
	return columns, data, None, chart


def getColumn():
	columns = []
	columns.append("Project ID" + ":Link/Project")
	columns.append("Project Title" + ":Data")
	columns.append("Objective" + ":Data")
	columns.append("Key Sector" + ":Data")
	columns.append("Key Sub-sector" + ":Data")
	columns.append("Cost in USD" + ":Float")
	columns.append("Location" + ":Data")
	columns.append("Implementing entity or entities" + ":Data")
	columns.append("Other Agency" + ":Data")
	columns.append("Start Date" + ":Date")
	columns.append("Lifetime in Years" + ":Int")
	columns.append("Included In" + ":Data")
	columns.append("Impact Summaries" + ":Data")
	return columns

def getData(filters):
	i = filters
	conditions = ""
	if filters.get("year"):
		conditions += f" AND  YEAR(P.financial_closure_date) <= '{filters.get('year')}'"
	if filters.get("year") == None:
		conditions += f"AND YEAR(P.financial_closure_date) <= '{frappe.utils.today()[0:4]}'"
	if filters.get("key_sector"):
		conditions += f" AND P.key_sector like '{filters.get('key_sector')}'"
	if filters.get("key_sub_sector"):
		conditions += f" AND P.key_sub_sector like '{filters.get('key_sub_sector')}'"
	if filters.get("impact_summaries"):
		cur_ele = filters.get("impact_summaries").lower()
		cur_word = cur_ele.split(" ")
		resWord = "_".join(cur_word)
		conditions += f" AND SDG.{resWord} = 1"

	query= f"""
			SELECT
				P.name as project_id,
				P.project_name as project_title,
				P.objective,
				P.key_sector,
				P.key_sub_sector,
				P.costusd as cost_in_usd,
				P.location,
				P.implementing_entity as implementing_entity_or_entities,
				P.other_agency,
				P.start_date,
				P.lifetime as lifetime_in_years,
				SDG.included_in,
				SDG.name
			FROM
				`tabProject` as P
			INNER JOIN
				`tabSDG Assessment` as SDG 
			ON
				P.name = SDG.project_id
			WHERE 
				P.docstatus != 2
				{conditions}
			ORDER BY
				SDG.project_id
	"""
	result = frappe.db.sql(query, as_dict=1)
	field_list = []
	meta = frappe.get_meta("SDG Assessment")
	meta_dict = meta.as_dict()
	fields = meta_dict["fields"]
	for field in fields:
		if field["fieldtype"] == "Check":
			field_list.append(field["fieldname"])
	for each in result:
		get_list=[]
		values= frappe.db.get_value("SDG Assessment",each["name"],field_list,as_dict=1)
		for key,value in values.items():
			if value == 1:
				cur_ele = key.split("_")
				cur_word = " ".join(cur_ele)
				resu = cur_word.title()
				get_list.append(resu)
		resString = ",".join(get_list)
		each["impact_summaries"] = resString
	return result


def getChart():
	field_list = []
	get_counts = []
	meta = frappe.get_meta("SDG Assessment")
	meta_dict = meta.as_dict()
	fields = meta_dict["fields"]
	for field in fields:
		if field["fieldtype"] == "Check":
			field_list.append(field["fieldname"])
	for field in field_list:
		count=0
		values=frappe.db.get_all("SDG Assessment",field)
		for i in values:
			for key,value in i.items():
				if value ==1:
					count= count+1
		get_counts.append(count)
		
	chart = {
		'data': {
		  'labels': ['Poverty Reduction', 'Inequality', 'Gender', 'Industry', 'Environment', 'Employment', 'Education', 'Water', 'Food','Health'], 
		  'datasets': [{'title': 'No. of Projects', 'values': get_counts}]
		  }, 
		'type': 'bar', 
		'colors': ['red']
	}
	return chart