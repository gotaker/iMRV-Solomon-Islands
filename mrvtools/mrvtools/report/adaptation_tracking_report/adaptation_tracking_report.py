# Copyright (c) 2023, tridotstech and contributors
# For license information, please see license.txt

import frappe


def execute(filters=None):
	columns, data, chart = get_columns(), get_datas(filters), get_chart()
	return columns, data, None, chart


def get_columns():
	col = []
	col.append("Project ID" + ":Link/Project")
	col.append("Project Name" + ":Data")
	col.append("Objective" + ":Data")
	col.append("Key Sector" + ":Data")
	col.append("Key Sub-sector" + ":Data")
	col.append("Cost in USD" + ":Float")
	col.append("Location" + ":Data")
	col.append("Implementing entity or entities" + ":Data")
	col.append("Other Agency" + ":Data")
	col.append("Start Date" + ":Data")
	col.append("Financial Closure Date" + ":Data")
	col.append("Lifetime in Years" + ":Int")
	col.append("Included In" + ":Data")
	col.append("Impact Summaries" + ":Data")
	return col

def get_datas(filters):
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
		conditions += f" AND A.{resWord} = 1"


	query= f"""
			SELECT
				P.name as project_id, 
				P.project_name,
				P.objective,
				P.key_sector,
				P.key_sub_sector,
				P.costusd as cost_in_usd,
				P.location,
				P.implementing_entity as implementing_entity_or_entities,
				P.other_agency,
				P.start_date,
				P.financial_closure_date,
				P.lifetime as lifetime_in_years,
				A.included_in,
				A.name
				
			FROM
				`tabProject` as P
			INNER JOIN
				`tabAdaptation` as A 
			ON
				P.name = A.project_id
			WHERE 
				P.docstatus != 2
				{conditions}
			ORDER BY
				A.project_id
	"""
	result = frappe.db.sql(query, as_dict=1)
	field_list = []
	meta = frappe.get_meta("Adaptation")
	meta_dict = meta.as_dict()
	fields = meta_dict["fields"]
	for field in fields:
		if field["fieldtype"] == "Check":
			field_list.append(field["fieldname"])
	for each in result:
		get_list=[]
		values= frappe.db.get_value("Adaptation",each["name"],field_list,as_dict=1)
		for key,value in values.items():
			if value == 1:
				cur_ele = key.split("_")
				cur_word = " ".join(cur_ele)
				resu = cur_word.title()
				get_list.append(resu)
		resString = ",".join(get_list)
		each["impact_summaries"] = resString
	return result

def get_chart():
	field_list = []
	get_counts = []
	meta = frappe.get_meta("Adaptation")
	meta_dict = meta.as_dict()
	fields = meta_dict["fields"]
	for field in fields:
		if field["fieldtype"] == "Check":
			field_list.append(field["fieldname"])
	for field in field_list:
		count=0
		values=frappe.db.get_all("Adaptation",field)
		for i in values:
			for key,value in i.items():
				if value ==1:
					count= count+1
		get_counts.append(count)
		
	chart = {
		'data': {
		  'labels': ['Forest Health', 'Watershed Health', 'Coastal Health', 'Water Security', 'Security of Place', 'Energy Security', 'Income Security', 'Community Health', 'Food Security'], 
		  'datasets': [{'title': 'No. of Projects', 'values': get_counts}]
		  }, 
		'type': 'bar', 
		'colors': ['red']
	}
	return chart


		