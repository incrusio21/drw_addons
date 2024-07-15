# Copyright (c) 2023, DAS and contributors
# For license information, please see license.txt

import frappe
from frappe import _, _dict
from frappe.utils import getdate, add_days, date_diff


def execute(filters=None):
	data = []

	items, invoice_payment, slip_pembayaran = RekapHarian(filters).process()

	start_date = getdate(filters.from_date)
	end_date = getdate(filters.to_date)

	def pasien_amount(item, out, field_group, itemgroup, amount_field, customer_item=None, customer_group=None, change_amount=False):
		if item.get(field_group) != itemgroup:
			return
		
		out[amount_field] += item.amount

		if change_amount:
			out[amount_field] -= item.change_amount

		if (isinstance(customer_item, set) and customer_group 
			and item.customer_group == customer_group):
			customer_item.add(item.customer)
	
	for date in [
		add_days(start_date, i)
		for i in range(date_diff(end_date,start_date) + 1)
	]:
		result = {
			"posting_date": date,
			"amount_produk": 0.0,
			"amount_treatment": 0.0,
			"pasien_baru": 0,	
			"pasien_produk": 0,	
			"pasien_treatment": 0,	
			"cash": 0.0,
			"debit_mandiri": 0.0,
			"debit_bni": 0.0,
			"debit_bca": 0.0,
			"debit_bri": 0.0,
			"qris_bni": 0.0,
			"tf_mandiri": 0.0,
			"tf_bri": 0.0,
			"tf_bni": 0.0,

			"item_biaya": "",
			"nominal_biaya": 0.0,
		}
		if items.get(date):
			pasien_produk, pasien_treatment = set(), set()
			for item in items[date]["items"]:
				pasien_amount(item, result, "item_group", "Produk BPOM", 'amount_produk', pasien_produk, "Klinik")
				pasien_amount(item, result, "item_group", "Layanan Klinik", 'amount_treatment', pasien_treatment, "Klinik")

			result['pasien_baru'] = len([key for key, value in items[date]["customer"].items() if value == "Klinik"]) 
			result['pasien_produk'] = len(pasien_produk) 
			result['pasien_treatment'] = len(pasien_treatment) 
		
		if invoice_payment.get(date):
			for item in invoice_payment[date]["payment"]:
				pasien_amount(item, result, "mode_of_payment", "Cash", 'cash', change_amount=True)
				
				# pasien_amount(item, result, "mode_of_payment", "Cash", 'debit_mandiri')
				# pasien_amount(item, result, "mode_of_payment", "Cash", 'debit_mandiri')
				pasien_amount(item, result, "mode_of_payment", "QRIS BNI", 'qris_bni')
				pasien_amount(item, result, "mode_of_payment", "Transfer Mandiri", 'tf_mandiri')
				pasien_amount(item, result, "mode_of_payment", "Transfer BRI", 'tf_bri')

		if slip_pembayaran.get("date"):
			for slip in slip_pembayaran[date]:
				result['item_biaya'] += (", " if result['item_biaya'] else "") + slip.keperluan
				result['nominal_biaya'] += slip.jumlah

		data.append(result)

	return get_columns(filters), data
	
def get_columns(filters):
	columns = [
		{
			"label": _("Tanggal"),
			"fieldname": "posting_date",
			"fieldtype": "Date",
		},
		{
			"label": _("Pedapatan Produk"),
			"fieldname": "amount_produk",
			"fieldtype": "Currency",
		},
		{
			"label": _("Pedapatan Treatment"),
			"fieldname": "amount_treatment",
			"fieldtype": "Currency",
		},
		{
			"label": _("Total Pasien Baru"),
			"fieldname": "pasien_baru",
			"fieldtype": "Int",
		},
		{
			"label": _("Pasien Transaksi Produk"),
			"fieldname": "pasien_produk",
			"fieldtype": "Int",
		},
		{
			"label": _("Pasien Transaksi Treatment"),
			"fieldname": "pasien_treatment",
			"fieldtype": "Int",
		},
		{
			"label": _("Cash"),
			"fieldname": "cash",
			"fieldtype": "Currency",
			"width": 150,
		},
		{
			"label": _("Debit Mandiri"),
			"fieldname": "debit_mandiri",
			"fieldtype": "Currency",
			"width": 150,
		},
		{
			"label": _("Debit BNI"),
			"fieldname": "debit_bni",
			"fieldtype": "Currency",
			"width": 150,
		},
		{
			"label": _("Debit BCA"),
			"fieldname": "debit_bca",
			"fieldtype": "Currency",
			"width": 150,
		},
		{
			"label": _("Debit BRI"),
			"fieldname": "debit_bca",
			"fieldtype": "Currency",
			"width": 150,
		},
		{
			"label": _("Qris BNI"),
			"fieldname": "qris_bni",
			"fieldtype": "Currency",
			"width": 150,
		},
		{
			"label": _("TF Mandiri"),
			"fieldname": "tf_mandiri",
			"fieldtype": "Currency",
			"width": 150,
		},
		{
			"label": _("TF BRI"),
			"fieldname": "tf_bri",
			"fieldtype": "Currency",
			"width": 150,
		},
		{
			"label": _("TF BNI"),
			"fieldname": "tf_bni",
			"fieldtype": "Currency",
			"width": 150,
		},
		{
			"label": _("Item Biaya"),
			"fieldname": "item_biaya",
			"fieldtype": "Text",
			"width": 200,
		},
		{
			"label": _("Nominal Biaya"),
			"fieldname": "nominal_biaya",
			"fieldtype": "Currency",
		},
	]

	return columns

class RekapHarian(object):
	def __init__(self, filters=None):
		self.pos_invoice_items, self.pos_invoice_payments, self.slip_pengeluaran = [], [], []
		self.filters = frappe._dict(filters)
		self.get_pos_invoice()
		self.get_pos_pembayaran()
		self.get_slip_pengeluaran()

	def process(self):
		self.grouped_invoice, self.grouped_invoice_payment, self.grouped_slip_pembayaran = {}, {}, {}
		

		for row in self.pos_invoice_items:
			self.grouped_invoice.setdefault(row.posting_date, {
				"customer": {},
				"items": []
			})

			self.grouped_invoice[row.posting_date]["customer"].setdefault(row.customer, row.customer_group)

			self.grouped_invoice[row.posting_date]["items"].append(row)

		for row in self.pos_invoice_payments:
			self.grouped_invoice_payment.setdefault(row.posting_date, {
				"customer": {},
				"payment": []
			})

			self.grouped_invoice_payment[row.posting_date]["customer"].setdefault(row.customer, row.customer_group)
			self.grouped_invoice_payment[row.posting_date]["payment"].append(row)

		for row in self.slip_pengeluaran:
			self.grouped_slip_pembayaran.setdefault(row.tanggal, []).append(row)
		
		return self.grouped_invoice, self.grouped_invoice_payment, self.grouped_slip_pembayaran
	
	def get_pos_invoice(self):

		conditions = ""

		for field in ["company", "branch"]:
			if self.filters.get(field):
				conditions += " and pos.{0} = %({1})s".format(field, field)

		if self.filters.get("from_date"):
			conditions += " and pos.posting_date >= %(from_date)s"

		if self.filters.get("to_date"):
			conditions += " and pos.posting_date <= %(to_date)s"

		self.pos_invoice_items = frappe.db.sql(
			"""
				SELECT
					posting_date, customer, customer_group, 
					posi.net_amount as amount, posi.item_group 
				FROM `tabPOS Invoice`pos
				JOIN `tabPOS Invoice Item` posi on pos.name = posi.parent
				WHERE pos.docstatus = 1 and pos.is_return != 1 and pos.outstanding_amount = 0 
				{conditions}
			""".format(
				conditions=conditions
			),
			self.filters,
			as_dict=1,
		)

	def get_pos_pembayaran(self):

		conditions = ""

		for field in ["company", "branch"]:
			if self.filters.get(field):
				conditions += " and pos.{0} = %({1})s".format(field, field)

		if self.filters.get("from_date"):
			conditions += " and pos.posting_date >= %(from_date)s"

		if self.filters.get("to_date"):
			conditions += " and pos.posting_date <= %(to_date)s"

		self.pos_invoice_payments = frappe.db.sql(
			"""
				SELECT
					posting_date, customer, customer_group, change_amount,
					posp.mode_of_payment, posp.amount 
				FROM `tabPOS Invoice`pos
				JOIN `tabSales Invoice Payment` posp on pos.name = posp.parent and posp.parenttype = "POS Invoice"
				WHERE pos.docstatus = 1 and pos.is_return != 1 and pos.outstanding_amount = 0 
				{conditions}
			""".format(
				conditions=conditions
			),
			self.filters,
			as_dict=1,
		)

	def get_slip_pengeluaran(self):

		conditions = ""

		# for field in ["company"]:
		# 	if self.filters.get(field):
		# 		conditions += " and pos.{0} = %({1})s".format(field, field)

		if self.filters.get("from_date"):
			conditions += " and tanggal >= %(from_date)s"

		if self.filters.get("to_date"):
			conditions += " and tanggal <= %(to_date)s"

		self.slip_pengeluaran = frappe.db.sql(
			"""
				SELECT
					tanggal, keperluan, jumlah
				FROM `tabSlip Pengeluaran Uang`
				WHERE docstatus = 1
				{conditions}
			""".format(
				conditions=conditions
			),
			self.filters,
			as_dict=1,
		)