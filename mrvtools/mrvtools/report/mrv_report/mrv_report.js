// Copyright (c) 2023, tridotstech and contributors
// For license information, please see license.txt
/* eslint-disable */

frappe.query_reports["MRV Report"] = {
	"filters": [
		{
			"fieldname": "project",
			"fieldtype": "Link",
			"label": __("Project ID"),
			"options":"Project"
		},
		{
			"fieldname": "report",
			"fieldtype": "Select",
			"label": __("Report"),
			"options":["","Project Details","Mitigation Summary","Adaptation Summary","Finance Summary","SDG Summary"]
		}
	]
};
