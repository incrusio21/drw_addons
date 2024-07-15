// Copyright (c) 2023, DAS and contributors
// For license information, please see license.txt

frappe.ui.form.on('Form Budget', {
	// refresh: function(frm) {

	// }
});

$.each(["januari", "februari", "maret", "april", "mei", "juni", "juli", "agustus", "september", "oktober", "november", "desember"], function(i, value){
	frappe.ui.form.on('Form Budget Detail', value, function(frm, cdt, cdn) { frm.script_manager.trigger("set_budget", cdt, cdn);  })
})

frappe.ui.form.on('Form Budget Detail', {
	set_budget: function(frm, cdt, cdn){
		var item = frappe.get_doc(cdt, cdn);
		console.log('aaa')
		var total_budget = 0
		$.each(["januari", "februari", "maret", "april", "mei", "juni", "juli", "agustus", "september", "oktober", "november", "desember"], function(i, value){
			total_budget += item[value]
		})

		frappe.model.set_value(cdt, cdn, "total_budget", total_budget)
	},
	total_budget: function(frm, cdt, cdn){
		// var item = frappe.get_doc(cdt, cdn);

		var total_budget = 0

		// $.each(["januari", "februari", "maret", "april", "mei", "juni", "juli", "agustus", "september", "oktober", "november", "desember"], function(i, value){
		// 	frappe.model.set_value(cdt, cdn, "_"+value, (item[value]/item.total_budget)*100)
		// })
		
		$.each(frm.doc.details, function(i, value){
			total_budget += value.total_budget
		})
		frm.set_value("total_budget", total_budget)
	}
});