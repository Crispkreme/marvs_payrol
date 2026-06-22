import frappe, json
from frappe.utils import (
    now_datetime,
    today,
    getdate
)

from marvs_payrol.utils import (
    safe_float,
    format_hours,
    format_time_only,
    time_diff_hours,
    time_diff_minutes
)

from datetime import datetime, time, timedelta

# =========================================================
# OFFICE RULES
# =========================================================
OFFICE_START_HOUR = 8
OFFICE_START_MIN = 30

OFFICE_END_HOUR = 17
OFFICE_END_MIN = 30


# =========================================================
# DAILY TOTAL HOURS
# =========================================================
def compute_total_hours(doc):
    am = time_diff_hours(doc.get("am_time_in"), doc.get("am_time_out"))
    pm = time_diff_hours(doc.get("pm_time_in"), doc.get("pm_time_out"))
    return round((am or 0) + (pm or 0), 2)

# =========================================================
# NIGHT SHIFT
# =========================================================
def compute_night_hours(time_in, time_out):

    if not time_in or not time_out:
        return 0

    # Night window: 10PM → 6AM
    night_start = time_in.replace(hour=22, minute=0, second=0, microsecond=0)
    night_end = time_in.replace(hour=6, minute=0, second=0, microsecond=0)

    # handle overnight
    if time_out < time_in:
        time_out += timedelta(days=1)
        night_end += timedelta(days=1)

    total_night = 0

    current = time_in

    while current < time_out:

        next_min = min(current.replace(minute=0, second=0, microsecond=0) + timedelta(hours=1), time_out)

        if current.hour >= 22 or current.hour < 6:
            total_night += (next_min - current).total_seconds() / 3600

        current = next_min

    return round(total_night, 2)

# =========================================================
# LATE + OVERTIME
# =========================================================
def compute_late_and_ot(doc):

    late_minutes = 0
    ot_hours = 0

    # LATE (8:30 AM)
    if doc.am_time_in:
        office_start = doc.am_time_in.replace(
            hour=OFFICE_START_HOUR,
            minute=OFFICE_START_MIN,
            second=0,
            microsecond=0
        )

        if doc.am_time_in > office_start:
            late_minutes = time_diff_minutes(office_start, doc.am_time_in)

    # OT (5:30 PM + approval rule)
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
# MONTHLY SUMMARY
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

    start_date = getdate().replace(day=1)
    end_date = getdate()

    logs = frappe.get_all(
        "PMS-Employee Attendance Log",
        filters={
            "employee": employee,
            "attendance_date": ["between", [start_date, end_date]]
        },
        fields=["status", "work_hour", "late", "overtime"]
    )

    total_hours = 0
    total_late = 0
    total_ot = 0
    present = 0
    absent = 0

    for row in logs:
        total_hours += row.work_hour or 0
        total_late += row.late or 0
        total_ot += row.overtime or 0

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
# ATTENDANCE HISTORY
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
            "work_hour",
            "late",
            "overtime"
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
# PAYROLL API
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

# =========================================================
# HELPERS
# =========================================================

def normalize_dt(value):
    if not value:
        return None

    if isinstance(value, str):
        return datetime.strptime(value, "%Y-%m-%d %H:%M:%S")

    return value

def compute_work_hours(doc):
    start = normalize_dt(doc.am_time_in)
    end = normalize_dt(doc.pm_time_out)

    if not start or not end:
        return 0

    diff_seconds = (end - start).total_seconds()

    if diff_seconds < 0:
        return 0  # safety guard for invalid logs

    hours = diff_seconds / 3600

    return round(hours, 2)

def compute_late(doc):
    time_in = normalize_dt(doc.am_time_in)

    if not time_in:
        return 0

    standard = datetime.combine(time_in.date(), time(8, 0))

    if time_in <= standard:
        return 0

    late_minutes = (time_in - standard).total_seconds() / 60

    return round(late_minutes)

# =========================================================
# UPDATE ATTENDANCE REPORT
# =========================================================
def update_attendance_report(employee):

    try:

        if not employee:
            return

        report_name = frappe.db.get_value(
            "PMS-Attendance Report",
            {"employee": employee},
            "name"
        )

        if not report_name:
            return

        report = frappe.get_doc("PMS-Attendance Report", report_name)

        # RESET
        report.day_shift_hrs = 0
        report.overtime_hrs = 0
        report.night_shift_hrs = 0
        report.night_overtime_hrs = 0
        report.absent = 0
        report.leave = 0
        report.late = 0

        logs = frappe.get_all(
            "PMS-Employee Attendance Log",
            filters={"employee": employee},
            fields=[
                "status",
                "work_hour",
                "overtime",
                "late",
                "night_shift_hrs",
                "night_overtime"
            ]
        )

        for d in logs:

            if d.status == "Present":

                report.day_shift_hrs += flt(d.work_hour)
                report.overtime_hrs += flt(d.overtime)

                report.night_shift_hrs += flt(d.night_shift_hrs)
                report.night_overtime_hrs += flt(d.night_overtime)

                report.late += flt(d.late)

            elif d.status == "Absent":
                report.absent += 1

            elif d.status == "Leave":
                report.leave += 1

        report.save(ignore_permissions=True)

    except Exception:
        frappe.log_error(frappe.get_traceback(), "ATTENDANCE REPORT ERROR")
        
# =========================================================
# RECORD ATTENDANCE
# =========================================================
@frappe.whitelist(allow_guest=True)
def record_attendance(employee):

    try:

        if not employee:
            return {"success": False, "message": "Employee is required"}

        current_time = now_datetime()

        log_name = frappe.db.get_value(
            "PMS-Employee Attendance Log",
            {"employee": employee, "attendance_date": today()},
            "name"
        )

        if not log_name:

            doc = frappe.get_doc({
                "doctype": "PMS-Employee Attendance Log",
                "employee": employee,
                "attendance_date": today(),
                "am_time_in": current_time,
                "status": "Present",
                "work_hour": 0,
                "overtime": 0,
                "late": 0,
                "night_shift_hrs": 0,
                "night_overtime": 0,
                "day_type": "Regular Day"
            })

            doc.insert(ignore_permissions=True)

        else:

            doc = frappe.get_doc("PMS-Employee Attendance Log", log_name)

            if not doc.am_time_in:
                doc.am_time_in = current_time

            elif not doc.am_time_out:
                doc.am_time_out = current_time

            elif not doc.pm_time_in:
                doc.pm_time_in = current_time

            elif not doc.pm_time_out:
                doc.pm_time_out = current_time

        # ======================================
        # FIXED TIME PICKING
        # ======================================
        time_in = doc.am_time_in
        time_out = (
            doc.pm_time_out or
            doc.pm_time_in or
            doc.am_time_out
        )

        if time_in and time_out:

            time_in = frappe.utils.get_datetime(time_in)
            time_out = frappe.utils.get_datetime(time_out)

            if time_out < time_in:
                time_out += timedelta(days=1)

            total_hours = (time_out - time_in).total_seconds() / 3600

            night_hours = compute_night_hours(time_in, time_out)

            regular_hours = max(total_hours - night_hours, 0)

            doc.work_hour = round(regular_hours, 2)
            doc.night_shift_hrs = round(night_hours, 2)

            # OPTIONAL: simple night OT rule
            doc.night_overtime = max(doc.night_shift_hrs - 8, 0)

        doc.overtime = safe_float(doc.overtime)
        doc.late = compute_late(doc)

        doc.save(ignore_permissions=True)

        update_attendance_report(employee)

        frappe.db.commit()

        return {
            "success": True,
            "message": "Attendance recorded successfully",
            "work_hour": doc.work_hour,
            "night_shift": doc.night_shift_hrs,
            "night_overtime": doc.night_overtime,
            "late": doc.late
        }

    except Exception:
        frappe.log_error(frappe.get_traceback(), "Attendance Error")
        return {
            "success": False,
            "message": frappe.get_traceback()
        }