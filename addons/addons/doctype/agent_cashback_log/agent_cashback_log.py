# Copyright (c) 2024, DAS and contributors
# For license information, please see license.txt
import math

import frappe
from frappe.model.document import Document

class AgentCashbackLog(Document):
	def validate(self):
		if self.get("total_coin"):
			self.total_amount = math.floor(self.total_coin * self.kelipatan)
		elif self.get("total_amount"):
			self.total_coin = math.floor(self.total_amount / self.kelipatan)

	def on_update(self):
		self.update_customer_coin()
		
	def after_delete(self):
		self.update_customer_coin()

	def update_customer_coin(self):
		# update coins customer
		frappe.db.sql(
			"""
			update `tabCustomer`
			set 
				total_coin_cashback = (select ifnull(sum(total_coin), 0) 
				from `tabAgent Cashback Log` where `customer`= %(customer)s)
			where name= %(customer)s
			"""
			, { "customer": self.customer }
		)