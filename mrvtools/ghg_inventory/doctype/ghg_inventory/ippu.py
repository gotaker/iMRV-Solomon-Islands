import frappe
import json

@frappe.whitelist()
def ippu_calculation(doc,doc_name,tablefields): 

	document = frappe.get_doc(doc,doc_name)
	
	tables_lst = tablefields
	if type(tablefields)==str:
		tables_lst = json.loads(tablefields)
	tab_fields = []
	for tf in tables_lst:
		if document.get(tf):
			if len(document.get(tf))>0:
				tab_fields.append(tf)
	
	if document.workflow_state == "Approved" and tab_fields:
		tab_fields = str(tab_fields)
		if frappe.db.exists("GHG Inventory Master Report", document.year):
			report_doc = frappe.get_doc("GHG Inventory Master Report", document.year)
			calculation_part(tab_fields,document,report_doc)
		else:
			# Create a new GHG Inventory Master Report if it does not exist
			report_doc = frappe.get_doc({
				"doctype": "GHG Inventory Master Report",
				"year": document.year
			})
			category_list = frappe.db.get_list('GHG Inventory Report Categories', 
					fields= ['category_name','display_order',"indent","parent1","parent2"],
					limit = 500,
					order_by ='display_order asc'
				)
			for i in category_list:
				report_doc.append("report",{"categories":i.category_name,"parent_categories":i.parent1,"parent_2_categories":i.parent2,"indent":i.indent})
			report_doc.insert(ignore_permissions = True)
			calculation_part(tab_fields,document,report_doc)



def calculation_part(tablefields,document,report_doc):
	if(tablefields != ""):
		solvents_sum_co2 = 0; solvents_cumulative_co2 = 0
		refrigeration_sum_co2 = 0; refrigeration_cumulative_co2 = 0
		other_applications_sum_co2 = 0; other_applications_cumulative_co2 = 0
		fire_protection_sum_co2 = 0; fire_protection_cumulative_co2 = 0
		foam_blowing_agents_sum_co2 = 0; foam_blowing_agents_cumulative_co2 = 0
		aerosols_sum_co2 = 0; aerosols_cumulative_co2 = 0
		sf6_and_pfcs_from_other_product_use_sum_co2 = 0; sf6_and_pfcs_from_other_product_use_cumulative_co2 = 0
		electrical_equipment_sum_co2 = 0; electrical_equipment_cumulative_co2 = 0
		other_use_sum_co2 = 0; other_use_cumulative_co2 = 0
		n2o_from_product_uses_sum_co2 = 0; n2o_from_product_uses_cumulative_co2 = 0
		table_str = str(tablefields)
		table_str = table_str[1:-1]
		table_str = "(" + table_str + ")"
		query = f"""
			SELECT CT.name,PT.co2, PT.ch4,PT.n2o,PT.cumulative_ch4,PT.cumulative_co2,PT.cumulative_n2o,PT.total_co2
			FROM `tabGHG Inventory Report Formulas` PT
			INNER JOIN `tabGHG Inventory TableName ChildTable` CT ON CT.parent = PT.name
			WHERE CT.name IN {table_str}
		"""
		result = frappe.db.sql(query, as_dict=True)
		
		
		for i in result:
			gwp_methane = 0
			gwp_n2o = 0
			gwp_list = frappe.db.get_list('IPPU GWP Master List',
					fields= ["name","gwp"],
					filters= {
						"gas_name": ["in",["Methane ","Nitrous oxide"]],
					})

			for g in gwp_list:
				if(g.name == "Nitrous oxide"):
					gwp_n2o +=float( g.gwp)
				else:
					gwp_methane += float(g.gwp)

			if ( i.name == "lime_production"):
				amount =[]
				lime =  frappe.db.get_single_value('IPPU Emission Factors Master List', 'emission_factor_2')
				for a in document.get(i.name):
					amount.append(a.amount_produced_tonnes)
				cumulative_co2 = eval(i.cumulative_co2) 
				total_co2 = eval(i.total_co2)

				
				for row in report_doc.report:
					if row.categories == document.sub_sector:
						row.set("co2",cumulative_co2)
						row.set("total_co2_eq",total_co2)
			
			
			if(i.name == "cement_production"):
				sum_co2  = 0
				# clinker_fraction =[]
				cement =  frappe.db.get_single_value('IPPU Emission Factors Master List', 'emission_factor_1')
				clinker_import= document.clinker_data[0].clinker_import_tonnes
				clinker_export= document.clinker_data[0].clinker_export_tonnes
				for a in document.get(i.name):
					amount = a.amount_produced_tonnes
					clinker_fraction = a.clinker_fraction_cement
					sum_co2  += eval(i.co2)
					# clinker_fraction.append(a.clinker_fraction_cement)
				cumulative_co2 = eval(i.cumulative_co2)
				total_co2 = eval(i.total_co2)

				
				for row in report_doc.report:
					if row.categories == document.sub_sector:
						row.set("co2",cumulative_co2)
						row.set("total_co2_eq",total_co2)
			
			if(i.name == "chemical_industry"):
				
				# clinker_fraction =[]
				
				sum_co2 = 0;sum_ch4 = 0;sum_n2o = 0;sum_total_co2 = 0
				for a in document.get(i.name):
					quantity = a.amt_of_chemical_tonnes
					co2 = a.emission_factor_co2
					ch4 = a.emission_factor_ch4
					n2o = a.emission_factor_n2o
					cumulative_co2 = eval(i.cumulative_co2)
					cumulative_ch4 = eval(i.cumulative_ch4)
					cumulative_n2o = eval(i.cumulative_n2o)
					total_co2 = eval(i.total_co2)

					sum_co2 += cumulative_co2
					sum_ch4 += cumulative_ch4
					sum_n2o += cumulative_n2o
					sum_total_co2 += total_co2
					
					for row in report_doc.report:
						if row.categories == a.chemical and row.parent_categories == "2.B. Chemical industry":
							row.set("co2",cumulative_co2)
							row.set("ch4",cumulative_ch4)
							row.set("n2o",cumulative_n2o)
							row.set("total_co2_eq",total_co2)


				for row in report_doc.report:
					if row.categories == "2.B. Chemical industry":
						row.set("co2",sum_co2)
						row.set("ch4",sum_ch4)
						row.set("n2o",sum_n2o)
						row.set("total_co2_eq",sum_total_co2)


			if(i.name == "other_ippu"):
				sum_co2=0
				sum_ch4=0
				sum_n2o=0
				for j in document.get(i.name):
					amount = j.amount_of_production
					co2 = float(j.emission_factor_co2)
					ch4 = float(j.emission_factor_ch4)
					n2o = float(j.emission_factor_n2o)
					sum_co2 += eval(i.co2)
					sum_ch4 += eval(i.ch4)
					sum_n2o += eval(i.n2o)
				cumulative_co2=eval(i.cumulative_co2)
				cumulative_ch4=eval(i.cumulative_ch4)
				cumulative_n2o=eval(i.cumulative_n2o)
				total_co2=eval(i.total_co2)

				for row in report_doc.report:
					if row.categories == "2.D.3. Other":
						row.set("co2",cumulative_co2)
						row.set("ch4",cumulative_ch4)
						row.set("n2o",cumulative_n2o)
						row.set("total_co2_eq",total_co2)


			if(i.name == "activity_data"):
				sum_co2=0
				sum_ch4=0
				sum_n2o=0
				for j in document.get(i.name):
					amount = j.amount_of_production
					co2 = float(j.emission_factor_co2)
					ch4 = float(j.emission_factor_ch4)
					n2o = float(j.emission_factor_n2o)
					sum_co2 += eval(i.co2)
					sum_ch4 += eval(i.ch4)
					sum_n2o += eval(i.n2o)
				cumulative_co2=eval(i.cumulative_co2)
				cumulative_ch4=eval(i.cumulative_ch4)
				cumulative_n2o=eval(i.cumulative_n2o)
				total_co2=eval(i.total_co2)

				for row in report_doc.report:
					if row.categories == "2.H.2. Food and beverages industry":
						row.set("co2",cumulative_co2)
						row.set("ch4",cumulative_ch4)
						row.set("n2o",cumulative_n2o)
						row.set("total_co2_eq",total_co2)


			if(i.name == "lubricant_use"):
				
				sum_co2=0
				for j in document.get(i.name):
					amount_consumed  = float(j.amount_consumed)
					carbon_content  = float(j.carbon_content)
					fraction_oxidized = float(j.fraction_oxidised)
					category = j.lubricant_name
					sum_co2 += eval(i.co2)
					
				lubricant_cumulative_co2=eval(i.cumulative_co2)
				lubricant_total_co2=eval(i.total_co2)
				
				for row in report_doc.report:
					if row.categories == "2.D.1. Lubricant use":
						row.set("co2",lubricant_cumulative_co2)
						row.set("total_co2_eq",lubricant_total_co2)
						

			if(i.name in["solvents","refrigeration","other_applications","fire_protection","foam_blowing_agents","aerosols"]):
				
				sum_co2 =0
				for j in document.get(i.name):
					gwp = frappe.db.get_value('IPPU GWP Master List',
					["gwp"],
					{
						"gas_name": j.gas_consumed,
					})
					gwp_value = float(gwp)
					amount = j.amount
					if(i.name == "solvents"):
						solvents_sum_co2 +=eval(i.co2)
						sum_co2 +=eval(i.co2)
						solvents_cumulative_co2 = eval(i.cumulative_co2)
					if(i.name == "refrigeration"):
						refrigeration_sum_co2 +=eval(i.co2)
						sum_co2 +=eval(i.co2)
						refrigeration_cumulative_co2 = eval(i.cumulative_co2)
					if(i.name == "other_applications"):
						other_applications_sum_co2 +=eval(i.co2)
						sum_co2 +=eval(i.co2)
						other_applications_cumulative_co2 = eval(i.cumulative_co2)
					if(i.name == "fire_protection"):
						fire_protection_sum_co2 +=eval(i.co2)
						sum_co2 +=eval(i.co2)
						fire_protection_cumulative_co2 = eval(i.cumulative_co2)
					if(i.name == "foam_blowing_agents"):
						foam_blowing_agents_sum_co2 +=eval(i.co2)
						sum_co2 +=eval(i.co2)
						foam_blowing_agents_cumulative_co2 = eval(i.cumulative_co2)
					if(i.name == "aerosols"):
						aerosols_sum_co2 +=eval(i.co2)
						sum_co2 +=eval(i.co2)
						aerosols_cumulative_co2 += eval(i.cumulative_co2)


				for row in report_doc.report:
					if row.categories == '2.F.1. Refrigeration and air-conditioning':
						row.set("co2",refrigeration_cumulative_co2)
						row.set("total_co2_eq",refrigeration_cumulative_co2)
					if row.categories == '2.F.2. Foam blowing agents':
						row.set("co2",foam_blowing_agents_cumulative_co2)
						row.set("total_co2_eq",foam_blowing_agents_cumulative_co2)
					if row.categories == '2.F.3. Fire protection':
						row.set("co2",fire_protection_cumulative_co2)
						row.set("total_co2_eq",fire_protection_cumulative_co2)
					if row.categories == '2.F.4. Aerosols':
						row.set("co2",aerosols_cumulative_co2)
						row.set("total_co2_eq",aerosols_cumulative_co2)
					if row.categories == '2.F.5. Solvents':
						row.set("co2",solvents_cumulative_co2)
						row.set("total_co2_eq",solvents_cumulative_co2)
					if row.categories == '2.F.6. Other applications':
						row.set("co2",other_applications_cumulative_co2)
						row.set("total_co2_eq",other_applications_cumulative_co2)

			if(i.name in["electrical_equipment","sf6_and_pfcs_from_other_product_use","other_use"]):
				
				sum_co2 =0
				for j in document.get(i.name):
					gwp = frappe.db.get_value('IPPU GWP Master List',
					["gwp"],
					{
						"gas_name": j.gas_consumed,
					})
					gwp_value = float(gwp)
					amount = j.amount
					if(i.name == "electrical_equipment"):
						electrical_equipment_sum_co2 +=eval(i.co2)
						sum_co2 +=eval(i.co2)
						electrical_equipment_cumulative_co2 += eval(i.cumulative_co2)
					if(i.name == "sf6_and_pfcs_from_other_product_use"):
						sf6_and_pfcs_from_other_product_use_sum_co2 +=eval(i.co2)
						sum_co2 +=eval(i.co2)
						sf6_and_pfcs_from_other_product_use_cumulative_co2 += eval(i.cumulative_co2)
					if(i.name == "other_use"):
						other_use_sum_co2 +=eval(i.co2)
						sum_co2 +=eval(i.co2)
						other_use_cumulative_co2 += eval(i.cumulative_co2)


				for row in report_doc.report:
					if row.categories == '2.G.1. Electrical equipment':
						row.set("co2",electrical_equipment_cumulative_co2)
						row.set("total_co2_eq",electrical_equipment_cumulative_co2)
					if row.categories == '2.G.2. SF6 and PFCs from other product use':
						row.set("co2",sf6_and_pfcs_from_other_product_use_cumulative_co2)
						row.set("total_co2_eq",sf6_and_pfcs_from_other_product_use_cumulative_co2)
					if row.categories == '2.G.4. Other':
						row.set("co2",other_use_cumulative_co2)
						row.set("total_co2_eq",other_use_cumulative_co2)
						

			if(i.name == "n2o_from_product_uses"):
				
				sum_co2 =0
				for j in document.get(i.name):
					gwp = frappe.db.get_value('IPPU GWP Master List',
					["gwp"],
					{
						"gas_name": "Nitrous oxide",
					})
					gwp_value = float(gwp)
					amount = j.amount
					if(i.name == "n2o_from_product_uses"):
						n2o_from_product_uses_sum_co2 +=eval(i.co2)
						sum_co2 +=eval(i.co2)
						n2o_from_product_uses_cumulative_co2 += eval(i.cumulative_co2)


				for row in report_doc.report:
					if row.categories == '2.G.3. N2O from product uses':
						row.set("co2",n2o_from_product_uses_cumulative_co2)
						row.set("total_co2_eq",n2o_from_product_uses_cumulative_co2)



			category_co2=0;sector_co2 = 0
			category_ch4=0;sector_ch4 = 0
			category_n2o=0;sector_n2o = 0
			category_total=0;setcor_total = 0
			total_sector_co2 = 0
			total_sector_ch4 = 0
			total_sector_n2o = 0
			total_sector_total = 0
			without_land_use_total = 0
			with_land_use_total = 0
			for row in report_doc.report:
				if row.parent_categories == document.category:
					category_co2 += row.co2
					category_ch4 += row.ch4
					category_n2o += row.n2o
					category_total += row.total_co2_eq

			for row in report_doc.report:
				if(row.categories == document.category):
					row.set("co2",category_co2)
					row.set("ch4",category_ch4)
					row.set("n2o",category_n2o)
					row.set("total_co2_eq",category_total)
			for row in report_doc.report:
				if row.parent_categories == document.sector:
					sector_co2 += row.co2
					sector_ch4 += row.ch4
					sector_n2o += row.n2o
					setcor_total += row.total_co2_eq

			for row in report_doc.report:
				if(row.categories == document.sector):
					row.set("co2",sector_co2)
					row.set("ch4",sector_ch4)
					row.set("n2o",sector_n2o)
					row.set("total_co2_eq",setcor_total)
			
			for row in report_doc.report:
				if row.parent_categories == 'Total National Emissions and Removals':
					total_sector_co2 += row.co2
					total_sector_ch4 += row.ch4
					total_sector_n2o += row.n2o
					total_sector_total += row.total_co2_eq

			for row in report_doc.report:
				if(row.categories == 'Total National Emissions and Removals'):
					row.set("co2",total_sector_co2)
					row.set("ch4",total_sector_ch4)
					row.set("n2o",total_sector_n2o)
					row.set("total_co2_eq",total_sector_total)

			for row in report_doc.report:
				if row.parent_2_categories == 'Total CO2 equivalent emissions without land use':
					without_land_use_total += row.total_co2_eq

			for row in report_doc.report:
				if(row.categories == 'Total CO2 equivalent emissions without land use'):
					row.set("total_co2_eq",without_land_use_total)

			for row in report_doc.report:
				if row.parent_2_categories == 'Total CO2 equivalent emissions with land use':
					with_land_use_total += row.total_co2_eq

			for row in report_doc.report:
				if(row.categories == 'Total CO2 equivalent emissions with land use'):
					row.set("total_co2_eq",with_land_use_total)
			
						
			report_doc.save(ignore_permissions=True)
			frappe.db.commit()
