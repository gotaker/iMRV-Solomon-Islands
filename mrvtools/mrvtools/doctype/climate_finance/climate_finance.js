// Copyright (c) 2023, tridotstech and contributors
// For license information, please see license.txt

frappe.ui.form.on('Climate Finance', {

	refresh: function(frm){
		$('[id="page-Climate Finance"]').find('.actions-btn-group').hide();
		setTimeout(function() {
			// $('[id="climate-finance-tab_break_eii2f-tab"]').click()
			$('[id="climate-finance-tab_break_eii2f"]').addClass("active show")
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
	// 		$('head').append('<style>[class="btn ellipsis btn-primary"] {display:inline-block !important;}</style>')

	// 		$('[data-fieldtype="Select"]').on("change",function(){
				
	// 			$('head').append('<style>[class="btn ellipsis btn-primary"] {display:none !important;}</style>')
	// 		})
	// 		$('[data-fieldtype="Float"],[data-fieldtype="Int"]').on("focusout",function(){
	// 			$('head').append('<style>[class="btn ellipsis btn-primary"] {display:none !important;}</style>')
				
	// 		})
	// 		$('[data-fieldtype="Data"],[data-fieldtype="Small Text"],[data-fieldtype="Percentage"]').on("keyup",function(){
	// 			$('head').append('<style>[class="btn ellipsis btn-primary"] {display:none !important;}</style>')
				
	// 		})
	// 		$('[class="btn btn-xs btn-secondary grid-add-row"]').on("click",function(){
	// 			$('head').append('<style>[class="btn ellipsis btn-primary"] {display:none !important;}</style>')
	// 		})

	// 	$('.btn-default').on("click",function(){	
	// 		$('head').append('<style>[class="btn ellipsis btn-primary"] {display:none !important;}</style>')
	// 	})
	// 	$('[data-fieldname="sources_of_finance"]').on("keyup",function(){
	// 		$('[data-fieldname="national_international"],[data-fieldname="type"],[data-fieldname="amount"],[data-fieldname="channels"],[data-fieldname="country"],[data-fieldname="agency_name"]').on("focusout",function(){
	// 			$('head').append('<style>[class="btn ellipsis btn-primary"] {display:none !important;}</style>')
	// 	})
	// })
	// $('[data-fieldname="cost_breakdown"]').on("keyup",function(){
	// 	$('[data-fieldname="disbursement_category"],[data-fieldname="amount"],[data-fieldname="percentage"]').on("focusout",function(){
	// 		$('head').append('<style>[class="btn ellipsis btn-primary"] {display:none !important;}</style>')
	// })
	// })
	// $('[data-fieldname="budget_disbursement_schedule"]').on("keyup",function(){
	// 	$('[data-fieldname="financial_year"],[data-fieldname="amount"],[data-fieldname="percentage"]').on("focusout",function(){
	// 		$('head').append('<style>[class="btn ellipsis btn-primary"] {display:none !important;}</style>')
	// })
	// })	
	// 		$('head').append('<style>[class="btn ellipsis btn-primary"] {display:inline-block !important;}</style>')
	// if (frm.doc.__islocal == 1) {
	// 	$('head').append('<style>[class="btn ellipsis btn-primary"] {display:none !important;}</style>');
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
	
	// if (frm.doc.work_state == '' && !frm.doc.__islocal){
	// 	if (frm.doc.workflow_state == "Pending") {
	// 		frm.set_value("work_state","Pending")
	// 		frm.save()
	// 	}
	// // }
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
	// 		// $('[id="mitigations-tab1"]').attr("style","pointer-events:auto;")
	// 		frm.set_value("work_state","Approved")
	// 		frm.save()
	// 	}
	// 	else if(frm.doc.workflow_state == "Rejected"){
	// 		// $('[id="mitigations-tab1"]').attr("style","pointer-events:none;color: #999; opacity: 0.7;")
	// 		frm.set_value("work_state","Rejected")
	// 		frm.save()
	// 	}
	// 	else if(frm.doc.workflow_state == "Pending"){
	// 		frm.set_value("work_state","Rejected")
	// 		frm.save()
	// 	}
	// }

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


		// if (frm.doc.work_state == "Approved"){
		// 	cur_frm.fields_dict.project_id.df.read_only = 1
		// 	cur_frm.fields_dict.select_approver.df.read_only = 1
		// }

		if(frm.doc.work_state =="Approved" && (frm.doc.workflow_state == "Draft" || frm.doc.workflow_state == "Pending" || frm.doc.workflow_state =="Rejected") && frm.doc.edited_sources_of_finance.length != 0){
			frm.fields_dict.sources_of_finance.df.read_only = 1
			frm.refresh_field("sources_of_finance")
			frm.fields_dict.edit_button1.df.hidden = 0
			frm.refresh_field("edit_button1")
		}
		else{
			frm.fields_dict.sources_of_finance.df.read_only = 0
			frm.refresh_field("sources_of_finance")
			frm.fields_dict.edit_button1.df.hidden = 1
			frm.refresh_field("edit_button1")
		}
		if(frm.doc.work_state =="Approved" && (frm.doc.workflow_state == "Draft" || frm.doc.workflow_state == "Pending" || frm.doc.workflow_state =="Rejected") && frm.doc.edited_cost_breakdown.length != 0){
			frm.fields_dict.cost_breakdown.df.read_only = 1
			frm.refresh_field("cost_breakdown")
			frm.fields_dict.edit_button2.df.hidden = 0
			frm.refresh_field("edit_button2")
		}
		else{
			frm.fields_dict.cost_breakdown.df.read_only = 0
			frm.refresh_field("cost_breakdown")
			frm.fields_dict.edit_button2.df.hidden = 1
			frm.refresh_field("edit_button2")
		}
		if(frm.doc.work_state =="Approved" && (frm.doc.workflow_state == "Draft" || frm.doc.workflow_state == "Pending" || frm.doc.workflow_state =="Rejected") && frm.doc.edited_budget_disbursement_schedule.length != 0){
			frm.fields_dict.budget_disbursement_schedule.df.read_only = 1
			frm.refresh_field("budget_disbursement_schedule")
			frm.fields_dict.edit_button3.df.hidden = 0
			frm.refresh_field("edit_button3")
		}
		else{
			frm.fields_dict.budget_disbursement_schedule.df.read_only = 0
			frm.refresh_field("budget_disbursement_schedule")
			frm.fields_dict.edit_button3.df.hidden = 1
			frm.refresh_field("edit_button3")
		}

		frappe.db.get_list('Climate Finance', {
			fields: ['project_id'],
			pluck:'project_id'
		}).then(r => {
			frm.set_query("project_id",function(){

				return{
					filters:{
						work_state:"Approved",
						name:['not in',r]
					}
				}
			})
		})

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

		
		
		// if (frm.doc.workflow_state == "Approved" || frm.doc.__islocal){
		// 	$('[id="climate-finance-tab_break_eii2f-tab"]').addClass("active")
		// 	$('#climate-finance-tab_break_eii2f-tab').attr('aria-selected', 'true');
		// 	$('[id="climate-finance-tab_break_eii2f"]').addClass("active")
		// }
		

	},
	
	edit_button1:function(frm){
		if(frm.doc.work_state =="Approved" && (frm.doc.workflow_state == "Draft" || frm.doc.workflow_state == "Pending" || frm.doc.workflow_state =="Rejected") && frm.doc.edited_sources_of_finance.length != 0){
			frm.set_value("sources_of_finance")
			for(var i of frm.doc.edited_sources_of_finance){
				var row = frm.add_child("sources_of_finance")
				row.type = i.type
				row.national_international = i.national_international
				row.amount = i.amount
				row.channels = i.channels
				row.agency_name = i.agency_name
				row.country = i.country
			}
			frm.fields_dict.sources_of_finance.df.read_only = 0
			frm.refresh_field("sources_of_finance")
			frm.fields_dict.edit_button1.df.hidden = 1
			frm.refresh_field("edit_button1")
		}
	},
	edit_button2:function(frm){
		if(frm.doc.work_state =="Approved" && (frm.doc.workflow_state == "Draft" || frm.doc.workflow_state == "Pending" || frm.doc.workflow_state =="Rejected") && frm.doc.edited_cost_breakdown.length != 0){
			frm.set_value("cost_breakdown")
			for(var i of frm.doc.edited_cost_breakdown){
				var row = frm.add_child("cost_breakdown")
				row.disbursement_category = i.disbursement_category
				row.amount = i.amount
				row.percentage = i.percentage
			}
			frm.fields_dict.cost_breakdown.df.read_only = 0
			frm.refresh_field("cost_breakdown")
			frm.fields_dict.edit_button2.df.hidden = 1
			frm.refresh_field("edit_button2")
		}
	},
	edit_button3:function(frm){
		if(frm.doc.work_state =="Approved" && (frm.doc.workflow_state == "Draft" || frm.doc.workflow_state == "Pending" || frm.doc.workflow_state =="Rejected") && frm.doc.edited_budget_disbursement_schedule.length != 0){
			frm.set_value("budget_disbursement_schedule")
			for(var i of frm.doc.edited_budget_disbursement_schedule){
				var row = frm.add_child("budget_disbursement_schedule")
				row.financial_year = i.financial_year
				row.amount = i.amount
				row.percentage = i.percentage
			}
			frm.fields_dict.budget_disbursement_schedule.df.read_only = 0
			frm.refresh_field("budget_disbursement_schedule")
			frm.fields_dict.edit_button3.df.hidden = 1
			frm.refresh_field("edit_button3")
		}
	},

	before_save:function(frm){
		setTimeout(function() {
			$('[id="climate-finance-tab_break_eii2f-tab"]').click()
			$('[id="climate-finance-tab_break_eii2f"]').addClass("active show")
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
			frm.set_value("edited_project_details",[])
			frm.set_value("actual_sources_of_finance",[])
			frm.set_value("actual_cost_breakdown",[])
			frm.set_value("actual_budget_disbursement_schedule",[])
			frm.set_value("edited_sources_of_finance",[])
			frm.set_value("edited_cost_breakdown",[])
			frm.set_value("edited_budget_disbursement_schedule",[])
			// frm.set_value("workflow_state","Approved")
			// frm.set_value('work_state','Approved')
		}
		if ((frm.doc.workflow_state == "Approved")){
			for (var i of frm.doc.edited_project_details){
					frm.set_value(i.field_name,i.new_values)
			}
			if(frm.doc.edited_sources_of_finance.length != 0){
				frm.set_value("sources_of_finance",[])
				for(var i of frm.doc.edited_sources_of_finance){
					var row = frm.add_child("sources_of_finance")
					row.type = i.type
					row.national_international = i.national_international
					row.amount = i.amount
					row.channels = i.channels
					row.agency_name = i.agency_name
					row.country = i.country
				}
				frm.refresh_field("sources_of_finance")
			}
			if(frm.doc.edited_cost_breakdown.length != 0){
				frm.set_value("cost_breakdown",[])
				for(var i of frm.doc.edited_cost_breakdown){
					var row = frm.add_child("cost_breakdown")
					row.disbursement_category = i.disbursement_category
					row.amount = i.amount
					row.percentage = i.percentage
				}
				frm.refresh_field("cost_breakdown")
			}
			
			if(frm.doc.edited_budget_disbursement_schedule.length != 0){
				frm.set_value("budget_disbursement_schedule",[])
				for(var i of frm.doc.edited_budget_disbursement_schedule){
					var row = frm.add_child("budget_disbursement_schedule")
					row.financial_year = i.financial_year
					row.amount = i.amount
					row.percentage = i.percentage
				}
				frm.refresh_field("budget_disbursement_schedule")
			}
			frm.set_value("edited_project_details",[])
			frm.set_value('work_state','Approved')
			frm.set_value("actual_sources_of_finance",[])
			frm.set_value("actual_cost_breakdown",[])
			frm.set_value("actual_budget_disbursement_schedule",[])
			frm.set_value("edited_sources_of_finance",[])
			frm.set_value("edited_cost_breakdown",[])
			frm.set_value("edited_budget_disbursement_schedule",[])
			// frm.save()
		}
		

		if(frm.doc.work_state == "Approved"){
			if (frm.doc.workflow_state != "Approved"  && !frm.doc.__islocal){
				// if(frm.doc.actual_sources_of_finance.length == 0 ||frm.doc.actual_cost_breakdown.length == 0 || frm.doc.actual_budget_disbursement_schedule.length == 0   ){
				// 	// window.location.href = `${frm.doc.name}`
				// }
				if(frm.fields_dict.sources_of_finance.df.read_only == 0){
					frm.call({
						doc:frm.doc,
						method:"before_saving_table1",
						async:false,
						callback:function(r){
							
					

						}
					})
				}
			
				if(frm.fields_dict.cost_breakdown.df.read_only == 0){
					frm.call({
						doc:frm.doc,
						method:"before_saving_table2",
						async:false,
						callback:function(r){
							
					

						}
					})
				}
				
				if(frm.fields_dict.budget_disbursement_schedule.df.read_only == 0){
					frm.call({
						doc:frm.doc,
						method:"before_saving_table3",
						async:false,
						callback:function(r){
							
					

						}
					})
				}

				frm.call({
					doc:frm.doc,
					method:"get_all_datas",
					async:false,
					callback:function(r){
						var result= r.message

						var field_name_list = []
						for(let [key,value] of Object.entries(result)){
							field_name_list.push(key)
						}
						for (var i of frm.doc.edited_project_details){
							if (field_name_list.includes(i.field_name) ){
								if(["approval_date","expected_end_date","financial_closure_date","effectiveness_date"].includes(i.field_name)){
									i.new_values = frm.doc[`${i.field_name}`]
								}
								else{
									i.new_values = frm.doc[`${i.field_name}`].toString()
								}
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
									if(["approval_date","expected_end_date","financial_closure_date","effectiveness_date"].includes(i)){
										child.new_values = frm.doc[`${i}`]
									}
									else{
										child.new_values = frm.doc[`${i}`].toString()
									}
								frm.set_value(i,result[`${i}`])
							}
						}
					}
				})

			}
		}
		setTimeout(function() {
			$('[id="climate-finance-tab_break_eii2f-tab"]').click()
			$('[id="climate-finance-tab_break_eii2f"]').addClass("active show")
		})	 

	},
	project_id:function(frm){
		frappe.db.get_value('Project',`${frm.doc.project_id}`,'financial_closure_date').then(r =>
			{
			frm.set_value('financial_closure_date',r.message.financial_closure_date)
		})
		frm.refresh_field("budget_disbursement_schedule")
		},
	total_project_cost:function(frm){
		var others = frm.doc.total_project_cost - frm.doc.national_budget - frm.doc.sub_national_budget - frm.doc.green_bonds - frm.doc.total_sources_of_finance
		if(others >= 0){
			frm.set_value("others",others)
		}
		else{
			frappe.msgprint({ title:"Alert",message:`Others(USD) can't be Negative. Others = ${others}`})
			frm.set_value("others",others)
		}
		
	},

	national_budget:function(frm){
		var others = frm.doc.total_project_cost - frm.doc.national_budget - frm.doc.sub_national_budget - frm.doc.green_bonds - frm.doc.total_sources_of_finance
		if(others >= 0){
			frm.set_value("others",others)
		}
		else{
			frappe.msgprint({ title:"Alert",message:`Others(USD) can't be Negative. Others = ${others}`})
			frm.set_value("others",others)
		}
	},

	sub_national_budget:function(frm){
		var others = frm.doc.total_project_cost - frm.doc.national_budget - frm.doc.sub_national_budget - frm.doc.green_bonds - frm.doc.total_sources_of_finance
		if(others >= 0){
			frm.set_value("others",others)
		}
		else{
			frappe.msgprint({ title:"Alert",message:`Others(USD) can't be Negative. Others = ${others}`})
			frm.set_value("others",others)
		}
	},

	green_bonds:function(frm){
		var others = frm.doc.total_project_cost - frm.doc.national_budget - frm.doc.sub_national_budget - frm.doc.green_bonds - frm.doc.total_sources_of_finance
		if(others >= 0){
			frm.set_value("others",others)
		}
		else{
			frappe.msgprint({ title:"Alert",message:`Others(USD) can't be Negative. Others = ${others}`})
			frm.set_value("others",others)
		}
	},
	
	total_sources_of_finance:function(frm){
		var others = frm.doc.total_project_cost - frm.doc.national_budget - frm.doc.sub_national_budget - frm.doc.green_bonds - frm.doc.total_sources_of_finance
		if(others >= 0){
			frm.set_value("others",others)
		}
		else{
			frappe.msgprint({ title:"Alert",message:`Others(USD) can't be Negative. Others = ${others}`})
			frm.set_value("others",others)
		}
	},

	// financial_closure_date:function(frm){
	// 	// frm.call({
	// 	// 	doc:cur_frm.doc,
	// 	// 	method:"get_years",
	// 	// 	async:false,
	// 	// 	callback: function(r){
	
	// 	// 		var year_options=""
	// 	// 		for (var i of r.message){
	// 	// 			year_options += ('\n'+ i)
	// 	// 		}
	// 	// 		frm.fields_dict.budget_disbursement_schedule.grid.update_docfield_property("financial_year","options",year_options);
	// 	// 		frm.refresh_field('budget_disbursement_schedule')
	
	// 	// 	}
	// 	// })
	// }
});


frappe.ui.form.on('Sources of Climate Finance ChildTable',{
	amount:function(frm,cdt,cdn){
		var child = locals[cdt][cdn];
		var total=0;
		for(var i in frm.doc.sources_of_finance){
			total += parseFloat(frm.doc.sources_of_finance[i].amount);	
		}
		
		frm.set_value('total_sources_of_finance',total);
		refresh_field('total_sources_of_finance')
	},
	sources_of_finance_remove:function(frm){
		var total=0;
		for(var i in frm.doc.sources_of_finance){
			total += parseFloat(frm.doc.sources_of_finance[i].amount);	
		}
		
		frm.set_value('total_sources_of_finance',total);
		refresh_field('total_sources_of_finance')
	},
	// sources_of_finance_add:function(frm){
	// 	var others = frm.doc.total_project_cost - frm.doc.national_budget - frm.doc.sub_national_budget - frm.doc.green_bonds
	// 	if(!frm.doc.total_project_cost == 0){
	// 		if(others >= 0){
	// 			frm.set_value("others",others)
	// 		}
	// 		else{
	// 			frappe.msgprint({ title:"Alert",message:`Others(USD) can't be Negative. Others = ${others}`})
	// 			frm.set_value("others",0)
	// 		}
			
			
	// 	}
	// 	frm.set_value("total_rows_sources_of_finance",frm.doc.sources_of_finance.length)
		
	// },
	// sources_of_finance_remove:function(frm){
	// 	var others = frm.doc.total_project_cost - frm.doc.national_budget - frm.doc.sub_national_budget - frm.doc.green_bonds
	// 	if(!frm.doc.total_project_cost == 0){
	// 		if(others >= 0){
	// 			frm.set_value("others",others)
	// 		}
	// 		else{
	// 			frappe.msgprint({ title:"Alert",message:`Others(USD) can't be Negative. Others = ${others}`})
	// 			frm.set_value("others",0)
	// 		}
			
			
	// 	}
		// frm.set_value("total_rows_sources_of_finance",frm.doc.sources_of_finance.length)
	// },
});


frappe.ui.form.on('Climate Finance detailed Budget ChildTable',{
	amount:function(frm,cdt,cdn){
		var child = locals[cdt][cdn];
		frappe.model.set_value(cdt, cdn, "percentage",  ((child.amount / frm.doc.total_project_cost)*100).toFixed(2));
		refresh_field('percentage')
		var total=0;
		for(var i in frm.doc.cost_breakdown){
			total += parseFloat(frm.doc.cost_breakdown[i].amount);	
		}
		
		frm.set_value('total_amount_of_cost_breakdown',total);
		refresh_field('total_amount_of_cost_breakdown')
		frm.set_value('total_percentage_of_cost_breakdown', ((frm.doc.total_amount_of_cost_breakdown / frm.doc.total_project_cost)*100))
		refresh_field('total_percentage_of_cost_breakdown')
	},
	cost_breakdown_remove:function(frm){
		var total=0;
		for(var i in frm.doc.cost_breakdown){
			total += parseFloat(frm.doc.cost_breakdown[i].amount);	
		}
		
		frm.set_value('total_amount_of_cost_breakdown',total);
		refresh_field('total_amount_of_cost_breakdown')
		frm.set_value('total_percentage_of_cost_breakdown', ((frm.doc.total_amount_of_cost_breakdown / frm.doc.total_project_cost)*100))
		refresh_field('total_percentage_of_cost_breakdown')
	},
	disbursement_category:function(frm,cdt,cdn){
		var category_list=[]
		for(var i of frm.doc.cost_breakdown){
			category_list.push(i.disbursement_category)
		}
		frm.set_query("disbursement_category","cost_breakdown",function(){
			return {
				filters:{
				"disbursement_category":["not in",category_list]
				}
			}
		})
		frm.refresh_fields("disbursement_category")
	},
	cost_breakdown_add:function(frm){
		var category_list=[]
		for(var i of frm.doc.cost_breakdown){
			category_list.push(i.disbursement_category)
		}
		frm.set_query("disbursement_category","cost_breakdown",function(){
			return {
				filters:{
				"disbursement_category":["not in",category_list]
				}
			}
		})
		frm.refresh_fields("disbursement_category")
	}
});


frappe.ui.form.on('Climate Finance Disbursement Schedule ChildTable',{
	budget_disbursement_schedule_add:function(frm,cdt,cdn){
		// var child = locals[cdt][cdn]
		var yearList = []
		for (var i of frm.doc.budget_disbursement_schedule){
			if(i.financial_year != undefined){
				yearList.push(i.financial_year)
			}
		}

		frm.call({
			doc:cur_frm.doc,
			method:"get_years",
			async:false,
			callback: function(r){
				
				var year_options=""
				for (var i of r.message){
					if(!yearList.includes(i)){
						year_options += ('\n'+ i)
					}
				}
				frm.fields_dict.budget_disbursement_schedule.grid.update_docfield_property("financial_year","options",year_options);
				frm.refresh_field('budget_disbursement_schedule')
				
			}
		})
	},
	amount:function(frm,cdt,cdn){
		var child = locals[cdt][cdn];
		frappe.model.set_value(cdt, cdn, "percentage",  ((child.amount / frm.doc.total_project_cost)*100).toFixed(2));
		refresh_field('percentage')
		var total=0;
		for(var i in frm.doc.budget_disbursement_schedule){
			total += parseFloat(frm.doc.budget_disbursement_schedule[i].amount);	
		}
		
		frm.set_value('total_amount_of_budget_disbursement_schedule',total);
		refresh_field('total_amount_of_budget_disbursement_schedule')
		frm.set_value('total_percentage_of_budget_disbursement_schedule', ((frm.doc.total_amount_of_budget_disbursement_schedule / frm.doc.total_project_cost)*100))
		refresh_field('total_percentage_of_budget_disbursement_schedule')
	},
	budget_disbursement_schedule_remove:function(frm){
		var total=0;
		for(var i in frm.doc.budget_disbursement_schedule){
			total += parseFloat(frm.doc.budget_disbursement_schedule[i].amount);	
		}
		
		frm.set_value('total_amount_of_budget_disbursement_schedule',total);
		refresh_field('total_amount_of_budget_disbursement_schedule')
		frm.set_value('total_percentage_of_budget_disbursement_schedule', ((frm.doc.total_amount_of_budget_disbursement_schedule / frm.doc.total_project_cost)*100))
		refresh_field('total_percentage_of_budget_disbursement_schedule')
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