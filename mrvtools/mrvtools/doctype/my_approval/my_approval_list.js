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
	// Replace Frappe's default empty-state copy ("You haven't created a My Approval
	// yet"), which is misleading — approvers don't *create* approvals, they
	// receive them. The empty-state node is rendered by frappe-listview after the
	// list resolves to zero rows; we run on every list refresh and rewrite the
	// copy in place.
	refresh: function (listview) {
		const rewrite = () => {
			const $page = listview && listview.$page ? listview.$page : $(document);
			const heading = $page.find(".no-result h1, .empty-state h1, .msg-box h1").first();
			const message = $page.find(".no-result p, .empty-state p, .msg-box p").first();
			if (!heading.length && !message.length) return;
			heading.text(__("Nothing to review"));
			message.text(__("Approvals waiting on you will appear here."));
		};
		// Fire on initial render and after every render (filter changes, etc.)
		rewrite();
		setTimeout(rewrite, 200);
		listview && listview.$result && listview.$result.on("DOMNodeInserted", rewrite);
	},
};
