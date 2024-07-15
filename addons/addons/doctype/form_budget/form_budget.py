# Copyright (c) 2023, DAS and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe.utils import flt

class FormBudget(Document):
	
	def validate(self):
		month = ["januari", "februari", "maret", "april", "mei", "juni", "juli", "agustus", "september", "oktober", "november", "desember"]

		for row in self.details:
			# pengecekan jika account telah digunakan
			account_used = frappe.db.sql_list("""
				SELECT COUNT(account)
				FROM `tabForm Budget Detail` fbd
				JOIN `tabForm Budget` fb on fbd.parent = fb.name
				WHERE fbd.account = %s
					and fb.company = %s
					and fb.fiscal_year = %s
				 	and fbd.name != %s
			""", (row.account, self.company, self.fiscal_year, row.name))
			
			if account_used[0]:
				frappe.throw("Account {} telah digunakan".format(row.account))

			# pengecekan jika budget account lebih kecil dari realisasi
			detail = vars(row)
			for bulan in month:
				row.update({ "_"+bulan : flt((detail["r_"+bulan]/detail[bulan])*100) if detail[bulan] else 0 })
				if detail[bulan] < detail["r_"+bulan]:
					frappe.throw("Nilai Budget Bulan {} pada Account {} tidak boleh lebih kecil dari nilai realisasi yaitu {}".format(bulan, row.account, detail["r_"+bulan]))