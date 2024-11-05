// Copyright (c) 2023, tridotstech and contributors
// For license information, please see license.txt

frappe.ui.form.on('GHG Inventory Master Report', {
	refresh: function(frm) {
		if(frm.doc.report == undefined){
			frappe.db.get_list('GHG Inventory Report Categories', {
				fields: ['category_name', 'indent','display_order','parent1','parent2'],
				limit:500,
				order_by:'display_order asc'
			}).then(records => {
				for (var record of records){
					let row = frm.add_child('report')
					row.categories= record.category_name
					row.indent= record.indent
					row.parent_categories= record.parent1
					row.parent_2_categories= record.parent2
				}
				frm.refresh_field('report');
			})
		}
	}
});
