// Copyright (c) 2024, tridotstech and contributors
// For license information, please see license.txt

frappe.ui.form.on('Approved User', {
	refresh: function(frm) {
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
		if(cur_frm.doc.doctype == "Approved User"){
            $(`[id="page-Approved User"] [class="col-lg-2 layout-side-section"]`).css({"display":"block","margin-left":"95px"});
            $(`[id="page-Approved User"] [class="col layout-main-section-wrapper"]`).css("margin-left","0px");
            $(`[id="page-Approved User"] [class="page-title"]`).css({"margin-left":"95px !important"});
            $(`[id="page-Approved User"] [class="list-unstyled sidebar-menu form-assignments"]`).css({"display":"none"});
            $(`[id="page-Approved User"] [class="list-unstyled sidebar-menu form-attachments"]`).css({"display":"none"});
            $(`[id="page-Approved User"] [class="list-unstyled sidebar-menu form-shared"]`).css({"display":"none"});
            $(`[id="page-Approved User"] [class="list-unstyled sidebar-menu followed-by-section"]`).css({"display":"none"});
            $(`[id="page-Approved User"] [class="list-unstyled sidebar-menu form-tags"]`).css({"display":"none"});
            $(`[id="page-Approved User"] [class="list-unstyled sidebar-menu"]`).css({"display":"none"});
            $(`[id="page-Approved User"] [class="list-unstyled sidebar-menu form-sidebar-stats"]`).css({"display":"none"});
            $(`[id="page-Approved User"] [class="list-unstyled sidebar-menu form-sidebar-stats"]`).css({"display":"none"});
            $(`[id="page-Approved User"] [class="list-unstyled sidebar-menu text-muted"]`).css({"display":"none"});
            $(`[id="page-Approved User"] [class="form-sidebar overlay-sidebar hidden-xs hidden-sm"] hr:last`).css({"display":"none"});
            $(`[id="page-Approved User"] [class="row form-dashboard-section form-links"]`).css({"display":"none"});
		}
		frm.add_custom_button(
			__("Reset Password"),
			function () {
				frappe.call({
					method: "mrvtools.mrvtools.doctype.approved_user.approved_user.reset_password",
					args: {
						user: frm.doc.name,
					},
				});
			},
			__("Password")
		);
	}
});
