// Copyright (c) 2023, tridotstech and contributors
// For license information, please see license.txt

frappe.ui.form.on('Adaptation Monitoring Information', {
	
	
	refresh: function(frm){
		$('[id="page-Adaptation Monitoring Information"]').find('.actions-btn-group').hide();
		setTimeout(function() {
			// $('[id="adaptation-monitoring-information-tab1-tab"]').click()
			$('[id="adaptation-monitoring-information-tab1"]').addClass("active show")

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
		// 	$('[data-fieldtype="Link"]').on("click", function() {
		// 		var hide = true;
		// 		if(hide){
		// 			$('head').append('<style>.btn.ellipsis.btn-primary { display: none !important; }</style>');
		// 			$('.primary-action').removeClass('hide')
		// 			$('.primary-action').html("S<span class='alt-underline'>a</span>ve")
		// 			frm.dirty()
		// 		}
		// 		else{
		// 			$('head').append('<style>.btn.ellipsis.btn-primary { display:inline-block !important; }</style>');
		// 		}
		// 	});	
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

	// 	$('.control-input').on("keyup",function(){
	// 		$('head').append('<style>[class="btn ellipsis btn-primary"] {display:none !important;}</style>')
			
	// 	})

	// 	$('.btn-default').on("click",function(){
	// 		$('head').append('<style>[class="btn ellipsis btn-primary"] {display:none !important;}</style>')
	// 	})
	
	// 	$('[data-fieldname="quantitative_impact"]').on("keyup",function(){
	// 		$('[data-fieldname="actual_value"]').on("focusout",function(){
	// 			$('head').append('<style>[class="btn ellipsis btn-primary"] {display:none !important;}</style>')
	// 	})
	// })
		
	// 	$('[class="btn btn-xs btn-secondary grid-add-row"]').on("click",function(){
	// 		$('head').append('<style>[class="btn ellipsis btn-primary"] {display:none !important;}</style>')
	// 	})
		
	// 	$('head').append('<style>[class="btn ellipsis btn-primary"] {display:inline-block !important;}</style>')

		// if(frm.doc.workflow_state == "Approved" || frm.doc.workflow_state == "Draft" || frm.doc.workflow_state == "Pending"){
		
		// 	$('[id="page-Adaptation Monitoring Information"]').find('.actions-btn-group').hide();

		// 	}else{
		// 		$('[id="page-Adaptation Monitoring Information"]').find('.actions-btn-group').show();
		// 	}
	
			if (frm.doc.work_state == "Approved"){
				cur_frm.fields_dict.project_id.df.read_only = 1
				cur_frm.fields_dict.select_approver.df.read_only = 1
			}
			
			// if (frm.doc.work_state == '' && !frm.doc.__islocal){
			// 	if (frm.doc.workflow_state == "Pending") {
			// 		frm.set_value("work_state","Pending")
			// 		frm.save()
			// 	}
			// }
			// else if(frm.doc.work_state == "Pending"){
			// 	if (frm.doc.workflow_state == "Rejected"){
			// 		frm.set_value("work_state","Rejected")
			// 		frm.save()
			// 	}
			// 	else if(frm.doc.workflow_state == "Approved"){
			// 		frm.set_value("work_state","Approved")
			// 		frm.save()
			// 	}
			// }
			// else if(frm.doc.work_state == "Rejected"){
			// 	if (frm.doc.workflow_state == "Draft"){
			// 		frm.set_value("work_state","Rejected")
			// 		frm.save()
			// 	}
			// 	else if(frm.doc.workflow_state == "Approved"){
			// 		// $('[id="adaptation-monitoring-information-tab1"]').attr("style","pointer-events:auto;")
			// 		frm.set_value("work_state","Approved")
			// 		frm.save()
			// 	}
			// 	else if(frm.doc.workflow_state == "Rejected"){
			// 		// $('[id="adaptation-monitoring-information-tab1"]').attr("style","pointer-events:none;color: #999; opacity: 0.7;")
			// 		frm.set_value("work_state","Rejected")
			// 		frm.save()
			// 	}
			// 	else if(frm.doc.workflow_state == "Pending"){
			// 		frm.set_value("work_state","Rejected")
			// 		frm.save()
			// 	}
			// }
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
			// else if(frm.doc.workflow_state == "Approved"  && !frm.doc.__islocal){
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
			// else if(frm.doc.workflow_state == "Rejected"  && !frm.doc.__islocal){
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




		if (frm.doc.workflow_state =="Draft" && frm.doc.__unsaved ==1 && frm.doc.work_state == "Approved"){
			frm.call({
				doc:frm.doc,
				method:"year_validation",
				async:false,
				callback:function(r){


				}
			})
		}
		
		if(frm.doc.work_state =="Approved" && (frm.doc.workflow_state == "Draft" || frm.doc.workflow_state == "Pending" || frm.doc.workflow_state =="Rejected") && frm.doc.edited_quantitative_impact.length != 0){
			frm.fields_dict.quantitative_impact.df.read_only = 1
			frm.fields_dict.edit_button.df.hidden = 0
			frm.refresh_field("edit_button")
			frm.refresh_field("quantitative_impact")
		}
		else{
			frm.fields_dict.quantitative_impact.df.read_only = 0
			frm.fields_dict.edit_button.df.hidden = 1
			frm.refresh_field("edit_button")
			frm.refresh_field("quantitative_impact")
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
		// 	// $("head").append(`<style>[id="project-tab2-tab"] {display: none !important}</style>`)
		// 	frm.set_value("edited_project_details",[])
		// 	frm.set_value("edited_quantitative_impact",[])
		// 	// frm.set_value("workflow_state","Approved")
		// 	frm.set_value("actual_performance_indicator",[])
		// 	// frm.set_value('work_state','Approved')
			
		// }
		// if(frm.doc.workflow_state == "Approved"){
		// 	if (frm.doc.workflow_state == "Approved"  && (frm.doc.edited_quantitative_impact.length != 0 || frm.doc.edited_project_details.length != 0)){
		// 		for (var i of frm.doc.edited_project_details){

		// 			frm.set_value(i.field_name,i.new_values)
		// 		}

		// 		frm.set_value('work_state','Approved')
		// 		if(frm.doc.edited_quantitative_impact.length){
		// 			frm.set_value("quantitative_impact",[])
		// 			for(var i of frm.doc.edited_quantitative_impact){
		// 				var row = frm.add_child("quantitative_impact")
		// 				row.category = i.category
		// 				row.question = i.question
		// 				row.expected_value = i.expected_value
		// 				row.actual_value = i.actual_value
		// 				row.data_source = i.data_source
		// 			}
		// 			frm.refresh_field("quantitative_impact")
		// 		}
		// 		frm.set_value("edited_project_details",[])
		// 		frm.set_value("edited_quantitative_impact",[])
		// 		frm.refresh_field("edited_quantitative_impact")
		// 	}
		// 	frm.set_value('work_state','Approved')
		// 	frm.set_value("actual_performance_indicator",[])
		// 	frm.save()
		// }

		
		

	},
	edit_button:function(frm){
		if(frm.doc.work_state =="Approved" && (frm.doc.workflow_state == "Draft" || frm.doc.workflow_state == "Pending" || frm.doc.workflow_state =="Rejected") && frm.doc.edited_quantitative_impact.length != 0){
			frm.set_value("quantitative_impact")
			for(var i of frm.doc.edited_quantitative_impact){
				var row = frm.add_child("quantitative_impact")
				row.category = i.category
				row.question = i.question
				row.expected_value = i.expected_value
				row.actual_value = i.actual_value
				row.data_source = i.data_source
			}
			frm.fields_dict.quantitative_impact.df.read_only = 0
			frm.refresh_field("quantitative_impact")
			frm.fields_dict.edit_button.df.hidden = 1
			frm.refresh_field("edit_button")
		}
	},

	before_save:function(frm){
		setTimeout(function() {
			$('[id="adaptation-monitoring-information-tab1-tab"]').click()
			$('[id="adaptation-monitoring-information-tab1"]').addClass("active show")

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
		if (frm.doc.workflow_state == "Rejected"){
			// $("head").append(`<style>[id="project-tab2-tab"] {display: none !important}</style>`)
			frm.set_value("edited_project_details",[])
			frm.set_value("edited_quantitative_impact",[])
			// frm.set_value("workflow_state","Approved")
			frm.set_value("actual_performance_indicator",[])
			// frm.set_value('work_state','Approved')
			
		}
		if(frm.doc.workflow_state == "Approved"){
			if (frm.doc.workflow_state == "Approved"  && (frm.doc.edited_quantitative_impact.length != 0 || frm.doc.edited_project_details.length != 0)){
				for (var i of frm.doc.edited_project_details){

					frm.set_value(i.field_name,i.new_values)
				}

				frm.set_value('work_state','Approved')
				if(frm.doc.edited_quantitative_impact.length){
					frm.set_value("quantitative_impact",[])
					for(var i of frm.doc.edited_quantitative_impact){
						var row = frm.add_child("quantitative_impact")
						row.category = i.category
						row.question = i.question
						row.expected_value = i.expected_value
						row.actual_value = i.actual_value
						row.data_source = i.data_source
					}
					frm.refresh_field("quantitative_impact")
				}
				frm.set_value("edited_project_details",[])
				frm.set_value("edited_quantitative_impact",[])
				frm.refresh_field("edited_quantitative_impact")
			}
			frm.set_value('work_state','Approved')
			frm.set_value("actual_performance_indicator",[])
			// frm.save()
		}
		if(frm.doc.work_state == "Approved"){
			if (frm.doc.workflow_state != "Approved"  && !frm.doc.__islocal){
				if(frm.fields_dict.quantitative_impact.df.read_only == 0){
					frm.call({
						doc:frm.doc,
						method:"before_saving_table",
						async:false,
						callback:function(r){

						}
					})
				}
				
				
			}
			
		}
		setTimeout(function() {
			$('[id="adaptation-monitoring-information-tab1-tab"]').click()
			$('[id="adaptation-monitoring-information-tab1"]').addClass("active show")

		})

	},


	project_id: function(frm) {
		if( frm.doc.project_id){
			frm.call({
				doc:cur_frm.doc,
				method:"get_json",
				async:false,
				callback:function(r){
					var json_field=JSON.parse(r.message).quantitative

					frm.set_value("json",JSON.stringify(json_field))
					frm.refresh_field("json")
					frm.set_value("quantitative_impact",[])
					for (var i of JSON.parse(frm.doc.json)){
						if (!i.expected_value == 0){
							var child=frm.add_child("quantitative_impact")
							child.category = i.category
							child.question = i.question
							child.expected_value = i.expected_value
						}
						frm.refresh_field("quantitative_impact")
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
