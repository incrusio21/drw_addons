# Copyright (c) 2023, DAS and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document

class ClinicManager(Document):
	pass

@frappe.whitelist()
def validate_clinic_manager(username, password):
	clinic_manager = frappe.db.get_value("Clinic Manager", username, ['name', 'user'], as_dict=1)
	if not clinic_manager:
		frappe.throw("Clinic Manager tidak ditemukan")
		
	from addons.custom.custom_method import check_password
	check_password(password, clinic_manager.user)