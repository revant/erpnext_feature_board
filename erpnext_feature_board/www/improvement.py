import frappe
from frappe import _


def get_context(context):
	context.no_cache = 1

	improvement_name = frappe.local.request.args.get("name")
	context.parents = [dict(route='/improvements', label=_('Improvements'))]

	if improvement_name:
		context.query = improvement_name
		context.user = frappe.session.user
		context.csrf_token = frappe.local.session.data.csrf_token
	else:
		frappe.local.flags.redirect_location = '/improvements'
		raise frappe.Redirect
