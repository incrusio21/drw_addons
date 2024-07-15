# Copyright (c) 2023, DAS and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document

class AgentStockBin(Document):
	pass

def on_doctype_update():
	frappe.db.add_unique("Agent Stock Bin", ["item_code", "customer"], constraint_name="unique_item_customer")