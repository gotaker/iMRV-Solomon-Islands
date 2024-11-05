// Copyright (c) 2023, tridotstech and contributors
// For license information, please see license.txt

frappe.ui.form.on('Mitigation Monitoring Information', {
	
	refresh: function(frm){

		$('[id="page-Mitigation Monitoring Information"]').find('.actions-btn-group').hide();
		setTimeout(function() {
			// $('[id="mitigation-monitoring-information-tab1-tab"]').click()
			$('[id="mitigation-monitoring-information-tab1"]').addClass("active show")
		})
		
		// $(document).ready(function(){
		// 	$('[data-fieldname]').on({
		// 		keyup:function(){
		// 			$('head').append('<style>[class="btn ellipsis btn-primary"] {display:none !important;}</style>')
		// 			$('.primary-action').removeClass('hide');
		// 			$('.primary-action').html("S<span class='alt-underline'>a</span>ve");
		// 			frm.dirty()
		// 		},
		// 		click:function(){
		// 			$('[data-fieldname]').on("focus",function(){
						
		// 				$('[data-fieldname]').on("click",function(){
		// 					$('head').append('<style>[class="btn ellipsis btn-primary"] {display:none !important;}</style>')
		// 					$('.primary-action').removeClass('hide')
		// 					$('.primary-action').html("S<span class='alt-underline'>a</span>ve")
		// 					frm.dirty()
		// 				})
		// 			})
		// 		},
				
		// 		change:function(){
		// 			$('[data-fieldtype = "Select"]').on("change",function(){
		// 				$('head').append('<style>[class="btn ellipsis btn-primary"] {display:none !important;}</style>')
		// 				$('.primary-action').removeClass('hide')
		// 				$('.primary-action').html("S<span class='alt-underline'>a</span>ve")
		// 				frm.dirty()
		// 			})
		// 		}
		// 	});

		// 	$('[class="btn btn-xs btn-secondary grid-add-row"], [data-fieldname="edit_button"]').on("click",function(){
		// 		$('head').append('<style>[class="btn ellipsis btn-primary"] {display:none !important;}</style>')
		// 		$('.primary-action').removeClass('hide')
		// 		$('.primary-action').html("S<span class='alt-underline'>a</span>ve")
		// 		frm.dirty()
		// 	})

		// 	$('[data-fieldtype="Table MultiSelect"]').on("mouseenter", function() {

		// 		$('[data-fieldtype="Table MultiSelect"]').on("focusout", function() {
		// 			var hide = true;
		// 			if(hide){
		// 			$('head').append('<style>.btn.ellipsis.btn-primary { display: none !important; }</style>');
		// 			$('.primary-action').removeClass('hide')
		// 			$('.primary-action').html("S<span class='alt-underline'>a</span>ve")
		// 			frm.dirty()
		// 			}
		// 			else{
		// 				$('head').append('<style>.btn.ellipsis.btn-primary { display:inline-block !important; }</style>');
		// 			}
		// 		});
				
	
				
		// 	});
		// });
		// 	$('head').append('<style>[class="btn ellipsis btn-primary"] {display:inline-block !important;}</style>')
	
		// 	$('[data-fieldtype="Int"]').on("focusout",function(){
		// 		$('head').append('<style>[class="btn ellipsis btn-primary"] {display:none !important;}</style>')
				
		// 	})
		// 	$('[data-fieldtype="Data"],[data-fieldtype="Small Text"]').on("keyup",function(){
		// 		$('head').append('<style>[class="btn ellipsis btn-primary"] {display:none !important;}</style>')
				
		// 	})
		// 	// $('[data-fieldtype="Link"]').on("click", function() {
		// 	// 			var hide = true;
		// 	// 			if(hide){
		// 	// 				$('head').append('<style>.btn.ellipsis.btn-primary { display: none !important; }</style>');
		// 	// 				$('.primary-action').removeClass('hide')
		// 	// 				$('.primary-action').html("S<span class='alt-underline'>a</span>ve")
		// 	// 				frm.dirty()
		// 	// 			}
						
		// 	// 		});	
	
		// 	$('[data-fieldtype="Attach"]').on("change",function(){
			
		// 		$('head').append('<style>[class="btn ellipsis btn-primary"] {display:none !important;}</style>')
		// 	})
		// 	$('[data-fieldname="performance_indicator"]').on("keyup",function(){
		// 		$('[data-fieldname="actual_monitored_value"],[data-fieldname="reference"]').on("focusout",function(){
		// 			$('head').append('<style>[class="btn ellipsis btn-primary"] {display:none !important;}</style>')
		// 	})
		// })
			
		// 	$('head').append('<style>[class="btn ellipsis btn-primary"] {display:inline-block !important;}</style>')
				// if (frm.doc.work_state == "" && frm.doc.workflow_state == "Pending" && frm.doc.project_id == ""){
				// 	window.location.href = `${frm.doc.name}`		
				// }
		
		
				

				// if(frm.doc.workflow_state == "Approved" || frm.doc.workflow_state == "Draft" || frm.doc.workflow_state == "Pending"){
				// 	$('[id="page-Mitigation Monitoring Information"]').find('.actions-btn-group').hide();
					
				// }else{
				// 	$('[id="page-Mitigation Monitoring Information"]').find('.actions-btn-group').show();
				// }
		
				if (frm.doc.work_state == "Approved"){
					cur_frm.fields_dict.project_id.df.read_only = 1
					cur_frm.fields_dict.select_approver.df.read_only = 1
				}
				
				if(frm.doc.work_state == "Rejected"){
					if (frm.doc.workflow_state == "Draft" && frm.doc.__unsaved == 1){
						frm.set_value("work_state","Rejected")
						frm.save()
					}
				}

				if(frm.doc.work_state == "Rejected"){
					if(frm.doc.workflow_state == "Pending" && frm.doc.__unsaved == 1){
						frm.set_value("work_state","Rejected")
						frm.save()
					}
				}
				
				
				// if(frm.doc.workflow_state == "Pending" && !frm.doc.__islocal){
				// 	frm.add_custom_button('Approve',()=>{
				// 		frappe.confirm('Are you sure you want to proceed?',
				// 			() => {
				// 				frm.set_value("workflow_state","Approved")
				// 				frm.refresh_field("workflow_state")
				// 				frm.save()
				// 			}, () => {
		
				// 		})
		
				// 	},"Actions")
		
				// 	frm.add_custom_button('Reject',()=>{
				// 		frappe.confirm('Are you sure you want to proceed?',
				// 			() => {
				// 				frm.set_value("workflow_state","Rejected")
				// 				frm.refresh_field("workflow_state")
				// 				frm.save()
				// 			}, () => {
		
				// 		})
		
				// 	},"Actions")
		
					
				// }
				// else if(frm.doc.workflow_state == "Approved" && !frm.doc.__islocal){
				// 	frm.add_custom_button('Edit',()=>{
				// 		frappe.confirm('Are you sure you want to proceed?',
				// 			() => {
				// 				frm.set_value("workflow_state","Draft")
				// 				frm.refresh_field("workflow_state")
				// 				frm.save()
				// 			}, () => {
			
				// 			})
			
				// 		},"Actions")
				// }
				// else if(frm.doc.workflow_state == "Draft" && !frm.doc.__islocal){
				// 	frm.add_custom_button('Send for Approval',()=>{
				// 		frappe.confirm('Are you sure you want to proceed?',
				// 			() => {
				// 				frm.set_value("workflow_state","Pending")
				// 				frm.refresh_field("workflow_state")
				// 				frm.save()
				// 			}, () => {
							
				// 		})
						
				// 	},"Actions")
				// }
				// else if(frm.doc.workflow_state == "Rejected" && !frm.doc.__islocal){
				// 	frm.add_custom_button('Edit',()=>{
				// 		frappe.confirm('Are you sure you want to proceed?',
				// 			() => {
				// 				frm.set_value("workflow_state","Draft")
				// 				frm.refresh_field("workflow_state")
				// 				frm.save()
				// 			}, () => {
			
				// 			})
			
				// 		},"Actions")
				// }
				// $('.inner-group-button button').removeClass("btn-default").addClass("btn-primary")





		// $('[data-fieldname="performance_indicator"] [class="grid-buttons"]').css("display","none")
		// $('head').append('<style>[id="page-Mitigation Monitoring Information"] div[data-fieldname="performance_indicator"] .grid-row .col:last-child {display:none !important;}</style>')
		// $('head').append('<style>[id="page-Mitigation Monitoring Information"] div[data-fieldname="performance_indicator"] .grid-row .col:first-child {display:none !important;}</style>')

		if(frm.doc.work_state =="Approved" && (frm.doc.workflow_state == "Draft" || frm.doc.workflow_state == "Pending" || frm.doc.workflow_state =="Rejected") && frm.doc.edited_performance_indicator.length != 0){
			frm.fields_dict.performance_indicator.df.read_only = 1
			frm.refresh_field("performance_indicator")
			frm.fields_dict.edit_button.df.hidden = 0
			frm.refresh_field("edit_button")
		}
		else{
			frm.fields_dict.performance_indicator.df.read_only = 0
			frm.refresh_field("performance_indicator")
			frm.fields_dict.edit_button.df.hidden = 1
			frm.refresh_field("edit_button")
		}


		if(frm.doc.monitoring_year && frm.doc.work_state == "Approved"){
			cur_frm.fields_dict.monitoring_year.df.options = frm.doc.monitoring_year
			cur_frm.fields_dict.monitoring_year.df.read_only = 1
		}

		if(frm.doc.project_id && frm.doc.work_state != "Approved"){
			frm.call({
				doc:cur_frm.doc,
				method:"get_years",
				async:false,
				args:{
					name:frm.doc.project_id
				},
				callback: function(r){
					var year_options=""
					for (var i of r.message){
						year_options += ('\n'+ i)
					}
					cur_frm.fields_dict.monitoring_year.df.options = year_options
					frm.refresh_field('monitoring_year')
				}
			})
		}

		frm.call({
		  doc:frm.doc,
		  method:'get_user',
		  async:false,
		  callback: function(r){
			var userList = []
			for (var i of r.message){
			  userList.push(i[0])
			}

			frm.set_query("select_approver",function(){
			  return {
				filters:{
				  email:['in',userList],
				  enabled:1
				}
			  }
			})
		  }
		})
		frm.set_query("project_id",function(){
			return{
				filters:{
					work_state:"Approved"
				}
			}
		})


		// if (frm.doc.workflow_state == "Rejected"){
		// 	frm.set_value("edited_project_details",[])
		// 	frm.set_value("edited_performance_indicator",[])
		// 	frm.set_value("actual_performance_indicator",[])

		// 	// frm.set_value("workflow_state","Approved")
		// 	// frm.set_value('work_state','Approved')
		// 	// frm.save()
		// }
		

		
		// if(frm.is_dirty()){
		// 	// $('[id="mitigation-monitoring-information-tab1"]').addClass("active")
		// 	$('[id="mitigation-monitoring-information-tab1-tab"]').addClass("active")
		// 	// $('[id="mitigation-monitoring-information-tab1-tab"]').attr('aria-selected', 'true');
		// 	$('[id="mitigation-monitoring-information-tab2-tab"]').removeClass("active")
		// 	// $('[id="mitigation-monitoring-information-tab2-tab"]').attr('aria-selected', 'false');
		// }
		
	},
	
	edit_button:function(frm){
		if(frm.doc.work_state =="Approved" && (frm.doc.workflow_state == "Draft" || frm.doc.workflow_state == "Pending" || frm.doc.workflow_state =="Rejected") && frm.doc.edited_performance_indicator.length != 0){
			frm.set_value("performance_indicator",[])
			for(var i of frm.doc.edited_performance_indicator){
				var child = frm.add_child("performance_indicator")
				child.performance_indicator = i.performance_indicator
				child.unit = i.unit
				child.expected_value = i.expected_value
				child.actual_monitored_value = i.actual_monitored_value
				child.reference = i.reference
			}
			frm.fields_dict.performance_indicator.df.read_only = 0
			frm.refresh_field("performance_indicator")
			frm.fields_dict.edit_button.df.hidden = 1
			frm.refresh_field("edit_button")
		}
	},

	before_save:function(frm){
		
		setTimeout(function() {
			$('[id="mitigation-monitoring-information-tab1-tab"]').click()
			$('[id="mitigation-monitoring-information-tab1"]').addClass("active show")
		})
		if (frm.doc.work_state == ''){
			if (frm.doc.workflow_state == "Pending") {
				frm.set_value("work_state","Pending")
			}
		}

		else if(frm.doc.work_state == "Pending"){
			if (frm.doc.workflow_state == "Rejected"){
				frm.set_value("work_state","Rejected")
			}
			else if(frm.doc.workflow_state == "Approved"){
				frm.set_value("work_state","Approved")
			}
		}

		else if(frm.doc.work_state == "Rejected"){
				
			if(frm.doc.workflow_state == "Approved"){
				frm.set_value("work_state","Approved")
			}
		}
		if (frm.doc.workflow_state == "Rejected" && frm.doc.work_state == "Approved"){
			frm.set_value("edited_project_details",[])
			frm.set_value("edited_performance_indicator",[])
			frm.set_value("actual_performance_indicator",[])
		}
		if(frm.doc.workflow_state == "Approved"){
			if (frm.doc.work_state == "Approved" && (frm.doc.edited_performance_indicator.length != 0 || frm.doc.edited_project_details.length != 0)){
				for (var i of frm.doc.edited_project_details){
						frm.set_value(i.field_name,i.new_values)
					}
					
					if(frm.doc.edited_performance_indicator.length != 0){
						frm.set_value("performance_indicator",[])
					for(var i of frm.doc.edited_performance_indicator){
						var child = frm.add_child("performance_indicator")
						child.performance_indicator = i.performance_indicator
						child.unit = i.unit
						child.expected_value = i.expected_value
						child.actual_monitored_value = i.actual_monitored_value
						child.reference = i.reference
					}
					frm.refresh_field("performance_indicator")
				}
				
				frm.refresh_field("edited_performance_indicator")
			}
			frm.set_value("edited_performance_indicator",[])
			frm.set_value("edited_project_details",[])
			frm.set_value("actual_performance_indicator",[])
			frm.set_value('work_state','Approved')
			// frm.save()
		}     


		if(frm.doc.work_state == "Approved"){
			if (frm.doc.workflow_state != "Approved"  && !frm.doc.__islocal){
				if(frm.fields_dict.performance_indicator.df.read_only == 0){
					frm.call({
						doc:frm.doc,
						method:"before_saving_table",
						async:false,
						callback:function(r){

						}
					})
				}

				frm.call({
					doc:frm.doc,
					method:"get_all_data",
					async:false,
					callback:function(r){
						var result= r.message

						var field_name_list = []
						for(let [key,value] of Object.entries(result)){
							field_name_list.push(key)
						}

						for (var i of frm.doc.edited_project_details){

							if (field_name_list.includes(i.field_name) ){
								i.new_values = frm.doc[`${i.field_name}`].toString()
								frm.set_value(i.field_name,i.old_values)
								frm.refresh_field("edited_project_details")

								const index = field_name_list.indexOf(i.field_name);
								const x = field_name_list.splice(index, 1)
							}
						}
						if (field_name_list){

							for (var i of field_name_list){
								var label = i.replaceAll("_"," ")
								label = toTitleCase(label)

								var child =frm.add_child("edited_project_details")


								child.field_label = label
								child.field_name = i
								child.old_values = result[`${i}`]
								child.new_values = frm.doc[`${i}`].toString()
								frm.set_value(i,result[`${i}`])

							}
						}
					}
				})

			}
		}
		setTimeout(function() {
			$('[id="mitigation-monitoring-information-tab1-tab"]').click()
			$('[id="mitigation-monitoring-information-tab1"]').addClass("active show")
		})
	},

	project_id: function(frm) {
		// frm.set_value("project_name","")
		// frm.set_value("contact_details","")
		// frm.set_value("other_contact_details","")
		// frm.set_value("lifetime","")
		// frm.set_value("status","")
		// frm.set_value("gender_inclusiveness_assessment","")
		// frm.set_value("market_based_mechanism","")
		// frm.set_value("project_impacts","")
		// frm.set_value("expected_project_output","")
		// frm.set_value("market_based_mechanism","")
		// frm.set_value("weblink","")
		// frm.set_value("beneficiaries","")


		// frm.call({
		// 	doc:cur_frm.doc,
		// 	method:"get_data",
		// 	async:false,
		// 	callback:function(r){
		// 		frm.set_value("project_name",r.message[0].project_id)
		// 		frm.set_value("contact_details",r.message[0].contact_details)
		// 		frm.set_value("other_contact_details",r.message[0].other_contact_details)
		// 		frm.set_value("lifetime",r.message[0].lifetime)
		// 		frm.set_value("status",r.message[0].status)
		// 		frm.set_value("gender_inclusiveness_assessment",r.message[0].gender_inclusiveness_assessment)
		// 		frm.set_value("market_based_mechanism",r.message[0].market_based_mechanism)
		// 		frm.set_value("project_impacts",r.message[0].project_impacts)
		// 		frm.set_value("expected_project_output",r.message[0].expected_project_output)
		// 		frm.set_value("weblink",r.message[0].weblink)
		// 		frm.set_value("beneficiaries",r.message[0].beneficiaries)
		// 	}
		// })
		// frm.call({
		// 	doc:cur_frm.doc,
		// 	method:"get_data",
		// 	async:false,
		// 	callback:function(r){
				
		// 		var values=[]
		// 		for(var i of r.message){
		// 			values.push(i)
		
		// 		}
		// 		values=values.join(",")
		// 		frm.set_value("included_in",values)
		// 	}
		// })
		if( frm.doc.project_id){
			frm.call({
				doc:cur_frm.doc,
				method:"get_value1",
				async:false,
				callback:function(r){

					var values=[]
					for(var i of r.message){
						values.push(i)
						
					}
					values=values.join(",")
					frm.set_value("non_ghg_mitigation_benefits",values)
				}
			})
			frm.call({
				doc:cur_frm.doc,
				method:"get_value2",
				async:false,
				callback:function(r){


					var values=[]
					for(var i of r.message){
						values.push(i)
						
					}
					values=values.join(",")
					frm.set_value("target_ghgs",values)
				}
			})
			frm.call({
				doc:cur_frm.doc,
				method:"get_child",
				async:false,
				callback:function(r){
					var col=r.message

					frm.set_value("performance_indicator",[])
					for (var i of col){
						var child=frm.add_child("performance_indicator")
						child.performance_indicator = i.performance_indicator
						child.unit = i.unit
						child.expected_value = i.expected_value
						frm.refresh_field("performance_indicator")
					}
				}
			})
			frm.call({
				doc:cur_frm.doc,
				method:"get_years",
				async:false,
				args:{
					name:frm.doc.project_id
				},
				callback: function(r){
					var year_options=""
					for (var i of r.message){
						year_options += ('\n'+ i)
					}
					cur_frm.fields_dict.monitoring_year.df.options = year_options
					frm.refresh_field('monitoring_year')
				}
			})
		}
	},

	monitoring_year:function(frm){
		frappe.db.get_list(frm.doc.doctype, {
			fields: ['monitoring_year'],
			filters:{'project_id':frm.doc.project_id},
			pluck:'monitoring_year',
			order_by: "monitoring_year asc",
		}).then(r => {

				if(frm.doc.project_id){
					if (r.includes(frm.doc.monitoring_year)){
						frm.set_value("monitoring_year","")
						frm.refresh_field("monitoring_year")
						
						var yearList =""
						for (var y of r){
							yearList += `<li> ${y} </li>`
						}
						// year = r.join(",")
						frappe.msgprint({title:("Already Exists"),message:(`<b>${frm.doc.project_id}</b> <b><ul>${yearList}</b></ul>`)})
					}
				}
		});
	}
});

function toTitleCase(str) {
	return str.replace(
	  /\w\S*/g,
	  function(txt) {
		return txt.charAt(0).toUpperCase() + txt.substr(1).toLowerCase();
	  }
	); 
}