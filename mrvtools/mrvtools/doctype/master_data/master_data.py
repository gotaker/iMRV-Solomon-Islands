# Copyright (c) 2023, tridotstech and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document

class MasterData(Document):
	@frappe.whitelist()
	def getMasterValues(self):
		masterValues = frappe.db.get_all("Master Data Test",
			  fields = ["module","table","sdg_mapping","impact_area","indicator"])
		# masterValues = [
		# 	{'module': 'SDG', 'table': 'Quantitative', 'impact_area': 'Poverty Reduction', 'indicator': 'Additional gender-sensitive policy frameworks at regional and national level to accelerate investment in poverty reduction:'}, 
		# 	{'module': 'SDG', 'table': 'Quantitative', 'impact_area': 'Poverty Reduction', 'indicator': 'Additional resources to implement programmes and policies for poverty reduction:'}, 
		# 	{'module': 'SDG', 'table': 'Quantitative', 'impact_area': 'Poverty Reduction', 'indicator': 'Additional number of people with social security:'}, 
		# 	{'module': 'SDG', 'table': 'Quantitative', 'impact_area': 'Poverty Reduction', 'indicator': 'Additional number of people living on more than $1.25 per day:'}, 
		# 	{'module': 'SDG', 'table': 'Qualitative', 'impact_area': 'Poverty Reduction', 'indicator': 'Does the action lead to increased spending by the national government into sectors that accelerate poverty eradication?'}, 
		# 	{'module': 'SDG', 'table': 'Qualitative', 'impact_area': 'Poverty Reduction', 'indicator': 'Does the action contribute to building resilience and reducing vulnerability against climate events and resulting social, economic and environmental impacts in the country/ community?'}, 
		# 	{'module': 'SDG', 'table': 'Qualitative', 'impact_area': 'Poverty Reduction', 'indicator': 'Does the action contribute to bringing access to basic services to the vulnerable sections of the country/society?'}, 
		# 	{'module': 'SDG', 'table': 'Qualitative', 'impact_area': 'Poverty Reduction', 'indicator': 'Does the action contribute to reducing poverty levels in the country/community?'}]
		
		return masterValues