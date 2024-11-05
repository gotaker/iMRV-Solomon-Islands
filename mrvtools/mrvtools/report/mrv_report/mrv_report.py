# Copyright (c) 2023, tridotstech and contributors
# For license information, please see license.txt


import frappe

monitoringYears = []
def execute(filters=None):
	columns, data, chart = get_columns(filters), get_datas(filters), get_chart(filters)
	return columns, data, None, chart


def get_columns(filters):
	col = []
	if filters.get("project"):	
		if filters.get("report") == "Project Details":
			col.append("Project Title" + ":Link/Project")
			col.append("Cost in USD" + ":Float")
			col.append("Location" + ":Data")
			col.append("Implementing entity or entities" + ":Data")
			col.append("Other Agency" + ":Data")
			col.append("Start Date" + ":Data")
			col.append("Lifetime in Years" + ":Int")

		if filters.get("report") == "Mitigation Summary":
			col.append("Performance Indicator" + ":Data")
			col.append("Unit" + ":Data")
			col.append("Expected Value" + ":Data")
			totalMonitoringYearsMitigation = frappe.db.get_all('Mitigation Monitoring Information',
						filters={'proj_id':filters.get("project")},
						fields = ['monitoring_year'],
						order_by = 'monitoring_year asc' )
			monitoringYears = totalMonitoringYearsMitigation
			for i in totalMonitoringYearsMitigation:
				col.append(f"{i.monitoring_year}" + ":Data")

		if filters.get("report") == "Adaptation Summary":
			col.append("Category" + ":Data")
			col.append("Question" + ":Data")
			col.append("Expected Value" + ":Float")
			totalMonitoringYearsAdaptation = frappe.db.get_all('Adaptation Monitoring Information',
							filters={'proj_id':filters.get("project")},
							fields = ['monitoring_year'],
							order_by = 'monitoring_year asc' )
			for i in totalMonitoringYearsAdaptation:
				col.append(f"{i.monitoring_year}" + ":Data")
		
		if filters.get("report") == "Finance Summary":
			col.append("Finance Data" + ":Data")
			name = frappe.db.get_value('Climate Finance', {'project_id': f'{filters.get("project")}'}, 'name')
			totalMonitoringYearsFinance = frappe.db.get_list(
				"Climate Finance Disbursement Schedule ChildTable",
				fields=['financial_year'],
				filters = {"parent" : name},
				order_by = 'financial_year')
			for i in totalMonitoringYearsFinance:
				col.append(f"{i.financial_year}" + ":Data")

		if filters.get("report") == "SDG Summary":
			col.append("Category" + ":Data")
			col.append("Question" + ":Data")
			col.append("Expected Value" + ":Float")
			totalMonitoringYearsAdaptation = frappe.db.get_all('SDG Monitoring Information',
							filters={'proj_id':filters.get("project")},
							fields = ['monitoring_year'],
							order_by = 'monitoring_year asc' )
			for i in totalMonitoringYearsAdaptation:
				col.append(f"{i.monitoring_year}" + ":Data")
		
		
	return col

def get_datas(filters):
	conditions = ""
	if filters.get("project"):	
		if filters.get("report") == "Project Details":
				conditions += f" AND P.name like '{filters.get('project')}'"
				query= f"""
					SELECT
						P.project_name as project_title,
						P.costusd as cost_in_usd,
						P.location,
						P.implementing_entity as implementing_entity_or_entities,
						P.other_agency,
						P.start_date,
						P.lifetime as lifetime_in_years,
						P.name
					FROM
						`tabProject` as P
					WHERE 
						P.docstatus != 2
						{conditions}
					"""
				result = frappe.db.sql(query, as_dict=1)
				return result
		
		if filters.get("report") == "Mitigation Summary":
				conditions += f" AND MI.project_id = '{filters.get('project')}'"

				expectedValue = frappe.db.get_value('Mitigations',{"project_id":f'{filters.get("project")}'},'expected_annual_ghg')
				output = [{"performance_indicator":"GHG Emissions Achieved (tCO2e)","unit":"tCO2e","expected_value":expectedValue}]
				monitoringYears = frappe.db.get_all('Mitigation Monitoring Information',
						filters={'proj_id':filters.get("project")},
						fields = ['monitoring_year'],
						order_by = 'monitoring_year asc' )
				for i in monitoringYears:
					currentValue = frappe.db.get_value('Mitigation Monitoring Information',{"proj_id":f'{filters.get("project")}',"monitoring_year":i.monitoring_year},'actual_annual_ghg')
					output[0][f'{i.monitoring_year}'] = currentValue if currentValue else 0
				
				query= f"""
					SELECT
						MCT.performance_indicator,
						MCT.unit,
						MCT.expected_value
					FROM
						`tabMitigations` as MI
					INNER JOIN
						`tabMitigation Performance Indicator ChildTable` as MCT
					ON
						MI.name = MCT.parent
					WHERE 
						MI.docstatus != 2
						{conditions}
					"""
				result = frappe.db.sql(query, as_dict=1)
				for each in result:
					for i in monitoringYears:
						query = f"""
									SELECT
										MCT.actual_monitored_value
									FROM
										`tabMitigation Monitoring Information` AS MI
									INNER JOIN
										`tabMitigation Monitoring Information ChildTable` AS MCT
									ON
										MI.name = MCT.parent
									WHERE
										MI.proj_id = '{filters.get('project')}'
									AND
										MI.monitoring_year = '{i.monitoring_year}'
									AND 
										MCT.performance_indicator = '{each.performance_indicator}'
									"""
						value = frappe.db.sql(query,as_dict =1)

						

						each[f'{i.monitoring_year}'] = value[0].actual_monitored_value if value and value[0].actual_monitored_value else 0
				output.extend(result)
				return output
	
		if filters.get("report") == "Adaptation Summary":
				conditions += f" AND AM.project_id like '{filters.get('project')}'"
				query= f"""
					SELECT
						QI.category,
						QI.question,
						QI.expected_value
					FROM
						`tabAdaptation` AS AM
					INNER JOIN
						`tabAdaptation Quantitative ChildTable` as QI
					ON
						AM.name = QI.parent
					WHERE
						AM.docstatus != 2
					AND
						QI.expected_value != 0
						{conditions}
					"""
				result = frappe.db.sql(query, as_dict=1)
				monitoringYearsAdaptation = frappe.db.get_all('Adaptation Monitoring Information',
							filters={'proj_id':filters.get("project")},
							fields = ['monitoring_year'],
							order_by = 'monitoring_year asc')
				for each in result:
					for i in monitoringYearsAdaptation:
						query = f"""
									SELECT
										ACT.actual_value
									FROM
										`tabAdaptation Monitoring ChildTable` AS ACT
									INNER JOIN
										`tabAdaptation Monitoring Information` AS AMI
									ON
										ACT.parent = AMI.name
									WHERE
										AMI.proj_id = '{filters.get('project')}'
									AND
										AMI.monitoring_year = '{i.monitoring_year}'
									AND 
										ACT.question = '{each.question}'
									"""
						valueAdaptation = frappe.db.sql(query,as_dict =1)
						each[f'{i.monitoring_year}'] = valueAdaptation[0].actual_value if valueAdaptation and valueAdaptation[0].actual_value else 0
				return result
		#############################################
		if filters.get("report") == "Finance Summary":
				amountExpected = {'finance_data': 'Expected Spend (USD)'}
				amountSpent = {'finance_data':'Amount Spent (USD)'}
				# name = frappe.db.get_value('Climate Finance', {'project_id': f'{filters.get("project")}'}, 'name')
				# monitoringYearsFinance = frappe.db.get_list(
				# 	"Climate Finance Disbursement Schedule ChildTable",
				# 	fields=['financial_year'],
				# 	filters = {"parent" : name},
				# 	order_by = 'financial_year')
				expectedDoc = frappe.get_doc('Climate Finance',{'project_id': filters.get('project')})
				expectedDocList = expectedDoc.as_dict().budget_disbursement_schedule
				for i in expectedDocList:
					amountExpected[f'{i.financial_year}'] = i.amount
				
				spentDoc = frappe.get_last_doc('Climate Finance Monitoring Information', {'proj_id': filters.get('project')})
				spentDocList = spentDoc.as_dict().total_budget_disbursement
				for i in spentDocList:
					amountSpent[f'{i.financial_year}']=i.total_disbursement_usd
				
				
				return [amountSpent,amountExpected]
		#############################################
		if filters.get("report") == "SDG Summary":
				conditions += f" AND SDG.project_id like '{filters.get('project')}'"
				query= f"""
					SELECT
						QI.category,
						QI.question,
						QI.data AS expected_value
					FROM
						`tabSDG Assessment` AS SDG
					INNER JOIN
						`tabSDG Quantitative ChildTable` as QI
					ON
						SDG.name = QI.parent
					WHERE
						SDG.docstatus != 2
					AND
						QI.data != 0
						{conditions}
					"""
				result = frappe.db.sql(query, as_dict=1)
				monitoringYearsSDG = frappe.db.get_all('SDG Monitoring Information',
							filters={'proj_id':filters.get("project")},
							fields = ['monitoring_year'],
							order_by = 'monitoring_year asc' )
				for each in result:
					for i in monitoringYearsSDG:
						query = f"""
									SELECT
										ACT.data
									FROM
										`tabSDG Quantitative ChildTable` AS ACT
									INNER JOIN
										`tabSDG Monitoring Information` AS AMI
									ON
										ACT.parent = AMI.name
									WHERE
										AMI.proj_id = '{filters.get('project')}'
									AND
										AMI.monitoring_year = '{i.monitoring_year}'
									AND 
										ACT.question = '{each.question}'
									"""
						valueSDG = frappe.db.sql(query,as_dict =1)
						each[f'{i.monitoring_year}'] = valueSDG[0].data if valueSDG and valueSDG[0].data else 0
				return result
		###################################################





def get_chart(filters):
	if filters.get("report") == "Mitigation Summary":
		get_actual_ghg = []
		expectedValue = frappe.db.get_value('Mitigations',{"project_id":f'{filters.get("project")}'},'expected_annual_ghg')
		monitoringYears = frappe.db.get_all('Mitigation Monitoring Information',
							filters={'proj_id':filters.get("project")},
							fields = ['monitoring_year'],
							order_by = 'monitoring_year asc',
							pluck="monitoring_year")
		for i in monitoringYears:
			currentValue = frappe.db.get_value('Mitigation Monitoring Information',{"proj_id":f'{filters.get("project")}',"monitoring_year":i},'actual_annual_ghg')
			# output[0][f'{i.monitoring_year}'] = currentValue if currentValue else 0
			get_actual_ghg.append(currentValue)
		
			
		chart = {
			'data': {
			'labels': monitoringYears, 
			'datasets': [{'title': 'GHG Emissions Achieved (tCO2e)', 'values': get_actual_ghg}]
			}, 
			'type': 'bar', 
			'colors': ['pink']
		}
		return chart
	
	if filters.get("report") == "Finance Summary":
		year_list=[]
		amountExpected = []
		amountSpent = []
		# name = frappe.db.get_value('Climate Finance', {'project_id': f'{filters.get("project")}'}, 'name')
		# monitoringYearsFinance = frappe.db.get_list(
		# 	"Climate Finance Disbursement Schedule ChildTable",
		# 	fields=['financial_year'],
		# 	filters = {"parent" : name},
		# 	order_by = 'financial_year')
		expectedDoc = frappe.get_doc('Climate Finance',{'project_id': filters.get('project')})
		expectedDocList = expectedDoc.as_dict().budget_disbursement_schedule
		for i in expectedDocList:
			amountExpected.append(i.amount)
		spentDoc = frappe.get_last_doc('Climate Finance Monitoring Information', {'proj_id': filters.get('project')})
		spentDocList = spentDoc.as_dict().total_budget_disbursement
		for i in spentDocList:
			amountSpent.append(i.total_disbursement_usd)


		name = frappe.db.get_value('Climate Finance', {'project_id': f'{filters.get("project")}'}, 'name')
		totalMonitoringYearsFinance = frappe.db.get_list(
			"Climate Finance Disbursement Schedule ChildTable",
			fields=['financial_year'],
			filters = {"parent" : name},
			order_by = 'financial_year')
		for i in totalMonitoringYearsFinance:
			year_list.append(f"{i.financial_year}")
				
			
		chart = {
			'data': {
			'labels': year_list, 
			'datasets': [{'title': 'Amount Spent (USD)', 'values':amountSpent},{'title': 'Expected Spend (USD)', 'values':amountExpected}]
			}, 
			'type': 'bar', 
			'colors': ['pink','blue']
		}
		return chart

	