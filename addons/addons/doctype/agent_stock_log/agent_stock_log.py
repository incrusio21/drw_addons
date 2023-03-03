# Copyright (c) 2023, DAS and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document

class AgentStockLog(Document):
	# pass
	def after_insert(self):
		stock = frappe.db.get_value('Agent Stock Bin', {'item_code': self.item_code, 'customer': self.customer}, 'name')
		if stock:
			bin = frappe.get_doc('Agent Stock Bin', stock)
			bin.qty += self.qty
		else:
			bin = frappe.get_doc({
				'doctype': "Agent Stock Bin",
				'item_code': self.item_code,
				'customer': self.customer,
				'qty': self.qty
			})

		bin.save()

	def on_trash(self):
		stock = frappe.db.get_value('Agent Stock Bin', {'item_code': self.item_code, 'customer': self.customer}, 'name')
		if stock:
			bin = frappe.get_doc('Agent Stock Bin', stock)
			bin.qty -= self.qty
			bin.save()