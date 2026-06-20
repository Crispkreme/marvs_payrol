import frappe
from frappe.utils import getdate, time_diff_in_hours


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
@frappe.whitelist()
def submit_overtime(employee, attendance_date, start_time, end_time, reason):

    if not employee:
        frappe.throw("Employee is required")

    if not attendance_date:
        frappe.throw("Attendance date is required")

    if not start_time or not end_time:
        frappe.throw("Start and End time are required")

    if not reason:
        frappe.throw("Reason is required")

    # =====================================================
    # COMPUTE HOURS
    # =====================================================
    hours = time_diff_in_hours(end_time, start_time)

    # =====================================================
    # CREATE OT DOC
    # =====================================================
    doc = frappe.get_doc({
        "doctype": "PMS-Overtime",
        "employee": employee,
        "attendance_date": getdate(attendance_date),
        "start_time": start_time,
        "end_time": end_time,
        "reason": reason,
        "requested_hours": round(hours, 2),
        "status": "Pending"
    })

    doc.insert(ignore_permissions=True)

    return {
        "success": True,
        "message": "Overtime request submitted successfully",
        "requested_hours": doc.requested_hours
    }