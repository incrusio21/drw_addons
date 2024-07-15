
from __future__ import unicode_literals

import frappe
from frappe.utils import cint, flt, format_date, now

def cek_form_budget(self, method):
    month = ["januari", "februari", "maret", "april", "mei", "juni", "juli", "agustus", "september", "oktober", "november", "desember"]
    
    # mengecek jika akun memiliki budget pada tahun dan company
    budget = frappe.db.sql(""" SELECT fb.name, {}
        FROM `tabForm Budget` fb 
            JOIN `tabForm Budget Detail` fb_d on fb.name = fb_d.parent 
        WHERE 
            account = %s and fiscal_year = %s and company = %s
        """.format(
            ", ".join(month)
        ), (self.account, self.fiscal_year, self.company)
    )

    if not budget or not budget[0]:
        return 
    
    now_month = cint(format_date(self.posting_date, "M"))
    budget_month = budget[0][now_month]
    # jika ada maka cek apakah total debit - credit lebih besar dari budget
    total_account = frappe.db.sql_list(""" 
        SELECT sum(debit-credit) FROM `tabGL Entry` where account = %s and fiscal_year = %s and company = %s and month(posting_date) = %s and is_cancelled != 1 FOR UPDATE """, 
        (self.account, self.fiscal_year, self.company, now_month)
    )[0] or 0.0
    

    if total_account > budget_month:
        frappe.throw("Budget yang telah digunakan untuk Akun <b>{}</b> yaitu <b>{}</b> melebihi batas maksimal Budget maksimal senilai <b>{}</b> .".format(self.account, total_account, budget_month))
    
    # ubah nilai persetasi bulan kemudian buat budget log
    persentase = flt((total_account/budget_month)*100)
    if persentase >= 80 and not frappe.db.sql(""" SELECT name FROM `tabBudget Notif Log` WHERE company = %s and account = %s and bulan = %s """, (self.company, self.account, now_month)):
        budget_notif =  frappe.new_doc("Budget Notif Log")
        budget_notif.update({
            'date': now(),
            'bulan': now_month,
            'form_budget': budget[0][0],
            'company': self.company,
            'account': self.account,
        })
        budget_notif.insert()

    # frappe.throw("Mohon Bersabar, Ini Ujian")
    frappe.db.sql(""" UPDATE `tabForm Budget Detail` set r_{0} = %s, _{0} = %s WHERE parent = %s and account = %s  """.format(month[now_month-1]), (total_account, persentase, budget[0][0], self.account))

    