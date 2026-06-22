# Copyright (c) 2026, Marvin Ramos and contributors
# For license information, please see license.txt

import frappe
from frappe.utils import flt
from frappe.model.document import Document

class PMSPayrollEntry(Document):
    pass

@frappe.whitelist()
def get_payroll_inputs(employee):

    emp = frappe.get_doc("PMS-Employee", employee)

    report_name = frappe.db.get_value(
        "PMS-Attendance Report",
        {"employee": employee},
        "name"
    )

    report = frappe.get_doc("PMS-Attendance Report", report_name) if report_name else None

    frappe.logger().info(f"EMPLOYEE: {emp.as_dict()}")
    frappe.logger().info(f"REPORT: {report.as_dict() if report else None}")

    return {
        # ======================
        # EMPLOYEE DATA
        # ======================
        "employee_name": emp.full_name,
        "employment_status": emp.employment_status,
        "basic_salary": emp.basic_salary,
        "allowance": emp.allowance,
        "hourly_rate": emp.hourly_rate,
        "daily_rate": emp.daily_rate,

        "sss_contribution": emp.sss_contribution,
        "philhealth_contribution": emp.philhealth_contribution,
        "tin_contribution": emp.tin_contribution,
        "pagibig_contribution": emp.pagibig_contribution,

        # ======================
        # ATTENDANCE DATA
        # ======================
        "day_shift_hrs": report.day_shift_hrs if report else 0,
        "overtime_hrs": report.overtime_hrs if report else 0,
        "night_shift_hrs": report.night_shift_hrs if report else 0,
        "night_overtime_hrs": report.night_overtime_hrs if report else 0,

        "regular_holiday": report.regular_holiday if report else 0,
        "regular_holiday_ot": report.regular_holiday_ot if report else 0,
        "special_holiday": report.special_holiday if report else 0,
        "special_holiday_ot": report.special_holiday_ot if report else 0,
        "rest_day": report.rest_day if report else 0,
        "rest_day_ot": report.rest_day_ot if report else 0,

        "absent": report.absent if report else 0,
        "leave": report.leave if report else 0,
        "late": report.late if report else 0,
    }