import frappe,json
from datetime import datetime

# @frappe.whitelist(allow_guest=True)
# def get_cards_data():
# 	data_counts = {}
# 	total_ghg_emmission = 0
# 	ghg_master_report_list = frappe.db.get_all("GHG Inventory Master Report",pluck="name")
# 	for i in ghg_master_report_list:
# 		chart_value = f"""
# 						SELECT 
# 							total_co2_eq
# 						FROM 
# 							`tabGHG Inventory Master Report ChildTable` 
# 						WHERE 
# 							parent = {i}
# 						AND
# 							categories = 'Total National Emissions and Removals'
# 					"""
# 		value = frappe.db.sql(chart_value,as_dict = 1)
# 	total_ghg_emmission += value[0]["total_co2_eq"]
	
	


# 	till_date_finance_disbursed = 0 
# 	finance_doc_list = frappe.db.get_all("Climate Finance Monitoring Information",pluck="name")
# 	for i in finance_doc_list:
# 		if frappe.db.exists("Climate Finance Monitoring Information",{"name":i,"monitoring_year":["<=",frappe.utils.today()[0:4]]}):
# 			finance_doc =  frappe.get_doc("Climate Finance Monitoring Information",{"name":i,"monitoring_year":["<=",frappe.utils.today()[0:4]]})
# 			till_date_finance_disbursed += finance_doc.total_budget_disbursement[len(finance_doc.total_budget_disbursement)-1].total_disbursement_usd

# 	data_counts["till_date_finance_disbursed"] = till_date_finance_disbursed

# 	till_date_ghg_reduction = 0 
# 	mitigation_doc_list = frappe.db.get_all("Mitigation Monitoring Information",pluck="name")
# 	for i in mitigation_doc_list:
# 		if frappe.db.exists("Mitigation Monitoring Information",{"name":i,"monitoring_year":["<=",frappe.utils.today()[0:4]]}):
# 				finance_doc =  frappe.get_doc("Mitigation Monitoring Information",{"name":i,"monitoring_year":["<=",frappe.utils.today()[0:4]]})
# 				if finance_doc.actual_annual_ghg is not None:
# 					till_date_ghg_reduction += finance_doc.actual_annual_ghg
# 				else:
# 					till_date_ghg_reduction += 0

# 	data_counts["till_date_ghg_reduction"] = till_date_ghg_reduction
# 	return data_counts

# @frappe.whitelist(allow_guest=True)
# def get_finance_data():
# 	year_list = []
# 	for i in range(9, -1, -1):
# 		year_list.append(int(frappe.utils.nowdate()[:4]) - i)
# 	year_data =[]
# 	for i in year_list:
# 		till_date_finance_disbursed = 0
# 		finance_doc_list = frappe.db.get_all("Climate Finance Monitoring Information",pluck="name",filters={"monitoring_year":i})
		
# 		for id in finance_doc_list:
# 			if frappe.db.exists("Climate Finance Monitoring Information",{"name":id}):
# 				finance_doc =  frappe.get_doc("Climate Finance Monitoring Information",{"name":id})
# 				till_date_finance_disbursed += finance_doc.total_budget_disbursement[len(finance_doc.total_budget_disbursement)-1].total_disbursement_usd
# 		year_data.append(till_date_finance_disbursed)

# 	return {"data":year_data,"labels":year_list}


# @frappe.whitelist(allow_guest=True)
# def ghg_emission_reduction_data():
# 	year_list = []
# 	for i in range(9, -1, -1):
# 		year_list.append(int(frappe.utils.nowdate()[:4]) - i)
# 	year_data =[]
# 	for i in year_list:
# 		till_date_ghg_reduction = 0 
# 		mitigation_doc_list = frappe.db.get_all("Mitigation Monitoring Information",pluck="name",filters={"monitoring_year":i})
# 		for id in mitigation_doc_list:
# 			if frappe.db.exists("Mitigation Monitoring Information",{"name":id}):
# 					finance_doc =  frappe.get_doc("Mitigation Monitoring Information",{"name":id})
# 					if finance_doc.actual_annual_ghg is not None:
# 						till_date_ghg_reduction += finance_doc.actual_annual_ghg
# 					else:
# 						till_date_ghg_reduction += 0
# 		year_data.append(till_date_ghg_reduction)

# 	return {"data":year_data,"labels":year_list}

# @frappe.whitelist(allow_guest=True)
# def ghg_emissions_data():
# 	year_list = []
# 	for i in range(10, -1, -1):
# 		year_list.append(int(frappe.utils.nowdate()[:4]) - i)
# 	year_data =[]
# 	for i in year_list:
# 		if frappe.db.exists("GHG Inventory",{"year":i}):
# 			chart_value = f"""
# 							SELECT 
# 								total_co2_eq
# 							FROM 
# 								`tabGHG Inventory Master Report ChildTable` 
# 							WHERE 
# 								parent = {i}
# 							AND
# 								categories = 'Total National Emissions and Removals'
# 						"""
# 			value = frappe.db.sql(chart_value,as_dict = 1)
# 			if value:
# 				year_data.append(value[0]["total_co2_eq"])
# 		else:
# 			value = 0
# 			year_data.append(value)
# 	return {"data":year_data,"labels":year_list}
	# chart = {
	# 	"data": {
	# 		"labels": chart_label,
	# 		"datasets": [
	# 			{
	# 				"name": "CO2",
	# 				"values": co2_value,
	# 				"chartType": "bar",
	# 			},
	# 			{
	# 				"name": "CH4",
	# 				"values": ch4_value,
	# 				"chartType": "bar"
	# 			},
	# 			{
	# 				"name": "N2O",
	# 				"values": n2o_value,
	# 				"chartType": "bar"
	# 			}
	# 		]
	# 	},
	# 	"barOptions": {
	# 		"stacked": 1
	# 	},
	# 	"colors":["pink","blue","green"]
	# }
	# return chart
@frappe.whitelist()
def get_document_count():
	data_counts = {}
	total_mitigation_projects = frappe.db.sql("""
		SELECT COUNT(name) as count from tabProject WHERE objective = 'Mitigation'
	""",as_dict=1)
	total_adaptation_projects = frappe.db.sql("""
		SELECT COUNT(name) as count from tabProject WHERE objective = 'Adaptation'
	""",as_dict=1)
	total_cross_cutting_projects = frappe.db.sql("""
		SELECT COUNT(name) as count from tabProject WHERE objective = 'Cross-Cutting'
	""",as_dict=1)
	total_enabler_projects = frappe.db.sql("""
		SELECT COUNT(name) as count from tabProject WHERE objective = 'Enablers'
	""",as_dict=1)
	total_transparency_projects = frappe.db.sql("""
		SELECT COUNT(name) as count from tabProject WHERE objective = 'Transparency'
	""",as_dict=1)

	data_counts["Mitigation"]=total_mitigation_projects[0]['count']
	data_counts["Adaptation"]=total_adaptation_projects[0]['count']
	data_counts["Cross-Cutting"]=total_cross_cutting_projects[0]['count']
	data_counts["Enablers"]=total_enabler_projects[0]['count']
	data_counts["Transparency"]=total_transparency_projects[0]['count']


	miti_keySector = frappe.db.sql(f'''SELECT name from `tabProject Key Sector` WHERE objective in ("Mitigation","Cross-Cutting")''',as_dict=1)
	miti_count_list=[]
	for i in miti_keySector:
		if frappe.db.exists("Mitigations",{"key_sector":i.name}):
			miti_count = frappe.db.get_all("Mitigations",fields=["key_sector","COUNT(name) count"],filters={'key_sector':i.name})
			miti_count_list.append(miti_count[0])
			
	adapt_keySector = frappe.db.sql(f'''SELECT name from `tabProject Key Sector` WHERE objective in ("Adaptation","Cross-Cutting")''',as_dict=1)
	adapt_count_list=[]
	for i in adapt_keySector:
		if frappe.db.exists("Adaptation",{"key_sector":i.name}):
			adapt_count = frappe.db.get_all("Adaptation",fields=["key_sector","COUNT(name) count"],filters={'key_sector':i.name})
			adapt_count_list.append(adapt_count[0])
			
	# project_planned = frappe.db.count("Project",{"status":["in",["Planned","Planning"]]})
	# project_ongoing = frappe.db.count("Project",{"status":["in",["Adopted","Under Implementation","Implemented","Operational"]]})
	project_planning = frappe.db.count("Project",{"status":"Planning"})
	project_planned = frappe.db.count("Project",{"status":"Planned"})
	project_adopted = frappe.db.count("Project",{"status":"Adopted"})
	project_under_implementation = frappe.db.count("Project",{"status":"Under Implementation"})
	project_implemented = frappe.db.count("Project",{"status":"Implemented"})
	project_operational = frappe.db.count("Project",{"status":"Operational"})
	project_completed = frappe.db.count("Project",{"status":"Completed"})
	project_status=[{"status":"Planning","count":project_planning}, {"status":"Completed","count":project_completed},
				 	{"status":"Planned","count":project_planned}, {"status":"Adopted","count":project_adopted},
					{"status":"Under Implementation","count":project_under_implementation},{"status":"Implemented","count":project_implemented},
					{"status":"Operational","count":project_operational}]

	return {"project_count":[data_counts],"mitigation":miti_count_list,"adaptation":adapt_count_list,
		 	"project_status":project_status}


@frappe.whitelist()
def get_commulative_mitigation_till_date():
	query = f"""
	SELECT
		MT.key_sector
	FROM
		`tabMitigations` MT
	WHERE 
		MT.docstatus != 2 
	ORDER BY
		MT.project_id
		"""
	data = frappe.db.sql(query,as_dict=1)
	
	result = list(dict((json.dumps(d, sort_keys=True), d) for d in data).values())
	sector_label_list=[]
	actual_reduction_list=[]
	expected_annual_ghg_list=[]
	for i in result:
		tillDateActual = frappe.db.get_all('Mitigation Monitoring Information',
			filters={"key_sector":f"{i.key_sector}"},
			fields = ["sum(actual_annual_ghg) as till_date_actual_ghg","expected_annual_ghg"])
		if tillDateActual[0].till_date_actual_ghg != None and tillDateActual[0].till_date_actual_ghg != 0.0:
			actual_reduction_list.append(tillDateActual[0].till_date_actual_ghg)
			sector_label_list.append(i.key_sector)
			if tillDateActual[0].expected_annual_ghg != None and tillDateActual[0].expected_annual_ghg != 0.0:
				expected_annual_ghg_list.append(tillDateActual[0].expected_annual_ghg)
   
	return {"data":actual_reduction_list,"labels":sector_label_list,"expected":expected_annual_ghg_list}

@frappe.whitelist()
def get_commulative_mitigation_last_year():
	query = f"""
	SELECT
		MT.key_sector
	FROM
		`tabMitigations` MT
	WHERE 
		MT.docstatus != 2 
	ORDER BY
		MT.project_id
		"""
	data = frappe.db.sql(query,as_dict=1)
	
	result = list(dict((json.dumps(d, sort_keys=True), d) for d in data).values())
	sector_label_list=[]
	actual_reduction_list=[]
	expected_annual_ghg_list = []
	today = frappe.utils.today()
	today_date = datetime.strptime(today, '%Y-%m-%d')
	last_from_year_date = datetime(today_date.year -1, 1, 1)
	last_to_year_date = datetime(today_date.year -1, 12, 31)
	last_from_year_date_str = last_from_year_date.strftime('%Y-%m-%d')
	last_to_year_date_str = last_to_year_date.strftime('%Y-%m-%d')
	for i in result:
		tillDateActual = frappe.db.get_all('Mitigation Monitoring Information',
			filters={"key_sector":f"{i.key_sector}","start_date":["between",[f"{last_from_year_date_str}",f"{last_to_year_date_str}"]]},
			fields = ["sum(actual_annual_ghg) as till_date_actual_ghg","expected_annual_ghg"])
		
		if tillDateActual[0].till_date_actual_ghg != None and tillDateActual[0].till_date_actual_ghg != 0.0:
			actual_reduction_list.append(tillDateActual[0].till_date_actual_ghg)
			sector_label_list.append(i.key_sector)
			if tillDateActual[0].expected_annual_ghg != None and tillDateActual[0].expected_annual_ghg != 0.0:
				expected_annual_ghg_list.append(tillDateActual[0].expected_annual_ghg)
   
	return {"data":actual_reduction_list,"labels":sector_label_list,"expected":expected_annual_ghg_list}

@frappe.whitelist()
def total_co2_emission_latest():
	labels = ['1. Energy', '2. Industrial processes and product use', '3. Agriculture', '4. LAND USE, LAND-USE CHANGE AND FORESTRY', '5. Waste', '6. Other']

	query = f"""
			SELECT
				total_co2_eq as 'Total CO2 Emission'
			FROM
				`tabGHG Inventory Master Report ChildTable`
			WHERE 
				docstatus != 2
			AND
				categories IN ('1. Energy', '2. Industrial processes and product use', '3. Agriculture', '4. LAND USE, LAND-USE CHANGE AND FORESTRY', '5. Waste', '6. Other')
			AND parent = {frappe.utils.today()[0:4]}
			ORDER BY
				categories
			"""
	data = frappe.db.sql(query)
	return {"data":data,"labels":labels}

@frappe.whitelist()
def get_total_project_ndp():
	doc = frappe.db.get_all("Adaptation",pluck="ndp_coverage")
	counts = {}
	for item in doc:
		if item in counts:
			counts[item] += 1
		else:
			counts[item] = 1
	return counts

@frappe.whitelist()
def get_total_sdg_category_wise():
	values=frappe.db.get_all("SDG Assessment",fields=["categories_json"])
	counts = {}
	for d in values:
		categories = json.loads(d['categories_json'])
		for category, value in categories.items():
			if category not in counts:
				counts[category] = 0
			if value:
				counts[category] += 1
	categories = list(counts.keys())
	get_counts = list(counts.values())
	return {"data":get_counts,"categories":categories}

@frappe.whitelist()
def total_co2_emission_last_five_years():
	current_year = datetime.now().year
	last_five_years = list(range(current_year - 4, current_year + 1))
	val = f"""
			SELECT 
				name 
			FROM 
				`tabGHG Inventory Master Report` 
			WHERE 
				name >= '2011' 
			AND 
				name <= '{current_year}' 
			ORDER BY 
				year ASC;

		"""

	value = frappe.db.sql(val,as_dict = 1)
	categories = ['1. Energy', '2. Industrial processes and product use', '3. Agriculture', '4. LAND USE, LAND-USE CHANGE AND FORESTRY', '5. Waste', '6. Other']
	energy = []
	ippu = []
	agriculture = []
	land = []
	waste = []
	other = []
	all = []
	for j in categories:
		for i in last_five_years:
			if frappe.db.exists('GHG Inventory Master Report',{'name':i}):
				query = f"""
					SELECT 
						categories as name, total_co2_eq as 'values' 
					FROM 
						`tabGHG Inventory Master Report ChildTable` 
					WHERE 
						parent = '{i}' 
					AND 
						categories = '{j}'
					ORDER BY 
						categories
				"""
				result = frappe.db.sql(query,as_dict=1)
				if result[0]['name'] == "1. Energy":
					energy.append(result[0]['values'])
				if result[0]['name'] == '2. Industrial processes and product use':
					ippu.append(result[0]['values'])
				if result[0]['name'] == '3. Agriculture':
					agriculture.append(result[0]['values'])
				if result[0]['name'] == '4. LAND USE, LAND-USE CHANGE AND FORESTRY':
					land.append(result[0]['values'])
				if result[0]['name'] == '5. Waste':
					waste.append(result[0]['values'])
				if result[0]['name'] == '6. Other':
					other.append(result[0]['values'])
			else:
				if j == "1. Energy":
					energy.append(0)
				if j == "2. Industrial processes and product use":
					ippu.append(0)
				if j == "3. Agriculture":
					agriculture.append(0)
				if j == "4. LAND USE, LAND-USE CHANGE AND FORESTRY":
					land.append(0)
				if j == "5. Waste":
					waste.append(0)
				if j == "6. Other":
					other.append(0)
	data = {
		"labels": last_five_years,
			"datasets": [
				{
					"name": "1. Energy",
					"values": energy,
					"chartType": "bar",
				},
				{
					"name": "2. Industrial processes and product use",
					"values": ippu,
					"chartType": "bar"
				},
				{
					"name": "3. Agriculture",
					"values": agriculture,
					"chartType": "bar"
				},
				{
					"name": "4. LAND USE, LAND-USE CHANGE AND FORESTRY",
					"values": land,
					"chartType": "bar"
				},
				{
					"name": "5. Waste",
					"values": waste,
					"chartType": "bar"
				},
				{
					"name": "6. Other",
					"values": other,
					"chartType": "bar"
				}
			]
		}
	return data


@frappe.whitelist()
def get_finance_support():
	support_needed_sum=frappe.db.get_all("Climate Finance",fields=["SUM(others) as 'Support Needed'"],filters={"others":[">",0]})
	support_received_sum=frappe.db.get_all("Climate Finance",fields=["SUM(total_sources_of_finance) as 'Support Received'"],filters={"total_sources_of_finance":[">",0]})
	support_needed_count=frappe.db.get_all("Climate Finance",fields=["COUNT(name) as 'Support Needed'"],filters={"others":[">",0]})
	support_received_count=frappe.db.get_all("Climate Finance",fields=["COUNT(name) as 'Support Received'"],filters={"total_sources_of_finance":[">",0]})
	
	return [support_needed_count[0],support_received_count[0],support_needed_sum[0],support_received_sum[0]]