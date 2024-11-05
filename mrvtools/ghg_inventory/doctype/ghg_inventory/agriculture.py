import frappe
import json
# from frappe.model.document import Document

@frappe.whitelist()
def agri_calculation(doc,doc_name,tablefields):
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
			SELECT PT.co2, PT.ch4,PT.n2o,PT.cumulative_ch4,PT.cumulative_co2,PT.cumulative_n2o,PT.total_co2,CT.name
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

		for i in result:
			sum_co2=0
			sum_ch4=0
			sum_n2o=0
			total_sector_co2 = 0
			total_sector_ch4 = 0
			total_sector_n2o = 0
			total_setcor_total = 0
			without_land_use_total = 0
			with_land_use_total = 0
			# cumulative_co2=0
			n_leaching_cumulative_n2o=0
			# cumulative_ch4=0
			# cumulative_n2o=0

			if i.name == 'enteric_fermentation':
				for j in document.get(i.name):
					data = frappe.get_list("Livestock Emission Factor Master List",
						fields=["enteric_fermentation"],
						filters={
						"category" : j.category
					})
					head = float(j.heads)
					enteric_fermentation = float(data[0].enteric_fermentation)
					sum_ch4 += eval(i.ch4)
				cumulative_co2=0
				cumulative_n2o=0
				cumulative_ch4=eval(i.cumulative_ch4)
				total_co2=eval(i.total_co2)
				
				for row in report_doc.report:
					if row.categories == '3.A. Enteric fermentation':
						row.set("ch4",cumulative_ch4)
						row.set("total_co2_eq",total_co2)

			
			if i.name == 'indirect_manure_management':
				for j in document.get(i.name):
					data = frappe.get_list("Livestock Emission Factor Master List",
							fields=["manure_management", "excretion_rate", "typical_animal_mass","nitrogen_excretion","direct_n2o_n_emissions","managed_manure","managed_ivestock_manure","atmospheric_deposition"],
							filters={
							"category" : j.category
					})
					head = float(j.heads)
					nitrogen_excretion_rate = float(data[0].excretion_rate  )
					animal_mass = float(data[0].typical_animal_mass)
					nitrogen_excretion_managed = float(data[0].nitrogen_excretion)
					emission_factor_n2o = float(data[0].atmospheric_deposition)
					managed_livestock_manure_n2o = float(data[0].managed_ivestock_manure)
					sum_n2o += eval(i.n2o)
				cumulative_co2=0
				cumulative_ch4=0
				cumulative_n2o=eval(i.cumulative_n2o)
				total_co2=eval(i.total_co2)
				
				for row in report_doc.report:
					if row.categories == '3.B.5. Indirect N2O Emissions from Manure Management':
						row.set("n2o",cumulative_n2o)
						row.set("total_co2_eq",total_co2)

			if i.name == 'direct_emission_mms':
				for j in document.get(i.name):
					data = frappe.get_list("Livestock Emission Factor Master List",
							fields=["manure_management", "excretion_rate", "typical_animal_mass","nitrogen_excretion","direct_n2o_n_emissions","managed_manure","managed_ivestock_manure","atmospheric_deposition"],
							filters={
							"category" : j.category
					})
					head = float(j.heads)
					nitrogen_excretion_rate = float(data[0].excretion_rate  )
					animal_mass = float(data[0].typical_animal_mass)
					nitrogen_excretion_managed = float(data[0].nitrogen_excretion)
					direct_n2o_n_emissions = float(data[0].direct_n2o_n_emissions)
					sum_n2o += eval(i.n2o)
				cumulative_co2=0
				cumulative_ch4=0
				cumulative_n2o=eval(i.cumulative_n2o)
				total_co2=eval(i.total_co2)
				
				for row in report_doc.report:
					if row.categories == '3.B.b. Direct N2O emissions per MMS (kt N2O)':
						row.set("n2o",cumulative_n2o)
						row.set("total_co2_eq",total_co2)


			if i.name == 'direct_managed_soils':
				
				sum_co2 = 0;sum_ch4 = 0;sum_n2o = 0;sum_total_co2 = 0
				for j in document.get(i.name):
					total_amount = float(j.total_amount)
					emission_factor = float(j.emission_factor)
					cumulative_co2=0
					cumulative_ch4=0
					cumulative_n2o=eval(i.cumulative_n2o)
					total_co2=eval(i.total_co2)
					for row in report_doc.report:
							if row.categories == j.anthropogenic_n_input and row.parent_categories == "3.D.1. Direct N2O emissions from managed soils":
								row.set("n2o",cumulative_n2o)
								row.set("total_co2_eq",total_co2)

			if i.name == 'atmospheric_deposit':
			
				sum_co2 = 0;sum_ch4 = 0;sum_n2o = 0;sum_total_co2 = 0
				
				amount_of_synthetic_n_fertilizers = float(document.get(i.name)[0].value)
				fraction_of_synthetic_n_fertilizers = float(document.get(i.name)[1].value )
				annual_amount_of_animal_manure = float(document.get(i.name)[2].value)
				annual_amount_of_urine = float(document.get(i.name)[3].value )
				fraction_of_applied_organic_n_fertilizer = float(document.get(i.name)[4].value)
				emission_factor_n2o = float(document.get(i.name)[5].value)
				
				cumulative_co2=0
				cumulative_ch4=0
				cumulative_n2o=eval(i.cumulative_n2o)
				total_co2=eval(i.total_co2)
				for row in report_doc.report:
						if row.categories == "3.D.2.a. From atmospheric deposition of N volatilized from managed soils from agricultural inputs of N":
							row.set("n2o",cumulative_n2o)
							row.set("total_co2_eq",total_co2)

			if i.name == 'n2o_from_n_leaching':
				
				sum_co2 = 0;sum_ch4 = 0;sum_n2o = 0;sum_total_co2 = 0
				
				annual_amount_of_synthetic_fertilizer = float(document.get(i.name)[0].value)
				annual_amoun_of_animal_manure = float(document.get(i.name)[1].value)
				annual_amount_of_urine = float(document.get(i.name)[2].value)
				amount_of_n_in_crop = float(document.get(i.name)[3].value)
				annual_amount_of_n_mineralized = float(document.get(i.name)[4].value)
				fraction_of_all_n_additions = float(document.get(i.name)[5].value)
				emission_factor_for_n20 = float(document.get(i.name)[6].value)
				
				
				n_leaching_cumulative_n2o=eval(i.cumulative_n2o)
				n_leaching_total_n2o=eval(i.total_co2)
				for row in report_doc.report:
						if row.categories == "3.D.2.b. From N leaching/runoff from managed soils":
							row.set("n2o",n_leaching_cumulative_n2o)
							row.set("total_co2_eq",n_leaching_total_n2o)

			if(i.name == "activity_data_burning"):
				
				sum_co2=0
				sum_ch4=0
				sum_n2o=0
				for j in document.get(i.name):
					amount = j.amount
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
					if row.categories == "3.E. Prescribed burning of savannahs":
						row.set("co2",cumulative_co2)
						row.set("ch4",cumulative_ch4)
						row.set("n2o",cumulative_n2o)
						row.set("total_co2_eq",total_co2)
				report_doc.save(ignore_permissions=True)
				frappe.db.commit()
			if(i.name == "activity_data_agriculture"):
				
				sum_co2=0
				sum_ch4=0
				sum_n2o=0
				for j in document.get(i.name):
					amount = j.amount
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
					if row.categories == "3.F. Field burning of agricultural residues":
						row.set("co2",cumulative_co2)
						row.set("ch4",cumulative_ch4)
						row.set("n2o",cumulative_n2o)
						row.set("total_co2_eq",total_co2)


			if(i.name == "urea_application"):
				
				sum_co2=0
				for j in document.get(i.name):
					amount_of_urea  = float(j.urea_applied)
					emission_factor_co2  = float(j.emission_factor)
					sum_co2 += eval(i.co2)
				cumulative_n2o=0
				cumulative_ch4=0
				cumulative_co2=eval(i.cumulative_co2)
				total_co2=eval(i.total_co2)
				
				for row in report_doc.report:
					if row.categories == "3.H. Urea Fertilization":
						row.set("co2",cumulative_co2)
						row.set("total_co2_eq",total_co2)

						
		a_co2=0;a_ch4=0;a_n2o=0;a_total=0
		category_co2=0;category_ch4=0;category_n2o=0;category_total=0
		sector_co2=0;sector_ch4=0;sector_n2o=0;sector_total=0
		sub_sector_co2=0;sub_sector_ch4=0;sub_sector_n2o=0;sub_sector_total=0
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
			if(row.parent_categories == document.sub_sector):
				sub_sector_co2 += float(row.co2)
				sub_sector_ch4 += float(row.ch4)
				sub_sector_n2o += float(row.n2o)
				sub_sector_total += float(row.total_co2_eq)
		for row in report_doc.report:
			if(row.categories == document.category  and row.categories != "3.E. Prescribed burning of savannahs" and row.categories != "3.A. Enteric fermentation" ):
				row.set("co2",category_co2)
				row.set("ch4",category_ch4)
				row.set("n2o",category_n2o)
				row.set("total_co2_eq",category_total)
			if(row.categories == document.sector):
				row.set("co2",sector_co2)
				row.set("ch4",sector_ch4)
				row.set("n2o",sector_n2o)
				row.set("total_co2_eq",sector_total)	
			if(row.categories == document.sub_sector):
				row.set("co2",sub_sector_co2)
				row.set("ch4",sub_sector_ch4)
				row.set("n2o",sub_sector_n2o)
				row.set("total_co2_eq",sub_sector_total)	

		for row in report_doc.report:
			if row.parent_categories == '3.B. Manure Management':
				a_co2 += row.co2
				a_ch4 += row.ch4
				a_n2o += row.n2o
				a_total += row.total_co2_eq

		for row in report_doc.report:
			if(row.categories == '3.B. Manure Management'):
				row.set("co2",a_co2)
				row.set("ch4",a_ch4)
				row.set("n2o",a_n2o)
				row.set("total_co2_eq",a_total)
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
		