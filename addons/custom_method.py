from __future__ import unicode_literals
import frappe
from frappe import _
from frappe.utils import getdate

def day_of_week(_date):
    weekdays = ["Senin","Selasa","Rabu","Kamis","Jumat","Sabtu","Minggu"]
    return weekdays[getdate(_date).weekday()]

def clear_customer():
    def get_customer(name):
        upline = frappe.db.get_list("Customer", pluck='name',  filters={ 'upline': name })
        for row in upline:
            get_customer(row)

        if frappe.db.exists("Customer", name):
            doc = frappe.get_doc("Customer", name)
            print(name)
            doc.delete()
            print('----------------')
            # frappe.db.commit()

    customer = frappe.db.get_list("Customer", pluck='name')
    for row in customer:
        print('----------------')
        get_customer(row)

def clear_so():
    parent = frappe.db.sql_list(""" select distinct(parent) from `tabSales Order Item` where item_code = "Item Cut Off" order by parent desc """)
    print(str(len(parent)))
    for row in parent:
        print(row)

        if frappe.db.exists("Sales Invoice Item", { 'sales_order' : row}):
            print('----------------')
            parent_sinv = frappe.db.sql_list(""" select distinct(parent) from `tabSales Invoice Item` where sales_order = '{}' order by parent desc """.format(row))
            for sinv_row in parent_sinv:
                doc_sinv = frappe.get_doc("Sales Invoice", sinv_row)
                print(sinv_row)
                doc_sinv.cancel()
                doc_sinv.delete()
            print('----------------')

        doc = frappe.get_doc("Sales Order", row)
        doc.cancel()
        doc.delete()
        # frappe.db.commit()

def clear_stock():
    list_doctype = ["Purchase Receipt"]
    for doctype in list_doctype:
        list_docs = frappe.db.sql("SELECT name,docstatus FROM `tab{}` order by posting_date desc".format(doctype),as_dict=1)
        for d in list_docs:
            # doc = frappe.get_doc(doctype, d.name)
            try:
                # doc.cancel()
                frappe.delete_doc(doctype, d.name,force=1)
                print(d.name)   
                frappe.db.commit()
            except Exception as e:
                print(e)

def update_so_status():
    sales_order = frappe.db.get_all("Sales Order", filters={
        'docstatus': 1,
        'status': "Draft"
    })

    for row in sales_order:
        print(row.name)
        doc = frappe.get_doc("Sales Order", row.name)
        doc.status = "To Deliver and Bill"
        doc.db_update()
        frappe.db.commit()


