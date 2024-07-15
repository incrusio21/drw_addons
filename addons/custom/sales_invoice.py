# Copyright (c) 2023, Frappe Technologies Pvt. Ltd. and Contributors
# License: GNU General Public License v3. See license.txt

import json

import frappe
from frappe.model.mapper import get_mapped_doc
from frappe.utils import (
	flt,
)

@frappe.whitelist()
def make_data_ongkir(source_name, total_ongkir):
    ongkir = frappe.db.sql(" SELECT name FROM `tabData Ongkir` WHERE sinv = %s ", (source_name), as_dict=1)
    if len(ongkir):
        data_ongkir = frappe.get_doc("Data Ongkir", ongkir[0].name)
    else:
        sinv = frappe.get_doc("Sales Invoice", source_name)

        data_ongkir = frappe.new_doc("Data Ongkir")
        data_ongkir.sinv = sinv.name
        data_ongkir.cust = sinv.customer

    data_ongkir.ongkir = total_ongkir

    data_ongkir.save()

@frappe.whitelist()
def make_delivery_note(source_name, target_doc=None):
    def set_missing_values(source, target):
        target.run_method("set_missing_values")
        target.run_method("set_po_nos")
        target.run_method("calculate_taxes_and_totals")

        check_so_si = target.get("items", {"against_sales_order": True})
        if not check_so_si:
            return
        
        target.dropshipper = frappe.db.get_value("Sales Order", check_so_si[0].against_sales_order, "dropshipper")

    def update_item(source_doc, target_doc, source_parent):
        target_doc.qty = flt(source_doc.qty) - flt(source_doc.delivered_qty)
        target_doc.stock_qty = target_doc.qty * flt(source_doc.conversion_factor)

        target_doc.base_amount = target_doc.qty * flt(source_doc.base_rate)
        target_doc.amount = target_doc.qty * flt(source_doc.rate)

    doclist = get_mapped_doc(
        "Sales Invoice",
        source_name,
        {
            "Sales Invoice": {"doctype": "Delivery Note", "validation": {"docstatus": ["=", 1]}},
            "Sales Invoice Item": {
                "doctype": "Delivery Note Item",
                "field_map": {
                    "name": "si_detail",
                    "parent": "against_sales_invoice",
                    "serial_no": "serial_no",
                    "sales_order": "against_sales_order",
                    "so_detail": "so_detail",
                    "cost_center": "cost_center",
                },
                "postprocess": update_item,
                "condition": lambda doc: doc.delivered_by_supplier != 1,
            },
            "Sales Taxes and Charges": {"doctype": "Sales Taxes and Charges", "add_if_empty": True},
            "Sales Team": {
                "doctype": "Sales Team",
                "field_map": {"incentives": "incentives"},
                "add_if_empty": True,
            },
        },
        target_doc,
        set_missing_values,
    )

    doclist.set_onload("ignore_price_list", True)

    return doclist