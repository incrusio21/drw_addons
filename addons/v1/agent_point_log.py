import frappe
from addons.custom.sales_order import make_point_log

@frappe.whitelist()
def add_new(sales_order):
    # memastikan tidak akan membentuk poin log berkali2
    so = frappe.get_doc("Sales Order", sales_order, for_update=1)

    if frappe.db.exists("Agent Point Log", {"sales_order": sales_order}):
        return
    
    make_point_log(so, so.customer)