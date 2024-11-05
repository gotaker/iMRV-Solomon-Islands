from . import __version__ as app_version
# from mrvtools.route import routes


app_name = "mrvtools"
app_title = "Mrvtools"
app_publisher = "tridotstech"
app_description = "mrvtools"
app_email = "info@tridotstech.com"
app_license = "MIT"


website_redirects = [
    {"source": "/", "target": "/frontend/home"},
]  

permission_query_conditions = {
    "My Approval":"mrvtools.mrvtools.doctype.my_approval.my_approval.get_query_conditions",
    "Approved User":"mrvtools.mrvtools.doctype.approved_user.approved_user.get_query_conditions"
}
# website_route_rules = routes

# Includes in <head>
# ------------------

# include js, css files in header of desk.html
app_include_css = "/assets/mrvtools/css/mrvtools.css"
app_include_js = ["/assets/mrvtools/js/mrvtools.js","/assets/mrvtools/js/map_defaults.js"]
# app_include_js = "/assets/mrvtools/js/adaptationreport.js"

website_route_rules = [{'from_route': '/frontend/<path:app_path>', 'to_route': 'frontend'},{"from_route":"/login","to_route":"custom_login"},]

after_install = "mrvtools.mrvtools.after_install.after_install"
# include js, css files in header of web template
# web_include_css = "/assets/mrvtools/css/mrvtools.css"
# web_include_js = "/assets/mrvtools/js/mrvtools.js"

# include custom scss in every website theme (without file extension ".scss")
# website_theme_scss = "mrvtools/public/scss/website"

# include js, css files in header of web form
# webform_include_js = {"doctype": "public/js/doctype.js"}
# webform_include_css = {"doctype": "public/css/doctype.css"}

# include js in page
# page_js = {"page" : "templates/pages/adaptationreport.js"}

# include js in doctype views
# doctype_js = {"doctype" : "public/js/doctype.js"}
doctype_js = {"User" : "public/js/user.js"}
# doctype_list_js = {"doctype" : "public/js/doctype_list.js"}
doctype_list_js = {"User" : "public/js/user_list.js"}
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
#	"methods": "mrvtools.utils.jinja_methods",
#	"filters": "mrvtools.utils.jinja_filters"
# }

# Installation
# ------------

# before_install = "mrvtools.install.before_install"
# after_install = "mrvtools.install.after_install"

# Uninstallation
# ------------

# before_uninstall = "mrvtools.uninstall.before_uninstall"
# after_uninstall = "mrvtools.uninstall.after_uninstall"

# Desk Notifications
# ------------------
# See frappe.core.notifications.get_notification_config

# notification_config = "mrvtools.notifications.get_notification_config"

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
#		"mrvtools.tasks.all"
#	],
#	"daily": [
#		"mrvtools.tasks.daily"
#	],
#	"hourly": [
#		"mrvtools.tasks.hourly"
#	],
#	"weekly": [
#		"mrvtools.tasks.weekly"
#	],
#	"monthly": [
#		"mrvtools.tasks.monthly"
#	],
# }

# Testing
# -------

# before_tests = "mrvtools.install.before_tests"

# Overriding Methods
# ------------------------------
#
# override_whitelisted_methods = {
#	"frappe.desk.doctype.event.event.get_events": "mrvtools.event.get_events"
# }
#
# each overriding function accepts a `data` argument;
# generated from the base implementation of the doctype dashboard,
# along with any modifications made in other Frappe apps
# override_doctype_dashboards = {
#	"Task": "mrvtools.task.get_dashboard_data"
# }

# exempt linked doctypes from being automatically cancelled
#
# auto_cancel_exempted_doctypes = ["Auto Repeat"]

# Ignore links to specified DocTypes when deleting documents
# -----------------------------------------------------------

# ignore_links_on_delete = ["Communication", "ToDo"]

# Request Events
# ----------------
# before_request = ["mrvtools.utils.before_request"]
# after_request = ["mrvtools.utils.after_request"]

# Job Events
# ----------
# before_job = ["mrvtools.utils.before_job"]
# after_job = ["mrvtools.utils.after_job"]

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
#	"mrvtools.auth.validate"
# ]

