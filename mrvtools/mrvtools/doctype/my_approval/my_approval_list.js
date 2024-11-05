frappe.listview_settings["My Approval"] = {
	get_form_link: (doc) => {
		let doctype = "";
		let docname = "";
        doctype = doc.reference_doctype;
        docname = doc.reference_name;
		docname = docname.match(/[%'"]/) ? encodeURIComponent(docname) : docname;

		const link = "/app/" + frappe.router.slug(doctype) + "/" + docname;
		return link;
	},
};
