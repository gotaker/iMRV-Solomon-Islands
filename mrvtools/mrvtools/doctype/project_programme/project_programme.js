// Copyright (c) 2024, tridotstech and contributors
// For license information, please see license.txt
var sector_list = []
frappe.ui.form.on('Project Programme', {
	refresh:function(frm){
		if(frm.doc.__islocal){
			$('[title="New Project Programme"]').prop('innerText','New Programme')
		}
	},
	action_id: function(frm){
		frm.set_value("sector_affected",[])
		frm.refresh_field("sector_affected")
		frm.set_value("sub_sector_affected",[])
		frm.refresh_field("sub_sector_affected")
		// frappe.form.link_formatters['Project Programme'] = function(value, doc) {
		// 	if(doc && doc.action_name && doc.action_name !== value) {
		// 		return value + ': ' + doc.action_name;
		// 	} else {
		// 		return value;
		// 	}
		// }
	},
	focus: function(frm){
		if(frm.doc.focus != "Others"){
			cur_frm.fields_dict.sector_affected.get_query = function (frm) {
				return {
					filters: {
						objective: cur_frm.doc.focus,
					},
				}
			}
		}
		
	},
	sector_affected: function(frm) {
		sector_list = []
		for(let i of frm.doc.sector_affected){
			sector_list.push(i.sector)
		}
		cur_frm.fields_dict.sub_sector_affected.get_query = function (frm) {
			return {
				filters: {
					key_sector: ['in', sector_list],
				},
			}
		}
		frm.set_value("sub_sector_affected",[])
		frm.refresh_field("sub_sector_affected")
	},
});

