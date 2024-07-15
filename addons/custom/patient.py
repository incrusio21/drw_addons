# Copyright (c) 2023 DAS
# For license information, please see license.txt

import frappe

def update_customer(self, method):
    if self.customer:
        frappe.db.set_value("Customer", self.customer, "no_rm_patient", self.name)