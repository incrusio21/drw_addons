from __future__ import unicode_literals
import frappe
from frappe import _

def validate(self, method):
    if self.id_drw and frappe.db.exists("Customer", {'id_drw' : self.id_drw, 'name' : ['!=', self.name ]}):
        frappe.throw('ID DRW telah digunakan')