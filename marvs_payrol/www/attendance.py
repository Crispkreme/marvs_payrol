import frappe
from frappe.utils import (
    now_datetime,
    today,
    time_diff_in_hours,
    getdate
)

# =========================================================
# OFFICE RULES
# =========================================================
OFFICE_START_HOUR = 8
OFFICE_START_MIN = 30

OFFICE_END_HOUR = 17
OFFICE_END_MIN = 30


# =========================================================
# TIME FORMATTER (UI ONLY)
# =========================================================
def format_time_only(dt):
    if not dt:
        return "-"
    try:
        return dt.strftime("%I:%M %p").lstrip("0")
    except:
        return "-"


# =========================================================
# TIME HELPERS
# =========================================================
def time_diff_hours(start, end):
    if start and end:
        return time_diff_in_hours(end, start)
    return 0


def time_diff_minutes(start, end):
    if start and end:
        return time_diff_in_hours(end, start) * 60
    return 0


# =========================================================
# DAILY TOTAL HOURS
# =========================================================
def compute_total_hours(doc):
    am = time_diff_hours(doc.get("am_time_in"), doc.get("am_time_out"))
    pm = time_diff_hours(doc.get("pm_time_in"), doc.get("pm_time_out"))
    return round((am or 0) + (pm or 0), 2)


# =========================================================
# LATE + OVERTIME COMPUTATION
# =========================================================
def compute_late_and_ot(doc):

    late_minutes = 0
    ot_hours = 0

    # -------------------------
    # LATE RULE (8:30 AM)
    # -------------------------
    if doc.am_time_in:
        office_start = doc.am_time_in.replace(
            hour=OFFICE_START_HOUR,
            minute=OFFICE_START_MIN,
            second=0,
            microsecond=0
        )

        if doc.am_time_in > office_start:
            late_minutes = time_diff_minutes(office_start, doc.am_time_in)

    # -------------------------
    # OT RULE (5:30 PM + APPROVAL)
    # -------------------------
    if doc.pm_time_out:

        office_end = doc.pm_time_out.replace(
            hour=OFFICE_END_HOUR,
            minute=OFFICE_END_MIN,
            second=0,
            microsecond=0
        )

        if doc.pm_time_out > office_end:

            if int(getattr(doc, "overtime_approved", 0) or 0) == 1:
                ot_hours = time_diff_hours(office_end, doc.pm_time_out)

    return round(late_minutes, 2), round(ot_hours, 2)


# =========================================================
# MONTHLY SUMMARY (FOR PAYROLL)
# =========================================================
def compute_monthly_summary(employee):

    if not employee:
        return {
            "total_work_hours": 0,
            "total_late_minutes": 0,
            "total_overtime_hours": 0,
            "present_days": 0,
            "absent_days": 0
        }

    today_date = getdate()
    start_date = today_date.replace(day=1)

    logs = frappe.get_all(
        "PMS-Employee Attendance Log",
        filters={
            "employee": employee,
            "attendance_date": ["between", [start_date, today_date]]
        },
        fields=[
            "status",
            "total_work_hours",
            "late_minute",
            "total_overtime_hours"
        ]
    )

    total_hours = 0
    total_late = 0
    total_ot = 0
    present = 0
    absent = 0

    for row in logs:

        total_hours += row.total_work_hours or 0
        total_late += row.late_minute or 0
        total_ot += row.total_overtime_hours or 0

        if row.status == "Present":
            present += 1
        elif row.status == "Absent":
            absent += 1

    return {
        "total_work_hours": round(total_hours, 2),
        "total_late_minutes": round(total_late, 2),
        "total_overtime_hours": round(total_ot, 2),
        "present_days": present,
        "absent_days": absent
    }


# =========================================================
# EMPLOYEE INFO
# =========================================================
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
        emp.first_name,
        emp.middle_name,
        emp.last_name
    ])).strip()

    return {
        "employee_name": full_name or emp.name,
        "employee_id": emp.name
    }


# =========================================================
# ATTENDANCE HISTORY (UI)
# =========================================================
@frappe.whitelist(allow_guest=True)
def get_attendance_history(employee):

    if not employee:
        return []

    data = frappe.get_all(
        "PMS-Employee Attendance Log",
        filters={"employee": employee},
        fields=[
            "attendance_date",
            "status",
            "am_time_in",
            "am_time_out",
            "pm_time_in",
            "pm_time_out",
            "total_work_hours",
            "late_minute",
            "total_overtime_hours"
        ],
        order_by="attendance_date desc",
        limit=30
    )

    for row in data:
        row["am_time_in"] = format_time_only(row.get("am_time_in"))
        row["am_time_out"] = format_time_only(row.get("am_time_out"))
        row["pm_time_in"] = format_time_only(row.get("pm_time_in"))
        row["pm_time_out"] = format_time_only(row.get("pm_time_out"))

    return data


# =========================================================
# RECORD ATTENDANCE (CORE LOGIC)
# =========================================================
@frappe.whitelist(allow_guest=True)
def record_attendance(employee):

    if not employee:
        return {"success": False, "message": "Employee is required"}

    current_time = now_datetime()

    attendance_name = frappe.db.exists(
        "PMS-Employee Attendance Log",
        {
            "employee": employee,
            "attendance_date": today()
        }
    )

    if not attendance_name:

        doc = frappe.get_doc({
            "doctype": "PMS-Employee Attendance Log",
            "employee": employee,
            "attendance_date": today(),
            "am_time_in": current_time,
            "status": "Present",
            "overtime_approved": 0
        })

        doc.insert(ignore_permissions=True)

    else:

        doc = frappe.get_doc("PMS-Employee Attendance Log", attendance_name)

        if not doc.am_time_in:
            doc.am_time_in = current_time

        elif not doc.am_time_out:
            doc.am_time_out = current_time

        elif not doc.pm_time_in:
            doc.pm_time_in = current_time

        elif not doc.pm_time_out:
            doc.pm_time_out = current_time

        else:
            return {
                "success": False,
                "message": "All attendance logs are already completed today."
            }

    # =====================================================
    # COMPUTE DAILY VALUES
    # =====================================================
    doc.total_work_hours = compute_total_hours(doc)

    late, ot = compute_late_and_ot(doc)
    doc.late_minute = late
    doc.total_overtime_hours = ot

    doc.save(ignore_permissions=True)
    frappe.db.commit()

    # =====================================================
    # MONTHLY SUMMARY (FOR PAYROLL)
    # =====================================================
    monthly = compute_monthly_summary(employee)

    return {
        "success": True,
        "message": "Attendance recorded successfully",
        "status": doc.status,

        # DAILY
        "total_work_hours": doc.total_work_hours,
        "late_minute": doc.late_minute,
        "total_overtime_hours": doc.total_overtime_hours,

        # MONTHLY (PAYROLL READY)
        "monthly_summary": monthly,

        # UI TIME ONLY
        "am_time_in": format_time_only(doc.am_time_in),
        "am_time_out": format_time_only(doc.am_time_out),
        "pm_time_in": format_time_only(doc.pm_time_in),
        "pm_time_out": format_time_only(doc.pm_time_out),
    }


# =========================================================
# PAYROLL API (CLEAN INTERFACE)
# =========================================================
@frappe.whitelist()
def get_payroll_inputs(employee):

    summary = compute_monthly_summary(employee)

    return {
        "total_work_hours": summary["total_work_hours"],
        "overtime_hours": summary["total_overtime_hours"],
        "late_minutes": summary["total_late_minutes"],
        "absences": summary["absent_days"]
    }