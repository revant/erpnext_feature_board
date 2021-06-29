// Copyright (c) 2021, ERPNext Community and contributors
// For license information, please see license.txt

frappe.ui.form.on('Review Request', {
	refresh: function(frm) {
		if (frm.doc.test_user_password) {
			frm.add_custom_button(
				__('Reveal Password'), () => frm.trigger('reveal_password'),
			);
		}
		if (frm.doc.request_type === 'Add Testing User' && frm.doc.request_status === 'Open') {
			frm.add_custom_button(
				__('Add Testing User'), () => frm.trigger('add_testing_user'),
			);
		}
	},

	reveal_password: (frm) => {
		frm.call({
			method: 'erpnext_feature_board.erpnext_feature_board.doctype.review_request.review_request.get_test_user_password',
			args: { review_request: frm.doc.name },
			callback: r => {
				if (r.message) {
					frappe.msgprint({
						title: __('Test User Password'),
						message: r.message,
					});
				}
			}
		});
	},

	add_testing_user: (frm) => {
		frm.call({
			method: 'erpnext_feature_board.erpnext_feature_board.doctype.review_request.review_request.create_test_user_for_improvement',
			args: {
				improvement_name: frm.doc.improvement,
				review_request_uuid: frm.doc.name,
			},
			callback: r => {
				if (r.message) {
					frm.refresh();
				}
			},
		});
	}
});
