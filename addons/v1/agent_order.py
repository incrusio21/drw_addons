from __future__ import print_function, unicode_literals

import json
import frappe
from frappe.utils import (
	nowdate,
)
from erpnext import get_default_company

@frappe.whitelist()
def create(id_drw, items, data = ""):
    # error jika id drw tidak di temukan
    customer = frappe.db.get_value("Customer", {'id_drw' : id_drw}, 'name')
    if not customer:
        frappe.throw("ID DRW '{}' tidak ditemukan. Mohon update data Customer terlebih dahulu".format(id_drw)) 

    # daftar data diluar item
    body = data if isinstance(data, dict) else json.loads(data if data else "{}")
    
    doc = frappe.new_doc("Agent Order")
    doc.set('customer', customer)
    doc.tanggal = body['tanggal'] if 'tanggal' in body.keys() else nowdate()
    doc.id_drw_order = body['id_drw_order'] if 'id_drw_order' in body.keys() else ''
    doc.company = body['company'] if 'company' in body.keys() else get_default_company()
    doc.dc = body['dc'] if 'dc' in body.keys() else ''

    #daftar data yang memiliki hbungan dengan item 
    list =  items if isinstance(items, dict) else json.loads(items)

    doc.biaya_ongkir = list['biaya_ongkir'] if 'biaya_ongkir' in list.keys() else 0.0
    doc.ekspedisi = list['ekspedisi'] if 'ekspedisi' in list.keys() else ''
    doc.biaya_penanganan = list['biaya_penanganan'] if 'biaya_penanganan' in list.keys() else 0.0

    if 'paket' in list.keys():
        paket = []
        for row in list['paket']:
            master_paket = frappe.db.get_value("Master Paket", {'id_drw': row['id']}, ['id_paket', 'harga'], as_dict=1)
            paket.append({
                'id_paket': master_paket.id_paket,
                'qty': row['qty']
            })

        doc.set('daftar_paket', paket)

    doc.set('daftar_promo', list['promo'] if 'promo' in list.keys() else [])

    if 'item' in list.keys():
        item = []
        for index, row in enumerate(list['item']):
            if 'id_item' not in row.keys():
                frappe.throw("ID Item pada Row {} tidak ditemukan".format(index+1))

            item_name = frappe.db.get_value("Item", { 'id_item_drw': row['id_item']}, 'name')
            if not item_name:
                frappe.throw("Item dengan ID Item '{}' tidak ditemukan. Mohon update data Item terlebih dahulu".format(row['id_item']))

            item.append({
                'kode_item': item_name,
                'qty': row['qty'],
                'price_list': row['price_list'],
                'discount': row['discount'] if 'discount' in row.keys() else 0.0,
                'catatan': row['catatan'] if 'catatan' in row.keys() else None
            })

        doc.set('items', item)

    doc.status = "To Deliver and Bill"
    try:
        doc.submit()
    except Exception as e:
        frappe.error_log("Error Create SO from Agent Order", e)

    return 'Agent Order berhasil dibuat'