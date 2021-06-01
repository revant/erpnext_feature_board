import datetime

import frappe
from kubernetes import client, config
from kubernetes.client.rest import ApiException


def get_container_registry():
	return frappe.get_conf().get(
		"container_registry",
		"registry.localhost:5000",
	)


def to_dict(obj):
	if hasattr(obj, "attribute_map"):
		result = {}
		for k, v in getattr(obj, "attribute_map").items():
			val = getattr(obj, k)
			if val is not None:
				result[v] = to_dict(val)
		return result
	elif type(obj) == list:
		return [to_dict(x) for x in obj]
	elif type(obj) == datetime:
		return str(obj)
	else:
		return obj


def load_config():
	if frappe.get_conf().get("developer_mode"):
		config.load_kube_config()
	else:
		config.load_incluster_config()


def get_namespace():
	return frappe.get_conf().get("kubernetes_namespace", "efb")


def create_build_image_job(improvement_name, image_tag, git_repo, git_branch):
	load_config()
	job_name = f"build-{improvement_name}".lower()  # only lowercase email allowed
	batch_v1_api = client.BatchV1Api()
	body = client.V1Job(api_version="batch/v1", kind="Job")
	body.metadata = client.V1ObjectMeta(
		namespace=get_namespace(),
		name=job_name,
	)
	body.status = client.V1JobStatus()
	volume_mounts = None
	volumes = None
	host_aliases = None
	worker_args = [
		"--dockerfile=build/erpnext-worker/Dockerfile",
		"--context=git://github.com/frappe/frappe_docker.git",
		f"--build-arg=GIT_REPO={git_repo}",
		f"--build-arg=IMAGE_TAG={image_tag}",
		f"--build-arg=GIT_BRANCH={git_branch}",
		f"--destination={get_container_registry()}/erpnext-worker:{improvement_name}",
	]
	nginx_args = [
		"--dockerfile=build/erpnext-nginx/Dockerfile",
		"--context=git://github.com/frappe/frappe_docker.git",
		f"--build-arg=GIT_REPO={git_repo}",
		f"--build-arg=IMAGE_TAG={image_tag}",
		f"--build-arg=GIT_BRANCH={git_branch}",
		f"--destination={get_container_registry()}/erpnext-nginx:{improvement_name}",
	]

	if frappe.get_conf().get("developer_mode"):
		worker_args.append("--insecure")
		nginx_args.append("--insecure")
		host_aliases = [
			client.V1HostAlias(
				ip=frappe.get_conf().get("docker_host_ip", "172.17.0.1"),
				hostnames=["registry.localhost"],
			)
		]

	if not frappe.get_conf().get("developer_mode"):
		volume_mounts = [
			client.V1VolumeMount(
				mount_path="/kaniko/.docker",
				name="container-config",
			)
		]
		volumes = [
			client.V1Volume(
				name="container-config",
				projected=client.V1ProjectedVolumeSource(
					sources=[
						client.V1VolumeProjection(
							secret=client.V1SecretProjection(
								name=frappe.get_conf().get(
									"container_push_secret", "regcred"
								),
								items=[
									client.V1KeyToPath(
										key=".dockerconfigjson",
										path="config.json",
									)
								],
							)
						)
					]
				),
			)
		]

	body.spec = client.V1JobSpec(
		template=client.V1PodTemplateSpec(
			spec=client.V1PodSpec(
				security_context=client.V1PodSecurityContext(
					supplemental_groups=[1000]
				),
				containers=[
					client.V1Container(
						name="build-worker",
						image="gcr.io/kaniko-project/executor:latest",
						args=worker_args,
						volume_mounts=volume_mounts,
					),
					client.V1Container(
						name="build-nginx",
						image="gcr.io/kaniko-project/executor:latest",
						args=nginx_args,
						volume_mounts=volume_mounts,
					),
				],
				restart_policy="Never",
				volumes=volumes,
				host_aliases=host_aliases,
			)
		)
	)

	try:
		api_response = batch_v1_api.create_namespaced_job(
			get_namespace(), body, pretty=True
		)
		return to_dict(api_response)
	except (ApiException, Exception) as e:
		print(e)
		out = {
			"error": e,
			"params": {
				"improvement_name": improvement_name,
				"image_tag": image_tag,
				"git_repo": git_repo,
				"git_branch": git_branch,
			},
		}
		reason = getattr(e, "reason")
		if reason:
			out["reason"] = reason

		frappe.log_error(out, "Exception: BatchV1Api->create_namespaced_job")
		return out


def get_job_status(job_name):
	load_config()
	batch_v1 = client.BatchV1Api()

	try:
		job = batch_v1.read_namespaced_job(name=job_name, namespace=get_namespace())
		return to_dict(job)
	except (ApiException, Exception) as e:
		out = {
			"error": e,
			"params": {"job_name": job_name},
		}
		reason = getattr(e, "reason")
		if reason:
			out["reason"] = reason

		frappe.log_error(out, "Exception: BatchV1Api->read_namespaced_job")
		return out


def create_helm_release(improvement_name):
	improvement = frappe.get_doc("Improvement", improvement_name)
	site_password = frappe.generate_hash(length=10)

	# Save site password
	# improvement.site_password = site_password
	# improvement.save()
	# frappe.db.commit()

	db_root_user = frappe.get_conf().get("db_root_user", "root")
	db_root_password = frappe.get_conf().get("db_root_password", "admin")
	mariadb_host = frappe.get_conf().get(
		"mariadb_host", "mariadb.mariadb.svc.cluster.local"
	)
	install_apps = frappe.get_conf().get("install_apps", "erpnext")
	domain_name = frappe.get_conf().get("domain_name", "test-erpnext.org")
	site_name = improvement_name.lower() + "." + domain_name
	load_config()
	crd = client.CustomObjectsApi()
	body = {
		"kind": "HelmRelease",
		"apiVersion": "helm.fluxcd.io/v1",
		"metadata": client.V1ObjectMeta(
			namespace=get_namespace(),
			name=improvement_name.lower(),
		),
		"spec": {
			"chart": {
				"repository": "https://helm.erpnext.com",
				"name": "erpnext",
				# Use >=3.2.3
				"version": "3.2.3",
			},
			"values": {
				"nginxImage": {
					"repository": f"{get_container_registry()}/erpnext-nginx",
					"tag": improvement_name,
					"pullPolicy": "Always",
				},
				"pythonImage": {
					"repository": f"{get_container_registry()}/erpnext-worker",
					"tag": improvement_name,
					"pullPolicy": "Always",
				},
				"mariadbHost": mariadb_host,
				"dbRootPassword": db_root_password,
				"redisQueueHost": "redis-master.redis.svc.cluster.local:6379/0",
				"redisCacheHost": "redis-master.redis.svc.cluster.local:6379/1",
				"redisSocketIOHost": "redis-master.redis.svc.cluster.local:6379/2",
				"persistence": {
					"logs": {"storageClass": "nfs"},
					"worker": {"storageClass": "nfs"},
				},
				"createSite": {
					"enabled": True,
					"siteName": site_name,
					"dbRootPassword": db_root_password,
					"dbRootUser": db_root_user,
					"adminPassword": site_password,
					"installApps": install_apps,
					"dropSiteOnUninstall": True,
				},
				"ingress": {
					"enabled": True,
					"hosts": [
						{
							"host": site_name,
							"paths": [
								{
									"path": "/",
									"pathType": "ImplementationSpecific",
								}
							],
						},
					],
				},
			},
		},
	}
	try:
		res = crd.create_namespaced_custom_object(
			"helm.fluxcd.io", "v1", get_namespace(), "helmreleases", body, pretty=True
		)
		return to_dict(res)
	except (ApiException, Exception) as e:
		out = {
			"error": e,
			"params": {"improvement_name": improvement_name},
		}
		reason = getattr(e, "reason")
		if reason:
			out["reason"] = reason

		frappe.log_error(out, "Exception: BatchV1Api->read_namespaced_job")
		return out


def update_helm_release(improvement_name):
	improvement = frappe.get_doc("Improvement", improvement_name)

	load_config()
	crd = client.CustomObjectsApi()
	try:
		res = crd.patch_namespaced_custom_object(
			"helm.fluxcd.io",
			"v1",
			get_namespace(),
			"helmreleases",
			improvement_name.lower(),
			body,
			pretty=True,
		)
		return to_dict(res)
	except (ApiException, Exception) as e:
		out = {
			"error": e,
			"params": {"improvement_name": improvement_name},
		}
		reason = getattr(e, "reason")
		if reason:
			out["reason"] = reason

		frappe.log_error(out, "Exception: BatchV1Api->read_namespaced_job")
		return out


def delete_helm_release(improvement_name):
	load_config()
	crd = client.CustomObjectsApi()
	try:
		res = crd.delete_namespaced_custom_object(
			"helm.fluxcd.io",
			"v1",
			get_namespace(),
			"helmreleases",
			improvement_name,
		)
		return to_dict(res)
	except (ApiException, Exception) as e:
		out = {
			"error": e,
			"params": {"improvement_name": improvement_name},
		}
		reason = getattr(e, "reason", None)
		if reason:
			out["reason"] = reason

		frappe.log_error(
			out, "Exception: CustomObjectsApi->delete_namespaced_custom_object"
		)
		return out


def tear_down_improvement_site_resources(improvement_name):
	# TODO: delete images
	# TODO: delete Build jobs
	pass
