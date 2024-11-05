# Copyright (c) 2023, tridotstech and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document

class GHGInventory(Document):

	@frappe.whitelist()
	def get_user(self):
		if self.sector == "1. Energy":
			doc = frappe.db.sql(f""" SELECT parent FROM `tabHas Role` WHERE role = 'Approver Energy'""")
			return doc
		elif self.sector == "2. Industrial processes and product use":
			doc = frappe.db.sql(f""" SELECT parent FROM `tabHas Role` WHERE role = 'Approver IPPU'""")
			return doc
		elif self.sector == "3. Agriculture":
			doc = frappe.db.sql(f""" SELECT parent FROM `tabHas Role` WHERE role = 'Approver Agriculture'""")
			return doc
		elif self.sector == "4. LAND USE, LAND-USE CHANGE AND FORESTRY":
			doc = frappe.db.sql(f""" SELECT parent FROM `tabHas Role` WHERE role = 'Approver Land Use'""")
			return doc
		elif self.sector == "5. Waste":
			doc = frappe.db.sql(f""" SELECT parent FROM `tabHas Role` WHERE role = 'Approver Waste'""")
			return doc
		elif self.sector == "6. Other":
			doc = frappe.db.sql(f""" SELECT parent FROM `tabHas Role` WHERE role = 'Approver Other'""")
			return doc
		


	@frappe.whitelist()
	def get_data(self,table_name):
		get_doc = frappe.db.sql(f"""SELECT * FROM `tabDirect and Indirect Managed Soils Master List` WHERE table_name = '{table_name}' """,as_dict=1,)
		return get_doc
	
	@frappe.whitelist()
	def get_livestock_details(self):
		get_doc = frappe.db.get_list("Livestock Population ChildTable",
				  filters={
					  'parent':self.year
				  },
				  fields=['category','heads'])
		# get_doc = frappe.db.sql(f"""SELECT category,heads FROM `tabLivestock Population ChildTable` WHERE parent = '{self.year}'""")
		return get_doc
	
	@frappe.whitelist()
	def get_all_data(self):
		old_doc =self.get_doc_before_save()
		field_list = {}
		meta = frappe.get_meta(self.doctype)
		meta_dict = meta.as_dict()
		fields = meta_dict["fields"]
		for field in fields:
			if frappe.db.exists(self.doctype,self.name):
				if field["fieldtype"] != "Date" and field["fieldtype"] != "Table MultiSelect" and field["fieldtype"] != "Table" and field["fieldtype"] != "Geolocation" and field["fieldtype"] != "JSON" and field["fieldtype"] != "HTML" and field["fieldtype"] != "Button" and field["fieldtype"] != "Check":
					repeated_list=["calculation_approach","was_uncertainty_analysis_performed","were_qa_or_qc_and_verification_procedures_implemented"]
					if field["fieldname"] in repeated_list:
						if old_doc.get(field["fieldname"]) != self.get(field["fieldname"]):
							field_list[field["fieldname"]] = str(old_doc.get(field["fieldname"]))
		return field_list
	

	@frappe.whitelist()
	def get_table(self):
		field_list = []
		meta = frappe.get_meta(self.doctype)
		meta_dict = meta.as_dict()
		fields = meta_dict["fields"]
		for field in fields:
			if field["fieldtype"] == "Table":
				if field["fieldname"] in  ["electricity_generation","transport","manufacturing_industries","other_sectors","other_energy","international_bunkers"]:
					field_list.append(field["fieldname"])
		return field_list


	@frappe.whitelist()
	def before_saving_table(self):
		old_doc =self.get_doc_before_save()
		meta = frappe.get_meta(self.doctype)
		meta_dict = meta.as_dict()
		fields = meta_dict["fields"]
		for field in fields:
			if field["fieldtype"] == "Table":
				if field["fieldname"] not in ["ghg_inventory_details","edited_reference_approach","edited_electricity_generation","edited_manufacturing_industries","edited_transport","edited_other_sectors","edited_other_energy","edited_international_bunkers","edited_co2_emissions_from_biomass","edited_cement_production","edited_clinker_data","edited_lime_production","edited_chemical_industry","edited_lubricant_section","edited_lubricant_use","edited_section_break_shpf2","edited_other_ippu","edited_section_break_xabuv","edited_refrigeration","edited_foam_blowing_agents_section","edited_foam_blowing_agents","edited_fire_protection_section","edited_fire_protection","edited_aerosols_section","edited_aerosols","edited_solvents_section","edited_solvents","edited_other_applications_section","edited_other_applications","edited_section_break_jvzrb","edited_electrical_equipment","edited_sf6_and_pfcs_from_other_product_use_section","edited_sf6_and_pfcs_from_other_product_use","edited_n2o_from_product_uses_section","edited_n2o_from_product_uses","edited_other_section","edited_other_use","edited_section_break_7vpnb","edited_activity_data","edited_enteric_fermentation","edited_indirect_manure_management","edited_direct_emissions_mms","edited_direct_managed_soils","edited_atmospheric_deposit","edited_n2o_from_n_leaching","edited_activity_data_burning","edited_activity_data_agriculture","edited_urea_application","edited_forest_land","edited_cropland","edited_grassland","edited_wetlands","edited_settlements","edited_other_land","edited_harvested_wood_products","edited_biomass_burning","edited_solid_waste","edited_biological_treatment","edited_waste_incineration","edited_open_burning_of_waste","edited_ch4_wastewater_treatment","edited_n2o_wastewater_treatment","edited_industrial_wastewater_treatment","edited_other_wastewater_treatement","edited_other_waste","edited_other_sector"]:
					if len(self.get(field["fieldname"])) != 0:
						meta1 = frappe.get_meta(field["options"])
						meta_dict2 = meta1.as_dict()
						fields1 = meta_dict2["fields"]
						counter1 = 0
						self.set("edited_"+ field["fieldname"],[])
						for i in fields1:
							if counter1 == 0:
								counter1 = 1
								for j in self.get(field["fieldname"]):
									row = self.append('edited_' + field["fieldname"],{})
									row.set(i["fieldname"], j.get(i["fieldname"]))
							else:
								for idx, j in enumerate(self.get(field["fieldname"])):
									row = self.get('edited_' + field["fieldname"])[idx]
									row.set(i["fieldname"], j.get(i["fieldname"]))

						counter2 = 0
						self.set(field["fieldname"],[])
						for i in fields1:	
							if counter2 == 0:
								counter2 = 1
								for j in old_doc.get(field["fieldname"]):
									row = self.append(field["fieldname"],{})
									row.set(i["fieldname"], j.get(i["fieldname"]))
							else:
								for idx, j in enumerate(old_doc.get(field["fieldname"])):
									row = self.get(field["fieldname"])[idx]
									row.set(i["fieldname"], j.get(i["fieldname"]))
					
		return "YES"


	@frappe.whitelist()
	def after_saving_table(self):
		old_doc =self.get_doc_before_save()
		meta = frappe.get_meta(self.doctype)
		meta_dict = meta.as_dict()
		fields = meta_dict["fields"]
		for field in fields:
			if field["fieldtype"] == "Table":
				if field["fieldname"] in ["edited_reference_approach","edited_electricity_generation","edited_manufacturing_industries","edited_transport","edited_other_sectors","edited_other_energy","edited_international_bunkers","edited_co2_emissions_from_biomass","edited_cement_production","edited_clinker_data","edited_lime_production","edited_chemical_industry","edited_lubricant_section","edited_lubricant_use","edited_section_break_shpf2","edited_other_ippu","edited_section_break_xabuv","edited_refrigeration","edited_foam_blowing_agents_section","edited_foam_blowing_agents","edited_fire_protection_section","edited_fire_protection","edited_aerosols_section","edited_aerosols","edited_solvents_section","edited_solvents","edited_other_applications_section","edited_other_applications","edited_section_break_jvzrb","edited_electrical_equipment","edited_sf6_and_pfcs_from_other_product_use_section","edited_sf6_and_pfcs_from_other_product_use","edited_n2o_from_product_uses_section","edited_n2o_from_product_uses","edited_other_section","edited_other_use","edited_section_break_7vpnb","edited_activity_data","edited_enteric_fermentation","edited_indirect_manure_management","edited_direct_emissions_mms","edited_direct_managed_soils","edited_atmospheric_deposit","edited_n2o_from_n_leaching","edited_activity_data_burning","edited_activity_data_agriculture","edited_urea_application","edited_forest_land","edited_cropland","edited_grassland","edited_wetlands","edited_settlements","edited_other_land","edited_harvested_wood_products","edited_biomass_burning","edited_solid_waste","edited_biological_treatment","edited_waste_incineration","edited_open_burning_of_waste","edited_ch4_wastewater_treatment","edited_n2o_wastewater_treatment","edited_industrial_wastewater_treatment","edited_other_wastewater_treatement","edited_other_waste","edited_other_sector"]:
					if len(self.get(field["fieldname"])) != 0:
						meta1 = frappe.get_meta(field["options"])
						meta_dict2 = meta1.as_dict()
						fields1 = meta_dict2["fields"]
						counter1 = 0
						field_name = field["fieldname"]
						parts = field_name.split("_")
						parts.pop(0)
						new_field_name = "_".join(parts)
						self.set(new_field_name,[])
						for i in fields1:
							if counter1 == 0:
								counter1 = 1
								for j in self.get(field["fieldname"]):
									row = self.append(new_field_name,{})
									row.set(i["fieldname"], j.get(i["fieldname"]))
							else:
								for idx, j in enumerate(self.get(field["fieldname"])):
									row = self.get(new_field_name)[idx]
									row.set(i["fieldname"], j.get(i["fieldname"]))

					
		
		return "YES"


	@frappe.whitelist()
	def edit_table(self):
		meta = frappe.get_meta(self.doctype)
		meta_dict = meta.as_dict()
		fields = meta_dict["fields"]
		for field in fields:
			if field["fieldtype"] == "Table":
				if field["fieldname"] in ["edited_reference_approach","edited_electricity_generation","edited_manufacturing_industries","edited_transport","edited_other_sectors","edited_other_energy","edited_international_bunkers","edited_co2_emissions_from_biomass","edited_cement_production","edited_clinker_data","edited_lime_production","edited_chemical_industry","edited_lubricant_section","edited_lubricant_use","edited_section_break_shpf2","edited_other_ippu","edited_section_break_xabuv","edited_refrigeration","edited_foam_blowing_agents_section","edited_foam_blowing_agents","edited_fire_protection_section","edited_fire_protection","edited_aerosols_section","edited_aerosols","edited_solvents_section","edited_solvents","edited_other_applications_section","edited_other_applications","edited_section_break_jvzrb","edited_electrical_equipment","edited_sf6_and_pfcs_from_other_product_use_section","edited_sf6_and_pfcs_from_other_product_use","edited_n2o_from_product_uses_section","edited_n2o_from_product_uses","edited_other_section","edited_other_use","edited_section_break_7vpnb","edited_activity_data","edited_enteric_fermentation","edited_indirect_manure_management","edited_direct_emissions_mms","edited_direct_managed_soils","edited_atmospheric_deposit","edited_n2o_from_n_leaching","edited_activity_data_burning","edited_activity_data_agriculture","edited_urea_application","edited_forest_land","edited_cropland","edited_grassland","edited_wetlands","edited_settlements","edited_other_land","edited_harvested_wood_products","edited_biomass_burning","edited_solid_waste","edited_biological_treatment","edited_waste_incineration","edited_open_burning_of_waste","edited_ch4_wastewater_treatment","edited_n2o_wastewater_treatment","edited_industrial_wastewater_treatment","edited_other_wastewater_treatement","edited_other_waste","edited_other_sector"]:
					if len(self.get(field["fieldname"])) != 0:
						meta1 = frappe.get_meta(field["options"])
						meta_dict2 = meta1.as_dict()
						fields1 = meta_dict2["fields"]
						counter1 = 0
						field_name = field["fieldname"]
						parts = field_name.split("_")
						parts.pop(0)
						new_field_name = "_".join(parts)
						self.set(new_field_name,[])
						for i in fields1:
							if counter1 == 0:
								counter1 = 1
								for j in self.get(field["fieldname"]):
									row = self.append(new_field_name,{})
									row.set(i["fieldname"], j.get(i["fieldname"]))
							else:
								for idx, j in enumerate(self.get(field["fieldname"])):
									row = self.get(new_field_name)[idx]
									row.set(i["fieldname"], j.get(i["fieldname"]))
		
		return "YES"
	

	@frappe.whitelist()
	def table_list(self):
		field_list=[]
		meta = frappe.get_meta(self.doctype)
		meta_dict = meta.as_dict()
		fields = meta_dict["fields"]
		for field in fields:
			if field["fieldtype"] == "Table":
				if field["fieldname"] in  ["edited_reference_approach","edited_electricity_generation","edited_manufacturing_industries","edited_transport","edited_other_sectors","edited_other_energy","edited_international_bunkers","edited_co2_emissions_from_biomass","edited_cement_production","edited_clinker_data","edited_lime_production","edited_chemical_industry","edited_lubricant_section","edited_lubricant_use","edited_section_break_shpf2","edited_other_ippu","edited_section_break_xabuv","edited_refrigeration","edited_foam_blowing_agents_section","edited_foam_blowing_agents","edited_fire_protection_section","edited_fire_protection","edited_aerosols_section","edited_aerosols","edited_solvents_section","edited_solvents","edited_other_applications_section","edited_other_applications","edited_section_break_jvzrb","edited_electrical_equipment","edited_sf6_and_pfcs_from_other_product_use_section","edited_sf6_and_pfcs_from_other_product_use","edited_n2o_from_product_uses_section","edited_n2o_from_product_uses","edited_other_section","edited_other_use","edited_section_break_7vpnb","edited_activity_data","edited_enteric_fermentation","edited_indirect_manure_management","edited_direct_emissions_mms","edited_direct_managed_soils","edited_atmospheric_deposit","edited_n2o_from_n_leaching","edited_activity_data_burning","edited_activity_data_agriculture","edited_urea_application","edited_forest_land","edited_cropland","edited_grassland","edited_wetlands","edited_settlements","edited_other_land","edited_harvested_wood_products","edited_biomass_burning","edited_solid_waste","edited_biological_treatment","edited_waste_incineration","edited_open_burning_of_waste","edited_ch4_wastewater_treatment","edited_n2o_wastewater_treatment","edited_industrial_wastewater_treatment","edited_other_wastewater_treatement","edited_other_waste","edited_other_sector"]:
					if len(self.get(field["fieldname"])) != 0:
						field_list.append(field["fieldname"])
		return field_list
	

	@frappe.whitelist()
	def table_name_list(self):
		field_list=[]
		meta = frappe.get_meta(self.doctype)
		meta_dict = meta.as_dict()
		fields = meta_dict["fields"]
		for field in fields:
			if field["fieldtype"] == "Table":
				if field["fieldname"] not in ["ghg_inventory_details","edited_reference_approach","edited_electricity_generation","edited_manufacturing_industries","edited_transport","edited_other_sectors","edited_other_energy","edited_international_bunkers","edited_co2_emissions_from_biomass","edited_cement_production","edited_clinker_data","edited_lime_production","edited_chemical_industry","edited_lubricant_section","edited_lubricant_use","edited_section_break_shpf2","edited_other_ippu","edited_section_break_xabuv","edited_refrigeration","edited_foam_blowing_agents_section","edited_foam_blowing_agents","edited_fire_protection_section","edited_fire_protection","edited_aerosols_section","edited_aerosols","edited_solvents_section","edited_solvents","edited_other_applications_section","edited_other_applications","edited_section_break_jvzrb","edited_electrical_equipment","edited_sf6_and_pfcs_from_other_product_use_section","edited_sf6_and_pfcs_from_other_product_use","edited_n2o_from_product_uses_section","edited_n2o_from_product_uses","edited_other_section","edited_other_use","edited_section_break_7vpnb","edited_activity_data","edited_enteric_fermentation","edited_indirect_manure_management","edited_direct_emissions_mms","edited_direct_managed_soils","edited_atmospheric_deposit","edited_n2o_from_n_leaching","edited_activity_data_burning","edited_activity_data_agriculture","edited_urea_application","edited_forest_land","edited_cropland","edited_grassland","edited_wetlands","edited_settlements","edited_other_land","edited_harvested_wood_products","edited_biomass_burning","edited_solid_waste","edited_biological_treatment","edited_waste_incineration","edited_open_burning_of_waste","edited_ch4_wastewater_treatment","edited_n2o_wastewater_treatment","edited_industrial_wastewater_treatment","edited_other_wastewater_treatement","edited_other_waste","edited_other_sector"]:
					if len(self.get(field["fieldname"])) != 0:
						field_list.append(field["fieldname"])
		return field_list


	@frappe.whitelist()
	def edited_table_list(self):
		field_dict = {}
		meta = frappe.get_meta(self.doctype)
		meta_dict = meta.as_dict()
		fields = meta_dict["fields"]
		for field in fields:
			if field["fieldtype"] == "Table":
				if field["fieldname"] in  ["edited_reference_approach","edited_electricity_generation","edited_manufacturing_industries","edited_transport","edited_other_sectors","edited_other_energy","edited_international_bunkers","edited_co2_emissions_from_biomass","edited_cement_production","edited_clinker_data","edited_lime_production","edited_chemical_industry","edited_lubricant_section","edited_lubricant_use","edited_section_break_shpf2","edited_other_ippu","edited_section_break_xabuv","edited_refrigeration","edited_foam_blowing_agents_section","edited_foam_blowing_agents","edited_fire_protection_section","edited_fire_protection","edited_aerosols_section","edited_aerosols","edited_solvents_section","edited_solvents","edited_other_applications_section","edited_other_applications","edited_section_break_jvzrb","edited_electrical_equipment","edited_sf6_and_pfcs_from_other_product_use_section","edited_sf6_and_pfcs_from_other_product_use","edited_n2o_from_product_uses_section","edited_n2o_from_product_uses","edited_other_section","edited_other_use","edited_section_break_7vpnb","edited_activity_data","edited_enteric_fermentation","edited_indirect_manure_management","edited_direct_emissions_mms","edited_direct_managed_soils","edited_atmospheric_deposit","edited_n2o_from_n_leaching","edited_activity_data_burning","edited_activity_data_agriculture","edited_urea_application","edited_forest_land","edited_cropland","edited_grassland","edited_wetlands","edited_settlements","edited_other_land","edited_harvested_wood_products","edited_biomass_burning","edited_solid_waste","edited_biological_treatment","edited_waste_incineration","edited_open_burning_of_waste","edited_ch4_wastewater_treatment","edited_n2o_wastewater_treatment","edited_industrial_wastewater_treatment","edited_other_wastewater_treatement","edited_other_waste","edited_other_sector"]:
						if len(self.get(field["fieldname"])) != 0:
							field_list = []
							meta1 = frappe.get_meta(field["options"])
							meta_dict2 = meta1.as_dict()
							fields1 = meta_dict2["fields"]
							for i in fields1:
								field_list.append(i["fieldname"])
							field_dict[field["fieldname"]] = field_list
		return field_dict




# @frappe.whitelist()
# def custom_sql_query(doc,doc_name,tablefields):
# 	pass
	