# Copyright (c) 2024, DAS and contributors
# For license information, please see license.txt

import frappe
from frappe import _, throw
from frappe.model.document import Document

class PrintPengiriman(Document):
	
	@frappe.whitelist()
	def get_delivery_note(self):
		if not self.user_admin:
			throw("Pilih User Admin terlebih dahulu") 

		if not self.date:
			throw("Pilih Tanggal terlebih dahulu")

		dn_list = frappe.get_list("Delivery Note", filters={"owner": self.user_admin, "company": self.company, "posting_date": self.date, "docstatus": 0}, fields=["name as id_delivery_note", "posting_date as delivery_date"])

		self.detail = []
		self.extend("detail", dn_list)