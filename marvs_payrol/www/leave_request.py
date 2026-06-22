import frappe
from datetime import datetime

# =========================================================
# EMPLOYEE INFO
# =========================================================
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

# =========================
# CREATE LEAVE REQUEST
# =========================
@frappe.whitelist(allow_guest=True)
def create_leave(employee, employee_name, leave_type, from_date, to_date, reason):

    try:

        if not employee or not from_date or not to_date:
            return {"success": False, "message": "Missing required fields"}

        # calculate total days
        d1 = datetime.strptime(from_date, "%Y-%m-%d")
        d2 = datetime.strptime(to_date, "%Y-%m-%d")

        total_days = (d2 - d1).days + 1

        if total_days <= 0:
            return {"success": False, "message": "Invalid date range"}

        doc = frappe.get_doc({
            "doctype": "PMS-Leave Request",
            "employee": employee,
            "employee_name": employee_name,
            "leave_type": leave_type,
            "from_date": from_date,
            "to_date": to_date,
            "reason": reason,
            "status": "Pending",
            "total_days": total_days
        })

        doc.insert(ignore_permissions=True)
        frappe.db.commit()

        return {
            "success": True,
            "message": "Leave request submitted successfully"
        }

    except Exception:
        frappe.log_error(frappe.get_traceback(), "Leave Request Error")

        return {
            "success": False,
            "message": frappe.get_traceback()
        }