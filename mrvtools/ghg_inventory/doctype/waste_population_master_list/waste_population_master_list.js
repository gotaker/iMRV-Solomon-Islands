// Copyright (c) 2023, tridotstech and contributors
// For license information, please see license.txt

frappe.ui.form.on('Waste Population Master List', {
	// refresh: function(frm) {

	// }
	before_save:function(frm){
		frm.doc.total_population = frm.doc.rural_population + frm.doc.urban_population
	}
});
