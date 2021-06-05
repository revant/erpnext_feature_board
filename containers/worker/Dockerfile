ARG FRAPPE_BRANCH=develop
FROM frappe/frappe-worker:${FRAPPE_BRANCH}

USER root

COPY . /home/frappe/frappe-bench/apps/erpnext_feature_board

RUN /home/frappe/frappe-bench/env/bin/pip install -e /home/frappe/frappe-bench/apps/erpnext_feature_board

USER frappe
