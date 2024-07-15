// Copyright (c) 2023, DAS and contributors
// For license information, please see license.txt

frappe.ui.form.on('Travel Request', {
	refresh: function(frm) {
		if(frm.doc.docstatus == 1){
			frm.add_custom_button(__("Create Employee Advance"), function() {
				return frappe.call({
					method: "addons.custom.travel_request.create_employee_advance",
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

frappe.ui.form.on('Travel Request Costing', {
    update_total_amount: function(frm, cdt, cdn){
        var item = frappe.get_doc(cdt, cdn);
        frappe.model.set_value(cdt, cdn, "total_amount", item.sponsored_amount + item.funded_amount)
    },
	sponsored_amount: function(frm, cdt, cdn){
        frm.script_manager.trigger("update_total_amount", cdt, cdn);
    },
    funded_amount: function(frm, cdt, cdn){
        frm.script_manager.trigger("update_total_amount", cdt, cdn);
    }
});
