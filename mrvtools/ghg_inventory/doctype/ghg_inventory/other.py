import frappe
import json
# from frappe.model.document import Document

@frappe.whitelist()
def other_calculation(doc,doc_name,tablefields):

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
		for i in result:
			sum_co2=0
			sum_ch4=0
			sum_n2o=0
			gwp_methane = 0
			gwp_n2o = 0
			total_sector_co2 = 0
			total_sector_ch4 = 0
			total_sector_n2o = 0
			total_setcor_total = 0
			without_land_use_total = 0
			with_land_use_total = 0
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
			if i.name == "other_sector":
				for j in document.get(i.name):
					amount = j.amount_of_activity
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
						if row.categories == "6. Other":
							row.set("co2",cumulative_co2)
							row.set("ch4",cumulative_ch4)
							row.set("n2o",cumulative_n2o)
							row.set("total_co2_eq",total_co2)

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