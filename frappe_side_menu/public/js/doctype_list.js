frappe.listview_settings["Project"] = Object.assign(frappe.listview_settings["Project"] || {}, {
	refresh: function (listview) {
		const root = listview?.$page || $(document);
		root.find('[class="search"]').css("display", "none");
		root.find('[id="recordListContainer"]').css("display", "none");
		root.find('[id="treeview"]').css("display", "contents");
	},
});   