# Copyright (c) 2021, ERPNext Community and contributors
# For license information, please see license.txt

import uuid

import frappe
from frappe import _
from frappe.model.document import Document


class ReviewRequest(Document):
	def autoname(self):
		self.name = str(uuid.uuid4())


@frappe.whitelist()
def get_test_user_password(review_request):
	request = frappe.get_doc("Review Request", review_request)

	if request.user != frappe.session.user:
		frappe.throw(_("Not Permitted"))
		return None

	if request.test_user_password:
		return request.get_password("test_user_password")
