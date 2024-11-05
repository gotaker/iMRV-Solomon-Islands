// Copyright (c) 2023, tridotstech and contributors
// For license information, please see license.txt
var dynamicTitleList = ['','','','']
var tableFields = [];
var not_hidden_table_fields = []
frappe.ui.form.on('GHG Inventory', {
	
	refresh: function(frm) {

		not_hidden_table_fields = []
		
		var data = frappe.get_meta('GHG Inventory');
		for (var field of data.fields) {
			if (field.fieldtype === 'Table') {
				if(!field.fieldname.startsWith('edited') && field.fieldname !== 'ghg_inventory_details'){
					tableFields.push(field.fieldname);
					if(frm.fields_dict[field.fieldname].df.hidden_due_to_dependency == undefined || frm.fields_dict[field.fieldname].df.hidden_due_to_dependency == false){
						not_hidden_table_fields.push(field.fieldname)
					}
				}
			}
		}
			
		
		if (frm.doc.workflow_state == "Approved"){
			let method = '';
			if (frm.doc.sector == "1. Energy") {
				method = 'mrvtools.ghg_inventory.doctype.ghg_inventory.energy.energy_calculation';
			} else if (frm.doc.sector == "2. Industrial processes and product use") {
				method = 'mrvtools.ghg_inventory.doctype.ghg_inventory.ippu.ippu_calculation';
			} else if (frm.doc.sector == "3. Agriculture") {
				method = 'mrvtools.ghg_inventory.doctype.ghg_inventory.agriculture.agri_calculation';
			} else if (frm.doc.sector == "4. LAND USE, LAND-USE CHANGE AND FORESTRY") {
				method = 'mrvtools.ghg_inventory.doctype.ghg_inventory.land_use.land_calculation';
			} else if (frm.doc.sector == "5. Waste") {
				method = 'mrvtools.ghg_inventory.doctype.ghg_inventory.waste.waste_calculation';
			} else {
				method = 'mrvtools.ghg_inventory.doctype.ghg_inventory.other.other_calculation';
			}
			
							
			frappe.call({
				method: method,
				args:{
					"tablefields": not_hidden_table_fields,
					"doc": frm.doc.doctype,
					"doc_name": frm.doc.name
				},
				async: false,
				callback: function(r) {
				}
			})
		}
			

		


		
		

		if (frm.doc.work_state == "Approved"){
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
		// }$('.inner-group-button button').removeClass("btn-default").addClass("btn-primary")



		if(frm.is_new()){
			frm.set_value('dynamic_title',dynamicTitleList.join(''))
			frm.refresh_field('dynamic_title')
			frappe.db.get_list('GHG Sector',{
				order_by : 'name asc',
				pluck: 'name'
			}).then(r =>{
				var sector_options = ""
				for (var i of r){
					
					var user_obj = {
						"Energy Tracking" : "1. Energy",
						"IPPU Tracking":"2. Industrial processes and product use",
						"Agriculture Tracking":"3. Agriculture",
						"Land Use Tracking":"4. LAND USE, LAND-USE CHANGE AND FORESTRY",
						"Waste Tracking":"5. Waste",
						"Other Tracking":"6. Other"
					}
					if(!frappe.user_roles.includes("Administrator") && !frappe.user_roles.includes("MRV Admin")){
						if(frappe.user_roles.includes("Energy Tracking") && i == user_obj["Energy Tracking"]){
							sector_options += ('\n'+ i)
						}
						if(frappe.user_roles.includes("IPPU Tracking") && i == user_obj["IPPU Tracking"]){
							sector_options += ('\n'+ i)
						}
						if(frappe.user_roles.includes("Agriculture Tracking") && i == user_obj["Agriculture Tracking"]){
							sector_options += ('\n'+ i)
						}
						if(frappe.user_roles.includes("Land Use Tracking") && i == user_obj["Land Use Tracking"]){
							sector_options += ('\n'+ i)
						}
						if(frappe.user_roles.includes("Waste Tracking") && i == user_obj["Waste Tracking"]){
							sector_options += ('\n'+ i)
						}
						if(frappe.user_roles.includes("Other Tracking") && i == user_obj["Other Tracking"]){
							sector_options += ('\n'+ i)
						}
					}
					else{
						sector_options += ('\n'+ i)
					}
					
				}

				cur_frm.fields_dict.sector.df.options = sector_options
				frm.refresh_field('sector')
			})
		}
		else{
			cur_frm.fields_dict.sector.df.options = frm.doc.sector
			frm.refresh_field('sector')

			cur_frm.fields_dict.category.df.options = frm.doc.category
			frm.refresh_field('category')
			
			cur_frm.fields_dict.sub_sector.df.options = frm.doc.sub_sector
			frm.refresh_field('sub_sector')

			cur_frm.fields_dict.sub_category.df.options = frm.doc.sub_category
			frm.refresh_field('sub_category')
		}
		


		

		if (frm.doc.__islocal || frm.doc.work_state != "Approved" || frm.doc.workflow_state == "Approved"){
			frm.fields_dict.edit_button.df.hidden = 1
			frm.refresh_field("edit_button")
		}

		frm.call({
			doc:frm.doc,
			method:'table_list',
			async:false,
			callback: function(r){
				for (var i of r.message){
					var table_name = ""
					var parts = i.split("_");
					parts.shift();
					table_name = parts.join("_");
					if(frm.doc.work_state =="Approved" && (frm.doc.workflow_state == "Draft" || frm.doc.workflow_state == "Pending" || frm.doc.workflow_state =="Rejected") && frm.doc[i].length != 0){
						frm.fields_dict[table_name].df.read_only = 1
						frm.refresh_field(table_name)
						frm.fields_dict.edit_button.df.hidden = 0
						frm.refresh_field("edit_button")
					}
					else{
						frm.fields_dict[table_name].df.read_only = 0
						frm.refresh_field(table_name)
						frm.fields_dict.edit_button.df.hidden = 1
						frm.refresh_field("edit_button")
					}
				}
			}
		})

		if(frm.doc.sub_category != ""){
			

			frm.call({
				doc:frm.doc,
				method:"get_table",
				async:false,
				callback:function(r){
					for (var i of r.message){
						$(`[data-fieldname=${i}] [class="control-label"]`).prop("textContent",`${frm.doc.sub_category}`)
						frm.refresh_field(i)
					}
				
				}
			})

		
			frm.call({
				doc:frm.doc,
				method:"table_list",
				async:false,
				callback:function(r){
					for (var i of r.message){
						$(`[data-fieldname=${i}] [class="control-label"]`).prop("textContent",'Edited '+`${frm.doc.sub_category}`  + ' table')
						frm.refresh_field(i)
					}
				
				}
			})
		}
		for (let field of not_hidden_table_fields){

			if(["reference_approach","electricity_generation","transport","manufacturing_industries","other_sectors","other_energy","international_bunkers"].includes(field) && frm.doc[field].length != 0){
				
				frappe.db.get_list('Energy Fuel Master List',{
					fields : ['fuel_type'],
					order_by : 'fuel_type asc',
					group_by:'fuel_type',
					pluck: 'fuel_type'
				}).then(r =>{
					var fuel_type_options = ""
					for (var i of r){
						fuel_type_options += ('\n'+ i)
					}
					
					for (let row =0; row < frm.doc[field].length;row++){
						cur_frm.fields_dict[field].grid.grid_rows[row].columns.fuel_type.df.options = fuel_type_options
						frm.refresh_field(field)
						
						frappe.db.get_list('Energy Fuel Master List',{
							fields : ['fuel'],
							filters:{fuel_type:frm.doc[field][row].fuel_type},
							pluck: 'fuel'
						})
						.then(r =>{
							
							var fuel_options = ""
		
							for (var i of r){
								fuel_options += ('\n'+ i)
							}
							cur_frm.fields_dict[field].grid.grid_rows[row].columns.fuel.df.options = fuel_options
						
						})

					}
					frm.refresh_field(field)
				})
			}
		}


			
		// 	// if(.fuel_type){
		// 	// 	frappe.db.get_list('Energy Fuel Master List',{
		// 	// 		fields : ['fuel'],
		// 	// 		filters:{fuel_type:d.fuel_type},
		// 	// 		order_by : 'fuel asc',
		// 	// 		pluck: 'fuel'
		// 	// 	}).then(r =>{
		// 	// 		var fuel_options = ""
		// 	// 		for (var i of r){
		// 	// 			fuel_options += ('\n'+ i)
		// 	// 		}
		// 	// 		if(cur_frm.doc.electricity_generation.length != 0 && frm.doc.sub_sector=="1.A.1. Energy industries"){
		// 	// 			cur_frm.grids[1].grid.grid_rows[d.idx-1].columns.fuel.df.options = fuel_options
		// 	// 			frm.refresh_field('electricity_generation')
		// 	// 			}
		// 	// 		if(cur_frm.doc.manufacturing_industries.length != 0 && frm.doc.sub_sector=="1.A.2 Manufacturing industries and construction"){
		// 	// 			cur_frm.grids[2].grid.grid_rows[d.idx-1].columns.fuel.df.options = fuel_options
		// 	// 			frm.refresh_field('manufacturing_industries')
		// 	// 			}
		// 	// 		if(cur_frm.doc.transport.length != 0 && frm.doc.sub_sector=="1.A.3. Transport"){
		// 	// 			cur_frm.grids[3].grid.grid_rows[d.idx-1].columns.fuel.df.options = fuel_options
		// 	// 			frm.refresh_field('transport')
		// 	// 			}
		// 	// 		if(cur_frm.doc.other_sectors.length != 0 && frm.doc.sub_sector=="1.A.4. Other sectors"){
		// 	// 			cur_frm.grids[4].grid.grid_rows[d.idx-1].columns.fuel.df.options = fuel_options
		// 	// 			frm.refresh_field('other_sectors')
		// 	// 			}
		// 	// 		if(cur_frm.doc.other_energy.length != 0 && frm.doc.sub_sector=="1.A.5. Other"){
		// 	// 			cur_frm.grids[5].grid.grid_rows[d.idx-1].columns.fuel.df.options = fuel_options
		// 	// 			frm.refresh_field('other_energy')
		// 	// 			}
		// 	// 		if(cur_frm.doc.international_bunkers.length != 0 && frm.doc.sub_sector=="1.D.1. International bunkers"){
		// 	// 			cur_frm.grids[6].grid.grid_rows[d.idx-1].columns.fuel.df.options = fuel_options
		// 	// 			frm.refresh_field('international_bunkers')
		// 	// 			}
		// 	// 	});
		// 	// }
		// }
		// if(frm.doc.sub_sector == '3.C.6. Indirect N2O Emissions from manure management'){
		// 	// frm.fields_dict.indirect_manure_management.df.hidden = 0
		// 	frm.refresh_field('indirect_manure_management')
		// }
		// else{
		// 	frm.doc.indirect_manure_management = []
		// 	// frm.fields_dict.indirect_manure_management.df.hidden = 1
		// 	frm.refresh_field('indirect_manure_management')
		// }

		// cur_frm.fields_dict.category.df.options = ''
		// frm.refresh_field('category')
		
		// cur_frm.fields_dict.sub_sector.df.options = ''
		// frm.refresh_field('sub_sector')

		// cur_frm.fields_dict.sub_category.df.options = ''
		// frm.refresh_field('sub_category')	
		// if (frm.doc.workflow_state == "Approved" || frm.doc.__islocal){
		// 	$('[id="ghg-inventory-tab1"]').addClass("active")
		// }
	},
	

	before_save:function(frm){
   
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
		
		
		
		frm.call({
			doc:frm.doc,
			method:'table_list',
			async:false,
			callback: function(r){
				for (var i of r.message){

					if (frm.doc.workflow_state == "Rejected"){
						frm.set_value(i,[])
						frm.save()
					}

					if(frm.doc.workflow_state == "Approved"){
						if (frm.doc.work_state == "Approved" && (frm.doc[i].length != 0 || frm.doc.ghg_inventory_details.length != 0)){

							for (let row of frm.doc.ghg_inventory_details){
								frm.set_value(row.field_name,row.new_values)
							}



							if(frm.doc[i].length!=0){
								frm.call({
									doc:frm.doc,
									method:"after_saving_table",
									async:false,
									callback:function(res){
									}
								})
								
							}
							frm.set_value(i,[])
							frm.refresh_field(i)	
							
							
						}
						frm.set_value("ghg_inventory_details",[])
						frm.set_value('work_state','Approved')
					}
				}
			}
		})
		frm.call({
			doc:frm.doc,
			method:'table_name_list',
			async:false,
			callback: function(r){
				for (var i of r.message){
					if(frm.doc.work_state == "Approved"){
						if (frm.doc.workflow_state != "Approved"  && !frm.doc.__islocal){

							if(frm.fields_dict[i].df.read_only == 0){
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

									for (var i of frm.doc.ghg_inventory_details){

										if (field_name_list.includes(i.field_name) ){
											i.new_values = frm.doc[`${i.field_name}`].toString()
											frm.set_value(i.field_name,i.old_values)
											frm.refresh_field("ghg_inventory_details")

											const index = field_name_list.indexOf(i.field_name);
											const x = field_name_list.splice(index, 1)
										}
									}
									if (field_name_list){

										for (var i of field_name_list){
											var label = i.replaceAll("_"," ")
											label = toTitleCase(label)
											var child =frm.add_child("ghg_inventory_details")
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
				}
			}
		})

	},

	edit_button:function(frm,cdt,cdn){
		
		frm.call({
			doc:frm.doc,
			method:'edited_table_list',
			async:false,
			callback: function(r){
				for(var [key,value] of Object.entries(r.message)){
					var table_name = ""
					var parts = key.split("_");
					parts.shift();
					table_name = parts.join("_");
					if(frm.doc.work_state =="Approved" && (frm.doc.workflow_state == "Draft" || frm.doc.workflow_state == "Pending" || frm.doc.workflow_state =="Rejected") && frm.doc[key].length != 0){
						var counter1=0
						frm.set_value(table_name,[])
						for (var i of value){
							if (counter1 == 0){
								counter1 = 1
								for(var row of frm.doc[key]){
									var child = frm.add_child(table_name)
									child[i] = row[i]
								}
							}
							else{
								for(var j=0;j<frm.doc[key].length;j++){
									frm.doc[table_name][j][i] = frm.doc[key][j][i]
									frm.refresh_field(table_name);
								}
								
							}
							
						}
						
						frm.fields_dict[table_name].df.read_only = 0
						frm.fields_dict.edit_button.df.hidden = 1
						frm.refresh_field("edit_button")
						frm.refresh_field(table_name)
					}

					

				}
			}
		})
		for (let field of not_hidden_table_fields){

			if(["reference_approach","electricity_generation","transport","manufacturing_industries","other_sectors","other_energy","international_bunkers"].includes(field) && frm.doc[field].length != 0){
				
				frappe.db.get_list('Energy Fuel Master List',{
					fields : ['fuel_type'],
					order_by : 'fuel_type asc',
					group_by:'fuel_type',
					pluck: 'fuel_type'
				}).then(r =>{
					var fuel_type_options = ""
					for (var i of r){
						fuel_type_options += ('\n'+ i)
					}
					for (let row =0; row < frm.doc[field].length;row++){
						cur_frm.fields_dict[field].grid.grid_rows[row].columns.fuel_type.df.options = fuel_type_options
						frm.refresh_field(field)
						
						frappe.db.get_list('Energy Fuel Master List',{
							fields : ['fuel'],
							filters:{fuel_type:frm.doc[field][row].fuel_type},
							pluck: 'fuel'
						})
						.then(r =>{
							
							var fuel_options = ""
		
							for (var i of r){
								fuel_options += ('\n'+ i)
							}
							cur_frm.fields_dict[field].grid.grid_rows[row].columns.fuel.df.options = fuel_options
						
						})

					}
					frm.refresh_field(field)
				})
			}
		}
		// frm.call({
		// 	doc:frm.doc,
		// 	method:'edit_table',
		// 	async:false,
		// 	callback: function(r){
		// 		for (var i of r.message){
		// 			if(frm.doc.work_state =="Approved" && (frm.doc.workflow_state == "Draft" || frm.doc.workflow_state == "Pending" || frm.doc.workflow_state =="Rejected")){
		// 				frm.call({
		// 					doc:frm.doc,
		// 					method:"after_saving_table",
		// 					async:false,
		// 					callback:function(res){
		// 					}
		// 				})
		// 				frm.set_value(i,[])
		// 				frm.refresh_field(i)
		// 			}
		// 			// frm.set_value("ghg_inventory_details",[])
		// 			frm.set_value('work_state','Approved')
		// 			frm.save()
		// 		}
				
		// 	}
		// })
	},

	sector: function(frm){

		dynamicTitleList[0] = frm.doc.sector
		dynamicTitleList[1] = ''
		dynamicTitleList[2] = ''
		dynamicTitleList[3] = ''
		frm.set_value('dynamic_title',dynamicTitleList.join(''))
		frm.refresh_field('dynamic_title')
		frm.set_value('approach','')
		frm.refresh_field('approach')

		
		frappe.db.get_list('GHG Category',{
			filters : {sector:frm.doc.sector},
			order_by : 'name asc',
			pluck: 'name'
		}).then(r =>{
			cur_frm.fields_dict.category.df.options = ''
			frm.refresh_field('category')
			
			cur_frm.fields_dict.sub_sector.df.options = ''
			frm.refresh_field('sub_sector')

			cur_frm.fields_dict.sub_category.df.options = ''
			frm.refresh_field('sub_category')
			var category_options = ""
			for (var i of r){
				category_options += ('\n'+ i)
			}
			frm.set_value('category','')
			cur_frm.fields_dict.category.df.options = category_options
			frm.refresh_field('category')
		});

		// frm.set_query("category", function(){
        //     return {
        //         filters: {
        //             sector : frm.doc.sector
        //         }
        //     }
        // });
		// frm.set_value('category',"")
		// frm.refresh_field('category')
		if (frm.doc.sector == "1. Energy"){
			frm.fields_dict.approach.df.hidden = 0
			frm.refresh_field('approach')

			frm.fields_dict.category.df.hidden = 1
			frm.refresh_field('category')

			frm.fields_dict.sub_category.df.hidden = 1
			frm.refresh_field('sub_category')

			frm.fields_dict.sub_sector.df.hidden = 1
			frm.refresh_field('sub_sector')
		}
		else if(frm.doc.sector == ""){
			frm.fields_dict.approach.df.hidden = 1
			frm.refresh_field('approach')

			frm.fields_dict.category.df.hidden = 1
			frm.refresh_field('category')

			frm.fields_dict.sub_category.df.hidden = 1
			frm.refresh_field('sub_category')

			frm.fields_dict.sub_sector.df.hidden = 1
			frm.refresh_field('sub_sector')
		}
		else{
			frm.set_value('approach',"")
			frm.refresh_field('approach')

			frm.fields_dict.approach.df.hidden = 1
			frm.refresh_field('approach')

			frm.fields_dict.category.df.hidden = 0
			frm.refresh_field('category')

			frm.fields_dict.sub_category.df.hidden = 0
			frm.refresh_field('sub_category')

			frm.fields_dict.sub_sector.df.hidden = 0
			frm.refresh_field('sub_sector')

			
		};


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
		// frm.set_query("category", function(){
        //     return {
        //         filters: {
        //             sector : frm.doc.sector
        //         }
        //     }
        // });
		// frm.set_value('category',"")
		// frm.refresh_field('category')
	},
	approach:function(frm){

		dynamicTitleList[1] = "/"+frm.doc.approach
		dynamicTitleList[2] = ''
		dynamicTitleList[3] = ''
		frm.set_value('dynamic_title',dynamicTitleList.join(''))
		frm.refresh_field('dynamic_title')

		if (frm.doc.approach == 'Sectoral Approach'){

			frm.set_value('category','')
			frm.fields_dict.category.df.hidden = 0
			frm.refresh_field('category')

			frm.set_value('sub_category','')
			frm.fields_dict.sub_category.df.hidden = 0
			frm.refresh_field('sub_category')

			frm.set_value('sub_sector','')
			frm.fields_dict.sub_sector.df.hidden = 0
			frm.refresh_field('sub_sector')
		}
		else if (frm.doc.approach == 'Reference Approach'){
		// 	// frm.fields_dict.reference_approach.df.hidden = 0
		// 	frm.refresh_field('reference_approach')
		
			not_hidden_table_fields = []
			
			var data = frappe.get_meta('GHG Inventory');
			for (var field of data.fields) {
				if (field.fieldtype === 'Table') {
					if(!field.fieldname.startsWith('edited') && field.fieldname !== 'ghg_inventory_details'){
						tableFields.push(field.fieldname);
						if(frm.fields_dict[field.fieldname].df.hidden_due_to_dependency == undefined || frm.fields_dict[field.fieldname].df.hidden_due_to_dependency == false){
							not_hidden_table_fields.push(field.fieldname)
						}
					}
				}
			}
			

			frm.set_value('category','')
			frm.fields_dict.category.df.hidden = 1
			frm.refresh_field('category')

			frm.set_value('sub_category','')
			frm.fields_dict.sub_category.df.hidden = 1
			frm.refresh_field('sub_category')

			frm.set_value('sub_sector','')
			frm.fields_dict.sub_sector.df.hidden = 1
			frm.refresh_field('sub_sector')
		}
		else if(frm.doc.sector =='1. Energy' && !frm.doc.approach){
			frm.fields_dict.category.df.hidden = 1
			frm.refresh_field('category')

			frm.fields_dict.sub_category.df.hidden = 1
			frm.refresh_field('sub_category')

			frm.fields_dict.sub_sector.df.hidden = 1
			frm.refresh_field('sub_sector')
		}
		// else{
		// 	// frm.fields_dict.reference_approach.df.hidden = 1
		// 	frm.refresh_field('reference_approach')
		// }
	},
	category: function(frm){
		if(frm.doc.category){
		dynamicTitleList[1] = "/"+frm.doc.category}
		dynamicTitleList[2] = ''
		dynamicTitleList[3] = ''
		frm.set_value('dynamic_title',dynamicTitleList.join(''))
		frm.refresh_field('dynamic_title')
		if(frm.doc.year){
			
			population_calculation(frm)

			if (frm.doc.category == '5.A. Solid waste disposal'){
				frappe.db.exists('Waste Population Master List',frm.doc.year).then(exists =>{
					if (exists){
					frappe.db.get_doc('Waste Population Master List',frm.doc.year).then(
						doc => {
							frm.doc.solid_waste = []
							let row = frm.add_child('solid_waste')
							row.urban_population = doc.urban_population
							frm.refresh_field('solid_waste')
						}
					)
					}
					else{
						frappe.show_alert({
							message:__('No Data'),
							// indicator:'orange'
						}, 2);
						frm.doc.solid_waste = []
						frm.refresh_field('solid_waste')
					}
				})
			}

			if (frm.doc.category == '5.D. Wastewater treatment and discharge'){
				frappe.db.exists('Waste Population Master List',frm.doc.year).then(exists =>{
					if (exists){
					frappe.db.get_doc('Waste Population Master List',frm.doc.year).then(
						doc => {
							frm.doc.ch4_wastewater_treatment = []
							frm.doc.n2o_wastewater_treatment = []
							frm.add_child('ch4_wastewater_treatment',{
								population : doc.total_population
							})
							frm.refresh_field('ch4_wastewater_treatment')
							frm.add_child('n2o_wastewater_treatment',{
								population : doc.total_population
							})
							frm.refresh_field('n2o_wastewater_treatment')
						}
					)
					}
					else{
						frappe.show_alert({
							message:__('No Data'),
							// indicator:'orange'
						}, 2);
						frm.doc.ch4_wastewater_treatment = []
						frm.doc.n2o_wastewater_treatment = []
						frm.refresh_field('ch4_wastewater_treatment')
						frm.refresh_field('n2o_wastewater_treatment')
					}
				})
			}
			if (frm.doc.category == '5.C. Incineration and open burning of waste'){
				frappe.db.exists('Waste Population Master List',frm.doc.year).then(exists =>{
					if (exists){
					frappe.db.get_doc('Waste Population Master List',frm.doc.year).then(
						doc => {
							frm.doc.open_burning_of_waste = []
							frm.add_child('open_burning_of_waste',{
								urban_population : doc.total_population
							})
							frm.refresh_field('open_burning_of_waste')
						}
					)
					}
					else{
						frappe.show_alert({
							message:__('No Data'),
							// indicator:'orange'
						}, 2);
						frm.doc.ch4_wastewater_treatment = []
						frm.doc.n2o_wastewater_treatment = []
						frm.refresh_field('ch4_wastewater_treatment')
						frm.refresh_field('n2o_wastewater_treatment')
					}
				})
			}
		}
		
		frappe.db.get_list('GHG Sub Sector',{
			filters : {category:frm.doc.category},
			order_by : 'name asc',
			pluck: 'name'
		}).then(r =>{
			var sub_sector_options = ""
			for (var i of r){
				sub_sector_options += ('\n'+ i)
			}
			frm.set_value('sub_sector','')
			frm.set_value('sub_category','')
			cur_frm.fields_dict.sub_sector.df.options = sub_sector_options
			frm.refresh_field('sub_sector')
		});

		if(frm.doc.category == '4.A. Forest land'){
			frappe.db.get_list('Forest Category Master List', {
				fields: ['category'],
				filters:{'link_category':frm.doc.category},
				order_by:'category'
			}).then(records => {
				for(var i in records){
					var child = frm.add_child(`forest_land`)
					child.forest_category = records[i].category
					frm.refresh_field(`forest_land`)
					
				}
			})
		}
		else{
			frm.doc.forest_land = []
			// frm.fields_dict.forest_land.df.hidden = 1
			frm.refresh_field(`forest_land`)
		}
			if(frm.doc.category == '4.B. Cropland'){
				frappe.db.get_list('Forest Category Master List', {
					fields: ['category'],
					filters:{'link_category':frm.doc.category},
					pluck:'category',
					order_by:'category'
				}).then(records => {
					for(var i of records){
						var child = frm.add_child(`cropland`)
						child.forest_category = i
					}
					frm.refresh_field(`cropland`)
				})
			}
			else{
				frm.doc.cropland = []
				// frm.fields_dict.forest_land.df.hidden = 1
				frm.refresh_field('cropland')
			}
			if(frm.doc.category == '4.C. Grassland'){
				frappe.db.get_list('Forest Category Master List', {
					fields: ['category'],
					filters:{'link_category':frm.doc.category},
					pluck:'category',
					order_by:'category'
				}).then(records => {
					for(var i of records){
						var child = frm.add_child(`grassland`)
						child.forest_category = i
					}
					frm.refresh_field(`grassland`)
				})
			}
			else{
				frm.doc.grassland = []
				frm.refresh_field('grassland')
			}
			if(frm.doc.category == '4.D. Wetlands'){
				frappe.db.get_list('Forest Category Master List', {
					fields: ['category'],
					filters:{'link_category':frm.doc.category},
					pluck:'category',
					order_by:'category'
				}).then(records => {
					for(var i of records){
						var child = frm.add_child(`wetlands`)
						child.forest_category = i
					}
					frm.refresh_field(`wetlands`)
				})
			}
			else{
				frm.doc.wetlands = []
				// frm.fields_dict.wetlands.df.hidden = 1
				frm.refresh_field('wetlands')
			}
			if(frm.doc.category == '4.E. Settlements'){
				frappe.db.get_list('Forest Category Master List', {
					fields: ['category'],
					filters:{'link_category':frm.doc.category},
					pluck:'category',
					order_by:'category'
				}).then(records => {
					for(var i of records){
						var child = frm.add_child(`settlements`)
						child.forest_category = i
					}
					frm.refresh_field(`settlements`)
				})
			}
			else{
				frm.doc.settlements = []
				// frm.fields_dict.settlements.df.hidden = 1
				frm.refresh_field('settlements')
			}
			if(frm.doc.category == '4.F. Other land'){
				frappe.db.get_list('Forest Category Master List', {
					fields: ['category'],
					filters:{'link_category':frm.doc.category},
					pluck:'category',
					order_by:'category'
				}).then(records => {
					for(var i of records){
						var child = frm.add_child(`other_land`)
						child.forest_category = i
					}
					frm.refresh_field(`other_land`)
				})
			}
			else{
				frm.doc.other_land = []
				// frm.fields_dict.other_land.df.hidden = 1
				frm.refresh_field('other_land')
			}

		
	},
	sub_sector: function(frm){
		if (frm.doc.sub_sector){
		dynamicTitleList[2] = "/"+frm.doc.sub_sector}
		dynamicTitleList[3] = ''
		frm.set_value('dynamic_title',dynamicTitleList.join(''))
		frm.refresh_field('dynamic_title')
		if(frm.doc.year){
			population_calculation(frm)
		}
		frappe.db.get_list('GHG Sub Category',{
			filters : {sub_sector:frm.doc.sub_sector},
			order_by : 'name asc',
			pluck: 'name'
		}).then(r =>{
			var sub_category_options = ""
			for (var i of r){
				sub_category_options += ('\n'+ i)
			}
			frm.set_value('sub_category','')
			cur_frm.fields_dict.sub_category.df.options = sub_category_options
			frm.refresh_field('sub_category')
		});

		if(frm.doc.sub_sector == "1.A.5. Other"){
			not_hidden_table_fields = []
			
			var data = frappe.get_meta('GHG Inventory');
			for (var field of data.fields) {
				if (field.fieldtype === 'Table') {
					if(!field.fieldname.startsWith('edited') && field.fieldname !== 'ghg_inventory_details'){
						tableFields.push(field.fieldname);
						if(frm.fields_dict[field.fieldname].df.hidden_due_to_dependency == undefined || frm.fields_dict[field.fieldname].df.hidden_due_to_dependency == false){
							not_hidden_table_fields.push(field.fieldname)
						}
					}
				}
			}
		}

		if(frm.doc.sub_sector=='2.A.1. Cement production'){
			var row = frm.add_child('clinker_data')
			frm.refresh_field("clinker_data")
			
		}
		$.ajax({
			success:function(){
				$('[data-fieldname="clinker_data"] [class="row-index sortable-handle col"]').css("display","none")
				$('[data-fieldname="clinker_data"] [class="row-check sortable-handle col"]').css("display","none")
				$('[data-fieldname="clinker_data"] [class="btn-open-row"]').parent().remove()
				$('[data-fieldname="clinker_data"] [class="col grid-static-col d-flex justify-content-center"]').remove()
			}
		})
		// frm.fields_dict['clinker_data'].$wrapper.find('.row-check sortable-handle col').hide()
		$('[data-fieldname="clinker_data"] [class="small form-clickable-section grid-footer"]').remove()
		frm.refresh_field('clinker_data')

		//Direct N2O Emissions from managed soils//
		if(frm.doc.sub_sector == '3.D.1. Direct N2O emissions from managed soils'){
			var table_name_list = {
				'direct_managed_soils': 'Managed Soils',
			}
				// 'direct_managed_soils':,'direct_flooded_rice','direct_managed_organic_soils','direct_grazed_soils']
			for (let table in table_name_list){
				frm.call({
					doc:cur_frm.doc,
					method:"get_data",
					async:false,
					args:{
						table_name: table_name_list[table]
					},
					callback:function(r){
							frm.doc[`${table}`] = []
							for(var i of r.message){
								var child = frm.add_child(`${table}`)
								child.anthropogenic_n_input= i.anthropogenic_n_input 
								child.reference = i.reference
							}
							frm.refresh_field(`${table}`)
					}
				})
			}
			// frm.fields_dict.direct_managed_soils.df.hidden = 0
			frm.refresh_field('direct_managed_soils')

			// frm.fields_dict.direct_flooded_rice.df.hidden = 0
			frm.refresh_field('direct_flooded_rice')

			// frm.fields_dict.direct_managed_organic_soils.df.hidden = 0
			frm.refresh_field('direct_managed_organic_soils')

			// frm.fields_dict.direct_grazed_soils.df.hidden = 0
			frm.refresh_field('direct_grazed_soils')
		}
		else{
			frm.doc.direct_managed_soils = []
			// frm.fields_dict.direct_managed_soils.df.hidden = 1
			frm.refresh_field('direct_managed_soils')

			frm.doc.direct_flooded_rice = []
			// frm.fields_dict.direct_flooded_rice.df.hidden = 1
			frm.refresh_field('direct_flooded_rice')

			frm.doc.direct_managed_organic_soils = []
			// frm.fields_dict.direct_managed_organic_soils.df.hidden = 1
			frm.refresh_field('direct_managed_organic_soils')

			frm.doc.direct_grazed_soils = []
			// frm.fields_dict.direct_grazed_soils.df.hidden = 1
			frm.refresh_field('direct_grazed_soils')
		}

		//Indirect N2O Emissions from managed soils//
		if(frm.doc.sub_sector == '3.D.2. Indirect N2O Emissions from managed soils'){
			var table_name_list = {
				'atmospheric_deposit': 'N2O Atmospheric Deposition',
				'n2o_from_n_leaching': 'N2O from N Leaching/ Runoff',
				
			}
			for (let table in table_name_list){
				frm.call({
					doc:cur_frm.doc,
					method:"get_data",
					async:false,
					args:{
						table_name: table_name_list[table]
					},
					callback:function(r){
							frm.doc[`${table}`] = []
							for(var i of r.message){
								var child = frm.add_child(`${table}`)
								child.description= i.description
								child.value = i.value
								child.unit= i.unit
								child.reference = i.reference
							}
							frm.refresh_field(`${table}`)
					}
				})
			}
			// frm.fields_dict.atmospheric_deposit.df.hidden = 0
			frm.refresh_field('atmospheric_deposit')

			// frm.fields_dict.n2o_from_n_leaching.df.hidden = 0
			frm.refresh_field('n2o_from_n_leaching')

		}
		else{
			
			frm.doc.atmospheric_deposit = []
			// frm.fields_dict.atmospheric_deposit.df.hidden = 1
			frm.refresh_field('atmospheric_deposit')

			frm.doc.n2o_from_n_leaching = []
			// frm.fields_dict.n2o_from_n_leaching.df.hidden = 1
			frm.refresh_field('n2o_from_n_leaching')
		}

		// //Urea Application//
		// if(frm.doc.sub_sector == '3.C.6. Indirect N2O Emissions from manure management'){
		// 	// frm.fields_dict.indirect_manure_management.df.hidden = 0
		// 	frm.refresh_field('indirect_manure_management')
		// }
		// else{
		// 	frm.doc.indirect_manure_management = []
		// 	// frm.fields_dict.indirect_manure_management.df.hidden = 1
		// 	frm.refresh_field('indirect_manure_management')
		// }
	},
	

	/////////////////////////////////////////////////////////////////////
	/////////// Conditions to Show/Hide Respective Table Fields /////////
	///////////////////////////SUB-CATEGORY//////////////////////////////
	/////////////////////////////////////////////////////////////////////
	sub_category:function(frm){
		if(frm.doc.sub_category){
		dynamicTitleList[3] = "/"+frm.doc.sub_category}
		frm.set_value('dynamic_title',dynamicTitleList.join(''))
		frm.refresh_field('dynamic_title')
		// cur_frm.fields_dict.table_label.df.options = frm.doc.sub_category
		// frm.set_value("table_label",frm.doc.sub_category)
		if(frm.doc.sub_category != ""){
			frm.call({
				doc:frm.doc,
				method:"get_table",
				async:false,
				callback:function(r){
					for (var i of r.message){
						$(`[data-fieldname=${i}] [class="control-label"]`).prop("textContent",`${frm.doc.sub_category}`)
						frm.refresh_field(i)
					}
				
				}
			})
			
		}
		if(frm.doc.sector == "1. Energy"){
			not_hidden_table_fields = []
			
			var data = frappe.get_meta('GHG Inventory');
			for (var field of data.fields) {
				if (field.fieldtype === 'Table') {
					if(!field.fieldname.startsWith('edited') && field.fieldname !== 'ghg_inventory_details'){
						tableFields.push(field.fieldname);
						if(frm.fields_dict[field.fieldname].df.hidden_due_to_dependency == undefined || frm.fields_dict[field.fieldname].df.hidden_due_to_dependency == false){
							not_hidden_table_fields.push(field.fieldname)
						}
					}
				}
			}
		}
		// cur_frm.fields_dict.table_label.df.label = frm.doc.sub_category
		// frm.update_docfield_property('manufacturing_industries','label','Hello')
		// frm.refresh_field('manufacturing_industries')
		// if(frm.doc.sub_category == '1.A.1.a.i. Electricity generation'){
		// 	// frm.fields_dict.electricity_generation.df.hidden = 0
		// 	frm.refresh_field('electricity_generation')
		// }
		// else{
			
		// 	frm.doc.electricity_generation = []
		// 	// frm.fields_dict.electricity_generation.df.hidden = 1
		// 	frm.refresh_field('electricity_generation')
		// }
	},


	year: async function(frm){

		population_calculation(frm)

		if (frm.doc.category == '5.A. Solid waste disposal'){
			frappe.db.exists('Waste Population Master List',frm.doc.year).then(exists =>{
				if (exists){
				frappe.db.get_doc('Waste Population Master List',frm.doc.year).then(
					doc => {
						frm.doc.solid_waste = []
						let row = frm.add_child('solid_waste')
						row.urban_population = doc.urban_population
						frm.refresh_field('solid_waste')
					}
				)
				}
				else{
					frappe.show_alert({
						message:__('No Data'),
						// indicator:'orange'
					}, 2);
					frm.doc.solid_waste = []
					frm.refresh_field('solid_waste')
				}
			})
		}

		if (frm.doc.category == '5.D. Wastewater treatment and discharge'){
			frappe.db.exists('Waste Population Master List',frm.doc.year).then(exists =>{
				if (exists){
				frappe.db.get_doc('Waste Population Master List',frm.doc.year).then(
					doc => {
						frm.doc.ch4_wastewater_treatment = []
						frm.doc.n2o_wastewater_treatment = []
						frm.add_child('ch4_wastewater_treatment',{
							population : doc.total_population
						})
						frm.refresh_field('ch4_wastewater_treatment')
						frm.add_child('n2o_wastewater_treatment',{
							population : doc.total_population
						})
						frm.refresh_field('n2o_wastewater_treatment')
					}
				)
				}
				else{
					frappe.show_alert({
						message:__('No Data'),
						// indicator:'orange'
					}, 2);
					frm.doc.ch4_wastewater_treatment = []
					frm.doc.n2o_wastewater_treatment = []
					frm.refresh_field('ch4_wastewater_treatment')
					frm.refresh_field('n2o_wastewater_treatment')
				}
			})
		}
		if (frm.doc.category == '5.C. Incineration and open burning of waste'){
			frappe.db.exists('Waste Population Master List',frm.doc.year).then(exists =>{
				if (exists){
				frappe.db.get_doc('Waste Population Master List',frm.doc.year).then(
					doc => {
						frm.doc.open_burning_of_waste = []
						frm.add_child('open_burning_of_waste',{
							urban_population : doc.total_population
						})
						frm.refresh_field('open_burning_of_waste')
					}
				)
				}
				else{
					frappe.show_alert({
						message:__('No Data'),
						// indicator:'orange'
					}, 2);
					frm.doc.ch4_wastewater_treatment = []
					frm.doc.n2o_wastewater_treatment = []
					frm.refresh_field('ch4_wastewater_treatment')
					frm.refresh_field('n2o_wastewater_treatment')
				}
			})
		}

		// let mappedData = {
		// 	'Sub Category':{
		// 		'1.A.1.a.i. Electricity generation':'electricity_generation',
		// 	},
		// 	'Sub Sector':{
		// 		'1.A.3. Transport':'transport',
		// 		'1.A.4. Other sectors':'others',
		// 		'2.D.1. Lubricant use':'lubricant_use',
		// 		'3.A.1. Enteric Fermentation':'enteric_fermentation',
		// 		'3.A.2. Manure Management':'manure_management',
		// 		'3.B.1. Forest Land':'forest_land',
		// 		'3.C.3. Urea Application':'urea_application',
		// 		'3.C.4. Direct N2O Emissions from managed soils':['direct_managed_soils','direct_flooded_rice',
		// 													  'direct_managed_organic_soils','direct_grazed_soils'],
		// 		'3.C.5. Indirect N2O Emissions from managed soils':['atmospheric_deposit','n2o_from_n_leaching'],
		// 		'3.C.6. Indirect N2O Emissions from manure management':'indirect_manure_management',
		// 	},
		// 	'Category':{
		// 		'4.A. Solid Waste Disposal':'solid_waste',
		// 		'4.D. Wastewater Treatment and Discharge':['ch4_wastewater_treatment',
		// 											   'n2o_wastewater_treatment','industrial_wastewater_treatment']
		// 	},
		// 	'Reference Approach':'reference_approach',
		// }
		// if(frm.doc.sub_category){

		// }
		// else if(frm.doc.sub_sector){
		// 	if(frm.doc.sub_sector in mappedData['Sub Sector']){

		// 	}
		// }
		// else if(frm.doc.category){

		// }
	}

	// table_type: function(frm){
	// 	// var table =''
	// 	// var table_name_values = frm.doc.table_type
	// 	// table_name_values = table_name_values.split(" ")
	// 	// table_name_values.unshift('direct')
	// 	// table = table_name_values.join("_")
	// 	// table = table.toLowerCase()

	// 	let table_name_list = ['direct_managed_soils','direct_flooded_rice','direct_managed_organic_soils','direct_grazed_soils']
	// 	frm.call({
	// 		doc:cur_frm.doc,
	// 		method:"get_data",
	// 		async:false,
	// 		args:{
	// 			table_name:frm.doc.table_type
	// 		},
	// 		callback:function(r){
	// 			for (var table of table_name_list){ 
	// 				frm.doc[`${table}`] = []
	// 				for(var i of r.message){
	// 					var child = frm.add_child(`${table}`)
	// 					child.anthropogenic_n_input= i.anthropogenic_n_input
	// 					child.amount = i.amount
	// 					child.emission_factor= i.emission_factor
	// 					child.reference = i.reference
	// 				}
	// 				frm.refresh_field(`${table}`)
	// 			}
	// 		}
	// 	})
	// }

});
frappe.ui.form.on('Forest Land ChildTable',{
area_ha:function(frm){
		var categoryName = frm.doc.category.toLowerCase().split(' ').slice(1).join('_');
		var totalArea = 0;
		for (var i = 2; i < frm.doc[categoryName].length; i++) {
			var row = frm.doc[categoryName][i];
			totalArea += row.area_ha || 0;	
		}
		var secondRow = frm.doc[categoryName][1];
		secondRow.area_ha = totalArea;
		frm.refresh_field(categoryName);
		cur_frm.fields_dict[categoryName].grid.grid_rows[1].docfields.forEach(function(field) {
				field.read_only = 1;
			
		});
		
		// Refresh the child table to reflect the changes
		cur_frm.fields_dict[categoryName].grid.refresh();
	
},
ghg_emissions_tco2:function(frm){
	var categoryName = frm.doc.category.toLowerCase().split(' ').slice(1).join('_');
	var totalGHGEmissions  = 0;
	for (var i = 2; i < frm.doc[categoryName].length; i++) {
		var row = frm.doc[categoryName][i];
		totalGHGEmissions  += row.ghg_emissions_tco2 || 0;	
	}
	var secondRow = frm.doc[categoryName][1];
	secondRow.ghg_emissions_tco2 = totalGHGEmissions ;
	frm.refresh_field(categoryName);
	cur_frm.fields_dict[categoryName].grid.grid_rows[1].docfields.forEach(function(field) {
		field.read_only = 1;
	
});

// Refresh the child table to reflect the changes
cur_frm.fields_dict[categoryName].grid.refresh();
}
})
frappe.ui.form.on('Energy Reference ChildTable',{
	reference_approach_add(frm, cdt, cdn) {
		var d = locals[cdt][cdn]
		frappe.db.get_list('Energy Fuel Master List',{
			fields : ['fuel_type'],
			order_by : 'fuel_type asc',
			group_by:'fuel_type',
			pluck: 'fuel_type'
		}).then(r =>{
			var fuel_type_options = ""
			for (var i of r){
				fuel_type_options += ('\n'+ i)
			}
			cur_frm.grids[0].grid.grid_rows[d.idx-1].columns.fuel_type.df.options = fuel_type_options
			frm.refresh_field('reference_approach')
		});
	},
	fuel_type:function(frm,cdt,cdn){
		var d = locals[cdt][cdn]
		frappe.db.get_list('Energy Fuel Master List',{
			fields : ['fuel'],
			filters:{fuel_type:d.fuel_type},
			order_by : 'fuel asc',
			pluck: 'fuel'
		}).then(r =>{
			for(var i of frm.doc.reference_approach){
				if(r.includes(i.fuel)){
					const index = r.indexOf(i.fuel);
					if (index > -1) { // only splice array when item is found
						r.splice(index, 1); // 2nd parameter means remove one item only
						}
				} 
			}
			var fuel_options = ""
			for (var i of r){
				fuel_options += ('\n'+ i)
			}
			if(cur_frm.doc.reference_approach.length != 0 && frm.doc.approach=="Reference Approach"){
				cur_frm.grids[0].grid.grid_rows[d.idx-1].columns.fuel.df.options = fuel_options
				frm.refresh_field('reference_approach')
			}
		})
	}
})

frappe.ui.form.on('Energy Sector ChildTable', {
	electricity_generation_add(frm, cdt, cdn) {
		var d = locals[cdt][cdn]
		frappe.db.get_list('Energy Fuel Master List',{
			fields : ['fuel_type'],
			order_by : 'fuel_type asc',
			group_by:'fuel_type',
			pluck: 'fuel_type'
		}).then(r =>{
			var fuel_type_options = ""
			for (var i of r){
				fuel_type_options += ('\n'+ i)
			}
			cur_frm.grids[1].grid.grid_rows[d.idx-1].columns.fuel_type.df.options = fuel_type_options
			frm.refresh_field('electricity_generation')
		});
	},
	manufacturing_industries_add(frm, cdt, cdn) {
		var d = locals[cdt][cdn]
		frappe.db.get_list('Energy Fuel Master List',{
			fields : ['fuel_type'],
			order_by : 'fuel_type asc',
			group_by:'fuel_type',	
			pluck: 'fuel_type'
		}).then(r =>{
			var fuel_type_options = ""
			for (var i of r){
				fuel_type_options += ('\n'+ i)
			}
			cur_frm.grids[2].grid.grid_rows[d.idx-1].columns.fuel_type.df.options = fuel_type_options
			frm.refresh_field('manufacturing_industries')
		});
	},
    transport_add(frm, cdt, cdn) {
			var d = locals[cdt][cdn]
			frappe.db.get_list('Energy Fuel Master List',{
				fields : ['fuel_type'],
				order_by : 'fuel_type asc',
				group_by:'fuel_type',
				pluck: 'fuel_type'
			}).then(r =>{
				var fuel_type_options = ""
				for (var i of r){
					fuel_type_options += ('\n'+ i)
				}
				cur_frm.grids[3].grid.grid_rows[d.idx-1].columns.fuel_type.df.options = fuel_type_options
				frm.refresh_field('transport')
			});
    },
	other_sectors_add(frm, cdt, cdn) {
			var d = locals[cdt][cdn]
			frappe.db.get_list('Energy Fuel Master List',{
				fields : ['fuel_type'],
				order_by : 'fuel_type asc',
				group_by:'fuel_type',
				pluck: 'fuel_type'
			}).then(r =>{
				var fuel_type_options = ""
				for (var i of r){
					fuel_type_options += ('\n'+ i)
				}
				cur_frm.grids[4].grid.grid_rows[d.idx-1].columns.fuel_type.df.options = fuel_type_options
				frm.refresh_field('other_sectors')
		});
	},
	other_energy_add(frm, cdt, cdn) {
			var d = locals[cdt][cdn]
			frappe.db.get_list('Energy Fuel Master List',{
				fields : ['fuel_type'],
				order_by : 'fuel_type asc',
				group_by:'fuel_type',
				pluck: 'fuel_type'
			}).then(r =>{
				var fuel_type_options = ""
				for (var i of r){
					fuel_type_options += ('\n'+ i)
				}
				cur_frm.grids[5].grid.grid_rows[d.idx-1].columns.fuel_type.df.options = fuel_type_options
				frm.refresh_field('other_energy')
		});
	},
	international_bunkers_add(frm, cdt, cdn) {
			var d = locals[cdt][cdn]
			frappe.db.get_list('Energy Fuel Master List',{
				fields : ['fuel_type'],
				order_by : 'fuel_type asc',
				group_by:'fuel_type',
				pluck: 'fuel_type'
			}).then(r =>{
				var fuel_type_options = ""
				for (var i of r){
					fuel_type_options += ('\n'+ i)
				}
				cur_frm.grids[6].grid.grid_rows[d.idx-1].columns.fuel_type.df.options = fuel_type_options
				frm.refresh_field('international_bunkers')
		});
	},
	
	fuel_type:function(frm,cdt,cdn){
		var d = locals[cdt][cdn]
		frappe.db.get_list('Energy Fuel Master List',{
			fields : ['fuel'],
			filters:{fuel_type:d.fuel_type},
			order_by : 'fuel asc',
			pluck: 'fuel'
		}).then(r =>{
			for (let field of not_hidden_table_fields){
				
				for(let i of frm.doc[field]){
					if(r.includes(i.fuel)){
						const index = r.indexOf(i.fuel);
						if (index > -1) { // only splice array when item is found
							r.splice(index, 1); // 2nd parameter means remove one item only
							}
					} 
				}

				var fuel_options = ""

				for (let i of r){
					fuel_options += ('\n'+ i)
				}
				cur_frm.fields_dict[field].grid.grid_rows[d.idx-1].columns.fuel.df.options = fuel_options
				frm.refresh_field(field)
			}
				

				// for(var i of not_hidden_table_fields){
				// 	if(r.includes(i.fuel)){
				// 		const index = r.indexOf(i.fuel);
				// 		if (index > -1) { // only splice array when item is found
				// 			r.splice(index, 1); // 2nd parameter means remove one item only
				// 			}
				// 	} 
				// }
				// var fuel_options = ""
				// for (var i of r){
				// 	fuel_options += ('\n'+ i)
				// }
				// if(cur_frm.doc.electricity_generation.length != 0 && frm.doc.sub_sector=="1.A.1. Energy industries"){
				// 	cur_frm.grids[1].grid.grid_rows[d.idx-1].columns.fuel.df.options = fuel_options
				// 	frm.refresh_field('electricity_generation')
				// 	}
				// if(cur_frm.doc.manufacturing_industries.length != 0 && frm.doc.sub_sector=="1.A.2 Manufacturing industries and construction"){
				// 	cur_frm.grids[2].grid.grid_rows[d.idx-1].columns.fuel.df.options = fuel_options
				// 	frm.refresh_field('manufacturing_industries')
				// 	}
				// if(cur_frm.doc.transport.length != 0 && frm.doc.sub_sector=="1.A.3. Transport"){
				// 	cur_frm.grids[3].grid.grid_rows[d.idx-1].columns.fuel.df.options = fuel_options
				// 	frm.refresh_field('transport')
				// 	}
				// if(cur_frm.doc.other_sectors.length != 0 && frm.doc.sub_sector=="1.A.4. Other sectors"){
				// 	cur_frm.grids[4].grid.grid_rows[d.idx-1].columns.fuel.df.options = fuel_options
				// 	frm.refresh_field('other_sectors')
				// 	}
				// if(cur_frm.doc.other_energy.length != 0 && frm.doc.sub_sector=="1.A.5. Other"){
				// 	cur_frm.grids[5].grid.grid_rows[d.idx-1].columns.fuel.df.options = fuel_options
				// 	frm.refresh_field('other_energy')
				// 	}
				// if(cur_frm.doc.international_bunkers.length != 0 && frm.doc.sub_sector=="1.D.1. International bunkers"){
				// 	cur_frm.grids[6].grid.grid_rows[d.idx-1].columns.fuel.df.options = fuel_options
				// 	frm.refresh_field('international_bunkers')
				// 	}
			})
		}
});

frappe.ui.form.on('IPPU Chemical ChildTable',{
	chemical_industry_add:function(frm,cdt,cdn){
		var d = locals[cdt][cdn]
		var chemicalOptionsList = ["2.B.1. Ammonia production","2.B.2. Nitric acid production","2.B.3. Adipic acid production","2.B.4. Caprolactam, glyoxal and glyoxylic acid production","2.B.5. Carbide production","2.B.6. Titanium dioxide production","2.B.7. Soda ash production","2.B.8. Petrochemical and carbon black production","2.B.9. Fluorochemical production","2.B.10. Other"]
		for(var i of frm.doc.chemical_industry){
			if(chemicalOptionsList.includes(i.chemical)){
				const index = chemicalOptionsList.indexOf(i.chemical);
				if (index > -1) { // only splice array when item is found
					chemicalOptionsList.splice(index, 1); // 2nd parameter means remove one item only
					}
			} 
		}
		var chemicalOptions = ""
		for(var i of chemicalOptionsList){
			chemicalOptions += i + "\n"
		}
		cur_frm.grids[11].grid.grid_rows[d.idx-1].columns.chemical.df.options = chemicalOptions
		frm.refresh_field('chemical_industry')
		
	},
	emission_factor_co2:function(frm,cdt,cdn){
		// var code = frm.doc.code
			var d = locals[cdt][cdn]
			var quantity = d.amt_of_chemical_tonnes; 
			var co2 = d.emission_factor_co2; 
			if(quantity != 0){
				var co2Emission = (quantity * co2) / ((10)**3);
			
					frappe.model.set_value(cdt, cdn, "calculated_co2", co2Emission);
					frm.refresh_field('calculated_co2');
			}else{
				frappe.model.set_value(cdt, cdn, "calculated_co2", 0);
				frm.refresh_field('calculated_co2');

			}
	},
	emission_factor_ch4: function(frm, cdt, cdn) {
		var d = locals[cdt][cdn];
		var quantity = d.amt_of_chemical_tonnes;
		var ch4 = d.emission_factor_ch4;
		
		if (quantity != 0) {
			var ch4Emission = (quantity * ch4) / ((10)**3); // 1000 is used to convert to the desired units (e.g., kg to tonnes).
			frappe.model.set_value(cdt, cdn, "calculated_ch4", ch4Emission);
			frm.refresh_field('calculated_ch4');
		} else {
			frappe.model.set_value(cdt, cdn, "calculated_ch4", 0);
			frm.refresh_field('calculated_ch4');
		}
	},
	
	emission_factor_n2o: function(frm, cdt, cdn) {
		var d = locals[cdt][cdn];
		var quantity = d.amt_of_chemical_tonnes;
		var n2o = d.emission_factor_n2o;
		
		if (quantity != 0) {
			var n2oEmission = (quantity * n2o) /((10)**3); // 1000 is used to convert to the desired units (e.g., kg to tonnes).
			frappe.model.set_value(cdt, cdn, "calculated_n2o", n2oEmission);
			frm.refresh_field('calculated_n2o');
		} else {
			frappe.model.set_value(cdt, cdn, "calculated_n2o", 0);
			frm.refresh_field('calculated_n2o');
		}
	},
	// Calculate emissions when the "amount" field changes
	amt_of_chemical_tonnes: function (frm, cdt, cdn) {
		var d = locals[cdt][cdn];
		var quantity = d.amt_of_chemical_tonnes;
		var co2 = d.emission_factor_co2;
		var ch4 = d.emission_factor_ch4;
		var n2o = d.emission_factor_n2o;

		if (co2 != 0) {
			var co2Emission = (quantity * co2) /((10)**3); 
			frappe.model.set_value(cdt, cdn, "calculated_co2", co2Emission);
			frm.refresh_field("calculated_co2");
		} else {
			frappe.model.set_value(cdt, cdn, "calculated_co2", 0);
			frm.refresh_field("calculated_co2");
		}

		if ( ch4 !== 0) {
			var ch4Emission = (quantity * ch4) / ((10)**3); 
			frappe.model.set_value(cdt, cdn, "calculated_ch4", ch4Emission);
			frm.refresh_field("calculated_ch4");
		} else {
			frappe.model.set_value(cdt, cdn, "calculated_ch4", 0);
			frm.refresh_field("calculated_ch4");
		}

		if ( n2o !== 0) {
			var n2oEmission = (quantity * n2o) /((10)**3); 
			frappe.model.set_value(cdt, cdn, "calculated_n2o", n2oEmission);
			frm.refresh_field("calculated_n2o");
		} else {
			frappe.model.set_value(cdt, cdn, "calculated_n2o", 0);
			frm.refresh_field("calculated_n2o");
		}
	}

	
})

frappe.ui.form.on('IPPU Ozone ChildTable',{
	electrical_equipment_add:function(frm,cdt,cdn){
		var d = locals[cdt][cdn]
		frappe.db.get_list("IPPU GWP Master List",{
			fields : ['gas_name'],
			filters:{name:["like","%PFC%"]},
			order_by : 'name asc',
			pluck: 'gas_name'
		}).then(r =>{
			var gas_name_list = ["Sulfur hexafluoride"]

			for (let i of r){
				gas_name_list.push(i)
			}

			frm.set_query("gas_consumed", "electrical_equipment", function() {
				return {
					filters: {
						"name": ["in", gas_name_list] 
						
					}
				}
			});
			frm.refresh_fields("gas_consumed");
		})
		
		
	},
	sf6_and_pfcs_from_other_product_use_add:function(frm,cdt,cdn){
		var d = locals[cdt][cdn]
		frappe.db.get_list("IPPU GWP Master List",{
			fields : ['gas_name'],
			filters:{name:["like","%PFC%"]},
			order_by : 'name asc',
			pluck: 'gas_name'
		}).then(r =>{
			var gas_name_list = ["Sulfur hexafluoride"]

			for (let i of r){
				gas_name_list.push(i)
			}

			frm.set_query("gas_consumed", "electrical_equipment", function() {
				return {
					filters: {
						"name": ["in", gas_name_list] 
						
					}
				}
			});
			frm.refresh_fields("gas_consumed");
		})
		
		
	},

})

async function population_calculation(frm){
	var tableList = {
		'3.A. Enteric fermentation':'enteric_fermentation',
		'3.B.b. Direct N2O emissions per MMS (kt N2O)':'direct_emissions_mms',
		'3.B.5. Indirect N2O emissions':'indirect_manure_management'
	}
	var formulaList = {
		'3.A. Enteric fermentation':'Enteric Fermentation',
		'3.B.b. Direct N2O emissions per MMS (kt N2O)':'Direct N2O Emissions',
		'3.B.5. Indirect N2O emissions':'Indirect N2O Emissions'
	}
	for (var j of Object.keys(tableList)){
		if(frm.doc.category == j || frm.doc.sub_sector == j){
			for(var k of Object.keys(formulaList)){
				if(j == k){
					var table_key_j = `${tableList[j]}`
					frm.doc[table_key_j] = []
					var table_key_k = k
					var res =  await frappe.db.get_list("GHG Inventory Report Formulas",{
						fields:[ "co2", "ch4","n2o","cumulative_ch4","cumulative_co2","cumulative_n2o","total_co2"],
						filters:{
							"name": formulaList[table_key_k]
						}
					})
					
					frm.call({
						doc:frm.doc,
						method:"get_livestock_details",
						async:false,
						callback:async function(r){
							for (var i of r.message){
								var table_key_i = i
								var child = frm.add_child(table_key_j)
								child.category = table_key_i.category,
								child.heads = table_key_i.heads
								var result = await frappe.db.get_list("Livestock Emission Factor Master List",{
									fields:["category","enteric_fermentation","manure_management", "excretion_rate", "typical_animal_mass","nitrogen_excretion","direct_n2o_n_emissions","managed_manure","managed_ivestock_manure","atmospheric_deposition"],
									filters:{
										"category" : table_key_i.category
									}
								})
								// .then(function(result){
									let head = parseFloat(table_key_i.heads)
									let enteric_fermentation = parseFloat(result[0].enteric_fermentation)
									let nitrogen_excretion_rate = parseFloat(result[0].excretion_rate  )
									let animal_mass = parseFloat(result[0].typical_animal_mass)
									let nitrogen_excretion_managed = parseFloat(result[0].nitrogen_excretion)
									let emission_factor_n2o = parseFloat(result[0].atmospheric_deposition)
									let managed_livestock_manure_n2o = parseFloat(result[0].managed_ivestock_manure)
									let direct_n2o_n_emissions = parseFloat(result[0].direct_n2o_n_emissions)
									if(table_key_k == "3.A. Enteric fermentation"){
										child.ghg_emissions_tco2e = eval(res[0].ch4)
									}
									else{
										child.ghg_emissions_tco2e = eval(res[0].n2o)
									}
									frm.refresh_field(table_key_j)
								// })
							}
						}
					})
				}
				
			}
			
		}
	}
}

function toTitleCase(str) {
	return str.replace(
	  /\w\S*/g,
	  function(txt) {
		return txt.charAt(0).toUpperCase() + txt.substr(1).toLowerCase();
	  }
	); 
}


// Functions //

// function populateFourTables(frm){
// 	let table_name_list = ['direct_managed_soils','direct_flooded_rice','direct_managed_organic_soils','direct_grazed_soils']
// 		frm.call({
// 			doc:cur_frm.doc,
// 			method:"get_data",
// 			async:false,
// 			args:{
// 				table_name:frm.doc.table_type
// 			},
// 			callback:function(r){
// 				for (var table of table_name_list){ 
// 					frm.doc[`${table}`] = []
// 					for(var i of r.message){
// 						var child = frm.add_child(`${table}`)
// 						child.anthropogenic_n_input= i.anthropogenic_n_input
// 						child.amount = i.amount
// 						child.emission_factor= i.emission_factor
// 						child.reference = i.reference
// 					}
// 					frm.refresh_field(`${table}`)
// 				}
// 			}
// 		})
// }