// Copyright (c) 2023, tridotstech and contributors
// For license information, please see license.txt
/* eslint-disable */

frappe.query_reports["GHG Inventory Report Year Wise"] = {
	"filters": [
		{
			"fieldname": "from_year",
			"fieldtype": "Select",
			"label": __("From Year"),
			"options": [" ","1990","1991","1992","1993","1994","1995","1996","1997","1998","1999","2000","2001","2002","2003","2004","2005","2006","2007","2008","2009","2010","2011","2012","2013","2014","2015","2016","2017","2018","2019","2020","2021","2022","2023","2024","2025","2026","2027","2028","2029","2030","2031","2032","2033","2034","2035","2036","2037","2038","2039","2040","2041","2042","2043","2044","2045","2046","2047","2048","2049","2050"],
			change:function(){
				var data = $('[data-route="query-report/GHG Inventory Report Year Wise"] select[data-fieldname="from_year"]').val()
				frappe.query_report.filters[0].value = data

				frappe.query_report.filters[0].placeholder = data ? "" : "From Year"
				frappe.query_report.filters[0].refresh()
				// if (data != ""){
				// 	frappe.query_report.filters[0].placeholder = ""
				// 	frappe.query_report.filters[0].refresh()
				// }
				// else{
				// 	frappe.query_report.filters[0].placeholder = "From Year"
				// 	frappe.query_report.filters[0].refresh()
				// }
					
				var option = []
				for(let i = parseInt(data);i<=(parseInt(data)+10);i++){
					option.push(i)
				}

				
				var year_filter = frappe.query_report.get_filter('to_year');
				year_filter.df.options = option;
				// year_filter.df.default = r.message.split("\n")[0];
				year_filter.refresh();
				year_filter.set_input([""]);
				
			}
		},
		{
			"fieldname": "to_year",
			"fieldtype": "Select",
			"label": __("To Year"),	
			"options": [""]
		},
		{
			"fieldname": "inventory_unit",
			"fieldtype": "Select",
			"label": __("Inventory Unit"),
			"options": [" ","tCO2e","GgCO2e"]
		}
	]
};
