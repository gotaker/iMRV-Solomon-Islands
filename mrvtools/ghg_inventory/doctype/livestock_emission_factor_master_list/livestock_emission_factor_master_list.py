# Copyright (c) 2023, tridotstech and contributors
# For license information, please see license.txt


import frappe
from frappe.model.document import Document
from mrvtools.ghg_inventory.doctype.ghg_inventory.agriculture import agri_calculation

class LivestockEmissionFactorMasterList(Document):
	def on_update(self):
		tablefields=[]
		meta = frappe.get_meta("GHG Inventory")
		meta_dict = meta.as_dict()
		fields = meta_dict["fields"]
		for field in fields:
			if field["fieldtype"] == "Table":
				if field["fieldname"] not in ["ghg_inventory_details","edited_reference_approach","edited_electricity_generation","edited_manufacturing_industries","edited_transport","edited_other_sectors","edited_other_energy","edited_international_bunkers","edited_co2_emissions_from_biomass","edited_cement_production","edited_clinker_data","edited_lime_production","edited_chemical_industry","edited_lubricant_section","edited_lubricant_use","edited_section_break_shpf2","edited_other_ippu","edited_section_break_xabuv","edited_refrigeration","edited_foam_blowing_agents_section","edited_foam_blowing_agents","edited_fire_protection_section","edited_fire_protection","edited_aerosols_section","edited_aerosols","edited_solvents_section","edited_solvents","edited_other_applications_section","edited_other_applications","edited_section_break_jvzrb","edited_electrical_equipment","edited_sf6_and_pfcs_from_other_product_use_section","edited_sf6_and_pfcs_from_other_product_use","edited_n2o_from_product_uses_section","edited_n2o_from_product_uses","edited_other_section","edited_other_use","edited_section_break_7vpnb","edited_activity_data","edited_enteric_fermentation","edited_indirect_manure_management","edited_direct_emissions_mms","edited_direct_managed_soils","edited_atmospheric_deposit","edited_n2o_from_n_leaching","edited_activity_data_burning","edited_activity_data_agriculture","edited_urea_application","edited_forest_land","edited_cropland","edited_grassland","edited_wetlands","edited_settlements","edited_other_land","edited_harvested_wood_products","edited_biomass_burning","edited_solid_waste","edited_biological_treatment","edited_waste_incineration","edited_open_burning_of_waste","edited_ch4_wastewater_treatment","edited_n2o_wastewater_treatment","edited_industrial_wastewater_treatment","edited_other_wastewater_treatement","edited_other_waste","edited_other_sector"]:
					tablefields.append(field["fieldname"])

			if field["fieldname"] == "workflow_state":
				document_name = frappe.db.sql(f"""SELECT name,sector,workflow_state FROM `tabGHG Inventory`""",as_dict =1)
				doc = "GHG Inventory"
				for i in document_name:
					if i.workflow_state == "Approved":
						if i.sector == '3. Agriculture':
							doc_name = i.name
							docu= frappe.get_doc("GHG Inventory",i.name)
							frappe.enqueue(agri_calculation, doc=doc, doc_name=doc_name, tablefields=tablefields)
