// Copyright (c) 2023, tridotstech and contributors
// For license information, please see license.txt

frappe.ui.form.on('Mitigations', {
	
	project_id: function(frm) {
		if(!frm.doc.included_in && frm.doc.project_id){
			frm.call({
				doc:cur_frm.doc,
				method:"get_data",
				async:false,
				callback:function(r){
					var values=[]
					for(var i of r.message){
						values.push(i)
						
					}
					values=values.join(",")
					
					frm.set_value("included_in",values)
					frm.refresh_field('included_in')
				}
			})
		}
		
	},

	
	edit_button:function(frm){
		if(frm.doc.work_state =="Approved" && (frm.doc.workflow_state == "Draft" || frm.doc.workflow_state == "Pending" || frm.doc.workflow_state =="Rejected") && frm.doc.edited_performance_indicator.length != 0){
			frm.set_value("performance_indicator")
			for(var i of frm.doc.edited_performance_indicator){
				var child = frm.add_child("performance_indicator")
				child.performance_indicator = i.performance_indicator
				child.unit = i.unit
				child.expected_value = i.expected_value
				child.reference = i.reference
			}
			frm.fields_dict.performance_indicator.df.read_only = 0
			frm.fields_dict.edit_button.df.hidden = 1
			frm.refresh_field("edit_button")
			frm.refresh_field("performance_indicator")
		}
	},
	// observeDoc(frm){
	// 	var targetNode = document.querySelector('.indicator-pill');
		
	// 		// Options for the observer (which mutations to observe)
	// 		var config = { attributes: true, attributeFilter: ['class'] };
		
	// 		// Callback function to execute when mutations are observed
	// 		var callback = function(mutationsList, observer) {
	// 			for(var mutation of mutationsList) {
	// 				if (mutation.type === 'attributes') {
	// 					if (targetNode.innerText == "Not Saved") {
	// 						frm.clear_custom_buttons();
	// 					}
	// 				}
	// 			}
	// 		};
		
	// 		// Create an observer instance linked to the callback function
	// 		var observer = new MutationObserver(callback);
		
	// 		// Start observing the target node for configured mutations
	// 		observer.observe(targetNode, config);
	// },
	// onload_post_render(frm){
	// 	frm.trigger("observeDoc")
	// },
	
	refresh: function(frm){
		

		
		setTimeout(function() {
			$('[id="mitigations-tab1"]').addClass("active show")
		})	
		///////////////////////////////////
		
	

		
		

					// if(frm.doc.workflow_state == "Approved" || frm.doc.workflow_state == "Draft" || frm.doc.workflow_state == "Pending"){
					// 	$('[id="page-Mitigations"]').find('.actions-btn-group').hide();
						
					// }else{
					// 	$('[id="page-Mitigations"]').find('.actions-btn-group').show();
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


		if(frm.doc.work_state =="Approved" && (frm.doc.workflow_state == "Draft" || frm.doc.workflow_state == "Pending" || frm.doc.workflow_state =="Rejected") && frm.doc.edited_performance_indicator.length != 0){
			frm.fields_dict.performance_indicator.df.read_only = 1
			frm.fields_dict.edit_button.df.hidden = 0
			frm.refresh_field("edit_button")
			frm.refresh_field("performance_indicator")
		}
		else{
			frm.fields_dict.performance_indicator.df.read_only = 0
			frm.fields_dict.edit_button.df.hidden = 1
			frm.refresh_field("edit_button")
			frm.refresh_field("performance_indicator")
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
		
		frappe.db.get_list('Mitigations', {
			fields: ['project_id'],
			pluck:'project_id'
		}).then(r => {
			frm.set_query("project_id",function(){

				return{
					filters:{
						objective: ['in',['Cross-Cutting','Mitigation']],
						work_state:"Approved",
						name:['not in',r]
					}
				}
			})
		});













		
		// if(frm.doc.workflow_state == "Approved"){
		// 	if (frm.doc.workflow_state == "Approved"  && (frm.doc.edited_performance_indicator.length != 0 || frm.doc.edited_project_details.length != 0)){
		// 		for (var i of frm.doc.edited_project_details){

		// 			if(i.field_name != "non_ghg_mitigation_benefits" && i.field_name != "target_ghgs"){
		// 				frm.set_value(i.field_name,i.new_values)
		// 			}
					
		// 			else if(i.field_name == "non_ghg_mitigation_benefits"){

		// 				var new_list = i.new_values.split(",")

		// 				frm.clear_table("non_ghg_mitigation_benefits")
		// 				for (var value of new_list){
		// 					var row = frm.add_child("non_ghg_mitigation_benefits")
		// 					row.non_ghg_mitigation_benefits = value



		// 				}
		// 			}

		// 			else if(i.field_name == "target_ghgs"){

		// 				var new_list = i.new_values.split(",")

		// 				frm.clear_table("target_ghgs")
		// 				for (var value of new_list){
		// 					var row = frm.add_child("target_ghgs")
		// 					row.target_ghgs = value



		// 				}
		// 			}
					
		// 		}

		// 		if(frm.doc.edited_performance_indicator.length != 0){
		// 			frm.set_value("performance_indicator",[])
		// 			for(var i of frm.doc.edited_performance_indicator){
		// 				var child = frm.add_child("performance_indicator")
		// 				child.performance_indicator = i.performance_indicator
		// 				child.unit = i.unit
		// 				child.expected_value = i.expected_value
		// 				child.reference = i.reference
		// 			}
					
		// 			frm.refresh_field("performance_indicator")
		// 		}
		// 		frm.set_value("edited_project_details",[])
		// 		frm.set_value("edited_performance_indicator",[])
		// 		frm.refresh_field("edited_performance_indicator")
		// 	}
		// 	frm.set_value("original_performance_indicator",[])
		// 	frm.set_value('work_state','Approved')
		// 	if(frm.is_dirty()){
		// 		frm.save()
		// 	}
		// 	// frm.save()
		// }

		
	},




	before_save:function(frm){
		setTimeout(function() {
			$('[id="mitigations-tab1-tab"]').click()
			$('[id="mitigations-tab1"]').addClass("active show")
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
			frm.set_value("original_performance_indicator",[])
		}

		if(frm.doc.workflow_state == "Approved"){ 
			if (frm.doc.work_state == "Approved"  && (frm.doc.edited_performance_indicator.length != 0 || frm.doc.edited_project_details.length != 0)){
				for (var i of frm.doc.edited_project_details){

					if(i.field_name != "non_ghg_mitigation_benefits" && i.field_name != "target_ghgs"){
						frm.set_value(i.field_name,i.new_values)
					}
					
					else if(i.field_name == "non_ghg_mitigation_benefits"){

						var new_list = i.new_values.split(",")

						frm.clear_table("non_ghg_mitigation_benefits")
						for (var value of new_list){
							var row = frm.add_child("non_ghg_mitigation_benefits")
							row.non_ghg_mitigation_benefits = value



						}
					}

					else if(i.field_name == "target_ghgs"){

						var new_list = i.new_values.split(",")

						frm.clear_table("target_ghgs")
						for (var value of new_list){
							var row = frm.add_child("target_ghgs")
							row.target_ghgs = value



						}
					}
					
				}

				if(frm.doc.edited_performance_indicator.length != 0){
					frm.set_value("performance_indicator",[])
					for(var i of frm.doc.edited_performance_indicator){
						var child = frm.add_child("performance_indicator")
						child.performance_indicator = i.performance_indicator
						child.unit = i.unit
						child.expected_value = i.expected_value
						child.reference = i.reference
					}
					
					frm.refresh_field("performance_indicator")
				}
				frm.set_value("edited_project_details",[])
				frm.set_value("edited_performance_indicator",[])
				frm.refresh_field("edited_performance_indicator")
			}
			frm.set_value("original_performance_indicator",[])
			frm.set_value('work_state','Approved')
			// if(frm.is_dirty()){
			// 	frm.save()
			// }
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
				
				

				var list=[]
				var new_list =[]
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
								if (i.field_name != "non_ghg_mitigation_benefits" && i.field_name != "target_ghgs"){
									i.new_values = frm.doc[`${i.field_name}`].toString()
									frm.set_value(i.field_name,i.old_values)
								}
								else if(i.field_name == "non_ghg_mitigation_benefits"){
									var non_ghg_mitigation_benefits_result = ""


									for(var res of frm.doc.non_ghg_mitigation_benefits){

										if(non_ghg_mitigation_benefits_result == ""){

											non_ghg_mitigation_benefits_result += res.non_ghg_mitigation_benefits
										}else{

											non_ghg_mitigation_benefits_result += ","
											non_ghg_mitigation_benefits_result += res.non_ghg_mitigation_benefits
										}
									}

									i.new_values = non_ghg_mitigation_benefits_result
									list=i.old_values.split(",")
									frm.clear_table("non_ghg_mitigation_benefits")
									for (var value of list){
										var row = frm.add_child("non_ghg_mitigation_benefits")
										row.non_ghg_mitigation_benefits = value
									}
									frm.refresh_field("non_ghg_mitigation_benefits")

								}
								else if(i.field_name == "target_ghgs"){
									var target_ghgs_result = ""

									for(var res of frm.doc.target_ghgs){
										if(target_ghgs_result == ""){
											target_ghgs_result += res.target_ghgs
										}else{
											target_ghgs_result += ","
											target_ghgs_result += res.target_ghgs
										}
									}

									i.new_values = target_ghgs_result
									new_list=i.old_values.split(",")
									frm.clear_table("target_ghgs")
									for (var value of new_list){
										var row = frm.add_child("target_ghgs")
										row.target_ghgs = value
									}
									frm.refresh_field("target_ghgs")

								}
								frm.refresh_field("edited_project_details")
								const index = field_name_list.indexOf(i.field_name);
								const x = field_name_list.splice(index, 1)
								
							}
						}
						if (field_name_list){
							var list2=[]
							var new_list2 =[]

							for (var i of field_name_list){
								var label = i.replaceAll("_"," ")
								label = toTitleCase(label)

								var child =frm.add_child("edited_project_details")
								if (i != "non_ghg_mitigation_benefits"  && i != "target_ghgs"){


									child.field_label = label
									child.field_name = i
									child.old_values = result[`${i}`]
									child.new_values = frm.doc[`${i}`].toString()
									frm.set_value(i,result[`${i}`])

								}
								else if(i == "non_ghg_mitigation_benefits"){
									child.field_label = label
									child.field_name = i
									child.old_values = result[`${i}`]



									var non_ghg_mitigation_benefits_result = ""


									for(var res of frm.doc.non_ghg_mitigation_benefits){
										if(non_ghg_mitigation_benefits_result == ""){

											non_ghg_mitigation_benefits_result += res.non_ghg_mitigation_benefits
										}else{

											non_ghg_mitigation_benefits_result += ","
											non_ghg_mitigation_benefits_result += res.non_ghg_mitigation_benefits
										}
									}

									child.new_values = non_ghg_mitigation_benefits_result

									frm.refresh_fields("edited_project_details")

									list2 = result[`${i}`].split(",")

									frm.clear_table("non_ghg_mitigation_benefits")
									for(var value of list2){
										var row = frm.add_child("non_ghg_mitigation_benefits")

										row.non_ghg_mitigation_benefits = value      
									}
									frm.refresh_fields("non_ghg_mitigation_benefits")
								}
								else if(i == "target_ghgs"){
									child.field_label = label
									child.field_name = i
									child.old_values = result[`${i}`]



									var target_ghgs_result = ""

									for(var res of frm.doc.target_ghgs){
										if(target_ghgs_result == ""){
											target_ghgs_result += res.target_ghgs
										}else{
											target_ghgs_result += ","
											target_ghgs_result += res.target_ghgs
										}
									}

									child.new_values = target_ghgs_result

									frm.refresh_fields("edited_project_details")

									new_list2 = result[`${i}`].split(",")
									

									frm.clear_table("target_ghgs")
									for(var value of new_list2){
										var row = frm.add_child("target_ghgs")

										row.target_ghgs = value
									}
									frm.refresh_fields("target_ghgs")
								}

								
							}
						}
					}
				})
				
			}
		}
		
		setTimeout(function() {
			$('[id="mitigations-tab1-tab"]').click()
			$('[id="mitigations-tab1"]').addClass("active show")
		})
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