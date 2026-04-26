import frappe

# Legacy blue/grey/white defaults that the editorial CSS retint replaces.
# Includes both the original spec list (#267db9, #184482, #1f272e, #26b979,
# greys, whites/blacks) and the legacy doctype JSON defaults (#005fb3,
# #062541, #222222) that older installs will have persisted.
LEGACY_COLORS = {
	"#267db9", "#184482", "#1f272e", "#26b979",
	"#005fb3", "#062541", "#222222",
	"#f4f5f6", "#f0f0f0", "#fff", "#ffffff",
	"#000", "#000000", "white", "black",
}

# Every Color fieldtype in side_menu_settings.json (do not include logo Attach
# Image fields). Keep in sync if new color fields are added to the doctype.
COLOR_FIELDS = [
	"side_bar_background_color",
	"side_bar_hover_color",
	"side_bar_text_color",
	"side_bar_text_hover_color",
	"sub_menu_background_color",
	"sub_menu_text_color",
	"sub_menu_background_hover_color",
	"sub_menu_text_hover_color",
	"logo_background_color",
	"logo_bottom_border_color",
]


def execute():
	if not frappe.db.exists("DocType", "Side Menu Settings"):
		return
	doc = frappe.get_single("Side Menu Settings")
	changed = False
	for f in COLOR_FIELDS:
		val = (getattr(doc, f, "") or "").strip().lower()
		if val in LEGACY_COLORS:
			setattr(doc, f, "")
			changed = True
	if changed:
		doc.save(ignore_permissions=True)
		frappe.db.commit()
