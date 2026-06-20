import frappe


# =========================================================
# EMPLOYEE INFO
# =========================================================
import frappe


@frappe.whitelist(allow_guest=True)
def get_employee_info(employee):

    if not employee:
        return {"success": False, "message": "No employee provided"}

    if not frappe.db.exists("PMS-Employee", employee):
        return {"success": False, "message": "Employee not found"}

    emp = frappe.get_doc("PMS-Employee", employee)

    # Build full name safely
    full_name = " ".join(filter(None, [
        getattr(emp, "first_name", ""),
        getattr(emp, "middle_name", ""),
        getattr(emp, "last_name", "")
    ])).strip()

    return {
        "success": True,
        "data": {
            "employee_name": full_name or getattr(emp, "employee_id", emp.name),
            "employee_status": getattr(emp, "status", "") or getattr(emp, "employment_status", ""),
            "employee_id": emp.name
        }
    }