import frappe
from frappe import _


def get_context(context):
	if frappe.session.user == "Guest":
		frappe.throw(_("Login to access improvements"), exc=frappe.PermissionError)

