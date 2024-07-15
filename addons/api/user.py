import frappe
from frappe.utils.password import check_password


@frappe.whitelist(allow_guest=True)
def forgot_password(user):
    usr = frappe.get_all("User", or_filters=[["name", "=", user], ["username", "=", user]])
    self = None
    if len(usr) > 0:
        self = frappe.get_doc("User", usr[0]['name'])
    else:
        customer = frappe.get_value("Customer", {"id_drw": user})
        if customer:
            user_perm = frappe.get_value("User Permission", {"for_value": customer}, "user")
            if user_perm:
                self = frappe.get_doc("User", user_perm)
    
    if self:
        from frappe.utils import random_string

        key = random_string(32)
        self.db_set("reset_password_key", key)

        url = "https://skincare.drwhub.com/update-password?key=" + key
        self.password_reset_mail(url)
    else:
        frappe.log_error(user, "API: Reset Password Failed")

    return "ok"


@frappe.whitelist()
def change_password(usr: str, old_password: str, new_password: str):
    valid_usr = check_password(usr, old_password)

    doc = frappe.get_doc("User", valid_usr)
    doc.new_password = new_password
    doc.save(ignore_permissions=True)
    return "ok"
    