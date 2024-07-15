// Copyright (c) 2024, DAS and contributors
// For license information, please see license.txt

frappe.ui.form.on('Sales Order', {
	total_coin: function(frm){
        frm.set_value("total_coin_amount", frm.doc.total_coin)
    },
})