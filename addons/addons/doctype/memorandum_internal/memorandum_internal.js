// Copyright (c) 2023, DAS and contributors
// For license information, please see license.txt

frappe.ui.form.on('Memorandum Internal', {
	refresh: function(frm) {
		if(frm.doc.docstatus == 1){
			frm.add_custom_button(__("Journal Entry"), function() {
				return frappe.call({
					method: "addons.addons.doctype.memorandum_internal.memorandum_internal.create_journal_entry",
					args: {"source_name": frm.doc.name},
					callback: function(r) {
						var doclist = frappe.model.sync(r.message);
						frappe.set_route("Form", doclist[0].doctype, doclist[0].name);
					}
				});
			});
		}
	}
});
