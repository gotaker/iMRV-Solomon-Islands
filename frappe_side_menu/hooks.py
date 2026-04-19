
app_name = "frappe_side_menu"
app_title = "Frappe Side Menu"
app_publisher = "NetZeroLabs"
app_description = "Frappe Side Menu"
app_email = "info@netzerolabs.io"
app_license = "MIT"

# Includes in <head>
# ------------------

# include js, css files in header of desk.html
app_include_css = ["https://fonts.googleapis.com/css2?family=Poppins:wght@200;400;500;600&display=swap","/assets/frappe_side_menu/css/frappe_side_menu.css","/assets/frappe_side_menu/css/ui-icons-regular.css"]
app_include_js = "/assets/frappe_side_menu/js/frappe_side_menu.js"

on_session_creation  = "frappe_side_menu.frappe_side_menu.api.set_default_route"

# include js, css files in header of web template
# web_include_css = "/assets/frappe_side_menu/css/frappe_side_menu.css"
# web_include_js = "/assets/frappe_side_menu/js/detail.js"

# include custom scss in every website theme (without file extension ".scss")
# website_theme_scss = "frappe_side_menu/public/scss/website"

# include js, css files in header of web form
# webform_include_js = {"*": "public/js/detail.js"}
# webform_include_css = {"doctype": "public/css/doctype.css"}

# include js in page
# page_js = {"page" : "public/js/file.js"}

# include js in doctype views
# doctype_js = {"*" : "public/js/detail.js"}
doctype_list_js = {"Project" : "public/js/doctype_list.js"}
# doctype_tree_js = {"doctype" : "public/js/doctype_tree.js"}
# doctype_calendar_js = {"doctype" : "public/js/doctype_calendar.js"}

# Home Pages
# ----------

# application home page (will override Website Settings)
# home_page = "login"

# website user home page (by Role)
# role_home_page = {
#	"Role": "home_page"
# }

# Generators
# ----------

# automatically create page for each record of this doctype
# website_generators = ["Web Page"]

# Jinja
# ----------

# add methods and filters to jinja environment
# jinja = {
#	"methods": "frappe_side_menu.utils.jinja_methods",
#	"filters": "frappe_side_menu.utils.jinja_filters"
# }

# Installation
# ------------

# before_install = "frappe_side_menu.install.before_install"
# after_install = "frappe_side_menu.install.after_install"

# Uninstallation
# ------------

# before_uninstall = "frappe_side_menu.uninstall.before_uninstall"
# after_uninstall = "frappe_side_menu.uninstall.after_uninstall"

# Desk Notifications
# ------------------
# See frappe.core.notifications.get_notification_config

# notification_config = "frappe_side_menu.notifications.get_notification_config"

# Permissions
# -----------
# Permissions evaluated in scripted ways

# permission_query_conditions = {
#	"Event": "frappe.desk.doctype.event.event.get_permission_query_conditions",
# }
#
# has_permission = {
#	"Event": "frappe.desk.doctype.event.event.has_permission",
# }

# DocType Class
# ---------------
# Override standard doctype classes

# override_doctype_class = {
#	"ToDo": "custom_app.overrides.CustomToDo"
# }

# Document Events
# ---------------
# Hook on document methods and events

# doc_events = {
#	"*": {
#		"on_update": "method",
#		"on_cancel": "method",
#		"on_trash": "method"
#	}
# }

# Scheduled Tasks
# ---------------

# scheduler_events = {
#	"all": [
#		"frappe_side_menu.tasks.all"
#	],
#	"daily": [
#		"frappe_side_menu.tasks.daily"
#	],
#	"hourly": [
#		"frappe_side_menu.tasks.hourly"
#	],
#	"weekly": [
#		"frappe_side_menu.tasks.weekly"
#	],
#	"monthly": [
#		"frappe_side_menu.tasks.monthly"
#	],
# }

# Testing
# -------

# before_tests = "frappe_side_menu.install.before_tests"

# Overriding Methods
# ------------------------------
#
# override_whitelisted_methods = {
#	"frappe.desk.doctype.event.event.get_events": "frappe_side_menu.event.get_events"
# }
#
# each overriding function accepts a `data` argument;
# generated from the base implementation of the doctype dashboard,
# along with any modifications made in other Frappe apps
# override_doctype_dashboards = {
#	"Task": "frappe_side_menu.task.get_dashboard_data"
# }

# exempt linked doctypes from being automatically cancelled
#
# auto_cancel_exempted_doctypes = ["Auto Repeat"]

# Ignore links to specified DocTypes when deleting documents
# -----------------------------------------------------------

# ignore_links_on_delete = ["Communication", "ToDo"]

# Request Events
# ----------------
# before_request = ["frappe_side_menu.utils.before_request"]
# after_request = ["frappe_side_menu.utils.after_request"]

# Job Events
# ----------
# before_job = ["frappe_side_menu.utils.before_job"]
# after_job = ["frappe_side_menu.utils.after_job"]

# User Data Protection
# --------------------

# user_data_fields = [
#	{
#		"doctype": "{doctype_1}",
#		"filter_by": "{filter_by}",
#		"redact_fields": ["{field_1}", "{field_2}"],
#		"partial": 1,
#	},
#	{
#		"doctype": "{doctype_2}",
#		"filter_by": "{filter_by}",
#		"partial": 1,
#	},
#	{
#		"doctype": "{doctype_3}",
#		"strict": False,
#	},
#	{
#		"doctype": "{doctype_4}"
#	}
# ]

# Authentication and authorization
# --------------------------------

# auth_hooks = [
#	"frappe_side_menu.auth.validate"
# ]
