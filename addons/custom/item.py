
import frappe
from frappe.utils import flt, now

# Hooks
def delete_old_agent_stock_bin(self, method, old_name, new_name, merge=False):
    if merge:
        frappe.db.delete("Agent Stock Bin", {"item_code": old_name})

def recalculate_agent_stock_bin(self, method, old_name, new_name, merge):
    if merge:
        repost_stock_for_customer  = frappe.get_all(
			"Agent Stock Log",
			filters={"item_code": new_name},
			pluck="customer",
			group_by="customer",
		)

        for customer in repost_stock_for_customer:
            bin = get_bin(new_name, customer)
            
            actulal_stock = frappe.db.sql("""
                SELECT 
                    SUM(qty)
                FROM `tabAgent Stock Log` 
                WHERE 
                    item_code= %s AND customer= %s
            """,
                (new_name, customer)
            )

            actulal_stock = flt(actulal_stock[0][0]) if actulal_stock else 0

            if bin.qty != actulal_stock:
                bin.qty = actulal_stock

                bin.modified = now()
                bin.db_update()

# get stock bin
def get_bin(item_code, customer):
	bin = frappe.db.get_value("Agent Stock Bin", {'item_code': item_code, 'customer': customer})
	if not bin:
		bin_obj = _create_bin(item_code, customer)
	else:
		bin_obj = frappe.get_doc("Agent Stock Bin", bin, for_update=True)
	bin_obj.flags.ignore_permissions = True
	
	return bin_obj

def _create_bin(item_code, customer):
	"""Create a bin and take care of concurrent inserts."""

	bin_creation_savepoint = "create_bin"
	try:
		frappe.db.savepoint(bin_creation_savepoint)
		bin_obj = frappe.get_doc(doctype="Agent Stock Bin", item_code=item_code, customer=customer)
		bin_obj.flags.ignore_permissions = 1
		bin_obj.insert()
	except frappe.UniqueValidationError:
		frappe.db.rollback(save_point=bin_creation_savepoint)  # preserve transaction in postgres
		bin_obj = frappe.get_last_doc("Agent Stock Bin", {"item_code": item_code, "customer": customer})

	return bin_obj