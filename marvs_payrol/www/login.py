import frappe

@frappe.whitelist(allow_guest=True)
def employee_login(email, password):

    employee = frappe.db.get_value(
        "PMS-Employee",
        {"email_address": email},
        ["name", "full_name", "email_address", "employment_status", "image"],
        as_dict=True
    )

    if not employee:
        return None

    if password != employee.name:
        return None

    return {
        "employee_id": employee.name,
        "full_name": employee.full_name,
        "email": employee.email_address,
        "status": employee.employment_status,
        "image": employee.image
    }

@frappe.whitelist()
def employee_logout():
    frappe.local.login_manager.logout()
    return {"message": "Logged out successfully"}