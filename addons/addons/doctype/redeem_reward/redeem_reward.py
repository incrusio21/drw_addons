# Copyright (c) 2024, DAS and contributors
# For license information, please see license.txt

import frappe
from frappe.utils import (
	flt,
)
from frappe.model.document import Document

class RedeemReward(Document):
	
	def validate(self):
		final_point = self.remaining_points - self.required_points
		if final_point < 0: 
			frappe.throw("Point yang dibutuhkan tidak mencukupi")

		self.final_points = final_point
		
	def on_submit(self):
		point = frappe.new_doc("Agent Point Log")
		point.posting_date = self.posting_date
		point.redeem_reward = self.name
		point.customer = self.bc
		point.total_point = flt(-1 * self.required_points, point.precision("total_point"))
		point.save()

	def on_cancel(self):
		point_log = frappe.db.get_list("Agent Point Log", {"redeem_reward": self.name})
		for row in point_log:
			doc = frappe.get_doc("Agent Point Log", row)
			doc.delete()