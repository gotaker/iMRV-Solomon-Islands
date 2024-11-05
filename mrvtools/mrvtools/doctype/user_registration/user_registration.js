// Copyright (c) 2023, tridotstech and contributors
// For license information, please see license.txt

frappe.ui.form.on('User Registration', {
    refresh:function(frm){
        if (frm.doc.workflow_state == 'Approved'){
 
            
            // var ghg = frm.doc.ghg;
     
            // var project = frm.doc.project_tracking;
        
            // var reports = frm.doc.reports;
        
            
          
            // frappe.call({
            //     doc:frm.doc,
            //     args:{
            //         ghg: ghg,
            //         reports: reports,
            //         project:project
            //     },
            //     method:"check_user_exists",
            //     async:false,
            //     callback:function(r){
            //     }
            // })
        }
		
		frm.set_query("ghg", function(){
            return {
                filters: {
                    category : "GHG"
                }
            }
        });

		frm.set_query("project_tracking", function(){
            return {
                filters: {
                    category : "Project Tracking"
                }
            }
        });


		// let child = frm.add_child('Project Tracking ChildTable')
		// child.project_tracking = 'Adaptation Tracking'
		// frm.refresh_field('project_tracking')
		// frm.set_query("project_tracking", function(){
        //     return {
        //         filters: {
        //             category : "Project Tracking"
        //         }
        //     }
        // });
		frm.set_query("reports", function(){
            return {
                filters: {
                    category : "Reports"
                }
            }
        });
        // frm.call({
        //     doc:cur_frm.doc,
        //     method:"createUser",
        //     async:false,
        //     args:{
        //         formData:
        //     },
        //     callback:function(r){
        //     }
        // })
	},
    before_save(frm){
        // if(frm.doc.workflow_state == 'Approved'){
        //     var ghg = frm.doc.ghg;
     
        //     var project = frm.doc.project_tracking;
        
        //     var reports = frm.doc.reports;
        //     frappe.call({
        //         doc:frm.doc,
        //         args:{
        //             ghg: ghg,
        //             reports: reports,
        //             project:project
        //         },
        //         method:"check_user_exists",
        //         async:false,
        //         callback:function(r){
        //         }
        //     })
        // }
    }
	// role :function(frm){
	// 	if (frm.doc.role == "Observer" ){
	// 		frm.fields_dict["ghg"].df.hidden = 1
	// 		frm.fields_dict["project_tracking"].df.hidden = 1
	// 		frm.fields_dict["reports"].df.hidden = 0
	// 	}
	// 	else{
	// 		frm.fields_dict["ghg"].df.hidden = 0
	// 		frm.fields_dict["project_tracking"].df.hidden = 0
	// 		frm.fields_dict["reports"].df.hidden = 0
	// 	}
	// 	frm.refresh_field("ghg")
	// 	frm.refresh_field("project_tracking")
	// 	frm.refresh_field("reports")
	// }
});
