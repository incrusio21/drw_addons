from . import __version__ as app_version

app_name = "addons"
app_title = "Addons"
app_publisher = "DAS"
app_description = "Addons"
app_icon = "octicon octicon-file-directory"
app_color = "grey"
app_email = "DAS"
app_license = "MIT"

# Includes in <head>
# ------------------

# include js, css files in header of desk.html
# app_include_css = "/assets/addons/css/addons.css"
# app_include_js = "/assets/addons/js/addons.js"

# include js, css files in header of web template
# web_include_css = "/assets/addons/css/addons.css"
# web_include_js = "/assets/addons/js/addons.js"

# include custom scss in every website theme (without file extension ".scss")
# website_theme_scss = "addons/public/scss/website"

# include js, css files in header of web form
# webform_include_js = {"doctype": "public/js/doctype.js"}
# webform_include_css = {"doctype": "public/css/doctype.css"}

# include js in page
page_js = {
    "point-of-sale" : "public/js/page/point_of_sale.js"
}

# include js in doctype views
doctype_js = {
    "Travel Request" : "public/js/travel_request.js",
    "Sales Order" : "public/js/sales_order.js",
    "Sales Invoice" : "public/js/sales_invoice.js",
    "Therapy Session" : "public/js/therapy_session.js",
    "Material Request" : "public/js/material_request.js",
    "POS Opening Entry": "public/js/pos_opening_entry.js",
}

# doctype_list_js = {"doctype" : "public/js/doctype_list.js"}
# doctype_tree_js = {"doctype" : "public/js/doctype_tree.js"}
# doctype_calendar_js = {"doctype" : "public/js/doctype_calendar.js"}


fixtures = [
    "Custom Field"
]
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

# Installation
# ------------

# before_install = "addons.install.before_install"
# after_install = "addons.install.after_install"

# Uninstallation
# ------------

# before_uninstall = "addons.uninstall.before_uninstall"
# after_uninstall = "addons.uninstall.after_uninstall"

# Desk Notifications
# ------------------
# See frappe.core.notifications.get_notification_config

# notification_config = "addons.notifications.get_notification_config"

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

fixtures = [
	{
		"dt": "Client Script"
	},
    {
		"dt": "Server Script"
	},
	{
		"dt": "Custom Field"
	},
    {
		"dt": "Property Setter"
	},
]

jenv = {
    "filters": [
        "get_qr_svg_code_asset:addons.jinja.get_qr_svg_code_asset",
	],
    "methods": [
        "get_qr_svg_code:addons.jinja.get_qr_svg_code",
	]
}

# DocType Class
# ---------------
# Override standard doctype classes

# override_doctype_class = {
#	"ToDo": "custom_app.overrides.CustomToDo"
# }

# Document Events
# ---------------
# Hook on document methods and events

doc_events = {
    "Travel Request": {
		"validate": "addons.custom.travel_request.validate"	
	},
    "Patient": {
		"on_update": "addons.custom.patient.update_customer"	
	},
    "Customer": {
		"validate": "addons.custom.customer.validate"	
	},
    "Sales Order": {
		"before_validate": "addons.custom.sales_order.validate_coin",		
		"on_submit": [
            "addons.custom.sales_order.agent_coin_log", 
            "addons.custom.sales_order.agent_cashback_log", 
            "addons.custom.sales_order.agent_point_log", 
            "addons.custom.sales_order.make_invoice", "addons.custom.sales_order.update_field_get"],		
		"on_cancel": ["addons.custom.sales_order.agent_coin_log", "addons.custom.sales_order.agent_cashback_log", "addons.custom.sales_order.agent_point_log", "addons.custom.sales_order.remove_invoice"],		
	},
	"Delivery Note": {
		"on_submit": "addons.custom.delivery_note.create_agent_stock_log",		
		"on_cancel": "addons.custom.delivery_note.delete_log",		
	},
    "Item": {
        "before_rename": "addons.custom.item.delete_old_agent_stock_bin",
        "after_rename": "addons.custom.item.recalculate_agent_stock_bin",
	},
    "GL Entry": {
		"on_submit": "addons.custom.gl_entry.cek_form_budget",
	},
}

# Scheduled Tasks
# ---------------

# scheduler_events = {
#	"all": [
#		"addons.tasks.all"
#	],
#	"daily": [
#		"addons.tasks.daily"
#	],
#	"hourly": [
#		"addons.tasks.hourly"
#	],
#	"weekly": [
#		"addons.tasks.weekly"
#	]
#	"monthly": [
#		"addons.tasks.monthly"
#	]
# }

# Testing
# -------

# before_tests = "addons.install.before_tests"

# Overriding Methods
# ------------------------------
#
override_whitelisted_methods = {
	"erpnext.selling.page.point_of_sale.point_of_sale.get_items": "addons.custom.page.point_of_sale.get_items",
    "erpnext.accounts.doctype.sales_invoice.sales_invoice.make_delivery_note": "addons.custom.sales_invoice.make_delivery_note"
}
#
# each overriding function accepts a `data` argument;
# generated from the base implementation of the doctype dashboard,
# along with any modifications made in other Frappe apps
# override_doctype_dashboards = {
#	"Task": "addons.task.get_dashboard_data"
# }

# exempt linked doctypes from being automatically cancelled
#
# auto_cancel_exempted_doctypes = ["Auto Repeat"]


# User Data Protection
# --------------------

user_data_fields = [
	{
		"doctype": "{doctype_1}",
		"filter_by": "{filter_by}",
		"redact_fields": ["{field_1}", "{field_2}"],
		"partial": 1,
	},
	{
		"doctype": "{doctype_2}",
		"filter_by": "{filter_by}",
		"partial": 1,
	},
	{
		"doctype": "{doctype_3}",
		"strict": False,
	},
	{
		"doctype": "{doctype_4}"
	}
]

# Authentication and authorization
# --------------------------------

# auth_hooks = [
#	"addons.auth.validate"
# ]


