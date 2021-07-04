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
	from erpnext_feature_board.erpnext_feature_board.doctype.improvement.improvement import Improvement
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
		except BadCredentialsException:
			# process 403 errors
			frappe.throw(_("Invalid Github URL"))
		except UnknownObjectException:
			# process 404 errors
			frappe.throw(_("""The repository was not found. If your repository is private,
				please generate and set a personal access token with read permissions for 'repo'."""))

	def connect(self, raise_exception=False):
		github_url = parse(self.repository_url)
		client = Github(
			login_or_token=self.get_password("access_token") if self.access_token else None
		)

		repo = None
		try:
			repo = client.get_repo(f"{github_url.owner}/{github_url.name}")
		except (BadCredentialsException, UnknownObjectException) as e:
			if raise_exception:
				raise e

		return repo

	@frappe.whitelist()
	def sync_pull_requests(self):
		frappe.enqueue(method=sync_improvements, repository=self.name)


def sync_improvements(repository: str):
	"""
	Syncs and updates Improvement records from Github
		- Sync pull requests for existing and open Improvements from Github
		- Fetch open pull requests from the repository and create new Improvement records

	Args:
		repository (str): The ID of the Github Repository document
	"""

	repo_doc: GithubRepository = frappe.get_doc("Github Repository", repository)
	repo = repo_doc.connect()
	if not repo:
		return

	synced_improvements = []

	# sync existing Improvements from Github
	repository_improvements = frappe.get_all("Improvement",
		filters={"repository": repository, "status": "Open"},
		fields=["number"])

	for improvement in repository_improvements:
		improvement_pr = repo.get_pull(int(improvement.number))
		sync_improvement(improvement_pr, repository)
		synced_improvements.append(improvement.number)

	# fetch open pull requests and sync new improvements
	pull_requests = repo.get_pulls(state="open")
	for pull in pull_requests:
		if pull.number not in synced_improvements:
			sync_improvement(pull, repository)
			synced_improvements.append(pull.number)


def sync_improvement(pull_request: "PullRequest", repository: str):
	if not frappe.db.exists("Improvement", {"pull_request_url": pull_request.html_url}):
		improvement_doc: "Improvement" = frappe.new_doc("Improvement")
	else:
		improvement = frappe.db.get_value("Improvement", {"pull_request_url": pull_request.html_url})
		improvement_doc: "Improvement" = frappe.get_doc("Improvement", improvement)

	# extract app name from the pull request; if none found, don't process improvement
	if pull_request.head.repo:
		app_name = pull_request.head.repo.name
	elif pull_request.base.repo:
		app_name = pull_request.base.repo.name
	else:
		return

	# Github sets a PR's status as either "open" or "closed"; use the API to check if it has been merged
	if pull_request.is_merged():
		pull_status = "Merged"
	else:
		pull_status = pull_request.state.title()

	improvement_doc.update({
		"app_name": app_name,
		"description": markdown(pull_request.body),
		"fork_url": pull_request.head.repo.html_url if pull_request.head.repo else None,
		"number": pull_request.number,
		"pull_request_url": pull_request.html_url,
		"raw_data": json.dumps(pull_request.raw_data),
		"repository": repository,
		# create a unique route based on the PR details
		"route": f"/improvement/{app_name}/{pull_request.number}",
		"source_branch": pull_request.head.ref,
		"status": pull_status,
		"target_branch": pull_request.base.ref,
		"title": pull_request.title[:140]
	})
	improvement_doc.save()
