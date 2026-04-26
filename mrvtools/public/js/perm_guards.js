// BUG-016 mitigation: gate frappe.new_doc on the user's create perm.
//
// Frappe v16 ships `frappe.new_doc(doctype)` as a thin opener that calls
// `frappe.model.with_doctype(...)` and then routes to a New form. It does not
// consult the user's create permission, so a user with read-only access to a
// doctype can still land on a fully editable New form. The server-side
// `frappe.client.insert` correctly returns 403 on save, but the time spent in
// the form is wasted and the UX implies a create path that doesn't exist.
//
// This wrapper short-circuits with a localized warning before the form opens.
// Frappe's own UI hides "+ ADD" buttons for users without create perm, so
// real-user flows aren't affected — this catches programmatic calls (forms,
// custom buttons in app code, console invocations) that bypass the gate.
//
// Notes:
// - frappe.boot.user.can_create is the canonical client-side array of
//   doctypes the current session can create.
// - "File" is special-cased in core new_doc to spawn a FileUploader; we let
//   that pass through unconditionally because the upload widget is itself
//   permission-aware on the server side.
// - System Manager + Administrator skip the guard via the standard role
//   check baked into can_create.

(function () {
	if (typeof window === "undefined") return;

	function patchNewDoc() {
		if (
			!window.frappe ||
			typeof window.frappe.new_doc !== "function" ||
			window.frappe.new_doc.__permGuardPatched
		) {
			return false;
		}
		var orig = window.frappe.new_doc;
		var wrapped = function (doctype, opts, init_callback) {
			if (doctype !== "File") {
				var canCreate =
					(frappe.boot && frappe.boot.user && frappe.boot.user.can_create) || [];
				if (Array.isArray(canCreate) && canCreate.indexOf(doctype) === -1) {
					if (typeof frappe.show_alert === "function") {
						frappe.show_alert(
							{
								message: __("You don't have permission to create {0}.", [
									__(doctype),
								]),
								indicator: "orange",
							},
							5,
						);
					}
					return Promise.resolve();
				}
			}
			return orig.call(this, doctype, opts, init_callback);
		};
		wrapped.__permGuardPatched = true;
		window.frappe.new_doc = wrapped;
		return true;
	}

	if (!patchNewDoc()) {
		var attempts = 0;
		var t = setInterval(function () {
			if (patchNewDoc() || ++attempts > 40) clearInterval(t);
		}, 100);
	}
})();
