
frappe.ui.form.on("POS Opening Entry", {
    refresh: function(frm){
        if(frm.doc.status == "Open" && frm.doc.docstatus == 1){
            frm.add_custom_button(__('Make POS Closing Entry'),
                function() {
                    cur_frm.cscript.make_pos_closing_entry()
                }
            );
        }
    }
})

cur_frm.cscript['make_pos_closing_entry'] = function() {
    frappe.call({
        method: "addons.custom.pos_opening_entry.make_pos_closing_entry",
        args: {
            dt: this.frm.doc.doctype,
            dn: this.frm.doc.name,
        },
        callback: function (r) {
            var doc = frappe.model.sync(r.message);
            frappe.set_route("Form", doc[0].doctype, doc[0].name);
        },
    })
}