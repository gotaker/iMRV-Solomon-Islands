# Copyright (c) 2023, tridotstech and contributors
# For license information, please see license.txt

import frappe


def execute(filters=None):
	columns, data = get_columns(),get_datas(filters)
	return columns, data

def get_columns():
	col = []
	col.append("Project ID" + ":Link/Project")
	col.append("Project Title" + ":Data")
	col.append("Objective" + ":Data")
	col.append("Key Sector" + ":Data")
	col.append("Key Sub-sector" + ":Data")
	col.append("Cost in USD" + ":Float")
	col.append("Cost in SBD" + ":Float")
	col.append("Location" + ":Data")
	col.append("Implementing entity or entities" + ":Data")
	col.append("Other Agency" + ":Data")
	col.append("Start Date" + ":Data")
	col.append("Lifetime in Years" + ":Int")
	col.append("Included In" + ":Data")
	col.append("Exchange Rate" + ":Data")
	col.append("Funding Type" + ":Data")
	col.append("Channel" + ":Data")
	col.append("Expected Budget Spend in USD" + ":Data")
	col.append("Budget Spent in USD" + ":Data")
	return col

def get_datas(filters):
	conditions = ""
	if filters.get("objective"):
		conditions += f"AND P.objective = '{filters.get('objective')}'"
	if filters.get("year"):
		conditions += f" AND BDS.financial_year = '{filters.get('year')}' AND  CFTB.financial_year = '{filters.get('year')}'"
	if filters.get("year") == None:
		conditions += f" AND YEAR(C.financial_closure_date) <= '{frappe.utils.today()[0:4]}'" 
	if filters.get("key_sector"):
			conditions += f" AND P.key_sector like '{filters.get('key_sector')}'"
	if filters.get("key_sub_sector"):
		conditions += f" AND P.key_sub_sector like '{filters.get('key_sub_sector')}'"

	query= f"""
			SELECT
				P.name as project_id,
				P.project_name as project_title,
				P.objective,
				P.key_sector,
				P.key_sub_sector,
				P.costusd as cost_in_usd,
				P.cost as cost_in_sbd,
				P.location,
				P.implementing_entity as implementing_entity_or_entities,
				P.other_agency,
				P.start_date,
				P.lifetime as lifetime_in_years,
				C.applied_exchange_rate as exchange_rate,
				CT.type as funding_type,
				CT.channels as channel,
				BDS.amount as expected_budget_spend_in_usd,
				CFTB.total_disbursement_usd AS  budget_spent_in_usd

				
			FROM
				(((((`tabClimate Finance` as C
			INNER JOIN
				`tabProject` as P
			ON
				C.project_id = P.name)
			INNER JOIN
				`tabSources of Climate Finance ChildTable` as CT
			ON
				C.name = CT.parent)
			INNER JOIN 
				`tabClimate Finance Disbursement Schedule ChildTable` AS BDS
			ON
				C.name = BDS.parent)
			INNER JOIN
				`tabClimate Finance Monitoring Information` AS CFMI
			ON 
				CFMI.project_id = C.name)
			INNER JOIN
				`tabClimate Finance Total Budget Disbursement ChildTable` AS CFTB
			ON
				CFTB.parent = CFMI.name)
			WHERE 
				P.docstatus != 2 
				{conditions} 
			GROUP BY 
			P.name;
	"""

	result = frappe.db.sql(query, as_dict=1)
	return result
