import frappe
import os

@frappe.whitelist()
def upload(doctype, docname, docfield, is_private=0):
    try:
        f = frappe.request.files['file']
        site_path = frappe.utils.get_bench_path() + '/sites' + frappe.utils.get_site_path().replace('./','/')
        if is_private == 0:
            public_path = site_path + '/public/files/'
            if '.' not in f.filename:
                filename = f.filename + '.jpg'
            else:
                filename = f.filename
            f.save(public_path + filename)
            file_size = os.stat(public_path + f.filename).st_size
            file_url = '/files/' + f.filename
        else:
            private_path = site_path + '/private/files/'
            if '.' not in f.filename:
                filename = f.filename + '.jpg'
            else:
                filename = f.filename
            f.save(private_path + filename)
            file_size = os.stat(private_path + f.filename).st_size
            file_url = '/private/files/' + f.filename
        
        doc = frappe.new_doc("File")
        doc.update({
            "file_name": f.filename,
            "is_private": is_private,
            "file_url": file_url,
            "file_size": file_size,
            "folder": "Home/Attachments",
            "attached_to_doctype": doctype,
            "attached_to_name": docname,
            "attached_to_field": docfield,
            "doctype": "File"
            })
        doc.insert(ignore_permissions=True)

        frappe.db.set_value(doctype, docname, docfield, file_url)
        frappe.db.commit()
        return {
            'code': 200,
            'data': frappe.get_doc(doctype, docname)
        }
    except:
        frappe.log_error("{} {} {} {}\n\n".format(doctype, docname, docfield, f.filename) + frappe.get_traceback(), "ERROR: Upload file")
        return {
            'code': 500,
            'error': 'Upload error'
        }
    