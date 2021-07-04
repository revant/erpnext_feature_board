from typing import TYPE_CHECKING, List

import frappe
from erpnext_feature_board.erpnext_feature_board.doctype.improvement.improvement import (
	queue_delete,
)

if TYPE_CHECKING:
	from erpnext_feature_board.erpnext_feature_board.doctype.improvement.improvement import (
		Improvement,
	)


def delete_closed_improvements():
	"""
	Scheduled hook to clear out closed Improvements and any linked Review Requests.
	"""

	closed_improvements: List["Improvement"] = frappe.get_all(
		"Improvement",
		filters={"status": ["in", ["Closed", "Merged"]]},
		fields=["name", "deployment_status"]
	)

	for improvement in closed_improvements:
		if improvement.deployment_status:
			# if a site is still deployed for the improvement, mark the site for deletion
			queue_delete(improvement.name)
			continue

		# if there is no linked site to it, delete all linked review requests
		# and finally delete the improvement itself
		improvement_review_requests = frappe.get_all(
			"Review Request", filters={"improvement": improvement.name}
		)

		for request in improvement_review_requests:
			frappe.delete_doc("Review Request", request.name)

		frappe.delete_doc("Improvement", improvement.name)
