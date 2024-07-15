# Copyright (c) 2024, DAS and contributors
# For license information, please see license.txt

import frappe
from frappe import _, _dict
from frappe.utils import cint, getdate, format_date, flt

from erpnext.accounts.utils import get_fiscal_years
from erpnext.accounts.doctype.fiscal_year.fiscal_year import get_from_and_to_date

from addons.addons.doctype.budget_sales_harian.budget_sales_harian import MONTHS
def execute(filters=None):
	data = []
	
	curr_fiscal, date, month = filters.get("fiscal_year"), getdate(), 12

	fiscal_years = get_fiscal_years(date)
	if len(fiscal_years) > 1:
		frappe.throw(
			_("Multiple fiscal years exist for the date {0}. Please set company in Fiscal Year").format(
				format_date(date)
			)
		)
	else:
		fiscal_year = fiscal_years[0][0]


	if curr_fiscal == fiscal_year:
		month = cint(date.strftime("%m"))

	budget = get_budget(curr_fiscal)
	sales_order = get_sales_order(curr_fiscal)
	sales_order_last = get_sales_order_last(cint(curr_fiscal)-1, month, sales_order)

	ytd_last, ytd, ytd_budget = 0, 0, 0
	for bln in range(1, month+1):
		data.append({
			"tanggal": MONTHS[bln]
		})
		total = { "budget": 0, "act": 0, "lm": 0, "ly": 0 }
		for tgl in range(1, 32):
			ress = { "tanggal": tgl, "budget": 0, "act": 0, "lm": 0, "ly": 0 }

			# date_tgl = tgl if tgl > 9 else "0"+str(tgl)
			# date_bulan = bln if bln > 9 else "0"+str(bln)
			tanggal = "{:02d}-{:02d}-{}".format(tgl, bln, curr_fiscal)

			lm_bulan, lm_fiscal = bln-1, curr_fiscal
			if not lm_bulan:
				lm_bulan = 12
				lm_fiscal = cint(curr_fiscal)-1

			lm_tanggal = "{:02d}-{:02d}-{}".format(tgl, lm_bulan, lm_fiscal)

			ly_tanggal = "{:02d}-{:02d}-{}".format(tgl, bln, cint(curr_fiscal)-1)
			
			if budget.get(tanggal):
				ress.update({"budget": budget.get(tanggal) })

			if sales_order.get(tanggal):
				ress.update({"act": sales_order.get(tanggal) })
			
			if sales_order_last.get(lm_tanggal):
				ress.update({"lm": sales_order_last.get(lm_tanggal) })

			if sales_order_last.get(ly_tanggal):
				ress.update({"ly": sales_order_last.get(ly_tanggal) })

			ress.update({
				"act_persen": (ress["act"]/ress["budget"]*100) if ress["budget"] else 0,
				"lm_persen": (ress["act"]/ress["lm"]*100) if ress["lm"] else 0,
				"ly_persen": (ress["act"]/ress["ly"]*100) if ress["ly"] else 0,
			})
			data.append(ress)
			total.update({
				"budget": flt(total["budget"] + ress["budget"]),
				"act": flt(total["act"] + ress["act"]),
				"lm": flt(total["lm"] + ress["lm"]),
				"ly": flt(total["ly"] + ress["ly"]),
			})

		total.update({
			"act_persen": (total["act"]/total["budget"]*100) if total["budget"] else 0,
			"lm_persen": (total["act"]/total["lm"]*100) if total["lm"] else 0, 
			"ly_persen": (total["act"]/total["ly"]*100) if total["ly"] else 0 
		})

		ytd = flt(ytd + total["act"])
		ytd_last = flt(ytd_last + total["ly"])
		ytd_budget = flt(ytd_budget + total["budget"])

		data.append(total)
		data.append({})

	data.extend([
		{ 
			"budget": "YTD "+ str(cint(curr_fiscal)-1), "act": "YTD "+ curr_fiscal, "lm": "(+/-)", "ly": "YTD VS BUDGET", "is_column": 1
		},
		{ 
			"budget": ytd_last, "act": ytd, "act_persen": ytd/ytd_last*100, "lm": flt(ytd-ytd_last), "ly": ytd_budget, "ly_persen": ytd_budget/ytd*100
		},
	])
	return get_column(), data

def get_budget(fiscal_year):
	budget_list = frappe.db.sql("""
		SELECT 
			date, target
		FROM `tabBudget Sales Harian Detail` bshd
		JOIN `tabBudget Sales Harian` bsh ON bsh.name = bshd.parent
		WHERE bsh.fiscal_year = %s
	""", (fiscal_year), as_dict=1)

	budget_date = frappe._dict()
	for row in budget_list:
		budget_date.update({format_date(row.date): row.target})

	return budget_date

def get_sales_order(fiscal_year):
	except_name = """ and name not like %s """
	grand_total = frappe.db.sql("""
		SELECT 
			transaction_date, company, sum(grand_total) as grand_total
		FROM `tabSales Order`
		WHERE 
			docstatus = 1
			and YEAR(transaction_date) = %s
			{}
		GROUP BY transaction_date
	""".format(except_name), (fiscal_year, "%APP%"), as_dict=1)


	act = frappe._dict()
	for row in grand_total:
		act.update({format_date(row.transaction_date): row.grand_total})

	return act

def get_sales_order_last(fiscal_year, month, act):
	except_name = """ and name not like %s """
	grand_total = frappe.db.sql("""
		SELECT 
			transaction_date, company, sum(grand_total) as grand_total
		FROM `tabSales Order`
		WHERE 
			docstatus = 1
			and YEAR(transaction_date) = %s AND (MONTH(transaction_date) <= %s OR MONTH(transaction_date) = 12)
			{}
		GROUP BY transaction_date
	""".format(except_name), (fiscal_year, month, "%APP%"), as_dict=1)

	for row in grand_total:
		act.update({format_date(row.transaction_date): row.grand_total})

	return act

def get_column():
	columns = [
		{
			"label": _("TGL"),
			"fieldname": "tanggal",
			"fieldtype": "Data",
			"width": 150,
		},
		{
			"label": _("Budget"),
			"fieldname": "budget",
			"fieldtype": "Currency",
			"width": 150,
		},
		{
			"label": _("ACT"),
			"fieldname": "act",
			"fieldtype": "Currency",
			"width": 150,
		},
		{
			"label": _("%"),
			"fieldname": "act_persen",
			"fieldtype": "Percent",
			"width": 80,
		},
		{
			"label": _("LM"),
			"fieldname": "lm",
			"fieldtype": "Currency",
			"width": 150,
		},
		{
			"label": _("%"),
			"fieldname": "lm_persen",
			"fieldtype": "Percent",
			"width": 80,
		},
		{
			"label": _("LY"),
			"fieldname": "ly",
			"fieldtype": "Currency",
			"width": 150,
		},
		{
			"label": _("%"),
			"fieldname": "ly_persen",
			"fieldtype": "Percent",
			"width": 100,
		},
	]

	return columns