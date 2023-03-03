from __future__ import unicode_literals
import frappe

def is_director(customer):
    director = frappe.db.get_value("Customer Group", "Director", ['lft', 'rgt'], as_dict=1)
    is_director = frappe.db.sql("""
        SELECT name from `tabCustomer Group` where name = (SELECT customer_group from `tabCustomer` where name = '{}') and lft >= {} and rgt <= {}
    """.format(customer,director.lft,director.rgt))

    return True if len(is_director) > 0 else False
