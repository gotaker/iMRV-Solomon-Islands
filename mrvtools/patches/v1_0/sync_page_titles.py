import frappe


# (page_name, expected_title) — bench migrate doesn't re-import existing
# standard Page records, so a JSON-fixture title edit needs a paired backfill.
# Add new pairs here when a Page fixture's title changes.
_PAGE_TITLES = {
	"ghg-inventory-report": "GHG Inventory Report",
	"mrv-report": "MRV Report",
}


def execute():
	for page_name, expected in _PAGE_TITLES.items():
		if not frappe.db.exists("Page", page_name):
			continue
		current = frappe.db.get_value("Page", page_name, "title")
		if current == expected:
			continue
		frappe.db.set_value("Page", page_name, "title", expected)
	frappe.db.commit()
