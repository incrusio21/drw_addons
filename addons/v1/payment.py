from __future__ import print_function, unicode_literals

import json
import frappe
from frappe.utils import flt

@frappe.whitelist()
def create(id_drw_order, paid_amount, account_bank = None, posting_date = None):
    # error jika id drw tidak ada pada sales invoice
    if not frappe.db.exists("Sales Invoice", {'id_drw_order' : id_drw_order}):
        frappe.throw("ID '{}' tidak ditemukan pada Sales Invoice".format(id_drw_order))
    
    bank = frappe.db.get_value("Account", {'id_account_drw' : account_bank }, 'name')
    if account_bank and not bank:
        frappe.throw("Acount dengan ID Bank '{}' tidak ditemukan. Mohon update data Account terlebih dahulu".format(account_bank))

    # buat sinv dari so
    from addons.custom.payment_entry import get_payment_entry
    invoice = frappe.db.get_value("Sales Invoice", {'id_drw_order' : id_drw_order}, ['name', 'outstanding_amount'], as_dict=1)
    # if flt(paid_amount) > invoice.outstanding_amount:
    #     frappe.throw("Jumlah pembayaran melebihi sisa piutang pada Sales Invoice")

    payment = get_payment_entry("Sales Invoice", invoice.name, paid_amount, bank, posting_date=posting_date)

    payment.reference_no = id_drw_order
    payment.reference_date = payment.posting_date
    payment.submit()

    return 'Payment Berhasi dibuat'