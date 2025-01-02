# Copyright (c) 2023, DAS and contributors
# For license information, please see license.txt

import frappe
import math
from frappe.model.document import Document

class AgentCoinLog(Document):
	def validate(self):
		if self.total_margin and self.kelipatan:
			self.total_coin = math.floor(self.total_margin / self.kelipatan)

	def on_update(self):
		self.update_customer_coin()
		
	def after_delete(self):
		self.update_customer_coin()

	def update_customer_coin(self):
		# update coins customer
		fields = "total_coin_cashback" if self.is_cashback else "total_coins"
		frappe.db.sql(
			"""
			update `tabCustomer`
			set 
				{0} = (select ifnull(sum(total_coin), 0) from `tabAgent Coin Log` where `customer`= %(customer)s and is_cashback = %(is_cashback)s)
			where name= %(customer)s
			""".format(fields)
			, { "customer": self.customer, "is_cashback": self.is_cashback }
		)