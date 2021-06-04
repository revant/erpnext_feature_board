# Copyright (c) 2021, ERPNext Community and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.website.website_generator import WebsiteGenerator


class Improvement(WebsiteGenerator):
	# the WebsiteGenerator class overrides the naming_series in the
	# doctype definition, overriding the override
	autoname = "naming_series:"


@frappe.whitelist(methods=["POST"])
def queue_deployment(improvement_name):
	return set_deployment_status(
		improvement_name,
		"Build Queued",
	).as_dict()


@frappe.whitelist(methods=["POST"])
def queue_upgrade(improvement_name):
	return set_deployment_status(
		improvement_name,
		"Upgrade Queued",
	).as_dict()


@frappe.whitelist(methods=["POST"])
def queue_delete(improvement_name):
	return set_deployment_status(
		improvement_name,
		"Delete Queued",
	).as_dict()


def set_deployment_status(improvement_name, deployment_status):
	imps_under_process = frappe.get_list(
		"Improvement",
		filters={
			"deployment_status": [
				"in",
				[
					"Build Queued",
					"Building",
					"Build Complete",
					"Release Queued",
					"Upgrade Queued",
					"Rebuilding",
					"Rebuild Complete",
					"Upgrading",
					"Delete Queued",
					"Release Deleted",
				],
			],
		},
	)
	if imps_under_process:
		frappe.throw(_("Improvements already under process"))

	improvement = frappe.get_doc("Improvement", improvement_name)
	improvement.deployment_status = deployment_status
	improvement.save()
	return improvement
