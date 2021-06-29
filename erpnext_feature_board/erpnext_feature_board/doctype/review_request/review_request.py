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
		if (
			frappe.session.user == "Guest"
			or not frappe.get_conf().get("developer_mode")
			and frappe.session.user == "Administrator"
		):
			frappe.throw(_("Invalid User, Guest or Administrator not allowed"))

		if not self.user:
			self.user = frappe.session.user

		if not self.request_status:
			self.request_status = "Open"


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
	s = requests.Session()

	if "System Manager" not in frappe.get_roles(frappe.session.user):
		frappe.throw(_("Insufficient Permission"))

	improvement = frappe.get_doc("Improvement", improvement_name)
	review_request = frappe.get_doc("Review Request", review_request_uuid)

	if review_request.request_type != "Add Testing User":
		frappe.throw(
			_("Incorrect Request Type : {0}".format(review_request.request_type))
		)

	if review_request.request_status != "Open":
		frappe.throw(
			_("Incorrect Request Status : {0}".format(review_request.request_status))
		)

	if not improvement.site_url:
		frappe.throw(_("Site URL Not found for {0}".format(improvement.name)))

	if improvement.deployment_status != "Ready":
		frappe.throw(_("Deployment Status Not Ready for {0}".format(improvement.name)))

	s.post(
		f"{improvement.site_url}/api/method/login",
		data={
			"usr": "Administrator",
			"pwd": improvement.get_password("site_admin_password"),
		},
	).json()

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

	s.post(f"{improvement.site_url}/api/resource/User", data=json.dumps(user)).json()

	review_request.test_user_name = email
	review_request.test_user_password = new_password
	review_request.request_status = "Approved"
	review_request.save()

	return review_request.as_dict()
