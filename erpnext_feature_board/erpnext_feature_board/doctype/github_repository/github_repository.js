// Copyright (c) 2021, ERPNext Community and contributors
// For license information, please see license.txt

frappe.ui.form.on('Github Repository', {
	refresh: function (frm) {
		frm.set_intro(__(`A Github <a href="https://github.com/settings/tokens">Personal Access Token</a>
			is required for private repositories. For public repositories, setting a token will help avoid
			API rate limits. For more info on Github's rate limits, refer to their
			<a href="https://docs.github.com/en/rest/overview/resources-in-the-rest-api#rate-limiting">documentation</a>.`));

		if (!frm.is_new() && frm.doc.repository_url) {
			frm.add_custom_button(__("Sync Open Pull Requests"), () => {
				frm.call({
					doc: frm.doc,
					method: "sync_pull_requests",
					freeze: true,
					callback: (r) => {
						if (!r.exc) {
							frappe.msgprint(__(`Pull requests are being fetched and
								will be created as Improvement records`))
						}
					}
				});
			}).addClass("btn-primary");
		}
	}
});
