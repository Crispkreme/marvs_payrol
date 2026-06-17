import frappe
from frappe.utils import now_datetime, today, time_diff_in_hours


# =========================
# CALCULATE HOURS
# =========================
def calc_hours(start, end):
    if start and end:
        return time_diff_in_hours(end, start)
    return 0


def compute_total_hours(doc):
    am_hours = calc_hours(doc.get("am_time_in"), doc.get("am_time_out"))
    pm_hours = calc_hours(doc.get("pm_time_in"), doc.get("pm_time_out"))

    return round((am_hours or 0) + (pm_hours or 0), 2)


# =========================
# EMPLOYEE INFO
# =========================
@frappe.whitelist(allow_guest=True)
def get_employee_info(employee):

    if not employee:
        return {}

    if not frappe.db.exists("PMS-Employee", employee):
        return {
            "employee_name": "Not Found",
            "employee_id": employee
        }

    emp = frappe.get_doc("PMS-Employee", employee)

    full_name = " ".join(filter(None, [
        getattr(emp, "first_name", ""),
        getattr(emp, "middle_name", ""),
        getattr(emp, "last_name", "")
    ])).strip()

    return {
        "employee_name": full_name or emp.name,
        "employee_id": emp.name
    }


# =========================
# ATTENDANCE HISTORY
# =========================
@frappe.whitelist(allow_guest=True)
def get_attendance_history(employee):

    if not employee:
        return []

    return frappe.get_all(
        "PMS-Employee Attendance Log",
        filters={"employee": employee},
        fields=[
            "attendance_date",
            "status",
            "am_time_in",
            "am_time_out",
            "pm_time_in",
            "pm_time_out",
            "total_work_hours"
        ],
        order_by="attendance_date desc",
        limit=30
    )


# =========================
# RECORD ATTENDANCE
# =========================
@frappe.whitelist(allow_guest=True)
def record_attendance(employee):

    if not employee:
        return {
            "success": False,
            "message": "Employee is required"
        }

    current_time = now_datetime()

    attendance_name = frappe.db.exists(
        "PMS-Employee Attendance Log",
        {
            "employee": employee,
            "attendance_date": today()
        }
    )

    # =========================
    # CREATE NEW RECORD
    # =========================
    if not attendance_name:

        doc = frappe.get_doc({
            "doctype": "PMS-Employee Attendance Log",
            "employee": employee,
            "attendance_date": today(),
            "am_time_in": current_time,
            "status": "Present"
        })

        doc.insert(ignore_permissions=True)

        return {
            "success": True,
            "message": "AM Time In recorded",
            "status": doc.status,
            "total_hours": 0
        }

    # =========================
    # UPDATE EXISTING RECORD
    # =========================
    doc = frappe.get_doc("PMS-Employee Attendance Log", attendance_name)

    message = ""

    if not doc.am_time_in:
        doc.am_time_in = current_time
        doc.status = "Present"
        message = "AM Time In recorded"

    elif not doc.am_time_out:
        doc.am_time_out = current_time
        message = "AM Time Out recorded"

    elif not doc.pm_time_in:
        doc.pm_time_in = current_time
        message = "PM Time In recorded"

    elif not doc.pm_time_out:
        doc.pm_time_out = current_time
        message = "PM Time Out recorded"

    else:
        return {
            "success": False,
            "message": "All attendance logs are already completed today."
        }

    # =========================
    # UPDATE HOURS SAFELY
    # =========================
    doc.total_work_hours = compute_total_hours(doc)

    doc.save(ignore_permissions=True)
    frappe.db.commit()

    return {
        "success": True,
        "message": message,
        "status": doc.status,
        "total_hours": doc.total_work_hours or 0
    }