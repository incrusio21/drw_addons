# Copyright (c) 2023, DAS and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document

class AssetQRCode(Document):
	
	def validate(self):
		self.validate_repeating_asset()

	def validate_repeating_asset(self):
		"""Error when Same Asset is entered multiple times in reference"""
		asset_list = []
		for entry in self.reference:
			asset_list.append(entry.asset)

		if len(asset_list) != len(set(asset_list)):
			frappe.throw(_("Same Asset is entered more than once"))
