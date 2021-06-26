import frappe
from frappe import _


def get_context(context):
	improvement_name = frappe.local.request.args.get("name")
	context.parents = [dict(route='/improvements', label=_('Improvements'))]

	if improvement_name:
		context["query"] = improvement_name
	else:
		frappe.local.flags.redirect_location = '/improvements'
		raise frappe.Redirect
