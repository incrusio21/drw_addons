from __future__ import unicode_literals
import frappe
from frappe import _

from frappe.utils import flt, now, today

@frappe.whitelist()
def repair_gl_entry(doctype,docname):
	
	docu = frappe.get_doc(doctype, docname)	
	# delete_sl = frappe.db.sql(""" DELETE FROM `tabStock Ledger Entry` WHERE voucher_no = "{}" """.format(docname))
	delete_gl = frappe.db.sql(""" DELETE FROM `tabGL Entry` WHERE voucher_no = "{}" """.format(docname))

	# frappe.db.sql(""" UPDATE `tabSingles` SET VALUE = 1 WHERE `field` = "allow_negative_stock" """)
	# docu.update_stock_ledger()
	docu.make_gl_entries()
	# frappe.db.sql(""" UPDATE `tabSingles` SET VALUE = 0 WHERE `field` = "allow_negative_stock" """)

def update_stock_bin():
    stock_bin = frappe.db.sql("""
        select name, item_code, customer from `tabAgent Stock Bin` GROUP BY item_code, customer HAVING (COUNT(item_code) > 1) AND 
        (COUNT(customer) > 1)
    """, as_dict=1)

    for row in stock_bin:
        frappe.msgprint(row.name)
        frappe.db.sql(""" DELETE FROM `tabAgent Stock Bin` where name != %s and item_code = %s and customer = %s """, (row.name, row.item_code, row.customer) )
        
        actulal_stock = frappe.db.sql("""
			SELECT 
				SUM(qty)
			FROM `tabAgent Stock Log` 
			WHERE 
				item_code= %s AND customer= %s
		""",
			(row.item_code, row.customer)
		)
        
        actulal_stock = flt(actulal_stock[0][0]) if actulal_stock else 0

        frappe.db.sql(""" UPDATE `tabAgent Stock Bin` SET qty = %s where name = %s  """, (actulal_stock, row.name))

def update_coa():
    coa = frappe.db.get_list("GL Entry", 
        filters={
            'account': '5110.024 - HPP Penjualan - ESTK',
        },
        fields=['name', 'voucher_type', 'voucher_no'],
        group_by="voucher_no"
    )

    for row in coa:
        # ubah nilai expense pada table detail item
        table = ""    
        if  row.voucher_type in ["Delivery Note", "Sales Invoice", "Purchase Receipt", "Purchase Invoice"]:
            table = "Item" 
        elif row.voucher_type in ["Stock Entry"]:
            table = "Detail"
        
        if table:
            frappe.db.sql(
                """
                    UPDATE `tab{} {}` 
                    SET 
                        expense_account = "4220.000 - HPP Penjualan - ESTK" 
                    WHERE parent = "{}"
                """.format(row.voucher_type, table, row.voucher_no)
            )

            repair_gl_entry(row.voucher_type, row.voucher_no)
            print(row.voucher_type + "-" + row.voucher_no)
        else:
            print("error:" + row.voucher_type + "-" + row.voucher_no)

# bench execute addons.patch.create_user_employee
def create_user_employee():
    employee = frappe.db.get_list("Employee",
        filters={
            'user_id': ('in', [None, '']),
            "company_email": ('not in', [None, ''])
        },
        fields=['name', 'company_email']
    )

    print(len(employee))
    from erpnext.hr.doctype.employee.employee import create_user
    for row in employee:
        print(row.name)
        if not frappe.db.exists("User", row.company_email):
            user_id = create_user(row.name, email=row.company_email)
        else:
            user_id = row.company_email
            
        emp = frappe.get_doc("Employee", row.name)
        emp.user_id = user_id
        emp.save()

def delivery_note_status():
    dn = frappe.db.sql(""" 
        SELECT dn.name, dni.against_sales_order, so.status
            FROM `tabDelivery Note` dn 
            JOIN  `tabDelivery Note Item` dni on dni.parent = dn.name
            JOIN `tabSales Order` so on dni.against_sales_order = so.name
        WHERE
            dn.per_billed > 0
            and dn.status = "To Bill"
            and so.status = "Completed"
        GROUP BY dn.name, so.name             
    """, as_dict=1)

    for row in dn:
        frappe.db.sql(""" update `tabDelivery Note` set status = "Completed" where name = %s  """, (row.name))

def cancel_prec():
    prec_list = [
    ]    
    for row in prec_list:
        print(row)
        doc = frappe.get_doc("Purchase Receipt", row)
        if doc.docstatus == 2:
            doc.db_set("workflow_state", "Cancelled")

def prec_status():
    prec_item = frappe.db.sql(""" 
        SELECT preci.parent, preci.purchase_order
            FROM `tabPurchase Receipt Item` preci
            JOIN  `tabPurchase Receipt` prec on prec.name = preci.parent
            JOIN  `tabPurchase Order Item` poi on poi.name = preci.purchase_order_item
        WHERE
            prec.docstatus = 1
            and preci.purchase_order is not null
            and prec.status != "Completed"
            and poi.received_qty = 0
            and poi.parent not in ("DRW-PO-06-23-003", "DRW-PO-06-23-005")
        group by  preci.parent, preci.purchase_order
        order by preci.parent
    """, as_dict=1)

    print(len(prec_item))
    # for row in prec_item:
    #     prec = frappe.get_doc("Purchase Receipt", row.parent)
    #     print(row.parent)
    #     prec.update_prevdoc_status()
    #     if flt(prec.per_billed) < 100:
    #         prec.update_billing_status()
    #     else:
    #         prec.db_set("status", "Completed")

def purchase_order_status():
    prec_item = frappe.db.sql(""" 
        SELECT preci.parent, preci.purchase_order
            FROM `tabPurchase Receipt Item` preci 
        WHERE
            preci.docstatus = 1
            and (preci.purchase_order_item is null or preci.purchase_order_item = "")
            and preci.purchase_order is not null
        group by  preci.parent, preci.purchase_order
        order by preci.parent
        limit 1
    """, as_dict=1)

    for row in prec_item:
        prec = frappe.get_doc("Purchase Receipt", row.parent)
        print(row.parent)
        update = False
        for d in prec.items:
            if d.purchase_order_item or not d.purchase_order:
                continue

            po_item = frappe.get_value("Purchase Order Item", {"parent": d.purchase_order, "item_code": d.item_code, 'rate': d.rate, "received_qty": 0}, "name")
            if not po_item:
                print(row.parent + "Row" + str(d.idx))
            else:
                update = True
                d.db_set("purchase_order_item", po_item)

        if not update:
            print(row.parent + "Gagal Update")
            continue

        prec.update_prevdoc_status()
        if flt(prec.per_billed) < 100:
            prec.update_billing_status()
        else:
            prec.db_set("status", "Completed")

def patient_price_list():
    patient = frappe.get_list("Patient", pluck="name", filters={
        "default_price_list": ["!=", "Klinik"],
        "status": "Active"
    })

    for row in patient:
        print(row)
        doc = frappe.get_doc("Patient", row)
        doc.default_price_list = "Klinik"
        doc.save()

        frappe.db.commit()

def fix_agent_order_gl_tax():
    so_error = ["DRW-ORD-23-108873"]

    so = frappe.db.sql(""" 
        SELECT name, id_drw_order, company FROM `tabSales Order` WHERE id_drw_order IN (
            SELECT id_drw_order FROM `tabAgent Order` WHERE biaya_penanganan > 0 AND biaya_ongkir = 0
        ) and name not in %(so_error)s
    """, {"so_error" : so_error}, as_dict=1)

    for row in so:
        print("--------")
        print(row.name)
        d_company = frappe.db.get_value("Company", row.company, ['default_biaya_ongkir', 'default_biaya_penanganan', "default_warehouse", "cost_center"], as_dict=1)

        agent_order = frappe.db.get_value("Agent Order", {"id_drw_order": row.id_drw_order }, ["biaya_penanganan"], as_dict=1)
        sales_order = frappe.get_doc("Sales Order", row.name)
        
        so_updated = False
        for so_taxes in sales_order.taxes:
            if so_taxes.account_head == d_company.default_biaya_penanganan and so_taxes.tax_amount == agent_order.biaya_penanganan:
                so_updated = True

        if not so_updated:
            continue

        sales_order.append("taxes", {
            'charge_type' : 'Actual',
            'account_head': d_company.default_biaya_penanganan,
            'tax_amount' : agent_order.biaya_penanganan,
            'description' : 'Biaya Penanganan',
            "cost_center" : d_company.cost_center
        })

        sales_order.flags.ignore_validate_update_after_submit = True
        sales_order.calculate_taxes_and_totals()
        sales_order.save()
        print("--so updated--")
        # get sales invoice
        sinv = frappe.db.get_value("Sales Invoice Item", { "sales_order": row.name }, "parent")
        print(sinv)
        sales_invoice = frappe.get_doc("Sales Invoice", sinv)
        sales_invoice.append("taxes", {
            'charge_type' : 'Actual',
            'account_head': d_company.default_biaya_penanganan,
            'tax_amount' : agent_order.biaya_penanganan,
            'description' : 'Biaya Penanganan',
            "cost_center" : d_company.cost_center
        })
        sales_invoice.flags.ignore_validate_update_after_submit = True
        sales_invoice.calculate_taxes_and_totals()
        sales_invoice.save()
        
        repair_gl_entry("Sales Invoice", sinv)
        print("--sinv updated--")

        # if sales_invoice.outstanding_amount > 0:  
        #     frappe.db.commit()  
        #     continue
        
        payment_reference = frappe.db.sql(""" select pe.name as payment_entry, per.name, per.allocated_amount from `tabPayment Entry` pe join `tabPayment Entry Reference` 
            per on pe.name = per.parent where per.reference_doctype = "Sales Invoice" and per.reference_name = %s and unallocated_amount >= %s """, 
            (sinv, agent_order.biaya_penanganan), as_dict=1)
        
        if payment_reference and payment_reference[0]:
            print(payment_reference[0].payment_entry)
            pe = frappe.get_doc("Payment Entry", payment_reference[0].payment_entry)
            for pe_row in pe.references:
                if pe_row.name != payment_reference[0].name:
                    continue
                
                pe_row.allocated_amount += agent_order.biaya_penanganan

            pe.flags.ignore_validate_update_after_submit = True
            pe.set_amounts()
            pe.save()

            repair_gl_entry("Payment Entry", payment_reference[0].payment_entry)
            print("--pe updated--")

        frappe.db.commit()

def trigger_patient_customer():
    patient = frappe.get_list("Patient", pluck="name", filters={
        "customer": ["is", "not set"],
        "status": "Active"
    })

    from erpnext.healthcare.doctype.patient.patient import create_customer

    for row in patient:
        print(row)
        doc = frappe.get_doc("Patient", row)
        create_customer(doc)

        frappe.db.commit()

def update_customer_rm():
    patient = frappe.get_list("Patient", fields=["name", "customer"], filters={
        "customer": ["is", "set"],
        "status": "Active"
    })

    for row in patient:
        frappe.db.set_value("Customer", row.customer, "no_rm_patient", row.name)

def trigger_depreciation_entry():
    dep_schedule = frappe.get_list("Depreciation Schedule", fields=["parent as asset_name", "schedule_date"], filters={
        "journal_entry": ["is", "not set"],
        "docstatus": 1,
        "schedule_date": ["<", today()],
    })

    print(len(dep_schedule))
    from erpnext.assets.doctype.asset.depreciation import make_depreciation_entry

    for row in dep_schedule:
        print(row.asset_name)
        make_depreciation_entry(row.asset_name, row.schedule_date)
        frappe.db.commit()

def remove_agent_point():
    point_log = frappe.get_all(
        "Agent Point Log",
        filters={
            "posting_date": (
                "<",
                "2024-01-01",
            ),
        }
    )

    print(len(point_log))
    for row in point_log:
        print(row)
        doc = frappe.get_doc("Agent Point Log", row)
        doc.delete()
        frappe.db.commit()

def so_diskon_fix():
    so_error = []

    so = frappe.db.sql(""" 
        SELECT 
            ao.name, ao.id_drw_order, ao.grand_total, so.`name` AS so_name, so.`grand_total` AS so_total,
            so.company
        FROM `tabAgent Order` ao
        LEFT JOIN `tabSales Order` so ON ao.`id_drw_order` = so.`id_drw_order`
        WHERE tanggal BETWEEN "2024-04-01" AND "2024-04-30" AND ao.`grand_total` != so.`grand_total`
        # and so.name not in %(so_error)s 
    """, {"so_error" : so_error}, as_dict=1)
    
    for row in so:
        print("--------")
        print(row.so_name)
        d_company = frappe.db.get_value("Company", row.company, ['default_biaya_ongkir', 'default_biaya_penanganan', "default_warehouse", "cost_center"], as_dict=1)

        agent_order = frappe.db.get_value("Agent Order", row.name, ["biaya_penanganan", "total_promo"], as_dict=1)
        sales_order = frappe.get_doc("Sales Order", row.so_name)

        new_taxes = []        
        for so_taxes in sales_order.taxes:
            if not (so_taxes.account_head == d_company.default_biaya_penanganan and so_taxes.tax_amount == agent_order.biaya_penanganan):
                new_taxes.append({
                    'charge_type' : 'Actual',
                    'account_head': d_company.default_biaya_penanganan,
                    'tax_amount' : agent_order.biaya_penanganan,
                    'description' : 'Biaya Penanganan',
                    "cost_center" : d_company.cost_center
                })
        
        if new_taxes:
            sales_order.extend("taxes", new_taxes)

        sales_order.discount_amount = agent_order.total_promo
        sales_order.flags.ignore_validate_update_after_submit = True
        sales_order.calculate_taxes_and_totals()

        sales_order.db_update()
        sales_order.update_children()
        print("--so updated--")

        sinv = frappe.db.get_value("Sales Invoice Item", { "sales_order": row.so_name }, "parent")
        print(sinv)
        sales_invoice = frappe.get_doc("Sales Invoice", sinv)

        if new_taxes:
            sales_invoice.extend("taxes", new_taxes)
        

        sales_invoice.discount_amount = agent_order.total_promo
        sales_invoice.calculate_taxes_and_totals()

        sales_invoice.db_update()
        sales_invoice.update_children()

        repair_gl_entry("Sales Invoice", sinv)
        print("--sinv updated--")

        frappe.db.commit()

def agent_cashback_log():
    acl = frappe.get_list("Agent Cashback Log", pluck="name")
    for row in acl:
        print(row)
        doc = frappe.get_doc("Agent Cashback Log", row)
        get_coin = frappe.get_value("Sales Order", doc.sales_order, "get_cashback")
        if not get_coin:
            continue

        doc.total_coin = get_coin
        doc.save()