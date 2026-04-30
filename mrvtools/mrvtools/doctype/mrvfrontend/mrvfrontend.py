# Copyright (c) 2023, NetZeroLabs and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document


class MrvFrontend(Document):
	pass

# @frappe.whitelist(allow_guest=True)
# def get_all():
# 	categories = frappe.db.sql("""SELECT * FROM tabSingles Where doctype='MrvFrontend';""",as_dict=1)
	
# 	return categories


@frappe.whitelist(allow_guest=True)
def get_all():
    # SECURITY: this endpoint is intentionally guest-readable — it serves the
    # SPA home page payload at /frontend/home for unauthenticated visitors.
    # Audited 2026-04-29: MrvFrontend is a Single doctype containing ONLY
    # public-facing homepage content (carousel images, about-section copy,
    # project/report image tiles, partner logos, public contact email +
    # phone numbers, knowledge-resource child tables). It has no Password
    # fields, no API keys, no PII, no internal config. The four child tables
    # surfaced below (knowledge_resource_details, knowledge_resource_details2,
    # climate_change_division_images, add_new_content) are likewise editorial
    # content. If a future PR adds a sensitive field to MrvFrontend, switch
    # this function to an explicit field allowlist instead of `as_dict()`.
    #
    # TODO(editorial-wiring): expose editorial home content to the SPA Home page.
    # Add the following child tables to the MrvFrontend doctype (schema change
    # requires editor review — do NOT modify mrvfrontend.json from code):
    #
    # editorial_programs (child table): num (Data), title (Data), metaTop (Data),
    #   metaBottom (Data), img (Attach Image), alt (Data)
    # editorial_stats (child table): num (Data), sup (Data), label (Data),
    #   sub (Data, optional), subSup (Data, optional)
    #
    # Once the fields exist, parent_doc.as_dict() will surface them under
    # parent_data.editorial_programs / parent_data.editorial_stats and
    # frontend/src/pages/Home.vue will swap its fallback arrays for live data.
    parent_doc = frappe.get_doc('MrvFrontend')
    parent_data = parent_doc.as_dict()
    
    child_table_data = []
    for child_record in parent_doc.get('knowledge_resource_details'):
        child_table_data.append(child_record.as_dict())

    child_table_data2 = []
    for child_record in parent_doc.get('knowledge_resource_details2'):
        child_table_data2.append(child_record.as_dict())
    CCDImages = []
    for child_record in parent_doc.get('climate_change_division_images'):
        CCDImages.append(child_record.as_dict())
    whatsNew = []
    for child_record in parent_doc.get('add_new_content'):
        if(child_record.hide != 1):
            whatsNew.append(child_record.as_dict())
    
    result = {
        'parent_data': parent_data,
        'child_table_data': child_table_data,
        'child_table_data2': child_table_data2,
        'CCDImages': CCDImages,
        'add_new_content': whatsNew[::-1],

    }

    return result


# @frappe.whitelist(allow_guest=True)
# def get_all():
# 	categories = frappe.db.get_single_value('MrvFrontend', 'heading')	
# 	return categories
