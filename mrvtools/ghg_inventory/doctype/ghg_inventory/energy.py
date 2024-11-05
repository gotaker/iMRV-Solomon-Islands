import frappe
import json
# from frappe.model.document import Document

@frappe.whitelist()
def energy_calculation(doc,doc_name,tablefields):

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
		table_str = str(tablefields)
		table_str = table_str[1:-1]
		table_str = "(" + table_str + ")"
		query = f"""
			SELECT PT.co2, PT.ch4,PT.n2o,PT.cumulative_ch4,PT.cumulative_co2,PT.cumulative_n2o,PT.total_co2,CT.name,PT.net_consumption
			FROM `tabGHG Inventory Report Formulas` PT
			INNER JOIN `tabGHG Inventory TableName ChildTable` CT ON CT.parent = PT.name
			WHERE CT.name IN {table_str}
		"""
		result = frappe.db.sql(query, as_dict=True)
		gwp_methane = 0;gwp_n2o = 0
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
		# return result,tablefields
		for i in result:
			# return i
			q=[]
			sum_co2=0
			sum_ch4=0
			sum_n2o=0
			total_sector_co2 = 0
			total_sector_ch4 = 0
			total_sector_n2o = 0
			total_setcor_total = 0
			without_land_use_total = 0
			with_land_use_total = 0
			if(i.name == "reference_approach"):
				for j in document.get(i.name):

					data = frappe.get_list("Energy Fuel Master List",
							fields=["ncv", "co2_emission_factor", "ch4_emission_factor", "n2o_emission_factor"],
							filters={
							"fuel_type" : j.fuel_type,
							"fuel" : j.fuel
					})
					co2 = float(data[0].co2_emission_factor)
					ch4 = float(data[0].ch4_emission_factor)
					n2o = float(data[0].n2o_emission_factor)
					ncv = float(data[0].ncv)
					Production =j.production
					Imports =j.imports
					Exports =j.exports
					Bunker =j.international_bunkers
					Stock_change =j.stock_change
					Excluded =j.excluded_consumption
					quantity =eval(i.net_consumption)
					sum_co2 +=eval(i.co2)
					sum_ch4 +=eval(i.ch4)
					sum_n2o +=eval(i.n2o)
				cumulative_co2=eval(i.cumulative_co2)
				cumulative_ch4=eval(i.cumulative_ch4)
				cumulative_n2o=eval(i.cumulative_n2o)
				total_co2=eval(i.total_co2)
				for row in report_doc.report:
					if row.categories == "Energy (Reference Approach)":
						row.set("co2",cumulative_co2)
						row.set("ch4",cumulative_ch4)
						row.set("n2o",cumulative_n2o)
						row.set("total_co2_eq",total_co2)
				report_doc.save(ignore_permissions=True)
				frappe.db.commit() 
			if(i.name == "co2_emissions_from_biomass"):
				for j in document.get(i.name):
					Amount =float(j.amount_consumed)
					co2 = float(j.emission_factor__ton_co2)
					sum_co2 +=eval(i.co2)
				cumulative_co2=eval(i.cumulative_co2)
				for row in report_doc.report:
					if row.categories == document.sub_sector:
						row.set("co2",cumulative_co2)
						row.set("total_co2_eq",cumulative_co2)
				report_doc.save(ignore_permissions=True)
				frappe.db.commit()
			
			if(i.name in ["electricity_generation","transport","manufacturing_industries","other_sectors","international_bunkers","other_energy"]):
				sum_co2=0
				sum_ch4=0
				sum_n2o=0

				for j in document.get(i.name):
					data = frappe.get_list("Energy Fuel Master List",
							fields=["ncv", "co2_emission_factor", "ch4_emission_factor", "n2o_emission_factor"],
							filters={
							"fuel_type" : j.fuel_type,
							"fuel" : j.fuel
					})
					quantity = j.amount
					co2 = float(data[0].co2_emission_factor)
					ch4 = float(data[0].ch4_emission_factor)
					n2o = float(data[0].n2o_emission_factor)
					ncv = float(data[0].ncv)
					sum_co2 += eval(i.co2)
					sum_ch4 += eval(i.ch4)
					sum_n2o += eval(i.n2o)
				cumulative_co2=eval(i.cumulative_co2)
				cumulative_ch4=eval(i.cumulative_ch4)
				cumulative_n2o=eval(i.cumulative_n2o)
				total_co2=eval(i.total_co2)
				
				a_co2=0;a_ch4=0;a_n2o=0;a_total=0
				b_co2=0;b_ch4=0;b_n2o=0;b_total=0
				energy_co2=0;energy_ch4=0;energy_n2o=0;energy_total=0
				for row in report_doc.report:
					if row.categories == document.sub_category:	
						# return row.categories, document.sub_category
						row.set("co2",cumulative_co2)
						row.set("ch4",cumulative_ch4)
						row.set("n2o",cumulative_n2o)
						row.set("total_co2_eq",total_co2)
					if(row.parent_categories =="1.A.1.a. Public electricity and heat production"):
						energy_co2 += row.co2
						energy_ch4 += row.ch4
						energy_n2o += row.n2o
						energy_total += row.total_co2_eq

					if(row.parent_categories == "1.A.4.a. Commercial/institutional"):
						a_co2 += row.co2
						a_ch4 += row.ch4
						a_n2o += row.n2o
						a_total += row.total_co2_eq
					if(row.parent_categories == "1.A.4.b. Residential" ):
						b_co2 += row.co2
						b_ch4 += row.ch4
						b_n2o += row.n2o
						b_total += row.total_co2_eq

				for row in report_doc.report:
					if(row.categories == "1.A.1.a. Public electricity and heat production"):
						row.set("co2",energy_co2)
						row.set("ch4",energy_ch4)
						row.set("n2o",energy_n2o)
						row.set("total_co2_eq",energy_total)

					if(row.categories == "1.A.4.a. Commercial/institutional"):
						row.set("co2",a_co2)
						row.set("ch4",a_ch4)
						row.set("n2o",a_n2o)
						row.set("total_co2_eq",a_total)
					if(row.categories == "1.A.4.b. Residential"):
						row.set("co2",b_co2)
						row.set("ch4",b_ch4)
						row.set("n2o",b_n2o)
						row.set("total_co2_eq",b_total)
				# sub sector
				subsector_co2 =0
				subsector_ch4 =0
				subsector_n2o =0
				subsector_total=0
				for row in report_doc.report:
					if row.parent_categories == document.sub_sector:
						# yes.append(row)
						subsector_co2 += row.co2
						subsector_ch4 += row.ch4
						subsector_n2o += row.n2o
						subsector_total += row.total_co2_eq
						
				for row in report_doc.report:
					if row.categories != '1.A.5. Other':
						if(row.categories == document.sub_sector):
							row.set("co2",subsector_co2)
							row.set("ch4",subsector_ch4)
							row.set("n2o",subsector_n2o)
							row.set("total_co2_eq",subsector_total)
					if row.categories == "1.A.5. Other" and document.sub_sector == "1.A.5. Other":
						row.set("co2",cumulative_co2)
						row.set("ch4",cumulative_ch4)
						row.set("n2o",cumulative_n2o)
						row.set("total_co2_eq",total_co2)
				#category
				category_co2=0
				category_ch4=0
				category_n2o=0
				category_total=0
				for row in report_doc.report:
					if row.parent_categories != '1.D.1. International bunkers':
						if row.parent_categories == document.category:
							category_co2 += row.co2
							category_ch4 += row.ch4
							category_n2o += row.n2o
							category_total += row.total_co2_eq
				

				for row in report_doc.report:
					if row.categories != '1.D.1. International bunkers' and  document.sub_sector != '1.D.1. International bunkers':
						if(row.categories == document.category):
							row.set("co2",category_co2)
							row.set("ch4",category_ch4)
							row.set("n2o",category_n2o)
							row.set("total_co2_eq",category_total)
						
						if(row.categories == document.sector):
							row.set("co2",category_co2)    
							row.set("ch4",category_ch4)
							row.set("n2o",category_n2o)
							row.set("total_co2_eq",category_total)

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
		# return tablefields,table_str

			

				

			
