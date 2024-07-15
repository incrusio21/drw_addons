from __future__ import print_function, unicode_literals

import json
import frappe
from frappe import _, _dict
from frappe.utils import nowdate

@frappe.whitelist()
def create(id_drw_order, data):
    # error jika id drw tidak ada pada sales invoice
    if not frappe.db.exists("Sales Order", {'id_drw_order' : id_drw_order }):
        frappe.throw("ID {0} tidak ditemukan pada Sales Order".format(id_drw_order))
    
    # daftar data diluar id drw order
    body = data if isinstance(data, dict) else json.loads(data if data else "{}")

    if 'items' not in body or len(body['items']) == 0:
        frappe.throw("Harus tedapat minimal satu items untuk membuat Delivery Note")

    # buat dn dari so
    from erpnext.selling.doctype.sales_order.sales_order import make_delivery_note
    order = frappe.db.get_value("Sales Order", {'id_drw_order' : id_drw_order}, 'name')
    dn = make_delivery_note(order)
    dn.posting_date = body.get('tanggal') or nowdate()
    dn.set_posting_time = 1

    # fetch existing items in bulk
    id_items = [row['id_item'] for row in body['items']]
    existing_items = frappe.db.get_all(
        "Item",
        filters={'id_item_drw': ('in', id_items)},
        fields=['name', 'id_item_drw']
    )

    # convert id_item_drw ke item_code terus buat dict dari item_code:qty (ex. {ItemCode1:1, ItemCode2:3})
    dict_item_code = {item.name: row['qty'] for row in body['items'] for item in existing_items if item.id_item_drw == row['id_item']}
    if not dict_item_code:
        frappe.throw("Tidak ada item yang cocok ditemukan")
    
    # cek dn item yg sesuai inputan api, jika ada rubah qty sesuai inputan, jika tidak ada hapus item_code yang sudah ada di dn.item
    dn_items = []
    dn.items = [row for row in dn.items if row.item_code in dict_item_code]
    for row in dn.items:
        if dict_item_code[row.item_code] < 0 or dict_item_code[row.item_code] > row.qty:
            frappe.throw("Qty untuk '{0}' tidak boleh negative atau lebih besar dari Sales Order".format(row.item_code))
        row.qty = dict_item_code[row.item_code]
        row.warehouse = body.get('warehouse') or row.warehouse
        dn_items.append(row)

    dn.items = dn_items
    
    # hapus smua actual taxes and charges jika sudah pernah ada dn
    if frappe.db.exists("Delivery Note Item", {"against_sales_order" : order, "docstatus" : 1}):
        for row in dn.get("taxes", { "charge_type": "Actual" }):
            dn.remove(row)

    # ubah nilai diskon sesuai dgn total barang kirim
    if dn.additional_discount_percentage == 0 and dn.discount_amount != 0:
        total_before_disc = frappe.db.get_value("Sales Order", {'id_drw_order' : id_drw_order}, 'total')
        new_disc_amount = 0
        
        for row in dn.items:
            distributed_amount = dn.discount_amount * row.amount / total_before_disc
            new_disc_amount += distributed_amount
        
        # memastikan
        dn.discount_amount = new_disc_amount

    dn.submit()

    return "Delivery Note berhasil dibuat"