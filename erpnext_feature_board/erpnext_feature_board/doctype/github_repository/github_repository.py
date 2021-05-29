# Copyright (c) 2021, ERPNext Community and contributors
# For license information, please see license.txt

from typing import TYPE_CHECKING

import json

from github import Github
from github.GithubException import BadCredentialsException, UnknownObjectException
from giturlparse import parse
from giturlparse.parser import ParserError

import frappe
from frappe import _
from frappe.model.document import Document
from frappe.utils import markdown

if TYPE_CHECKING:
	from github.PullRequest import PullRequest


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
		frappe.enqueue(method=create_repository_improvements, repository=self.name)


def create_repository_improvements(repository: str):
	repo_doc: GithubRepository = frappe.get_doc("Github Repository", repository)
	repo = repo_doc.connect()
	if not repo:
		return

	pull_requests = repo.get_pulls(state="open")
	for pull in pull_requests:
		update_improvement(pull, repository)


def update_improvement(pull_request: "PullRequest", repository: str):
	if not frappe.db.exists("Improvement", {"pull_request_url": pull_request.html_url}):
		improvement_doc = frappe.new_doc("Improvement")
	else:
		improvement = frappe.db.get_value("Improvement", {"pull_request_url": pull_request.html_url})
		improvement_doc = frappe.get_doc("Improvement", improvement)

	improvement_doc.update({
		"branch": pull_request.head.ref,
		"description": markdown(pull_request.body),
		"fork_url": pull_request.head.repo.html_url,
		"number": pull_request.number,
		"pull_request_url": pull_request.html_url,
		"raw_data": json.dumps(pull_request.raw_data),
		"repository": repository,
		"status": pull_request.state.title(),
		"title": pull_request.title[:140]
	})
	improvement_doc.save()
