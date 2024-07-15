// Copyright (c) 2024, DAS and contributors
// For license information, please see license.txt

frappe.ui.form.on('Sales Invoice', {
	refresh(frm) {
        if(frm.doc.docstatus==1) {			
            frm.add_custom_button(__('Create Ongkir'), function() { 
                frm.trigger('make_data_ongkir');
            }, "fa fa-file-text").addClass("btn-primary");
		}
    },
    make_data_ongkir(frm){
        let fields = [{
			"fieldtype": "Currency",
			"label": __("Total Ongkir"),
			"fieldname": "total_ongkir",
            "reqd": 1
		}];

        let dialog = new frappe.ui.Dialog({
			title: __("Create Data Ongkir"),
			fields: fields,
            primary_action: function() {
                var args = dialog.get_values();
                frappe.call({
                    method: "addons.custom.sales_invoice.make_data_ongkir",
                    args: {
                        "source_name": frm.doc.name,
                        "total_ongkir": args.total_ongkir
                    },
                    freeze: true,
                    callback: function(r) {
                        if(!r.exc) {
                            dialog.hide();
                        }
                    }
                });

            }
		});

        dialog.show();
    }
})