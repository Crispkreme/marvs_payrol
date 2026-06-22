import frappe
from datetime import datetime
from frappe.model.document import Document


# =====================================================
# GET EMPLOYEE FROM LOGGED-IN USER
# =====================================================
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


# =====================================================
# SUBMIT OVERTIME
# =====================================================
@frappe.whitelist(allow_guest=True)
def create_overtime(
    employee,
    attendance_date,
    start_time,
    end_time,
    reason,
    overtime_type
):

    try:

        if not employee:
            return {
                "success": False,
                "message": "Employee is required"
            }

        fmt = "%H:%M"

        start = datetime.strptime(start_time, fmt)
        end = datetime.strptime(end_time, fmt)

        diff = end - start

        # Crossing midnight
        if diff.total_seconds() < 0:
            diff = (
                (datetime.strptime("24:00", fmt) - start)
                +
                (end - datetime.strptime("00:00", fmt))
            )

        hours = round(
            diff.total_seconds() / 3600,
            2
        )

        doc = frappe.new_doc("PMS-Overtime Request")

        doc.employee = employee
        doc.attendance_date = attendance_date
        doc.start_time = start_time
        doc.end_time = end_time
        doc.requested_hours = hours
        doc.reason = reason
        doc.overtime_type = overtime_type
        doc.status = "Pending"
        doc.employee_status = "Pending"

        doc.insert(ignore_permissions=True)

        frappe.db.commit()

        return {
            "success": True,
            "message": "Overtime request submitted successfully"
        }

    except Exception:
        return {
            "success": False,
            "message": frappe.get_traceback()
        }