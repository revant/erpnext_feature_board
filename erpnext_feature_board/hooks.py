from . import __version__ as app_version

app_name = "erpnext_feature_board"
app_title = "ERPNext Feature Board"
app_publisher = "ERPNext Community"
app_description = "Feature board for ERPNext"
app_icon = "octicon octicon-file-directory"
app_color = "grey"
app_email = "community@erpnext.com"
app_license = "MIT"

# Includes in <head>
# ------------------

# include js, css files in header of desk.html
# app_include_css = "/assets/erpnext_feature_board/css/erpnext_feature_board.css"
# app_include_js = "/assets/erpnext_feature_board/js/erpnext_feature_board.js"

# include js, css files in header of web template
web_include_css = [
	"/assets/erpnext_feature_board/css/webcomponents.css",
	"https://fonts.googleapis.com/icon?family=Material+Icons&display=block",
]
web_include_js = [
	"/assets/erpnext_feature_board/js/webcomponents.js",
]

# include custom scss in every website theme (without file extension ".scss")
# website_theme_scss = "erpnext_feature_board/public/scss/website"

# include js, css files in header of web form
# webform_include_js = {"doctype": "public/js/doctype.js"}
# webform_include_css = {"doctype": "public/css/doctype.css"}

# include js in page
# page_js = {"page" : "public/js/file.js"}

# include js in doctype views
# doctype_js = {"doctype" : "public/js/doctype.js"}
# doctype_list_js = {"doctype" : "public/js/doctype_list.js"}
# doctype_tree_js = {"doctype" : "public/js/doctype_tree.js"}
# doctype_calendar_js = {"doctype" : "public/js/doctype_calendar.js"}

# Home Pages
# ----------

# application home page (will override Website Settings)
home_page = "improvements"

# website user home page (by Role)
# role_home_page = {
# 	"Role": "home_page"
# }

# Generators
# ----------

# automatically create page for each record of this doctype
# website_generators = ["Web Page"]

# Jinja
# ----------

# add methods and filters to jinja environment
# jinja = {
# 	"methods": "erpnext_feature_board.utils.jinja_methods",
# 	"filters": "erpnext_feature_board.utils.jinja_filters"
# }

# Installation
# ------------

# before_install = "erpnext_feature_board.install.before_install"
# after_install = "erpnext_feature_board.install.after_install"

# Desk Notifications
# ------------------
# See frappe.core.notifications.get_notification_config

# notification_config = "erpnext_feature_board.notifications.get_notification_config"

# Permissions
# -----------
# Permissions evaluated in scripted ways

# permission_query_conditions = {
# 	"Event": "frappe.desk.doctype.event.event.get_permission_query_conditions",
# }
#
# has_permission = {
# 	"Event": "frappe.desk.doctype.event.event.has_permission",
# }

# DocType Class
# ---------------
# Override standard doctype classes

# override_doctype_class = {
# 	"ToDo": "custom_app.overrides.CustomToDo"
# }

# Document Events
# ---------------
# Hook on document methods and events

# doc_events = {
# 	"*": {
# 		"on_update": "method",
# 		"on_cancel": "method",
# 		"on_trash": "method"
# 	}
# }

# Scheduled Tasks
# ---------------

scheduler_events = {
	"hourly": [
		"erpnext_feature_board.hook_events.github_repository.sync_repository_improvements",
		"erpnext_feature_board.hook_events.improvement.delete_closed_improvements",
		"erpnext_feature_board.hook_events.review_request.delete_approved_build_requests"
	],
	"all": [
		"erpnext_feature_board.tasks.deploy.process_build_queue_improvements",
		"erpnext_feature_board.tasks.deploy.process_building_improvements",
		"erpnext_feature_board.tasks.deploy.process_build_complete_improvements",
		"erpnext_feature_board.tasks.deploy.process_release_queued_improvements",
		"erpnext_feature_board.tasks.deploy.process_upgrade_queued_improvements",
		"erpnext_feature_board.tasks.deploy.process_rebuilding_improvements",
		"erpnext_feature_board.tasks.deploy.process_rebuild_complete_improvements",
		"erpnext_feature_board.tasks.deploy.process_upgrading_improvements",
		"erpnext_feature_board.tasks.deploy.process_delete_queued_improvements",
		"erpnext_feature_board.tasks.deploy.process_release_deleted_improvements",
	],
}

# Testing
# -------

# before_tests = "erpnext_feature_board.install.before_tests"

# Overriding Methods
# ------------------------------
#
# override_whitelisted_methods = {
# 	"frappe.desk.doctype.event.event.get_events": "erpnext_feature_board.event.get_events"
# }
#
# each overriding function accepts a `data` argument;
# generated from the base implementation of the doctype dashboard,
# along with any modifications made in other Frappe apps
# override_doctype_dashboards = {
# 	"Task": "erpnext_feature_board.task.get_dashboard_data"
# }

# exempt linked doctypes from being automatically cancelled
#
# auto_cancel_exempted_doctypes = ["Auto Repeat"]


# User Data Protection
# --------------------

# user_data_fields = [
# 	{
# 		"doctype": "{doctype_1}",
# 		"filter_by": "{filter_by}",
# 		"redact_fields": ["{field_1}", "{field_2}"],
# 		"partial": 1,
# 	},
# 	{
# 		"doctype": "{doctype_2}",
# 		"filter_by": "{filter_by}",
# 		"partial": 1,
# 	},
# 	{
# 		"doctype": "{doctype_3}",
# 		"strict": False,
# 	},
# 	{
# 		"doctype": "{doctype_4}"
# 	}
# ]

# Authentication and authorization
# --------------------------------

# auth_hooks = [
# 	"erpnext_feature_board.auth.validate"
# ]
