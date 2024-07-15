# Copyright (c) 2023, DAS and contributors
# For license information, please see license.txt

import frappe

from erpnext.accounts.doctype.pos_closing_entry.pos_closing_entry import make_closing_entry_from_opening

@frappe.whitelist()
def make_pos_closing_entry(dt, dn):
    doc = frappe.get_doc(dt, dn)

    pos_closing = make_closing_entry_from_opening(doc)

    return pos_closing