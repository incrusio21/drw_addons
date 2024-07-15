# Copyright (c) 2023, DAS and contributors
# For license information, please see license.txt
import math

import frappe
from frappe.utils import (
	nowdate,
)

from frappe.model.document import Document

from erpnext.accounts.utils import get_fiscal_year

class AgentPointLog(Document):
	def validate(self):
		if self.total_belanja and self.kelipatan:
			self.total_point = math.floor(self.total_belanja / self.kelipatan)

	def after_insert(self):
		self.update_customer()

	def after_delete(self):
		self.update_customer(True)

	def update_customer(self, delete=False):
		customer = frappe.get_doc("Customer", self.customer)
		if not delete:
			customer.total_belanja = self.total_belanja
			customer.benlanja_terakhir = self.posting_date
			customer.total_point = self.total_point

		point_log_fiscal_year = get_fiscal_year(self.posting_date, as_dict=True)
		current_fiscal_year = get_fiscal_year(nowdate(), as_dict=True)
		if point_log_fiscal_year != current_fiscal_year:
			return
		
		remaining_point = frappe.get_all(
			"Agent Point Log",
			filters={
				"customer": self.customer,
				"posting_date": (
					"between",
					[current_fiscal_year.year_start_date, current_fiscal_year.year_end_date],
				),
			},
			group_by="customer",
			fields=[
				"sum(total_point) as total_point",
			],
		)
		
		if remaining_point and remaining_point[0]:
			remaining_point = remaining_point[0].get("total_point")

		customer.remaining_point = remaining_point or 0 
		customer.db_update()