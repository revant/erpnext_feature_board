import json
import os

import dxf
import frappe
from erpnext_feature_board.clients.k8s import get_container_registry


def get_registry_client(repo=None):
	auth = get_container_registry_auth()
	is_dev_mode = True if frappe.get_conf().get("developer_mode") else False

	dxf_client = dxf.DXF(
		get_container_registry(),
		auth=auth,
		repo=repo,
		insecure=is_dev_mode,
		tlsverify=not is_dev_mode,
	)
	dxf_client.authenticate(authorization=auth, actions=["*"])

	return dxf_client


def get_container_registry_auth():
	config = {}
	home = os.environ.get("HOME", "/home/frappe")
	docker_config = os.path.join(home, ".docker", "config.json")

	with open(docker_config, encoding="utf-8") as f:
		config = json.load(f)

	return "Basic " + (
		config.get("auths", {})
		.get(get_container_registry(), {})
		.get("auth", "YWRtaW46cGFzc3dvcmQ=")
	)


def delete_image_tag(image_name, tag_name):
	try:
		dxf_client = get_registry_client(image_name)
		res = dxf_client.del_alias(tag_name)
		return res
	except Exception as e:
		out = {
			"error": e,
			"params": {"image_name": image_name, "tag_name": tag_name},
		}

		frappe.log_error(out, "delete_image_tag")
		return out
