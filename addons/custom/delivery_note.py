from __future__ import unicode_literals
import frappe
from frappe import _

@frappe.whitelist()
def create_agent_stock_log(self, method):
    from addons.custom.custom_method import is_director

    if is_director(self.customer):
        for row in self.items:
            # ADD AGENT STOCK LOG
            doc = frappe.get_doc({
				'doctype': "Agent Stock Log",
				'customer': self.customer,
				'item_code': row.item_code,
				'qty': row.qty,
                'id_delivery_note': self.name
			})

            doc.insert()

def delete_log(self, method):
    log_list = frappe.db.get_list('Agent Stock Log', pluck='name', filters={'id_delivery_note': self.name })
    for log in log_list:
        frappe.delete_doc("Agent Stock Log", log)                                                                                                                                                                                                                                                                                                                                                                                                                                                                   