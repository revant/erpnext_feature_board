// Copyright (c) 2021, ERPNext Community and contributors
// For license information, please see license.txt

frappe.ui.form.on('Github Repository', {
	refresh: function (frm) {
		if (!frm.is_new() && frm.doc.repository_url) {
			frm.add_custom_button(__("Sync Open Pull Requests"), () => {
				frm.call({
					doc: frm.doc,
					method: "sync_pull_requests",
					freeze: true,
					callback: (r) => {
						if (!r.exc) {
							frappe.msgprint(__("Improvement records created from all open Pull Requests"))
						}
					}
				});
			});
		}
	}
});
