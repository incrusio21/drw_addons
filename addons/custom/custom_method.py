# Copyright (c) 2023, DAS
# MIT License. See license.txt

from __future__ import unicode_literals
import frappe
from frappe import _

def is_director(customer):
    director = frappe.db.get_value("Customer Group", "Director", ['lft', 'rgt'], as_dict=1)
    is_director = frappe.db.sql("""
        SELECT name from `tabCustomer Group` where name = (SELECT customer_group from `tabCustomer` where name = '{}') and lft >= {} and rgt <= {}
    """.format(customer,director.lft,director.rgt))

    return True if len(is_director) > 0 else False

@frappe.whitelist()
def check_password(pwd, user=None, doctype= "User", fieldname="password"):
    """Checks if user and password are correct, else raises frappe.AuthenticationError"""
    from frappe.utils.password import Auth, passlibctx
    
    if not user:
        user = frappe.session.user
        
    result = (
        frappe.qb.from_(Auth)
        .select(Auth.name, Auth.password)
        .where(
            (Auth.doctype == doctype)
            & (Auth.name == user)
            & (Auth.fieldname == fieldname)
            & (Auth.encrypted == 0)
        )
        .limit(1)
        .run(as_dict=True)
    )

    if not result or not passlibctx.verify(pwd, result[0].password):
        frappe.throw(_("Incorrect User or Password"))
    
    # lettercase agnostic
    user = result[0].name

    return user