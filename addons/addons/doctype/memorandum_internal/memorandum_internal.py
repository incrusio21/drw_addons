# Copyright (c) 2023, DAS and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document

class MemorandumInternal(Document):
	pass

@frappe.whitelist()
def create_journal_entry(source_name, target_doc=None, ignore_permissions=False):

	doc = frappe.new_doc("Journal Entry")

	return doc