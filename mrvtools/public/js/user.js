frappe.ui.form.on('User', {
	refresh: function(frm){
        if(frappe.user_roles.includes("Dashboard Observer") && (!frappe.user_roles.includes("Administrator") || !frappe.user_roles.includes("System Manager"))){
			$('[class="page-content"]').append(`
				<style> 
					.search-bar,.dropdown-notifications,.vertical-bar {
						display: none !important;
					}
					.sidebar .sidebar-menu{
						background:#f9fafa !important;
						box-shadow: #f9fafa 0px 0px 0px 0px !important;
					}
					li.treeview.drop-down{
						display: none !important;
					}
				</style>
				`)
		}
        if(cur_frm.doc.doctype == "User"){
            $(`[id="page-User"] [class="col-lg-2 layout-side-section"]`).css({"display":"block","margin-left":"95px"});
            $(`[id="page-User"] [class="col layout-main-section-wrapper"]`).css("margin-left","0px");
            $(`[id="page-User"] [class="page-title"]`).css({"margin-left":"95px !important"});
            $(`[id="page-User"] [class="list-unstyled sidebar-menu form-assignments"]`).css({"display":"none"});
            $(`[id="page-User"] [class="list-unstyled sidebar-menu form-attachments"]`).css({"display":"none"});
            $(`[id="page-User"] [class="list-unstyled sidebar-menu form-shared"]`).css({"display":"none"});
            $(`[id="page-User"] [class="list-unstyled sidebar-menu followed-by-section"]`).css({"display":"none"});
            $(`[id="page-User"] [class="list-unstyled sidebar-menu form-tags"]`).css({"display":"none"});
            $(`[id="page-User"] [class="list-unstyled sidebar-menu"]`).css({"display":"none"});
            $(`[id="page-User"] [class="list-unstyled sidebar-menu form-sidebar-stats"]`).css({"display":"none"});
            $(`[id="page-User"] [class="list-unstyled sidebar-menu form-sidebar-stats"]`).css({"display":"none"});
            $(`[id="page-User"] [class="list-unstyled sidebar-menu text-muted"]`).css({"display":"none"});
            $(`[id="page-User"] [class="form-sidebar overlay-sidebar hidden-xs hidden-sm"] hr:last`).css({"display":"none"});
            $(`[id="page-User"] [class="row form-dashboard-section form-links"]`).css({"display":"none"});
            $(`[id="page-User"] [data-fieldname="desk_theme"]`).css({"display":"none"});
            $(`[id="page-User"] [data-fieldname="banner_image"]`).css({"display":"none"});
            // $(`[id="page-User"] [class="section-head collapsed"]:contains('More Information')`).parent().css({"display":"none"});
            $(`[id="page-User"] [class="section-head collapsed"]:contains('Document Follow')`).parent().css({"display":"none"});
            $(`[id="page-User"] [class="section-head collapsed"]:contains('Email')`).parent().css({"display":"none"});
            $(`[id="page-User"] [class="section-head collapsed"]:contains('Allow Modules')`).parent().css({"display":"none"});
            $(`[id="page-User"] [class="section-head collapsed"]:contains('Security Settings')`).parent().css({"display":"none"});
            $(`[id="page-User"] [class="section-head collapsed"]:contains('Third Party Authentication')`).parent().css({"display":"none"});
            $(`[id="page-User"] [class="section-head collapsed"]:contains('API Access')`).parent().css({"display":"none"});
        }
    }
})