ARG FRAPPE_BRANCH=develop
FROM node:14-buster

COPY containers/nginx/install_frappe.sh /install_frappe
COPY containers/nginx/prepare_production.sh /prepare_production
COPY  . /home/frappe/frappe-bench/apps/erpnext_feature_board

# Install frappe
RUN /install_frappe && \
  # Install app
  mkdir -p /home/frappe/frappe-bench/sites/assets && \
  cd /home/frappe/frappe-bench/apps/erpnext_feature_board && yarn && \
  cd /home/frappe/frappe-bench/apps/frappe && \
  yarn production --skip_frappe --app erpnext_feature_board && \
  mkdir -p /home/frappe/frappe-bench/sites/assets/erpnext_feature_board && \
  cp -R /home/frappe/frappe-bench/apps/erpnext_feature_board/erpnext_feature_board/public/* /home/frappe/frappe-bench/sites/assets/erpnext_feature_board 2>/dev/null || : && \
  cp -R /home/frappe/frappe-bench/apps/erpnext_feature_board/node_modules /home/frappe/frappe-bench/sites/assets/erpnext_feature_board/ 2>/dev/null || : && \
  echo "rsync -a --delete /var/www/html/assets/erpnext_feature_board /assets" >> /rsync && \
  chmod +x /rsync && \
  # Cleanup for production
  /prepare_production

FROM frappe/frappe-nginx:${FRAPPE_BRANCH}

COPY --from=0 /home/frappe/frappe-bench/sites/ /var/www/html/
COPY --from=0 /rsync /rsync

# Append list of installed to apps.txt
RUN echo -n "erpnext_feature_board" >> /var/www/html/apps.txt

VOLUME [ "/assets" ]

ENTRYPOINT ["/docker-entrypoint.sh"]
CMD ["nginx", "-g", "daemon off;"]
