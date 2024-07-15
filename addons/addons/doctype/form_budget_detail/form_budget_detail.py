# Copyright (c) 2023, DAS and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document

class FormBudgetDetail(Document):
	pass

def on_doctype_update():
	frappe.db.add_unique("Form Budget Detail", ["account", "parent"], constraint_name="unique_account_parent")