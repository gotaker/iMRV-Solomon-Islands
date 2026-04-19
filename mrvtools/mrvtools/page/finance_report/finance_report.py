# Copyright (c) 2023, NetZeroLabs and contributors
# For license information, please see license.txt

import frappe,json
import pandas as pd

from frappe.utils import get_site_base_path,now

@frappe.whitelist()
def execute(year = None,objective =None,key_sector = None,key_sub_sector = None):
	columns, data = get_columns(),get_datas(year,objective,key_sector,key_sub_sector)
	return columns, data

def get_columns():
	col = []
	col.append("Action" + ":Data")
	col.append("Programme" + ":Data")
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
	col.append("Exchange Rate" + ":Data")
	col.append("Funding Type" + ":Data")
	col.append("Channel" + ":Data")
	col.append("Expected Budget Spend in USD" + ":Data")
	col.append("Budget Spent in USD" + ":Data")
	keys_only = [item.split(':')[0] for item in col]
	return keys_only

def get_datas(year = None,objective = None,key_sector = None,key_sub_sector = None):
	conditions = ""
	if objective:
		conditions += f"AND P.objective = '{objective}'"
	if year:
		conditions += f" AND BDS.financial_year = '{year}' AND  CFTB.financial_year = '{year}'"
	if year == '':
		conditions += f" AND YEAR(C.financial_closure_date) <= '{frappe.utils.today()[0:4]}'"
	if key_sector:
			conditions += f" AND P.key_sector like '{key_sector}'"
	if key_sub_sector:
		conditions += f" AND P.key_sub_sector like '{key_sub_sector}'"

	query= f"""
			SELECT
				CONCAT(P.action,' | ',P.action_name) as action,
				CONCAT(P.programme,' | ',P.programme_name) as programme,
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
	# values_only = list(map(lambda x : str(x),result))
	# values_only = list(map(k,result))
	values_only = [list({k: v for k, v in item.items() if k != 'name'}.values()) for item in result]
	return values_only

# def k(x):
# 	if x.action and x.action_name:
# 		x.action = f"{x.action} | {x.action_name}"
# 	else:
# 		x.action = "s"
# 	if x.programme and x.programme_name:
# 		x.programme = f"{x.programme} | {x.programme_name}"
# 	else:
# 		x.programme = "s"
# 	del x.action_name
# 	del x.programme_name
# 	return x
	# CONCAT(P.action,' : ',P.action_name) as action,
				# CONCAT(P.programme,' : ',P.programme_name) as programme,

@frappe.whitelist()
def get_chart(year = None,objective = None,key_sector = None,key_sub_sector = None):
	conditions = ""
	if objective:
		conditions += f"AND P.objective = '{objective}'"
	if year:
		conditions += f" AND BDS.financial_year = '{year}' AND  CFTB.financial_year = '{year}'"
	if year == '':
		conditions += f" AND YEAR(C.financial_closure_date) <= '{frappe.utils.today()[0:4]}'" 
	if key_sector:
			conditions += f" AND P.key_sector like '{key_sector}'"
	if key_sub_sector:
		conditions += f" AND P.key_sub_sector like '{key_sub_sector}'"


	
	query= f"""
			SELECT
				C.name,
				CFMI.name as cmfi_name,
				P.name as project_id,
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
	till_sum_actual_budget_spent = 0
	till_sum_expected_budget_spend_in_usd = 0
	sum_actual_budget_spent = 0
	sum_expected_budget_spend_in_usd = 0

	for i in result:
		
		sum_actual_budget_spent +=i.budget_spent_in_usd if i.budget_spent_in_usd else 0
		sum_expected_budget_spend_in_usd += i.expected_budget_spend_in_usd if i.expected_budget_spend_in_usd else 0
	
		
		cfmi_id = frappe.db.get_all("Climate Finance Monitoring Information",filters={"project_id":i.name},pluck="name")
		
		for id in cfmi_id:
			
			if frappe.db.exists("Climate Finance Monitoring Information",{"name":id,"monitoring_year":["<=",frappe.utils.today()[0:4]]}):
				total_spent = frappe.get_doc("Climate Finance Monitoring Information",{"name":id,"monitoring_year":["<=",frappe.utils.today()[0:4]]})
				total_disbursement_usd = total_spent.total_budget_disbursement[len(total_spent.total_budget_disbursement)-1].total_disbursement_usd
				till_sum_actual_budget_spent += total_disbursement_usd
				
			
		total_expected_spend = frappe.db.get_all("Climate Finance Disbursement Schedule ChildTable",fields=["amount"],filters = {"parent":i.name,"financial_year":["<=",frappe.utils.today()[0:4]]})
		for amount in total_expected_spend:
			till_sum_expected_budget_spend_in_usd += amount.amount
					
	if year:	
		labels = [year,"Till Date"]
		return {"datasets": [
			{
				"name": "Expected Budget Spend", "chartType": "bar",
				"values": [sum_expected_budget_spend_in_usd,till_sum_expected_budget_spend_in_usd]
			},
			{
				"name": "Actual Budget Spent", "chartType": "bar",
				"values": [sum_actual_budget_spent,till_sum_actual_budget_spent]
			}
    	],"labels":labels}

	else:
		labels = ["Till Date"]
		return {"datasets": [
			{
				"name": "Expected Budget Spend", "chartType": "bar",
				"values": [till_sum_expected_budget_spend_in_usd]
			},
			{
				"name": "Actual Budget Spent", "chartType": "bar",
				"values": [till_sum_actual_budget_spent]
			}
    	],"labels":labels}


@frappe.whitelist()
def get_pie_chart(year = None,objective = None,key_sector = None,key_sub_sector = None):
	conditions = ""
	if objective:
		conditions += f"AND P.objective = '{objective}'"
	if year:
		conditions += f" AND BDS.financial_year = '{year}' AND  CFTB.financial_year = '{year}'"
	if year == '':
		conditions += f" AND YEAR(C.financial_closure_date) <= '{frappe.utils.today()[0:4]}'" 
	if key_sector:
			conditions += f" AND P.key_sector like '{key_sector}'"
	if key_sub_sector:
		conditions += f" AND P.key_sub_sector like '{key_sub_sector}'"
	
	query= f"""
		SELECT
			
			C.name,
			CFMI.name as cmfi_name,
			P.name as project_id,
			P.key_sector,
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
	data = frappe.db.sql(query, as_dict=1)
	sector_label_list=[]
	till_sum_actual_budget_spent_list =[]
	for i in data:
		till_sum_actual_budget_spent = 0
		sector_label_list.append(i.key_sector)
			
		if frappe.db.exists("Project",{"key_sector":i.key_sector}):
			project_id = frappe.db.get_all("Project",filters={"key_sector":i.key_sector},pluck="name")
			
			
		for id in project_id:
			if frappe.db.exists("Climate Finance",{"project_id":["in",[id]]}):
				finance_id = frappe.db.get_value("Climate Finance",{"project_id":id},"name")
				cfmi_id = frappe.db.get_all("Climate Finance Monitoring Information",filters={"project_id":finance_id},pluck="name")
				for j in cfmi_id:
					if frappe.db.exists("Climate Finance Monitoring Information",{"name":j,"monitoring_year":["<=",frappe.utils.today()[0:4]]}):
							total_spent = frappe.get_doc("Climate Finance Monitoring Information",{"name":j,"monitoring_year":["<=",frappe.utils.today()[0:4]]})
							total_disbursement_usd = total_spent.total_budget_disbursement[len(total_spent.total_budget_disbursement)-1].total_disbursement_usd
							till_sum_actual_budget_spent = till_sum_actual_budget_spent + total_disbursement_usd
		till_sum_actual_budget_spent_list.append(till_sum_actual_budget_spent)

	return {"data":till_sum_actual_budget_spent_list,"labels":sector_label_list}
	

   
	
	


@frappe.whitelist()
def download_excel(columns,data):

	data_list = json.loads(data)
	column_list = json.loads(columns)
	data_dict = {column_list[i]: [row[i] for row in data_list] for i in range(len(column_list))}
	export_data = pd.DataFrame(data_dict)

	site_name = get_site_base_path()
	nowTime = now()[:-7]
	nowTime = nowTime.replace(" ","")
	nowTime = nowTime.replace("-","")
	nowTime = nowTime.replace(":","")
	export_data.to_excel(f"{site_name}/public/files/Finance-Report-{nowTime}.xlsx",index=False)
	return f"../files/Finance-Report-{nowTime}.xlsx"