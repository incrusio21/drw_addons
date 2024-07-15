# Copyright (c) 2024, DAS and contributors
# For license information, please see license.txt

import frappe
from frappe.utils import cint, flt, format_date, format_date, get_last_day, getdate, add_days, date_diff
from frappe.model.document import Document

MONTHS = [
		"",
		"Januari",
		"Februari",
		"Maret",
		"April",
		"Mei",
		"Juni",
		"Juli",
		"Agustus",
		"September",
		"Oktober",
		"November",
		"Desember"
]

class BudgetSalesHarian(Document):
	
	@frappe.whitelist()
	def get_so_last_year(self):

		if not self.fiscal_year:
			frappe.throw("Pilih Fiscal Year terlebih dahulu")
		elif not self.bulan:
			frappe.throw("Pilih Bulan terlebih dahulu")
		
		act = frappe._dict()
		sel_month = MONTHS.index(self.bulan)
		last_fiscal = cint(self.fiscal_year) - 1
		except_name = """ and name not like %s """

		tanggal = "{}-{:02d}-01".format(self.fiscal_year,  sel_month)
		grand_total = frappe.db.sql("""
			SELECT 
				transaction_date, company, sum(grand_total) as grand_total
			FROM `tabSales Order`
			WHERE 
				docstatus = 1
				and YEAR(transaction_date) = %s AND MONTH(transaction_date) = %s 
				{}
			GROUP BY transaction_date
		""".format(except_name), (last_fiscal, sel_month, "%APP%"), as_dict=1)

		for row in grand_total:
			act.update({format_date(row.transaction_date, "YYYY-MM-dd"): row.grand_total})

		start_date = getdate(tanggal)
		end_date = get_last_day(tanggal)

		self.details = []
		for date in [
			add_days(start_date, i)
			for i in range(date_diff(end_date,start_date) + 1)
		]:
			target_date = str(date).replace(self.fiscal_year, str(last_fiscal))
			target = 0
			if act.get(target_date):
				target = act.get(target_date)

			self.append("details", {
				"date": date,
				"target": target + (target * flt(self.pertambahan_target)/100) 
			})

