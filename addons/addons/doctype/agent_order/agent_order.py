# Copyright (c) 2023, DAS and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from erpnext import get_default_company

class AgentOrder(Document):
	def validate(self):
		self.set_paket()
		self.set_item()
		self.set_promo()
		self.set_grand_total()

	def on_submit(self):
		from addons.custom.custom_method import is_director

		# jika customer merupakan direktor/parentny direktor. buat sales order dan sales invoice 
		if is_director(self.customer):
			doc = frappe.new_doc("Sales Order")
			doc.id_drw_order = self.id_drw_order
			doc.customer = self.customer
			doc.transaction_date = self.tanggal
			doc.delivery_date = self.tanggal

			items = []
			for row in self.items:
				items.append({
					'item_code': row.kode_item,
					'qty': row.qty,
					'delivery_date': doc.delivery_date,
					'price_list_rate': row.price_list
				})

			doc.discount_amount = self.total_promo

			taxes = frappe.db.get_value("Company", get_default_company(), ['default_biaya_ongkir', 'default_biaya_penanganan'], as_dict=1)
			taxes_charges = []

			if self.biaya_ongkir:
				taxes_charges.append({
					'charge_type' : 'Actual',
					'account_head': taxes.default_biaya_ongkir,
					'tax_amount' : self.biaya_ongkir,
					'description' : self.ekspedisi or 'Biaya Ongkir' 
				})

			if self.biaya_ongkir:
				taxes_charges.append({
					'charge_type' : 'Actual',
					'account_head': taxes.default_biaya_penanganan,
					'tax_amount' : self.biaya_penanganan,
					'description' : 'Biaya Penanganan'
				})

			if len(taxes_charges) > 0:
				doc.set('taxes', taxes_charges)

			doc.set('items', items)

			doc.submit()

			# buat sinv dari so
			from erpnext.selling.doctype.sales_order.sales_order import make_sales_invoice

			sinv = make_sales_invoice(doc.name)
			sinv.posting_date = self.tanggal
			sinv.set_posting_time = 1
			sinv.due_date = frappe.utils.add_days(self.tanggal, 90)

			sinv.submit()
		else:
			# jika bukan maka buat stock log
			upline = frappe.db.get_value("Customer", self.customer, 'upline')
			for row in self.items:
				# log customer
				doc = frappe.new_doc("Agent Stock Log")
				doc.customer = self.customer
				doc.item_code = row.kode_item
				doc.qty = row.qty
				doc.id_agent_order = self.name
				doc.save()
				# log upline
				if upline:
					doc_upline = frappe.new_doc("Agent Stock Log")
					doc_upline.customer = upline
					doc_upline.item_code = row.kode_item
					doc_upline.qty = row.qty * -1
					doc_upline.id_agent_order = self.name
					doc_upline.save()

		# cek apakah customer group memiliki nilai pada field kelipatan untuk membuat point log
		kelipatan = frappe.db.get_value("Customer Group", self.agent_group, 'kelipatan_transaksi_untuk_dapat_point')
		if kelipatan > 0:
			point = frappe.new_doc("Agent Point Log")
			point.posting_date = self.tanggal
			point.customer = self.customer
			point.agent_order = self.name
			point.kelipatan = kelipatan
			point.total_belanja = self.grand_total
			point.save()


	def set_paket(self):
		total = 0.0
		for row in self.daftar_paket:
			row.set('total', row.harga*row.qty)

			total += row.total

		self.total_paket = total
		self.base_total_paket = total

	def set_promo(self):
		total = 0.0
		for row in self.daftar_promo:
			total += row.nilai

		self.total_promo = total
		self.base_total_promo = total

	def set_item(self):
		total = 0.0
		for row in self.items:
			row.set('rate', row.price_list - row.discount)
			row.set('amount', row.rate * row.qty)

			total += row.amount

		self.total = total
		self.base_total = total

	def set_grand_total(self):
		self.net_total = self.total
		self.base_net_total = self.net_total

		self.grand_total = self.net_total + self.biaya_ongkir + self.biaya_penanganan - self.total_promo

	def on_cancel(self):
		log_list = frappe.db.get_list('Agent Stock Log', pluck='name', filters={'id_agent_order': self.name })
		for log in log_list:
			frappe.delete_doc("Agent Stock Log", log)