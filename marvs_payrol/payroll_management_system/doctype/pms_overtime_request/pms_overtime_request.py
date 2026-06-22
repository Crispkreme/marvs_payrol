# Copyright (c) 2026, Marvin Ramos and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe.utils import time_diff_in_hours, flt


class PMSOvertimeRequest(Document):

    # ======================================================
    # VALIDATE REQUEST HOURS
    # ======================================================
    def validate(self):
        if self.start_time and self.end_time:
            self.requested_hours = round(
                time_diff_in_hours(self.end_time, self.start_time),
                2
            )

    # ======================================================
    # MAIN ENTRY POINT
    # ======================================================
    def on_update(self):

        if self.status == "Approved":
            self.apply_overtime()

        elif self.status == "Rejected":
            self.remove_overtime()

    # ======================================================
    # APPLY OT
    # ======================================================
    def apply_overtime(self):

        if self.ot_applied_to_attendance:
            return

        attendance_name = frappe.db.get_value(
            "PMS-Employee Attendance Log",
            {
                "employee": self.employee,
                "attendance_date": self.attendance_date
            },
            "name"
        )

        if not attendance_name:
            frappe.throw("Attendance Log not found.")

        attendance = frappe.get_doc(
            "PMS-Employee Attendance Log",
            attendance_name
        )

        total_hours = flt(self.requested_hours)

        # Split hours
        regular_hours = min(total_hours, 8)
        ot_hours = max(total_hours - 8, 0)

        # ========================================
        # UPDATE ATTENDANCE LOG
        # ========================================
        attendance.work_hour = regular_hours
        attendance.overtime = ot_hours

        attendance.save(ignore_permissions=True)

        # ========================================
        # UPDATE ATTENDANCE REPORT
        # ========================================
        report_name = frappe.db.get_value(
            "PMS-Attendance Report",
            {"employee": self.employee},
            "name"
        )

        if not report_name:
            frappe.throw("Attendance Report not found.")

        report = frappe.get_doc(
            "PMS-Attendance Report",
            report_name
        )

        # Regular Day
        if self.overtime_type == "Overtime":

            report.day_shift_hrs += regular_hours
            report.overtime_hrs += ot_hours

        # Regular Holiday
        elif self.overtime_type == "Holiday":

            report.regular_holiday += regular_hours
            report.regular_holiday_ot += ot_hours

        # Special Holiday
        elif self.overtime_type == "Special Holiday":

            report.special_holiday += regular_hours
            report.special_holiday_ot += ot_hours

        # Rest Day
        elif self.overtime_type == "Rest Day":

            report.rest_day += regular_hours
            report.rest_day_ot += ot_hours

        report.save(ignore_permissions=True)

        # ========================================
        # MARK AS APPLIED
        # ========================================
        self.db_set(
            "ot_applied_to_attendance",
            1
        )

        frappe.db.commit()

    # ======================================================
    # REMOVE OT
    # ======================================================
    def remove_overtime(self):

        if not self.employee or not self.attendance_date:
            return

        attendance_name = frappe.db.get_value(
            "PMS-Employee Attendance Log",
            {
                "employee": self.employee,
                "attendance_date": self.attendance_date
            },
            "name"
        )

        if not attendance_name:
            return

        doc = frappe.get_doc(
            "PMS-Employee Attendance Log",
            attendance_name
        )

        doc.overtime = 0
        doc.save(ignore_permissions=True)

        self.db_set("ot_applied_to_attendance", 0)

        frappe.db.commit()