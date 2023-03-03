from __future__ import print_function, unicode_literals

import json
import frappe
from frappe.utils import cstr, date_diff, file_lock, flt, get_datetime_str, now

@frappe.whitelist()
def create(id_drw, customer, address = None, contact= None):
    # error jika id drw telah ada
    if frappe.db.exists("Customer", {'id_drw' : id_drw}):
        return "ID DRW telah digunakan"

    # insert data customer sesuai field
    doc = frappe.new_doc("Customer")
    customer = customer if isinstance(customer, dict) else json.loads(customer)
    doc.update(customer)
    doc.set('id_drw', id_drw)
    if 'upline' in customer:
        upline = frappe.db.get_value("Customer", { 'id_drw' : customer['upline'] }, 'name')
        doc.set('upline', upline or customer['upline'])

    if 'customer_group' in customer:
        default_price_list = frappe.db.get_value("Customer Group", customer['customer_group'], 'default_price_list')
        doc.set('default_price_list', default_price_list)

    doc.save()

    # insert address jika terdapat param address
    if address:
        doc_addres = frappe.new_doc("Address")
        doc_addres.update(address if isinstance(address, dict) else json.loads(address))
        doc_addres.set('links', [{'link_doctype': 'Customer', 'link_name': doc.name}])

        doc_addres.save()

        doc.set('customer_primary_address', doc_addres.name)

    # insert contact jika terdapat param contact
    if contact:
        doc_contact = frappe.new_doc("Contact")
        doc_contact.first_name = doc.name
        doc_contact.update(contact if isinstance(contact, dict) else json.loads(contact))
        doc_contact.set('links', [{'link_doctype': 'Customer', 'link_name': doc.name}])

        doc_contact.save()

        doc.set('customer_primary_contact', doc_contact.name)

    # jika terdapat param address atau contact tambah field primary pada customer
    if address or contact:
        doc.save()

    return "Customer berhasil di buat"
    

    