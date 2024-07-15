# Copyright (c) 2023, DAS and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe.utils import cstr, flt, now, nowdate, nowtime

from addons.custom.item import get_bin

class AgentStockLog(Document):
	# pass
	def after_insert(self):
		self.update_bin()
		
	def after_delete(self):
		self.update_bin()

	def update_bin(self):
		bin = get_bin(self.item_code, self.customer)

		actulal_stock = frappe.db.sql("""
			SELECT 
				SUM(qty)
			FROM `tabAgent Stock Log` 
			WHERE 
				item_code= %s AND customer= %s
		""",
			(self.item_code, self.customer)
		)

		actulal_stock = flt(actulal_stock[0][0]) if actulal_stock else 0

		if bin.qty != actulal_stock:
			bin.qty = actulal_stock

			bin.modified = now()
			bin.db_update()