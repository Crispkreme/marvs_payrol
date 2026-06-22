import frappe
from frappe.utils import nowdate, get_first_day, get_last_day

@frappe.whitelist(allow_guest=True)
def get_employee_dashboard(employee):

    # current month range
    from_date = get_first_day(nowdate())
    to_date = get_last_day(nowdate())

    report = frappe.db.get_value(
        "PMS-Attendance Report",
        {
            "employee": employee,
            "modified": ["between", [from_date, to_date]]
        },
        "name"
    )

    if not report:
        return {
            "total_work_hr": 0,
            "total_absent": 0,
            "total_late": 0,
            "total_ot": 0
        }

    doc = frappe.get_doc("PMS-Attendance Report", report)

    work_hours = (
        float(doc.day_shift_hrs or 0) +
        float(doc.night_shift_hrs or 0) +
        float(doc.regular_holiday or 0) +
        float(doc.special_holiday or 0) +
        float(doc.rest_day or 0)
    )

    ot_hours = (
        float(doc.overtime_hrs or 0) +
        float(doc.night_overtime_hrs or 0) +
        float(doc.regular_holiday_ot or 0) +
        float(doc.special_holiday_ot or 0) +
        float(doc.rest_day_ot or 0)
    )

    return {
        "total_work_hr": work_hours,
        "total_absent": doc.absent or 0,
        "total_late": doc.late or 0,
        "total_ot": ot_hours
    }