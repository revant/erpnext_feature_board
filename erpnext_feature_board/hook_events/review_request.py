import frappe


def delete_approved_build_requests():
	"""
	Scheduled hook to delete approved Review Requests for changing site deployments.
	"""

	approved_build_requests = frappe.get_all(
		"Review Request",
		filters={
			"request_type": ["in", ["Build", "Upgrade", "Delete"]],
			"request_status": "Approved",
		},
	)

	for request in approved_build_requests:
		frappe.delete_doc("Review Request", request.name)
