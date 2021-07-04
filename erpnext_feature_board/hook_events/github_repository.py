import frappe
from erpnext_feature_board.erpnext_feature_board.doctype.github_repository.github_repository import (
	sync_improvements,
)


def sync_repository_improvements():
	"""
	Scheduled hook to sync pull requests from all repositories and update Improvement records
	"""
	for repo in frappe.get_all("Github Repository"):
		sync_improvements(repo.name)
