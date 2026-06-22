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

        ot_hours = flt(self.requested_hours)

        # Safety check
        if ot_hours > flt(attendance.work_hour):
            frappe.throw(
                f"OT ({ot_hours}) cannot exceed work hours ({attendance.work_hour})"
            )

        # ========================================
        # TRANSFER HOURS
        # ========================================
        attendance.work_hour = flt(attendance.work_hour) - ot_hours
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

        if report_name:

            report = frappe.get_doc(
                "PMS-Attendance Report",
                report_name
            )

            report.day_shift_hrs = 0
            report.overtime_hrs = 0
            report.late = 0
            report.absent = 0
            report.leave = 0

            logs = frappe.get_all(
                "PMS-Employee Attendance Log",
                filters={
                    "employee": self.employee
                },
                fields=[
                    "work_hour",
                    "overtime",
                    "late",
                    "status"
                ]
            )

            for d in logs:

                if d.status == "Present":
                    report.day_shift_hrs += flt(d.work_hour)
                    report.overtime_hrs += flt(d.overtime)
                    report.late += flt(d.late)

                elif d.status == "Absent":
                    report.absent += 1

                elif d.status == "Leave":
                    report.leave += 1

            report.save(ignore_permissions=True)

        # Prevent duplicate application
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