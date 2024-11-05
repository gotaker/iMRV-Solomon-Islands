// Copyright (c) 2023, tridotstech and contributors
// For license information, please see license.txt

frappe.ui.form.on('Project', {

	get_location:function(frm){
		var existingGeoJSON = frm.doc.geographical_co_ordinate || '{"type":"FeatureCollection","features":[]}';
		var parsedGeoJSON = JSON.parse(existingGeoJSON);
				
		// New point coordinates
		var coordinatesList = frm.doc.coordinates.split(',');
		var latLetter = coordinatesList[0][coordinatesList[0].length-1]
		var longLetter = coordinatesList[1][coordinatesList[1].length-1]

		if(latLetter == 'S'){
			var latitude = parseFloat(coordinatesList[0]);
			latitude = -latitude
		}
		else{
			var latitude = parseFloat(coordinatesList[0]);
		}

		if(longLetter == 'W'){
			var longitude = parseFloat(coordinatesList[1]);
			longitude = -longitude
		}
		else{
			longitude = parseFloat(coordinatesList[1]);
		}

		// Check if the coordinates are valid numbers
		if (!isNaN(latitude) && !isNaN(longitude)) {
			var newFeature = {
				"type": "Feature",
				"properties": {},
				"geometry": {
					"type": "Point",
					"coordinates": [longitude, latitude]
				}
			};
			
			// Check if the new feature already exists in parsedGeoJSON
			var isFeatureExists = parsedGeoJSON.features.some(function(feature) {
				return (
					feature.geometry.coordinates[1] === longitude &&
					feature.geometry.coordinates[0] === latitude
				);
			});
			
			// Add the new feature only if it doesn't exist already
			if (!isFeatureExists) {
				parsedGeoJSON.features.push(newFeature);
			}
		}

		var updatedGeoJSON = JSON.stringify(parsedGeoJSON);
		// Set the updated GeoJSON string to the geolocation field
		frm.set_value('geographical_co_ordinate', updatedGeoJSON);
		frm.set_value("coordinates","") 
	},

	objective: function(frm){
		if(!frm.doc.objective){
			frm.set_df_property('key_sector','hidden',1)
			frm.refresh_field('key_sector')
		}
		else{
			frm.set_df_property('key_sector','hidden',0)
			frm.refresh_field('key_sector')
		}
	},

	action:function(frm){
		if(!frm.doc.action){
			frm.set_df_property('programme','hidden',1)
			frm.refresh_field('programme')
		}
		else{
			frm.set_df_property('programme','hidden',0)
			frm.refresh_field('programme')
		}
	},
	start_date: function(frm){
		if (frm.doc.end_date){
			let start_date = new Date(frm.doc.start_date)
			let end_date = new Date(frm.doc.end_date)
			
			const differenceMs = end_date - start_date;
			const millisecondsInYear = 1000 * 60 * 60 * 24 * 365.25;
			const years = differenceMs / millisecondsInYear;
			frm.set_value("lifetime",`${years.toFixed(1)}`)
			frm.refresh_field("lifetime")
			
		}
	},
	end_date: function(frm){
		if (frm.doc.start_date){
			let start_date = new Date(frm.doc.start_date)
			let end_date = new Date(frm.doc.end_date)
			
			const differenceMs = end_date - start_date;
			const millisecondsInYear = 1000 * 60 * 60 * 24 * 365.25;
			const years = differenceMs / millisecondsInYear;
			frm.set_value("lifetime",`${years.toFixed(1)}`)
			frm.refresh_field("lifetime")
			// const diffInMilliseconds = end_date - start_date;
			// const millisecondsInDay = 1000 * 60 * 60 * 24;
			// const days = Math.floor(diffInMilliseconds / millisecondsInDay);
		
			// const years = Math.floor(days / 365);
			// const remainingDays = days % 365;
			// const months = Math.floor(remainingDays / 30);
			// const finalDays = remainingDays % 30;
			// const result = years + months / finalDays;
			
		}
	},
	
	key_sector:function(frm){
		if(!frm.doc.key_sector){
			frm.set_value("key_sub_sector","")
			frm.set_df_property('key_sub_sector','hidden',1)
			frm.refresh_field('key_sub_sector')
		}
		else{
			frm.set_value("key_sub_sector","")
			frm.set_df_property('key_sub_sector','hidden',0)
			frm.refresh_field('key_sub_sector')
		}
	},


	before_save:function(frm){

		$('[id="project-tab1-tab"]').click()
		$('[id="project-tab1"]').addClass("active show")

		if(frm.doc.objective == "Mitigation"){
			frm.set_value("naming_series","SI-01-.####")
		}
		if(frm.doc.objective == "Adaptation"){
			frm.set_value("naming_series","SI-02-.####")
		}
		if(frm.doc.objective == "Cross-Cutting"){
			frm.set_value("naming_series","SI-03-.####")
		}
		if(frm.doc.objective == "Enablers"){
			frm.set_value("naming_series","SI-04-.####")
		}
		if(frm.doc.objective == "Transparency"){
			frm.set_value("naming_series","SI-05-.####")
		}
		frm.refresh_field("naming_series")
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
			frm.set_value("original_coordinates",'')
			frm.refresh_field("original_coordinates")
			frm.set_value("new_coordinates",'')
			frm.refresh_field("new_coordinates")
		}
		if(frm.doc.workflow_state == "Approved"){
				if ((frm.doc.work_state == "Approved" && frm.doc.edited_project_details.length != 0) || (frm.doc.workflow_state == "Approved" && frm.doc.new_coordinates)){
				for (var i of frm.doc.edited_project_details){

					if(i.field_name != "included_in" && i.field_name != "geographical_co_ordinate"){
						frm.set_value(i.field_name,i.new_values)
					}
					
					else if(i.field_name == "included_in"){
						var new_list = i.new_values.split(",")
						frm.clear_table("included_in")
						for (var value of new_list){
							var row = frm.add_child("included_in")
							row.included_in = value
						}
					}
					
				}
				frm.set_value("edited_project_details",[])
				// frm.fields_dict.edited_project_details.df.hidden = 1
				frm.set_value("geographical_co_ordinate",frm.doc.new_coordinates)
				frm.refresh_field("geographical_co_ordinate")

				frm.set_value("original_coordinates",'')
				// frm.fields_dict.original_coordinates.df.hidden = 1
				frm.refresh_field("original_coordinates")
				frm.set_value("new_coordinates",'')
				// frm.fields_dict.new_coordinates.df.hidden = 1
				frm.refresh_field("new_coordinates")
			}
			frm.set_value('work_state','Approved')
			
			
		}

		if(frm.doc.work_state == "Approved"){
			if (frm.doc.workflow_state != "Approved"  && !frm.doc.__islocal){
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
								if (i.field_name != "included_in" && i.field_name != "geographical_co_ordinate" && i != "original_coordinates"&& i != "new_coordinates"){
									i.new_values = frm.doc[`${i.field_name}`]
									frm.set_value(i.field_name,i.old_values)
								}
								else if(i.field_name == "included_in"){
									var included_in_result = ""

									for(var res of frm.doc.included_in){
										if(included_in_result == ""){
											included_in_result += res.included_in
										}else{
											included_in_result += ","
											included_in_result += res.included_in
										}
									}

									i.new_values = included_in_result
									list=i.old_values.split(",")
									frm.clear_table("included_in")
									for (var value of list){
										var row = frm.add_child("included_in")
										row.included_in = value
									}
									frm.refresh_field("included_in")

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
								
								if (i != "included_in" && i != "geographical_co_ordinate" && i != "original_coordinates"&& i != "new_coordinates"){
									child.field_label = label
									child.field_name = i
									child.old_values = result[`${i}`]
									child.new_values = frm.doc[`${i}`]
									frm.set_value(i,result[`${i}`])
								}
								else if(i == "included_in"){
									child.field_label = label
									child.field_name = i
									child.old_values = result[`${i}`]
									var included_in_result = ""

									for(var res of frm.doc.included_in){
										if(included_in_result == ""){
											included_in_result += res.included_in
										}else{
											included_in_result += ","
											included_in_result += res.included_in
										}
									}

									child.new_values = included_in_result
									list2 = result[`${i}`].split(",")
									

									frm.clear_table("included_in")
									for(var value of list2){
										var row = frm.add_child("included_in")

										row.included_in = value
									}
									frm.refresh_field("included_in")
								}
								else if(i == "geographical_co_ordinate"){
									frm.set_value("original_coordinates",result[`${i}`])
									frm.set_value("new_coordinates",frm.doc.geographical_co_ordinate)
									frm.set_value(i,result[`${i}`])


								}
								
								
							}
						}
					}
				})
			}
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
		$('[id="page-Project"]').find('.actions-btn-group').hide();
		$('div[data-fieldname="project_id"]').parent().parent().css({"flex": "0 0 25%"})
		$('div[data-fieldname="project_name"]').parent().parent().css({"max-width": "75%","flex": "0 0 75%"})
		$(`div[data-fieldname="project_name"]`).attr('style','max-width:100%;padding-right: 0px;');
		if($('div[data-fieldname="project_id"]').hasClass("hide-control")){
			$('div[data-fieldname="project_id"]').parent().parent().css({"flex": ""})
			$('div[data-fieldname="project_name"]').parent().parent().css({"max-width": "100%","flex": "0 0 100%"})
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
		if(!frm.doc.objective){
		frm.set_df_property('key_sector','hidden',1)
		frm.refresh_field('key_sector')
		frm.set_df_property('key_sub_sector','hidden',1)
		frm.refresh_field('key_sub_sector')
		}
		else{
		frm.set_df_property('key_sector','hidden',0)
		frm.refresh_field('key_sector')
		frm.set_df_property('key_sub_sector','hidden',0)
		frm.refresh_field('key_sub_sector')
		}

		if(!frm.doc.action){
			frm.set_df_property('programme','hidden',1)
			frm.refresh_field('programme')
		}
		else{
			frm.set_df_property('programme','hidden',0)
			frm.refresh_field('programme')
		}

		frm.set_query("key_sector", function(){
			return {
				filters: {
					objective : frm.doc.objective
				}
			}
		});
		frm.set_query("key_sub_sector", function(){
			return {
				filters: {
					key_sector : frm.doc.key_sector
				}
			}
		});
		frm.set_query("action", function(){
			return {
				filters: {
					focus : frm.doc.objective
				}
			}
		});
		frm.set_query("programme", function(){
			return {
				filters: {
					action_id : frm.doc.action
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

