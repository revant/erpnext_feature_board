import time

import frappe
from erpnext_feature_board.clients.container_registry import delete_image_tag
from erpnext_feature_board.clients.k8s import (
	create_build_image_job,
	create_helm_release,
	delete_helm_release,
	delete_job,
	get_helm_release,
	get_job_status,
	get_namespace,
	rollout_deployment,
	update_helm_release,
)


# TODO: Only allow configurable (default=1) build/deployment to run at a time
# TODO: Limit number of improvements with deployments through settings or config
def process_build_queue_improvements():
	improvement = None
	try:
		improvement = frappe.get_last_doc(
			"Improvement",
			filters={"deployment_status": "Build Queued"},
			order_by="modified asc",
		)

		job_name = f"build-{improvement.name}".lower()  # only lowercase only allowed
		res = create_build_job(improvement)

		if res.get("error"):
			improvement.deployment_status = "Build Queue Failed"
			improvement.save()
			frappe.db.commit()

		elif res.get("metadata", {}).get("name") == job_name:
			improvement.deployment_status = "Building"
			improvement.save()
			frappe.db.commit()

	except frappe.DoesNotExistError:
		print("No Improvement in 'Build Queued' state")


def process_building_improvements():
	improvement = None
	try:
		improvement = frappe.get_last_doc(
			"Improvement",
			filters={"deployment_status": "Building"},
			order_by="modified asc",
		)
		job_name = f"build-{improvement.name}".lower()
		status = get_job_status(job_name)
		if status.get("error") or status.get("status", {}).get("failed"):
			improvement.deployment_status = "Build Error"
			improvement.save()
			frappe.db.commit()
		elif status.get("status", {}).get("succeeded"):
			improvement.deployment_status = "Build Complete"
			improvement.save()
			delete_job(job_name)
			frappe.db.commit()

	except frappe.DoesNotExistError:
		print("No Improvement is 'Building' state")


def process_build_complete_improvements():
	improvement = None
	try:
		improvement = frappe.get_last_doc(
			"Improvement",
			filters={"deployment_status": "Build Complete"},
			order_by="modified asc",
		)

		domain_name = frappe.get_conf().get("domain_name", "test-erpnext.org")
		site_name = improvement.name.lower() + "." + domain_name
		site_password = frappe.generate_hash(length=10)

		improvement.site_url = "https://" + site_name
		improvement.site_admin_password = site_password

		status = create_helm_release(improvement.name, site_name, site_password)

		if status.get("metadata", {}).get("name") == improvement.name.lower():
			improvement.deployment_status = "Release Queued"
		elif status.get("error"):
			improvement.deployment_status = "Release Queue Failed"

		improvement.save()

	except frappe.DoesNotExistError:
		print("No Improvement is 'Build Complete' state")

	finally:
		frappe.db.commit()


def process_release_queued_improvements():
	improvement = None
	try:
		improvement = frappe.get_last_doc(
			"Improvement",
			filters={"deployment_status": "Release Queued"},
			order_by="modified asc",
		)

		status = get_job_status(
			f"{get_namespace()}-{improvement.name.lower()}-erpnext-create-site"
		)

		if status.get("error") or status.get("status", {}).get("failed"):
			improvement.deployment_status = "Release Error"
			improvement.save()
			frappe.db.commit()
		elif status.get("status", {}).get("succeeded"):
			improvement.deployment_status = "Ready"
			improvement.save()
			frappe.db.commit()

	except frappe.DoesNotExistError:
		print("No Improvement is 'Release Queued' state")


def process_upgrade_queued_improvements():
	improvement = None
	try:
		improvement = frappe.get_last_doc(
			"Improvement",
			filters={"deployment_status": "Upgrade Queued"},
			order_by="modified asc",
		)

		job_name = f"build-{improvement.name}".lower()  # only lowercase only allowed
		res = create_build_job(improvement)

		if res.get("error"):
			improvement.deployment_status = "Upgrade Queue Failed"
			improvement.save()
			frappe.db.commit()
		elif res.get("metadata", {}).get("name") == job_name:
			improvement.deployment_status = "Rebuilding"
			improvement.save()
			frappe.db.commit()

	except frappe.DoesNotExistError:
		print("No Improvement is 'Upgrade Queued' state")


def process_rebuilding_improvements():
	improvement = None
	try:
		improvement = frappe.get_last_doc(
			"Improvement",
			filters={"deployment_status": "Rebuilding"},
			order_by="modified asc",
		)
		job_name = f"build-{improvement.name}".lower()
		status = get_job_status(job_name)
		if status.get("error") or status.get("status", {}).get("failed"):
			improvement.deployment_status = "Rebuild Error"
			improvement.save()
			frappe.db.commit()
		elif status.get("status", {}).get("succeeded"):
			improvement.deployment_status = "Rebuild Complete"
			improvement.save()
			delete_job(job_name)
			frappe.db.commit()

	except frappe.DoesNotExistError:
		print("No Improvement is 'Rebuilding' state")


def process_rebuild_complete_improvements():
	improvement = None
	try:
		improvement = frappe.get_last_doc(
			"Improvement",
			filters={"deployment_status": "Rebuild Complete"},
			order_by="modified asc",
		)
		improvement_name = improvement.name.lower()
		status = update_helm_release(improvement_name)

		rollout_deployment(f"{get_namespace()}-{improvement_name}-erpnext-erpnext")
		rollout_deployment(f"{get_namespace()}-{improvement_name}-erpnext-scheduler")
		rollout_deployment(f"{get_namespace()}-{improvement_name}-erpnext-socketio")
		rollout_deployment(f"{get_namespace()}-{improvement_name}-erpnext-worker-d")
		rollout_deployment(f"{get_namespace()}-{improvement_name}-erpnext-worker-s")
		rollout_deployment(f"{get_namespace()}-{improvement_name}-erpnext-worker-d")

		if status.get("error"):
			improvement.deployment_status = "Upgrading Failed"
			improvement.save()
			frappe.db.commit()
		elif status.get("status", {}).get("phase") == "Succeeded":
			improvement.deployment_status = "Upgrading"
			improvement.save()
			frappe.db.commit()

	except frappe.DoesNotExistError:
		print("No Improvement is 'Rebuild Complete' state")


def process_upgrading_improvements():
	improvement = None
	try:
		improvement = frappe.get_last_doc(
			"Improvement",
			filters={"deployment_status": "Upgrading"},
			order_by="modified asc",
		)

		status = get_helm_release(improvement.name.lower())

		if status.get("error"):
			improvement.deployment_status = "Upgrading Failed"
			improvement.save()
			frappe.db.commit()
		elif status.get("metadata", {}).get("generation") > 1:
			improvement.deployment_status = "Ready"
			improvement.save()
			frappe.db.commit()

	except frappe.DoesNotExistError:
		print("No Improvement is 'Upgrading' state")


def process_delete_queued_improvements():
	improvement = None
	try:
		improvement = frappe.get_last_doc(
			"Improvement",
			filters={"deployment_status": "Delete Queued"},
			order_by="modified asc",
		)

		status = delete_helm_release(improvement.name.lower())

		if status.get("error"):
			improvement.deployment_status = "Delete Queue Failed"
		elif status.get("status") == "Success":
			improvement.deployment_status = "Release Deleted"
			improvement.site_url = None
			improvement.site_admin_password = None

		improvement.save()
		frappe.db.commit()

	except frappe.DoesNotExistError:
		print("No Improvement is 'Delete Queued' state")


def process_release_deleted_improvements():
	improvement = None
	try:
		improvement = frappe.get_last_doc(
			"Improvement",
			filters={"deployment_status": "Release Deleted"},
			order_by="modified asc",
		)
		improvement_name = improvement.name.lower()
		release_status = get_helm_release(improvement_name)
		job_status = get_job_status(
			f"{get_namespace()}-{improvement_name}-erpnext-drop-site"
		)

		if (
			release_status.get("error")
			and release_status.get("reason") == "Not Found"
			and job_status.get("error")
			and job_status.get("reason") == "Not Found"
		):
			delete_image_tag("erpnext-worker", improvement.name)
			delete_image_tag("erpnext-nginx", improvement.name)
			improvement.deployment_status = None
			improvement.save()
			frappe.db.commit()

	except frappe.DoesNotExistError:
		print("No Improvement is 'Release Deleted' state")


def create_build_job(improvement):
	image_tag = improvement.target_branch

	if "-hotfix" in improvement.target_branch:
		image_tag = improvement.target_branch.rstrip("-hotfix")

	res = create_build_image_job(
		improvement_name=improvement.name,
		image_tag=image_tag,
		git_repo=improvement.fork_url,
		git_branch=improvement.source_branch,
	)

	return res
