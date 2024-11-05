var categories=[]
var html_output= ""
var form_data = {}
var else_category=[]
var json_code=[]
var html_head =""


html_head += "<head><style>table, th, tr, td {border: 1px solid;}</style></head>"
html_head += "<table style='table-layout: fixed;width: 100%;' id=html_table class='table table-bordered'>"
html_head += "<tr><th scope=col>Table Name</th><th scope=col>Category</th><th scope=col style='width:30%;justify-content: center;'>Questions</th><th scope=col>Field Name</th><th scope=col style='width:15%;'>Old Values</th><th scope=col style='width:15%;'>New Values</th></tr>"
frappe.ui.form.on('Adaptation', {

	refresh: function(frm){
		frm.icon_html = ''
		frm.icon_html += `<div style="display:flex;gap:29px;flex-wrap: wrap;">`
		frappe.call({
			doc:frm.doc,
			method:'categorylist',
			async:false,
			callback:function(r){
				for(let i of r.message){
					frm.icon_html +=`<div id="${i.replaceAll(" ", "_")}" class= "adaptation-icon" onclick="check_categories(this)">
										<button class="adaptation-btn">${i}</button>
									</div>`
				}
			}
		})
		
		frm.icon_html += `
			</div>
			<script>
				function check_categories(event){
					event['selectedItem'] = !event['selectedItem']
					if(event['selectedItem']){
						$('#'+event.id).find('.adaptation-btn').attr("style","background-color: rgba(0,0,0,0.2) !important;")
					}else{
						$('#'+event.id).find('.adaptation-btn').attr("style","background-color: #f2f2f2 !important;")
					}
				}
			</script>
			<style>
				.adaptation-btn{
					background-color: #f2f2f2 !important;
					width: 131px;
					border-radius: 5px;
					font-size: 14px;
					font-family: 'Source Sans Pro', sans-serif;
					padding: 6px 9px;
					border: unset;
					box-shadow: rgba(0, 0, 0, 0.1) 0px 4px 4px 0px;
				}
				.adaptation-btn:focus{
					outline: none; !important;
				}
				.adaptation-icon{
					position: relative;
					border-radius:5px;
					border: unset;
					transition: transform .2s;
				}
				.adaptation-icon:hover {
					-ms-transform: scale(1.5);
					-webkit-transform: scale(1.5);
					transform: scale(1.1); 
					// box-shadow: 0px 0px 5px 0px #6c6c6c;
					z-index:3;
				}
				.overlay {
					position: absolute;
					border-radius:5px;
					display: none;
					top: 0;
					left: 0;
					right: 0;
					bottom: 0;
					background-color: rgba(0,0,0,0.2);
					z-index: 2;
					cursor: pointer;
				}
			</style>
		`
		$('[data-fieldname="category_html"]').html(frm.icon_html)
		if(frm.doc.category_json){
			for(let [key,value] of  Object.entries(JSON.parse(frm.doc.category_json)) ){
				if(value == true){
					
					$('#'+key.replaceAll(" ", "_")).find('.adaptation-btn').attr("style","background-color: rgba(0,0,0,0.2) !important;")
					$('#'+key.replaceAll(" ", "_")).prop("selectedItem",true)
					
				}
			}
		}
		$('.adaptation-icon').on("click",function(){
			frm.clear_custom_buttons()
			frm.dirty()
		})

		$(`div[data-fieldname="ndp_cov"]`).attr('style','max-width:100%;padding-right: 0px;');
		$(`div[data-fieldname="ndp_coverage"]`).attr('style','max-width:100%;padding-right: 0px;');
		$('[data-fieldtype="Check"]').children().css({"box-shadow":"rgba(0, 0, 0, 0.1) 0px 4px 4px 0px","border-radius":"5px","background": "#f2f2f2","color": "black","text-align": "center","width": "100%","display": "flex","justify-content": "center","cursor": "pointer","height": "35px","border-color": "#cabfb6","align-items": "center"});
		$('[class="input-area"]').css({"margin":"0px 0px 0px 10px"});
		$('[class="checkbox"]').children().css("cursor","pointer")
		$('[class="label-area"]').css({"width":"220px","padding":"8px","margin-left":"-14px","font-size": "14px"});
		$('[class="help-box small text-muted"]').css("margin","0px");

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



		// if (frm.doc.work_state == "Approved"){
		// 	cur_frm.fields_dict.project_id.df.read_only = 1
		// 	cur_frm.fields_dict.select_approver.df.read_only = 1
		// }


		// frm.fields_dict.html_table.$wrapper.html(html_output)
		if(!frm.doc.json){
			frm.call({
				doc:frm.doc,
				method:"getValues",
				async:false,
				callback: function(r){
					var valueList = r.message
					var json_code={"qualitative":[],"quantitative":[]}
					for(let i of valueList){
						
						if (i.table == "Qualitative"){
							json_code["qualitative"].push({"category":i.impact_area,"question":i.indicator,"likelihood":"","impact":"","table":i.table});
						}
						if (i.table == "Quantitative"){
							json_code["quantitative"].push({"category":i.impact_area,"question":i.indicator,"expected_value":0,"data_source":"","table":i.table});

						}
					}
					frm.set_value("json", JSON.stringify(json_code))
					frm.refresh_field("json")
				}
			
			})
		}
		if(frm.doc.html_json){
			var existing_html_json = JSON.parse(frm.doc.html_json)
			var html_output =""

			for(var i=0;i<existing_html_json.old.length;i++){
					if (existing_html_json.old[i].type == "qualitative"){ 
							if(existing_html_json.new[i].likelihood && (existing_html_json.new[i].likelihood != existing_html_json.old[i].likelihood)){
								html_output +=`<tr><td>${toTitleCase(existing_html_json.old[i].type)} Impact</td><td>${existing_html_json.old[i].category}</td><td style='justify-content: center;'>${existing_html_json.old[i].question}</td><td>Likelihood</td><td>${existing_html_json.old[i].likelihood}</td><td>${existing_html_json.new[i].likelihood}</td></tr>`
							}
							if(existing_html_json.new[i].impact && (existing_html_json.new[i].impact != existing_html_json.old[i].impact)){ 
								html_output +=`<tr><td>${toTitleCase(existing_html_json.old[i].type)} Impact</td><td>${existing_html_json.old[i].category}</td><td style='justify-content: center;'>${existing_html_json.old[i].question}</td><td>Impact</td><td>${existing_html_json.old[i].impact}</td><td>${existing_html_json.new[i].impact}</td></tr>`
							}
						
					}
					if (existing_html_json.old[i].type == "quantitative"){
							if(existing_html_json.new[i].expected_value && (existing_html_json.new[i].expected_value != existing_html_json.old[i].expected_value)){
									html_output +=`<tr><td>${toTitleCase(existing_html_json.old[i].type)} Impact</td><td>${existing_html_json.old[i].category}</td><td style='justify-content: center;'>${existing_html_json.old[i].question}</td><td>Expected Value</td><td>${existing_html_json.old[i].expected_value}</td><td>${existing_html_json.new[i].expected_value}</td></tr>`
							}
							if(existing_html_json.new[i].data_source && (existing_html_json.new[i].data_source != existing_html_json.old[i].data_source)){ 
								html_output +=`<tr><td>${toTitleCase(existing_html_json.old[i].type)} Impact</td><td>${existing_html_json.old[i].category}</td><td style='justify-content: center;'>${existing_html_json.old[i].question}</td><td>Data Source</td><td>${existing_html_json.old[i].data_source}</td><td>${existing_html_json.new[i].data_source}</td></tr>`
							}
						
					}
				
			}
			frm.fields_dict.html_table.$wrapper.html(html_head + html_output + "</table>")
			frm.refresh_field("html_table")
		}

		frappe.db.get_list('Adaptation', {
			fields: ['project_id'],
			pluck:'project_id'
		}).then(r => {
			frm.set_query("project_id",function(){

				return{
					filters:{
						objective: ['in',['Cross-Cutting','Adaptation']],
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
		});

		if (frm.doc.workflow_state == "Rejected" && frm.doc.work_state == "Approved"){
			frm.set_value("edited_project_details",[])
			frm.fields_dict.html_table.$wrapper.html("")
			frm.refresh_field("html_table")
		}
		// setTimeout(function() {
		// 	$('[id="adaptation-tab1-tab"]').click()
		// 	$('[id="adaptation-tab1"]').addClass("active show")
		// })

		if (frm.doc.workflow_state == "Approved" || frm.doc.workflow_state =="Rejected" || frm.doc.__islocal && frm.doc.work_state != "Approved"){
			$('[id="adaptation-tab1"]').addClass("active")
			$('[id="adaptation-tab1-tab"]').hide()
			$('[id="adaptation-tab2-tab"]').hide()
		}
		else if(frm.doc.work_state =="Approved" && (frm.doc.workflow_state == "Draft" || frm.doc.workflow_state == "Pending") && (cur_frm.fields_dict.html_table.$wrapper[0].innerHTML != '' || frm.doc.edited_project_details.length != 0)){
			$('[id="adaptation-tab1-tab"]').addClass("active")
			$('[id="adaptation-tab1-tab"]').attr('aria-selected', 'true');
			$('[id="adaptation-tab2-tab"]').removeClass("active")
			$('[id="adaptation-tab1-tab"]').show()
			$('[id="adaptation-tab2-tab"]').show()
			$('[id="adaptation-tab1"]').addClass("active")
			
		}
		
	},

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
				}
			})
		}
	},
	
	
	load_categories: function(frm){
		var existing_json = JSON.parse(frm.doc.json)
		for (var row of cur_frm.doc.qualitative_impact){
			for (var i of existing_json.qualitative){
				if (i.question == row.question){
					i.likelihood = row.likelihood
					i.impact = row.impact
				}
			}
		}
		for (var row of cur_frm.doc.quantitative_impact){
			for (var i of existing_json.quantitative){
				if (i.question == row.question){
					i.expected_value = row.expected_value
					i.data_source = row.data_source
				}
			}
		}
		frm.set_value("json", JSON.stringify(existing_json))


		var checkedList = []
		var result=frm.call({
			doc:frm.doc,
			method:'categorylist',
			async:false,
			callback: function(r)
			{
				frm.set_value("qualitative_impact",[]);
				frm.set_value("quantitative_impact",[]);	
				$(".adaptation-icon").each(function(){
					var field_name = $(this).attr('id');
					var value = $(this).prop("selectedItem");

					value = value ? value : false
					if (Array.isArray(form_data[field_name])) {
						form_data[field_name].push(value);
					} else {
						form_data[field_name] = value;
					}
				})
				// $("[type='checkbox']").each(function(){
				// 	var field_name = $(this).attr('data-fieldname');
				// 	var value = $(this).prop("checked");
				// 		if (Array.isArray(form_data[field_name])) {
				// 			form_data[field_name].push(value);
				// 		} 
				// 		else {
				// 			form_data[field_name] = value;
				// 		}
				// });
				console.log("form_dataform_data = ",form_data);
				for(var i of JSON.parse(frm.doc.json).qualitative){
					for(let [key,value] of Object.entries(form_data)){
						if(value ==true){
							if (key.replaceAll("_", " ") == i.category){
									if (!checkedList.includes(i.category)){
									checkedList.push(i.category)
								}
							}
						}
					}
				}
				
				if(cur_frm.doc.qualitative_impact.length == 0){
					for(let [key,value] of  Object.entries(form_data)){

						if(value ==true){
							for(var i of JSON.parse(frm.doc.json).qualitative){
								if (key.replaceAll("_", " ") == i.category){
									if (i.table == "Qualitative"){
										let row = frm.add_child('qualitative_impact')
											row.category= i.category,
											row.question= i.question,
											row.likelihood = i.likelihood,
											row.impact = i.impact
										
										categories.push(i.category)
										
									}
								}	
							}
							frm.refresh_field('qualitative_impact');
							for(var i of JSON.parse(frm.doc.json).quantitative){
								if (key.replaceAll("_", " ") == i.category){
									if (i.table == "Quantitative"){
										let row = frm.add_child('quantitative_impact')
												row.category= i.category,
												row.question= i.question,
												row.expected_value = i.expected_value,
												row.data_source = i.data_source
										
									}
								}
							}
							frm.refresh_field('quantitative_impact');
							categories=[...new Set(categories)]	
						}
					}
				}
				else{
					for (var i of  JSON.parse(frm.doc.json)){
						if (!categories.includes(i.category) && form_data[`${i.category}`]){
							else_category.push(i.category)
							if (i.table == "Qualitative"){
								let row = frm.add_child('qualitative_impact')
									row.category= i.category,
									row.question= i.question,
									row.likelihood = i.likelihood,
									row.impact = i.impact
								
							}
							if (i.table == "Quantitative"){
								let row = frm.add_child('quantitative_impact')
										row.category= i.category,
										row.question= i.question,
										row.expected_value = i.expected_value,
										row.data_source = i.data_source
								
							}
						}
					}
					frm.refresh_field('qualitative_impact');
					frm.refresh_field('quantitative_impact');
					categories = categories.concat(else_category)
					categories=[...new Set(categories)]
				}	
			}
		});
	},
	
	before_save:function(frm){
		frm.set_value("category_json", "")
		var existing_json = JSON.parse(frm.doc.json)
		for (var row of cur_frm.doc.qualitative_impact){
			for (var i of existing_json.qualitative){
				if (i.question == row.question){
					i.likelihood = row.likelihood
					i.impact = row.impact
				}
			}
		}
		for (var row of cur_frm.doc.quantitative_impact){
			for (var i of existing_json.quantitative){
				if (i.question == row.question){
					i.expected_value = row.expected_value
					i.data_source = row.data_source
				}
			}
		}
		frm.set_value("json", JSON.stringify(existing_json))
		frm.refresh_field("json")
		var json_={}
		$(".adaptation-icon").each(function(){
			let field_name = $(this).attr('id');
			let value = $(this).prop("selectedItem");
			value = value ? value : false
			json_[field_name]=(value)
			// json_.push(k)
		})
		frm.set_value("category_json", JSON.stringify(json_))
		frm.refresh_field("category_json")
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

		if (frm.doc.workflow_state == "Approved"){
			for (var i of frm.doc.edited_project_details){

				if(i.field_name != "ndp_cov"){
					frm.set_value(i.field_name,i.new_values)
				}
				
				else if(i.field_name == "ndp_cov"){
					var new_list = i.new_values.split(",")
					frm.clear_table("ndp_cov")
					for (var value of new_list){
						var row = frm.add_child("ndp_cov")
						row.ndp_coverage_tags = value
					}
				}
				
			}
			frm.set_value("edited_project_details",[])
			frm.set_value('work_state','Approved')


			var checkedList = []
			if(frm.doc.html_json){
				var existing_json = JSON.parse(frm.doc.json)
					var existing_json1 = JSON.parse(frm.doc.html_json)
				
				for (var row of existing_json1.new){
					if(row.type == "qualitative"){
						for (var i of existing_json.qualitative){
							if (i.question == row.question){
								i.likelihood = row.likelihood
								i.impact = row.impact
							}
						}
					}
				}
				for (var row of existing_json1.new){
					if(row.type == "quantitative"){
						for (var i of existing_json.quantitative){
							if (i.question == row.question){
								i.expected_value = row.expected_value
								i.data_source = row.data_source
							}
						}
					}
				}
				frm.set_value("json", JSON.stringify(existing_json))
				frm.refresh_field("json")
				


				var result=frm.call({
					doc:frm.doc,
					method:'categorylist',
					async:false,
					callback: function(r)
					{

						frm.set_value("qualitative_impact",[]);
						frm.set_value("quantitative_impact",[]);

						$(".adaptation-icon").each(function(){
							var field_name = $(this).attr('id');
							var value = $(this).prop("selectedItem");
		
							value = value ? value : false
							if (Array.isArray(form_data[field_name])) {
								form_data[field_name].push(value);
							} else {
								form_data[field_name] = value;
							}
						})

						// $("[type='checkbox']").each(function(){
						// 	var field_name = $(this).attr('data-fieldname');
						// 	var value = $(this).prop("checked");
						// 		if (Array.isArray(form_data[field_name])) {
						// 			form_data[field_name].push(value);
						// 		} else {
						// 			form_data[field_name] = value;
						// 		}
						// });

						for(var i of JSON.parse(frm.doc.json).qualitative){
							
							for(let [key,value] of Object.entries(form_data)){
								
								if(value ==true){
									
									if (key.replaceAll("_", " ") == i.category){
											if (!checkedList.includes(i.category)){
											
											checkedList.push(i.category)
										}
									}
								}
							}
						}
						
						if(cur_frm.doc.qualitative_impact.length == 0){
							for(let [key,value] of  Object.entries(form_data)){

								if(value ==true){
									for(var i of JSON.parse(frm.doc.json).qualitative){
										if (key.replaceAll("_", " ") == i.category){
											if (i.table == "Qualitative"){
												let row = frm.add_child('qualitative_impact')
													row.category= i.category,
													row.question= i.question,
													row.likelihood = i.likelihood,
													row.impact = i.impact
												
												categories.push(i.category)
												
											}
										}	
									}
									frm.refresh_field('qualitative_impact');
									for(var i of JSON.parse(frm.doc.json).quantitative){
										if (key.replaceAll("_", " ") == i.category){
											if (i.table == "Quantitative"){
												let row = frm.add_child('quantitative_impact')
														row.category= i.category,
														row.question= i.question,
														row.expected_value = i.expected_value,
														row.data_source = i.data_source
												
											}
										}
									}
									frm.refresh_field('quantitative_impact');
									categories=[...new Set(categories)]	
								}
							}
						}
						else{
							for (var i of  JSON.parse(frm.doc.json)){
									if (!categories.includes(i.category) && form_data[`${i.category}`]){
										else_category.push(i.category)
										
										if (i.table == "Qualitative"){
											let row = frm.add_child('qualitative_impact')
												row.category= i.category,
												row.question= i.question,
												row.likelihood = i.likelihood,
												row.impact = i.impact
												
											
											
										}
										if (i.table == "Quantitative"){
											let row = frm.add_child('quantitative_impact')
													row.category= i.category,
													row.question= i.question,
													row.expected_value = i.expected_value,
													row.data_source = i.data_source
											
										}
									}
							}
							frm.refresh_field('qualitative_impact');
							frm.refresh_field('quantitative_impact');
							categories = categories.concat(else_category)
							categories=[...new Set(categories)]
						}
						
					}
				});

				frm.set_value("html_json",undefined)
				frm.refresh_field("html_json")
				frm.fields_dict.html_table.$wrapper.html("")
				frm.refresh_field("html_table")
			}
			
		}

		if(frm.doc.workflow_state == "Draft"){
			var checkedList = []
			var result=frm.call({
				doc:frm.doc,
				method:'categorylist',
				async:false,
				callback: function(r)
				{
					frm.set_value("qualitative_impact",[]);
					frm.set_value("quantitative_impact",[]);

					$(".adaptation-icon").each(function(){
						var field_name = $(this).attr('id');
						var value = $(this).prop("selectedItem");
	
						value = value ? value : false
						if (Array.isArray(form_data[field_name])) {
							form_data[field_name].push(value);
						} else {
							form_data[field_name] = value;
						}
					})

					// $("[type='checkbox']").each(function(){
					// 	var field_name = $(this).attr('data-fieldname');
					// 	var value = $(this).prop("checked");
					// 		if (Array.isArray(form_data[field_name])) {
					// 			form_data[field_name].push(value);
					// 		} 
					// 		else {
					// 			form_data[field_name] = value;
					// 		}
					// });
					for(var i of JSON.parse(frm.doc.json).qualitative){
						for(let [key,value] of Object.entries(form_data)){
							if(value ==true){
								if (key.replaceAll("_", " ") == i.category){
										if (!checkedList.includes(i.category)){
										checkedList.push(i.category)
									}
								}
							}
						}
					}
					
					if(cur_frm.doc.qualitative_impact.length == 0){
						for(let [key,value] of  Object.entries(form_data)){

							if(value ==true){
								for(var i of JSON.parse(frm.doc.json).qualitative){
									if (key.replaceAll("_", " ") == i.category){
										if (i.table == "Qualitative"){
											let row = frm.add_child('qualitative_impact')
												row.category= i.category,
												row.question= i.question,
												row.likelihood = i.likelihood,
												row.impact = i.impact
											
											categories.push(i.category)
											
										}
									}	
								}
								frm.refresh_field('qualitative_impact');
								for(var i of JSON.parse(frm.doc.json).quantitative){
									if (key.replaceAll("_", " ") == i.category){
										if (i.table == "Quantitative"){
											let row = frm.add_child('quantitative_impact')
													row.category= i.category,
													row.question= i.question,
													row.expected_value = i.expected_value,
													row.data_source = i.data_source
											
										}
									}
								}
								frm.refresh_field('quantitative_impact');
								categories=[...new Set(categories)]
							}
						}
					}
					else{
						for (var i of  JSON.parse(frm.doc.json)){
							if (!categories.includes(i.category) && form_data[`${i.category}`]){
								else_category.push(i.category)
								if (i.table == "Qualitative"){
									let row = frm.add_child('qualitative_impact')
										row.category= i.category,
										row.question= i.question,
										row.likelihood = i.likelihood,
										row.impact = i.impact
									
								}
								if (i.table == "Quantitative"){
									let row = frm.add_child('quantitative_impact')
											row.category= i.category,
											row.question= i.question,
											row.expected_value = i.expected_value,
											row.data_source = i.data_source
									
								}
							}
						}
						frm.refresh_field('qualitative_impact');
						frm.refresh_field('quantitative_impact');
						categories = categories.concat(else_category)
						categories=[...new Set(categories)]
					}
				}
			});
		}
		
		

		if(frm.doc.work_state == "Approved"){
			if (frm.doc.workflow_state != "Approved" && !frm.doc.__islocal){
				
				var checkedList1 = []
				var result=frm.call({
					doc:frm.doc,
					method:'categorylist',
					async:false,
					callback: function(r)
					{
						frm.set_value("qualitative_impact",[]);
						frm.set_value("quantitative_impact",[]);
						
						$(".adaptation-icon").each(function(){
							var field_name = $(this).attr('id');
							var value = $(this).prop("selectedItem");
		
							value = value ? value : false
							if (Array.isArray(form_data[field_name])) {
								form_data[field_name].push(value);
							} else {
								form_data[field_name] = value;
							}
						})

						// $("[type='checkbox']").each(function(){
						// 	var field_name = $(this).attr('data-fieldname');
						// 	var value = $(this).prop("checked");
						// 		if (Array.isArray(form_data[field_name])) {
						// 			form_data[field_name].push(value);
						// 		} 
						// 		else {
						// 			form_data[field_name] = value;
						// 		}
						// });
						for(var i of JSON.parse(frm.doc.json).qualitative){
							for(let [key,value] of Object.entries(form_data)){
								if(value ==true){
									if (key.replaceAll("_", " ") == i.category){
											if (!checkedList1.includes(i.category)){
											checkedList1.push(i.category)
										}
									}
								}
							}
						}
						
						if(cur_frm.doc.qualitative_impact.length == 0){
							for(let [key,value] of  Object.entries(form_data)){

								if(value ==true){
									for(var i of JSON.parse(frm.doc.json).qualitative){
										if (key.replaceAll("_", " ") == i.category){
											if (i.table == "Qualitative"){
												let row = frm.add_child('qualitative_impact')
													row.category= i.category,
													row.question= i.question,
													row.likelihood = i.likelihood,
													row.impact = i.impact
												
												categories.push(i.category)
												
											}
										}	
									}
									frm.refresh_field('qualitative_impact');

									
									for(var i of JSON.parse(frm.doc.json).quantitative){
										if (key.replaceAll("_", " ") == i.category){
											if (i.table == "Quantitative"){
												let row = frm.add_child('quantitative_impact')
														row.category= i.category,
														row.question= i.question,
														row.expected_value = i.expected_value,
														row.data_source = i.data_source
												
											}
										}
									}
									frm.refresh_field('quantitative_impact');
									categories=[...new Set(categories)]	
								}
							}
						}
						else{
							for (var i of  JSON.parse(frm.doc.json)){
								if (!categories.includes(i.category) && form_data[`${i.category}`]){
									else_category.push(i.category)
									if (i.table == "Qualitative"){
										let row = frm.add_child('qualitative_impact')
											row.category= i.category,
											row.question= i.question,
											row.likelihood = i.likelihood,
											row.impact = i.impact
										
									}
									
									if (i.table == "Quantitative"){
										let row = frm.add_child('quantitative_impact')
												row.category= i.category,
												row.question= i.question,
												row.expected_value = i.expected_value,
												row.data_source = i.data_source
										
									}
								}
							}
							frm.refresh_field('qualitative_impact');
							frm.refresh_field('quantitative_impact');
							categories = categories.concat(else_category)
							categories=[...new Set(categories)]
						}	
						frm.refresh_field('qualitative_impact');
					}
				});



				var list=[]
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
								if (i.field_name != "ndp_cov"){
									i.new_values = frm.doc[`${i.field_name}`]
									frm.set_value(i.field_name,i.old_values)
								}
								else if(i.field_name == "ndp_cov"){
									var ndp_cov_result = ""

									for(var res of frm.doc.ndp_cov){
										if(ndp_cov_result == ""){
											ndp_cov_result += res.ndp_coverage_tags
										}else{
											ndp_cov_result += ","
											ndp_cov_result += res.ndp_coverage_tags
										}
									}

									i.new_values = ndp_cov_result
									list=i.old_values.split(",")
									frm.clear_table("ndp_cov")
									for (var value of list){
										var row = frm.add_child("ndp_cov")
										row.ndp_coverage_tags = value
									}
									frm.refresh_field("ndp_cov")

								}
								frm.refresh_field("edited_project_details")
								const index = field_name_list.indexOf(i.field_name);
								const x = field_name_list.splice(index, 1)
							}
						}
						if (field_name_list){
							var list2=[]

							
							for (var i of field_name_list){
								var label = i.replaceAll("_"," ")
								label = toTitleCase(label)

								var child =frm.add_child("edited_project_details")
								
								if (i != "ndp_cov"){


									child.field_label = label
									child.field_name = i
									child.old_values = result[`${i}`]
									child.new_values = frm.doc[`${i}`]
									frm.set_value(i,result[`${i}`])

								}
								else if(i == "ndp_cov"){
									child.field_label = label
									child.field_name = i
									child.old_values = result[`${i}`]



									var ndp_cov_result = ""

									for(var res of frm.doc.ndp_cov){
										if(ndp_cov_result == ""){
											ndp_cov_result += res.ndp_coverage_tags
										}else{
											ndp_cov_result += ","
											ndp_cov_result += res.ndp_coverage_tags
										}
									}

									child.new_values = ndp_cov_result

									frm.refresh_fields("edited_project_details")

									list2 = result[`${i}`].split(",")
									

									frm.clear_table("ndp_cov")
									for(var value of list2){
										var row = frm.add_child("ndp_cov")``

										row.ndp_coverage_tags = value      
									}
									frm.refresh_fields("ndp_cov")
									
								}
								

								
							}
						}
					}
				})

				frm.call({
					doc:frm.doc,
					method:"get_jsons",
					async: false,
					callback:function(r){
						if (r.message[0].length != 0){


							// frm.doc.html_json = `[{"old":${JSON.stringify(r.message[0])},"new":${JSON.stringify(r.message[1])}}]`
							if(frm.doc.html_json){
								var existing_html_json = JSON.parse(frm.doc.html_json)
								var new_questions_list=[]
								var old_questions_list=[]
								for (var i of existing_html_json.old){
									old_questions_list.push(i.question)
								}
								for (var i of existing_html_json.new){
									new_questions_list.push(i.question)
								}


								for (var row in r.message[0]){
									if (!old_questions_list.includes(r.message[0][row].question)){
										existing_html_json.old.push({"category":r.message[0][row].category,"question":r.message[0][row].question,"likelihood":r.message[0][row].likelihood,"impact":r.message[0][row].impact,"expected_value":r.message[0][row].expected_value,"data_source":r.message[0][row].data_source,"type":r.message[0][row].type});

									}
								}
								for (var row of r.message[1]){
									for (var i of existing_html_json.new){
										if (i.question == row.question && row.type == "qualitative"){
											i.likelihood = row.likelihood
											i.impact = row.impact
										}
										if (i.question == row.question && row.type == "quantitative"){
											i.expected_value = row.expected_value
											i.data_source = row.data_source
										}
										
									}
								}
								for (var row in r.message[1]){

									if (!new_questions_list.includes(r.message[0][row].question)){
										existing_html_json.new.push({"category":r.message[1][row].category,"question":r.message[1][row].question,"likelihood":r.message[1][row].likelihood,"impact":r.message[1][row].impact,"expected_value":r.message[1][row].expected_value,"data_source":r.message[1][row].data_source,"type":r.message[1][row].type});

									}
								}
								frm.set_value("html_json", JSON.stringify(existing_html_json))
								frm.refresh_field("html_json")


								var html_output =""
								for(var i=0;i<existing_html_json.old.length;i++){
									if (existing_html_json.old[i].type == "qualitative"){ 
											if(existing_html_json.new[i].likelihood && (existing_html_json.new[i].likelihood != existing_html_json.old[i].likelihood)){
												html_output +=`<tr><td>${toTitleCase(existing_html_json.old[i].type)} Impact</td><td>${existing_html_json.old[i].category}</td><td style='justify-content: center;'>${existing_html_json.old[i].question}</td><td>Likelihood</td><td>${existing_html_json.old[i].likelihood}</td><td>${existing_html_json.new[i].likelihood}</td></tr>`
											}
											if(existing_html_json.new[i].impact && (existing_html_json.new[i].impact != existing_html_json.old[i].impact)){

												html_output +=`<tr><td>${toTitleCase(existing_html_json.old[i].type)} Impact</td><td>${existing_html_json.old[i].category}</td><td style='justify-content: center;'>${existing_html_json.old[i].question}</td><td>Impact</td><td>${existing_html_json.old[i].impact}</td><td>${existing_html_json.new[i].impact}</td></tr>`
											}
										
									}
									if (existing_html_json.old[i].type == "quantitative"){
										if(existing_html_json.new[i].expected_value && (existing_html_json.new[i].expected_value != existing_html_json.old[i].expected_value)){
												html_output +=`<tr><td>${toTitleCase(existing_html_json.old[i].type)} Impact</td><td>${existing_html_json.old[i].category}</td><td style='justify-content: center;'>${existing_html_json.old[i].question}</td><td>Expected Value</td><td>${existing_html_json.old[i].expected_value}</td><td>${existing_html_json.new[i].expected_value}</td></tr>`
										}
										if(existing_html_json.new[i].data_source && (existing_html_json.new[i].data_source != existing_html_json.old[i].data_source)){

											html_output +=`<tr><td>${toTitleCase(existing_html_json.old[i].type)} Impact</td><td>${existing_html_json.old[i].category}</td><td style='justify-content: center;'>${existing_html_json.old[i].question}</td><td>Data Source</td><td>${existing_html_json.old[i].data_source}</td><td>${existing_html_json.new[i].data_source}</td></tr>`
										}
									}
									
								}
								frm.fields_dict.html_table.$wrapper.html(html_head + html_output + "</table>")
								frm.refresh_field("html_table")


								var existing_json2 = JSON.parse(frm.doc.json)
								for (var row of r.message[0]){
									for (var i of existing_json2.qualitative){
										if (i.question == row.question){
											i.likelihood = row.likelihood
											i.impact = row.impact
										}
									}
								}
								for (var row of r.message[0]){
									for (var i of existing_json2.quantitative){
										if (i.question == row.question){


											i.expected_value = row.expected_value
											i.data_source = row.data_source
											

											

										}
									}
								}
								frm.set_value("json", JSON.stringify(existing_json2))
								frm.refresh_field("json")


								var checkedList = []
								frm.call({
									doc:frm.doc,
									method:'categorylist',
									async:false,
									callback: function(r)
									{

										frm.set_value("qualitative_impact",[]);
										frm.set_value("quantitative_impact",[]);

										$(".adaptation-icon").each(function(){
											var field_name = $(this).attr('id');
											var value = $(this).prop("selectedItem");
						
											value = value ? value : false
											if (Array.isArray(form_data[field_name])) {
												form_data[field_name].push(value);
											} else {
												form_data[field_name] = value;
											}
										})

										// $("[type='checkbox']").each(function(){
										// 	var field_name = $(this).attr('data-fieldname');
										// 	var value = $(this).prop("checked");
										// 		if (Array.isArray(form_data[field_name])) {
										// 			form_data[field_name].push(value);
										// 		} else {
										// 			form_data[field_name] = value;
										// 		}
										// });

										for(var i of JSON.parse(frm.doc.json).qualitative){
											
											for(let [key,value] of Object.entries(form_data)){
												
												if(value ==true){
													
													if (key.replaceAll("_", " ") == i.category){
															if (!checkedList.includes(i.category)){
															
															checkedList.push(i.category)
														}
													}
												}
											}
										}
										
										if(cur_frm.doc.qualitative_impact.length == 0){
											for(let [key,value] of  Object.entries(form_data)){

												if(value ==true){
													for(var i of JSON.parse(frm.doc.json).qualitative){
														if (key.replaceAll("_", " ") == i.category){
															if (i.table == "Qualitative"){
																let row = frm.add_child('qualitative_impact')
																	row.category= i.category,
																	row.question= i.question,
																	row.likelihood = i.likelihood,
																	row.impact = i.impact
																
																categories.push(i.category)
																
															}
														}	
													}
													frm.refresh_field('qualitative_impact');
													for(var i of JSON.parse(frm.doc.json).quantitative){
														if (key.replaceAll("_", " ") == i.category){
															if (i.table == "Quantitative"){
																let row = frm.add_child('quantitative_impact')
																		row.category= i.category,
																		row.question= i.question,
																		row.expected_value = i.expected_value,
																		row.data_source = i.data_source
																
															}
														}
													}
													frm.refresh_field('quantitative_impact');
													categories=[...new Set(categories)]	
												}
											}
										}
										else{
											for (var i of  JSON.parse(frm.doc.json)){
													if (!categories.includes(i.category) && form_data[`${i.category}`]){
														else_category.push(i.category)
														
														if (i.table == "Qualitative"){
															let row = frm.add_child('qualitative_impact')
																row.category= i.category,
																row.question= i.question,
																row.likelihood = i.likelihood,
																row.impact = i.impact
																
															
															
														}
														if (i.table == "Quantitative"){
															let row = frm.add_child('quantitative_impact')
																	row.category= i.category,
																	row.question= i.question,
																	row.expected_value = i.expected_value,
																	row.data_source = i.data_source
															
														}
													}
											}
											frm.refresh_field('qualitative_impact');
											frm.refresh_field('quantitative_impact');
											categories = categories.concat(else_category)
											categories=[...new Set(categories)]
										}
										frm.refresh_field('qualitative_impact')
									}
								});
								
							}
							else{

								frm.doc.html_json = `${JSON.stringify({"old":r.message[0],"new":r.message[1]})}`
								frm.refresh_field("html_json")
								var one_time_json = `${JSON.stringify({"old":r.message[0],"new":r.message[1]})}`
								var one_time_html_json = JSON.parse(one_time_json)
								var html_output =""

								for(var i=0;i<one_time_html_json.old.length;i++){
									if (one_time_html_json.old[i].type == "qualitative"){ 
											if(one_time_html_json.new[i].likelihood && (one_time_html_json.new[i].likelihood != one_time_html_json.old[i].likelihood)){
												html_output +=`<tr><td>${toTitleCase(one_time_html_json.old[i].type)} Impact</td><td>${one_time_html_json.old[i].category}</td><td style='justify-content: center;'>${one_time_html_json.old[i].question}</td><td>Likelihood</td><td>${one_time_html_json.old[i].likelihood}</td><td>${one_time_html_json.new[i].likelihood}</td></tr>`
											}
											if(one_time_html_json.new[i].impact && (one_time_html_json.new[i].impact != one_time_html_json.old[i].impact)){

												html_output +=`<tr><td>${toTitleCase(one_time_html_json.old[i].type)} Impact</td><td>${one_time_html_json.old[i].category}</td><td style='justify-content: center;'>${one_time_html_json.old[i].question}</td><td>Impact</td><td>${one_time_html_json.old[i].impact}</td><td>${one_time_html_json.new[i].impact}</td></tr>`
											}
										
									}
									if (one_time_html_json.old[i].type == "quantitative"){
										if(one_time_html_json.new[i].expected_value && (one_time_html_json.new[i].expected_value != one_time_html_json.old[i].expected_value)){
												html_output +=`<tr><td>${toTitleCase(one_time_html_json.old[i].type)} Impact</td><td>${one_time_html_json.old[i].category}</td><td style='justify-content: center;'>${one_time_html_json.old[i].question}</td><td>Expected Value</td><td>${one_time_html_json.old[i].expected_value}</td><td>${one_time_html_json.new[i].expected_value}</td></tr>`
										}
										if(one_time_html_json.new[i].data_source && (one_time_html_json.new[i].data_source != one_time_html_json.old[i].data_source)){

											html_output +=`<tr><td>${toTitleCase(one_time_html_json.old[i].type)} Impact</td><td>${one_time_html_json.old[i].category}</td><td style='justify-content: center;'>${one_time_html_json.old[i].question}</td><td>Data Source</td><td>${one_time_html_json.old[i].data_source}</td><td>${one_time_html_json.new[i].data_source}</td></tr>`
										}
									}
									
								}
								frm.fields_dict.html_table.$wrapper.html(html_head + html_output + "</table>")
								frm.refresh_field("html_table")
								var existing_json2 = JSON.parse(frm.doc.json)
								for (var row of r.message[0]){
									for (var i of existing_json2.qualitative){
										if (i.question == row.question){
											i.likelihood = row.likelihood
											i.impact = row.impact
										}
									}
								}
								for (var row of r.message[0]){
									for (var i of existing_json2.quantitative){
										if (i.question == row.question){


											i.expected_value = row.expected_value
											i.data_source = row.data_source
											

											

										}
									}
								}
								frm.set_value("json", JSON.stringify(existing_json2))
								frm.refresh_field("json")


								var checkedList = []
								frm.call({
									doc:frm.doc,
									method:'categorylist',
									async:false,
									callback: function(r)
									{

										frm.set_value("qualitative_impact",[]);
										frm.set_value("quantitative_impact",[]);

										$(".adaptation-icon").each(function(){
											var field_name = $(this).attr('id');
											var value = $(this).prop("selectedItem");
						
											value = value ? value : false
											if (Array.isArray(form_data[field_name])) {
												form_data[field_name].push(value);
											} else {
												form_data[field_name] = value;
											}
										})

										// $("[type='checkbox']").each(function(){
										// 	var field_name = $(this).attr('data-fieldname');
										// 	var value = $(this).prop("checked");
										// 		if (Array.isArray(form_data[field_name])) {
										// 			form_data[field_name].push(value);
										// 		} else {
										// 			form_data[field_name] = value;
										// 		}
										// });

										for(var i of JSON.parse(frm.doc.json).qualitative){
											
											for(let [key,value] of Object.entries(form_data)){
												
												if(value ==true){
													
													if (key.replaceAll("_", " ") == i.category){
															if (!checkedList.includes(i.category)){
															
															checkedList.push(i.category)
														}
													}
												}
											}
										}
										
										if(cur_frm.doc.qualitative_impact.length == 0){
											for(let [key,value] of  Object.entries(form_data)){

												if(value ==true){
													for(var i of JSON.parse(frm.doc.json).qualitative){
														if (key.replaceAll("_", " ") == i.category){
															if (i.table == "Qualitative"){
																let row = frm.add_child('qualitative_impact')
																	row.category= i.category,
																	row.question= i.question,
																	row.likelihood = i.likelihood,
																	row.impact = i.impact
																
																categories.push(i.category)
																
															}
														}	
													}
													frm.refresh_field('qualitative_impact');
													for(var i of JSON.parse(frm.doc.json).quantitative){
														if (key.replaceAll("_", " ") == i.category){
															if (i.table == "Quantitative"){
																let row = frm.add_child('quantitative_impact')
																		row.category= i.category,
																		row.question= i.question,
																		row.expected_value = i.expected_value,
																		row.data_source = i.data_source
																
															}
														}
													}
													frm.refresh_field('quantitative_impact');
													categories=[...new Set(categories)]	
												}
											}
										}
										else{
											for (var i of  JSON.parse(frm.doc.json)){
													if (!categories.includes(i.category) && form_data[`${i.category}`]){
														else_category.push(i.category)
														
														if (i.table == "Qualitative"){
															let row = frm.add_child('qualitative_impact')
																row.category= i.category,
																row.question= i.question,
																row.likelihood = i.likelihood,
																row.impact = i.impact
																
															
															
														}
														if (i.table == "Quantitative"){
															let row = frm.add_child('quantitative_impact')
																	row.category= i.category,
																	row.question= i.question,
																	row.expected_value = i.expected_value,
																	row.data_source = i.data_source
															
														}
													}
											}
											frm.refresh_field('qualitative_impact');
											frm.refresh_field('quantitative_impact');
											categories = categories.concat(else_category)
											categories=[...new Set(categories)]
										}
										frm.refresh_field('qualitative_impact')
									}
								});
							}
						}
					}
				})
				
			}
		}
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