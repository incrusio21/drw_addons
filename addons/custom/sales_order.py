# Copyright (c) 2023, DAS and contributors
# For license information, please see license.txt

import frappe
from frappe import _dict
from frappe.utils import cint, flt

def validate_coin(self, method):
    if self.total_coin:
        self.total_coin_amount = self.total_coin * 1000

    if self.docstatus == 1 and self.total_coin_amount:
        self.discount_amount += self.total_coin_amount

def make_invoice(self, method):
    d_company = frappe.db.get_value("Company", self.company, ['default_biaya_ongkir', 'default_biaya_penanganan', "default_warehouse", "cost_center"], as_dict=1)

    # buat sinv dari so
    from erpnext.selling.doctype.sales_order.sales_order import make_sales_invoice

    sinv = make_sales_invoice(self.name)
    sinv.posting_date = self.transaction_date
    sinv.set_posting_time = 1
    sinv.due_date = frappe.utils.add_days(self.transaction_date, 2)

    for item in sinv.items:
        item.cost_center = d_company.cost_center
    
    sinv.save()

    self.flags.invoice_list = [sinv]

def remove_invoice(self, method):
    sinv_list = frappe.db.get_list("Sales Invoice Item", filters={"sales_order": self.name}, pluck="name", group_by="parent")
    for row in sinv_list:
        sinv = frappe.get_doc("Sales Invoice", row)
        if sinv.docstatus == 1:
            try:
                sinv.cancel()
            except Exception as e:
                return e
            
        sinv.delete()

def agent_point_log(self, method):
    if method == "on_submit":
        # cek apakah customer group memiliki nilai pada field kelipatan untuk membuat point log
        kelipatan = frappe.db.get_value("Customer Group", self.agent_group, 'kelipatan_transaksi_untuk_dapat_point')
        if kelipatan > 0:
            point = frappe.new_doc("Agent Point Log")
            point.posting_date = self.transaction_date
            point.customer = self.customer
            point.sales_order = self.name
            point.kelipatan = kelipatan
            point.total_belanja = self.rounded_total or self.grand_total
            point.save()

    elif method == "on_cancel":
        log_list = frappe.db.get_list('Agent Point Log', pluck='name', filters={'sales_order': self.name })
        for log in log_list:
            frappe.delete_doc("Agent Point Log", log)

def agent_coin_log(self, method):
    if method == "on_submit":
        # # used coin
        # if self.total_coin:
        #     # validasi jumlah coin customer harus lebih besar dari penggunaanny
        #     customer_coin = frappe.db.get_value("Customer", self.customer, "total_coin_cashback" if self.coin_type == "Cashback" else "total_coins", for_update=True)
        #     if customer_coin < self.total_coin:
        #         frappe.throw("Customer Hanya Memiliki {} Coin".format(customer_coin))

        #     point = frappe.new_doc("Agent Coin Log")
        #     point.posting_date = self.transaction_date
        #     point.customer = self.customer
        #     point.sales_order = self.name
        #     point.is_cashback = 1 if self.coin_type == "Cashback" else 0
        #     point.total_coin = flt(-1* self.total_coin, point.precision("total_coin"))
        #     point.save()

        # # cek apakah customer group memiliki nilai pada field kelipatan untuk membuat coin log
        # cashback = frappe.db.get_list("Aturan Cashback", filters={"company": self.company, "valid_from": ["<=", self.transaction_date ]}, order_by="valid_from desc", page_length=1)
        # if cashback and cashback[0]:
        #     aturan_cb = frappe.get_doc("Aturan Cashback", cashback[0])
        #     for row in aturan_cb.details:
        #         total = self.rounded_total or self.grand_total
        #         if not (total >= row.from_total and total <= row.to_total):
        #             continue 
                
        #         point = frappe.new_doc("Agent Coin Log")
        #         point.posting_date = self.transaction_date
        #         point.customer = self.customer
        #         point.sales_order = self.name
        #         point.is_cashback = 1
        #         point.total_coin = flt(total*row.percentage/100/1000, point.precision("total_coin"))
        #         point.save()

        #         break
            
        upline = frappe.get_value("Customer", self.customer, "upline")
        if not upline:
            return 

        if self.customer == upline:
            frappe.throw("Customer dan nama upline tidak bsa sama")

        item_price_list = []        
        pr_group = frappe.get_value("Customer Group", self.customer_group, "default_price_list")
        kelipatan = 1000
        
        for row in self.items:
            item_price = _dict({
                "item_code": row.item_code,
                "qty": row.qty,
            })
            
            harga = frappe.get_value("Item Price", {"item_code": row.item_code, "price_list": pr_group or self.customer_group, "selling": 1 }, "price_list_rate")
            if not harga:
                continue

            item_price.update({"rate": harga or 0})
            item_price_list.append(item_price)
            
        make_agent_coin_log(self, item_price_list, kelipatan, upline)
    elif method == "on_cancel":
        log_list = frappe.db.get_list('Agent Coin Log', pluck='name', filters={'sales_order': self.name })
        for log in log_list:
            frappe.delete_doc("Agent Coin Log", log)

def make_agent_coin_log(self, items, kelipatan, upline):
    # ambdil data upline, customer group, dan default price list
    customer_up = frappe.get_value("Customer", upline, ["customer_group", "upline"], as_dict=1)
    pr_group = frappe.get_value("Customer Group", customer_up.customer_group, "default_price_list")
    
    total_margin = 0
    for row in items:
        harga = frappe.get_value("Item Price", {"item_code": row.item_code, "price_list": pr_group or customer_up.customer_group, "selling": 1 }, "price_list_rate")
        if not harga:
            continue

        margin_item = flt(row.rate * row.qty, self.precision("total")) - flt(harga * row.qty, self.precision("total"))
        if margin_item > 0:
            total_margin += margin_item

    if total_margin:
        point = frappe.new_doc("Agent Coin Log")
        point.posting_date = self.transaction_date
        point.customer = upline
        point.sales_order = self.name
        point.kelipatan = kelipatan
        point.total_margin = total_margin
        point.save()

    if upline == customer_up.upline:
        frappe.throw("Upline {} tidak bsa memiliki upline yang sama".format(upline))
            
    if customer_up.upline:
        make_agent_coin_log(self, items, kelipatan, customer_up.upline)
