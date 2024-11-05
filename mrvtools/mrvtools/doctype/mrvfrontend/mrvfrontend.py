# Copyright (c) 2023, tridotstech and contributors
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
