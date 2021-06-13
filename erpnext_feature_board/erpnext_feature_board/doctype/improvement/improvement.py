# Copyright (c) 2021, ERPNext Community and contributors
# For license information, please see license.txt

import requests

import frappe
from frappe import _
from frappe.utils import get_datetime
from frappe.website.website_generator import WebsiteGenerator

DISCOURSE_CREATE_TOPIC_ENDPOINT = "/posts"
DISCOURSE_UPDATE_TOPIC_ENDPOINT = "/posts/{id}"


class Improvement(WebsiteGenerator):
	# the WebsiteGenerator class overrides the naming_series in the
	# doctype definition, overriding the override
	autoname = "naming_series:"

	def validate(self):
		if self.deployment_status == "Ready":
			self.sync_discourse_post()

	def sync_discourse_post(self):
		settings = frappe.get_single("Feature Board Settings")
		if not settings.enable_discourse:
			return

		discourse_url = settings.discourse_url
		discourse_api_username = settings.discourse_api_username
		discourse_api_key = settings.get_password("discourse_api_key")
		discourse_post_title = f"[Bot] [Discussion] [PR #{self.number}] {self.title}"
		discourse_post_body = f"<p>Pull Request URL: <a href='{self.pull_request_url}'>{self.pull_request_url}</a><br>Testing Site URL: {self.site_url or self.deployment_status}<p>"

		headers = {
			"Api-Key": discourse_api_key,
			"Api-Username": discourse_api_username,
			"Accept": "application/json"
		}

		if not self.topic_id:
			# create a new post
			data = {
				"title": discourse_post_title,
				"raw": discourse_post_body,
				"created_at": get_datetime().isoformat()
			}

			response = requests.post(discourse_url + DISCOURSE_CREATE_TOPIC_ENDPOINT, headers=headers, data=data)
			if response.ok:
				response_data = response.json()
				self.topic_id = response_data.get("topic_id")
				self.post_id = response_data.get("id")
				self.topic_slug = response_data.get("topic_slug")
		else:
			# update an existing post
			data = {
				"post": {
					"raw": discourse_post_body,
					"edit_reason": "Updating build details via API"
				}
			}

			formatted_endpoint = DISCOURSE_UPDATE_TOPIC_ENDPOINT.format(id=self.post_id)
			requests.put(discourse_url + formatted_endpoint, headers=headers, json=data)


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
