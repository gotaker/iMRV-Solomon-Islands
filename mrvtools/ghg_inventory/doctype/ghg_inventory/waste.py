import frappe
import json
# from frappe.model.document import Document

@frappe.whitelist()
def waste_calculation(doc,doc_name,tablefields):

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
	if(tablefields != []): 
		table_str = str(tablefields)
		table_str = table_str[1:-1]
		table_str = "(" + table_str + ")"
		query = f"""
			SELECT PT.co2, PT.ch4,PT.n2o,PT.cumulative_ch4,PT.cumulative_co2,PT.cumulative_n2o,PT.total_co2,CT.name,PT.co2_2,PT.cumulative_co2_additional,PT.total_cumulative
			FROM `tabGHG Inventory Report Formulas` PT
			INNER JOIN `tabGHG Inventory TableName ChildTable` CT ON CT.parent = PT.name
			WHERE CT.name IN {table_str}
		"""
		result = frappe.db.sql(query, as_dict=True)
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
		
	for f in result:    
		sum_ch4=0
		sum_co2=0
		sum_n2o=0
		sum_co2_additional =0
		total_sector_co2 = 0
		total_sector_ch4 = 0
		total_sector_n2o = 0
		total_setcor_total = 0
		without_land_use_total = 0
		with_land_use_total = 0
		for i in document.get(f.name):
			if(i.parentfield == "solid_waste"):
				cumulative_co2=0
				cumulative_n2o=0
				u = i.urban_population
				Urban=float(i.urban_population)
				Waste=float(i.waste_per_capita)
				Fraction_managed=float(i.fraction_of_waste)
				Fraction_unmanaged=float(i.fractionof_waste_go)
				ch4_managed=float(i.ch4_generation)
				ch4_unmanaged=float(i.ch4_generationper_ton)
				cumulative_ch4 = eval(f.cumulative_ch4)
				total_co2=eval(f.total_co2)
				for row in report_doc.report:
					if(row.categories == "5.A. Solid waste disposal" ):
						row.set("ch4",cumulative_ch4)
						row.set("total_co2_eq",total_co2)   
				report_doc.save(ignore_permissions=True)
				frappe.db.commit()  

			if(i.parentfield == "biological_treatment"):
				cumulative_ch4=0
				cumulative_n2o=0
				Amount= i.total_annual_amount
				co2= i.emission_factor_kgco2
				sum_co2 +=eval(f.co2)
				cumulative_co2 = eval(f.cumulative_co2)
				total_co2=eval(f.total_co2)
				for row in report_doc.report:
					if(row.categories == "5.B. Biological treatment of solid waste" ):
						row.set("co2",cumulative_co2)
						row.set("total_co2_eq",total_co2)  
						# return row.co2,row.ch4,row.total_co2_eq 
				report_doc.save(ignore_permissions=True)
				frappe.db.commit()  

			if(document.category == "5.D. Wastewater treatment and discharge"):
				if(i.parentfield == "ch4_wastewater_treatment"):
					cumulative_co2=0
					Population =float(i.population)
					Degradable = float(i.degradable_organic_component)
					Correction_industrial  =float(i.correction_factor)
					Methane_capacity =float(i.methane_producing)
					Protein = float(document.n2o_wastewater_treatment[0].per_capita_protein)
					Nitrogen_fraction = float(document.n2o_wastewater_treatment[0].nitrogen_fraction)
					Emission_factor = float(document.n2o_wastewater_treatment[0].emission_factor)
					cumulative_ch4 = eval(f.cumulative_ch4)
					cumulative_n2o = eval(f.cumulative_n2o)
					total_co2= eval(f.total_co2)
					for row in report_doc.report:
						if(row.categories == "5.D.1. Domestic wastewater" ):
							row.set("ch4",cumulative_ch4)
							row.set("n2o",cumulative_n2o)
							row.set("total_co2_eq",total_co2)  
					report_doc.save(ignore_permissions=True)
					frappe.db.commit()  

				if(i.parentfield == "industrial_wastewater_treatment"):
					cumulative_co2=0
					cumulative_n2o=0
					Production =float(i.production)
					Wastewater_generated =float(i.waste_water_gene)
					COD =float(i.cod)
					Wastewater_sludge =float(i.stuage_removed)
					Methane_produced =float(i.max_methane)
					Correction_factor =float(i.methane_correction)
					Methane_recovered =float(i.methane_recoverd)
					sum_ch4 += eval(f.ch4)
					cumulative_ch4 = eval(f.cumulative_ch4)
					total_co2 = eval(f.total_co2)
					for row in report_doc.report:
						if(row.categories == "5.D.2. Industrial wastewater" ):
							row.set("ch4",cumulative_ch4)
							row.set("total_co2_eq",total_co2)  
					report_doc.save(ignore_permissions=True)
					frappe.db.commit()  

				if(i.parentfield == "other_wastewater_treatement"):
					cumulative_co2=0
					Production = i.waste_water_generated_m3
					ch4 = i.emission_factor_tonne_ch4m3_of_wastewater_generated
					n2o =i.emission_factor_tonne_n2om3_of_wastewater_generated
					sum_ch4 += eval(f.ch4)
					sum_n2o += eval(f.n2o)
					cumulative_ch4 = eval(f.cumulative_ch4)
					cumulative_n2o = eval(f.cumulative_n2o)
					total_co2 = eval(f.total_co2)
					for row in report_doc.report:
						if(row.categories == "5.D.3. Other" ):
							row.set("ch4",cumulative_ch4)
							row.set("n2o",cumulative_n2o)
							row.set("total_co2_eq",total_co2)  
					report_doc.save(ignore_permissions=True)
					frappe.db.commit()  	

			if(i.parentfield == "other_waste"):		
				Amount =i.amount_of_waste_generated
				co2 = i.emission_factor_co2
				ch4 = i.emission_factor_ch4
				n2o = i.emission_factor_n2o
				sum_co2 += eval(f.co2)
				sum_ch4 += eval(f.ch4)
				sum_n2o += eval(f.n2o)
				cumulative_co2 = eval(f.cumulative_co2)
				cumulative_ch4 = eval(f.cumulative_ch4)
				cumulative_n2o = eval(f.cumulative_n2o)
				total_co2 = eval(f.total_co2)
				for row in report_doc.report:
					if(row.categories == "5.E. Other" ):
						row.set("co2",cumulative_co2)
						row.set("ch4",cumulative_ch4)
						row.set("n2o",cumulative_n2o)
						row.set("total_co2_eq",total_co2)  
				report_doc.save(ignore_permissions=True)
				frappe.db.commit()  
			# return total_co2,cumulative_co2
			if(i.parentfield == "waste_incineration"):	
				cumulative_ch4=0
				cumulative_n2o=0
				Waste_amount = i.total_amount
				dry_fraction1 = i.dry_matter_content
				carbon_fraction1 = i.fraction_of_carbon
				fossil_fraction = i.fraction_of_fossil
				oxidation_factor1 = i.oxidation_factor
				Population = float(document.open_burning_of_waste[0].urban_population)
				waste =float(document.open_burning_of_waste[0].waste_per_capita_kgyear)
				Population_fraction =float(document.open_burning_of_waste[0].fraction_of_population_burning_waste)
				dry_fraction2 = float(document.open_burning_of_waste[0].dry_matter)
				carbon_fraction2 = float(document.open_burning_of_waste[0].fraction_carbon)
				oxidation_factor2 = float(document.open_burning_of_waste[0].oxidation_factor)
				sum_co2 += eval(f.co2)
				sum_co2_additional  +=eval(f.co2_2)
				cumulative_co2 = eval(f.cumulative_co2)
				cumulative_co2_additional = eval(f.cumulative_co2_additional)
				total_cumulative = eval(f.total_cumulative)
				total_co2=eval(f.total_co2)
				for row in report_doc.report:
					if(row.categories == "5.C. Incineration and open burning of waste" ):
						row.set("co2",total_cumulative)
						# row.set("ch4",cumulative_ch4)
						# row.set("n2o",cumulative_n2o)
						row.set("total_co2_eq",total_co2)  
				report_doc.save(ignore_permissions=True)
				frappe.db.commit()
				
		category_co2=0;category_ch4=0;category_n2o=0;category_total=0
		sector_co2=0;sector_ch4=0;sector_n2o=0;sector_total=0
		for row in report_doc.report:
			if row.parent_categories == document.category:
				category_co2 += row.co2
				category_ch4 += row.ch4
				category_n2o += row.n2o
				category_total += row.total_co2_eq
			if(row.parent_categories == document.sector):
				sector_co2 += float(row.co2)
				sector_ch4 += float(row.ch4)
				sector_n2o += float(row.n2o)
				sector_total += float(row.total_co2_eq)
		for row in report_doc.report:
			if(row.categories == document.category and row.categories != "5.E. Other" ):
				row.set("co2",category_co2)
				row.set("ch4",category_ch4)
				row.set("n2o",category_n2o)
				row.set("total_co2_eq",category_total)
			if(row.categories == document.sector):
				row.set("co2",sector_co2)
				row.set("ch4",sector_ch4)
				row.set("n2o",sector_n2o)
				row.set("total_co2_eq",sector_total)


		for row in report_doc.report:
			if row.parent_categories == 'Total National Emissions and Removals':
				total_sector_co2 += row.co2
				total_sector_ch4 += row.ch4
				total_sector_n2o += row.n2o
				total_setcor_total += row.total_co2_eq

		for row in report_doc.report:
			if(row.categories == 'Total National Emissions and Removals'):
				row.set("co2",total_sector_co2)
				row.set("ch4",total_sector_ch4)
				row.set("n2o",total_sector_n2o)
				row.set("total_co2_eq",total_setcor_total)

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
	return "wo0rking"
