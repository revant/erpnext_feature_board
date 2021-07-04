# Copyright (c) 2021, ERPNext Community and contributors
# For license information, please see license.txt

import json
import uuid

import frappe
import requests
from frappe import _
from frappe.model.document import Document


class ReviewRequest(Document):
	def autoname(self):
		self.name = str(uuid.uuid4())

	def validate(self):
		self.validate_user()
		self.validate_status()
		self.approve_duplicate_requests()

	def validate_user(self):
		if (
			frappe.session.user in ["Guest", "Administrator"]
			and not frappe.get_conf().get("developer_mode")
		):
			frappe.throw(_("Invalid User: Guest or Administrator not allowed"))

		if not self.user:
			self.user = frappe.session.user

	def validate_status(self):
		if not self.request_status:
			self.request_status = "Open"

	def approve_duplicate_requests(self):
		if self.request_status != "Approved":
			return

		existing_requests = frappe.get_all(
			"Review Request",
			filters={
				"request_status": "Open",
				"request_type": self.request_type,
				"improvement": self.improvement,
			},
		)

		for request in existing_requests:
			frappe.db.set_value("Review Request", request.name, "request_status", "Approved")


@frappe.whitelist()
def get_test_user_password(review_request):
	request = frappe.get_doc("Review Request", review_request)

	if request.user != frappe.session.user:
		frappe.throw(_("Not Permitted"))
		return None

	if request.test_user_password:
		return request.get_password("test_user_password")


@frappe.whitelist(methods=["POST"])
def create_test_user_for_improvement(improvement_name, review_request_uuid):
	session = requests.Session()

	if "System Manager" not in frappe.get_roles(frappe.session.user):
		frappe.throw(_("Insufficient Permission"))

	improvement = frappe.get_doc("Improvement", improvement_name)
	review_request = frappe.get_doc("Review Request", review_request_uuid)

	if review_request.request_type != "Add Testing User":
		frappe.throw(_(f"Incorrect request type: {review_request.request_type}"))
	if review_request.request_status != "Open":
		frappe.throw(_(f"Incorrect request status: {review_request.request_status}"))
	if not improvement.site_url:
		frappe.throw(_(f"Site URL not found for {improvement.name}"))
	if improvement.deployment_status != "Ready":
		frappe.throw(_(f"Deployment is not ready for {improvement.name}"))

	session.post(
		f"{improvement.site_url}/api/method/login",
		data={
			"usr": "Administrator",
			"pwd": improvement.get_password("site_admin_password"),
		},
	)

	email = frappe.mock("email")
	first_name = frappe.mock("first_name")
	new_password = frappe.generate_hash(length=10)
	user = {
		"email": email,
		"first_name": first_name,
		"new_password": new_password,
		"send_welcome_email": 0,
		"roles": [{"role": "System Manager"}],
	}

	session.post(f"{improvement.site_url}/api/resource/User", data=json.dumps(user))

	review_request.test_user_name = email
	review_request.test_user_password = new_password
	review_request.request_status = "Approved"
	review_request.save()

	return review_request.as_dict()
