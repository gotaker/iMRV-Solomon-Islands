$(document).on("form-refresh", function(frm) {
	
	if(cur_frm.doc.doctype != "User Registration"){	
		$(`[id="page-${cur_frm.doc.doctype}"]`).find('.actions-btn-group').hide();
	}
	

	$.each(cur_frm.fields_dict, function(fieldname, field) {
		field.df.onchange = function() {
			cur_frm.clear_custom_buttons()
			if(cur_frm.doc.workflow_state == "Draft"){
				$('[data-label="Save"]').prop('textContent','Save as Draft')
			}
		};

	})
	
	$('[data-fieldtype="Table"]').on("change",function(){
		if(($(`[id='page-${cur_frm.doc.doctype}'] .indicator-pill`)).text() == "Not Saved"){
			cur_frm.clear_custom_buttons();
			if(cur_frm.doc.workflow_state == "Draft"){
				$('[data-label="Save"]').prop('textContent','Save as Draft')
			}
		}
	});
	
	$('[data-fieldtype="Table"]').on("focusout",function(){
		if(($(`[id='page-${cur_frm.doc.doctype}'] .indicator-pill`)).text() == "Not Saved"){
			cur_frm.clear_custom_buttons();
			if(cur_frm.doc.workflow_state == "Draft"){
				$('[data-label="Save"]').prop('textContent','Save as Draft')
			}
		}
	});
	
	$('[data-fieldtype="Button"]').on("click",function(){
		cur_frm.clear_custom_buttons()
		if(cur_frm.doc.workflow_state == "Draft"){
			$('[data-label="Save"]').prop('textContent','Save as Draft')
		}
	})
	
	if(cur_frm.doc.__unsaved == 1){
		setTimeout(function() {
			cur_frm.clear_custom_buttons()
			if(cur_frm.doc.workflow_state == "Draft"){
				$('[data-label="Save"]').prop('textContent','Save as Draft')
			}
		},1000)
		
		
	}
	if (cur_frm.doc.doctype != "User Registration"){
		if(cur_frm.doc.workflow_state == "Pending" && !cur_frm.doc.__islocal){
			if((frappe.user_roles).some(role => role.startsWith("Approver") || role === "System Manager" || role === "MRV Admin")){
				if(frappe.session.user == cur_frm.doc.select_approver || (frappe.user_roles).some(role => role === "System Manager" || role === "MRV Admin")){
					cur_frm.add_custom_button('Approve',()=>{
						frappe.confirm('Are you sure you want to proceed?',
							() => {
								cur_frm.set_value("workflow_state","Approved")
								cur_frm.refresh_field("workflow_state")
								cur_frm.save()
								frappe.call({
									method:"mrvtools.mrvtools.doctype.my_approval.my_approval.delete_record",
									args:{
										reference_name: cur_frm.doc.name,
										reference_doctype: cur_frm.doc.doctype

									},
									async:false
								})
							}, () => {

						})

					},"Actions")
					
					cur_frm.add_custom_button('Reject',()=>{
						frappe.confirm('Are you sure you want to proceed?',
						() => {
							cur_frm.set_value("workflow_state","Rejected")
							cur_frm.refresh_field("workflow_state")
							cur_frm.save()
							frappe.call({
								method:"mrvtools.mrvtools.doctype.my_approval.my_approval.delete_record",
								args:{
									reference_name: cur_frm.doc.name,
									reference_doctype: cur_frm.doc.doctype

								},
								async:false
							})
						}, () => {
							
						})
						
					},"Actions")
				}
			}
			

			
		}
		else if(cur_frm.doc.workflow_state == "Approved" && !cur_frm.doc.__islocal){
			if((frappe.user_roles).some(role => !role.startsWith("Approver") || role === "System Manager" || role === "MRV Admin")){
				if(frappe.session.user == cur_frm.doc.owner || (frappe.user_roles).some(role => role === "System Manager" || role === "MRV Admin")){
					cur_frm.add_custom_button('Edit',()=>{
						frappe.confirm('Are you sure you want to proceed?',
							() => {
								cur_frm.set_value("workflow_state","Draft")
								cur_frm.refresh_field("workflow_state")
								
								cur_frm.save()
							}, () => {
			
						})
		
					},"Actions")
				}
			}  
		}
		else if(cur_frm.doc.workflow_state == "Draft" && !cur_frm.doc.__islocal){
			if((frappe.user_roles).some(role => !role.startsWith("Approver") || role === "System Manager" || role === "MRV Admin")){
				if(frappe.session.user == cur_frm.doc.owner || (frappe.user_roles).some(role => role === "System Manager" || role === "MRV Admin")){
					cur_frm.add_custom_button('Send for Approval',()=>{
						frappe.confirm('Are you sure you want to proceed?',
							() => {
								cur_frm.set_value("workflow_state","Pending")
								cur_frm.refresh_field("workflow_state")
								
								cur_frm.save()
								frappe.call({
									method:"mrvtools.mrvtools.doctype.my_approval.my_approval.insert_record",
									args:{
										created_by:cur_frm.doc.owner,
										date: cur_frm.doc.modified,
										reference_name: cur_frm.doc.name,
										reference_doctype: cur_frm.doc.doctype,
										approver:cur_frm.doc.select_approver

									},
									async:false
								})
							}, () => {
							
						})
						
					},"Actions")
				}
			}
		}
		else if(cur_frm.doc.workflow_state == "Rejected" && !cur_frm.doc.__islocal){
			if((frappe.user_roles).some(role => !role.startsWith("Approver") || role === "System Manager" || role === "MRV Admin")){
				if(frappe.session.user == cur_frm.doc.owner || (frappe.user_roles).some(role => role === "System Manager" || role === "MRV Admin")){
					cur_frm.add_custom_button('Edit',()=>{
						frappe.confirm('Are you sure you want to proceed?',
							() => {
								cur_frm.set_value("workflow_state","Draft")
								cur_frm.refresh_field("workflow_state")
								
								cur_frm.save()
							}, () => {
								
						})
						
					},"Actions")
				}
			}
		}
		$('.inner-group-button button').removeClass("btn-default").addClass("btn-primary")
	}
	$.ajax({
		success:function(){
			$('[data-fieldtype="Link"]').attr("placeholder","Select")
			$('[data-fieldtype="Table MultiSelect"]').attr("placeholder","Select")
			$('[data-fieldtype="Table"] [class="btn-open-row"] [class="hidden-xs edit-grid-row"]').prop("innerText","View")
			$('[class="btn btn-xs btn-secondary grid-add-row"]').on("click",function(){
				
				$('[data-fieldtype="Table"] [class="btn-open-row"] [class="hidden-xs edit-grid-row"]').prop("innerText","View")
			})
		}
	})

	frappe.call({
		method:"mrvtools.api.get_approvers",
		asyc:true,	
		callback:function(r){
			if (frappe.session.user != "Administrator"){
				for (var i of r.message){
					if(cur_frm.doc.workflow_state == "Pending" || cur_frm.doc.workflow_state == "Approved"|| cur_frm.doc.workflow_state == "Rejected"){
						if(frappe.user_roles.includes(i)){
							$(`[id="page-${cur_frm.doc.doctype}"] [class="tab-pane fade show active"]`).attr("style","pointer-events:none !important;--text-color: var(--disabled-text-color); opacity: 0.9;")
						}
					}
					else{
						$('[class="tab-pane fade show active"]').attr("style","pointer-events:inherit !important;")
					}
				}
			}
		}
	})
})

$(document).ready(function(){
	$(".sidebar-menu").on("hover",function(){
		$('.treeview-menu').on("mouseenter",function(){
			$(".sidebar-menu").css("scrollbar-width","none !important")
		})
	})
})

frappe.router.on("change", page_changed)
 
function page_changed(event) {
    frappe.after_ajax(function () {
        var route = frappe.get_route();
        if (route[0] == "List") {
			
			setTimeout(() => {
				
				$("[class='actions-btn-group hide'] [class='user-action']").closest('li').css({"display":"none"});
				$("[class='dropdown-divider user-action']").closest('li').css({"display":"none"});
				$("span.menu-item-label[data-label='Edit']").closest('li').css({"display":"none"});
				$("span.menu-item-label[data-label='Assign%20To']").closest('li').css({"display":"none"});
				$("span.menu-item-label[data-label='Apply%20Assignment%20Rule']").closest('li').css({"display":"none"});
				$("span.menu-item-label[data-label='Add%20Tags']").closest('li').css({"display":"none"});
				$("span.menu-item-label[data-label='Print']").closest('li').css({"display":"none"});
			}, 1000);
        }
		setTimeout(() => {
			$('#co2_emission_last_five_years').find('g[class="bar-chart chart-draw-area"]').css('transform', 'translate(7%, 17%)')
		}, 1000);
		$('[class="heading-main"]').remove()
		$('<h2 class="heading-main" data-v-2dd66c2c="" style="color: rgb(0, 0, 0);font-weight: 700;font-size: 20px;font-family: sans-serif;display: flex;line-height: 1.5;align-items: start;justify-content: start !important;margin-left: 195px;margin-bottom: 0px !important;"> SOLOMON ISLANDS iMRV TOOL <span data-v-2dd66c2c="" style="color: green; margin: 0px 0px 0px 7px;">FOR CLIMATE ACTIONS</span></h2>').insertBefore($('[class="form-inline fill-width justify-content-end"]'))
		// $(".sidebar-menu .menu").on("mouseenter",function(){
		// 	if($(this).next().find('.treeview-menu').css('display') == "block"){
		// 		$("ul.sidebar-menu").append("<style>.sidebar-menu{scrollbar-width:none !important;}</style>")
		// 	}
		// 	else{
		// 		$("ul.sidebar-menu").append("<style>.sidebar-menu{scrollbar-width:thin !important;}</style>")
		// 	}
		// })
    })
}

// $.ajax({
// 	success:function(){
// 			$('<h2 class="heading-main" data-v-2dd66c2c="" style="color: rgb(0, 0, 0);font-weight: 700;font-size: 20px;font-family: sans-serif;display: flex;line-height: 1.5;align-items: start;justify-content: start !important;margin-left: 195px;margin-bottom: 0px !important;"> SOLOMON ISLANDS iMRV TOOL <span data-v-2dd66c2c="" style="color: green; margin: 0px 0px 0px 7px;">FOR CLIMATE ACTIONS</span></h2>').insertBefore($('[class="form-inline fill-width justify-content-end"]'))
// 	}
// })
$(document).ready(function(){
	$('[class="nav-item dropdown dropdown-help dropdown-mobile d-none d-lg-block"]').attr("style","display:none !important")
	$('[data-fieldtype="Table"] [class="btn-open-row"] [class="hidden-xs edit-grid-row"]').prop("innerText","View")
	$("head").append('<style>#page-Workspaces [class="flex col page-actions justify-content-end"]{display:none}</style>');
	
})


function route_user(){
	frappe.db.get_value("Approved User",frappe.session.user,'name').then( r => {
		if(!r.message.name){
			frappe.set_route("Form","User",frappe.session.user)
		}
		else{
			frappe.set_route("Form","Approved User",frappe.session.user)
		}
	})
}