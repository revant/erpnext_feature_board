# Copyright (c) 2021, ERPNext Community and contributors
# For license information, please see license.txt

import json

from github import Github
from github.GithubException import BadCredentialsException, UnknownObjectException
from giturlparse import parse
from giturlparse.parser import ParserError

import frappe
from frappe import _
from frappe.model.document import Document


class GithubRepository(Document):
	def validate(self):
		self.validate_github_url()

	def validate_github_url(self):
		try:
			github_url = parse(self.repository_url)
		except ParserError:
			frappe.throw(_("Invalid Github URL"))

		if not (github_url.owner and github_url.name):
			frappe.throw(_("Invalid Github URL"))

		try:
			self.connect(raise_exception=True)
		except (BadCredentialsException, UnknownObjectException):
			frappe.throw(_("Invalid Github URL"))

	def connect(self, raise_exception=False):
		github_url = parse(self.repository_url)
		client = Github(self.get_password("access_token"))

		repo = None
		try:
			repo = client.get_repo(f"{github_url.owner}/{github_url.name}")
		except (BadCredentialsException, UnknownObjectException) as e:
			if raise_exception:
				raise e

		return repo

	@frappe.whitelist()
	def sync_pull_requests(self):
		repo = self.connect()
		pull_requests = repo.get_pulls(state="open")
		for pull in pull_requests:
			improvement = frappe.new_doc("Improvement")
			improvement.update({
				"repository": self.name,
				"title": pull.title[:140],
				"branch": pull.head.ref,
				"raw_data": json.dumps(pull.raw_data),
				"url": pull.html_url,
				"status": pull.state.title(),
				"number": pull.number
			})
			improvement.insert()
