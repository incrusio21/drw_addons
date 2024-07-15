# Copyright (c) 2023, DAS and contributors
# For license information, please see license.txt

import frappe

def validate(self, method):
    
    for item in self.get("costings"):
        item.total_amount = item.sponsored_amount + item.funded_amount     

@frappe.whitelist()
def create_employee_advance(source_name, target_doc=None, ignore_permissions=False):
    doc = frappe.get_doc("Travel Request", source_name)
    
    employee_advance = frappe.new_doc("Employee Advance")
    employee_advance.employee = doc.employee

    employee_advance.purpose = doc.purpose_of_travel
    employee_advance.travel_request = doc.name

    employee_advance.advance_amount = sum([d.sponsored_amount + d.funded_amount for d in doc.costings])
    employee_advance.advance_account = frappe.get_cached_value("Company", employee_advance.company, "default_employee_advance_account") 

    return employee_advance