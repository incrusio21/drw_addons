# Copyright (c) 2023, DAS and contributors
# For license information, please see license.txt

import frappe
import math
from frappe.model.document import Document

class AgentPointLog(Document):
	def validate(self):
		self.total_point = math.floor(self.total_belanja / self.kelipatan)

	def after_insert(self):
		customer = frappe.get_doc("Customer", self.customer)
		customer.total_belanja = self.total_belanja
		customer.benlanja_terakhir = self.posting_date
		customer.total_point = self.total_point

		customer.db_update()