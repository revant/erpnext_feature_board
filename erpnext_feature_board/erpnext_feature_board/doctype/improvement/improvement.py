# Copyright (c) 2021, ERPNext Community and contributors
# For license information, please see license.txt

import requests
import time

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
			frappe.enqueue(method=self.sync_discourse_post)

	def sync_discourse_post(self):
		settings = frappe.get_single("Feature Board Settings")
		if not settings.enable_discourse:
			return

		pull_request_link = f"<a href='{self.pull_request_url}'>{self.pull_request_url}</a>"
		testing_site_link = f"<a href='{self.site_url}'>{self.site_url}</a>" if self.site_url else self.deployment_status
		discourse_post_body = f"""<p>
			<strong>Testing Site URL</strong>: {testing_site_link}<br><br>
			<strong>Pull Request URL</strong>: {pull_request_link}<br>
			<strong>Pull Request Title</strong>: {self.title}<br>
			<strong>Pull Request Description</strong>: {self.description}
		"""

		frappe.log_error(discourse_post_body)

		if not self.post_id:
			self.create_discourse_post(settings, discourse_post_body)
		else:
			self.update_discourse_post(settings, discourse_post_body)

	def create_discourse_post(self, settings, discourse_post_body, retry=3):
		headers = {
			"Api-Key": settings.get_password("discourse_api_key"),
			"Api-Username": settings.discourse_api_username,
			"Accept": "application/json"
		}

		discourse_post_title = f"[Bot] [Discussion] [PR #{self.number}] {self.title}"

		data = {
			"title": discourse_post_title,
			"raw": discourse_post_body,
			"created_at": get_datetime().isoformat()
		}

		while retry > 0:
			try:
				response = requests.post(
					settings.discourse_url + DISCOURSE_CREATE_TOPIC_ENDPOINT,
					headers=headers,
					data=data
				)
			except Exception as e:
				frappe.log_error(_(e))
				time.sleep(5)
				self.create_discourse_post(settings, discourse_post_body, retry=retry - 1)
			else:
				if response.ok:
					response_data = response.json()
					self.topic_id = response_data.get("topic_id")
					self.post_id = response_data.get("id")
					self.topic_slug = response_data.get("topic_slug")
				break

	def update_discourse_post(self, settings, discourse_post_body, retry=3):
		headers = {
			"Api-Key": settings.get_password("discourse_api_key"),
			"Api-Username": settings.discourse_api_username,
			"Accept": "application/json"
		}

		data = {
			"post": {
				"raw": discourse_post_body,
				"edit_reason": "Updating build details via API"
			}
		}

		formatted_endpoint = DISCOURSE_UPDATE_TOPIC_ENDPOINT.format(id=self.post_id)

		while retry > 0:
			try:
				requests.put(settings.discourse_url + formatted_endpoint, headers=headers, json=data)
			except Exception as e:
				frappe.log_error(_(e))
				time.sleep(5)
				self.update_discourse_post(settings, discourse_post_body, retry=retry - 1)
			else:
				break


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
