import frappe
from frappe import _
from frappe.desk.reportview import get_count as get_filtered_count
from frappe.desk.reportview import get_form_params


def get_context(context):
	context.no_cache = 1


@frappe.whitelist(allow_guest=True)
def get_improvements():
	args = get_form_params()
	docs = frappe.get_list(**args)

	frappe.local.form_dict.pop("limit_page_length", None)

	return {
		"docs": docs,
		"length": get_filtered_count(),
	}
